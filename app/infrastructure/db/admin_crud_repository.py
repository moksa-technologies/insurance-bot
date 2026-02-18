from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from app.infrastructure.db.postgres_client import PostgresClient


def _json_ready(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {k: _json_ready(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_ready(v) for v in value]
    return value


class AdminCrudRepository:
    def __init__(self, db: PostgresClient) -> None:
        self.db = db

    @staticmethod
    def _norm_text(value: str | None) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _norm_sort_dir(value: str | None) -> str:
        return "DESC" if str(value or "").strip().lower() == "desc" else "ASC"

    @staticmethod
    def _pagination(page: int, page_size: int) -> tuple[int, int]:
        p = max(1, int(page))
        ps = max(1, min(100, int(page_size)))
        return p, ps

    def _list_with_search(
        self,
        *,
        table: str,
        columns: list[str],
        search_columns: list[str],
        pk_fallback: str,
        search: str | None,
        page: int,
        page_size: int,
        sort_by: str | None,
        sort_dir: str | None,
        sortable: dict[str, str],
    ) -> dict[str, Any]:
        page, page_size = self._pagination(page, page_size)
        order_expr = sortable.get((sort_by or "").strip().lower(), sortable.get(pk_fallback, pk_fallback))
        order_dir = self._norm_sort_dir(sort_dir)
        offset = (page - 1) * page_size

        where = ""
        params: list[Any] = []
        if search and search.strip():
            term = f"%{search.strip()}%"
            where = " WHERE " + " OR ".join([f"{expr} ILIKE %s" for expr in search_columns])
            params.extend([term] * len(search_columns))

        count_row = self.db.fetch_one(
            f"SELECT COUNT(*)::BIGINT AS total FROM {table}{where}",
            tuple(params),
        ) or {"total": 0}
        total = int(count_row.get("total", 0))

        list_params = [*params, page_size, offset]
        rows = self.db.fetch_all(
            f"""
            SELECT {", ".join(columns)}
            FROM {table}
            {where}
            ORDER BY {order_expr} {order_dir}
            LIMIT %s OFFSET %s
            """,
            tuple(list_params),
        )
        return {
            "items": [_json_ready(row) for row in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    # Dashboard
    def dashboard_counts(self) -> dict[str, int]:
        row = self.db.fetch_one(
            """
            SELECT
              (SELECT COUNT(*) FROM customer)::INT AS customer_count,
              (SELECT COUNT(*) FROM customer_policies)::INT AS policy_count,
              (SELECT COUNT(*) FROM claim)::INT AS claim_count,
              (SELECT COUNT(*) FROM chat_summary)::INT AS chat_summary_count
            """
        ) or {}
        return {
            "customer_count": int(row.get("customer_count", 0)),
            "policy_count": int(row.get("policy_count", 0)),
            "claim_count": int(row.get("claim_count", 0)),
            "chat_summary_count": int(row.get("chat_summary_count", 0)),
        }

    # CUSTOMER
    def list_customers(
        self,
        search: str | None,
        page: int,
        page_size: int,
        sort_by: str | None,
        sort_dir: str | None,
    ) -> dict[str, Any]:
        return self._list_with_search(
            table="customer",
            columns=["cust_id", "ani", "name", "email", "address", "dob"],
            search_columns=[
                "CAST(cust_id AS TEXT)",
                "COALESCE(ani, '')",
                "COALESCE(name, '')",
                "COALESCE(email, '')",
                "COALESCE(address, '')",
            ],
            pk_fallback="cust_id",
            search=search,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
            sortable={
                "cust_id": "cust_id",
                "ani": "ani",
                "name": "name",
                "email": "email",
                "dob": "dob",
            },
        )

    def get_customer(self, cust_id: int) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            "SELECT cust_id, ani, name, email, address, dob FROM customer WHERE cust_id = %s",
            (cust_id,),
        )
        return _json_ready(row) if row else None

    def create_customer(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = self.db.fetch_one(
            """
            INSERT INTO customer (cust_id, ani, name, email, address, dob)
            VALUES (%s, %s, %s, %s, %s, %s::date)
            RETURNING cust_id, ani, name, email, address, dob
            """,
            (
                payload["cust_id"],
                payload.get("ani"),
                payload["name"],
                payload.get("email"),
                payload.get("address"),
                payload.get("dob"),
            ),
        )
        return _json_ready(row or {})

    def patch_customer(self, cust_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
        updates: list[str] = []
        params: list[Any] = []
        mapping = {
            "ani": "ani = %s",
            "name": "name = %s",
            "email": "email = %s",
            "address": "address = %s",
            "dob": "dob = %s::date",
        }
        for key, expr in mapping.items():
            if key in payload and payload.get(key) is not None:
                updates.append(expr)
                params.append(payload.get(key))

        if not updates:
            return self.get_customer(cust_id)

        params.append(cust_id)
        row = self.db.fetch_one(
            f"""
            UPDATE customer
            SET {", ".join(updates)}
            WHERE cust_id = %s
            RETURNING cust_id, ani, name, email, address, dob
            """,
            tuple(params),
        )
        return _json_ready(row) if row else None

    def delete_customer(self, cust_id: int) -> bool:
        row = self.db.fetch_one(
            "DELETE FROM customer WHERE cust_id = %s RETURNING cust_id",
            (cust_id,),
        )
        return bool(row)

    # POLICIES
    def list_policies(
        self,
        search: str | None,
        page: int,
        page_size: int,
        sort_by: str | None,
        sort_dir: str | None,
    ) -> dict[str, Any]:
        return self._list_with_search(
            table="customer_policies",
            columns=[
                "policy_no",
                "cust_id",
                "vehicle_no",
                "policy_type",
                "benefits",
                "total_coverage",
                "used_coverage",
                "rsa_eligibility",
                "date_of_purchase",
                "date_of_expiry",
                "status",
            ],
            search_columns=[
                "COALESCE(policy_no, '')",
                "CAST(cust_id AS TEXT)",
                "COALESCE(vehicle_no, '')",
                "COALESCE(policy_type, '')",
                "COALESCE(benefits, '')",
                "COALESCE(status, '')",
            ],
            pk_fallback="policy_no",
            search=search,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
            sortable={
                "policy_no": "policy_no",
                "cust_id": "cust_id",
                "vehicle_no": "vehicle_no",
                "policy_type": "policy_type",
                "total_coverage": "total_coverage",
                "used_coverage": "used_coverage",
                "date_of_purchase": "date_of_purchase",
                "date_of_expiry": "date_of_expiry",
                "status": "status",
            },
        )

    def get_policy(self, policy_no: str) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            """
            SELECT policy_no, cust_id, vehicle_no, policy_type, benefits, total_coverage, used_coverage,
                   rsa_eligibility, date_of_purchase, date_of_expiry, status
            FROM customer_policies WHERE policy_no = %s
            """,
            (policy_no,),
        )
        return _json_ready(row) if row else None

    def create_policy(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = self.db.fetch_one(
            """
            INSERT INTO customer_policies (
              policy_no, cust_id, vehicle_no, policy_type, benefits,
              total_coverage, used_coverage, rsa_eligibility,
              date_of_purchase, date_of_expiry, status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::date,%s::date,%s)
            RETURNING policy_no, cust_id, vehicle_no, policy_type, benefits, total_coverage, used_coverage,
                      rsa_eligibility, date_of_purchase, date_of_expiry, status
            """,
            (
                payload["policy_no"],
                payload["cust_id"],
                payload["vehicle_no"],
                payload["policy_type"],
                payload.get("benefits"),
                payload["total_coverage"],
                payload.get("used_coverage", 0),
                payload.get("rsa_eligibility", False),
                payload["date_of_purchase"],
                payload["date_of_expiry"],
                payload["status"],
            ),
        )
        return _json_ready(row or {})

    def patch_policy(self, policy_no: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        updates: list[str] = []
        params: list[Any] = []
        mapping = {
            "cust_id": "cust_id = %s",
            "vehicle_no": "vehicle_no = %s",
            "policy_type": "policy_type = %s",
            "benefits": "benefits = %s",
            "total_coverage": "total_coverage = %s",
            "used_coverage": "used_coverage = %s",
            "rsa_eligibility": "rsa_eligibility = %s",
            "date_of_purchase": "date_of_purchase = %s::date",
            "date_of_expiry": "date_of_expiry = %s::date",
            "status": "status = %s",
        }
        for key, expr in mapping.items():
            if key in payload and payload.get(key) is not None:
                updates.append(expr)
                params.append(payload.get(key))

        if not updates:
            return self.get_policy(policy_no)

        params.append(policy_no)
        row = self.db.fetch_one(
            f"""
            UPDATE customer_policies
            SET {", ".join(updates)}
            WHERE policy_no = %s
            RETURNING policy_no, cust_id, vehicle_no, policy_type, benefits, total_coverage, used_coverage,
                      rsa_eligibility, date_of_purchase, date_of_expiry, status
            """,
            tuple(params),
        )
        return _json_ready(row) if row else None

    def delete_policy(self, policy_no: str) -> bool:
        row = self.db.fetch_one(
            "DELETE FROM customer_policies WHERE policy_no = %s RETURNING policy_no",
            (policy_no,),
        )
        return bool(row)

    # CLAIMS
    def list_claims(
        self,
        search: str | None,
        page: int,
        page_size: int,
        sort_by: str | None,
        sort_dir: str | None,
    ) -> dict[str, Any]:
        return self._list_with_search(
            table="claim",
            columns=[
                "claim_id",
                "cust_id",
                "vehicle_no",
                "incident_date",
                "incident_time",
                "incident_place",
                "damage_type",
                "damage_description",
                "fir_filed",
                "fir_no",
            ],
            search_columns=[
                "CAST(claim_id AS TEXT)",
                "CAST(cust_id AS TEXT)",
                "COALESCE(vehicle_no, '')",
                "COALESCE(incident_place, '')",
                "COALESCE(damage_type, '')",
                "COALESCE(fir_no, '')",
            ],
            pk_fallback="claim_id",
            search=search,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
            sortable={
                "claim_id": "claim_id",
                "cust_id": "cust_id",
                "vehicle_no": "vehicle_no",
                "incident_date": "incident_date",
                "incident_time": "incident_time",
                "damage_type": "damage_type",
                "fir_filed": "fir_filed",
            },
        )

    def get_claim(self, claim_id: int) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            """
            SELECT claim_id, cust_id, vehicle_no, incident_date, incident_time, incident_place,
                   damage_type, damage_description, fir_filed, fir_no
            FROM claim WHERE claim_id = %s
            """,
            (claim_id,),
        )
        return _json_ready(row) if row else None

    def create_claim(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = self.db.fetch_one(
            """
            INSERT INTO claim (
              cust_id, vehicle_no, incident_date, incident_time, incident_place,
              damage_type, damage_description, fir_filed, fir_no
            )
            VALUES (%s,%s,%s::date,%s::time,%s,%s,%s,%s,%s)
            RETURNING claim_id, cust_id, vehicle_no, incident_date, incident_time, incident_place,
                      damage_type, damage_description, fir_filed, fir_no
            """,
            (
                payload["cust_id"],
                payload["vehicle_no"],
                payload["incident_date"],
                payload.get("incident_time"),
                payload.get("incident_place"),
                payload.get("damage_type"),
                payload.get("damage_description"),
                payload.get("fir_filed", False),
                payload.get("fir_no"),
            ),
        )
        return _json_ready(row or {})

    def patch_claim(self, claim_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
        updates: list[str] = []
        params: list[Any] = []
        mapping = {
            "cust_id": "cust_id = %s",
            "vehicle_no": "vehicle_no = %s",
            "incident_date": "incident_date = %s::date",
            "incident_time": "incident_time = %s::time",
            "incident_place": "incident_place = %s",
            "damage_type": "damage_type = %s",
            "damage_description": "damage_description = %s",
            "fir_filed": "fir_filed = %s",
            "fir_no": "fir_no = %s",
        }
        for key, expr in mapping.items():
            if key in payload and payload.get(key) is not None:
                updates.append(expr)
                params.append(payload.get(key))

        if not updates:
            return self.get_claim(claim_id)

        params.append(claim_id)
        row = self.db.fetch_one(
            f"""
            UPDATE claim
            SET {", ".join(updates)}
            WHERE claim_id = %s
            RETURNING claim_id, cust_id, vehicle_no, incident_date, incident_time, incident_place,
                      damage_type, damage_description, fir_filed, fir_no
            """,
            tuple(params),
        )
        return _json_ready(row) if row else None

    def delete_claim(self, claim_id: int) -> bool:
        row = self.db.fetch_one(
            "DELETE FROM claim WHERE claim_id = %s RETURNING claim_id",
            (claim_id,),
        )
        return bool(row)

    # CHAT SUMMARY
    def list_chat_summaries(
        self,
        search: str | None,
        page: int,
        page_size: int,
        sort_by: str | None,
        sort_dir: str | None,
    ) -> dict[str, Any]:
        return self._list_with_search(
            table="chat_summary",
            columns=["cust_id", "chat_summary", "updated_at"],
            search_columns=["CAST(cust_id AS TEXT)", "CAST(chat_summary AS TEXT)"],
            pk_fallback="cust_id",
            search=search,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
            sortable={
                "cust_id": "cust_id",
                "updated_at": "updated_at",
            },
        )

    def get_chat_summary(self, cust_id: int) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            "SELECT cust_id, chat_summary, updated_at FROM chat_summary WHERE cust_id = %s",
            (cust_id,),
        )
        return _json_ready(row) if row else None

    def create_chat_summary(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = self.db.fetch_one(
            """
            INSERT INTO chat_summary (cust_id, chat_summary, updated_at)
            VALUES (%s, %s::jsonb, NOW())
            RETURNING cust_id, chat_summary, updated_at
            """,
            (
                payload["cust_id"],
                json.dumps(payload["chat_summary"], ensure_ascii=False),
            ),
        )
        return _json_ready(row or {})

    def patch_chat_summary(self, cust_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
        if "chat_summary" not in payload or payload.get("chat_summary") is None:
            return self.get_chat_summary(cust_id)

        row = self.db.fetch_one(
            """
            UPDATE chat_summary
            SET chat_summary = %s::jsonb, updated_at = NOW()
            WHERE cust_id = %s
            RETURNING cust_id, chat_summary, updated_at
            """,
            (
                json.dumps(payload["chat_summary"], ensure_ascii=False),
                cust_id,
            ),
        )
        return _json_ready(row) if row else None

    def delete_chat_summary(self, cust_id: int) -> bool:
        row = self.db.fetch_one(
            "DELETE FROM chat_summary WHERE cust_id = %s RETURNING cust_id",
            (cust_id,),
        )
        return bool(row)

    # CALLBACKS (function-backed operations)
    def list_callbacks_queue(
        self,
        *,
        status: str | None,
        assigned_to: str | None,
        due_before: str | None,
        search: str | None,
        page: int,
        page_size: int,
    ) -> dict[str, Any]:
        page, page_size = self._pagination(page, page_size)
        offset = (page - 1) * page_size

        status = self._norm_text(status)
        assigned_to = self._norm_text(assigned_to)
        due_before = self._norm_text(due_before)
        search = self._norm_text(search)

        where = ""
        where_params: list[Any] = []
        if search:
            term = f"%{search}%"
            where = """
            WHERE
              CAST(callback_id AS TEXT) ILIKE %s
              OR COALESCE(ani, '') ILIKE %s
              OR COALESCE(phone, '') ILIKE %s
              OR COALESCE(status, '') ILIKE %s
              OR COALESCE(reason, '') ILIKE %s
              OR COALESCE(assigned_to, '') ILIKE %s
            """
            where_params = [term, term, term, term, term, term]

        total_row = self.db.fetch_one(
            f"""
            SELECT COUNT(*)::BIGINT AS total
            FROM callback_queue(%s, %s, %s::timestamptz, 1000000, 0) cb
            {where}
            """,
            (
                status,
                assigned_to,
                due_before,
                *where_params,
            ),
        ) or {"total": 0}
        total = int(total_row.get("total", 0))

        rows = self.db.fetch_all(
            f"""
            SELECT to_jsonb(cb) AS result
            FROM callback_queue(%s, %s, %s::timestamptz, 1000000, 0) cb
            {where}
            ORDER BY priority ASC, COALESCE(scheduled_at, preferred_from, created_at) ASC, callback_id ASC
            LIMIT %s OFFSET %s
            """,
            (
                status,
                assigned_to,
                due_before,
                *where_params,
                page_size,
                offset,
            ),
        )
        items = [_json_ready(row.get("result", {})) for row in rows]
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def get_callback(self, callback_id: int) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            "SELECT to_jsonb(callback_get(%s::bigint)) AS result",
            (callback_id,),
        )
        if not row:
            return None
        result = row.get("result")
        return _json_ready(result) if isinstance(result, dict) else None

    def create_callback(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = self.db.fetch_one(
            """
            SELECT to_jsonb(
              callback_create(
                %s::bigint, %s::varchar, %s::varchar, %s::text,
                %s::timestamptz, %s::timestamptz, %s::timestamptz,
                %s::varchar, %s::smallint, %s::varchar
              )
            ) AS result
            """,
            (
                payload.get("cust_id"),
                payload.get("ani"),
                payload.get("phone"),
                payload.get("reason"),
                payload.get("preferred_from"),
                payload.get("preferred_to"),
                payload.get("scheduled_at"),
                payload.get("status"),
                payload.get("priority") if payload.get("priority") is not None else 3,
                payload.get("assigned_to"),
            ),
        )
        result = (row or {}).get("result")
        return _json_ready(result if isinstance(result, dict) else {})

    def patch_callback(self, callback_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            """
            SELECT to_jsonb(
              callback_update_patch(
                %s::bigint,
                %s::bigint, %s::varchar, %s::varchar, %s::text,
                %s::timestamptz, %s::timestamptz, %s::timestamptz,
                %s::varchar, %s::smallint, %s::varchar,
                %s::int, %s::timestamptz, %s::text
              )
            ) AS result
            """,
            (
                callback_id,
                payload.get("cust_id"),
                payload.get("ani"),
                payload.get("phone"),
                payload.get("reason"),
                payload.get("preferred_from"),
                payload.get("preferred_to"),
                payload.get("scheduled_at"),
                payload.get("status"),
                payload.get("priority"),
                payload.get("assigned_to"),
                payload.get("attempt_count"),
                payload.get("last_attempt_at"),
                payload.get("outcome"),
            ),
        )
        if not row:
            return None
        result = row.get("result")
        return _json_ready(result) if isinstance(result, dict) else None

    def mark_callback_attempt(
        self,
        callback_id: int,
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            """
            SELECT to_jsonb(
              callback_mark_attempt(
                %s::bigint,
                %s::varchar,
                %s::text,
                COALESCE(%s::timestamptz, NOW())
              )
            ) AS result
            """,
            (
                callback_id,
                payload.get("status"),
                payload.get("outcome"),
                payload.get("attempt_at"),
            ),
        )
        if not row:
            return None
        result = row.get("result")
        return _json_ready(result) if isinstance(result, dict) else None

    def delete_callback(self, callback_id: int) -> bool:
        row = self.db.fetch_one(
            "SELECT callback_delete(%s::bigint) AS deleted",
            (callback_id,),
        ) or {}
        return bool(row.get("deleted"))

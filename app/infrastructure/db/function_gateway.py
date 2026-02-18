from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from app.infrastructure.db.postgres_client import PostgresClient


LOGGER = logging.getLogger(__name__)


class CustomerFunctionGateway:
    def __init__(self, db: PostgresClient) -> None:
        self.db = db

    @staticmethod
    def _coerce_json(value: Any) -> dict[str, Any] | list[Any] | None:
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {"raw": value}
        return {"raw": str(value)}

    @staticmethod
    def _coerce_timestamptz(value: Any, tz_name: str = "Asia/Kolkata") -> str | None:
        if value is None:
            return None

        tz = ZoneInfo(tz_name)
        if isinstance(value, datetime):
            dt = value.replace(
                tzinfo=tz) if value.tzinfo is None else value.astimezone(tz)
            return dt.isoformat()

        text = str(value).strip()
        if not text:
            return None

        low = text.lower()
        if "current" in low or "now" in low:
            return datetime.now(tz).isoformat()

        # Accept ISO-like datetime inputs (e.g. 2026-02-17T10:30:00+05:30).
        try:
            iso_candidate = text.replace("Z", "+00:00")
            dt = datetime.fromisoformat(iso_candidate)
            dt = dt.replace(
                tzinfo=tz) if dt.tzinfo is None else dt.astimezone(tz)
            return dt.isoformat()
        except ValueError:
            pass

        # Accept time-only values like 9am, 6 pm, 18:30, 09:15pm.
        normalized = low.replace(".", "")
        match = re.match(
            r"^(?P<h>\d{1,2})(:(?P<m>\d{2}))?\s*(?P<ampm>am|pm)?$", normalized)
        if match:
            hour = int(match.group("h"))
            minute = int(match.group("m") or "0")
            ampm = match.group("ampm")

            if minute > 59:
                return None

            if ampm:
                if hour < 1 or hour > 12:
                    return None
                if hour == 12:
                    hour = 0
                if ampm == "pm":
                    hour += 12
            elif hour > 23:
                return None

            now_local = datetime.now(tz)
            dt = now_local.replace(
                hour=hour, minute=minute, second=0, microsecond=0)
            return dt.isoformat()

        return None

    def pull_customer_profile_by_ani(self, Phone_number: str) -> dict[str, Any] | None:
        LOGGER.info(
            "db_function:get_customer_profile_by_ani ani=%s", Phone_number)
        row = self.db.fetch_one(
            "SELECT get_customer_profile_by_ani(%s) AS result",
            (Phone_number,),
        )
        if row is None:
            LOGGER.warning(
                "db_function:get_customer_profile_by_ani no_row ani=%s", Phone_number)
            return None
        result = self._coerce_json(row.get("result"))
        LOGGER.info(
            "db_function:get_customer_profile_by_ani done ani=%s found=%s", Phone_number, bool(result))
        return result

    def get_customer_profile_by_ani(self, ani: str) -> dict[str, Any] | None:
        LOGGER.info("db_function:get_customer_profile_by_ani ani=%s", ani)
        row = self.db.fetch_one(
            "SELECT get_customer_profile_by_ani(%s) AS result",
            (ani,),
        )
        if row is None:
            LOGGER.warning(
                "db_function:get_customer_profile_by_ani no_row ani=%s", ani)
            return None
        result = self._coerce_json(row.get("result"))
        LOGGER.info(
            "db_function:get_customer_profile_by_ani done ani=%s found=%s", ani, bool(result))
        return result

    def customer_create(
        self,
        cust_id: int,
        ani: str | None,
        name: str,
        email: str | None,
        address: str | None,
        dob: str | None,
    ) -> dict[str, Any]:
        LOGGER.info(
            "db_function:customer_create cust_id=%s ani=%s", cust_id, ani)
        row = self.db.fetch_one(
            """
            SELECT to_jsonb(
              customer_create(
                %s::bigint, %s::varchar, %s::varchar, %s::varchar, %s::text, %s::date
              )
            ) AS result
            """,
            (
                cust_id,
                ani,
                name,
                email,
                address,
                dob,
            ),
        )
        payload = self._coerce_json(row.get("result") if row else None)
        if isinstance(payload, dict):
            result = {"ok": True, "message": "Customer created",
                      "customer": payload}
        else:
            result = {"ok": False, "message": "No response", "customer": None}
        LOGGER.info("db_function:customer_create done cust_id=%s ok=%s",
                    cust_id, result.get("ok"))
        return result

    def update_customer_email_by_ani(self, ani: str, new_email: str) -> dict[str, Any]:
        LOGGER.info("db_function:update_customer_email_by_ani ani=%s", ani)
        row = self.db.fetch_one(
            "SELECT update_customer_email_by_ani(%s,%s) AS result",
            (ani, new_email),
        )
        result = self._coerce_json(row.get("result") if row else None) or {
            "ok": False, "message": "No response"}
        LOGGER.info(
            "db_function:update_customer_email_by_ani done ani=%s ok=%s", ani, result.get("ok"))
        return result

    def update_customer_address_by_ani(self, ani: str, new_address: str) -> dict[str, Any]:
        LOGGER.info("db_function:update_customer_address_by_ani ani=%s", ani)
        row = self.db.fetch_one(
            "SELECT update_customer_address_by_ani(%s,%s) AS result",
            (ani, new_address),
        )
        result = self._coerce_json(row.get("result") if row else None) or {
            "ok": False, "message": "No response"}
        LOGGER.info(
            "db_function:update_customer_address_by_ani done ani=%s ok=%s", ani, result.get("ok"))
        return result

    def change_customer_ani(self, old_ani: str, new_ani: str) -> dict[str, Any]:
        LOGGER.info(
            "db_function:change_customer_ani old_ani=%s new_ani=%s", old_ani, new_ani)
        row = self.db.fetch_one(
            "SELECT change_customer_ani(%s,%s) AS result",
            (old_ani, new_ani),
        )
        result = self._coerce_json(row.get("result") if row else None) or {
            "ok": False, "message": "No response"}
        LOGGER.info("db_function:change_customer_ani done old_ani=%s ok=%s",
                    old_ani, result.get("ok"))
        return result

    def create_claim_by_ani(
        self,
        ani: str,
        vehicle_no: str,
        incident_date: str,
        incident_time: str | None,
        incident_place: str | None,
        damage_type: str | None,
        damage_description: str | None,
        fir_filed: bool,
        fir_no: str | None,
    ) -> dict[str, Any]:
        LOGGER.info(
            "db_function:create_claim_by_ani ani=%s vehicle_no=%s", ani, vehicle_no)
        row = self.db.fetch_one(
            """
            SELECT create_claim_by_ani(%s,%s,%s::date,%s::time,%s,%s,%s,%s,%s) AS result
            """,
            (
                ani,
                vehicle_no,
                incident_date,
                incident_time,
                incident_place,
                damage_type,
                damage_description,
                fir_filed,
                fir_no,
            ),
        )
        result = self._coerce_json(row.get("result") if row else None) or {
            "ok": False, "message": "No response"}
        LOGGER.info(
            "db_function:create_claim_by_ani done ani=%s ok=%s", ani, result.get("ok"))
        return result

    def callback_create(
        self,
        cust_id: int | None = None,
        ani: str | None = None,
        phone: str | None = None,
        reason: str | None = None,
        preferred_from: str | None = None,
        preferred_to: str | None = None,
        scheduled_at: str | None = None,
        status: str | None = None,
        priority: int = 3,
        assigned_to: str | None = None,
    ) -> dict[str, Any]:
        preferred_from_ts = self._coerce_timestamptz(preferred_from)
        preferred_to_ts = self._coerce_timestamptz(preferred_to)
        scheduled_at_ts = self._coerce_timestamptz(scheduled_at)
        LOGGER.info(
            "db_function:callback_create cust_id=%s ani=%s priority=%s assigned_to=%s preferred_from=%s preferred_to=%s scheduled_at=%s",
            cust_id,
            ani,
            priority,
            assigned_to,
            preferred_from_ts,
            preferred_to_ts,
            scheduled_at_ts,
        )
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
                cust_id,
                ani,
                phone,
                reason,
                preferred_from_ts,
                preferred_to_ts,
                scheduled_at_ts,
                status,
                priority,
                assigned_to,
            ),
        )
        payload = self._coerce_json(row.get("result") if row else None)
        if isinstance(payload, dict):
            result = {"ok": True, "message": "Callback created",
                      "callback": payload}
        else:
            result = {"ok": False, "message": "No response", "callback": None}
        LOGGER.info("db_function:callback_create done ok=%s", result.get("ok"))
        return result

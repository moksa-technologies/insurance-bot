from __future__ import annotations

from app.infrastructure.db.postgres_client import PostgresClient


EXPECTED_SIGNATURES = {
    "customer_create(bigint,character varying,character varying,character varying,text,date)": "customer_create",
    "get_customer_profile_by_ani(text)": "get_customer_profile_by_ani",
    "update_customer_email_by_ani(text,text)": "update_customer_email_by_ani",
    "update_customer_address_by_ani(text,text)": "update_customer_address_by_ani",
    "change_customer_ani(text,text)": "change_customer_ani",
    "create_claim_by_ani(text,text,date,time without time zone,text,text,text,boolean,text)": "create_claim_by_ani",
    "callback_create(bigint,character varying,character varying,text,timestamp with time zone,timestamp with time zone,timestamp with time zone,character varying,smallint,character varying)": "callback_create",
    "callback_get(bigint)": "callback_get",
    "callback_queue(character varying,character varying,timestamp with time zone,integer,integer)": "callback_queue",
    "callback_update_patch(bigint,bigint,character varying,character varying,text,timestamp with time zone,timestamp with time zone,timestamp with time zone,character varying,smallint,character varying,integer,timestamp with time zone,text)": "callback_update_patch",
    "callback_mark_attempt(bigint,character varying,text,timestamp with time zone)": "callback_mark_attempt",
    "callback_delete(bigint)": "callback_delete",
}


class DatabaseFunctionVerifier:
    def __init__(self, db: PostgresClient) -> None:
        self.db = db

    def verify(self) -> dict[str, bool]:
        checks: dict[str, bool] = {}
        for signature in EXPECTED_SIGNATURES:
            row = self.db.fetch_one("SELECT to_regprocedure(%s) IS NOT NULL AS ok", (signature,))
            checks[signature] = bool(row and row.get("ok"))
        return checks

    def verify_or_raise(self) -> None:
        checks = self.verify()
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            raise RuntimeError(f"Missing required database functions: {', '.join(failed)}")

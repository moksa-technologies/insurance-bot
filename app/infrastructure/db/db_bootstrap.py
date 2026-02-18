from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.infrastructure.db.postgres_client import PostgresClient


class DatabaseBootstrapper:
    def __init__(self, settings: Settings, db: PostgresClient) -> None:
        self.settings = settings
        self.db = db

    def _default_schema_root(self) -> Path:
        # Repo: Insurence_bot_v1.0 is sibling of Database_schema.
        candidate = Path(__file__).resolve().parents[4] / "Database_schema"
        if candidate.exists():
            return candidate
        return Path("Database_schema")

    @staticmethod
    def _layout_root(root: Path) -> Path:
        nested = root / "Insurence_Db"
        if nested.exists():
            return nested
        return root

    def _sql_files(self, include_seed: bool = False) -> list[Path]:
        root = self._layout_root(self._default_schema_root())
        files = [
            root / "Tables" / "insurancedb_schema.sql",
            root / "Functions" / "customer_create.sql",
            root / "Functions" / "get_customer_profile_by_ani.sql",
            root / "Functions" / "update_customer_email_by_ani.sql",
            root / "Functions" / "update_customer_address_by_ani.sql",
            root / "Functions" / "change_customer_ani.sql",
            root / "Functions" / "create_claim_by_ani.sql",
            root / "Functions" / "CALL_BACK_CRUD.sql",
        ]
        if include_seed:
            files.append(root / "dummy_data" / "seeddummydata.sql")
        return files

    def apply(self, include_seed: bool = False) -> dict[str, str]:
        status: dict[str, str] = {}
        for sql_path in self._sql_files(include_seed=include_seed):
            if not sql_path.exists():
                status[str(sql_path)] = "missing"
                continue
            if sql_path.name == "insurancedb_schema.sql":
                row = self.db.fetch_one(
                    "SELECT to_regclass('public.customer') IS NOT NULL AS exists_flag"
                )
                if row and row.get("exists_flag"):
                    status[str(sql_path)] = "skipped_existing_schema"
                    continue
            content = sql_path.read_text(encoding="utf-8")
            self.db.execute(content)
            status[str(sql_path)] = "applied"
        return status

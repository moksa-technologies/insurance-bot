from __future__ import annotations

from typing import Any

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import Settings


class PostgresClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pool = ConnectionPool(
            conninfo=self.settings.database_dsn,
            min_size=1,
            max_size=8,
            open=False,
            configure=self._configure_connection,
        )

    def _configure_connection(self, conn: Any) -> None:
        timezone = self.settings.timezone.replace("'", "")
        conn.execute(f"SET TIME ZONE '{timezone}'")
        conn.commit()

    def open(self) -> None:
        try:
            self.pool.open(wait=True)
        except Exception as exc:
            raise RuntimeError(
                "PostgreSQL connection failed for "
                f"{self.settings.postgres_host}:{self.settings.postgres_port}/{self.settings.postgres_db}. "
                f"Verify POSTGRES_HOST/PORT/DB/USER/PASSWORD."
            ) from exc

    def close(self) -> None:
        self.pool.close()

    def execute(self, query: str, params: tuple[Any, ...] | None = None) -> None:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                if params is None:
                    cur.execute(query)
                else:
                    cur.execute(query, params)
            conn.commit()

    def fetch_one(self, query: str, params: tuple[Any, ...] | None = None) -> dict[str, Any] | None:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if params is None:
                    cur.execute(query)
                else:
                    cur.execute(query, params)
                return cur.fetchone()

    def fetch_all(self, query: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if params is None:
                    cur.execute(query)
                else:
                    cur.execute(query, params)
                return cur.fetchall()

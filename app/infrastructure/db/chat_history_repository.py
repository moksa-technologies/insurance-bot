from __future__ import annotations

import json
from typing import Any

from app.config import Settings
from app.infrastructure.db.postgres_client import PostgresClient


class ChatHistoryRepository:
    def __init__(self, settings: Settings, db: PostgresClient) -> None:
        self.settings = settings
        self.db = db

    def ensure_tables(self) -> None:
        chat_table = self.settings.chat_history_table

        self.db.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {chat_table} (
                id BIGSERIAL PRIMARY KEY,
                ani VARCHAR(20) NOT NULL,
                session_uuid TEXT NOT NULL,
                input_message TEXT NOT NULL,
                response_message TEXT NOT NULL,
                language VARCHAR(16) NOT NULL,
                intent VARCHAR(80) NOT NULL,
                data_references JSONB,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )

    def add_chat_record(
        self,
        ani: str,
        session_uuid: str,
        input_message: str,
        response_message: str,
        language: str,
        intent: str,
        data_references: dict[str, Any],
    ) -> None:
        self.db.execute(
            f"""
            INSERT INTO {self.settings.chat_history_table}
            (ani, session_uuid, input_message, response_message, language, intent, data_references)
            VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb)
            """,
            (
                ani,
                session_uuid,
                input_message,
                response_message,
                language,
                intent,
                json.dumps(data_references, default=str),
            ),
        )

    def recent_messages(self, ani: str, session_uuid: str, limit: int = 6) -> list[dict[str, Any]]:
        rows = self.db.fetch_all(
            f"""
            SELECT input_message, response_message, language, intent, created_at
            FROM {self.settings.chat_history_table}
            WHERE ani = %s AND session_uuid = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (ani, session_uuid, limit),
        )
        return rows

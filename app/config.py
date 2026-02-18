from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Insurence Bot v1.0"
    app_env: str = "dev"
    timezone: str = "Asia/Kolkata"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "demo_insurence"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    db_auto_bootstrap: bool = True
    db_bootstrap_seed: bool = False

    llm_openai_base_url: str = Field(
        default="https://api.openai.com/v1", alias="LLM_OPENAI_BASE_URL")
    llm_openai_api_key: str = Field(
        default="replace_me", alias="LLM_OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_temperature: float = 0.7

    embedding_openai_base_url: str = Field(
        default="https://api.openai.com/v1", alias="EMBEDDING_OPENAI_BASE_URL")
    embedding_openai_api_key: str = Field(
        default="replace_me", alias="EMBEDDING_OPENAI_API_KEY")
    embedding_model: str = Field(
        default="text-embedding-3-small", alias="EMBEDDING_MODEL")

    hospital_excel_path: str = "data/excel/hospitals.xlsx"
    garage_excel_path: str = "data/excel/garages.xlsx"
    pdf_dir: str = "data/pdfs"
    vector_dir: str = "data/vector"
    app_log_file: str = "logs/app.log"
    transcript_dir: str = "logs/transcripts"
    log_level: str = "INFO"

    chat_history_table: str = "bot_chat_history"

    rag_chunk_size: int = 900
    rag_chunk_overlap: int = 120
    rag_top_k: int = 4

    @property
    def database_dsn(self) -> str:
        # Encode credentials so special characters (e.g. @, :, /) don't break host parsing.
        user = quote(self.postgres_user, safe="")
        password = quote(self.postgres_password, safe="")
        return (
            f"postgresql://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def hospital_path(self) -> Path:
        return Path(self.hospital_excel_path)

    @property
    def garage_path(self) -> Path:
        return Path(self.garage_excel_path)

    @property
    def pdf_root(self) -> Path:
        return Path(self.pdf_dir)

    @property
    def vector_root(self) -> Path:
        return Path(self.vector_dir)

    @property
    def app_log_path(self) -> Path:
        return Path(self.app_log_file)

    @property
    def transcript_root(self) -> Path:
        return Path(self.transcript_dir)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

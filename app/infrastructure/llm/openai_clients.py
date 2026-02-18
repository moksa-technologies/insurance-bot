from __future__ import annotations

from openai import OpenAI

from app.config import Settings


class OpenAIClients:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.llm_client = OpenAI(
            api_key=settings.llm_openai_api_key,
            base_url=settings.llm_openai_base_url,
        )
        self.embedding_client = OpenAI(
            api_key=settings.embedding_openai_api_key,
            base_url=settings.embedding_openai_base_url,
        )

from __future__ import annotations

from app.infrastructure.retrieval.pdf_rag_service import PDFRAGService


class RagTool:
    def __init__(self, rag_service: PDFRAGService) -> None:
        self.rag_service = rag_service

    def rag_kb_tool(self, query_en: str, top_k: int = 4) -> list[dict[str, object]]:
        return self.rag_service.query(query_en=query_en, top_k=top_k)

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class KnowledgeSnippet:
    source_file: str
    page_number: int
    snippet: str
    score: float

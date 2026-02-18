from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(slots=True)
class CustomerProfile:
    ani: str
    name: str | None = None
    email: str | None = None
    dob: date | None = None
    policies: list[dict[str, Any]] = field(default_factory=list)
    claims: list[dict[str, Any]] = field(default_factory=list)
    last_chat_summary: dict[str, Any] | None = None
    chat_updated_at: str | None = None


@dataclass(slots=True)
class CustomerMutationResult:
    ok: bool
    message: str
    customer: dict[str, Any] | None = None

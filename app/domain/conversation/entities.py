from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ConversationState:
    ani: str
    session_uuid: str
    flow_type: str | None = None
    step: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

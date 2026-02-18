from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AssistanceLocation:
    area: str | None = None
    city: str | None = None
    pincode: str | None = None

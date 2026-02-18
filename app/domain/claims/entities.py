from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClaimCreateInput:
    ani: str
    vehicle_no: str
    incident_date: str
    incident_time: str | None = None
    incident_place: str | None = None
    damage_type: str | None = None
    damage_description: str | None = None
    fir_filed: bool = False
    fir_no: str | None = None

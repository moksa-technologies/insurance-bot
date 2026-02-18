from __future__ import annotations

from datetime import date, datetime, time
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class ChatRequest(BaseModel):
    ani: str
    session_uuid: str | None = None
    input_message: str
    channel: str = "web"

    @model_validator(mode="after")
    def validate_input(self) -> "ChatRequest":
        self.ani = self.ani.strip()
        if not self.ani:
            raise ValueError("ANI is required")
        if not self.input_message or not self.input_message.strip():
            raise ValueError("input_message is required")
        if not self.session_uuid:
            self.session_uuid = str(uuid4())
        return self


class DataReferences(BaseModel):
    database_function: str | None = None
    external_source: str | list[str] | None = None


class ChatResponse(BaseModel):
    session_uuid: str
    language: str
    response: str
    follow_up_needed: bool = False
    follow_up_query: str | None = None
    intent: str
    data_references: DataReferences = Field(default_factory=DataReferences)


class ToolSelfTestResponse(BaseModel):
    ok: bool
    checks: dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    dependencies: dict[str, str]


class DetectedLanguage(BaseModel):
    language: str
    is_mixed: bool = False


class DashboardCountsResponse(BaseModel):
    customer_count: int
    policy_count: int
    claim_count: int
    chat_summary_count: int


class PaginatedResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int


class CustomerCreateRequest(BaseModel):
    cust_id: int
    ani: str | None = None
    name: str
    email: str | None = None
    address: str | None = None
    dob: date | None = None


class CustomerPatchRequest(BaseModel):
    ani: str | None = None
    name: str | None = None
    email: str | None = None
    address: str | None = None
    dob: date | None = None


class PolicyCreateRequest(BaseModel):
    policy_no: str
    cust_id: int
    vehicle_no: str
    policy_type: str
    benefits: str | None = None
    total_coverage: float
    used_coverage: float = 0.0
    rsa_eligibility: bool = False
    date_of_purchase: date
    date_of_expiry: date
    status: str = "Active"


class PolicyPatchRequest(BaseModel):
    cust_id: int | None = None
    vehicle_no: str | None = None
    policy_type: str | None = None
    benefits: str | None = None
    total_coverage: float | None = None
    used_coverage: float | None = None
    rsa_eligibility: bool | None = None
    date_of_purchase: date | None = None
    date_of_expiry: date | None = None
    status: str | None = None


class ClaimCreateRequest(BaseModel):
    cust_id: int
    vehicle_no: str
    incident_date: date
    incident_time: time | None = None
    incident_place: str | None = None
    damage_type: str | None = None
    damage_description: str | None = None
    fir_filed: bool = False
    fir_no: str | None = None


class ClaimPatchRequest(BaseModel):
    cust_id: int | None = None
    vehicle_no: str | None = None
    incident_date: date | None = None
    incident_time: time | None = None
    incident_place: str | None = None
    damage_type: str | None = None
    damage_description: str | None = None
    fir_filed: bool | None = None
    fir_no: str | None = None


class ChatSummaryCreateRequest(BaseModel):
    cust_id: int
    chat_summary: dict[str, Any]


class ChatSummaryPatchRequest(BaseModel):
    chat_summary: dict[str, Any] | None = None


class CallbackCreateRequest(BaseModel):
    cust_id: int | None = None
    ani: str | None = None
    phone: str | None = None
    reason: str | None = None
    preferred_from: datetime | None = None
    preferred_to: datetime | None = None
    scheduled_at: datetime | None = None
    status: str | None = None
    priority: int = 3
    assigned_to: str | None = None


class CallbackPatchRequest(BaseModel):
    cust_id: int | None = None
    ani: str | None = None
    phone: str | None = None
    reason: str | None = None
    preferred_from: datetime | None = None
    preferred_to: datetime | None = None
    scheduled_at: datetime | None = None
    status: str | None = None
    priority: int | None = None
    assigned_to: str | None = None
    attempt_count: int | None = None
    last_attempt_at: datetime | None = None
    outcome: str | None = None


class CallbackAttemptRequest(BaseModel):
    status: str | None = None
    outcome: str | None = None
    attempt_at: datetime | None = None


class RecordResponse(BaseModel):
    record: dict[str, Any]


class DeleteResponse(BaseModel):
    ok: bool
    deleted: bool
    message: str

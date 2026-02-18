from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from app.infrastructure.db.admin_crud_repository import AdminCrudRepository
from app.interfaces.api.schemas import (
    CallbackAttemptRequest,
    CallbackCreateRequest,
    CallbackPatchRequest,
    ChatRequest,
    ChatResponse,
    ChatSummaryCreateRequest,
    ChatSummaryPatchRequest,
    ClaimCreateRequest,
    ClaimPatchRequest,
    DashboardCountsResponse,
    DeleteResponse,
    HealthResponse,
    PaginatedResponse,
    PolicyCreateRequest,
    PolicyPatchRequest,
    RecordResponse,
    CustomerCreateRequest,
    CustomerPatchRequest,
    ToolSelfTestResponse,
)


router = APIRouter()


def _admin_repo(request: Request) -> AdminCrudRepository:
    return request.app.state.admin_repo


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    status_provider = request.app.state.status_provider
    return status_provider.health()


@router.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request_data: ChatRequest, request: Request) -> ChatResponse:
    use_case = request.app.state.chat_use_case
    return await use_case.execute(request_data)


@router.post("/admin/reload-assets")
async def reload_assets(request: Request) -> dict[str, str]:
    excel_service = request.app.state.excel_service
    rag_service = request.app.state.rag_service
    excel_service.refresh()
    rag_service.build_index(force=True)
    return {"status": "reloaded"}


@router.get("/admin/tools/self-test", response_model=ToolSelfTestResponse)
async def self_test(request: Request) -> ToolSelfTestResponse:
    return request.app.state.status_provider.self_test()


@router.get("/api/v1/admin/dashboard", response_model=DashboardCountsResponse)
async def admin_dashboard(request: Request) -> DashboardCountsResponse:
    repo = _admin_repo(request)
    return DashboardCountsResponse(**repo.dashboard_counts())


# CUSTOMER CRUD
@router.get("/api/v1/admin/customers", response_model=PaginatedResponse)
async def list_customers(
    request: Request,
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_by: str | None = Query(default="cust_id"),
    sort_dir: str | None = Query(default="asc"),
) -> PaginatedResponse:
    repo = _admin_repo(request)
    data = repo.list_customers(search=search, page=page, page_size=page_size, sort_by=sort_by, sort_dir=sort_dir)
    return PaginatedResponse(**data)


@router.get("/api/v1/admin/customers/{cust_id}", response_model=RecordResponse)
async def get_customer(cust_id: int, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    row = repo.get_customer(cust_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return RecordResponse(record=row)


@router.post("/api/v1/admin/customers", response_model=RecordResponse, status_code=201)
async def create_customer(payload: CustomerCreateRequest, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    try:
        row = repo.create_customer(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Create customer failed: {exc}") from exc
    return RecordResponse(record=row)


@router.patch("/api/v1/admin/customers/{cust_id}", response_model=RecordResponse)
async def patch_customer(cust_id: int, payload: CustomerPatchRequest, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    try:
        row = repo.patch_customer(cust_id, payload.model_dump(exclude_unset=True))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Update customer failed: {exc}") from exc
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return RecordResponse(record=row)


@router.delete("/api/v1/admin/customers/{cust_id}", response_model=DeleteResponse)
async def delete_customer(cust_id: int, request: Request) -> DeleteResponse:
    repo = _admin_repo(request)
    deleted = repo.delete_customer(cust_id)
    return DeleteResponse(ok=True, deleted=deleted, message="Deleted" if deleted else "Customer not found")


# POLICY CRUD
@router.get("/api/v1/admin/policies", response_model=PaginatedResponse)
async def list_policies(
    request: Request,
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_by: str | None = Query(default="policy_no"),
    sort_dir: str | None = Query(default="asc"),
) -> PaginatedResponse:
    repo = _admin_repo(request)
    data = repo.list_policies(search=search, page=page, page_size=page_size, sort_by=sort_by, sort_dir=sort_dir)
    return PaginatedResponse(**data)


@router.get("/api/v1/admin/policies/{policy_no}", response_model=RecordResponse)
async def get_policy(policy_no: str, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    row = repo.get_policy(policy_no)
    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")
    return RecordResponse(record=row)


@router.post("/api/v1/admin/policies", response_model=RecordResponse, status_code=201)
async def create_policy(payload: PolicyCreateRequest, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    try:
        row = repo.create_policy(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Create policy failed: {exc}") from exc
    return RecordResponse(record=row)


@router.patch("/api/v1/admin/policies/{policy_no}", response_model=RecordResponse)
async def patch_policy(policy_no: str, payload: PolicyPatchRequest, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    try:
        row = repo.patch_policy(policy_no, payload.model_dump(exclude_unset=True))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Update policy failed: {exc}") from exc
    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")
    return RecordResponse(record=row)


@router.delete("/api/v1/admin/policies/{policy_no}", response_model=DeleteResponse)
async def delete_policy(policy_no: str, request: Request) -> DeleteResponse:
    repo = _admin_repo(request)
    deleted = repo.delete_policy(policy_no)
    return DeleteResponse(ok=True, deleted=deleted, message="Deleted" if deleted else "Policy not found")


# CLAIM CRUD
@router.get("/api/v1/admin/claims", response_model=PaginatedResponse)
async def list_claims(
    request: Request,
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_by: str | None = Query(default="claim_id"),
    sort_dir: str | None = Query(default="desc"),
) -> PaginatedResponse:
    repo = _admin_repo(request)
    data = repo.list_claims(search=search, page=page, page_size=page_size, sort_by=sort_by, sort_dir=sort_dir)
    return PaginatedResponse(**data)


@router.get("/api/v1/admin/claims/{claim_id}", response_model=RecordResponse)
async def get_claim(claim_id: int, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    row = repo.get_claim(claim_id)
    if not row:
        raise HTTPException(status_code=404, detail="Claim not found")
    return RecordResponse(record=row)


@router.post("/api/v1/admin/claims", response_model=RecordResponse, status_code=201)
async def create_claim(payload: ClaimCreateRequest, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    try:
        row = repo.create_claim(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Create claim failed: {exc}") from exc
    return RecordResponse(record=row)


@router.patch("/api/v1/admin/claims/{claim_id}", response_model=RecordResponse)
async def patch_claim(claim_id: int, payload: ClaimPatchRequest, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    try:
        row = repo.patch_claim(claim_id, payload.model_dump(exclude_unset=True))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Update claim failed: {exc}") from exc
    if not row:
        raise HTTPException(status_code=404, detail="Claim not found")
    return RecordResponse(record=row)


@router.delete("/api/v1/admin/claims/{claim_id}", response_model=DeleteResponse)
async def delete_claim(claim_id: int, request: Request) -> DeleteResponse:
    repo = _admin_repo(request)
    deleted = repo.delete_claim(claim_id)
    return DeleteResponse(ok=True, deleted=deleted, message="Deleted" if deleted else "Claim not found")


# CHAT_SUMMARY CRUD
@router.get("/api/v1/admin/chat-summaries", response_model=PaginatedResponse)
async def list_chat_summaries(
    request: Request,
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_by: str | None = Query(default="updated_at"),
    sort_dir: str | None = Query(default="desc"),
) -> PaginatedResponse:
    repo = _admin_repo(request)
    data = repo.list_chat_summaries(search=search, page=page, page_size=page_size, sort_by=sort_by, sort_dir=sort_dir)
    return PaginatedResponse(**data)


@router.get("/api/v1/admin/chat-summaries/{cust_id}", response_model=RecordResponse)
async def get_chat_summary(cust_id: int, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    row = repo.get_chat_summary(cust_id)
    if not row:
        raise HTTPException(status_code=404, detail="Chat summary not found")
    return RecordResponse(record=row)


@router.post("/api/v1/admin/chat-summaries", response_model=RecordResponse, status_code=201)
async def create_chat_summary(payload: ChatSummaryCreateRequest, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    try:
        row = repo.create_chat_summary(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Create chat summary failed: {exc}") from exc
    return RecordResponse(record=row)


@router.patch("/api/v1/admin/chat-summaries/{cust_id}", response_model=RecordResponse)
async def patch_chat_summary(cust_id: int, payload: ChatSummaryPatchRequest, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    try:
        row = repo.patch_chat_summary(cust_id, payload.model_dump(exclude_unset=True))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Update chat summary failed: {exc}") from exc
    if not row:
        raise HTTPException(status_code=404, detail="Chat summary not found")
    return RecordResponse(record=row)


@router.delete("/api/v1/admin/chat-summaries/{cust_id}", response_model=DeleteResponse)
async def delete_chat_summary(cust_id: int, request: Request) -> DeleteResponse:
    repo = _admin_repo(request)
    deleted = repo.delete_chat_summary(cust_id)
    return DeleteResponse(ok=True, deleted=deleted, message="Deleted" if deleted else "Chat summary not found")


# CALLBACK CRUD (function-backed)
@router.get("/api/v1/admin/callbacks", response_model=PaginatedResponse)
async def list_callbacks(
    request: Request,
    status: str | None = Query(default=None),
    assigned_to: str | None = Query(default=None),
    due_before: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> PaginatedResponse:
    repo = _admin_repo(request)
    data = repo.list_callbacks_queue(
        status=status,
        assigned_to=assigned_to,
        due_before=due_before,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(**data)


@router.get("/api/v1/admin/callbacks/{callback_id}", response_model=RecordResponse)
async def get_callback(callback_id: int, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    row = repo.get_callback(callback_id)
    if not row:
        raise HTTPException(status_code=404, detail="Callback not found")
    return RecordResponse(record=row)


@router.post("/api/v1/admin/callbacks", response_model=RecordResponse, status_code=201)
async def create_callback(payload: CallbackCreateRequest, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    try:
        row = repo.create_callback(payload.model_dump(exclude_unset=False))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Create callback failed: {exc}") from exc
    return RecordResponse(record=row)


@router.patch("/api/v1/admin/callbacks/{callback_id}", response_model=RecordResponse)
async def patch_callback(callback_id: int, payload: CallbackPatchRequest, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    try:
        row = repo.patch_callback(callback_id, payload.model_dump(exclude_unset=True))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Update callback failed: {exc}") from exc
    if not row:
        raise HTTPException(status_code=404, detail="Callback not found")
    return RecordResponse(record=row)


@router.post("/api/v1/admin/callbacks/{callback_id}/attempt", response_model=RecordResponse)
async def mark_callback_attempt(callback_id: int, payload: CallbackAttemptRequest, request: Request) -> RecordResponse:
    repo = _admin_repo(request)
    try:
        row = repo.mark_callback_attempt(callback_id, payload.model_dump(exclude_unset=True))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Mark callback attempt failed: {exc}") from exc
    if not row:
        raise HTTPException(status_code=404, detail="Callback not found")
    return RecordResponse(record=row)


@router.delete("/api/v1/admin/callbacks/{callback_id}", response_model=DeleteResponse)
async def delete_callback(callback_id: int, request: Request) -> DeleteResponse:
    repo = _admin_repo(request)
    deleted = repo.delete_callback(callback_id)
    return DeleteResponse(ok=True, deleted=deleted, message="Deleted" if deleted else "Callback not found")

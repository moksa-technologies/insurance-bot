from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.application.orchestration.multi_agent_orchestrator import MultiAgentOrchestrator
from app.application.use_cases.chat_use_case import ChatUseCase
from app.config import get_settings
from app.infrastructure.db.admin_crud_repository import AdminCrudRepository
from app.infrastructure.db.chat_history_repository import ChatHistoryRepository
from app.infrastructure.db.db_bootstrap import DatabaseBootstrapper
from app.infrastructure.db.function_gateway import CustomerFunctionGateway
from app.infrastructure.db.function_verifier import DatabaseFunctionVerifier
from app.infrastructure.db.postgres_client import PostgresClient
from app.infrastructure.external.excel_search_service import ExcelSearchService
from app.infrastructure.external.transcript_store import TranscriptStore
from app.infrastructure.llm.openai_clients import OpenAIClients
from app.infrastructure.retrieval.pdf_rag_service import PDFRAGService
from app.infrastructure.tools.assistance_tools import AssistanceTools
from app.infrastructure.tools.customer_tools import CustomerTools
from app.infrastructure.tools.rag_tool import RagTool
from app.infrastructure.tools.tool_executor import ToolExecutor
from app.interfaces.api.router import router as api_router
from app.interfaces.api.status_provider import StatusProvider
from app.interfaces.ws.router import router as ws_router


settings = get_settings()


def configure_logging() -> None:
    settings.app_log_path.parent.mkdir(parents=True, exist_ok=True)
    level_name = (settings.log_level or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handlers: list[logging.Handler] = [
        logging.StreamHandler(),
        RotatingFileHandler(
            filename=str(settings.app_log_path),
            maxBytes=5_000_000,
            backupCount=5,
            encoding="utf-8",
        ),
    ]
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=handlers,
        force=True,
    )


configure_logging()
LOGGER = logging.getLogger(__name__)
app = FastAPI(title=settings.app_name)


@app.on_event("startup")
async def startup() -> None:
    db_client = PostgresClient(settings)
    try:
        db_client.open()

        bootstrapper = DatabaseBootstrapper(settings, db_client)
        if settings.db_auto_bootstrap:
            bootstrapper.apply(include_seed=settings.db_bootstrap_seed)

        function_verifier = DatabaseFunctionVerifier(db_client)
        function_verifier.verify_or_raise()

        history_repo = ChatHistoryRepository(settings, db_client)
        history_repo.ensure_tables()
        admin_repo = AdminCrudRepository(db_client)

        excel_service = ExcelSearchService(settings.hospital_path, settings.garage_path)
        transcript_store = TranscriptStore(settings.transcript_root)

        clients = OpenAIClients(settings)
        rag_service = PDFRAGService(settings, embedding_client=clients.embedding_client)
        rag_service.build_index(force=False)

        customer_gateway = CustomerFunctionGateway(db_client)
        customer_tools = CustomerTools(customer_gateway)
        assistance_tools = AssistanceTools(excel_service)
        rag_tool = RagTool(rag_service)
        tool_executor = ToolExecutor(customer_tools, assistance_tools, rag_tool)

        orchestrator = MultiAgentOrchestrator(
            settings=settings,
            tool_executor=tool_executor,
            history_repo=history_repo,
            llm_client=clients.llm_client,
            model=settings.llm_model,
            transcript_store=transcript_store,
        )

        chat_use_case = ChatUseCase(orchestrator)
        status_provider = StatusProvider(function_verifier=function_verifier, tool_executor=tool_executor)

        app.state.settings = settings
        app.state.db_client = db_client
        app.state.excel_service = excel_service
        app.state.rag_service = rag_service
        app.state.transcript_store = transcript_store
        app.state.orchestrator = orchestrator
        app.state.chat_use_case = chat_use_case
        app.state.status_provider = status_provider
        app.state.admin_repo = admin_repo

        LOGGER.info("Startup complete")
    except Exception:
        db_client.close()
        raise


@app.on_event("shutdown")
async def shutdown() -> None:
    orchestrator: MultiAgentOrchestrator = app.state.orchestrator
    await orchestrator.close()
    app.state.db_client.close()


app.include_router(api_router)
app.include_router(ws_router)

ui_dir = Path(__file__).resolve().parent / "interfaces" / "ui"
app.mount("/static", StaticFiles(directory=ui_dir), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(ui_dir / "index.html")

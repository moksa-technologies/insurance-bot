from __future__ import annotations

from app.application.orchestration.multi_agent_orchestrator import MultiAgentOrchestrator
from app.interfaces.api.schemas import ChatRequest, ChatResponse


class ChatUseCase:
    def __init__(self, orchestrator: MultiAgentOrchestrator) -> None:
        self.orchestrator = orchestrator

    async def execute(self, request: ChatRequest) -> ChatResponse:
        return await self.orchestrator.handle_chat(request)

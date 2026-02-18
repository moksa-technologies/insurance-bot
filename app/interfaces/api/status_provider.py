from __future__ import annotations

from dataclasses import dataclass

from app.infrastructure.db.function_verifier import DatabaseFunctionVerifier
from app.infrastructure.tools.tool_executor import ToolExecutor
from app.interfaces.api.schemas import HealthResponse, ToolSelfTestResponse


@dataclass
class StatusProvider:
    function_verifier: DatabaseFunctionVerifier
    tool_executor: ToolExecutor

    def health(self) -> HealthResponse:
        fn_checks = self.function_verifier.verify()
        deps = {signature: ("ok" if ok else "missing") for signature, ok in fn_checks.items()}
        status = "ok" if all(fn_checks.values()) else "degraded"
        return HealthResponse(status=status, dependencies=deps)

    def self_test(self) -> ToolSelfTestResponse:
        checks = {}
        checks.update({f"db::{k}": v for k, v in self.function_verifier.verify().items()})
        checks.update({f"tool::{k}": v for k, v in self.tool_executor.self_test().items()})
        return ToolSelfTestResponse(ok=all(checks.values()), checks=checks)

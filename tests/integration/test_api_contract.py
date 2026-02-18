from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.interfaces.api.router import router as api_router
from app.interfaces.api.schemas import ChatResponse, DataReferences
from app.interfaces.ws.router import router as ws_router


class StubUseCase:
    async def execute(self, request):
        return ChatResponse(
            session_uuid=request.session_uuid,
            language="en",
            response="stubbed",
            follow_up_needed=False,
            follow_up_query=None,
            intent="greeting",
            data_references=DataReferences(database_function=None, external_source=None),
        )


class StubStatusProvider:
    def health(self):
        return {
            "status": "ok",
            "dependencies": {"db": "ok"},
        }

    def self_test(self):
        return {
            "ok": True,
            "checks": {"db::ok": True},
        }


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.state.chat_use_case = StubUseCase()
    app.state.status_provider = StubStatusProvider()
    app.state.excel_service = type("Excel", (), {"refresh": lambda self: None})()
    app.state.rag_service = type("Rag", (), {"build_index": lambda self, force=False: {"status": "ok"}})()
    app.include_router(api_router)
    app.include_router(ws_router)
    return app


def test_rest_contract() -> None:
    app = _build_test_app()
    with TestClient(app) as client:
        payload = {
            "ani": "9000000001",
            "input_message": "hello",
            "session_uuid": "session-1",
            "channel": "web",
        }
        resp = client.post("/api/v1/chat", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_uuid"] == "session-1"
        assert data["response"] == "stubbed"


def test_ws_contract() -> None:
    app = _build_test_app()
    with TestClient(app) as client:
        with client.websocket_connect("/ws/chat") as ws:
            ws.send_json(
                {
                    "ani": "9000000001",
                    "input_message": "hello",
                    "session_uuid": "session-2",
                    "channel": "web",
                }
            )
            data = ws.receive_json()
            assert data["session_uuid"] == "session-2"
            assert data["response"] == "stubbed"

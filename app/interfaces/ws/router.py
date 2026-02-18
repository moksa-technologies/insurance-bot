from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.interfaces.api.schemas import ChatRequest


router = APIRouter()


@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            try:
                request_obj = ChatRequest(**payload)
            except ValidationError as exc:
                await websocket.send_json({"type": "error", "detail": exc.errors()})
                continue

            use_case = websocket.app.state.chat_use_case
            response = await use_case.execute(request_obj)
            await websocket.send_json(response.model_dump())
    except WebSocketDisconnect:
        return

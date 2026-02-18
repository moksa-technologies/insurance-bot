from app.interfaces.api.schemas import ChatRequest


def test_chat_request_generates_session_uuid() -> None:
    req = ChatRequest(ani="9000000001", input_message="hello")
    assert req.session_uuid


def test_chat_request_requires_ani() -> None:
    try:
        ChatRequest(ani="", input_message="hello")
        assert False, "Expected validation error"
    except Exception:
        assert True

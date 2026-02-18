from app.application.orchestration.multi_agent_orchestrator import MultiAgentOrchestrator


def test_follow_up_only_payload_is_valid() -> None:
    payload = {
        "intent": "accident_help",
        "language": "en",
        "response": None,
        "follow_up_needed": True,
        "follow_up_query": "Are you safe right now?",
        "tool_call": None,
    }

    ok, result = MultiAgentOrchestrator._validate_agent_payload(payload)

    assert ok is True
    assert isinstance(result, dict)
    assert result["response"] == "Are you safe right now?"
    assert result["follow_up_needed"] is True


def test_follow_up_needed_string_is_coerced() -> None:
    payload = {
        "intent": "accident_help",
        "language": "en",
        "response": None,
        "follow_up_needed": "true",
        "follow_up_query": "Do you need medical assistance?",
        "tool_call": None,
    }

    ok, result = MultiAgentOrchestrator._validate_agent_payload(payload)

    assert ok is True
    assert isinstance(result, dict)
    assert result["follow_up_needed"] is True
    assert result["response"] == "Do you need medical assistance?"


def test_tool_name_alias_is_normalized() -> None:
    payload = {
        "intent": "create_claim",
        "language": "en",
        "response": None,
        "follow_up_needed": False,
        "follow_up_query": None,
        "tool_call": {"tool_name": "create_claim_by_ani", "args": {"vehicle_no": "TS09AB1234"}},
    }

    ok, result = MultiAgentOrchestrator._validate_agent_payload(payload)

    assert ok is True
    assert isinstance(result, dict)
    assert result["tool_call"]["tool_name"] == "create_claim_tool"


def test_unknown_tool_is_dropped_when_response_exists() -> None:
    payload = {
        "intent": "misc_query",
        "language": "en",
        "response": "I can help with that.",
        "follow_up_needed": False,
        "follow_up_query": None,
        "tool_call": {"tool_name": "some_custom_tool", "args": {}},
    }

    ok, result = MultiAgentOrchestrator._validate_agent_payload(payload)

    assert ok is True
    assert isinstance(result, dict)
    assert result["tool_call"] is None
    assert result["response"] == "I can help with that."


def test_callback_tool_name_alias_is_normalized() -> None:
    payload = {
        "intent": "schedule_callback",
        "language": "en",
        "response": None,
        "follow_up_needed": False,
        "follow_up_query": None,
        "tool_call": {"tool_name": "callback_create", "args": {"priority": 3}},
    }

    ok, result = MultiAgentOrchestrator._validate_agent_payload(payload)

    assert ok is True
    assert isinstance(result, dict)
    assert result["tool_call"]["tool_name"] == "callback_tool"


def test_customer_create_tool_name_alias_is_normalized() -> None:
    payload = {
        "intent": "register_customer",
        "language": "en",
        "response": None,
        "follow_up_needed": False,
        "follow_up_query": None,
        "tool_call": {"tool_name": "customer_create", "args": {"cust_id": 2001, "name": "John"}},
    }

    ok, result = MultiAgentOrchestrator._validate_agent_payload(payload)

    assert ok is True
    assert isinstance(result, dict)
    assert result["tool_call"]["tool_name"] == "customer_create_tool"

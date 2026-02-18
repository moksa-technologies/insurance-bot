import re

from app.infrastructure.db.function_gateway import CustomerFunctionGateway


def test_coerce_timestamptz_accepts_time_only_am_pm() -> None:
    output = CustomerFunctionGateway._coerce_timestamptz("9am")
    assert isinstance(output, str)
    assert re.search(r"T09:00:00\+05:30$", output) is not None


def test_coerce_timestamptz_accepts_current_phrase() -> None:
    output = CustomerFunctionGateway._coerce_timestamptz("current date/time in Asia/Kolkata time")
    assert isinstance(output, str)
    assert output.endswith("+05:30")


def test_coerce_timestamptz_preserves_iso_offset() -> None:
    output = CustomerFunctionGateway._coerce_timestamptz("2026-02-17T10:30:00+05:30")
    assert output == "2026-02-17T10:30:00+05:30"

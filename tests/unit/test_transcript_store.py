import json
from pathlib import Path

from app.infrastructure.external.transcript_store import TranscriptStore


def test_transcript_store_appends_json_turns(tmp_path: Path) -> None:
    store = TranscriptStore(tmp_path / "transcripts")
    store.append_turn(
        ani="9000000001",
        session_uuid="session-1",
        turn={"input_message": "hi", "response": {"text": "hello"}},
    )
    store.append_turn(
        ani="9000000001",
        session_uuid="session-1",
        turn={"input_message": "need help", "response": {"text": "sure"}},
    )

    output_file = tmp_path / "transcripts" / "9000000001" / "session-1.json"
    assert output_file.exists()

    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["input_message"] == "hi"
    assert data[1]["response"]["text"] == "sure"

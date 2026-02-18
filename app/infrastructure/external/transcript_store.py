from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger(__name__)


class TranscriptStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _sanitize(value: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip())
        return cleaned or "unknown"

    def _path_for(self, ani: str, session_uuid: str) -> Path:
        safe_ani = self._sanitize(ani)
        safe_session = self._sanitize(session_uuid)
        folder = self.root / safe_ani
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{safe_session}.json"

    def append_turn(self, ani: str, session_uuid: str, turn: dict[str, Any]) -> None:
        path = self._path_for(ani=ani, session_uuid=session_uuid)
        history: list[dict[str, Any]] = []
        if path.exists():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(raw, list):
                    history = raw
            except Exception:
                LOGGER.exception("Transcript read failed path=%s", path)
                history = []
        history.append(turn)
        try:
            path.write_text(
                json.dumps(history, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
        except Exception:
            LOGGER.exception("Transcript write failed path=%s", path)

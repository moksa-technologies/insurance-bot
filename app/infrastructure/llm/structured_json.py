from __future__ import annotations

import json
from typing import Any, Callable


ValidatorFn = Callable[[dict[str, Any]], tuple[bool, dict[str, Any] | str]]


class StructuredJSONClient:
    def __init__(self, llm_client: Any, model: str, max_retries: int = 2) -> None:
        self.llm_client = llm_client
        self.model = model
        self.max_retries = max_retries

    @staticmethod
    def extract_json(text: str) -> dict[str, Any]:
        cleaned = (text or "").strip()
        if not cleaned:
            return {}

        if cleaned.startswith("```"):
            parts = [part.strip() for part in cleaned.split("```") if part.strip()]
            for part in parts:
                candidate = part
                if candidate.lower().startswith("json"):
                    candidate = candidate[4:].strip()
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue
            return {}

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {}

    def call_json(
        self,
        system_prompt: str,
        payload: dict[str, Any],
        validator: ValidatorFn,
        fallback: dict[str, Any],
    ) -> dict[str, Any]:
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False, default=str)},
        ]
        last_error = "unknown_schema_error"

        for _ in range(self.max_retries + 1):
            try:
                resp = self.llm_client.chat.completions.create(
                    model=self.model,
                    temperature=0,
                    messages=messages,
                )
                raw_content = resp.choices[0].message.content or ""
            except Exception as exc:
                last_error = f"llm_call_failed:{type(exc).__name__}"
                raw_content = ""

            parsed = self.extract_json(raw_content)
            ok, result = validator(parsed)
            if ok:
                return result if isinstance(result, dict) else fallback

            if isinstance(result, str):
                last_error = result
            else:
                last_error = "invalid_payload"

            messages.append({"role": "assistant", "content": raw_content or "<empty>"})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Your previous response did not satisfy schema validation. "
                        f"Validation error: {last_error}. "
                        "Return only valid JSON matching the required schema."
                    ),
                }
            )

        return fallback

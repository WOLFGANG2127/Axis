"""Robust extraction for JSON emitted inside or outside markdown fences."""

from __future__ import annotations

import json
import re
from typing import Any

FENCE_RE = re.compile(r"^\s*```(?:json|JSON)?\s*|\s*```\s*$")
TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")


def _strip_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = FENCE_RE.sub("", text).strip()
    return text


def extract_json(raw: str | dict[str, Any]) -> dict[str, Any]:
    """Return the outermost JSON object from an LLM response string."""

    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("empty JSON response")

    text = _strip_fences(raw)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object found")
    candidate = text[start : end + 1]
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError:
        payload = json.loads(TRAILING_COMMA_RE.sub(r"\1", candidate))
    if not isinstance(payload, dict):
        raise ValueError("JSON payload must be an object")
    return payload

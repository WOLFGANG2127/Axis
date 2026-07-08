"""Role-based LLM router for AXIS analyst and verifier calls."""

from __future__ import annotations

import json
from typing import Any

from src.graph.state import AxisState
from src.llm.distributed_lock import acquire, release
from src.llm.json_extractor import extract_json

ANALYST_PRIMARY_MODEL = "gemini/gemini-2.5-flash"
ANALYST_FALLBACK_MODEL = "zai/glm-4.5-air"
VERIFIER_MODEL = "groq/llama-3.3-70b-versatile"


def _safe_state_payload(state: AxisState) -> str:
    payload = state.model_dump(mode="json", exclude_none=True)
    return json.dumps(payload, ensure_ascii=False, default=str)


def _messages(role: str, state: AxisState) -> list[dict[str, str]]:
    if role == "analyst":
        system = (
            "You are AXIS Agent One. Read deterministic state only; do not "
            "invent data. Return one compact JSON object with keys: "
            "view, confidence, reasons, degraded."
        )
    elif role == "verifier":
        system = (
            "You are AXIS Agent Two verifier. Return JSON only. The key "
            "decision must be PROCEED or BLOCK. Block if evidence is missing, "
            "stale, contradictory, low EV, or risk is unclear."
        )
    else:
        raise ValueError("role must be analyst or verifier")
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": _safe_state_payload(state)},
    ]


def _content(response: Any) -> str:
    choice = response.choices[0] if hasattr(response, "choices") else response["choices"][0]
    message = choice.message if hasattr(choice, "message") else choice["message"]
    content = message.get("content") if isinstance(message, dict) else message.content
    if not content:
        raise ValueError("LLM returned empty content")
    return str(content)


async def _acompletion(model: str, api_key: str, messages: list[dict[str, str]]) -> Any:
    from litellm import acompletion

    return await acompletion(
        model=model,
        messages=messages,
        api_key=api_key,
        temperature=0,
        num_retries=0,
        stream=False,
    )


def _provider_payload(raw: str, provider: str, role: str) -> dict[str, Any]:
    try:
        payload = extract_json(raw)
    except ValueError:
        if role == "verifier":
            payload = {
                "decision": "BLOCK",
                "reason": "VERIFIER_JSON_PARSE_FAILED",
                "raw": raw,
            }
        else:
            payload = {"raw": raw, "degraded": False}
    payload.setdefault("provider", provider)
    return payload


async def call_llm_router(role: str, state: AxisState) -> dict[str, Any]:
    """Call Gemini→Z.ai for analyst and Groq for verifier.

    Every LiteLLM call is non-streaming and uses ``num_retries=0`` exactly.
    """

    normalized = role.strip().lower()
    messages = _messages(normalized, state)
    from src.config.settings import settings

    if normalized == "analyst":
        try:
            response = await _acompletion(ANALYST_PRIMARY_MODEL, settings.GOOGLE_API_KEY, messages)
            return _provider_payload(_content(response), "gemini", normalized)
        except Exception as primary_error:
            acquired = await acquire("zai_api_call", ttl_seconds=60)
            try:
                if not acquired:
                    raise RuntimeError("zai_api_call lock unavailable") from primary_error
                response = await _acompletion(
                    ANALYST_FALLBACK_MODEL,
                    settings.ZAI_API_KEY,
                    messages,
                )
                payload = _provider_payload(_content(response), "zai", normalized)
                payload.setdefault("fallback_from", "gemini")
                return payload
            finally:
                await release("zai_api_call")

    if normalized == "verifier":
        acquired = await acquire("groq_agent_two", ttl_seconds=60)
        try:
            if not acquired:
                return {
                    "decision": "BLOCK",
                    "reason": "GROQ_VERIFIER_LOCK_UNAVAILABLE",
                    "synthetic": True,
                }
            response = await _acompletion(VERIFIER_MODEL, settings.GROQ_API_KEY, messages)
            payload = _provider_payload(_content(response), "groq", normalized)
            payload.setdefault("decision", "BLOCK")
            return payload
        finally:
            await release("groq_agent_two")

    raise ValueError("role must be analyst or verifier")

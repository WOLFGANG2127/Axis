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


class BudgetExhaustedError(RuntimeError):
    """Raised when the daily LLM budget firewall is breached."""


async def _acompletion(model: str, api_key: str, messages: list[dict[str, str]]) -> Any:
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from litellm import acompletion, completion_cost
    from src.database.supabase import get_supabase_client
    from src.config.settings import settings
    
    IST = ZoneInfo("Asia/Kolkata")
    today = datetime.now(IST).date().isoformat()
    db = get_supabase_client()
    
    # Phase A: Pre-Flight Budget Check
    res = db.table("llm_cost_guardrail").select("cumulative_spend_usd, hard_cap_usd").eq("trading_date", today).execute()
    cap = 2.0
    if res.data:
        row = res.data[0]
        spend = float(row.get("cumulative_spend_usd", 0.0))
        cap = float(row.get("hard_cap_usd", 2.0))
        if spend >= cap:
            msg = f"AXIS ALERT: Daily LLM budget of ${cap:.2f} exhausted (Spend: ${spend:.2f}). Pipeline locked into safe mode."
            try:
                from src.delivery.telegram_formatter import send_telegram_alert
                send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, msg)
            except Exception:
                import logging
                logging.getLogger("axis.llm").exception("Failed to send budget exhausted alert")
            raise BudgetExhaustedError(msg)

    # Phase B: Execute the actual LLM call
    response = await acompletion(
        model=model,
        messages=messages,
        api_key=api_key,
        temperature=0,
        num_retries=0,
        stream=False,
    )
    
    # Phase C: Post-Flight Accounting
    try:
        cost = float(completion_cost(completion_response=response) or 0.0)
    except Exception:
        cost = 0.0
        
    if cost > 0:
        try:
            rpc_res = db.rpc("increment_llm_spend", {
                "p_trading_date": today,
                "p_cost_usd": cost,
                "p_hard_cap_usd": cap
            }).execute()
            
            if rpc_res.data:
                new_total = float(rpc_res.data)
                if new_total >= (cap * 0.90):
                    msg = f"AXIS WARNING: Daily LLM budget nearly depleted! Spend: ${new_total:.2f} / ${cap:.2f}"
                    from src.delivery.telegram_formatter import send_telegram_alert
                    send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, msg)
        except Exception:
            import logging
            logging.getLogger("axis.llm").exception("Failed to update or alert LLM spend")
            
    return response


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

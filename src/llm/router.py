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



# D-T6 PROVENANCE: Analyst system prompt distilled from the following Appendix-F source files
# (Agent 5 — spot-check these rules trace back to these exact files):
#   1. data/knowledge/AXIS_Knowledge_Base.md          — §1 patterns P1–P22, §4 rules IR1–IR24
#   2. data/knowledge/AXIS_Knowledge_Base_Supplement.md — §1 patterns P23–P37
#   3. data/knowledge/AXIS_Knowledge_Base_v5_final_consolidation.md — §1 resolved gaps,
#      §3 cross-part consistency check, proposed Agent-1 decision procedure
#   4. data/knowledge/NIFTY JUNE 23 Analysis.md      — June 23 2026 real cascade example
# Hard cap: 2,500 words. If adding rules would breach the cap, delete oldest/least
# load-bearing rules first (bottom of block) before adding new ones.
_ANALYST_SYSTEM_PROMPT = """\
You are AXIS Agent One — the Analyst LLM. You read only the deterministic state \
provided in the user message. You do not fetch data, call APIs, or invent values. \
Return exactly one compact JSON object with keys: view, confidence, reasons, degraded.

=== REGIME IDENTIFICATION (apply before everything else) ===
RULE-1 (GEX IS THE MASTER SWITCH): Read Net GEX sign first — before PCR, before Max Pain, \
before any other signal. Negative GEX means dealers are short gamma; every further decline \
is mechanically self-reinforcing. Positive GEX means dealers stabilize range. Wrong GEX \
read invalidates all downstream analysis.

RULE-2 (PCR TRAP IN NEGATIVE GEX): If GEX is negative AND PCR is rising simultaneously, \
do NOT interpret this as bullish. Rising PCR with negative GEX = more put delta-hedge \
obligations loading into the system = cascade fuel, not a floor. This is the most common \
retail misread in the real data (June 22–23 2026: PCR 1.18→1.21 in negative GEX = fuel, \
confirmed cascade next session).

RULE-3 (MAX PAIN VALIDITY): Max Pain is a valid pinning target ONLY when GEX is positive. \
When GEX is negative, dealers fight the pin — ignore Max Pain, use VIX expected-move \
target and GEX Fibonacci levels instead. (June 23 2026: Max Pain failed by 211 pts \
in negative GEX — textbook example.)

RULE-4 (GAMMA FLIP LEVEL): Identify the spot level where net GEX crosses zero. \
Above it: slow, dampened moves. Below it: violent, self-reinforcing cascade. \
When state shows price below gamma flip: treat as confirmed cascade regime. \
(June 23 2026 Gamma Flip ≈24,050; below it NIFTY fell −213 pts.)

RULE-5 (VIX STRUCTURAL LEAD-TIME): A CHoCH (Change of Character) on VIX's own \
15-min chart is a persistent multi-day caution flag — keep it active until the VIX \
structure resolves. Do NOT fold it into a same-day score. \
(June 19 VIX CHoCH → June 23 explosion, 4-day lead time.)

=== SIGNAL HIERARCHY (execute in this fixed order) ===
STEP-1: GEX sign → establishes regime (positive = range/pin, negative = cascade).
STEP-2: GEX vs Gamma Flip Level → confirms whether cascade mode is active.
STEP-3: VIX standing flag (from state.market_context) → if True, reduce confidence on \
        any bullish read, even in positive GEX.
STEP-4: PCR — interpret relative to GEX sign per RULE-2.
STEP-5: Max Pain — valid only if GEX positive (RULE-3).
STEP-6: OI vs LTP divergence → rising OI + falling LTP at a strike = pure selling/writing \
        at that strike, regardless of PCR direction. (June 29 2026: 23,950 CE OI +851%, \
        LTP −46.80% → unambiguous institutional selling.)
STEP-7: Wyckoff structure (if state.structure_confirmed is available) → Spring/UTAD/SOS/SOW.
STEP-8: Volume Profile position → Order flow signals are only tradeable when price is AT a \
        marked boundary (VAH/VAL/VPOC/LVN). Mid-range order flow is noise.

=== EXPIRY-DAY PROTOCOL ===
EXPIRY-1: If is_expiry_day AND GEX is NEGATIVE at open → follow first directional break, \
           buy OTM option in break direction, do NOT sell premium. Cascade risk is high.
EXPIRY-2: If is_expiry_day AND GEX is POSITIVE at open → sell OTM premium, range trade \
           around Max Pain. Cascade logic does not apply.
EXPIRY-3: If is_expiry_day AND time >= 14:00 IST → hard block, no new entries.
EXPIRY-4: If overnight ATM OI increased >50% from prior session → elevated volatility day, \
           do not sell naked premium.

=== INSTITUTIONAL DETECTION RULES ===
INST-1 (OI RISING + LTP FALLING = WRITING): If Open Interest at any strike rises AND its \
premium falls simultaneously → institutions are net short that strike. This overrides PCR.
INST-2 (WYCKOFF PHASE DETECTION): Confirm phase sequence: Accumulation = \
PS→SC→AR→ST (Phase A) → sideways range (Phase B) → Spring shakeout (Phase C) → \
SOS breakout (Phase D) → Phase E trend. Distribution mirror of the above. \
A signal mid-sequence (Spring only, no SOS) carries lower confidence.
INST-3 (DELTA DIVERGENCE TRAP): Positive Delta + bearish candle close = institutional \
absorption (large passive sell wall absorbing aggressive buyers). Confirms Wyckoff \
Absorption; trade the short side.
INST-4 (VPOC MIGRATION): VPOC moves + price immediately accelerates = continuation. \
VPOC moves + price stalls sideways = Change of Character warning, reduce positions.
INST-5 (SHORTENING OF THRUST): 3+ consecutive impulse waves each shorter than prior: \
with high volume = institutional blocking; with low volume = participation exhaustion. \
Both signal impending reversal.

=== VOLUME PROFILE RULES ===
VP-1 (VALUE AREA RE-ENTRY): Price breaks out of Value Area, then closes BACK inside \
on a wide-range candle → high probability of rotating to the OPPOSITE VA extreme. \
VAH re-entry rejected → target VAL. VAL re-entry rejected → target VAH.
VP-2 (HVN GRAVITY): Price gravitates toward HVN (High Volume Node). Use for take-profit \
targets and premium-selling strikes.
VP-3 (LVN RAPID TRANSIT): LVN (Low Volume Node) provides no support — price moves \
through it violently. Ideal directional option entry zone (Delta + Vega gain simultaneously).
VP-4 (ORDER FLOW BOUNDARY REQUIREMENT): Order flow signals (exhaustion, absorption, \
delta divergence) are ONLY valid when price is AT a Volume Profile boundary. \
Signals in mid-range are noise. This is the single most critical caveat in the Order Flow layer.

=== RISK AND EXIT RULES ===
RISK-1 (NEVER HOLD WEEKLY OPTIONS OVERNIGHT): Theta decay on ATM weekly = 15–20%/day \
in final week. Overnight holds require monthly expiry options only.
RISK-2 (TIME STOP): If 70% of holding period has elapsed without the expected move, \
exit regardless of P&L.
RISK-3 (STRADDLE RANGE BREACH): If price exceeds 60% of straddle expected range, \
apply "Would I Do It Now?" test. If no → close.
RISK-4 (HARD LOSS STOP): If position loss reaches 150–200% of initial credit received, \
exit unconditionally.
RISK-5 (GREEK DRIFT): Net delta exceeding ±40: re-hedge. Daily theta exceeding 15% of \
remaining premium: re-evaluate viability. VIX intraday spike >15% while short Vega: buy a wing.
RISK-6 (STT TRAP): Square off any ITM option before 3:00 PM on expiry day. Letting ITM \
options expire triggers 0.125% STT vs. 0.0625% on normal sale.
RISK-7 (WIN-RATE TRIGGER): Win rate below 50% for 2 consecutive months: cut size 50% \
and switch to defined-risk structures only until recovery.

=== CAPITAL SIZING ===
SIZE-1 (LOT SIZE): NIFTY lot size = 65. BANKNIFTY lot size = 30. \
Use these numbers for all position sizing. Older sources showing 75 or 25 are outdated.
SIZE-2 (KELLY CAP): Use half-Kelly, capped at 2% of capital per trade. Take the smaller \
of the two. kelly_fraction = p - q/b where b = avg_gain/avg_loss.
SIZE-3 (EV MINIMUM): expected_value = (p × gain) - (q × loss) - transaction_cost. \
Only proceed if EV > 0 after transaction costs.

=== CONFIDENCE OUTPUT RULES ===
CONF-1: Return HIGH confidence only if GEX regime + Volume Profile boundary + \
Wyckoff sequence + VIX structure all agree.
CONF-2: Return MEDIUM confidence if 2–3 signals agree.
CONF-3: Return LOW confidence if only 1 signal agrees or signals conflict.
CONF-4: Return degraded=true if any critical input (GEX, spot, structure_confirmed) \
is missing or stale.
CONF-5: Near RBI/Budget/FOMC dates: downgrade confidence one level from whatever the \
signals otherwise warrant — IV is systematically elevated; event risk overrides pattern reads.

=== HARD CONSTRAINTS ===
HARD-1: Read deterministic state only. Do not invent data values.
HARD-2: GEX cannot be exactly 0.0 — that is a data-quality failure, not a neutral reading. \
Return degraded=true if GEX == 0.0.
HARD-3: direction_score in the 2–4 dead zone means no trade signal can be confirmed. \
Return view="neutral", confidence="LOW", degraded=false.
HARD-4: AXIS has no order-placement capability. Output is informational only.
HARD-5: Return exactly one JSON object: {view, confidence, reasons, degraded}. \
No prose, no markdown, no extra keys.
"""


def _messages(role: str, state: AxisState) -> list[dict[str, str]]:
    if role == "analyst":
        system = _ANALYST_SYSTEM_PROMPT
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

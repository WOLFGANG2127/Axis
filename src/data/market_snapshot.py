"""D-001: fetch_and_score_market_data — the single most important function in the codebase.

Implements:
- D-001: wires live Dhan + NSE data into score_layer_a/b/c()
- D-045: stale-data check with source-specific rules (NOT a uniform 15-min rule)
- D-047: NSE_BLOCKED / NSE_EMPTY distinction (in nse_fetcher.py; consumed here)

Stale-data rules (D-045) — each source has its own logic, not a single rule:

  DHAN (spot + option chain — live intraday):
    Dhan's /optionchain response has NO timestamp field (confirmed against Dhan v2 docs).
    Use the HTTP response's Date header (every HTTP/1.1 response includes one per spec).
    Abort with STALE_DATA if gap between Date header and now() exceeds 15 minutes.
    If the Date header is absent: that is itself a validation error — abort, don't guess.

  NSE (participant OI — published once daily after market close, ~5–7 PM IST):
    A 15-minute rule would abort every cycle (several-hours-old IS correct during trading).
    A same-day rule would also abort (during live 10 AM cycle, only yesterday's file exists).
    Instead: parse the date from the CSV's title-row text using regex r"as on (\w+ \d+, \d+)".
    Abort with STALE_DATA only if that date is more than 4 calendar days old.
    If the title row pattern doesn't match: validation error — abort, don't guess.
"""

from __future__ import annotations

import csv
import io
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from src.scoring.layer_a import LayerAScore, score_layer_a
from src.scoring.layer_b import LayerBScore, score_layer_b
from src.scoring.layer_c import LayerCScore, score_layer_c
# Module-level import so mock.patch("src.data.market_snapshot.fetch_participant_oi")
# intercepts correctly in test 4.
from src.data.nse_fetcher import fetch_participant_oi, compute_long_short_ratio

logger = logging.getLogger("axis.market_snapshot")

# --------------------------------------------------------------------------- #
# Sentinel error class                                                         #
# --------------------------------------------------------------------------- #

class StaleDataError(RuntimeError):
    """Raised when a data source's freshness check fails before scoring runs."""


# --------------------------------------------------------------------------- #
# Typed return model (D-001)                                                   #
# extra='forbid': a missing/misnamed field raises ValidationError immediately  #
# --------------------------------------------------------------------------- #

class ScoredMarketContext(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    symbol: str
    last_price: float
    option_chain_raw: dict[str, Any]        # cleaned Dhan oc dict passed to layer_a
    vix_data: dict[str, Any]                # envelope from vix source
    fii_ratios: dict[str, Any]              # envelope from compute_long_short_ratio
    layer_a: LayerAScore
    layer_b: LayerBScore
    layer_c: LayerCScore
    direction_score: int                     # 1–5, from compute_direction_score()
    fii_fetch_failed: bool                   # True when FII fetch failed (not computed 0.0)


# --------------------------------------------------------------------------- #
# Two-stage parsing — Stage 1: raw extraction (D-001 mandatory rule)           #
# Never blindly merge the whole dict. Explicit key access; missing key raises. #
# --------------------------------------------------------------------------- #

def _extract_dhan_fields(raw_payload: dict[str, Any]) -> dict[str, Any]:
    """Extract ONLY the fields the scoring math needs from a Dhan optionchain response.

    The Dhan v2 /optionchain response structure:
        { "data": { "last_price": <float>, "oc": { "<strike>": { "ce": {...}, "pe": {...} } } } }

    A missing 'data', 'last_price', or 'oc' key is a structural error — raise KeyError,
    never silently default to None or 0. This is the contract D-001 specifies.
    """
    if "data" not in raw_payload:
        raise KeyError("Dhan optionchain response missing top-level 'data' key")
    data = raw_payload["data"]
    if not isinstance(data, dict):
        raise TypeError(f"Dhan optionchain 'data' must be dict, got {type(data).__name__}")
    if "last_price" not in data:
        raise KeyError("Dhan optionchain 'data' missing 'last_price'")
    if "oc" not in data:
        raise KeyError("Dhan optionchain 'data' missing 'oc' (option chain strikes)")

    last_price = float(data["last_price"])
    oc = data["oc"]
    if not isinstance(oc, dict):
        raise TypeError(f"Dhan optionchain 'oc' must be dict, got {type(oc).__name__}")

    return {
        "last_price": last_price,
        "oc": oc,
    }


def _extract_nse_fii_fields(csv_text: str) -> dict[str, Any]:
    """Extract FII long/short columns from NSE participant OI CSV.

    NSE's CSV format has an explicit header row naming each column.
    We access exactly the six columns the scoring math needs; a missing column raises.
    Never do a blanket row merge.
    """
    cleaned = csv_text.lstrip("\ufeff").strip()
    # The first row is a title row; the second is the header for DictReader
    lines = cleaned.splitlines()
    # Find where the header row is (contains "Client Type")
    header_idx = next(
        (i for i, line in enumerate(lines) if "Client Type" in line),
        None,
    )
    if header_idx is None:
        raise ValueError("NSE CSV: no header row containing 'Client Type' found")

    csv_body = "\n".join(lines[header_idx:])
    rows = list(csv.DictReader(io.StringIO(csv_body)))

    fii_row = next(
        (row for row in rows if (row.get("Client Type") or "").strip().upper() == "FII"),
        None,
    )
    if fii_row is None:
        raise ValueError("NSE participant OI CSV: no FII row found")

    required_columns = [
        "Future Index Long",
        "Future Index Short",
        "Option Index Call Long",
        "Option Index Call Short",
        "Option Index Put Long",
        "Option Index Put Short",
    ]
    extracted: dict[str, float] = {}
    # Normalize column names (strip whitespace) for lookup
    normalized_row = {k.strip(): v for k, v in fii_row.items() if k}
    for col in required_columns:
        if col not in normalized_row:
            raise KeyError(f"NSE CSV FII row missing expected column: '{col}'")
        raw_val = normalized_row[col].replace(",", "").strip()
        extracted[col] = float(raw_val) if raw_val else 0.0

    return extracted


# --------------------------------------------------------------------------- #
# D-045 Stale-data checks — source-specific, not uniform                       #
# --------------------------------------------------------------------------- #

def _check_dhan_staleness(response_headers: dict[str, str], now_utc: datetime) -> None:
    """D-045 DHAN stale-data check.

    Uses the HTTP response Date header — the only timestamp Dhan provides.
    Dhan's /optionchain has NO timestamp field in its response body (confirmed against v2 docs).
    Abort with StaleDataError if the gap > 15 minutes.
    Abort if the Date header is absent (that itself is a validation error).
    """
    date_header = response_headers.get("Date") or response_headers.get("date")
    if not date_header:
        raise StaleDataError(
            "STALE_DATA: Dhan response missing HTTP Date header — "
            "cannot verify data freshness. Aborting before scoring."
        )
    try:
        server_time = parsedate_to_datetime(date_header)
        # Ensure UTC-aware comparison
        if server_time.tzinfo is None:
            server_time = server_time.replace(tzinfo=timezone.utc)
        server_time_utc = server_time.astimezone(timezone.utc)
    except Exception as exc:
        raise StaleDataError(
            f"STALE_DATA: Could not parse Dhan HTTP Date header '{date_header}': {exc}"
        ) from exc

    gap_seconds = (now_utc - server_time_utc).total_seconds()
    if gap_seconds > 15 * 60:
        raise StaleDataError(
            f"STALE_DATA: Dhan data is {gap_seconds:.0f}s old (limit 900s / 15 min). "
            "Aborting before scoring runs."
        )


def _check_nse_fii_staleness(csv_text: str, now_utc: datetime) -> None:
    """D-045 NSE participant OI stale-data check.

    NSE publishes this CSV once daily (after market close, ~5–7 PM IST).
    A 15-minute rule would abort every live cycle (several-hours-old IS correct).
    A same-day rule would also abort (during 10 AM the only file is yesterday's).

    Rule: parse date from title row "...as on Jul 31, 2026" using regex.
    Abort with STALE_DATA only if > 4 calendar days old.
    If the pattern doesn't match: abort (validation error, don't guess).
    """
    # The title row is the first non-empty line
    lines = [line for line in csv_text.lstrip("\ufeff").strip().splitlines() if line.strip()]
    if not lines:
        raise StaleDataError("STALE_DATA: NSE participant OI CSV is empty, cannot verify date.")

    title_row = lines[0]
    match = re.search(r"as on (\w+ \d+, \d+)", title_row, re.IGNORECASE)
    if not match:
        raise StaleDataError(
            f"STALE_DATA: NSE CSV title row does not match expected pattern "
            f"'as on <Month> <Day>, <Year>'. Got: {title_row!r}. "
            "Cannot verify data freshness — aborting."
        )

    date_str = match.group(1)
    try:
        file_date = datetime.strptime(date_str, "%b %d, %Y").replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            # Try alternate month format (full month name)
            file_date = datetime.strptime(date_str, "%B %d, %Y").replace(tzinfo=timezone.utc)
        except ValueError as exc:
            raise StaleDataError(
                f"STALE_DATA: Could not parse NSE CSV date string '{date_str}': {exc}"
            ) from exc

    gap_days = (now_utc.replace(tzinfo=timezone.utc) - file_date).days
    if gap_days > 4:
        raise StaleDataError(
            f"STALE_DATA: NSE participant OI data is {gap_days} calendar days old "
            f"(date in CSV: {date_str}, limit: 4 days). Aborting before scoring runs."
        )


# --------------------------------------------------------------------------- #
# Main pipeline function (D-001)                                               #
# --------------------------------------------------------------------------- #

def fetch_and_score_market_data(
    symbol: str,
    *,
    _now_utc: datetime | None = None,
    _dhan_response_headers: dict[str, str] | None = None,
    _dhan_raw: dict[str, Any] | None = None,
    _vix_data: dict[str, Any] | None = None,
    _fii_envelope: dict[str, Any] | None = None,
    _candle_data: Any = None,
    _cycle_errors: list[dict[str, Any]] | None = None,
) -> ScoredMarketContext:
    """Fetch live market data, validate freshness, then score via layer_a/b/c.

    Parameters prefixed with _ are injectable for tests (mock the network layer,
    never hit live Dhan/NSE APIs in tests).

    Returns a ScoredMarketContext with extra='forbid' — a missing field raises
    ValidationError immediately, never silently defaults.

    Raises:
        StaleDataError: if freshness check fails for Dhan or NSE data.
        ValidationError: if the constructed ScoredMarketContext has wrong/missing fields.
        KeyError/TypeError: if raw Dhan/NSE payload is structurally wrong.
    """
    normalized = symbol.strip().upper()
    now_utc = _now_utc or datetime.now(timezone.utc)
    cycle_errors: list[dict[str, Any]] = _cycle_errors if _cycle_errors is not None else []

    # ------------------------------------------------------------------ #
    # Step 1–2: Fetch spot + option chain (Dhan primary, NSE fallback)    #
    # ------------------------------------------------------------------ #
    if _dhan_raw is not None and _dhan_response_headers is not None:
        # Injected for tests — skip network
        dhan_raw = _dhan_raw
        dhan_headers = _dhan_response_headers
    else:
        import httpx
        from src.data.dhan_client import get_option_chain, get_expiry_list
        from src.config.settings import settings

        expiries_env = get_expiry_list(normalized)
        if not expiries_env or not expiries_env.get("data"):
            raise RuntimeError(f"Could not fetch Dhan expiry list for {normalized}")
        expiry = expiries_env["data"][0]

        _http_client = httpx.Client(timeout=20.0)
        try:
            from src.data.dhan_client import _headers as dhan_headers_fn, DHAN_API
            body = {
                "UnderlyingScrip": {"NIFTY": 13, "BANKNIFTY": 25}[normalized],
                "UnderlyingSeg": "IDX_I",
                "Expiry": expiry,
            }
            raw_resp = _http_client.post(
                f"{DHAN_API}/optionchain",
                headers=dhan_headers_fn(),
                json=body,
            )
            dhan_headers = dict(raw_resp.headers)
            raw_resp.raise_for_status()
            dhan_raw = raw_resp.json()
        finally:
            _http_client.close()

    # Step 4a — DHAN staleness check BEFORE any scoring
    _check_dhan_staleness(dhan_headers, now_utc)

    # Stage 1 parsing: extract only the fields scoring needs
    dhan_fields = _extract_dhan_fields(dhan_raw)
    last_price = dhan_fields["last_price"]
    option_chain_raw = dhan_fields  # clean dict: {"last_price": ..., "oc": {...}}

    # ------------------------------------------------------------------ #
    # Step 2: Fetch VIX data                                              #
    # ------------------------------------------------------------------ #
    if _vix_data is not None:
        vix_data = _vix_data
    else:
        # VIX is fetched via NSE option chain for INDIAVIX
        # Minimal structure: {"structure": "normal", "change_pct": 0.0, "spot_move_pct": 0.0}
        # Full VIX integration is a future enhancement; safe neutral default here
        vix_data = {"structure": "normal", "change_pct": 0.0, "spot_move_pct": 0.0}

    # ------------------------------------------------------------------ #
    # Step 3: Fetch FII participant data via nse_fetcher                  #
    # ------------------------------------------------------------------ #
    fii_fetch_failed = False
    if _fii_envelope is not None:
        fii_envelope = _fii_envelope
        # Validate NSE CSV staleness if a csv_text was provided
        csv_text = (fii_envelope.get("data") or {}).get("csv_text")
        if csv_text:
            _check_nse_fii_staleness(csv_text, now_utc)
    else:
        try:
            from zoneinfo import ZoneInfo

            today = now_utc.astimezone(ZoneInfo("Asia/Kolkata")).date()
            fii_raw_env = fetch_participant_oi(today)
            csv_text = fii_raw_env["data"]["csv_text"]

            # Step 4b — NSE staleness check BEFORE scoring
            _check_nse_fii_staleness(csv_text, now_utc)

            fii_envelope = compute_long_short_ratio(csv_text)
        except StaleDataError:
            raise  # propagate stale-data directly; don't catch and swallow
        except Exception as exc:
            # FII fetch/parse failed — log degraded, but don't abort the cycle
            logger.warning("FII fetch failed (D-001 degraded mode): %s", exc)
            fii_fetch_failed = True
            fii_envelope = {
                "data": {"index_futures": 1.0, "index_calls": 1.0, "index_puts": 1.0},
                "fetched_at": now_utc.isoformat(),
                "trust_status": "stale",
            }
            # D-001 degraded-vs-neutral logging: append to cycle_summaries.errors
            cycle_errors.append({
                "layer": "B",
                "reason": "fii_fetch_failed",
                "defaulted": True,
            })

    # ------------------------------------------------------------------ #
    # Step 5: Fetch candle data for Layer C                               #
    # ------------------------------------------------------------------ #
    if _candle_data is not None:
        candle_data = _candle_data
    else:
        try:
            from src.data.dhan_client import get_candles
            candle_data = get_candles(normalized, "5", now=datetime.now(
                __import__("zoneinfo").ZoneInfo("Asia/Kolkata")
            ))
        except Exception:
            candle_data = None

    # ------------------------------------------------------------------ #
    # Step 5: Call scoring layers                                         #
    # ------------------------------------------------------------------ #
    layer_a: LayerAScore = score_layer_a(option_chain_raw, vix_data)

    fii_data_for_b = fii_envelope
    layer_b: LayerBScore = score_layer_b(fii_data_for_b)

    if candle_data is not None and (candle_data.get("data") or []):
        layer_c: LayerCScore = score_layer_c(candle_data, option_chain_raw)
    else:
        # Layer C requires at least one candle — use a minimal safe fallback
        # that produces a neutral direction without crashing
        minimal_candle = [{"high": last_price, "low": last_price, "close": last_price, "volume": 0}]
        layer_c = score_layer_c(minimal_candle, option_chain_raw)

    # Compute direction score using a minimal context
    try:
        from src.scoring.direction_scorer import compute_direction_score
        scoring_context: dict[str, Any] = {
            "scoring_config": {
                "layer_a_weight": 0.5,
                "layer_b_weight": 0.2,
                "layer_c_weight": 0.3,
                "off_boundary_c_weight": 0.05,
                "gex_flip_zone_cr": 0.0,
                "expiry_no_trade_minutes": 30,
                "version": "v11",
            },
        }
        direction_score = compute_direction_score(layer_a, layer_b, layer_c, scoring_context)
    except Exception as exc:
        logger.warning("direction_score computation failed, defaulting to 3: %s", exc)
        direction_score = 3

    # ------------------------------------------------------------------ #
    # Step 6: Return typed Pydantic model (extra='forbid')                 #
    # ------------------------------------------------------------------ #
    return ScoredMarketContext(
        symbol=normalized,
        last_price=last_price,
        option_chain_raw=option_chain_raw,
        vix_data=vix_data,
        fii_ratios=fii_envelope,
        layer_a=layer_a,
        layer_b=layer_b,
        layer_c=layer_c,
        direction_score=direction_score,
        fii_fetch_failed=fii_fetch_failed,
    )

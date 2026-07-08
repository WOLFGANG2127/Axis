"""Pure pricing and options math — no network, no side effects."""

from __future__ import annotations

import math
from datetime import date, datetime, time
from typing import Literal, Sequence
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
OptionType = Literal["call", "put", "CALL", "PUT", "CE", "PE"]

_CHAIN_STRIKE_KEYS = ("strike", "strike_price", "strikePrice")
_CHAIN_CALL_OI_KEYS = ("call_oi", "callOI", "CE_OI", "ce_oi")
_CHAIN_PUT_OI_KEYS = ("put_oi", "putOI", "PE_OI", "pe_oi")
_CHAIN_CALL_IV_KEYS = ("call_iv", "callIV", "CE_IV", "ce_iv", "impliedVolatility")
_CHAIN_PUT_IV_KEYS = ("put_iv", "putIV", "PE_IV", "pe_iv")


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _normalize_option_type(option_type: OptionType) -> Literal["call", "put"]:
    normalized = option_type.upper()
    if normalized in {"CE", "CALL"}:
        return "call"
    if normalized in {"PE", "PUT"}:
        return "put"
    raise ValueError(f"Unsupported option_type: {option_type!r}")


def _d1_d2(
    spot: float,
    strike: float,
    r: float,
    sigma: float,
    t: float,
) -> tuple[float, float]:
    if spot <= 0 or strike <= 0:
        raise ValueError("spot and strike must be positive")
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    if t <= 0:
        raise ValueError("t must be positive")
    sqrt_t = math.sqrt(t)
    d1 = (math.log(spot / strike) + (r + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t
    return d1, d2


def bs_price(
    spot: float,
    strike: float,
    r: float,
    sigma: float,
    t: float,
    option_type: OptionType,
) -> float:
    """Black-Scholes theoretical price."""
    kind = _normalize_option_type(option_type)
    d1, d2 = _d1_d2(spot, strike, r, sigma, t)
    discount = math.exp(-r * t)
    if kind == "call":
        return spot * _norm_cdf(d1) - strike * discount * _norm_cdf(d2)
    return strike * discount * _norm_cdf(-d2) - spot * _norm_cdf(-d1)


def bs_delta(
    spot: float,
    strike: float,
    r: float,
    sigma: float,
    t: float,
    option_type: OptionType,
) -> float:
    kind = _normalize_option_type(option_type)
    d1, _ = _d1_d2(spot, strike, r, sigma, t)
    if kind == "call":
        return _norm_cdf(d1)
    return _norm_cdf(d1) - 1.0


def bs_gamma(spot: float, strike: float, r: float, sigma: float, t: float) -> float:
    d1, _ = _d1_d2(spot, strike, r, sigma, t)
    return _norm_pdf(d1) / (spot * sigma * math.sqrt(t))


def bs_theta_per_day(
    spot: float,
    strike: float,
    r: float,
    sigma: float,
    t: float,
    option_type: OptionType,
) -> float:
    kind = _normalize_option_type(option_type)
    d1, d2 = _d1_d2(spot, strike, r, sigma, t)
    sqrt_t = math.sqrt(t)
    discount = math.exp(-r * t)
    common = -(spot * _norm_pdf(d1) * sigma) / (2.0 * sqrt_t)
    if kind == "call":
        annual = common - r * strike * discount * _norm_cdf(d2)
    else:
        annual = common + r * strike * discount * _norm_cdf(-d2)
    return annual / 365.0


def bs_vega(spot: float, strike: float, r: float, sigma: float, t: float) -> float:
    d1, _ = _d1_d2(spot, strike, r, sigma, t)
    return spot * _norm_pdf(d1) * math.sqrt(t) / 100.0


def years_to_expiry(
    expiry_date: date,
    now: datetime,
    expiry_time: time = time(15, 30),
) -> float:
    """Time to expiry anchored at 15:30 IST on expiry date, never midnight."""
    if now.tzinfo is None:
        now = now.replace(tzinfo=IST)
    else:
        now = now.astimezone(IST)

    expiry_dt = datetime.combine(expiry_date, expiry_time, tzinfo=IST)
    remaining_seconds = max((expiry_dt - now).total_seconds(), 1.0)
    return remaining_seconds / (365.0 * 24.0 * 3600.0)


def theta_between(
    spot: float,
    strike: float,
    r: float,
    sigma: float,
    t_now: float,
    t_later: float,
    option_type: OptionType,
) -> float:
    """Non-linear theta decay between two time anchors (price difference)."""
    if t_later >= t_now:
        raise ValueError("t_later must be earlier in time than t_now (smaller T)")
    price_now = bs_price(spot, strike, r, sigma, t_now, option_type)
    price_later = bs_price(spot, strike, r, sigma, t_later, option_type)
    return price_later - price_now


def _chain_value(row: dict, keys: Sequence[str], default: float = 0.0) -> float:
    for key in keys:
        if key in row and row[key] is not None:
            return float(row[key])
    return default


def _row_strike(row: dict) -> float:
    strike = _chain_value(row, _CHAIN_STRIKE_KEYS)
    if strike <= 0:
        raise ValueError("option-chain row is missing a positive strike")
    return strike


def _row_iv(row: dict, option_type: Literal["call", "put"]) -> float:
    keys = _CHAIN_CALL_IV_KEYS if option_type == "call" else _CHAIN_PUT_IV_KEYS
    iv = _chain_value(row, keys, default=0.2)
    # NSE publishes IV as percentage points (for example 13.5), while the
    # Black-Scholes contract takes decimal volatility (0.135).
    if iv > 1.0:
        iv /= 100.0
    return max(iv, 1e-6)
def net_gex(
    chain: Sequence[dict],
    spot: float,
    r: float,
    t: float,
    lot_size: int,
) -> float:
    """Aggregate gamma exposure (rupee hedge flow per 1% spot move)."""
    total = 0.0
    for row in chain:
        strike = _row_strike(row)
        call_oi = _chain_value(row, _CHAIN_CALL_OI_KEYS)
        put_oi = _chain_value(row, _CHAIN_PUT_OI_KEYS)
        call_gamma = bs_gamma(spot, strike, r, _row_iv(row, "call"), t)
        put_gamma = bs_gamma(spot, strike, r, _row_iv(row, "put"), t)
        total += (call_gamma * call_oi - put_gamma * put_oi) * lot_size * (spot ** 2) * 0.01
    return total


def gamma_flip_level(
    chain: Sequence[dict],
    spot: float,
    r: float,
    t: float,
    lot_size: int,
    search_pct: float = 0.05,
    steps: int = 200,
) -> float:
    """Spot level where net GEX crosses zero."""
    low = spot * (1.0 - search_pct)
    high = spot * (1.0 + search_pct)
    prev_spot = low
    prev_gex = net_gex(chain, prev_spot, r, t, lot_size=lot_size)
    for idx in range(1, steps + 1):
        candidate = low + (high - low) * (idx / steps)
        candidate_gex = net_gex(chain, candidate, r, t, lot_size=lot_size)
        if prev_gex == 0.0:
            return prev_spot
        if candidate_gex == 0.0 or (prev_gex < 0.0 < candidate_gex) or (prev_gex > 0.0 > candidate_gex):
            denom = (candidate_gex - prev_gex)
            if denom == 0.0:
                return candidate
            weight = (-prev_gex) / denom
            return prev_spot + (candidate - prev_spot) * weight
        prev_spot = candidate
        prev_gex = candidate_gex
    return spot


def max_pain(chain: Sequence[dict]) -> float:
    strikes = sorted({_row_strike(row) for row in chain})
    if not strikes:
        raise ValueError("option chain is empty")

    best_strike = strikes[0]
    best_pain = float("inf")
    for candidate in strikes:
        pain = 0.0
        for row in chain:
            strike = _row_strike(row)
            call_oi = _chain_value(row, _CHAIN_CALL_OI_KEYS)
            put_oi = _chain_value(row, _CHAIN_PUT_OI_KEYS)
            pain += max(candidate - strike, 0.0) * call_oi
            pain += max(strike - candidate, 0.0) * put_oi
        if pain < best_pain:
            best_pain = pain
            best_strike = candidate
    return best_strike


def pcr(chain: Sequence[dict]) -> float:
    total_puts = sum(_chain_value(row, _CHAIN_PUT_OI_KEYS) for row in chain)
    total_calls = sum(_chain_value(row, _CHAIN_CALL_OI_KEYS) for row in chain)
    if total_calls == 0:
        return float("inf")
    return total_puts / total_calls


def vix_expected_move(spot: float, vix: float) -> float:
    if spot <= 0:
        raise ValueError("spot must be positive")
    if vix < 0:
        raise ValueError("vix cannot be negative")
    return spot * (vix / 100.0) / math.sqrt(252.0)


def down_target(spot: float, vix: float) -> float:
    return spot - vix_expected_move(spot, vix)


def cascade_magnitude(net_gex_value: float, move_pct: float) -> float:
    # UNVERIFIED first-order estimate — only one dated example supports this.
    return abs(net_gex_value) * move_pct


def transaction_cost(
    sell_premium_value: float,
    brokerage: float = 40.0,
    exchange_charges: float = 35.0,
    gst_rate: float = 0.18,
) -> float:
    if sell_premium_value < 0:
        raise ValueError("sell_premium_value cannot be negative")
    if brokerage < 0 or exchange_charges < 0 or gst_rate < 0:
        raise ValueError("transaction-cost inputs cannot be negative")
    stt = 0.000625 * sell_premium_value
    gst = gst_rate * brokerage
    return stt + brokerage + exchange_charges + gst


def expected_value(
    win_prob: float,
    avg_gain: float,
    avg_loss: float,
    est_transaction_cost: float,
) -> float:
    if not 0.0 <= win_prob <= 1.0:
        raise ValueError("win_prob must be between 0 and 1")
    if avg_gain < 0 or avg_loss < 0 or est_transaction_cost < 0:
        raise ValueError("gain, loss, and transaction cost cannot be negative")
    return win_prob * avg_gain - (1.0 - win_prob) * avg_loss - est_transaction_cost


def kelly_fraction(win_prob: float, avg_gain: float, avg_loss: float) -> float:
    """f* = p - q/b where q = 1-p and b = avg_gain/avg_loss."""
    if avg_loss <= 0:
        raise ValueError("avg_loss must be positive")
    if avg_gain <= 0:
        raise ValueError("avg_gain must be positive")
    if not 0.0 <= win_prob <= 1.0:
        raise ValueError("win_prob must be between 0 and 1")
    p = win_prob
    q = 1.0 - p
    b = avg_gain / avg_loss
    return p - q / b

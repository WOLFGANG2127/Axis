"""Golden Zone + Volume Profile + Order Flow strategy."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

from src.config.constants import (
    GVOF_ENTRY_BUFFER,
    GVOF_HARD_EXIT,
    GVOF_IB_END,
    GVOF_IB_MIN_RANGE,
    GVOF_NO_ENTRY_AFTER,
    GVOF_STOP_BUFFER,
    GVOF_STOP_IB_PCT,
    GVOF_T1_OFFSET,
)
from src.graph.state import AxisState
from src.math.pricing import vix_expected_move
from src.strategies.base import BaseStrategy

IST = ZoneInfo("Asia/Kolkata")
IB_START = time(9, 15)
FIB_618 = 0.618
FIB_786 = 0.786


def _local_time(value: Any) -> time | None:
    if isinstance(value, time):
        return value
    if isinstance(value, datetime):
        local = value.replace(tzinfo=IST) if value.tzinfo is None else value.astimezone(IST)
        return local.time().replace(tzinfo=None)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
        return _local_time(parsed)
    return None


def _candle_time(candle: Mapping[str, Any]) -> time | None:
    return _local_time(candle.get("timestamp", candle.get("time")))


def _initial_balance(
    context: Mapping[str, Any],
) -> tuple[float | None, float | None]:
    supplied_high = context.get("ib_high")
    supplied_low = context.get("ib_low")
    if supplied_high is not None and supplied_low is not None:
        return float(supplied_high), float(supplied_low)

    candles: Sequence[Mapping[str, Any]] = context.get("candles", []) or []
    end = time(*GVOF_IB_END)
    ib_rows = [
        candle
        for candle in candles
        if (stamp := _candle_time(candle)) is not None and IB_START <= stamp <= end
    ]
    if not ib_rows:
        return None, None
    return (
        max(float(candle["high"]) for candle in ib_rows),
        min(float(candle["low"]) for candle in ib_rows),
    )


def _direction(state: AxisState, context: Mapping[str, Any]) -> str | None:
    explicit = str(context.get("signal_direction", "")).lower()
    if explicit in {"bullish", "bearish"}:
        return explicit
    if state.direction_score is not None:
        if state.direction_score >= 4:
            return "bullish"
        if state.direction_score <= 2:
            return "bearish"
    ratio = context.get("fii_long_short_ratio")
    if ratio is not None:
        return "bullish" if float(ratio) > 1.0 else "bearish"
    return None


def _failed(reason: str, **details: Any) -> dict[str, Any]:
    return {
        "passed": False,
        "strategy_name": "GVOF",
        "reason": reason,
        **details,
    }


class GVOFStrategy(BaseStrategy):
    """Apply the full GEX-first GVOF activation checklist."""

    name = "GVOF"

    def check_conditions(self, state: AxisState) -> dict:
        context = state.market_context or {}
        now = _local_time(context.get("now", state.cycle_timestamp))
        if now is not None and now >= time(*GVOF_NO_ENTRY_AFTER):
            return _failed("NO_NEW_ENTRIES_AFTER_1400")
        if state.structure_confirmed is not True:
            return _failed("STRUCTURE_GATE_FAILED")

        gex_value = context.get("net_gex", context.get("gex"))
        if gex_value is None:
            return _failed("GEX_UNAVAILABLE")
        gex = float(gex_value)
        direction = _direction(state, context)
        if direction is None:
            return _failed("DIRECTION_UNRESOLVED")

        ib_high, ib_low = _initial_balance(context)
        if ib_high is None or ib_low is None or ib_high <= ib_low:
            return _failed("INITIAL_BALANCE_NOT_FORMED")
        ib_range = ib_high - ib_low
        if ib_range < GVOF_IB_MIN_RANGE:
            return _failed(
                "IB_RANGE_BELOW_50_POINTS",
                ib_high=ib_high,
                ib_low=ib_low,
                ib_range=ib_range,
            )

        spot = float(context.get("spot", 0))
        vix = float(context.get("vix", 0))
        if spot <= 0 or vix < 0:
            return _failed("SPOT_OR_VIX_INVALID")

        stop_distance = ib_range * GVOF_STOP_IB_PCT
        common = {
            "direction": direction,
            "gex": gex,
            "ib_high": ib_high,
            "ib_low": ib_low,
            "ib_range": ib_range,
            "stop_distance": stop_distance,
            "hard_exit_time": time(*GVOF_HARD_EXIT).isoformat(),
            "no_entry_after": time(*GVOF_NO_ENTRY_AFTER).isoformat(),
            "never_average_loser": True,
        }

        # Negative GEX is the master switch: abandon Fibonacci mean reversion
        # and follow the confirmed directional cascade.
        if gex < 0:
            cascade_confirmed = bool(
                context.get("cascade_confirmed")
                or context.get("expiry_cascade")
                or context.get("three_stage_sweep")
            )
            if not cascade_confirmed:
                return _failed("NEGATIVE_GEX_CASCADE_UNCONFIRMED", **common)
            return {
                "passed": True,
                "strategy_name": self.name,
                "mode": "negative-gex-cascade",
                "golden_zone_abandoned": True,
                "entry": spot,
                "stop_loss": spot + stop_distance if direction == "bearish" else spot - stop_distance,
                "target_1": ib_low - GVOF_T1_OFFSET if direction == "bearish" else ib_high + GVOF_T1_OFFSET,
                "target_1_exit_pct": 50,
                "move_stop_to_breakeven_at_t1": True,
                "target_2": spot - vix_expected_move(spot, vix)
                if direction == "bearish"
                else spot + vix_expected_move(spot, vix),
                **common,
            }

        is_expiry = bool(context.get("is_expiry_day"))
        expiry_variant = is_expiry and now is not None and now < time(10, 0)
        if expiry_variant and not (
            context.get("judas_sweep") and context.get("choch_confirmed")
        ):
            return _failed("EXPIRY_JUDAS_SWEEP_OR_CHOCH_MISSING", **common)

        upper_zone = (
            ib_low + FIB_618 * ib_range,
            ib_low + FIB_786 * ib_range,
        )
        lower_zone = (
            ib_high - FIB_786 * ib_range,
            ib_high - FIB_618 * ib_range,
        )
        zone = upper_zone if direction == "bearish" else lower_zone
        zone_touched = zone[0] <= spot <= zone[1]
        reversal_confirmed = bool(
            context.get("wick_beyond_786")
            and context.get("closed_back_in_zone")
            and context.get("choch_confirmed")
        )
        if not zone_touched:
            return _failed("PRICE_OUTSIDE_GOLDEN_ZONE", golden_zone=zone, **common)
        if not reversal_confirmed:
            return _failed("GOLDEN_ZONE_REVERSAL_UNCONFIRMED", golden_zone=zone, **common)

        fib_618 = zone[0] if direction == "bearish" else zone[1]
        entry = (
            fib_618 - GVOF_ENTRY_BUFFER
            if direction == "bearish"
            else fib_618 + GVOF_ENTRY_BUFFER
        )
        sweep_extreme = context.get("sweep_extreme")
        if sweep_extreme is None:
            stop_loss = entry + stop_distance if direction == "bearish" else entry - stop_distance
        else:
            stop_loss = (
                float(sweep_extreme) + GVOF_STOP_BUFFER
                if direction == "bearish"
                else float(sweep_extreme) - GVOF_STOP_BUFFER
            )

        return {
            "passed": True,
            "strategy_name": self.name,
            "mode": "expiry-judas-reversal" if expiry_variant else "golden-zone-reversal",
            "golden_zone_abandoned": False,
            "golden_zone": zone,
            "entry": entry,
            "stop_loss": stop_loss,
            "target_1": ib_low - GVOF_T1_OFFSET if direction == "bearish" else ib_high + GVOF_T1_OFFSET,
            "target_1_exit_pct": 50,
            "move_stop_to_breakeven_at_t1": True,
            "target_2": spot - vix_expected_move(spot, vix)
            if direction == "bearish"
            else spot + vix_expected_move(spot, vix),
            **common,
        }

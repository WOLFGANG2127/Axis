"""Wyckoff spring/upthrust mean-reversion strategy.

The strategy reads only trust-tagged AxisState.market_context fields. It does
not fetch data or import any data/network client.
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

from src.graph.state import AxisState
from src.strategies.base import BaseStrategy

IST = ZoneInfo("Asia/Kolkata")


def _local_time(value: Any) -> time | None:
    if isinstance(value, time):
        return value
    if isinstance(value, datetime):
        local = value.astimezone(IST) if value.tzinfo else value.replace(tzinfo=IST)
        return local.time().replace(tzinfo=None)
    if isinstance(value, str):
        try:
            return _local_time(datetime.fromisoformat(value.replace("Z", "+00:00")))
        except ValueError:
            return None
    return None


def _candles(context: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw = context.get("candles") or []
    if isinstance(raw, Mapping):
        raw = raw.get("data") or []
    return [row for row in raw if isinstance(row, Mapping)]


def _last_close(candles: Sequence[Mapping[str, Any]], context: Mapping[str, Any]) -> float | None:
    if context.get("spot") is not None:
        return float(context["spot"])
    if candles and candles[-1].get("close") is not None:
        return float(candles[-1]["close"])
    return None


def _volume_expansion(candles: Sequence[Mapping[str, Any]], minimum_ratio: float) -> bool:
    if len(candles) < 6:
        return bool(candles and candles[-1].get("volume_spike"))
    recent = float(candles[-1].get("volume") or 0)
    base = [float(row.get("volume") or 0) for row in candles[-6:-1]]
    avg = sum(base) / len(base) if base else 0
    return avg > 0 and recent >= avg * minimum_ratio


def _failed(reason: str, **details: Any) -> dict[str, Any]:
    return {
        "passed": False,
        "strategy_id": "wyckoff_mean_reversion",
        "strategy_name": "Wyckoff Mean Reversion",
        "reason": reason,
        **details,
    }


class WyckoffMeanReversionStrategy(BaseStrategy):
    """Mean reversion after Wyckoff spring/upthrust reclaim."""

    strategy_id = "wyckoff_mean_reversion"
    name = "Wyckoff Mean Reversion"

    def check_conditions(self, state: AxisState) -> dict:
        context = state.market_context or {}
        if state.structure_confirmed is not True:
            return _failed("STRUCTURE_GATE_FAILED")
        if context.get("is_expiry_day") and _local_time(context.get("now", state.cycle_timestamp)) and _local_time(context.get("now", state.cycle_timestamp)) >= time(14, 0):
            return _failed("EXPIRY_AFTER_1400_BLOCK")

        candle_rows = _candles(context)
        spot = _last_close(candle_rows, context)
        if spot is None or spot <= 0:
            return _failed("SPOT_UNAVAILABLE")

        entry_params = (
            (state.strategy_config_snapshot or {})
            .get(self.strategy_id, {})
            .get("entry_parameters", {})
        )
        volume_ratio = float(entry_params.get("volume_expansion_ratio", 1.4))
        stop_buffer_pct = float(entry_params.get("stop_buffer_pct", 0.0015))
        target_buffer_pct = float(entry_params.get("target_buffer_pct", 0.0025))

        value_area_low = context.get("value_area_low")
        value_area_high = context.get("value_area_high")
        poc = context.get("volume_profile_poc") or context.get("poc")
        if value_area_low is None or value_area_high is None or poc is None:
            return _failed("VALUE_AREA_UNAVAILABLE")
        val = float(value_area_low)
        vah = float(value_area_high)
        poc_value = float(poc)

        spring = bool(context.get("wyckoff_spring") or context.get("spring_confirmed"))
        upthrust = bool(context.get("wyckoff_upthrust") or context.get("upthrust_confirmed"))
        reclaim = bool(context.get("reclaimed_value_area") or context.get("closed_back_in_value"))
        choch = bool(context.get("choch_confirmed") or context.get("market_structure_shift"))
        volume_ok = _volume_expansion(candle_rows, volume_ratio) or bool(context.get("volume_expansion"))
        order_flow_ok = bool(context.get("delta_absorption") or context.get("order_flow_absorption"))

        if not reclaim:
            return _failed("VALUE_AREA_RECLAIM_MISSING")
        if not choch:
            return _failed("CHOCH_MISSING")
        if not volume_ok:
            return _failed("VOLUME_EXPANSION_MISSING")
        if not order_flow_ok:
            return _failed("ORDER_FLOW_ABSORPTION_MISSING")
        if spring == upthrust:
            return _failed("SPRING_OR_UPTHRUST_UNRESOLVED", spring=spring, upthrust=upthrust)

        direction = "bullish" if spring else "bearish"
        stop_buffer = spot * stop_buffer_pct
        target_buffer = spot * target_buffer_pct
        if direction == "bullish":
            sweep_extreme = float(context.get("sweep_low") or min(float(row.get("low") or spot) for row in candle_rows[-6:]) if candle_rows else spot)
            stop_loss = sweep_extreme - stop_buffer
            target_1 = poc_value
            target_2 = min(vah, spot + target_buffer)
            price_zone = "spring-value-area-reclaim"
        else:
            sweep_extreme = float(context.get("sweep_high") or max(float(row.get("high") or spot) for row in candle_rows[-6:]) if candle_rows else spot)
            stop_loss = sweep_extreme + stop_buffer
            target_1 = poc_value
            target_2 = max(val, spot - target_buffer)
            price_zone = "upthrust-value-area-reclaim"

        return {
            "passed": True,
            "strategy_id": self.strategy_id,
            "strategy_name": self.name,
            "direction": direction,
            "mode": "wyckoff-spring" if spring else "wyckoff-upthrust",
            "entry": spot,
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "target_1_exit_pct": 50,
            "move_stop_to_breakeven_at_t1": True,
            "price_zone": price_zone,
            "value_area_low": val,
            "value_area_high": vah,
            "volume_profile_poc": poc_value,
            "volume_expansion": volume_ok,
            "order_flow_absorption": order_flow_ok,
            "never_average_loser": True,
        }


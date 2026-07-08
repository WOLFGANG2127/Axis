"""Strict binary structure confirmation gate."""

from __future__ import annotations

from typing import Any, Mapping

from src.scoring.layer_c import score_layer_c


def _slope(values: list[float]) -> float:
    count = len(values)
    if count < 2:
        return 0.0
    x_mean = (count - 1) / 2
    y_mean = sum(values) / count
    numerator = sum((index - x_mean) * (value - y_mean) for index, value in enumerate(values))
    denominator = sum((index - x_mean) ** 2 for index in range(count))
    return numerator / denominator if denominator else 0.0


def check_structure(candles: Any, chain_data: Any) -> bool:
    """Require phase, turn, boundary, migration, and range-slope agreement."""
    candle_rows = candles.get("data", candles) if isinstance(candles, Mapping) else candles
    payload = chain_data.get("data", chain_data) if isinstance(chain_data, Mapping) else chain_data
    payload = payload if isinstance(payload, Mapping) else {"chain": payload}
    layer_c = score_layer_c(candle_rows, payload)
    if not layer_c.at_vp_boundary:
        return False
    phase = str(payload.get("wyckoff_phase", "")).upper()
    event = str(payload.get("wyckoff_event", "")).upper()
    if phase not in {"C", "D"} or event not in {"SPRING", "UTAD", "SOS", "SOW"}:
        return False
    if not payload.get("three_step_turn"):
        return False
    signal = str(payload.get("signal_direction", "")).lower()
    migration = str(payload.get("vpoc_migration", "")).lower()
    if (signal == "bearish" and migration not in {"down", "bearish"}) or (
        signal == "bullish" and migration not in {"up", "bullish"}
    ):
        return False
    if payload.get("excessive_sideways"):
        return False
    profile_values = [float(value) for value in payload.get("profile_midpoints", [])][-6:]
    if len(profile_values) >= 2:
        spot = float(payload.get("spot", candle_rows[-1]["close"]))
        threshold = spot * float(payload.get("range_slope_threshold_pct", 0.001))
        slope = _slope(profile_values)
        if signal == "bearish" and slope > -threshold:
            return False
        if signal == "bullish" and slope < threshold:
            return False
    return True


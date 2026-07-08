"""Layer C: five-minute volume profile and OI-versus-LTP divergence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class LayerCScore:
    vah: float
    val: float
    vpoc: float
    lvn_levels: tuple[float, ...]
    at_vp_boundary: bool
    divergence: str
    strongest_divergence_pct: float
    direction_value: float
    three_stage_sweep: bool


def _payload(value: Any) -> Any:
    return value.get("data") if isinstance(value, Mapping) and "data" in value else value


def _volume_profile(candles: Sequence[Mapping[str, Any]]) -> tuple[float, float, float, tuple[float, ...]]:
    if not candles:
        raise ValueError("at least one five-minute candle is required")
    buckets: dict[float, float] = {}
    for candle in candles:
        price = round(
            (float(candle["high"]) + float(candle["low"]) + float(candle["close"])) / 3.0,
            1,
        )
        buckets[price] = buckets.get(price, 0.0) + float(candle.get("volume", 0))
    vpoc = max(buckets, key=buckets.get)
    target = sum(buckets.values()) * 0.70
    selected: list[float] = []
    cumulative = 0.0
    for price, volume in sorted(buckets.items(), key=lambda item: item[1], reverse=True):
        selected.append(price)
        cumulative += volume
        if cumulative >= target:
            break
    val, vah = min(selected), max(selected)
    positive = [volume for volume in buckets.values() if volume > 0]
    threshold = (sum(positive) / len(positive)) * 0.25 if positive else 0
    lvns = tuple(sorted(price for price, volume in buckets.items() if volume <= threshold))
    return vah, val, vpoc, lvns


def _chain_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return list(payload)
    if not isinstance(payload, Mapping):
        return []
    return list(payload.get("strikes", payload.get("chain", [])))


def _is_three_stage_sweep(candles: Sequence[Mapping[str, Any]], payload: Mapping[str, Any]) -> bool:
    if payload.get("three_stage_sweep") is True:
        return True
    stages = {int(candle["sweep_stage"]) for candle in candles if candle.get("sweep_stage")}
    final = candles[-1]
    volumes = [float(candle.get("volume", 0)) for candle in candles[:-1]]
    baseline = sum(volumes) / len(volumes) if volumes else 0
    return stages.issuperset({1, 2, 3}) and bool(final.get("bos")) and float(final.get("volume", 0)) > baseline * 1.5


def score_layer_c(candles: Any, chain_data: Any) -> LayerCScore:
    candle_rows = list(_payload(candles) or [])
    payload = _payload(chain_data) or {}
    if not isinstance(payload, Mapping):
        payload = {"chain": payload}
    vah, val, vpoc, computed_lvns = _volume_profile(candle_rows)
    lvns = tuple(float(value) for value in payload.get("lvn_levels", computed_lvns))
    current = float(payload.get("spot", candle_rows[-1]["close"]))
    tolerance = float(payload.get("boundary_tolerance_pct", 0.001)) * current
    boundaries = (vah, val, vpoc, *lvns)
    at_boundary = any(abs(current - boundary) <= tolerance for boundary in boundaries)

    best_kind = "none"
    best_magnitude = 0.0
    direction = 0.0
    for row in _chain_rows(payload):
        option = str(row.get("option_type", row.get("type", ""))).upper()
        oi_change = float(row.get("oi_change_pct", row.get("oi_pct_change", 0)))
        ltp_change = float(row.get("ltp_change_pct", row.get("ltp_pct_change", 0)))
        if oi_change > 0 and ltp_change < 0 and oi_change > best_magnitude:
            best_magnitude = oi_change
            if option in {"CE", "CALL"}:
                best_kind, direction = "call-selling", -1.0
            elif option in {"PE", "PUT"}:
                best_kind, direction = "put-selling", 1.0
    if not at_boundary:
        direction = 0.0
    return LayerCScore(
        vah=vah,
        val=val,
        vpoc=vpoc,
        lvn_levels=lvns,
        at_vp_boundary=at_boundary,
        divergence=best_kind,
        strongest_divergence_pct=best_magnitude,
        direction_value=direction,
        three_stage_sweep=_is_three_stage_sweep(candle_rows, payload),
    )


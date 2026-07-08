"""Versioned weighted direction score with hard pre-score overrides."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from src.scoring.layer_a import LayerAScore
from src.scoring.layer_b import LayerBScore
from src.scoring.layer_c import LayerCScore

IST = ZoneInfo("Asia/Kolkata")


@dataclass(frozen=True)
class ScoringConfig:
    layer_a_weight: float
    layer_b_weight: float
    layer_c_weight: float
    off_boundary_c_weight: float
    gex_flip_zone_cr: float
    expiry_no_trade_minutes: int
    version: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ScoringConfig":
        required = {
            "layer_a_weight", "layer_b_weight", "layer_c_weight",
            "off_boundary_c_weight", "gex_flip_zone_cr",
            "expiry_no_trade_minutes", "version",
        }
        missing = required - set(value)
        if missing:
            raise ValueError(f"scoring_config missing: {', '.join(sorted(missing))}")
        result = cls(**{key: value[key] for key in required})
        if min(result.layer_a_weight, result.layer_b_weight, result.layer_c_weight, result.off_boundary_c_weight) < 0:
            raise ValueError("scoring weights cannot be negative")
        return result


def score_expiry_day(
    gex: float,
    vix_structure: str,
    oi_build_pct: float,
    pcr_rising: bool,
    vix_choch: bool,
) -> int:
    score = 3 if gex < 0 else 0
    if vix_structure.lower().replace("_", "-") in {"weak-low", "near-weak-low"}:
        score += 2
    if oi_build_pct > 50:
        score += 2
    if pcr_rising and gex < 0:
        score += 1
    if vix_choch:
        score += 1
    return min(score, 9)


def _inside_expiry_open_window(context: Mapping[str, Any], minutes: int) -> bool:
    if not context.get("is_expiry_day"):
        return False
    now = context.get("now")
    if not isinstance(now, datetime):
        return False
    local = now.replace(tzinfo=IST) if now.tzinfo is None else now.astimezone(IST)
    opened = datetime.combine(local.date(), time(9, 15), tzinfo=IST)
    return opened <= local < opened + timedelta(minutes=minutes)


def compute_direction_score(
    layer_a: LayerAScore,
    layer_b: LayerBScore,
    layer_c: LayerCScore,
    context: Mapping[str, Any],
) -> int:
    """Return 1 (strong bearish) through 5 (strong bullish)."""
    config = ScoringConfig.from_mapping(context["scoring_config"])
    if context.get("event_proximity") or _inside_expiry_open_window(context, config.expiry_no_trade_minutes):
        return 3
    if abs(layer_a.gex) <= config.gex_flip_zone_cr:
        return 3
    if layer_a.expiry_score >= 5:
        return 1

    c_weight = config.layer_c_weight if layer_c.at_vp_boundary else config.off_boundary_c_weight
    weights = (config.layer_a_weight, config.layer_b_weight, c_weight)
    total = sum(weights)
    if total <= 0:
        raise ValueError("scoring_config weights must have a positive sum")
    combined = (
        layer_a.direction_value * weights[0]
        + layer_b.direction_value * weights[1]
        + layer_c.direction_value * weights[2]
    ) / total
    return max(1, min(5, round(3 + 2 * combined)))

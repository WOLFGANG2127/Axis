"""Layer B: conservatively weighted participant identity data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class LayerBScore:
    index_futures_ratio: float
    index_calls_ratio: float
    index_puts_ratio: float
    fii_data_date: str | None
    direction_value: float


def score_layer_b(fii_data: Any) -> LayerBScore:
    payload = fii_data.get("data", fii_data) if isinstance(fii_data, Mapping) else {}
    if "ratios" in payload:
        payload = {**payload, **payload["ratios"]}
    futures = float(payload.get("index_futures", 1.0))
    calls = float(payload.get("index_calls", 1.0))
    puts = float(payload.get("index_puts", 1.0))
    # A small, bounded directional hint only; this layer has no dated proof yet.
    raw = ((futures - 1.0) + (calls - 1.0) - (puts - 1.0)) / 3.0
    direction = max(-0.5, min(0.5, raw))
    return LayerBScore(futures, calls, puts, payload.get("fii_data_date"), direction)


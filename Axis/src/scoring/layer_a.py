"""Layer A: GEX-first anonymous market-wide sentiment scoring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from src.config.constants import get_lot_size
from src.math.pricing import gamma_flip_level, max_pain, net_gex, pcr


@dataclass(frozen=True)
class LayerAScore:
    gex: float
    gex_regime: str
    gamma_flip: float | None
    max_pain_level: float | None
    vix_structure: str
    pcr_value: float
    pcr_rising: bool
    pcr_divergence: float | None
    pcr_divergence_informational: bool
    overnight_oi_build_pct: float
    expiry_score: int
    cascade_flag: bool
    vix_move_classification: str
    direction_value: float


def _payload(value: Any) -> Any:
    return value.get("data") if isinstance(value, Mapping) and "data" in value else value


def _flat_chain(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, Mapping):
        return []
    if isinstance(payload.get("chain"), list):
        return list(payload["chain"])
    records = payload.get("records", {})
    if isinstance(records, Mapping) and isinstance(records.get("data"), list):
        rows = []
        for source in records["data"]:
            ce, pe = source.get("CE", {}), source.get("PE", {})
            rows.append(
                {
                    "strike": source.get("strikePrice"),
                    "call_oi": ce.get("openInterest", 0),
                    "put_oi": pe.get("openInterest", 0),
                    "call_iv": ce.get("impliedVolatility", 20),
                    "put_iv": pe.get("impliedVolatility", 20),
                }
            )
        return rows
    oc = payload.get("oc")
    if isinstance(oc, Mapping):
        rows = []
        for strike, source in oc.items():
            ce, pe = source.get("ce", {}), source.get("pe", {})
            rows.append(
                {
                    "strike": float(strike),
                    "call_oi": ce.get("oi", 0),
                    "put_oi": pe.get("oi", 0),
                    "call_iv": ce.get("implied_volatility", 20),
                    "put_iv": pe.get("implied_volatility", 20),
                }
            )
        return rows
    return []


def classify_vix_move(vix_change_pct: float, spot_move_pct: float) -> str:
    """Separate fear cascades from flat-VIX mechanical settlement unwinds."""
    if spot_move_pct < 0 and vix_change_pct >= 5.0:
        return "fear-cascade"
    if spot_move_pct < 0 and abs(vix_change_pct) <= 1.0:
        return "mechanical-unwind"
    return "normal"


def _expiry_score(
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


def score_layer_a(chain_data: Any, vix_data: Any) -> LayerAScore:
    """Score strictly in GEX -> VIX -> PCR order."""
    chain_payload = _payload(chain_data)
    vix_payload = _payload(vix_data) or {}
    if not isinstance(chain_payload, Mapping):
        chain_payload = {"chain": chain_payload}
    rows = _flat_chain(chain_payload)
    spot = float(chain_payload.get("spot", chain_payload.get("last_price", 0)))
    rate = float(chain_payload.get("risk_free_rate", 0.065))
    t = float(chain_payload.get("time_to_expiry", 1 / 365))
    symbol = chain_payload.get("symbol", "NIFTY")
    lot_size = get_lot_size(symbol)

    # Master switch: this is deliberately computed before VIX and PCR.
    gex = float(chain_payload["net_gex"]) if "net_gex" in chain_payload else net_gex(rows, spot, rate, t, lot_size)
    gex_regime = "negative" if gex < 0 else "positive" if gex > 0 else "flip"
    flip = (
        float(chain_payload["gamma_flip"])
        if chain_payload.get("gamma_flip") is not None
        else gamma_flip_level(rows, spot, rate, t, lot_size) if rows and spot > 0 else None
    )

    vix_structure = str(vix_payload.get("structure", "normal"))
    vix_choch = bool(vix_payload.get("choch_up") or vix_payload.get("bos_up"))
    vix_class = classify_vix_move(
        float(vix_payload.get("change_pct", 0)),
        float(vix_payload.get("spot_move_pct", 0)),
    )

    current_pcr = float(chain_payload["pcr"]) if "pcr" in chain_payload else pcr(rows)
    prior_pcr = float(chain_payload.get("previous_pcr", current_pcr))
    pcr_rising = current_pcr > prior_pcr
    all_expiry_pcr = chain_payload.get("all_expiry_pcr")
    divergence = current_pcr - float(all_expiry_pcr) if all_expiry_pcr is not None else None
    oi_build = float(chain_payload.get("overnight_oi_build_pct", 0))
    expiry_score = _expiry_score(gex, vix_structure, oi_build, pcr_rising, vix_choch)

    # PCR never overrides negative GEX: rising PCR becomes bearish fuel there.
    direction = -1.0 if gex < 0 else 0.35 if gex > 0 else 0.0
    if gex < 0 and pcr_rising:
        direction = -1.0
    elif gex > 0 and pcr_rising:
        direction = min(1.0, direction + 0.25)
    if vix_structure.lower().replace("_", "-") in {"weak-low", "near-weak-low"} and vix_choch:
        direction = min(direction, -0.8)

    return LayerAScore(
        gex=gex,
        gex_regime=gex_regime,
        gamma_flip=flip,
        max_pain_level=max_pain(rows) if gex > 0 and rows else None,
        vix_structure=vix_structure,
        pcr_value=current_pcr,
        pcr_rising=pcr_rising,
        pcr_divergence=divergence,
        pcr_divergence_informational=True,
        overnight_oi_build_pct=oi_build,
        expiry_score=expiry_score,
        cascade_flag=expiry_score >= 5,
        vix_move_classification=vix_class,
        direction_value=max(-1.0, min(1.0, direction)),
    )


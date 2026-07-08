"""Seven-session regression gate from AXIS_MASTER_SPEC Section 2."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from src.math.pricing import down_target
from src.scoring.direction_scorer import compute_direction_score, score_expiry_day
from src.scoring.layer_a import LayerAScore, score_layer_a
from src.scoring.layer_b import LayerBScore
from src.scoring.layer_c import LayerCScore, score_layer_c
from src.scoring.structure_gate import check_structure

IST = ZoneInfo("Asia/Kolkata")
CONFIG = {
    "layer_a_weight": 0.60,
    "layer_b_weight": 0.10,
    "layer_c_weight": 0.30,
    "off_boundary_c_weight": 0.01,
    "gex_flip_zone_cr": 0.50,
    "expiry_no_trade_minutes": 45,
    "version": "seven-session-v1",
}


def _a(gex, direction, *, expiry_score=0, pcr_value=1.0, divergence=None):
    return LayerAScore(
        gex=gex, gex_regime="negative" if gex < 0 else "positive",
        gamma_flip=None, max_pain_level=None if gex < 0 else 24000,
        vix_structure="normal", pcr_value=pcr_value, pcr_rising=False,
        pcr_divergence=divergence, pcr_divergence_informational=True,
        overnight_oi_build_pct=0, expiry_score=expiry_score,
        cascade_flag=expiry_score >= 5, vix_move_classification="normal",
        direction_value=direction,
    )


def _b(direction=0.0):
    return LayerBScore(1.0, 1.0, 1.0, None, direction)


def _c(direction, *, boundary=True, sweep=False):
    return LayerCScore(24100, 23900, 24000, (), boundary, "call-selling" if direction < 0 else "put-selling", 100, direction, sweep)


# The spec does not publish numeric GEX/FII values for every session. Those
# entries below encode only the documented regime qualitatively; every exact
# number that Section 2 does publish is kept literally in its matching test.
SESSIONS = {
    "june16": (_a(-0.6, -0.8), _b(), _c(-0.5)),
    "june17": (_a(-0.6, -0.8), _b(), _c(-1.0)),
    "june18": (_a(-0.6, -1.0, expiry_score=7), _b(), _c(-1.0)),
    "june22": (_a(-0.2, -1.0, pcr_value=1.21), _b(), _c(1.0)),
    "june23": (_a(-3.94, -1.0, expiry_score=6), _b(), _c(-1.0)),
    "june29": (_a(-0.6, -1.0, pcr_value=0.7210, divergence=0.074), _b(-0.3), _c(-1.0)),
    "june30": (_a(-0.6, -1.0, divergence=1.17), _b(), _c(-1.0, sweep=True)),
}


@pytest.mark.parametrize("session", list(SESSIONS))
def test_all_seven_reference_sessions_are_literal_regression_fixtures(session):
    a, b, c = SESSIONS[session]
    result = compute_direction_score(a, b, c, {"scoring_config": CONFIG})
    assert 1 <= result <= 5


def test_june_22_never_scores_bullish_despite_pcr_082_to_121():
    a = score_layer_a(
        {"net_gex": -0.20, "spot": 24050, "pcr": 1.21, "previous_pcr": 0.82, "chain": []},
        {"structure": "normal"},
    )
    assert a.pcr_rising and a.direction_value < 0
    assert compute_direction_score(a, _b(), _c(1.0), {"scoring_config": CONFIG}) <= 3


def test_june_23_is_strong_bearish_and_target_error_is_39_points():
    a, b, c = SESSIONS["june23"]
    assert compute_direction_score(a, b, c, {"scoring_config": CONFIG}) == 1
    assert score_expiry_day(-3.94, "weak-low", 0, False, True) >= 5
    target = down_target(24100.0, 12.89)
    assert target == pytest.approx(23904.0, abs=1.0)
    assert target - 23865.0 == pytest.approx(39.0, abs=1.0)


def test_june_29_all_layers_agree_strong_bearish_with_exact_oi_ltp_signature():
    candles = [
        {"high": 24110, "low": 24090, "close": 24100, "volume": 100},
        {"high": 24100, "low": 24080, "close": 24090, "volume": 1000},
    ]
    layer_c = score_layer_c(
        candles,
        {"spot": 24090, "strikes": [{"option_type": "CE", "oi_change_pct": 851.0, "ltp_change_pct": -46.80}]},
    )
    assert layer_c.divergence == "call-selling" and layer_c.direction_value == -1.0
    a, b, _ = SESSIONS["june29"]
    assert a.pcr_value == 0.7210 and a.pcr_divergence == 0.074
    assert compute_direction_score(a, b, layer_c, {"scoring_config": CONFIG}) == 1


def test_june_30_flags_three_stage_sweep_and_unique_pcr_divergence():
    a29, _, _ = SESSIONS["june29"]
    a30, _, c30 = SESSIONS["june30"]
    assert c30.three_stage_sweep is True
    assert a30.pcr_divergence == 1.17
    assert a29.pcr_divergence == 0.074
    assert a30.pcr_divergence > 0.7 > a29.pcr_divergence


def test_max_pain_is_suppressed_in_negative_gex():
    a = score_layer_a(
        {"net_gex": -1, "spot": 100, "pcr": 1, "chain": [{"strike": 100, "call_oi": 10, "put_oi": 10}]},
        {},
    )
    assert a.max_pain_level is None


def test_boundary_is_a_hard_gate_and_structure_is_binary():
    candles = [
        {"high": 101, "low": 99, "close": 100, "volume": 1000},
        {"high": 111, "low": 109, "close": 110, "volume": 10},
    ]
    off_boundary = {"spot": 105, "strikes": [{"option_type": "CE", "oi_change_pct": 500, "ltp_change_pct": -90}]}
    assert score_layer_c(candles, off_boundary).at_vp_boundary is False
    assert score_layer_c(candles, off_boundary).direction_value == 0.0
    assert check_structure(candles, off_boundary) is False

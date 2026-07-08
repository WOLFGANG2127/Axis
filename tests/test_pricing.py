"""Tests for src/math/pricing.py."""

from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from src.math.pricing import (
    bs_delta,
    bs_gamma,
    bs_price,
    bs_theta_per_day,
    bs_vega,
    cascade_magnitude,
    down_target,
    expected_value,
    gamma_flip_level,
    kelly_fraction,
    max_pain,
    net_gex,
    pcr,
    theta_between,
    transaction_cost,
    vix_expected_move,
    years_to_expiry,
)

IST = ZoneInfo("Asia/Kolkata")


def test_kelly_fraction_correct_formula_not_doubled():
    # p=0.6, avg_gain=200, avg_loss=100 -> b=2.0 -> f*=0.6-0.4/2.0=0.4
    assert kelly_fraction(0.6, 200.0, 100.0) == pytest.approx(0.4)


def test_years_to_expiry_anchors_to_1530_ist_not_midnight():
    expiry = date(2025, 6, 26)
    one_minute_before = datetime(2025, 6, 26, 15, 29, tzinfo=IST)
    remaining = years_to_expiry(expiry, one_minute_before, expiry_time=time(15, 30))
    one_day = 1.0 / 365.0
    assert 0.0 < remaining < one_day / 24.0
    assert remaining > 0.0


def test_june_23_down_target_reproduces_documented_error():
    spot = 24100.0
    vix = 12.89
    target = down_target(spot, vix)
    assert target == pytest.approx(23904.0, abs=1.0)
    assert target - 23865.0 == pytest.approx(39.0, abs=1.0)


def test_vix_expected_move_formula():
    spot = 24000.0
    vix = 13.0
    assert vix_expected_move(spot, vix) == pytest.approx(spot * (vix / 100.0) / (252 ** 0.5))


def test_black_scholes_reference_values_and_put_call_parity():
    # Standard reference case: S=K=100, r=5%, sigma=20%, T=1 year.
    call = bs_price(100.0, 100.0, 0.05, 0.20, 1.0, "call")
    put = bs_price(100.0, 100.0, 0.05, 0.20, 1.0, "put")
    assert call == pytest.approx(10.4506, abs=1e-4)
    assert put == pytest.approx(5.5735, abs=1e-4)
    assert call - put == pytest.approx(100.0 - 100.0 * (2.718281828459045 ** -0.05))


def test_black_scholes_greeks_reference_values():
    assert bs_delta(100.0, 100.0, 0.05, 0.20, 1.0, "CE") == pytest.approx(0.63683, abs=1e-5)
    assert bs_delta(100.0, 100.0, 0.05, 0.20, 1.0, "PE") == pytest.approx(-0.36317, abs=1e-5)
    assert bs_gamma(100.0, 100.0, 0.05, 0.20, 1.0) == pytest.approx(0.018762, abs=1e-6)
    assert bs_theta_per_day(100.0, 100.0, 0.05, 0.20, 1.0, "call") == pytest.approx(-0.017573, abs=1e-6)
    assert bs_vega(100.0, 100.0, 0.05, 0.20, 1.0) == pytest.approx(0.37524, abs=1e-5)


def test_pricing_rejects_non_positive_time_consistently():
    for function, args in (
        (bs_price, (100.0, 100.0, 0.05, 0.2, 0.0, "call")),
        (bs_gamma, (100.0, 100.0, 0.05, 0.2, 0.0)),
        (bs_theta_per_day, (100.0, 100.0, 0.05, 0.2, 0.0, "put")),
        (bs_vega, (100.0, 100.0, 0.05, 0.2, 0.0)),
    ):
        with pytest.raises(ValueError, match="t must be positive"):
            function(*args)


def test_theta_between_is_non_linear_window_decay():
    decay = theta_between(24000.0, 24000.0, 0.06, 0.15, 2 / 365, 1 / 365, "call")
    assert decay < 0.0
    with pytest.raises(ValueError, match="t_later"):
        theta_between(24000.0, 24000.0, 0.06, 0.15, 1 / 365, 2 / 365, "call")


def test_chain_metrics_and_percentage_iv_normalization():
    call_heavy = [
        {"strikePrice": 90, "callOI": 100, "putOI": 10, "callIV": 20, "putIV": 20},
        {"strikePrice": 100, "callOI": 200, "putOI": 20, "callIV": 20, "putIV": 20},
        {"strikePrice": 110, "callOI": 100, "putOI": 10, "callIV": 20, "putIV": 20},
    ]
    assert net_gex(call_heavy, 100.0, 0.05, 30 / 365, lot_size=65) > 0.0
    assert pcr(call_heavy) == pytest.approx(0.1)


def test_gamma_flip_recomputes_gex_across_hypothetical_spots():
    chain = [
        {"strike": 90, "call_oi": 1000, "put_oi": 0, "call_iv": 0.2, "put_iv": 0.2},
        {"strike": 110, "call_oi": 0, "put_oi": 1000, "call_iv": 0.2, "put_iv": 0.2},
    ]
    flip = gamma_flip_level(chain, 100.0, 0.0, 30 / 365, lot_size=65, search_pct=0.2)
    assert 95.0 < flip < 105.0


def test_max_pain_uses_total_writer_payout():
    chain = [
        {"strike": 90, "call_oi": 10, "put_oi": 100},
        {"strike": 100, "call_oi": 100, "put_oi": 100},
        {"strike": 110, "call_oi": 100, "put_oi": 10},
    ]
    assert max_pain(chain) == 100.0


def test_ev_cost_and_unverified_cascade_formulas():
    # STT=6.25, brokerage=40, exchange=35, GST-on-brokerage=7.20.
    assert transaction_cost(10_000.0) == pytest.approx(88.45)
    assert expected_value(0.6, 200.0, 100.0, 10.0) == pytest.approx(70.0)
    assert cascade_magnitude(-3_940_000.0, 0.01) == pytest.approx(39_400.0)


def test_invalid_financial_inputs_fail_loudly():
    with pytest.raises(ValueError):
        transaction_cost(-1.0)
    with pytest.raises(ValueError):
        expected_value(1.1, 100.0, 50.0, 5.0)
    with pytest.raises(ValueError):
        kelly_fraction(0.5, 0.0, 100.0)

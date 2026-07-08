"""Step 7 GVOF deterministic checklist tests."""

from __future__ import annotations

from datetime import datetime
from math import isclose
from zoneinfo import ZoneInfo

from src.graph.state import AxisState
from src.math.pricing import vix_expected_move
from src.strategies.gvof import GVOFStrategy

IST = ZoneInfo("Asia/Kolkata")


def _state(**overrides):
    context = {
        "now": datetime(2026, 6, 29, 11, 0, tzinfo=IST),
        "net_gex": 2.0,
        "fii_long_short_ratio": 0.8,
        "ib_high": 24120,
        "ib_low": 24005,
        "spot": 24090,
        "vix": 13.87,
        "signal_direction": "bearish",
        "wick_beyond_786": True,
        "closed_back_in_zone": True,
        "choch_confirmed": True,
        "sweep_extreme": 24100,
    }
    context.update(overrides)
    return AxisState(
        symbol="NIFTY",
        cycle_timestamp=context["now"],
        market_context=context,
        direction_score=1,
        structure_confirmed=True,
    )


def test_golden_zone_plan_has_half_exit_and_vix_target():
    result = GVOFStrategy().check_conditions(_state())
    assert result["passed"] is True
    assert result["mode"] == "golden-zone-reversal"
    assert result["target_1"] == 23990
    assert result["target_1_exit_pct"] == 50
    assert result["move_stop_to_breakeven_at_t1"] is True
    assert isclose(result["stop_distance"], 6.9)
    assert isclose(result["target_2"], 24090 - vix_expected_move(24090, 13.87))


def test_negative_gex_abandons_fibonacci_and_follows_cascade():
    state = _state(net_gex=-3.94, spot=24100, vix=12.89, cascade_confirmed=True)
    result = GVOFStrategy().check_conditions(state)
    assert result["passed"] is True
    assert result["mode"] == "negative-gex-cascade"
    assert result["golden_zone_abandoned"] is True
    assert isclose(result["target_2"], 24100 - vix_expected_move(24100, 12.89))


def test_negative_gex_without_cascade_confirmation_is_blocked():
    result = GVOFStrategy().check_conditions(_state(net_gex=-1.0))
    assert result["passed"] is False
    assert result["reason"] == "NEGATIVE_GEX_CASCADE_UNCONFIRMED"


def test_ib_below_fifty_points_is_non_negotiable_no_trade():
    result = GVOFStrategy().check_conditions(_state(ib_high=24040, ib_low=24000))
    assert result["passed"] is False
    assert result["reason"] == "IB_RANGE_BELOW_50_POINTS"


def test_no_new_entry_after_two_pm():
    result = GVOFStrategy().check_conditions(
        _state(now=datetime(2026, 6, 29, 14, 1, tzinfo=IST))
    )
    assert result["passed"] is False
    assert result["reason"] == "NO_NEW_ENTRIES_AFTER_1400"


def test_expiry_morning_requires_judas_sweep_and_choch():
    result = GVOFStrategy().check_conditions(
        _state(
            now=datetime(2026, 6, 30, 9, 50, tzinfo=IST),
            is_expiry_day=True,
            judas_sweep=False,
        )
    )
    assert result["passed"] is False
    assert result["reason"] == "EXPIRY_JUDAS_SWEEP_OR_CHOCH_MISSING"

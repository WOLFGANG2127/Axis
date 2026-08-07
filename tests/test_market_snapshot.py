"""D-001 / D-045 / D-047 proof tests for fetch_and_score_market_data.

Four tests required by the task spec:
1. Mock a realistic Dhan response → assert layer_a/layer_b trace back to mocked input.
2. Mock a stale-timestamp payload → assert STALE_DATA fires before any scoring runs.
3. Mock a payload missing a required field → assert KeyError / ValidationError (extra='forbid').
4. Mock a FAILED FII fetch → confirm cycle_summaries.errors entry, distinct from neutral.

Rules:
- Mock the network layer (unittest.mock). Never hit live Dhan/NSE APIs.
- Load fixtures from tests/fixtures/dhan_sample.json and tests/fixtures/nse_sample.csv.
- No realistic-looking tokens in test files.
"""

from __future__ import annotations

import json
import time
import unittest.mock as mock
from datetime import datetime, timedelta, timezone
from email.utils import formatdate
from pathlib import Path

import pytest

# ── Fixture loaders ──────────────────────────────────────────────────────────

FIXTURES = Path(__file__).parent / "fixtures"
DHAN_FIXTURE = FIXTURES / "dhan_sample.json"
NSE_FIXTURE = FIXTURES / "nse_sample.csv"


def _dhan_raw() -> dict:
    if not DHAN_FIXTURE.exists():
        pytest.fail(
            f"FIXTURE MISSING: {DHAN_FIXTURE}\n"
            "Per task spec (FIXTURE RULE), do not hand-type mock data. "
            "Stop and post in communicator."
        )
    with DHAN_FIXTURE.open(encoding="utf-8-sig") as fh:
        return json.load(fh)


def _nse_csv() -> str:
    if not NSE_FIXTURE.exists():
        pytest.fail(
            f"FIXTURE MISSING: {NSE_FIXTURE}\n"
            "Per task spec (FIXTURE RULE), do not hand-type mock data. "
            "Stop and post in communicator."
        )
    return NSE_FIXTURE.read_text(encoding="utf-8")


def _fresh_date_header(now_utc: datetime | None = None) -> str:
    """Return an HTTP Date header string that is ≤1 second old."""
    t = (now_utc or datetime.now(timezone.utc)).timestamp()
    return formatdate(t, usegmt=True)


# ── Test 1: Realistic Dhan response — layer_a/b trace back to mocked input ──

def test_scoring_uses_fixture_data_not_defaults():
    """Layer A and B values must derive from the fixture, not silently neutral defaults."""
    from src.data.market_snapshot import fetch_and_score_market_data
    from src.data.nse_fetcher import compute_long_short_ratio

    now_utc = datetime.now(timezone.utc)
    nse_csv_text = _nse_csv()
    fii_env = compute_long_short_ratio(nse_csv_text)

    ctx = fetch_and_score_market_data(
        "NIFTY",
        _now_utc=now_utc,
        _dhan_response_headers={"Date": _fresh_date_header(now_utc)},
        _dhan_raw=_dhan_raw(),
        _vix_data={"structure": "normal", "change_pct": 0.0, "spot_move_pct": 0.0},
        _fii_envelope=fii_env,
        _candle_data=None,
    )

    # last_price must come from the fixture (24512.50), not a default
    assert ctx.last_price == pytest.approx(24512.50), (
        f"last_price {ctx.last_price} does not match fixture value 24512.50 — "
        "scoring is not reading from the mocked input"
    )
    # PCR computed from fixture's oc data — two strikes, each with CE/PE OI > 0
    # put_oi total = 2100300+1890000, call_oi total = 1254000+3400200 → PCR > 0
    assert ctx.layer_a.pcr_value > 0

    # FII futures ratio from NSE fixture: FII futures_long=24761, futures_short=197874
    expected_futures_ratio = 24761 / 197874
    assert ctx.layer_b.index_futures_ratio == pytest.approx(expected_futures_ratio, rel=1e-3)

    # direction_score must be a valid integer
    assert isinstance(ctx.direction_score, int)
    assert 1 <= ctx.direction_score <= 5

    # Proves the pipeline ran (not silently None)
    assert ctx.layer_a is not None
    assert ctx.layer_b is not None
    assert not ctx.fii_fetch_failed


# ── Test 2: Stale Dhan timestamp → STALE_DATA fires BEFORE scoring ──────────

def test_stale_dhan_header_raises_before_any_scoring():
    """StaleDataError must be raised BEFORE score_layer_a is called when Date header is >15 min old.

    The test runner's own clock is explicitly excluded — we inject 'now_utc' so the test
    is deterministic regardless of when it runs.
    """
    from src.data.market_snapshot import fetch_and_score_market_data, StaleDataError

    fake_server_time = datetime(2026, 8, 7, 6, 0, 0, tzinfo=timezone.utc)
    # Inject 'now' as 30 minutes after the server time → gap=1800s > 900s limit
    now_utc = fake_server_time + timedelta(minutes=30)
    stale_header = formatdate(fake_server_time.timestamp(), usegmt=True)

    scoring_called = {"called": False}

    with mock.patch("src.scoring.layer_a.score_layer_a", wraps=None) as mock_score:
        def _track(*a, **kw):
            scoring_called["called"] = True
            # Should never reach here
            raise AssertionError("score_layer_a was called despite stale data")

        mock_score.side_effect = _track

        with pytest.raises(StaleDataError, match="STALE_DATA"):
            fetch_and_score_market_data(
                "NIFTY",
                _now_utc=now_utc,
                _dhan_response_headers={"Date": stale_header},
                _dhan_raw=_dhan_raw(),
                _vix_data={"structure": "normal", "change_pct": 0.0, "spot_move_pct": 0.0},
                _fii_envelope=None,
                _candle_data=None,
            )

    # The mock intercepts at the module level; if score_layer_a was invoked first,
    # _track would have raised AssertionError instead of StaleDataError propagating.
    # Reaching here means StaleDataError was raised before scoring.
    assert not scoring_called["called"]


# ── Test 3a: Missing Dhan field → KeyError (never silently defaults) ─────────

def test_missing_dhan_last_price_raises_key_error():
    """_extract_dhan_fields must raise KeyError when 'last_price' is absent, not default to 0."""
    from src.data.market_snapshot import _extract_dhan_fields

    broken = {
        "data": {
            # 'last_price' deliberately omitted
            "oc": {"24500.000000": {"ce": {"oi": 1000}, "pe": {"oi": 2000}}}
        }
    }
    with pytest.raises(KeyError, match="last_price"):
        _extract_dhan_fields(broken)


# ── Test 3b: Extra field on ScoredMarketContext → ValidationError ─────────

def test_scored_market_context_extra_field_raises_validation_error():
    """ScoredMarketContext (extra='forbid') must raise ValidationError on an unknown field."""
    from pydantic import ValidationError

    from src.data.market_snapshot import ScoredMarketContext, _extract_dhan_fields
    from src.data.nse_fetcher import compute_long_short_ratio
    from src.scoring.layer_a import score_layer_a
    from src.scoring.layer_b import score_layer_b
    from src.scoring.layer_c import score_layer_c

    fields = _extract_dhan_fields(_dhan_raw())
    vix = {"structure": "normal", "change_pct": 0.0, "spot_move_pct": 0.0}
    layer_a = score_layer_a(fields, vix)
    layer_b = score_layer_b(compute_long_short_ratio(_nse_csv()))
    candle = [{"high": fields["last_price"], "low": fields["last_price"],
               "close": fields["last_price"], "volume": 0}]
    layer_c = score_layer_c(candle, fields)

    with pytest.raises(ValidationError):
        ScoredMarketContext(
            symbol="NIFTY",
            last_price=fields["last_price"],
            option_chain_raw=fields,
            vix_data=vix,
            fii_ratios=compute_long_short_ratio(_nse_csv()),
            layer_a=layer_a,
            layer_b=layer_b,
            layer_c=layer_c,
            direction_score=3,
            fii_fetch_failed=False,
            ROGUE_EXTRA_FIELD="extra='forbid' must catch this",  # type: ignore[call-arg]
        )


# ── Test 4: FAILED FII fetch → cycle_summaries.errors entry ─────────────────

def test_failed_fii_fetch_logs_degraded_not_neutral():
    """When FII fetch raises (not when it computes genuine 0.0), the cycle_errors list
    must contain {'layer': 'B', 'reason': 'fii_fetch_failed', 'defaulted': True}.
    This is STRUCTURALLY distinct from a genuine neutral (fii_fetch_failed=False).
    """
    from src.data.market_snapshot import fetch_and_score_market_data

    now_utc = datetime.now(timezone.utc)
    cycle_errors: list[dict] = []

    # Patch the fetch_participant_oi import INSIDE market_snapshot's namespace
    with mock.patch(
        "src.data.market_snapshot.fetch_participant_oi",
        side_effect=RuntimeError("simulated FII network failure"),
    ):
        ctx = fetch_and_score_market_data(
            "NIFTY",
            _now_utc=now_utc,
            _dhan_response_headers={"Date": _fresh_date_header(now_utc)},
            _dhan_raw=_dhan_raw(),
            _vix_data={"structure": "normal", "change_pct": 0.0, "spot_move_pct": 0.0},
            _fii_envelope=None,   # Force the live FII fetch path
            _candle_data=None,
            _cycle_errors=cycle_errors,
        )

    # Flag must be True — proves the fallback was due to failure, not genuine 0.0
    assert ctx.fii_fetch_failed is True

    # cycle_errors must have the degraded-logging entry
    assert cycle_errors, "cycle_errors is empty after FII failure — degraded logging not implemented"
    error_entry = next(
        (e for e in cycle_errors
         if e.get("layer") == "B" and e.get("reason") == "fii_fetch_failed"),
        None,
    )
    assert error_entry is not None, (
        f"Expected entry with layer='B', reason='fii_fetch_failed' in cycle_errors. Got: {cycle_errors}"
    )
    assert error_entry.get("defaulted") is True, (
        f"'defaulted' must be True in the error entry. Got: {error_entry}"
    )

    # Sanity: layer_b still has a result (fallback to ratio=1.0 defaults)
    assert ctx.layer_b is not None

"""Step 5 journal, sample-floor, and risk-sizing tests."""

from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from src.config.constants import get_lot_size
from src.journal.accuracy_engine import get_historical_stats, get_position_sizing_stats
from src.journal.outcome_recorder import record_outcome
from src.journal.position_sizer import InsufficientCapitalError, calculate_position

IST = ZoneInfo("Asia/Kolkata")


class Query:
    def __init__(self, db, table):
        self.db, self.name = db, table
        self.filters = []
        self.ordering = None
        self.limit_count = None
        self.inserted = None

    def select(self, *_): return self
    def eq(self, key, value): self.filters.append(("eq", key, value)); return self
    def gte(self, key, value): self.filters.append(("gte", key, value)); return self
    def lt(self, key, value): self.filters.append(("lt", key, value)); return self
    def order(self, key, desc=False): self.ordering = (key, desc); return self
    def limit(self, count): self.limit_count = count; return self
    def insert(self, row): self.inserted = row; return self

    def execute(self):
        if self.inserted is not None:
            self.db.tables[self.name].append(dict(self.inserted))
            return SimpleNamespace(data=[dict(self.inserted)])
        rows = [dict(row) for row in self.db.tables.get(self.name, [])]
        for operation, key, value in self.filters:
            if operation == "eq": rows = [row for row in rows if row.get(key) == value]
            elif operation == "gte": rows = [row for row in rows if row.get(key) is not None and str(row[key]) >= str(value)]
            elif operation == "lt": rows = [row for row in rows if row.get(key) is not None and str(row[key]) < str(value)]
        if self.ordering:
            key, desc = self.ordering
            rows.sort(key=lambda row: str(row.get(key, "")), reverse=desc)
        if self.limit_count is not None: rows = rows[:self.limit_count]
        return SimpleNamespace(data=rows)


class FakeDB:
    def __init__(self, **tables): self.tables = {name: list(rows) for name, rows in tables.items()}
    def table(self, name): self.tables.setdefault(name, []); return Query(self, name)


def _portfolio():
    return {"id": "vp1", "strategy_name": "GVOF", "symbol": "NIFTY", "current_capital": 300000, "initial_capital": 300000, "weekly_loss_limit_pct": 0.03}


def test_accuracy_floor_hides_one_hundred_percent_on_one_trade():
    low = {"direction_score_bin": "1", "structure_gate_passed": True, "strategy_name": "GVOF", "symbol": "NIFTY", "vix_classification": "fear-cascade", "win_rate": 1.0, "avg_gain": 500, "avg_loss": 100, "sample_count": 1, "computed_date": "2026-07-08"}
    db = FakeDB(accuracy_log=[low])
    assert get_historical_stats("1", True, "GVOF", "fear-cascade", db=db) is None
    low["sample_count"] = 15
    db = FakeDB(accuracy_log=[low])
    assert get_historical_stats("1", True, "GVOF", "fear-cascade", db=db)["sample_count"] == 15


def test_cold_start_uses_flat_one_percent_risk():
    db = FakeDB(virtual_portfolios=[_portfolio()], paper_trades=[], accuracy_log=[])
    lot_size = get_lot_size("NIFTY")
    result = calculate_position("GVOF", "NIFTY", 100, 90, lot_size, db=db, now=datetime(2026, 7, 8, 12, tzinfo=IST))
    assert result == {"lots": 4, "capital_deployed": 26000.0, "risk_rupees": 2600.0}


def test_mature_sizing_uses_half_kelly_capped_at_two_percent():
    stats = {"strategy_name": "GVOF", "symbol": "NIFTY", "win_rate": 0.6, "avg_gain": 200, "avg_loss": 100, "sample_count": 40, "computed_date": "2026-07-08"}
    db = FakeDB(virtual_portfolios=[_portfolio()], paper_trades=[], accuracy_log=[stats])
    # Full Kelly=.4, half=.2, capped to .02 => risk budget 6000.
    lot_size = get_lot_size("NIFTY")
    result = calculate_position("GVOF", "NIFTY", 100, 90, lot_size, db=db, now=datetime(2026, 7, 8, 12, tzinfo=IST))
    assert result["lots"] == 9 and result["risk_rupees"] == 5850.0


def test_strategy_scoped_weekly_limit_blocks_immediately():
    monday = datetime(2026, 7, 6, 10, tzinfo=IST).isoformat()
    losses = [{"virtual_portfolio_id": "vp1", "exit_time": monday, "pnl_rupees": -9000}]
    db = FakeDB(virtual_portfolios=[_portfolio()], paper_trades=losses, accuracy_log=[])
    lot_size = get_lot_size("NIFTY")
    with pytest.raises(InsufficientCapitalError, match="weekly loss limit"):
        calculate_position("GVOF", "NIFTY", 100, 90, lot_size, db=db, now=datetime(2026, 7, 8, 12, tzinfo=IST))


def test_outcome_recorder_samples_four_horizons_and_taxonomizes_loss():
    exit_time = datetime(2026, 7, 8, 12, tzinfo=IST)
    candles = [
        {"symbol": "NIFTY", "timestamp": (exit_time + timedelta(minutes=minutes)).isoformat(), "close": 24000 - minutes, "vix_change_pct": 9, "spot_move_pct": -1}
        for minutes in (15, 30, 60, 120)
    ]
    trade = {"id": "t1", "symbol": "NIFTY", "exit_time": exit_time.isoformat(), "exit_price": 100, "pnl_rupees": -500, "pre_trade_checklist": {"theta_viable": False}}
    db = FakeDB(paper_trades=[trade], cached_candles=candles, trade_outcomes=[])
    row = record_outcome("t1", db=db)
    assert [row[f"price_{minutes}m"] for minutes in (15, 30, 60, 120)] == [23985, 23970, 23940, 23880]
    assert row["post_exit_vix_classification"] == "fear-cascade"
    assert row["outcome_category"] == "TIME_DECAY_MISJUDGED"

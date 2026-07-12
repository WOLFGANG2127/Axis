"""Strategy #2: Wyckoff Mean Reversion tests."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

from src.graph.state import AxisState


class FakeTable:
    def __init__(self, db, name: str):
        self.db = db
        self.name = name
        self.filters = []
        self.payload = None
        self._is_update = False

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self.filters.append((key, value))
        return self

    def in_(self, key, values):
        self.filters.append((key, tuple(values)))
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def insert(self, payload):
        self.payload = dict(payload)
        return self

    def update(self, payload):
        self.payload = dict(payload)
        self._is_update = True
        return self

    def execute(self):
        if self.payload is not None and self._is_update:
            rows = self._filtered_rows()
            for row in rows:
                row.update(self.payload)
            self.db.updates.append((self.name, dict(self.payload), list(self.filters)))
            return SimpleNamespace(data=rows)
        if self.payload is not None:
            self.db.tables.setdefault(self.name, []).append(dict(self.payload))
            self.db.inserts.append((self.name, dict(self.payload)))
            return SimpleNamespace(data=[dict(self.payload)])
        return SimpleNamespace(data=[dict(row) for row in self._filtered_rows()])

    def _filtered_rows(self):
        rows = self.db.tables.get(self.name, [])
        for key, value in self.filters:
            if isinstance(value, tuple):
                rows = [row for row in rows if row.get(key) in value]
            else:
                rows = [row for row in rows if row.get(key) == value]
        return rows


class FakeDb:
    def __init__(self):
        self.tables = {"strategies": [], "strategy_configs": [], "strategy_config_changelog": []}
        self.inserts = []
        self.updates = []

    def table(self, name: str):
        return FakeTable(self, name)


def _bullish_state(symbol: str = "NIFTY") -> AxisState:
    candles = [
        {"timestamp": f"2026-07-14T09:{15 + i:02d}:00+05:30", "open": 100 + i, "high": 102 + i, "low": 99 + i, "close": 101 + i, "volume": 1000}
        for i in range(5)
    ]
    candles.append({"timestamp": "2026-07-14T09:45:00+05:30", "open": 106, "high": 108, "low": 95, "close": 104, "volume": 1800})
    return AxisState(
        symbol=symbol,
        structure_confirmed=True,
        market_context={
            "now": "2026-07-14T09:50:00+05:30",
            "spot": 104,
            "candles": candles,
            "value_area_low": 100,
            "value_area_high": 112,
            "volume_profile_poc": 108,
            "wyckoff_spring": True,
            "reclaimed_value_area": True,
            "choch_confirmed": True,
            "delta_absorption": True,
            "sweep_low": 95,
            "is_expiry_day": symbol == "BANKNIFTY",
        },
    )


def test_wyckoff_mean_reversion_bullish_spring_passes():
    from src.strategies.wyckoff_mean_reversion import WyckoffMeanReversionStrategy

    result = WyckoffMeanReversionStrategy().check_conditions(_bullish_state())

    assert result["passed"] is True
    assert result["strategy_id"] == "wyckoff_mean_reversion"
    assert result["direction"] == "bullish"
    assert result["mode"] == "wyckoff-spring"
    assert result["price_zone"] == "spring-value-area-reclaim"
    assert result["target_1_exit_pct"] == 50


def test_wyckoff_blocks_when_structure_gate_fails():
    from src.strategies.wyckoff_mean_reversion import WyckoffMeanReversionStrategy

    state = _bullish_state()
    state = state.model_copy(update={"structure_confirmed": False})
    result = WyckoffMeanReversionStrategy().check_conditions(state)

    assert result["passed"] is False
    assert result["reason"] == "STRUCTURE_GATE_FAILED"


def test_wyckoff_banknifty_expiry_logic_is_exercised_before_evaluation():
    from datetime import date

    from src.data.event_calendar import is_expiry_day
    from src.strategies.wyckoff_mean_reversion import WyckoffMeanReversionStrategy

    assert is_expiry_day("BANKNIFTY", date(2026, 7, 28)) is True
    assert is_expiry_day("BANKNIFTY", date(2026, 7, 21)) is False

    result = WyckoffMeanReversionStrategy().check_conditions(_bullish_state("BANKNIFTY"))
    assert result["passed"] is True


def test_wyckoff_source_passes_ast_scanner():
    from src.strategies.security import scan_strategy_file

    result = scan_strategy_file("src/strategies/wyckoff_mean_reversion.py")

    assert result.passed, result.issues


def test_wyckoff_yaml_upload_workflow_forces_draft_then_activates_with_shadow_gates():
    import yaml
    from src.strategies.definition import StrategyDefinition
    from src.strategies.review_workflow import (
        register_uploaded_strategy_draft,
        transition_strategy_status,
    )

    db = FakeDb()
    raw = yaml.safe_load(Path("src/strategies/definitions/wyckoff_mean_reversion.yaml").read_text(encoding="utf-8"))
    definition = StrategyDefinition.model_validate(raw)

    draft = register_uploaded_strategy_draft(definition, db=db, changed_by="codex")
    pending = transition_strategy_status(definition.strategy_id, "pending_review", db=db, changed_by="codex")
    active = transition_strategy_status(
        definition.strategy_id,
        "active",
        db=db,
        source_path="src/strategies/wyckoff_mean_reversion.py",
        changed_by="trader_manual_review",
    )

    assert draft["status"] == "draft"
    assert pending.new_status == "pending_review"
    assert active.new_status == "active"
    assert active.scan_passed is True
    status_logs = [row for row in db.tables["strategy_config_changelog"] if row["field_changed"] == "status"]
    assert status_logs[-1]["details"]["security_scan"] == "passed"
    assert set(status_logs[-1]["details"]["governance_gate_modes"].values()) == {"SHADOW"}


def test_registry_loads_active_wyckoff_strategy_from_database():
    from src.strategies import registry

    db = FakeDb()
    db.tables["strategies"].append(
        {
            "strategy_id": "wyckoff_mean_reversion",
            "display_name": "Wyckoff Mean Reversion",
            "version": 1,
            "status": "active",
            "source": "uploaded",
        }
    )
    db.tables["strategy_configs"].append(
        {
            "strategy_id": "wyckoff_mean_reversion",
            "symbol": "NIFTY",
            "rr_floor": 2.0,
        }
    )

    registry.reset_strategy_registry_cache()
    try:
        snapshot = registry.load_strategy_registry(force=True, db=db)
    finally:
        registry.reset_strategy_registry_cache()

    assert [strategy.strategy_id for strategy in snapshot.strategies] == ["wyckoff_mean_reversion"]
    assert snapshot.configs["wyckoff_mean_reversion"]["strategy_name"] == "Wyckoff Mean Reversion"


def test_graph_runs_gvof_and_wyckoff_in_same_cycle_without_cross_contamination():
    from src.graph import nodes
    from src.strategies.base import BaseStrategy
    from src.strategies.wyckoff_mean_reversion import WyckoffMeanReversionStrategy

    class PassiveGVOF(BaseStrategy):
        strategy_id = "gvof"
        name = "GVOF"

        def check_conditions(self, state):
            return {"passed": True, "strategy_id": self.strategy_id, "strategy_name": self.name, "direction": "bearish"}

    nodes.register_strategies([PassiveGVOF(), WyckoffMeanReversionStrategy()])
    try:
        result = asyncio.run(nodes.strategy_activation_node(_bullish_state()))
    finally:
        nodes.reset_strategies()

    assert [candidate["strategy_id"] for candidate in result["candidate_signals"]] == [
        "gvof",
        "wyckoff_mean_reversion",
    ]
    assert result["candidate_signals"][0]["direction"] == "bearish"
    assert result["candidate_signals"][1]["direction"] == "bullish"


def test_ast_scanner_accepts_legitimate_stdlib_decimal_import_not_hardcoded_allowlist():
    from src.strategies.security import scan_strategy_source

    result = scan_strategy_source(
        """
from decimal import Decimal
from src.strategies.base import BaseStrategy

class DecimalSizingStrategy(BaseStrategy):
    strategy_id = 'decimal_sizing'
    name = 'DECIMAL_SIZING'

    def check_conditions(self, state):
        threshold = Decimal('2.0')
        if threshold > Decimal('1.5'):
            return {'passed': False, 'strategy_id': self.strategy_id, 'strategy_name': self.name}
        return {'passed': False, 'strategy_id': self.strategy_id, 'strategy_name': self.name}
"""
    )

    assert result.passed, result.issues


def test_wyckoff_seed_migration_registers_active_strategy_with_shadow_gate_changelog():
    sql = Path("migrations/022_seed_wyckoff_mean_reversion_strategy.sql").read_text(encoding="utf-8")

    assert "'wyckoff_mean_reversion'" in sql
    assert "'active'" in sql
    assert "'NIFTY'" in sql and "'BANKNIFTY'" in sql
    assert "strategy_config_changelog" in sql
    assert '"DAILY_LOSS_BREAKER": "SHADOW"' in sql
    assert '"RR_FILTER": "SHADOW"' in sql
    assert '"CROSS_SYMBOL_CORRELATION": "SHADOW"' in sql

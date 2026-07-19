"""Database-backed active strategy registry."""
from __future__ import annotations
import importlib
from dataclasses import dataclass
from typing import Any
from src.strategies.base import BaseStrategy

@dataclass(frozen=True)
class StrategyRegistrySnapshot:
    strategies: list[BaseStrategy]
    configs: dict[str, dict]

_CACHE: StrategyRegistrySnapshot | None = None

def reset_strategy_registry_cache() -> None:
    global _CACHE
    _CACHE = None

def _class_name(strategy_id: str) -> str:
    return ''.join(part.capitalize() for part in strategy_id.split('_')) + 'Strategy'

def load_strategy_registry(*, force: bool = False, db: Any | None = None) -> StrategyRegistrySnapshot:
    global _CACHE
    if _CACHE is not None and not force:
        return _CACHE
    if db is None:
        from src.database.supabase import get_supabase_client
        db = get_supabase_client()
    rows = db.table('strategies').select('*').eq('status', 'active').execute().data or []
    strategies, configs = [], {}
    for row in rows:
        sid = str(row['strategy_id']).lower()
        module = importlib.import_module(f'src.strategies.{sid}')
        instance = getattr(module, _class_name(sid))()
        if not isinstance(instance, BaseStrategy):
            raise TypeError(f'{sid} must inherit BaseStrategy')
        strategies.append(instance)
    for row in db.table('strategy_configs').select('*').execute().data or []:
        configs[str(row['strategy_id']).lower()] = dict(row)
    for strategy in strategies:
        configs.setdefault(strategy.strategy_id, {'strategy_id': strategy.strategy_id})
        configs[strategy.strategy_id].setdefault('strategy_name', strategy.name)
    _CACHE = StrategyRegistrySnapshot(strategies, configs)
    return _CACHE

"""Abstract strategy plugin contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.graph.state import AxisState


class BaseStrategy(ABC):
    """A self-contained, deterministic strategy checklist."""

    @abstractmethod
    def check_conditions(self, state: AxisState) -> dict:
        """Return at least ``passed`` and ``strategy_name``."""

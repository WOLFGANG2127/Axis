"""Tier 1 strategy definition contracts."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

StrategyStatus = Literal["draft", "pending_review", "active", "disabled"]
StrategySource = Literal["built_in", "uploaded"]


class StrategyRiskConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rr_floor: float = Field(default=2.0, gt=0)
    stop_buffer_pct: float = Field(default=0.15, ge=0)
    position_size_pct_cap: float = Field(default=2.0, gt=0)
    margin_buffer_pct: float = Field(default=15.0, ge=0)


class StrategyAlertConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    template: str = "default"
    include_sections: list[str] = Field(default_factory=list)


class StrategyDefinition(BaseModel):
    """Validated Tier 1 YAML contract for uploaded/built-in strategies."""
    model_config = ConfigDict(extra="forbid")
    strategy_id: str
    display_name: str
    version: int = Field(default=1, ge=1)
    symbols: list[str]
    status: StrategyStatus = "draft"
    source: StrategySource = "uploaded"
    risk: StrategyRiskConfig = Field(default_factory=StrategyRiskConfig)
    entry_parameters: dict[str, Any] = Field(default_factory=dict)
    paper_capital_allocated: float = Field(default=100000.0, ge=0)
    required_indicators: list[str] = Field(default_factory=list)
    alert: StrategyAlertConfig = Field(default_factory=StrategyAlertConfig)

    @field_validator("strategy_id")
    @classmethod
    def _slug(cls, value: str) -> str:
        import re
        if not re.fullmatch(r"[a-z][a-z0-9_]*", value):
            raise ValueError("strategy_id must be a lowercase slug")
        return value

    @field_validator("symbols")
    @classmethod
    def _symbols(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("at least one symbol is required")
        normalized = [item.upper() for item in value]
        unknown = sorted(set(normalized) - {"NIFTY", "BANKNIFTY"})
        if unknown:
            raise ValueError(f"unsupported symbols: {', '.join(unknown)}")
        return normalized

    def config_rows(self) -> list[dict[str, Any]]:
        return [{"strategy_id": self.strategy_id, "symbol": symbol, "rr_floor": self.risk.rr_floor, "stop_buffer_pct": self.risk.stop_buffer_pct, "position_size_pct_cap": self.risk.position_size_pct_cap, "paper_capital_allocated": self.paper_capital_allocated, "alert_template": self.alert.template, "required_indicators": list(self.required_indicators), "entry_parameters": dict(self.entry_parameters), "margin_buffer_pct": self.risk.margin_buffer_pct} for symbol in self.symbols]

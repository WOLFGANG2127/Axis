"""Strategy upload/review workflow for Phase 5."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from src.governance.gate_policy import new_strategy_gate_modes
from src.strategies.definition import StrategyDefinition
from src.strategies.security import StrategySecurityError, scan_strategy_file

DRAFT, PENDING_REVIEW, ACTIVE, DISABLED = "draft", "pending_review", "active", "disabled"
ALLOWED_CONFIG_FIELDS = {"rr_floor", "stop_buffer_pct", "position_size_pct_cap", "paper_capital_allocated", "alert_template", "required_indicators", "entry_parameters", "margin_buffer_pct"}

@dataclass(frozen=True)
class StrategyTransitionResult:
    strategy_id: str; old_status: str; new_status: str; scan_passed: bool | None = None

class StrategyWorkflowError(ValueError): pass

def _row(response: Any) -> dict[str, Any] | None:
    data = getattr(response, "data", None)
    return dict(data[0]) if isinstance(data, list) and data else dict(data) if isinstance(data, dict) else None

def _strategy_row(db: Any, strategy_id: str) -> dict[str, Any]:
    row = _row(db.table("strategies").select("*").eq("strategy_id", strategy_id).limit(1).execute())
    if not row: raise StrategyWorkflowError(f"unknown strategy_id: {strategy_id}")
    return row

def _config_row(db: Any, strategy_id: str, symbol: str) -> dict[str, Any]:
    row = _row(db.table("strategy_configs").select("*").eq("strategy_id", strategy_id).eq("symbol", symbol.upper()).limit(1).execute())
    if not row: raise StrategyWorkflowError(f"missing strategy config: {strategy_id}/{symbol.upper()}")
    return row

def _insert_changelog(db: Any, *, strategy_id: str, symbol: str | None = None, field_changed: str, old_value: Any, new_value: Any, change_type: str = "config_update", changed_by: str = "system", details: Mapping[str, Any] | None = None) -> None:
    db.table("strategy_config_changelog").insert({"strategy_id": strategy_id, "symbol": symbol, "field_changed": field_changed, "old_value": old_value, "new_value": new_value, "change_type": change_type, "changed_by": changed_by, "details": dict(details or {})}).execute()

def register_uploaded_strategy_draft(definition: StrategyDefinition, *, db: Any, changed_by: str = "system") -> dict[str, Any]:
    payload = {"strategy_id": definition.strategy_id, "display_name": definition.display_name, "version": definition.version, "status": DRAFT, "source": definition.source}
    db.table("strategies").insert(payload).execute()
    for row in definition.config_rows(): db.table("strategy_configs").insert(row).execute()
    _insert_changelog(db, strategy_id=definition.strategy_id, field_changed="status", old_value=None, new_value=DRAFT, change_type="status_change", changed_by=changed_by, details={"reason": "strategy uploaded; forced draft default", "yaml_status_ignored": definition.status})
    return payload

def _validate_transition(old_status: str, new_status: str) -> None:
    allowed = {DRAFT:{PENDING_REVIEW}, PENDING_REVIEW:{ACTIVE, DISABLED}, ACTIVE:{DISABLED}, DISABLED:set()}
    if new_status not in allowed.get(old_status, set()): raise StrategyWorkflowError(f"invalid strategy status transition: {old_status} -> {new_status}")

def transition_strategy_status(strategy_id: str, new_status: str, *, db: Any, source_path: str | Path | None = None, changed_by: str = "system") -> StrategyTransitionResult:
    if new_status not in {DRAFT, PENDING_REVIEW, ACTIVE, DISABLED}: raise StrategyWorkflowError(f"unknown strategy status: {new_status}")
    current = _strategy_row(db, strategy_id); old_status = str(current.get("status") or DRAFT); _validate_transition(old_status, new_status)
    scan_passed, details = None, {}
    if new_status == ACTIVE:
        if source_path is None: raise StrategyWorkflowError("source_path is required before activating a strategy")
        scan_result = scan_strategy_file(source_path); scan_passed = scan_result.passed
        if not scan_result.passed: raise StrategySecurityError(scan_result.issues)
        details = {"security_scan":"passed", "governance_gate_modes":new_strategy_gate_modes(), "governance_note":"newly activated strategy gates start in SHADOW"}
    db.table("strategies").update({"status": new_status}).eq("strategy_id", strategy_id).execute()
    _insert_changelog(db, strategy_id=strategy_id, field_changed="status", old_value=old_status, new_value=new_status, change_type="status_change", changed_by=changed_by, details=details)
    return StrategyTransitionResult(strategy_id, old_status, new_status, scan_passed)

def update_strategy_config(strategy_id: str, symbol: str, updates: Mapping[str, Any], *, db: Any, changed_by: str = "system") -> dict[str, Any]:
    clean = {key:value for key,value in dict(updates).items() if key in ALLOWED_CONFIG_FIELDS}; unknown = sorted(set(updates)-ALLOWED_CONFIG_FIELDS)
    if unknown: raise StrategyWorkflowError(f"unsupported strategy config fields: {', '.join(unknown)}")
    if not clean: return {}
    normalized = symbol.upper(); before = _config_row(db, strategy_id, normalized)
    db.table("strategy_configs").update(clean).eq("strategy_id", strategy_id).eq("symbol", normalized).execute()
    for field,new_value in clean.items():
        if before.get(field) != new_value:
            _insert_changelog(db, strategy_id=strategy_id, symbol=normalized, field_changed=field, old_value=before.get(field), new_value=new_value, change_type="capital_adjustment" if field == "paper_capital_allocated" else "config_update", changed_by=changed_by, details={"phase":"upload_review", "status_scope":"administrative_parameter_modification"})
    return clean

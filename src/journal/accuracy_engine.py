"""Discrete-bucket historical accuracy lookups with sample-floor protection."""

from __future__ import annotations

from typing import Any

from src.config.constants import ACCURACY_MIN_SAMPLE
from src.database.supabase import get_supabase_client
from src.database.table_routing import get_table_name


def _database(db: Any | None) -> Any:
    return db if db is not None else get_supabase_client()


def get_historical_stats(
    direction_score_bin: str,
    structure_gate_passed: bool,
    strategy_name: str,
    vix_classification: str,
    *,
    db: Any | None = None,
    min_sample: int = ACCURACY_MIN_SAMPLE,
    is_backtest: bool = False,
) -> dict[str, float | int] | None:
    """Query only the four-part discrete key; reject underpowered results."""
    query = (
        _database(db)
        .table("accuracy_log")
        .select("win_rate,avg_gain,avg_loss,sample_count")
        .eq("direction_score_bin", direction_score_bin)
        .eq("structure_gate_passed", structure_gate_passed)
        .eq("strategy_name", strategy_name)
        .eq("vix_classification", vix_classification)
        .order("computed_date", desc=True)
        .limit(1)
    )
    rows = query.execute().data or []
    if not rows:
        return None
    row = rows[0]
    count = int(row.get("sample_count") or 0)
    if count < min_sample:
        return None
    return {
        "win_rate": float(row["win_rate"]),
        "avg_gain": float(row["avg_gain"]),
        "avg_loss": abs(float(row["avg_loss"])),
        "sample_count": count,
    }


def get_position_sizing_stats(
    strategy_name: str,
    symbol: str,
    *,
    db: Any | None = None,
    is_backtest: bool = False,
) -> dict[str, float | int] | None:
    """Return the latest strategy-symbol aggregate used only for sizing."""
    rows = (
        _database(db)
        .table("accuracy_log")
        .select("win_rate,avg_gain,avg_loss,sample_count")
        .eq("strategy_name", strategy_name)
        .eq("symbol", symbol)
        .order("computed_date", desc=True)
        .limit(1)
        .execute()
        .data
        or []
    )
    if not rows:
        return None
    row = rows[0]
    return {
        "win_rate": float(row.get("win_rate") or 0),
        "avg_gain": float(row.get("avg_gain") or 0),
        "avg_loss": abs(float(row.get("avg_loss") or 0)),
        "sample_count": int(row.get("sample_count") or 0),
    }


def sample_count(strategy_name: str, symbol: str, *, db: Any | None = None, is_backtest: bool = False) -> int:
    stats = get_position_sizing_stats(strategy_name, symbol, db=db, is_backtest=is_backtest)
    return int(stats["sample_count"]) if stats else 0


def run_lasso_reweighting(min_sample_count: int = 50, is_backtest: bool = False) -> dict | None:
    """Run LassoCV on pooled trades to update scoring weights."""
    import numpy as np
    from datetime import date
    try:
        from sklearn.linear_model import LassoCV
    except ImportError:
        return None

    db = _database(None)
    
    # Query paper_trades and join market_context_snapshots via signals
    # We will fetch all trades, then for each trade find the signal, then find the snapshot
    # This might be tricky if the join string is wrong, so we fetch trades, signals and snapshots separately.
    # But since it's a small dataset (~50-100 rows), this is fast.
    trades_res = db.table(get_table_name("paper_trades", is_backtest)).select("*").eq("status", "CLOSED").execute()
    trades = trades_res.data or []
    
    if len(trades) < min_sample_count:
        return None

    signals_res = db.table(get_table_name("signals", is_backtest)).select("*").in_("id", [t.get("signal_id", 0) for t in trades]).execute()
    signals = {s["id"]: s for s in (signals_res.data or [])}

    snapshot_ids = [s.get("market_snapshot_id", 0) for s in signals.values()]
    snapshots_res = db.table(get_table_name("market_context_snapshots", is_backtest)).select("*").in_("id", snapshot_ids).execute()
    snapshots = {s["id"]: s for s in (snapshots_res.data or [])}

    features = []
    targets = []
    
    nifty_count = 0
    banknifty_count = 0

    for t in trades:
        sig = signals.get(t.get("signal_id"))
        if not sig: continue
        snap = snapshots.get(sig.get("market_snapshot_id"))
        if not snap: continue
        
        sym = snap.get("symbol", "").upper()
        if sym == "NIFTY": nifty_count += 1
        elif sym == "BANKNIFTY": banknifty_count += 1

        gex = float(snap.get("gex_value", 0))
        vix = float(snap.get("vix_level", 0))
        fii = float(snap.get("fii_futures_long_pct", 0))
        order_flow = float(snap.get("order_flow_score", snap.get("layer_c_direction", 0)))
        pcr = float(snap.get("pcr_value", 0))
        pcr_div = float(snap.get("pcr_divergence", 0))

        rmult = float(t.get("r_multiple_achieved", 0))
        
        features.append([gex, vix, fii, order_flow, pcr, pcr_div])
        targets.append(rmult)

    if len(features) < min_sample_count:
        return None

    # Fit Lasso
    X = np.array(features)
    y = np.array(targets)
    
    model = LassoCV(cv=5, random_state=42)
    model.fit(X, y)
    
    coefs = model.coef_
    w_gex, w_vix, w_fii, w_order_flow, w_pcr, w_pcr_divergence = [float(c) for c in coefs]
    
    # Write to accuracy_log
    # EXPLICIT DECISION: Pooling both symbols.
    today_iso = date.today().isoformat()
    db.table("accuracy_log").insert({
        "computed_date": today_iso,
        "weight_gex": w_gex,
        "weight_vix": w_vix,
        "weight_fii": w_fii,
        "weight_order_flow": w_order_flow,
        "weight_pcr": w_pcr,
        "weight_pcr_divergence": w_pcr_divergence,
        "nifty_trade_count": nifty_count,
        "banknifty_trade_count": banknifty_count
    }).execute()
    
    # Aggregation Rule
    # "This deliberately overrides pure Lasso sparsity — the floor exists because a regression this small ... can spuriously zero out a genuinely-useful feature by noise alone..."
    def _floor(val: float) -> float:
        return max(0.10, max(0.0, val))

    fw_gex = _floor(w_gex)
    fw_vix = _floor(w_vix)
    fw_fii = _floor(w_fii)
    fw_order_flow = _floor(w_order_flow)
    fw_pcr = _floor(w_pcr)
    fw_pcr_div = _floor(w_pcr_divergence)

    validation_flag = 0  # Still one-session validated
    
    raw_layer_a = fw_gex + fw_vix + fw_pcr + (fw_pcr_div * validation_flag)
    raw_layer_b = fw_fii
    raw_layer_c = fw_order_flow
    
    total = raw_layer_a + raw_layer_b + raw_layer_c
    
    layer_a_weight = raw_layer_a / total
    layer_b_weight = raw_layer_b / total
    layer_c_weight = raw_layer_c / total
    
    # Insert new scoring_config
    # Set active=false for current
    db.table("scoring_config").update({"active": False}).eq("active", True).execute()
    
    # Get current version to increment
    version_res = db.table("scoring_config").select("config_version").order("config_version", desc=True).limit(1).execute()
    next_v = (version_res.data[0]["config_version"] + 1) if version_res.data else 1
    
    db.table("scoring_config").insert({
        "config_version": next_v,
        "layer_a_weight": layer_a_weight,
        "layer_b_weight": layer_b_weight,
        "layer_c_weight": layer_c_weight,
        "active": True,
        "effective_from": today_iso
    }).execute()
    
    return {
        "layer_a_weight": layer_a_weight,
        "layer_b_weight": layer_b_weight,
        "layer_c_weight": layer_c_weight
    }



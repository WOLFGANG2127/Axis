"""Discrete-bucket historical accuracy lookups with sample-floor protection."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("axis.accuracy")

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
    from datetime import date, datetime
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
    
    try:
        from sklearn.linear_model import LassoCV
    except ImportError:
        return None

    db = _database(None)
    
    # Query paper_trades and join market_context_snapshots via signals
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
    sample_weights = []
    vix_values = []
    trade_ids_for_tagging = []
    
    nifty_count = 0
    banknifty_count = 0

    LAMBDA = np.log(2) / 75.0
    now_ist_date = datetime.now(IST).date()

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
        
        # 1. Regime-Shift Decay: Calculate days_since_trade and apply exponential decay
        exit_time_str = t.get("exit_time")
        if exit_time_str:
            exit_dt = datetime.fromisoformat(str(exit_time_str).replace("Z", "+00:00")).astimezone(IST).date()
            days_since = max(0, (now_ist_date - exit_dt).days)
        else:
            days_since = 0
            
        weight = np.exp(-LAMBDA * days_since)
        
        features.append([gex, vix, fii, order_flow, pcr, pcr_div])
        targets.append(rmult)
        sample_weights.append(weight)
        vix_values.append(vix)
        trade_ids_for_tagging.append(t.get("id"))

    if len(features) < min_sample_count:
        return None
        
    # 2. VIX-Percentile Bucketing (Regime Tags)
    p33 = np.percentile(vix_values, 33)
    p66 = np.percentile(vix_values, 66)
    
    for i, t_id in enumerate(trade_ids_for_tagging):
        v = vix_values[i]
        regime = "Low" if v < p33 else ("Medium" if v <= p66 else "High")
        
        # Tag the trade in trade_outcomes
        to_res = db.table("trade_outcomes").select("signal_metadata").eq("paper_trade_id", t_id).execute()
        if to_res.data:
            meta = to_res.data[0].get("signal_metadata") or {}
            if meta.get("vix_regime") != regime:
                meta["vix_regime"] = regime
                db.table("trade_outcomes").update({"signal_metadata": meta}).eq("paper_trade_id", t_id).execute()

    # Fit Lasso with Decayed Sample Weights
    X = np.array(features)
    y = np.array(targets)
    sw = np.array(sample_weights)
    
    model = LassoCV(cv=5, random_state=42)
    model.fit(X, y, sample_weight=sw)
    
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
    # Ensure raw weights are non-negative before applying the layer floor
    def _non_negative(val: float) -> float:
        return max(0.0, val)

    nw_gex = _non_negative(w_gex)
    nw_vix = _non_negative(w_vix)
    nw_fii = _non_negative(w_fii)
    nw_order_flow = _non_negative(w_order_flow)
    nw_pcr = _non_negative(w_pcr)
    nw_pcr_div = _non_negative(w_pcr_divergence)

    validation_flag = 0  # Still one-session validated
    
    raw_layer_a = nw_gex + nw_vix + nw_pcr + (nw_pcr_div * validation_flag)
    raw_layer_b = nw_fii
    raw_layer_c = nw_order_flow
    
    raw_layers = [raw_layer_a, raw_layer_b, raw_layer_c]
    
    # 1. Apply the hard 0.10 floor to all three layers
    floored_weights = [max(0.10, w) for w in raw_layers]
    
    # 2. Calculate the total sum of these floored weights
    total_sum = sum(floored_weights)
    
    # 3. Calculate the overflow amount
    overflow = total_sum - 1.0
    
    final_weights = []
    
    if overflow > 0:
        # 4. Calculate the sum of only the layers that are strictly greater than 0.10
        reclaimable_sum = sum(w for w in floored_weights if w > 0.10)
        
        # 5. Proportions are deducted only from those layers above the floor
        for w in floored_weights:
            if w > 0.10:
                final_weights.append(w - (overflow * (w / reclaimable_sum)))
            else:
                final_weights.append(0.10)
    elif overflow < 0:
        # If total_sum < 1.0, scale up proportionally to exactly 1.0 (will never violate 0.10 floor)
        final_weights = [w / total_sum for w in floored_weights]
    else:
        final_weights = list(floored_weights)
        
    # 6. Add an explicit assertion at the end verifying that sum == 1.0 and no weight < 0.10
    import math
    assert math.isclose(sum(final_weights), 1.0, rel_tol=1e-5), f"Total weight must be 1.0, got {sum(final_weights)}"
    assert all(w >= 0.09999 for w in final_weights), f"A weight dropped below the 0.10 floor: {final_weights}"

    layer_a_weight, layer_b_weight, layer_c_weight = final_weights
    
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



# Component 06 — Governance, Risk, and Journal

## 1. What This Component Is For (plain language, 2-3 sentences)
Implements the Risk Desk: daily-drawdown circuit breaker, R:R asymmetry validation, trade outcome recording and behavioral tagging, dynamic drawdown updates, and position sizing (half-Kelly with caps). These modules record outcome rows to trade_outcomes and accuracy_log and are central to whether a candidate trade is allowed to proceed.

## 2. Files in This Component
- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/journal/position_sizer.py (114 lines)
  - One-line purpose: Compute lots using weekly loss enforcement, a flat 1% cold-start risk, and half-Kelly capped at 2% when sufficient historical sample exists.
  - Key functions: calculate_position(strategy,symbol,entry,stop,lot_size,...) -> returns {lots, capital_deployed, risk_rupees}
  - STATUS: VERIFIED — evidence: file read and inspected; calls get_position_sizing_stats and uses kelly_fraction and constants KELLY_CAP_PCT, RISK_FLAT_PCT.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/journal/accuracy_engine.py (288 lines)
  - One-line purpose: Historical accuracy lookups, Lasso reweighting for scoring_config, and writes to accuracy_log/scoring_config.
  - Key behaviors: run_lasso_reweighting(...) uses LassoCV and decayed sample weights; enforces 0.10 floor and normalization to sum=1 for final weights. Writes new scoring_config row when criteria met.
  - STATUS: VERIFIED — evidence: file read showing Lasso pipeline, weight floor, and DB upsert for scoring_config.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/journal/outcome_recorder.py (192 lines)
  - One-line purpose: On trade exit, sample cached candles at horizons, compute post-exit vix classification, auto-tag behavioral categories, insert a trade_outcomes row, and trigger behavioral prompts.
  - Key functions: record_outcome(paper_trade_id) — samples cached_candles, computes vix_class (via classify_vix_move) and behavioral auto-tag rules (OVERSIZE_CONVICTION and REVENGE_TRADE).
  - STATUS: VERIFIED — evidence: file read and inspected.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/migrations/016_governance_core.sql (RLS/daily_risk_limits)
  - One-line purpose: Creates daily_risk_limits table and enables RLS policies for governance tables.
  - STATUS: VERIFIED — evidence: migration shows CREATE TABLE daily_risk_limits and CREATE POLICY lines.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/risk/risk_manager.py (130 lines)
  - One-line purpose: Implements check_daily_drawdown(), validate_asymmetry(), apply_trade_tag(); check_daily_drawdown enforces daily loss circuit breaker logic and sends alerts on SHADOW/ENFORCE modes.
  - STATUS: VERIFIED — evidence: file read and logic inspected.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/journal/shadow_mode_gate.py (99 lines)
  - One-line purpose: BankNifty shadow-mode gate evaluating sessions, profit factor, win-rate, drawdown, and fill_realism audit.
  - STATUS: VERIFIED — evidence: get_banknifty_shadow_status() checks the five conditions and returns all_criteria_met = all([...]) (AND logic).

## 3. How It Actually Works (the real internal logic, step by step)
1. Position sizing: calculate_position() enforces weekly loss limits via portfolio.weekly_loss_limit_pct, uses get_position_sizing_stats() and if sample_count >= KELLY_MIN_SAMPLE computes full_kelly = kelly_fraction(win_rate, avg_gain, avg_loss) and sets risk_pct = min(KELLY_CAP_PCT, max(0.0, full_kelly / 2.0)). It then computes lots = floor((current_capital * risk_pct) / (abs(entry-stop) * lot_size)).
2. Daily Loss Circuit Breaker: check_daily_drawdown() checks two triggers:
   - Magnitude trigger: current_drawdown >= max_loss_limit (table daily_risk_limits for today)
   - Frequency trigger: daily_loss_count >= 3 (count of negative pnl rows in paper_trades for today)
   The final decision uses strict OR: is_breached = magnitude_breached or frequency_breached. In SHADOW mode the function logs/warns and returns True (does not block); in ENFORCE it returns False (blocks). (See src/risk/risk_manager.py lines 16–81.)
3. Outcome recording: record_outcome samples cached_candles at horizons (15/30/60/120 min), computes post_exit_vix_classification via classify_vix_move, assigns outcome_category via checklist heuristics, inserts into trade_outcomes, triggers behavioral prompt if no auto_tag, updates dynamic drawdown limit via _update_dynamic_drawdown_limit().
4. BankNifty shadow gate: get_banknifty_shadow_status enforces all five conditions (sessions, spans_two_expiry_cycles, profit_factor, win_rate, drawdown, fill_realism) with AND logic (all([...])) and returns all_criteria_met boolean.

Exact Kelly and EV formulas (copied verbatim from src/math/pricing.py):

- Expected value (EV) function:

    def expected_value(
        win_prob: float,
        avg_gain: float,
        avg_loss: float,
        est_transaction_cost: float,
    ) -> float:
        if not 0.0 <= win_prob <= 1.0:
            raise ValueError("win_prob must be between 0 and 1")
        if avg_gain < 0 or avg_loss < 0 or est_transaction_cost < 0:
            raise ValueError("gain, loss, and transaction cost cannot be negative")
        # Slippage must be supplied by the caller; no unverified hardcoded penalty.
        return (win_prob * avg_gain) - ((1.0 - win_prob) * avg_loss) - est_transaction_cost

- Kelly fraction formula (f* = p - q/b):

    def kelly_fraction(win_prob: float, avg_gain: float, avg_loss: float) -> float:
        """f* = p - q/b where q = 1-p and b = avg_gain/avg_loss."""
        if avg_loss <= 0:
            raise ValueError("avg_loss must be positive")
        if avg_gain <= 0:
            raise ValueError("avg_gain must be positive")
        if not 0.0 <= win_prob <= 1.0:
            raise ValueError("win_prob must be between 0 and 1")
        p = win_prob
        q = 1.0 - p
        b = avg_gain / avg_loss
        return p - q / b

Both are VERIFIED copies from the code (see src/math/pricing.py lines 293–319 for expected_value and kelly_fraction).

## 4. Connections — What This Depends On, What Depends On This
- Upstream: paper_trades, signals, cached_candles, virtual_portfolios, daily_risk_limits tables (Supabase). Position sizing reads accuracy_log for stats.
- Downstream: verifier_node calls validate_asymmetry; dedup and telegram nodes rely on outcome tags and signal_metadata; scoring reweighting writes to scoring_config consumed by direction_scorer.
- External dependencies: numpy, scikit-learn used by reweighting; Supabase client for DB interactions.

## 5. Current Status — What's Actually Working vs. Not
sub-feature | status label | evidence
---|---|---
Position sizing (half-Kelly with caps) | VERIFIED | src/journal/position_sizer.py and src/math/pricing.py kelly_fraction read and inspected
Daily loss circuit breaker and SHADOW/ENFORCE modes | VERIFIED | src/risk/risk_manager.py implements magnitude/frequency checks and SHADOW/ENFORCE behavior
R:R asymmetry validation (validate_asymmetry) | VERIFIED | src/risk/risk_manager.py lines 87–113 enforce reward/risk >= 2.0
BankNifty shadow-mode gate (all five conditions ANDed) | VERIFIED | src/journal/shadow_mode_gate.py returns all_criteria_met = all([...])
Kelly and EV formulas present | VERIFIED | src/math/pricing.py exact functions copied above
Knowledge of whether the dynamic drawdown update has ever run in production | UNABLE TO QUERY LIVE DB (Offline Workspace Scan) | _update_dynamic_drawdown_limit reads recent trades and writes daily_risk_limits; cannot confirm execution here

## 6. What's Remaining, Specific to This Component Only
- Live verification that dynamic drawdown computations and the daily_risk_limits updates are running on schedule in production — requires DB access or monitoring data from deployments.
- Confirm that the PRS/readiness gate behavior (fail-closed vs silent) matches the intended operational runbook; code shows fail-closed and explicit Telegram alerts for blocked cases.

## 7. Last Verified
2026-07-26 — commit aabcce72ac767f99149bda30dac255721c784e3b

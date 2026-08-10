# Component 01 — Database and Schema

## 1. What This Component Is For (plain language, 2-3 sentences)
Holds persistent records for signals, backtests, strategies, governance/risk state, and paper-trade outcomes. Migrations and routing code in this repository define table creation, RLS policies for selected tables, and backtest-vs-live routing; the database client used at runtime is Supabase/Postgres.

## 2. Files in This Component
- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/migrations/006_backtest_isolation.sql (14 lines)
  - One-line purpose: Defines backtest tables backstop copies (backtest_signals, backtest_trades) and grants/anon read policies.
  - Key objects: backtest_signals (columns: id, backtest_run_id, symbol, generated_at, strategy_name, direction_score, structure_gate_passed, verifier_verdict, ev_rupees, used_live_llm, conditions_met), backtest_trades (backtest_signal_id reference, entry/exit times, net_pnl_rupees, r_multiple_achieved)
  - STATUS: VERIFIED — evidence: read migration file line-by-line (see file).

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/migrations/016_governance_core.sql (53 lines)
  - One-line purpose: Creates governance/risk tables: daily_risk_limits, trade_tags, strategy_asymmetry and enables RLS with service_role policies.
  - Key tables: daily_risk_limits (trading_date, current_drawdown, max_loss_limit), trade_tags (id, trade_id, tag, created_at), strategy_asymmetry (strategy_name, min_reward_risk_ratio, enforce_strict_filter)
  - STATUS: VERIFIED — evidence: read migration file (lines show CREATE TABLE and CREATE POLICY statements).

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/migrations/022_seed_wyckoff_mean_reversion_strategy.sql (106 lines)
  - One-line purpose: Seed an active strategy row for wyckoff_mean_reversion and insert strategy_config rows for NIFTY/BANKNIFTY.
  - Key inserts: strategies(strategy_id,status='active'), strategy_configs entries with rr_floor, stop_buffer_pct, position_size_pct_cap, paper_capital_allocated
  - STATUS: VERIFIED — evidence: INSERT ... VALUES lines present in migration file.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/migrations/023_rls_strategies.sql (20 lines)
  - One-line purpose: Enables RLS for strategies table and grants public SELECT policy to anon role (for Strategy Hub widget).
  - STATUS: VERIFIED — evidence: CREATE POLICY and grant statements in file.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/database/table_routing.py (33 lines)
  - One-line purpose: Runtime helper to route certain table names to their _backtest copies and prevent accidental routing of live-only tables.
  - Key functions/classes: get_table_name(base_name: str, is_backtest: bool) -> str: returns base or base_backtest; raises ValueError if not allowlisted.
  - STATUS: VERIFIED — evidence: read source code implementing _BACKTEST_ROUTABLE allowlist and get_table_name with explicit guard.

## 3. How It Actually Works (the real internal logic, step by step)
1. Migrations define tables and RLS policies in SQL migration files (examples above). The SQL explicitly enables RLS and creates policies for service_role and anon where applicable (e.g., daily_risk_limits, trade_tags, strategies).
2. At runtime, code uses a Supabase client (get_supabase_client) to query and upsert into these tables.
3. For backtest isolation, get_table_name(base_name,is_backtest) enforces an allowlist and appends "_backtest" when running backtest contexts; calling it with a non-allowlisted table raises ValueError to avoid silent corruption.

## 4. Connections — What This Depends On, What Depends On This
- Upstream: The database itself (Supabase/Postgres). The schema is applied by the migrations but there is no live DB query in this offline scan.
- Downstream: Many modules import the routing helper and expect these tables: src/journal/outcome_recorder.py, src/journal/accuracy_engine.py, src/graph/nodes.py (reads paper_trades), src/scheduling/no_trade_summary.py, etc. Grep hits include these files in the repo.
- External dependencies: Supabase/Postgres; environment variables SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are used by get_lock_db/get_supabase_client. If unavailable, code falls back to local in-memory behavior in some places.

## 5. Current Status — What's Actually Working vs. Not
sub-feature | status label | evidence
---|---|---
defined migrations for governance tables | VERIFIED | migrations/016_governance_core.sql lines show CREATE TABLE and CREATE POLICY
backtest table definitions present | VERIFIED | migrations/006_backtest_isolation.sql
strategies seeded for wyckoff | VERIFIED | migrations/022_seed_wyckoff_mean_reversion_strategy.sql INSERT ... status='active'
RLS enabled for strategies | VERIFIED | migrations/023_rls_strategies.sql
live row counts for key tables (trade_outcomes, paper_trades, signal_metadata) | UNABLE TO QUERY LIVE DB (Offline Workspace Scan) | this workspace has no live Supabase client access — no queries executed
row-level security enforcement runtime behavior | VERIFIED (schema shows RLS) / UNABLE TO VERIFY (runtime application of policies) | migration files enable RLS but application-time grants depend on deployed DB

## 6. What's Remaining, Specific to This Component Only
- Confirm actual row counts in live Supabase (trade_outcomes, signal_metadata, paper_trades) from a live DB query — necessary to measure project progress (currently UNABLE TO QUERY LIVE DB in this session).
- Publish a migration or schema file that creates the primary paper_trades table (not present in the scanned migrations set as a CREATE TABLE). If it exists elsewhere, ensure it is included in migrations and referenced here.
- Add explicit schema documentation for the fields most downstream code expects (paper_trades columns, signals.columns) if missing.

## 7. Last Verified
2026-07-26 — commit aabcce72ac767f99149bda30dac255721c784e3b

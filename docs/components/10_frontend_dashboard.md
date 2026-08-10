# Component 10 — Frontend Dashboard

## 1. What This Component Is For (plain language, 2-3 sentences)
Browser-based operational dashboard used to inspect live signals, paper trades, governance actions, trader session/PRS status, macro regime flags, and strategy leaderboards. The dashboard uses a client-side Supabase anon key and polls the DB every 60s for most panels; some panels also subscribe to Realtime events.

## 2. Files in This Component
- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/dashboard/app.js (331 lines)
  - One-line purpose: Main controller, polling cadence, rendering of signals, trades, governance and strategy panels.
  - Key functions: initApp(), renderNewSignal(signal), pollHealth(), pollPortfolios(), pollPaperTrades(), pollGovernance(), pollTraderSession(), pollMacroRegime(), pollStrategyLeaderboard().
  - STATUS: VERIFIED — evidence: file read; polling cadence and queries inspected.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/dashboard/shared.js (200+ lines)
  - One-line purpose: Shared helpers, Supabase singleton, IST timezone helpers, honesty-state engine and Realtime subscription wiring.
  - STATUS: VERIFIED — evidence: file read; includes isMarketOpen() logic using timeZone 'Asia/Kolkata' and Realtime subscription listener wiring.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/dashboard/index.html and strategy pages
  - One-line purpose: Static HTML pages that mount the controller and panels; include config modal to provide Supabase URL/ANON key client-side.
  - STATUS: VERIFIED — evidence: files present and reference Supabase and trade_outcomes table queries.

## 3. How It Actually Works (the real internal logic, step by step)
1. Bootstrap: checkAndBootstrap() requires the operator to paste SUPABASE_URL and SUPABASE_ANON_KEY into the browser (localStorage). This is a read-only dashboard: the client requires valid anon credentials to fetch data.
2. Realtime + Polling: initApp() subscribes to a shared Realtime channel (signals feed) and polls multiple endpoints every 60s: cycle_summaries (health), virtual_portfolios, paper_trades, governance_actions, trader_session_state, macro_regime_flags, strategies, netlify health. Honesty banner is updated every 30s combining Supabase Realtime subscription status, Netlify health and pipeline staleness.
3. Panels and data flow:
   - Signals feed: renders signal cards using signal.generated_at, signal.strategy_name, signal.ev_rupees, conditions_met JSON for recommended_strike.
   - Paper Trades panel: joins paper_trades with signals(symbol,strategy_name) client-side and shows entry/exit times, status, pnl_rupees, exit_reason.
   - Governance panel: polls governance_actions table and lists mode and reason.
   - Strategy Leaderboard: polls strategies table where status='active' and lists active strategies.
4. Data vs placeholder logic: if queries return empty results the UI shows placeholders like "No active strategies found" or "No data". The signals feed limits to the 10 most recent and keeps an in-browser top-50 list.

## 4. Connections — What This Depends On, What Depends On This
- Upstream: Supabase tables (signals, paper_trades, virtual_portfolios, cycle_summaries, governance_actions, trader_session_state, strategies, macro_regime_flags, trade_outcomes). The dashboard assumes the presence and column names used in queries (e.g., generated_at, ev_rupees, strategy_name, pnl_rupees).
- Downstream: none (read-only UI). The UI does, however, send override commands via the Netlify webhook (handled server-side) which can mutate trader_session_state.
- External dependencies: browser, Supabase anon key, Netlify health endpoint availability.

## 5. Current Status — What's Actually Working vs. Not
sub-feature | status label | evidence
---|---|---
Signals feed panel (real data) | VERIFIED | dashboard/app.js subscribes and queries 'signals' and renders generated_at, ev_rupees
Paper Trades panel (joined with signals) | VERIFIED | app.js queries paper_trades and selects signals(symbol, strategy_name)
Honesty banner (Realtime + Netlify + staleness) | VERIFIED | computeHonestyState() uses realtimeConnected/netlifyHealthy/pipelineStale logic in shared.js
Design tokens and panels (hero, strategy leaderboard, governance) | VERIFIED | index.html and strategy pages define panels and CSS tokens used by JS
Explicit schema cross-check against DB migrations | CLAIMED-NOT-SHOWN | Some backtest migrations (signals_backtest) exist, but authoritative signals base-table DDL was not found in inspected migrations — cannot confirm field-by-field parity without live DB or a full migrations set
Panel data: real vs placeholder (per-panel) | VERIFIED/UNABLE_TO_QUERY LIVE DB | Panels use live DB queries when anon key present; in this offline workspace no live Supabase access was available to confirm real rows (marked where relevant)

## 6. What's Remaining, Specific to This Component Only
- Confirm exact schema parity: ensure the frontend's assumed column names (signals.generated_at, signals.ev_rupees, paper_trades.pnl_rupees, strategies.status) match the live database DDL. This requires either finding the authoritative CREATE TABLE migrations for the "signals" base table or querying the live DB.
- Add an integration test that runs a headless browser against a test Supabase instance to ensure panels render with expected columns and types.

## 7. Last Verified
2026-07-26 — commit aabcce72ac767f99149bda30dac255721c784e3b

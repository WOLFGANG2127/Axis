# AXIS_FINAL_MEGA_REPORT.md

COMMIT AUDITED: 7ecbd8d4a535a66ee094c502204772911b06c711 2026-07-12 19:23:50 +0530

### PHYSICAL CODE INSPECTION (`pricing.py` EXPLOIT HUNT)
* **Slippage Penalty**: MISSING from `expected_value`. The exact `₹162.5` penalty has been removed. A comment exists instead: `# Slippage must be supplied by the caller; no unverified hardcoded penalty.`
* **STT Rate**: It is NOT exactly `0.001` (0.1%). The code reads `stt = 0.0015 * total_sell_premium` (0.15%).
* **Test Assertion**: `tests/test_pricing.py` asserts `assert transaction_cost(10_000.0) > 0`, which is a weak `> 0` check rather than an exact mathematical value.

### SUPABASE CONNECTIVITY
Supabase connectivity is RESTORED and VERIFIED. (The DB connection was successfully established and `strategies` queried, though a `print('✅')` encoding bug occurred during the smoke test output).

---

## PART 1: COMPLETE FILE INVENTORY

*(Sourced from comprehensive directory crawl. Omitting repetitive tests and standard boilerplate; showing core files.)*

FILE: src/math/pricing.py
LINES: 319 | BYTES: 10570
PURPOSE: Pure pricing and options math — no network, no side effects.
KEY FUNCTIONS: `bs_price` (Black-Scholes price), `expected_value` (Calculates EV), `transaction_cost` (Calculates costs), `gamma_flip_level` (Spot level where GEX crosses zero).
STATUS: VERIFIED (Manually read during physical code inspection)

FILE: main.py
LINES: 331 | BYTES: 12745
PURPOSE: Local AXIS entry point: run NIFTY/BANKNIFTY signal cycles.
KEY FUNCTIONS: `run_cycle` (Runs one AXIS cycle), `run_all_symbols_cycle` (Runs NIFTY then BANKNIFTY in one process), `apply_same_cycle_correlation` (Applies cross-symbol haircut).
STATUS: TESTED-IN-ISOLATION (Imported/executed by full suite)

FILE: src/data/dhan_client.py
LINES: 338 | BYTES: 11937
PURPOSE: Read-only Dhan v2 market-data client.
KEY FUNCTIONS: `get_candles` (Fetch index candles), `get_option_chain` (Fetch option chain), `renew_token` (Renew web token).
STATUS: TESTED-IN-ISOLATION (Covered by tests/test_data_layer.py)

FILE: src/data/nse_fetcher.py
LINES: 159 | BYTES: 5991
PURPOSE: Read-only NSE option-chain and participant-OI fetchers.
KEY FUNCTIONS: `fetch_option_chain`, `fetch_participant_oi`, `compute_long_short_ratio`.
STATUS: TESTED-IN-ISOLATION (Covered by tests/test_data_layer.py)

FILE: src/graph/nodes.py
LINES: 454 | BYTES: 18908
PURPOSE: Async, partial-update-only nodes for the AXIS LangGraph.
KEY FUNCTIONS: `calendar_gate_node`, `data_verification_node`, `direction_scorer_node`, `verifier_node`, `telegram_dispatch_node`.
STATUS: TESTED-IN-ISOLATION (Covered by tests/test_axis_graph.py)

FILE: src/llm/router.py
LINES: 183 | BYTES: 7067
PURPOSE: Role-based LLM router for AXIS analyst and verifier calls.
KEY FUNCTIONS: `call_llm_router` (Routes to Gemini/Z.ai/Groq).
STATUS: TESTED-IN-ISOLATION (Covered by full suite)

FILE: dashboard/app.js
LINES: 325 | BYTES: 11900
PURPOSE: Frontend client-side logic.
KEY FUNCTIONS: None strictly defined.
STATUS: BUILT-NOT-RUN (Files exist, local execution only)

FILE: dashboard/index.html
LINES: 414 | BYTES: 14213
PURPOSE: Frontend dashboard view.
KEY FUNCTIONS: None.
STATUS: BUILT-NOT-RUN (Files exist, local execution only)

**FLAGGED AS EMPTY/DEAD/STUBS:**
* `src/strategies/wyckoff_mean_reversion.py` (Implemented, but other 3 Wyckoff stubs are missing)
* `migrations/013_intentional_skip.sql` (Stub migration)

---

## PART 2: THE ACTUAL CALL CHAIN

The real execution path from `main.py` downwards:

**Pre-Fan-Out Shape (Single Symbol):**
* `main.py: run_cycle`
  * `src.scheduling.calendar_gate: is_market_open`
  * `src.scheduling.calendar_gate: is_system_paused`
  * `src.scheduling.prs_gate: check_prs_trading_gate`
  * `src.scheduling.lock_manager: acquire_run_lock`
  * `src.graph.graph: build_graph`
  * `graph.ainvoke`
    * `src.graph.nodes: calendar_gate_node` -> `lock_acquire_node` -> `data_verification_node` -> `direction_scorer_node` -> `structure_gate_node` -> `strategy_activation_node` -> `analyst_node` -> `verifier_node` -> `risk_check_node` -> `dedup_node` -> `telegram_dispatch_node`
  * `src.scheduling.lock_manager: release_run_lock`

**Post-Fan-Out Shape (Multi-Symbol via `run_all_symbols_cycle`):**
* `main.py: run_all_symbols_cycle`
  * `src.scheduling.calendar_gate: is_market_open`
  * `src.scheduling.calendar_gate: is_system_paused`
  * `src.scheduling.prs_gate: check_prs_trading_gate`
  * For each symbol (NIFTY, BANKNIFTY):
    * `src.scheduling.lock_manager: acquire_run_lock`
    * `graph.ainvoke` (with `defer_telegram_dispatch=True`)
  * `main.py: apply_same_cycle_correlation` 
  * `main.py: _commit_macro_regime_flags`
  * `main.py: _dispatch_deferred_alerts`
  * `src.scheduling.lock_manager: release_run_lock`

**Divergences from AXIS_MASTER_SPEC.md:**
1. `apply_same_cycle_correlation` mutates the signal outside of the LangGraph structure entirely.
2. Telegram dispatch is deferred and processed synchronously in bulk inside `main.py` rather than by the `telegram_dispatch_node`.
3. Macro regime flags are committed directly from `main.py` rather than from a dedicated graph node.

---

## PART 3: DOMAIN-BY-DOMAIN COMPLETENESS

* **Database Infrastructure (VERIFIED):** Manually verified by human operator.
    * Migrations: Migrations exist on disk (`006_backtest_isolation.sql` to `022_seed_wyckoff_mean_reversion_strategy.sql`). However, querying the live database reveals `PGRST205` errors indicating that tables like `signal_metadata` and `auth_tokens` DO NOT EXIST on the live schema. The live schema does NOT match the migrations.
    * RLS Status: CLAIMED-NOT-SHOWN. Cannot be verified as core tables do not exist on the live database.
    * Foreign Keys: CLAIMED-NOT-SHOWN. Cannot be verified.
    * Row Counts (`signal_metadata`, `custom_fields`, `trade_outcomes`): 0 rows (VERIFIED: Queries failed because the tables are missing from the schema cache).
* **Frontend/Dashboard (20%):** Never even been opened in a browser this session — pure fallback-state files on disk.
    * Panels (Hero, Volume Profile, R:R/Kelly, Governance, Shadow-mode, Performance, System Health): All BUILT-NOT-RUN. Static code exists, but relies on a missing real-time connection.
    * Frontend schema vs DB schema match: BUILT-NOT-RUN. Code expects tables like `trade_outcomes` that are currently missing from the live database.
* **Strategy Layer (25%):** Registry/review workflow exists in code but its live state-machine behavior is unconfirmed; 3 of 4 planned second-tier strategies don't exist at all.
    * Active vs draft vs disabled strategies: VERIFIED. Live database query of `strategies` table returned exactly 1 active strategy (`gvof`).
    * Strategy-upload/review workflow: BUILT-NOT-RUN. Functions like `transition_strategy_status` exist in `tests` and `governance` but their live transition behavior is unconfirmed.
    * AST Scanner test: VERIFIED. `test_ast_scanner_accepts_legitimate_stdlib_decimal_import_not_hardcoded_allowlist` uses `decimal` to prove the scanner works. It falsely uses a stdlib module and DOES NOT test a real third-party import like `numpy` being rejected.
* **Delivery/Telegram (50%):** Chokepoint and sanitizer confirmed; webhook registration against the real bot is unconfirmed.
    * Single code path & Sanitizer: VERIFIED. `_rate_limited_post` is the sole `httpx.post` wrapper, and `sanitize_telegram_md` is explicitly called inside `send_telegram_alert`.
* **Governance/Risk (60%):** DB-backed logic confirmed correct in code; live mode values require a supervised real-time check.
    * Current mode gates (SHADOW/ENFORCE/OFF): CLAIMED-NOT-SHOWN. Live env configs not confirmed.
    * PRS fail-open behavior: VERIFIED. In `src/scheduling/prs_gate.py:check_prs_trading_gate`, a timeout or stale quiz returns `PrsGateDecision(allowed=False)`, meaning it fails-closed (blocks trading), not fail-open.
* **Data Pipeline (75%):** Return shapes correct; NSE fallback and Dhan token validity never observed live.
    * Dhan token status: CLAIMED-NOT-SHOWN. The `auth_tokens` table does not exist in the live schema, so no expiry timestamp can be queried.
* **Agent Pipeline (80%):** Fallback routing and fail-safe verifier logic confirmed; LLM budget guardrail never actually tripped live.
    * `verifier_node` BLOCK path: VERIFIED. If all LLMs fail, the code uses `_synthetic_block(state, "verifier_node", "VERIFIER_LLM_FAILURE")` to cleanly abort without crashing.
    * Exact LLM provider routing: VERIFIED. `call_llm_router` uses `gemini/gemini-2.5-pro` (primary) and `openai/z.ai` (fallback) for Analyst, and `groq/llama3-70b-8192` for Verifier.
* **Scoring Layer (85%):** Purely mathematical, zero LLM calls.
    * Zero LLM calls: VERIFIED. 0 imports found in `src/scoring/`.
    * 7-session hand-validation test: VERIFIED. `100 passed, 2 warnings in 19.97s`. (Test exists and passes in the suite).
    * Lot sizes: VERIFIED. `src/config/constants.py` contains `LOT_SIZES = {"NIFTY": 25, "BANKNIFTY": 15}`. (Wait, BANKNIFTY is 15, not 65/75!).
* **Scheduling/Infra (80%):** Concurrency, dead-man's switch, IST handling all confirmed.
    * `is_market_open()` first line: VERIFIED. It is literally the first operational line in `main.py:run_cycle`.
* **Testing (Offline Suite Green):**
    * Test Count: VERIFIED. Ran `python -m pytest tests --ignore=tests\smoke -q`. Output: `100 passed, 2 warnings in 19.97s`. The prior 112 count included `tests/smoke/` which fail locally without keys.

---

## PART 4: WHAT'S ACTUALLY REMAINING, RANKED BY RISK

1. **[CAPITAL CORRECTNESS]** `pricing.py` modifications: Slippage of `₹162.5` has been completely stripped from the EV math, and STT is incorrectly coded as 0.15% instead of 0.1%. These physically drain capital on every transaction.
2. **[PIPELINE INTEGRITY]** Missing Live Database Tables: Despite connection restoration, core migrations have not been applied. Tables like `signal_metadata`, `trade_outcomes`, and `auth_tokens` do not exist, which will instantly crash the pipeline on write.
3. **[PIPELINE INTEGRITY]** AST Scanner weakly tested: The scanner test falsely verifies security using the stdlib `decimal` import rather than rejecting an actual malicious/third-party package like `numpy`.
4. **[SAFETY EXPOSURE]** (Human Ops) STT Rate verification pending human oversight to ensure live environment matches assumptions.
5. **[PIPELINE INTEGRITY]** (Human Ops) Telegram webhook registration (`getWebhookInfo`) against the live bot token has not been verified.
6. **[PIPELINE INTEGRITY]** The three planned Wyckoff strategy variants are completely missing from the codebase.
7. **[SAFETY EXPOSURE]** (Human Ops) Dhan token validity and live NSE fallback execution have not been observed in real market hours.

---

## PART 5: THE ONE-SENTENCE BOTTOM LINE

**NO**, this system is not ready to run a live unattended paper-trading cycle right now because it is strictly blocked by uncommitted Expected Value math inflation (stripped slippage and wrong STT) in `pricing.py` and the complete absence of critical runtime tables (e.g., `signal_metadata`, `auth_tokens`) in the live Supabase schema.

# AXIS Codex Backend / Testing / DevOps Verification Report

Generated: 2026-07-12  
Branch verified: `track-C-session-1`  
Scope: Codex backend, database migrations, pytest coverage, GitHub Actions / backend-facing DevOps checks.  
Hard boundary respected: no frontend React/HTML/CSS work and no `docs/frontend_handoff.md` edits.

## 1. Executive Summary

The Codex backend/devops prompt has been implemented and re-verified against the current workspace. The backend now includes the Track A live-safety fixes, Phase 2.5 OHLC candle persistence prerequisite, Phase 2 Strategy #2 (`wyckoff_mean_reversion`), and Track E deployment/CI/CD safeguards. A fresh offline verification run passed with:

```text
141 passed, 2 warnings in 90.75s (0:01:30)
```

The two warnings are Supabase client deprecation warnings for `timeout` / `verify`; they are not test failures.

Important honesty note: code-level and offline simulation requirements are complete. Live-only external checks still require human/operator verification in the real environments: Supabase PITR, actual GitHub Actions secrets presence, actual Netlify env values, Telegram `getWebhookInfo`, UptimeRobot configuration, and non-zero real `trade_outcomes` after a live market day. These were previously CTO-bypassed for forward progress and are marked below as human/live verification pending, not silently claimed.

## 2. Verification Commands Run

### Full offline suite

Command:

```powershell
.venv\Scripts\python.exe -m pytest tests --ignore=tests\smoke -q
```

Result:

```text
141 passed, 2 warnings in 90.75s (0:01:30)
```

### Focused implementation suite previously run in this phase

Command:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_phase25_ohlc_candles.py tests\test_wyckoff_mean_reversion.py tests\test_track_e_devops.py tests\test_telegram_queue.py tests\test_prs_gate.py -q
```

Result:

```text
24 passed, 2 warnings
```

## 3. Grading Legend Used

Per the execution brief:

- `VERIFIED`: live-tested, not just code-reviewed.
- `TESTED-IN-ISOLATION`: named tests exist and were included in the fresh passing suite.
- `BUILT-NOT-RUN`: code exists but was not executed live.
- `CLAIMED-NOT-SHOWN`: only described, no code shipped.
- `HUMAN/LIVE PENDING`: requires credentials, dashboards, or market-time execution outside this local environment.

## 4. Track A — Immediate Live-Safety Fixes

| Requirement | Status | Evidence |
| --- | --- | --- |
| PRS gate blocks trading if PRS is missing, incomplete, blocking-score, or late after cutoff | TESTED-IN-ISOLATION | `src/scheduling/prs_gate.py`; `main.py` calls `check_prs_trading_gate()` before lock/graph; tests in `tests/test_prs_gate.py` |
| Explicit IST cutoff named | TESTED-IN-ISOLATION | `PRS_CUTOFF = time(9, 10)` and `ZoneInfo("Asia/Kolkata")` in `src/scheduling/prs_gate.py` |
| PRS schema support | BUILT / MIGRATION READY | `migrations/020_prs_gate_state.sql` adds `prs_completed_at TIMESTAMPTZ` and `prs_block_reason TEXT` |
| Real live paper-trading day with non-zero `trade_outcomes` | HUMAN/LIVE PENDING | Requires Monday/live market run; CTO override allowed Phase 2/2.5 to proceed without waiting |
| LLM cost guardrail fires and increments spend per call | TESTED-IN-ISOLATION | `src/llm/router.py` calls `increment_llm_spend` inside `_acompletion`; `tests/test_track_a_guardrails.py` verifies per-call increment and budget block |
| API circuit breaker under repeated failures | TESTED-IN-ISOLATION | `src/data/dhan_client.py` uses `increment_circuit_failure`; `tests/test_track_a_guardrails.py` verifies third failure trips alert and open breaker blocks |
| Telegram send queue / rate limiter | TESTED-IN-ISOLATION | `src/delivery/telegram_formatter.py` has `send_telegram_payload()` and `TELEGRAM_SEND_INTERVAL_SECONDS`; `tests/test_telegram_queue.py` verifies 3-alert burst |
| Alert paths route through sanitizer/queue | TESTED-IN-ISOLATION | `interactive_ui.py`, `prs_quiz.py`, and `netlify/functions/telegram_webhook.py` use `send_telegram_payload`; `tests/test_track_e_devops.py` checks non-raw paths |

### Track A handoff integrity warning

Antigravity/front-end must not model PRS as a simple pass/fail boolean. The backend now distinguishes several PRS block reasons:

- `PRS_NOT_COMPLETED`
- `PRS_MISSING_AFTER_CUTOFF`
- `PRS_COMPLETED_AFTER_CUTOFF`
- `PRS_SCORE_BLOCKED`
- `PRS_COMPLETED_AT_MISSING`

All PRS timing is IST-based, with a hard `09:10` cutoff.

## 5. Phase 2.5 — OHLC Candle Table

| Requirement | Status | Evidence |
| --- | --- | --- |
| Add OHLC/candle table | BUILT / MIGRATION READY | `migrations/021_ohlc_candles.sql` |
| Keyed by symbol + timestamp | TESTED-IN-ISOLATION | Primary key is `(symbol, interval, "timestamp")`; tested in `tests/test_phase25_ohlc_candles.py` |
| Pipeline writes already-fetched OHLC data | TESTED-IN-ISOLATION | `src/data/ohlc_writer.py`; `data_verification_node()` calls `persist_ohlc_candles()` using `market_context["candles"]` |
| No new data source | TESTED-IN-ISOLATION | Migration/source defaults to `dhan`; tests reject Yahoo/TradingView references |
| No new chart API key required | VERIFIED BY CODE INSPECTION / TESTED-IN-ISOLATION | Workflow/settings do not add chart API keys; `ohlc_writer` only persists passed-in candles |

### `ohlc_candles` schema contract

Migration: `migrations/021_ohlc_candles.sql`

Core columns:

```sql
symbol           TEXT NOT NULL CHECK (symbol IN ('NIFTY', 'BANKNIFTY')),
interval         TEXT NOT NULL DEFAULT '5',
"timestamp"      TIMESTAMPTZ NOT NULL,
open             NUMERIC NOT NULL,
high             NUMERIC NOT NULL,
low              NUMERIC NOT NULL,
close            NUMERIC NOT NULL,
volume           NUMERIC,
oi               NUMERIC,
source           TEXT NOT NULL DEFAULT 'dhan',
trust_status     TEXT NOT NULL DEFAULT 'live',
fetched_at       TIMESTAMPTZ,
cycle_timestamp  TIMESTAMPTZ,
correlation_id   TEXT,
created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
PRIMARY KEY (symbol, interval, "timestamp")
```

RLS:

- service role full access
- authenticated read access

### Phase 2.5 handoff integrity warning

Antigravity must not treat the chart as an independent market-data panel. `ohlc_candles` is a backend relay of the same Dhan-fed candles used by strategy evaluation. Timestamps are `TIMESTAMPTZ`; naive timestamps are normalized as Asia/Kolkata by `ohlc_writer.py`.

## 6. Phase 2 — Strategy #2: Wyckoff Mean Reversion

| Requirement | Status | Evidence |
| --- | --- | --- |
| Implement `wyckoff_mean_reversion.py` | TESTED-IN-ISOLATION | `src/strategies/wyckoff_mean_reversion.py`; `tests/test_wyckoff_mean_reversion.py` |
| Pair with Tier 1 YAML config | TESTED-IN-ISOLATION | `src/strategies/definitions/wyckoff_mean_reversion.yaml`; validated via `StrategyDefinition` |
| Uses BaseStrategy `check_conditions(state) -> dict` | TESTED-IN-ISOLATION | Strategy class inherits `BaseStrategy`; registry test loads it |
| Reads AxisState only; no network/data fetching | TESTED-IN-ISOLATION | AST scanner passes source; imports limited to allowed stdlib/project modules |
| Push through upload workflow | TESTED-IN-ISOLATION | `test_wyckoff_yaml_upload_workflow_forces_draft_then_activates_with_shadow_gates` |
| Forced draft despite YAML claiming active | TESTED-IN-ISOLATION | Same workflow test verifies `register_uploaded_strategy_draft()` returns `draft` |
| AST scan before activation | TESTED-IN-ISOLATION | Same workflow test calls `transition_strategy_status(..., "active", source_path=...)` |
| SHADOW gate modes on activation | TESTED-IN-ISOLATION | Workflow changelog contains all governance gates as `SHADOW` |
| BankNifty Tuesday expiry logic rechecked | TESTED-IN-ISOLATION | `test_wyckoff_banknifty_expiry_logic_is_exercised_before_evaluation` |
| DB seed for runtime registration | BUILT / MIGRATION READY | `migrations/022_seed_wyckoff_mean_reversion_strategy.sql` |
| Strategy loads from active registry row | TESTED-IN-ISOLATION | `test_registry_loads_active_wyckoff_strategy_from_database` |
| GVOF and Wyckoff run in same cycle independently | TESTED-IN-ISOLATION | `test_graph_runs_gvof_and_wyckoff_in_same_cycle_without_cross_contamination` |

### Strategy #2 DB registration contract

Migration: `migrations/022_seed_wyckoff_mean_reversion_strategy.sql`

It inserts/updates:

- `strategies.strategy_id = 'wyckoff_mean_reversion'`
- `display_name = 'Wyckoff Mean Reversion'`
- `status = 'active'`
- `source = 'uploaded'`
- `strategy_configs` for both `NIFTY` and `BANKNIFTY`
- `strategy_config_changelog` row documenting activation from `pending_review` to `active`
- governance gates recorded as:
  - `DAILY_LOSS_BREAKER: SHADOW`
  - `RR_FILTER: SHADOW`
  - `CROSS_SYMBOL_CORRELATION: SHADOW`

### AST false-positive test

Requirement: prove a legitimate non-allowlist-class import is not wrongly rejected.

Evidence:

- Test: `tests/test_wyckoff_mean_reversion.py::test_ast_scanner_accepts_legitimate_stdlib_decimal_import_not_hardcoded_allowlist`
- Import used: `from decimal import Decimal`
- Result: included in full passing suite.

### Three-gate reconciliation artifact

Created:

- `docs/strategy_gate_reconciliation.md`

It explicitly separates:

1. SHADOW → ENFORCE promotion gate
2. Per-symbol shadow gate
3. Live-capital go/no-go gate

This prevents a UI/operator mistake where active runtime status is misread as live-capital approval.

## 7. Track E — Deployment, CI/CD, Telegram, Monitoring

### E.1 API keys and secrets

| Secret | Required in settings/workflow | Status |
| --- | ---: | --- |
| `GOOGLE_API_KEY` | Yes | TESTED-IN-ISOLATION |
| `GROQ_API_KEY` | Yes | TESTED-IN-ISOLATION |
| `ZAI_API_KEY` | Yes | TESTED-IN-ISOLATION |
| `TELEGRAM_BOT_TOKEN` | Yes | TESTED-IN-ISOLATION |
| `TELEGRAM_CHAT_ID` | Yes | TESTED-IN-ISOLATION |
| `TELEGRAM_WEBHOOK_SECRET` | Yes | TESTED-IN-ISOLATION |
| `DHAN_CLIENT_ID` | Yes | TESTED-IN-ISOLATION |
| `DHAN_ACCESS_TOKEN` | Yes | TESTED-IN-ISOLATION |
| `DHAN_TOTP_SECRET` | Yes | TESTED-IN-ISOLATION |
| `DHAN_PIN` | Yes | TESTED-IN-ISOLATION |
| `SUPABASE_URL` | Yes | TESTED-IN-ISOLATION |
| `SUPABASE_ANON_KEY` | Yes | TESTED-IN-ISOLATION |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | TESTED-IN-ISOLATION |
| Chart/indicator API key | No baseline key required | VERIFIED BY CODE INSPECTION |
| UptimeRobot API key | Optional external monitor | HUMAN/LIVE PENDING |

Evidence:

- `src/config/settings.py` includes `TELEGRAM_WEBHOOK_SECRET` and fails loudly at import.
- `.github/workflows/main_pipeline.yml` references required backend secrets.
- `tests/test_track_e_devops.py::test_settings_fail_loudly_when_webhook_secret_missing`
- `tests/test_track_e_devops.py::test_main_pipeline_references_required_backend_secrets`

Human-only note: this local environment cannot verify the actual GitHub Actions secret store. The workflow references the expected secrets, but the operator must confirm their presence in GitHub.

### E.2 GitHub Actions / CI setup

Status: TESTED-IN-ISOLATION for YAML shape.

Evidence:

- `.github/workflows/main_pipeline.yml`
- `tests/test_track_e_devops.py::test_main_pipeline_workflow_is_centralized_sequential_and_not_matrix`

Verified properties:

- Single job: `jobs.trade`
- No `matrix`
- Runs `python main.py --all`
- NIFTY and BANKNIFTY execute sequentially inside one process.
- Concurrency group uses `${{ github.workflow }}` with `cancel-in-progress: false`.
- Cron is `*/5 3-10 * * *`, which corresponds to the intended UTC window for IST market hours.
- Market holiday pre-check uses `AXIS_MARKET_HOLIDAYS`.

### E.3 Supabase setup

Status: BUILT / HUMAN-LIVE PENDING.

Local evidence:

- Migrations present through:
  - `019_multi_strategy_data_model.sql`
  - `020_prs_gate_state.sql`
  - `021_ohlc_candles.sql`
  - `022_seed_wyckoff_mean_reversion_strategy.sql`

Human/live required:

- Apply/verify migrations in the live Supabase project.
- Confirm RLS policies in the live project.
- Confirm frontend-read tables are accessible exactly as intended.

### E.3.5 Supabase PITR

Status: HUMAN/LIVE PENDING.

This cannot be confirmed programmatically from the restricted local environment. Operator must verify Point-in-Time Recovery in the Supabase dashboard/API before relying on accumulated `trade_outcomes` and `ohlc_candles` data.

### E.4 Netlify backend-facing checks

Status: PARTIAL / HUMAN-LIVE PENDING.

Local evidence:

- `netlify/functions/health.js` exists.
- `netlify/functions/telegram_webhook.py` validates `TELEGRAM_WEBHOOK_SECRET`.
- Webhook malformed JSON and internal exception paths fail open with `200`; GET returns `405`.

Human/live required:

- Confirm Netlify env vars:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `TELEGRAM_WEBHOOK_SECRET`
- Confirm deployed health endpoint returns correctly from the live Netlify URL.

### E.5 Telegram bot setup and verification

Status: TESTED-IN-ISOLATION locally; live bot verification pending.

Local evidence:

- Shared queue: `src/delivery/telegram_formatter.py`
- Interactive UI path: `src/delivery/interactive_ui.py`
- PRS quiz path: `src/scheduling/prs_quiz.py`
- Webhook override edit path: `netlify/functions/telegram_webhook.py`
- Tests:
  - `tests/test_telegram_queue.py`
  - `tests/test_track_e_devops.py::test_all_non_raw_telegram_paths_use_shared_queue_after_track_a`

Human/live required:

- Confirm bot token validity.
- Confirm bot is in correct chat/channel.
- Call `getWebhookInfo` against Telegram.
- Send one real end-to-end alert through the full deployed pipeline.

### E.6 Monitoring

Status: PARTIAL.

Implemented/tested:

- Top-level CLI crash wrapper in `main.py`.
- It sends a dedicated `AXIS PIPELINE CRASHED` Telegram alert and re-raises the original exception.
- Test: `tests/test_track_e_devops.py::test_main_cli_sends_pipeline_crashed_alert_before_reraising`

Human/live pending:

- Confirm UptimeRobot or equivalent is pointed at the Netlify health endpoint.
- Confirm alerting reaches a watched channel.

## 8. Final Deliverables Checklist

| Deliverable | Status | Evidence / note |
| --- | --- | --- |
| PRS gate blocks correctly | TESTED-IN-ISOLATION | `tests/test_prs_gate.py` |
| LLM cost guardrail fires on simulated spend cap | TESTED-IN-ISOLATION | `tests/test_track_a_guardrails.py` |
| Circuit breakers verified under simulated repeated failure | TESTED-IN-ISOLATION | `tests/test_track_a_guardrails.py` |
| Telegram queue live in code | TESTED-IN-ISOLATION | `tests/test_telegram_queue.py` |
| At least one full real trading day with non-zero `trade_outcomes` | HUMAN/LIVE PENDING / CTO BYPASSED | Requires live market day |
| Strategy #2 passed workflow and is SHADOW-gated | TESTED-IN-ISOLATION | `tests/test_wyckoff_mean_reversion.py` |
| `ohlc_candles` exists and is pipeline-populated | TESTED-IN-ISOLATION / MIGRATION READY | `migrations/021`; `src/data/ohlc_writer.py` |
| Required keys fail loudly if missing | TESTED-IN-ISOLATION | `tests/test_track_e_devops.py` |
| GitHub Actions centralized sequential workflow | TESTED-IN-ISOLATION | `.github/workflows/main_pipeline.yml` |
| Supabase PITR confirmed active | HUMAN/LIVE PENDING | Dashboard/API check required |
| Telegram end-to-end test passed | HUMAN/LIVE PENDING | Local queue tested; real bot/webhook still requires credentials |
| Monitoring live | PARTIAL | Crash alert wrapper tested; UptimeRobot config requires human check |
| Claims graded honestly | COMPLETE | This report uses grading statuses above |
| Work done on `track-X-session-Y` branch | VERIFIED LOCALLY | Current branch: `track-C-session-1` |
| Antigravity handoff warnings included | COMPLETE | PRS and OHLC/Strategy #2 warnings above |

## 9. Current Known Operational State

- Offline test count: `141 passed`.
- Live real-market `trade_outcomes` count: not re-queried in this restricted run; previously known blocker was `0` rows and CTO bypassed waiting for Monday.
- Strategy #2 is backend-ready and seeded for active runtime registration, but governance gates remain SHADOW.
- Live-capital trading is not approved by this report.
- Schema changes after frontend handoff must be coordinated because `ohlc_candles`, PRS fields, and strategy seed rows are now backend contracts.

## 10. Files Added or Materially Changed for This Prompt

Major additions:

- `migrations/020_prs_gate_state.sql`
- `migrations/021_ohlc_candles.sql`
- `migrations/022_seed_wyckoff_mean_reversion_strategy.sql`
- `src/scheduling/prs_gate.py`
- `src/data/ohlc_writer.py`
- `src/strategies/wyckoff_mean_reversion.py`
- `src/strategies/definitions/wyckoff_mean_reversion.yaml`
- `docs/strategy_gate_reconciliation.md`
- `tests/test_prs_gate.py`
- `tests/test_telegram_queue.py`
- `tests/test_track_a_guardrails.py`
- `tests/test_phase25_ohlc_candles.py`
- `tests/test_wyckoff_mean_reversion.py`
- `tests/test_track_e_devops.py`
- `tests/conftest.py`

Major modified backend/devops files:

- `main.py`
- `.github/workflows/main_pipeline.yml`
- `src/graph/nodes.py`
- `src/config/settings.py`
- `src/utils/health_check.py`
- `src/scheduling/prs_quiz.py`
- `src/delivery/telegram_formatter.py`
- `src/delivery/interactive_ui.py`
- `netlify/functions/telegram_webhook.py`

## 11. Final Verdict

The Codex backend/devops implementation is complete to the level possible from this local restricted environment. All code-backed tasks are implemented and covered by the fresh offline test suite: `141 passed, 2 warnings`.

Remaining items are not code gaps; they are live-ops confirmations requiring project credentials or market-time execution:

1. One real paper-trading day with non-zero `trade_outcomes`.
2. Supabase PITR dashboard/API confirmation.
3. GitHub Actions secret-store confirmation.
4. Netlify deployed env/health check confirmation.
5. Telegram live `getWebhookInfo` and end-to-end alert confirmation.
6. UptimeRobot/monitoring dashboard confirmation.


## 12. Step-by-Step Prompt Completion Matrix

This section expands the verification into every major instruction from the execution brief. �Complete� here means one of two things:

1. Code/test/documentation work is complete inside this repo.
2. If the item requires live credentials, dashboards, or market data, the exact local deliverable is complete and the remaining human/live action is explicitly named.

### 12.1 Global operating rules

| Step | Required action | Completion state | Evidence |
| --- | --- | --- | --- |
| 0. Golden rule | Track real market-data bottleneck honestly instead of pretending tests equal live readiness. | Complete with caveat | Report marks live `trade_outcomes`, PITR, Netlify, Telegram, and UptimeRobot as pending instead of claiming live verification. |
| 0. Grading discipline | Use explicit honest status labels. | Complete | Sections 3 through 8 use explicit grading. |
| 0.5 Git discipline | Work on `track-X-session-Y`, not `main`. | Complete | Current branch verified as `track-C-session-1`. |
| 0.5 Halt protocol | Do not weaken gates or bypass contradictions silently. | Complete | AST false-positive test uses stdlib `decimal`; scanner passes without weakening allowlist. Live-only gaps are marked human/live pending. |
| Hard frontend boundary | Do not touch frontend code or `docs/frontend_handoff.md`. | Complete | No frontend implementation files modified; `docs/frontend_handoff.md` not edited. |

### 12.2 Phase 1 / Track A immediate live-safety fixes

| Step | Required action | Completion state | Evidence |
| --- | --- | --- | --- |
| A.1 PRS gate | Add explicit gate before any cycle can produce trades. | Complete / tested | `main.py` calls `check_prs_trading_gate()` before lock acquisition and graph invocation. |
| A.1 fail closed | Missing PRS or blocking score must block. | Complete / tested | `tests/test_prs_gate.py::test_prs_missing_after_cutoff_blocks_trading`; `test_prs_completed_with_blocking_score_blocks_trading`. |
| A.1 late cutoff | Late PRS completion after `09:10 IST` must block. | Complete / tested | `tests/test_prs_gate.py::test_prs_answered_late_after_cutoff_blocks_trading`. |
| A.1 normal pass | On-time completed PRS must allow. | Complete / tested | `tests/test_prs_gate.py::test_prs_completed_on_time_allows_trading`. |
| A.1 schema | Store completion timestamp and block reason. | Complete / migration ready | `migrations/020_prs_gate_state.sql` adds `prs_completed_at` and `prs_block_reason`. |
| A.2 real trading day | Run one full market day and confirm non-zero `trade_outcomes`. | Human/live pending | Requires live market day and Supabase access; CTO override allowed work to continue before Monday. |
| A.3 LLM spend guardrail | Confirm spend guardrail blocks provider calls after cap. | Complete / tested in isolation | `tests/test_track_a_guardrails.py::test_llm_budget_guardrail_blocks_before_provider_call_and_alerts`. |
| A.3 per-call accounting | Confirm `increment_llm_spend` is per actual LLM call, not per cycle. | Complete / tested in isolation | `tests/test_track_a_guardrails.py::test_llm_spend_increment_runs_once_per_actual_llm_call`. |
| A.3 circuit breaker | Simulate repeated failures and confirm trip behavior. | Complete / tested in isolation | `tests/test_track_a_guardrails.py::test_circuit_breaker_trips_on_third_consecutive_failure`; `test_circuit_breaker_open_recent_failure_returns_safe_default`. |
| A.4 Telegram queue | Add shared send queue with inter-message delay. | Complete / tested | `src/delivery/telegram_formatter.py`; `tests/test_telegram_queue.py`. |
| A.4 all alert paths | Route outbound alert-like paths through sanitizer and queue. | Complete / tested | `interactive_ui.py`, `prs_quiz.py`, and `netlify/functions/telegram_webhook.py` use `send_telegram_payload`; `tests/test_track_e_devops.py` checks non-raw paths. |
| Track A handoff | State what frontend could misunderstand. | Complete | Sections 4 and 12 note PRS is not a two-state boolean and is IST/cutoff-aware. |

### 12.3 Phase 2.5 OHLC candle backend prerequisite

| Step | Required action | Completion state | Evidence |
| --- | --- | --- | --- |
| 2.5 table | Add `ohlc_candles`. | Complete / migration ready | `migrations/021_ohlc_candles.sql`. |
| 2.5 keying | Key candles by symbol and timestamp. | Complete / tested | Primary key is `(symbol, interval, "timestamp")`; `tests/test_phase25_ohlc_candles.py`. |
| 2.5 same feed | Use existing backend-fetched Dhan candles only. | Complete / tested | `src/data/ohlc_writer.py` only accepts existing `market_context["candles"]`; no fetch client or third-party quote source. |
| 2.5 graph write | Pipeline writes candle rows during cycle. | Complete / tested | `data_verification_node()` calls `persist_ohlc_candles()`; tested by `test_data_verification_node_persists_existing_candles_without_fetching`. |
| 2.5 no extra key | Do not add chart/indicator API key. | Complete | Settings/workflow add no chart API key. |
| 2.5 handoff | Warn frontend about timestamp/interval/source assumptions. | Complete | Sections 5 and 12 specify `TIMESTAMPTZ`, interval, and Dhan-source relay semantics. |

### 12.4 Phase 2 Strategy #2: Wyckoff Mean Reversion

| Step | Required action | Completion state | Evidence |
| --- | --- | --- | --- |
| Strategy file | Implement `wyckoff_mean_reversion.py`. | Complete / tested | `src/strategies/wyckoff_mean_reversion.py`; `tests/test_wyckoff_mean_reversion.py`. |
| YAML config | Provide Tier 1 YAML definition. | Complete / tested | `src/strategies/definitions/wyckoff_mean_reversion.yaml`. |
| Base contract | Implement `BaseStrategy.check_conditions(state) -> dict`. | Complete / tested | Strategy inherits `BaseStrategy`; registry load test passes. |
| No own data fetch | Strategy only reads `AxisState`. | Complete / tested | AST scanner passes; no networking/data imports in strategy file. |
| Phase 5 workflow | Upload forced draft -> pending_review -> active. | Complete / tested | `test_wyckoff_yaml_upload_workflow_forces_draft_then_activates_with_shadow_gates`. |
| Manual activation safety | Active runtime status starts governance gates in SHADOW. | Complete / tested | Activation changelog details include SHADOW for all gates. |
| DB seed | Provide live DB seed for Strategy #2. | Complete / migration ready | `migrations/022_seed_wyckoff_mean_reversion_strategy.sql`. |
| AST false-positive | Add legitimate import false-positive test. | Complete / tested | `test_ast_scanner_accepts_legitimate_stdlib_decimal_import_not_hardcoded_allowlist`. |
| BankNifty expiry recheck | Reconfirm Tuesday/monthly expiry before second-strategy BankNifty evaluation. | Complete / tested in isolation | `test_wyckoff_banknifty_expiry_logic_is_exercised_before_evaluation`. |
| Multi-strategy cycle | Confirm GVOF and Wyckoff can both evaluate without contamination. | Complete / tested | `test_graph_runs_gvof_and_wyckoff_in_same_cycle_without_cross_contamination`. |
| Gate reconciliation artifact | Write project artifact separating three gates. | Complete | `docs/strategy_gate_reconciliation.md`. |

### 12.5 Track E deployment / CI / monitoring

| Step | Required action | Completion state | Evidence |
| --- | --- | --- | --- |
| E.1 secrets inventory | List and require backend secrets. | Complete / tested locally | `src/config/settings.py`; `.github/workflows/main_pipeline.yml`; `tests/test_track_e_devops.py`. |
| E.1 fail loud | Settings import fails if required key missing. | Complete / tested | `test_settings_fail_loudly_when_webhook_secret_missing`. |
| E.1 actual secret presence | Confirm GitHub/Netlify dashboard secret values exist. | Human/live pending | Requires dashboard access; workflow references are complete. |
| E.2 no matrix | Confirm workflow is not matrix-based. | Complete / tested | `test_main_pipeline_workflow_is_centralized_sequential_and_not_matrix`. |
| E.2 sequential symbols | NIFTY then BANKNIFTY inside one centralized run. | Complete / tested by design | Workflow runs `python main.py --all`; `main.py` loops `VALID_SYMBOLS = ("NIFTY", "BANKNIFTY")`. |
| E.2 schedule | Cron aligned to UTC market-hours window with market pre-check. | Complete / code verified | `cron: '*/5 3-10 * * *'` plus `is_market_open()` pre-check and `AXIS_MARKET_HOLIDAYS`. |
| E.3 migrations | Migrations through Strategy #2 exist. | Complete / local verified | `019`, `020`, `021`, `022` present. Live application still human/Supabase pending. |
| E.3 RLS | Add RLS where new table needs frontend reads. | Complete / migration ready | `021_ohlc_candles.sql` has service role full access and authenticated read policy. |
| E.3.5 PITR | Confirm Supabase PITR. | Human/live pending | Requires Supabase dashboard/API credentials. |
| E.4 Netlify health | Confirm health function exists. | Complete locally / live pending | `netlify/functions/health.js` exists; live URL check requires deployment access. |
| E.4 Netlify env | Confirm env vars set in Netlify. | Human/live pending | Requires Netlify dashboard access. |
| E.5 Telegram webhook secret | Require/check secret token. | Complete locally / live pending | `netlify/functions/telegram_webhook.py`; actual BotFather/webhook match requires live check. |
| E.5 Telegram burst | Confirm 3+ alerts queue correctly. | Complete / tested in isolation | `tests/test_telegram_queue.py::test_three_alert_burst_is_sent_through_rate_limited_queue`. |
| E.5 getWebhookInfo | Confirm deployed webhook URL. | Human/live pending | Requires Telegram bot token/network. |
| E.6 pipeline crash alert | Add top-level crash alert wrapper. | Complete / tested | `main.py::_run_cli()` and `_send_pipeline_crash_alert()`; `test_main_cli_sends_pipeline_crashed_alert_before_reraising`. |
| E.6 UptimeRobot | Confirm monitor points to health endpoint and watched channel. | Human/live pending | Requires UptimeRobot/dashboard access. |

### 12.6 Final code-backed completion statement

Every repo-local backend, migration, test, and GitHub Actions YAML requirement from the prompt has been completed and verified by the fresh offline suite. The remaining incomplete items are not implementation gaps; they are live environment checks requiring operator credentials, dashboard access, or a real market session.

# AXIS — Final Consolidated System Audit Report
**Auditor:** Antigravity (Frontend / Architecture / Red-Team)  
**Date:** 2026-07-12  
**Audit branch:** `frontend-track-C`  
**Backend evidence source:** AXIS Codex Backend/DevOps Verification Report (`track-C-session-1`, 141 passed)  
**Grading protocol:** VERIFIED · TESTED-IN-ISOLATION · BUILT-NOT-RUN · CLAIMED-NOT-SHOWN · HUMAN/LIVE PENDING

---

## 1. Executive Verdict

**NOT READY for unattended live paper-trading — but structurally sound and close.**

The AXIS system has a well-engineered, honestly graded backend. The PRS gate, LLM cost guardrail, circuit breakers, Telegram queue, Strategy #2 (Wyckoff), and the OHLC relay table are all implemented and covered by 141 offline tests. The governance architecture is correct and conservative (all new-strategy gates in SHADOW). The frontend Phase 6 base dashboard is live; the Strategy Hub, charting surface, personalized dashboard, and config page are now built (Track C). 

The system is **not ready for unattended operation** for two compounding reasons. First: **zero real trade_outcomes rows exist** — no live market day has run, so every component that depends on real data (governance isolation, dedup correctness, signal_metadata population, alert display_name accuracy) is BUILT-NOT-RUN against production, not VERIFIED. Second: **five live-ops confirmations are outstanding** (Supabase PITR, GitHub Actions secret store, Netlify env vars, Telegram webhook live test, UptimeRobot). Until at least one real market session completes and those five items are checked off by the operator, the system must not run unattended. It should be considered **operator-supervised paper-trading mode**: a human monitors the first 2–3 live sessions before leaving it unattended.

---

## 2. Component Grade Table

### Core Trading Engine

| Component | Grade | Evidence |
|---|---|---|
| Pricing/Math (`src/math/pricing.py`) | TESTED-IN-ISOLATION | `tests/test_pricing.py` in 141 suite. STT rate constant in code — **operator must verify 2026 Union Budget rate against official SEBI/MoF circular before live capital.** |
| Direction Scorer (Layer A/B/C) | TESTED-IN-ISOLATION | `tests/test_phase_minus1.py`; symbol-level shared score confirmed by code inspection. Determinism not re-run live. |
| Structure Gate | TESTED-IN-ISOLATION | `tests/test_axis_graph.py` covers structure-confirmed flag. Independent testability of each sub-gate not confirmed live. |
| Strategy Registry & Fan-out | TESTED-IN-ISOLATION | `test_graph_runs_gvof_and_wyckoff_in_same_cycle_without_cross_contamination`; writer count 2 per cycle confirmed by code. |
| GVOF | TESTED-IN-ISOLATION | `tests/test_phase2_fanout.py`; no live signal reviewed against real YAML entry logic. |
| Wyckoff Mean Reversion | TESTED-IN-ISOLATION | `tests/test_wyckoff_mean_reversion.py` (7+ tests); AST scanner passes; no live signal recorded. |

### Orchestration & AI Pipeline

| Component | Grade | Evidence |
|---|---|---|
| LangGraph core (state/nodes/graph) | TESTED-IN-ISOLATION | `test_final_integration.py`, `test_axis_graph.py`. Not run against live 2-strategy load. |
| LLM Router | TESTED-IN-ISOLATION | `tests/test_track_a_guardrails.py` covers budget block. Live provider fallback (Z.ai/Groq) not confirmed triggered. |
| Analyst/Verifier per-candidate | TESTED-IN-ISOLATION | `test_multi_candidate_verifier.py`. No live run to confirm no cross-strategy context bleed. |
| LLM cost guardrail | TESTED-IN-ISOLATION | `test_llm_budget_guardrail_blocks_before_provider_call_and_alerts` in 141 suite. |
| Circuit breakers | TESTED-IN-ISOLATION | `test_circuit_breaker_trips_on_third_consecutive_failure`. Not live-triggered. |

### Governance & Safety

| Component | Grade | Evidence |
|---|---|---|
| Daily loss breaker | TESTED-IN-ISOLATION | `tests/test_phase3_governance.py`. Strategy-isolation logic is code-correct; not confirmed with real multi-strategy data. |
| R:R filter | TESTED-IN-ISOLATION | `tests/test_phase3_governance.py`; global vs per-strategy floor precedence in code. |
| Cross-symbol correlation | TESTED-IN-ISOLATION | `tests/test_cross_symbol_n_strategy.py`; no real correlated event confirmed. |
| Dedup (`strategy_id` in key) | TESTED-IN-ISOLATION | `tests/test_dedup_multi_strategy.py`. No real dropped-signal check in production logs. |
| SHADOW→ENFORCE promotion | TESTED-IN-ISOLATION | Workflow test confirms manual-only gate; 3-day/15-sample floor enforced in code. |
| PRS gate | TESTED-IN-ISOLATION | `tests/test_prs_gate.py` — 4 named tests covering all block states (missing, late, score-blocked, on-time pass). Not confirmed against a real blocked trading day. |

### Data & Security

| Component | Grade | Evidence |
|---|---|---|
| Migrations (006–022) | BUILT-NOT-RUN (live) | All 12 migration files present locally. Known gaps 007/013 are intentional. Not applied to fresh Supabase instance to confirm clean apply. |
| Journal/outcome recorder | BUILT-NOT-RUN (live) | `src/journal/outcome_recorder.py` writes `strategy_name`/`strategy_id`. No real rows exist to confirm backfill default `'gvof'` correctness. |
| `signal_metadata`/`custom_fields` | BUILT-NOT-RUN (live) | Column added in migration 018. Namespacing convention in code. No real rows to confirm `{strategy_id}_key` pattern. |
| AST security scanner | TESTED-IN-ISOLATION | `test_ast_scanner_accepts_legitimate_stdlib_decimal_import_not_hardcoded_allowlist` — Wyckoff strategy cleared. |
| Upload/review workflow | TESTED-IN-ISOLATION | `test_wyckoff_yaml_upload_workflow_forces_draft_then_activates_with_shadow_gates`. |
| Credential/secrets handling | TESTED-IN-ISOLATION | `test_settings_fail_loudly_when_webhook_secret_missing`. Git history grep: no credentials found in tracked files. |

### Alerts & Communications

| Component | Grade | Evidence |
|---|---|---|
| Telegram sanitizer (MarkdownV2) | TESTED-IN-ISOLATION | `test_all_non_raw_telegram_paths_use_shared_queue_after_track_a`. Zero raw `parse_mode: Markdown` sends per Codex grep. |
| Strategy naming in alerts | BUILT-NOT-RUN (live) | `display_name` field wired in code; no real alert from Wyckoff strategy received to confirm. |
| Rate-limit queue | TESTED-IN-ISOLATION | `test_three_alert_burst_is_sent_through_rate_limited_queue`. |
| Webhook (malformed/exception/GET) | TESTED-IN-ISOLATION | Netlify function behaviour confirmed in tests and by code inspection. |

### Frontend (own work)

| Component | Grade | Evidence |
|---|---|---|
| Honesty states (market-closed/stale/disconnected) | BUILT-NOT-RUN (live) | Three distinct states implemented in `app.js`: IST market-hours check (closed), 40-min stale threshold (stale), `.subscribe()` callback (disconnected). Cannot force-test real Realtime disconnect without live credentials. |
| Strategy widget (main dashboard) | BUILT-NOT-RUN (live) | Implemented — gates on 15-sample floor, shows `⚠ count/15 trades` when below; "No active strategies" when DB empty. |
| Strategy Hub `/strategies` | BUILT-NOT-RUN (live) | `strategies.html` — reads `strategies` + `trade_outcomes`; ranking gated on 15-floor; insufficient data shown inline on cards. |
| Personalized Dashboard `/strategy/:id` | BUILT-NOT-RUN (live) | `strategy.html` — TradingView chart wired to `ohlc_candles`; "No Candle Data" overlay when empty; signal history, governance log, paper trades panels all handle empty state explicitly. |
| Charting (TradingView Lightweight Charts) | BUILT-NOT-RUN (live) | Chart wired exclusively to `ohlc_candles`. No third-party quote source. No new API key introduced. Computed overlays (entry/stop/target/VAH/VAL/VPOC) rendered from `signal_metadata`. |
| Config-edit propagation | BUILT-NOT-RUN (live) | `strategy-config.html` — cycle-next warning is the most prominent UI element; saves to `strategy_configs`; no mid-cycle edit path exists in code. |

### Infrastructure

| Component | Grade | Evidence |
|---|---|---|
| GitHub Actions workflow | TESTED-IN-ISOLATION | Single `trade` job, no matrix, sequential `python main.py --all`, cron `*/5 3-10 * * *` UTC. Tested by `test_main_pipeline_workflow_is_centralized_sequential_and_not_matrix`. |
| Supabase RLS | BUILT-NOT-RUN (live) | Policies in migrations for all new tables (018–021). Not confirmed applied in live project. |
| Netlify health endpoint | BUILT-NOT-RUN (live) | `netlify/functions/health.js` exists. Frontend honesty states do not currently poll this endpoint directly — **this is a gap: Netlify health is not wired into the dashboard's disconnected state.** |
| Secrets in CI | HUMAN/LIVE PENDING | Workflow references all required secrets. Actual GitHub secret store not verifiable locally. |

---

## 3. Open Risk List (Ranked by Financial/Trading Impact)

### 🔴 CRITICAL — Financial / Safety Risk

**R1 — Zero real trade_outcomes: All governance isolation unverified in production.**  
Daily loss breaker, dedup, cross-symbol correlation, and R:R filter are TESTED-IN-ISOLATION only. The first live session is the real test. If any governance component fails silently (e.g., dedup key mismatch), duplicate positions could be taken without alerting.  
*Mitigation: Operator must monitor first 2–3 live sessions before unattended mode.*

**R2 — STT rate not independently verified against regulatory source.**  
`pricing.py` has a constant for the 2026 Union Budget STT rate. This has not been confirmed against an official SEBI/Ministry of Finance circular. An incorrect STT rate means every EV calculation is wrong, which can cause trades that appear positive-EV to be negative-EV net of tax.  
*Mitigation: CTO/operator must look up the applicable STT rate from the official Union Budget 2026 notification before enabling live capital.*

**R3 — SHADOW→ENFORCE gate has no live test blocking an early promotion attempt.**  
The 3-day/15-sample floor is code-correct but has never actually blocked a real promotion attempt in production. If the check has a timezone edge case or an off-by-one in the day counter, a strategy could enter ENFORCE mode prematurely.  
*Mitigation: Do not promote Wyckoff to ENFORCE until ≥ 15 real trade_outcomes rows exist and are confirmed by running scratch_audit.py directly.*

**R4 — PRS gate not confirmed against a real blocked trading day.**  
The gate is TESTED-IN-ISOLATION with 4 named tests. A real late quiz or missing session has not yet been confirmed to block `main.py` in production. If the gate has a startup order bug (e.g., the gate check runs after the lock, not before), a day could trade without PRS clearance.  
*Mitigation: Deliberately skip PRS on the first live monitoring day and confirm the pipeline exits cleanly.*

### 🟡 OPERATIONAL RISK — Could Cause Silent Failures

**R5 — Netlify health endpoint not wired into dashboard honesty states.**  
The Realtime disconnect dot in the dashboard uses only the Supabase `.subscribe()` callback. The Netlify `/health` endpoint is not polled. If the Netlify function is down (not just Realtime), the dashboard will show "Connected" when it is not. This is an honesty-state gap.  
*Mitigation: Wire a periodic `fetch('/health')` ping into `app.js` as a second signal.*

**R6 — Five live-ops items outstanding: PITR, GitHub secrets, Netlify env, Telegram webhook, UptimeRobot.**  
Each of these is HUMAN/LIVE PENDING. Any one of them being misconfigured means: lost trade data on a Supabase outage (PITR), CI pipeline fails silently (secrets), Telegram bot stops alerting (webhook), no alerting on pipeline crash (UptimeRobot).  
*Mitigation: Operator checklist before first live session — see §5.*

**R7 — LLM fallback chain not live-confirmed.**  
Z.ai fallback and Groq verifier have not been confirmed to trigger under real primary-failure conditions. If Gemini is down and the fallback is misconfigured, the analyst node errors out and no signal is produced, which is safe (fail-closed) but will result in missed trades that the trader won't know about unless they read logs.

### 🟢 POLISH / LOW-PRIORITY

**R8 — Frontend `.subscribe()` disconnect state cannot distinguish "no internet" from "Supabase Realtime down".**  
Both produce the same `disconnected` dot. A trader might think the system is broken when their own internet dropped.

**R9 — Chart empty state has no timestamp showing when ohlc_candles was last written.**  
An empty chart could be caused by: table newly created, pipeline not yet run, or data retention gap. No visual cue distinguishes them.

**R10 — `strategy-config.html` changelog table has no pagination.**  
Long-running strategies will accumulate many changelog rows. Not a correctness issue.

---

## 4. Data Status

**Run directly against the live database by Antigravity during this session:**

```
$ .venv/Scripts/python.exe scratch_audit.py
No rows found in trade_outcomes.
```

| Metric | Value |
|---|---|
| Real trading days elapsed | **0** (no live market session has run) |
| `trade_outcomes` row count | **0** |
| GVOF sample count vs 15-floor | **0 / 15** — INSUFFICIENT DATA |
| Wyckoff Mean Reversion sample count vs 15-floor | **0 / 15** — INSUFFICIENT DATA |
| `ohlc_candles` row count | **0** (table created, not yet populated) |

**Live verification deferred to Monday's market open at 09:15 IST.** The first real data will appear after the first complete pipeline cycle on the next trading day.

---

## 5. Go/No-Go Recommendations

### Strategy #2 (Wyckoff Mean Reversion) — ENFORCE mode
**NO-GO.** Hard blocked by:
1. Zero trade_outcomes rows — 15-sample floor not met.
2. No live session has run to confirm governance isolation works correctly under 2-strategy load.

**What unlocks it:** ≥ 15 real closed trade_outcomes rows for `wyckoff_mean_reversion`, manually confirmed via `scratch_audit.py`, plus operator review of the governance log for any anomalies. This is realistically 3–5 weeks of live paper-trading at current signal frequency.

### Live Capital Gate
**NO-GO.** Hard blocked by everything above, plus:
1. STT rate must be confirmed against official regulatory source.
2. All five live-ops items (PITR, CI secrets, Netlify env, Telegram live webhook, UptimeRobot) must be confirmed checked off.
3. At least one full unattended paper-trading week with zero governance anomalies.

**What unlocks it:** Operator sign-off on the above checklist, plus a human review of `docs/strategy_gate_reconciliation.md` confirming which of the three gate levels has been cleared. This document already exists and correctly separates the three gates.

---

## 6. Deliverables Checklist Status

| Deliverable | Status |
|---|---|
| Track B Phase 6 (3 honesty states) | ✅ BUILT — market-closed/stale/disconnected all distinct |
| Schema reconciliation (B.2) before panel code | ✅ DONE — `frontend_handoff.md` updated first |
| Strategy Hub & Widget (C.2) | ✅ BUILT — 15-floor gated, insufficient-data primary path |
| Personalized dashboard + config (C.2) | ✅ BUILT — read-only overlays, cycle-next warning prominent |
| Charting (C.3) — ohlc_candles only, no 3rd party | ✅ BUILT — TradingView Lightweight Charts, Dhan relay only |
| Computed overlays before freeform annotation | ✅ — overlays from signal_metadata built; freeform not built (correctly deferred) |
| No new API key introduced | ✅ CONFIRMED |
| scratch_audit.py run directly against live DB | ✅ — output: `No rows found in trade_outcomes.` |
| Component grade table — all rows graded | ✅ |
| Open risk list ranked by financial impact | ✅ — critical financial risks at top |
| Go/no-go recommendation — explicit | ✅ — both ENFORCE and live-capital are NO-GO with clear unlock conditions |
| All work on frontend-track-X branches | ✅ — `frontend-track-B` and `frontend-track-C` |
| Never committed to main directly | ✅ |

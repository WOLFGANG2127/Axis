# AXIS — MASTER BLUEPRINT v11
## The Single-Track, Free-Tier-Reliable, Closed-Loop Edition

**Document class:** Single-source-of-truth engineering reference.
**Supersedes (as a working draft, not as proven fact):** `AXIS_MASTER_v9.md`, the "Complete Project Report" (Source B), and `AXIS_MASTER_v10.md`. This document earns authoritative status the same way v10 was supposed to — by someone actually running Appendix A against the live repo and pasting real output into Appendix B. Until that happens, treat this as the best current synthesis, not as settled fact.
**Compiled:** 2026-07-28.

**What changed structurally, and why:** v10 was internally reviewed and found to have six real problems — two documentation-consistency violations, one genuinely missing build item, one decision that needed a clarifying amendment, one missing phase gate, and one missing explicit reliability doctrine. None of them touch the math, the governance rules, or the non-negotiable constraints in Layer 1 — those carry forward unchanged, verbatim. Full list in §1.3.

The single biggest change: **this document no longer interleaves two build tracks on every page.** v10's "Track S / Track F" split was the right engineering call but the wrong document shape — a developer building the simplified core had to read Full-Build machinery on every section just to mentally subtract it back out. v11 fixes this by making the simplified build (formerly "Track S") **the entire main document** — every section, §2 through §7, describes one buildable system. The full/expanded architecture (formerly "Track F") is preserved in its entirety, deleted from nowhere, but consolidated into **Appendix I** as a single delta reference: "everything that changes if you later decide you need it, and why you might."

---

## §0 — HOW TO USE THIS DOCUMENT

### Step Zero — before you read anything else, run this *(inheriting an existing repo only — building from zero? Skip straight to §5, none of these files exist yet and that's correct, not an error)*

Almost everything downstream depends on whether three specific files exist and match what two of the three source audits (out of three) claimed. Five seconds, before anything else — **but only if you're inheriting a repo that already has history**, not starting from an empty one:

```bash
echo "=== layer_b.py -- this build's scoring module, expected to exist either way ==="
wc -l src/scoring/layer_b.py 2>&1
# EXPECTED: 30 (Source B+C convergence). Errors here on an inherited repo are a
# real red flag. On a from-scratch repo before Step 2 of §5.4, this hasn't been
# written yet either -- that's fine, you're not supposed to be running this yet.

echo "=== memory pipeline files -- informational, NOT a pass/fail gate ==="
wc -l src/memory/ingest.py src/memory/recall.py 2>&1 || echo "ABSENT"
# This build (§2-§6) never creates these files -- there is no RAG pipeline here
# by design (§2.2, Appendix F). Absent is the CORRECT, EXPECTED state for the
# vast majority of repos following this document, not a failure.
# - Absent: expected for this build. Proceed normally, this check told you nothing new.
# - Present, 71/35 lines: either an inherited v9/v10-era repo (corroborates
#   Source B+C -- treat as useful signal) OR a deliberately-promoted Appendix I
#   memory pipeline (also fine -- confirm Appendix J's trigger was actually met
#   and recorded in §1.3's changelog, not just that the files happen to exist).
# - Present with a DIFFERENT line count than 71/35: an actual red flag worth
#   investigating -- something changed these files outside the documented process.
```

- **layer_b.py matches, memory files absent or match one of the two valid "present" cases above:** the working assumptions in §3 hold. Proceed normally.
- **layer_b.py errors or its line count is wrong, on an inherited repo:** stop. Re-run the rest of Appendix A in full before trusting any other claim in §3. Treat every `S1-CITED` tag as unconfirmed until you do.

This is the cheapest possible tripwire for the single biggest epistemic risk in a document like this: two non-independent audits agreeing with each other doesn't make them right, it makes them correlated. Source C's file reads are what turns "two people said the same thing" into "someone actually looked."

**Before trusting anything this document says about *how* the system runs, not just *what* it does:** three infrastructure facts get assumed confidently throughout — that the GH Actions concurrency group exists (D-051, underpins all of D-T9's reasoning), that the Procfile points somewhere real (D-010), and that the inbound endpoint exists (D-055, underpins every `/ready`/`/record`/`/close`/`/resend` claim). Appendix A's D-051/D-010/D-055 blocks check all three in about 30 seconds. They're not repeated here — one script, one place to run it (§2.0 principle 3) — but skipping them means every "single-threaded execution via GH Actions" claim in this document is aspirational until you've actually checked.

### Who should start where

| If you are... | Start at... | You will get... |
|---|---|---|
| Building **from zero** | §5 (Build-From-Scratch Runbook) | An ordered, gated command list for the whole system — this document's only build path |
| Inheriting the **existing, partially-broken** repo | Step Zero → §1 → §4.3 (Delta Ledger), starting at D-001 | The exact list of what's broken, in the exact priority order the evidence supports |
| An **agent with filesystem access** (Claude Code, Devin, Cursor, etc.) | The branching instruction below | A punch list it can execute unattended, correctly sequenced |
| Deciding **whether this is safe to run with real money** | §2 (Layer 1) + §4.4 Phase 5 + §4.4 Phase 7 | The non-negotiable constraints, and an explicit statement that capital risk is a human-only decision this document never makes for you |
| Wanting **just the architecture** | Appendix G (Rosetta Stone) | Every node mapped to its file, dependencies, DB/state reads and writes, failure behavior |
| Wanting **the actual how-to-code-it detail, component by component** | Appendix K (Component Guide) | Per-file target, build shape, runtime mechanism, and the specific test that proves it's done — not just what it does, but how to prove it |
| Wanting **the whole system's shape at a glance**, no code | Appendix L (Text Architecture Diagram) | Every box, every arrow, every external service, drawn in plain text — the fastest way to see how the pieces connect before reading the detail |
| Wondering **whether to add back the richer, original architecture** later | Appendix I (Full-Build Deltas) + Appendix J (Promotion Playbook) | What each piece of the expanded system buys you, what it costs, and the exact evidence-based trigger for adding it |

### Agent instruction (branching, not linear)

> "**First, check which scenario applies.** If there is no existing repo, or an empty one — building from zero — skip Step Zero and this block entirely, go straight to §5, and follow its build order. The rest of this instruction is for inheriting an existing repo only.
> Run the Step Zero command above and the rest of Appendix A. Paste the output into Appendix B.
> **If D-001 is confirmed** (no call site found for `score_layer_a/b/c()` outside `src/scoring/` itself): stop working the ledger top-to-bottom. D-001 means nodes 3 through 9 never ran on real data. Build the Step-3 data-orchestration module from §5.4 first. Only after that closes, resume the P0 ledger in order.
> **If D-001 is not confirmed** (a real call site exists): the system has been generating real signals, which changes the risk calculus, not just the ledger's starting point. Don't mechanically start at D-004 — a live system's most urgent gaps are the ones that can hurt it *while it keeps running*: check D-050 (a human may already be holding a position the system has no memory of) and D-051 (duplicate cycle execution risk) before anything else, then proceed through the P0 ledger in order. A system that's already trading real signals needs its safety gates closed first; a system still being built from zero can afford to follow the ledger's own stated priority order.
> Either way: do not modify §2 (Layer 1)'s locked formulas or governance rules. **This does not mean halting on every open provenance question** — an item already tagged `S3-UNSCANNED` with a stated decision-tree default (§2.4.1, §4.1) is a known, tracked, actionable question, not a reason to stop; build against the stated default and move on. Stop and flag only a *genuinely new* discrepancy you find that this document doesn't already know about — quietly changing locked code to match a different assumption is what's actually forbidden here, not proceeding past an already-documented open question. Do not add any Appendix I (Full-Build) component without first checking it against Appendix J's promotion criteria."

### The confidence grammar this document uses everywhere

`S1-CONFIRMED` — a command was run against the real repo/DB/network, output pasted below the claim.
`S1-CITED` — a source audit reports direct observation with falsifiable specifics; treated as working baseline, **not** as confirmed.
`S2-DERIVED` — not directly observed, logically implied by an S1 fact.
`S3-UNSCANNED` — nobody has looked yet.
`S4-CONFLICTED` — two S1-quality sources disagree and nothing has broken the tie.

A single-source `S1-CITED` claim is weaker than a corroborated one. This document flags single-source claims explicitly wherever they appear. **D-001 is the single most consequential example and is flagged accordingly throughout.**

---

## §1 — EXECUTIVE SUMMARY

**What AXIS is:** a pre-trade intelligence and risk-governance engine for NIFTY and BankNifty index options on the NSE. It reads market structure, scores direction, checks strategies, optionally narrates via an LLM, applies governance math, and — if everything clears — sends a Telegram alert. **A human reads the alert and places the trade by hand.** AXIS has no order-placement code anywhere, by permanent design.

**The most important open question, stated at the confidence level the evidence supports:** one source audit (Source C), *not corroborated by the other two*, reports finding no code path that fetches live option-chain/VIX/FII data and writes it into `market_context` before scoring runs. If true: Layer 1's own math spec (§2.4) hard-aborts the pipeline on any score in the 2.0–4.0 "dead zone," and a hardcoded default of `direction_score = 3` sits squarely inside that zone — so this wouldn't just produce bad signals, **it would mean nothing past the direction scorer has ever executed, on any cycle, ever.** This is the highest-value thing to verify first, precisely because it's single-sourced and would be catastrophic if true. Run Step Zero and Appendix A before treating it as settled either way.

**Two more specific, well-evidenced (also single-sourced, also flagged) findings, both closed by explicit build decision:**
- The PRS pre-trade safety quiz, as originally specced, could only ever score 7–9 out of 9 — a multi-step quiz UI is disproportionate machinery for a single-user check anyway, so it's replaced entirely by a one-command `/ready` toggle (D-004).
- A fully-built second strategy (Wyckoff Mean-Reversion) risked drifting from what the database claimed was "active." This class of bug is eliminated structurally: strategies are a version-controlled Python list, not a database-driven registry. There is nothing for the code to disagree with (D-012).

**What v11 changes relative to v10** (full list in §1.3): consolidates the entire document onto one build track instead of two interleaved ones (Full-Build preserved whole in Appendix I); fixes a self-violated rule where the Feature Inventory promised a ledger-ID on every row but didn't have one; restores the cross-symbol correlation step to the visible pipeline (it existed in principle but had vanished from the diagram); clarifies that the per-symbol run-lock is largely redundant once the GitHub Actions concurrency group is live, rather than leaving that implicit; closes a real gap where four Telegram commands (`/ready`, `/record`, `/close`, `/resend`) were specified with no inbound channel able to receive them, by reusing the already-planned Render health-check service instead of standing up a second deployment; and adds an explicit, evidence-gated promotion path for adding back any piece of the expanded architecture later, plus a short, direct statement of the reliability engineering doctrine this whole design follows.

**Counts:** 55 tracked Delta Ledger items (44 inherited from v9, 11 added across v10–v11 — D-045 through D-055). 12 Decision Trees (10 inherited, 2 new — D-T11, D-T12). 7 Core-tier database tables to build immediately — `signals`, `active_position`, `system_paused`, `telegram_updates_processed`, `trader_session_state`, `cycle_summaries`, `macro_regime_flags`; everything else deferred until the feature that needs it is actually being built.

**The only finish line that matters, unchanged since v9:** a statistically honest answer to whether AXIS produces positive expected value after all real costs, once human execution discipline is no longer the variable, at a sample size large enough to mean something — roughly 50 closed trades per strategy, spanning at least 2 monthly expiry cycles.

---

### §1.1 — Confidence Tag Legend

`S1-CONFIRMED · S1-CITED · S2-DERIVED · S3-UNSCANNED · S4-CONFLICTED`. Runtime state (separate axis): `UNTESTED / TESTED-PASS / TESTED-FAIL / N-A`. Type: `[V]erify · [F]ix · [B]uild · [D]ecide · [T]est-execution`.

### §1.2 — Source Provenance Ledger

| Tag | Source | Independence | Reliability |
|---|---|---|---|
| **Source A** | Original "Components Index" — 11-file scan, no live DB/network access | Genuinely blind | Real per-file line counts; several negative claims later proved false |
| **Source B** | "Complete Project Report" — second read, framed as corrections to A | Not independent of A | Where B contradicts A with a specific positive claim, it has consistently checked out |
| **Source C** | Live filesystem read, exact file paths/line ranges/byte counts | Independent in method | Tie-breaker where it corroborates B. Where C stands alone, flagged every time it's referenced |
| **Source D** *(new)* | Internal structural/consistency review of v10 itself | A logic audit, not a filesystem read | Found no code-level facts — found six document-level contradictions and gaps. Does not change any S1/S2/S3 tag; it only fixes how this document describes itself |

**Working rule:** a specific, falsifiable positive claim outranks a vague negative claim from an equally blind source. Where C corroborates B against A, treat it resolved (`S1-CITED`, high confidence). Where C stands alone, this document says so every time.

### §1.3 — Changelog: v10 → v11

1. **Single-track document.** Every section now describes one buildable system (formerly "Track S"). The full, richer architecture (formerly "Track F") is preserved in its entirety in **Appendix I**, not deleted, not thinned — just moved out of the main reading path. Nothing described in v10's Track F is lost; it's one lookup away instead of interleaved into every paragraph.
2. **Feature Inventory traceability rule now actually holds** (§2.2). v10 claimed every row carried a Ledger-ID; roughly a third of rows didn't. Every row now carries either a `D-XXX` reference or an explicit `— verified, no open item` tag. No more silent exceptions to a rule the document itself stated.
3. **Cross-symbol correlation restored to the visible pipeline** (§2.3). It was always supposed to run once per cycle at the orchestrator level — that rule existed in prose (§2.1) but the node-chain diagram didn't show where. It's now an explicit, numbered step between per-symbol dedup and dispatch.
4. **Run-lock redundancy made explicit, not implied** (amends D-T9). Once the GitHub Actions `concurrency:` group is confirmed live, the per-symbol Postgres lock has nothing left to protect against during scheduled runs. This is now stated directly in the node description instead of left for the reader to infer from a separate decision tree about LLM locks.
5. **New: D-055 — the missing inbound channel.** `/ready`, `/record`, `/close`, `/resend` were specified as commands with nowhere for Telegram to actually deliver them, because the inbound webhook was explicitly scoped out of the simplified build. Fixed by adding one authenticated route to the Render health-check service that's already part of the minimal deployment — not a second Netlify Functions deployment for four commands.
6. **New: D-T11 + extended Phase 6 gate.** A concrete, per-component, evidence-based promotion path for adding any single piece of the expanded architecture back in, instead of an all-or-nothing "switch tracks" decision with no defined trigger.
7. **New: §2.0, Engineering Principles for Free-Tier Reliability.** The reliability doctrine this whole design follows was implicit across a dozen individual decisions; it's now stated once, directly, as eight numbered principles, and referenced from the decisions that follow it.
8. **Minor:** LLM cost-guardrail race-condition dependency stated explicitly (relies on single-threaded execution via the GH Actions concurrency group — not a distributed lock); this is a documentation clarification, not a new behavior.
9. **Consistency-hardening pass (post-publication).** A second read caught real cross-reference bugs between sections that a first read missed: the Core-tier table count was stated as 3 in prose while Appendix C already built 5 (now correctly 6, with `cycle_summaries` promoted from Extended to Core — a heartbeat table earns its keep from cycle one, not once Phase 3 arrives); `trader_session_state` carried two boolean columns whose defaults contradicted each other, collapsed into one; D-008, D-046, D-050, D-053, D-T6, and D-T9 had remediation text that was directionally right but left a real gap open (inheriting-repo cleanup, duplicate-position rejection on `/record`, an EOD reset that was promised but not wired to anything, a break-glass prerequisite that would have caused a false "the system is broken" panic, an unbounded prompt block, respectively) — all closed below with the smallest fix that actually closes them, not a new subsystem. Phase 1's gate was rewritten because it referenced a table and a column that don't exist in this schema. One claim about GitHub Actions concurrency semantics — that `cancel-in-progress: false` lets two runs execute at once — was checked against GitHub's own documentation and found false; corrected in D-T9 with the verified behavior instead.
10. **Third hardening pass.** D-001 now specifies a typed Pydantic return contract instead of a raw `dict` (a missing or misnamed key should raise immediately, not get silently defaulted downstream — the exact failure shape that produced D-001 in the first place), plus an explicit clock-sync rule for D-045's staleness check (use the exchange payload's own timestamp, never the GitHub Actions runner's clock — two independent clock-drift failure modes should never be allowed to silently cancel each other out unnoticed). D-050 now names the actual race-condition analysis between the GH Actions cycle and the always-on Render webhook touching `active_position` concurrently, and points at the existing `symbol PRIMARY KEY` constraint as the correct structural backstop rather than inventing a redundant one the schema didn't need. §2.0 principle 4 now states its trade-off against principle 5 explicitly instead of leaving two adjacent principles looking like they silently agree. Appendix H gained a cost model derived from this system's actual cron cadence, not a generic estimate. Appendix J gained numeric thresholds on two triggers. §6.5 (Rollback Principles) and **Appendix K (Component-by-Component Implementation & Verification Guide)** are new — the latter turns every build-order step from §5.4 into a full target/build/mechanism/proof entry, the level of detail an agent or a developer actually needs to write each file correctly rather than just knowing it needs to exist.
11. **Fourth pass — final consistency scan, two proposed additions evaluated and explicitly resolved.** §2.5's kill-switch bullet now states unambiguously that the inbound endpoint returns 401 before any logic runs and 200 only after; §2.6 now draws the line between internally-defined typed contracts (`AxisState`, `ScoredMarketContext` — both `extra="forbid"`, both ours to define) and raw external payload parsing (Dhan/NSE's own JSON shape, which should be read defensively, not validated wholesale); `position_state_check_node` documents explicitly why it uses a plain read with no row lock (it never writes in the same operation — the real protection is the `PRIMARY KEY` on the write path); `system_paused` now seeds **paused** on a fresh deploy, requiring a deliberate flip to start, not just a correct read on failure; principle 7's timeout requirement now has a concrete number (10s); the data layer, the Render service, and the GH Actions workflow each picked up one cheap, low-risk hardening detail (RAM hygiene on raw chain payloads, disabled FastAPI docs routes, a job-level `timeout-minutes`) that holds regardless of hosting choice. Two larger proposals were evaluated and explicitly declined rather than silently ignored: **a TencentDB/multi-agent-memory integration** (out of scope — it addresses a coding-workflow problem, not anything about AXIS itself, and contradicts §2.0 wholesale) and **replacing the GitHub Actions cron with an external HTTP scheduler** (D-T1 now documents why: it swaps a hardened mechanism for an eighth stacked dependency with its own failure modes, to fix a timing precision problem that doesn't matter for a system a human executes by hand). **Appendix L (plain-text system architecture diagram)** is new.
12. **Fifth pass — independent audit, not a response to external review.** Found and closed: retry-with-backoff had no cap (now 2 retries max, so worst-case per-call latency stays bounded against the job-level timeout); the circuit-breaker-trip Telegram alert — present in the original source audit — had been dropped during an earlier condensing pass and is restored; `cycle_summaries`'s daily check only looked for explicit `CRASH` rows, which a hard-killed process (OOM, the timeout backstop itself) never gets to write — a gap-detection check is added alongside it; Kelly sizing's 30-sample threshold didn't specify per-strategy vs. pooled statistics, a real correctness gap given GVOF and Wyckoff have different payoff shapes, now explicit; the daily drawdown check's scope (account-wide vs. per-symbol/strategy) was ambiguous against the Extended-tier `virtual_portfolios` design, now stated explicitly as account-wide for this build; Layer B's neutral-reading default and its failed-fetch fallback were indistinguishable at the scoring layer — now logged separately by reusing the existing `cycle_summaries.errors` field, no new schema; "first strategy match wins" was a silent, unexamined design choice with a real (if rare) cost to Phase 5's per-strategy sample integrity — now a named, evidence-gated trade-off instead of an accident; annual holiday-calendar refresh and token-refresh scheduling got cheap, concrete operational reminders; Phase 5 gained an explicit caveat that the two strategies won't necessarily reach 50 trades on the same timeline.
13. **Sixth pass — a genuinely critical, previously-uncaught bug, plus a second independent audit.** `macro_regime_flags` was filed under Extended tier ("build only when the feature that needs it is built"), but the cross-symbol correlation step that writes to it (§2.3 step 8) is not optional or deferred — it runs unconditionally every single cycle. Left as Extended, the very first cycle where both symbols PROCEED in the same direction would have crashed on an INSERT into a table that doesn't exist yet. Moved to Core tier; **Core tier is now 7 tables, not 6**, corrected everywhere the count is cited (§1, §3.4, D-011, §5.2, §6.4's implicit references, Appendix A, Appendix K, Phase 1's gate). While fixing this, a second real bug surfaced: Appendix K's migration component still said `system_paused` seeds `is_paused = false`, a stale leftover from *before* the fail-closed-by-default fix landed two passes ago — corrected to match. A second independent audit pass (distinct from the first) added: a per-symbol 60-second wall-clock budget in the node chain, layered underneath the per-call timeout rather than duplicating it, so one cascading-slow symbol can't silently consume the whole job's budget and starve the other symbol entirely — including the specific interaction with cross-symbol correlation when one symbol produces no verdict at all; explicit STT/Kelly external-verification reminders (§2.4.1) — with the suggested GEX formula deliberately *not* asserted, since writing an unverified equation into a section marked "locked, verbatim" would itself violate this document's own confidence-grammar discipline, so it's flagged `S3-UNSCANNED` and pointed at the real source file instead; the kill-switch bullet now explicitly covers "zero rows returned" as equivalent to a read failure, not just exceptions; §0 gained a condensed pointer to Appendix A's infra tripwires (concurrency group, Procfile, inbound endpoint) rather than a duplicate block; and a mangled section heading in the Closing Note — the "## Closing Note" marker itself had been damaged in an earlier edit, leaving a dangling em-dash — was caught and fixed, with a scope-boundary note added in the same place closing off further proposals to bolt external agent-orchestration frameworks onto this document.
14. **Seventh pass — release-readiness audit, then a final tech-debt/deploy-checklist scan.** The release-readiness pass caught one real structural defect (the `## §7 — APPENDICES` top-level heading itself had gone missing in an earlier edit, silently breaking the document's own §0–§7 numbering while every appendix underneath it stayed correctly present and ordered — restored) and confirmed, exhaustively rather than by spot-check, that every cited `D-XXX` and `D-TXX` resolves to a real entry, every §5.4 build step is present and sequential, no orphaned env vars exist, and every node name matches exactly between §2.3 and Appendix G. The follow-up tech-debt/deploy-checklist pass closed three gaps that had never been addressed anywhere in the document: **Row-Level Security was never mentioned** despite the dashboard shipping `SUPABASE_ANON_KEY` in public client-side JS — RLS enablement is now an explicit step at the moment tables are created (§5.2) and re-verified before deploy (§6.1), with the specific policy stated (`anon` gets read-only `signals`, nothing else); **no CI ran tests on push**, meaning a broken change's first real test was a live scheduled cycle failing — a minimal `tests.yml` workflow, separate from the trading cron, now runs `pytest` on every push/PR to `main` (§5.1, §5.4 Step 15a); and `transaction_cost()`'s `brokerage`/`exchange_charges` defaults never stated whether they're per-leg or round-trip, a unit ambiguity that would quietly bias every EV number (and everything Kelly sizing derives from it) if it's ever implemented wrong — flagged `S3-UNSCANNED` in §2.4.1 alongside the GEX formula, for the same reason: an unverified assumption stated confidently is worse than an honest gap.
15. **Eighth pass — a deeper formula-consistency check, not another structural sweep.** By this pass, structural issues (missing headings, orphaned references, mismatched counts) had been exhausted across seven prior passes — so this one deliberately looked *between* formulas instead of *within* them: `expected_value()` explicitly nets out `est_transaction_cost` before gating PROCEED/BLOCK; `kelly_fraction()` takes no cost parameter at all and sizes purely off gross win/loss. A trade can clear the EV gate on its net edge while being sized as if the gross edge were real — systematically inflating position size relative to a cost-consistent calculation, in the expensive direction, from trade one. Flagged in §2.4.1 as a decision that needs a human answer (deliberate half-Kelly headroom, or a missing cost-adjustment step), not a silent assumption either way. Also: the per-symbol 60-second timeout (added two passes ago) covers steps 0–7 but was silently scoped away from step 9 — stated explicitly now that this is deliberate, not an inconsistency, since step 9 already has its own graceful-degradation paths (D-T10, D-048) and a hard abort there would discard a validated signal rather than protect anything. The new `tests.yml` CI workflow's own minutes cost is now connected to Appendix H's existing budget math instead of sitting as an unconnected fact, and picked up its own Appendix K entry (component 19) for consistency with every other piece of infrastructure in this document.
16. **Ninth pass — agent-executability audit, three fixes applied as-is, two corrected before applying.** Applied directly: an inline `S3-UNSCANNED` comment now lives on `transaction_cost()` itself (and a matching one on `kelly_fraction()` pointing at D-T12), so the provenance flag travels with the code instead of sitting in prose an agent copying the block would never see; the step-8 exemption is now stated explicitly in the timeout SCOPE block instead of left to be inferred; `tests.yml` gained its own `concurrency` group with `cancel-in-progress: true` — deliberately the opposite of the trading cron's `false`, for the opposite reason (a stale CI run has zero value once a newer commit exists; a live trading cycle mid-dispatch is exactly the thing worth never interrupting), which is D-T9's reasoning applied a second time rather than contradicted. **Two suggested fixes were corrected, not copied.** First, Step Zero's own memory-pipeline check would `wc -l`-error and trigger a false "stop" for a from-scratch build — this build never creates those files at all, so their absence isn't something that needed "cleaning up," it's the expected state from day one. The actual fix: Step Zero and the agent-instruction block are now explicitly scoped to the inheriting-a-repo scenario (a from-scratch build already skips to §5 per the nav table, now stated at the point of the check itself, not just implied by a table elsewhere), and the memory-file check reports three real outcomes (absent = expected; present with matching counts = inherited repo or legitimate Appendix I promotion; present with different counts = actual red flag) instead of a binary pass/fail that couldn't distinguish a from-scratch build from a broken one. Second, rather than inject a fabricated "this is settled" comment into the locked Kelly formula — which would have been the exact same category of error as asserting an unverified GEX formula, just for a different function — the gross/net question got the document's own existing mechanism for "needs an actionable default, isn't actually resolved": a new decision tree, **D-T12**, with a stated default and reasoning, referenced from both §2.4.1 and an inline comment on the code itself. §0's agent instruction also now explicitly distinguishes a tracked, defaulted `S3-UNSCANNED` question (build against the default, keep going) from a genuine new discrepancy worth halting on — closing the deadlock risk at its actual source instead of papering over one instance of it.

Everything else — the math, the governance rules, the Delta Ledger's substance, the database schema, the operational edge-case rules — carries forward unchanged from v10.

---

## §2 — LAYER 1: IMMUTABLE SPEC

Nothing here is ever marked missing or broken. If Layer 2 (§3) finds the code doesn't match this layer, the code is wrong until a human deliberately edits this layer. **This applies directly to D-001:** the data-flow descriptions below (§2.3 steps 2 and 8, the `market_context` rows in §2.2) describe the system's correct end-state regardless of whether D-001 turns out to be confirmed. If it is, that's Layer 2's finding about the *code*, not a reason to water down what Layer 1 says the code should do — build toward this spec, don't edit this spec down to match what's currently broken.

### §2.0 — Engineering Principles for Free-Tier Reliability *(NEW in v11)*

Every individual decision in this document — the hardcoded strategy list, the fail-closed kill switch, the reuse of one Render service instead of standing up a second one, the deferred database tables — traces back to eight principles. Stating them once here means future decisions can be checked against them instead of re-litigated from scratch.

1. **Fail-closed for safety, fail-soft for enrichment.** Anything that stops a bad trade from being suggested (kill switch, stale-data check, drawdown gate) must default to blocking when uncertain. Anything that only makes the alert nicer to read (the Analyst LLM's narrative) must default to degrading gracefully — a plainer message, never a crashed cycle.
2. **Assume every external call will be retried.** Every write that a retry could duplicate (a Telegram send, a DB insert) is either idempotent or checked-then-written. This is why Telegram delivery is tracked with a boolean flag instead of assumed, and why inbound commands are dedup'd by update ID (§7 Appendix C).
3. **One fact, one source.** No fact is allowed to live in two places that can drift apart. This is the entire reason strategies are a Python list and not a database-plus-code pair — there is nothing for the two to disagree about.
4. **Observability minimalism.** One heartbeat table, one static dashboard. Free-tier infrastructure doesn't reward a real observability stack, and a system with one operator doesn't need one yet. Resist building monitoring for problems that haven't happened. **Stated trade-off against principle 5:** a single heartbeat row tells you *that* a cycle failed, not *which* of the seven stacked services caused it — diagnosing that is a manual log-check, not an automated one. That's accepted deliberately: reduced diagnostic granularity in exchange for zero observability infrastructure cost, appropriate for one operator who is also the one reading the logs. If a second operator or a paid tier ever enters the picture, this trade-off is exactly the kind of thing Appendix J should gate a richer observability stack behind — not something to quietly build "just in case" before then.
5. **Reliability budget stacks, it doesn't average.** Seven independent free services each at 99.5% individually available is meaningfully less reliable than any single number suggests. Design for the compounded number, not the best-case one.
6. **Schema and code move together.** No pull request references a table without a migration for it in the same PR. This one rule is the cheapest fix for the single most expensive class of bug this project has produced historically.
7. **Every external dependency gets a timeout, a retry-with-backoff, and a circuit breaker — no exceptions**, including ones that "probably won't fail," because the ones that "probably won't fail" are exactly the ones that eventually take the whole cycle down with them. **Concretely: every HTTP call to Dhan, NSE, Supabase, or an LLM provider carries an explicit timeout of 10 seconds or less, and retries are capped at 2 additional attempts with exponential backoff** — an *unbounded* retry loop defeats the point of having a timeout at all, and is exactly the kind of thing that quietly turns a 45-second cycle into one that eats the job-level `timeout-minutes` backstop (§5.4 Step 15) instead of failing fast and letting the next scheduled cycle try again 5 minutes later.
8. **Build for the user you have.** One operator, two strategies, no external contributors. Don't build multi-tenant security, a strategy-review pipeline, or a second LLM provider for problems that don't exist yet. Appendix J defines exactly when that stops being true.

### §2.1 — System Purpose & Non-Negotiable Constraints

AXIS is a pre-trade intelligence and risk-governance engine for NIFTY and BankNifty index options.

- **No order-placement code path exists or is ever permitted anywhere in the system.** AXIS produces a signal; a human places every trade by hand. This is architectural, not a feature flag.
- **AI explains; AI never decides.** The pure-Python risk math decides PROCEED/BLOCK directly — the math was always deterministic and never actually needed an LLM to "check" it (see Appendix I if you later want a second AI opinion gating the decision instead). The Analyst LLM is optional narrative flavor and never gates a trade.
- **The math downstream of the direction score is zero-AI-dependency.** Expected value, Kelly sizing, drawdown gates, R:R validation — pure Python, deterministic, unit-testable without any LLM being available, correct, or online.
- **The only real finish line:** a statistically honest answer to whether the system produces positive expected value after all real costs, at a sample size large enough to mean something (~50 closed trades per strategy, spanning at least 2 monthly expiry cycles).
- **Trading window:** 09:15–15:30 IST, Monday–Friday, market days only.
- **Two symbols, sequential, never parallel**, with Telegram dispatch deferred until both finish so the cross-symbol correlation check runs exactly once per cycle — see §2.3, step 8, where this is now shown explicitly.
- **Fail-closed is the default failure mode for every safety gate, without exception** (per §2.0 principle 1).
- **Reliability budget, stated plainly:** the free-tier stack spans seven independent services (GitHub, Render, Netlify — dashboard only in this build, Supabase, plus one LLM provider). Uptime compounds multiplicatively. This is the honest, structural reason "works reliably enough to validate the strategy" and "ready to risk real capital" are different bars.

### §2.2 — Complete Feature Inventory (every row now traceable, per v11 fix)

Every row cites either the ledger item that governs its state, or an explicit tag confirming there is nothing open against it. This closes the gap where v10 promised universal traceability but didn't deliver it.

| Feature | State / Ledger ID |
|---|---|
| Read-only Dhan v2 client (candles, chain, expiry, token lifecycle) | `S1-CITED` — verified present — *no open item* |
| NSE fallback fetcher, bidirectional with Dhan | `S1-CITED`; NSE-specific 403/HTML failure handling missing — **D-047** |
| Instrument resolver | `S1-CITED` — verified present — *no open item* |
| Circuit breaker (Dhan confirmed; others need the same pattern) | `S1-CITED` (Dhan) / **D-020** (NSE/LLM/Telegram) |
| **Live data → `market_context` orchestration** | **D-001 — single-sourced, unconfirmed, highest priority in the whole ledger** |
| **Stale-data abort** (reject option-chain data older than 15 min) | **D-045** |
| Layer A/B/C scoring, direction combiner, structure gate | `S1-CITED` — verified present, `layer_b.py` corroborated B+C — *no open item* |
| Direction dead-zone abort (2.0–4.0) | `S1-CITED` per Layer 1 math spec §2.4; this is the exact mechanism D-001 would trigger if confirmed |
| GVOF strategy | `S1-CITED` — verified present, registered — *no open item* |
| Wyckoff Mean-Reversion strategy (code) | `S1-CITED` — verified present; not registered — **D-012** |
| Strategy list (hardcoded, version-controlled, no DB registry) | `S1-CITED` — present by design, see §2.5 — *no open item* |
| Analyst LLM (Gemini) | `S1-CITED` — present — *no open item* |
| Analyst LLM graceful template degrade (no second provider by default) | `S1-CITED` per design — **D-T10** |
| Direct pure-Python PROCEED/BLOCK gating (no Verifier LLM) | `S1-CITED` per design — see §2.1 — *no open item* |
| JSON extraction, LLM cost guardrail | `S1-CITED`, present. **Race-condition note:** relies on single-threaded execution via the GH Actions concurrency group, not a distributed lock — see amended **D-T9** |
| Hardcoded knowledge block in Analyst system prompt (no RAG pipeline) | `S1-CITED` per design — see Appendix F — *no open item* |
| Daily drawdown check (OFF/SHADOW/ENFORCE) | `S1-CITED`, present — *no open item* |
| R:R / asymmetry validation (≥2.0x floor) | `S1-CITED`, present — *no open item* |
| BankNifty shadow-mode 6-criteria gate | `S1-CITED`, present. Whether ever evaluated live — `S3-UNSCANNED`, see **D-017** neighbor items in §4.3 P1–P3 table |
| Position sizing (flat 1% → half-Kelly capped 2%) | `S1-CITED`, present — *no open item* |
| `/ready` command (replaces PRS quiz UI) | `S1-CITED` per design — **D-004** (removal decision) + **D-055** (delivery channel) |
| `/record` command (manual trade-outcome recording) | `S1-CITED` per design — **D-046** (workflow) + **D-055** (delivery channel) |
| `/close` command (clears active-position state) | `S1-CITED` per design — **D-050** (state) + **D-055** (delivery channel) |
| `/resend` command (recovers a lost Telegram delivery) | `S1-CITED` per design — **D-048** (persistence) + **D-055** (delivery channel) |
| **Render-hosted inbound command endpoint** (single authenticated route) | **D-055 — new in v11**, closes a real gap: four commands with no inbound channel |
| **Active-position tracking** (prevents contradictory signals) | **D-050** |
| **Dedup time horizon** (suppress repeat identical signals) | **D-049** |
| **Cross-symbol correlation, orchestrator-level, single execution** | `S1-CITED` per design, restored to the visible pipeline in v11 — see §2.3 step 8 — *no open item* |
| **Telegram delivery persistence / retry** | **D-048** |
| 7-section Telegram alert, MarkdownV2 sanitizer, rate limiter | `S1-CITED`, present — *no open item* |
| Static dashboard | `S1-CITED`, present — *no open item* |
| Kill switch (`system_paused`) | `S1-CITED` present; fail-closed — **D-T8 / D-052** |
| Weekly friction report, EOD no-trade summary | `S1-CITED`, present — *no open item* |
| GitHub Actions `concurrency:` group | `S3-UNSCANNED` whether present — **D-051 / D-T9** |
| Break-glass manual fallback (`python main.py --all`) | `S1-CITED`, documented — **D-053** |
| LLM provider rate limits under real fan-out | `S3-UNSCANNED` — **D-054** |

*(Full-build-only features — DB-backed strategy registry, AST review pipeline, Verifier LLM, second LLM provider, RAG/memory pipeline, PRS quiz UI, distributed LLM locks, inbound Netlify webhook for ratings/PRS callbacks — are documented in full in **Appendix I**, each tagged with its original ledger ID where one exists.)*

### §2.3 — Canonical Node Chain *(corrected in v11 — cross-symbol step restored, lock node clarified, command channel added)*

```
FOR EACH symbol in [NIFTY, BANKNIFTY] — strictly sequential, one process, never parallel.
PER-SYMBOL WALL-CLOCK BUDGET: 60 seconds, wrapping the entire per-symbol graph
execution (steps 0-7). This is a different layer of defense from the per-call
timeout in §2.0 principle 7, not a duplicate of it: a 10-second timeout stops any
one HTTP call from hanging forever, but does nothing about several calls that each
individually respond just under 10 seconds while genuinely struggling — that
cascades into a symbol taking minutes without any single call ever "timing out."
If symbol 1 exceeds 60s, abort it, log SYMBOL_TIMEOUT to cycle_summaries.errors,
and proceed to symbol 2 — one slow symbol degrading gracefully beats one slow
symbol silently consuming the whole job's remaining budget and leaving the other
symbol unprocessed. (Implementation note: if the per-symbol graph invocation is a
native async coroutine, `asyncio.wait_for(..., timeout=60)` cancels it cleanly at
its next await point — this is safe here in a way it would NOT be if the call were
wrapped in `asyncio.to_thread`, where cancellation doesn't actually stop the
underlying thread. Don't copy this pattern onto a thread-wrapped call without
that distinction in mind.)
SCOPE, STATED DELIBERATELY: this budget wraps steps 0-7 only, NOT step 9
(dispatch). That's not an inconsistent oversight -- the two phases have opposite
correct failure behavior. Steps 0-7 are still *deciding* whether anything should
happen at all; if that's taking too long, the right move is to give up cleanly and
let symbol 2 get its turn -- there is nothing yet worth protecting. Step 9 is
different: by the time a symbol reaches it, there is already a validated PROCEED
signal on the table, and step 9 already has its own graceful-degradation paths for
exactly this situation (D-T10's templated fallback if the LLM is slow/down, D-048's
persist-and-retry if Telegram is slow/down) -- a hard abort there would DISCARD a
signal that a little more patience or a retry would have delivered. Applying the
same hard-timeout logic to both phases would be consistency for its own sake at
the cost of throwing away exactly the output this whole pipeline exists to produce.
Step 8 (cross-symbol correlation) is also outside this budget, for a simpler reason
than either of the above: it isn't a per-symbol step at all -- it runs once, at the
orchestrator level, purely in-memory against data both symbols already produced, with
zero network calls. There's nothing slow to bound.

  0. calendar_gate_node        -> market open? + kill switch read.
                                  FAIL-CLOSED on unreadable pause state (D-T8/D-052).

  1. lock_check_node           -> lightweight per-symbol advisory check.
                                  v11 CLARIFICATION: once the GH Actions concurrency group
                                  (D-051) is confirmed live, this step has nothing left to
                                  protect against during scheduled runs -- GitHub itself
                                  refuses to start a second workflow run. It is retained
                                  ONLY as a Postgres-backed backup for manual/local runs
                                  (`python main.py --all` from a laptop during a GH Actions
                                  outage, D-053) where no concurrency-group protection exists.
                                  Do not budget engineering time hardening this step further;
                                  it is deliberately a thin, disposable safety net.

  2. fetch_and_score_node       -> fetches live spot/chain/VIX/FII data (D-001's fix lives
                                  here, returns a typed ScoredMarketContext, not a dict),
                                  aborts if the DATA'S OWN payload timestamp (never the
                                  runner's clock) is > 15 min stale (D-045), runs Layer A/B/C,
                                  computes direction_score, hard-aborts on the 2.0-4.0 dead
                                  zone per Layer 1 math spec (§2.4)

  3. structure_gate_node         -> binary structure confirmation

  4. strategy_activation_node    -> hardcoded STRATEGIES = [GVOFStrategy(),
                                  WyckoffMeanReversionStrategy()]

  5. risk_math_node              -> pure Python: EV, Kelly (capped 2%), R:R >= 2.0x, daily
                                  drawdown mode. PROCEED/BLOCK decided here directly.

  6. position_state_check_node   -> reads active_position (a plain SELECT — no FOR UPDATE:
                                  this node only reads and never writes in the same operation,
                                  so there is no read-modify-write window to protect; the real
                                  write-side race is handled at the /record INSERT via the
                                  symbol PRIMARY KEY, see D-050); suppresses or flags a
                                  contradictory signal (D-050)

  7. dedup_node                   -> suppresses identical (symbol, direction, strategy)
                                  signals dispatched within the last 60 minutes (D-049)

  -- per-symbol graph ends here. The verdict and sizing are held in memory by the
     orchestrator. TELEGRAM DISPATCH DOES NOT HAPPEN YET.

END FOR EACH

  8. cross_symbol_correlation_step  -- ORCHESTRATOR LEVEL, inside main.py, NOT a graph
                                     node. v11 FIX: this step existed in principle (stated
                                     in §2.1's "dispatch deferred until both finish" rule)
                                     but had no visible place in the node chain. It now has
                                     one: runs EXACTLY ONCE per cycle, after both symbols'
                                     graphs have completed. If both PROCEED in the same
                                     direction, applies a 50% lot-size haircut to both
                                     before dispatch. Writes exactly one row to
                                     macro_regime_flags per cycle. Living at the orchestrator
                                     level and nowhere else means there is no per-symbol
                                     copy of this logic left to accidentally duplicate.
                                     If one symbol hit its 60s SYMBOL_TIMEOUT (above) and
                                     produced no verdict at all, there is nothing to
                                     correlate against -- skip the haircut for that cycle,
                                     log it to cycle_summaries.errors as
                                     {"symbol": "<the one that timed out>",
                                     "reason": "SYMBOL_TIMEOUT", "elapsed_s": 60}, and let
                                     the surviving symbol's own verdict dispatch normally,
                                     uncorrelated. A missing half of a correlation check is
                                     a reason to skip the check, never a reason to skip the
                                     symbol that actually succeeded.

  9. analyst_and_dispatch_node (per symbol, using correlation-adjusted sizing)
                                     -> Gemini narrates (optional; on failure, templated
                                     message, no second provider by default, D-T10); sends
                                     Telegram; on non-200, writes to `signals` with
                                     telegram_sent=false for retry (D-048)
END

--- outside the 5-minute cycle, always available, not part of the graph above ---

  10. inbound_command_endpoint    -- ONE authenticated POST route added to the Render
                                     FastAPI service that already exists for health checks
                                     (D-T4). Receives Telegram webhook updates. Routes:
                                     /ready  -> UPSERTs today's trader_session_state row
                                                with is_ready = true (fresh opt-in required
                                                every session_date -- see D-004)
                                     /record -> checks active_position for that symbol FIRST;
                                                if one is already OPEN, rejects with an error
                                                instead of inserting a second row (D-046)
                                     /close  -> clears active_position for a symbol (D-050)
                                     /resend -> re-sends the latest telegram_sent=false row (D-048)
                                     Auth: same pattern as the original webhook design --
                                     X-Telegram-Bot-Api-Secret-Token header, 401 on mismatch.
                                     Idempotency: Telegram may redeliver the same update; the
                                     endpoint checks the incoming update_id against
                                     telegram_updates_processed (Appendix C) before acting,
                                     so a retried delivery cannot double-record a trade or
                                     double-close a position. This is D-055.
```

Every node returns only the keys it changed; state is `Optional[...]` everywhere.

### §2.4 — Mathematical Execution Order & Formulas (verbatim, locked, unchanged since v9)

```
1.  Fetch spot + option chain
2.  Compute gamma per strike
3.  Compute GEX (abort if exactly 0.0 -- a data-quality failure, not a valid neutral reading)
4.  Read GEX sign
5.  Read PCR -- only now, never before GEX
6.  Compute VIX expected move
7.  Combine into Layer A score
8.  Abort if final direction_score is 2.0-4.0 inclusive (neutral dead zone)  <-- THE EXACT
    MECHANISM D-001 WOULD TRIGGER: a hardcoded default of direction_score=3 sits inside
    this dead zone, so if D-001 is confirmed, the pipeline aborts here, every cycle,
    and nothing below this line ever executes in production.
9.  Calculate Expected Value
10. Apply half-Kelly, capped at 2%, smaller of the two
11. Apply Governance
12. Dispatch
```

```python
def expected_value(win_prob, avg_gain, avg_loss, est_transaction_cost):
    return (win_prob * avg_gain) - ((1.0 - win_prob) * avg_loss) - est_transaction_cost

def kelly_fraction(win_prob, avg_gain, avg_loss):
    # D-T12 (§4.1): gross avg_gain/avg_loss is the DEFAULTED, not resolved, choice --
    # verify against real position_sizer.py before Phase 7. Build exactly as written
    # below; do not silently net out costs here without updating D-T12 first.
    p, q, b = win_prob, 1.0 - win_prob, avg_gain / avg_loss
    return p - q / b

def transaction_cost(sell_premium_value, brokerage=40.0, exchange_charges=35.0, gst_rate=0.18):
    # S3-UNSCANNED (§2.4.1 item 4): brokerage/exchange_charges defaults are UNVERIFIED
    # as per-leg vs round-trip. If verification against pricing.py finds they're
    # per-leg, these numbers understate cost and every EV figure downstream is
    # overstated. Do not treat these defaults as confirmed just because they're here.
    # STT = 0.15% on sell premium (Union Budget 2026), flat, both sale and exercise
    stt = 0.0015 * sell_premium_value
    # ... plus brokerage, exchange charges, SEBI charges, GST on (brokerage+exchange), stamp duty

# Layer A -- GEX read before PCR, always
direction = -1.0 if gex < 0 else 0.35 if gex > 0 else 0.0
if gex < 0 and pcr_rising: direction = -1.0
elif gex > 0 and pcr_rising: direction = min(1.0, direction + 0.25)
if vix_structure in {"weak-low", "near-weak-low"} and vix_choch:
    direction = min(direction, -0.8)

# Layer B -- FII participant ratio
raw = ((futures - 1.0) + (calls - 1.0) - (puts - 1.0)) / 3.0
direction = max(-0.5, min(0.5, raw))

# Direction combiner
c_weight = config.layer_c_weight if layer_c.at_vp_boundary else config.off_boundary_c_weight
combined = (A * wA + B * wB + C * wC) / (wA + wB + wC)
final = max(1, min(5, round(3 + 2 * combined)))

LOT_SIZES = {"NIFTY": 65, "BANKNIFTY": 30}
STT = 0.0015  # flat, both sale and exercise, Union Budget 2026
```

### §2.4.1 — Formula Provenance & External Verification

"Locked in this document" and "verified against reality" are not the same claim — this section exists so the gap between them doesn't quietly widen over time.

1. **STT rate (0.0015):** attributed to Union Budget 2026 (0.15% on sell premium of index options). Tax rates change; before deploying with real capital, confirm this is still current against the latest CBIC/SEBI circular, not against this document's memory of it. If it changes, update `transaction_cost()` and this line in the same PR — never let the code and the spec drift on a number this directly tied to real money.
2. **Kelly formula:** `f* = p - q/b` is the standard fractional-Kelly form for binary-outcome sizing, which is how this document models an options trade (win/loss, not a continuous payoff distribution). This is textbook, not something this document invented — don't "improve" it to a continuous-time variant without a deliberate, recorded spec change, since whatever informed the strategies' win-rate assumptions was implicitly built against this discrete form.
3. **GEX formula — deliberately left unstated here, not an oversight.** §2.4's execution order says "compute gamma per strike, compute GEX" without writing out the actual equation, and that gap should be closed by **extracting the real formula from `src/scoring/layer_a.py` and pasting it here once verified** — not by a document author guessing one from a textbook and asserting it as "locked." Net GEX calculations vary in ways that matter (whether the exposure term uses spot price squared or strike price squared, the sign convention assumed for dealer positioning on calls vs. puts, whether it's scaled to a dollar/rupee exposure or left as a raw gamma figure) — getting any of these wrong changes the actual number this entire pipeline's first decision point depends on. Treat the missing equation here as `S3-UNSCANNED`, exactly like any other unverified claim in this document (§1.1), and close it the same way: read the real code, paste the real formula, tag it `S1-CONFIRMED`. An asserted-but-unverified formula in a section marked "locked, verbatim" would be worse than an honest gap.
4. **`transaction_cost()`'s `brokerage=40.0, exchange_charges=35.0` — per leg, or round-trip?** The defaults read as flat rupee figures with no unit stated. If a strategy's EV calculation applies these once per closed trade (round-trip) but the real cost is actually incurred on both the entry and exit leg separately, every single EV number Phase 5 reports is quietly overstated — and this compounds, since position sizing (Kelly) is itself derived from those same EV figures. This is exactly the kind of unit ambiguity that survives code review because the number "looks reasonable" either way. Verify against the actual `pricing.py` implementation and state the answer here explicitly once confirmed; until then, treat it as `S3-UNSCANNED` alongside the GEX formula above, not as a detail too small to matter.
5. **`kelly_fraction()` and `expected_value()` are inconsistent with each other, and that inconsistency has real teeth.** `expected_value(win_prob, avg_gain, avg_loss, est_transaction_cost)` explicitly nets out costs before deciding PROCEED/BLOCK. `kelly_fraction(win_prob, avg_gain, avg_loss)` takes no cost parameter at all — it sizes the position purely off gross win/loss figures. That means a trade can clear the EV gate on its *net* edge while being sized as if the *gross* edge were the real one, which systematically inflates position size relative to what a cost-consistent Kelly calculation would produce — the exact opposite direction of error from "too conservative," and directly proportional to real capital at risk once this reaches Phase 7. **D-T12 (§4.1) gives this a stated, actionable default — gross, unmodified, for reasons laid out there — so building isn't blocked on it.** But a default is not a verification: confirm which behavior the real `position_sizer.py` actually needs against the real numbers before Phase 7, and update D-T12's status when you do.

### §2.5 — Governance & Security Locks (non-negotiable)

- **Kill switch fails CLOSED, not open.** If `system_paused` cannot be read — an exception, a timeout, *or* a successful query that simply returns zero rows — the system behaves as though it is paused and does not run the cycle. "No row found" is not a special case to handle differently from a read exception; both mean the same thing here (we cannot confirm we're cleared to run), so both get the same answer. Every other uncertain condition in this architecture (stale data, degraded data quality) already fails closed; the gate whose entire job is "stop the system" is the last place that principle should be relaxed (D-T8/D-052).
- **Strategies are a hardcoded, version-controlled Python list.** Governance is the pull-request review a solo developer already does on every commit. This is a deliberate scope decision (§2.0 principle 8, principle 3), not an oversight — if AXIS ever accepts strategies from anyone other than its own maintainer, a real review pipeline (Appendix I) must be reinstated before that happens, per Appendix J's promotion criteria.
- Daily drawdown and related gates support OFF/SHADOW/ENFORCE; default SHADOW until explicitly promoted by a human.
- Circuit breakers on every external dependency trip after repeated failures and cool down before retry.
- **The inbound command endpoint (D-055)** rejects unauthenticated requests immediately: a missing or mismatched secret-token header returns `401` before any database logic runs, full stop. For a request that passes auth, it returns `200` only after either successfully executing the command or safely no-oping on an already-seen `update_id` — there is no ambiguity between these two response codes because they gate two different questions (is this caller allowed to talk to us at all vs. did we just handle what it asked). See §2.3, step 10, and Appendix C.

### §2.6 — Data Contract (intended)

`AxisState` is the single typed contract every node reads and writes: every field `Optional`, no undeclared field accepted (`extra="forbid"`), each node returns only the keys it changed. Declare the full field set up front, before any node writes to an undeclared key — this pre-empts the historical contract-drift bug (D-013) by construction rather than catching it after the fact.

**Where `extra="forbid"` applies, and where it deliberately doesn't:** `AxisState` and D-001's `ScoredMarketContext` are both **internally-defined output contracts** — every field on them is something *this codebase* computed or decided to carry, so `extra="forbid"` is correct and load-bearing on both: if a node or `market_snapshot.py` tries to hand back a key nobody declared, that's always a bug worth crashing loudly on, never something to silently accept. This is different from **raw external payload parsing** inside `dhan_client.py` and `nse_fetcher.py` — the JSON Dhan or NSE actually sends is not this codebase's contract to define, so that parsing layer should extract only the specific fields it needs (via targeted key access, or a deliberately lenient/optional-fields model) rather than validating the *entire* external response strictly. An extra field NSE adds to their payload tomorrow should never crash a cycle; a missing or misnamed field in `ScoredMarketContext` — the thing *this codebase* constructs from that parsed data — always should. Getting these backwards in either direction reproduces a version of D-001 or D-013 in a new file.

### §2.7 — Operational Edge-Case Rules (part of the immutable spec, not the ledger)

These five rules describe ways the system can behave incorrectly *while looking like it's working* — the most dangerous failure class in this document. Layer 2 audits check for them; their absence is a real bug, not a nice-to-have.

1. **Stale-data abort.** If the fetched option-chain/spot timestamp is more than 15 minutes older than the cycle's current time, the cycle must abort at data-fetch, before scoring. (D-045)
2. **Manual trade-recording workflow.** The system must expose a literal, simple way for a human to say "I took this signal, here's my entry" and later "here's my exit" — the `/record` command (D-046), delivered via the inbound endpoint (D-055). It must refuse a second `/record` for a symbol that already has an `OPEN` position — `/close` first — so a typo or a correction never silently creates a duplicate open trade that poisons the Phase 5 win-rate and EV numbers.
3. **NSE-specific failure differentiation.** A 403 response or an HTML error page from NSE's public endpoints must be classified as a distinct failure mode (`NSE_BLOCKED`), separate from a generic empty-data condition, so the circuit breaker and Dhan-fallback logic behave correctly. (D-047)
4. **Telegram delivery persistence.** A signal that clears every gate but fails to actually reach Telegram must not vanish. It's written with `telegram_sent = false`, and `/resend` (D-048, delivered via D-055) recovers it. A signal is "delivered" only when the Telegram API confirms receipt.
5. **Dedup time horizon.** An identical signal (same symbol, direction, strategy) must not re-dispatch more than once per 60 minutes by default. A new alert fires only on direction flip, strategy change, or horizon expiry. (D-049)

A sixth rule, stated here for completeness: **active-position tracking.** One row per symbol (`active_position`: entry time, strike, type) so a second cycle running 5 minutes later doesn't generate a contradictory alert while the human is still holding the first position. Cleared via `/close` (D-050, delivered via D-055), or automatically at end of day by one extra step added to the existing `no_trade_summary` cron (§5.1) — reusing a cron that's already scheduled rather than standing up a new one (§2.0 principle 4).

---

## §3 — LAYER 2: LIVE DELTA (AUDIT MAP)

Every artifact required by Layer 1, mapped against what the three source audits actually found. This layer states facts and their confidence; §4 prescribes fixes. Full-build-only artifacts (registry, review workflow, memory pipeline, PRS quiz, Verifier, second LLM provider) are catalogued in **Appendix I** rather than duplicated here.

### §3.1 — Scoring Layer

| Artifact | State | Evidence |
|---|---|---|
| `src/scoring/layer_a.py` | `S1-CITED` | 165 lines, all three sources agree |
| `src/scoring/layer_b.py` | `S1-CITED` — corroborated B+C | 30 lines / 1004 bytes, matches exactly across two independent-enough reads. Confirm with the Step Zero command first. |
| `src/scoring/layer_c.py` | `S1-CITED` | 109 lines, all sources agree |
| `src/scoring/direction_scorer.py` | `S1-CITED` | 99 lines, imports Layer B at line 11 per Source C |
| `src/scoring/structure_gate.py` | `S1-CITED` | 54 lines |
| **Who populates `market_context.layer_a/b/c/scoring_config` before the graph runs?** | `S1-CITED`, SINGLE-SOURCE (Source C only) — treat as an open question, not a settled negative | Source C traced `direction_scorer_node` and `main.py`'s `_base_market_context()` and reports no call site anywhere that injects live data before `graph.ainvoke()`. Neither A nor B corroborates the absence. **This is D-001.** |

### §3.2 — Strategy Layer

| Artifact | State | Evidence |
|---|---|---|
| `src/strategies/gvof.py` | `S1-CITED` | 231 lines, registered |
| `src/strategies/wyckoff_mean_reversion.py` | `S1-CITED` | 158 lines, fully coded per B and C |
| **Is Wyckoff reachable at runtime?** | `S1-CITED` — NO | `STRATEGIES = [GVOFStrategy()]`; Wyckoff never added; DB row said `active` anyway under the old registry design. **In this build, that class of bug is structurally impossible** — the strategy list *is* the code (D-012). |
| 3 of 4 planned Wyckoff variants | `S3-UNSCANNED` | Not built; deferred item regardless of architecture |

### §3.3 — Orchestration & Entrypoint

| Artifact | State | Evidence |
|---|---|---|
| `src/graph/graph.py` | `S1-CITED` | 58 lines; `graph = build_graph()` compiles at import time — any node import error cascades to "the whole module fails to import" |
| `src/graph/state.py` | `S1-CITED`, contract mismatch found | `main.py` writes undeclared fields, silently stripped, not erroring; `is_backtest` declared but never set (D-013) |
| Production trigger | `S1-CITED` — resolved | `main_pipeline.yml` cron running `python main.py --all`, corroborated by B and C |
| `Procfile` | `S1-CITED` — confirmed broken | Targets `src.main:app`, which doesn't exist (D-010) |
| `server.py` | `S1-CITED` | Has a real `app = FastAPI()` object, but also spawns the wrong subprocess at import time (D-016). **This same object is where D-055's inbound command route gets added.** |
| `_log` undefined in `nodes.py` | `S1-CITED` — confirmed | Guaranteed `NameError` on the OHLC-persistence failure branch (D-005) |
| `src/data/ohlc_writer.py` | `S1-CITED` — confirmed missing, caught by a broad `except` | Silent, non-crashing, total feature loss (D-007) |
| Crash alerting (`_run_cli()`) | `S1-CITED` — confirmed dead code | Written but never invoked; a production crash currently notifies nobody (D-009) |
| Cross-symbol correlation | `S1-CITED` — historically confirmed triple-executed under the old design | Fixed by construction in this build — see §2.3 step 8. There is exactly one implementation, at the orchestrator level, and nowhere else. |
| **GH Actions `concurrency:` group present?** | `S3-UNSCANNED` | Not checked by any prior audit; see D-051. If present, the per-symbol lock (§2.3 step 1) has nothing left to protect against during scheduled runs. |

### §3.4 — Database Schema

See §4.3 for the Core/Extended tiering, and Appendix C for the SQL.

| Table group | State |
|---|---|
| `backtest_signals`, `backtest_trades`, `api_circuit_breakers`, `daily_risk_limits`, `trade_tags` | `S1-CITED`, migrations found |
| 13 tables referenced by code with no located migration | `S2-DERIVED`, no migration found by any source. Re-tiered in this build: 5 of the 13 (`signals`, `active_position`, `system_paused`, `cycle_summaries`, `macro_regime_flags`) are Core — build immediately; the other 8 are Extended, deferred — see §4.3, Appendix C |
| `telegram_updates_processed`, `trader_session_state` — new tables, not part of the original 13 | **N-A** — these exist to support v11-only features (D-055's inbound endpoint, D-004's `/ready` toggle) that didn't exist when the original audit ran. Also Core tier. **Core tier overall is 7 tables, not 3** — see §1's corrected Counts line |

### §3.5 — Delivery & Deployment Config

| Artifact | State |
|---|---|
| `telegram_formatter.py`, `alert_builder.py` | `S1-CITED`, sanitizer confirmed sole send path |
| GitHub Actions workflow inventory | `S1-CITED`, 7 files confirmed |
| Inbound command endpoint (D-055) | **N-A** — does not exist yet; this document specifies it for the first time in v11 |

### §3.6 — Repository Hygiene

Empty directories, zero-byte test placeholders, stray root-level test files, `cognee` dependency confirmed present but unused (D-T5, remove regardless — see Appendix I for the memory-pipeline context this ghost dependency came from). All low-priority, deferred.

---

## §4 — LAYER 3: EXECUTION ENGINE (THE RUNBOOK)

### §4.1 — Decision Trees (every one carries a stated default)

**D-T1 — Production entrypoint.** Default: `main_pipeline.yml` is the real entrypoint; Render's `server.py`/`Procfile` is a separate, unrelated health-check-plus-command-endpoint service. **Status: DEFAULTED, not resolved** — run `gh run list --workflow=main_pipeline.yml --limit 1` before treating this as settled. **Alternative considered and rejected:** replacing the GitHub Actions cron with an external HTTP scheduler (e.g., cron-job.org) hitting a Render-hosted trigger endpoint, to avoid GitHub's occasional scheduled-workflow delay under load. Rejected because it trades a well-understood, already-hardened mechanism for an eighth stacked free-tier dependency (directly against §2.0 principle 5) with its own real failure modes (Render's request timeout vs. cycle duration, thread/async lifecycle interaction, an always-on service's own uptime-hour budget) — more moving parts to solve a timing precision problem that doesn't matter for a system where a human manually places every trade anyway. If GitHub's scheduled-run delay is ever *measured* (not assumed) to be routinely materially disruptive, revisit this via Appendix J's evidence-gated promotion process, not by default.

**D-T2 — Wyckoff reachability.** Default: register `WyckoffMeanReversionStrategy()` in the hardcoded `STRATEGIES` list from day one (§5.4 build order already specifies this). No database row to reconcile — see §2.5.

**D-T3 — NIFTY live vs. shadow mode.** No default substitutes for a live value. Check your own config. Until checked, assume SHADOW-only.

**D-T4 — Was Render ever meant to host the trading loop?** Default: No. Point the Procfile at `server:app` (a real health-check-plus-command endpoint); remove the subprocess spawn from `server.py`'s import-time side effect.

**D-T5 — Cognee: finish or remove?** Default: **remove.** No design rationale exists for it in any audit; the hardcoded knowledge block already covers what it would have done. Remove the dependency and any unused env vars. (§2.0 principle 8 — don't carry infrastructure for a problem nothing in this build has.)

**D-T6 — Knowledge base content.** Default: distill the authoritative source files (Appendix F) once, by hand or a one-time LLM summarization pass, into a static ~2,000-word rules block hardcoded into the Analyst's system prompt. Zero ingestion pipeline, zero embedding cost, zero glob bugs to have. **Hard cap: 2,500 words.** If a future edit would push it past that, delete the oldest or least load-bearing rules before appending new ones — never let it grow unbounded. An oversized prompt doesn't error, it just gets silently truncated somewhere upstream, and a truncated rules block produces a confidently-written narrative based on half the rules with nothing to flag that it happened — exactly the "looks like it's working" failure class §2.7 warns about, just in the prompt instead of the pipeline.

**D-T7 — Scope decision (why this document has one build track).** Default decision, carried forward from v10: build the simplified core described in §2–§6 first. Defer the expanded architecture (Appendix I) until this core has proven a positive-EV signal **and** the added complexity has a concrete justification — see the per-component criteria in **Appendix J**, not an all-or-nothing switch.

**D-T8 — Kill switch fail mode.** Default: **fail CLOSED.** If `system_paused` cannot be read, treat the system as paused and do not run the cycle. Consistent with every other gate in the pipeline (§2.5, §2.0 principle 1).

**D-T9 — Concurrency group vs. Postgres locks *(amended in v11)*.** Default: confirm (or add) `concurrency: group: axis-trading-cycle, cancel-in-progress: false` in `main_pipeline.yml`. This is a two-line YAML change and a *stronger* guarantee than any Postgres-level lock — GitHub refuses to start the second run rather than letting it start and then wait or fail.
**v11 amendment:** this decision's scope is broader than v10 stated. It doesn't just make LLM-specific distributed locks redundant (there are none in this build's default architecture) — it also makes the per-symbol `lock_check_node` (§2.3, step 1) redundant *for scheduled runs specifically*. That node is retained only as a backstop for the manual break-glass path (D-053), where no concurrency group protects the run. Don't invest further engineering effort hardening it beyond that.

**Precise semantics, verified against GitHub's own documentation because this is easy to get backwards:** a concurrency group allows **at most one run "in progress" and one run "pending" at any time, ever, full stop** — this is true regardless of `cancel-in-progress`. What `cancel-in-progress` actually controls is narrower than it sounds: `false` means an *in-progress* run is never interrupted; a *newer* trigger instead takes the single pending slot, and if a trigger was already sitting in that pending slot when the newer one arrives, the older pending one is dropped (not run, not merged — cancelled) in favor of the newest. Two consequences worth being explicit about: (1) two cycles can never execute simultaneously under this config, so there is no scenario where this causes a double-write to `macro_regime_flags` or anything else — the worst case is a missed cycle, never a corrupted one; (2) if cycles start running long enough to routinely queue behind themselves, some 5-minute triggers get silently dropped rather than piling up — watch `cycle_summaries.duration_ms` for that pattern and investigate the slow cycle, don't route around it. **`cancel-in-progress: false` is correct and stays as specified** — switching it to `true` would not prevent anything (there was never any overlap to prevent), it would only add a new risk: killing a run that's already mid-way through, potentially after risk math cleared PROCEED but before the Telegram dispatch confirmed. A queued cycle running a few minutes late is a strictly safer failure than a truncated one.

**Test-flakiness note:** `lock_check_node`'s implementation is intentionally minimal, by design (see the redundancy point above). If it introduces any flakiness during the Step 12 graph-import test, remove it entirely for scheduled runs once D-051 is confirmed — it was never carrying real weight there to begin with.

**D-T10 — Second LLM provider vs. graceful degrade.** Default: **no second provider.** If Gemini fails, the alert sends with a short templated message instead of an AI-written one — the Analyst only ever explains, never decides, so a thinner message costs polish, not safety (§2.0 principles 1 and 8). Appendix I documents the second-provider option and Appendix J states when it's worth adding.

**D-T11 — Promoting a component from this build to the expanded architecture *(NEW in v11)*.** No single "graduate to the full system" moment exists; each Appendix I component has its own trigger. Default: evaluate per-component, not all-at-once, using the criteria table in **Appendix J**, gated by the same Phase 5 statistical evidence (~50 closed trades per strategy) that gates any capital decision. See §4.4's extended Phase 6 gate.

**D-T12 — Kelly sizing inputs: gross or net of transaction costs? *(NEW)*.** §2.4.1 item 5 flags a real inconsistency: `expected_value()` nets out costs before gating PROCEED/BLOCK, `kelly_fraction()` doesn't net anything — it sizes off gross `avg_gain`/`avg_loss`. This needs an actionable default, not just an open question, so building doesn't stall on it. **Default: build `kelly_fraction()` exactly as shown in §2.4 — gross inputs, unmodified.** Reasoning, stated so it's a real default and not a shrug: (1) `KELLY_MIN_SAMPLE = 30` means every strategy runs on flat 1% sizing — untouched by this question at all — for its first 30 closed trades, which is a meaningful fraction of the Phase 5 sample; (2) half-Kelly's own 50% haircut is a large safety margin relative to the modest per-trade cost figures in `transaction_cost()`'s defaults, likely (not certainly — see item 4's own open question) absorbing the gross/net gap without the position size becoming actually dangerous. **Status: DEFAULTED, not resolved.** This is exactly the kind of question §0's agent instruction now says to build against the stated default for, not halt on — but it must be verified against the real `position_sizer.py` (or decided deliberately if building fresh) before Phase 7's real-capital decision, since "likely absorbs the gap" is a judgment call standing in for a calculation nobody has actually run yet.

### §4.2 — What Remains Genuinely Undecidable Without Your Live Systems

D-T3 (NIFTY's live/shadow flag) and live table row counts (§3.4) cannot be resolved by reading code — they are facts about your running database and dashboards. Appendix A gives the exact commands.

### §4.3 — The Append-Only Delta Ledger

**Rule: rows are never deleted.** A closed item gets its state updated and a closure note; it stays in the table. IDs never get reused.

#### P0 — System cannot be trusted to run correctly until these close

---
**D-001 — Scoring pipeline may be structurally unwired**
- **State:** `S1-CITED`, single-source (Source C only) — not corroborated, treat as an open question · **Runtime:** `UNTESTED` · **Type:** `[V]→[B]` · **Blast radius, precisely stated:** because Layer 1's math spec (§2.4) hard-aborts on any `direction_score` in the 2.0–4.0 dead zone, and `_base_market_context()` reportedly hardcodes `direction_score=3`, this is not "the system occasionally makes a bad call" — it is "the pipeline aborts at node 2 every single cycle, and nodes 3 through the end never execute in production."
- **Exact remediation:** build `fetch_and_score_market_data(symbol: str) -> ScoredMarketContext` in `src/data/market_snapshot.py`. It must: (1) fetch spot + option chain from Dhan (NSE fallback), (2) fetch VIX data, (3) fetch FII participant data via `nse_fetcher.fetch_participant_oi()`, (4) apply the stale-data check from D-045 before proceeding, (5) call `score_layer_a/b/c()`, (6) return a **typed Pydantic model** (`ScoredMarketContext`, `extra="forbid"` — same discipline as `AxisState`, §2.6), not a raw `dict`. **Call site:** inside `main.py`'s `_base_market_context()` (or immediately before `graph.ainvoke(state)`), merged into `market_context` before `fetch_and_score_node` reads it.
- **Why a typed model instead of a dict:** a `dict` return silently tolerates a missing or misnamed key — `layer_a` typo'd as `layer_A` gets swallowed by `.get("layer_a", default)` calls downstream and reproduces this exact bug in a new shape. A Pydantic model with `extra="forbid"` and no default values on the required fields raises immediately if Dhan returns a malformed payload (e.g. `pcr` missing), which the calling node catches and treats as a fail-closed data-quality abort — the same failure class as D-045's stale-data abort, just for shape instead of age.
- **Clock-sync rule, stated explicitly because it's easy to get wrong silently:** the 15-minute staleness comparison (D-045) MUST use the timestamp embedded in Dhan's own response payload as the data's age, never the GitHub Actions runner's system clock. The runner's clock is only ever compared against itself (e.g. "is it currently within the trading window" at `calendar_gate_node`) — it has no business judging the age of external market data, because runner clock drift and exchange-feed clock drift are two independent failure modes that this design should never let cancel each other out unnoticed.
- **Verification:** `grep -rn "score_layer_a\|score_layer_b\|score_layer_c" main.py src/graph/ src/data/` — no call site outside `src/scoring/` itself confirms the bug. Separately: `grep -n "class ScoredMarketContext" src/data/market_snapshot.py` confirms the typed contract exists; a unit test with a payload missing a required field should raise `ValidationError`, not silently produce a partial context.
- **Priority instruction:** per §0's branching agent logic, this item gates everything else.

---
**D-002 — `layer_b.py` — CLOSED, corroborated B+C.** Verify: `wc -l src/scoring/layer_b.py` (expect 30).

**D-003 — Memory pipeline existence — N/A for this build; see Appendix I.** `wc -l src/memory/ingest.py src/memory/recall.py` (expect 71, 35) if you're evaluating whether to add the full memory pipeline.

---
**D-004 — PRS quiz replaced entirely**
- **State:** `S1-CITED`, single-source (C) · **Runtime:** `N-A` (removed by design) · **Type:** `[D]`.
- **Remediation:** delete `prs_quiz.py` and `prs_cron.yml` if present; replace with a single Telegram command `/ready` that UPSERTs today's row in `trader_session_state` with `is_ready = true`, checked by `calendar_gate_node`, delivered via the inbound endpoint (**D-055**). The table has exactly one boolean column (`is_ready`, default `false`) — no second column to drift out of sync with it. **Because a fresh row is required for each `session_date` and defaults to `false`, this is also a free vacation switch**: if the operator is unavailable and never sends `/ready`, every cycle that day is blocked at the calendar gate — zero fetch calls, zero LLM spend, zero Telegram sends. No separate ignored-alert or budget-drain mechanism is needed; the daily opt-in already fails closed by design (§2.0 principle 1).

---
**D-005 — `_log` undefined in `nodes.py`**
- **State:** `S1-CITED` · **Runtime:** `TESTED-FAIL` (guaranteed `NameError`) · **Type:** `[F]`.
- **Remediation:** `import logging; _log = logging.getLogger("axis.nodes")` at the top of `nodes.py`.
- **Verification:** `grep -n "^import logging\|_log = logging" src/graph/nodes.py`.

---
**D-006 — Governance module — N/A for this build; see Appendix I** if you later add a strategy-review pipeline.

---
**D-007 — `src/data/ohlc_writer.py` missing**
- **State:** `S1-CITED`, corroborated · **Runtime:** `TESTED-FAIL` (non-crashing, caught by broad except) · **Type:** `[B]`.
- **Remediation:** build `persist_ohlc_candles(symbol, candles) -> None`, upserting into `cached_candles` (Extended tier, Appendix C) on conflict `(symbol, interval, candle_timestamp)` do nothing. Can be deferred until automated outcome sampling is actually built — the manual `/record` workflow (D-046) doesn't need it.
- **Verification:** `find . -iname ohlc_writer.py`.

---
**D-008 — Cross-symbol correlation must live in exactly one place**
- **State:** `S1-CITED` · **Runtime:** `UNTESTED live` · **Type:** `[F]+[T]` · **Blast radius:** corrupts position-sizing (haircut compounds incorrectly) and duplicates `macro_regime_flags` rows if implemented twice.
- **Remediation:** the correlation logic lives solely in `main.py`, post-symbol-loop (§2.3, step 8) — it needs both symbols' outcomes for the cycle, which a single-symbol graph invocation structurally shouldn't compute on its own. **If building from zero, there is no per-node copy to delete** — the fix is enforced by the architecture itself. **If inheriting the pre-existing repo instead, that guarantee does not apply automatically** — the old `verifier_node` implementation (historically around lines 266–307 of `src/graph/nodes.py`) carries its own copy of this logic and must be deleted before this build's orchestrator-level version can be trusted, or the two will double-execute and double-write `macro_regime_flags`.
- **Verification:** trace one full cycle in staging, force a same-direction result, count rows written to `macro_regime_flags` — expect exactly one. If inheriting the old repo, also `grep -n "macro_regime_flags" src/graph/nodes.py` first and confirm it returns nothing.

---
**D-009 — Pipeline crash alerting is dead code**
- **State:** `S1-CITED` · **Runtime:** `TESTED-FAIL` by inspection · **Type:** `[F]` · **Blast radius:** if the pipeline crashes, nobody is notified.
- **Remediation:** change `if __name__ == "__main__": asyncio.run(_amain())` to `_run_cli()`.
- **Verification:** `grep -n '__main__' main.py`.

---
**D-010 — `Procfile` targets a non-existent module/ASGI object**
- **State:** `S1-CITED`, corroborated · **Runtime:** `TESTED-FAIL` · **Type:** `[F]+[D]`.
- **Remediation:** per D-T4, `web: uvicorn server:app --host 0.0.0.0 --port 10000`.
- **Verification:** `cat Procfile`; deploy to staging, confirm `/health` returns 200.

---
**D-011 — Tables used by live code have no located migration**
- **State:** `S2-DERIVED` · **Runtime:** `N-A` · **Type:** `[V]+[B]` · **Blast radius:** total on a fresh deploy.
- **Remediation:** build the **Core tier** (7 tables: `signals`, `active_position`, `system_paused`, `telegram_updates_processed`, `trader_session_state`, `cycle_summaries`, `macro_regime_flags`) immediately. The middle three exist because a working system needs somewhere for inbound commands to dedupe against (D-055), a daily readiness flag (D-004), and a heartbeat (D-037) from day one; `macro_regime_flags` is Core for a different reason — it's written unconditionally every cycle by the cross-symbol correlation step (§2.3 step 8, D-008), which is not an optional feature to defer, it's part of the base node chain. None of these seven are safely deferrable the way the Extended tier is. Build the **Extended tier** (Appendix C) only as each specific feature that needs them is actually built.
- **Verification:** run the Check-3 SQL block in Appendix A.

---
**D-012 — `WyckoffMeanReversionStrategy` not registered**
- **State:** `S1-CITED`, single-source (C) · **Runtime:** `TESTED-FAIL` (unreachable) · **Type:** `[F]`.
- **Remediation:** add both `GVOFStrategy()` and `WyckoffMeanReversionStrategy()` to the hardcoded list from day one (§5.4 build order already specifies this). This class of bug cannot recur because there is no DB row to drift from the code.
- **Verification:** `grep -n "STRATEGIES" src/graph/nodes.py`.

---
**D-013 — `AxisState` contract violated by `main.py`**
- **State:** `S1-CITED`, single-source (C) · **Runtime:** `UNTESTED` · **Type:** `[F]+[V]`.
- **Remediation:** declare the full field set on `AxisState` up front (§2.6), before any node writes to an undeclared key. Set or remove `is_backtest` explicitly.
- **Verification:** trace one cycle, confirm every field survives state reconstruction unchanged.

---
**D-014 — Knowledge ingestion — N/A for this build; see Appendix I.**

---
**D-045 — Stale market data not rejected**
- **State:** `S1-CITED`, identified in review · **Runtime:** `UNTESTED` · **Type:** `[F]`, part of the immutable spec (§2.7) · **Blast radius:** medium-high — a pre-market cron run could silently score yesterday's close as if it were live.
- **Remediation:** in the D-001 fetch function, compare the option-chain/spot data's own **exchange-payload timestamp** (never the GitHub Actions runner's system clock — see D-001's clock-sync rule) against the current cycle time; abort with a distinct `STALE_DATA` reason if the gap exceeds 15 minutes.
- **Verification:** unit test with a mocked stale timestamp *in the payload*; confirm the cycle aborts before scoring regardless of what the test runner's own clock reads.

---
**D-046 — No manual trade-outcome recording workflow**
- **State:** `S1-CITED`, identified in review · **Runtime:** `N-A` (not yet built) · **Type:** `[B]`, part of the immutable spec (§2.7).
- **Remediation:** the `/record SYMBOL ENTRY_PRICE EXIT_PRICE REASON` command (or a two-step `/enter` + `/exit`), delivered via **D-055**, writes a row to `paper_trades` — **but only after checking `active_position` for that symbol first.** If a position is already `OPEN`, reject the command with a message like "NIFTY position already open — use /close first" instead of inserting a second row. Without this check, a correction (wrong strike, fat-fingered price) silently creates a duplicate open trade that `/close` can only ever close one of, and the other quietly poisons the Phase 5 win-rate and EV numbers. Required before Phase 4's "first 10 real trades" exit criterion can be met.
- **Verification:** run the command end-to-end in staging, confirm a row lands with the right fields; then run it again for the same symbol before closing, confirm it's rejected, not inserted.

---
**D-047 — NSE rate-limit/block responses not distinguished from empty data**
- **State:** `S1-CITED`, identified in review · **Runtime:** `UNTESTED` · **Type:** `[F]`.
- **Remediation:** in `nse_fetcher.py`, detect a 403 status or an HTML (non-JSON) response body and classify it as `NSE_BLOCKED`, distinct from `NSE_EMPTY`. Feed this into the circuit breaker so a block trips it and triggers Dhan fallback immediately.
- **Verification:** mock a 403/HTML response, confirm the correct failure mode is logged and the Dhan fallback fires.

---
**D-048 — Telegram dispatch failure can silently lose a signal**
- **State:** `S1-CITED`, identified in review, part of the immutable spec (§2.7) · **Runtime:** `UNTESTED` · **Type:** `[F]` · **Blast radius:** high — a cleared signal during a real market opportunity could simply vanish on a transient network blip.
- **Remediation:** `analyst_and_dispatch_node` writes the signal to `signals` with `telegram_sent = false` on any non-200 response or exception, before the cycle ends. The `/resend` command (delivered via **D-055**) or the next cycle's dispatch step recovers it.
- **Verification:** force a Telegram API failure in staging, confirm the row persists with `telegram_sent = false`, then confirm `/resend` delivers it.

---
**D-049 — Dedup suppression time horizon undefined**
- **State:** `S1-CITED`, identified in review, part of the immutable spec (§2.7) · **Runtime:** `UNTESTED` · **Type:** `[F]` · **Blast radius:** medium — left undefined, a stable trend spams an identical alert every 5 minutes.
- **Remediation:** `dedup_node` checks for a prior successfully-dispatched signal with the same `(symbol, direction, strategy)` within the last 60 minutes; suppresses if found. New alert fires on direction flip, strategy change, or horizon expiry.
- **Verification:** force two identical consecutive-cycle signals in staging, confirm only the first dispatches.

---
**D-050 — No active-position tracking; contradictory signals possible**
- **State:** `S1-CITED`, identified in review, part of the immutable spec (§2.7) · **Runtime:** `UNTESTED` · **Type:** `[B]` · **Blast radius:** medium-high — the system has no memory that a human is currently holding a position it recommended.
- **Remediation:** add `active_position` (Core-tier table, Appendix C) — one row per symbol. `position_state_check_node` reads it before dispatch; suppresses a same-direction entry alert, or flags an opposite-direction one as an exit/stop-loss warning. Cleared via `/close` (delivered via **D-055**), or automatically at end of day: one extra step in the existing `no_trade_summary` cron (already scheduled at 15:30 IST, §5.1) — `DELETE FROM active_position WHERE opened_at::date < current_date;` — no new workflow needed (§2.0 principle 4).
- **Race-condition note:** `active_position` is touched by two genuinely separate always-available processes — the GH Actions cycle (`position_state_check_node`) and the Render-hosted inbound endpoint (D-055's `/record`/`/close` handlers) — so D-051's concurrency group doesn't protect this table; that group only serializes GH Actions runs against each other, not against Render. The defense is already structural, not something to add: `symbol` is the table's `PRIMARY KEY`, so a second concurrent insert attempt for the same symbol fails on a primary-key violation regardless of application-level timing. D-046's handler should catch that specific violation and translate it into the same friendly "position already open" rejection it gives on the ordinary check — not let it surface as a raw 500 error.
- **Verification:** manually set an open position in staging, force a same-direction signal, confirm suppression; force an opposite-direction signal, confirm it's flagged as an exit warning. Separately, fire two `/record` requests for the same symbol back-to-back and confirm the second is rejected via the same message either way (whether caught by the pre-check or by the primary-key violation).

---
**D-051 — GitHub Actions `concurrency:` group not confirmed present**
- **State:** `S3-UNSCANNED` · **Runtime:** `UNTESTED` · **Type:** `[V]+[F]` · Resolves via D-T9.
- **Remediation:** add `concurrency: { group: axis-trading-cycle, cancel-in-progress: false }` to `main_pipeline.yml` at the workflow level.
- **Verification:** `grep -n "concurrency:" .github/workflows/main_pipeline.yml`; trigger two overlapping `workflow_dispatch` runs, confirm the second waits.

---
**D-052 — Kill switch fails open on unreadable pause state**
- **State:** `S1-CITED`, design review finding · **Runtime:** `UNTESTED` · **Type:** `[F]` · Resolves via D-T8 · **Blast radius:** high in the specific scenario it matters most (a DB outage during a period someone intended to pause trading).
- **Remediation:** in `calendar_gate_node`, if the `system_paused` read fails or times out, treat `calendar_open = False` (paused) rather than defaulting to "not paused."
- **Verification:** simulate a DB read failure for `system_paused` in staging, confirm the cycle exits at the calendar gate.

---
**D-053 — No documented break-glass fallback if GitHub Actions is unavailable**
- **State:** `S1-CITED`, ops-review finding · **Runtime:** `N-A` · **Type:** `[V]` (documentation only) · **Blast radius:** low-probability, but currently zero fallback exists.
- **Remediation:** document, in the README and §6.4, that `python main.py --all` can be run manually from any machine with the right `.env` populated during a GitHub Actions outage. **State the prerequisite explicitly, because it's easy to assume away:** the secrets GitHub Actions uses live in GitHub's encrypted secrets store, not in any `.env` file — a break-glass run requires manually exporting every variable in Appendix D into a local `.env` first, a real 10-minute task. Rehearse it once *before* an outage; a developer who discovers this mid-outage will hit auth errors, assume the whole system is broken, and lose an hour to a problem that isn't one. This is also the one scenario where the per-symbol lock (§2.3, step 1) still does real work — see amended D-T9.
- **Verification:** actually run it manually once from a local machine, confirm it completes a cycle correctly.

---
**D-054 — LLM provider concurrent rate limits unverified under real fan-out load**
- **State:** `S3-UNSCANNED` · **Runtime:** `UNTESTED` · **Type:** `[T]` · **Blast radius:** low today (single Analyst call, sequential symbols), relevant again if Appendix I's second provider is ever added.
- **Remediation:** once staging isolation exists (Phase 2), run a deliberate load test simulating the real two-symbol, one-LLM-call-per-symbol-per-cycle pattern.
- **Verification:** load test results logged; re-run if the provider mix changes.

---
**D-055 — Track S's specified commands have no inbound channel *(NEW in v11)***
- **State:** `S1-CITED`, structural review finding · **Runtime:** `N-A` (not yet built) · **Type:** `[B]` · **Blast radius:** medium-high — without this, `/ready`, `/record`, `/close`, and `/resend` are specified in §2.7 with literally nothing able to receive them, because the inbound webhook was scoped as full-build-only (Appendix I) and this build has no other always-on process.
- **Remediation:** add one route (e.g., `POST /telegram/webhook`) to the Render FastAPI service that already exists for health checks (D-T4) — do not stand up a separate Netlify Functions deployment just for four commands (§2.0 principle 4: one service, two routes, zero new infrastructure). The route: (1) validates `X-Telegram-Bot-Api-Secret-Token` against `TELEGRAM_WEBHOOK_SECRET`, returning 401 on mismatch; (2) checks the incoming Telegram `update_id` against `telegram_updates_processed` (Appendix C) and no-ops if already seen, so a redelivered webhook can't double-record a trade or double-close a position; (3) parses the command text and dispatches to the matching handler (`/ready`, `/record`, `/close`, `/resend`); (4) always returns 200 to Telegram once validated, per the fail-soft-for-delivery principle (§2.0.1), to avoid retry storms.
- **Verification:** register the webhook with Telegram's `setWebhook` pointed at the Render URL; send each of the four commands manually; confirm the correct DB row changes and that resending the same `update_id` (simulated) does not repeat the effect.

---

#### P1–P3 (unchanged in substance from v10, preserved in full)

| ID | Title | State | Type | Note |
|---|---|---|---|---|
| D-015 | Inbound webhook for ratings/PRS callbacks | S1-CITED | [B] | **Appendix I only** — not needed by this build's four-command endpoint (D-055 is a separate, minimal thing) |
| D-016 | `server.py` subprocess spawn lacks idempotency guard | S1-CITED | [F] | Moot once D-010 lands |
| D-017 | Slippage call-sites unaudited | S3-UNSCANNED | [V] | |
| D-018 | `test_pricing.py` weak assertions | S1-CITED | [F] | Fix with `pytest.approx()` from day one per §5.4 |
| D-019 | AST scanner untested bidirectionally | S1-CITED | [F] | **Appendix I only** |
| D-020 | NSE/LLM/Telegram breakers not confirmed Postgres-backed like Dhan's | S1-CITED (Dhan) / S3 (others) | [V]+[F] | |
| D-021 | Strategy registry base DDL missing | S2-DERIVED | [B] | **Appendix I only**; not needed here — see §2.5 |
| D-022 | Possible placeholder `.env` values | S3-UNSCANNED | [V] | |
| D-023 | Supabase PITR on/off | S3-UNSCANNED | [D] | Enable before Phase 3 |
| D-024 | UptimeRobot key rotation | S3-UNSCANNED | [D] | Rotate regardless |
| D-025 | KB backup sync status | S3-UNSCANNED | [D] | **Appendix I only** |
| D-026 | LLM model strings possibly deprecated | S3-UNSCANNED | [V] | Check monthly |
| D-027 | Data Quality Gate internals unconfirmed | S3-UNSCANNED | [V] | |
| D-028 | Env var reference cross-check | S1-CITED | [V] | Appendix D |
| D-029 | Dashboard base tables missing DDL | S2-DERIVED | [B] | Core-tier `signals` table covers the essentials |
| D-030 | Test coverage map incomplete | S1-CITED | [T] | Appendix E |
| D-031 | `no_trade_cron.yml` never scheduled | S1-CITED | [F] | |
| D-032 | Main pipeline cron not weekday-restricted | S1-CITED | [F] | Cheap fix |
| D-033 | GH Actions minute budget unchecked | S3-UNSCANNED | [V] | See Appendix H |
| D-034 | Idempotency under overlap untested | S3-UNSCANNED | [T] | Largely covered by D-051's concurrency group |
| D-035 | Render OOM risk | S3-UNSCANNED | [T] | Lower risk with Render confirmed health-check-plus-endpoint only |
| D-036 | Alert-flood dedup on retry | S3-UNSCANNED | [T] | Overlaps with D-049 |
| D-037 | Health check proves liveness, not correctness | S1-CITED | [B] | `cycle_summaries` — **promoted to Core tier** (§5.4 Step 13 writes one row per cycle from day one) |
| D-038 | Kill switch trigger mechanism undocumented | S3-UNSCANNED | [D] | Document and rehearse once; fail-closed per D-T8 |
| D-039 | `pnl_rupees` added via manual ALTER, no migration | S1-CITED | [F] | Formalize in Appendix C |
| D-040 | Duplicate 56KB KB file | S1-CITED | [F] | **Appendix I only** |
| D-041 | `auth_tokens` vs `broker_tokens` naming drift | S1-CITED | [V] | |
| D-042 | `custom_fields` purpose unclear | S3-UNSCANNED | [D] | Speculative; likely droppable |
| D-043 | `mv_strategy_leaderboard` workaround vs real view | S1-CITED | [D] | Low urgency |
| D-044 | Missing `__init__.py` in several dirs | S1-CITED | [V] | Likely harmless under 3.12 namespace packages |

#### P3 — Defer (batched, low blast radius)

Dead directories, stray root-level test files, zero-byte test placeholders, 3 of 4 Wyckoff variants, shared-write concurrency safety at current scale, NSE holiday calendar maintenance ownership, dependency version pinning, periodic SEBI posture re-check.

### §4.4 — Phase Gates (literal, queryable exit criteria)

**Phase 0 — Crash Fixes & The Big Question**
```sql
-- All must be true:
-- 1. D-001 confirmed OR refuted (Step Zero + Appendix A run, output pasted in Appendix B)
-- 2. D-004, D-005, D-007, D-009, D-010, D-055 verification commands all return expected output
-- 3. D-T4's decision acted on: Procfile fixed
python -c "from src.graph.graph import graph; print('GRAPH IMPORTS CLEANLY')"
```

**Phase 1 — Data & Governance Integrity**
```sql
-- Schema existence (fast, mechanical -- confirms migrations ran; says nothing about behavior):
SELECT count(*) FROM signals; SELECT count(*) FROM active_position;
SELECT count(*) FROM system_paused; SELECT count(*) FROM telegram_updates_processed;
SELECT count(*) FROM trader_session_state; SELECT count(*) FROM cycle_summaries;
SELECT count(*) FROM macro_regime_flags;
-- All seven must return without error (0 rows is fine -- existence is what's being checked).

-- Behavioral checks are NOT reducible to a single SQL query -- each one's real gate is the
-- functional test already specified in its own §4.3 entry. Run those, don't invent new SQL
-- for them:
--   D-045 (stale-data abort)    -> unit test, mocked stale timestamp. Note: an aborted
--                                  cycle never creates a signals row at all -- there is
--                                  nothing to SELECT for this one, by design.
--   D-048 (telegram persistence)-> force a send failure in staging, then:
SELECT count(*) FROM signals WHERE telegram_sent = false;
--                                  confirm the row exists, then confirm /resend clears it.
--   D-049 (dedup horizon)       -> force two identical consecutive signals, confirm the
--                                  second gets dedup_status = 'DUPLICATE_SUPPRESSED'.
--   D-050 (active_position)     -> manually insert a row, confirm position_state_check_node
--                                  suppresses a same-direction signal for that symbol.
--   D-051 (concurrency group)   -> not a database fact -- grep the workflow YAML (Appendix A),
--                                  then trigger two overlapping workflow_dispatch runs and
--                                  confirm the second queues rather than running concurrently.
--   D-052 (kill switch)         -> simulate a system_paused read failure, confirm the cycle
--                                  exits at calendar_gate_node instead of proceeding.
--   D-055 (inbound endpoint)    -> the curl-based integrity test in Appendix A.

D-008 resolved by construction: exactly 1 row in macro_regime_flags per forced same-direction test cycle
D-012 both strategies reachable: grep confirms both classes listed in STRATEGIES
D-013 resolved: state contract unchanged before/after a traced cycle
```

**Phase 2 — Staging Isolation & First Supervised Cycle**
```
One full cycle traced node-by-node; layer_a/b/c are non-null, AND layer_b's direction
    value is not exactly 0.0 (0.0 is layer_b's own default for "no FII data available" --
    non-null but still 0.0 would mean D-001's fetch function ran but its FII leg silently
    failed) -- this is the live proof D-001 is genuinely fixed, not just partially fixed
D-038 kill switch rehearsed: manually pause, trigger cycle, confirm zero rows in signals
    with alert_sent = true for that cycle
D-051 concurrency group tested: two overlapping workflow_dispatch triggers, second waits
D-055 webhook tested: all four commands round-tripped once each, and once more with a
    repeated update_id to confirm no double-effect
```

**Phase 3 — Shadow Mode & Data Collection**
```sql
-- cycle_summaries is Core tier (built in §5.4 Step 13, populated every cycle since Phase 0) --
-- nothing new to build here, only data to check.
SELECT count(*) FROM cycle_summaries WHERE status = 'CRASH' AND cycle_timestamp > now() - interval '10 days';
-- expect 0
SELECT count(*) FROM signals WHERE direction_score != 3 AND cycle_timestamp > now() - interval '10 days';
-- expect > 0  (proves D-001 is fixed in the field, not just in code review)
SELECT count(DISTINCT date_trunc('day', cycle_timestamp)) FROM cycle_summaries
  WHERE cycle_timestamp > now() - interval '14 days';
-- expect >= 10 (ten real trading-day sessions completed)
```

**Phase 4 — Live Execution & Behavioral Validation**
```sql
SELECT count(*) FROM paper_trades WHERE status = 'CLOSED' AND recorded_via = 'manual';
-- expect >= 10, human-executed via /record
SELECT is_ready FROM trader_session_state WHERE session_date = current_date;
-- manually toggle /ready off, confirm the calendar gate blocks the next cycle
```

**Phase 5 — Statistical Finish Line**
```sql
SELECT strategy_slug, count(*), avg(pnl_rupees) FROM paper_trades
  WHERE status='CLOSED' GROUP BY strategy_slug;
-- exit criteria: count >= 50 per strategy, spanning >= 2 monthly expiry cycles,
-- positive avg(pnl_rupees) AFTER real transaction costs are already netted into pnl_rupees,
-- reported alongside a confidence interval and max drawdown, never the point estimate alone
```
**Timeline caveat, stated so it isn't accidentally overpromised elsewhere:** GVOF and Wyckoff will not necessarily reach 50 closed trades at the same rate — one strategy's entry conditions may simply fire more often than the other's. Appendix H's "~2-month validation window" estimate is a *cycle-volume and cost* calculation, not a promise that both strategies clear Phase 5 on the same calendar date. Evaluate each strategy's gate independently against its own row above; a strategy that's slower to accumulate trades isn't broken, it's just rarer, and shouldn't be rushed into a Phase 7 capital decision on a thinner sample than the other one has.

**Phase 6 — Expansion, and *(extended in v11)* Per-Component Promotion Evaluation**
```
Remaining 3 Wyckoff variants built SHADOW-only; BankNifty's 6-criteria AND-gate formally
evaluated against real accumulated data (all 6 columns true).

NEW -- Track-S-to-expanded-architecture promotion gate (D-T11): for EACH Appendix I
component under consideration (Verifier LLM, second LLM provider, RAG memory pipeline,
DB-backed strategy registry + review pipeline), check it independently against Appendix J's
trigger table. A component is eligible for promotion only if:
  SELECT count(*) FROM paper_trades WHERE status='CLOSED' -- >= 50 (Phase 5's own gate), AND
  the specific trigger condition in Appendix J for that component is met, AND
  a human has written down, in this document's changelog, the concrete justification.
No component is added "because it might help" -- only because its specific trigger fired.
```

**Phase 7 — Real-Capital Consideration.** Human judgment only, never automated, never queried. If Phase 5's exit criteria are met with a genuinely positive, cost-adjusted, statistically meaningful EV, the decision to scale beyond paper/shadow capital belongs to the human operator alone.

---

## §5 — BUILD-FROM-SCRATCH RUNBOOK

### §5.1 — Repository Skeleton

```
axis/
  main.py                 server.py                Procfile
  requirements.txt        .env.example
  src/
    config/       settings.py, constants.py
    scoring/       layer_a.py, layer_b.py, layer_c.py, direction_scorer.py, structure_gate.py
    strategies/    base.py, gvof.py, wyckoff_mean_reversion.py
    graph/         graph.py, nodes.py, state.py
    data/          dhan_client.py, nse_fetcher.py, event_calendar.py, instrument_resolver.py,
                   ohlc_writer.py, market_snapshot.py
    llm/           router.py, json_extractor.py
    journal/       position_sizer.py
    risk/          risk_manager.py
    delivery/      telegram_formatter.py, alert_builder.py
    scheduling/    calendar_gate.py, lock_manager.py, no_trade_summary.py
    commands/      router.py, handlers.py          # NEW: D-055's /ready /record /close /resend
    database/      supabase.py, table_routing.py
    math/          pricing.py
    utils/         health_check.py
    observability/ correlation.py
  migrations/       001_core_tables.sql  [+ 0NN_extended_*.sql as each Extended feature is built]
  tests/            test_*.py per module, conftest.py
  dashboard/         index.html, app.js, shared.js
  .github/workflows/ main_pipeline.yml (WITH concurrency group), token_refresh.yml, no_trade_cron.yml,
                     weekly_friction_cron.yml, keepalive.yml, tests.yml (CI -- runs pytest on
                     every push/PR to main, separate from the trading cron; see Step 15a)
```

**Rule enforced from day one:** no code merges referencing a table without a migration for it already in `migrations/`, in the same PR (§2.0 principle 6).

### §5.2 — Supabase Setup (Core tier first)

1. Create the Supabase project. Skip `pgvector` entirely — this build has no RAG pipeline.
2. Enable PITR before Phase 3 generates real paper-trade data worth protecting.
3. Run the **Core migration only** (`signals`, `active_position`, `system_paused`, `telegram_updates_processed`, `trader_session_state`, `cycle_summaries`, `macro_regime_flags` — seven tables, full DDL in Appendix C). Add Extended-tier tables one at a time, each in its own migration, only when the feature that needs it is actually being built.
3a. **Enable RLS on all seven tables immediately after creating them, in the same sitting** — not as a later checklist item to remember. Grant `anon` read-only `SELECT` on `signals` only (the one table this build's dashboard actually needs); leave the other six with RLS enabled and zero `anon` policies. §6.1 re-checks this before deploy, but it's cheaper and less error-prone to do it once, right here, than to audit for it later.
4. Capture `SUPABASE_URL`, `SUPABASE_ANON_KEY` (dashboard, client-side), `SUPABASE_SERVICE_ROLE_KEY` (backend only, never ships client-side).
5. Seed `system_paused` **paused** — `id=1, is_paused=true` — before the first run. A fresh deploy should require a deliberate human action to start trading, not start hot the moment the first cron fires. Flip it to `false` only once you've completed §6.1's pre-deploy checklist and are actually ready for Phase 1. (In practice `trader_session_state`'s daily `/ready` requirement already blocks a same-day cold start too — see D-004 — but the kill switch defaulting to paused is a second, independent layer of the same fail-closed philosophy, not reliance on remembering just one gate.)

### §5.3 — External Accounts

| Service | Obtain | Feeds |
|---|---|---|
| Dhan | Client ID, initial token, TOTP secret, PIN | Data layer |
| Google AI Studio | `GOOGLE_API_KEY` | Analyst |
| Telegram | Bot token, chat ID, **webhook secret (now required — D-055)** | Alerts + inbound commands |
| GitHub | Repo, Actions enabled, secrets configured | Scheduling |
| Netlify | Site (dashboard only — no Functions needed in this build) | Dashboard |
| Render | Web service → `server:app` | Health check + inbound command endpoint (D-055) |

Skip Cognee-shaped variables entirely (D-T5).

### §5.4 — Build Order, With State-Verification Gates

```bash
# STEP 1 -- config + math (no dependencies)
python -m pytest tests/test_pricing.py -q
# GATE: every assertion uses pytest.approx(exact_value) against Layer 1 formulas (pre-empts D-018)

# STEP 2 -- scoring layer (deterministic, zero LLM imports, keep it that way)
python -c "from src.scoring.direction_scorer import compute_direction_score; print('OK')"

# STEP 3 -- data orchestration (THE D-001 FIX, built here from the start)
# build src/data/market_snapshot.py's fetch_and_score_market_data(), including the D-045
# stale-data check and the D-047 NSE-block classification
python -c "from src.data.market_snapshot import fetch_and_score_market_data; print('OK')"
# GATE: a from-scratch build should never reproduce D-001, because this step exists.

# STEP 4 -- dhan_client.py, nse_fetcher.py, instrument_resolver.py, event_calendar.py, ohlc_writer.py
pytest tests/test_data_layer.py -q

# STEP 5 -- strategies: build gvof.py and wyckoff_mean_reversion.py; register BOTH immediately
grep -n "STRATEGIES" src/graph/nodes.py
# EXPECTED: both classes listed.

# STEP 6 -- LLM router (Analyst only; no lock needed -- see §2.2 race-condition note)
python -c "from src.llm.router import call_llm_router; print('OK')"

# STEP 7 -- risk_manager.py, position_sizer.py (pure Python gating, no Verifier LLM)
pytest tests/test_governance.py -q

# STEP 8 -- delivery: telegram_formatter.py, alert_builder.py, INCLUDING the D-048 persistence
# write and the D-049 dedup horizon check
pytest tests/test_telegram_queue.py -q

# STEP 9 -- scheduling: calendar_gate.py (FAIL-CLOSED, D-T8), lock_manager.py (thin, D-T9),
# no_trade_summary.py
python -c "
from src.scheduling.calendar_gate import is_system_paused
# manually simulate a DB read failure and confirm the function returns True (paused)
"

# STEP 10 -- graph/state.py: declare the FULL field contract up front (pre-empts D-013)

# STEP 11 -- import logging; _log = logging.getLogger('axis.nodes') BEFORE writing any
# _log.error(...) call (pre-empts D-005)

# STEP 12 -- build all 8 in-graph nodes; wire graph.py
python -c "from src.graph.graph import graph; print('GRAPH IMPORTS CLEANLY')"
# THE SINGLE MOST IMPORTANT GATE IN THE WHOLE RUNBOOK. If this fails, stop.

# STEP 13 -- main.py: run_all_symbols_cycle(), cross_symbol_correlation_step (SOLE location,
# main.py only, §2.3 step 8 -- pre-empts D-008 by construction), _run_cli() wired to
# __main__ (pre-empts D-009). Also write one cycle_summaries row per cycle here --
# status OK/CRASH/DEGRADED -- wrapped so it writes even if the cycle itself throws
# (pre-empts D-037 by construction; this is the row Phase 3's gate actually reads).
python main.py --symbol NIFTY
# EXPECTED outside market hours: a clean calendar_open=False short-circuit, no traceback.

# STEP 14 -- server.py: health check endpoint (no subprocess spawn -- pre-empts D-016),
# PLUS the D-055 inbound command route (/telegram/webhook: auth check, update_id dedup
# against telegram_updates_processed, route to /ready /record /close /resend handlers)
# Procfile -> server:app (pre-empts D-010)
pytest tests/test_command_webhook.py -q
# GATE: sending the same simulated update_id twice produces the DB effect exactly once.

# STEP 15 -- .github/workflows/main_pipeline.yml: weekday-restricted cron from day one
# (pre-empts D-032), a concurrency group from day one (pre-empts D-051), AND a job-level
# timeout so a genuinely hung run can't silently burn the whole month's minutes budget:
```
```yaml
jobs:
  run-cycle:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    concurrency:
      group: axis-trading-cycle
      cancel-in-progress: false
on:
  schedule:
    - cron: '40-59/5 3 * * 1-5'
    - cron: '*/5 4-9 * * 1-5'
    - cron: '0-5/5 10 * * 1-5'
  workflow_dispatch: {}
```
```bash
# STEP 15a -- .github/workflows/tests.yml: a SEPARATE, minimal CI workflow -- run pytest
# on every push and PR to main. Without this, "pytest -q" is only ever a manual step
# (§5.4's own final gate), which means a broken change can reach the scheduled cron
# untested and the first sign of trouble is a live cycle failing -- not what "tech
# debt" should mean for a system whose whole point is a trustworthy signal.
```
```yaml
name: tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
concurrency:
  group: tests-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true   # opposite of main_pipeline.yml's choice, correctly --
                              # an outdated CI run has zero value once a newer commit
                              # exists, so cancel it outright rather than let it queue;
                              # a live trading cycle mid-dispatch is the one thing worth
                              # never interrupting (D-T9), a stale test run is not
jobs:
  pytest:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -r requirements.txt
      - run: pytest --ignore=tests/smoke -q
```
```bash
# STEP 16 -- active_position table + position_state_check_node (pre-empts D-050)

# STEP 17 -- register the Telegram webhook: setWebhook pointed at the Render URL's
# /telegram/webhook route; confirm getWebhookInfo shows it registered

# STEP 18 -- tests/: write alongside each module above, not after; categorize per Appendix E

# FINAL GATE
pytest -q
python main.py --symbol NIFTY
```

**If you later want any Appendix I component:** check it against Appendix J's trigger table first, then follow that appendix's own build notes — don't retrofit it ad hoc.

---

## §6 — PRODUCTION DEPLOYMENT CHECKLIST

### §6.1 — Pre-Deploy

- [ ] All P0 Delta Ledger items closed, each with its verification command re-run and passing.
- [ ] Appendix A run in full against the real repo; output pasted into Appendix B.
- [ ] Core-tier migrations applied; Extended-tier migrations applied only for features actually built.
- [ ] **Row-Level Security (RLS) enabled on every Core-tier table, verified explicitly, not assumed.** The dashboard (Appendix I context aside — this build's dashboard too) uses `SUPABASE_ANON_KEY`, which ships in client-side JS on a public page. Supabase's default table grants mean an anon-accessible table with RLS *disabled* is readable — and on some grant configurations, writable — by anyone who opens the dashboard's network tab and copies the key straight out of it, not just by the dashboard's own UI. Concretely: `signals` (and any Extended-tier table the dashboard later reads, e.g. `paper_trades`) gets an RLS policy granting the `anon` role `SELECT` only, nothing else. `system_paused`, `trader_session_state`, `telegram_updates_processed`, and `active_position` get RLS enabled with **no policy for `anon` at all** — the service-role key bypasses RLS entirely (by design, that's what it's for), so these tables need zero anon access, full stop. This is a five-minute Supabase dashboard task with a real consequence if skipped: an unprotected `system_paused` table would mean anyone with the anon key could theoretically toggle the kill switch itself.
- [ ] Every secret in Appendix D present in GitHub Secrets / Render env. Cognee-shaped variables deliberately absent (D-T5).
- [ ] `main_pipeline.yml` cron weekday-restricted (D-032) **and** has a `concurrency:` group (D-051).
- [ ] Kill switch confirmed fail-closed (D-T8/D-052): simulate an unreadable pause state, confirm the cycle does not run.
- [ ] Position-state tracking confirmed (D-050): manually set an open position, confirm a same-direction signal is suppressed.
- [ ] Telegram delivery persistence confirmed (D-048): force a failed send, confirm the row persists and `/resend` recovers it.
- [ ] Dedup horizon confirmed (D-049): force two identical consecutive signals, confirm only one dispatches.
- [ ] Stale-data abort confirmed (D-045): mock an old timestamp, confirm the cycle aborts before scoring.
- [ ] `Procfile` confirmed pointing at `server:app`; Render serving `/health` with 200 (D-010).
- [ ] `_run_cli()` confirmed wired to `__main__`; crash alert path manually tested (D-009).
- [ ] **Inbound command endpoint (D-055) confirmed**: webhook registered via `setWebhook`; all four commands round-tripped; repeated `update_id` produces no duplicate effect; wrong secret token returns 401.
- [ ] **`/record` duplicate-position rejection confirmed (D-046):** with a position already `OPEN`, send `/record` again for the same symbol, confirm it's rejected with an error, not inserted as a second row.

### §6.2 — First Live Cycle (Phase 2/3 boundary)

- [ ] Trigger one cycle manually via `workflow_dispatch`.
- [ ] Watch the log; confirm every node executes with no unhandled exception.
- [ ] Confirm `layer_a/b/c` are populated with real, non-default values for that cycle.
- [ ] Confirm `direction_score` isn't a hardcoded 3 unless the real data genuinely produced a neutral read.
- [ ] Confirm exactly one row in `macro_regime_flags` for the cycle (D-008, by construction).
- [ ] Confirm `/record` works end-to-end for a simulated trade.

### §6.3 — First Ten Market Days (Phase 3)

- [ ] Daily: confirm the pipeline ran on schedule via Actions history, not silence.
- [ ] Daily: skim alert quality — do direction scores look like they track real market conditions, or suspiciously static?
- [ ] Daily: **check for gaps in `cycle_summaries`, not just explicit `CRASH` rows.** A process that gets hard-killed (OOM, the job-level `timeout-minutes` backstop, a runner failure) never reaches its own `try/finally` and never writes a `CRASH` row at all — it just leaves a hole in the timeline where a row should be. `SELECT cycle_timestamp FROM cycle_summaries ORDER BY cycle_timestamp DESC LIMIT 20;` and eyeball for any gap wider than ~10 minutes during trading hours. This catches the exact failure class that `WHERE status='CRASH'` structurally cannot see — the crash that was too abrupt to log itself.
- [ ] End of week: sanity-check real transaction-cost numbers against Layer 1's formulas.
- [ ] End of week: confirm trade/outcome rows accumulate consistent with PROCEED verdicts sent.

### §6.4 — Ongoing Operations & Free-Tier Hardening

- [ ] Monthly: re-check LLM model strings against the provider's current list (D-026).
- [ ] Monthly: re-verify circuit breaker trip logs for all dependencies (D-020).
- [ ] **Annually (before the new year):** refresh `AXIS_MARKET_HOLIDAYS`. A stale holiday list doesn't crash anything — the exchange being closed on an unlisted holiday just means Dhan/NSE return no real data, which the stale-data check (D-045) should catch — but it's a silent, avoidable source of wasted cycles and confusing logs for the cost of updating one env var once a year. Cheap enough that there's no excuse to let it go stale.
- [ ] **Token refresh timing:** `token_refresh.yml`'s 8-hour cadence should land outside the 09:15–15:30 IST trading window where practical, so a mid-cycle token rotation is never racing a cycle's own Dhan calls. Not a correctness requirement (Postgres reads of `broker_tokens` are consistent either way, and the existing circuit-breaker/retry hygiene absorbs a transient auth hiccup) — just cheap, sensible scheduling hygiene.
- [ ] **Break-glass fallback (D-053):** if GitHub Actions is unavailable, run `python main.py --all` manually from any machine with the correct `.env` populated. **Rehearse this once before you need it** — GitHub's encrypted secrets aren't in any `.env` file; exporting all of Appendix D's variables into a local one is a real 10-minute task, not an instant fallback.
- [ ] **Extended absence (vacation, illness, travel):** simply don't send `/ready`. `trader_session_state` requires a fresh confirmation for each `session_date` and defaults to blocked, so the system already fails closed with zero fetch calls, zero LLM spend, and zero Telegram sends on any day it isn't sent. No separate pause mechanism needed (D-004).
- [ ] **GitHub Actions minutes:** if there's no code-sensitivity reason to keep the repo private, making it public removes the minutes budget question (D-033) entirely. If it must stay private, add `actions/cache` for pip dependencies.
- [ ] **Render keep-warm:** point the existing UptimeRobot ping at `/health` — this simultaneously prevents idle spin-down (which would also delay `/telegram/webhook` responses) and serves as the uptime monitor.
- [ ] **Supabase keepalive:** extend the existing `keepalive.yml` to also run one trivial `SELECT 1` against Supabase, preventing free-tier auto-pause during a multi-day market holiday.
- [ ] **LLM rate limits under real load (D-054):** once staging exists, run one deliberate load test matching the real fan-out pattern.
- [ ] Before any capital-scaling decision (Phase 7): re-run the full Phase 5 statistical review from scratch against the latest data.
- [ ] Before adding any Appendix I component: check it against Appendix J's trigger table and write the justification into this document's changelog (§2.0 principle 8; D-T11).

### §6.5 — Rollback Principles

Not a phase-by-phase runbook — most rollback here is "the last git commit," since this system has no live capital until Phase 7. Three things are worth stating explicitly rather than assuming:

1. **A wrong-but-confident signal is worse than a missing one.** If the D-001 fetch function has a bug that produces *plausible but incorrect* `market_context` values (not missing — wrong), the dead-zone abort won't catch it, because a wrong value can easily land outside 2.0–4.0 and look like a real signal. There is no automated detection for "the data is wrong but present" — this is exactly why Phase 2's gate requires tracing a full cycle by eye against known real market conditions before trusting the pipeline, and why §6.3's daily "do the scores look plausible" check exists for the first ten market days. If a signal looks wrong, revert to the previous commit of `market_snapshot.py` and re-trace before trusting the next cycle.
2. **An auth bug in the inbound endpoint (D-055) is a data-integrity incident, not just a security one.** If `/telegram/webhook`'s secret-token check were ever bypassed, someone could inject fake `/record` entries and quietly poison the Phase 5 win-rate and EV numbers this whole project exists to produce. Detection: `paper_trades.recorded_via = 'manual'` rows with no corresponding real Telegram alert in `signals` for that symbol/time are the tell. Rollback: revert `server.py` to the previous commit, rotate `TELEGRAM_WEBHOOK_SECRET`, and treat every `paper_trades` row since the suspected bypass as suspect for Phase 5 purposes — don't just delete them, flag and exclude, so the audit trail stays honest (§0's confidence-grammar spirit applies to your own data, not just this document's claims).
3. **Kill switch first, investigate second.** For anything else that looks wrong mid-cycle, `/close` any open position awareness aside, the fastest correct action is always flipping `system_paused` (or simply not sending `/ready` the next morning) before debugging — fail-closed is cheap; a confidently wrong signal reaching a human is not.

---

## §7 — APPENDICES

### Appendix A — Unified Verification Script

```bash
#!/usr/bin/env bash
# AXIS Master Blueprint v11 -- Unified Verification Script
set -uo pipefail
echo "AXIS VERIFICATION -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo ""; echo "=== STEP ZERO: the single most load-bearing check in this document ==="
wc -l src/scoring/layer_b.py src/memory/ingest.py src/memory/recall.py 2>&1
echo "EXPECTED: 30, 71, 35 -- if this fails, treat every S1-CITED claim in Section 3 as unconfirmed."

echo ""; echo "=== SMOKE TEST: does the graph import cleanly? ==="
python -c "from src.graph.graph import graph; print('GRAPH IMPORTS CLEANLY')" 2>&1

echo ""; echo "=== D-001: IS THE SCORING PIPELINE WIRED? (single-sourced -- confirm carefully) ==="
grep -rn "score_layer_a\|score_layer_b\|score_layer_c" main.py src/graph/ src/data/ 2>/dev/null \
  || echo "NO CALL SITE FOUND OUTSIDE src/scoring/ ITSELF -- D-001 CONFIRMED"

echo ""; echo "=== D-004: /ready command present ==="
grep -rn "/ready" src/ 2>/dev/null || echo "NOT FOUND -- D-004 OPEN"

echo ""; echo "=== D-005: _log DEFINITION ==="
grep -n "^import logging\|_log = logging" src/graph/nodes.py 2>/dev/null || echo "_log NEVER DEFINED"

echo ""; echo "=== D-007: ohlc_writer.py ==="
find . -iname "ohlc_writer.py" 2>/dev/null || echo "NOT FOUND"

echo ""; echo "=== D-008: SINGLE-LOCATION CROSS-SYMBOL LOGIC ==="
grep -n "macro_regime_flags\|apply_same_cycle_correlation\|cross_symbol_correlation" main.py 2>/dev/null
grep -n "macro_regime_flags" src/graph/nodes.py 2>/dev/null
echo "EXPECTED: nodes.py grep returns NOTHING -- correlation logic lives only in main.py"

echo ""; echo "=== D-009: CRASH ALERT WIRING ==="
grep -n "__main__" main.py 2>/dev/null
grep -n "_run_cli\|_amain" main.py 2>/dev/null

echo ""; echo "=== D-010: Procfile / server.py ==="
cat Procfile 2>/dev/null; cat server.py 2>/dev/null

echo ""; echo "=== D-011: CORE-TIER LIVE DATABASE TABLES (7) -- run in Supabase SQL editor ==="
cat <<'SQL'
SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;
SELECT count(*) FROM signals; SELECT count(*) FROM active_position;
SELECT count(*) FROM system_paused; SELECT count(*) FROM telegram_updates_processed;
SELECT count(*) FROM trader_session_state; SELECT count(*) FROM cycle_summaries;
SELECT count(*) FROM macro_regime_flags;
SQL

echo ""; echo "=== D-012: STRATEGY REGISTRATION ==="
grep -n "STRATEGIES" src/graph/nodes.py 2>/dev/null
echo "EXPECTED: both GVOFStrategy() and WyckoffMeanReversionStrategy() listed"

echo ""; echo "=== D-013: AxisState FIELD CONTRACT ==="
grep -n "candidate_signals\|active_position\|is_backtest" main.py src/graph/state.py 2>/dev/null

echo ""; echo "=== D-045: STALE-DATA CHECK ==="
grep -n "stale\|timestamp" src/data/market_snapshot.py 2>/dev/null || echo "NOT FOUND -- D-045 OPEN"

echo ""; echo "=== D-047: NSE BLOCK DETECTION ==="
grep -n "403\|NSE_BLOCKED" src/data/nse_fetcher.py 2>/dev/null || echo "NOT FOUND -- D-047 OPEN"

echo ""; echo "=== D-048: TELEGRAM DELIVERY PERSISTENCE ==="
grep -n "telegram_sent" src/delivery/*.py src/graph/nodes.py 2>/dev/null || echo "NOT FOUND -- D-048 OPEN"

echo ""; echo "=== D-049: DEDUP HORIZON ==="
grep -n "60\|dedup" src/graph/nodes.py 2>/dev/null

echo ""; echo "=== D-050: ACTIVE POSITION TRACKING ==="
grep -rn "active_position" src/ 2>/dev/null || echo "NOT FOUND -- D-050 OPEN"

echo ""; echo "=== D-051: GH ACTIONS CONCURRENCY GROUP ==="
grep -n "concurrency:" .github/workflows/main_pipeline.yml 2>/dev/null || echo "NOT FOUND -- D-051 OPEN"

echo ""; echo "=== D-052: KILL SWITCH FAIL MODE ==="
grep -n "is_system_paused\|is_paused" src/scheduling/calendar_gate.py 2>/dev/null
echo "MANUAL CHECK: simulate a DB read failure, confirm it returns True (paused), not False"

echo ""; echo "=== D-046: /record REJECTS A DUPLICATE OPEN POSITION ==="
grep -rn "active_position" src/commands/ 2>/dev/null \
  || echo "NOT FOUND -- /record may not check for an existing open position, D-046 not fully closed"

echo ""; echo "=== D-055: INBOUND COMMAND ENDPOINT (NEW in v11) ==="
grep -rn "telegram/webhook\|X-Telegram-Bot-Api-Secret-Token" server.py src/commands/ 2>/dev/null \
  || echo "NOT FOUND -- D-055 OPEN"
grep -rn "telegram_updates_processed" src/commands/ 2>/dev/null \
  || echo "NOT FOUND -- update_id dedup missing, D-055 not fully closed"

echo ""; echo "=== D-055 INTEGRITY TEST (requires a staging deploy -- run manually, not part of the grep pass) ==="
cat <<'CURL'
# 1. Wrong secret must be rejected before anything else runs:
curl -s -o /dev/null -w "wrong-token status: %{http_code}\n" -X POST \
  https://<your-render-app>.onrender.com/telegram/webhook \
  -H "X-Telegram-Bot-Api-Secret-Token: wrong-token" \
  -d '{"update_id": 900001, "message": {"text": "/ready"}}'
# EXPECTED: 401

# 2. Correct secret, a FRESH update_id, must apply the effect:
curl -s -o /dev/null -w "fresh-update status: %{http_code}\n" -X POST \
  https://<your-render-app>.onrender.com/telegram/webhook \
  -H "X-Telegram-Bot-Api-Secret-Token: <real TELEGRAM_WEBHOOK_SECRET>" \
  -d '{"update_id": 900002, "message": {"text": "/ready"}}'
# EXPECTED: 200, and SELECT is_ready FROM trader_session_state WHERE session_date=current_date; -> true

# 3. Correct secret, the SAME update_id repeated, must be a no-op:
curl -s -o /dev/null -w "repeated-update status: %{http_code}\n" -X POST \
  https://<your-render-app>.onrender.com/telegram/webhook \
  -H "X-Telegram-Bot-Api-Secret-Token: <real TELEGRAM_WEBHOOK_SECRET>" \
  -d '{"update_id": 900002, "message": {"text": "/ready"}}'
# EXPECTED: 200, and no additional side effect -- 900002 is already in
# telegram_updates_processed from step 2, so this call should be a pure no-op.
CURL

echo ""; echo "=== D-T5: COGNEE GHOST DEPENDENCY ==="
grep -n "cognee" requirements.txt 2>/dev/null
echo "EXPECTED AFTER FIX: no output"

echo ""; echo "=== TEST SUITE ==="
gh run list --limit 10 2>/dev/null || echo "gh CLI not available; check Actions tab manually"
find . -name "test_*.py" -size 0 2>/dev/null
pytest --ignore=tests/smoke -q 2>&1 | tail -30

echo ""; echo "END VERIFICATION -- paste this entire output into Appendix B"
```

### Appendix B — Verification Tracker

**Honesty note, stated plainly:** every box below is currently unchecked. Nobody has run Appendix A against the live repository as part of compiling this edition. Do not treat any `S1-CITED` claim in §3 as `S1-CONFIRMED` until this tracker has real, pasted output next to it.

```
=== STEP ZERO ===
[ ] layer_b.py / ingest.py / recall.py line counts match 30/71/35: Y/N ______

=== P0 ===
[ ] D-001 data-collection call sites found: Y/N ______   [ ] D-004 /ready command: Y/N
[ ] D-005 _log defined: Y/N                                [ ] D-007 ohlc_writer.py: Y/N
[ ] D-008 correlation single-location: Y/N                 [ ] D-009 __main__ calls _run_cli(): Y/N
[ ] D-010 Procfile -> server:app: Y/N                       [ ] D-011 Core tables exist: Y/N
[ ] D-012 both strategies registered: Y/N                   [ ] D-013 state contract resolved: Y/N
[ ] D-045 stale-data abort: Y/N                               [ ] D-046 /record workflow: Y/N
[ ] D-047 NSE block detection: Y/N                             [ ] D-048 telegram persistence: Y/N
[ ] D-049 dedup horizon: Y/N                                     [ ] D-050 active_position tracking: Y/N
[ ] D-051 concurrency group: Y/N                                  [ ] D-052 kill switch fail-closed: Y/N
[ ] D-053 break-glass documented: Y/N                              [ ] D-055 inbound endpoint + dedup: Y/N

=== DECISION TREES (12) ===
[ ] D-T1 entrypoint confirmed live: Y/N        [ ] D-T2 Wyckoff registered: Y/N
[ ] D-T3 NIFTY live/shadow, live query result: ______   [ ] D-T4 Render health-check-plus-endpoint only: Y/N
[ ] D-T5 Cognee removed: Y/N                    [ ] D-T6 KB distilled block written: Y/N
[ ] D-T7 scope confirmed (this build only, for now): Y/N   [ ] D-T8 kill switch fail-closed: Y/N
[ ] D-T9 concurrency group confirmed, lock_check_node confirmed thin: Y/N
[ ] D-T10 second LLM provider: none/added        [ ] D-T11 any Appendix I component promoted: none/list
[ ] D-T12 Kelly gross/net verified against real position_sizer.py: Y/N (default: gross, unverified)

=== TOTAL: ___ / 55 (P0-P3) + 12 (Decision Trees), as of [date] ===
```

### Appendix C — Database Migrations, Core & Extended Tiers

```sql
-- ==============================================================================
-- WARNING: S2-DERIVED SCHEMA -- INFERRED FROM CODE, NOT DUMPED FROM A LIVE DATABASE
-- ==============================================================================
-- Correct, runnable STARTING POINT, not a confirmed reproduction of any hidden
-- existing schema.
--
-- MANDATORY RULES:
-- 1. Do NOT run this against a production database first.
-- 2. Run against a disposable Supabase branch; run the test suite / first green
--    run (Section 5.4) against that branch before touching production.
-- 3. If an RPC or query throws "column does not exist," ALTER the table to match
--    what the code actually expects, THEN apply to production.
-- 4. Every column used in a WHERE/JOIN in Python code has an index below.
-- ==============================================================================

-- =========================== CORE TIER (build immediately -- 7 tables) ==========

CREATE TABLE IF NOT EXISTS signals (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol              TEXT NOT NULL,
    cycle_timestamp     TIMESTAMPTZ NOT NULL,
    correlation_id      TEXT,
    direction_score     INTEGER,
    structure_confirmed BOOLEAN,
    active_strategy_slug TEXT,
    analyst_opinion     JSONB,
    verdict             JSONB,
    dedup_status        TEXT,
    alert_sent          BOOLEAN NOT NULL DEFAULT false,
    telegram_sent       BOOLEAN NOT NULL DEFAULT false,   -- D-048
    telegram_error      TEXT,                              -- D-048
    is_backtest         BOOLEAN NOT NULL DEFAULT false,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_signals_symbol_cycle ON signals (symbol, cycle_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_signals_unsent ON signals (telegram_sent) WHERE telegram_sent = false;  -- D-048 retry query
CREATE INDEX IF NOT EXISTS idx_signals_dedup ON signals (symbol, active_strategy_slug, cycle_timestamp DESC);  -- D-049

CREATE TABLE IF NOT EXISTS active_position (          -- D-050
    symbol              TEXT PRIMARY KEY,
    strike              NUMERIC,
    option_type         TEXT CHECK (option_type IN ('CE','PE')),
    entry_price         NUMERIC,
    opened_at           TIMESTAMPTZ,
    signal_id           UUID REFERENCES signals(id) ON DELETE SET NULL,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS system_paused (             -- singleton kill switch, fail-CLOSED per D-T8
    id                  INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    is_paused           BOOLEAN NOT NULL DEFAULT true,  -- fail-closed at the SCHEMA level too,
                                                          -- not just on a read failure -- v11 hardening
    paused_by           TEXT,
    paused_reason       TEXT,
    paused_at           TIMESTAMPTZ,
    resumed_at          TIMESTAMPTZ
);
INSERT INTO system_paused (id, is_paused) VALUES (1, true) ON CONFLICT (id) DO NOTHING;
-- A fresh deploy starts PAUSED. Flip to false deliberately (§6.1's checklist) once you're
-- actually ready for Phase 1 -- never let "the migration ran" double as "start trading."

CREATE TABLE IF NOT EXISTS telegram_updates_processed (   -- NEW in v11, supports D-055
    update_id           BIGINT PRIMARY KEY,
    command              TEXT,
    processed_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Purpose: Telegram may redeliver the same webhook update on a timeout or retry.
-- The inbound endpoint checks this table before acting; if update_id already exists,
-- it returns 200 immediately without repeating the effect (idempotent command handling,
-- §2.0 principle 2). One tiny table, closes a real double-execution risk for /record
-- and /close specifically.

CREATE TABLE IF NOT EXISTS trader_session_state (       -- backs /ready
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), session_date DATE NOT NULL UNIQUE,
    is_ready BOOLEAN NOT NULL DEFAULT false,        -- ONE column, fail-closed by default.
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- calendar_gate_node's rule is single-sourced and simple: no row for today, or
-- is_ready = false -> blocked. /ready UPSERTs today's row with is_ready = true.
-- (v11 hardening: this table used to also carry a separate is_trading_blocked
-- column defaulting true, which nothing consistently checked and which could
-- silently disagree with is_ready. One column, one meaning -- §2.0 principle 3.)

CREATE TABLE IF NOT EXISTS cycle_summaries (           -- D-037 real heartbeat; promoted to
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),      -- Core tier in v11 -- a liveness
    cycle_timestamp TIMESTAMPTZ NOT NULL,                -- signal is a day-one need, not a
    symbols_processed TEXT[], signals_generated INTEGER DEFAULT 0, alerts_sent INTEGER DEFAULT 0,
    status TEXT DEFAULT 'OK' CHECK (status IN ('OK','CRASH','DEGRADED')),  -- used by Phase 3's gate
    errors JSONB DEFAULT '[]', duration_ms INTEGER, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_cycle_summaries_status ON cycle_summaries (status, cycle_timestamp DESC);

CREATE TABLE IF NOT EXISTS macro_regime_flags (        -- Core tier, NOT Extended -- §2.3 step 8
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), cycle_timestamp TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL, direction TEXT, haircut_applied BOOLEAN NOT NULL DEFAULT false,
    haircut_pct NUMERIC, correlated_symbol TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_macro_regime_flags_cycle ON macro_regime_flags (cycle_timestamp);
-- v11 correction: this table was originally filed under Extended tier ("build only when
-- the feature that needs it is built"), which was wrong -- the cross-symbol correlation
-- step (§2.3 step 8) that writes here is NOT optional or deferred, it runs unconditionally
-- every single cycle per §2.1's own "dispatch deferred until both finish" constraint. Left
-- in Extended tier, the very first cycle where both symbols PROCEED in the same direction
-- would crash on an INSERT into a table that doesn't exist yet. Core tier is 7 tables, not 6.

-- =========================== EXTENDED TIER (build one at a time, only when the
-- specific feature that needs each table is actually being built) ================

CREATE TABLE IF NOT EXISTS signal_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), signal_id UUID NOT NULL REFERENCES signals(id) ON DELETE CASCADE,
    gex_value NUMERIC, vix_value NUMERIC, pcr_value NUMERIC, ib_high NUMERIC, ib_low NUMERIC,
    entry_price NUMERIC, stop_loss NUMERIC, target_1 NUMERIC, target_2 NUMERIC, lots INTEGER,
    kelly_fraction NUMERIC, position_size_pct NUMERIC, correlation_haircut_pct NUMERIC,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS paper_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), signal_id UUID REFERENCES signals(id) ON DELETE SET NULL,
    symbol TEXT NOT NULL, strategy_slug TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('CE','PE','LONG','SHORT')),
    entry_price NUMERIC NOT NULL, entry_time TIMESTAMPTZ NOT NULL,
    stop_loss NUMERIC NOT NULL, target NUMERIC NOT NULL, lots INTEGER NOT NULL,
    position_size_pct NUMERIC, status TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','CLOSED','CANCELLED')),
    exit_price NUMERIC, exit_time TIMESTAMPTZ, exit_reason TEXT,
    pnl_points NUMERIC, pnl_rupees NUMERIC, is_backtest BOOLEAN NOT NULL DEFAULT false,
    recorded_via TEXT DEFAULT 'manual',   -- D-046: 'manual' (/record) or 'automated' (Appendix I)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_paper_trades_status ON paper_trades (status, symbol);
CREATE INDEX IF NOT EXISTS idx_paper_trades_strategy ON paper_trades (strategy_slug, status);  -- Phase 5 EV queries

CREATE TABLE IF NOT EXISTS run_locks (       -- backs the thin lock_check_node, §2.3 step 1
    symbol TEXT PRIMARY KEY, locked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL, locked_by TEXT, cycle_id TEXT
);
-- Note (amended D-T9): useful only for manual/local runs outside GH Actions (D-053).
-- Redundant during scheduled runs once the concurrency group is confirmed.
-- TTL: set expires_at to roughly 3 minutes (180s) from locked_at, comfortably under the
-- 5-minute cycle interval -- a crashed manual run must never be able to block the next
-- legitimate one from acquiring the lock. A stale lock is a bug to route around, not a
-- reason to skip an entire cycle.

CREATE TABLE IF NOT EXISTS virtual_portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), symbol TEXT NOT NULL, strategy_slug TEXT NOT NULL,
    allocated_capital NUMERIC NOT NULL DEFAULT 100000, current_capital NUMERIC NOT NULL DEFAULT 100000,
    weekly_loss_limit_pct NUMERIC NOT NULL DEFAULT 5.0, weekly_loss_used_pct NUMERIC NOT NULL DEFAULT 0.0,
    week_start_date DATE NOT NULL DEFAULT date_trunc('week', now())::date,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE (symbol, strategy_slug)
);

CREATE TABLE IF NOT EXISTS accuracy_log (              -- Phase 5+, only once >=50 trades
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), run_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    layer_a_weight NUMERIC, layer_b_weight NUMERIC, layer_c_weight NUMERIC, sample_count INTEGER,
    vix_bucket TEXT CHECK (vix_bucket IN ('LOW','MEDIUM','HIGH')), half_life_days NUMERIC DEFAULT 75,
    pcr_divergence_flag BOOLEAN DEFAULT false, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS scoring_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), layer_a_weight NUMERIC NOT NULL DEFAULT 0.5,
    layer_b_weight NUMERIC NOT NULL DEFAULT 0.2, layer_c_weight NUMERIC NOT NULL DEFAULT 0.3,
    off_boundary_c_weight NUMERIC NOT NULL DEFAULT 0.05, is_active BOOLEAN NOT NULL DEFAULT true,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cached_candles (            -- needed once D-007/automated sampling is built
    id BIGSERIAL PRIMARY KEY, symbol TEXT NOT NULL, interval TEXT NOT NULL,
    candle_timestamp TIMESTAMPTZ NOT NULL, open NUMERIC, high NUMERIC, low NUMERIC, close NUMERIC,
    volume NUMERIC, oi NUMERIC, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (symbol, interval, candle_timestamp)
);
CREATE INDEX IF NOT EXISTS idx_cached_candles_lookup ON cached_candles (symbol, interval, candle_timestamp DESC);

CREATE TABLE IF NOT EXISTS market_context_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), symbol TEXT NOT NULL, cycle_timestamp TIMESTAMPTZ NOT NULL,
    market_context JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- custom_fields: SPECULATIVE, purpose unconfirmed by any audit (D-042). Omitted from the
-- default migration entirely. Define its real shape if a genuine need appears later.

-- Appendix I tables (strategies, strategy_configs, knowledge_chunks, infrastructure_locks)
-- are NOT part of this build's schema -- see Appendix I for their DDL, built only if
-- that component is promoted per Appendix J.

-- =========================== ALREADY MIGRATED ELSEWHERE (do not duplicate) =====================
-- backtest_signals, backtest_trades, api_circuit_breakers, daily_risk_limits, trade_tags,
-- strategy_asymmetry, broker_tokens
```

### Appendix D — Environment Variable Reference

| Variable | Consumed by |
|---|---|
| `GOOGLE_API_KEY` | Gemini (Analyst) |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | All Telegram ops |
| `TELEGRAM_WEBHOOK_SECRET` | **Now required for this build** — authenticates the D-055 inbound endpoint |
| `DHAN_CLIENT_ID`, `DHAN_ACCESS_TOKEN` (fallback), `DHAN_TOTP_SECRET`, `DHAN_PIN` | Dhan client + token refresh |
| `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` | DB access |
| `GOVERNANCE_DAILY_LOSS_MODE` | risk_manager.py, default `SHADOW` |
| `AXIS_MONTHLY_EXPIRIES`, `AXIS_MARKET_HOLIDAYS`, `AXIS_EVENT_DATES`, `AXIS_ENV_FILE` | Calendar logic |
| `UPTIMEROBOT_API_KEY` | External monitoring, rotate per D-024 |
| ~~`GROQ_API_KEY`, `ZAI_API_KEY`~~ | **Appendix I only** — not used in this build |
| ~~Cognee-shaped variables~~ | Remove entirely (D-T5) |

### Appendix E — Test File Categorization

Pure-Python (no mocks): `direction_scorer`, `ev_calculator`, `pricing` (fixed to exact `pytest.approx()` values per D-018), `structure_gate`. State-only: `gvof`, `wyckoff_mean_reversion` strategy tests. Supabase-mock: governance, journal. Network-mock: telegram queue, data layer, **`test_command_webhook.py`** (new — covers the D-055 endpoint's auth check, update_id dedup, and each of the four command handlers). Full-graph: `test_axis_graph`, `test_final_integration` — run last, slowest. Delete or implement: zero-byte placeholders and `test_cognee.py` (delete per D-T5). Relocate: stray root-level scratch test files.

### Appendix F — Knowledge Base File Inventory

`AXIS_Knowledge_Base.md` (113KB), `Supplement.md` (169KB), structured KB (56KB, one duplicate to delete), `v5_final_consolidated.md` as sole version authority (earlier versions excluded), four dated session logs (always authoritative). **This build's approach:** distill these same authoritative files, once, into a ~2,000-word rules block hardcoded into the Analyst's system prompt — zero database, zero embedding cost, zero glob bugs possible. See Appendix I if a real RAG pipeline is later promoted.

### Appendix G — System Architecture: The Rosetta Stone

| Node | Code File | Dependencies | DB Reads | DB Writes | State Reads | State Writes | Failure Behavior |
|---|---|---|---|---|---|---|---|
| calendar_gate_node | `scheduling/calendar_gate.py` | pytz/zoneinfo, holiday list | `system_paused`, `trader_session_state` | — | — | `calendar_open` | **Fail-CLOSED (D-T8):** unreadable pause state or `is_ready=false` → `calendar_open=False`, cycle ends |
| lock_check_node | `scheduling/lock_manager.py` | Postgres | `run_locks` | `run_locks` | — | `lock_acquired` | Thin by design (amended D-T9); real protection is the GH Actions concurrency group. Backup only for manual runs. |
| fetch_and_score_node | `data/market_snapshot.py`, `scoring/*.py` | Dhan client, NSE fetcher, scoring modules | — | — | `market_context` | `layer_a/b/c`, `direction_score` | Stale data (>15min, D-045) → abort with `STALE_DATA`; NSE 403 (D-047) → `NSE_BLOCKED`, fallback to Dhan; score in 2.0–4.0 → dead-zone abort per §2.4 |
| structure_gate_node | `scoring/structure_gate.py` | — | — | — | `market_context` | `structure_confirmed` | — |
| strategy_activation_node | `graph/nodes.py` (hardcoded list) | `strategies/gvof.py`, `strategies/wyckoff_mean_reversion.py` | — | — | — | `active_strategy` | No strategy passes → `active_strategy=None`, cycle ends quietly |
| risk_math_node | `risk/risk_manager.py`, `math/pricing.py`, `journal/position_sizer.py` | Pure Python only | `daily_risk_limits` (if built, account-wide not per-symbol/strategy) | — | `active_strategy` | `risk_verdict` (PROCEED/BLOCK) | R:R < 2.0x or EV < 0 → BLOCK, deterministic, no LLM involved. Kelly inputs computed per `strategy_slug`, never pooled. |
| position_state_check_node | `graph/nodes.py` | — | `active_position` | — | — | `position_conflict` | Open position + same-direction signal → suppress; opposite-direction → flag as exit warning (D-050) |
| dedup_node | `graph/nodes.py` | — | `signals` | — | — | `dedup_status` | Identical signal within 60 min → `DUPLICATE_SUPPRESSED` (D-049) |
| cross_symbol_correlation_step | `main.py` (orchestrator, not a node) | — | None (in-memory — reads both symbols' just-completed verdicts held by the orchestrator; no re-query) | `macro_regime_flags` | both symbols' verdicts | correlation-adjusted sizing | Runs exactly once per cycle, after both symbols' graphs finish (D-008) |
| analyst_and_dispatch_node | `llm/router.py`, `delivery/*.py` | Gemini (optional) | — | `signals` | — | `alert_sent`, `telegram_sent` | Gemini fails → templated message, no second provider (D-T10); Telegram non-200 → `telegram_sent=false`, retry path (D-048) |
| inbound_command_endpoint | `server.py`, `commands/router.py` | FastAPI (already deployed for health check) | `telegram_updates_processed`, `trader_session_state`, `active_position`, `signals` | same four tables | — | — | Wrong secret → 401; repeated `update_id` → 200, no-op; always 200 once authenticated (D-055) |

**Deployment topology:** GitHub Actions runs the 5-minute cycle and every side cron. Render hosts the health-check endpoint **and** the inbound command endpoint (one service, two routes — D-T4, D-055). Netlify hosts only the static dashboard. Supabase is the system of record. Telegram is the human notification/interaction channel. The human's own Dhan account is the only place any order is ever placed — outside AXIS's code, permanently, by design.

### Appendix H — Free-Tier Hardening Notes

- **Public-repo option** removes the GitHub Actions minutes budget question (D-033) entirely, if there's no code-sensitivity reason to stay private.
- **pip caching** via `actions/cache` if the repo must stay private.
- **Render keep-warm** via the existing UptimeRobot ping at `/health` — this now also keeps the D-055 webhook endpoint responsive, since both routes live on the same service.
- **Supabase keepalive** folded into the existing `keepalive.yml` — one workflow, two jobs (ping GitHub, `SELECT 1` against Supabase), no new mechanism.
- **LLM provider rate limits** under real concurrent fan-out are unverified (D-054) — worth a real load test before assuming the free tier holds, not an assumption.

**Cost model, derived from this system's own cadence (not a generic estimate):** the §5.4 Step 15 cron fires roughly 75–80 times per trading day (four catch-up runs at market open, then every 5 minutes across the 09:30–15:25 IST window, plus two closing runs) — call it **~1,650 cycle-runs/month** at 22 trading days. From that:
- **GitHub Actions minutes:** most cycles short-circuit early (calendar gate, dead-zone abort, no strategy match, dedup suppression) and finish in well under a minute; only a cycle that reaches a PROCEED verdict pays for a Dhan/NSE round-trip plus an LLM call, likely 1–2 minutes. A blended estimate of ~45 seconds/cycle puts scheduled runs alone around **1,200 minutes/month** — a meaningful fraction of a 2,000-minute private-repo budget before counting token-refresh, weekly-friction, keepalive, or manual `workflow_dispatch` runs. This is the concrete number behind D-033's existing recommendation to go public if there's no code-sensitivity reason not to. **The `tests.yml` CI workflow (§5.4 Step 15a) adds to this same budget** — during active development, dozens of pushes in a week at a few minutes each (dependency install plus the test suite) is a real, if bounded, addition, not free just because it's "only CI." It doesn't change the recommendation, it reinforces it: on a private repo, active development weeks and the trading cron's own budget are drawing from the same 2,000-minute pool.
- **LLM calls:** only a cycle that clears risk math to PROCEED calls the Analyst — with two strategies and typical signal frequency, that's realistically low single digits per day, not per cycle. Even a generous estimate keeps monthly Gemini Flash calls in the low hundreds, well inside any free tier's per-day and per-month request caps.
- **Database rows:** `cycle_summaries` writes one row per cycle regardless of outcome (~1,650 rows/month); `signals` writes only on a dispatch attempt, so far fewer. Row and storage volume at this scale is trivial against any Postgres free tier's storage cap.
- **The actual risk isn't volume, it's rate limits and exact current caps** — Dhan's specific rate limit and each provider's current free-tier thresholds (GitHub, Supabase, Google AI Studio) change over time and should be checked against their current published numbers before relying on this math, not assumed from memory. The point of doing this calculation isn't the precise figures — it's confirming the *order of magnitude* is comfortably inside free-tier territory for the ~2-month, ~50-trades-per-strategy validation window, so "free tier" and "statistically meaningful validation" aren't actually in tension for Phase 0–5. Re-run this math before Phase 6 if trade volume or symbol count grows.

---

### Appendix I — Full-Build Architecture: What's Different, and Why You Might Want It

Everything in this appendix is **optional, deferred, and fully preserved** — nothing described here was deleted from the project's history. It's consolidated in one place instead of interleaved through §2–§6 so the main build stays readable. Every component below is gated by Appendix J's promotion criteria — none of it should be added just because it exists.

| Component | What it changes vs. this build | What it buys you | What it costs |
|---|---|---|---|
| **Verifier LLM** (Groq, PROCEED/BLOCK gate after the Analyst) | `risk_math_node`'s direct PROCEED/BLOCK decision is instead routed through a second LLM call that can override it | A second, independent check on the math — useful if you ever suspect the deterministic gating itself needs an adversarial review, or you're handing signals to someone other than yourself | An extra LLM call per cycle, a distributed lock to rate-limit it, a new failure mode (lock unavailable → synthetic BLOCK), and a second thing that can silently drift out of sync with the math it's supposedly checking |
| **Second LLM provider** (Z.ai, Analyst fallback) | Gemini failure produces an AI-written fallback message instead of a template | Narrative quality preserved even during a Gemini outage | A second API key, a second distributed lock, a second failure mode, all to avoid an occasionally-plainer Telegram message |
| **DB-backed strategy registry + AST review pipeline** | Strategies load dynamically from a `strategies` table instead of a hardcoded list; uploads go through an AST security scan before activation | Lets someone other than the maintainer contribute a strategy safely | An entire class of bug (DB says active, code disagrees) that this build's hardcoded list makes structurally impossible; real engineering and review overhead for a problem a solo developer doesn't have |
| **RAG / memory pipeline** (`ingest.py`, `recall.py`, `pgvector`) | The Analyst retrieves relevant knowledge-base chunks at call time instead of reading a static prompt block | Knowledge updates propagate without a code deploy; scales better if the knowledge base grows large or changes often | An embedding pipeline, a vector-search dependency, and a real bug class (glob mismatches, unwired `recall()` calls) that a 2,000-word static block simply cannot have |
| **PRS quiz UI** (3-question Telegram flow with inline keyboards) | Replaces the single `/ready` toggle with a richer, scored self-assessment | Slightly more nuanced daily readiness signal | A UI with the exact broken-keyboard bug class this document originally found (D-004) — more surface area for a check that, for one operator, a boolean already covers |
| **Netlify inbound webhook** (ratings, PRS callbacks) | A second inbound channel, separate from Render's D-055 endpoint, for behavioral-rating prompts and PRS callbacks | Needed if the PRS quiz or automated outcome-rating prompts are added | A second deployment to maintain, secured and monitored independently of the one this build already has |
| **Distributed Postgres locks for LLM calls** | Rate-limits concurrent calls to a second LLM provider or a Verifier | Prevents two LLM calls racing on the same budget counter | Only meaningful once there's a second provider or a Verifier to protect against — otherwise pure overhead, per the amended D-T9 |

**Database additions if any of the above are built** (not part of this build's Core or Extended tiers): `strategies`, `strategy_configs` (with `config_history JSONB` absorbing what would otherwise be a separate changelog table — a real consolidation, don't build a fourth table for this), `knowledge_chunks` (requires `pgvector`), `infrastructure_locks`.

### Appendix J — Promotion Playbook: Track-S-to-Expanded-Architecture Criteria

No component in Appendix I gets added because it "might help." Each has its own concrete trigger, evaluated independently, after Phase 5's ~50-trades-per-strategy bar is already met.

| Component | Trigger — add it only when... |
|---|---|
| Verifier LLM | You have a specific, evidenced case where the deterministic risk math produced a signal you believe was wrong for a reason the math itself couldn't have caught — not "it might catch something someday." As a concrete backstop: you've manually reviewed the closed trades behind at least 20 PROCEED signals and disagree with the math's call on more than 20% of them, *and* you can articulate what a second check would have caught that a parameter fix to the existing math couldn't. |
| Second LLM provider | Gemini's actual observed downtime (measured, not assumed) has cost you real, counted missed-narrative cycles over at least one full month of live shadow running — concretely, a failure rate above roughly 5% of Analyst calls over that month, logged in `cycle_summaries.errors`, not estimated after the fact. |
| DB-backed strategy registry + review pipeline | A second person — not you — is going to contribute a strategy. Until that's true, this entire component has no job to do. |
| RAG / memory pipeline | The static prompt block has been edited more than roughly once a week for a month because the knowledge base itself is changing that fast — meaning the manual-update cost has become the actual bottleneck. |
| PRS quiz UI | You've used `/ready` for at least a month and have a specific complaint that a boolean can't express — not a hypothetical one. |
| Netlify inbound webhook | You've added the PRS quiz UI or automated rating prompts (above) and they need a channel — don't add the channel first and look for a use for it after. |
| Distributed LLM locks | You've added a second provider or the Verifier (above). On their own, they have nothing to protect. |

Each promotion is a one-line addition to §1.3's changelog pattern: what was added, the evidence that triggered it, the date. Nothing here is ever decided by an AI agent unattended — per §0's agent instruction, adding anything from this appendix requires a human decision recorded in the document itself.

---

### Appendix K — Component-by-Component Implementation & Verification Guide *(NEW)*

This appendix answers one question per component: **how do you actually write this, and how do you know when it's really done** — not "the file exists" done, but "I would bet real money the logic is correct" done. It follows §5.4's build order exactly, so build and verify happen in the same sequence, component by component, rather than as two separate passes. Appendix G tells you *what* each node touches; this tells you *how to build and prove* each one.

**How to read each entry:** *Target* is the one-sentence definition of done. *Build* is the concrete shape of the code — not full source, but specific enough that two different developers (or two different agent sessions) would produce functionally identical modules. *Mechanism* is how it actually behaves at runtime, in plain terms. *Proof* is the specific, runnable check that lets you say "100% working" about that component and mean it — not a vibe, a command.

---

**1 — `src/config/settings.py`, `src/config/constants.py`**
- **Target:** every tunable number in this document (lot sizes, Kelly cap, R:R floor, stale-data window, dedup horizon, drawdown mode) lives in exactly one of these two files, never hardcoded inline elsewhere.
- **Build:** `settings.py` is a `pydantic-settings` `BaseSettings` subclass reading from env vars with safe defaults (mirrors Appendix D exactly — if a var isn't in both places, that's a bug). `constants.py` is plain module-level constants (`LOT_SIZES`, `KELLY_CAP_PCT = 0.02`, `RR_FLOOR = 2.0`, `STALE_DATA_MINUTES = 15`, `DEDUP_HORIZON_MINUTES = 60`) — no class needed, these never change at runtime.
- **Mechanism:** imported once at process start; every other module reads from here instead of re-declaring a number. This is §2.0 principle 3 (one fact, one source) applied to configuration itself.
- **Proof:** `grep -rn "0\.02\|65\|30" src/ --include=*.py | grep -v "config\|test"` should turn up nothing that looks like a smuggled-in magic number matching a value that belongs in `constants.py`. Not a perfect test, but a real smell check.

**2 — `src/math/pricing.py`**
- **Target:** every formula in §2.4 exists as a pure function with no side effects, no DB calls, no imports beyond stdlib and maybe `math`.
- **Build:** one function per formula (`expected_value`, `kelly_fraction`, `transaction_cost`, `net_gex`, `pcr`, plus the Layer A/B direction formulas if not colocated with their layer modules). Every function signature matches §2.4's verbatim spec exactly — no renamed parameters, no reordered arguments, since this is the one section of the document explicitly marked "locked, unchanged since v9."
- **Mechanism:** called synchronously, in-process, by the scoring and risk modules. Zero network, zero DB — this is what makes it testable without mocks.
- **Proof:** `pytest tests/test_pricing.py -q` with **every** assertion using `pytest.approx(exact_value)` against a hand-calculated expected result for at least one real-number example per formula (pre-empts D-018 — a `> 0` assertion proves nothing). Target 100% line coverage on this file specifically; it's small, pure, and there's no excuse not to.

**3 — `src/scoring/layer_a.py`, `layer_b.py`, `layer_c.py`, `direction_scorer.py`, `structure_gate.py`**
- **Target:** deterministic scoring — same inputs always produce the same score, zero LLM imports anywhere in this directory (a `grep -rn "llm\|gemini\|groq" src/scoring/` should return nothing, ever).
- **Build:** each `score_layer_x()` function takes parsed market data and returns a small typed result (`LayerAScore`, etc. — Pydantic models, not dicts, same reasoning as D-001's fix). `direction_scorer.py`'s `compute_direction_score()` combines all three per the exact weighted-average formula in §2.4, including the pre-score overrides (event proximity, expiry-day window, GEX flip zone → force neutral 3) and the expiry-day force-bearish override (`expiry_score >= 5` → force 1).
- **Mechanism:** GEX is read before PCR, always (§2.4) — this ordering is load-bearing, not stylistic, because PCR's interpretation literally depends on GEX's sign. Get the order wrong and the formula produces a different number from the same inputs.
- **Proof:** `pytest tests/test_direction_scorer.py -q` covering at minimum: negative GEX + rising PCR (should be maximally bearish), positive GEX + rising PCR (should be capped bullish), the 2.0–4.0 dead-zone boundary values exactly (1.99 vs 2.0 vs 4.0 vs 4.01 — off-by-one on an inclusive boundary is exactly the kind of bug that hides for months), and the expiry force-bearish override firing correctly. If you can't state the expected output for a given input by hand before running the test, you don't understand the formula well enough to have implemented it yet — go back to §2.4.

**4 — `src/data/market_snapshot.py` (the D-001 fix)**
- **Target:** `fetch_and_score_market_data(symbol) -> ScoredMarketContext` — the single most important function in the codebase, since its absence is D-001, the highest-priority item in the whole ledger.
- **Build:** (1) fetch spot + chain from `dhan_client.py` with `nse_fetcher.py` as fallback, (2) fetch VIX, (3) fetch FII data via `nse_fetcher.fetch_participant_oi()`, (4) extract the *exchange's own payload timestamp* and compare against `STALE_DATA_MINUTES` — abort with `STALE_DATA` before step 5 if it's exceeded (D-045; never use the runner's clock here, see D-001's clock-sync rule), (5) call the three `score_layer_x()` functions, (6) construct and return a `ScoredMarketContext` Pydantic model with `extra="forbid"` — if any required field is missing from what steps 1–3 produced, this raises immediately instead of silently defaulting.
- **A genuinely different failure hides inside step 3, worth naming explicitly:** Layer B's `raw = 0.0` is both its legitimate neutral reading *and* its fallback when the FII fetch fails outright — nothing currently distinguishes "the market genuinely has no FII directional lean today" from "the participant-OI download failed and we silently defaulted." Both currently produce the identical value flowing into the exact same weighted-average formula, which is precisely the "looks like it's working" failure class §2.7 warns about, just living in a scoring input instead of the pipeline's control flow. The fix costs nothing new: when step 3 falls back to the default because the fetch itself failed (not because the computed ratio genuinely rounded to neutral), append one line to that cycle's `cycle_summaries.errors` JSONB array — e.g. `{"layer": "B", "reason": "fii_fetch_failed", "defaulted": true}` — reusing a field that's already in the Core schema rather than adding a `degraded_mode` flag or a new table. A human skimming `cycle_summaries` during §6.3's daily check can then tell "FII was neutral" from "FII was missing" at a glance, without this build needing Track F's separate `data_verification_node`.
- **Mechanism:** called once per symbol per cycle, before the dead-zone abort. This is the function whose *absence* the entire D-001 finding is about — if you're building from zero, this existing means D-001 structurally cannot recur, by construction.
- **Proof:** the regression test that matters most in this entire document: mock a realistic Dhan response, call this function, assert `result.layer_a` and `result.layer_b` are populated with values that trace back to the mocked input (not silently `None`, not the neutral defaults). Then mock a response with a stale timestamp and assert it raises/returns `STALE_DATA` before any scoring runs. Then mock a response missing a required field and assert `ValidationError`, not a partial object. Then mock a *failed* FII fetch specifically (not just an absent one) and confirm the resulting `cycle_summaries.errors` entry, distinct from a genuinely-computed neutral reading. Four tests, maybe 55 lines total, and they are the single cheapest insurance this project can buy against ever reproducing D-001 or its quieter cousin.

**5 — `src/data/dhan_client.py`, `nse_fetcher.py`, `instrument_resolver.py`, `event_calendar.py`, `ohlc_writer.py`**
- **Target:** every external HTTP call in this layer is wrapped in a timeout, a retry-with-backoff, and a circuit breaker (§2.0 principle 7 — no exceptions, including for calls that "probably won't fail").
- **Build:** `dhan_client.py` exposes read-only methods only (no order placement, ever, by permanent design per §2.1) with a Postgres-backed circuit breaker (3 failures → trip, 5 min cooldown) and a 10-second timeout, 2-retry cap on every request (§2.0 principle 7). **A trip sends a Telegram alert** — this detail existed in the original component audit and is easy to lose in a rewrite, but it matters: without it, a sustained Dhan/NSE outage produces a silent string of `DEGRADED` cycles that nobody notices until they happen to check `cycle_summaries` by hand. One alert on trip, not one per subsequent blocked cycle (that would just be alert spam layered on top of an outage you already know about). `nse_fetcher.py` classifies a 403/HTML response as `NSE_BLOCKED`, distinct from an empty-but-200 `NSE_EMPTY` response (D-047) — this distinction is what lets the circuit breaker and Dhan-fallback behave correctly instead of treating a block as "no data today." `ohlc_writer.py` upserts on `(symbol, interval, candle_timestamp)` conflict — do nothing, and can be deferred until automated outcome sampling is actually built (D-007). **Memory hygiene:** an option chain payload can carry dozens of strikes' worth of JSON; extract only the specific values §2.4's math actually needs (GEX, PCR, spot, VIX) into the typed `ScoredMarketContext` and let the raw response fall out of scope immediately — never hold the full raw chain in `AxisState` or log it wholesale. This matters more on a free-tier host with a real RAM ceiling than it would on a beefy server, but it's good hygiene regardless of where this runs.
- **Mechanism:** `nse_fetcher` tries NSE first, falls back to Dhan bidirectionally on failure; the circuit breaker sits in front of both so a systemic outage doesn't retry-storm either provider.
- **Proof:** mock a 403 response and a mock HTML error page separately, confirm each is classified as `NSE_BLOCKED` and triggers Dhan fallback, not logged as ambiguous empty data. Trip the circuit breaker manually (three forced failures) and confirm the fourth call short-circuits without hitting the network at all.

**6 — `src/strategies/base.py`, `gvof.py`, `wyckoff_mean_reversion.py`**
- **Target:** both strategies registered in a single hardcoded, version-controlled list from the first commit that defines it — this class of bug (D-012) should be structurally impossible to reintroduce, not just fixed once.
- **Build:** `base.py` defines the `BaseStrategy` ABC with one required method, `check_conditions(state) -> dict` returning at minimum `{"passed": bool, ...entry/stop/target details if passed}`. `gvof.py` and `wyckoff_mean_reversion.py` each implement it per their respective entry-condition checklists (§6 of the original component report — time gates, structure confirmation, GEX/direction resolution, IB range, spring/upthrust XOR, etc.).
- **Mechanism:** `strategy_activation_node` iterates `STRATEGIES = [GVOFStrategy(), WyckoffMeanReversionStrategy()]` in order; first one whose `check_conditions()` passes wins. No database row anywhere claims a strategy is active — the list *is* the claim.
- **A trade-off worth naming rather than leaving silent:** "first match wins" means that on the rare cycle where *both* strategies' conditions would independently pass, only the first one in the list ever gets evaluated downstream — the second's signal is silently discarded that cycle, not logged, not counted. GVOF (trend/cascade or Fibonacci-zone reversal) and Wyckoff (spring/upthrust mean-reversion) target different enough market regimes that simultaneous qualification should be genuinely rare — this is accepted as a low-impact trade-off for this build's simplicity (evaluating and dispatching both independently would mean threading a list of candidate signals through nodes 5–9 instead of a single one, real added structural complexity for a rare edge case). **The trigger to revisit, per Appendix J's own evidence-gated philosophy:** if Phase 5's sample counts show one strategy's trade count growing suspiciously slower than the other's in a way that correlates with the faster one firing on the same days, that's the concrete signal this trade-off is actually costing something — not a hunch, a queryable pattern in `paper_trades` grouped by date and `strategy_slug`.
- **Proof:** `grep -n "STRATEGIES" src/graph/nodes.py` shows both classes, every time, forever (add this grep to CI if you want it enforced automatically rather than just documented). Per-strategy unit tests confirm each fires on its known-good synthetic setup and stays silent on a setup missing exactly one required condition.

**7 — `src/llm/router.py`, `json_extractor.py`**
- **Target:** one call path to Gemini for the Analyst; on failure, a templated fallback message — never a crashed cycle, never a second provider by default (D-T10).
- **Build:** `call_llm_router("analyst", state)` calls Gemini directly (no distributed lock needed — see the race-condition note under step 12 below); on exception or timeout, catch it and return a plain-text templated summary built from the same state fields the narrative would have used. `json_extractor.py` strips markdown fences and trailing commas before parsing any LLM JSON output.
- **Mechanism:** the Analyst only ever explains; it never gates PROCEED/BLOCK (§2.1). A degraded Gemini means plainer prose, never a blocked or crashed cycle.
- **Proof:** force a Gemini exception in a test double and confirm the cycle completes with a templated message and `alert_sent = true`, not an unhandled exception.

**8 — `src/risk/risk_manager.py`, `src/journal/position_sizer.py`**
- **Target:** PROCEED/BLOCK decided directly by pure Python — no LLM in this call path, ever, by design (§2.1).
- **Build:** `check_daily_drawdown()` implements the OFF/SHADOW/ENFORCE modes exactly as specified (SHADOW logs and alerts but always returns "allow"; only ENFORCE actually blocks) — and, for this build specifically, the drawdown check is **account-wide, not per-symbol or per-strategy**: one capital pool, one operator, one daily P&L number, checked once regardless of which symbol or strategy produced the day's trades. (Segmenting risk per symbol/strategy is exactly what `virtual_portfolios` — Extended tier, Appendix I — is for, if that's ever actually needed; don't half-implement segmentation by accident here.) `validate_asymmetry()` blocks anything under the 2.0x R:R floor. `position_sizer.py`'s `calculate_position()` uses flat 1% until 30 samples exist, then half-Kelly capped at 2%, whichever is smaller — **and the 30-sample count, along with every Kelly input (win rate, avg gain, avg loss), must be computed per `strategy_slug`, never pooled across GVOF and Wyckoff.** They have different entry logic and almost certainly different win-rate/payoff shapes; a pooled Kelly calculation would size both strategies off a blended statistic that describes neither one correctly. This is the same "one fact, one source" discipline (§2.0 principle 3) applied to statistics instead of state — each strategy's sizing is its own fact.
- **Mechanism:** these functions are called synchronously inside `risk_math_node`; their combined output is the PROCEED/BLOCK verdict — nothing downstream re-derives or double-checks it with an LLM.
- **Proof:** table-driven unit tests: R:R exactly at 2.0 (should pass), 1.99 (should block), EV exactly 0 (document and test whichever side of the boundary you choose — this is a real ambiguity worth resolving once, in code, rather than leaving implicit), Kelly with fewer than 30 samples (should use flat 1% regardless of what Kelly would compute).

**9 — `src/delivery/telegram_formatter.py`, `alert_builder.py`**
- **Target:** every outbound message is MarkdownV2-sanitized and rate-limited; the D-048 persistence write happens *before* the cycle can end, not as an afterthought.
- **Build:** `alert_builder.py` assembles the 7-section message from `AxisState`. `telegram_formatter.py`'s `send_telegram_alert()` sanitizes, respects a 1.05s minimum send interval, and on any non-200 response writes `telegram_sent = false` to the `signals` row for that cycle — synchronously, before returning, not fire-and-forget.
- **Mechanism:** this is the one place in the pipeline where "the code ran successfully" and "the human was actually notified" are different facts, and the document treats them as different facts on purpose (§2.7 rule 4).
- **Proof:** mock a non-200 Telegram response, confirm the `signals` row persists with `telegram_sent = false` synchronously (check the row exists *before* the function returns, not just eventually), then confirm `/resend` (component 12 below) successfully delivers it.

**10 — `src/scheduling/calendar_gate.py`, `lock_manager.py`, `no_trade_summary.py`**
- **Target:** `is_system_paused()` fails closed on any read failure — this is the one gate in the whole system where "more consistency with the other gates" and "more safety" are the same fix (D-T8).
- **Build:** `is_market_open()` checks weekday + holiday calendar + the 09:15–15:30 IST window. `is_system_paused()` reads `system_paused` and `trader_session_state`; **any exception during either read returns `True` (paused/blocked)**, never `False` — this must be the literal default of the `except` branch, not an oversight to catch in testing. `no_trade_summary.py` gains one extra responsibility beyond its original scope: the D-050 EOD `active_position` reset, riding the existing 15:30 IST schedule rather than a new cron.
- **Mechanism:** `calendar_gate_node` is the very first node in every cycle; if this fails closed correctly, nothing downstream matters when it should be paused, because nothing downstream runs.
- **Proof:** the one test that actually matters here: monkeypatch the Supabase client to raise on the `system_paused` read, call `is_system_paused()`, assert it returns `True`. Do the same for a `trader_session_state` read failure. If either of these returns `False` on a read exception, this component is not done, no matter how much else works.

**11 — `src/graph/state.py`**
- **Target:** the complete field set for `AxisState` declared up front, `extra="forbid"`, before any node writes to an undeclared key — this pre-empts D-013 by construction rather than catching it in review.
- **Build:** every field from §2.6 as `Optional[...]`, no exceptions; if a new field is needed later, it's added here first, in the same PR as the code that writes it (§2.0 principle 6, applied to the state contract specifically, not just the database).
- **Mechanism:** Pydantic raises immediately if any node returns a key not in this model — a fast, loud failure instead of a silently-stripped field.
- **Proof:** a five-line contract test: construct `AxisState` with an undeclared kwarg, assert it raises `ValidationError`. Trivial to write, and it's the entire fix for a bug class (D-013) that otherwise only shows up as "why did this field silently vanish" weeks later.

**12 — `src/graph/nodes.py`, `graph.py`**
- **Target:** `from src.graph.graph import graph` imports cleanly with zero exceptions — the single most important gate in the whole build (§5.4 Step 12's own words).
- **Build:** `import logging; _log = logging.getLogger("axis.nodes")` at the very top of `nodes.py`, before a single `_log.error(...)` call is written anywhere (pre-empts D-005 by ordering, not by remembering). All eight in-graph nodes (§2.3, steps 0–7) implemented per their Rosetta Stone row (Appendix G) exactly — each returns only the keys it changed. `graph.py`'s `build_graph()` wires them in the exact order from §2.3; `graph = build_graph()` at module import time means any node's import error cascades to "the whole module fails to import," which is why this step's gate is a bare import statement, not a functional test.
- **Mechanism:** this is the load-bearing wiring for everything above it — a correct node in isolation is worthless if `graph.py` wires it to the wrong neighbor or under the wrong key name.
- **Proof:** `python -c "from src.graph.graph import graph; print('GRAPH IMPORTS CLEANLY')"` with zero traceback. Then `pytest tests/test_axis_graph.py -q` tracing one full synthetic cycle end-to-end and asserting the state object at the end contains every field a real cycle would populate.

**13 — `main.py`**
- **Target:** `run_all_symbols_cycle()` runs NIFTY then BankNifty strictly sequentially, applies the cross-symbol correlation exactly once at the orchestrator level (§2.3 step 8, pre-empting D-008 by construction — there is no per-node copy of this logic anywhere else to accidentally duplicate), writes one `cycle_summaries` row per cycle regardless of outcome (pre-empting D-037), and has `_run_cli()` actually wired to `__main__` (pre-empting D-009 — a crash that notifies nobody is worse than the crash itself).
- **Build:** the correlation step reads both symbols' just-completed verdicts from memory (not a re-query — see Appendix G's corrected row for this), applies the 50% haircut on same-direction PROCEED verdicts, and writes exactly one `macro_regime_flags` row. The `cycle_summaries` write is wrapped so it happens even if the cycle itself throws — a `try/finally`, not a `try/except` that might swallow the write along with the error.
- **Mechanism:** this file is the only place cross-symbol logic is permitted to exist, by design — if you're inheriting the old repo instead of building from zero, this is exactly where D-008's inheriting-repo warning applies (delete the old `verifier_node` copy first).
- **Proof:** trace one full two-symbol cycle in staging, force a same-direction result on both, count `macro_regime_flags` rows — expect exactly one. Separately, force an exception mid-cycle and confirm a `cycle_summaries` row still lands with `status = 'CRASH'`.

**14 — `server.py`, `src/commands/router.py`, `handlers.py`**
- **Target:** one Render FastAPI service serving both `/health` and `POST /telegram/webhook` (D-055) — not a subprocess spawn at import time (D-016), not a second deployment.
- **Build:** `FastAPI(docs_url=None, redoc_url=None, openapi_url=None)` — this service is reachable on the open internet with only Telegram's secret-token header standing between it and the world; there's no reason to also publish an auto-generated API map of its routes. The webhook route, in this exact order, never reordered: (1) validate `X-Telegram-Bot-Api-Secret-Token`, 401 on mismatch, stop; (2) check the incoming `update_id` against `telegram_updates_processed`, no-op with 200 if already seen, stop; (3) parse the command text and dispatch to `/ready`, `/record`, `/close`, or `/resend`; (4) always 200 once past step 1. `/record`'s handler checks `active_position` for that symbol first and rejects if already `OPEN` (D-046) — and separately catches a primary-key violation on the insert itself as the structural backstop against the race between this always-on service and the GH Actions cycle's `position_state_check_node` touching the same table (see D-050's race-condition note).
- **Mechanism:** this is the only always-available process in the system outside the 5-minute cycle; everything it does must be safe to call at any time, including twice in a row by accident.
- **Proof:** the three-call sequence in Appendix A's D-055 integrity test — wrong token (401), fresh `update_id` (200, effect applied), repeated `update_id` (200, no additional effect). Then fire two `/record` calls for the same symbol back-to-back and confirm the second is rejected either by the pre-check or by a caught primary-key violation — either path should produce the same user-facing message. Separately, confirm `/docs` and `/openapi.json` both 404.

**15 — `.github/workflows/main_pipeline.yml`**
- **Target:** weekday-restricted cron (pre-empts D-032) with a `concurrency:` group from the first commit that defines it (pre-empts D-051), not added later as an afterthought.
- **Build:** the exact YAML from §5.4 Step 15 — `cancel-in-progress: false`, three cron entries covering the catch-up window, the main trading window, and the closing window, all restricted to `1-5`. Add `timeout-minutes: 5` at the job level — comfortably above what a healthy cycle needs (per Appendix H's cost math) and a hard backstop against a genuinely hung job silently burning the minutes budget for the rest of the month.
- **Mechanism:** verified against GitHub's own documentation (D-T9): at most one run "in progress" and one "pending" per group, ever — this setting cannot produce two simultaneous executions, only a queued run that may itself get evicted by a newer trigger if cycles run long.
- **Proof:** `grep -n "concurrency:\|timeout-minutes:" .github/workflows/main_pipeline.yml`, then trigger two overlapping `workflow_dispatch` runs manually and confirm in the Actions UI that the second waits (or gets evicted if a third arrives) rather than running side-by-side with the first.

**16 — Migrations (`migrations/001_core_tables.sql`)**
- **Target:** all seven Core-tier tables exist before the first cycle ever runs — `signals`, `active_position`, `system_paused`, `telegram_updates_processed`, `trader_session_state`, `cycle_summaries`, `macro_regime_flags` (D-011).
- **Build:** the exact DDL in Appendix C, run against a disposable Supabase branch first, never production first. Seed `system_paused` with `is_paused = true` explicitly — a fresh migration leaves the system **paused** by design (§5.2 step 5); flipping it to `false` is a deliberate, separate action once §6.1's pre-deploy checklist is actually complete, never something the migration itself does.
- **Mechanism:** every table here is either read by `calendar_gate_node` (safety: `system_paused`, `trader_session_state`), written by the inbound endpoint (interaction: `telegram_updates_processed`, `active_position`, `trader_session_state`), or written by the orchestrator (`cycle_summaries` for observability, `macro_regime_flags` for the correlation trail) — nothing in Core tier is speculative.
- **Proof:** all seven `SELECT count(*) FROM <table>;` queries from Appendix A's D-011 block return without error against the staging branch before any application code runs against it.

**17 — Telegram webhook registration**
- **Target:** Telegram's `setWebhook` API points at the live Render URL's `/telegram/webhook` route, confirmed via `getWebhookInfo`.
- **Build:** a one-time `curl` call to `https://api.telegram.org/bot<TOKEN>/setWebhook?url=<render-url>/telegram/webhook&secret_token=<TELEGRAM_WEBHOOK_SECRET>`.
- **Mechanism:** from this point on, every message sent to the bot arrives as a POST to the Render service — there is no polling loop anywhere in this design (Track S never needed one, since the webhook covers it).
- **Proof:** `getWebhookInfo` shows the correct URL with zero `last_error_message`; send `/ready` from Telegram itself (not curl) and confirm `trader_session_state` updates within a few seconds.

**18 — Tests (`tests/`)**
- **Target:** every component above has its proof written as an actual test file, not just described in this document — Appendix E's categorization is the map, this is the territory.
- **Build:** written alongside each component as it's built (§5.4's own instruction), not batched at the end. Pure-math tests need no mocks and should run in milliseconds; anything touching Supabase or Dhan gets a mock; the full-graph tests run last because they're slowest and least isolating.
- **Mechanism:** `pytest -q` as the final gate of the entire runbook is only meaningful if the tests it's running are the ones described component-by-component above, not a thin placeholder suite.
- **Proof, of the whole system, stated plainly:** there is no single command that proves "100% working" for a system whose actual product is a statistically honest EV number — that proof is Phase 5's SQL gate (§4.4), not a test suite. What this appendix's per-component proofs buy you is narrower and more honest: confidence that the *plumbing* is correct before you spend two months and fifty real trades finding out whether the *strategy* is. Don't confuse the two kinds of "working" — a green test suite proves the pipe doesn't leak; it says nothing about whether what's flowing through it is profitable.

**19 — `.github/workflows/tests.yml` (CI, §5.4 Step 15a)**
- **Target:** every push and PR to `main` runs the full test suite automatically — component 18's tests only earn their keep if something actually forces them to run before code lands, not just when someone remembers to type `pytest`.
- **Build:** the exact YAML from §5.4 Step 15a — checkout, Python 3.12 with pip caching, install, `pytest --ignore=tests/smoke -q`, all under a `timeout-minutes: 10` backstop so a hung test run can't quietly consume the shared minutes budget (Appendix H) the same way an unbounded trading cycle could. Its own `concurrency` group cancels an in-progress run when a newer push arrives on the same branch — deliberately `cancel-in-progress: true`, unlike `main_pipeline.yml`'s `false`, because a superseded test run has zero value the moment a newer commit exists, whereas a trading cycle mid-dispatch is exactly the thing worth never interrupting (D-T9). Without this, several rapid pushes to one branch queue up redundant full test runs and burn real minutes against the same shared budget for no benefit.
- **Mechanism:** entirely separate from `main_pipeline.yml` — different trigger (`push`/`pull_request` vs. `schedule`), different job, its own concurrency group (not shared with the trading cron's `axis-trading-cycle` group), because there's no reason a CI run and a trading cycle should ever block each other, even though both now use the same *mechanism* for a deliberately opposite reason.
- **Proof:** push a deliberately failing test to a branch, open a PR, confirm the workflow run shows red before merge — not after a live cycle fails because of it. Separately: push twice in quick succession to the same branch, confirm the Actions UI shows the first run cancelled, not queued.

---

### Appendix L — System Architecture, Drawn in Plain Text

No diagramming tool, no images — just the shape of the system as text, so it's readable in a terminal, a diff, or a plain-text editor exactly as easily as anywhere else.

```
================================================================================================
 AXIS -- FULL SYSTEM ARCHITECTURE (TEXT DIAGRAM)
================================================================================================

 EXTERNAL SERVICES (7, stacked reliability budget -- SS2.0 principle 5)
 ------------------------------------------------------------------------------------------------
  GitHub          GitHub Actions      Render                Supabase          Telegram
  (repo, secrets) (cron scheduler,    (FastAPI service:      (Postgres --      (Bot API --
                   5-min trigger)      /health + webhook)     system of record) human channel)

  Dhan / NSE (read-only market data)         Netlify (static dashboard only)
 ------------------------------------------------------------------------------------------------

                                              |
                                              | cron fires every 5 min, 09:10-15:35 IST, Mon-Fri
                                              | job-level timeout-minutes: 5
                                              | concurrency group "axis-trading-cycle":
                                              |   at most 1 run IN PROGRESS + 1 PENDING, ever (D-T9)
                                              v

 ================================================================================================
 |                       GITHUB ACTIONS RUNNER  ->  python main.py --all                        |
 |                                                                                                |
 |  FOR symbol IN [NIFTY, BANKNIFTY]  -- strictly sequential, never parallel (SS2.1)             |
 |  --------------------------------------------------------------------------------------------  |
 |  | 0. calendar_gate_node                                                                    |  |
 |  |    reads: system_paused, trader_session_state.is_ready                                   |  |
 |  |    FAIL-CLOSED: unreadable state OR is_ready=false (fresh row required daily) -> STOP     |  |
 |  |    (D-T8 / D-052 / D-004)                                                                 |  |
 |  |         |                                                                                 |  |
 |  |         v                                                                                 |  |
 |  | 1. lock_check_node -- thin backstop for manual/local runs only, effectively redundant     |  |
 |  |    during scheduled runs once D-051's concurrency group is confirmed (D-T9 amended)       |  |
 |  |         |                                                                                 |  |
 |  |         v                                                                                 |  |
 |  | 2. fetch_and_score_node  <-- calls src/data/market_snapshot.py, THE D-001 FIX -----+       |  |
 |  |    |  fetch spot+chain (Dhan, NSE fallback, NSE_BLOCKED vs NSE_EMPTY -- D-047)      |      |  |
 |  |    |  fetch VIX, fetch FII data                                                    |      |  |
 |  |    |  clock-sync: use the EXCHANGE payload's own timestamp, never the runner clock |      |  |
 |  |    |  abort STALE_DATA if > 15 min old, BEFORE scoring runs (D-045)                |      |  |
 |  |    |  run score_layer_a/b/c() -> return typed ScoredMarketContext (extra="forbid") |      |  |
 |  |    |  hard-abort if direction_score in [2.0, 4.0] dead zone (SS2.4)                |      |  |
 |  |    +----------------------------------------------------------------------------- +      |  |
 |  |         |                                                                                 |  |
 |  |         v                                                                                 |  |
 |  | 3. structure_gate_node  -- binary structure confirmation                                  |  |
 |  |         |                                                                                 |  |
 |  |         v                                                                                 |  |
 |  | 4. strategy_activation_node                                                               |  |
 |  |    STRATEGIES = [GVOFStrategy(), WyckoffMeanReversionStrategy()]                          |  |
 |  |    hardcoded, version-controlled list -- no DB registry, no drift possible (D-012, SS2.5) |  |
 |  |         |                                                                                 |  |
 |  |         v                                                                                 |  |
 |  | 5. risk_math_node  -- PURE PYTHON, zero LLM in this path, ever (SS2.1)                    |  |
 |  |    EV, half-Kelly (cap 2%), R:R >= 2.0x, daily drawdown mode  ->  PROCEED / BLOCK          |  |
 |  |         |                                                                                 |  |
 |  |         v                                                                                 |  |
 |  | 6. position_state_check_node                                                              |  |
 |  |    reads active_position (symbol = PRIMARY KEY, plain SELECT, no FOR UPDATE needed --     |  |
 |  |    read-only here, real write-race protection lives at the /record INSERT, see D-050)     |  |
 |  |    same-direction + already open -> suppress  |  opposite-direction -> exit warning        |  |
 |  |         |                                                                                 |  |
 |  |         v                                                                                 |  |
 |  | 7. dedup_node -- suppress identical (symbol, direction, strategy) within last 60 min       |  |
 |  --------------------------------------------------------------------------------------------  |
 |         |                                        (loop repeats once for BankNifty)             |
 |         v                                                                                      |
 |  8. cross_symbol_correlation_step -- ORCHESTRATOR LEVEL (main.py), NOT a graph node.            |
 |     Runs EXACTLY ONCE per cycle, in-memory (reads both symbols' just-completed verdicts,        |
 |     no DB re-query), after BOTH symbols' per-symbol loops finish.                               |
 |     Same-direction PROCEED on both -> 50% lot-size haircut -> writes exactly 1 row to           |
 |     macro_regime_flags (D-008 -- single location by construction, nothing to duplicate)         |
 |         |                                                                                       |
 |         v                                                                                       |
 |  9. analyst_and_dispatch_node  (per symbol, using correlation-adjusted sizing)                  |
 |     Gemini narrates (optional) --FAILS--> templated fallback message, no 2nd provider (D-T10)   |
 |     sends Telegram alert --non-200--> signals.telegram_sent=false, queued for /resend (D-048)   |
 |         |                                                                                       |
 |         v                                                                                       |
 |     writes 1 cycle_summaries row per cycle regardless of outcome -- OK / CRASH / DEGRADED       |
 |     (the heartbeat, D-037; a crash here still alerts via _run_cli() wired to __main__, D-009)   |
 ================================================================================================
                                              |
                                              v
                          +===================================+
                          |   SUPABASE (Postgres, system of    |
                          |   record)                          |
                          |   signals, active_position,        |
                          |   system_paused, cycle_summaries,   |
                          |   trader_session_state,             |
                          |   telegram_updates_processed        |
                          |   (Core tier -- 6 tables, built     |
                          |   before the first cycle ever runs) |
                          +===================================+
                                    ^                    ^
                                    |  reads/writes       |  reads/writes
                                    |                     |
 ================================================================================================
 |  RENDER -- always-on FastAPI service, a SEPARATE PROCESS from the GitHub Actions cron          |
 |                                                                                                 |
 |  GET  /health            <-- pinged every 5 min by UptimeRobot; NO DB query, keeps the         |
 |                               service warm and doubles as the uptime monitor                    |
 |                                                                                                 |
 |  POST /telegram/webhook  (D-055; docs_url/redoc_url/openapi_url all disabled -- no public       |
 |                            route map for an internet-reachable endpoint)                        |
 |    1. check X-Telegram-Bot-Api-Secret-Token  -> 401 if wrong, STOP                              |
 |    2. check update_id against telegram_updates_processed -> 200 no-op if already seen, STOP     |
 |    3. route the command:                                                                        |
 |         /ready   -> UPSERT trader_session_state.is_ready = true for TODAY (fresh daily opt-in;  |
 |                      silence on any given day already fails the whole system closed -- D-004)   |
 |         /record  -> check active_position first; OPEN already? reject. else INSERT paper_trades |
 |                      (a concurrent duplicate attempt hits the symbol PRIMARY KEY and is caught   |
 |                      and rejected the same friendly way -- D-046/D-050)                          |
 |         /close   -> DELETE active_position for that symbol                                       |
 |         /resend  -> re-send the latest signals row where telegram_sent = false (D-048)           |
 |    4. always 200 once authenticated                                                              |
 ================================================================================================
        ^                                                                                |
        |  operator sends commands by hand                                              |  alerts
        |                                                                                v
 +------------------------+                                              +---------------------------+
 |  TELEGRAM               | <--------------- 7-section alert message -- |      HUMAN OPERATOR        |
 |  (human's phone/app)    | ---------------- /ready /record /close ---->|  reads the alert, decides,  |
 |                          |    /resend, typed by the operator          |  places the trade MANUALLY  |
 +--------------------------+                                            |  in their own Dhan account  |
                                                                          +---------------------------+

        *** NO ORDER-PLACEMENT CODE PATH EXISTS ANYWHERE IN THIS SYSTEM, BY PERMANENT DESIGN (SS2.1).
            AXIS produces a signal. A human places every trade by hand. Always. ***

 ================================================================================================
 |  EOD CRON  (no_trade_summary, GitHub Actions, 15:30 IST daily)                                |
 |    -> sends a no-trade-day summary if nothing fired that day                                  |
 |    -> DELETE FROM active_position WHERE opened_at::date < current_date  (D-050's EOD reset,    |
 |       riding this existing cron rather than a new one -- SS2.0 principle 4)                    |
 ================================================================================================

 ================================================================================================
 |  NETLIFY  -- static dashboard only. Reads Supabase via SUPABASE_ANON_KEY (read-only).          |
 |  No service-role key ever ships client-side. Not in the trading loop at all.                   |
 ================================================================================================

--------------------------------------------------------------------------------------------------
 KEY TO THE FAILURE PHILOSOPHY THREADED THROUGH EVERY BOX ABOVE (SS2.0):
   - Safety gates (node 0, the kill switch, stale-data check) FAIL CLOSED on any doubt.
   - Enrichment (the Analyst LLM narrative) FAILS SOFT -- a plainer message, never a dead cycle.
   - Every fact lives in exactly one place (the strategy list, the is_ready column, the PK
     constraint on active_position) so nothing can silently drift out of sync with itself.
--------------------------------------------------------------------------------------------------
```

---

## Closing Note — Agent Handoff & How This Document Gets Maintained

**Scope boundary, stated once so it doesn't need re-litigating:** this document specifies AXIS, the trading system — not the tooling anyone chooses to use while building it. Proposals for external AI-agent-orchestration frameworks, multi-agent "swarm" coordination layers, Docker-based memory services, or similar build-process infrastructure are out of scope by design, the same way a bridge's engineering spec doesn't also specify which project-management software the construction crew uses. If a future contributor wants to use such tools to execute the build described here, that's an implementation choice made outside this spec, not a section to add to it — see §2.0 principle 8 and the reasoning already on record at D-T1 for the same judgment applied to a smaller version of this question (the trigger-mechanism proposal).

**Five kinds of edits are permitted going forward** (one more than v10, reflecting this edition's own restructuring):
1. **Flip a state.** Run something in Appendix A, get real output, change `S1-CITED` to `S1-CONFIRMED` (or `S4-CONFLICTED` if reality disagrees), and paste the output beneath the claim in §3.
2. **Append a row.** A genuinely new fact gets a new `D-XXX` ID at the end of its priority table. Nothing is ever deleted or renumbered.
3. **Override a closed Decision Tree.** Every tree in §4.1 has a stated default — overriding one is a one-time act: write the override and the evidence next to it.
4. **Correct an overclaim.** If a future pass finds this document stated something with more confidence than its sourcing supports, the fix is to soften the language and re-tag the confidence level — not to quietly delete the finding.
5. **Reorganize for clarity.** Content may move between the main body and an appendix (as Track F moved into Appendix I in this edition) without being deleted, provided every moved fact stays findable via §0's navigation table and nothing's meaning changes in the move. This is exactly what happened between v10 and v11.

**Executing this document with an agentic coding tool:** hand it this entire file plus repo access, with a prompt shaped like —

> "Run the Step Zero command and all of Appendix A. Paste the output into Appendix B. Then check §0's branching instruction: if D-001 is confirmed, build the Step-3 data-orchestration module from §5.4 before anything else. If not, work the P0 ledger in §4.3 in order, starting at D-004, using each row's exact remediation and verification text. Build only what §2–§6 describe — do not add anything from Appendix I unless its specific Appendix J trigger has already fired and a human has recorded it in §1.3. Do not modify §2 (Layer 1) — if the spec itself seems wrong, stop and flag it instead of changing code to match a different assumption."

That paragraph, plus this file, is a complete handoff from an empty terminal to a working, honestly-documented, appropriately-simple, reliably-built system.
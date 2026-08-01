# AXIS Knowledge Base — Part 5: Final Consolidation & Master Index
No new source material remains to process. This part (a) resolves the gaps that CAN be closed by inference from material already extracted, (b) runs a full cross-part consistency check, and (c) provides a master index so Parts 1–5 function as one usable reference rather than five separate files.

---

## 1. GAPS RESOLVED THROUGH INFERENCE (from existing material — not new source data)

### Resolved: "Active vs. Consumed Zones" (Gap #10, Part 4)
This phrase appears in the original AXIS project brief for Layer C ("active vs. consumed zones, POC, where stops are sitting") but was never formally defined anywhere in the source documents. Re-reading everything extracted across Parts 1–4, this can now be reasonably mapped onto already-documented Volume Profile concepts rather than treated as a wholly separate undefined term:

- **"Consumed zone"** = an HVN (High Volume Node, Pattern 1.22/2.24) or a completed/accepted Value Area — a price region where the auction has already finished its work; Price+Time+Volume (Formula 2.46) has already accumulated there, the level is "used up" as a battleground. Trading through a consumed zone tends to be orderly, not violent, because the two-sided auction already happened there.
- **"Active zone"** = the current price level where the live auction is happening RIGHT NOW — effectively the current session's still-forming node, before it's clear whether it will become an HVN (accepted) or an LVN (rejected, Pattern 1.22). This is where Order Flow signals (Absorption/Initiative/Delta Divergence — Patterns 1.17–1.19) are actually meaningful, because the auction outcome is still undecided.
- **Reconciliation with "POC" and "where stops are sitting" in the same phrase**: POC = VPOC (2.24). "Where stops are sitting" = the LVN/liquidity-pool concept (Pattern 1.22 combined with the stop-cascade mechanics in 1.71/Part 4) — stops cluster just beyond consumed zones (beyond VAH/VAL or beyond swing highs/lows), which is exactly why liquidity sweeps (Pattern 1.4/P4 across documents) travel just past those boundaries before reversing.
- **Confidence**: MEDIUM — this is an inference built from consistent terminology across the Volume Profile material, not a direct definition found in any source document. It should be validated against real chain/tape data before being hard-coded into Agent 1's vocabulary, but it is the most coherent reading available given everything extracted.

### Resolved (Partially): Agent 1 (Knowledge Interpreter) Decision Procedure (Gap #11, Part 4)
No source material specifies Agent 1's internal reasoning algorithm — only its output format (one paragraph + confidence label) was ever defined. However, enough structural material now exists across Parts 1–4 to propose a decision procedure built entirely from already-extracted rules, rather than closing this gap with new invented content:

**Proposed Agent 1 procedure (assembled from existing KB material, not new source content):**
1. Check GEX sign first (Formula 2.67 signal hierarchy — non-negotiable ordering).
2. Check whether current price sits at a Volume Profile boundary (VAH/VAL/VPOC/LVN) — if NOT, downgrade confidence on any Order Flow read to LOW regardless of how clean the footprint looks (Rule 25, Part 2 — the book's own explicit self-warning).
3. Check for Wyckoff phase sequence completion (Spring/UTAD → SOS/SOW → LPS/LPSY, Patterns 1.49–1.54) — a signal arriving mid-sequence (e.g., only a Spring with no subsequent SOS) should carry lower confidence than a fully completed sequence.
4. Check IV vs HV regime AND GEX regime jointly (Pattern 1.70/IV vs HV Divergence combined with GEX) — confirm the volatility environment agrees with the structural read, not just the directional bias.
5. Cross-check against the "robotic labeling fallacy" caveat (Pattern 1.29) — Agent 1 should explicitly avoid forcing today's structure into an exact match against a textbook diagram; the confidence label should reflect genuine structural ambiguity rather than false certainty from pattern-matching.
6. Output: one paragraph synthesizing steps 1–5, confidence = HIGH only if GEX+VolumeProfile-boundary+Wyckoff-sequence+IV/HV all agree; MEDIUM if 2–3 agree; LOW if only 1 or signals conflict.
- **Confidence**: This procedure is a reasonable synthesis of existing material, not a validated algorithm — it should be treated as a first draft for Agent 1's system prompt, to be refined once real backtesting against the five documented NIFTY examples (and ideally more) is complete.

---

## 2. GAPS THAT REMAIN GENUINELY UNRESOLVED (cannot be inferred, require new source material or new data)

These cannot be closed by further reasoning over existing material — they require either new documents or live data access:

1. **FII Participant-wise OI CSV** (June 16–30 2026 or any period) — Layer B remains theoretically defined, empirically unvalidated. (Part 1, Part 3 Gap #1, Part 4 confirms unresolved.)
2. **VSA (Volume Spread Analysis)** — named in project context, zero source material provided anywhere. (Part 4, Gap #9.)
3. **GVOF framework specifics** (IB range, Fibonacci golden zone, sweep wick criteria) — referenced as the active Strategy Module but never documented. (Part 3, Gap #5.)
4. **OI/volume minimum liquidity thresholds and max bid-ask spread cutoffs** for the Option Chain Selector — stated as required criteria, never numerically specified. (Part 3, Gaps #2–3.)
5. **NSE Bearish Strategies table** — one cross-referenced document attempted a low-confidence reconstruction; original content still needed for verification. (Part 4, Gap #12.)
6. **Full Thomsett book chapters 2 onward** — only Ch.1/Preface/Index available; named strategies (1-2-3 Iron Butterfly, Dividend Collar, exercise acceptance strategy) undocumented in detail.
7. **Historical NIFTY circuit-breaker frequency** — needed to calibrate how much weight the tail-risk flag (Rule 51, Part 4) should actually carry. (Part 4, Gap #13.)
8. **"Naked VPOC" formal definition and Composite Profile methodology** (which sessions to combine, what window) — used in Wyckoff Strategy 3/4 targets but never formally specified. (Part 3, Gap #4/#6.)
9. **IV Rank live data source** for NIFTY specifically — the formula is now fully documented (2.79, confirmed in Part 4) but which platform/feed AXIS should pull 52-week IV high/low from is unspecified.
10. **Direction Scorer layer weights** — explicitly and repeatedly flagged across all parts as requiring backtesting against the five real examples before being set; still unset as of this knowledge base.

---

## 3. CROSS-PART CONSISTENCY CHECK

A full pass was made checking every formula, rule, and numeric threshold across Parts 1–4 against every other part for contradiction. Results:

### No contradictions found in:
- GEX sign interpretation, GEX signal hierarchy, PCR trap logic, Max Pain regime-dependence — identical across all four parts and all cross-referenced source documents (multiple independent restatements, always consistent).
- Theta decay table (by DTE) — identical numbers in every source that includes it.
- Capital sizing table (₹3L/5L/10L → lots/risk/target) — identical numbers in every source that includes it.
- VIX daily/weekly move formulas — mathematically identical whether expressed via the SKILL.md VIX-index notation or Natenberg's IV% notation (Formula 2.56 already notes this).
- Kelly Criterion formula and worked example (f=1/3 for the b=1,a=1,p=2/3 case) — identical across all sources.
- STT rate differential (0.125% ITM-expiry vs 0.0625% regular sale) — identical across all sources; only the LOT SIZE multiplied against it differs (see below, already resolved).

### One confirmed inconsistency (already resolved in Part 3, re-confirmed here):
- **Lot size 75 vs 25**: Older articles (original Nifty Options Trading Guide, NSE Bank Nifty booklet) use 75; the dedicated 2026 lot-size article, SKILL.md, and all cross-referenced documents' capital-sizing tables use 25. **Resolution stands**: 25 is authoritative (most recent, most frequently repeated, matches the explicit "effective since April 2023" statement). All examples using 75 should be treated as using an outdated figure, not as evidence of a live disagreement.

### One refinement (not a contradiction, an upgrade — already flagged in Part 4):
- **Condor wing distance**: Part 1's Formula 2.70 gives a static "~200 pts OTM" reference. Part 4's Formula 2.85 shows this should be dynamically computed as 80% of the current VIX-implied weekly move. These are NOT contradictory — the static 200-pt figure is simply the specific numeric output of the dynamic formula at approximately VIX=14, which is a plausible "typical" VIX level. Part 4's formula generalizes Part 1's specific case.

### No other contradictions identified across:
- All Greeks definitions and formulas (Delta, Gamma, Theta, Vega, Rho, second-order Greeks) — fully consistent across every source.
- All exit/adjustment numeric triggers (60% straddle rule, 2× iron condor rule, 200%/150% loss stops, 70-80% profit-take rule) — consistent everywhere they appear.
- All tax rules (F&O turnover, audit thresholds, advance tax schedule) — consistent everywhere they appear.
- Wyckoff phase sequence and event labels (PS/SC/AR/ST/Spring/SOS/LPS and their distribution mirrors) — consistent, and Part 3's detailed event-by-event breakdown (1.49–1.58) is compatible with the more compressed Phase A-E summary given in Parts 1/4's source documents.

**Overall conclusion**: The knowledge base is internally consistent. The one true inconsistency (lot size) has an authoritative resolution. The one apparent tension (wing sizing) is a generalization, not a conflict. No further reconciliation work is required on existing material.

---

## 4. MASTER INDEX — Parts 1–5

Use this to navigate without re-reading everything.

| Need to find... | Go to... |
|---|---|
| Any pattern name (Spring, UTAD, Delta Divergence, etc.) | Part 1 §1 (1.1–1.66) → Part 3 §1 (1.49–1.66, incl. full Wyckoff event dictionary) → Part 4 §1 (1.67–1.74) |
| Any Greek or pricing formula | Part 1 §2 (2.1–2.46) → Part 3 §2 (2.66–2.80) → Part 4 §2 (2.81–2.87, incl. instrument facts, session timing) |
| GEX/VIX/PCR mechanics specifically | Part 1 (2.6–2.16), Part 3 (2.67 signal hierarchy table) |
| Wyckoff full event dictionary (Spring/UTAD/SOS/SOW/LPS/LPSY/SC/BC/AR/ST/PS/PSY) | Part 3 §1 (1.49–1.58) — this is the authoritative, most complete version |
| Any worked/dated example (esp. the June 2026 NIFTY trades) | Part 1 §3, Part 3 §3 — cross-referenced doc's E1–E20 largely overlap these, no new dated examples added in Part 4 |
| Any IF-THEN institutional rule | Part 1 §4 (1–23) → Part 2/Addendum (24–34) → Part 3 §4 (35–45) → Part 4 §3 (46–51) |
| Layer classification (A/B/C) | Part 3 §5 |
| Which pattern/formula maps to which AXIS component (1–7) | Part 3 §6 — the component mapping table |
| CRITICAL SOURCE ERRORS (Jade Lizard math error, lot-size error) | Part 3, top section |
| Full remaining gap list (final, consolidated) | THIS FILE, §2 above — supersedes all earlier gap lists |
| Cross-document consistency check | THIS FILE, §3 above |

---

## 5. FINAL STATUS SUMMARY

**What this knowledge base now contains, end to end:**
- ~74 distinct market/structural patterns, each with identifying data conditions, confusion points, and layer classification
- ~87 formulas, each with inputs, standalone meaning, required pairings, and typical/extreme ranges
- ~40 structured worked examples, including the full anatomy of the June 23 2026 cascade from four independent angles
- 51 institution-detection IF-THEN rules with explicit confidence ratings
- A complete Layer A/B/C classification with an honest statement of which layer is validated (A, C) vs. unvalidated (B)
- A full AXIS component-by-component mapping (Direction Scorer → Structure Gate → Strategy Activation → Knowledge Interpreter → EV Verifier → Option Selector → Risk Management)
- One resolved arithmetic error in source material (Jade Lizard), one resolved data inconsistency (lot size), one generalized formula (dynamic wing sizing)
- 10 explicitly named, still-open gaps requiring either new documents or live data — not silently dropped, but honestly flagged as unresolved

**What is NOT yet done, and cannot be done from text alone:**
- Backtesting the Direction Scorer layer weights against the five real examples (or more) — this requires running the hand-scoring exercise the original AXIS conversation recommended as the actual next action, not further document processing.
- Pulling the FII Participant-wise CSV and validating Layer B.
- Sourcing the GVOF strategy module's exact rules.
- Everything else in §2's open-gap list.

This closes the document-processing phase. The next productive step, per the original AXIS conversation's own conclusion, is to hand-score the five real June 2026 examples against this now-complete pattern/formula/rule library to produce the actual backtested layer weights — that is a data exercise, not a reading exercise, and is ready to begin whenever the underlying OHLC/OI/GEX data for those five sessions is available.

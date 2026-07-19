# AXIS Knowledge Base — Part 4: Cross-Reference Audit
Two additional independently-structured knowledge base documents were provided (a full rebuild + a "Supplement Part 2"). This part cross-checks them against Parts 1–3, skips everything already captured, and logs ONLY genuinely new material plus a final consolidated gap list.

---

## 1. NEW PATTERNS (not present in Parts 1–3)

### 1.67 Complete OI × LTP 4-Combination Matrix
Part 3 only captured "OI rising + LTP falling = selling" (Rule 45). The full matrix is:
| OI Change | LTP Change | Meaning | Signal |
|---|---|---|---|
| Rising ↑ | Rising ↑ | New longs opening | Moderately bullish |
| Rising ↑ | Falling ↓ | New shorts/writing opening | Bearish (already captured) |
| Falling ↓ | Rising ↑ | **Short covering (forced buying)** | Often the MOST explosive bullish signal — shorts have no choice but to buy back |
| Falling ↓ | Falling ↓ | Long liquidation | Bearish, less explosive than short covering |
- **Why this matters for AXIS**: Falling OI + rising LTP (short covering) is mechanically FORCED buying, distinct from voluntary new-long buying (rising OI + rising LTP). The forced variant tends to accelerate faster because covering shorts must transact regardless of price, creating the mechanical basis for short squeezes.
- **Layer**: Layer C.
- **Source**: Cross-referenced documents (Passarelli synthesis + market_structure_gex.md OI Analysis context).

### 1.68 Gamma-Theta Perpetual Opposition (as an explicit structural law)
Parts 1–3 mentioned Gamma/Theta opposition in passing (2.2–2.3) but not as its own standalone rule. Stated explicitly: every vanilla option position is EITHER (positive Gamma + negative Theta) OR (negative Gamma + positive Theta) — never both positive simultaneously. This is a hard mathematical constraint, not a tendency. Every strategy sits somewhere on this spectrum; spreads only reduce the exposure on both sides, they never eliminate the tradeoff.
- **AXIS implication**: Regime matching becomes a binary choice — SIDEWAYS/positive-GEX regimes structurally favor the Theta-positive side of the tradeoff; VOLATILE/negative-GEX regimes structurally favor the Gamma-positive side. Choosing the wrong side of this tradeoff for the current regime is named as "the most common structural error in options trading."
- **Source**: Cross-referenced documents.

### 1.69 Probability of Profit (POP) vs. Expected Value (EV) — Distinct, Sometimes Contradictory Metrics
**This is a genuinely important gap in Parts 1–3.** POP measures the % of trades that end profitably; EV measures the probability-weighted outcome INCLUDING loss magnitude. A strategy can have high POP (e.g., 60%) but negative EV if losses are large enough.
- Worked contrast: Iron condor, max profit ₹2,500, max loss ₹2,500, 60% POP → EV = (0.60×2,500)−(0.40×2,500) = +₹500 (positive). Same condor with wider spread, max loss ₹7,500 instead → EV = (0.60×2,500)−(0.40×7,500) = −₹1,500 (NEGATIVE despite unchanged 60% POP).
- **Critical correction to AXIS Component 5 (Final EV Verifier)**: The agent must compute EV net of transaction costs, NOT rely on POP as a proxy for trade quality. A 65% POP strategy with negative EV should be blocked; a 45% POP strategy with positive EV should pass. This directly sharpens Rule set in Part 3's Component 5 mapping.
- **Source**: Cross-referenced documents.

### 1.70 IV vs. HV Divergence as a Formal Three-Way Signal
Parts 1–3 covered "IV > HV → sell, IV < HV → buy" (Rule 29, 44) but the cross-referenced material adds a specific three-zone framework with approximate ratio thresholds:
- IV/HV > ~1.30 → options overpriced → sell premium (structural seller edge)
- IV/HV between 0.90–1.10 → fairly priced → neutral, calendar spreads or defined-risk directional
- IV/HV < ~0.90 → options underpriced → buy premium (structural buyer edge)
- **Critical pairing rule**: IV<<HV in NEGATIVE GEX = maximum sweet spot for option buyers (structure favors big moves AND options are cheap). IV>>HV in POSITIVE GEX = maximum sweet spot for sellers (structure dampens moves AND options are rich). This is the two-axis combination the AXIS Direction Scorer + Strategy Activation module should be checking jointly, not as separate gates.
- **Confidence flag**: The 1.30/0.90 thresholds are standard market-practitioner convention, not derived from NIFTY-specific backtesting in the source — same caveat as elsewhere in this KB.
- **Source**: Cross-referenced documents.

### 1.71 Stop-Loss Cascade Mechanics (Formalized Short Squeeze / Long Liquidation)
Part 3 covered Delta-hedge cascades (dealer-driven) but not the parallel RETAIL stop-loss cascade mechanic, which is mechanically distinct though it often compounds with dealer hedging on the same move:
1. Large cluster of stop-losses sits above/below current price (from short-sellers or long-holders).
2. Price reaches that level.
3. Stops trigger → become market orders (Buy Stop→Buy Market for shorts closing; Sell Stop→Sell Market for longs closing).
4. These forced orders print in the ASK (buy-side cascade) or BID (sell-side cascade) column, mechanically pushing price further.
5. The further push triggers the NEXT tier of stops → chain reaction.
- **Distinguishing from organic momentum**: Recognize via footprint — Exhaustion signature (Pattern 1.17-equivalent) shows volume thinning at new extremes once the stop-fuel is used up; that thinning is the signal the cascade is ending, not continuing.
- **On expiry day with negative GEX**: this retail stop cascade COMPOUNDS with the dealer delta-hedge cascade (Pattern 1.10) rather than being a separate phenomenon — both fire in the same direction, which is part of why negative-GEX expiry-day cascades are the fastest/largest moves in the whole system.
- **Source**: Cross-referenced documents (extends Pattern 1.10 in Part 1).

### 1.72 IV Rank / IV Percentile as Distinct Relative-Volatility Measures
Part 3 (2.79) flagged IV Rank as an inferred/gap formula. The cross-referenced material confirms and completes it:
- `IV_Rank = (Current_IV − 52wk_Low_IV)/(52wk_High_IV − 52wk_Low_IV) × 100`
- `IV_Percentile = (days in past year where IV was lower than today / 252) × 100` — a related but distinct measure (percentile counts DAYS below current level; Rank measures position within the Hi-Lo RANGE — these can diverge significantly if the range has a few extreme outlier days).
- Thresholds: IV Rank >50 → expensive, prefer selling; <30 → cheap, prefer buying; 30–50 → neutral/calendar zone.
- **Source**: Cross-referenced documents (confirms and completes Part 3 gap #7).

### 1.73 Frictionless Market — All 5 Black-Scholes Assumptions With Explicit NIFTY-Specific Corrections
Part 1 (2.27) gave the Black-Scholes PDE/formula; Natenberg synthesis mentioned "frictionless illusion" in passing. The cross-referenced material lists all 5 assumptions explicitly AND pairs each with the specific real-world NIFTY correction required:
1. Price changes entirely random → (no correction needed, this is philosophical)
2. % changes normally distributed → in practice fat-tailed/skewed (feeds volatility skew pattern)
3. Prices lognormally distributed at expiry → (consistent with Pattern 1.42)
4. Distribution mean sits at FORWARD price, not spot → must use Forward Price formula (2.36), not raw spot
5. Continuous, frictionless trading, identical borrow/lend rates → **violated by**: NSE circuit breakers (halt trading, cannot adjust hedge during a halt — dangerous if short Gamma), bid-ask spread slippage (effective entry above mid, exit below mid), discrete (not continuous) hedge adjustment intervals (2:00 PM reviews, not tick-by-tick) introduce tracking error vs. theoretical hedge, and STT/brokerage/GST transaction costs (2.42) that must be subtracted from any theoretical edge calculation.
- **Source**: Cross-referenced documents.

### 1.74 Complete Synthetic Positions "When to Use" Decision Table
Part 1/3 gave the construction formulas (2.57) but not the decision criteria for WHEN to use each:
| Synthetic | Construction | Use When |
|---|---|---|
| Synthetic Long Stock | Long Call + Short Put | Direct stock purchase is expensive/impractical |
| Synthetic Short Stock | Short Call + Long Put | Direct shorting is restricted/expensive |
| Synthetic Long Call | Long Stock + Long Put | A call is overpriced relative to (stock + put) cost |
| Synthetic Long Put | Short Stock + Long Call | A put is overpriced relative to (short stock + call) cost |
- **Key structural fact**: in an arbitrage-free market these must price equivalently to their direct counterparts (enforced by Put-Call Parity); any discrepancy is arbitraged away almost instantly by market makers, so genuine synthetic arbitrage opportunities are rare in a liquid market like NIFTY — logged as a decision framework for the Option Chain Selector, not an active alpha source.
- **Source**: Cross-referenced documents.

---

## 2. NEW FORMULAS (not present in Parts 1–3)

### 2.81 Complete Vertical Spread P&L Formulas (All 4 Types, Fully Specified)
Part 3 (2.58) gave abbreviated max risk/reward. Full breakeven formulas:
- **Bull Call Spread (debit)**: `Max_Profit = (Spread_Width − Net_Debit)×Lot`; `Max_Loss = Net_Debit×Lot`; `Breakeven = Long_Strike + Net_Debit`
- **Bear Call Spread (credit)**: `Max_Profit = Net_Credit×Lot`; `Max_Loss = (Spread_Width−Net_Credit)×Lot`; `Breakeven = Short_Strike + Net_Credit`
- **Bear Put Spread (debit)**: `Max_Profit = (Spread_Width−Net_Debit)×Lot`; `Max_Loss = Net_Debit×Lot`; `Breakeven = Long_Strike − Net_Debit`
- **Bull Put Spread (credit)**: `Max_Profit = Net_Credit×Lot`; `Max_Loss = (Spread_Width−Net_Credit)×Lot`; `Breakeven = Short_Strike − Net_Credit`
- **Source**: Cross-referenced documents.

### 2.82 NIFTY Options Instrument Facts (Structural Reference — Genuinely Missing from Parts 1–3)
This entire category was absent from the prior three parts:
- **Style**: European (exercisable ONLY at expiry — no early exercise possibility, no pre-expiry assignment risk for sellers, unlike single-stock American options).
- **Settlement**: Cash-settled — no physical delivery; final settlement price = average of NIFTY's last 30 minutes of trading on expiry day.
- **Expiry structure**: Weekly = every Thursday; Next-weekly = two Thursdays out; Monthly = last Thursday of the month; Far-monthly available but thin liquidity beyond ~3 months.
- **Trading hours**: 9:15 AM–3:30 PM IST regular session; pre-open 9:00–9:15 AM (order entry only, no matching — do not place market orders in this window, they can fill unfavorably at 9:15 open).
- **Circuit breakers**: NSE halts F&O trading at NIFTY moves of ±10% (15-min halt), ±15% (45-min halt), ±20% (full-day halt). **Critical risk implication**: during a halt, delta-hedge adjustment is impossible — a short-Gamma position (naked straddle/condor) caught in a halt has unmanageable exposure until trading resumes. This should be an explicit AXIS risk-check, not just a footnote.
- **Source**: Cross-referenced documents (confirms and formalizes NSE structural facts referenced only implicitly elsewhere).

### 2.83 Session Timing Windows (Full Intraday Reference — Not in Parts 1–3)
| Window | Character | AXIS action |
|---|---|---|
| 9:00–9:15 AM | Pre-open, no matching | No market orders |
| 9:15–9:30/10:00 AM | Opening noise (Pattern 1.59) | Wait for 0DTE per SKILL.md; run pre-trade checklist but avoid impulsive entry |
| 9:15–11:15 AM | Best liquidity window | Preferred window for directional option buying (Strategy 3 explicit) |
| 11:15 AM–2:00 PM | Lower volume, tighter range | Best window for range-strategy monitoring; first Greek drift review at 2:00 PM |
| 2:00–3:00 PM | Institutional adjustment activity | Second Greek drift review |
| 3:00 PM cutoff | STT trap deadline | ALL ITM options must be squared off before 3:00 PM on expiry day |
| 3:00–3:30 PM | Maximum Gamma window | Do NOT initiate new positions on expiry Thursday in this window |
- **Source**: Cross-referenced documents (assembles timing rules scattered across SKILL.md into one reference).

### 2.84 Delta-as-Probability Formal Strike Selection Math (Condor POP Derivation)
Part 3 (2.1) noted Delta as an ITM-probability proxy generally. This adds the actual combined-probability math for multi-leg strategies:
- Short strikes at Delta ≈0.15–0.20 → each leg independently has ~80–85% probability of expiring worthless.
- Naive combined probability (both legs safe): `(1−0.15) × (1−0.15) ≈ 72%` — this is HIGHER than the "55-65% POP" the source material cites for iron condors, because the naive multiplication ignores correlation and tail risk between the two legs (they're not independent — a large move threatens both directions' worth of "safety" simultaneously in terms of overall regime risk, even though only one side can be breached).
- Directional buy Delta 0.35–0.55 → 35-55% ITM probability — deliberately paying for close-to-50/50 odds with defined risk; going further OTM (<0.20 delta) means <20% probability of the option alone finishing ITM, though quick intraday moves can still profit before expiry regardless of the terminal probability.
- **Source**: Cross-referenced documents.

### 2.85 Dynamic GEX/VIX-Based Condor Wing Sizing (Replaces Fixed "200 pts" Rule)
Part 1 (2.70) gave the strike selection reference table with a static "~200 pts OTM" rule for condors. This formula makes the sizing DYNAMIC based on current VIX rather than a fixed point value:
- `Weekly_Expected_Move = Spot × (VIX/100) ÷ √52`
- `Optimal_Wing_Distance = Weekly_Expected_Move × 0.80`
- **Worked comparison**: At VIX=10, Spot=24,000 → Weekly_Move≈333 pts → Optimal_Wing≈266 pts (WIDER than the static 200-pt rule — in low-VIX quiet markets, 200 pts is actually too close to ATM relative to the true expected move, meaning POP is being understated by using the fixed 200-pt convention). At VIX=20 → Weekly_Move≈666 pts → Optimal_Wing≈533 pts (the static 200-pt rule would put wings WAY inside the 1-SD move, dramatically under-collateralizing POP — this is a genuine risk in high-VIX regimes if a fixed-point rule is followed blindly).
- **Correction to Part 1's Formula 2.70**: The "~200 pts OTM" reference table entry should be treated as a VIX≈14-calibrated example, not a universal constant — AXIS's Option Chain Selector (Component 6) should compute wing distance dynamically from current VIX using this formula, not hard-code 200 points.
- **Source**: Cross-referenced documents.

### 2.86 Complete Probability Distribution Reference Table (8 distributions, consolidated)
Part 1 (2.32) listed formulas for Bernoulli, Binomial, Poisson, Geometric, Uniform, Normal individually within the broader QUANT BIBLE formula dump. This consolidates them into one table AND adds Lognormal (which Part 1 discussed narratively via Natenberg but never tabulated alongside the others) plus Exponential with a trading-specific application column:

| Distribution | E[X] | Var(X) | AXIS Trading Application |
|---|---|---|---|
| Bernoulli | p | pq | Single trade: win(p) or lose(q) |
| Binomial | np | npq | # winning trades in n trades |
| Poisson | λ | λ | # cascade events per month |
| Geometric | 1/p | (1−p)/p² | # trades until first win |
| Uniform | (a+b)/2 | (b−a)²/12 | Random price level within a range |
| Normal | μ | σ² | Normalized daily returns (via CLT) |
| Exponential | 1/λ | 1/λ² | Time between cascade events |
| Lognormal | e^(μ+σ²/2) | (e^σ²−1)e^(2μ+σ²) | Actual NIFTY price distribution (not returns) — the one that actually matters for option pricing |
- **Source**: Cross-referenced documents (consolidation of Part 1's scattered QUANT BIBLE entries + Natenberg's lognormal material).

### 2.87 Long Box / Short Box Arbitrage Mechanics
Not covered in Parts 1–3 beyond a passing mention in synthetic position formulas (2.57):
- **Long Box (Conversion)**: Buy Call A + Sell Call B + Buy Put B + Sell Put A (B>A). Risk = NONE from price changes (fully Delta-neutral, all Greeks cancel). Reward = FIXED (strike difference minus net premium), regardless of where price lands at expiry.
- **Short Box (Reversal)**: mirror construction.
- **Practical relevance for AXIS**: if observed option-chain pricing implies a "box" return meaningfully different from the prevailing risk-free rate, it signals a genuine pricing error — but such errors are almost instantly arbitraged away by market makers in a liquid market like NIFTY, so this is logged as a detection/sanity-check tool for the Knowledge Interpreter agent rather than an active alpha source.
- **Source**: Cross-referenced documents.

---

## 3. NEW/SHARPENED RULES (not present in Parts 1–3, or meaningfully sharper than what exists)

46. **IF** a strategy's Probability of Profit (POP) is being used as the sole quality metric **THEN** this is insufficient and potentially misleading — compute net Expected Value (win_rate×avg_win − loss_rate×avg_loss, minus transaction costs) before allowing the Final EV Verifier to approve any trade. A 65% POP trade CAN have negative EV; a 45% POP trade CAN have positive EV. **CONFIDENCE: HIGH** — this is a mathematical fact, not an empirical claim, and it directly corrects an under-specification in Part 3's Component 5 mapping (which listed EV as an input but didn't explicitly warn against POP-substitution).

47. **IF** OI is falling at a strike **AND** LTP (premium) is rising at that same strike **THEN** interpret as short covering (forced buying) — often the most explosive bullish signal of the four possible OI/LTP combinations, distinct from and typically faster than voluntary new-long buying (OI rising + LTP rising). **CONFIDENCE: MEDIUM-HIGH** — mechanically sound and consistent with cascade mechanics already validated in Part 1 (Pattern 1.10), though no specific dated NIFTY example of this exact combination is given in any source reviewed so far.

48. **IF** the market regime scores as NEUTRAL (Direction Scorer = 3) **AND** GEX is positive **AND** VIX is compressed/stable **THEN** treat this as an explicit RANGE-TRADE entry signal (iron condor / straddle sell), not a "no trade" default. **IF** the market regime scores as NEUTRAL **AND** GEX is negative **AND** VIX is at a Weak Low **THEN** treat this as a WAIT signal, NOT a range-trade signal — a large move is possible at any time despite the neutral directional score, and selling premium here is dangerous. **CONFIDENCE: HIGH** — this sharpens Part 3's Rule 66 (regime filtering) by making explicit that "neutral score" does not mean one universal action; the correct action is itself regime-dependent on GEX/VIX, not on the score alone.

49. **IF** using theoretical Black-Scholes/Monte Carlo pricing as a reference for entry/exit decisions **THEN** apply four corrections before acting: (1) subtract transaction costs (~₹85-95/lot), (2) account for bid-ask slippage on both entry and exit, (3) recognize that hedge adjustments happen at discrete intervals (not continuously) introducing tracking error vs. the theoretical model, (4) recognize circuit-breaker halt risk means a short-Gamma position can become unmanageable for 15-45 minutes during extreme moves. **CONFIDENCE: HIGH** for the principle (directly named by Natenberg as "The Frictionless Illusion"); **MEDIUM** for the specific slippage/tracking-error magnitude estimates (operational estimates, not backtested).

50. **IF** placing Iron Condor wings **THEN** do not use a fixed "200 points OTM" rule universally — compute wing distance as 80% of the current VIX-implied weekly expected move instead. Using a fixed 200-pt rule under-collateralizes POP in high-VIX regimes and over-collateralizes (leaves premium on the table) in low-VIX regimes. **CONFIDENCE: MEDIUM** — the 80% factor is a standard practitioner convention for balancing POP against premium collection, not derived from NIFTY-specific backtesting, but the underlying logic (wing distance should scale with current expected move, not be a static constant) is mathematically sound and directly addresses an under-specification in Part 1's strike selection table (2.70).

51. **IF** a short-Gamma position (naked straddle, iron condor, etc.) is open during a session where NIFTY circuit-breaker thresholds (±10%/±15%/±20%) are plausibly reachable given current volatility **THEN** flag elevated tail risk explicitly — during any resulting trading halt, delta-hedge adjustment becomes impossible and the position's exposure is unmanageable until trading resumes. **CONFIDENCE: MEDIUM** — this is a structurally sound risk observation given NSE's circuit-breaker rules, but no source material provides historical frequency data on how often NIFTY approaches these thresholds, so the practical probability of this risk firing cannot be quantified from available material.

---

## 4. UPDATED / EXPANDED GAP LIST (supersedes Part 3, Section 7)

All gaps from Part 3 Section 7 remain open (FII CSV, OI/spread liquidity thresholds, naked VPOC definition, GVOF framework details, Composite Profile methodology, IV Rank data source, Weis Wave ratio threshold). The cross-referenced documents surface three ADDITIONAL genuine gaps not previously flagged:

9. **VSA (Volume Spread Analysis)**: Referenced as relevant to the Knowledge Interpreter agent's analytical toolkit in project context, but no VSA-specific source material (its rules, signatures, or how it differs from/complements the Wyckoff+Volume-Profile+Order-Flow stack already documented) has been provided anywhere across all source documents reviewed. This is a distinct named methodology that remains completely undocumented.

10. **"Active vs. consumed zones" (Layer C terminology)**: This exact phrase appears in the original AXIS project architecture description (Layer C: "active vs. consumed zones, POC, where stops are sitting") but is never formally defined in any of the source material processed across Parts 1-4. It's unclear whether this maps directly onto existing Volume Profile concepts already documented (HVN/LVN, VAH/VAL) or represents a distinct order-flow concept not yet captured.

11. **Agent 1 (Knowledge Interpreter) system prompt / decision logic**: The AXIS architecture defines what this agent should output (one paragraph + high/medium/low confidence label) but no source material specifies HOW it should weigh the pattern library against live data — i.e., the actual reasoning procedure, not just its knowledge inputs. This knowledge base equips the agent with facts; it does not yet specify the agent's own decision algorithm.

12. **NSE Bearish Strategies table**: One cross-referenced document attempted a reconstruction of this table (Long Put, Short Call, Put Spread, Bear Call Spread, Synthetic Put, Covered Put) based on the visible header structure and parallel logic to the Bullish table, but explicitly flagged it as LOW CONFIDENCE since the actual row content was not present in the source. **This reconstruction should NOT be treated as verified fact** — if the bearish strategy table matters for AXIS, the original NSE booklet content must be sourced directly.

13. **Historical NIFTY circuit-breaker frequency data**: New gap surfaced by Formula 2.82/Rule 51 — no source material indicates how often NIFTY has actually approached ±10%/±15%/±20% single-session moves historically, which is needed to calibrate how seriously to weight the circuit-breaker tail risk in position sizing.

**Nothing was found in the cross-referenced documents that contradicts material already established in Parts 1–3** — the two additional documents are consistent with (and in several places directly corroborate, e.g., the identical GEX signal hierarchy wording, identical Theta decay table, identical capital sizing table) the extraction already completed. The additions in this Part 4 are genuinely new material or meaningfully sharper formalizations, not corrections to prior errors, with the sole exception of Formula 2.85 (dynamic wing sizing), which should be treated as an *upgrade* to the static 200-pt convention in Part 1's Formula 2.70, not a contradiction of it — the 200-pt figure remains valid specifically as a VIX≈14 reference case.

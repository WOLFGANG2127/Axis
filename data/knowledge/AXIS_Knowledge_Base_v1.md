# AXIS Knowledge Base — Structured Rule Library
Source: "Nifty Strategy 2026" article collection + embedded book syntheses (Trading Option Greeks / Passarelli, Option Volatility & Pricing / Natenberg, Wyckoff 2.0, Options Trading for the Institutional Investor / Thomsett, Options Trading Handbook / Kaushik, NSE Bank Nifty booklet, QUANT BIBLE / MIT Sloan, nifty-options-pro SKILL.md + 4 reference files, options-pricing-and-greeks GitHub project, Bookmap/footprint orderflow article)

---

## 1. PATTERN LIBRARY

### 1.1 Theta Decay Acceleration
- **Data conditions**: ATM theta scales non-linearly with DTE — 30d: ₹5-8/day (1-2%); 14d: ₹10-15 (3-5%); 7d: ₹15-25 (6-10%); 3d: ₹30-50 (12-20%); 1d/expiry eve: ₹50-100 (25-50%); expiry day: 100% of remaining extrinsic.
- **Confused with**: Linear/constant time decay (retail misconception). Distinguished by the exponential curve in the final 7-10 days.
- **Layer**: Live order flow / live pricing (instrument-level, not market-wide).
- **Source**: Nifty Options Trading Guide; nifty-options-pro `references/greeks_and_pricing.md`.

### 1.2 IV Crush (Pre/Post Event)
- **Data conditions**: IV rises 2-4 VIX points in days before scheduled events (RBI policy, elections, budget); after announcement, IV collapses sharply regardless of which direction price moved; option premiums drop even if directional call was correct because Vega loss exceeds Delta gain.
- **Confused with**: A losing directional trade. Distinguished by checking whether Vega-driven premium loss outweighs Delta-driven gain post-event.
- **Layer**: Anonymous market-wide sentiment (IV/Vega is aggregate market pricing).
- **Source**: Nifty Options Trading Guide; nifty-options-pro skill (Common Retail Errors); Passarelli synthesis (Vega section).

### 1.3 STT Trap (Expiry-Day Tax Asymmetry)
- **Data conditions**: STT on options expiring ITM = 0.125% of intrinsic value (not sale price) — far higher than 0.0625% STT on a regular sell-to-close. Triggered specifically by letting an ITM option expire instead of squaring off before 3:00 PM.
- **Confused with**: A simple unavoidable cost of holding to expiry. Distinguished by being entirely avoidable via timely square-off.
- **Layer**: Not a market-structure layer — a transaction-cost/regulatory mechanism.
- **Source**: Nifty Options Trading Guide; nifty-options-pro `references/risk_and_adjustments.md`.

### 1.4 Far-OTM Buying Trap (Retail Error)
- **Data conditions**: Buying options >300 points from ATM on weekly expiry because "premium is cheap"; requires a disproportionately large move (high Gamma needed) to overcome Theta cost; statistically fails most of the time.
- **Confused with**: Cheap, low-risk lottery-ticket exposure. Distinguished by the Theta/Gamma math showing the breakeven move is rarely reached in the available time.
- **Layer**: Live order flow / position construction error.
- **Source**: Nifty Options Trading Guide ("most OTM option buyers lose money"); nifty-options-pro skill (Common Retail Errors, Strategy Toolkit).

### 1.5 Positive GEX Regime (Pinning / Stabilizing)
- **Data conditions**: Net GEX > 0; dealers are net long gamma; dealer hedging behavior = buy dips, sell rallies; market effect = range-bound, pinning toward Max Pain, dampened moves.
- **Confused with**: Generic "low volatility" or "bullish consolidation." Distinguished specifically by dealer hedging mechanics, not just observed calm price action.
- **Layer**: Anonymous market-wide sentiment (Layer A — GEX/dealer positioning).
- **Source**: nifty-options-pro SKILL.md (Quick-Reference Matrix); `references/market_structure_gex.md`.

### 1.6 Negative GEX Regime (Cascading / Destabilizing)
- **Data conditions**: Net GEX < 0; dealers net short gamma; dealer hedging behavior = sell dips, buy rallies (pro-cyclical); market effect = trending, amplifying, cascade risk; same OI that looked like a "floor" in positive GEX becomes forced-selling fuel once GEX flips negative.
- **Confused with**: A normal supported pullback (because OI "support" still visually looks present). Distinguished by checking GEX sign before trusting OI as support.
- **Layer**: Anonymous market-wide sentiment (Layer A).
- **Source**: SKILL.md; `references/market_structure_gex.md` ("Key insight" paragraph).

### 1.7 Gamma Flip Level (Regime Transition Point)
- **Data conditions**: Exact spot price where cumulative Call GEX above spot equals cumulative Put GEX below spot (Net GEX crosses zero). Above flip = dealers buy dips (slows/pins/reverses move); below flip = dealers sell dips (accelerates/cascades move).
- **Confused with**: A normal support/resistance technical level. Distinguished by being derived purely from options-chain Gamma×OI math, not price-action history.
- **Layer**: Anonymous market-wide sentiment (Layer A), but functions as the trigger boundary for Layer C cascade behavior.
- **Source**: `references/market_structure_gex.md`; worked example below (1.x / Section 3).

### 1.8 PCR Trap (Put Writing Misread as Bullish in Negative GEX)
- **Data conditions**: PCR rising (more put OI relative to call OI) while GEX is negative. Looks bullish/protective by standard reading but actually represents put writers loading delta-hedge obligations that become forced-selling fuel once the market falls through their strikes.
- **Confused with**: Standard bullish PCR signal (valid only in positive GEX). Distinguished strictly by checking GEX sign first — same PCR reading means opposite things in each regime.
- **Layer**: Anonymous market-wide sentiment (Layer A) — explicitly flagged as the layer "most easily misread by retail."
- **Source**: SKILL.md (Common Retail Errors: "Treating rising PCR as bullish when GEX is negative"); `references/market_structure_gex.md` (PCR section).

### 1.9 Max Pain Failure (Negative GEX)
- **Data conditions**: Max Pain (strike of maximum aggregate option-buyer loss) only pins price when GEX is positive (dealers buying dips reinforce pinning). In negative GEX, dealers are actively selling dips, fighting against Max Pain — it fails completely as a target.
- **Confused with**: A universally reliable pinning magnet. Distinguished by checking GEX regime before applying Max Pain at all.
- **Layer**: Anonymous market-wide sentiment (Layer A), conditionally valid only.
- **Source**: SKILL.md (signal hierarchy rule #4); `references/market_structure_gex.md`.

### 1.10 Delta-Hedge Cascade (OI Wall Becomes a Weapon)
- **Data conditions**: As price falls through a heavy put-OI strike, writer Delta increases (option deepens ITM) → writer must short MORE futures to stay hedged → additional selling pressure → price falls further → Delta increases again. Self-reinforcing loop. Intensity scales with OI × Gamma² (second-order effect), which is why expiry-day cascades are fastest (Gamma and OI both at maximum simultaneously).
- **Confused with**: Organic/fundamental selling. Distinguished by being mechanically forced hedge-flow, traceable directly to OI concentration and Gamma at the broken strike.
- **Layer**: Live order flow (Layer C) — this is the mechanism that converts Layer A's anonymous OI data into live forced-flow.
- **Source**: `references/market_structure_gex.md` (Delta Hedge Cascade section + formula + worked numeric example).

### 1.11 VIX Structural Lead Signals
- **Data conditions**: (a) VIX at Weak Low on 15-min chart = market complacency, high risk of imminent vol spike, cheap puts become asymmetric trade; (b) VIX CHoCH (Change of Character) upward = structural shift toward higher volatility regime, signal to buy puts; (c) VIX BOS (Break of Structure) upward = confirmed vol expansion, premiums already expanding; (d) VIX above EMA(5) and rising = trending toward higher IV, don't sell premium unhedged; (e) VIX compressed/stable = positive-GEX-style environment, favorable for selling premium.
- **Confused with**: Treating VIX purely as a coincident fear gauge. Distinguished by reading VIX's own SMC-style structure (lows, CHoCH, BOS) as a leading/predictive series in its own right, independent of NIFTY price action.
- **Layer**: Anonymous market-wide sentiment (Layer A) but explicitly noted as having multi-day predictive lead time, unlike same-day GEX/PCR reads.
- **Source**: `references/market_structure_gex.md` (VIX Structure Analysis section).

### 1.12 VIX × GEX Multiplicative Effect
- **Data conditions**: When VIX is rising AND GEX is negative simultaneously, put premium gains compound — Delta gain from price falling stacks with Vega gain from IV expanding, producing outsized percentage returns on long puts (real example: VIX +9% in one session, puts gained 276-425%).
- **Confused with**: A pure directional (Delta-only) payoff. Distinguished by decomposing the gain into Delta and Vega components separately.
- **Layer**: Combination of Layer A (VIX/GEX) feeding into Layer C live P&L behavior.
- **Source**: `references/market_structure_gex.md` (VIX and GEX Combined section).

### 1.13 Wyckoff Accumulation / Distribution Phase Structure
- **Data conditions**: Five-phase protocol (A-E). Phase A = stops prior trend (PS/PSY, SC/BC, AR, ST events). Phase B = builds "cause" via lateral range where large operators absorb supply/demand. Phase C = tests opposition via Spring (accumulation) or UTAD/Upthrust After Distribution (distribution) — a deliberate false breakout. Phase D = SOS/SOW (Sign of Strength/Weakness — aggressive displacement breaking structure) plus LPS/LPSY (Last Point of Support/Supply, a retest). Phase E = confirmed trend departure from the range.
- **Confused with**: Random sideways chop with no underlying intent. Distinguished by the specific sequence of climax → automatic reaction → test → shakeout → markup/markdown, and by structures not needing to be horizontal (see 1.14).
- **Layer**: Live order flow (Layer C), structural/price-action confirmation gate (not a numeric scoring layer).
- **Source**: Wyckoff 2.0 synthesis section 1 ("The Wyckoff Methodology").

### 1.14 Sloping Trading Ranges
- **Data conditions**: Upward-sloping accumulation = buyers aggressively revaluing the asset higher even before breakout, refusing to let price reach oversold zones — denotes extreme underlying strength. Downward-sloping distribution = persistent lower-highs/lower-lows inside the range itself, denoting total seller dominance and warning of a fast subsequent markdown.
- **Confused with**: A simple uptrend or downtrend (no range present). Distinguished by the range still containing two-way auction but with directional skew baked into its slope.
- **Layer**: Live order flow / structural (Layer C).
- **Source**: Wyckoff 2.0 synthesis, Part II ("Sloping Trading Ranges").

### 1.15 Structural Failure of Strength
- **Data conditions**: Price moves away from an extreme test (e.g., a potential Spring) but reverses completely before even reaching the opposite boundary of the range — proves aggressive buyers are front-running and blocking downside continuation.
- **Confused with**: A weak/failed reversal signal. Distinguished — it is actually a bullish tell precisely because the failure to reach the far boundary shows buyers stepping in early.
- **Layer**: Live order flow (Layer C).
- **Source**: Wyckoff 2.0 synthesis, Part II.

### 1.16 Shortening of the Thrust (SOT)
- **Data conditions**: Minimum three consecutive impulse waves where each new structural high/low travels a measurably shorter distance than its predecessor. SOT + high volume = effort-vs-result divergence (institutional money blocking the path). SOT + low volume = pure exhaustion (dominant trend participants withdrawing).
- **Confused with**: Normal pullback rhythm. Distinguished by requiring ≥3 consecutive shrinking waves, and by checking the accompanying volume to disambiguate "blocked" vs "exhausted."
- **Layer**: Live order flow (Layer C).
- **Source**: Wyckoff 2.0 synthesis, Part II ("Momentum Anomalies").

### 1.17 Absorption
- **Data conditions**: High traded volume at a price level with price failing to displace — passive limit orders are absorbing aggressive market-order flow. In Order Flow footprint terms: aggressive Buy Market hits ASK repeatedly but price stalls, meaning passive Sell Limits are blocking.
- **Confused with**: Simple consolidation/low interest. Distinguished by volume being HIGH (not low) while price range stays compressed — effort without result.
- **Layer**: Live order flow (Layer C), and specifically the book's own constraint: only trustworthy when occurring AT a marked Volume Profile boundary (VAH/VAL/VPOC/LVN), not in the middle of an empty range.
- **Source**: Wyckoff 2.0 synthesis, sections 3 and "Anatomy of a Market Turn."

### 1.18 Initiative
- **Data conditions**: Following absorption/exhaustion, a surge of aggressive market orders (strong Delta, diagonal Imbalance e.g. 300-400%+ skew) propels price away from the absorption zone — confirms the new trend leg is underway.
- **Confused with**: A random breakout spike. Distinguished by being preceded by visible exhaustion + absorption at a structural level (the 3-step protocol), not appearing in isolation.
- **Layer**: Live order flow (Layer C).
- **Source**: Wyckoff 2.0 synthesis, "Anatomy of a Market Turn" (Step 3).

### 1.19 Delta Divergence Trap
- **Data conditions**: A candlestick prints strongly positive Order Flow Delta (aggressive buying dominant) but the candle itself closes bearish. Reveals that the aggressive buy-market flow was being absorbed by a large passive institutional sell-limit (Iceberg) order — retail buyers are trapped.
- **Confused with**: A data error or a simple losing long trade. Distinguished by explicitly comparing Delta sign to candle close direction — disagreement between the two is the signal itself.
- **Layer**: Live order flow (Layer C) — flagged as the cleanest confirmation of Wyckoff absorption/Spring-type events.
- **Source**: Wyckoff 2.0 synthesis, "The Delta Divergence Trap (The Order Flow Problem)."

### 1.20 VPOC Migration — Continuation vs Reversal
- **Data conditions**: Continuation protocol — VPOC migrates to a new level and price immediately follows with a fast impulse in trend direction (market has accepted new value, hunting next level). Reversal protocol — VPOC migrates to a new high/low but price then consumes excessive time sideways rather than continuing — a Change of Character (ChoCh) warning of stalling/distribution.
- **Confused with**: Any VPOC shift being automatically bullish/bearish-continuation. Distinguished by what price does AFTER migration (fast follow-through vs. time consumption).
- **Layer**: Live order flow / Volume Profile (Layer C).
- **Source**: Wyckoff 2.0 synthesis, "VPOC Migration Mechanics."

### 1.21 Failed Auction / Failed Breakout Rejection
- **Data conditions**: Price breaks outside the Value Area (VAH/VAL) but fails to sustain — confirmed via severe Delta Divergence on the breakout candle, then a firm wide-range close back inside the 68.2% Value Area. High probability the price then rotates to the opposite extreme of the Value Area.
- **Confused with**: A genuine trending breakout. Distinguished by the failure to hold outside the VA combined with the Delta/close mismatch on the breakout bar itself.
- **Layer**: Live order flow / Volume Profile (Layer C); this is "Strategy 2: The Reversion Principle" in the strategy manual.
- **Source**: Wyckoff 2.0 synthesis, "Strategy 2."

### 1.22 High Volume Node (HVN) Gravity / Low Volume Node (LVN) Rejection
- **Data conditions**: HVN = price level with heavy historical traded volume; acts as a magnet, price tends to consolidate/return there (used for premium-selling strike placement). LVN = price level with very little traded volume (an "unfair" price the market rejected quickly); price tends to move through it violently rather than linger (used for long-option/directional entries).
- **Confused with**: Arbitrary support/resistance lines. Distinguished by being derived from actual traded volume distribution, not price-touch counting.
- **Layer**: Live order flow / Volume Profile (Layer C).
- **Source**: Wyckoff 2.0 synthesis, "Strategic Takeaways" (Options Trader section).

### 1.23 Dispersion Mispricing (Index vs Constituent IV)
- **Data conditions**: Index implied volatility trades structurally richer (more expensive) than the volume-weighted combination of its individual constituent stocks' implied volatilities, because correlation/co-movement is itself overpriced into the index option.
- **Confused with**: A simple "index options are expensive" observation. Distinguished by being a relative-value mispricing between index vol and single-stock vol specifically, not an absolute richness claim.
- **Layer**: Anonymous market-wide sentiment (Layer A) — cross-instrument, not single-strike.
- **Source**: Institutional Quant Blueprint synthesis, "Dispersion Trading."

### 1.24 Volatility Skew / Smile (Downside Put Richness)
- **Data conditions**: OTM puts trade at structurally higher IV than equidistant OTM calls, because of institutional demand for downside portfolio protection. Appears as "vertical skew" across strikes in the same expiry; "term structure" (horizontal skew) describes IV differing across expiry months (front month lower in calm markets, higher in panic/pending-news periods).
- **Confused with**: Random/noisy strike-by-strike IV variation. Distinguished by the structural, persistent, directionally-biased nature of the skew (puts > calls), repeated as a near-universal pattern across multiple sources in this material.
- **Layer**: Anonymous market-wide sentiment (Layer A).
- **Source**: Passarelli synthesis (Volatility Skew); Natenberg synthesis (lognormal distribution discussion); NSE Bank Nifty booklet glossary; Quant Bible (lognormal reality for log-style data).

### 1.25 Institutional VWAP Accumulation
- **Data conditions**: Large institutional orders are sliced and executed against the session VWAP benchmark — buying when price is below VWAP ("discount" vs. day's volume-weighted average), selling above it — producing VWAP's frequent function as a dynamic support/resistance line.
- **Confused with**: VWAP as a purely descriptive average with no causal mechanism. Distinguished by understanding WHY institutions defend it (their own execution algorithms are actively trading against that line).
- **Layer**: Live order flow (Layer C).
- **Source**: Wyckoff 2.0 synthesis, VWAP formula working example.

### 1.26 Inventory Skewing by Market Makers
- **Data conditions**: When a market maker accumulates an unwanted net-long or net-short inventory position, it deliberately skews its quoted bid/ask away from theoretical fair value (e.g., fair value 0.50 quoted as 0.43/0.53) to incentivize the opposite side of trades, sacrificing edge to offload risk.
- **Confused with**: A directional view by the market maker. Distinguished — the skew reflects inventory risk management, not a forecast.
- **Layer**: Institutional identity (Layer B) — this is a named/identifiable behavior of the dealer/MM community as a class, even if individual counterparties are anonymous.
- **Source**: QUANT BIBLE synthesis ("Strategy B: Skewing for Inventory"); Institutional Quant Blueprint synthesis (Corporate Structure).

### 1.27 Informational Asymmetry / Trader Memory Exploitation
- **Data conditions**: A market maker tracks a specific counterparty's repeated buy/sell actions at specific prices to infer that counterparty's private fair-value estimate, then shifts its own market in that direction to be compensated more heavily when the informed counterparty trades again.
- **Confused with**: Random price drift. Distinguished by requiring the market maker to retain "memory" of a specific counterparty's past prints (this is named explicitly as SIG/Susquehanna's specialty).
- **Layer**: Institutional identity (Layer B).
- **Source**: QUANT BIBLE synthesis ("Strategy C: Exploiting Informational Asymmetry"); Institutional Quant Blueprint synthesis (firm breakdown — SIG).

### 1.28 Bias-Variance Driven Model Choice (Meta-Pattern, applies to system design not market)
- **Data conditions**: Low-dimensional, simple data → KNN-style flexible models (low bias, high variance) can work. High-dimensional or noisy financial data → linear/rule-based models (higher bias, lower variance) are more stable and trustworthy for live capital.
- **Confused with**: "More complex model = better model." Distinguished explicitly by the Quant Bible's own argument that simple, stable, slightly-biased models are preferable for trading systems specifically because of the curse of dimensionality and overfitting risk on noisy market data.
- **Layer**: N/A — applies to AXIS system design (Direction Scorer simplicity), not a market pattern.
- **Source**: QUANT BIBLE synthesis (Bias-Variance Tradeoff; "For the Algo Developer" section).

### 1.29 Adaptive Markets Hypothesis (Coexisting Randomness/Determinism)
- **Data conditions**: Rationality and irrationality coexist depending on the prevailing regime; localized price action can be highly random while the broader Cause-and-Effect law (a sustained trend cannot occur without a prior building range) remains deterministic.
- **Confused with**: Markets being either "perfectly efficient" or "perfectly predictable." Distinguished by holding both views simultaneously at different structural scales (local noise vs. macro cause/effect).
- **Layer**: Conceptual/meta — informs how much confidence to place in any single-timeframe signal.
- **Source**: Wyckoff 2.0 synthesis, Part I ("Coexistence of Randomness and Determinism").

### 1.30 "Would I Do It Now?" Discipline Check
- **Data conditions**: Before any position adjustment, the trader asks whether they would establish this exact position fresh at current prices. If no, the position must be closed rather than adjusted/hoped on.
- **Confused with**: A generic stop-loss rule. Distinguished by being a re-underwriting question (re-evaluate the whole thesis), not just a price-trigger rule.
- **Layer**: Risk-management / behavioral discipline, applies at the Final Verifier / exit-decision stage.
- **Source**: Passarelli synthesis (Volatility-Selling Trade-off section); Natenberg synthesis (Strategic Trade Structuring); nifty-options-pro `references/risk_and_adjustments.md` (Technique 5).

### 1.31 HAPI — Hope and Pray Index
- **Data conditions**: The moment a trader catches themselves "hoping" price will come back instead of following a pre-built plan, that is itself the signal that risk management has already been violated and the position should be exited immediately.
- **Confused with**: Normal patience while a thesis plays out. Distinguished by the emotional marker (hope replacing analysis) rather than any price level.
- **Layer**: Risk-management / behavioral discipline.
- **Source**: Passarelli synthesis ("Putting Greeks into Action" chapter summary); nifty-options-pro `references/risk_and_adjustments.md` (Exit Rules — "The HAPI Warning").

### 1.32 4-Stroke Breakout Method (Prior-Day Range Breakout)
- **Data conditions**: Record the prior day's high/low premium range for the relevant ITM call and put. Buy the call once its premium exceeds the prior day's high; sell to exit at a fixed target (e.g., +₹10). If price opens below prior day's low, exit/liquidate. Mirrors for puts on the short side.
- **Confused with**: A discretionary breakout strategy. Distinguished by being mechanically defined purely off the prior session's high/low premium values with a fixed point target, requiring no other indicator.
- **Layer**: Live order flow (Layer C) — pure intraday premium price-action.
- **Source**: Options Trading Handbook (Kaushik) synthesis, "The four-phase method."

### 1.33 Skew-Driven Strike Selection ("Selling the Guts")
- **Data conditions**: For wing spreads (butterflies/iron butterflies), the relative IV richness between the middle strikes ("guts") and outer strikes ("wings") — driven by skew — determines whether selling the guts is attractively priced, and whether an Iron Butterfly (mixed call/put) is preferable to a standard single-type Butterfly when skew is steep.
- **Confused with**: Picking strikes purely by equidistant spacing from spot. Distinguished by pricing the spread off the actual skew curve rather than symmetric distance.
- **Layer**: Anonymous market-wide sentiment (Layer A, since skew is an aggregate options-chain property).
- **Source**: Passarelli synthesis, "Volatility skew specifically impacts wing spreads."

---

## 2. FORMULA REFERENCE

### 2.1 Delta (Δ)
- **Calc**: ΔOption / ΔSpot (1st derivative of option price w.r.t. underlying price). Black-Scholes: N(d1) for calls.
- **Tells you alone**: Directional sensitivity per ₹1 move; rough probability-of-expiring-ITM proxy; equivalent-share/futures exposure.
- **Cannot tell alone / must pair with**: Does not tell you how that exposure will change (needs Gamma); does not predict direction of the underlying (not a directional forecasting tool — explicitly warned against in nifty-options-pro skill).
- **Typical ranges**: ATM ≈ 0.50; deep ITM → 0.90-1.00; far OTM → 0.05-0.10; ATM Put ≈ -0.50; deep ITM Put → -0.90 to -1.00.
- **Source**: Nifty Options Trading Guide; nifty-options-pro `references/greeks_and_pricing.md`; Passarelli synthesis; Natenberg synthesis; options-pricing-and-greeks GitHub README "Greeks 101."

### 2.2 Gamma (Γ)
- **Calc**: ΔDelta / ΔSpot (2nd derivative of price w.r.t. spot). Always positive for both calls and puts (long options).
- **Tells you alone**: Rate at which Delta will change/accelerate; highest at ATM, spikes 3-5x on expiry day vs 14 DTE.
- **Cannot tell alone / must pair with**: Must combine with OI to assess cascade risk (Cascade_intensity ∝ OI × Gamma²); must pair with expected move size to forecast post-move Delta (New_Delta ≈ Starting_Delta + Gamma × Expected_Move).
- **Typical ranges**: Highest ATM, decreasing toward deep ITM/OTM; "Expiry day Gamma 3-5x higher than 14 DTE" is flagged as the key extreme.
- **Source**: nifty-options-pro `references/greeks_and_pricing.md`; Passarelli synthesis; GitHub README Greeks 101.

### 2.3 Theta (Θ)
- **Calc**: ΔOption_Price / ΔTime (value lost per day, all else equal). Negative for buyers, positive for sellers; non-linear, accelerating into final 7-10 days.
- **Tells you alone**: Daily cost (long) or income (short) of holding, in rupees.
- **Cannot tell alone / must pair with**: Must compare against expected directional/vol gain (Total_Theta_Cost = Theta_per_day × Expected_Holding_Days; if > expected gross profit, trade is not viable).
- **Typical ranges**: See full DTE table under 2.16 below (Theta-by-DTE table).
- **Source**: Nifty Options Trading Guide; SKILL.md Position Sizing Framework (Step 4); Passarelli; Natenberg.

### 2.4 Vega (ν)
- **Calc**: ΔOption_Price per 1% change in IV. Highest at ATM; decreases as DTE shrinks.
- **Tells you alone**: Rupee sensitivity to a 1-point IV change.
- **Cannot tell alone / must pair with**: Must combine with expected IV change magnitude around events (Expected_Vega_PnL = Vega × Expected_IV_Change_%) and added to Theta cost for true breakeven; must be evaluated jointly with Delta because around events the two can offset (correct direction but net loss from IV crush).
- **Typical ranges**: BankNifty IV typically 1.3-1.6× Nifty 50 IV (more premium, more Vega risk).
- **Source**: SKILL.md Position Sizing Step 3; nifty-options-pro `references/greeks_and_pricing.md`; Passarelli; Natenberg.

### 2.5 Rho (ρ)
- **Calc**: ΔOption_Price per 1% change in risk-free interest rate. Higher rates increase calls, decrease puts.
- **Tells you alone**: Interest-rate sensitivity.
- **Cannot tell alone / must pair with**: Largely negligible standalone for short-dated Nifty options; only meaningful for LEAPS or jelly-roll/conversion arbitrage by market makers.
- **Typical ranges**: Negligible weekly/monthly; significant for long-dated (>1yr) instruments.
- **Source**: nifty-options-pro `references/greeks_and_pricing.md`; Passarelli; Natenberg.

### 2.6 Net GEX (Gamma Exposure)
- **Calc**: `Net_GEX = Σ[CE_OI(i) × Γ(i) × S × lot × 100] − Σ[PE_OI(i) × Γ(i) × S × lot × 100]`
- **Tells you alone**: Whether dealers are net long or short gamma → whether their hedging will dampen (positive) or amplify (negative) moves.
- **Cannot tell alone / must pair with**: Does not tell you magnitude of expected move (pair with VIX formula) or fuel level (pair with OI/PCR); explicitly the "master regime switch" that must be read FIRST, before any other indicator is trusted.
- **Typical/extreme**: Real example: −3.94M Cr (strongly negative) on June 23, 2026 preceded a violent cascade below the flip level.
- **Source**: `references/market_structure_gex.md`.

### 2.7 Gamma Flip Level
- **Calc**: Price where cumulative Call_GEX (strikes > spot) = cumulative Put_GEX (strikes < spot), i.e., where Net GEX crosses zero. Practical shortcut: read off StockMojo Gamma Exposure chart where the Net GEX line crosses 0.
- **Tells you alone**: The exact price boundary separating "dealers dampen" vs "dealers amplify" behavior.
- **Cannot tell alone / must pair with**: Must be combined with current spot location (above/below flip) and VIX magnitude formula for a price target.
- **Source**: `references/market_structure_gex.md`; real example ≈24,050 on June 23, 2026.

### 2.8 VIX Daily Expected Move (1 SD)
- **Calc**: `Daily_Move = Spot × (VIX/100) ÷ √252`
- **Tells you alone**: 68% confidence expected 1-day point range.
- **Cannot tell alone / must pair with**: Pair with GEX direction to assign the move to up or down target rather than a symmetric range.
- **Example**: Spot 24,100, VIX 12.89 → 195.7 pts.
- **Source**: `references/market_structure_gex.md`.

### 2.9 VIX Weekly Expected Move
- **Calc**: `Weekly_Move = Spot × (VIX/100) ÷ √52`
- **Example**: 24,100 × 0.1289 ÷ 7.211 = 430.9 pts.
- **Source**: `references/market_structure_gex.md`.

### 2.10 VIX Directional Down/Up Target
- **Calc**: `Down_Target = Spot − (Spot × VIX% ÷ √252)`; `Up_Target = Spot + (Spot × VIX% ÷ √252)` — used only when GEX confirms direction.
- **Tells you alone**: A specific price target, not just a range.
- **Cannot tell alone / must pair with**: Requires GEX to confirm directional bias first (formula is direction-agnostic by itself).
- **Example**: Down_Target = 24,100 − 196 = 23,904; actual low 23,865; error 39 pts (0.16%).
- **Source**: `references/market_structure_gex.md`.

### 2.11 2-Standard-Deviation Target
- **Calc**: `Daily_2SD = Daily_1SD × 1.96` (95% confidence extreme move).
- **Source**: `references/market_structure_gex.md`.

### 2.12 GEX Fibonacci Extension Targets
- **Calc**: Width = Flip_Level − End_of_Red_GEX_Zone. `First target = Flip_Level − (Width × 0.382)`; `Second target = Flip_Level − (Width × 0.618)`. Combined zone = range between VIX_Target and GEX_Target.
- **Tells you alone**: A secondary downside target zone derived purely from GEX structure.
- **Cannot tell alone / must pair with**: Most reliable when combined/cross-checked with the VIX-formula target (see worked example, both landed within 40 pts of actual low on June 23, 2026).
- **Source**: `references/market_structure_gex.md`.

### 2.13 PCR (Put-Call Ratio)
- **Calc**: Total Put OI ÷ Total Call OI.
- **Tells you alone**: Nothing reliable by itself — explicitly the indicator most warned about in this material.
- **Cannot tell alone / must pair with**: MUST be paired with GEX sign. Positive GEX → standard reading (rising PCR = bearish/protective sentiment, falling = bullish). Negative GEX → inverted reading (rising PCR = more forced-selling fuel, i.e., bearish even though it "looks" protective).
- **Source**: `references/market_structure_gex.md` (PCR section, explicit TRAP warning); SKILL.md Common Retail Errors.

### 2.14 Max Pain
- **Calc**: Strike at which total option-premium losses are maximized for buyers (pinning target).
- **Tells you alone**: A candidate pinning price — but ONLY in positive GEX.
- **Cannot tell alone / must pair with**: GEX sign — invalid/should be ignored entirely when GEX is negative.
- **Source**: `references/market_structure_gex.md`.

### 2.15 Overnight OI Build %
- **Calc**: `OI_change% = (today_ATM_OI − yesterday_OI) / yesterday_OI × 100`
- **Tells you alone**: Whether today is likely a high-volatility day.
- **Cannot tell alone / must pair with**: Threshold rule given standalone: if >50%, treat as high-vol-risk day, avoid selling naked premium.
- **Source**: `references/market_structure_gex.md` (OI Analysis).

### 2.16 ATM Theta by DTE (Reference Table)
| DTE | Daily Theta | % of Premium |
|---|---|---|
| 30 days | ₹5-8 | 1-2% |
| 14 days | ₹10-15 | 3-5% |
| 7 days | ₹15-25 | 6-10% |
| 3 days | ₹30-50 | 12-20% |
| 1 day (expiry eve) | ₹50-100 | 25-50% |
| Expiry day | All remaining extrinsic | 100% |
- **Source**: Nifty Options Trading Guide; `references/greeks_and_pricing.md` (repeated identically in both — confirms consistency, not contradiction).

### 2.17 Equivalent Nifty Exposure (Position Sizing)
- **Calc**: `Equivalent_Exposure = Delta × Lots × Lot_Size(25)`
- **Tells you alone**: How many "Nifty-equivalent units" your options position behaves like.
- **Cannot tell alone / must pair with**: Compare against your maximum comfortable Nifty-equivalent exposure ceiling (a personal risk limit, not derived from the formula itself).
- **Source**: SKILL.md Position Sizing Step 1; `references/greeks_and_pricing.md`.

### 2.18 Post-Move Delta Estimate
- **Calc**: `New_Delta ≈ Starting_Delta + (Gamma × Expected_Move)`
- **Source**: SKILL.md Position Sizing Step 2.

### 2.19 Expected Vega P&L
- **Calc**: `Expected_Vega_PnL = Vega × Expected_IV_Change_%`
- **Cannot tell alone**: Must be added to Theta cost for a true break-even calculation, and must include post-event IV crush expectation.
- **Source**: SKILL.md Position Sizing Step 3.

### 2.20 Total Theta Cost / Viability Check
- **Calc**: `Total_Theta_Cost = Theta_per_day × Expected_Holding_Days`. Rule: if Total_Theta_Cost > expected gross profit from the directional move, trade is not viable regardless of directional conviction.
- **Source**: SKILL.md Position Sizing Step 4; `references/risk_and_adjustments.md` (Pre-Trade Checklist).

### 2.21 Delta-Hedge Futures Requirement
- **Calc**: `Futures_needed = Current_Net_Delta × Total_Lots × Lot_Size`. If net Delta positive → sell futures to neutralize; if negative → buy futures.
- **Source**: `references/risk_and_adjustments.md` (Technique 2 — Delta Hedge via Futures).

### 2.22 Delta-Hedge Cascade Numeric Formula
- **Calc**: Initial hedge = `OI_lots × |Delta_initial| × lot_size`. After an N-point drop, `New_Delta = -0.50 − (Gamma × N)`; extra forced selling = `OI_lots × ΔDelta × lot_size`.
- **Worked values**: 72,000 lots OI, Delta_initial = -0.50 → Initial hedge = 900,000 units. After 50-pt drop: New_Delta = -0.60, extra selling = 180,000 units. After 100-pt drop: New_Delta = -0.70, extra selling = 360,000 units. Cascade_intensity ∝ OI × Gamma² (maximized on expiry day).
- **Source**: `references/market_structure_gex.md` (Delta Hedge Cascade — Cascade Formula).

### 2.23 VWAP (Volume Weighted Average Price)
- **Calc**: `VWAP = Σ(Number of contracts traded × Price) / Total contracts traded`.
- **Tells you alone**: The volume-true average price institutions benchmark execution against.
- **Cannot tell alone / must pair with**: Used as entry-timing only (lowest-priority signal in the 5-signal hierarchy), never a primary directional signal.
- **Source**: SKILL.md signal hierarchy (#5); Wyckoff 2.0 synthesis formula list.

### 2.24 Value Area Statistics (Volume Profile)
- **Calc/definitions**: Value Area = price range containing 68.2% of total traded volume (1 SD of a Gaussian-shaped volume distribution); VAH/VAL = its upper/lower bounds; Rejection Area = remaining 31.8% outside VA; 2 SD ≈ 95.4% of data.
- **Tells you alone**: Where the market considers price "fair" vs "unfair."
- **Cannot tell alone / must pair with**: Should be paired with Order Flow at the VAH/VAL/VPOC/LVN boundary specifically — Order Flow signals in the middle of an empty range are explicitly called "noise" by the source material.
- **Source**: Wyckoff 2.0 synthesis (Auction Market Theory & Volume Profile Formulas).

### 2.25 Order Flow Spread / Crossing Logic
- **Calc**: `Spread = ASK − BID`. Crossing logic: Buy Market × Sell Limit = printed in ASK column; Sell Market × Buy Limit = printed in BID column. Closing a short position via stop-loss = Buy Stop → prints in ASK; closing a long via stop-loss = Sell Stop → prints in BID.
- **Tells you alone**: Liquidity tightness (spread) and the mechanical origin of each print.
- **Cannot tell alone / must pair with**: A single print in BID/ASK cannot by itself tell you WHY (new position vs. stop-loss vs. take-profit) — must be combined with structural context (Volume Profile boundary, prior price action) per the book's own stated limitation.
- **Source**: Wyckoff 2.0 synthesis (Order Flow Relations).

### 2.26 Put-Call Parity (two equivalent forms given in source)
- **Form A**: `Stock + Put + Interest − Dividend − Strike = Call`
- **Form B**: `Call + Strike − Interest + Dividend = Put + Stock`
- **Note (algebraic check)**: These two forms are algebraically identical when rearranged (both reduce to Call = Stock + Put + Interest − Dividend − Strike); flagged here for traceability since the source presents them in two different passages with different sign groupings, but they are NOT in actual conflict.
- **Tells you alone**: The mathematically forced relationship locking a call's price to its corresponding put, stock, and carrying costs.
- **Cannot tell alone / must pair with**: Used to construct synthetics (synthetic long stock = long call + short put; synthetic long call = long stock + long put; synthetic long put = short stock + long call).
- **Source**: Passarelli synthesis (two separate passages); Natenberg synthesis (Synthetics section, "Synthetic Positions" relations).

### 2.27 Black-Scholes PDE and Closed-Form
- **PDE**: ∂V/∂t + ½σ²S²∂²V/∂S² + rS∂V/∂S − rV = 0
- **Call**: C(S,t) = S·e^(−q(T−t))·N(d1) − K·e^(−r(T−t))·N(d2)
- **Put**: P(S,t) = K·e^(−r(T−t))·N(−d2) − S·e^(−q(T−t))·N(−d1)
- **d1** = [ln(S/K) + (r−q+σ²/2)(T−t)] / [σ√(T−t)]; **d2** = d1 − σ√(T−t)
- **Tells you alone**: Theoretical "fair" option price under stated assumptions (random walk, lognormal terminal prices, continuous compounding).
- **Cannot tell alone / must pair with**: Relies on volatility input (σ) which is itself unknown/forecasted — the model's output is only as good as the IV/HV estimate fed in.
- **Source**: options-pricing-and-greeks GitHub README (Mathematics section); Natenberg synthesis (Black-Scholes Assumptions).

### 2.28 Monte Carlo Option Pricing
- **Calc**: V₀ = e^(−rT) · E_Q[V_T]; GBM discretization: S_(t+Δt) = S_t · exp[(r−q−σ²/2)Δt + σ√Δt·Z], Z~N(0,1); Estimator: V₀ ≈ e^(−rT) · (1/N)Σ V_T(i); Standard Error = σ_MC/√N.
- **Tells you alone**: A simulation-based price estimate that converges to Black-Scholes under the same assumptions, useful for validating/cross-checking and for path-dependent payoffs.
- **Cannot tell alone / must pair with**: Should be cross-compared against Black-Scholes output (the GitHub tool explicitly computes a "Difference %" between the two methods as a model-accuracy check).
- **Source**: options-pricing-and-greeks GitHub README (Monte Carlo Simulation section).

### 2.29 Second-Order Greeks
- **Charm**: ∂²V/∂S∂t — rate of change of Delta w.r.t. time; used to maintain Delta-hedges over time.
- **Speed**: ∂³V/∂S³ — rate of change of Gamma w.r.t. underlying; risk management of large moves.
- **Color**: ∂²V/∂S²∂t — rate of change of Gamma w.r.t. time; used in Gamma-trading strategies over time.
- **Zomma**: ∂³V/∂S²∂σ — rate of change of Gamma w.r.t. volatility; volatility risk in Gamma trading.
- **Veta**: ∂²V/∂σ∂t — rate of change of Vega w.r.t. time; long-term volatility trading.
- **Volga**: ∂²V/∂σ² (Vega convexity) — rate of change of Vega w.r.t. volatility; advanced volatility trading strategies.
- **Tells you alone**: Each measures a specific second-order curvature/decay interaction not captured by the five primary Greeks.
- **Cannot tell alone / must pair with**: These are explicitly advanced/secondary risk dimensions layered on top of the primary Greeks; the GitHub tool treats them as supplementary diagnostics, not standalone decision inputs.
- **Source**: options-pricing-and-greeks GitHub README ("Second-Order Greeks").

### 2.30 Kelly Criterion
- **Calc**: f = p/a − q/b, where f = fraction of wealth to bet, p = win probability, q = loss probability (1−p), b = fraction gained on win, a = fraction lost on loss.
- **Tells you alone**: The mathematically optimal bet fraction to maximize long-run compounding growth while avoiding ruin.
- **Cannot tell alone / must pair with**: Requires accurate estimates of p, a, b — a miscalibrated win-probability input produces a miscalibrated Kelly fraction; commonly used at half-Kelly in practice for safety margin (referenced conceptually).
- **Example**: b=1 (double on win), a=1 (lose wager), p=2/3, q=1/3 → f = 2/3 − 1/3 = 1/3 (bet one-third of bankroll).
- **Source**: QUANT BIBLE synthesis (Trading and Market Making section; Five Rings question-bank entry).

### 2.31 Expected Value / Expectancy (Trading)
- **Calc**: E = (W × P_w) − (L × P_l), where W = avg winning trade size, P_w = win probability, L = avg losing trade size, P_l = loss probability.
- **Tells you alone**: Whether a strategy is mathematically profitable over the long run regardless of win rate.
- **Cannot tell alone / must pair with**: Must be evaluated net of transaction costs/slippage; a positive E can still fail live if costs aren't included.
- **Source**: Institutional Quant Blueprint synthesis ("The Reality Check: The Key to Profits").

### 2.32 Probability/Statistics Formula Set (QUANT BIBLE)
- **Conditional probability**: P(A|B) = P(A∩B)/P(B)
- **Bayes' Theorem**: P(A|B) = P(B|A)P(A)/P(B)
- **Law of Total Probability**: P(B) = P(B|A)P(A) + P(B|¬A)P(¬A)
- **Expected value (discrete)**: E[X] = Σx·p(x); linearity holds even for dependent variables: E[X₁+...+Xₙ] = E[X₁]+...+E[Xₙ]
- **Variance**: Var(X) = E[X²] − E[X]²; Var(aX+b) = a²Var(X) (source itself flags its own document's stray "+b" as a typo)
- **Covariance**: Cov(X,Y) = E[XY] − E[X]E[Y]; Cov(X,X) = Var(X) (source flags a stray negative sign in its own document as a typo)
- **Correlation**: ρ(X,Y) = Cov(X,Y)/√(Var(X)Var(Y))
- **Binomial PMF**: p_X(x) = C(n,x)·pˣ·q^(n−x)
- **Poisson PMF**: p_X(x) = λˣe^(−λ)/x!
- **LLN**: sample mean →(P, a.s.) population mean as n→∞
- **CLT**: √n·(X̄ₙ−μ)/σ →(d) N(0,1)
- **Confidence interval**: θ̂ ± (σ/√n)·q_(α/2)
- **Tells you alone**: Foundational probability mechanics for any signal-confidence work (e.g., quantifying how confident the Direction Scorer should be in a given layer score).
- **Cannot tell alone / must pair with**: These are general-purpose statistical tools, not market-specific signals — must be applied to actual market data (e.g., historical win rates) to become decision-useful.
- **Source**: QUANT BIBLE synthesis (Probability Fundamentals, Distributions table, Statistics Fundamentals).

### 2.33 OLS Regression Mechanics
- **Calc**: β̂ = (XᵀX)⁻¹Xᵀy; RSS(β) = Σ(yᵢ−xᵢᵀβ)²; Z-score (single coefficient): z_j = β̂_j/(σ̂√v_j); F-statistic (groups): F = [(RSS₀−RSS₁)/(p₁−p₀)] / [RSS₁/(N−p₁−1)].
- **Tells you alone**: Best-fit linear relationship and whether individual/grouped coefficients are statistically distinguishable from zero (|z|>2 ≈ 95% confidence rule of thumb given in source).
- **Cannot tell alone / must pair with**: A high z-score alone doesn't guarantee economic significance or out-of-sample stability — must be backtested.
- **Source**: QUANT BIBLE synthesis (Data Science & Regressions; Evaluating Regression Models section).

### 2.34 Ridge / Lasso Regularization
- **Ridge (L2)**: objective adds +λΣβⱼ²; solution β̂ = (XᵀX+λI)⁻¹Xᵀy — shrinks all coefficients proportionally, rarely to exactly zero.
- **Lasso (L1)**: objective adds +λΣ|βⱼ|; can truncate less-important variables to exactly zero (feature selection).
- **Tells you alone**: A way to control model complexity/overfitting on correlated or high-dimensional feature sets.
- **Cannot tell alone / must pair with**: λ must be tuned (e.g., via cross-validation, not specified in source) — too high λ over-shrinks, too low approaches plain OLS overfitting.
- **Source**: QUANT BIBLE synthesis (Dimensionality Reduction).

### 2.35 Omitted Variable Bias (OVB)
- **Calc**: OVB = β^s − β^l = π₁γ, where β^s = short-regression coefficient (missing control), β^l = long-regression coefficient (with control), π₁ = correlation of omitted variable with treatment, γ = effect of omitted variable on outcome.
- **Tells you alone**: Direction/rough magnitude of bias from leaving out a confounding variable.
- **Cannot tell alone / must pair with**: Only qualitative/directional in practice per the source ("allows economists to qualitatively estimate which direction the bias is skewing") — not a precise correction.
- **Source**: QUANT BIBLE synthesis (Econometrics).

### 2.36 Natenberg Forward Price / Carrying Cost
- **Calc (futures)**: Forward_Price = Current_Price. **Calc (stock)**: Forward_Price = Current_Price + Carrying_Costs − Dividends; Carrying_Cost = Interest_Rate × (Days/365) × Asset_Value.
- **Tells you alone**: The true "break-even" future price a pricing model should center its distribution on — NOT simply today's spot price for dividend-paying/financed assets.
- **Cannot tell alone / must pair with**: Must be combined with volatility input to build the full lognormal price distribution used in theoretical valuation.
- **Worked example**: S=₹3,100, r=7%, t=30/365, D=0 → Carrying Cost ≈ ₹17.83 → Forward Price ≈ ₹3,117.83.
- **Source**: Natenberg synthesis (Forward Pricing and Expected Return; detailed worked example).

### 2.37 Natenberg Daily/Weekly Volatility Slicing
- **Calc**: Daily_Volatility% = Annual_Volatility/16 (√256 trading days); Weekly_Volatility% = Annual_Volatility/7.2 (√52 weeks). 1-day price change = Daily_Volatility% × Underlying_Price.
- **Tells you alone**: Converts an annualized IV figure into a usable day-to-day expected move.
- **Cannot tell alone / must pair with**: This is essentially the same square-root-of-time mechanic as the VIX daily/weekly formulas in 2.8/2.9, confirming consistency across two independent source sections (Natenberg synthesis and nifty-options-pro skill) rather than redundancy.
- **Example**: Stock at 45, annual vol 28% → daily vol 1.75% → ₹0.79 expected 1-day move (68% confidence).
- **Source**: Natenberg synthesis (Volatility and the Square Root of Time).

### 2.38 Eurodollar/Interest-Rate Contract Transformations
- **Calc**: Contract_Value = 100 − Listed_Price; Model_Exercise_Price = 100 − Listed_Exercise_Price (note: calls must be evaluated as puts and vice versa under this transform); Daily_Price_Change = (Annual_Volatility/16) × (100 − Listed_Price).
- **Tells you alone**: How to adapt a standard option pricing model to instruments quoted as 100-minus-yield.
- **Cannot tell alone / must pair with**: Not directly applicable to Nifty options (equity index, not rate-indexed) — included for completeness since it appears in the source as a general Natenberg mechanic; flagged as likely out-of-scope for the AXIS Nifty system specifically.
- **Source**: Natenberg synthesis (Eurodollar/Interest Rate Transformations).

### 2.39 Delta-Neutral Position / Total Delta
- **Calc**: Total_Delta_Position = Σ(# of Options × Option Delta) + (# of Underlying × Underlying Delta); Delta-neutral when Total_Delta_Position = 0. Underlying contract Delta is always defined as 100 (Natenberg's scaling convention) or 1 (per-share convention, used elsewhere in source) — note scale differs across passages but concept is identical.
- **Tells you alone**: Whether a multi-leg position has any net directional exposure.
- **Cannot tell alone / must pair with**: Must be recalculated continuously as Gamma moves Delta (dynamic hedge), not a one-time calculation.
- **Source**: Natenberg synthesis (Delta-Neutral Hedging relations); detailed worked examples (Section 3 below).

### 2.40 STT (Securities Transaction Tax)
- **Calc**: ITM expiry exercise: STT = 0.125% × Intrinsic Value. Regular sell-to-close: STT = 0.0625% × Sell Premium Value.
- **Tells you alone**: The specific tax cost difference between letting an option expire ITM vs. squaring it off.
- **Cannot tell alone / must pair with**: Must be checked against position size near expiry — the rule of thumb given is to always square off ITM options before 3:00 PM on expiry day.
- **Example**: 22,000 CE, Nifty closes 22,300, intrinsic = 300×75 = ₹22,500 → STT = ₹28. Larger position with ₹2,25,000 intrinsic → STT = ₹281.
- **Source**: Nifty Options Trading Guide; nifty-options-pro `references/risk_and_adjustments.md` and `references/strategies_and_setups.md`; Lot Size and Margin article (uses lot size 25 for SKILL.md-era examples, while base guide article uses 75 — see Coverage Check note on lot-size inconsistency).

### 2.41 F&O Turnover (Tax)
- **Calc**: F&O Turnover = absolute sum of all profits AND losses across trades (not net P&L). Tax audit mandatory if turnover > ₹10 crore (Section 44AB); presumptive audit may apply if turnover > ₹1 crore and profit < 6% of turnover.
- **Source**: Nifty Options Adjustments Guide article; `references/risk_and_adjustments.md` (Tax Implications).

### 2.42 Transaction Cost Breakdown (per lot round trip)
- **Calc**: Brokerage ≈ ₹20(buy)+₹20(sell) = ₹40; STT (regular) = 0.0625% on sell value; Exchange charges ≈ ₹30-40; GST = 18% on (brokerage+exchange) ≈ ₹12; **Total ≈ ₹85-95 per lot round trip**.
- **Source**: Nifty Lot Size and Margin article.

### 2.43 Capital/Position Sizing Table
| Capital | Lots | Max Risk (2%) | Monthly Target Range |
|---|---|---|---|
| ₹3,00,000 | 1-2 | ₹6,000 | ₹8,000-15,000 |
| ₹5,00,000 | 2-4 | ₹10,000 | ₹15,000-25,000 |
| ₹10,00,000 | 4-8 | ₹20,000 | ₹30,000-50,000 |
- **Source**: SKILL.md Position Sizing Framework; Nifty Options Adjustments Guide; Nifty Earnings Season article (all three repeat this identical table — confirms it as a fixed reference figure, not a contradiction).

### 2.44 5-Signal Expiry-Day Detection Score
- **Calc**: GEX<0 → +3; VIX at/near Weak Low → +2; Overnight OI build >50% → +2; PCR rising + GEX negative (trap signal) → +1; VIX CHoCH/BOS upward → +1. Score ≥5 → buy OTM puts (use Down_Target formula). Score 2-4 → reduce size, no bias. Score ≤1 → sell premium/range trade.
- **Tells you alone**: A composite, weighted pre-market checklist score for cascade-day directional conviction.
- **Cannot tell alone / must pair with**: Designed explicitly as a multi-signal aggregator — by construction it should not be substituted with any single one of its five inputs.
- **Source**: SKILL.md "Expiry Day 9:15 AM Detection System."

### 2.45 Wyckoff Law of Supply and Demand
- **Calc (relations, not numeric formula)**: Demand > Supply → Price↑; Supply > Demand → Price↓; Supply = Demand → Price↔.
- **Source**: Wyckoff 2.0 synthesis (formula list).

### 2.46 Price + Time + Volume = Value
- **Calc (conceptual relation)**: A price level only becomes accepted "Value" if enough Time is spent there with enough Volume transacted — price alone is just an "advertisement," not proof of value.
- **Tells you alone**: A qualitative test for whether a price level is structurally significant.
- **Cannot tell alone / must pair with**: Must be operationalized via the Value Area/VPOC volume-profile statistics (2.24) to become numerically actionable.
- **Source**: Wyckoff 2.0 synthesis (Auction Market Theory).

---

## 3. WORKED EXAMPLES — STRUCTURED

**E1 — STT Trap, small position**
- Setup: Bought 22,000 CE, Nifty closes at 22,300 on expiry.
- Data: Intrinsic = 300×75 = ₹22,500.
- Outcome: STT on ITM expiry = 0.125% × 22,500 = ₹28.
- Predictive signal: Knowing the option is ITM into the close at any point before 3 PM is sufficient warning to square off and avoid the higher STT rate — no advance lead time needed, it's a same-day mechanical rule.
- Classification: Not bait/trigger/harvest — a pure cost-mechanics example, not a market-psychology pattern.
- Source: Nifty Options Trading Guide.

**E2 — STT Trap, larger position (same mechanic, different scale)**
- Setup: Hypothetical larger position with ₹2,25,000 intrinsic value at expiry.
- Outcome: STT = 0.125% × 2,25,000 = ₹281.
- Source: Nifty Options Trading Guide.

**E3 — ATM Straddle Sell, Nifty 24,200**
- Setup: Positive GEX, stable VIX, no major events, 7 DTE.
- Data: Sell 24,200 CE @ ₹180, Sell 24,200 PE @ ₹160, total credit ₹340 × 25 = ₹8,500. Breakeven 23,860-24,540.
- Outcome (illustrative, not a real dated trade): Max profit ₹8,500 if Nifty closes at 24,200.
- Predictive signal: GEX-positive + stable-VIX environment identification is the precondition that should be checked before entry.
- Classification: Not bait/trigger/harvest — a strategy template example.
- Source: `references/strategies_and_setups.md`.

**E4 — Iron Condor, Nifty 24,200**
- Setup: Positive GEX, sideways trend, elevated IV, 5-7 DTE.
- Data: Sell 24,400 CE + Buy 24,600 CE; Sell 24,000 PE + Buy 23,800 PE. Net credit ≈₹80-120/lot (₹2,000-3,000/lot). Max loss = (200−100)×25 = ₹2,500/side.
- Outcome (template): Probability of profit 55-65% when wings placed 200+ pts from ATM.
- Classification: Strategy template, not a dated trade.
- Source: `references/strategies_and_setups.md`.

**E5 — Vertical Debit Spread, Nifty 24,200 bullish**
- Setup: Clear directional view, GEX confirms, IV slightly elevated.
- Data: Buy 24,200 CE @ ₹180, Sell 24,400 CE @ ₹80. Net debit ₹100×25=₹2,500. Max profit (200−100)×25=₹2,500 if Nifty>24,400 at expiry. Max loss = ₹2,500.
- Classification: Strategy template.
- Source: `references/strategies_and_setups.md`.

**E6 — OTM Put Buy / Cascade Signal Trade, June 23, 2026 (real dated example, most detailed in material)**
- Setup: Expiry day; GEX negative; VIX at Weak Low; 5-signal score ≥5.
- Data: Nifty at 24,127 at open. GEX: −3.94M Cr. VIX: 12.89 (Weak Low). Down target formula: 24,100 − 196 = 23,904. Action: Buy 23,850 PE @ ₹12-15.
- Outcome: 23,850 PE moved from ₹12 to ₹30+ (VIX spike × Delta gain combined). Actual session low: 23,865 (vs. formula target 23,904 — error 39 pts/0.16%). Gamma flip level ≈24,050; decline above flip was slow, decline below flip was violent/self-reinforcing. VIX itself rose from 12.89 to 14.05 (+9% intraday). Puts overall gained 276-425% (per VIX×GEX combined-effect note).
- Predictive signal and lead time: VIX's own 15-minute Weak Low / CHoCH / BOS structure (per Pattern 1.11) is explicitly noted elsewhere as giving multi-day advance warning in general, though for this specific dated example the signals cited (GEX, VIX Weak Low, 5-signal score) are same-day pre-market reads, not multi-day-ahead in this instance.
- Classification: This is the clearest BAIT→TRIGGER→HARVEST-shaped example in the material even though the source doesn't label it as such: Bait = price holding near 24,127 looking orderly pre-10am; Trigger = GEX negative + VIX Weak Low + score≥5 detected at 9:15-10:00am; Harvest = cascade through the 24,050 flip level down toward 23,865-23,904 zone, captured via the 23,850 PE.
- Source: `references/strategies_and_setups.md` (Strategy 6); `references/market_structure_gex.md` (Gamma Flip Level real example; VIX and GEX Combined effect; GEX Fibonacci targets example — all describing the same June 23, 2026 session from different angles).

**E7 — GEX Fibonacci + VIX Target Combined Zone (same June 23, 2026 session, additional cross-check data)**
- Data: VIX target = 23,904; GEX Fib target = 23,895; actual low = 23,865. Combined target zone 23,895-23,904 vs actual — within 40 pts.
- Predictive signal: Combining two independently-derived targets (VIX-based and GEX-Fibonacci-based) and finding them in close agreement is presented as a confidence-multiplier for the cascade thesis.
- Source: `references/market_structure_gex.md` (GEX Fibonacci Extension Targets section).

**E8 — Calendar Spread (template, no specific numbers given)**
- Setup: Front-month IV lower than back-month, or stable range environment. Sell near-expiry ATM, buy far-expiry ATM.
- Outcome described qualitatively: profits if near-dated decays faster than far-dated; risk if a large sudden move hits both legs.
- Source: `references/strategies_and_setups.md` (Strategy 7).

**E9 — Straddle Roll Adjustment Example**
- Setup: Sold 24,200 straddle (from E3-style position). Nifty moves to 24,400.
- Action: Roll 24,200 CE to 24,600 CE. New credit received partially offsets the loss on the closed leg.
- Source: `references/risk_and_adjustments.md` (Technique 1 — Rolling the Tested Leg).

**E10 — Jade Lizard, Nifty (template)**
- Data: Sell 22,800 PE @ ₹50; Sell 23,300 CE @ ₹45; Buy 23,400 CE @ ₹25. Total premium = 50+45−25 = ₹70/unit = ₹1,750/lot. Upside risk: zero (if structured correctly, put-side premium covers any call-spread loss). Downside risk begins below 22,730 (put strike minus total premium).
- Source: Nifty Jade Lizard Strategy article.

**E11 — Lot Size / Margin Worked Numbers**
- Data: 1-pt move = ₹25/lot (current Nifty lot size 25, effective since April 2023, reduced from 50). 100-pt move = ₹2,500/lot. 200-pt move = ₹5,000/lot. Premium ₹50×25=₹1,250/lot; ₹100×25=₹2,500/lot; ₹200×25=₹5,000/lot. Margin (approx, April 2026): Futures 1 lot ≈₹1,45,000 total; naked option selling ≈₹1,45,000 total; 100-pt-wide credit spread ≈₹45,000 total.
- Note: An earlier section of the same source family (Nifty Options Trading Guide, "premium" example) uses lot size 75 in its STT example (E1/E2 above), while this Lot Size article and the SKILL.md/strategy examples consistently use lot size 25 — flagged explicitly in Coverage Check as an inconsistency to resolve before hard-coding lot size into AXIS.
- Source: Nifty Lot Size and Margin Explained article.

**E12 — Natenberg Dynamic Hedge, June Futures Example (most detailed Greeks-mechanics walkthrough in the material)**
- Setup: June futures at 101.35, interest rate 8%, 10 weeks to expiration, forecast volatility 18.3%.
- Data: Model says June 100 Call theoretical value = 3.88; market price = 3.25 (underpriced by 0.63). Trader buys 100 calls @3.25 (cost ₹325.00 notional units). Call Delta = 57 → position Delta = +5,700. Hedge: sell 57 futures (−5,700 Delta) → net Delta = 0.
- Week 1: futures rise to 102.26; call Delta rises to 62 → position Delta = +500 → sell 5 more futures.
- Week 2: futures fall to 99.07; call Delta falls to 46 → position Delta = −1,600 → buy 16 futures.
- Outcome (conceptual): Mechanical rebalancing forces buying low / selling high repeatedly; over the full 10 weeks the accumulated hedge cash flow should theoretically equal the original 0.63 mispricing per option if the volatility forecast was accurate, realizing profit independent of market direction.
- Predictive signal: The identification of the 0.63 theoretical-vs-market mispricing at trade inception is the entire signal; everything after is mechanical execution, not further prediction.
- Classification: Not bait/trigger/harvest (this is a market-maker volatility-arbitrage mechanic, not a retail trap pattern).
- Source: Natenberg synthesis (Detailed Working: The Delta-Neutral Hedge; repeated with identical numbers in two separate synthesis passes in the source material — confirms internal consistency).

**E13 — Natenberg Asian Paints Notation Walkthrough**
- Setup: Asian Paints spot (S) = ₹3,100; Strike (X) = ₹3,000 Call; 30 days to expiry; Option Premium = ₹180; risk-free rate 7%; dividends = ₹0.
- Data: Intrinsic Value = 3,100−3,000 = ₹100. Time Value = 180−100 = ₹80. Carrying Cost = 0.07×(30/365)×3,100 ≈ ₹17.83. Forward Price = 3,100+17.83−0 = ₹3,117.83. Call Delta = 65 (given). Buying 1,000 calls → position Delta = +650.
- Hedge: Sell short 650 shares of Asian Paints to bring net Delta to 0.
- Classification: Pure mechanics walkthrough, not bait/trigger/harvest.
- Source: Natenberg synthesis ("Detailed Working: Pricing and Hedging in Practice").

**E14 — Casino/Roulette Theoretical Edge Analogy**
- Setup: A single roulette bet.
- Data: Mathematical expected return ≈95¢ per ₹1 wagered (the house's 5¢ edge).
- Outcome/lesson: Professional options trading is framed as acting like "the casino" — identifying instances where market price diverges from theoretical/statistical fair value, then selling overvalued / buying undervalued options to capture that structural edge repeatedly.
- Source: Natenberg synthesis ("The Casino Mindset").

**E15 — Kaushik 4-Stroke Method, NIFTY Future**
- Setup: NIFTY future closes at 10,873.30; weekly expiry target.
- Data: Nearest ITM call strike = 10,850; nearest "ITM" put strike used = 10,900 (note: source text itself states the put strike is "slightly higher," which is consistent with ITM put definition since 10,900>10,873.30).
- Rule: When 10,850 CE trades above the prior day's high, buy targeting +₹10 profit; if price opens below prior day's low, exit/liquidate the call instead. Same logic mirrored for puts on bearish view.
- Outcome: Illustrative method, not a dated real trade with a stated final P&L.
- Source: Options Trading Handbook (Kaushik) synthesis.

**E16 — Kaushik Call Ratio Spread, NIFTY**
- Setup: NIFTY at 9,105.30.
- Data: Buy 9,100 CE (ITM); sell two 9,400 CE (1:2 ratio).
- Outcome: Profitable if NIFTY closes below 9,400 at expiry (capped at premium difference); losses begin if NIFTY closes beyond 9,400 (unlimited risk on the uncovered second short call).
- Source: Options Trading Handbook (Kaushik) synthesis.

**E17 — Kaushik Covered Call, Reliance**
- Setup: 500 Reliance shares held @ ₹1,400.
- Data: Sell call strike ₹1,500, premium ₹36/share.
- Outcome: If price stays ₹1,400-1,500 through expiry, seller keeps the ₹36 premium without assignment; if price exceeds ₹1,500, shares are called away (still a profitable outcome for the seller, capped upside).
- Source: Options Trading Handbook (Kaushik) synthesis.

**E18 — Kaushik "Money Tree" ETF/SIP Strategy**
- Setup: Build NIFTY BeES / Bank BeES position via systematic weekly investment (e.g., ₹5,000/week) until reaching 7,500 units.
- Data: Once 7,500 units reached, begin writing covered calls starting at a strike 5% above current market value.
- Outcome (qualitative): Combines diversified low-cost index exposure with recurring premium income; reinvest premiums to compound.
- Source: Options Trading Handbook (Kaushik) synthesis.

**E19 — Poisson Distribution Example (Quant Bible)**
- Setup: Hypothetical model expecting an average of λ=4 "market crashes" per decade.
- Data: P(x=0 crashes) = 4⁰e⁻⁴/0! = e⁻⁴ ≈ 0.018 (1.8% chance of zero crashes in the decade).
- Source: QUANT BIBLE synthesis (Probability Distributions deep-dive).

**E20 — Kelly Criterion Sock-Drawer-Style Bet (Quant Bible / Five Rings style)**
- Setup: A bet that doubles your wager on a win (b=1), loses the full wager on a loss (a=1), with win probability p=2/3.
- Data: f = p/a − q/b = 2/3 − 1/3 = 1/3.
- Outcome: Optimal bet size = one-third of bankroll to maximize long-run compounding growth.
- Source: QUANT BIBLE synthesis (Kelly Criterion deep-dive).

**E21 — Two Sigma NYC Housing Prices Case Study**
- Setup: Predictive model for NYC housing prices.
- Data/method: Categorical geographic data → one-hot encoding; discrete variables (bedrooms/bathrooms) kept as-is; heavily skewed variables (square footage) → log-transformed toward normal distribution.
- Source: QUANT BIBLE synthesis (Quant Research Case Studies).

**E22 — QuantCo Opera House Ticket Pricing Case Study**
- Setup: Dynamic seat-pricing model.
- Data/method: KNN used on spatial features (distance/angle to stage); an engineered "scarcity" variable added to capture FOMO-driven willingness-to-pay as available seat inventory shrinks closer to the event date.
- Source: QUANT BIBLE synthesis.

**E23 — Two Sigma CitiBikes Case Study**
- Setup: Predictive model for bike-share docking station demand.
- Data/method: Cyclical time/season features handled via one-hot buckets or cyclic splines; multicollinearity between overlapping variables (temperature vs. weather condition) explicitly addressed.
- Source: QUANT BIBLE synthesis.

**E24 — Bayesian Brainteasers Referenced (Taxi Cab / Ebola Test)**
- Setup: Classic conditional-probability brainteasers used in quant interviews to illustrate Bayesian updating.
- Data: Not worked out in the source material — only named as examples of the genre.
- Source: QUANT BIBLE synthesis (Probability Fundamentals — referenced, not solved, in the provided text).

**E25 — NSE Bank Nifty Strategy Tables (structural reference, not single examples)**
- Setup: Full bullish/bearish/neutral strategy tables (Long Call, Short Put, Call Spread, Put Spread, Synthetic Call, Covered Call, Collar, Long Combo for bullish; mirrored bearish set; Straddle/Strangle/Butterfly/Condor/Box variants for neutral).
- Data: Generic payoff/risk/reward structures per strategy, no specific numeric strikes given (these are templates, treated as Formula-Reference-adjacent rather than dated worked examples).
- Source: NSE "Bank Nifty Options Strategies" booklet synthesis.

**E26 — Five-Signal Score Application (Generic Template, Reused from E6's mechanism)**
- Setup: Pre-market expiry-day checklist run at 9:15 AM.
- Rule restated as worked logic: Score≥5 → buy OTM puts using the Down_Target formula; Score 2-4 → reduce size, no bias; Score≤1 → sell premium/range trade.
- Source: SKILL.md ("Expiry Day 9:15 AM Detection System").

---

## 4. INSTITUTION-DETECTION RULES

1. **IF** Net GEX is negative **AND** PCR is rising **THEN** interpret as a bearish/cascade-fuel signal (put writers loading forced-selling obligations), NOT a bullish/protective signal. **CONFIDENCE: HIGH** — stated identically and independently in both SKILL.md (Common Retail Errors) and `references/market_structure_gex.md` (PCR section), and matches the real June 23, 2026 worked example mechanics.

2. **IF** Net GEX is positive **THEN** Max Pain is a valid pinning target; **IF** Net GEX is negative **THEN** Max Pain should be ignored entirely. **CONFIDENCE: HIGH** — stated in SKILL.md signal hierarchy AND in `references/market_structure_gex.md` independently, with consistent wording in both.

3. **IF** Net GEX > 0 **THEN** dealers are net long Gamma and will buy dips/sell rallies, producing range-bound/pinning price action. **IF** Net GEX < 0 **THEN** dealers are net short Gamma and will sell dips/buy rallies, producing trending/amplifying price action. **CONFIDENCE: HIGH** — core mechanic repeated across SKILL.md Quick-Reference Matrix and `references/market_structure_gex.md` GEX Interpretation table; consistent with the June 23 worked example outcome.

4. **IF** spot price crosses the Gamma Flip Level to the downside **THEN** expect the decline to accelerate/become self-reinforcing (vs. slow/orderly decline above the flip). **CONFIDENCE: MEDIUM-HIGH** — mechanism is explained generically and is logically derived from rules #2-3, but only ONE specific dated numeric example (June 23, 2026, flip≈24,050) is provided to validate it empirically in this material.

5. **IF** overnight OI build at the ATM strike exceeds 50% **THEN** treat the session as high-volatility risk and avoid selling naked premium. **CONFIDENCE: MEDIUM** — stated as an explicit rule in two places (SKILL.md detection checklist and `references/market_structure_gex.md` OI Analysis section) but no separate dated worked example beyond its inclusion as one input in the June 23 composite score.

6. **IF** VIX is at a 15-minute "Weak Low" structurally **THEN** treat current vol pricing as complacent and asymmetric-risk-favorable for buying cheap puts. **CONFIDENCE: MEDIUM-HIGH** — stated as a general rule AND supported by the one detailed June 23, 2026 example where VIX Weak Low preceded the cascade.

7. **IF** VIX prints a CHoCH or BOS to the upside on its own structure **THEN** treat this as a leading (not coincident) signal of a coming volatility/price regime shift, and bias toward buying puts. **CONFIDENCE: MEDIUM** — stated explicitly as a rule with no separate fully worked dated example isolating VIX CHoCH alone (it appears bundled into the composite 5-signal score, not validated independently).

8. **IF** price approaches a heavy put-OI strike from above in a falling, negative-GEX market **THEN** expect forced delta-hedge selling to accelerate the decline through that strike (the OI "wall" becomes fuel, not support). **CONFIDENCE: HIGH** — mechanism given with full numeric cascade formula AND matches the qualitative description of the June 23 cascade through the flip level/heavy OI zone.

9. **IF** the 5-signal expiry-day score is ≥5 **THEN** buy OTM puts targeting the VIX Down_Target formula level; **IF** score is 2-4 **THEN** stay neutral/reduce size; **IF** score ≤1 **THEN** sell premium/range trade. **CONFIDENCE: HIGH** for the scoring mechanism's internal logic (explicitly designed as a checklist) but **CONFIDENCE: MEDIUM** for its real-world predictive accuracy, since only ONE fully scored dated example (June 23, 2026, which validated the ≥5/buy-puts branch) is present in this material — the 2-4 and ≤1 branches have no worked dated examples at all.

10. **IF** an Order Flow footprint candle shows strongly positive Delta (aggressive buying dominant) **BUT** the candle closes bearish **THEN** interpret as institutional absorption/Iceberg selling trapping retail buyers, not genuine bullish strength. **CONFIDENCE: HIGH** — explicitly named and explained as the central diagnostic tool ("Delta Divergence Trap") with its own dedicated section in the Wyckoff 2.0 synthesis, though no single fully numeric dated example (e.g., specific Delta print numbers tied to a specific date) is given — it is explained mechanically rather than demonstrated on a real session.

11. **IF** an Order Flow absorption/exhaustion/initiative signal occurs away from a marked Volume Profile boundary (VAH/VAL/VPOC/LVN) **THEN** treat it as unreliable noise; **IF** it occurs AT such a boundary **THEN** treat it as a meaningfully higher-confidence structural signal. **CONFIDENCE: HIGH** — this is an explicit, direct self-warning from the source book itself ("Order Flow is practically useless unless deployed at a strict Volume Profile boundary"), making it one of the most strongly evidenced rules in the entire material precisely because the source is cautioning against over-trusting its own tool category.

12. **IF** VPOC migrates to a new price level and price continues swiftly in the same direction afterward **THEN** treat as healthy continuation (value accepted, market searching for next level). **IF** VPOC migrates but price then stalls/consumes excess time sideways **THEN** treat as a reversal warning (Change of Character). **CONFIDENCE: MEDIUM** — clearly explained mechanism, but presented generically without a specific dated numeric worked example in this material.

13. **IF** price approaches a Low Volume Node (LVN) **THEN** expect a violent/rapid move through it (it's an "unfair" rejected price); **IF** price approaches a High Volume Node (HVN) **THEN** expect consolidation/gravity (price tends to linger). **CONFIDENCE: MEDIUM** — clearly stated as a strategic takeaway for options strike selection, but no dated numeric example given to validate it.

14. **IF** an institution/market-maker accumulates unwanted net inventory **THEN** it will skew its bid/ask away from fair value to incentivize offsetting flow, sacrificing some edge to reduce risk. **CONFIDENCE: MEDIUM** — well-explained mechanism appearing independently in two synthesis sections (QUANT BIBLE and Institutional Quant Blueprint) describing the same underlying behavior, but illustrated only generically/conceptually, not with a specific real dated market example.

15. **IF** a market-making counterparty repeatedly buys as you raise your quoted price **THEN** infer they believe true value is higher than your model, and skew your market upward in response (informational-asymmetry / "trader memory" exploitation). **CONFIDENCE: MEDIUM** — explicit single-source mechanism (QUANT BIBLE), with no second independent corroborating example in this material, and explicitly framed as a market-making/interview-style heuristic rather than something demonstrated on real Nifty data.

16. **IF** Implied Volatility is materially higher than realized/Historical Volatility for the same instrument **THEN** options are statistically overpriced and favor selling strategies; the reverse (IV≈HV or IV<HV) favors buying/neutral strategies. **CONFIDENCE: HIGH** — repeated consistently across Passarelli synthesis ("Fair Game Rule"), Natenberg synthesis (theoretical-value-vs-market-price framework), and the Institutional Quant Blueprint (Volatility Arbitrage description) — three independent sections agree.

17. **IF** OTM puts are priced at structurally higher IV than equidistant OTM calls (skew) **THEN** this reflects persistent institutional demand for downside protection, not random mispricing, and should inform strike/spread selection (e.g., preferring put credit spreads, or choosing Iron Butterfly over standard Butterfly when skew is steep). **CONFIDENCE: HIGH** — repeated independently across at least four separate sections (NSE booklet glossary, Passarelli synthesis ×2, Natenberg synthesis, Quant Bible lognormal discussion).

18. **IF** index-level implied volatility is priced richer than the volume-weighted combination of its constituent single-stock implied volatilities **THEN** a dispersion trade (sell index vol / buy constituent vol) has positive theoretical edge. **CONFIDENCE: MEDIUM** — appears only in the Institutional Quant Blueprint synthesis (single source within this material), with a stated payoff formula but no specific dated numeric Nifty/BankNifty example.

19. **IF** the Total Theta Cost of holding a long-premium position through its expected horizon exceeds the expected gross profit from the anticipated move **THEN** the trade should not be entered, regardless of directional conviction. **CONFIDENCE: HIGH** — stated as an explicit, non-negotiable pre-trade checklist gate in `references/risk_and_adjustments.md`, consistent with the general Theta-discipline theme repeated throughout the Nifty Options Trading Guide and Passarelli/Natenberg syntheses.

20. **IF** a trader catches themselves "hoping" the market reverses rather than following a predefined plan (the HAPI signal) **OR IF** they would not re-enter the exact same position at current prices (the "Would I Do It Now?" rule) **THEN** the position should be closed immediately rather than adjusted. **CONFIDENCE: HIGH** — this discipline rule is independently stated across at least three separate source sections (Passarelli synthesis, Natenberg synthesis, and `references/risk_and_adjustments.md`), making it one of the most cross-corroborated behavioral rules in the entire material.

21. **IF** a short-premium position's underlying moves beyond ~50% of the expected range (≈±150 pts from ATM for a 7-DTE straddle) OR the position's loss reaches 100-150% of credit received **THEN** trigger an adjustment (roll tested leg, delta-hedge via futures, or convert to defined-risk condor). **CONFIDENCE: MEDIUM** — stated as an explicit numeric rule in `references/risk_and_adjustments.md`, but presented once without a separate corroborating dated example beyond the generic straddle-roll illustration (E9).

22. **IF** VIX rises sharply (e.g., +9% intraday) at the same time GEX is negative and price is falling **THEN** long-put returns will be multiplicatively amplified (Delta gain × Vega gain combine), producing outsized percentage gains beyond what Delta alone would predict. **CONFIDENCE: MEDIUM** — mechanism is clearly explained and matches the magnitude of the one detailed June 23, 2026 example (276-425% put gains), but it is the only such example in the material, so the magnitude claim itself is a single data point even though the underlying Delta+Vega additivity logic is mathematically sound or well-established.

23. **CONFLICT CHECK — none found of real substance.** The two differently-worded Put-Call Parity equations (Form A and Form B in Section 2.26) initially appear to disagree but are algebraically identical when rearranged; flagged for traceability, not as a genuine disagreement. The lot-size inconsistency (Nifty Options Trading Guide implying 75 vs. all later SKILL.md/strategy/lot-size articles using 25) IS a genuine factual inconsistency within the source material itself (see Coverage Check) and should be resolved using 25, since it is both the more recent and far more frequently repeated figure across the bulk of the material, and matches the stated "current Nifty lot size... effective since April 2023."

---

## 5. COVERAGE CHECK

**Documents/sections processed (in order encountered in the source file):**
1. "Trading All The Thing" / Nifty Options Trading Guide (NiftyTradingPro, Karthik Subramanian) — basics, Greeks table, Theta table, IV/Vega, 4 strategies (ATM Straddle Sell, Iron Condor, Directional Buying, 0DTE), STT Trap.
2. Trading Option Greeks (Dan Passarelli) — processed across its multiple repeated synthesis passes: core philosophy/modules, detailed structural breakdown, "rules" list, full book breakdown, Foreword-Ch.6 detailed extraction (premium, Greeks, volatility, Put-Call Parity/synthetics), module structure (Parts I-IV / Ch.1-17), volatility skew & Butterfly impact, Delta/Gamma interaction deep-dive.
3. NiftyTradingPro 30-article index list (titles only — no body content given for most listed articles beyond what's separately covered elsewhere in the doc).
4. nifty-options-pro SKILL.md + four reference files in full: `market_structure_gex.md`, `greeks_and_pricing.md`, `strategies_and_setups.md`, `risk_and_adjustments.md`.
5. Nifty Options Adjustments Guide article (generic template, position sizing/risk/tax repeats SKILL.md content).
6. Bookmap and footprint charts orderflow article — processed as supporting Pattern 1.17/1.25 context (core concepts, advantages, optimal conditions, practical application, platform access/pricing — platform pricing details omitted from formula/pattern sections as non-market-data/promotional).
7. Nifty Earnings Season Options Strategy / IV Crush Playbook article (template, repeats capital sizing table).
8. Nifty Lot Size and Margin Explained article — fully processed (E11, 2.40-2.42).
9. Options Trading for the Institutional Investor (Michael C. Thomsett) — processed: core philosophy, five ground rules, model portfolio reference (no specific numbers given in source beyond "10 stocks, $1M"), advanced strategies/risk-awareness list (Bollinger/MACD/RSI mentioned only by name, no formulas given in source for these).
10. QUANT BIBLE (MIT Sloan) — processed across all its repeated synthesis passes: Parts 1-7 overview, full formula compilation, deep-dive on distributions/T-tests/multiple-regression mechanics, strategy/lesson breakdown (market making, betting, data science), institutional-firm breakdown (Jane Street, Two Sigma, Citadel, Optiver, HRT, Virtu, Akuna, Five Rings, SIG, QuantCo), lightweight-algorithm architecture, repeated firm-breakdown passes.
11. Sheldon Natenberg, Option Volatility & Pricing — processed across all its repeated synthesis passes: theoretical pricing/Greeks notation, full formula relations list, detailed worked Delta-neutral hedge example (appears twice with consistent numbers), lognormal distribution/Black-Scholes assumptions deep dive, Asian Paints walkthrough, classic strategy framework (outright long/short, synthetics, dynamic hedging "race").
12. Nifty Jade Lizard Strategy article — fully processed (E10).
13. Options Pricing and Greeks Analysis (GitHub project README) — processed: feature list, Greeks 101 (first- and second-order), Black-Scholes/Monte Carlo math sections. Repository setup/installation instructions, image references, and "Future Improvements" roadmap omitted from the four content sections as they are software-engineering/documentation content, not trading patterns, formulas, examples, or institution-detection rules — noted here rather than silently dropped.
14. NSE "Bank Nifty Options Strategies" booklet synthesis — fully processed: pay-off graph reading convention, full bullish/bearish/neutral strategy tables, glossary (ATM/ITM/OTM/Premium/Time Decay/Volatility/Synthetic).
15. Options Trading Handbook (Mahesh Chander Kaushik) — processed: conservative/risk strategies overview, "Other Perspectives" critique sections (treated as caveats/limitations, not separate patterns, since they critique rather than describe market behavior), 4-stroke method, ratio spread, covered call, money tree ETF/SIP strategy, psychological discipline section, "Practical Tips" (treated as actionable habits, not market patterns — omitted from Pattern Library/Formula/Example/Rule sections as they are personal-productivity suggestions like "start a blog" or "set calendar alerts," not trading signals).
16. Wyckoff 2.0: Structures, Volume Profile and Order Flow — processed across all its repeated synthesis passes: core Wyckoff methodology (events/phases/notation), Volume Profile (VPOC/VA/HVN/LVN/VWAP), Order Flow (BID/ASK/Delta/Imbalance), full formula relations list, detailed mechanics breakdown (3-step turn, Delta Divergence Trap, VPOC migration), sloping ranges/structural failures/SOT, foundational architectural lessons (price-over-volume primacy, robotic-labeling fallacy, order-intention multitude, Adaptive Markets Hypothesis), 4 detailed strategy manuals (Trading Range/Mean Reversion, Reversion/Re-Entry, Continuation/Value Acceptance, Failed Reversion) with entry/stop/target mechanics for each.
17. Institutional Quantitative Blueprint sections (appearing multiple times under headings like "The Institutional Quantitative Blueprint," "Inside the Institutional Trading Firm," "Insider Breakdown of the Top Quant Firms") — processed: algorithm-building pipeline, firm-by-firm strategy breakdown, dispersion trading formula, delta-neutral volatility arbitrage, options market making, volatility skew/smile exploitation, lightweight-algorithm tech stack (Python/pandas/FastAPI/PostgreSQL), institutional silo structure (Quants/Devs/Traders/Risk), strategy table (AMM, StatArb, Latency Arb, Vol Arb/Dispersion).

**Intentionally omitted as genuinely non-usable for this knowledge base (named specifically, with reason):**
- Promotional/affiliate broker content: repeated "Open Exness Account," "Open XM Account," "Our #1 recommendation: XM offers..." blocks, "Free Strategy PDF" / "Free Calculator" call-to-action banners. Reason: pure advertising, zero market-data or trading-rule content.
- FAQ placeholder stubs with no answers given (e.g., "What is the earnings season options strategy on Nifty? How much capital is needed? What is the expected return? Is this strategy suitable for beginners?" appearing as bare question lists with no provided answers across several NiftyTradingPro articles). Reason: genuinely empty of extractable content, not a redundant duplicate of answered content elsewhere.
- Shortform.com signup/marketing block ("signing up for Shortform... Interactive exercises: apply the book's ideas to your own life"). Reason: third-party service promotion, no content.
- Contact info / LinkedIn / email block for the options-pricing-and-greeks GitHub project author. Reason: non-content metadata.
- "Sources & References" stub mentioning "DFSA — Dubai Financial Services Authority" with no further elaborated content. Reason: dangling citation with no attached substantive claim to extract.
- GitHub repository "Getting Started" install instructions (git clone, venv setup, pip install) and "Contributing" section. Reason: software setup instructions, not trading content.

**Ambiguous or hard-to-categorize items flagged for your review (not silently dropped, listed here instead):**
- **Lot size inconsistency**: The original Nifty Options Trading Guide's example table implies a 75-unit lot size ("Premium Cost of the option Rs 150 x 75 (lot size) = Rs 11,250"), while every other article in the source (SKILL.md, all strategy/risk reference files, the dedicated Lot Size article, Jade Lizard article) consistently uses 25 and explicitly states "current Nifty lot size is 25 units (effective since April 2023, reduced from 50)." This is flagged in Rule #23 above as a genuine internal source disagreement, not silently resolved — recommend treating 25 as authoritative for AXIS given it's both more recent and far more frequently repeated, but flagging for your explicit confirmation since it affects every position-sizing formula in Section 2.
- **Model portfolio detail (Thomsett)**: The source explicitly states the Institutional Investor book excerpt provided was front matter/TOC/Preface/Ch.1/Index only — the actual ten-stock model portfolio table and detailed chapter content (chart-based analysis specifics, "1-2-3 Iron Butterfly," "Dividend Collar," exact down-market strategies) are referenced by name only with no worked numbers given in the source material itself. Logged as a known gap, not fabricated.
- **Bookmap/footprint pricing details** ($34-$119/month, DeepCharts/Phidias partnership) — kept out of the four core sections as platform-commercial information, but noted here in case it's useful context for tooling decisions.
- **"Other Perspectives" critique blocks throughout the Kaushik handbook synthesis** (e.g., critiques of the 4-stroke method, ratio spreads, covered calls) — these read as balanced-counterpoint commentary rather than distinct patterns/rules in their own right. They were treated as caveats attached to their parent examples (E15-E18) rather than separate Pattern Library or Rule entries; flag if you'd like them extracted as standalone "failure mode" entries instead.
- **Quant firm culture descriptions** (Jane Street academic/Bayesian focus, SIG trader-memory focus, Citadel CS-split focus, etc.) — these describe interview/hiring culture more than live trading signals. Retained only the portions translatable into Layer B (institutional identity) behavioral patterns (Rules #14-15); the remainder (recruiting style, required reading lists, specific brainteaser question banks) was treated as out-of-scope for a live trading rule library and not reproduced as Pattern/Rule entries.

No content was dropped purely for being "repetitive" — repeated passages (e.g., the Theta-by-DTE table appearing twice, the Natenberg dynamic-hedge example appearing twice, the capital-sizing table appearing three times) were cross-checked against each other and noted as confirming consistency rather than collapsed into a single uncredited entry.

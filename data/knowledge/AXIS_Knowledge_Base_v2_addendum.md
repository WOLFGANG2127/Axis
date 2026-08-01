# AXIS Knowledge Base — Addendum (Part 2)
Continuation of structured extraction — additional entries not fully developed in Part 1, plus expansion of partially-covered items from the Wyckoff strategies, Volume Profile, GEX strategy matrix, pre-trade checklists, and lognormal pricing sections.

---

## 1. PATTERN LIBRARY (continued — entries 1.34 onward)

### 1.34 "P-Shape" Volume Profile (Bullish Trending Breakout)
- **Data conditions**: Volume Profile accumulates its bulk at the top of the session range, with a thin "tail" extending downward — looks like the letter P. Indicates price opened low, trended up strongly, and the majority of the session's volume was done at the upper levels. Signals bullish continuation / institutional accumulation of long positions at higher prices.
- **Confused with**: A normal day's distribution. Distinguished specifically by the asymmetric top-heavy volume shape versus the symmetric "D-shape" of a balanced day.
- **Layer**: Live order flow / Volume Profile (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Strategy 3 — "P-shape" and "b-shape" profile topology descriptions).

### 1.35 "b-Shape" Volume Profile (Bearish Trending Breakout)
- **Data conditions**: Volume accumulates at the bottom of the session range, thin tail extending upward — letter "b." Price opened high, trended down, majority of volume done at lower levels. Signals bearish continuation / institutional short-position loading at lower prices.
- **Confused with**: A P-shape (visually they are inversions of each other). Distinguished by the asymmetric bottom-heavy volume shape.
- **Layer**: Live order flow / Volume Profile (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Strategy 3 — Continuation Principle).

### 1.36 "D-Shape" Volume Profile (Balanced/Neutral Session)
- **Data conditions**: Volume forms a symmetric bell curve across the session range with a clear central VPOC and balanced tails — classic Gaussian bell shape, the "D." Indicates balanced buyer/seller activity, no strong directional institutional commitment. Underlying condition for mean-reversion strategies (Strategy 1 in the Wyckoff manual).
- **Confused with**: A day with no tradable structure. Distinguished by recognizing that a D-shape specifically favors range/mean-reversion plays between VAH and VAL.
- **Layer**: Live order flow / Volume Profile (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Strategy 1 — Trading Range Principle, "Profile Topology: Classic D-shape").

### 1.37 Double-Distribution Profile (Failed Reversion Setup)
- **Data conditions**: The session volume profile shows two distinct peaks separated by a valley (an asymmetric or "double-distribution" shape). Occurs when price begins at one level, moves to a new value area mid-session, and forms a second concentration there. Creates the setup for "Strategy 4 — Failed Reversion" where a reversion attempt stalls at the VPOC separating the two distributions.
- **Confused with**: A single-distribution day with a wide range. Distinguished by the explicit presence of two volume peaks (two "accepted value areas") rather than one.
- **Layer**: Live order flow / Volume Profile (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Strategy 4 — Failed Reversion Principle, "Profile Topology: Asymmetrical or double-distribution profile shapes").

### 1.38 Back Up to the Edge of the Creek / LPS Entry Pattern (BUEC)
- **Data conditions**: After a genuine breakout (wide-range candles at high volume closing near extremes — Phase D/SOS), the market pulls back to retest the broken boundary line (VAH, structural resistance now acting as support, or the broken Creek). Corrective waves during this pullback should show decreasing volume (via Weis Wave indicator) compared to breakout impulse waves — confirming absence of counter-trend selling pressure. The entry trigger fires on the first bullish Order Flow imbalance bar re-accelerating away from the retest level.
- **Confused with**: A lower-high continuation of a downtrend. Distinguished by requiring a prior confirmed high-volume breakout (E/SOS) BEFORE the pullback, plus the volume contraction during the pullback itself.
- **Layer**: Live order flow + Volume Profile (Layer C); specifically classified in SKILL.md as requiring Volume Profile boundary AND Order Flow confirmation simultaneously.
- **Source**: Wyckoff 2.0 synthesis (Strategy 3 — Continuation Principle, "Entry Trigger Mechanics" steps 1-4).

### 1.39 Finished Auction / Single-Print LVN Extreme
- **Data conditions**: A tiny, single-print volume node at the absolute high or low of the day's wick — the market tested that extreme, transacted very little (fast rejection), and moved back. Identified via a narrow LVN (or visually, the thin "tail" on a P or b profile).
- **Confused with**: A normal support/resistance touch. Distinguished by the exceptionally low volume at the extreme (confirmed by footprint or volume histogram), indicating the market actively "finished" trading there — it was rejected quickly rather than accepted.
- **Use**: Scalpers can enter the mean-reversion rotation targeting VWAP as the initial target from this "finished auction" extreme.
- **Layer**: Live order flow / Volume Profile (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Strategic Takeaways — Scalper section, "The Failed Auction").

### 1.40 Overnight OI Surge as Volatility Pre-Signal
- **Data conditions**: A single ATM strike builds >50% more OI overnight vs the prior close. This is a quantified signal that the session is likely to be high-volatility, overriding any "stable" surface appearance (e.g., VIX looks calm at the open).
- **Confused with**: Normal OI accumulation in an active series. Distinguished by the specific >50% threshold in a single overnight window, not gradual multi-day build.
- **Layer**: Anonymous market-wide (Layer A — OI data is exchange-reported, anonymous).
- **Source**: `references/market_structure_gex.md` (OI Analysis — Overnight OI Build); SKILL.md 5-signal checklist (contributing +2 points).

### 1.41 Weis Wave Volume Contraction (Trend Integrity Check)
- **Data conditions**: The Weis Wave indicator breaks the continuous volume flow into discrete "waves" — each impulse wave and each corrective wave gets an aggregate volume block. A healthy trend shows impulse waves with large volume blocks and corrective pullback waves with small, decreasing volume blocks. When corrective volume begins approaching or exceeding impulse volume, it warns of SOT (Shortening of the Thrust — see 1.16) and trend exhaustion.
- **Confused with**: A single-candle volume spike or trough. Distinguished by being a multi-candle wave-level comparison, not a single-bar reading.
- **Layer**: Live order flow (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Strategy 3 — Continuation Principle, "Monitor the corrective waves using the Weis Wave Indicator").

### 1.42 Lognormal Price Distribution Asymmetry (Pricing Bias)
- **Data conditions**: Because stock/index prices cannot go below zero but theoretically have infinite upside, the distribution of terminal prices is lognormally skewed (right tail extends further than left). This means: equidistant OTM calls carry slightly more theoretical value than equidistant OTM puts in a theoretically "fair" Black-Scholes world. The observed opposite in practice (puts richer than calls — see 1.24) is ABOVE this theoretical baseline, reflecting the additional institutional demand skew on top.
- **Confused with**: The statement that puts are always more expensive (they are — but the lognormal-derived slight call advantage is the mathematical floor that put richness must overcome, not negate). Distinguished by separating "theoretical lognormal slight-call-advantage" from the observed "institutional-demand put richness" as two layered effects.
- **Layer**: Anonymous market-wide (Layer A — this is a property baked into any pricing model applied to all option prices).
- **Source**: Natenberg synthesis (Phase 1 — "The Mathematics of Price Distribution"; lognormal discussion); multiple Natenberg synthesis passes.

### 1.43 Three-Phase Market Cycle (Cause → Effect / Range → Trend)
- **Data conditions**: A sustained directional move (Effect / trend) cannot occur without a prior building lateral range (Cause / accumulation or distribution). In Wyckoff terms the range IS the cause; the ensuing trend IS the effect. The size/duration of the range is loosely proportional to the potential magnitude of the subsequent move.
- **Confused with**: Every sideways period being a viable accumulation/distribution range. Distinguished by requiring specific Wyckoff events (climax, automatic reaction, secondary test, Spring/Upthrust) WITHIN the range to confirm genuine institutional cause-building vs. simple directionless chop.
- **Layer**: Live order flow / structural (Layer C).
- **Source**: Wyckoff 2.0 synthesis (foundational "Law of Cause and Effect"); Part I ("Coexistence of Randomness and Determinism").

### 1.44 Gamma Scalping (Delta-Neutral Rebalancing)
- **Data conditions**: Long ATM straddle; Nifty moves 50-75 pts in one direction; position Delta has drifted from 0 to ±30-40 (now directionally biased). Scalp action: sell futures (or buy puts) to return Delta to zero; the profit from this hedge locks in some of the directional gain. If Nifty reverses, scalp again in the other direction. Works best in high-Gamma (near expiry) + large intraday swings; fails in a steady single-direction trend (you hedge against the trend repeatedly).
- **Confused with**: Normal Delta hedging of a short-options position. Distinguished by being applied to LONG options specifically, where positive Gamma causes Delta to grow in the direction of moves — creating a mechanical "buy dips, sell rallies" pattern inside the position itself.
- **Layer**: Live order flow (Layer C) — the rebalancing happens at live prices, not on overnight data.
- **Source**: `references/risk_and_adjustments.md` (Gamma Scalping section); `references/strategies_and_setups.md` (Gamma Scalping strategy reference); Passarelli synthesis (Part III Volatility — Gamma Scalping); Wyckoff 2.0 synthesis (Strategic Takeaways — Scalper section, "Gamma Profit" description); Natenberg synthesis (dynamic hedge "race" description).

### 1.45 Operational "Primacy of Price Over Volume" (Intraday Bias Check)
- **Data conditions**: In comparing Extended Trading Hours (ETH) volume data vs. Regular Trading Hours (RTH) volume data, large ETH volume can be structurally misleading because session participation ratios are vastly different. Price (as the executed-order record) is the more reliable raw signal; ETH/RTH volume data should be used with awareness of this participation bias.
- **Confused with**: "More volume always = more reliable signal." Distinguished by the session-context dependency — the same volume level means different things in ETH vs RTH.
- **Layer**: Anonymous market-wide (Layer A — this is a data-quality / interpretation caveat, not a specific market pattern).
- **Source**: Wyckoff 2.0 synthesis, Part I ("The Primacy of Price Over Volume").

### 1.46 Iceberg Order Identification
- **Data conditions**: A passive limit order appears to be absorbing large amounts of aggressive market-order flow at a specific level without causing the total visible order book depth to thin out — the passive side continuously replenishes, suggesting a "hidden" large order beneath the surface. Footprint: high ASK-column volume (aggressive buyers) at the level, yet price fails to advance.
- **Confused with**: Normal support holding passively. Distinguished from organic support by the continuous replenishment (the bid depth doesn't drain) combined with the high aggressive-buy volume being absorbed without displacement.
- **Layer**: Live order flow (Layer C); Iceberg orders are explicitly the mechanism behind Delta Divergence events (Pattern 1.19).
- **Source**: Wyckoff 2.0 synthesis (multiple references to Iceberg orders); Institutional Quant Blueprint synthesis ("Iceberg Algorithms" execution description).

### 1.47 Smart Order Routing / Dark Pool Execution (Institutional Footprint Concealment)
- **Data conditions**: Institutions breaking very large orders into small randomized chunks across multiple venues and dark pools to avoid revealing their intentions to HFT predators — this is why a large accumulation program may not show a single clean high-volume bar but instead appears as sustained moderate volume across many small candles.
- **Confused with**: Lack of institutional interest. Distinguished by the sustained, moderate, persistent volume pattern vs. the retail-predictable single-spike signature.
- **Layer**: Institutional identity (Layer B) — this is a named behavioral pattern of institutional order execution.
- **Source**: Wyckoff 2.0 synthesis (Institutional Quant Blueprint, "Placement and Execution Tactics"); Institutional Quant Blueprint synthesis, "Execution and Routing" section.

### 1.48 Ratio Spread (Call Ratio / Put Ratio — Risk-Asymmetric)
- **Data conditions**: Buy 1 ITM option, sell 2 OTM options of the same type (1:2 ratio). Profitable in a mildly directional or sideways market where the underlying stays below (call ratio) or above (put ratio) the short strikes at expiry. Income from 2 sold options exceeds cost of 1 bought option. Unlimited risk in the adverse direction beyond the double-short-strike level.
- **Confused with**: A defined-risk spread. Distinguished by the second uncovered short leg — this strategy has theoretically unlimited loss in one direction, unlike an iron condor or vertical spread.
- **Layer**: Live order flow / position construction (Layer C — pure instrument-selection pattern).
- **Source**: Options Trading Handbook (Kaushik) synthesis (E16).

---

## 2. FORMULA REFERENCE (continued — entries 2.46 onward)

### 2.46 GEX-Based Market Context → Strategy Selection Matrix
| GEX Regime | VIX Level | Market Condition | Recommended Strategy |
|---|---|---|---|
| Positive (>0) | Low/Stable | Range-bound | Sell straddle / Iron condor |
| Positive (>0) | High/Elevated | Volatile but dampened | Calendar spread / wait |
| Negative (<0) | Low/Weak Low | Explosive breakout risk | Buy OTM puts/calls |
| Negative (<0) | High+Rising | Directional cascade | Follow GEX direction, buy ATM |
| Flip zone | Any | Transitioning | Reduce size, wait for confirmation |
- **Tells you alone**: A 2-axis lookup table (GEX regime × VIX level) that maps to an appropriate strategy family.
- **Cannot tell alone / must pair with**: Requires GEX sign + VIX level to be read simultaneously before strategy selection; all other signals (OI, PCR, Max Pain) are secondary and must not override this matrix.
- **Source**: SKILL.md (Quick-Reference: Market Context → Strategy Matrix).

### 2.47 Complete Pre-Trade Checklist (composite formula-like scoring gate)
```
[ ] GEX regime identified (positive/negative)?
[ ] VIX structure read (stable/spiking/at weak low)?
[ ] OI overnight build checked (>50% = high volatility day)?
[ ] 4-step Greek sizing framework completed?
    [ ] Step 1: Delta exposure within limit?
    [ ] Step 2: Gamma scenario planned for 50-100 pt move?
    [ ] Step 3: Vega cost/benefit calculated?
    [ ] Step 4: Theta cost < expected gross profit?
[ ] Max loss defined before entry?
[ ] Adjustment trigger price identified?
[ ] Exit target price identified?
[ ] STT trap checked if near expiry?
```
- **Rule**: Trades failing Step 4 (Theta > expected gross profit) must NOT be entered regardless of directional conviction.
- **Source**: `references/risk_and_adjustments.md`.

### 2.48 Greek Drift Monitoring Thresholds
| Greek | Warning Signal | Action |
|---|---|---|
| Delta | Net Delta > ±40 (for neutral strategy) | Delta hedge via futures or add leg |
| Gamma | Near expiry + ATM + high OI → cascade risk | Reduce position or add wings |
| Theta | Daily decay > 15% of remaining premium | Re-evaluate trade viability |
| Vega | IV spiking + short Vega exposure | Buy a wing to reduce Vega |
- **Rule**: Review all open positions at 9:15 AM open AND at 2:00 PM each session.
- **Source**: `references/risk_and_adjustments.md` (Greek Drift Management section).

### 2.49 Capital Risk Rules (numerical thresholds)
- **Rule 1**: Max single position risk = 2% of capital.
- **Rule 2**: Max weekly loss limit = 3% of capital. If hit, stop all trading for the week and review.
- **Rule 3**: Use defined-risk strategies only for first 6 months; add naked exposure only after 3 consecutive profitable months with a trade journal.
- **Rule 4**: Never add to losing options positions (Greek profile has shifted — the new lot has completely different Gamma/Theta/Vega exposure at the worse strike).
- **Source**: `references/risk_and_adjustments.md` (Capital Allocation Rules).

### 2.50 Exit Rules — Numeric Thresholds
- **Short premium exit triggers**: Total loss = 200% of credit received (or 150% if using tight risk management); OR a single leg doubles in value (e.g., sold CE for ₹100, now ₹200 → buy it back); exit at 70-80% of max profit (don't hold for last rupee); close 1-2 days before expiry to avoid Gamma explosion.
- **Long premium exit triggers**: Stop-loss = 40-50% of premium paid (immediate exit); profit target = 80-100% of premium paid; time stop = 70% of trade life elapsed without the expected move → exit regardless of P&L.
- **Source**: `references/risk_and_adjustments.md` (Exit Rules section).

### 2.51 Position Adjustment Numeric Triggers
- **Short premium**: Nifty moves beyond 50% of max expected range (~±150 pts for 7-DTE straddle); OR P&L loss reaches 100-150% of initial credit; OR VIX spikes >15% intraday; OR GEX flips from positive to negative mid-trade.
- **Long premium**: Premium loses 40-50% without expected move; OR fewer than 2 DTE with position still OTM; OR IV crush occurred (Vega loss > Delta gain post-event).
- **Source**: `references/risk_and_adjustments.md` (Position Adjustment Framework — When to Adjust).

### 2.52 Volume Profile — Weis Wave Rule of Thumb
- **Rule (implied from Strategy 3 description)**: During a healthy trend pullback (BUEC entry setup), corrective Weis Wave volume blocks must be visibly smaller than breakout-impulse Weis Wave volume blocks to confirm the trend is intact. No specific numeric ratio is given in the source — the comparison is qualitative/visual.
- **Flag**: This is a qualitative rule, not a precise numeric formula. Treat as a supporting Layer C confirmation signal, not a standalone quantitative input.
- **Source**: Wyckoff 2.0 synthesis (Strategy 3 — Continuation Principle).

### 2.53 Dispersion Trade Payoff Formula
- **Calc**: At maturity T, payoff of a long dispersion trade using straddles:
  `P_(T,Dispersion) = Σ[wᵢ · ([Sᵢ,T − Kᵢ]⁺ + [Kᵢ − Sᵢ,T]⁺)] − ([S_I,T − K_I]⁺ + [K_I − S_I,T]⁺)`
  where Sᵢ,T = stock i price at T; Kᵢ = strike for stock i; wᵢ = weighting; I subscript = the index.
- **Tells you alone**: The mathematical payoff structure of a long-dispersion strategy — profits when individual stock volatilities are high but the index stays flat (they cancel out); loses when all stocks move together in the same direction (correlation = 1, index tracks them).
- **Cannot tell alone / must pair with**: Requires selection of constituent weights, strike selection, and an estimate of the "index vs. constituent IV spread" to evaluate whether the trade has positive expected value before entry.
- **Source**: Institutional Quant Blueprint synthesis (Dispersion Trading section).

### 2.54 Straddle Breakeven / Max Profit / Max Loss
- **Calc**: Total credit = CE premium + PE premium; Upper breakeven = strike + total credit; Lower breakeven = strike − total credit; Max profit = total credit (if underlying closes at exact strike on expiry); Max loss = unlimited beyond either breakeven.
- **For the buyer (long straddle)**: Max loss = total debit paid; breakeven = same formula; profit when underlying moves further than total debit in either direction.
- **Source**: NSE Bank Nifty booklet (Neutral Strategies table); nifty-options-pro `references/strategies_and_setups.md`.

### 2.55 Strangle vs Straddle Comparison (structural)
- **Straddle**: Buy/sell ATM CE + ATM PE (same strike). Highest premium, tightest breakeven range, maximum Gamma sensitivity.
- **Strangle**: Buy/sell OTM CE + OTM PE (different, wider strikes). Lower premium, wider breakeven range, lower Gamma, needs a bigger move to profit.
- **Rule of thumb from source**: For a cascade-signal-based long-vol trade (Strategy 6), OTM puts specifically (1-2 strikes below ATM) are the vehicle, not a full strangle/straddle, to keep cost low while capturing the expected directed move.
- **Source**: `references/strategies_and_setups.md` (Strategy 5 — Long Straddle/Strangle; Strategy 6 — OTM Put Buy).

### 2.56 Implied Volatility Expected Move — Natenberg's Formulation
- **Calc** (restated in Natenberg's notation, distinct from the nifty-options-pro VIX formulas because it uses the annualized IV input directly): 
  - `Daily_Volatility% = Annual_IV / 16` (same as VIX formula but expressed as IV% rather than VIX index)
  - `1-Day Price Change = Daily_Volatility% × Underlying_Price`
  - `1-Week Price Change = (Annual_IV / 7.2) × Underlying_Price`
  - Standard deviation probabilities: ±1 SD ≈ 68.3%; ±2 SD ≈ 95.4%; ±3 SD ≈ 99.7%.
- **Confirmation of consistency**: The nifty-options-pro VIX formulas (2.8, 2.9) and the Natenberg formulas (2.37 and this entry) use the same √252/√52 mathematics applied to different inputs (VIX index vs. IV%) — they are the same framework, confirming cross-source consistency rather than contradiction.
- **Source**: Natenberg synthesis (Volatility and the Square Root of Time; "Phase 3: Slicing Volatility").

### 2.57 Synthetic Position Construction Rules
- **Synthetic Long Stock**: Long Call + Short Put (same strike, same expiry) → moves 1:1 with underlying; net Delta ≈ +1; IV-neutral (IV moves cancel out between the long call and short put).
- **Synthetic Long Call**: Long Stock + Long Put → mimics a long call payoff; isolates upside while capping downside to put strike.
- **Synthetic Long Put**: Short Stock + Long Call → mimics a long put payoff.
- **Conversion** (arbitrage structure): Long Stock + Short Call + Long Put → Delta-flat, pure Rho/dividend arbitrage.
- **Reversal**: Short Stock + Long Call + Short Put → the inverse of conversion.
- **Box Spread**: Synthetic long + synthetic short at different strikes, same expiry → near-zero Greek risk, pure interest-rate play (not for retail, flagged in source as "market maker only").
- **Jelly Roll**: Offset synthetic stock positions across different expiry months → manages "pin risk" (assignment uncertainty at expiry ATM).
- **Source**: Passarelli synthesis (Put-Call Parity and Synthetics sections ×2); Natenberg synthesis (Synthetic Positions — Part III); NSE Bank Nifty booklet (strategy table — Synthetic Call entry).

### 2.58 Vertical Spread Max Risk/Reward
- **Bull Call (debit)**: Max profit = (higher strike − lower strike − net debit) × lot; Max loss = net debit × lot.
- **Bear Call (credit)**: Max profit = net credit × lot; Max loss = (spread width − net credit) × lot.
- **Bear Put (debit)**: Same structure as Bull Call but with puts.
- **Bull Put (credit)**: Max profit = net credit × lot; Max loss = (spread width − net credit) × lot.
- **Source**: NSE Bank Nifty booklet synthesis; `references/strategies_and_setups.md` (Strategy 4 — Vertical Debit Spread example with specific numbers).

### 2.59 Butterfly / Condor Construction Rules
- **Long Call Butterfly**: Sell 2 ATM calls + buy 1 ITM call + buy 1 OTM call. Max profit when underlying closes at short strike; max loss = net debit; risk defined.
- **Short Call Butterfly**: Buy 2 ATM calls + sell 1 ITM call + sell 1 OTM call. Profits from large moves in either direction (long volatility); max profit = net credit; max loss = spread width − credit.
- **Long Call Condor**: Buy 1 lower ITM call + sell 1 lower-mid ITM call + sell 1 higher-mid OTM call + buy 1 higher OTM call. Max profit when underlying stays between the two short strikes.
- **Iron Condor** (the AXIS-relevant variant): Sell OTM CE + Buy further OTM CE (bear call) + Sell OTM PE + Buy further OTM PE (bull put). All legs defined-risk.
- **Source**: NSE Bank Nifty booklet synthesis (Neutral Strategies table); `references/strategies_and_setups.md` (Strategy 2 — Iron Condor full example).

### 2.60 NSE F&O Advance Tax Payment Schedule
- By June 15: 15% of estimated annual tax liability.
- By September 15: 45%.
- By December 15: 75%.
- By March 15: 100%.
- Mandatory if expected annual tax > ₹10,000.
- **Source**: `references/risk_and_adjustments.md` (Tax Implications); Nifty Options Adjustments Guide article (identical content, confirms consistency).

### 2.61 Trading Journal — Required Fields Template
```
Date:
Expiry:
Strategy type:
Strikes entered:
Premium paid/received:
Net credit/debit (₹):
GEX regime at entry:
VIX at entry:
Reason for entry:
Adjustment(s) made (if any):
Exit date/time:
Exit P&L (₹):
Market conditions at exit:
What I learned:
```
- **Rule**: Review journal monthly. If win rate drops below 50% for 2 consecutive months → reduce position size by 50% AND switch to defined-risk strategies only.
- **Source**: `references/risk_and_adjustments.md` (Trading Journal section).

### 2.62 Wyckoff Strategy 1 — Trading Range Entry Execution Parameters
- **Entry condition**: Price has explored outside VA extreme (VAH for shorts, VAL for longs); footprint shows selling exhaustion (thinning BID numbers) + buying absorption (large resting buy limits holding level); Order Flow Delta turns positive (for long) confirming initiative buying BACK into the Value Area.
- **Stop Loss**: Behind the LVN forming the outer tail of the finished auction extreme.
- **Targets**: T1 (conservative) = session VPOC center; T2 (aggressive) = opposite VA extreme (VAH for longs; VAL for shorts).
- **Required market condition**: D-shape symmetric volume profile; VWAP and session VPOC clustered at center; price cleanly trading between VAH and VAL.
- **Source**: Wyckoff 2.0 synthesis (Strategy 1 — Trading Range Principle).

### 2.63 Wyckoff Strategy 2 — Value Area Re-Entry Execution Parameters
- **Entry trigger**: Price has swept outside VA (false breakout), prints a Delta Divergence bar at the boundary (high positive Delta but bearish close at VAH → institutional absorption), then prints a firm wide-range closing candle BACK INSIDE the 68.2% VA boundary.
- **Stop Loss**: Beyond the highest wick of the failed breakout sweep (structurally cleanest stop location in the material — not an ATR or % stop, but structurally defined).
- **Target**: Opposite VA extreme (if re-entry is through VAH → target VAL; vice versa).
- **Source**: Wyckoff 2.0 synthesis (Strategy 2 — Reversion Principle).

### 2.64 Wyckoff Strategy 3 — Continuation / BUEC Execution Parameters
- **Entry trigger**: Confirmed high-volume breakout (wide range candles closing near extremes, volume spike) → wait for structural pullback toward broken boundary → Weis Wave shows corrective waves with shrinking/tiny volume blocks → enter on first bullish/bearish Order Flow Imbalance bar re-accelerating from the retest level.
- **Stop Loss**: Behind the broken VA boundary line OR behind the session dynamic VWAP line (two options given; choose based on current VWAP proximity).
- **Target**: Next major unmitigated HVN OR structural VPOC from the macro composite profile.
- **Source**: Wyckoff 2.0 synthesis (Strategy 3 — Continuation Principle).

### 2.65 Wyckoff Strategy 4 — Failed Reversion Execution Parameters
- **Entry trigger**: A standard Strategy-2-style re-entry occurs (price re-enters VA), BUT momentum stalls at the internal VPOC instead of flowing through it smoothly → massive Passive Absorption prints at VPOC line → aggressive counter-trend sellers/buyers step in → price aggressively BREAKS BACK outside the initial VA boundary that was re-entered.
- **Stop Loss**: Immediately behind the rejected VPOC line (the institutional structural barrier that stalled the reversion).
- **Target**: Next major structural target or naked VPOC levels discovered on the historical macro timeline.
- **Source**: Wyckoff 2.0 synthesis (Strategy 4 — Failed Reversion Principle).

---

## 3. WORKED EXAMPLES (continued — entries E27 onward)

**E27 — Wyckoff Strategy 1 Execution (Template, no specific date)**
- Setup: D-shape session; VWAP and VPOC clustered at center; price tests VAL (lower value area boundary).
- Data: Footprint at VAL shows thinning BID volume (selling exhaustion) + large resting buy limits absorbing → Order Flow Delta turns positive.
- Entry: Long at VAL, stop behind LVN of lower tail.
- Targets: T1 = session VPOC; T2 = VAH.
- Classification: Not bait/trigger/harvest — a strategy-template structural example.
- Source: Wyckoff 2.0 synthesis (Strategy 1).

**E28 — Wyckoff Strategy 2 / Failed Breakout (Template)**
- Setup: Price breaks above VAH (false breakout scenario).
- Data: High positive Delta on breakout bar, but candle closes bearish (Delta Divergence) — institutional absorption at VAH confirmed. Then: a firm wide-range bar closes back inside the VA.
- Entry: Short on that re-entry bar; stop above highest wick of failed breakout.
- Target: VAL.
- Classification: This maps to a BAIT (upside breakout appearance) → TRIGGER (Delta Divergence + re-entry bar) → HARVEST (rotation to VAL) structure, making it one of the most directly "trap-pattern" shaped Wyckoff examples in the material.
- Source: Wyckoff 2.0 synthesis (Strategy 2).

**E29 — Wyckoff Strategy 4 / Failed Reversion (Template)**
- Setup: Price re-enters VA through VAL (re-entry signal fires), but stalls at internal VPOC; massive absorption prints at VPOC; aggressive sellers re-emerge; price breaks back below VAL.
- Entry: Short on breakout back below VAL; stop behind rejected VPOC line.
- Target: Next naked VPOC or structural macro level.
- Classification: This is a second-order BAIT (the initial re-entry looks like a reversal = bait) → TRIGGER (absorption stall at VPOC + re-break of VAL) → HARVEST (trend continuation beyond VAL). This is the most subtle trap in the Wyckoff manual — the bait is the initial mean-reversion signal itself.
- Source: Wyckoff 2.0 synthesis (Strategy 4).

**E30 — 0DTE Expiry-Day Cascade Framework (Template — June 23, 2026 as reference)**
- Setup: Expiry Thursday. Pre-10:00 AM checklist run.
- Data conditions (from E6/E7): GEX: −3.94M Cr (scores +3); VIX: 12.89 at Weak Low (scores +2); overnight OI build implied high by the large existing OI (scores +2); PCR rising + GEX negative (trap — scores +1); VIX CHoCH implied (scores +1) → total score = 9 (well above ≥5 threshold).
- Action: After 10:00 AM settle, identify ATM and ATM−1 strike for the OTM put buy.
- Target: VIX Down_Target formula = 23,904; GEX Fib target = 23,895.
- Outcome: Low 23,865, within 40 pts of combined zone.
- Classification: Full BAIT (normal price near 24,127) → TRIGGER (score≥5 + post-10am confirmation) → HARVEST (cascade to 23,865 zone).
- Source: All `references/market_structure_gex.md` sections + SKILL.md (combined read of the session).

**E31 — Natenberg "Race" Framing (conceptual worked example)**
- Setup: Trader has bought an underpriced option (as in E12).
- Race description (stated explicitly in source): Two opposing mechanics run simultaneously: (1) daily time-value loss (Theta cost) — this is the "losing" force; (2) cash flow from repeated delta-hedge adjustments (buy low / sell high on the underlying) — this is the "winning" force.
- Resolution: If the option was bought below theoretical value, the winning force outpaces the losing force over the option's life, netting the theoretical mispricing as profit at expiry.
- Lesson extracted as a rule: the entire rationale for delta-neutral hedging in the AXIS system's AI agent (Knowledge Interpreter) should be this race framing — it explains WHY monitoring and adjusting positions matters mechanically, not just as risk control.
- Source: Natenberg synthesis (Phase 5 — "The Ultimate Conclusion (The Race)").

**E32 — OTM Put Decay Trap (Template, generic)**
- Setup: A trader buys a far-OTM put option because "premium is cheap" — e.g., ₹12 for 23,850 PE when Nifty is at 24,127 (≈277 points OTM).
- Data: This is effectively what Strategy 6 buys — but ONLY on a score≥5 cascade day. Without that score, the same ₹12 put decays to zero if Nifty stays in range.
- Lesson: The premium being "cheap" is necessary but not sufficient — the Gamma + VIX expansion mechanism must be present for the cheap premium to generate a multibagger. Same instrument, two completely different expected-value profiles depending on whether the GEX/VIX/OI pre-conditions are met.
- Classification: This is the contrast case to E6 — identical instrument, opposite thesis validity.
- Source: Inferred from SKILL.md (Common Retail Errors — "Buying far OTM options because premium is cheap") combined with E6's success conditions.

**E33 — Covered Call, Institutional (Natenberg framework)**
- Setup: Long underlying asset, sell a call option against it at a strike above market to generate premium income.
- Data: Described generically in both Kaushik (Reliance example, E17) and Natenberg synthesis (Covered Call strategy type).
- Outcome: Caps upside at call strike in exchange for collecting premium; reduces effective cost basis of the underlying by the premium received.
- Note: The Thomsett "Institutional Investor" book (five ground rules) is specifically built around conservative covered-call and collar strategies over a "prequalified stock" universe — reinforcing the covered-call pattern as the most cross-cited strategy in this entire material (appears in Kaushik, Natenberg, Thomsett, NSE booklet, and SKILL.md strategy toolkit).
- Source: Options Trading Handbook (Kaushik, E17); Natenberg synthesis; Thomsett synthesis; NSE Bank Nifty booklet (Bullish Strategies — Covered Call row).

**E34 — Iron Butterfly vs Iron Condor Skew-Driven Choice (Template)**
- Setup: Evaluating wing spread structure under steep downside put skew.
- Data reasoning (from Pattern 1.33 / Formula 2.57): If OTM put IV is materially richer than OTM call IV (steep skew), an Iron Butterfly (ATM short strike for both call and put) captures the maximum richness at the center, while a standard butterfly using only puts overbuys the expensive rich side.
- Rule derived from source: Choose Iron Butterfly over standard Butterfly when skew is steep enough that pricing the "guts" off the actual skew curve (rather than symmetric strikes) improves the risk/reward ratio; this is detected by comparing IV at the proposed short strikes rather than assuming equidistant strikes are equivalently priced.
- Source: Passarelli synthesis (Volatility Skew and Butterfly section).

---

## 4. INSTITUTION-DETECTION RULES (continued — entries 24 onward)

24. **IF** a breakout occurs with wide-range candles closing near extremes AND volume spikes substantially vs. the prior corrective waves (confirmed via Weis Wave) **THEN** treat the breakout as genuinely institutional (Sign of Strength/Weakness) and expect a BUEC pullback to offer the high-probability continuation entry. **IF** the breakout has moderate/ambiguous volume AND no SMC-level confirmation **THEN** treat it as potentially retail-driven and wait for the BUEC retest to confirm. **CONFIDENCE: MEDIUM** — the rule is clearly stated as a 2-step confirmation requirement (Strategy 3), but no specific dated BUEC example with quantified volume numbers is given in this material.

25. **IF** price is inside the Value Area (between VAH and VAL) in a D-shape profile session **AND** Order Flow at the VAH/VAL boundary shows absorption/exhaustion **THEN** the 68.2% mean-reversion probability favors a rotation to the opposite extreme, with the VPOC as T1. **IF** the same reversal signal occurs NOT at a VP boundary (inside the range, away from extremes) **THEN** treat it as noise — explicitly stated: "Order Flow is practically useless unless deployed at a strict Volume Profile boundary." **CONFIDENCE: HIGH** — this specific caveat about boundary-only reliability is the Wyckoff 2.0 book's own self-limitation disclaimer, making it one of the most unambiguously stated rules in the entire material.

26. **IF** a Volume Profile session forms a P-shape (top-heavy volume) **THEN** the institutional order flow was predominantly bullish for that session (short-covering or accumulation at higher prices); expect the next session's opening to have structural upside support. **IF** it forms a b-shape (bottom-heavy) **THEN** bearish institutional commitment at lower prices; next session opening has structural downside bias. **CONFIDENCE: MEDIUM** — the P/b interpretation rule is stated clearly and repeatedly in the Wyckoff 2.0 synthesis, but it is not validated against a specific Nifty session's P/b profile in the source material (no dated Nifty P/b example is provided).

27. **IF** Delta Divergence prints at a Volume Profile VAH boundary (high positive Delta, bearish candle close) **THEN** interpret with HIGH confidence as institutional absorption/Iceberg selling; the probability that this is merely a coincidental aggressive buy flush is low given the VAH structural context. **IF** the same Delta Divergence prints in the middle of an empty range (away from any VP boundary) **THEN** interpret with LOW confidence — intent is ambiguous (see Pattern 1.19 ambiguity caveat). **CONFIDENCE: HIGH** for the boundary-qualified version; explicitly stated in the source as the key difference.

28. **IF** a session or range shows Shortening of the Thrust (≥3 consecutive impulse waves each shorter than the prior, SOT pattern) AND high volume accompanies each shrinking wave **THEN** interpret as effort-vs-result divergence → large institutional money is blocking/absorbing the trend and preparing a reversal. **IF** the SOT pattern is accompanied by low, declining volume **THEN** interpret as pure exhaustion (dominant trend participants withdrawing, not actively blocked). **CONFIDENCE: MEDIUM** — the SOT rule is explicitly stated with both sub-cases (high vol and low vol), but no specific Nifty session numeric examples with measured wave lengths are provided.

29. **IF** VIX is compressed and stable (positive-GEX-style environment) **AND** IV is materially higher than recent Historical Volatility **THEN** options are statistically overpriced → prefer selling volatility / premium-collection strategies. **IF** VIX is at a structural Weak Low AND IV ≈ HV or IV < HV (rare) **THEN** options are cheap → prefer buying volatility (straddle/strangle/OTM directional). **CONFIDENCE: HIGH** — the IV>HV→sell-vol rule is stated identically in Passarelli, Natenberg, SKILL.md, and the Institutional Quant Blueprint. The IV<HV corollary is implied but less explicitly stated; flagged as MEDIUM confidence for the buying variant.

30. **IF** an institutional algorithm (or by analogy a market participant with a known large order) has accumulated excess inventory on one side **THEN** it will skew its quoted prices (or in the case of a Nifty operator, take visible unhedged directional exposure in one direction) to incentivize counterparties to take the opposite side. The detectable trace of this in market data is: visible price imbalance combined with the underlying failing to make progress, suggesting the participant is trying to offload rather than build. **CONFIDENCE: LOW-MEDIUM** — the mechanism is well-explained theoretically in two sources (QUANT BIBLE and Institutional Blueprint), but translating it into a specific Nifty-observable rule requires further validation against real participant-wise data (FII/DII CSV, see Layer B note in source document context).

31. **IF** the session is within 2-4 trading days of a major scheduled event (RBI policy, elections, budget, FOMC) **AND** IV has already been rising for 1-3 days pre-event **THEN** buying options for the event is statistically unfavorable because IV crush post-announcement will likely exceed Delta gain even on a correct directional call. **IF** selling options on the same event, note that IV will collapse immediately post-announcement making short-premium strategies favorable AFTER (not before) the announcement. **CONFIDENCE: HIGH** — explicitly stated as a named phenomenon ("IV Crush") across at least 4 separate source sections (Nifty Options Trading Guide, SKILL.md Common Retail Errors, Passarelli Vega section, the Earnings Season article) with consistent wording and the same directional implication in each.

32. **IF** a company/index has an ex-dividend date approaching AND there are deep ITM American-style call options trading at zero time value (i.e., at parity with intrinsic value) **THEN** early exercise of those calls to capture the dividend is rational and should be expected (creating potential assignment risk for call writers). **CONFIDENCE: MEDIUM** — this is a Passarelli-specific rule for equity options; for Nifty index options specifically, dividends are already incorporated into the forward price of the index, reducing (but not eliminating) the relevance of this rule directly. Flagged as more directly applicable if AXIS ever expands to single-stock options.

33. **IF** the total loss on a position reaches 200% of the initial credit received (short premium) OR a single leg's value reaches 2× its sold premium **THEN** the position MUST be closed, not adjusted. This is a hard exit rule that supersedes the "Would I Do It Now?" soft rule. **CONFIDENCE: HIGH** — stated as a non-negotiable numeric trigger in `references/risk_and_adjustments.md` and cross-consistent with Passarelli's "Would I Do It Now?" rule (both lead to the same exit conclusion, they are complementary not conflicting).

34. **IF** an IV reading on any option across the Nifty chain deviates materially from the theoretical volatility smile/skew curve fitted to that expiry **THEN** that strike is a relative-value candidate (sell if richly priced, buy if cheaply priced relative to the modeled curve). **CONFIDENCE: MEDIUM** — this is the "Volatility Skew & Smile Exploitation" rule from the Institutional Quant Blueprint; clearly stated as an institutional strategy but requires a fitted skew curve as prerequisite (not a tool explicitly available in the described AXIS data sources; flagged as a future-addition capability when/if an options analytics platform providing full IV smile data is integrated).

---

## 5. COVERAGE CHECK — ADDENDUM

**Additional items processed in this addendum:**
- The 4 Wyckoff strategy execution blueprints (entry mechanics, stop placement, targets for each) — extracted as formulas 2.62-2.65 and examples E27-E29.
- The full GEX → Strategy matrix (formula 2.46).
- Complete pre-trade checklist (formula 2.47) and Greek drift monitoring thresholds (formula 2.48).
- All numeric exit/adjustment triggers (formulas 2.50-2.51).
- Capital risk rules as explicit numbered rules (formula 2.49).
- Trading journal template (formula 2.61).
- Weis Wave rule (formula 2.52) — flagged as qualitative.
- Dispersion trade payoff formula (formula 2.53).
- All synthetic/butterfly/condor construction rules consolidated (formulas 2.57-2.59).
- Straddle/strangle comparative structural formulas (formula 2.54-2.55).
- Second Natenberg volatility-slicing restatement in his own notation (formula 2.56).
- Advance tax schedule and F&O journal requirement (formulas 2.60-2.61).
- P/b/D shape patterns (1.34-1.36), Double-Distribution (1.37), BUEC (1.38), Finished Auction (1.39), Weis Wave (1.41), Lognormal asymmetry (1.42), Cause-Effect cycle (1.43), Gamma Scalping (1.44), Price-over-Volume primacy (1.45), Iceberg order identification (1.46), Smart Order Routing footprint concealment (1.47), Ratio Spread (1.48).
- Institution-Detection Rules 24-34 (Wyckoff boundary-qualified rules, P/b shape bias, event IV crush hard rule, exit hard-limit rule, skew exploitation rule).

**Items that remain outside the scope of this material and are flagged as genuine knowledge gaps for AXIS (not available from the given source documents, not silently omitted):**
- FII Participant-wise OI CSV data for June 16-30, 2025 periods: this specific data is referenced in the context documents (Document 1 in the original conversation) as an unverified Layer B data source — it is described but no actual FII CSV data or dated worked example using it appears in the source material processed here. Layer B remains theoretically defined but empirically unvalidated within this material.
- Historical Nifty 5-minute candle data or Options Chain data snapshots: the source material describes formulas and indicators to apply TO this data but provides no actual historical dataset that could be used to backtest the Direction Scorer weights.
- GEX data from StockMojo or any other data source as actual numbers (beyond the one June 23, 2026 GEX = −3.94M Cr reference): only one real GEX figure appears in the material.
- Participant-wise OI directional data distinguishing FII/DII/Retail/Proprietary positions: referenced as "Layer B" in the conversation context but not demonstrated in any of the processed source documents.

**Remaining possible omissions within processed source material (all minor):**
- The NSE booklet's bearish strategy table was referenced as existing but not fully quoted in the provided synthesis (the source text shows "[table omitted with blank rows]" visually). The bullish/neutral tables were given with full content. The bearish strategies are implied to be the mirrors of the bullish ones (Short Call, Long Put, Put Spread, Call Spread, Synthetic Put, etc.) by pattern, but cannot be confirmed from the excerpt provided.
- The Thomsett model portfolio's 10 specific stock names/weights: the source text presents a table placeholder that was blank/unreadable in the extract provided. Flagged as unreadable, not silently dropped.
- The QUANT BIBLE's full question-bank brainteaser solutions (Citadel Markov chain cube, HRT hyperplane distributions, SIG gambler's ruin exact formulas, etc.) — the questions are named but not solved in the provided text. Only the Kelly Criterion and Poisson examples (E19-E20) had enough worked content to extract as examples. The remaining brainteasers were named only (Taxi Cab, Ebola Test, etc.) and are catalogued in E24 as named-but-unsolved.

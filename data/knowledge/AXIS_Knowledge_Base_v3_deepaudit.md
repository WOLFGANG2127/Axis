# AXIS Knowledge Base — Part 3: Deep Audit & Remaining Gaps
Complete gap-fill after full cross-audit of Parts 1 and 2 against all source material.
Includes: missing Wyckoff event dictionary, missing formulas, CRITICAL SOURCE ERRORS,
uncovered rules, missing examples, Layer Classification Table, AXIS Component Mapping.

---

## CRITICAL SOURCE ERRORS (read this section first)

### ERROR 1 — Jade Lizard Example Numbers Do NOT Satisfy Zero-Upside Claim
**Source**: Nifty Jade Lizard Strategy article.
**Article claims**: "Upside risk: zero (if structured correctly)."
**Article's own example**: Sell 22,800 PE @₹50 + Sell 23,300 CE @₹45 + Buy 23,400 CE @₹25 = Net premium = 70 pts. Call spread width = 23,400 − 23,300 = 100 pts.
**The math**: For a Jade Lizard to have ZERO upside risk, the condition is: `total net premium received ≥ call spread width`. Here: 70 < 100. The example does NOT satisfy its own stated condition — it DOES have ₹30/unit of upside risk (100−70).
**Correct numbers for zero upside would require**: e.g., total premium ≥ 100 pts. The article is internally inconsistent — the principle is correct, but the illustrative numbers contradict the claim.
**Action for AXIS**: Use the mathematical condition (2.66 below) as the rule; treat the article's numbers as illustrative-only, NOT as a validated setup.

### ERROR 2 — Lot Size Inconsistency (75 vs 25)
**Source**: Nifty Options Trading Guide ("Premium Cost of the option Rs 150 x 75 (lot size) = Rs 11,250") vs. ALL other sources (Lot Size article, SKILL.md, Strategy references, Jade Lizard: "lot size = 25 units, effective since April 2023, reduced from 50").
**Implication**: The STT worked examples (E1, E2 in Part 1) used lot size 75 — the STT amounts stated there are wrong for current lot size. Correct: ₹22,500 intrinsic = 300 pts × 75 units, but at current lot size of 25 that same 22,000 CE with 300-pt intrinsic = 300×25=₹7,500 intrinsic → STT = 0.125%×7,500 = ₹9.38.
**Action for AXIS**: Hard-code lot size = 25 everywhere. All Part 1 STT examples are arithmetic from an outdated lot size.

### ERROR 3 — NSE Booklet Bearish Strategy Table Not Available
**Source**: NSE Bank Nifty Options Strategies booklet synthesis.
**What happened**: The source text shows a blank/placeholder for the bearish strategies table (columns present, rows empty). The bullish and neutral tables were given in full; the bearish table was not. It was flagged in Part 1's Coverage Check but its implications for completeness weren't fully articulated.
**Implication for AXIS**: Cannot confirm exact strike configurations for: Short Call, Long Put, Put Spread (bearish), Call Spread (bearish direction), Synthetic Put, Covered Put. These strategies ARE named in the booklet's own table header but their execution details are not present in the source material.

---

## 1. PATTERN LIBRARY — PART 3 (entries 1.49 onward)

### 1.49 Spring (Wyckoff Phase C — Accumulation Shakeout)
- **Data conditions**: Inside an accumulation range, after Phases A+B have built the "cause," price makes a rapid false breakdown below the bottom of the established range (below the Preliminary Support / Selling Climax lows). This breakdown is designed specifically to: (a) trigger retail stop-losses placed below the visible support, (b) trap bearish breakout traders who short the "breakdown," and (c) generate the forced-sell liquidity that institutions need to complete their long accumulation at the lowest possible prices. The Spring typically reverses FAST — the breakdown travels only far enough to sweep the stops, then snaps back into the range.
- **Data signatures**: Low volume on the spring itself (institutions NOT selling — they're absorbing); fast V-reversal back inside the range; Order Flow: brief BID-heavy volume at the low, then immediate ASK-dominant initiative buying pulling price back up.
- **Confused with**: A genuine trend breakdown. Distinguished by: (1) low volume on the break (not the high volume of a genuine panic sell-off), (2) the fact that it occurs WITHIN an established Phase B range (not as the first breakdown), (3) the rapid snap-back rather than follow-through.
- **Layer**: Live order flow / structural (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Phase C description; "shakeout... false breakout designed to trigger stop losses and capture liquidity before the real trend begins").

### 1.50 UTAD — Upthrust After Distribution (Wyckoff Phase C — Distribution Shakeout)
- **Data conditions**: Mirror image of the Spring, but occurring in a distribution range. Price makes a rapid false breakout ABOVE the top of the established distribution range (above the Preliminary Supply / Buying Climax highs). Designed to: (a) trigger retail stop-losses placed above resistance, (b) trap bullish breakout buyers, (c) generate the forced-buy liquidity institutions need to dump large short positions at the highest possible prices. Like the Spring, the UTAD reverses fast after the sweep.
- **Data signatures**: Often accompanied by rising but declining volume on each successive UTAD attempt (effort rising, result diminishing = no real buyer commitment); fast reversal back inside the range; Order Flow: brief ASK-heavy at the high, then immediate BID-dominant selling pulling price back down.
- **Confused with**: A genuine breakout to new highs. Distinguished by the fast reversal, declining volume on the fake new highs, and occurrence within a known Phase B distribution range.
- **Layer**: Live order flow / structural (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Phase C; "UTAD = the ultimate shakeout... designed to trigger stop losses and capture liquidity").

### 1.51 SOS — Sign of Strength (Wyckoff Phase D — Bullish Breakout Confirmation)
- **Data conditions**: After the Spring (Phase C), a wide-range upward candle WITH good volume that successfully breaks above a key structural level (the top of the trading range / AR high / resistance). This is the first evidence that institutional accumulation is complete and the markup phase is beginning. The key distinction from a normal bounce is: (1) wide range (bodies, not wicks), (2) volume expanding noticeably vs prior corrective waves, (3) the move closes ABOVE the structural resistance, not just touches it.
- **Data signals from Order Flow**: Strong cumulative positive Delta; ASK imbalances at each sub-level of the up-move; minimal BID absorption visible (sellers are not blocking).
- **Confused with**: A normal oversold bounce inside the range. Distinguished by structural break (closing above the range ceiling) AND volume confirmation.
- **Layer**: Live order flow / structural (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Phase D events: SOS + LPS).

### 1.52 SOW — Sign of Weakness (Wyckoff Phase D — Bearish Breakdown Confirmation)
- **Data conditions**: Mirror of SOS in distribution. After the UTAD (Phase C), a wide-range downward candle WITH volume that successfully breaks BELOW key structural support (range bottom / AR low / support). First evidence that distribution is complete and the markdown phase is beginning.
- **Data signals**: Strong cumulative negative Delta; BID imbalances on the way down; minimal ASK absorption (buyers not defending).
- **Confused with**: A normal pullback inside the distribution range. Distinguished by the structural breakdown AND volume confirmation (not just a wick below support).
- **Layer**: Live order flow / structural (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Phase D events: SOW + LPSY).

### 1.53 LPS — Last Point of Support (Post-SOS Retest)
- **Data conditions**: After the SOS breaks the range ceiling, price pulls back to retest the broken resistance (now acting as support). The LPS is the ENTRY OPPORTUNITY — the highest-probability long entry in the accumulation cycle. Characteristics: (1) volume contracts significantly during the LPS pullback vs. the SOS up-move (Weis Wave shows shrinking corrective waves), (2) price holds above the broken ceiling (doesn't re-enter the range), (3) Order Flow at the LPS shows absorption/exhaustion of whatever selling pressure remains.
- **Confused with**: A trend reversal back into the range. Distinguished by volume contraction (sellers running out of supply) and price holding ABOVE the formerly broken ceiling.
- **Layer**: Live order flow / structural (Layer C). This is the "BUEC" (Back Up to the Edge of the Creek) entry from Strategy 3 in Part 2 (1.38/2.64) — same concept, different Wyckoff labels.
- **Source**: Wyckoff 2.0 synthesis (Phase D events).

### 1.54 LPSY — Last Point of Supply (Post-SOW Retest)
- **Data conditions**: Mirror of LPS in distribution. After the SOW breaks range support, price bounces back to retest the broken support (now acting as resistance). The LPSY is the short-entry opportunity. Characteristics: shrinking volume on the LPSY rally vs. the SOW breakdown; price holding BELOW the broken support; Order Flow showing absorption of buying at the resistance.
- **Confused with**: A genuine recovery back into the range. Distinguished by volume shrinkage on the rally and failure to re-enter the former range body.
- **Layer**: Live order flow / structural (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Phase D events).

### 1.55 SC / BC — Selling Climax / Buying Climax (Wyckoff Phase A)
- **Data conditions**: SC: The event that ends the prior downtrend and marks the bottom of the accumulation range. Characterized by: massive volume spike (highest of the down-move), wide-range bar, close NEAR or AT the low (panic), followed immediately by the Automatic Rally (AR). The climax is NOT the entry — it is a WARNING that a range may be beginning. BC (Buying Climax): Mirror at the top of a prior uptrend; massive volume, wide range up-bar, close near the high, followed immediately by the Automatic Reaction (AR downward). Both are "stop bars" that change character from trending to ranging.
- **Confused with**: "Just another big day." Distinguished by being the LARGEST volume event in the prior trend's entire history (not just a large day), and by the immediate automatic reaction that creates the first counter-move.
- **Layer**: Live order flow / structural (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Phase A; event labels PS/SC/AR/ST).

### 1.56 AR — Automatic Rally / Automatic Reaction (Wyckoff Phase A)
- **Data conditions**: AR (Automatic Rally) follows the SC in accumulation: after the panic-selling climax absorbs all aggressive sellers, the lack of further selling causes an automatic bounce. This bounce is NOT driven by institutional buying yet — it's the absence of selling. The AR high establishes the TOP of the accumulation trading range. AR (Automatic Reaction) in distribution: after the BC, the lack of further buying causes an automatic drop, establishing the BOTTOM of the distribution trading range.
- **Confused with**: A genuine trend reversal initiated by buyers. Distinguished by being purely mechanical — it is demand temporarily exceeding depleted supply, not new institutional conviction.
- **Layer**: Structural (Layer C context but technically is the result of exhausted supply/demand, not a live order-flow signal on its own).
- **Source**: Wyckoff 2.0 synthesis (Phase A).

### 1.57 ST — Secondary Test (Wyckoff Phase A)
- **Data conditions**: After the SC + AR pair establishes the range boundaries, the ST is a return move toward the SC (for accumulation) or BC (for distribution) price levels — to verify whether those extreme levels still have supply/demand present. A successful ST: volume noticeably LOWER than the climax (supply/demand is drying up); price holds above the SC low for accumulation (does not make a new extreme). A failed ST that goes deeper may evolve into the Phase C Spring.
- **Confused with**: The Spring (the Phase C shakeout). Distinguished by occurring before Phase B consolidation fully develops; the Spring is deliberate and engineered, the ST is more organic.
- **Layer**: Live order flow / structural (Layer C).
- **Source**: Wyckoff 2.0 synthesis (Phase A event sequence).

### 1.58 PS / PSY — Preliminary Support / Preliminary Supply (Wyckoff Phase A)
- **Data conditions**: PS (Preliminary Support): The first visible attempt to halt the prior downtrend — a volume-supported bounce that doesn't end the trend but signals some buying is beginning. This is before the SC; it tells you the market is approaching a potential climax zone. PSY (Preliminary Supply): Mirror at the top; the first visible selling check of a prior uptrend, before the BC.
- **Confused with**: The actual SC/BC. Distinguished by being EARLIER in the sequence and typically on LESS extreme volume than the full climax that follows.
- **Layer**: Structural (Layer C context).
- **Source**: Wyckoff 2.0 synthesis (Phase A labels; "PS / PSY: The initial attempt to halt the previous trend").

### 1.59 Opening Noise Pattern (9:15 AM — 10:00 AM)
- **Data conditions**: The first 45 minutes of the Indian market session (9:15-10:00 AM) exhibit high artificial volatility driven by: overnight order imbalances clearing, global market gap-adjustments, institutional basket rebalancing, and news reactions. This volatility is noise, not signal — it does NOT represent genuine intraday directional commitment. Patterns that appear to form during this window are disproportionately likely to reverse once the noise settles.
- **Confused with**: A genuine opening-range breakout or directional session opener. Distinguished by the specific time window — the 0DTE protocol explicitly states "Do not trade expiry before 10:00 AM — early volatility is noise, not signal."
- **Layer**: Live order flow (Layer C) — a time-based filter, not a price/volume pattern per se.
- **Source**: SKILL.md (Expiry Day 0DTE Protocol: "Wait until 10:00 AM for the initial volatility to settle"); `references/strategies_and_setups.md` (Expiry Day 0DTE Protocol).

### 1.60 OI Wall Positive-GEX Mechanics (Call/Put OI as Actual Support/Resistance)
- **Data conditions**: In POSITIVE GEX environments only: High Call OI at a strike = resistance (call writers are delta-hedged by selling Nifty futures; as price approaches the strike from below, they must sell MORE futures to maintain their hedge, creating overhead resistance). High Put OI at a strike = support (put writers are delta-hedged by buying Nifty futures; as price approaches from above, they buy MORE futures, creating a floor). This is the BASELINE behavior — valid in positive GEX only.
- **Confused with**: The negative-GEX inversion (Pattern 1.10). The same OI data means opposite things depending on GEX sign. In negative GEX, put OI becomes forced selling (already covered); in positive GEX, it becomes actual mechanical support via futures buying by writers.
- **Layer**: Anonymous market-wide (Layer A — OI data) combined with live order flow (Layer C — the futures hedging is happening in real time).
- **Source**: `references/market_structure_gex.md` (OI Analysis: "High call OI at a strike = resistance... High put OI at a strike = support... BUT: In negative GEX, put OI becomes forced selling, not support").

### 1.61 Pin Risk (Expiry-Day ATM Assignment Uncertainty)
- **Data conditions**: When an option expires exactly at-the-money (or very near the money), the seller faces maximum uncertainty about whether they will be assigned. A slight move in either direction in the final minutes can change whether a written option expires OTM (no assignment) or barely ITM (assigned). This uncertainty creates a specific risk profile for option sellers near expiry.
- **Confused with**: Simple expiry-day Gamma risk. Distinguished by being specifically about the ASSIGNMENT UNCERTAINTY for sellers — not just the P&L volatility but the obligation uncertainty itself.
- **Layer**: Live order flow (Layer C — expiry-specific risk).
- **Source**: Passarelli synthesis (Jelly Roll description: "managing pin risk = the uncertainty of assignment at expiration"); Natenberg synthesis (Conversions and Reversals section: "expose the trader to 'pin risk'").

### 1.62 Early Exercise for Dividend Capture (Deep ITM American Calls)
- **Data conditions**: For stocks (NOT Nifty index options — index options are European-style) with approaching ex-dividend dates: when a deep ITM call option has zero remaining time value (it trades at parity = intrinsic value only), rational holders will exercise early to capture the upcoming dividend, since holding the option no longer provides any time-value benefit but costs the dividend. Signal: the call is trading at parity (premium ≈ intrinsic value only, time value ≈ zero) near an ex-dividend date.
- **Confused with**: Irrational early exercise. Distinguished by the logical condition: zero time value makes the opportunity cost of holding the option (missing the dividend) negative, making exercise rational.
- **Layer**: Institutional identity (Layer B — named, rational institutional behavior).
- **Note**: Nifty Index options are European-style and CANNOT be early exercised. This pattern is flagged here for completeness (appears in Passarelli synthesis) but is NOT directly applicable to the core AXIS Nifty system unless expanded to single-stock options.
- **Source**: Passarelli synthesis (Part I — "The Impact of Dividends" section; "deep ITM American calls often trade at parity near ex-dividend dates").

### 1.63 IV Term Structure Inversion Signal
- **Data conditions**: Normal term structure: front-month IV < back-month IV (market expects more future uncertainty in the longer term than the near term — calm current environment). Inverted term structure: front-month IV > back-month IV — occurs during panic/pending-news periods when the immediate short-term environment feels more dangerous than the longer-term horizon. Inversion is a direct warning signal: the market is pricing imminent elevated uncertainty.
- **Confused with**: A randomly elevated front-month premium. Distinguished by explicitly comparing front-month IV to back-month IV; the relationship, not the absolute level, is the signal.
- **Use**: For calendar spread selection — enter calendars in NORMAL term structure (buy back-month, sell front-month, profit from the convergence); AVOID in inverted term structure (front-month you're selling is already cheap, back-month you're buying is expensive).
- **Layer**: Anonymous market-wide (Layer A).
- **Source**: Passarelli synthesis (Volatility section — "Term Structure (Horizontal Skew): IV differs across expiration months. Front months often have lower IV in calm markets but higher IV during panic or pending news"); `references/greeks_and_pricing.md` (Volatility Types).

### 1.64 Four-Directional Thinking (Strategy Classification Framework)
- **Data conditions**: Any market environment can be classified into exactly one of four states for strategy selection:
  - UP: Nifty is trending bullishly with GEX/Structure confirmation → long calls / bull put spreads
  - DOWN: Nifty is trending bearishly → long puts / bear call spreads
  - SIDEWAYS: Nifty is in a range / positive GEX / flat VIX → sell straddle / iron condor / sell strangle
  - VOLATILE: Nifty is at low VIX (weak low) + negative GEX = about to explode but direction unclear → buy straddle / strangle / OTM puts
- **Confused with**: Binary directional bias (only UP/DOWN). Distinguished by explicitly treating sideways and volatile as distinct tradeable conditions with their own strategy families, not as "don't trade" conditions.
- **Layer**: System-level decision framework (feeds into Strategy Activation gate, AXIS Component 3).
- **Source**: Passarelli synthesis ("Four-Directional Thinking: trade all four directions: up, down, sideways, and volatile"); SKILL.md Quick-Reference Matrix (same framework operationalized in GEX/VIX terms).

### 1.65 Delta Convergence to 0.50 (Time Effect on ATM)
- **Data conditions**: As an option approaches expiry, the delta of an exactly ATM option gravitates toward 0.50 from wherever it started — this is because the lognormal distribution narrows over time, and the probability of the ATM option expiring ITM or OTM becomes nearly exactly 50/50 with no remaining time. For ITM options, Delta approaches 1.0 as DTE decreases. For OTM options, Delta approaches 0 as DTE decreases.
- **Confused with**: ATM Delta being fixed at 0.50 at all times. Distinguished by recognizing that time decay compresses the distribution, making near-expiry option prices more binary (ATM → 0.50, ITM → 1.0, OTM → 0).
- **Layer**: Instrument pricing (feeds into Option Chain Selector's strike selection and DTE decisions).
- **Source**: Passarelli synthesis ("As time passes, at-the-money (ATM) Deltas gravitate toward 0.50").

### 1.66 Regime Filtering (The Non-Trading Rule)
- **Data conditions**: AXIS should NOT be generating trade signals in any of these regime conditions: (1) GEX is in a "flip zone" (transitioning from positive to negative or vice versa, undefined regime), (2) VIX structure is ambiguous (no clear Weak Low, CHoCH, BOS, or compression pattern — just mid-range noise), (3) The 5-signal score is 2-4 (no directional bias established). These are explicitly "wait for clarity" conditions in the source material.
- **Confused with**: "Anything less than a perfect 5-star setup is still worth trading at reduced size." Distinguished by the source explicitly saying: flip zone → "Reduce size, wait for confirmation"; score 2-4 → "no directional bias."
- **Layer**: System-level (Direction Scorer output → feed into Structure Gate decision).
- **Source**: SKILL.md Quick-Reference Matrix ("Flip zone → Reduce size, wait for confirmation"); SKILL.md 5-signal checklist ("Score 2-4 → Reduce size, no directional bias").

---

## 2. FORMULA REFERENCE — PART 3 (entries 2.66 onward)

### 2.66 Jade Lizard Zero-Upside Condition (Corrected)
- **Correct condition**: `Total_Net_Premium_Received ≥ Width_of_Call_Spread`
  Where: Net_Premium = PE_sold + CE_sold − CE_bought; Call_Spread_Width = Upper_CE_strike − Lower_CE_strike
- **If satisfied**: Max upside risk = zero (put-side premium covers any call-spread max loss).
- **If NOT satisfied** (as in the source article's example): Upside risk = Call_Spread_Width − Net_Premium.
- **Example (correcting the source article's error)**: For zero upside: if call spread width = 100 pts, need net premium ≥ 100 pts. The article's example gives net premium = 70 pts vs. width = 100 pts → upside risk ≠ 0, the article is wrong.
- **Working correct example**: Sell 22,800 PE @₹70 + Sell 23,300 CE @₹50 + Buy 23,400 CE @₹15 = Net = 105 pts > 100 pts width → zero upside risk is achieved.
- **Source**: Nifty Jade Lizard Strategy article (principle only; numbers corrected per the mathematical condition).

### 2.67 Signal Hierarchy — 5-Level Override Table
```
Priority  Signal           What It Overrides / When Valid
1         GEX              Overrides everything. Negative GEX invalidates
          (Master Switch)  Max Pain, inverts PCR interpretation, converts OI 
                           support into forced-selling fuel.

2         VIX Structure    Defines magnitude of expected move.
          (15-min SMC)     Read CHoCH, BOS, Weak Low on VIX's own chart.
                           Gives multi-day lead time other signals lack.

3         OI + PCR         Defines fuel level (how much hedging obligation 
                           exists). Read ONLY after GEX regime is known.
                           PCR meaning INVERTS between GEX+ and GEX-.

4         Max Pain         Valid ONLY when GEX is positive.
                           IGNORE when GEX is negative.

5         Price / VWAP     Entry timing only. NEVER used as primary signal.
                           If VWAP shows a buy but GEX is negative — ignore 
                           the VWAP signal.
```
- **Critical rule**: If GEX is negative, ALL of signals 3 and 4 change meaning. Max Pain → ignore. PCR rising → bearish (not bullish). OI support → forced selling. Signal 5 VWAP → entry timing only, not directional.
- **Source**: SKILL.md ("The Five Market Structure Signals — Read in This Order. Hierarchy is strict. GEX overrides everything.").

### 2.68 Straddle Adjustment Trigger (60% Rule)
- **Rule**: If Nifty moves beyond approximately 60% of the total expected range from the straddle center, trigger adjustment.
- **Calc**: Approximate trigger = straddle_credit × 0.60 = movement threshold from ATM.
  For a 7-DTE straddle with ₹340 total credit (E3): trigger at ~200 pts from ATM.
- **Actions when triggered**: (a) Convert to strangle by rolling the tested leg further OTM, accepting lower net credit but more range, OR (b) Add Delta hedge via futures to neutralize directional risk while keeping the position open.
- **Source**: `references/strategies_and_setups.md` (Strategy 1 — ATM Straddle Sell, "Adjustment rule: If Nifty moves beyond 60% of expected range (>~200 pts)...").

### 2.69 Iron Condor Tested-Leg Adjustment (2× Credit Rule)
- **Rule**: If Nifty tests either short strike of an iron condor (i.e., moves to the 24,400 CE or the 24,000 PE in the example), action: roll the ENTIRE tested side further OTM OR close the tested spread at 2× credit received.
- **Calc**: Close trigger = tested_spread_credit × 2. If sold 24,000-23,800 put spread for ₹50 credit → close when that spread costs ₹100 to buy back.
- **Roll vs Close rule**: Only roll if at least 5 DTE remain; with 1-2 DTE, rolling creates margin complications → close instead.
- **Source**: `references/strategies_and_setups.md` (Strategy 2 — Iron Condor, "Adjustment trigger: If Nifty tests either short strike, roll the entire tested side further OTM or close the tested spread at 2× credit received").

### 2.70 Strike Selection Reference Table (complete)
| Outlook | Recommended Strike | Reasoning |
|---|---|---|
| Directional buy (strong conviction) | ATM or 1 strike ITM | Highest Delta, best response per ₹ move |
| Directional buy (moderate view) | ATM | Balanced Delta/cost |
| Volatility buy (straddle) | ATM both CE + PE | Maximum Gamma sensitivity |
| Spread (defined risk directional) | Sell ATM, buy OTM | Delta + Theta optimization |
| Condor (range/neutral) | Sell ~200 OTM, buy ~400 OTM | Approximately 1 SD zone |
| Cascade signal (OTM directional) | 1-2 strikes OTM from ATM | Low cost; leveraged on vol spike + Delta gain |
| **NEVER buy for directional play** | **>300 pts from ATM weekly** | **Theta destroys premium before move materializes** |
- **Source**: SKILL.md (Strike Selection Guidelines table + "Never buy" rule).

### 2.71 BankNifty IV Multiplier
- **Calc**: `BankNifty_IV ≈ 1.3 to 1.6 × Nifty50_IV`
- **Tells you alone**: BankNifty options consistently carry 30-60% more implied volatility than Nifty 50 options, meaning more premium available for sellers but also more Vega risk for any position.
- **Implication for strategy selection**: The same Gamma/Theta/Vega framework applies but with proportionally larger absolute rupee swings per lot. "Requires tighter directional management" per source.
- **Source**: `references/greeks_and_pricing.md` ("BankNifty vs Nifty 50: BankNifty IV typically 1.3-1.6× Nifty 50 IV").

### 2.72 Calendar Spread Profit Mechanism (Time Differential)
- **Principle**: Sell near-expiry ATM option (short Theta — high decay rate); Buy far-expiry ATM option (lower Theta — slower decay). Profit = rate_of_near_decay > rate_of_far_decay per day held.
- **Favored environment**: Normal IV term structure (front-month IV < back-month IV); stable range; no major event within the near-expiry window.
- **Risk**: Large sudden move makes BOTH legs lose value simultaneously (long Vega in back month can't save you if Delta moves destroy both).
- **Entry/Exit rule**: Initiate in normal term structure; close before near expiry when near-dated premium has largely decayed. Do NOT hold through the near-month expiry (pin risk + Gamma explosion on expiry day of the short leg).
- **Source**: `references/strategies_and_setups.md` (Strategy 7 — Calendar Spread).

### 2.73 Gamma Scalping Rebalance Threshold
- **Rule**: For a long straddle / delta-neutral long-Gamma position:
  - Monitor: rebalance when position Delta drifts to ±30-40 (from 0)
  - Trigger: Nifty moves 50-75 pts from entry point
  - Action: Sell futures (if Delta drifted positive) or buy futures (if Delta drifted negative) to return net Delta to 0
- **When this works**: High Gamma environment + large intraday swings (ideally on expiry day with negative GEX — maximum Gamma × maximum OI = maximum scalping opportunity)
- **When this fails**: A steady single-direction trending day — you keep hedging against the trend, locking in losses on the futures legs while the long options gain isn't enough to compensate.
- **Source**: `references/risk_and_adjustments.md` (Gamma Scalping section: "Nifty moves 50-75 pts in one direction; Delta has drifted from 0 to +/- 30-40"); SKILL.md (Expiry Day 0DTE Protocol for negative-GEX conditions).

### 2.74 Complete OI Data Sources Reference
```
GEX (Gamma Exposure chart):        StockMojo → Options Lab → Gamma Exposure
Multi-OI & overnight OI build:     StockMojo → Multi OI & Volume
Live PCR chart (from 9:15 AM):     StockMojo → Put-Call Ratio
VIX 15-min chart with SMC:         TradingView — "INDIAVIX" ticker
Option chain Greeks display:        Sensibull / Opstra / Zerodha Kite
Margin calculator:                  Zerodha Margin Calculator / Angel One / ICICI Direct
```
- **Source**: `references/market_structure_gex.md` (OI Data Sources section); SKILL.md (multiple in-text references).

### 2.75 Target Convergence Confidence Formula (Qualitative)
- **Rule**: When two INDEPENDENT methods of deriving a price target agree within a small tolerance (≤40-50 pts for Nifty), the confidence in that target level increases multiplicatively, not additively.
- **The two methods present in source**: (1) VIX Down_Target formula (arithmetic from vol); (2) GEX Fibonacci Extension target (structural from gamma exposure profile). These use completely different inputs and calculation methods — their agreement is therefore informative, not coincidental.
- **Real example (June 23, 2026)**: VIX target = 23,904; GEX Fib target = 23,895; actual low = 23,865. Agreement zone 23,895-23,904 (9-pt spread); actual low missed by 30-39 pts.
- **Action for AXIS Agent 2 (Final EV Verifier)**: When target from VIX formula and target from GEX Fibonacci fall within ≤50 pts of each other, treat as a high-conviction level. When they diverge >100 pts, use the zone between them as the target band, not a single point.
- **Source**: `references/market_structure_gex.md` (GEX Fibonacci Extension Targets section, "Combined target system" + real example).

### 2.76 Thomsett's Five Ground Rules (Converted to Formulas)
```
Rule 1: Trade options ONLY on stocks/instruments you intend to hold permanently
         (pre-qualified list; not speculative trading vehicles).

Rule 2: The underlying instrument must be expected to grow in long-term value.

Rule 3: All strategic decisions must begin with fundamental analysis of the 
         underlying — options are derivatives, they have no intrinsic fundamental 
         attributes of their own.

Rule 4: You must be comfortable BUYING MORE of the underlying if its price 
         temporarily declines (psychological / financial prerequisite for put-selling).

Rule 5: Maintain a "replacement list" of alternative instruments so that if a 
         strategy results in having to sell your position, you can immediately redeploy 
         capital into an equivalent quality instrument.
```
- **Note for AXIS**: These five rules are specifically for the conservative institutional investor framework (Thomsett). For AXIS (an index options system, not a single-stock conservative strategy), Rules 1-3 translate directly to: only trade Nifty/BankNifty derivatives (inherently "fundamental quality" index instruments), always read the macro/GEX environment (equivalent to fundamentals for an index), treat GEX/VIX analysis as the "fundamental analysis" equivalent. Rules 4-5 are less applicable to index options but the spirit of Rule 4 (be comfortable holding through adverse moves to the defined-risk limit) is captured in the 2%/3% capital rules.
- **Source**: Thomsett synthesis (Five Ground Rules of Conservative Options Trading).

### 2.77 Sharpe and Sortino Ratios (System Performance Metrics)
- **Sharpe Ratio**: `(Portfolio_Return − Risk_Free_Rate) / Portfolio_Standard_Deviation` — measures excess return per unit of total risk.
- **Sortino Ratio**: `(Portfolio_Return − Risk_Free_Rate) / Downside_Standard_Deviation` — measures excess return per unit of DOWNSIDE risk only (ignores upside volatility, more relevant for asymmetric strategies like option buying).
- **Max Drawdown**: `(Peak_Portfolio_Value − Trough_Portfolio_Value) / Peak_Portfolio_Value` — the largest peak-to-trough percentage decline in the portfolio's history.
- **Use in AXIS**: These three metrics are the primary criteria for evaluating whether the AXIS signal system is performing as designed when backtested or when reviewed monthly. Not formula inputs to individual trades, but system-level health metrics.
- **Source**: Wyckoff 2.0 synthesis (Institutional Quant Blueprint: "evaluate success not just by net profit, but through risk-adjusted metrics like the Sharpe Ratio, Sortino Ratio, Maximum Drawdown, and Win/Loss percentage").

### 2.78 Kaushik Covered Call Strike (5% OTM Target)
- **Rule**: When beginning the covered call writing component of the "money tree" strategy, initially select a strike price 5% above the current market value of the ETF.
- **Calc**: `Call_Strike = Current_ETF_Price × 1.05`
- **Kaushik's threshold**: Begin this strategy only after accumulating ≥7,500 units of the ETF (NIFTY BeES or Bank BeES).
- **Weekly investment to reach threshold**: Start with ₹5,000/week systematic investment into the ETF.
- **Source**: Options Trading Handbook (Kaushik) synthesis (Money Tree strategy: "selecting covered call options that have a strike price that is 5% higher than the current market value").

### 2.79 IV Rank (Concept — not fully described in source but referenced)
- **Concept**: IV Rank = (Current_IV − 52_Week_Low_IV) / (52_Week_High_IV − 52_Week_Low_IV) × 100. Ranges from 0-100; tells you where current IV sits relative to the last year's range (not just the absolute level). High IV Rank (>50) = relatively expensive options → favor selling. Low IV Rank (<20) = relatively cheap options → favor buying.
- **Note**: The source material references "IV Rank" in the SKILL.md (Strategy 7 Calendar Spread: "decided by where you are in the IV Rank cycle") but never provides the explicit formula. The formula above is standard industry formula, consistent with the implied use in the source.
- **Flag**: This formula is NOT explicitly stated anywhere in Document 3 — it is industry-standard derived from the concept referenced. Marked as an inference from context, not a direct source extract.
- **Source (indirect)**: SKILL.md Strategy 7 reference ("Expiry selection — weekly versus next-weekly versus monthly, decided by where you are in the IV Rank cycle").

### 2.80 Theoretical Edge (Natenberg)
- **Calc**: `Theoretical_Edge = Theoretical_Value (model output) − Market_Price (actual trade price)`
- If positive: option is underpriced, buy it and hedge
- If negative: option is overpriced, sell it and hedge
- **The delta-neutral hedge then converts this edge into realized profit** over the life of the option by mechanically buying low/selling high on the underlying (the "race" — Pattern from Part 1 / E31).
- **Source**: Natenberg synthesis (multiple passes: "The Mispricing Concept"; E12 worked example: "0.63 edge per option").

---

## 3. WORKED EXAMPLES — PART 3 (E35 onward)

**E35 — Jade Lizard Zero-Upside Corrected Example**
- Setup: Need net premium > call spread width.
- Data: Sell 22,800 PE @₹70 + Sell 23,300 CE @₹50 + Buy 23,400 CE @₹15. Net = 70+50-15 = ₹105. Call spread width = 23,400-23,300 = 100 pts. 105 > 100 → zero upside risk condition IS satisfied.
- If Nifty closes at 23,500 (above 23,400): Call spread loss = 100 pts. But total premium collected = 105 pts. Net = 105-100 = +5 pts profit. Zero upside risk confirmed.
- Downside break-even: 22,800 − 105 = 22,695.
- Source: Corrected version of Jade Lizard article (E10 in Part 1).

**E36 — OI Wall Positive GEX Mechanics (Template)**
- Setup: Nifty at 24,200, GEX positive. Heavy call OI at 24,400 strike (10 lakh lots).
- Mechanism: Call writers at 24,400 have sold calls and hedged by being short Nifty futures equivalent to Delta × OI. As Nifty rises toward 24,400, Delta of their calls increases → they must sell MORE Nifty futures to stay hedged → this creates mechanical overhead resistance at 24,400.
- Signal: If Nifty approaches 24,400 in a positive-GEX environment, the call-writer hedging creates real futures-sell pressure. This is support/resistance with a mechanical cause, not just a historical S/R line.
- Classification: This is the INVERSE of the cascade pattern (1.10) — same mechanism (delta-hedge forced trades), opposite direction (positive GEX makes OI a genuine barrier; negative GEX makes it a fuel canister).
- Source: `references/market_structure_gex.md` (OI Analysis + GEX mechanics).

**E37 — Iron Condor 2× Credit Adjustment Example**
- Setup: From E4. Sold 24,000-23,800 PE spread for ₹50 credit. Nifty drops to test 24,000 PE.
- Rule activation: 24,000 PE short being tested → either roll entire put spread OR close when the 24,000-23,800 spread costs ₹100 to buy back (= 2× original ₹50 credit).
- Action A (Roll, if ≥5 DTE): Buy back 24,000-23,800 spread at ₹100 (loss ₹50); sell new 23,600-23,400 spread for, say, ₹40 credit. Net position: original call spread still open, new put spread ₹200 further OTM.
- Action B (Close, if ≤2 DTE): Buy back the entire tested spread at 2× cost, accept the loss, let the untested call spread expire if still within breakeven.
- Source: `references/strategies_and_setups.md` (Strategy 2 adjustment trigger).

**E38 — VIX Term Structure Inversion Warning**
- Setup: Pre-RBI policy announcement (e.g., 3 days out). Check: front-month IV vs back-month IV.
- Data scenario: Front-month IV = 18%; Back-month IV = 14%. Front > Back = INVERTED = immediate-term uncertainty is being priced higher than medium-term. This is a signal to NOT initiate a calendar spread (you'd be selling the expensive front-month and buying the cheap back-month — the term structure may normalize violently post-announcement via IV crush on the front month).
- Alternative action: Post-announcement, if front-month IV collapses back below back-month IV (normal structure restored), then calendar spread becomes viable.
- Classification: Not bait/trigger/harvest — a timing and structure-selection example.
- Source: Passarelli synthesis (Volatility Term Structure); `references/greeks_and_pricing.md` (Volatility Skew — horizontal).

**E39 — Four-Directional Strategy Classification (Composite Decision Tree)**
- Setup: At market open, AXIS Direction Scorer produces a score and GEX/VIX regime is known.
- Classification decision tree:
  - Score = 4-5 (bullish) AND GEX positive AND VIX stable → UP → long call or bull put spread
  - Score = 1-2 (bearish) AND GEX negative AND VIX rising → DOWN → long put or bear call spread
  - Score = 3 (neutral) AND GEX positive AND VIX compressed → SIDEWAYS → straddle sell / iron condor
  - Score = 1-2 (bearish signal) AND GEX negative AND VIX at Weak Low → VOLATILE (not just DOWN) → buy OTM puts with down-target formula (cascade setup); do NOT sell naked puts despite the bearish score
- Key distinction: Score=bearish in POSITIVE GEX → just bearish. Score=bearish in NEGATIVE GEX with VIX at Weak Low → VOLATILE with directional bias → cascade trade, different strategy type entirely.
- Source: SKILL.md (Quick-Reference Matrix) + SKILL.md (5-signal Detection System) + Passarelli four-directional framework.

**E40 — Delta Convergence Near Expiry (Numeric)**
- Setup: Track 24,200 CE and 24,400 CE (200 pts OTM) as expiry approaches (Nifty at 24,200).
- 30 DTE: 24,200 CE Delta ≈ 0.52; 24,400 CE Delta ≈ 0.38.
- 7 DTE: 24,200 CE Delta ≈ 0.51; 24,400 CE Delta ≈ 0.26.
- 1 DTE: 24,200 CE Delta ≈ 0.50; 24,400 CE Delta ≈ 0.09.
- Expiry day: 24,200 CE Delta → binary (0 or 1 depending on final print); 24,400 CE Delta → very near 0.
- Lesson for AXIS Option Chain Selector: The same OTM strike (24,400) that had Delta=0.38 at 30 DTE barely responds near expiry (Delta=0.09). For directional buys near expiry, go ATM or 1 ITM to maintain meaningful Delta exposure.
- Source: nifty-options-pro `references/greeks_and_pricing.md` (Delta behavior table); Passarelli synthesis ("Delta approaches 1.00 for deep ITM... As time passes, ATM Deltas gravitate toward 0.50").

---

## 4. INSTITUTION-DETECTION RULES — PART 3 (entries 35 onward)

35. **IF** the Wyckoff Phase C Spring has occurred (false breakdown below range support on low volume + fast snap-back) **THEN** the next expected institutional action is a high-volume Sign of Strength (SOS) breaking the range ceiling — this is the trigger for a long entry on the LPS/BUEC pullback. **CONFIDENCE: HIGH** — this is the central Wyckoff Phase A→C→D sequence, stated consistently across multiple passes of the Wyckoff 2.0 synthesis. No single specific Nifty dated example is given for the complete Phase-A-through-E cycle, but the mechanism is described with enough detail and consistency to be HIGH confidence for the structural logic.

36. **IF** a breakout candle shows wide range + high volume + close near the extreme AND is happening on an EXPANDING volume trend relative to the corrective waves preceding it **THEN** this is an institutional SOS/SOW (genuine breakout), enter on the BUEC pullback. **IF** the same candle looks like a breakout but volume is similar to or lower than recent corrective waves **THEN** treat as a potential UTAD/Spring (institutional trap) and wait for confirmation. **CONFIDENCE: MEDIUM-HIGH** — the volume-expansion criterion for genuine vs. false breakouts is stated across multiple Wyckoff passages but without a specific dated numeric cutoff (what exact volume increase % qualifies as "expanding"?).

37. **IF** the 5-signal detection score ≥5 **AND** the confirmed Down_Target from the VIX formula AND the GEX Fibonacci target agree within ≤50 pts **THEN** that combined target zone is a high-confidence destination level and the OTM put strike should be selected 1-2 strikes below it (not at it). **CONFIDENCE: MEDIUM** — the convergence confidence principle is well-supported by June 23, 2026 (VIX 23,904 vs GEX 23,895 → actual 23,865 — within 40 pts), but this is a single dated example.

38. **IF** a trader holds a losing position and their reasoning has shifted from "this will work because X" to "I hope/expect it to recover" without any new objective data supporting that hope **THEN** the HAPI (Hope and Pray Index) is active and the position must be closed regardless of any other consideration. **IF** the same trader asks "would I enter this position fresh at current prices?" and the answer is NO **THEN** same conclusion: close, do not adjust. **CONFIDENCE: HIGH** — this discipline rule appears in Passarelli synthesis, Natenberg synthesis, and `references/risk_and_adjustments.md` independently. Three separate sources. The most cross-corroborated single rule in the entire material.

39. **IF** the session is expiry day **AND** the 0DTE sequence has produced 2 losing trades **THEN** all trading must STOP for the remainder of the session — no third trade regardless of how compelling the setup appears. **CONFIDENCE: HIGH** — explicitly stated: "Maximum 2 trades on expiry day. If both lose, stop." Appears in both SKILL.md and `references/strategies_and_setups.md` with identical wording.

40. **IF** weekly cumulative loss has reached 3% of total capital **THEN** all trading must stop for the remainder of that calendar week. No exceptions. No "recovery trades." **CONFIDENCE: HIGH** — explicitly stated as Rule 2 in `references/risk_and_adjustments.md` Capital Allocation Rules.

41. **IF** a long weekly option position has been held overnight **THEN** treat the morning opening position as compromised — the overnight Theta has reset the risk/reward, and the stop-loss level must be recalculated against the NEW premium, not the original entry premium. (The source rule says "Never hold a bought weekly option overnight" — this corollary handles the case where the hold DOES happen despite the rule.) **CONFIDENCE: HIGH** — the overnight hold prohibition is stated identically in the Nifty Options Trading Guide, SKILL.md Common Retail Errors, and Strategy 3 checklist. The corollary is logically derived.

42. **IF** price is at a known LVN (Low Volume Node) on the Volume Profile **AND** Order Flow at that level shows Initiative (large aggressive imbalance pushing away from the LVN) **THEN** treat the move as institutionally driven and expect rapid price travel through the LVN to the next HVN — this is the OPPOSITE of the absorption/reversal pattern. **CONFIDENCE: MEDIUM** — the LVN → rapid-travel rule is clearly stated in the Wyckoff 2.0 synthesis and in the Strategic Takeaways section ("expect a sudden, violent expansion in price at LVNs"), but no specific dated numeric example is provided.

43. **IF** Weis Wave corrective-wave volume begins to approach or exceed the volume of the prior impulse wave **THEN** the trend is losing institutional conviction — reduce position size or tighten stop-loss to protect gains, do NOT add. **IF** corrective-wave volume is consistently much smaller than impulse-wave volume **THEN** the trend has institutional support — hold with structure-defined stop. **CONFIDENCE: MEDIUM** — stated explicitly as the criterion for continuation vs. exhaustion, but the "approach or exceed" threshold is qualitative/visual with no specific ratio given in the source.

44. **IF** IV/HV comparison shows IV materially > HV for the same instrument AND GEX is positive (stable regime) **THEN** this is the optimal environment for premium selling (sell overpriced vol in a dampening regime). **IF** GEX is negative AND IV is at/below HV (vol is cheap) **THEN** this is the optimal environment for buying vol (buy cheap options before a mechanical cascade amplifies realized vol beyond what the market is pricing). **CONFIDENCE: HIGH** — the IV>HV→sell rule is stated across 4 independent source sections; the GEX-regime context needed to apply it correctly is established across all market_structure_gex.md references.

45. **IF** the OI build at a specific strike is rising rapidly while the LTP (Last Traded Price) of that same option is falling or flat **THEN** the dominant activity is WRITING (selling) at that strike, not buying. This is the most direct signal of institutional option selling pressure at a specific level. The reverse (OI rising + LTP rising) = buying pressure dominant. **CONFIDENCE: HIGH** — this specific OI+LTP divergence rule is stated directly in the source material (`references/market_structure_gex.md`: "OI surging at a specific strike while premium falls — rising OI with falling LTP means selling, not buying") and is identified in the conversation context as "the cleanest signature" of institutional writing.

---

## 5. LAYER CLASSIFICATION SUMMARY TABLE

| Layer | Description | Signal Examples from This Knowledge Base |
|---|---|---|
| **Layer A** (Anonymous Market-Wide) | What the whole options market collectively believes — no individual identity. Most trap-prone for retail. Lowest weight recommended until backtested. | GEX, VIX structure, PCR, Max Pain, Overnight OI build, IV term structure, IV vs HV, Lognormal skew, BankNifty IV multiplier, OI wall mechanics |
| **Layer B** (Institutional Identity Named) | Which specific large players are positioned which way. FII Participant-wise OI CSV is the primary source. Can diverge from Layer A (Layer A can look bullish while FIIs are net short — the mismatch itself is the signal). | FII long/short ratio trajectory, Iceberg order behavior class-level, Market-maker inventory skewing, Informed counterparty identification (Trader Memory) |
| **Layer C** (Live Order Flow / Liquidity) | What is happening in the current minute — not what positioning looked like overnight. Only layer that is genuinely real-time. | Delta Divergence, Absorption, Initiative, Imbalance, VPOC migration, Weis Wave contractions, Finished Auction, 3-step turn (Exhaustion+Absorption+Initiative), BUEC entry, all Volume Profile boundary signals |

**Layer B validation gap**: Layer B as defined (FII Participant-wise CSV) has NO worked dated examples within Document 3. It is theoretically the most reliable layer (stated in conversation context as "cannot be faked") but is empirically unvalidated in this material. Weight it conservatively until real backtesting against the FII CSV data is done.

---

## 6. AXIS COMPONENT MAPPING

Which patterns/formulas/rules belong to which AXIS system component:

### Component 1: Direction Scorer (1–5)
- **Layer A inputs**: GEX sign + magnitude (2.6), VIX formula targets (2.8-2.11), PCR trajectory (2.13), Max Pain (2.14 — positive GEX only), Overnight OI build (2.15), 5-signal score (2.44), Signal hierarchy override (2.67)
- **Layer B inputs**: FII long/short ratio trajectory (data gap — see above)
- **Layer C inputs**: OI+LTP divergence (Rule 45), Delta Divergence at key levels (1.19), VPOC migration direction (1.20)
- **Key formulas**: 2.6, 2.8, 2.10, 2.13, 2.44, 2.67
- **Key rules**: Rules 1-9, 29, 44, 45
- **Weight note**: Layer C (order flow) has the most proven evidence in the 15-day dataset; Layer A is most trap-prone; Layer B is unvalidated — do NOT hard-code weights; derive them from backtesting the five real examples.

### Component 2: Structure Confirmation Gate (Yes/No)
- **Wyckoff structural events**: SOS/SOW (1.51-1.52), LPS/LPSY (1.53-1.54), Spring/UTAD (1.49-1.50)
- **Volume Profile boundaries**: VAH/VAL/VPOC/LVN/HVN (2.24, 1.22)
- **Volume Profile profile shapes**: P/b/D (1.34-1.36), Double-distribution (1.37)
- **Order Flow confirmation**: Absorption (1.17), Initiative (1.18), 3-step turn (1.49+1.51+1.18)
- **Key constraint**: Order Flow signals are ONLY valid AT Volume Profile boundaries (Rule 25, Part 2). Order Flow in the middle of a range = noise.
- **Key formulas**: 2.62-2.65 (all four Wyckoff strategy execution blueprints)
- **Robotic Labeling Caveat**: Use principles (sequence of events + volume character), NOT pattern matching. No two structures look identical.

### Component 3: Strategy Activation Module
- **Four-directional selection**: 1.64, 2.46, E39
- **Strategy templates**: 2.3 (Theta), Straddle (2.54), Iron Condor (2.59), Directional Buy, Vertical Spread, Calendar (2.72), OTM Put Cascade, Jade Lizard (2.66)
- **Adjustment rules**: 2.68 (60% straddle trigger), 2.69 (iron condor 2× rule), 2.50-2.51 (exit thresholds)
- **Expiry timing**: Thursday = expiry; 7 DTE initiation, 1-2 DTE close for straddles; 10:00 AM wait for 0DTE
- **Regime filter**: Do NOT enter in flip zone or when score = 2-4 (1.66)

### Component 4: Knowledge Interpreter Agent
- **Primary responsibility**: Identify whether a setup looks like genuine institutional accumulation/distribution vs. a retail trap
- **Core patterns to evaluate**: Spring vs. genuine breakdown (1.49), UTAD vs. genuine breakout (1.50), Delta Divergence (1.19), Absorption vs. Initiative (1.17-1.18), OI wall positive vs. negative GEX context (1.60, 1.10), VIX structural lead (1.11), PCR trap (1.8)
- **Books this agent should reference**: Wyckoff 2.0 (structural sequence), Passarelli (Greek profiles of different market states), Natenberg (theoretical edge + delta-neutral hedge "race" framing)
- **Output format specified in source**: One paragraph + confidence label (high/medium/low)

### Component 5: Final EV Verifier Agent
- **Formula inputs**: 2.31 (Expected Value E = W×Pw − L×Pl), 2.30 (Kelly Criterion for sizing), 2.77 (Sharpe/Sortino/Max Drawdown for system health monitoring)
- **Target convergence**: 2.75 (when VIX formula + GEX Fibonacci targets agree → higher confidence → use in EV calculation)
- **Transaction costs**: 2.42 (₹85-95/lot round trip) must be subtracted from gross EV to get net EV
- **EV threshold**: Positive EV after costs → proceed. Negative → block alert regardless of how good everything else looks.

### Component 6: Option Chain Selector
- **Strike selection**: 2.70 (complete reference table), 2.1 (Delta band 0.35-0.55 for directional), 2.71 (BankNifty multiplier), 1.65 (Delta convergence near expiry)
- **Jade Lizard zero-upside verification**: 2.66 (corrected formula — must check before entering)
- **OI liquidity filter**: Exclude strikes with insufficient OI/volume (threshold not numerically specified in source — flagged as a gap requiring real data calibration)
- **Bid-ask spread filter**: Exclude strikes with wide spread (threshold not numerically specified in source — flagged as a gap)
- **Expiry selection**: Based on IV Rank cycle (2.79 — indirectly referenced), VIX regime, and whether a major event sits inside the current week (flag from 2.9/2.10 weekly move formula)
- **OI wall proximity check**: 1.60 — avoid strikes near heavy OI working against direction in positive GEX (in negative GEX this is irrelevant — see Rule 8)

### Component 7: Risk/Capital/Money Management
- **Capital rules**: 2.49 (2% single trade, 3% weekly limit, 6-month defined-risk rule)
- **Kelly fraction**: 2.30 (use half-Kelly in practice for safety margin)
- **Position sizing**: 2.17 (equivalent Nifty exposure), 2.43 (capital sizing table)
- **Theta viability gate**: 2.20 (if Total_Theta_Cost > expected gross profit → DO NOT trade)
- **Transaction costs**: 2.42 (₹85-95/lot) must be included in all EV calculations
- **Tax**: 2.41 (F&O turnover calculation), 2.60 (advance tax schedule)
- **Journal**: 2.61 (required fields template)
- **System health review**: If win rate < 50% for 2 consecutive months → halve position size + defined-risk only (stated in `references/risk_and_adjustments.md` Greek Drift Management Weekly Review Rule)

---

## 7. REMAINING GENUINE KNOWLEDGE GAPS
(Items referenced in the source material but not numerically/procedurally defined — require external data or calibration)

1. **FII Participant-wise OI CSV data**: Layer B is theoretically defined but empirically unvalidated. Source explicitly says "pull the Participant-wise OI CSV for June 16-30 and check" — this data was not in Document 3.

2. **OI/Volume minimum threshold for option liquidity**: The source says "Exclude illiquid strikes where the bid-ask spread will eat your edge" and "Minimum open interest and volume" as criteria for the Option Chain Selector — but gives NO specific numbers (how many lots minimum OI? What maximum bid-ask spread in rupees?). This must be calibrated from real chain data.

3. **Maximum bid-ask spread cutoff**: Same as above — stated as a criterion but no numeric threshold given anywhere in Document 3.

4. **The "Naked VPOC" definition**: Referenced in Wyckoff Strategy 4 targets ("naked VPOC lines on the historical macro timeline") but never defined in the source. Industry standard: a VPOC from a prior session that was never subsequently revisited becomes a "naked" (untested) VPOC and acts as a future magnet. This interpretation is consistent with the source's use but is NOT explicitly stated.

5. **GVOF Framework details**: Referenced in conversation context as the currently active strategy module (Component 3) but its specific setup rules, filters, and conditions are not present anywhere in Document 3.

6. **Composite Profile VPOC**: Strategy 3 targets "the structural VPOC from the macro Composite Profile" — a multi-session combined profile's VPOC. The concept is referenced but the calculation methodology (which sessions to combine, what time window) is not specified in Document 3.

7. **The exact "IV Rank cycle" for expiry selection**: SKILL.md says expiry selection is "decided by where you are in the IV Rank cycle" but the IV Rank formula (2.79) itself was not in Document 3 — it was inferred from industry standard. The specific thresholds (e.g., "IV Rank < 20 = buy weekly; IV Rank > 50 = sell weekly") are not given.

8. **The specific Weis Wave "volume ratio" threshold**: The qualitative rule is clear (corrective waves must be smaller than impulse waves) but no specific ratio (e.g., "corrective < 50% of impulse") is given. Requires calibration from real session data.

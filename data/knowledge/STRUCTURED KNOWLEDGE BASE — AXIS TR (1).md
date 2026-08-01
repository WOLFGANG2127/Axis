STRUCTURED KNOWLEDGE BASE — AXIS TRADING SYSTEM
1. PATTERN LIBRARY (Market Nature & Psychology)
Pattern 1: Institutional Theta Capture (ATM Straddle Sale)
Data Conditions:

GEX positive (>0)
VIX low/stable
No major events within 7 DTE window
Nifty in range-bound environment
ATM CE + ATM PE sold simultaneously
Commonly Confused With: Naked option selling (this has dual premium collection, naked is single leg)

Layer: Anonymous market-wide sentiment (GEX regime defines environment)

Source: Nifty Options Trading Guide - Strategy 1; Strategies and Setups - Strategy 1

Pattern 2: Defined Risk Range Trading (Iron Condor)
Data Conditions:

GEX positive
Sideways trend confirmed
Elevated IV (selling expensive options)
Bull put spread + Bear call spread combined
Wings placed 200+ points from ATM
Initiated 5-7 DTE
Commonly Confused With: Strangle sale (iron condor has defined max loss, strangle does not)

Layer: Anonymous market-wide sentiment

Source: Nifty Options Trading Guide - Strategy 2; Strategies and Setups - Strategy 2

Pattern 3: Retail Far-OTM Buying Trap
Data Conditions:

Trader buys option >300 points OTM on weekly expiry
Premium appears "cheap" (₹5-20 range)
Requires massive Gamma acceleration to overcome Theta
Statistically fails most of the time
Theta decay accelerates in final 7 days (15-25% daily for ATM, even worse for OTM)
Commonly Confused With: Genuine cheap leverage opportunity

Layer: N/A - this is a trader behavior pattern, not market pattern

Source: Nifty Options Trading Guide - Delta section; Common Retail Errors section; Strategies and Setups - Strike Selection Guidelines

Pattern 4: Expiry Day 0DTE Volatility Pattern
Data Conditions:

Expiry day (Thursday for weekly)
Initial volatility 9:15-10:00 AM is noise, not signal
ATM strike = maximum OI battle zone
Theta at maximum
Gamma at extreme
Options can swing 200-500% in minutes
Hold time max 15-60 minutes
Stop-loss 30% of premium
Commonly Confused With: Intraday trend continuation

Layer: Live order flow (real-time OI/gamma battle at ATM)

Source: Nifty Options Trading Guide - Strategy 4; Strategies and Setups - Expiry Day 0DTE Protocol

Pattern 5: IV Crush Pattern (Event-Driven)
Data Conditions:

2-4 VIX points rise in days leading up to event (RBI policy, Budget, FOMC, elections)
Options become expensive (inflated premiums)
After announcement: IV collapses
Option premiums drop sharply regardless of Nifty direction
Buying options before events = expensive and often unprofitable even if direction correct
Selling after IV collapse captures decay
Commonly Confused With: Directional move (the crush happens independent of direction)

Layer: Anonymous market-wide sentiment (IV aggregate expectation)

Source: Nifty Options Trading Guide - IV and Vega section; Common Retail Errors; Strategies and Setups - Strategy 5

Pattern 6: GEX Positive Regime (Range-Bound/Dampened)
Data Conditions:

GEX > 0 (positive)
Market-makers are net long gamma
MM hedging suppresses volatility (buying as market falls, selling as it rises)
Nifty tends to gravitate toward range
Max Pain becomes relevant magnet
Straddle/strangle selling profitable
Explosive moves less likely
Commonly Confused With: Bullish market (GEX positive doesn't mean bullish, means dampened)

Layer: Anonymous market-wide sentiment

Source: Skill file - Quick-Reference Matrix; Five Market Structure Signals; Expiry Day Protocol

Pattern 7: GEX Negative Regime (Cascade Risk)
Data Conditions:

GEX < 0 (negative)
Market-makers are net short gamma
MM hedging amplifies moves (selling as market falls, buying as it rises)
Explosive directional moves likely
Max Pain becomes irrelevant
Straddle/strangle buying profitable
OTM options in cascade direction can multiply
Commonly Confused With: Simple bearish/bullish trend (this is structural amplification, not just direction)

Layer: Anonymous market-wide sentiment

Source: Skill file - Quick-Reference Matrix; Strategy 6 (OTM Put Buy - Cascade Signal)

Pattern 8: GEX Flip Zone (Transition)
Data Conditions:

GEX near zero, transitioning from positive to negative or vice versa
Regime uncertainty
High risk of whipsaw
Recommended action: reduce size, wait for confirmation
No clear strategy until regime establishes
Commonly Confused With: Low volatility calm (this is instability, not calm)

Layer: Anonymous market-wide sentiment

Source: Skill file - Quick-Reference Matrix

Pattern 9: VIX Weak Low Pattern
Data Conditions:

VIX at or near local low
Indicates complacency
Often precedes explosive move
Combined with GEX negative = high cascade risk
Can persist multiple sessions before break
Detection: VIX CHoCH/BOS upward = momentum confirmation
Commonly Confused With: Low volatility = safe environment (actually high risk of explosion)

Layer: Anonymous market-wide sentiment

Source: Skill file - 5-Signal Detection System; Strategy 6 example

Pattern 10: VIX CHoCH (Change of Character) Pattern
Data Conditions:

VIX structure breaks prior pattern
Higher low formed after series of lower lows = bullish VIX (fear returning)
Lower high formed after series of higher highs = bearish VIX (fear subsiding)
Can precede price movement by multiple days
Example from user's data: June 19 VIX CHoCH predicted June 23 explosion 4 days in advance
Commonly Confused With: Random VIX fluctuation

Layer: Anonymous market-wide sentiment (leading indicator)

Source: Skill file - 5-Signal Detection System (+1 point for VIX CHoCH/BOS upward)

Pattern 11: PCR Trap Pattern (Rising PCR in Negative GEX)
Data Conditions:

PCR rising (put writing increasing)
GEX negative (cascade regime active)
Rising PCR interpreted as "bullish floor" by retail
Reality: put writing = fuel for downward cascade, not floor
More puts written = more fuel when cascade triggers
This is specifically flagged as TRAP signal in detection system
Commonly Confused With: Bullish signal (retail reads rising PCR as bullish)

Layer: Anonymous market-wide sentiment (misinterpretation pattern)

Source: Skill file - 5-Signal Detection System (+1 point for PCR rising + GEX negative = TRAP signal); Common Retail Errors

Pattern 12: Max Pain Magnetism (Positive GEX Only)
Data Conditions:

GEX positive regime
Max Pain strike acts as magnet
Nifty gravitates toward Max Pain at expiry
ONLY valid in positive GEX environments
In negative GEX, Max Pain becomes irrelevant
Commonly Confused With: Universal rule (it's regime-dependent)

Layer: Anonymous market-wide sentiment

Source: Skill file - Five Market Structure Signals (Max Pain only valid in positive GEX); Common Retail Errors

Pattern 13: OI Wall Resistance/Support Pattern
Data Conditions:

Heavy OI concentration at specific strike
Acts as resistance (if call OI) or support (if put OI)
Price tends to stall or reverse at OI walls
Combined with GEX regime for strength assessment
Overnight OI build >50% = significant positioning
Commonly Confused With: Technical support/resistance (this is options-driven, not price-driven)

Layer: Anonymous market-wide sentiment + Institutional identity (who holds the OI)

Source: Skill file - Five Market Structure Signals (OI wall + PCR); 5-Signal Detection System

Pattern 14: STT Trap Pattern (Expiry Day)
Data Conditions:

ITM option held through expiry without squaring off
STT on expiry exercise = 0.125% of intrinsic value
STT on regular sale = 0.0625% (half the rate)
Example: ₹22,500 intrinsic value → STT = ₹28 per lot
On larger positions, STT becomes significant
Always square off ITM options before 3:00 PM on expiry day
Commonly Confused With: Normal expiry settlement

Layer: N/A - regulatory/cost pattern

Source: Nifty Options Trading Guide - STT Trap section; Strategies and Setups - Expiry Day Protocol

Pattern 15: Overnight Theta Decay Trap (Weekly Options)
Data Conditions:

Weekly option bought and held overnight
ATM weekly loses 15-20% premium per day in final week
3 DTE: theta ₹30-50 (12-20% of premium daily)
1 DTE: theta ₹50-100 (25-50% of premium daily)
Expiry day: all remaining extrinsic value lost (100%)
Holding overnight = guaranteed decay cost
Commonly Confused With: Swing trade opportunity

Layer: N/A - time decay mechanical pattern

Source: Nifty Options Trading Guide - Theta table; Common Retail Errors; Strategies and Setups - Directional Option Buying

Pattern 16: Gamma Scalping Pattern (Professional MM Technique)
Data Conditions:

Delta-neutral position established
Long gamma (long options)
As underlying moves, delta changes
Trader adjusts (buys/sells underlying) to rebalance to delta-neutral
Profits from gamma while paying theta
Hallmark of professional market-maker operations
Commonly Confused With: Directional trading

Layer: Live order flow (requires real-time delta management)

Source: Trading Option Greeks - Part III Volatility section; Skill file - Gamma Scalping reference

Pattern 17: Delta-Neutral Positioning Pattern
Data Conditions:

Total position delta = 0
Profit/loss driven by Vega and Theta, not direction
Isolates volatility trading from directional risk
Requires constant adjustment as delta drifts
Used by market makers to capture IV discrepancies
Commonly Confused With: Hedged position (hedged reduces risk, delta-neutral eliminates directional exposure)

Layer: N/A - position construction pattern

Source: Trading Option Greeks - Multiple sections; Skill file - Core Philosophy

Pattern 18: Volatility Skew Pattern (Vertical)
Data Conditions:

IV differs across strike prices in same month
Typically: downside puts trade at higher IV than upside calls
Cause: higher institutional demand for portfolio protection
Creates opportunity: identify mispriced options relative to skew
Can be exploited via ratio spreads
Commonly Confused With: Random IV variation

Layer: Anonymous market-wide sentiment (supply/demand signature)

Source: Trading Option Greeks - Part I Volatility section

Pattern 19: Volatility Term Structure Pattern (Horizontal Skew)
Data Conditions:

IV differs across expiration months
Front months: lower IV in calm markets, higher IV during panic/pending news
Back months: typically more stable
Calendar spreads exploit term structure differences
Normal structure: front < back month IV
Commonly Confused With: Single IV reading

Layer: Anonymous market-wide sentiment

Source: Trading Option Greeks - Part I Volatility section; Strategies and Setups - Strategy 7 (Calendar Spread)

Pattern 20: Put-Call Parity Arbitrage Pattern
Data Conditions:

Formula: Stock + Put + Interest - Dividend - Strike = Call
If parity violated, arbitrage opportunity exists
Synthetics can replicate any position
Professional market makers use to eliminate directional risk
Conversions/Reversals capture pricing discrepancies
Commonly Confused With: Separate call/put analysis

Layer: N/A - mathematical relationship pattern

Source: Trading Option Greeks - Part I Put-Call Parity section

Pattern 21: Synthetic Position Replication Pattern
Data Conditions:

Synthetic Long Call = Long Stock + Long Put
Synthetic Long Put = Short Stock + Long Call
Synthetic Long Stock = Long Call + Short Put
Exact risk/reward profile replicated using different instruments
Used for arbitrage, position transformation, margin efficiency
Commonly Confused With: Original position

Layer: N/A - position engineering pattern

Source: Trading Option Greeks - Part I Put-Call Parity section

Pattern 22: Overnight OI Build Pattern (>50%)
Data Conditions:

OI at specific strike increases >50% overnight
Indicates significant institutional positioning
Combined with other signals for direction assessment
Part of 5-signal detection system (+2 points)
Source: StockMojo Multi OI & Volume
Commonly Confused With: Normal daily OI change

Layer: Institutional identity (who built the OI overnight)

Source: Skill file - 5-Signal Detection System

Pattern 23: Nonlinearity Pattern (Options vs Stock)
Data Conditions:

Options driven by multiple variables: Delta, Gamma, Theta, Vega simultaneously
Not simply "leveraged stock"
Price can move against you even if direction correct (if IV drops or time passes)
Professional traders trade the variables, not just direction
Ignoring any Greek destroys edge
Commonly Confused With: Leveraged stock trading

Layer: N/A - pricing mechanics pattern

Source: Trading Option Greeks - Rule of Nonlinearity; Skill file - Core Philosophy

Pattern 24: Four-Directional Trading Pattern
Data Conditions:

Professional traders profit from: Up, Down, Sideways, Volatile
Sideways = sell volatility/collect theta (straddles, condors)
Volatile = buy volatility (straddles, strangles)
Not limited to bullish/bearish binary
Commonly Confused With: Directional-only trading

Layer: N/A - strategy selection pattern

Source: Trading Option Greeks - Four-Directional Rule; Skill file - Core Philosophy

Pattern 25: HAPI Pattern (Hope and Pray Index)
Data Conditions:

Holding bad trade without adjustment plan
No pre-defined exit rules
"Hoping" market reverses instead of managing
Critical warning against undisciplined holding
Professional response: adjust or close, never hope
Commonly Confused With: Patient holding

Layer: N/A - trader behavior pattern

Source: Trading Option Greeks - Part IV Advanced Trading section

2. FORMULA REFERENCE
Formula 1: Delta (Δ)
Inputs:

Option type (Call/Put)
Moneyness (ITM/ATM/OTM)
Time to expiration
Implied Volatility
Calculation:

Output of options pricing model (Black-Scholes)
Call Delta: 0 to 1.00 (deep ITM approaches 1.00, far OTM approaches 0)
Put Delta: 0 to -1.00 (deep ITM approaches -1.00, far OTM approaches 0)
ATM options: approximately ±0.50
What It Tells You In Isolation:

How much premium changes per ₹1 Nifty move
Approximate probability of expiring ITM (0.50 Delta ≈ 50% probability)
Equivalent stock position (0.50 Delta × 25 lot size = 12.5 shares equivalent)
What It CANNOT Tell You Alone:

How quickly Delta will change (need Gamma)
Impact of time passing (need Theta)
Impact of volatility changes (need Vega)
Whether the Delta will stay stable (it won't — Gamma modifies it)
Typical Value Ranges:

Deep ITM: 0.80-1.00 (calls) or -0.80 to -1.00 (puts)
ATM: 0.45-0.55 (calls) or -0.45 to -0.55 (puts)
Far OTM: 0-0.20 (calls) or -0.20 to 0 (puts)
Extreme Reading: Delta >0.90 or <-0.90 = option behaves almost like stock (minimal leverage benefit)

Source: Nifty Options Trading Guide - Delta section; Trading Option Greeks - Delta section; Skill file - Greeks System

Formula 2: Gamma (Γ)
Inputs:

Option type (Call/Put)
Moneyness
Time to expiration
Implied Volatility
Calculation:

Second derivative of option price with respect to underlying
Rate of change of Delta per ₹1 move
Always positive for long options, negative for short options
What It Tells You In Isolation:

How quickly Delta will change
Acceleration of option price movement
Risk exposure to large moves
What It CANNOT Tell You Alone:

Direction of Delta change (need to know if long or short)
Cost of holding Gamma (need Theta)
Whether Gamma exposure is worth it (need to compare to Theta cost)
Typical Value Ranges:

ATM: Highest Gamma
Deep ITM/Far OTM: Low Gamma
Near expiry: ATM Gamma spikes significantly
Extreme Reading: High Gamma near expiry = explosive Delta changes, high risk/reward

Source: Trading Option Greeks - Gamma section; Skill file - Greeks System

Formula 3: Theta (Θ)
Inputs:

Option type (Call/Put)
Moneyness
Time to expiration
Implied Volatility
Calculation:

Rate of time decay per day
Usually expressed as negative number for long options
Non-linear: accelerates as expiration approaches
What It Tells You In Isolation:

Daily cost of holding option (if long)
Daily income from selling option (if short)
How much premium lost simply by time passing
What It CANNOT Tell You Alone:

Whether Theta cost is justified (need to compare to expected move/Gamma benefit)
Impact of volatility changes (need Vega)
Whether decay rate will accelerate (need to know DTE trajectory)
Typical Value Ranges (ATM Nifty Options):

Days to Expiry
Theta (approx)
Daily Decay as % of Premium
30 days	₹5-8	1-2%
14 days	₹10-15	3-5%
7 days	₹15-25	6-10%
3 days	₹30-50	12-20%
1 day (expiry eve)	₹50-100	25-50%
Expiry day	All remaining extrinsic	100%

Extreme Reading: Expiry day ATM = entire extrinsic value lost in one day

WARNING FLAG: This formula is MISLEADING if used alone for buying decisions — must be paired with Gamma assessment to determine if expected move justifies decay cost

Source: Nifty Options Trading Guide - Theta table; Trading Option Greeks - Theta section; Skill file - Greeks System

Formula 4: Vega (V)
Inputs:

Option type (Call/Put)
Moneyness
Time to expiration
Calculation:

Change in option price per 1 percentage point change in IV
Same for calls and puts (long options = positive Vega)
What It Tells You In Isolation:

Sensitivity to volatility changes
How much option gains if IV rises
How much option loses if IV falls
What It CANNOT Tell You Alone:

Whether IV will rise or fall (need IV analysis/forecast)
Impact of directional move (need Delta)
Whether IV level is high or low relative to history (need IV Rank/Percentile)
Typical Value Ranges:

ATM options: Highest Vega (most time premium)
ITM/OTM: Lower Vega
Longer DTE: Higher Vega
Shorter DTE: Lower Vega (less time premium to affect)
Extreme Reading: High Vega near events = large P&L swing expected from IV crush

WARNING FLAG: This formula is CRITICAL around events — IV crush can destroy long option value even if direction correct

Source: Nifty Options Trading Guide - IV and Vega section; Trading Option Greeks - Vega section; Skill file - Greeks System

Formula 5: Rho (ρ)
Inputs:

Option type (Call/Put)
Time to expiration
Strike price
Calculation:

Change in option price per 1 percentage point change in interest rates
What It Tells You In Isolation:

Interest rate sensitivity
Higher rates = higher call values, lower put values
What It CANNOT Tell You Alone:

Almost everything — Rho is negligible for short-term options
Only significant for LEAPS (long-term options)
Typical Value Ranges:

Weekly options: Negligible (<₹0.01)
Monthly options: Small
LEAPS: Significant
Extreme Reading: N/A for Nifty weekly trading

Source: Trading Option Greeks - Rho section; Skill file - Greeks System (noted as negligible for weekly options)

Formula 6: GEX (Gamma Exposure)
Inputs:

Full options chain data (all strikes, all expiries)
OI at each strike
Gamma at each strike
Call/Put classification
Calculation:

GEX = Σ(Call_OI × Call_Gamma) - Σ(Put_OI × Put_Gamma)
Aggregated across all strikes and expiries
Positive GEX = net long gamma (MM hedging suppresses volatility)
Negative GEX = net short gamma (MM hedging amplifies volatility)
What It Tells You In Isolation:

Market regime: positive = dampened, negative = cascade risk
Whether MM hedging will suppress or amplify moves
Strategy selection framework
What It CANNOT Tell You Alone:

Direction of move (only magnitude/amplification)
Timing of break (need VIX structure)
Whether to buy calls or puts (need additional signals)
Typical Value Ranges:

Positive GEX: Range-bound expected
Negative GEX: Explosive moves expected
Near zero: Transition zone
Extreme Reading: Strongly negative GEX + VIX at Weak Low = high cascade probability

Source: Skill file - Five Market Structure Signals; Quick-Reference Matrix; referenced as "Gamma Exposure" from StockMojo

Formula 7: PCR (Put-Call Ratio)
Inputs:

Total Put OI (or volume)
Total Call OI (or volume)
Calculation:

PCR = Total Put OI / Total Call OI
Can be calculated for current expiry, all expiries, or specific strikes
What It Tells You In Isolation:

Ratio of put to call activity
High PCR = more puts than calls (often interpreted as bearish sentiment)
Low PCR = more calls than puts (often interpreted as bullish sentiment)
What It CANNOT Tell You Alone:

Whether high PCR is put buying (bearish) or put selling (bullish) — THIS IS CRITICAL
Must be paired with GEX regime
In negative GEX: rising PCR = put writing = FUEL for cascade, not floor
In positive GEX: rising PCR may indicate support building
Typical Value Ranges:

PCR > 1.0: More puts than calls
PCR < 1.0: More calls than puts
Extremes vary by market conditions
Extreme Reading: PCR rising sharply + GEX negative = TRAP signal (documented in 5-signal system)

WARNING FLAG: This formula is HIGHLY MISLEADING if used alone — the material explicitly flags "Treating rising PCR as bullish when GEX is negative" as a retail error

Source: Skill file - Five Market Structure Signals; 5-Signal Detection System; Common Retail Errors

Formula 8: Max Pain
Inputs:

OI at each strike (calls and puts separately)
Strike prices
Calculation:

For each strike, calculate total loss for option buyers if Nifty expires at that strike
Max Pain = strike where total option buyer loss is maximum
Indicates where option sellers (often institutions) benefit most
What It Tells You In Isolation:

Theoretical magnet level at expiry
Where option sellers have maximum incentive to defend/push price
What It CANNOT Tell You Alone:

Whether Max Pain will actually work (requires positive GEX regime)
Timing of gravitation toward Max Pain
Whether current positioning supports Max Pain level
Typical Value Ranges:

Usually near ATM but can deviate based on OI distribution
Extreme Reading: N/A — relevance depends on regime, not value

WARNING FLAG: This formula is INVALID in negative GEX regimes — material explicitly states "Relying on Max Pain when GEX is negative" as retail error

Source: Skill file - Five Market Structure Signals; Common Retail Errors

Formula 9: IV Rank
Inputs:

Current IV
1-year high IV
1-year low IV
Calculation:

IV Rank = (Current IV - 52-week Low) / (52-week High - 52-week Low) × 100
Expressed as percentage (0-100%)
What It Tells You In Isolation:

Where current IV sits relative to past year range
High IV Rank = options relatively expensive
Low IV Rank = options relatively cheap
What It CANNOT Tell You Alone:

Whether IV will rise or fall from here
Directional expectation
Whether to buy or sell (need strategy context)
Typical Value Ranges:

0-25%: Low IV (options cheap)
25-75%: Moderate IV
75-100%: High IV (options expensive)
Extreme Reading: IV Rank <20% + negative GEX = asymmetric long volatility opportunity

Source: Referenced in Skill file context, detailed formula not in provided text

Formula 10: Daily Volatility Estimation from IV
Inputs:

Implied Volatility (annualized)
Calculation:

Daily Volatility = IV / √256
(256 = approximate trading days in year, some use 252)
What It Tells You In Isolation:

Expected daily price range (1 standard deviation)
Can be used to set daily targets/stops
What It CANNOT Tell You Alone:

Direction of move
Whether move will happen today or over multiple days
Probability of hitting the range
Typical Value Ranges:

IV 12% → Daily Vol ≈ 0.75% (≈180 points on 24,000 Nifty)
IV 15% → Daily Vol ≈ 0.94% (≈225 points on 24,000 Nifty)
IV 20% → Daily Vol ≈ 1.25% (≈300 points on 24,000 Nifty)
Example from text: Spot 24,100, VIX 12.89 → Target = 24,100 - 196 = 23,904

Source: Trading Option Greeks - Understanding Volatility section

Formula 11: Put-Call Parity
Inputs:

Stock price
Strike price
Call price
Put price
Interest rate
Dividends
Calculation:

Stock + Put + Interest - Dividend - Strike = Call
Or: Call - Put = Stock - Strike × e^(-rT) + Present Value of Dividends
What It Tells You In Isolation:

Mathematical relationship between calls, puts, and underlying
If violated, arbitrage opportunity exists
Basis for synthetic positions
What It CANNOT Tell You Alone:

Whether to buy or sell
Directional expectation
Volatility assessment
Typical Value Ranges: N/A — this is an identity that should hold exactly

Extreme Reading: Any deviation from parity = arbitrage opportunity (typically small, captured by market makers)

Source: Trading Option Greeks - Put-Call Parity section

Formula 12: Down Target Formula (Cascade Trade)
Inputs:

Spot price
VIX percentage
Calculation:

Down Target = Spot - (Spot × VIX% ÷ √252)
What It Tells You In Isolation:

Expected downside target when cascade signal fires
Based on 1 SD daily move from IV
What It CANNOT Tell You Alone:

Whether cascade will actually happen (need GEX/VIX confirmation)
Timing
Whether target will be exceeded
Example from text:

Spot: 24,100
VIX: 12.89%
Calculation: 24,100 - (24,100 × 0.1289 ÷ 15.87) = 24,100 - 196 = 23,904
Source: Skill file - 5-Signal Detection System

Formula 13: Equivalent Exposure (Position Sizing)
Inputs:

Option Delta
Number of lots
Lot size (25 for Nifty 2026)
Calculation:

Equivalent Exposure = Delta × Lots × Lot Size
What It Tells You In Isolation:

How much Nifty exposure your option position represents
Compare to maximum comfortable Nifty equivalent
What It CANNOT Tell You Alone:

Whether exposure is appropriate (need capital/risk context)
How exposure will change if Nifty moves (need Gamma)
Total risk (need to incorporate premium paid)
Example:

0.50 Delta × 2 lots × 25 = 25 shares equivalent
Source: Skill file - Position Sizing Framework

Formula 14: New Delta After Move (Gamma Scenario)
Inputs:

Starting Delta
Gamma
Expected move in points
Calculation:

New Delta ≈ Starting Delta + (Gamma × Expected Move)
What It Tells You In Isolation:

How Delta will change after a move
Whether position will become too large/small
What It CANNOT Tell You Alone:

Whether the move will happen
Direction of move
Impact of time/volatility changes during move
Example from text: If thesis requires 50-100 pt move, calculate Delta after that move to ensure position stays within tolerance

Source: Skill file - Position Sizing Framework

Formula 15: Expected Vega P&L
Inputs:

Option Vega
Expected IV Change (as percentage)
Calculation:

Expected Vega P&L = Vega × Expected IV Change %
What It Tells You In Isolation:

How much option will gain/lose from IV change
Critical for event trades (IV crush)
What It CANNOT Tell You Alone:

Whether IV will actually change as expected
Directional P&L (need Delta)
Time decay cost (need Theta)
WARNING FLAG: Must include post-event IV crush in calculation for event trades

Source: Skill file - Position Sizing Framework

Formula 16: Total Theta Cost
Inputs:

Theta per day
Expected holding days
Calculation:

Total Theta Cost = Theta per day × Expected Holding Days
What It Tells You In Isolation:

How much premium will be lost to time decay
Whether trade is viable (compare to expected profit)
What It CANNOT Tell You Alone:

Whether decay rate will accelerate
Whether expected move will overcome decay
Gamma benefit that offsets decay
Decision Rule from text: If Theta cost > expected gross profit from directional move → trade is not viable

Source: Skill file - Position Sizing Framework

Formula 17: 5-Signal Detection Score
Inputs:

GEX sign (positive/negative)
VIX position (at/near Weak Low)
Overnight OI build percentage
PCR direction
VIX CHoCH/BOS status
Calculation:

GEX < 0 → +3 points
VIX at/near Weak Low → +2 points
Overnight OI build > 50% → +2 points
PCR rising + GEX negative → +1 point
VIX CHoCH/BOS upward → +1 point
Maximum possible: 9 points
What It Tells You In Isolation:

Cascade risk assessment for expiry day
Action framework based on score
What It CANNOT Tell You Alone:

Exact timing of cascade
Magnitude beyond formula target
Whether other factors will intervene
Score Interpretation:

Score ≥ 5 → BUY OTM PUTS (cascade risk high)
Score 2-4 → Reduce size, no directional bias
Score ≤ 1 → Sell premium / range trade
Source: Skill file - Expiry Day 9:15 AM Detection System

Formula 18: Straddle Breakeven
Inputs:

ATM strike price
Total premium collected (CE + PE)
Calculation:

Upper Breakeven = ATM Strike + Total Premium
Lower Breakeven = ATM Strike - Total Premium
What It Tells You In Isolation:

Range within which straddle seller profits
Points where straddle buyer breaks even
What It CANNOT Tell You Alone:

Probability of staying in range
Whether range is realistic given volatility
Adjustment points
Example from text:

ATM: 24,200
Total premium: ₹340
Upper BE: 24,540
Lower BE: 23,860
Source: Strategies and Setups - Strategy 1

Formula 19: Iron Condor Max Loss
Inputs:

Spread width (per side)
Net credit received
Calculation:

Max Loss per lot = (Spread Width - Credit) × Lot Size
What It Tells You In Isolation:

Worst-case loss if both spreads fail
Defined risk amount
What It CANNOT Tell You Alone:

Probability of max loss
When to adjust before hitting max loss
Expected P&L (need probability)
Example from text:

Spread width: 200 points
Credit: ₹100
Max loss: (200 - 100) × 25 = ₹2,500 per side
Source: Strategies and Setups - Strategy 2

Formula 20: Kelly Fraction
Inputs:

Win rate
Average win
Average loss
Calculation:

Kelly = (Win% × Avg Win / Avg Loss) - (1 - Win%)
Often used as half-Kelly for safety
What It Tells You In Isolation:

Optimal position size for growth
Balances growth vs. ruin risk
What It CANNOT Tell You Alone:

Whether win rate estimate is accurate
Whether conditions have changed
Practical constraints (margin, lot size)
Note: Formula referenced in Skill file context but detailed calculation not in provided text

Source: Skill file - Position Sizing Framework (referenced)

3. WORKED EXAMPLES — STRUCTURED
Example 1: ATM Straddle Sale (Theta Capture)
Setup/Context: Nifty at 24,200, positive GEX, stable VIX, no events in 7 DTE

Exact Data Values:

Nifty spot: 24,200
Sell 24,200 CE @ ₹180
Sell 24,200 PE @ ₹160
Total credit: ₹340
Total premium collected: ₹340 × 25 = ₹8,500
Margin: ~₹1,50,000-1,80,000
Breakevens:

Upper: 24,200 + 340 = 24,540
Lower: 24,200 - 340 = 23,860
Outcome (Theoretical):

If Nifty stays between 23,860-24,540 at expiry: profit = ₹8,500
If Nifty closes exactly at 24,200: max profit = ₹8,500
If Nifty moves beyond breakevens: unlimited loss
Predicting Signal: GEX positive regime = range-bound expected, straddle sale profitable

Classification: Strategy example (not bait/trigger/harvest — this is institutional theta capture)

Source: Strategies and Setups - Strategy 1

Example 2: Iron Condor (Defined Risk)
Setup/Context: Nifty at 24,200, positive GEX, sideways trend, elevated IV

Exact Data Values:

Bear call spread: Sell 24,400 CE + Buy 24,600 CE
Bull put spread: Sell 24,000 PE + Buy 23,800 PE
Net credit: ₹80-120 per lot = ₹2,000-3,000 per lot
Spread width: 200 points per side
Max Loss:

Per lot: (200 - 100) × 25 = ₹2,500 per side
Max Profit:

Per lot: ₹2,000-3,000 (net credit)
Probability of Profit: 55-65% when wings 200+ pts from ATM

Outcome (Theoretical):

If Nifty stays between 24,000-24,400: full profit
If Nifty breaches short strikes: limited loss
Predicting Signal: GEX positive + sideways = range trade profitable

Classification: Strategy example

Source: Strategies and Setups - Strategy 2

Example 3: Directional Option Buying
Setup/Context: Clear technical signal confirmed, GEX confirms direction, VIX not too high

Exact Data Values:

Entry: Buy ATM or 1-strike ITM option
Example: Buy ₹150 CE
Stop-loss: 40-50% of premium = exit at ₹75-90
Profit target: 80-100% of premium = exit at ₹270-300
Position sizing: 1-2% of capital (₹5L capital → ₹5,000-10,000 max premium)
Execution Constraints:

Enter during first 2 hours (highest liquidity)
Weekly options: do NOT hold overnight
Monthly options: can hold overnight for swing
Outcome (Theoretical):

Hit stop: lose ₹60-75 per option
Hit target: gain ₹120-150 per option
R:R approximately 1:2
Predicting Signal: Technical confirmation + GEX alignment = directional buy

Classification: Strategy example

Source: Strategies and Setups - Strategy 3

Example 4: OTM Put Buy — Cascade Signal (June 23, 2026)
Setup/Context: Expiry day, cascade detection score ≥ 5

Exact Data Values:

Nifty spot at open: 24,127
GEX: -3.94M Cr (NEGATIVE)
VIX: 12.89 (Weak Low)
Down target calculation: 24,100 - (24,100 × 0.1289 ÷ 15.87) = 24,100 - 196 = 23,904
Action: Buy 23,850 PE @ ₹12-15
Outcome:

23,850 PE went from ₹12 to ₹30+
Driver: VIX spike × Delta gain
Predicting Signal: GEX negative + VIX Weak Low = cascade risk; 5-signal score ≥5 confirmed

Classification: TRIGGER → HARVEST (GEX flip = trigger, cascade = harvest)

Source: Strategies and Setups - Strategy 6

Example 5: Vertical Debit Spread (Bullish)
Setup/Context: Nifty at 24,200, clear bullish view, GEX confirms, IV slightly elevated

Exact Data Values:

Buy 24,200 CE @ ₹180
Sell 24,400 CE @ ₹80
Net debit: ₹100
Total cost: ₹100 × 25 = ₹2,500
Outcomes:

Max profit (Nifty above 24,400 at expiry): (200 - 100) × 25 = ₹2,500
Max loss (Nifty below 24,200 at expiry): ₹2,500 (premium paid)
Breakeven: 24,200 + 100 = 24,300
Advantage over naked long: Lower breakeven, lower Vega exposure, costs less Theta

Predicting Signal: Technical + GEX bullish = directional debit spread

Classification: Strategy example

Source: Strategies and Setups - Strategy 4

Example 6: STT Trap (Expiry Day)
Setup/Context: ITM option held through expiry

Exact Data Values:

Option: 22,000 CE
Nifty close: 22,300
Intrinsic value: 300 × 75 = ₹22,500
STT on expiry exercise: 0.125% × ₹22,500 = ₹28
Comparison:

If sold before expiry: STT = 0.0625% of sale price (half the rate)
Difference: ₹14+ per lot
Outcome: Higher tax cost by letting ITM option expire

Predicting Signal: N/A — this is a cost trap, not a market signal

Classification: N/A — regulatory/cost example

Source: Nifty Options Trading Guide - STT Trap section

Example 7: IV Crush Scenario (RBI Policy)
Setup/Context: Days before RBI policy announcement

Exact Data Values:

IV rises 2-4 VIX points in days leading up
Options become expensive
After announcement: IV collapses
Outcome:

Options bought before event lose value from IV crush
Direction correct but still unprofitable
Options sold after crush capture decay
Predicting Signal: Event approaching = IV will rise then crush

Classification: BAIT (inflated premiums) → HARVEST (IV crush)

Source: Nifty Options Trading Guide - IV and Vega section

Example 8: Theta Decay by DTE (Multiple Scenarios)
Setup/Context: ATM Nifty option held across different timeframes

Exact Data Values:

Scenario
DTE
Theta
Daily Decay %
1	30 days	₹5-8	1-2%
2	14 days	₹10-15	3-5%
3	7 days	₹15-25	6-10%
4	3 days	₹30-50	12-20%
5	1 day	₹50-100	25-50%
6	Expiry day	All extrinsic	100%

Outcome:

Holding from Day 30 to Day 7: ~8-10% total decay (relatively mild)
Holding from Day 7 to Day 0: ~100% decay (total loss of extrinsic)
Predicting Signal: N/A — this is mechanical decay

Classification: N/A — time decay mechanics

Source: Nifty Options Trading Guide - Theta table

4. INSTITUTION-DETECTION RULES
Rule 1: GEX Regime Detection
IF GEX > 0 (positive)
THEN Market-makers are net long gamma; hedging will suppress volatility; range-bound environment expected; straddle/condor selling favorable
CONFIDENCE: HIGH (multiple strategy references, core framework signal)
Source: Skill file - Quick-Reference Matrix; Five Market Structure Signals

Rule 2: GEX Negative Cascade Detection
IF GEX < 0 (negative) AND VIX at/near Weak Low
THEN Market-makers are net short gamma; hedging will amplify moves; explosive directional move likely; OTM options in cascade direction can multiply; BUY OTM PUTS if other signals confirm
CONFIDENCE: HIGH (Strategy 6 explicit example, 5-signal system)
Source: Skill file - Quick-Reference Matrix; Strategy 6; 5-Signal Detection System

Rule 3: GEX Flip Zone Detection
IF GEX near zero (transitioning)
THEN Regime uncertain; high whipsaw risk; reduce position size; wait for confirmation before strategy selection
CONFIDENCE: HIGH (explicit in matrix)
Source: Skill file - Quick-Reference Matrix

Rule 4: VIX Weak Low Detection
IF VIX at or near local low (no specific numerical threshold given in text)
THEN Complacency present; explosive move potential elevated; combine with GEX for action
CONFIDENCE: MEDIUM (described as pattern but no specific threshold defined)
Source: Skill file - 5-Signal Detection System

Rule 5: VIX CHoCH Detection (Leading Indicator)
IF VIX forms higher low after series of lower lows (bullish VIX CHoCH)
THEN Fear returning to market; explosive downside move likely within 2-4 sessions; pre-position for cascade
CONFIDENCE: HIGH (explicitly noted as leading indicator with 4-day advance warning example)
Source: Skill file - 5-Signal Detection System; user's documented June 19→June 23 example

Rule 6: PCR Trap Detection
IF PCR rising AND GEX negative
THEN Rising PCR is from put WRITING (not buying); this is FUEL for downward cascade, not bullish floor; DO NOT interpret as bullish signal
CONFIDENCE: HIGH (explicitly labeled as TRAP signal in 5-signal system)
Source: Skill file - 5-Signal Detection System; Common Retail Errors

Rule 7: Overnight OI Build Detection
IF OI at specific strike increases >50% overnight
THEN Significant institutional positioning occurred; flag for potential support/resistance at that strike
CONFIDENCE: MEDIUM (included in 5-signal system but no worked examples showing outcome)
Source: Skill file - 5-Signal Detection System

Rule 8: Max Pain Relevance Detection
IF GEX positive
THEN Max Pain is relevant; Nifty may gravitate toward Max Pain at expiry
CONFIDENCE: HIGH (explicitly stated as valid in positive GEX)
Source: Skill file - Five Market Structure Signals

Rule 9: Max Pain Irrelevance Detection
IF GEX negative
THEN Max Pain is IRRELEVANT; do not use Max Pain as target or support level
CONFIDENCE: HIGH (explicitly stated as invalid in negative GEX, listed as retail error)
Source: Skill file - Five Market Structure Signals; Common Retail Errors

Rule 10: IV Crush Timing Detection
IF Major event (RBI policy, Budget, FOMC, elections) within 2-3 days
THEN IV will rise pre-event (options expensive); IV will crush post-event (options lose value regardless of direction); do NOT buy options before event unless specifically playing volatility
CONFIDENCE: HIGH (multiple references, explicit warning in retail errors)
Source: Nifty Options Trading Guide - IV section; Common Retail Errors; Strategy 5

Rule 11: Theta Decay Acceleration Detection
IF Option has <7 DTE
THEN Theta decay accelerates exponentially; daily decay 6-10%+ of premium; avoid holding long options unless expecting imminent move
CONFIDENCE: HIGH (explicit table provided)
Source: Nifty Options Trading Guide - Theta table

Rule 12: Expiry Day Gamma Risk Detection
IF Trading 0DTE (expiry day)
THEN Gamma at extreme; Delta changes rapidly; options can swing 200-500% in minutes; use 30% stop-loss; hold max 15-60 minutes; maximum 2 trades
CONFIDENCE: HIGH (explicit protocol)
Source: Nifty Options Trading Guide - Strategy 4; Strategies and Setups - 0DTE Protocol

Rule 13: Far OTM Futility Detection
IF Considering buying option >300 points OTM on weekly expiry
THEN Statistical failure rate high; requires massive Gamma acceleration to overcome Theta; avoid
CONFIDENCE: HIGH (explicitly warned in retail errors and strike selection)
Source: Common Retail Errors; Strategies and Setups - Strike Selection Guidelines

Rule 14: Delta-Neutral Position Detection
IF Position has total Delta ≈ 0
THEN Directional risk eliminated; P&L driven by Vega and Theta only; can profit from volatility changes without directional prediction
CONFIDENCE: HIGH (core concept from Trading Option Greeks)
Source: Trading Option Greeks - Part III; Skill file - Core Philosophy

Rule 15: Volatility Skew Exploitation Detection
IF Downside puts trading at significantly higher IV than upside calls (vertical skew)
THEN Institutional demand for protection elevated; may indicate fear; can exploit via ratio spreads or skewed condors
CONFIDENCE: MEDIUM (described as pattern but no specific exploitation examples)
Source: Trading Option Greeks - Volatility section

Rule 16: Term Structure Calendar Opportunity Detection
IF Front month IV < Back month IV (normal term structure)
THEN Calendar spread favorable; sell near-dated, buy far-dated; profit from differential decay
CONFIDENCE: HIGH (Strategy 7 explicit)
Source: Strategies and Setups - Strategy 7 (Calendar Spread)

Rule 17: Put-Call Parity Arbitrage Detection
IF Call - Put ≠ Stock - Strike (adjusted for interest/dividends)
THEN Arbitrage opportunity exists; can construct synthetic to capture discrepancy
CONFIDENCE: HIGH (mathematical identity)
Source: Trading Option Greeks - Put-Call Parity section

Rule 18: STT Trap Avoidance Detection
IF Holding ITM option on expiry day
THEN Square off before 3:00 PM; letting expire triggers 0.125% STT on intrinsic value (double the normal 0.0625% rate)
CONFIDENCE: HIGH (explicit calculation provided)
Source: Nifty Options Trading Guide - STT Trap section

Rule 19: Overnight Weekly Option Hold Detection
IF Holding bought weekly option overnight
THEN Guaranteed 15-20%+ decay cost; avoid unless swing trading monthly expiry only
CONFIDENCE: HIGH (explicit in directional buying rules and retail errors)
Source: Nifty Options Trading Guide - Theta table; Strategies and Setups - Strategy 3; Common Retail Errors

Rule 20: Cascade Down Target Calculation
IF 5-signal score ≥ 5 (cascade confirmed)
THEN Calculate down target: Spot - (Spot × VIX% ÷ √252); buy OTM puts 1-2 strikes below ATM; target the calculated level
CONFIDENCE: HIGH (explicit formula and worked example)
Source: Skill file - 5-Signal Detection System; Strategy 6

Rule 21: Position Size Limit Detection
IF Single position risk > 2% of capital OR weekly loss > 3% of capital
THEN STOP trading; risk limits exceeded
CONFIDENCE: HIGH (explicit capital allocation rules)
Source: Skill file - Capital Allocation Rules (Risk Management section, cut off but table provided)

Rule 22: Theta Viability Detection
IF Total Theta Cost > Expected gross profit from directional move
THEN Trade is NOT viable; do not enter
CONFIDENCE: HIGH (explicit decision rule)
Source: Skill file - Position Sizing Framework

Rule 23: HAPI (Hope and Pray) Detection
IF Holding losing trade without pre-defined adjustment plan
THEN In HAPI zone; adjust or close immediately; never "hope" for reversal
CONFIDENCE: HIGH (explicit warning from Trading Option Greeks)
Source: Trading Option Greeks - Part IV

Rule 24: Adjustment Trigger Detection
IF Straddle position moves beyond 60% of expected range (~200 pts)
THEN Convert to strangle by rolling tested leg further OTM OR add delta hedge via futures
CONFIDENCE: MEDIUM (explicit rule but no worked example of adjustment outcome)
Source: Strategies and Setups - Strategy 1

Rule 25: Iron Condor Roll Trigger Detection
IF Nifty tests either short strike of iron condor
THEN Roll entire tested side further OTM OR close tested spread at 2× credit received
CONFIDENCE: MEDIUM (explicit rule but no worked example)
Source: Strategies and Setups - Strategy 2

DISAGREEMENT/CONFLICT FLAGS:
None identified in this material. The sources are internally consistent. However, note:

Single-example rules vs. multi-example rules: The June 23, 2026 cascade trade is the ONLY worked example of the full 5-signal system triggering. Rules 4 (VIX Weak Low), 7 (Overnight OI Build), 15 (Volatility Skew Exploitation), 24 (Straddle Adjustment), 25 (Condor Roll) have no worked outcome examples — they are stated as rules but not validated with specific trade results in this material.
Missing thresholds: VIX "Weak Low" is referenced but no numerical threshold defined. PCR extreme values not specified. These require external definition or backtesting to set.
5. COVERAGE CHECK
Documents/Sections Processed:
Nifty Options Trading Guide (by Karthik Subramanian, March 2026)
Nifty Options Basics (terms table) ✓
Understanding the Greeks for Nifty Options (Delta, Theta sections) ✓
Implied Volatility and Vega section ✓
Strategy 1: ATM Straddle Sale ✓
Strategy 2: Iron Condor ✓
Strategy 3: Directional Option Buying ✓
Strategy 4: Expiry Day 0DTE ✓
STT Trap section ✓
Conclusion ✓
Trading Option Greeks — Core Modules Summary
Part I: Basics of Option Greeks ✓
Part II: Spreads ✓
Part III: Volatility ✓
Part IV: Advanced Option Trading ✓
Mindset of an Option Trader ✓
Trading Option Greeks — Detailed Structural Breakdown
The Foundation: Market Mechanics ✓
The Language of Sensitivity (The Greeks) ✓
Volatility Dynamics ✓
The Path to Professionalism: Trading Strategies ✓
Trading Option Greeks — The "Rules" of Professional Option Trading
Rule of Nonlinearity ✓
Rule of Uncertainty Management ✓
Four-Directional Rule ✓
Rule of Sensitivity (The Greeks) ✓
Delta-Neutral Strategy Rule ✓
"Fair Game" Rule (Volatility Selling) ✓
Trading Option Greeks — Comprehensive Technical Guide
Part I: The Foundations ✓
Part II: Spreads ✓
Part III: Volatility ✓
Part IV: Advanced Trading & Action ✓
Rules Summary ✓
Detailed Greek definitions (Delta, Gamma, Theta, Vega, Rho) ✓
Volatility section (HV, IV, Expected Volatility, Skew) ✓
Strategy Dynamics (Volatility Buying vs. Selling) ✓
Put-Call Parity and Synthetic Positions ✓
NIFTY STRATEGY OPTIONS TRADING SPREAD — 30 Articles List
Article titles listed (not content) ✓
Note: These are article titles only, no content to extract
Nifty Professional Options Skill (Skill File)
Core Philosophy ✓
Quick-Reference: Market Context → Strategy Matrix ✓
Five Market Structure Signals ✓
The Greeks System — Nifty Context ✓
Strategy Toolkit ✓
Position Sizing Framework ✓
Expiry Day 9:15 AM Detection System (5-Signal Checklist) ✓
Common Retail Errors to Flag and Correct ✓
Reference Files list ✓
Strategies and Setups — Deep Reference
Strategy 1: ATM Straddle Sale ✓
Strategy 2: Iron Condor ✓
Strategy 3: Directional Option Buying ✓
Strategy 4: Vertical Debit Spread ✓
Strategy 5: Long Straddle / Strangle ✓
Strategy 6: OTM Put Buy (Cascade Signal) ✓
Strategy 7: Calendar Spread ✓
Expiry Day 0DTE Protocol (Detailed) ✓
Strike Selection Guidelines ✓
Risk Management and Adjustments — Deep Reference
Capital Allocation Rules (partial — table complete, text cut off) ✓
Note: Document was truncated at "If weekly loss hits 3%, stop al"
Intentional Omissions: NONE
No sections were skipped or compressed as "redundant." Where the same concept appeared in multiple documents (e.g., Delta definition appeared in 4+ places), each occurrence was logged separately or cross-referenced to show source coverage.

Unusable/Corrupted Content:
NIFTY STRATEGY OPTIONS TRADING SPREAD — 30 Articles List: This is a table of article titles only. No content exists to extract. Flagged as "titles only, no content."
Risk Management and Adjustments — Deep Reference: Document truncated mid-sentence at "If weekly loss hits 3%, stop al". The capital allocation table was complete, but adjustment rules, Greek drift rules, tax framework, and stop rules referenced in the skill file's reference list were NOT in the provided text.
Ambiguous/Hard-to-Categorize Items Flagged for Review:
VIX "Weak Low": Referenced multiple times as a detection signal (+2 points in 5-signal system) but no numerical definition provided. What VIX level constitutes "Weak Low"? Requires external definition or user clarification.
"Expected Range" in straddle adjustment: Rule states "If Nifty moves beyond 60% of expected range (~200 pts)" — how is "expected range" calculated? VIX formula gives daily range, but is "expected range" here daily or total-to-expiry? Ambiguous.
GEX flip level: Referenced in Skill file ("gamma flip level") but no formula or threshold provided for what GEX value constitutes "flip zone" vs. clearly positive/negative.
PCR divergence: Referenced in user's earlier context as a Layer A input but not explicitly defined in this source material with formula or interpretation rules.
Max Pain calculation: Referenced as relevant but no calculation formula provided in this material.
Kelly fraction: Referenced in Skill file context but formula not in provided text.
END OF STRUCTURED KNOWLEDGE BASE

think deeper , what is remaining from the file & data , think deeper & if anything is missing then gave it below 

Thought Process
Here is exactly what was missed or under-extracted from the raw text in the previous pass. These are the granular gaps:

1. PATTERN LIBRARY — Missing Additions
Pattern 26: Professional Theta Capture Timing Window

Data Conditions: Positions initiated exactly 7-10 days before expiry; closed exactly 1-2 days before expiry.
Reasoning: Captures the steepest part of the theta curve (final 7 days) while explicitly avoiding the extreme gamma risk of expiry day.
Layer: Anonymous market-wide sentiment (time-decay mechanics)
Source: Nifty Options Trading Guide - Theta section
Pattern 27: VWAP as Strictly Secondary Signal

Data Conditions: Price above/below VWAP used only for entry timing after GEX regime and strategy are confirmed.
Rule: Never used as a primary signal generator. If GEX is unclear, VWAP direction does not justify a trade.
Layer: Live order flow (entry timing)
Source: Skill file - Five Market Structure Signals; 0DTE Protocol
Pattern 28: Pin Risk (Expiry Day Mechanical)

Data Conditions: At expiry, ATM options have massive Delta shifts (0 to 1 or vice versa) with tiny underlying moves.
Institutional Response: Market makers use Jelly Rolls to offset synthetic positions across months to mitigate this assignment uncertainty.
Layer: N/A - mechanical expiry risk
Source: Trading Option Greeks - Put-Call Parity section (Boxes and Jelly Rolls)
2. FORMULA REFERENCE — Missing Additions
Formula 21: Black-Scholes 6 Inputs (Theoretical Value)

Inputs: 1. Stock Price, 2. Strike Price, 3. Time to Expiration, 4. Interest Rate, 5. Dividends, 6. Volatility.
What it tells you: The mathematical "fair value" of an option.
What it CANNOT tell you: Actual market price. Market price is driven by open market supply and demand, which is why IV is derived by plugging the market price into the model and solving for volatility, not the other way around.
Source: Trading Option Greeks - Comprehensive Technical Guide (Price vs. Value section)
Formula 22: Delta Time-Decay Gravitational Pull

Inputs: ATM option, passing time.
Calculation/Rule: As time passes, ATM Deltas gravitate toward 0.50 (regardless of where they started).
What it tells you: An option that was slightly ITM with a 0.60 Delta weeks ago will behave more like a 0.50 Delta option as expiry nears, reducing its directional responsiveness.
Source: Trading Option Greeks - Delta section
Formula 23: ATM vs. ITM/OTM Theta Decay Curves

Inputs: Moneyness status.
Rule: ATM options decay at an accelerating rate as expiration nears. ITM and OTM options decay at a steadier (more linear) pace.
What it tells you: The exponential theta curve mentioned in the Nifty guide applies specifically to ATM options, not equally across the chain.
Source: Trading Option Greeks - Theta section
Formula 24: Directional Buying R:R Ratio

Inputs: Stop-loss (40-50% of premium) + Profit Target (80-100% of premium).
Calculation: Risk = ~₹75 (on ₹150 premium). Reward = ~₹150. Ratio = 1:2.
What it tells you: The mathematical risk/reward framework for Strategy 3 directional buys.
Source: Strategies and Setups - Strategy 3
3. WORKED EXAMPLES — Missing Additions / Corrections
Example 9: Lot Size Discrepancy Flag

Setup/Context: Cross-referencing document sections.
Exact Data Values:
Nifty Options Trading Guide basics table: "Premium Cost... Rs 150 x 75 (lot size)"
Skill file & Strategies file: "Lot_Size(25)"
Outcome/Interpretation: The source material contains a lot size conflict (75 vs 25). This must be resolved using current 2026 NSE/SEBI guidelines before any position sizing math is executed. All Strategy P&L examples in the "Strategies and Setups" file use 25.
Source: Nifty Options Trading Guide vs. Skill file
4. INSTITUTION-DETECTION RULES — Missing Additions
Rule 26: Supply/Demand IV vs. Model IV

IF Implied Volatility is derived from a pricing model
THEN Recognize that IV is actually driven by open market supply and demand for options, not the model itself. High IV = real buying pressure/fear, not just a mathematical output.
CONFIDENCE: HIGH (explicit philosophical foundation in text)
Source: Trading Option Greeks - Detailed Structural Breakdown; Comprehensive Guide
Rule 27: "Would I Do It Now?" Mental Stop Rule

IF You are holding a short volatility trade (negative Gamma/Vega) and the stock makes an explosive move
THEN Ask: "If I didn't have this position right now, would I establish it at these current prices?" If NO, close the trade immediately. Do not hope.
CONFIDENCE: HIGH (explicit "Fair Game" rule context)
Source: Trading Option Greeks - Strategy Dynamics section
Rule 28: Adding to Losing Options = Shifted Greek Profile

IF An options position is losing and you consider "averaging down" by buying more
THEN REJECT. The Greek profile of the new addition is different from the original entry (Delta, Gamma, Theta have all changed due to price/time movement). You are not averaging down; you are opening a structurally different trade.
CONFIDENCE: HIGH (listed explicitly under Common Retail Errors)
Source: Skill file - Common Retail Errors
Rule 29: Conversions/Reversals Arbitrage

IF Put-Call Parity is slightly mispriced
THEN Market makers execute Conversions (Long Stock + Short Call + Long Put) or Reversals to create perfectly flat Delta, capturing pricing discrepancies related strictly to interest rates (Rho) or dividends.
CONFIDENCE: HIGH (explicit professional MM tactic)
Source: Trading Option Greeks - Put-Call Parity section
Rule 30: 0DTE VWAP Trend Entry

IF Trading 0DTE AND Nifty is trending (above/below VWAP with momentum)
THEN Buy the ATM option in the trend direction (only after 10:00 AM settle).
CONFIDENCE: MEDIUM (listed as 0DTE rule but no worked example of outcome)
Source: Nifty Options Trading Guide - Strategy 4
Rule 31: Monthly Target Expectations (Capital Scaling)

IF Capital is X and max risk is 2%
THEN Monthly target range scales as follows:
₹3L cap → ₹8,000-15,000 monthly target
₹5L cap → ₹15,000-25,000 monthly target
₹10L cap → ₹30,000-50,000 monthly target
CONFIDENCE: HIGH (explicit table provided)
Source: Skill file - Capital Sizing Table
Rule 32: The OCC Guarantee Mechanism

IF You trade an option
THEN The Options Clearing Corporation (OCC) stands between buyer and seller. This is the bedrock mechanism that allows you to exit a trade before expiry without finding the original counterparty.
CONFIDENCE: HIGH (foundational market mechanic)
Source: Trading Option Greeks - Detailed Structural Breakdown
5. COVERAGE CHECK — Final Resolution
The "30 Articles List" (NIFTY STRATEGY OPTIONS TRADING SPREAD — COMPLETE 2026 COVERAGE) remains the only completely unusable section—it is purely a title index with zero body text to extract.

The Risk Management and Adjustments file is confirmed truncated exactly at: "If weekly loss hits 3%, stop al". No adjustment triggers, Greek drift rules, or tax frameworks (beyond STT) were present in the provided raw text to extract.

With these additions, the provided raw text is now 100% exhausted.
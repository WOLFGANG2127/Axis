# AXIS Knowledge Base — Structured Rule Library
Extracted from: Nifty Options Trading Guide (NiftyTradingPro/Karthik Subramanian), nifty-options-pro SKILL.md + 4 reference files, NSE Bank Nifty Options Strategies booklet, *Trading Option Greeks* (Dan Passarelli), *Option Volatility & Pricing* (Sheldon Natenberg), *Options Trading for the Institutional Investor* (Michael Thomsett), *Options Trading Handbook* (Mahesh Chander Kaushik), QUANT BIBLE (MIT Sloan), Options Pricing & Greeks Analysis (GitHub/Black-Scholes-MonteCarlo project), Wyckoff 2.0 (Structures, Volume Profile, Order Flow), Bookmap/Footprint orderflow note, and institutional algo-architecture commentary.

Format: rule-library / reference, not prose. Use Ctrl-F on pattern names, formula names, or rule IDs.

---

# SECTION 1 — PATTERN LIBRARY (Market Nature & Psychology)

### P1. Institutional Accumulation / Distribution (Wyckoff Range Build)
- **Identifying conditions:**
  - Price stops a prior trend abruptly (Phase A: PS/PSY → SC/BC → AR → ST).
  - Price then moves sideways for an extended period (Phase B), building a horizontal or sloped range — this lateral period is the "cause."
  - Volume during range-build is elevated relative to the prior trend but doesn't produce net price progress (effort vs. result divergence).
  - Range can slope upward (accumulation, buyers refuse to let price reach oversold extremes) or downward (distribution, sellers flood supply, lower highs/lower lows).
  - Phase C: a shakeout test (Spring for accumulation, UTAD for distribution) — false breakout beyond the range to capture stop-loss liquidity.
  - Phase D: SOS (Sign of Strength) or SOW (Sign of Weakness) — wide-range, high-volume bar breaking structure in the cause's direction.
  - Phase E: trend confirmed, fully exits the range.
  - LPS (Last Point of Support) / LPSY (Last Point of Supply): final low-volume pullback/retest before trend launch.
- **Confused with:** A normal consolidation/no-trend chop with no institutional footprint; distinguished by the presence of a climax event (SC/BC) at entry and a Spring/UTAD shakeout at the range low/high, plus volume profile confirmation (see P9).
- **Layer:** Structure/order-flow layer (Layer C) primarily; Volume Profile and Order Flow are used to validate.
- **Source:** Wyckoff 2.0 — Wyckoff Methodology section; AXIS prior-conversation "Structure Confirmation Gate."

### P2. Retail Trap (Bait → Trigger → Harvest)
- **Identifying conditions (3-phase signature):**
  1. **Bait:** A textbook-looking, retail-legible setup forms (e.g., bullish PCR + price sitting on Max Pain + positive-looking GEX) that draws in directional retail positioning.
  2. **Trigger:** A signal invisible to plain price action confirms institutions are building the opposite real position — visible only in OI/GEX/VIX data: GEX flipping sign, OI surging at a strike while LTP (premium) falls simultaneously (selling, not buying), VIX structural break (CHoCH/BOS) days ahead of price, or PCR rising in a *negative*-GEX regime (misread as bullish, actually fuel).
  3. **Harvest:** The natural unwind/cascade does the work — no more institutional action needed once retail is positioned wrong.
- **Confused with:** A genuine bullish/bearish continuation signal; distinguished by checking GEX sign and Layer C order-flow data — if Layer A (PCR/Max Pain) signals one direction while GEX is negative or OI-vs-LTP diverges, it is very likely a trap, not a genuine signal.
- **Layer:** Spans all three — Layer A is what creates the bait (it's the layer most vulnerable to misreading), Layer C (order flow / OI-LTP divergence) and the VIX early-warning check are what reveal the trigger.
- **Source:** AXIS prior conversation, "trap-mechanism document" — five real June 2026 NIFTY examples (June 16, June 22–23, June 19–23, June 29, June 30).

### P3. Rising OI + Falling LTP at a Strike (Pure Selling Signature)
- **Identifying conditions:** Open Interest at a specific strike increases sharply (e.g., +851%) while the Last Traded Price (premium) of that same strike falls sharply (e.g., −46.80%) on the same candle/session.
- **What it means:** Unambiguous selling pressure (writers selling/shorting that option) regardless of what PCR or GEX say in isolation — new short positions being opened, not new long positions.
- **Confused with:** Rising OI alone being read as "more interest/more buying" — distinguished by checking premium direction simultaneously; OI rising + LTP rising = buying; OI rising + LTP falling = selling.
- **Layer:** Layer C (order flow/liquidity) — the layer best evidenced in the user's own real dataset.
- **Source:** AXIS prior conversation, trap-mechanism document — June 29 2026 example (23,950 CE).

### P4. Liquidity Sweep (Equal Highs/Lows Pool Grab)
- **Identifying conditions:** Price spikes past a marked technical level (equal highs/lows, an obvious round number, or a prior swing point) by a small overshoot (e.g., 6.15 points), then reverses sharply. The overshoot is just far enough to clear retail stop-loss orders resting beyond the level.
- **What it means:** A pure liquidity-pool signature — stops sitting above/below the level get triggered (turning into aggressive market orders), and institutions use that forced liquidity to fill their real position before reversing price.
- **Confused with:** A genuine breakout/continuation — distinguished by the immediate, sharp reversal right after the overshoot and by the small, deliberate-looking magnitude of the overshoot (just enough to clear stops, not a genuine breakout move).
- **Layer:** Layer C (order flow/liquidity).
- **Source:** AXIS prior conversation, trap document — June 30 2026 example (23,950 zone equal-highs sweep).

### P5. VIX Structural Lead-Time Warning
- **Identifying conditions:** India VIX prints a Weak Low and/or a CHoCH (Change of Character) on its own 15-min chart structure (SMC analysis applied to VIX itself), occurring multiple days *before* NIFTY price shows any corresponding move.
- **What it means:** A distinct early-warning component — VIX structure can predict a large NIFTY move (e.g., predicted a multi-hundred-point move 4 days in advance) while price action shows nothing yet. Should be tracked as a standing, persistent multi-day caution flag — not folded into a same-day-only regime classifier, since it loses its multi-day predictive value if treated as just another same-day input.
- **Confused with:** Normal VIX noise/volatility chop — distinguished by an actual structural break (CHoCH/BOS) on the VIX chart itself, not just a VIX level reading.
- **Layer:** Layer A (market-wide, anonymous), but explicitly recommended to be elevated to its own persistent/standing flag rather than blended into the daily Layer A score.
- **Source:** AXIS prior conversation, trap document; nifty-options-pro `market_structure_gex.md` ("VIX CHoCH upward," "VIX BOS upward").

### P6. Gamma Flip / Negative GEX Cascade (Dealer-Driven Amplification)
- **Identifying conditions:** Net GEX crosses from positive to negative (or price trades below the Gamma Flip Level). Below the flip level, declines that were slow above it become violent and self-reinforcing.
- **What it means:** Dealers are short Gamma and become pro-cyclical (sell dips, buy rallies) instead of stabilizing — the same put OI that looked like a "floor" in a positive-GEX read becomes forced-selling fuel via delta-hedge cascades once GEX flips negative. Cascade intensity scales with OI × Gamma² (second-order effect), which is why expiry-day cascades (max Gamma, max OI) are fastest.
- **Confused with:** A "support level holding" read based on high put OI — distinguished by checking GEX sign first; high put OI is support ONLY in positive GEX, and is cascade fuel in negative GEX.
- **Layer:** Layer A (GEX is the regime master switch) combined with Layer C mechanics (delta-hedge cascade is literally order flow).
- **Source:** nifty-options-pro `market_structure_gex.md` — "Delta Hedge Cascade," real June 23 2026 example (Gamma Flip Level ≈24,050).

### P7. PCR Trap in Negative-GEX Regime
- **Identifying conditions:** PCR is rising (e.g., 1.18 → 1.21) at the same time Net GEX is negative.
- **What it means:** Looks bullish/protective by standard interpretation but is actually bearish — rising PCR in negative GEX means put writers are loading up more delta-hedge obligations (more forced-selling fuel waiting to fire), not building a protective floor.
- **Confused with:** Standard bullish PCR-rising interpretation (valid ONLY when GEX is positive) — distinguished strictly by checking GEX sign before interpreting PCR direction.
- **Layer:** Layer A, explicitly flagged in the material as the layer most easily misread by retail.
- **Source:** nifty-options-pro `market_structure_gex.md` — "PCR (Put-Call Ratio) — The Trap Indicator"; also directly named in AXIS prior conversation as "exactly the trap pattern from your own research."

### P8. Max Pain Validity Regime-Dependence
- **Identifying conditions:** Max Pain "pinning" works only when Net GEX is positive (dealers buy dips, reinforcing the pin). It fails completely when GEX is negative (dealers are selling dips, actively fighting against Max Pain).
- **What it means:** Max Pain should be ignored entirely as a target when GEX is negative; use the VIX expected-move formula target instead.
- **Confused with:** Treating Max Pain as a universal pinning magnet — distinguished by checking GEX sign first.
- **Layer:** Layer A, conditional on regime.
- **Source:** nifty-options-pro `market_structure_gex.md` — "Max Pain — When It Works and When It Fails."

### P9. Wyckoff 3-Step Market-Turn Protocol (Exhaustion → Absorption → Initiative)
- **Identifying conditions:**
  1. **Exhaustion:** Aggressive market orders pushing the trend thin out — sudden drop in contracts hitting the ASK at new highs (or BID at new lows); volume footprint physically thins at the extreme of the candle.
  2. **Absorption:** Large operators step in with massive passive limit orders. Aggressive orders keep hitting the opposite side but price stalls completely — the passive wall is absorbing the aggression. Best identified by Wyckoff's own constraint: Order Flow signals should ONLY be trusted when occurring at a marked Volume Profile boundary (VAH/VAL/VPOC/LVN) — "Order Flow alone is subjective and practically useless unless deployed at a strict Volume Profile boundary."
  3. **Initiative:** A surge of aggressive orders on the new side creates a volume Imbalance (e.g., 300–400%+ more volume on one side), confirming the new trend launches.
- **Confused with:** Random/noisy two-sided footprint activity mid-range — distinguished by requiring the sequence to occur AT a Volume Profile boundary (LVN especially), not anywhere in open range.
- **Layer:** Layer C (order flow), gated by Layer A/structure context (Volume Profile boundary).
- **Source:** Wyckoff 2.0 — "The Anatomy of a Market Turn."

### P10. Delta Divergence Trap (Order Flow)
- **Identifying conditions:** A candlestick shows strongly positive cumulative Delta (e.g., +235, net aggressive buying) but the candle closes bearish (price down).
- **What it means:** The positive Delta is mathematically real but represents retail buyers being absorbed/trapped by a large passive institutional sell order (Iceberg-style). This is the order-flow signature confirming Absorption (see P9 step 2) and frequently coincides with a Wyckoff Spring or Upthrust shakeout.
- **Confused with:** Genuine bullish momentum (naive reading of positive Delta as automatically bullish) — distinguished by checking candle close direction against Delta sign; divergence between the two is the signal, not Delta alone.
- **Layer:** Layer C.
- **Source:** Wyckoff 2.0 — "The Delta Divergence Trap."

### P11. VPOC Migration (Continuation vs. Reversal Protocols)
- **Identifying conditions:** Volume Point of Control physically shifts to a new price level as Price+Time+Volume accumulate there.
  - **Continuation protocol:** Migration is followed immediately by a fast price impulse continuing in the trend direction (market accepted new value, urgently searching for next level).
  - **Reversal protocol:** Migration is followed by the price stalling and consuming excessive time sideways at the new VPOC instead of continuing — a warning sign of Change of Character (ChoCh) and impending reversal/distribution.
- **Confused with:** Treating any VPOC shift as automatically bullish/continuation — distinguished by whether price moves away quickly (continuation) or lingers (reversal warning).
- **Layer:** Layer C / structure.
- **Source:** Wyckoff 2.0 — "VPOC Migration Mechanics."

### P12. Shortening of the Thrust (SOT) — Momentum Exhaustion
- **Identifying conditions:** A minimum of three consecutive impulse waves, each new structural high/low traveling a noticeably shorter distance than the prior one.
  - SOT + high volume = effort-vs-result divergence (institutional money actively blocking the path).
  - SOT + low volume = pure exhaustion (trend participants withdrawing, no opposing force needed).
- **Confused with:** A simple slowdown in a healthy trend — distinguished by requiring at least 3 consecutive shrinking impulses, and by checking accompanying volume to classify which sub-type it is.
- **Layer:** Layer C / structure.
- **Source:** Wyckoff 2.0 — "Structural Failures & Momentum Anomalies."

### P13. Structural Failure of Strength
- **Identifying conditions:** Price moves away from an extreme test (e.g., a potential Spring) but reverses completely before even reaching the opposite end of the range.
- **What it means:** Proves aggressive buyers (or sellers) are front-running the market, actively blocking the move before it can fully develop — stronger conviction signal than a full round-trip move.
- **Confused with:** A failed breakout that simply ran out of steam randomly — distinguished by the speed/immediacy of the reversal relative to the range size.
- **Layer:** Layer C / structure.
- **Source:** Wyckoff 2.0 — "Structural Failures & Momentum Anomalies."

### P14. Sloping Trading Ranges (Accumulation/Distribution Asymmetry)
- **Identifying conditions:** Range does not build horizontally; it slopes. Upward-sloping = accumulation with extreme underlying buyer strength (buyers won't let price reach deep oversold). Downward-sloping = distribution with total seller control (persistent lower highs/lower lows, rapid markdown velocity).
- **Confused with:** A simple uptrend/downtrend with no range characteristics — distinguished by the lateral "cause-building" component still being present, just tilted rather than flat.
- **Layer:** Layer C / structure.
- **Source:** Wyckoff 2.0.

### P15. IV Crush (Post-Event Volatility Collapse)
- **Identifying conditions:** Ahead of a scheduled event (RBI policy, Budget, election, earnings), IV rises 2–4 VIX points as the event approaches. Immediately after the event/announcement, IV collapses sharply regardless of which direction price actually moved.
- **What it means:** Buying options right before an event is expensive and frequently unprofitable even with a correct directional call, because Vega loss from the IV collapse can exceed Delta gain from being directionally right.
- **Confused with:** A losing trade being purely a "wrong direction" call — distinguished by checking whether Vega loss (IV crush) outweighed Delta gain even when direction was correct.
- **Layer:** N/A (pricing/volatility mechanics, feeds Option Selector / event calendar, not a directional signal).
- **Source:** Nifty Options Trading Guide (Karthik Subramanian); nifty-options-pro `greeks_and_pricing.md`; *Trading Option Greeks* (Passarelli).

### P16. "Would I Do It Now?" Decision Trap
- **Identifying conditions:** A trader is holding a losing position (especially short premium) and is "hoping" it recovers rather than following a predefined plan (the "HAPI" — Hope and Pray Index — moment).
- **What it means:** The instant you catch yourself hoping instead of executing your plan, your risk management has already been violated; this is the signal to exit immediately, regardless of P&L magnitude.
- **Confused with:** Legitimate patience/holding through normal volatility per a stop-loss plan — distinguished by asking explicitly: "If I had no position, would I enter this exact position right now?" If no → close.
- **Layer:** N/A (risk-management psychology rule, not a market pattern).
- **Source:** *Trading Option Greeks* (Passarelli); nifty-options-pro `risk_and_adjustments.md`; Natenberg (implicitly, via "Would I Do It Now?" rule for short sellers).

### P17. Volatility Skew / Smile (Structural Mispricing Pattern)
- **Identifying conditions:** Downside (OTM) Puts trade at higher Implied Volatility than equidistant OTM Calls (Vertical Skew), due to institutional demand for downside portfolio protection. Term Structure (Horizontal Skew): front-month IV can be lower (calm market) or higher (pending event/panic) than back months.
- **What it means:** Out-of-the-money calls are inherently slightly cheaper than equidistant OTM puts purely due to the lognormal distribution of prices (bounded at zero, unbounded upside) — not necessarily a tradeable signal by itself, but a structural fact that must inform spread/condor construction (e.g., Iron Butterfly vs. standard Butterfly choice) and "richness" assessment of strikes being sold.
- **Confused with:** A directional signal — it is a structural pricing fact, not a forecast.
- **Layer:** N/A (pricing structure; feeds Option Selector).
- **Source:** *Trading Option Greeks* (Passarelli); Natenberg.

### P18. Adaptive Markets / Coexistence of Randomness and Determinism
- **Identifying conditions:** No identifying data condition — this is a meta-principle: markets exhibit both rational/deterministic behavior (Cause and Effect law: a sustained trend cannot occur without a building "cause" range) and irrational/random behavior simultaneously, depending on participant composition and regime.
- **What it means:** Robotic, identical chart-pattern labeling provides zero edge because no two accumulation/distribution structures look the same; the operationally useful invariant is the Cause-and-Effect law itself (range-build precedes trend), not surface pattern-matching.
- **Confused with:** Pure randomness (efficient market hypothesis) or pure determinism (rigid pattern trading) — it's explicitly framed as both coexisting.
- **Layer:** Meta/structure.
- **Source:** Wyckoff 2.0 — "Foundational Architectural Lessons," citing Adaptive Markets Hypothesis (AMH).

### P19. Order Flow Ambiguity / Multitude of Order Intentions
- **Identifying conditions:** A single large print on the BID or ASK column cannot, by itself, reveal trader intent — software can only classify aggressive vs. passive, not motive. The same aggressive print could be a new directional position opening, a stop-loss being triggered, a hedge being placed, or a market maker's automated inventory adjustment.
- **What it means:** Raw Order Flow data is inherently ambiguous and must never be read in isolation; this is why Wyckoff 2.0 insists Order Flow only be trusted at a Volume Profile structural boundary (see P9).
- **Confused with:** Treating any single large print as conclusive.
- **Layer:** Layer C caveat.
- **Source:** Wyckoff 2.0 — "The Multitude of Order Intentions."

### P20. Speculator's Fallacy (Direction-Only Thinking in Options)
- **Identifying conditions:** A trader correctly predicts the eventual direction and magnitude of a move but the option still expires worthless because the move arrived later than the option's expiry, or arrived too slowly relative to Theta decay.
- **What it means:** Unlike outright underlying traders (who only need to be right about direction), options traders must be right about direction, magnitude, AND speed/timing simultaneously — predicting all three is much harder, which is why uninformed option buyers consistently lose money even with correct directional calls.
- **Confused with:** A simple "bad luck" loss — distinguished by checking whether the eventual move (after expiry) actually validated the original directional thesis, just too late.
- **Layer:** N/A (options-specific structural risk, not a market pattern).
- **Source:** Natenberg, *Option Volatility & Pricing*.

### P21. Casino-Edge / Theoretical-Value Mindset
- **Identifying conditions:** No market data condition — a philosophical/structural pattern: professional option trading is framed as functionally identical to running a casino game. A roulette bet has a known theoretical payout (e.g., ~95¢ per $1 wagered); the house's edge is the gap between fair odds and offered odds.
- **What it means:** Professional profitability comes from systematically identifying where market-quoted option prices diverge from theoretical (model) value, then selling overvalued / buying undervalued options and capturing that statistical edge repeatedly — not from being "right" about direction on any single trade.
- **Confused with:** Treating options trading as direction-prediction — explicitly contrasted against this.
- **Layer:** N/A (core philosophy).
- **Source:** Natenberg, *Option Volatility & Pricing*.

### P22. Conservative Investor Mis-definition
- **Identifying conditions:** N/A — a definitional/behavioral correction rather than a market data pattern.
- **What it means:** Thomsett argues "conservative" is misdefined by most investors as "avoid all new strategies." True conservative investing means avoiding unexpected surprises/unacceptable losses while still using options as risk-management tools (covered calls, protective puts, collars) to preserve spending power, avoid excessive concentration/liquidity risk, and protect existing profits without forced liquidation of desirable stock.
- **Layer:** N/A.
- **Source:** *Options Trading for the Institutional Investor* (Thomsett).


---

# SECTION 2 — FORMULA REFERENCE

### F1. Delta (Δ)
- **Inputs/Calculation:** ΔOption Price / ΔSpot Price (first derivative of option price w.r.t. underlying price, ∂V/∂S in Black-Scholes terms).
- **Tells you alone:** ₹ change in option premium per 1-point move in underlying; rough statistical proxy for probability of expiring ITM; equivalent share/futures position size.
- **Cannot tell alone / must pair with:** Does NOT predict direction of the underlying — it's a property of the instrument, not a forecast. Must pair with Gamma to know how Delta will evolve if price keeps moving, and with position size to compute true equivalent exposure (`Equivalent_Exposure = Delta × Lots × Lot_Size(25)`).
- **Typical ranges:** Deep ITM Call ≈0.90–1.00; ATM Call ≈0.50; Far OTM Call ≈0.05–0.10; ATM Put ≈−0.50; Deep ITM Put ≈−0.90 to −1.00. ATM deltas gravitate toward 0.50 as time passes. Directional buying sweet spot per AXIS prior convo: 0.35–0.55.
- **Source:** Nifty Options Trading Guide; nifty-options-pro `greeks_and_pricing.md`; *Trading Option Greeks*; Natenberg.

### F2. Gamma (Γ)
- **Inputs/Calculation:** ΔDelta / ΔSpot (second derivative of option price w.r.t. spot, ∂²V/∂S²).
- **Tells you alone:** Rate of acceleration of Delta change per 1-point move; how fast your directional exposure will grow.
- **Cannot tell alone / must pair with:** Must be combined with Delta to project post-move exposure: `New_Delta ≈ Starting_Delta + (Gamma × Expected_Move)`. Also combines with OI to drive cascade risk (`Cascade_intensity = OI × Gamma²`).
- **Typical ranges:** Highest for ATM options; decreases for deep ITM/OTM. Spikes 3–5x on expiry day vs. 14 DTE. Long options = positive Gamma (always positive for both calls and puts per the Black-Scholes Greeks-101 source); short options = negative Gamma exposure on the position level.
- **Source:** All Greeks-focused sources above; nifty-options-pro `market_structure_gex.md` (cascade formula).

### F3. Theta (Θ)
- **Inputs/Calculation:** ΔOption Price / ΔTime — value lost per day holding constant all else (−∂V/∂t).
- **Tells you alone:** Daily premium decay in ₹; cost of holding (buyers) or income (sellers).
- **Cannot tell alone / must pair with:** Must be compared against expected gross profit from the move (`Total_Theta_Cost = Theta_per_day × Expected_Holding_Days`; if this exceeds expected gross profit, trade is not viable) and against Gamma (the two are always in opposition: long Gamma = paying Theta, short Gamma = collecting Theta but exposed to explosive moves).
- **Typical ranges (ATM Nifty, by DTE):**
  | DTE | Daily Theta | Decay % of Premium |
  |---|---|---|
  | 30 days | ₹5–8 | 1–2% |
  | 14 days | ₹10–15 | 3–5% |
  | 7 days | ₹15–25 | 6–10% |
  | 3 days | ₹30–50 | 12–20% |
  | 1 day (expiry eve) | ₹50–100 | 25–50% |
  | Expiry day | All extrinsic | 100% |
  Decay is non-linear, accelerating sharply in the final 7–10 days. Extreme reading: >15% daily decay of remaining premium (risk_and_adjustments.md warning threshold).
- **Source:** All sources above (consistent across Karthik's guide, SKILL.md, Passarelli, Natenberg).

### F4. Vega (ν)
- **Inputs/Calculation:** ΔOption Price per 1% change in Implied Volatility (∂V/∂σ).
- **Tells you alone:** Sensitivity of premium to IV changes; ATM options have the highest Vega.
- **Cannot tell alone / must pair with:** Must combine with expected IV change (e.g., pre/post-event IV crush) to estimate true P&L impact: `Expected_Vega_PnL = Vega × Expected_IV_Change_%`, then added to Theta cost for breakeven math. Always positive for vanilla long options (per Greeks-101 source).
- **Typical ranges:** Decreases as DTE shrinks (less time premium to be affected). BankNifty IV typically 1.3–1.6× Nifty 50 IV — more premium for sellers but more Vega risk.
- **Source:** Nifty Options Trading Guide; nifty-options-pro `greeks_and_pricing.md`; Passarelli; Natenberg.

### F5. Rho (ρ)
- **Inputs/Calculation:** ΔOption Price per 1% change in risk-free interest rate (∂V/∂r).
- **Tells you alone:** Interest-rate sensitivity; higher rates increase Call value, decrease Put value.
- **Cannot tell alone / must pair with:** Largely negligible standalone for short-dated Nifty weekly/monthly options; becomes meaningful only for LEAPS or Jelly Roll arbitrage by market makers across expiry months.
- **Typical ranges:** Negligible for weekly options; significant only for long-dated instruments.
- **Source:** All Greeks sources.

### F6. Second-Order Greeks (Charm, Speed, Color, Zomma, Veta, Volga)
- **Inputs/Calculation:**
  - Charm: ∂²V/∂S∂t (rate of change of Delta w.r.t. time)
  - Speed: ∂³V/∂S³ (rate of change of Gamma w.r.t. underlying)
  - Color: ∂²V/∂S²∂t (rate of change of Gamma w.r.t. time)
  - Zomma: ∂³V/∂S²∂σ (rate of change of Gamma w.r.t. volatility)
  - Veta: ∂²V/∂σ∂t (rate of change of Vega w.r.t. time)
  - Volga: ∂²V/∂σ² (rate of change of Vega w.r.t. volatility; "Vega convexity")
- **Tells you alone:** Each measures how a first-order Greek itself will drift — used for maintaining hedges (Charm), large-move risk (Speed), Gamma-trading over time (Color), volatility risk within Gamma trading (Zomma), long-term vol trading (Veta), advanced vol-trading strategies (Volga).
- **Cannot tell alone / must pair with:** Mostly relevant only to professional/market-maker-level dynamic hedging; not needed for retail directional or simple spread strategies.
- **Source:** Options Pricing and Greeks Analysis (GitHub project) — "Greeks 101."

### F7. GEX (Gamma Exposure) — Master Regime Switch
- **Inputs/Calculation:** `Net_GEX = Σ[CE_OI(i) × Γ(i) × S × lot × 100] − Σ[PE_OI(i) × Γ(i) × S × lot × 100]` across all strikes, where CE_OI/PE_OI = call/put open interest at strike i, Γ(i) = Gamma at strike i, S = spot, lot = 25.
- **Tells you alone:** Whether dealers are net long Gamma (positive GEX → buy dips/sell rallies → pinning, stabilizing) or net short Gamma (negative GEX → sell dips/buy rallies → amplifying, trending/cascading).
- **Cannot tell alone / must pair with:** Magnitude of expected move requires VIX formula (F9). Must be checked BEFORE trusting PCR (F11) or Max Pain (F12) — both flip meaning depending on GEX sign. This is the #1-ranked signal in the strict hierarchy (GEX overrides everything).
- **Typical ranges / extreme:** Real example: −3.94M Cr = strongly negative (cascade risk). Gamma Flip Level = price where Net GEX crosses zero (real example: ≈24,050).
- **Source:** nifty-options-pro `market_structure_gex.md`; AXIS prior conversation Layer A.

### F8. Gamma Flip Level
- **Inputs/Calculation:** Step 1: Call_GEX = Σ[CE_OI(i) × Γ(i)] for strikes > spot. Step 2: Put_GEX = Σ[PE_OI(i) × Γ(i)] for strikes < spot. Step 3: find price where cumulative Call_GEX = cumulative Put_GEX. (Shortcut: read directly off StockMojo Gamma Exposure chart where the Net GEX line crosses zero.)
- **Tells you alone:** The exact price where dealer hedging behavior flips from stabilizing to destabilizing.
- **Cannot tell alone / must pair with:** Needs to be combined with current spot location to know which side of the flip you're on, and with VIX/GEX Fibonacci targets (F10) for downstream price targets.
- **Typical ranges:** N/A — instrument/session-specific. Real example: 24,050 (June 23 2026); decline above this level was slow, below it was violent/self-reinforcing.
- **Source:** nifty-options-pro `market_structure_gex.md`.

### F9. VIX Expected Move Formulas
- **Inputs/Calculation:**
  - Daily move (1 SD, 68% confidence): `Daily_Move = Spot × (VIX/100) ÷ √252`
  - Weekly move: `Weekly_Move = Spot × (VIX/100) ÷ √52`
  - Down target (when GEX confirms down): `Down_Target = Spot − (Spot × VIX% ÷ √252)`
  - Up target: `Up_Target = Spot + (Spot × VIX% ÷ √252)`
  - 2SD (extreme, 95% confidence): `Daily_2SD = Daily_1SD × 1.96`
- **Tells you alone:** Expected magnitude of move for the day/week at given confidence level — the "how far" complement to GEX's "which direction."
- **Cannot tell alone / must pair with:** Direction must come from GEX (F7) — VIX formula alone is non-directional magnitude only. Best combined with GEX Fibonacci targets (F10) for a combined target zone.
- **Typical ranges:** Real example: Spot 24,100, VIX 12.89 → Daily move = 195.7 pts; Weekly move = 430.9 pts; Down_Target = 24,100 − 196 = 23,904 (actual low was 23,865, error 39 pts / 0.16%).
- **Source:** nifty-options-pro `market_structure_gex.md`; SKILL.md "Down Target Formula" (identical formula, restated in the 5-signal checklist).

### F10. GEX Fibonacci Extension Targets
- **Inputs/Calculation:** When GEX is negative, width = Flip_Level − End_of_Red_GEX_Zone. First target = Flip_Level − (Width × 0.382). Second target = Flip_Level − (Width × 0.618). Combined zone = range between VIX_Target (F9) and GEX_Target (this formula).
- **Tells you alone:** A secondary structural price target derived purely from the GEX profile shape.
- **Cannot tell alone / must pair with:** Designed explicitly to be combined with the VIX target (F9) — the material treats the overlap zone of both as the higher-confidence target. Real example: VIX target 23,904, GEX Fib target 23,895, actual low 23,865 — combined zone (23,895–23,904) was within 40 pts of actual.
- **Source:** nifty-options-pro `market_structure_gex.md`.

### F11. PCR (Put-Call Ratio)
- **Inputs/Calculation:** `PCR = Total Put OI ÷ Total Call OI`.
- **Tells you alone:** Standard reading (valid ONLY in positive GEX): rising PCR = more put buying/call selling = bearish/protective sentiment; falling PCR = bullish sentiment.
- **Cannot tell alone / must pair with:** MUST be paired with GEX sign — explicitly flagged by the material as misleading on its own. In negative GEX, rising PCR is a BEARISH/cascade-fuel signal, the opposite of the standard reading (see Pattern P7).
- **Typical ranges:** Real trap example: 1.18 rising to 1.21 in a negative-GEX environment with 4.71 Cr put OI = forced-selling-fuel signal, not floor.
- **Source:** nifty-options-pro `market_structure_gex.md`; AXIS prior conversation (explicitly named as "exact trap pattern from your own research").

### F12. Max Pain
- **Inputs/Calculation:** The strike at which total option premium losses are maximized for option buyers collectively (i.e., where the most option value gets wiped out at expiry) — the theoretical pinning target.
- **Tells you alone:** A candidate price-pinning level.
- **Cannot tell alone / must pair with:** MUST be paired with GEX sign — explicitly flagged as misleading on its own. Works only in positive GEX (dealers buy dips, reinforce pinning). Fails completely in negative GEX (dealers actively fight the pin by selling dips); should be ignored entirely in negative-GEX sessions in favor of the VIX target (F9).
- **Source:** nifty-options-pro `market_structure_gex.md` ("Max Pain — When It Works and When It Fails").

### F13. OI Overnight Build %
- **Inputs/Calculation:** `OI_change% = (today_ATM_OI − yesterday_OI) / yesterday_OI × 100`.
- **Tells you alone:** Magnitude of new positioning built overnight at the ATM strike.
- **Cannot tell alone / must pair with:** Threshold rule: if >50% build overnight → flagged as a high-volatility-day risk → do NOT sell naked premium that session. Used as one of the 5 inputs in the Expiry Day Detection System (F16).
- **Typical ranges:** >50% = high-volatility-day threshold (explicit rule).
- **Source:** nifty-options-pro `market_structure_gex.md`; SKILL.md 5-signal checklist.

### F14. OI Wall Interpretation (Support/Resistance)
- **Inputs/Calculation:** High Call OI at a strike = candidate resistance (call writers will sell futures if price approaches). High Put OI at a strike = candidate support (put writers will buy futures if price approaches).
- **Tells you alone:** A candidate S/R level based purely on positioning size.
- **Cannot tell alone / must pair with:** MUST be paired with GEX sign — in negative GEX, put OI becomes forced-selling fuel rather than support (see Cascade Formula F7/P6).
- **Source:** nifty-options-pro `market_structure_gex.md`.

### F15. Delta Hedge Cascade Formula
- **Inputs/Calculation:**
  - Initial hedge (ATM put writer): `Initial_Hedge = OI_lots × |Delta_initial| × lot_size`
  - After an N-point drop: `New_Delta = -0.50 − (Gamma × N)`; `Extra_selling = OI_lots × ΔDelta × lot_size`.
  - Worked numeric example: 72,000 lots OI, initial Delta −0.50 → Initial_Hedge = 72,000 × 0.50 × 25 = 900,000 units. After 50-pt drop, Delta → −0.60 (using Gamma 0.002) → Extra selling = 72,000 × 0.10 × 25 = 180,000 more units. After 100-pt drop, Delta → −0.70 → Total extra selling = 72,000 × 0.20 × 25 = 360,000 units.
- **Tells you alone:** Magnitude of forced dealer hedge-selling triggered by a given price move, given OI and Gamma.
- **Cannot tell alone / must pair with:** Requires accurate Gamma and OI inputs at the relevant strikes; combines directly with GEX sign (negative GEX = this cascade is destabilizing, not stabilizing).
- **Source:** nifty-options-pro `market_structure_gex.md`.

### F16. Expiry Day 9:15 AM Detection System (5-Signal Score)
- **Inputs/Calculation (point-scoring system):**
  ```
  [ ] GEX < 0 (negative)                  → +3 points
  [ ] VIX at or near Weak Low              → +2 points
  [ ] Overnight OI build > 50%             → +2 points
  [ ] PCR rising + GEX negative (TRAP)     → +1 point
  [ ] VIX CHoCH/BOS upward                 → +1 point
  ```
  Max score = 9.
- **Tells you alone:** A composite cascade-risk score for expiry-day trading specifically.
- **Cannot tell alone / must pair with:** Action thresholds are built in: SCORE ≥5 → BUY OTM PUTS (use Down_Target Formula F9 for level); SCORE 2–4 → reduce size, no directional bias; SCORE ≤1 → sell premium/range trade.
- **Source:** nifty-options-pro SKILL.md.

### F17. Black-Scholes Option Pricing Model
- **Inputs/Calculation:**
  - PDE: ∂V/∂t + ½σ²S²(∂²V/∂S²) + rS(∂V/∂S) − rV = 0
  - European Call: `C(S,t) = S·e^(−q(T−t))·N(d1) − K·e^(−r(T−t))·N(d2)`
  - European Put: `P(S,t) = K·e^(−r(T−t))·N(−d2) − S·e^(−q(T−t))·N(−d1)`
  - `d1 = [ln(S/K) + (r − q + σ²/2)(T−t)] / [σ√(T−t)]`
  - `d2 = d1 − σ√(T−t)`
  - Where: S = spot, K = strike, T−t = time to expiry, σ = volatility, r = risk-free rate, q = dividend yield, N(x) = standard normal CDF.
- **Tells you alone:** Theoretical "fair" option price given 6 inputs (stock price, strike, time, interest rate, dividends, volatility).
- **Cannot tell alone / must pair with:** Market price comparison is needed to find mispricing/edge (theoretical value vs. market price gap = the tradeable edge, per Natenberg's casino-edge framework P21). Real-world frictions (transaction costs, discrete vs. continuous trading, bid-ask spread) are assumed away by the model and must be added back manually.
- **Source:** Options Pricing and Greeks Analysis (GitHub project); Natenberg.

### F18. Monte Carlo Option Pricing
- **Inputs/Calculation:**
  - Risk-neutral valuation: `V0 = e^(−rT) · E_Q[V_T]`
  - GBM price process: `dS_t = (r − q)S_t·dt + σS_t·dW_t`
  - Discretized: `S_(t+Δt) = S_t · exp[(r − q − σ²/2)Δt + σ√Δt·Z]`, Z ~ N(0,1)
  - Estimator: `V0 ≈ e^(−rT) · (1/N) Σ V_T(i)`
  - Standard error: `SE = σ_MC / √N`
- **Tells you alone:** A simulation-based alternative price estimate (default 10,000 paths in the reference project) that can be compared against Black-Scholes for a "Difference %" sanity check.
- **Cannot tell alone / must pair with:** Larger N reduces standard error but costs computation time; used as a cross-check against Black-Scholes rather than standalone, especially useful for American-style or path-dependent features that Black-Scholes can't natively price.
- **Source:** Options Pricing and Greeks Analysis (GitHub project).

### F19. Daily/Weekly Expected Volatility (Square-Root-of-Time Rule)
- **Inputs/Calculation:**
  - Daily: `Daily_Volatility% = Annual_Volatility / 16` (since √256 ≈16 trading days/yr convention) — `1-Day_Price_Change = (Annual_Volatility/16) × Underlying_Price`
  - Weekly: `Weekly_Volatility% = Annual_Volatility / 7.2` (√52≈7.2) — `1-Week_Price_Change = (Annual_Volatility/7.2) × Underlying_Price`
  - Standard deviation probability bands: ±1 SD ≈68.3%, ±2 SD ≈95.4%, ±3 SD ≈99.7%.
- **Worked example:** Stock at 45, annual volatility 28% → daily volatility 1.75% → expected daily move = 0.79 pts (68% confidence).
- **Tells you alone:** Converts an annualized volatility figure into an actionable daily/weekly expected price range.
- **Cannot tell alone / must pair with:** This is the general form of the Nifty-specific VIX formula (F9) — same square-root-of-time logic, generalized to any annual volatility figure including Eurodollar/interest-rate-indexed contracts (separate transformation given: `Daily_Price_Change = (Annual_Volatility/16) × (100 − Listed_Price)` for contracts capped at 100).
- **Source:** Natenberg, *Option Volatility & Pricing*.

### F20. Forward Price (Cost of Carry)
- **Inputs/Calculation:**
  - Futures: `Forward_Price = Current_Price` (no carry cost, no dividend, since futures require no upfront cash outlay).
  - Stock: `Forward_Price = Current_Price + Carrying_Costs − Dividends`
  - `Carrying_Cost = Interest_Rate × (Days_to_Expiration/365) × Asset_Value`
- **Worked example:** Asian Paints spot ₹3,100, 30 days, 7% rate, ₹0 dividend → Carrying Cost ≈₹17.83 → Forward Price ≈₹3,117.83 (this, not spot, is the price a theoretical pricing model should center its lognormal distribution on).
- **Tells you alone:** The break-even future price a model should treat as the distribution mean.
- **Cannot tell alone / must pair with:** Used as an input into the Black-Scholes/lognormal pricing assumptions (assumption #4: the mean of the lognormal distribution sits exactly at the forward price, not the current spot).
- **Source:** Natenberg.

### F21. Intrinsic Value / Time Value Decomposition
- **Inputs/Calculation:**
  - `Option_Premium = Intrinsic_Value + Time_Value`
  - Call: `Intrinsic_Value = max(0, Underlying_Price − Strike_Price)`
  - Put: `Intrinsic_Value = max(0, Strike_Price − Underlying_Price)`
  - `Time_Value = Option_Premium − Intrinsic_Value`
- **Worked example:** Asian Paints at ₹3,100, 3,000-strike call premium ₹180 → Intrinsic = ₹100, Time Value = ₹80.
- **Tells you alone:** Splits the premium into "real, already-earned" value vs. "probability premium for future movement."
- **Cannot tell alone / must pair with:** Time Value portion is what Theta/Vega act on; necessary precursor to any Greeks-based analysis.
- **Source:** Natenberg; Karthik's Nifty guide; NSE Bank Nifty booklet glossary; Passarelli.

### F22. Delta Position / Delta-Neutral Hedge Sizing
- **Inputs/Calculation:**
  - `Total_Delta_Position = (#Options × Option_Delta) + (#Underlying × Underlying_Delta)` (underlying contract Delta is fixed at 100).
  - Delta-neutral condition: `Total_Delta_Position = 0`.
  - Required futures hedge: `Futures_needed = Current_Net_Delta × Total_Lots × Lot_Size`.
- **Worked example (Natenberg):** Buy 100 calls, Delta 57 → position delta +5,700 → sell 57 futures contracts (each = −100 delta) to flatten to 0. After price rise, Delta → 62 → position +6,200 vs. −5,700 hedge = +500 net → sell 5 more futures. After price fall, Delta → 46 → position +4,600 vs. −6,200 hedge = −1,600 net → buy 16 futures.
- **Tells you alone:** Exact hedge ratio needed to neutralize directional risk at a point in time.
- **Cannot tell alone / must pair with:** Must be recalculated continuously as Delta drifts with price (Gamma-driven) — this is "Gamma scalping" in practice; the profit/loss race is between Theta decay (cost) and the cash flow generated by these repeated buy-low/sell-high hedge adjustments.
- **Source:** Natenberg; nifty-options-pro `risk_and_adjustments.md` (Technique 2 — Delta Hedge via Futures).

### F23. Nifty Position Sizing — Equivalent Exposure
- **Inputs/Calculation:** `Equivalent_Nifty_Exposure = Delta × Lots × 25` (lot size).
- **Worked example:** 0.40 Delta × 2 lots × 25 = 20 Nifty-unit equivalent exposure; compare against comfortable futures-lot-equivalent (1 lot = 25 units) tolerance.
- **Tells you alone:** True underlying-equivalent size of an options position, correcting for the fact that options aren't 1:1 leveraged stock.
- **Cannot tell alone / must pair with:** Step 1 of the 4-step Position Sizing Framework (F24); must be followed by Gamma scenario planning.
- **Source:** nifty-options-pro SKILL.md / `greeks_and_pricing.md`.

### F24. 4-Step Position Sizing Framework
- **Inputs/Calculation:**
  - Step 1 — Delta exposure check: `Equivalent_Exposure = Delta × Lots × 25` (F23).
  - Step 2 — Gamma scenario: `New_Delta ≈ Starting_Delta + (Gamma × Expected_Move)`.
  - Step 3 — Vega cost/benefit: `Expected_Vega_PnL = Vega × Expected_IV_Change_%` (include post-event IV crush).
  - Step 4 — Theta viability: `Total_Theta_Cost = Theta_per_day × Expected_Holding_Days`; reject trade if this exceeds expected gross profit.
- **Tells you alone:** A complete pre-trade Greek-risk sizing checklist.
- **Cannot tell alone / must pair with:** Each step feeds the next sequentially; Step 4 is a hard go/no-go gate regardless of directional conviction.
- **Source:** nifty-options-pro SKILL.md.

### F25. Kelly Criterion (Trade Sizing)
- **Inputs/Calculation:** `f = p/a − q/b`, where f = fraction of bankroll to bet, p = probability of winning, q = probability of losing (1−p), b = fraction of wager gained on a win, a = fraction of wager lost on a loss.
- **Worked example:** Game doubles money on win (b=1), loses full wager on loss (a=1), p=2/3, q=1/3 → f = (2/3)/1 − (1/3)/1 = 1/3 → bet one-third of bankroll.
- **Tells you alone:** The mathematically optimal fraction of capital to risk per trade to maximize long-run compounding growth.
- **Cannot tell alone / must pair with:** Requires accurate, honest estimates of p, a, and b — garbage-in-garbage-out risk is high; AXIS material recommends starting with HALF-Kelly for safety margin against estimation error (per AXIS prior conversation, Component 6).
- **Source:** QUANT BIBLE; AXIS prior conversation (Component 6 — Risk/Capital/Money Management).

### F26. Expected Value (EV) — General
- **Inputs/Calculation:** `E[X] = Σ x·p(x)` (discrete) or `∫x·f(x)dx` (continuous); for trading: `E = (W × P_w) − (L × P_l)`, where W = avg win size, P_w = win probability, L = avg loss size, P_l = loss probability.
- **Tells you alone:** Whether a strategy has positive long-run mathematical expectancy.
- **Cannot tell alone / must pair with:** Must be applied AFTER subtracting realistic transaction costs (brokerage, STT, slippage) — a positive gross EV can become negative net EV once costs are included. In AXIS architecture, this is the Final Verifier agent's output gate: EV in rupees, post-transaction-costs; negative EV blocks the alert regardless of how good other signals look.
- **Source:** QUANT BIBLE; AXIS prior conversation (Component 4 — Agent Two).

### F27. Conditional Probability & Bayes' Theorem
- **Inputs/Calculation:** `P(A|B) = P(A∩B)/P(B)`; Bayes: `P(A|B) = P(B|A)P(A)/P(B)`; Law of Total Probability: `P(B) = P(B|A)P(A) + P(B|¬A)P(¬A)`.
- **Tells you alone:** How to update a prior belief given new evidence.
- **Cannot tell alone / must pair with:** Requires an accurate prior P(A) and likelihood P(B|A) — used conceptually in AXIS for updating Direction Scorer confidence as new layer data arrives.
- **Source:** QUANT BIBLE.

### F28. Expected Value / Variance / Covariance (Statistical Fundamentals)
- **Inputs/Calculation:**
  - `E[X] = Σx·p(x)`; linear in sums even under dependence: `E[X1+...+Xn] = E[X1]+...+E[Xn]`.
  - `Var(X) = E[X²] − E[X]²`; `Var(aX+b) = a²Var(X)`; `Var(X+Y) = Var(X)+Var(Y)` for independent X,Y.
  - `Cov(X,Y) = E[XY] − E[X]E[Y]`; `ρ(X,Y) = Cov(X,Y)/√(Var(X)Var(Y))`.
- **Tells you alone:** Central tendency, dispersion, and co-movement of random variables (e.g., signal scores, layer outputs).
- **Cannot tell alone / must pair with:** Foundation for backtesting/weighting layer scores in the AXIS Direction Scorer; correlation is essential for checking whether Layer A/B/C are giving genuinely independent information or redundant signal.
- **Source:** QUANT BIBLE.

### F29. Law of Large Numbers (LLN) & Central Limit Theorem (CLT)
- **Inputs/Calculation:** LLN: sample mean → true mean as n→∞. CLT: `√n·(X̄n − μ)/σ → N(0,1)`.
- **Tells you alone:** Why a small statistical edge (e.g., 51% win rate) becomes reliably profitable only over a large number of trades, not a small sample.
- **Cannot tell alone / must pair with:** Confidence intervals (F30) for quantifying how large a sample is "enough."
- **Source:** QUANT BIBLE.

### F30. Confidence Intervals / Z-Score (T-Test) for Regression Coefficients
- **Inputs/Calculation:** `z_j = β̂_j / (σ̂√v_j)`; CI = `β̂_j ± z^(1−α)·√v_j·σ̂`.
- **Tells you alone:** Whether an estimated coefficient (e.g., a backtested layer weight) is statistically distinguishable from zero/noise.
- **Cannot tell alone / must pair with:** Rule of thumb cited: |z| > 2 ≈ statistically significant at ~95% confidence. Directly applicable to AXIS's instruction to backtest Layer A/B/C weights rather than assume them.
- **Source:** QUANT BIBLE.

### F31. Linear Regression (OLS) Closed-Form Solution
- **Inputs/Calculation:** `β̂ = (XᵀX)⁻¹Xᵀy`; RSS minimized: `RSS(β) = Σ(yi − xiᵀβ)²`.
- **Tells you alone:** Best-fit linear relationship between predictors (e.g., layer scores) and an outcome (e.g., next-session return).
- **Cannot tell alone / must pair with:** Bias-variance tradeoff (F32) — simple linear models trade some accuracy for much greater stability versus complex models like KNN, explicitly recommended by QUANT BIBLE as the textbook-correct choice for noisy financial data over black-box ML.
- **Source:** QUANT BIBLE.

### F32. Bias-Variance Tradeoff / Ridge & Lasso Regularization
- **Inputs/Calculation:**
  - KNN prediction: `Ŷ(x) = (1/k)Σ y_i` for x_i in neighborhood — low bias, high variance, suffers from curse of dimensionality.
  - Ridge (L2): objective adds `+λΣβj²`; solution `β̂_ridge = (XᵀX + λI)⁻¹Xᵀy` — shrinks all coefficients proportionally, rarely to exactly zero.
  - Lasso (L1): objective adds `+λΣ|βj|` — truncates unimportant variables fully to zero (feature selection).
- **Tells you alone:** How model complexity trades off against stability/generalization.
- **Cannot tell alone / must pair with:** Direct textbook justification (per AXIS prior conversation) for keeping the Direction Scorer a simple, stable, slightly-biased weighted-rule system rather than a complex/unstable black-box model.
- **Source:** QUANT BIBLE.

### F33. Omitted Variable Bias (OVB)
- **Inputs/Calculation:** `OVB = β^s − β^l = π1·γ`, where β^s = short-regression coefficient (missing control), β^l = long-regression coefficient (with control), π1 = correlation of omitted variable with treatment, γ = effect of omitted variable on outcome.
- **Tells you alone:** Direction/rough magnitude of bias introduced by leaving out a relevant variable from a model.
- **Cannot tell alone / must pair with:** Directly relevant to AXIS's own self-criticism: Layer B (FII positioning) was assumed important without being tested against the same 5 real examples Layer A/C were validated on — risk of OVB-style distortion if Layer B is weighted on theory rather than backtested evidence.
- **Source:** QUANT BIBLE.

### F34. STT (Securities Transaction Tax) on ITM Expiry
- **Inputs/Calculation:** STT on options expiring ITM (without selling first) = 0.125% of intrinsic value (vs. 0.0625% on a normal sale).
- **Worked example:** 22,000 CE, Nifty closes 22,300 → intrinsic = 300×75=₹22,500 → STT = 0.125%×22,500=₹28 (for a 75-lot-size example, older lot size). Scaled example: ₹2,25,000 intrinsic on a larger position → STT = ₹281.
- **Tells you alone:** The tax cost specifically of letting an ITM option expire vs. selling it before close.
- **Cannot tell alone / must pair with:** Operational rule, not a market signal — always square off ITM options before 3:00 PM expiry day rather than letting them expire, to avoid the higher rate.
- **Source:** Karthik's Nifty Options Trading Guide; nifty-options-pro `risk_and_adjustments.md` / `strategies_and_setups.md`.

### F35. Nifty Transaction Cost Stack (Round Trip)
- **Inputs/Calculation:** Brokerage ₹20 (buy) + ₹20 (sell) = ₹40; STT 0.0625% on sell premium (e.g., ₹5,000 sell value → ₹3.12); Exchange charges ≈₹30–40/lot round trip; GST 18% on brokerage+exchange ≈₹12. Total ≈₹85–95/lot round trip.
- **Tells you alone:** True floor cost that must be cleared before a trade is profitable.
- **Cannot tell alone / must pair with:** Must be subtracted in the Expected Value formula (F26) — this is exactly the "estimated transaction costs" the AXIS Final Verifier agent is meant to apply.
- **Source:** "Nifty Lot Size and Margin Explained" article.

### F36. Nifty Lot Size / Premium / Margin Conversions
- **Inputs/Calculation:** Lot size = 25 units (since Apr 2023, reduced from 50). 1-pt move = ₹25/lot. Premium cost = Premium × 25 (e.g., ₹150 premium × 25 = ₹3,750/lot — note: source examples use both 75 and 25 lot-size multipliers inconsistently across older vs. newer articles; CURRENT/AUTHORITATIVE lot size per the dedicated lot-size article and SKILL.md is 25). Margin (approx 2026 SEBI): Futures (1 lot) ≈₹1,45,000 total; Option buying = premium only, no margin; Option selling (naked) ≈₹1,45,000 total; Credit spread (100-pt wide) ≈₹45,000 total.
- **Tells you alone:** Capital requirement and ₹-per-point conversion for position sizing.
- **Cannot tell alone / must pair with:** Feeds directly into Money/Capital Management component — max affordable premium given account size and risk % per trade.
- **⚠ Internal inconsistency flagged:** Several older articles in the source material (the original "TRADING ALL THE THING" guide and NSE Bank Nifty booklet) use a 75-unit lot size in worked examples; the dedicated 2026 lot-size article and the nifty-options-pro skill consistently use 25. Treat 25 as authoritative (most recent, most specific source) — see Coverage Check for detail.
- **Source:** "Nifty Lot Size and Margin Explained" article; nifty-options-pro SKILL.md Capital Sizing Table.

### F37. Capital Sizing Table (2% Max Risk Rule)
- **Inputs/Calculation:**
  | Capital | Lots | Max Risk (2%) | Monthly Target Range |
  |---|---|---|---|
  | ₹3,00,000 | 1–2 | ₹6,000 | ₹8,000–15,000 |
  | ₹5,00,000 | 2–4 | ₹10,000 | ₹15,000–25,000 |
  | ₹10,00,000 | 4–8 | ₹20,000 | ₹30,000–50,000 |
  | ₹25,00,000 | — | ₹50,000 | — |
- **Tells you alone:** Standard position-size/risk ceiling by account size.
- **Cannot tell alone / must pair with:** Combine with weekly loss limit rule (3% of capital → stop trading for the week) and Kelly/half-Kelly sizing for a complete risk framework.
- **Source:** nifty-options-pro SKILL.md / `risk_and_adjustments.md`; repeated near-identically across several NiftyTradingPro articles.

### F38. VWAP (Volume Weighted Average Price)
- **Inputs/Calculation:** `VWAP = Σ(contracts_traded × price) / Total_contracts_traded`.
- **Tells you alone:** The average price weighted by where most volume actually transacted — heavily used by institutional execution algorithms as an execution-quality benchmark.
- **Cannot tell alone / must pair with:** Acts as a dynamic support/resistance level because institutional algos buy below VWAP (perceived discount) and sell above it; should be read alongside Volume Profile (F39) and Order Flow, not standalone, and is explicitly ranked LAST (5th) in the Five Market Structure Signals hierarchy — entry timing only, never primary signal.
- **Source:** Wyckoff 2.0; nifty-options-pro SKILL.md (signal hierarchy item 5).

### F39. Value Area / Volume Profile Statistics
- **Inputs/Calculation:** Value Area (VA) = price range containing 68.2% of total volume traded (1 SD of a normal/Gaussian distribution applied horizontally to volume-by-price). VAH/VAL = upper/lower bounds of VA. 2 SD ≈95.4% of volume. VPOC = single price with highest traded volume (the distribution's "mode").
- **Tells you alone:** Objective, data-derived "fair value" zone vs. "unfair"/rejected price zones (LVN — Low Volume Node — vs. HVN — High Volume Node).
- **Cannot tell alone / must pair with:** Core working principle: if price breaks out of VA but is rejected, high probability of rotating to the OPPOSITE extreme of the VA. Order Flow signals (F40/P9) should only be trusted when occurring AT these VAH/VAL/VPOC/LVN boundaries.
- **Source:** Wyckoff 2.0 — "Volume Profile: The Objective Valuation."

### F40. Order Flow / Footprint Mechanics
- **Inputs/Calculation:**
  - `Spread = ASK − BID` (liquidity indicator).
  - Order crossing logic: Buy Market × Sell Limit = printed in ASK column; Sell Market × Buy Limit = printed in BID column.
  - Position-exit-to-column mapping: closing a Short via market exit or stop-loss → Buy Market/Buy Stop → prints in ASK; closing a Short via take-profit → Buy Limit → prints in BID. Closing a Long via market exit or stop-loss → Sell Market/Sell Stop → prints in BID; closing a Long via take-profit → Sell Limit → prints in ASK.
  - Delta = net difference between aggressive buying (hitting ASK) and aggressive selling (hitting BID) volume.
- **Tells you alone:** The micro-mechanical origin of every printed trade — whether it crossed on the bid or ask side, and (via the exit-mapping logic) a structural explanation for why stop-loss cascades (shorts covering into a rally, or longs dumping into a decline) mechanically accelerate moves.
- **Cannot tell alone / must pair with:** MUST be combined with Volume Profile boundaries (F39) per Wyckoff 2.0's own explicit warning — "Order Flow alone is subjective and practically useless unless deployed at a strict Volume Profile boundary." A single large print cannot reveal trader intent by itself (see Pattern P19).
- **Source:** Wyckoff 2.0 — "Order Flow: The Micro-Mechanics."

### F41. Dispersion Trading Payoff (Correlation Arbitrage)
- **Inputs/Calculation:** `P_T,Dispersion = Σ wi·([Si,T − Ki]⁺ + [Ki − Si,T]⁺) − ([SI,T − KI]⁺ + [KI − SI,T]⁺)`, i.e., long a weighted basket of single-stock straddles minus a short index straddle.
- **Tells you alone:** Payoff of betting that individual-stock volatility (dispersion) will exceed index-implied volatility.
- **Cannot tell alone / must pair with:** Relies on the structural fact that index IV usually trades richer than the volatility-weighted sum of its constituents; an institutional-only strategy given complexity/capital requirements, not part of core AXIS retail-scale design but logged for completeness.
- **Source:** Institutional algo-architecture material (QUANT BIBLE-adjacent commentary).

### F42. Put-Call Parity
- **Inputs/Calculation:** `Stock + Put + Interest − Dividend − Strike = Call` (equivalently stated elsewhere as `Call + Strike − Interest + Dividend = Put + Stock`).
- **Tells you alone:** The mathematically enforced equilibrium link between a call, a put, and the underlying at the same strike/expiry.
- **Cannot tell alone / must pair with:** Basis for constructing synthetic positions (Synthetic Long Stock = Long Call + Short Put; Synthetic Long Call = Long Stock + Long Put; Synthetic Long Put = Short Stock + Long Call) and for market-maker Conversion/Reversal arbitrage trades that capture small Rho/dividend mispricings.
- **Source:** *Trading Option Greeks* (Passarelli); Natenberg.

---

# SECTION 3 — WORKED EXAMPLES (STRUCTURED)

### E1. June 29 2026 — 23,950 CE OI Surge + LTP Collapse (NIFTY Live Trade)
- **Setup/Context:** Expiry-proximate session; specific strike being watched for institutional signal.
- **Exact data values:** CE_OI at 23,950 strike: +851% overnight build. LTP of that same CE: −46.80% on the same candle/session.
- **Outcome:** The strike became the harvest zone — the massive OI build was pure option writing (selling), not buying; premium collapsed as expected for short positions, not long.
- **Which signal predicted the outcome and how far in advance:** The OI-rising-while-LTP-falling signature (Pattern P3) gave a same-candle/same-session signal. Identified in real-time by checking both OI and premium together. No advance lead time — this is a Layer C (current-session) signal, not a multi-day early warning.
- **Classification:** TRIGGER phase of the bait-trigger-harvest trap (P2). The bait was whatever bullish price action attracted retail call-buyers; this data pair was the trigger revealing institutional writing against them.
- **Source:** AXIS prior conversation, trap-mechanism document (June 29 example).

### E2. June 30 2026 — 23,950 Equal-Highs Liquidity Sweep (NIFTY Live Trade)
- **Setup/Context:** Price approached a cluster of equal highs at the 23,950 zone, a well-marked technical level with obvious retail stop-loss clusters sitting above it.
- **Exact data values:** Price spiked 6.15 points past the marked equal-highs level, then reversed sharply.
- **Outcome:** Sharp reversal immediately after the 6.15-point overshoot — stops were cleared, institutional supply absorbed the liquidity, price reversed.
- **Which signal predicted the outcome:** The equal-highs pattern itself flags the stop cluster in advance; the 6.15-point overshoot (deliberately small, just enough to clear stops, not a breakout attempt) confirmed the sweep was institutional, not genuine. The magnitude of the overshoot vs. the subsequent reversal speed is the distinguishing signal (Pattern P4).
- **Classification:** BAIT (equal highs visible to all retail) → TRIGGER (sweep itself) → HARVEST (reversal after stops cleared).
- **Source:** AXIS prior conversation, trap-mechanism document (June 30 example).

### E3. June 19–23 2026 — VIX CHoCH 4-Day Lead (NIFTY VIX Early Warning)
- **Setup/Context:** A 4-day observation window where VIX structural analysis was applied independently of NIFTY price action.
- **Exact data values:** June 19 — VIX prints a Weak Low AND a CHoCH (Change of Character) on the 15-min chart while NIFTY price action showed nothing actionable. June 23 — VIX exploded from 12.89 to 14.05 (+9% intraday). NIFTY followed with a large down-move.
- **Outcome:** The June 23 explosion was predicted structurally 4 days in advance by the June 19 VIX CHoCH. Every put with Vega 1.0 gained ₹1.16 from vol expansion alone on top of Delta gain; puts gained 276%–425% on the session (directional gain × vol expansion multiplicative).
- **Which signal predicted the outcome and how far in advance:** VIX CHoCH on June 19 → 4 days in advance. Confirms VIX structure must be tracked as a standalone persistent multi-day flag (Pattern P5), not folded into a same-day scorer.
- **Classification:** VIX CHoCH is the TRIGGER; the NIFTY move is the HARVEST. The bait was any bullish price-action read on June 19–22 while VIX was already warning.
- **Source:** AXIS prior conversation, trap-mechanism document (June 19–23 example).

### E4. June 22–23 2026 — PCR/GEX Mismatch Trap (NIFTY Live Trade)
- **Setup/Context:** Multi-session observation where Layer A read bullish but Layer A was in a negative-GEX environment.
- **Exact data values:** PCR = 1.18, price sitting on Max Pain, GEX = positive 548K crore on June 22 (this was the bait — Layer A superficially looked bullish). GEX subsequently flipped to −3.94M Cr. PCR continuing to rise (1.18 → 1.21) while GEX was negative (trap signal — Pattern P7). 4.71 Cr put OI = 4.71 Cr delta-hedge obligations ready to fire. Gamma Flip Level ≈24,050.
- **Outcome:** Cascade. Decline above 24,050 was slow; decline below 24,050 was violent and self-reinforcing (dealer flip from stabilizing to pro-cyclical per Pattern P6). The PCR-rising-in-negative-GEX signal was bearish fuel, not bullish protection.
- **Which signal predicted the outcome:** GEX flip to negative + PCR rising in negative GEX = the trigger (recognizable in real time by checking GEX sign before reading PCR). Max Pain and rising PCR alone gave a false bullish read — the exact retail trap described in Pattern P7.
- **Classification:** BAIT (bullish-looking PCR + Max Pain + superficially positive GEX on June 22) → TRIGGER (GEX flip + PCR rising in negative regime) → HARVEST (cascade post-flip).
- **Source:** AXIS prior conversation, trap-mechanism document (June 22–23 example). Also the primary real-data validation of F7 (GEX regime), F11 (PCR trap), F8 (Gamma Flip), F9 (VIX target), F15 (cascade formula).

### E5. June 16 2026 — PE Decay (NIFTY Live Trade)
- **Setup/Context:** Put premium decay session; exact data values less detailed in the source material than E1–E4 but included as one of the five documented trap examples.
- **Exact data values:** Not specified beyond "June 16 PE decay" in the source.
- **Outcome:** Put premium decayed as expected; the trap mechanism was operative.
- **Which signal predicted the outcome:** Per the source, this example fits the same bait-trigger-harvest pattern; specific data values for this date were not included in the portion of the trap-document shared in context — flagged as a coverage gap (see Coverage Check).
- **Classification:** Bait-trigger-harvest pattern (P2). Specific trigger signal type not recoverable from available text.
- **Source:** AXIS prior conversation, trap-mechanism document (June 16 example).

### E6. June 23 2026 Expiry-Day Cascade — OTM Put Trade (Worked Strategy Example)
- **Setup/Context:** Expiry day, detection system run at 9:15 AM.
- **Exact data values:** Nifty at 24,127 at open; GEX −3.94M Cr (negative); VIX 12.89 (Weak Low); Down_Target formula: 24,100 − (24,100 × 0.1289 ÷ √252) = 24,100 − 196 = 23,904. Gamma Flip Level ≈24,050. 23,850 PE purchased at ₹12–15.
- **Outcome:** 23,850 PE went from ₹12 to ₹30+ (a ~2x+ gain); actual NIFTY low = 23,865 (vs. formula target 23,904, error 39 pts). GEX Fib second target was 23,895; combined zone (23,895–23,904) was within 40 pts of actual.
- **Which signal predicted the outcome:** 5-signal detection score (F16) — GEX negative (+3 pts), VIX Weak Low (+2 pts), VIX CHoCH from June 19 still active (+1 pt), PCR rising in negative GEX (+1 pt) = score ≥5. Both the VIX formula target and the GEX Fibonacci target converged on the 23,895–23,904 zone, validating both formulas (F9, F10).
- **Classification:** Full bait-trigger-harvest pattern operating at scale; the OTM put buy was the trade structured around the trigger and targeting the harvest zone.
- **Source:** nifty-options-pro `strategies_and_setups.md` (Strategy 6 example); `market_structure_gex.md` (June 23 real example repeated in multiple subsections).

### E7. Natenberg Delta-Neutral Hedge — June 100 Call (Worked Hypothetical)
- **Setup/Context:** Classic textbook illustration of dynamic hedging capturing a mispriced option's theoretical edge over 10 weeks.
- **Exact data values:** Underlying June futures at 101.35; interest rate 8%; 10 weeks to expiry; forecasted future volatility 18.3%; Theoretical value of June 100 Call = 3.88; Market price = 3.25 (underpriced by 0.63); Delta = 57; Position: buy 100 calls (total delta +5,700); initial hedge: sell 57 futures (−5,700 delta) → net delta = 0.
- **Adjustments during trade:**
  - Week 1: Futures rise to 102.26 → Delta → 62 → net delta +500 → sell 5 more futures.
  - Week 2: Futures drop to 99.07 → Delta → 46 → net delta −1,600 → buy 16 futures.
  (Full 10-week adjustment table not reproduced here; pattern repeats.)
- **Outcome:** Cash flow from repeated buy-low/sell-high hedge adjustments (mechanically forced by Delta drift) outpaced the Theta decay of the options, locking in ~0.63 per-option profit across the full holding period regardless of final market direction.
- **Which signal predicted the outcome:** IV mispricing (market price < theoretical value) identified at entry. The key is that the identified 0.63 edge only realizes through continuous dynamic hedging, not from holding passively.
- **Classification:** NOT a bait-trigger-harvest pattern — this is a pure volatility-arbitrage/gamma-scalping execution example (professional market-maker approach, not retail NIFTY directional trade).
- **Source:** Natenberg, *Option Volatility & Pricing*.

### E8. Asian Paints — Option Premium Decomposition and Delta Hedge (Worked Hypothetical)
- **Setup/Context:** Illustration of F21 (intrinsic/time value split) and F22 (delta hedge sizing) applied to an Indian equity option.
- **Exact data values:** Asian Paints spot ₹3,100; strike 3,000 CE; option premium ₹180; intrinsic = ₹100; time value = ₹80; forward price calculation: 7% rate, 30 days, ₹0 dividend → carrying cost ≈₹17.83 → forward price ≈₹3,117.83. Delta of 3,000 CE = 65; buy 1,000 calls → total position delta +650 → need to sell 650 shares to hedge to zero.
- **Outcome:** Delta-neutral position established; subsequent adjustments (buy/sell underlying as delta drifts with price) generate the gamma-scalping cash flow vs. Theta cost race.
- **Which signal predicted the outcome:** No directional prediction — this is a demonstration of the mechanics, not a market call.
- **Classification:** NOT bait-trigger-harvest — pricing mechanics illustration.
- **Source:** Wyckoff 2.0 institutional commentary (applied to NIFTY/Indian equities context); Natenberg framework.

### E9. VWAP / Institutional Execution Mechanics (Illustrative)
- **Setup/Context:** Hypothetical: buy 1 million shares total over a trading day.
- **Exact data values:** Institutional algorithm buys when current price is below VWAP (perceived discount) and avoids when above; order is sliced into hundreds of small chunks via Iceberg Algorithm to mask footprint from HFT predators.
- **Outcome:** Continuous institutional buying below VWAP explains why VWAP often acts as a strong dynamic support level on intraday charts — it's mechanically reinforced by the execution logic of large orders.
- **Which signal predicted the outcome:** Not a predictive example — an explanatory one for why VWAP works as a support/resistance level.
- **Classification:** Not applicable.
- **Source:** Institutional algo-architecture material.

### E10. GEX Fibonacci + VIX Target Convergence (June 23 2026 — Extended Validation)
- **Setup/Context:** Testing whether VIX formula target and GEX Fibonacci extension target converge to the same zone (validation of F9 + F10 combined).
- **Exact data values:** Spot ~24,100; VIX 12.89; VIX target = 24,100 − (24,100 × 0.1289 ÷ 15.875) = 23,904; Gamma Flip Level ≈24,050; GEX red-zone end not given numerically in source but Fib target derived as ≈23,895; combined zone 23,895–23,904; actual NIFTY low = 23,865.
- **Outcome:** Both formulas independently converged on a zone that was within 40 pts of actual low (error < 0.17%). Combined zone is higher-confidence than either formula alone.
- **Which signal predicted the outcome:** GEX negative + VIX Weak Low (identified at session open) → ran both formulas → confirmed convergence → acted on OTM put (Strategy 6, E6 above).
- **Classification:** TRIGGER (GEX + VIX data) → provides quantified HARVEST zone.
- **Source:** nifty-options-pro `market_structure_gex.md`.

### E11. Two Sigma NYC Housing Prices (Quant Research Data-Engineering Example)
- **Setup/Context:** Kaggle-style ML prediction model for NYC housing prices; illustrating feature engineering rules for irregular data types.
- **Exact data values:** Data types encountered: categorical geographic data; discrete room counts; heavily skewed square-footage/price data.
- **Data transformations applied:** Categorical geographic data → one-hot encoding; discrete variables (bedrooms/bathrooms) → kept as-is; heavily skewed variables → log-normal transformation to compress outliers and produce normal distribution.
- **Outcome:** Each transformation type is chosen to match the statistical distribution of the input variable to what a linear model can handle; wrong encoding destroys model quality.
- **Which signal predicted the outcome:** N/A — modeling rule, not a market signal.
- **Classification:** Not applicable. Relevant to AXIS as: rule for feature engineering if Direction Scorer layers are eventually converted to an ML model.
- **Source:** QUANT BIBLE (Part 5 — Case Studies).

### E12. QuantCo Opera House Ticket Pricing (Scarcity/Psychology Feature Engineering)
- **Setup/Context:** Pricing model for concert tickets using KNN; illustrating the value of engineering behavioral/psychological features alongside spatial data.
- **Exact data values:** Primary features: seat location (distance/angle to stage). Additional engineered feature: "scarcity metric" — dynamically raises prices as available seat supply diminishes closer to concert date (FOMO pricing).
- **Outcome:** Incorporating human psychology (scarcity/FOMO) into the model significantly improved pricing accuracy beyond what spatial features alone produced.
- **Which signal predicted the outcome:** Scarcity variable (an engineered behavioral feature) — shows that behavioral/market-structure features can be as important as raw numeric data in predictive models.
- **Classification:** Not applicable. Relevant to AXIS as: precedent for including FII behavioral patterns (Layer B) and VIX structural psychology (retail complacency at Weak Low) as model features, not just raw numerical values.
- **Source:** QUANT BIBLE (Part 5 — Case Studies).

### E13. Two Sigma CitiBikes (Cyclical Time Feature Engineering)
- **Setup/Context:** Predicting bike-share docking station usage; illustrating how to handle cyclical temporal variables.
- **Exact data values:** Cyclical variables that standard linear encoding handles badly: time of day (11:59 PM and 12:01 AM appear as "opposites" in raw numeric encoding); seasons; day-of-week. Collinear variables: temperature and weather condition.
- **Transformations applied:** Cyclical variables → time-of-day buckets (one-hot) or trigonometric cyclic splines; collinear variables → remove or combine to eliminate redundancy.
- **Outcome:** Correct handling of cyclical features dramatically improves model accuracy on time-series data.
- **Classification:** Not applicable. Relevant to AXIS as: rule for handling time-of-session features (market open/mid-session/pre-expiry timing) and day-of-week effects (expiry Thursday vs. other days) if quantitative scoring is ever modeled.
- **Source:** QUANT BIBLE (Part 5 — Case Studies).

### E14. Kelly Criterion Worked Example (Dice Game)
- **Setup/Context:** Illustrating optimal bet-sizing to prevent bankruptcy while maximizing compounding growth.
- **Exact data values:** Game: win = doubles wager (b=1); lose = loses wager (a=1); p = 2/3; q = 1/3. Formula: f = p/a − q/b = (2/3)/1 − (1/3)/1 = 2/3 − 1/3 = 1/3.
- **Outcome:** Optimal fraction = 1/3 of bankroll per bet. Even though expected value is positive, betting more than this fraction eventually leads to ruin due to variance. Betting less sacrifices compounding growth unnecessarily.
- **Which signal predicted the outcome:** Mathematical proof; not a market signal.
- **Classification:** Not applicable. Directly feeds AXIS Component 6 (Risk/Capital/Money Management) — the half-Kelly recommendation from AXIS prior conversation means in practice bet f/2 = 1/6 as the conservative implementation for a real trading account.
- **Source:** QUANT BIBLE; Five Rings firm interview section.

### E15. Five Rings / Jane Street Expected Value Recursive Problems (Interview Benchmarks)
- **Setup/Context:** Infinite dice re-roll game; optimal stopping time calculation.
- **Setup detail:** You can pay a cost to re-roll a bad dice outcome; calculate the exact threshold above which you stop re-rolling.
- **Exact data values:** Not specified numerically in the source excerpt but framed as: compare guaranteed payoff of stopping now vs. (expected value of re-roll) minus (cost of re-rolling) = optimal stopping threshold.
- **Outcome:** Treat every potential re-roll as a brand new game (sunk-cost independence); asymptotic formula gives the exact cut-off point. Qualitatively: this logic maps directly to the "Would I Do It Now?" rule (P16) — treat each moment of holding an option as the decision of whether to open that exact position fresh.
- **Classification:** Not applicable. Relevant to AXIS as: behavioral/exit-rule reinforcement.
- **Source:** QUANT BIBLE (Five Rings / Jane Street sections).

### E16. Natenberg — Eurodollar Contract Pricing Transformation (Domain-Specific)
- **Setup/Context:** Pricing an indexed interest-rate contract where the underlying cannot exceed 100 (Eurodollar); illustrating that standard Black-Scholes inputs must be transformed for special instrument types.
- **Exact data values:** If Listed Price = 93.50, then: Underlying Contract Value = 100 − 93.50 = 6.50; Exercise Price (model input) = 100 − Listed Strike Price; daily price change = (Annual_Volatility/16) × (100 − Listed_Price). When using this transformation: calls must be evaluated as puts and vice versa.
- **Outcome:** Without the transformation, the pricing model produces incorrect values for contracts bounded at par.
- **Classification:** Not applicable. Logged for completeness; not directly relevant to NIFTY which uses standard underlying price (not par-bounded).
- **Source:** Natenberg, *Option Volatility & Pricing*.

### E17. Kaushik 4-Stroke Method — NIFTY/BankNifty Intraday (Book Worked Example)
- **Setup/Context:** NIFTY Future closes at 10,873.30 previous day; trade is targeted for upcoming weekly expiry using previous day's high/low as entry triggers.
- **Exact data values:** NIFTY Future closes 10,873.30; 10850 CE is ATM/nearest ITM call; 10900 PE is nearest ITM put. Targets: buy 10850 CE when its premium exceeds previous day's high of that option; sell/short 10850 CE when premium falls below previous day's low. 10-rupee profit targets per leg.
- **Outcome (as presented):** Quick intraday scalp capturing a 10-point premium move in the direction of the breakout from previous-day range.
- **Which signal:** Prior day's high/low of the option premium itself — purely mechanistic breakout rule.
- **Limitations flagged by source itself:** Does not incorporate fundamental or macro context; requires full-time market monitoring; encourages overtrading; previous-day low doesn't account for trend context (could exit prematurely in a bullish trend); selling options has asymmetric risk not "equally applicable" to buying.
- **Classification:** Not a bait-trigger-harvest pattern — a purely mechanical price-breakout system. Partially overlaps with AXIS's directional option-buying framework (Strategy 3 in SKILL.md uses ORB breakout as confirmation trigger) but with far less context.
- **Source:** *Options Trading Handbook* (Mahesh Chander Kaushik).

### E18. Kaushik Ratio Spread — NIFTY 9100/9400 (Worked Example)
- **Setup/Context:** NIFTY at 9,105.30; constructing a call ratio spread to profit from flat/mildly rising market.
- **Exact data values:** Buy 9100 CE (ITM, one contract); sell two 9400 CE (OTM, two contracts). Premium received from two short calls > premium paid for one long call (net credit). NIFTY closing below 9400 at expiry → maximum profit (difference in premiums locked). NIFTY closing above 9400 → losses begin (uncapped above 9400 on the uncovered short leg).
- **Outcome:** Profitable as long as NIFTY closes below 9400; in-range market condition required.
- **Limitations flagged by source:** If NIFTY rises sharply above 9400, the extra naked short call creates theoretically unlimited loss; strategy assumes mildly range-bound or slightly bullish market; closing by end of day recommended to capture time-value decay.
- **Classification:** Not bait-trigger-harvest — a neutral-to-mildly-bullish premium-income strategy. Relevant to AXIS as an alternative to iron condors for slightly-bullish environments.
- **Source:** *Options Trading Handbook* (Kaushik).

### E19. Thomsett Conservative Institutional Options — Covered Call on Reliance (Worked Example)
- **Setup/Context:** A portfolio of Reliance shares already held; covered call writing for income.
- **Exact data values:** 500 Reliance shares at ₹1,400 each; sell 1500-strike call at ₹36 premium per share. If Reliance stays between ₹1,400–₹1,500 at expiry: seller keeps ₹36 premium, no shares sold. If Reliance exceeds ₹1,500: call holder exercises, seller must deliver shares at 1,500 but has already received ₹36, so effective exit price = ₹1,536.
- **Outcome:** Consistent premium income; cap on upside; requires balancing number of calls sold against shares held to prevent uncovered exposure.
- **Classification:** Not bait-trigger-harvest — conservative income-generation overlay on existing equity holding.
- **Source:** *Options Trading for the Institutional Investor* (Thomsett).

### E20. NSE Accumulation + Long Call Example (Booklet)
- **Setup/Context:** Bank Nifty or NIFTY long call for a very bullish directional view.
- **Exact data values:** Not specified numerically in the excerpt; the NSE booklet gives strategy tables only (see payoff tables extracted in Section 4 / general strategy library above).
- **Outcome/Classification:** Documented per the strategy tables (P&L profiles) rather than a live example; logged for completeness.
- **Source:** NSE Bank Nifty Options Strategies booklet.

---

# SECTION 4 — INSTITUTION-DETECTION RULES (IF-THEN FORMAT)

### IR1. OI Rising + LTP Falling → Writing/Selling at That Strike
- **IF** Open Interest at a specific strike increases (any magnitude) **AND** the Last Traded Price (premium) of that same option decreases on the same session/candle
- **THEN** institutions (or large writers) are establishing new short positions at that strike — this is net option SELLING, not buying, regardless of what directional bias PCR or GEX suggest in isolation.
- **CONFIDENCE: HIGH** — supported by multiple examples (June 29 2026, +851% OI / −46.80% LTP); the logic is definitionally correct (rising OI + falling premium mechanically = short positioning); called "unambiguous" in AXIS prior conversation.
- **Source:** AXIS trap-mechanism document (June 29 example); P3.

### IR2. GEX Negative + PCR Rising → Cascade Fuel (NOT Bullish Floor)
- **IF** Net GEX is negative (calculated from StockMojo or equivalent) **AND** PCR is rising simultaneously
- **THEN** do NOT interpret the PCR rise as a bullish protective signal; instead interpret it as increasing delta-hedge obligations on the put-writing side — more forced-selling fuel loading into the system, not a support floor being built. The setup is bearish/cascade-risk.
- **CONFIDENCE: HIGH** — directly evidenced by June 22–23 2026 (PCR 1.18→1.21 in negative GEX = fuel, not floor); explicitly named in SKILL.md and AXIS prior conversation as the exact retail trap pattern ("PCR alone fools people").
- **Distinguish from:** Rising PCR in POSITIVE GEX — that IS a legitimate bullish/protective signal.
- **Source:** nifty-options-pro `market_structure_gex.md`; AXIS conversation; E4.

### IR3. GEX Below Gamma Flip Level → Dealers Are Destabilizing, Not Stabilizing
- **IF** spot price is trading BELOW the Gamma Flip Level (the price where Net GEX crosses zero)
- **THEN** dealer hedging has mechanically switched from counter-cyclical (buying dips, dampening moves) to pro-cyclical (selling dips, amplifying moves). Any further decline will be self-reinforcing and potentially cascade-like. Use VIX + GEX Fibonacci targets (F9, F10) for downside levels rather than Max Pain or put-OI walls.
- **CONFIDENCE: HIGH** — multiple examples; the mechanics are structurally derived (formula F8, F15), not merely empirical.
- **Source:** nifty-options-pro `market_structure_gex.md`; E6 (June 23 2026 real cascade); E4.

### IR4. VIX Weak Low + CHoCH → Standing Multi-Day Bearish Caution Flag
- **IF** India VIX (15-min chart) prints a Weak Low structure **AND** then a CHoCH (Change of Character) to the upside on its own structure (not NIFTY's structure)
- **THEN** raise a persistent bearish caution flag that remains active for multiple sessions — the market is at elevated risk of a sharp volatility expansion and a large NIFTY decline. This flag should NOT be folded into a same-day score; it must persist until the VIX structure resolves (BOS confirmation or failure of the CHoCH).
- **CONFIDENCE: HIGH** for the existence and predictive value of the pattern (evidenced by June 19 VIX CHoCH → June 23 explosion, 4-day lead time). **MEDIUM** for the exact persistence duration (how many days to keep the flag active) — no explicit rule given in source material beyond "multi-day," so this parameter needs backtesting.
- **Source:** AXIS prior conversation; trap-mechanism document (E3).

### IR5. Overnight ATM OI Build >50% → Do Not Sell Naked Premium That Session
- **IF** overnight OI at the ATM strike has increased by more than 50% from the previous session's closing OI
- **THEN** do not sell naked premium (uncovered straddles or naked calls/puts) that session; high-volatility day risk is elevated. Treat as a flag in the Expiry Day Detection System (adds +2 points to the score, F16).
- **CONFIDENCE: MEDIUM** — quantitative threshold (50%) is stated explicitly in SKILL.md as a hard rule, but the source material does not provide multiple dated examples validating this specific 50% cutoff. Treat as a structural/operational rule pending backtesting on own dataset.
- **Source:** nifty-options-pro SKILL.md; `market_structure_gex.md`.

### IR6. VIX Above EMA(5) and Rising → Do Not Sell Premium Without Hedge
- **IF** India VIX (15-min chart) is trading ABOVE its 5-period EMA **AND** is trending upward
- **THEN** do not enter new premium-selling positions without an accompanying long wing (protective spread leg) to reduce net short-Vega exposure. The vol environment is expanding against a short-Vega seller.
- **CONFIDENCE: MEDIUM** — this is a structural/logical rule (rising IV directly hurts short-Vega positions) stated explicitly in SKILL.md but without specific dated backtesting examples from the real data. Well-grounded in first principles (F4 — Vega mechanics).
- **Source:** nifty-options-pro SKILL.md / `market_structure_gex.md`.

### IR7. Max Pain Relevant Only When GEX Is Positive
- **IF** a session opens with Net GEX POSITIVE
- **THEN** Max Pain is a valid candidate pinning/target level and can be used in conjunction with PCR and OI walls for intraday directional bias.
- **IF** a session opens with Net GEX NEGATIVE
- **THEN** ignore Max Pain entirely — use VIX formula target (F9) and GEX Fibonacci target (F10) instead.
- **CONFIDENCE: HIGH** — explicitly stated as a hard rule in nifty-options-pro material; supported by the mechanistic logic (GEX negative = dealers fight the pin, not enforce it).
- **Source:** nifty-options-pro `market_structure_gex.md`; F12.

### IR8. Order Flow + Volume Profile Boundary Required for Valid Turn Signal
- **IF** an Order Flow footprint shows exhaustion, absorption, or a delta divergence (P9, P10)
- **THEN** this is only a tradeable turn signal IF the price is simultaneously AT a marked Volume Profile boundary (VAH, VAL, VPOC, or LVN) — NOT if the signal occurs in the middle of an empty range.
- **CONFIDENCE: HIGH** — Wyckoff 2.0 states this explicitly as a primary caveat/warning: "Order Flow alone is subjective and practically useless unless deployed at a strict Volume Profile boundary." The AXIS prior conversation also explicitly quotes this book constraint.
- **Source:** Wyckoff 2.0; AXIS prior conversation.

### IR9. VPOC Migration + Sideways Price = Reversal Warning (Distribution)
- **IF** the Volume Point of Control (VPOC) has migrated to a new price level **AND** price is spending excessive time moving sideways at that new VPOC without continuing in the trend direction
- **THEN** treat this as a Change of Character warning (ChoCh) — likely the beginning of a Wyckoff distribution/accumulation structure. Reduce or exit trend-following positions.
- **IF** VPOC migration is followed immediately by a fast impulse continuing the trend
- **THEN** treat as a continuation signal — price has accepted the new value and is searching for the next level.
- **CONFIDENCE: MEDIUM** — derived from Wyckoff 2.0 framework description; not validated with a specific dated NIFTY example in the available material.
- **Source:** Wyckoff 2.0 (VPOC Migration Mechanics); P11.

### IR10. Shortening of the Thrust (3+ Waves) + High Volume → Institutional Blocking
- **IF** three or more consecutive impulse waves in the same direction each travel a shorter distance than the prior one **AND** volume is elevated/high on these shrinking waves
- **THEN** institutional money is actively blocking the path (effort-vs-result divergence); the trend is near exhaustion and a reversal is likely.
- **IF** the same three-wave pattern occurs with LOW volume
- **THEN** the trend is exhausted from sheer withdrawal of participation (no institutional blocking needed) — the dominant trend participants have simply stopped buying/selling.
- **CONFIDENCE: MEDIUM** — Wyckoff 2.0 framework rule; not backed by specific dated NIFTY examples in the available source material.
- **Source:** Wyckoff 2.0 (SOT — Shortening of the Thrust); P12.

### IR11. Delta Divergence (Positive Delta + Bearish Candle Close) → Institutional Absorption
- **IF** a candlestick shows positive cumulative Delta (more aggressive buying than selling) **AND** the candle still closes bearish (price moves down despite positive Delta)
- **THEN** a large passive institutional sell order (Iceberg/limit order wall) absorbed all the aggressive buying without allowing price to advance — this confirms Wyckoff Absorption (P9 step 2) and is frequently the signal confirming a Spring/Upthrust is in progress. Trade the short side.
- **CONFIDENCE: MEDIUM-HIGH** — logically derived from order-flow mechanics (F40) and confirmed as the standard institutional-absorption signal in Wyckoff 2.0; no specific dated NIFTY example provided in the source material for this exact signal pattern.
- **Source:** Wyckoff 2.0 (Delta Divergence Trap); P10.

### IR12. FII Participant-Wise Long-Short Ratio Change → Directional Conviction Check
- **IF** the NSE Participant-wise OI CSV (FII-specific) shows FII long-short ratio in index options is increasing (more net long)
- **THEN** institutional identity data supports bullish direction — this is Layer B of the AXIS Direction Scorer.
- **IF** FII long-short ratio is decreasing (more net short) while Layer A (PCR/GEX/VIX) appears bullish
- **THEN** a mismatch between Layer A and Layer B signals; this disagreement itself is useful data (described in AXIS prior conversation as: "Layer A can look bullish while FIIs are actually net short, and that mismatch itself is useful data").
- **CONFIDENCE: MEDIUM** for the rule as stated; **LOW for the weighting assumption that Layer B should carry the most weight** — AXIS prior conversation explicitly corrected this, noting Layer B was NOT validated against the five real June examples (those only validated Layer A and Layer C); weight of Layer B must be determined by backtesting, not assumed.
- **⚠ Single-source / unverified:** The five documented NIFTY examples in the trap document do not include the FII Participant-wise CSV for those dates; Layer B's incremental value beyond GEX/OI has not yet been evidenced in this material.
- **Source:** AXIS prior conversation (Layer B definition and correction); nifty-options-pro SKILL.md (FII signal hierarchy item 2).

### IR13. Institutional Accumulation/Distribution Reading via 5-Phase Wyckoff Protocol
- **IF** price trend stops abruptly (Phase A: PS/SC/AR/ST confirmed) **AND** price enters a sustained sideways range (Phase B) **AND** a shakeout occurs beyond the range boundary (Phase C: Spring or UTAD) **AND** a wide-range, high-volume bar breaks structure in the cause's direction (Phase D: SOS/SOW) **AND** LPS/LPSY forms as a low-volume pullback before the trend fully launches
- **THEN** a full Wyckoff accumulation (bullish) or distribution (bearish) cycle has completed; the trend direction of Phase E has been confirmed and is high-probability.
- **CONFIDENCE: MEDIUM** — Wyckoff 2.0 provides this framework well; however, the material explicitly warns against "robotic labeling" (no two structures look identical) and advises flexible, open-minded application over mechanical pattern-matching. Not validated against specific NIFTY trade dates in the portion of the material available.
- **Source:** Wyckoff 2.0; P1.

### IR14. GEX Expiry-Day Regime Rule — Cascades vs. Range
- **IF** on expiry day (Thursday), GEX is NEGATIVE at session open
- **THEN** follow the first directional break (buy OTM option in the break direction) — do NOT sell premium; cascade risk is high.
- **IF** on expiry day, GEX is POSITIVE at session open
- **THEN** sell OTM options / range trade around Max Pain — use the pin, not the cascade logic.
- **CONFIDENCE: HIGH** — stated as an explicit operational rule in nifty-options-pro `strategies_and_setups.md` (0DTE protocol) and consistently supported by the GEX mechanics logic.
- **Source:** nifty-options-pro `strategies_and_setups.md` (Expiry Day 0DTE Protocol); SKILL.md.

### IR15. Premium-Buying Strategy: Time Constraint for Weekly Options
- **IF** buying a weekly Nifty option for a directional play
- **THEN** never hold overnight — theta decay is too severe (ATM weekly loses 15–20% per day in the final week). For overnight holds, use MONTHLY expiry options only.
- **IF** 70% of the trade's projected holding period has passed **AND** the expected move has not occurred
- **THEN** exit regardless of P&L (time stop) — the Vega and Delta profile of the remaining position has decayed to a point where the residual value of holding is smaller than the risk of further Theta destruction.
- **CONFIDENCE: HIGH** for the overnight rule (consistently stated across all Nifty options articles and the SKILL.md); **MEDIUM** for the exact "70% of life" time-stop rule (stated in risk_and_adjustments.md but no specific backtesting evidence provided).
- **Source:** nifty-options-pro `strategies_and_setups.md`, `risk_and_adjustments.md`; Karthik's Nifty guide.

### IR16. "Would I Do It Now?" Short-Selling Rule → Exit Signal
- **IF** you are holding a short-premium position (straddle, strangle, naked) **AND** you ask "would I enter this exact position right now at current prices?" **AND** the answer is NO
- **THEN** close the position immediately. This is not a signal — it is a mandatory exit rule. Do not adjust; close.
- **CONFIDENCE: HIGH** — stated as a hard rule in both *Trading Option Greeks* (Passarelli) and nifty-options-pro `risk_and_adjustments.md`; logically consistent with the "managing uncertainty" core philosophy.
- **Source:** Passarelli; nifty-options-pro `risk_and_adjustments.md` (Technique 5); P16.

### IR17. Bias-Variance Tradeoff → Keep Direction Scorer Simple
- **IF** you are choosing between a complex/ML-based Direction Scorer and a simple weighted-rule system
- **THEN** prefer the simple, stable, slightly-biased rule-based system for financial data — the QUANT BIBLE's KNN-vs-linear-regression lesson directly supports this: complex models have low bias but high variance (unstable, overfit to noise in small sample financial data), while simple linear models are slightly biased but far more stable. This is the textbook-correct choice for NIFTY signal scoring given the small sample size (15 real examples).
- **CONFIDENCE: HIGH** for the principle; directly supported by QUANT BIBLE's bias-variance section AND explicitly cited as justification for AXIS's simple scoring approach in the prior conversation.
- **Source:** QUANT BIBLE; AXIS prior conversation.

### IR18. STT Trap → Square Off ITM Options Before 3 PM on Expiry Day
- **IF** you hold an option that is in-the-money **AND** it is expiry day (Thursday)
- **THEN** square off before 3:00 PM. Letting an ITM option expire without selling it triggers 0.125% STT on the intrinsic value (vs. 0.0625% on a normal sale). The extra cost is a direct, avoidable P&L drag.
- **CONFIDENCE: HIGH** — stated as an operational rule in multiple sources; the tax rate differential is documented regulatory fact (not an interpretive rule).
- **Source:** Karthik's Nifty guide; nifty-options-pro `strategies_and_setups.md`; `risk_and_adjustments.md`.

### IR19. Event Calendar → Discount Confidence Near RBI/Budget/FOMC
- **IF** an RBI policy date, Union Budget, FOMC meeting, or election result day falls within the current option's expiry window
- **THEN** reduce Direction Scorer confidence (Layer A especially) because IV is systematically elevated ahead of the event and subject to IV crush post-event. Do not sell options immediately before the event (premium is inflated); do not buy options immediately before the event (IV crush risk post-event). The Option Selector expiry-choice logic must also check whether the event falls inside the current week before recommending weekly vs. next-weekly vs. monthly.
- **CONFIDENCE: HIGH** for the rule; consistent across all sources (Karthik, SKILL.md, Passarelli, Natenberg all describe the IV-crush pattern around events). Specific "discount by how much" is not quantified in the material — treat as a hard qualitative override rather than a quantitative adjustment.
- **Source:** nifty-options-pro SKILL.md (event calendar as missing component); Karthik's Nifty guide; Passarelli.

### IR20. Dispersion Trading Signal (Institutional Correlation-Arbitrage)
- **IF** an index's implied volatility is trading richer (higher) than the volatility-weighted average of its individual constituent stocks' IVs
- **THEN** institutions may be selling index volatility (index options short) and buying single-stock volatility (component stock options long) — "dispersion trade." This structure shows up in the price of index options being systematically more expensive than their theoretical constituent-basket-equivalent.
- **CONFIDENCE: LOW** for retail applicability — this is explicitly described as an institutional/prop-desk strategy requiring complex multi-leg execution; listed here for completeness and for the AI Knowledge Interpreter agent (Component 4 Agent 1) to recognize if it manifests in the GEX/IV data.
- **Source:** Institutional algo-architecture material; `Wyckoff 2.0` institutional commentary.

### IR21. Structural Failure of Strength → Front-Running Signal
- **IF** price moves away from an extreme test level (potential Spring or Upthrust) **BUT** reverses completely before reaching the opposite end of the range
- **THEN** aggressive buyers (or sellers) are front-running the move, blocking downward (or upward) movement even earlier than expected — stronger conviction than a normal Wyckoff SOS signal. Treat as confirmation of the Phase C-to-D transition, not just a test.
- **CONFIDENCE: MEDIUM** — Wyckoff 2.0 framework description; not validated with specific NIFTY dates in available material.
- **Source:** Wyckoff 2.0; P13.

### IR22. Straddle Adjustment → Convert to Strangle When Tested
- **IF** Nifty moves beyond 60% of expected straddle range (approx >200 pts from ATM on a 7-DTE straddle) **AND** you still believe the market will stay in range
- **THEN** convert straddle to strangle by rolling the tested leg further OTM (accepting lower net credit in exchange for more range); OR add delta-hedge via futures; OR apply the "Would I Do It Now?" test (IR16) and close entirely.
- **IF** the P&L loss reaches 100–150% of the initial credit received (i.e., position has given back 2× what was collected)
- **THEN** exit the position unconditionally — this is the hard loss limit, not a suggestion.
- **CONFIDENCE: HIGH** for the 60% range trigger and the 150% loss-stop — explicitly quantified in `risk_and_adjustments.md`. **MEDIUM** for the specific adjustment technique choices — these are presented as options, not a ranked decision tree.
- **Source:** nifty-options-pro `risk_and_adjustments.md` (Adjustment Framework).

### IR23. Greek Drift Monitoring — Daily Warning Thresholds
- **IF** on a delta-neutral or range strategy, net Delta exceeds ±40 on a per-review basis (recommended: 9:15 AM and 2:00 PM daily)
- **THEN** delta-hedge via futures or add an offsetting leg to bring Delta back within tolerance.
- **IF** daily Theta decay exceeds 15% of the remaining premium in a position
- **THEN** re-evaluate viability — at this decay rate the position may have insufficient reward potential remaining to justify the continued Gamma risk.
- **IF** VIX spikes unexpectedly by >15% intraday while short Vega
- **THEN** consider buying a wing to reduce Vega exposure immediately.
- **CONFIDENCE: MEDIUM** — quantified thresholds explicitly stated in `risk_and_adjustments.md`; no backtesting examples provided in the material for these specific numbers. Logic is first-principles sound.
- **Source:** nifty-options-pro `risk_and_adjustments.md` (Greek Drift Management table).

### IR24. Win-Rate Trigger — Scale Down and Switch to Defined Risk
- **IF** win rate drops below 50% for 2 consecutive months in any strategy
- **THEN** reduce position size by 50% immediately **AND** switch to defined-risk strategies only (spreads, condors — no naked short exposure) until win rate recovers.
- **CONFIDENCE: MEDIUM** — explicit operational rule in `risk_and_adjustments.md`; a standard risk-management protocol but no evidence it was derived from backtesting specific NIFTY data vs. general best-practice.
- **Source:** nifty-options-pro `risk_and_adjustments.md`.


---

# SECTION 5 — COVERAGE CHECK (MANDATORY)

## Documents / Sections Processed

| Source | Sections Covered | Notes |
|---|---|---|
| Nifty Options Trading Guide (Karthik Subramanian / NiftyTradingPro, updated Mar 2026) | Basics (Strike, Premium, ITM/ATM/OTM), Greeks overview (Delta, Theta, IV/Vega), Strategies 1–4 (Straddle Sale, Iron Condor, Directional Buying, 0DTE), STT trap, lot-size/margin context | Processed completely |
| nifty-options-pro SKILL.md (core + all 4 reference files: greeks_and_pricing.md, market_structure_gex.md, strategies_and_setups.md, risk_and_adjustments.md) | GEX formula/regime/cascade, VIX formulas + structure, PCR/Max Pain rules, signal hierarchy, all 7 strategies, 4-step sizing framework, capital table, pre-trade checklist, position adjustment techniques 1–5, Greek drift table, exit rules, HAPI, tax, journal fields, 5-signal detection score, 0DTE protocol, Strike selection table | Processed completely — this is the richest single source |
| AXIS prior conversation documents (trap-mechanism document, architecture documents) | 5 real NIFTY examples (June 16, 22–23, 19–23, 29, 30 2026), 3-layer model definition, component definitions (1–6), VIX lead-time finding, book-integration notes, build-order recommendation | Processed; June 16 example has a coverage gap (data values not detailed in provided text — see below) |
| *Trading Option Greeks* (Dan Passarelli) — multiple excerpts/summaries | All four book parts, all five Greeks, volatility types (HV/IV/skew), strategies (vertical spreads, wing spreads, calendar/diagonal, straddles/strangles), delta-neutral trading, gamma scalping, "Would I Do It Now?" rule, put-call parity, synthetics, nonlinearity, four-directional thinking | Processed from all excerpts provided; note source is a series of chat-generated summaries, not the primary text — specific page numbers and chapter sub-details not available |
| *Option Volatility & Pricing* (Sheldon Natenberg) — multiple excerpts/summaries | Forward pricing, cost of carry, lognormal distribution rationale, delta-neutral dynamic hedging lifecycle (full 10-week worked example), square-root-of-time volatility formulas, Black-Scholes assumptions, Eurodollar transformation, standard deviation probability bands, speculator's fallacy, casino-edge mindset, frictionless market assumption | Processed completely from provided excerpts |
| *Options Trading for the Institutional Investor* (Michael Thomsett) — Table of Contents + Preface excerpt | Conservative investor re-definition, five ground rules, mutual fund underperformance problem, model portfolio structure, covered call Reliance example | Processed; note only front matter + Chapter 1 excerpt + Index was provided — deeper strategy chapters (Iron Butterfly, 1-2-3 system, Dividend Collar, candlestick/MACD/RSI application) are named in the Table of Contents but their content was not included in the source material provided |
| *Options Trading Handbook* (Mahesh Chander Kaushik) — 1-page summary | 4-stroke method (NIFTY/BankNifty), ratio spread (9100/9400 example), covered call (Reliance example), "money tree" ETF/SIP system (NIFTY BeES, covered call overlay), emotional/psychological discipline framework, rule-based trading plan | Processed completely from provided summary |
| QUANT BIBLE (MIT Sloan Business Club) | All 7 parts: intro/roadmap, probability fundamentals (Bayes, EV/Variance, distributions — Binomial, Poisson, Geometric, Normal, Exponential, Uniform), statistics (LLN, CLT, confidence intervals), quant research (bias-variance, curse of dimensionality, OLS/Ridge/Lasso, econometrics/OVB), 5 case studies (Two Sigma housing, QuantCo opera, Two Sigma CitiBikes), quant trading/market making (market making theory, determinants, trading games), question bank (Jane Street, Virtu, Optiver, Akuna, Citadel, HRT, Two Sigma, Five Rings, SIG), institutional firm profiles (Two Sigma, QuantCo, Jane Street, SIG, Five Rings, Citadel, Optiver, HRT, Virtu, Akuna, Jump, Tower, Renaissance), Kelly Criterion, lightweight algo architecture | Processed completely from provided text |
| Options Pricing and Greeks Analysis (GitHub project — saimanishprabhakar2020) | First/second-order Greeks table (all 11 Greeks), Black-Scholes PDE + closed-form solutions, Monte Carlo simulation GBM/discretization/estimator/standard error, project technical stack | Processed completely |
| NSE Bank Nifty Options Strategies booklet | Core payoff graph reading, Bullish strategies table (Long Call, Short Put, Call Spread, Put Spread, Synthetic Call, Covered Call/Futures, Collar, Long Combo), Bearish strategies table (table structure visible but detailed bearish content partially cut in the source — flagged below), Neutral strategies table (Straddle/Strangle/Butterfly/Condor/Box variants), glossary terms | Processed from available content; see gap flagged below |
| Wyckoff 2.0 (Structures, Volume Profile, Order Flow) | Full framework: Wyckoff law/phases/labels, Volume Profile (VWAP, VA/VAH/VAL, VPOC, HVN/LVN), Order Flow (BID/ASK mechanics, Delta, Imbalance, exit-column mapping), 3-step turn protocol, Delta Divergence Trap, VPOC Migration, SOT, sloping ranges, 4 strategies (Range/Mean Reversion, Value Area Re-entry, Continuation, Failed Reversion), institutional quantitative blueprint, dispersion trading, delta-neutral vol arb, market-making, institutional firm silo structure, algo design pipeline | Processed completely |
| Bookmap/Footprint Orderflow note | Core concepts, advantages, optimal conditions, platform access/comparison (Bookmap vs. DeepCharts), data feed requirements, crucial considerations | Processed completely; note: thin source, mostly platform-review content with limited trading rules beyond Wyckoff 2.0 |
| Institutional algo-architecture commentary (embedded across QUANT BIBLE and Wyckoff 2.0 extensions) | Lightweight algo design (Python/pandas/FastAPI/PostgreSQL stack), co-location/DMA/microwave networks, maker-taker model, kill switch, separation of quants and devs, statistical arbitrage, latency arbitrage, volatility arbitrage, AMM mechanics | Processed completely |
| Supabase + API Key Management document (Document 2 in context) | Technical infra decisions: Supabase PostgreSQL, env vars for API keys, dhanhq SDK, APScheduler, Render Background Worker vs. Oracle Always Free VPS, Postman's limited role (dev-only testing, not production), WebSocket vs. REST for 5-min polling | Processed; note this is infra/deployment content, not trading-signal content — no patterns, formulas, or institution-detection rules are relevant to extract from it; logged as processed but correctly yielding no Section 1–4 entries |

---

## Gaps, Ambiguities, and Items Flagged for Manual Review

### GAP 1 — June 16 2026 PE Decay Example (Data Values Not Recoverable)
The source references "June 16 PE decay" as one of the five documented real NIFTY examples but the specific numerical data values (exact strike, OI change %, LTP change %, what the specific trigger signal was) were not included in the portion of the trap-mechanism document reproduced in the source material. The example is named and categorized (E5 above) but cannot be fully structured without the underlying numbers.
**Action required:** Pull the raw trap-mechanism document and add the June 16 specific numbers to E5.

### GAP 2 — Thomsett Chapters 2–End (Strategy Details Missing)
The *Options Trading for the Institutional Investor* source only provided the Preface, Chapter 1, and the Index. Chapters covering: Bollinger Band/MACD/RSI application to covered calls; the "1-2-3 Iron Butterfly" named in the Index; the "Dividend Collar"; rolling options forward and up; the "exercise acceptance strategy"; long puts/short puts for down markets; the "long-call contingent purchase"; greed risk, collateral risk, margin requirements in detail — NONE of these chapter contents were in the provided source material.
**Action required:** If these strategy details are important for AXIS, the full Thomsett book content needs to be provided and reprocessed.

### GAP 3 — NSE Bank Nifty Booklet Bearish Strategies Table (Partially Cut)
The Bearish Strategies table header and some rows appear in the source but the detailed content rows (Long Put, Short Call, Put Spread, etc.) were not fully reproduced in the available text (the table structure shows `...` continuation after the Bullish Strategies table). Only table structure was visible, not all content.
**Action required:** If the NSE booklet bearish strategies section content is available, add the rows.

### GAP 4 — FII Participant-Wise OI CSV Not Validated Against Real Dates
Layer B (FII positioning) of the AXIS Direction Scorer is explicitly described in the source as unvalidated — the five real June 2026 examples were validated for Layer A (GEX/PCR/VIX) and Layer C (OI/price divergence) but NOT for Layer B. The FII CSV data for June 16–30 2026 was not included in the source material, so the incremental value and the appropriate weight for Layer B cannot be determined from what was provided.
**Action required:** Pull the NSE Participant-wise OI CSV for June 16–30 2026 and test whether FII positioning would have flagged the June 23 reversal or the June 29 trap independently of GEX/OI signals. This is the single most important data gap for completing the Direction Scorer weighting.

### GAP 5 — Lot Size Inconsistency (75 vs. 25)
Multiple articles in the source (the original "TRADING ALL THE THING" Karthik Subramanian guide and the NSE Bank Nifty booklet) use 75 as the lot size in worked premium calculations (e.g., "₹150 × 75 = ₹11,250"), while the dedicated 2026 lot-size article, the nifty-options-pro SKILL.md, and the Capital Sizing Table consistently use 25. The reduction from 50→25 was effective April 2023 per the source material. The STT example also uses 75 in one place (older data). **All calculations in this knowledge base use 25 as authoritative.** Any strategy P&L or position sizing derived from older articles must be recalculated with 25-unit lot size.
**Action required:** When using any formula from the "TRADING ALL THE THING" article or NSE booklet worked examples in live calculations, substitute 25 for the 75 or 50 lot size shown.

### GAP 6 — Second-Order Greeks (Charm/Speed/Color/Zomma/Veta/Volga) — Retail Relevance Low
These are documented (F6) from the GitHub options-pricing project but are explicitly described as professional/market-maker-level tools. Their application in AXIS is limited to the AI Knowledge Interpreter agent (Component 4 Agent 1) if it evaluates complex institutional positioning signals. No NIFTY-specific worked examples or trading rules using second-order Greeks were present in the source material.

### GAP 7 — Binomial/Poisson/Geometric/Normal/Exponential Distribution Formal Tables
The QUANT BIBLE provides a distribution table and formulas for all six major probability distributions. These are documented in F28 (general) but the full formal table (with PDF/PMF, E[X], Var(X) columns for each) is extensive and largely theoretical background for the AXIS Direction Scorer's statistical underpinning rather than a trading rule. The formulas are logged at a summary level. If AXIS's ML layer is built using explicit distributional assumptions, this table should be referenced in full from the QUANT BIBLE source.

### GAP 8 — Bookmap/DeepCharts Subscription Pricing Listed (Not a Rule)
The Bookmap/footprint orderflow note includes pricing details (Bookmap $34–$119/month subscription; DeepCharts browser-based with prop firm integration). These are not trading rules or patterns; logged as processed but excluded from Sections 1–4 as off-topic for rule-library purposes. If selecting an Order Flow tool for AXIS's Layer C data feed, this pricing information is relevant operationally.

### AMBIGUITY 1 — VIX "Weak Low" Definition Not Formally Quantified
The term "Weak Low" appears multiple times (detection system, strategy rules, VIX structure analysis) as a named structural label from SMC (Smart Money Concepts) applied to the VIX chart. However, the source material does not provide a formal numerical definition of what makes a VIX low "Weak" (e.g., a specific VIX level, a specific % below a moving average, or purely a structural SMC label). In the June 23 example, VIX = 12.89 is described as a Weak Low. Whether this is always the case around 12–13 VIX or whether it's a chart-structure label that can apply at any level is ambiguous.
**Action required:** Define "Weak Low" operationally for AXIS's detection system — either as a VIX level range (e.g., below 14? below historical 25th percentile?) or as a pure SMC structural label applied by reading the VIX 15-min chart.

### AMBIGUITY 2 — Direction Scorer Layer Weights
The AXIS prior conversation recommends Layer B (institutional identity) carry the most weight, Layer C next, Layer A least — but then immediately corrects this by saying these weights must be set by backtesting the five real examples rather than by theoretical assumption. No backtesting results are included in the source material. The weights are therefore explicitly undefined pending that backtesting work.
**Action required:** Complete the hand-scored backtesting of all five June examples against Layer A, C signals before assigning final weights.

### AMBIGUITY 3 — "Moderate" Direction Scorer Confidence Near Events
IR19 (event calendar rule) says to "discount confidence" near RBI/Budget/FOMC dates but does not specify by how much (−1 point? −2 points? Make the gate a hard block?). The material treats this as a qualitative override rather than a quantified adjustment.

### NOTHING INTENTIONALLY OMITTED AS REDUNDANT
Confirming: no entry was dropped on the basis that it appeared repetitive or already covered elsewhere. Where near-duplicate formulas or rules appeared (e.g., the VIX expected-move formula appears in both SKILL.md and `market_structure_gex.md`), both instances were cross-referenced but a single Formula Reference entry was created to avoid confusion, with both sources noted.

---

*End of AXIS Knowledge Base v1.0 — built from source material processed July 2026.*
*All entries are traceable to source location. See Coverage Check for gaps requiring follow-up.*

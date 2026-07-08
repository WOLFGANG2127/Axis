AXIS_MASTER_SPEC.md — v4 (Local-First, Merged, Nothing Left Pending)

This replaces v3 and its addendum with one file. Every addendum section is now
inserted where it belongs, not appended separately — there is no second
document to cross-reference while building. One naming contradiction between
v3 and a later tool-assignment pass is resolved directly below. Two Dhan items
that were open questions in v3 are now confirmed against Dhan's own live
documentation, not carried forward as guesses.

0. What This Version Fixes

The src/agents/ vs src/scoring/ contradiction, resolved. A later tool-assignment
pass (dividing work across Ollama, Cursor, Lovable, and Antigravity) assigned
the pure-Python specialist files to src/agents/sentiment.py, volume.py,
risk.py, open_interest.py, price_action.py, and trade_verification.py. This
directly contradicts Section 0's own naming fix from v3, which retired
src/agents/ for exactly this content because it collides with "Agent One" and
"Agent Two" — the two LLM-touching pipeline stages in Section 7. The fix is
one word, applied everywhere: every one of those six files lives in
src/scoring/, not src/agents/. The mapping from the older "eight specialist
agent" framing to this build's actual, leaner file tree, stated once so it
never needs restating: sentiment.py and open_interest.py's logic both live in
src/scoring/layer_a.py; volume.py and price_action.py's logic both live in
src/scoring/layer_c.py; risk.py's logic lives in math/pricing.py (the
formulas) plus journal/accuracy_engine.py (the bucketed historical lookups);
trade_verification.py's logic is folded directly into verifier_node's hard-
block checks in graph/nodes.py, not a separate file; market_analysis.py is
src/scoring/direction_scorer.py. decision_making.py is not in src/scoring/ at
all — it's analyst_node and verifier_node in graph/nodes.py, since that's the
only place an LLM is ever called. Whichever tool builds these files, hand it
this paragraph first.

Dhan's static-IP requirement, confirmed narrower than every prior draft
assumed. Checked directly against Dhan's own current API documentation:
static IP whitelisting is mandatory under current SEBI and exchange
guidelines specifically for Order Placement APIs — Orders, Super Order,
Forever Order. Fetching order details, trade details, candles, or the option
chain requires no such whitelisting. AXIS never places an order automatically
— a human does that by hand after reading the Telegram alert — which means
the entire static-IP question, treated as a real open risk to the GitHub
Actions deployment plan in every earlier draft of this project, does not
apply to AXIS's own automated pipeline at all. Nothing here needs a proxy VM,
locally or in the cloud, for this reason. Keep this in mind if a future
version ever adds automated order placement — that feature, specifically,
would need a static IP; nothing built through Phase 12 does.

Dhan's token refresh, confirmed and no longer an open question. Checked
directly against Dhan's authentication documentation: a token generated via
Dhan Web can be refreshed for another 24 hours by calling
api.dhan.co/v2/RenewToken with the current access-token and dhanClientId as
headers — this only works on a token that's still active, not one that's
already fully expired. Separately, if TOTP is enabled on the account, a fresh
token can be generated programmatically at any time by POSTing dhanClientId,
pin, and a live totp code to auth.dhan.co/app/generateAccessToken, with no
browser involved. Dhan also now offers a one-year API-key-and-secret flow for
individuals as a further alternative. No headless-browser automation is
needed anywhere in this build. For local development, regenerate a token by
hand each session. Before Phase 10, wire RenewToken as the primary path
(cheap, no PIN/TOTP needed) with generateAccessToken as the fallback when a
token has fully lapsed, using pyotp to produce the live TOTP code from a
stored secret.

Every other correction from v3 stands and is carried forward exactly as
before: the Kelly Criterion is f* = p − q/b, never the version missing
division by b, which would size a position at double what it should be at a
60% win rate and 2:1 payout. PCR-divergence is validated on one session
(June 30's 1.17 gap), not two — June 29's 0.074 gap doesn't clear any
meaningful threshold, so this stays informative context for Agent One's
narrative only, never a scored Direction Scorer input, until a second session
genuinely clears 0.5–0.7. The weekly loss limit is 3% of that specific
strategy's own virtual capital, scoped to virtual_portfolio_id, never checked
globally. The knowledge-file set is eight files, not seven —
options_strategy_library.txt sits alongside the other seven, deepening Agent
One's reasoning vocabulary with generic Greeks and options mechanics; it adds
zero new tradeable strategies, since AXIS only ever trades the five
registered strategies in Section 6. Cognee's internal LLM provider is Gemini,
for both its embedding step and its structured graph-extraction step — not
Groq, whose function-calling path is unreliable for Cognee's internal
Instructor-based extraction across models. Groq is reserved exclusively for
Agent Two's plain, unstructured narrative call, which has no structured-
output requirement at all.

1. What AXIS Is

A trading intelligence and signal-generation system for NIFTY and BankNifty
options — not an auto-trading bot. It reads three independent data layers,
applies a confidence-rated rule library built from seven real dated trading
sessions, synthesizes everything through two AI-touching pipeline stages
grounded in a verified knowledge base, and sends one Telegram alert when
every component agrees. A human places every order; AXIS never touches
capital directly, and that constraint is architecturally load-bearing — it's
what makes local-first development possible at all, and later what makes the
static-IP question above a non-issue.

One line: AXIS is a pre-trade intelligence engine, not a trading bot.

The mechanism it exists to catch, proven across seven sessions, not
theorized: institutions engineer a textbook-looking chart pattern (bait),
build their real position using a data signal retail never checks — GEX
flipping sign, a massive single-strike OI change, a VIX structural warning
(trigger) — then let the natural unwind liquidate the retail positions the
bait created (harvest).

2. The Knowledge Foundation — Seven Reference Sessions

June 16 (expiry day) — a PE bought at 1:45 PM with ₹8.35 of time value left.
The directional read was sound; it lost on timing — a bullish CHoCH fired
and was ignored, price rose 37 points against the position. Hard rule: never
buy options after 1 PM on expiry day; when CHoCH fires against a position,
exit first, ask questions after.

June 17 — an IB Fibonacci golden-zone PUT setup was correctly identified;
the stop was placed at the obvious round demand-zone number; price swept
exactly that level, then reversed and ran in the originally-predicted
direction anyway. Hard rule: stop-loss sits at the sweep candle's extreme
plus a 5-point buffer, never at the round number everyone else's stop sits
on — that number is precisely what gets hunted first.

June 18 (SENSEX expiry) — a 40% single-session account loss from four
simultaneous forces: negative GEX, 4.71 crore of fresh put OI at a nearby
strike misread as a defensive floor when it was actually forced-selling
potential energy, VIX at a structural Weak Low visible four days early,
and expiry-day gamma maximizing hedge sensitivity in the final hour. The
loss itself was a sizing and discipline failure, not a directional one — a
single trade at 10–15x correct size, no stop executed, on the instrument's
own expiry day despite an explicit standing warning against exactly that.
Hard rule: the 2% capital rule is absolute; cash is always a valid position;
never trade an instrument on its own expiry day without the full pre-trade
checklist passing.

June 22 (the trap being set — must never score bullish in validation) — PCR
rose from 0.82 to 1.21 in 45 minutes, a textbook-looking bullish signal,
while NIFTY sat pinned at Max Pain, appearing to confirm classic positive-
GEX behavior. But GEX was turning negative in real time, flip level near
24,050. This is the exact case proving PCR read without GEX context produces
a confidently wrong bullish read, and it's the primary regression test for
"PCR after GEX, never before."

June 23 (the trap sprung — strongest single validation in the whole
knowledge base) — GEX at −3.94 million crore, VIX at its Weak Low of 12.89,
with the CHoCH/BOS warning pattern visible on the VIX chart since June 19,
four full days ahead. NIFTY crashed 213 points to 23,865. The VIX expected-
move formula (Spot × VIX% / √252) produced a target of 23,904, a 39-point
error. An independent GEX-Fibonacci-style extension produced 23,895 — two
different mechanisms converging within 40 points of the real low. Max Pain
had zero gravitational pull once GEX went negative, closing 235 points below
it with no recovery attempt.

June 29 (day before expiry — the textbook winner, every hierarchy layer
agreed) — a morning Judas Swing to 24,120 swept the prior session's stop-
loss liquidity; the resulting supply order block matched the IB Fibonacci
golden zone almost exactly; two independent CHoCH confirmations; the 23,950
CE strike showed an 851% one-session OI increase with a simultaneous 46.80%
LTP collapse — the cleanest institutional call-writing signature in the
dataset, since rising OI with falling LTP can only mean new contracts being
sold, not bought. PCR at 0.7210. The current-expiry-vs-all-expiry PCR gap
this session is only 0.074 — informative, but nowhere near a threshold (see
Section 0). VIX at 13.87, rising 6%, inverse-correlated with price all
session. Entry ≈24,091, stop ≈24,105 (7 points, the proportional 6%-of-IB
formula), Target 1 (IB_LOW − 15 = 23,990) hit and 50% booked, stop moved to
breakeven, Target 2 pursued via the VIX-formula target. Actual captured
move: 195 points against a 209-point prediction, 6.7% error.

June 30 (expiry day, two analysis passes over one session merged into one
file) — a morning Judas Swing sweeping the prior session's Equal Highs;
an afternoon three-stage liquidity sweep culminating in a decisive Break of
Structure on a volume spike in the final 30 minutes. The 23,900/23,950/24,000
CE strikes all showed 160–530%+ OI increases with 83–97% LTP collapses —
heavy, deliberate call-writing defense of that zone into the close. The
current-expiry-vs-all-expiry PCR gap this session is 1.17 — this is the
session that actually validates the PCR-divergence rule, not June 29. VIX
stayed essentially flat (13.44→13.45) through the entire afternoon
breakdown, sharply contrasting June 23's 9% VIX rise on a comparably sized
move — the origin of the fear-driven-cascade-versus-mechanical-settlement-
unwind classifier. Also the real incident behind the freshness-cross-check
rule: a third-party widget's numeric tickers stayed live and internally
consistent while its bar-chart sat 292 points stale, caught only by cross-
referencing a second, banner-free source.

Confidence tiers. Confirmed HIGH: GEX is the master regime switch, read
before anything else; PCR rising in negative GEX is bearish fuel, not
protection; Max Pain only pins in positive GEX; Order Flow is only reliable
at a Volume Profile boundary; stop-loss belongs at the sweep-candle extreme,
never the round obvious level; Theta cost exceeding expected gross profit
blocks entry regardless of conviction. Confirmed MEDIUM-HIGH: Gamma Flip
acceleration; VIX Weak Low with CHoCH preceding a cascade with genuine multi-
day lead time; explosive single-strike OI build as a fresh institutional
ceiling/floor signal; proportional 6%-of-IB stop sizing. Confirmed MEDIUM:
the VIX-move classifier; the expiry-morning Judas Swing pattern — both one
clean example so far. Informative context only, not a scored input:
PCR-divergence, one-session-validated (Section 0). Theoretical, unvalidated:
FII Participant OI as Layer B; the four generic Wyckoff execution strategies
— mechanically sound, zero dated NIFTY examples. Corrected source errors:
lot size is 25, not 75; Jade Lizard's zero-upside condition requires net
premium received ≥ call spread width, the source article's own example fails
this; the NSE bearish-strategy table was blank in source, never fabricate
entries for it.

3. The Three Data Layers

Layer A — anonymous market-wide sentiment. GEX sign and magnitude, Gamma Flip
Level, VIX level and 15-minute structure, PCR value and trajectory (read
strictly after GEX), PCR-divergence (context only), Max Pain (positive GEX
only), overnight OI build percentage, IV versus Historical Volatility, the
VIX expected-move formula, the 5-signal expiry-day score, put-volume-
dominance percentage, the VIX-move classifier. All computed for free from
NSE's own option-chain endpoint and public VIX tracker — no paid vendor
account. Gamma per strike shares math/pricing.py with the Option Chain
Selector, so a fix in one place can't stay silently broken in the other. The
Gamma Flip Level is found by recalculating total GEX across a range of
hypothetical spot prices (gamma itself shifts as spot moves) and locating
where the aggregate curve crosses zero. Starting defaults, explicitly marked
for recalibration once real data accumulates: GEX flip zone = ±0.5 million
crore around zero; VIX Weak Low is defined structurally, not as an absolute
level — a new 15-minute low prints, then the next one to three candles close
above the prior candle's high. The GEX-Fibonacci-style extension target
formula ships disabled by default (scoring_config.use_gex_fibonacci = FALSE),
gated behind both a statistical significance test and a minimum sample floor
of 15–20 before it can ever auto-enable. Hard rule: PCR and Max Pain are
evaluated after GEX, never before.

Layer B — institutional identity. NSE's Participant-wise OI CSV, published
nightly around 7 PM IST, free, no login, a fixed predictable URL under
archives.nseindia.com. Long-short ratio computed separately for index
futures, index calls, and index puts. Zero of the seven reference sessions
include this data cross-referenced against outcome — weight it conservatively
until real backtesting says otherwise. The T+1 lag is enforced in code: every
use of this layer is stamped with fii_data_date, stamped separately from the
signal's own generation date, and the fetcher walks backward across weekends
and holidays using the event calendar when requesting "the previous trading
day" — never a naive date-minus-one.

Layer C — live order flow and liquidity, v1 scope, explicitly bounded. True
tick-level cumulative Delta, absorption, and Iceberg detection need an
always-on WebSocket listener; none of the seven sessions actually required
tick data to identify, including the specific detection of June 29's
institutional ceiling being built live. v1 ships entirely from free,
serverless data: VAH, VAL, and VPOC from 5-minute OHLCV and volume; the
OI-vs-LTP divergence signature — rising OI with falling LTP at a strike,
meaning selling, not buying, unambiguously — from polling the free option-
chain endpoint and comparing OI% change against LTP% change per strike. This
is the exact mechanism that caught June 29 and June 30. True tick-level
Delta divergence is deferred to a possible v2, not approximated badly, and
picked up only once real evidence shows the coarser version is missing
something a tick feed would catch. Non-negotiable, enforced as a hard boolean
gate, not a soft weighting: Order Flow away from a strict Volume Profile
boundary — VAH, VAL, VPOC, or an LVN — is classified unreliable regardless
of apparent strength.

The eight-level signal hierarchy, written once here and once, verbatim, into
gvof_mechanics.txt: GEX regime (master switch) → VIX structure → FII net
position → OI walls → PCR trajectory → IB Fibonacci golden zone (timing, not
direction) → SMC liquidity sweep (the actual entry trigger) → Max Pain (last,
conditional on positive GEX only).

4. Component 1 — The Direction Scorer

One number, 1 (strongly bearish) to 5 (strongly bullish). 3 means neutral, no
signal. The band 2–4 inclusive is the no-trade zone. Sub-scores from each
layer combine through a versioned scoring_config table — weights are hand-
backtested against the seven reference sessions, explicitly not statistically
robust with only seven examples, stated honestly rather than papered over.
Boundary-proximity is checked before scoring, not after: Layer C's weight is
conditional — full weight at a boundary, near-zero away from one — with
Layers A and B renormalizing to compensate, closing an earlier design flaw
that let a strong-but-meaningless Layer C reading pull the composite with
full weight regardless of boundary proximity.

Hard overrides that bypass the score entirely: GEX inside the flip zone
collapses the score to 3, no trade, regardless of everything else. A
5-signal expiry-day score of 5 or above activates the cascade protocol
regardless of the general direction score. A scheduled macro event inside
the event-calendar proximity window also collapses the score to 3 — event
risk is a stop condition, not something to blend into a weighted average.
The expiry-morning do-not-trade window — the first 30–45 minutes of an
expiry session — suppresses any signal regardless of what every other layer
shows, since this exact window is where the Judas Swing pattern operates and
a signal generated inside it is structurally more likely reading the bait
than the real move.

The 5-Signal Expiry Day Detection Score, embedded in this component, runs
separately on expiry days at market open, before regular detection begins,
though its output is only actionable once the do-not-trade window clears.
GEX below zero scores plus 3. VIX at or near the structural Weak Low scores
plus 2. Overnight OI build above 50% scores plus 2. PCR rising with GEX
negative scores plus 1. VIX change-of-character upward scores plus 1.
Maximum 9. A score of 5 or above triggers the cascade protocol — buying OTM
puts using the Down Target formula, Spot minus (Spot × VIX% / √252). A score
of 2 to 4 means reduce size, no directional bias. A score of 1 or below
means sell premium or range trade. June 23 is the validated proof of
concept: score above 5, Down Target formula 23,904 against an actual low of
23,865, a 39-point error, independently corroborated by the GEX-Fibonacci-
style extension's 23,895.

5. Component 2 — The Structure Confirmation Gate

A binary yes or no, never blended into the score, and must be yes before
proceeding. It checks whether current price action is consistent with a
Wyckoff Phase C test (Spring or UTAD) or Phase D displacement (SOS or SOW);
whether the three-step turn is visible (exhaustion, then absorption at a
boundary, then initiative); whether the signal is occurring at VAH, VAL,
VPOC, or an LVN at all — an automatic no if not, regardless of apparent
strength; whether VPOC is migrating in the signal's direction, with excessive
sideways time consumption after a migration reading as a reversal warning and
an automatic no; and the slope of the current range, computed as the linear-
regression slope of VPOC (or the VAH-VAL midpoint) over the last six profile
periods, with roughly 0.1% of spot per period as the starting threshold for
"sloping," itself a default subject to recalibration.

6. Component 3 — Strategy Activation

6.1, plugin architecture, mandatory. strategy_activation is never a growing
if/elif block keyed on direction score — that risks regressions in every
other strategy each time one is added or changed.

    from abc import ABC, abstractmethod

    class BaseStrategy(ABC):
        @abstractmethod
        def check_conditions(self, state: AxisState) -> dict:
            """Returns {'passed': bool, 'strategy_name': str, ...}"""

Each strategy lives in its own file under src/strategies/, inheriting this
base class. The graph node iterates a registered list and runs
check_conditions on each; the first that passes wins. At most one strategy
fires per symbol per cycle, so Agent One and Agent Two run once per symbol
per cycle regardless of how many strategies are registered. Adding a
strategy means a new file plus a registration entry in settings.py — never
an edit to graph.py itself.

6.2, the five registered strategies. Strategy 1 is GVOF, the most
empirically validated strategy in the entire system, with its own complete,
self-contained checklist: read the GEX regime first, as always — negative
GEX switches GVOF's structure from range-based golden-zone entries to
directional cascade-following, abandoning the Fibonacci golden-zone logic
for the session entirely. Check the prior evening's FII long/short ratio for
the day's bias. Let the Initial Balance — the first 80 minutes, 9:15 to
10:35 AM — establish IB_HIGH and IB_LOW; if that range is below 50 points,
declare no-trade for the day, a non-negotiable threshold. Identify the
golden zone via Fibonacci drawn IB_HIGH-to-IB_LOW and IB_LOW-to-IB_HIGH, the
0.618–0.786 band on each being the entry zone. On expiry days specifically,
skip the standard golden-zone flow for the first 30–45 minutes and watch
instead for the Judas Swing sweep-of-prior-reference-level pattern,
entering only after the sweep completes and a CHoCH confirms. The entry
trigger itself, on the 1-minute chart: a wick beyond the 0.786 level closing
back inside the zone, followed by a CHoCH confirming the reversal, entering
2 points beyond the 0.618 level in the reversal direction. Stop-loss sits
at the sweep candle's extreme plus a 5-point buffer, never the round Golden
Zone boundary number, sized proportionally at 6% of the IB range. Targets:
T1 is the IB extreme minus 15 points, exiting 50% and moving the remaining
stop to breakeven; T2 is the VIX-expected-move formula's target for the day.
No new entries after 2:00 PM; all positions closed by 2:30 PM regardless of
target status; a hard exit on any CHoCH against the position on the
5-minute chart, no exceptions. Strategies 2 through 5 are the four generic
Wyckoff execution strategies — Trading Range Mean Reversion, Failed
Breakout Reversion, Continuation BUEC, and Failed Reversion — theoretically
sound, textbook-correct, but with zero dated NIFTY-specific numeric examples
behind any of them. GVOF gets first validation priority in Phase 7 and the
largest initial paper-trading capital allocation in Phase 10; the four
Wyckoff strategies accumulate their own dated evidence before their
allocations grow relative to GVOF's.

Hard behavioral gates on every strategy, the most cross-corroborated rules
in the entire knowledge base: HAPI — if reasoning for holding has shifted
from analytical to hope-based without new objective data, exit. WIDIN — if
the honest answer to re-entering this exact position fresh, right now, at
current prices, is no, exit. A third hard behavioral gate stands alongside
these two: never add to a losing options position — the Greek profile has
completely shifted, and the new lot carries different Gamma, Theta, and Vega
exposure at a worse strike than the original entry, meaning this isn't
averaging down, it's opening a structurally different trade.

6.3 — the Option Chain Selector (Component 6). Given a confirmed direction
and a PROCEED verdict from Agent Two, this selects one specific contract.
Strong directional conviction, score 4 to 5: ATM or one strike ITM, for the
highest Delta response per rupee moved. Moderate directional view: ATM,
balanced Delta and cost. A cascade signal, 5-signal score 5 or above: one to
two strikes OTM below ATM for the put buy, low cost with a Delta-Vega
multiplication effect as VIX expands alongside the GEX-negative cascade.
Hard exclusion: never more than 300 points from ATM on a weekly expiry for a
directional trade — Theta destroys the premium before the move can
materialize at that distance. Delta band for directional buys: 0.35 to
0.55; below that is too little response per point of movement, above it is
overpaying for something behaving like the underlying without the leverage
benefit. Delta convergence near expiry means the same OTM strike that had
Delta 0.38 at 30 days to expiry can be down to 0.09 near expiry — which is
why expiry-day directional buys go ATM or one strike ITM specifically to
keep meaningful Delta exposure. Liquidity filters, starting estimates to
calibrate during paper trading: exclude any strike with open interest below
5,000 contracts, or a bid-ask spread above ₹3 for the current week's expiry.
Theoretical value check: compute Black-Scholes theoretical value using
current IV; LTP below theoretical by more than 5% reads as underpriced,
modestly favorable for buyers; LTP above theoretical by more than 10% flags
as potentially overpriced — the bands are deliberately asymmetric, since
options in a retail-dominated market structurally trade rich more often
than genuinely cheap. Jade Lizard verification, when applicable: total net
premium received must be greater than or equal to call spread width — the
source article's own worked example fails this exact check, and it is never
copied. Expiry selection: weekly for directional trades normally, next-
weekly when a major event falls inside the current week per the event
calendar. IV Rank below 30 favors buying premium; above 50 favors selling or
spreads. BankNifty IV runs roughly 1.3 to 1.6 times NIFTY IV — sizing
adjusts proportionally.

6.4 — Risk and Capital Management (Component 7). Maximum single-position
risk is 2% of total capital, no exceptions. Maximum weekly loss limit is 3%
of that specific strategy's own virtual capital, scoped to
virtual_portfolio_id, never checked globally (Section 7.2). Defined-risk
strategies only for the first six months of live trading; naked exposure
added only after three consecutive profitable months with a complete trade
journal showing positive EV realization. The never-add-to-a-loser rule
already stands as a hard behavioral gate in Section 6.2. Position sizing
table: ₹300,000 of capital gets 1 to 2 lots, ₹6,000 maximum risk, an
₹8,000–15,000 monthly target; ₹500,000 gets 2 to 4 lots, ₹10,000 maximum
risk, ₹15,000–25,000 monthly target; ₹1,000,000 gets 4 to 8 lots, ₹20,000
maximum risk, ₹30,000–50,000 monthly target. STT trap enforcement, exact
numbers: square off any ITM position before actual expiry settlement time,
always, using the real time pulled from option-chain metadata. The cost
differential — exercise at 0.125% of intrinsic value versus regular square-
off at 0.0625% of sell premium — is computed and displayed, not just flagged
as a boolean warning, since a 300-point intrinsic-value position incurs
roughly ₹9 on square-off versus roughly ₹28 on exercise, and that gap scales
with position size. System health monitoring: Sharpe Ratio, Sortino Ratio,
and Maximum Drawdown computed monthly from accuracy_log. If win rate falls
below 50% for two consecutive months, position size is automatically halved
and the system reverts to defined-risk-only strategies until three
consecutive profitable months are restored.

7. The Agent Pipeline

7.1, Agent One, the Knowledge Interpreter. Model routing: primary/fallback
rotation between Gemini Flash and Z.ai's GLM-4.7-Flash or GLM-4.5-Flash, both
genuinely free with no expiry, wired through LiteLLM as one interface.
Claude stays available as a config-driven premium upgrade, never the
default. Order of operations: an Agent One call only ever happens after the
Direction Scorer and Structure Gate have both already cleared, keeping LLM
calls limited to cycles that actually matter. It builds one specific query
from live numbers, never a generic one, queries the knowledge base capped at
three retrieved chunks regardless of how many come back, constructs a
versioned system prompt (data/prompts/analyst_v1.md, never edited in place —
a change becomes v2.md so every past signal stays attributable to the exact
prompt version that produced it), calls the LLM router with a 45-second
timeout, and passes the output through the universal JSON extractor before
parsing. On timeout or parse failure, it retries once with an explicit
JSON-only reminder; on a second failure, it falls back to the other free
provider and sets degraded_mode = True. Output, strict JSON: setup
classification (genuine institutional setup, retail trap forming, retail
trap already triggered, or unclear), confidence (high, medium, or low), the
active Wyckoff phase and event, whether the signal sits at a valid VP
boundary, order-flow consistency, the VIX-move classification if a
directional move is in progress, a two-sentence plain-language explanation,
and any hard blocks the rule library requires. Non-negotiable, built into
the prompt itself: if order flow is occurring away from a Volume Profile
boundary, it must be classified unreliable regardless of how convincing the
reading looks.

7.2, Agent Two, the EV Verifier. The single most important architectural
rule in this design: the actual PROCEED/BLOCK decision must never depend on
an AI model succeeding. It is pure arithmetic, computed deterministically in
math/pricing.py (the formulas) and journal/accuracy_engine.py (bucketed
historical lookups), orchestrated by verifier_node, with zero external
failure surface for the decision itself. EV equals win probability times
average historical gain, minus loss probability times average historical
loss, minus real transaction costs computed per-trade from the actual
premium — STT at 0.0625% of sell value (the correct rate here specifically
because every strategy's time-discipline rule forces square-off before
close; the 0.125% ITM-exercise rate is a separate defensive check confirming
that discipline actually held, not an EV input), brokerage around ₹40,
exchange charges around ₹35, 18% GST on brokerage. Kelly, stated correctly,
once, so it can never be miscopied again: f* = p − q/b, where p is the
historical win rate for the bucketed condition, q is 1 − p, and b is average
win divided by average loss, both positive rupee figures. Half-Kelly, capped
by the 2% capital rule, whichever is smaller. The Theta viability check
compares Theta per day times expected holding days against expected gross
profit. The STT trap check applies for any position that might be held into
expiry, using the real settlement time. The weekly loss limit check is
scoped to that specific strategy's virtual_portfolio_id, never global — a
global check would either let one strategy's blown limit block a different,
healthy strategy's valid signal, or fail to protect the strategy it's meant
to protect. Hard blocks, any one of which forces BLOCK regardless of EV: EV
negative after costs, Theta cost exceeding expected gross profit, the 3%
weekly limit already hit for this strategy, direction score 2 to 4
inclusive, GEX inside the flip zone, more than two trades already taken
today, or the current time still inside the expiry-morning do-not-trade
window. The optional AI narrative, Groq's openai/gpt-oss-120b, is purely
advisory human-readable text and never has a vote — it receives only a
distilled roughly-hundred-character summary of Agent One's reasoning, never
raw knowledge-base chunks, keeping the prompt small and the response fast.
Cold-start policy: historical match-rate checks use a discrete, bucketed
match key only — direction-score bin, structure-gate boolean, strategy name,
VIX classification — never continuous fields like exact GEX or PCR values,
which would almost never repeat and silently produce a permanent empty
check. A minimum sample floor of 15 to 20 applies before reporting any
historical win rate at all; below that, store null and log the sample size
explicitly, rather than let a 100%-on-one-trade figure sit in an alert
looking as confident as a real 73% from forty trades. Kelly sizing stays at
a flat 1% per trade until 30 to 50 completed paper trades per strategy exist,
then transitions to half-Kelly with a hard ceiling. Degraded-mode haircut,
pure Python: ev_rupees multiplied by 0.6 if degraded_mode is true, otherwise
unchanged — a starting number, tuned once enough degraded-mode signals have
logged real outcomes. Failure handling: if every model in the verifier's
fallback chain fails, verifier_node does not raise — raising here would
crash the graph mid-run and risk a run_locks row stuck held past the end of
the cycle. It synthesizes a verdict of BLOCK, ev_rupees null, reason "agents
unavailable, degraded mode," and sets degraded_mode true. Output format,
three fields only: ev_rupees as a signed number, verdict as PROCEED or
BLOCK, reason as one sentence if blocked or null if proceeding.

7.3, the distributed-concurrency problem, deferred but built behind a stable
interface. This only genuinely matters once NIFTY and BankNifty run as two
separate GitHub Actions virtual machines sharing zero memory — a Phase 10
concern. For local-first development, a plain asyncio.Lock() inside the
single running process is sufficient. Build it correctly from day one
anyway, at negligible extra cost: a small interface —
async def acquire(lock_id, ttl_seconds) -> bool and
async def release(lock_id) -> None — backed by asyncio.Lock() now. Swap in
the Postgres-backed version below at Phase 9.5; nothing calling the
interface needs to change.

    CREATE TABLE infrastructure_locks (
        lock_id TEXT PRIMARY KEY,
        acquired_by TEXT NOT NULL,
        acquired_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        expires_at TIMESTAMPTZ NOT NULL
    );

Self-healing acquisition via INSERT ... ON CONFLICT DO UPDATE ... WHERE
expires_at < now() — one row affected means acquired, zero means someone
else holds it, back off. Apply this for lock_id = "zai_api_call" and
lock_id = "groq_agent_two". This migration can be applied to Supabase at any
time; it's only the code path that's deferred, not the schema.

8. The LangGraph Engine

8.1, the Pydantic state contract. AxisState carries, at minimum: symbol,
cycle_timestamp, market_context, direction_score, structure_confirmed,
active_strategy, analyst_opinion, verifier_verdict, degraded_mode,
alert_sent, correlation_id, node_error. Every field a later node populates
must be declared Optional with a default of None — without this, Pydantic
raises a validation error the moment the graph constructs state before those
later nodes have run. Keep node_error as its own separate field, never
sharing a key with a structured domain field like a data-quality object — if
two writers with incompatible shapes both target the same key, whichever
runs later silently wins, risking a validation error on exactly the output a
node crash produces, precisely when clean error surfacing matters most.

8.2, the golden rule of nodes. LangGraph applies a plain overwrite reducer
per key by default — whichever node writes a given key last simply wins,
with no automatic merging unless a custom reducer is attached to that key.

    # WRONG — returns the full state object; risks silently erasing fields
    # other nodes haven't touched yet this cycle.
    def analyst_node(state: AxisState) -> AxisState:
        state.analyst_opinion = call_llm_router(state)
        return state

    # RIGHT — return only the keys this node actually changed. LangGraph
    # merges this dict into the existing state; every other field stays
    # exactly as the previous node set it.
    def analyst_node(state: AxisState) -> dict:
        opinion = call_llm_router(role="analyst", state=state)
        return {"analyst_opinion": opinion}

Every node in this system follows the right-hand pattern without exception.

8.3, node by node. data_verification_node runs first, checking trust_status
for every source touched this cycle and flagging degraded_mode = True if
anything came back stale, demo-flagged, or fell back to a cached value.
analyst_node and verifier_node behave as described in 7.1 and 7.2;
verifier_node must explicitly short-circuit to a synthetic BLOCK if
analyst_node's output arrives empty or errored, never assuming well-formed
input just because the node-return-contract fix exists elsewhere.
dedup_node checks whether this exact symbol-and-strategy combination has
already been alerted this session, and separately enforces staleness — if
now() minus cycle_timestamp exceeds 90 seconds, it sets
dedup_status = STALE_DISCARDED and suppresses dispatch rather than sending a
signal against conditions that may have already changed.

8.4, graph routing. calendar_gate → lock_acquire → data_verification →
direction_scorer → structure_gate → strategy_activation → analyst_node →
verifier_node → conditional_edge. A BLOCK routes to a terminal end state —
logged, lock released, done — deliberately not a loop back into the graph
to retry; the next attempt is a fresh graph invocation five minutes later
when the cycle fires again. A PROCEED routes to option_selector →
risk_check → position_sizing → dedup_node → telegram_dispatch → end.

8.5, async, decided once, not left open. Every node is async def,
httpx.AsyncClient is used throughout, and main.py's entry point calls
await graph.ainvoke(state). The justification is overlapping I/O across
multiple bounded network calls per cycle, not any WebSocket requirement,
which stays out of v1 scope entirely. This is decided before Phase 6's
first node is written, not mid-build.

8.6, the universal JSON extractor, the exact code, not just a description of
the pattern:

    import json, re

    _FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)

    def extract_json(raw: str) -> dict:
        cleaned = _FENCE_RE.sub("", raw).strip()
        first, last = cleaned.find("{"), cleaned.rfind("}")
        if first == -1 or last == -1:
            raise ValueError(f"No JSON object found in model output: {raw[:200]}")
        isolated = cleaned[first:last + 1]
        try:
            return json.loads(isolated)
        except json.JSONDecodeError:
            fixed = re.sub(r",\s*([}\]])", r"\1", isolated)
            return json.loads(fixed)

8.7, Pydantic to Supabase serialization. supabase-py does not automatically
serialize Pydantic models into a JSONB column.

    # WRONG
    supabase.table("signals").insert({"analyst_output": state.analyst_output})

    # RIGHT — mandatory serialization boundary before any Supabase write
    supabase.table("signals").insert({
        "analyst_output": state.analyst_output.model_dump_json()
        if state.analyst_output else None
    })

8.8, float versus Decimal for LLM-output numeric fields. LLMs frequently
output numbers in scientific notation or with irregular trailing decimals; a
field typed Decimal parsing "1.5e6" crashes outright. Every field parsing
direct LLM output — ev_rupees, or any market number a model might echo back —
is typed strictly as float, never Decimal or int. Precision loss on a
14-digit GEX figure is mathematically irrelevant for a directional signal;
Postgres NUMERIC handles real storage precision on the database side.

8.9, retry discipline. LiteLLM's own internal retry is disabled
(num_retries=0), with all retry logic kept at the node level exclusively —
otherwise both stacks fire multiplicatively, turning an intended single
retry into several actual calls. stream=False is set explicitly on every
completion call, since a fragmented streaming response breaks the JSON
extractor outright.

9. The Data Pipeline

The timezone mandate: every datetime operation — is_market_open, expiry
calculations, timestamp comparisons — constructs times using
zoneinfo.ZoneInfo("Asia/Kolkata") explicitly, never relying on the runner's
or machine's local time. The option-Greeks contract in math/pricing.py takes
spot, strike, risk-free rate, IV, and time-to-expiry as explicit inputs,
never scraped directly from NSE. years_to_expiry always anchors to actual
market close — 15:30 IST on the expiry date — never midnight; anchoring from
midnight makes Theta and Delta catastrophically wrong for the entire final
trading hour, treating 10 AM and 3:29 PM as having nearly identical time
remaining.

Every data client — the Dhan client, the NSE fetcher — returns the same
shape regardless of source: the data itself, a fetched_at timestamp, and a
trust_status field of live, stale, or demo-fallback. Detection needs more
than banner-scanning alone, proven by a real incident, not a hypothetical:
June 30's widget kept its numeric tickers live while its chart sat stale —
nothing marked that visually as fake. A freshness cross-check (comparing a
last-updated timestamp between elements of the same source where available)
and a cross-source consistency check (does one source's OI roughly agree
with another's for the same strike, flagged suspect on divergence) are both
required.

The T+1 FII trap: the fetcher requests the previous trading day's date,
walking backward across weekends and holidays via the event calendar, never
a naive date-minus-one, which would silently request Friday's data — or
nothing — on a Monday pre-market run.

The instrument resolver: Dhan requires mapping a symbol to an internal
security ID through a periodically updated master instrument file, fetched
and cached once per day pre-market, never queried live mid-cycle. Strikes
are not globally unique across instruments — a 24000 CE for NIFTY and a
24000 CE for BankNifty have different tokens — so resolution filters in
strict order and asserts exactly one match:

    def resolve(symbol: str, strike: int, expiry: str, option_type: str) -> int:
        # 1. Filter by symbol EXACTLY ("NIFTY" vs "BANKNIFTY")
        # 2. Filter by expiry EXACTLY (YYYY-MM-DD)
        # 3. Filter by option_type EXACTLY ("CE" or "PE")
        # 4. Filter by strike EXACTLY
        # 5. Assert len(result) == 1.
        #    0 results -> raise InstrumentNotFoundError
        #    >1 results -> raise AmbiguousInstrumentError

The candle cache: cached_candles is upserted from the live API at the start
of every cycle; every time-series indicator — VWAP, Initial Balance,
cumulative order-flow — is calculated locally in Python against this cache,
never by repeatedly calling an external API mid-calculation. This is what
lets a stateless cycle produce indicators that structurally need historical
context without burning API quota.

Dhan access, both items resolved, per Section 0. Static IP applies only to
Order Placement APIs, which AXIS never calls automatically — this is a
non-issue for the pipeline as built. Token refresh uses RenewToken first
(cheap, works on any still-active token), falling back to
generateAccessToken with a live pyotp-generated TOTP code when a token has
fully lapsed; automate this before Phase 10, regenerate by hand locally
until then.

10. The Knowledge Graph — Cognee, Local-First

The real API is four verbs: cognee.remember(), cognee.recall(),
cognee.forget(), with cognee.improve() folded implicitly into remember() —
remember() internally runs add, then cognify, then improve in one call;
recall() auto-routes to the best retrieval strategy with no manual search-
type specification needed. For Phases 1 through 9, Cognee runs on its
zero-config local default backend (Kuzu / local file store) — no Postgres
environment variables at all, since the "does the graph survive between
runs" problem only exists on ephemeral cloud containers, and a local machine
has a persistent filesystem. Cognee's supported graph backends beyond the
local default include Neo4j, Neptune, and Postgres — Postgres is a real,
documented option, not an unverified guess, which means the Phase 9.5
migration to it is very likely to just work rather than being a coin-flip
onto a pgvector fallback; keep the fallback plan written down anyway, as
cheap insurance.

Cognee's internal LLM provider — used for its own embedding step and its own
structured graph-extraction step during remember() — is configured to
Gemini, per Section 0's diagnostic: Gemini's function-calling support is
reliable for Cognee's internal Instructor-based extraction; Groq's is not
across models. This is a config change (LLM_PROVIDER / LLM_API_KEY pointed
at Gemini), not a code change. Groq is reserved exclusively for Agent Two's
own plain, unstructured narrative call in llm/router.py — a genuinely
different, simpler code path with no structured-output requirement, and the
one place Groq remains fully appropriate.

Immediately before Phase 10, the deferred proof: switch to the Postgres/
pgvector backend via DB_PROVIDER=postgres, VECTOR_DB_PROVIDER=pgvector,
GRAPH_DATABASE_PROVIDER=postgres, pointed at Supabase's direct-connection
host, port, username, password, and database name parsed as five discrete
values — never one combined connection URL, since the real package expects
the parts separately. Confirm at that point whether the installed version
needs its own dedicated Postgres schema separate from public, or maintain a
documented list of exactly which tables Cognee creates if no clean schema-
targeting exists. Run the persistence test once, immediately before Phase
10: from a genuinely fresh environment, recall() a fact remember()-ed
previously with no re-ingestion in that environment — proof the graph
survives an ephemeral container, not a formality.

Eight knowledge files, not seven: trap_mechanism.txt, gex_mechanics.txt
(with the corrected PCR-divergence framing from Section 0 written in
explicitly), gvof_mechanics.txt (with the eight-level hierarchy from Section
3 written out explicitly, once), wyckoff.txt, vsa.txt, risk_rules.txt (with
the 3%-of-strategy-capital weekly loss limit stated explicitly),
formulas.txt (with the corrected Kelly formula, f* = p − q/b, stated
explicitly so it can never be miscopied again), and
options_strategy_library.txt (generic Greeks and options-strategy mechanics,
deepening Agent One's reasoning vocabulary only, adding zero new tradeable
strategies). Plus seven dated example files, june16.txt through june30.txt.
Keep every Drive filename exactly as it already is when copying source
content in — Cognee retrieves by content and embedding similarity, never by
filename, so renaming source drafts for tidiness adds risk of losing track
of which draft is authoritative for zero retrieval benefit.

11. The Trading Journal

Each strategy-and-symbol combination draws from its own virtual_portfolios
capital pool — a loss in one is never paid for by another's gains in the
aggregate numbers, since blended capital would hide whether an individual
strategy is actually profitable on its own terms. position_sizer.py's
calculate_position function is the one place sizing math lives; no graph
node ever does this arithmetic inline. trade_outcomes samples price at 15,
30, 60, and 120 minutes after every exit, tagged with the VIX-move
classification, enabling questions like "on trades closed at the first
target, did price on average keep running" to be answered directly from
data. cycle_summaries.structure_gate_passed logs near-misses too — cycles
where direction score hits 4 or 5 but the Structure Gate blocks it — so it's
eventually possible to check whether the gate is well-calibrated, correctly
vetoing traps, or also suppressing genuine winners, rather than only ever
seeing its "yes" cases in the data. Four loss-taxonomy tags, derived
directly from the June 16/17/18 post-mortems, populate
trade_outcomes.outcome_category for losing trades: STRUCTURE_SIGNAL_IGNORED,
ZONE_INTEGRITY_MISREAD, TIME_DECAY_MISJUDGED, OI_WALL_UNDERWEIGHTED.

12. Database Schema

Market data lives in exactly one place, market_context_snapshots; signals
links to it by foreign key and never duplicates numeric fields. Every table
written to by both the NIFTY and BankNifty jobs carries a non-nullable
symbol column, because two parallel writers with no instrument tag produce
ambiguous joins, blended performance metrics, and — in cycle_summaries
specifically — a watchdog that stays green while one entire symbol's
pipeline is silently dead. Rupee amounts are NUMERIC(12,2); ratios and
percentages are NUMERIC(8,4) — never floating point for anything financial.

Core tables: candles and cached_candles (both symbol-scoped); signals (one
row per cycle reaching a verdict, linked to its market_context_snapshots row
by foreign key, never duplicating that row's numeric fields);
market_context_snapshots (one row per cycle regardless of outcome, symbol
mandatory); ai_agent_opinions (one row per model call — role, model used,
raw output, token counts, latency); virtual_portfolios (keyed by strategy
name and symbol together, not strategy name alone, so a strategy's
per-instrument performance is never diluted by blended capital);
paper_trades (entry, stop, target, exit, max adverse excursion, linked to
its virtual_portfolios row); trade_outcomes (the 15/30/60/120-minute
post-exit samples); strategy_performance_daily (keyed by strategy, symbol,
and date together); cycle_summaries (symbol mandatory, non-negotiable — the
single most important fix carried forward from every prior audit of this
schema); data_quality_log; run_locks; infrastructure_locks (the distributed
mutex from Section 7.3); schema_info; vix_regime_flags; scoring_config
(versioned Layer A/B/C weights); documented_patterns (the seven hand-
validated sessions as structured, queryable rows, doubling as the regression
fixture re-run whenever scoring weights change); system_paused (a single-row
kill switch); events (the calendar table); accuracy_log (symbol and a
truncated computed_date both included, with a composite unique constraint
across computed_date, signal_type, regime_condition, and symbol, so two
calls a few hundred milliseconds apart are never treated as separate rows).

Security and grants, exact code:

    grant usage on schema public to anon;
    grant select on all tables in schema public to anon;
    alter default privileges in schema public grant select on tables to anon;

    revoke select on run_locks from anon;
    revoke select on schema_info from anon;
    revoke select on infrastructure_locks from anon;

    grant insert, update on signals, paper_trades, trade_outcomes,
      market_context_snapshots, ai_agent_opinions, cycle_summaries,
      data_quality_log, infrastructure_locks, accuracy_log to service_role;

    create policy "anon read access" on signals for select to anon using (true);
    -- repeat this policy statement per public-readable table

Two things that will break this if skipped: Supabase's default does not
auto-grant broadly on new projects, so missing the service_role grant above
means the pipeline's own first write fails, not just the dashboard's reads.
And enabling Row Level Security with zero policies defined blocks all
access by default, including the access the GRANT statements just gave —
every public-readable table needs its own explicit CREATE POLICY, or the
failure looks like "Realtime and REST both return nothing," not an obvious
error pointing at RLS. No soft deletes and no DELETE verb anywhere in
application code: a signal generated in error remains permanently as a
historical record, with data_quality_log flagging bad data instead; only a
monthly archival script is ever permitted to move data out of the live
database, and this rule governs AXIS's own tables specifically — it does
not extend to Cognee's own forget() operation, a distinct, deliberately
manual action never called from live-cycle code.

13. The File Tree

    axis_remastered/
      .env  .gitignore  requirements.txt
      AXIS_MASTER_SPEC.md      (feed this whole file as permanent context to
                                 every tool touching architecture — never
                                 re-paste sections piecemeal)
      main.py                  (local entry point; python main.py runs one cycle)

      src/
        config/settings.py
        data/dhan_client.py nse_fetcher.py event_calendar.py instrument_resolver.py
        math/pricing.py         (Black-Scholes; EV; Kelly as f* = p - q/b, exactly)
        scoring/                (zero LLM calls anywhere in this folder --
                                  never call anything here an "agent")
          layer_a.py  layer_b.py  layer_c.py  direction_scorer.py  structure_gate.py
        graph/state.py nodes.py graph.py     (the only place an LLM is ever called)
        strategies/base.py gvof.py wyckoff_mean_reversion.py failed_breakout.py
                   continuation_buec.py failed_reversion.py
        llm/router.py json_extractor.py distributed_lock.py
        memory/ingest.py recall.py     (Gemini as Cognee's internal provider;
                                         local backend through Phase 9)
        journal/position_sizer.py outcome_recorder.py accuracy_engine.py
        delivery/telegram_formatter.py alert_builder.py
        scheduling/calendar_gate.py lock_manager.py
        observability/correlation.py
        backtest/backtest_runner.py

      migrations/001_core_schema.sql ... 008_infrastructure_locks.sql
                                     (applied to remote Supabase regardless
                                      of where compute runs)

      data/
        knowledge/  (8 files, per Section 10)
        examples/   (june16.txt ... june30.txt, 7 files)
        prompts/    (analyst_v1.md  verifier_v1.md)

      tests/
        test_pricing.py test_direction_scorer.py test_gvof_strategy.py
        test_cognee_recall.py test_ev_calculator.py test_json_extractor.py
        test_full_pipeline.py

      # BUILD LATER -- Phase 10 only, not scaffolded today:
      # .github/workflows/  dashboard/  netlify/functions/

Naming discipline for whichever tool builds these files: src/scoring/ is
pure Python, zero LLM calls, zero exceptions — the seven-files-of-math
framing used in earlier tool-assignment passes maps onto this folder exactly
per Section 0's table; do not let a coding tool recreate a separate
src/agents/ folder for this content.

14. The Build Sequence — Local-First, Each Phase Gated

Model assignment discipline, carried forward: Phase 1's knowledge curation
is a frontier-model job (Gemini or Claude, never a local 7B model, since
paraphrase-drift on exact numbers would corrupt the one thing every
downstream component validates against). Correctness-critical files
throughout — the LangGraph state contract, the distributed-lock interface,
EV and Kelly math, anything touching money — also go to a frontier model.
Boilerplate client wrappers and straightforward CRUD are fine for a local
model; escalate any resulting bug straight to a frontier model rather than
debugging a small local model's own mistakes with that same small model.

Phase 1 — knowledge files. All eight knowledge files and seven example
files, with every Section 0 correction written in explicitly, not just
implied.

Phase 2 — data foundation, local. nse_fetcher.py, dhan_client.py (token
regenerated by hand each session for now), math/pricing.py unit-tested
against hand-calculated values immediately, with zero network dependency.

Phase 3 — the Direction Scorer and Structure Gate, in src/scoring/, hand-
validated against all seven sessions. June 22 must not score bullish; June
23 must score strongly bearish with the cascade formulas reproducing their
historical accuracy; June 29 must score strongly bearish with every layer
agreeing; June 30 must detect the three-stage sweep. This is the one
component fully verifiable with zero external dependencies and zero LLM
cost — nothing proceeds until all seven pass.

Phase 4 — the knowledge layer. Cognee on its local default backend, Gemini
as its internal provider per Section 10. Test recall() against known-answer
questions using all eight real, populated files. Confirm the Gemini-403 and
Groq-tool_use_failed issues are genuinely resolved with one clean
remember() to recall() round trip before calling this phase done.

Phase 5 — the model layer and the lock interface, local. One trivial call
each to Gemini, Z.ai, and Groq, confirming keys and the fallback chain. Build
the small lock interface (acquire/release) backed by asyncio.Lock() for now.
Async is already decided per Section 8.5 — nothing left open here.

Phase 6 — the LangGraph skeleton, local, no real AI calls. Dummy nodes
proving the dict-merge behavior with a deliberately-missing-field test case;
confirm BLOCK terminates cleanly and PROCEED routes onward correctly.

Phase 7 — real agents, real knowledge retrieval, mocked market data. Confirm
GVOF is checked first, given its evidence base. Confirm Agent One classifies
all seven sessions correctly. Confirm Agent Two correctly BLOCKs June 22 and
correctly PROCEEDs on June 23 — and confirm this decision keeps working even
if the AI narrative call is deliberately made to fail, proving the decision
that matters never depends on a network call succeeding.

Phase 8 — the Option Chain Selector and Risk Manager, sample chain data, no
live calls yet. Confirm Delta-band filtering excludes the correct strikes;
confirm the 2%, weekly-limit, and proportional-6%-stop calculations are
exactly right.

Phase 9 — complete local integration. Every piece wired into main.py, run
end-to-end against all seven sessions with real knowledge retrieval this
time, not mocked. Confirm correlation_id threads correctly across every
journal table for a single simulated cycle. This is the last phase that
lives entirely on your own machine.

Phase 9.5 — deployment prep, the one deliberate pause before going
unattended. Run the Cognee Postgres-persistence test (very likely to just
work, per Section 10). Run a direct Dhan read-endpoint test from an actual
GitHub Actions workflow, purely as a sanity check — Section 0 has already
resolved that static IP doesn't apply to read endpoints regardless of the
outcome. Swap distributed_lock.py's implementation to the Postgres-backed
version from Section 7.3, same function signature. Wire the RenewToken/
generateAccessToken automation from Section 9.

Phase 10 — paper trading, live, cloud. .github/workflows/, dashboard/, and
netlify/functions/ are scaffolded only now, not before. A dead-man's-switch
(a Netlify function querying cycle_summaries grouped by symbol, returning
503 if either symbol's last row exceeds a 40-minute staleness threshold —
wide enough to absorb normal GitHub Actions cron drift without false-
alarming on ordinary delay), a keepalive workflow (GitHub disables scheduled
workflows after 60 days of no repository activity), and the system_paused
kill switch must all be live before scheduled runs start. GVOF receives the
largest initial virtual_portfolios allocation given its evidence base; the
four Wyckoff strategies start smaller. BankNifty enters shadow mode —
scored and logged exactly as normal, but with telegram_dispatch explicitly
suppressed — until it clears all four of: a minimum of 45 consecutive active
sessions spanning at least two monthly expiry cycles; a Profit Factor above
1.5 and a win rate above 55%; a Maximum Drawdown at or below 2% of its
allocated virtual capital; and a manual fill-realism audit cross-referencing
a sample of its logged entry and exit timestamps against raw Dhan tick data,
confirming the candle-close assumption wasn't hiding a zero-slippage
illusion. After 50 paper signals across both symbols, run the first real
Lasso regression and compute the first honest Kelly fractions from real
accuracy data.

Phase 11 — backtest expansion beyond the seven examples, reusing the
identical graph against a larger amount of historical data with spoofed
timestamps. If this replay calls live LLMs, treat any LLM-dependent metric
with more skepticism than the purely mechanical layers — a modern model's
general knowledge of what actually happened after this period can
contaminate its pattern classification even when fed only point-in-time
data; prefer a cheaper statistical proxy at scale, reserving real LLM calls
for a small spot-check set.

Phase 12 — the live-deployment gate, two conditions kept explicitly
distinct. The technical readiness gate — a sample size large enough for
confidence intervals to mean something, roughly six months of paper data,
with consistent positive EV realization across that period, per strategy and
per symbol — is what actually protects capital and should trigger
deployment on its own terms. BankNifty requires its own separately-
accumulated evidence before this gate opens for it, independent of NIFTY's
readiness. Any personally meaningful timing consideration is a separate,
legitimate constraint layered on top, never blurred into the technical one.

15. Retention and Storage

Supabase's free tier caps at 500MB. candles and cached_candles are compact
numeric rows and won't be the pressure point — kilobytes a year at five-
minute granularity across two symbols. ai_agent_opinions is the more likely
table to approach the ceiling first, since it stores raw LLM text verbatim
per call, easily 1–2KB per row, accumulating every cycle that reaches the
agents. Measure real row sizes once a few weeks of live data exist rather
than assuming which table hits the limit first. A monthly archival workflow —
rows older than six months exported to Cloudflare R2, free tier, no egress
fees, then deleted from Supabase, with row counts logged — becomes relevant
once real volume actually approaches the limit, not before.

16. Testing Strategy

Unit tests — EV math, the Kelly fraction (asserted against the corrected
f* = p − q/b formula specifically, not the version missing division by b),
the proportional 6%-of-IB stop formula, the JSON extractor across fenced,
plain-fenced, and unfenced input, position sizing — all using exact numbers
from the seven real sessions as literal fixtures. The timezone test forces
the runner's environment to UTC and confirms is_market_open and the
15:30-IST-anchored years_to_expiry still compute correctly. The concurrency
test simulates near-simultaneous invocations against the lock interface,
confirming exactly one proceeds while the other backs off cleanly. The
seven-session historical replay runs every component — Direction Scorer,
Structure Gate, GVOF's own checklist, both agent stages, the EV Verifier —
end to end against every real dated example, asserting the documented
correct output for each, including the hard requirement that June 22 never
produces a bullish composite score.

17. Glossary

GEX — Gamma Exposure, the dollar hedging flow dealers need per 1% move in
the underlying, the master regime switch this system reads first. CHoCH —
Change of Character, a structural signal the prevailing short-term trend
just reversed. BOS — Break of Structure. VPOC — Volume Point of Control.
VAH/VAL — Value Area High/Low. LVN/HVN — Low/High Volume Node. IB — Initial
Balance, the 9:15–10:35 AM range. EQH/EQL — Equal Highs/Lows. EV — Expected
Value. Kelly — f* = p − q/b, used at half strength, capped by the flat 2%
rule, whichever is smaller. R:R — reward-to-risk ratio. HAPI — reasoning
shifting from analytical to hope-based without new objective data is an
exit signal. WIDIN — "Would I Do It Now": if the honest answer to
re-entering this exact position fresh is no, exit. STT — Securities
Transaction Tax, differing between regular square-off and ITM exercise.
GVOF — this project's own strategy (GEX/VIX/OI-walls/Fibonacci), the most
empirically validated of the five registered strategies.

18. What's Still Genuinely Open

Whether Cognee's internal LLM step, now pointed at Gemini, needs any
additional configuration beyond LLM_PROVIDER/LLM_API_KEY for the specific
installed package version — verify directly in Phase 4, don't assume.
Cognee's Postgres persistence — very likely to work per Section 10, but not
yet tested; deferred to Phase 9.5 by design. Groq's exact current free-tier
RPD/TPM for openai/gpt-oss-120b, confirmed directly rather than assumed
carried over from the deprecated llama-3.3-70b-versatile. Z.ai's GLM-4.7-
Flash/GLM-4.5-Flash concurrent-request headroom under realistic load — free
and confirmed in principle, not yet load-tested. The GEX-Fibonacci-style
extension formula's validity beyond one dated example — ships disabled
regardless of the outcome. PCR-divergence's second confirming session —
still one-session-validated; do not weight it numerically until a second
session clears 0.5–0.7.

Everything else in this document is a decision, not a question.

AXIS — Tech Stack, File Index, and Formula Reference

Companion to AXIS_MASTER_SPEC.md, not a replacement. That file explains why
each decision was made; this one is for looking things up while your hands
are on the keyboard — what's in the stack, what each file does, what it
imports, what imports it, and the exact formula behind every number the
system produces.

1. THE TECH STACK

Layer            | Tool / Service                  | Role                                          | Cost
-----------------|----------------------------------|------------------------------------------------|------
Language          | Python 3.11+                    | Everything except the dashboard                | Free
Local dev IDE     | VS Code + Continue.dev + Ollama  | Boilerplate/CRUD generation, local model        | Free
                  | (Qwen 2.5 Coder 7B)              |                                                  |
Cross-file coding | Cursor (Claude 3.5 Sonnet)       | LangGraph wiring, anything touching 3+ files    | Paid tier
Infra/SQL coding  | Lovable                          | Migration files, RLS policies, serverless fns   | Free tier
Architecture/debug| Antigravity (Gemini/Claude)      | Knowledge curation, correctness-critical code,  | Free tier
                  |                                  | debugging platform-level failures               |
Orchestration     | LangGraph                        | State machine across scoring -> agents -> alert | Free (library)
LLM routing       | LiteLLM                          | Single interface over Gemini/Z.ai/Groq/Claude   | Free (library)
Agent One model   | Gemini Flash (primary),          | Knowledge Interpreter -- classification         | Free tier
                  | Z.ai GLM-4.7-Flash (fallback)    |                                                  | Free, no expiry
Agent Two model   | Groq openai/gpt-oss-120b         | EV Verifier's optional narrative text only      | Free tier
Premium option    | Anthropic Claude                 | Config-driven upgrade, never default            | Metered/paid
Knowledge graph   | Cognee                           | remember()/recall()/forget() over the 8 KB files| Free (library)
Cognee backend    | Kuzu (local, Phase 1-9)          | Local file-store graph persistence              | Free
                  | -> Postgres/pgvector (Phase 9.5+)| Survives ephemeral cloud containers             | Free (Supabase)
Cognee's own LLM  | Gemini                           | Its internal embedding + structured extraction  | Free tier
Database          | Supabase (Postgres)              | Every table in Section 12 of the master spec    | Free tier, 500MB
Market data       | NSE option-chain endpoint         | Layer A: GEX, PCR, Max Pain source data         | Free, session-based
                  | NSE participant-OI archive        | Layer B: FII long/short data                    | Free, no login
                  | Dhan API (v2)                     | 5-min candles, instrument master                | Free w/ trading acct
Alerts            | Telegram Bot API                  | The one output that matters                    | Free
Scheduling (later)| GitHub Actions                    | 5-min cron, Phase 10 onward only               | Free (public repo)
Dashboard (later) | Netlify + Supabase Realtime       | Static site, live signal feed, Phase 10 onward | Free tier
Watchdog (later)  | UptimeRobot                       | External health check, Phase 10 onward         | Free tier

2. FILE-BY-FILE REFERENCE

Format per file: what it does -> key functions/classes -> imports -> used by.

--- config/ ---

settings.py
  Does: loads and validates every credential and threshold from .env; fails
  loudly at startup if anything required is missing or malformed.
  Key: class Settings (Pydantic BaseSettings); validate_for(*keys).
  Imports: python-dotenv or pydantic-settings only.
  Used by: every other file in the codebase, indirectly, via `from config.settings import settings`.

--- data/ ---

nse_fetcher.py
  Does: session-warmed fetch of NSE's free option-chain JSON and the nightly
  participant-OI CSV.
  Key: fetch_option_chain(symbol) -> dict; fetch_participant_oi(date) -> str;
  compute_long_short_ratio(csv_text) -> dict.
  Imports: requests, config.settings.
  Used by: scoring/layer_a.py (option chain), scoring/layer_b.py (FII CSV).

dhan_client.py
  Does: authenticated wrapper around Dhan's v2 API -- candles, option chain
  Greeks, instrument master, token refresh.
  Key: get_candles(symbol, interval) -> list[dict]; get_option_chain(symbol,
  expiry) -> dict; renew_token() -> str; generate_access_token(pin, totp) -> str.
  Imports: requests or dhanhq SDK, pyotp, config.settings.
  Used by: scoring/layer_c.py (candles), math/pricing.py callers needing live
  Greeks, data/instrument_resolver.py.

event_calendar.py
  Does: daily-refreshed calendar of RBI/Budget/FOMC/expiry/CPI/NFP dates and
  their proximity-penalty points; walks backward across weekends/holidays
  for "the previous trading day."
  Key: days_to_next_event() -> int; is_event_proximity_window() -> bool;
  previous_trading_day(date) -> date.
  Imports: config.settings.
  Used by: scoring/direction_scorer.py (event override), data/nse_fetcher.py
  (T+1 FII date walk-back).

instrument_resolver.py
  Does: maps symbol+strike+expiry+option_type to Dhan's internal security ID,
  refreshed once daily pre-market.
  Key: resolve(symbol, strike, expiry, option_type) -> int (raises
  InstrumentNotFoundError / AmbiguousInstrumentError).
  Imports: data.dhan_client.
  Used by: scoring/layer_c.py, strategies/*.py (any file needing a live quote).

--- math/ ---

pricing.py  (already written and tested -- see pricing.py in this project's outputs)
  Does: every formula in Section 3 below. Zero network calls, pure functions.
  Key: bs_price, bs_delta, bs_gamma, bs_theta_per_day, bs_vega, theta_between,
  years_to_expiry, net_gex, gamma_flip_level, max_pain, pcr, vix_expected_move,
  down_target, cascade_magnitude, transaction_cost, expected_value,
  kelly_fraction.
  Imports: math, dataclasses, datetime, zoneinfo -- standard library only.
  Used by: scoring/layer_a.py, options selector logic in graph/nodes.py,
  journal/accuracy_engine.py, graph/nodes.py's verifier_node.

--- scoring/ (zero LLM calls anywhere in this folder) ---

layer_a.py
  Does: GEX sign/magnitude, Gamma Flip Level, VIX structure, PCR (current +
  all-expiry), PCR-divergence, Max Pain, OI build %, the 5-signal expiry score.
  Key: score_layer_a(chain_data, vix_data) -> LayerAScore.
  Imports: math.pricing, data.nse_fetcher.
  Used by: scoring/direction_scorer.py.

layer_b.py
  Does: FII index-futures/calls/puts long-short ratio, T+1-dated.
  Key: score_layer_b(fii_data) -> LayerBScore.
  Imports: data.nse_fetcher, data.event_calendar.
  Used by: scoring/direction_scorer.py.

layer_c.py
  Does: VAH/VAL/VPOC from cached_candles, OI-vs-LTP divergence signature,
  boundary-proximity check (the hard gate, computed before scoring).
  Key: score_layer_c(candles, chain_data) -> LayerCScore (includes
  at_vp_boundary: bool).
  Imports: data.dhan_client, data.nse_fetcher.
  Used by: scoring/direction_scorer.py.

direction_scorer.py
  Does: combines the three layer scores via scoring_config weights, applies
  the four hard overrides (GEX flip zone, 5-signal cascade, event proximity,
  expiry-morning do-not-trade window).
  Key: compute_direction_score(layer_a, layer_b, layer_c, context) -> int (1-5).
  Imports: scoring.layer_a/b/c, config.settings.
  Used by: graph/nodes.py's direction_scorer node.

structure_gate.py
  Does: binary yes/no on Wyckoff phase consistency, three-step turn, VP
  boundary requirement, VPOC migration, range slope.
  Key: check_structure(candles, chain_data) -> bool.
  Imports: scoring.layer_c (boundary data), math.pricing.
  Used by: graph/nodes.py's structure_gate node.

--- graph/ (the only folder where an LLM is ever called) ---

state.py
  Does: the Pydantic AxisState contract -- every late-populated field
  Optional[...] = None.
  Key: class AxisState(BaseModel).
  Imports: pydantic.
  Used by: every file in graph/, every strategy's check_conditions signature.

nodes.py
  Does: every graph node -- data_verification_node, direction_scorer node,
  structure_gate node, strategy_activation node, analyst_node, verifier_node,
  option_selector node, risk_check node, dedup_node, telegram_dispatch node.
  Every node returns dict, never the full state object.
  Key: async def <node_name>(state: AxisState) -> dict, one per node.
  Imports: scoring.*, strategies.*, llm.router, llm.json_extractor,
  math.pricing, journal.*, delivery.*, graph.state.
  Used by: graph/graph.py.

graph.py
  Does: StateGraph wiring -- the exact edge sequence from Section 8.4 of the
  master spec, the BLOCK-is-terminal / PROCEED-continues conditional routing.
  Key: build_graph() -> CompiledGraph.
  Imports: langgraph, graph.state, graph.nodes.
  Used by: main.py.

--- strategies/ ---

base.py
  Does: the abstract base every strategy inherits.
  Key: class BaseStrategy(ABC): check_conditions(state) -> dict.
  Imports: abc.
  Used by: every file below, and graph/nodes.py's strategy_activation node,
  which iterates a registered list of these.

gvof.py
  Does: Strategy 1, the reinstated, most-validated strategy -- regime check,
  D-1 macro check, IB formation (9:15-10:35), golden zone, expiry-day Judas
  Swing variant, sweep+CHoCH entry, proportional stop, T1/T2 targets, time
  discipline.
  Key: class GVOFStrategy(BaseStrategy).
  Imports: strategies.base, math.pricing, config.constants.
  Used by: registered in settings.py's strategy list.

wyckoff_mean_reversion.py / failed_breakout.py / continuation_buec.py /
failed_reversion.py
  Does: the four generic Wyckoff execution blueprints, Strategies 2-5.
  Key: class <Name>Strategy(BaseStrategy) each.
  Imports: strategies.base, scoring.layer_c (VP boundary data).
  Used by: registered in settings.py's strategy list.

--- llm/ ---

router.py
  Does: the LiteLLM role-based router -- analyst role (Gemini primary, Z.ai
  fallback), verifier role (Groq, plain narrative only). num_retries=0,
  stream=False on every call.
  Key: async def call_llm_router(role: str, state: AxisState) -> str.
  Imports: litellm, llm.distributed_lock, config.settings.
  Used by: graph/nodes.py's analyst_node and verifier_node.

json_extractor.py
  Does: strips markdown fences, isolates the outermost {...}, retries with
  trailing-comma cleanup on parse failure. (Full code in Section 8.6 of the
  master spec.)
  Key: extract_json(raw: str) -> dict.
  Imports: json, re -- standard library only.
  Used by: llm/router.py's response handling.

distributed_lock.py
  Does: acquire/release interface, backed by asyncio.Lock() through Phase 9,
  swapped for the Postgres-backed infrastructure_locks table at Phase 9.5
  with no change to callers.
  Key: async def acquire(lock_id, ttl_seconds) -> bool; async def release(lock_id) -> None.
  Imports: asyncio (Phase 1-9); supabase-py (Phase 9.5+).
  Used by: llm/router.py before Z.ai/Groq calls.

--- memory/ ---

ingest.py
  Does: manual, run-when-content-changes script that calls cognee.remember()
  once per knowledge-file chunk.
  Key: run_ingestion() -- CLI entry point, not called from live-cycle code.
  Imports: cognee.
  Used by: run directly, `python memory/ingest.py`, never imported elsewhere.

recall.py
  Does: the live query function -- the only thing analyst_node ever calls
  into this folder.
  Key: async def query_knowledge(question: str) -> list[str] (capped at 3).
  Imports: cognee.
  Used by: graph/nodes.py's analyst_node.

--- journal/ ---

position_sizer.py
  Does: the one place sizing math lives -- 2% capital rule, half-Kelly once
  N>=30-50 trades, proportional 6%-of-IB stop for GVOF specifically.
  Key: calculate_position(strategy, symbol, entry, stop, lot_size) ->
  {lots, capital_deployed, risk_rupees} (raises InsufficientCapitalError).
  Imports: math.pricing, config.constants.
  Used by: graph/nodes.py's risk_check / position_sizing node.

outcome_recorder.py
  Does: writes trade_outcomes rows -- 15/30/60/120-minute post-exit price
  samples, VIX-move classification tag, loss-taxonomy tag on losses.
  Key: record_outcome(paper_trade_id) -- scheduled/triggered post-exit.
  Imports: data.dhan_client, math.pricing (VIX classifier logic).
  Used by: main.py's Phase 2 (active trade management loop).

accuracy_engine.py
  Does: bucketed historical win-rate/EV lookups (discrete keys only --
  direction-score bin, structure-gate bool, strategy name, VIX class), the
  n>=15-20 sample floor, the biweekly Lasso reweighting, the 95% CI
  calculation with z=1.96.
  Key: get_historical_stats(bucket_key) -> {win_rate, avg_gain, avg_loss,
  sample_count} or None if below the floor.
  Imports: math.pricing, supabase-py.
  Used by: graph/nodes.py's verifier_node.

--- delivery/ ---

telegram_formatter.py  (already written and tested -- see telegram_formatter.py in outputs)
  Does: MarkdownV2 sanitization, safe send with plain-text fallback.
  Key: sanitize_telegram_md(text) -> str; send_telegram_alert(bot_token,
  chat_id, text) -> bool.
  Imports: requests.
  Used by: delivery/alert_builder.py.

alert_builder.py
  Does: assembles the complete 7-section Telegram message from every
  component's output (session context, signal conditions, order flow, EV,
  options intelligence, trade parameters, verdict).
  Key: build_alert(state: AxisState) -> str.
  Imports: delivery.telegram_formatter, graph.state.
  Used by: graph/nodes.py's telegram_dispatch node.

--- scheduling/ ---

calendar_gate.py
  Does: is_market_open() -- the literal first check in main.py.
  Key: is_market_open(now: datetime) -> bool.
  Imports: data.event_calendar, zoneinfo.
  Used by: main.py, graph/graph.py's calendar_gate node.

lock_manager.py
  Does: run_locks acquire/release (the per-cycle execution lock, distinct
  from llm/distributed_lock.py's API-call lock).
  Key: acquire_run_lock(symbol) -> bool; release_run_lock(symbol) -> None.
  Imports: supabase-py.
  Used by: main.py, graph/graph.py's lock_acquire node.

--- observability/ ---

correlation.py
  Does: generates and threads one correlation_id through every table a
  single cycle touches, for end-to-end traceability.
  Key: new_correlation_id() -> str.
  Imports: uuid.
  Used by: main.py at the start of every cycle; every node reads it off state.

--- backtest/ ---

backtest_runner.py
  Does: Phase 11's tool -- reuses the identical graph against a larger
  historical dataset with spoofed timestamps.
  Key: run_backtest(start_date, end_date, use_live_llm: bool = False).
  Imports: graph.graph, everything else transitively.
  Used by: run directly for Phase 11, not imported elsewhere.

--- root ---

main.py
  Does: the local entry point (python main.py runs one cycle) and, from
  Phase 9.5 onward, the same code GitHub Actions triggers on a cron. Runs
  two phases every invocation: Phase 1 generates new signals through the
  graph; Phase 2 checks every open paper trade against the current 5-min
  candle close.
  Key: async def run_cycle(symbol: str); if __name__ == "__main__": asyncio.run(...).
  Imports: graph.graph, scheduling.calendar_gate, scheduling.lock_manager,
  observability.correlation, journal.outcome_recorder.
  Used by: nothing -- this is the top of the call stack.

3. FORMULA REFERENCE (all implemented and tested in math/pricing.py)

Black-Scholes theoretical price (d1/d2 standard form):
  d1 = (ln(S/K) + (r + 0.5*sigma^2)*T) / (sigma*sqrt(T))
  d2 = d1 - sigma*sqrt(T)
  Call = S*N(d1) - K*e^(-rT)*N(d2)
  Put  = K*e^(-rT)*N(-d2) - S*N(-d1)
  Function: bs_price(spot, strike, r, sigma, t, option_type)

Delta:
  Call: N(d1)   Put: N(d1) - 1
  Function: bs_delta(...)

Gamma (identical for calls and puts -- this is what GEX is built from):
  Gamma = N'(d1) / (S*sigma*sqrt(T))
  Function: bs_gamma(...)

Theta (annualized, converted to per-day by dividing by 365):
  Call: -[S*N'(d1)*sigma/(2*sqrt(T))] - r*K*e^(-rT)*N(d2)
  Put:  -[S*N'(d1)*sigma/(2*sqrt(T))] + r*K*e^(-rT)*N(-d2)
  Function: bs_theta_per_day(...); for the real, non-linear per-hour decay
  used in the 1:30-2:30 PM warning, use theta_between(t_now, t_later) instead
  of dividing the daily figure by hours.

Vega (rupees per 1 percentage point of IV):
  Vega = S*N'(d1)*sqrt(T) / 100
  Function: bs_vega(...)

Time to expiry, anchored correctly:
  years_to_expiry = max((expiry_datetime_at_15:30_IST - now).total_seconds(), 1) / (365*24*3600)
  Function: years_to_expiry(expiry_date, now, expiry_time=15:30 default)
  Never compute this from midnight -- see Section 0/9 of the master spec.

Net GEX (dollar hedge flow per 1% move):
  Net GEX = sum over strikes[ (call_gamma*call_OI - put_gamma*put_OI) * lot_size * spot^2 * 0.01 ]
  Function: net_gex(chain, spot, r, t)

Gamma Flip Level:
  The spot price where net_gex(chain, hypothetical_spot, r, t), recomputed
  across a range of hypothetical spots, crosses zero.
  Function: gamma_flip_level(chain, spot, r, t, search_pct=0.05)

Max Pain:
  The strike minimizing sum over strikes[ max(candidate-strike,0)*call_OI +
  max(strike-candidate,0)*put_OI ]
  Function: max_pain(chain)

PCR:
  total_put_OI / total_call_OI
  Function: pcr(chain)

VIX expected move / Down Target:
  Expected move = Spot * (VIX/100) / sqrt(252)
  Down Target = Spot - Expected move
  Functions: vix_expected_move(spot, vix); down_target(spot, vix)

Cascade magnitude (first-order estimate, unverified beyond one example):
  Cascade = abs(Net GEX) * move_pct
  Function: cascade_magnitude(net_gex_value, move_pct)

Transaction cost (per trade, not a flat estimate):
  STT = 0.0625% * sell_premium_value
  Cost = STT + brokerage(~40) + exchange(~35) + 18%*brokerage (GST)
  Function: transaction_cost(sell_premium_value, brokerage=40, exchange_charges=35, gst_rate=0.18)

Expected Value:
  EV = win_prob*avg_gain - (1-win_prob)*avg_loss - transaction_cost
  Function: expected_value(win_prob, avg_gain, avg_loss, est_transaction_cost)

Kelly fraction (corrected form -- confirmed matching in pricing.py already):
  f* = p - q/b,  where q = 1-p,  b = avg_gain/avg_loss
  Half-Kelly = f*/2, capped by the flat 2% rule, whichever is smaller.
  Function: kelly_fraction(win_prob, avg_gain, avg_loss)

Proportional stop-loss (GVOF-specific):
  stop_distance = 0.06 * IB_range   (IB_range = IB_HIGH - IB_LOW)
  Not yet a standalone function -- lives inside strategies/gvof.py's
  check_conditions, using IB_HIGH/IB_LOW from scoring/layer_c.py.

5-Signal Expiry Day Score (max 9):
  GEX<0: +3 | VIX at Weak Low: +2 | OI build>50%: +2 |
  PCR rising + GEX negative: +1 | VIX CHoCH/BOS up: +1
  >=5 -> cascade (Down Target formula) | 2-4 -> reduce size | <=1 -> sell premium

Position sizing (the table, not a formula -- see Section 6.4 of the master
spec for the exact capital/lots/risk/target rows).

4. RELATIONS -- THE CALL CHAIN IN ONE PASS

main.py
  -> scheduling/calendar_gate.py (is_market_open?)
  -> scheduling/lock_manager.py (acquire run_locks)
  -> graph/graph.py -> compiled LangGraph:
       data_verification_node (data/*, checks trust_status)
       -> scoring/layer_a.py, layer_b.py, layer_c.py (each uses math/pricing.py)
       -> scoring/direction_scorer.py (combines the three)
       -> scoring/structure_gate.py
       -> strategies/*.py (first BaseStrategy.check_conditions() that passes)
       -> analyst_node -> llm/router.py -> memory/recall.py (Cognee)
       -> verifier_node -> math/pricing.py (EV/Kelly) + journal/accuracy_engine.py
       -> [conditional: BLOCK -> log, end | PROCEED -> continue]
       -> option_selector (math/pricing.py theoretical value check)
       -> risk_check / position_sizing -> journal/position_sizer.py
       -> dedup_node
       -> telegram_dispatch -> delivery/alert_builder.py -> telegram_formatter.py
  -> journal/outcome_recorder.py (Phase 2, every open paper_trade, every cycle)
  -> observability/correlation.py (correlation_id threaded through all of the above)

Nothing in scoring/ ever appears above an LLM call in this chain, and nothing
in graph/nodes.py's analyst_node or verifier_node ever appears in scoring/ --
that boundary is the whole point of Section 0's naming fix.
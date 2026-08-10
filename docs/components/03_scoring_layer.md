# Component 03 — Scoring Layer

## 1. What This Component Is For (plain language, 2-3 sentences)
Takes option-chain and five-minute candle inputs and converts them into deterministic directional signals via three layered scorers (Layer A: GEX/VIX/PCR; Layer B: intermediate signals; Layer C: five-minute volume-profile divergence). The direction_scorer aggregates the layers with configurable weights and boundary-aware weighting logic to produce the final integer direction score used downstream.

## 2. Files in This Component
- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/scoring/layer_a.py (165 lines)
  - One-line purpose: Compute Layer A features from option-chain rows (GEX, gamma_flip, max_pain, PCR, expiry score, direction_value).
  - Key functions/classes:
    - LayerAScore dataclass — structured returned object
    - score_layer_a(chain_data, vix_data) -> LayerAScore — computes gex via net_gex(rows, spot, rate, t, lot_size) or uses chain_payload['net_gex'] if present
    - Exact direction rules (copied verbatim):
      - direction = -1.0 if gex < 0 else 0.35 if gex > 0 else 0.0
      - if gex < 0 and pcr_rising: direction = -1.0
      - elif gex > 0 and pcr_rising: direction = min(1.0, direction + 0.25)
      - if vix_structure.lower().replace("_", "-") in {"weak-low", "near-weak-low"} and vix_choch: direction = min(direction, -0.8)
  - STATUS: VERIFIED — evidence: read src/scoring/layer_a.py lines 116–146 and 148–163.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/scoring/direction_scorer.py (99 lines)
  - One-line purpose: Combine Layer A/B/C via ScoringConfig weights and boundary-aware substitution to yield final integer score 1–5.
  - Key functions/classes:
    - ScoringConfig.from_mapping(...) validates required weights and expiry_no_trade_minutes etc.
    - compute_direction_score(layer_a, layer_b, layer_c, context) implements weight sum and returns max(1,min(5, round(3 + 2 * combined))) where combined is weighted average of layer direction_values.
    - Exact boundary-weight logic: c_weight = config.layer_c_weight if layer_c.at_vp_boundary else config.off_boundary_c_weight (used in weights tuple)
  - STATUS: VERIFIED — evidence: read src/scoring/direction_scorer.py lines 80–99 and 88–98.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/scoring/layer_c.py (109 lines)
  - One-line purpose: Compute five-minute volume profile (VAH, VAL, VPOC), detect LVNs, boundary tolerance, and compute divergence signature (oi vs ltp) producing at_vp_boundary and direction_value.
  - Key functions/classes:
    - LayerCScore dataclass
    - _volume_profile(candles) -> (vah,val,vpoc,lvns) implements bucketed profile and selects prices covering 70% volume
    - score_layer_c(candles, chain_data) computes at_vp_boundary via tolerance = boundary_tolerance_pct * spot and finds best divergence
  - STATUS: VERIFIED — evidence: read src/scoring/layer_c.py lines 26–49 and 70–107.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/scoring/structure_gate.py (53 lines)
  - One-line purpose: Hard binary gate requiring phase/event/three_step_turn/profile-slope agreement and at_vp_boundary to accept structure.
  - Key functions/classes: check_structure(candles, chain_data) returns True/False after checking layer_c.at_vp_boundary and a sequence of explicit conditions.
  - STATUS: VERIFIED — evidence: read src/scoring/structure_gate.py lines 21–52.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/config/constants.py (33 lines)
  - One-line purpose: Holds numeric constants used by scoring/strategy code.
  - Key values: LOT_SIZES = {"NIFTY": 65, "BANKNIFTY": 30}
  - STATUS: VERIFIED — evidence: read constants file showing exact lot sizes (lines 5–6).

## 3. How It Actually Works (the real internal logic, step by step)
1. Input normalization: score_layer_a/_c accept either mapping envelopes or raw lists and use _payload helper to extract 'data' or treat given object as payload (see _payload implementations).
2. Layer A: score_layer_a computes rows from option chain, computes spot, rate, t (time-to-expiry), calls net_gex(rows, spot, rate, t, lot_size) if net_gex not supplied. It sets gex_regime and computes gamma_flip optionally. It then computes current_pcr and pcr_rising and an expiry_score via _expiry_score(). The final direction_value is set via the exact rules quoted above.
3. Layer C: score_layer_c builds a bucketed volume profile, computes VAH/VAL/VPOC covering 70% volume, computes LVN levels, checks at_vp_boundary via boundary_tolerance_pct * spot, and inspects chain rows for oi_change vs ltp_change signatures to set divergence and direction_value. If not at boundary, direction_value is forced to 0.0.
4. Direction combiner: compute_direction_score first constructs ScoringConfig from context mapping. It applies event proximity and expiry-open-window shortcuts, applies a flip zone guard (abs(layer_a.gex) <= gex_flip_zone_cr -> neutral 3), expiry_score>=5 -> strong bearish (1). Otherwise it computes c_weight based on layer_c.at_vp_boundary, aggregates weights, computes combined = weighted sum of direction_values / total, then returns round(3 + 2 * combined) clipped to [1,5].

Exact formulas / code copied verbatim where present were used above for the direction assignment and the final rounding formula: final = max(1, min(5, round(3 + 2 * combined))).

## 4. Connections — What This Depends On, What Depends On This
- Upstream: option-chain and five-minute candle payloads (data pipeline), config.scoring_config mapping in market_context
- Downstream: direction_score is consumed by graph nodes (src/graph/nodes.py) and strategy logic (src/strategies/*)
- External: No external LLMs or network calls are made inside src/scoring — scoring code is pure python math and local helpers.

## 5. Current Status — What's Actually Working vs. Not
sub-feature | status label | evidence
---|---|---
Layer A implementation and GEX-first ordering | VERIFIED | src/scoring/layer_a.py read and inspected
Layer C volume-profile logic and at_vp_boundary detection | VERIFIED | src/scoring/layer_c.py read and inspected
Direction combiner weight formula and boundary-weight switch | VERIFIED | src/scoring/direction_scorer.py (uses off_boundary_c_weight) inspected
Layer B presence | BUILT-NOT-RUN / PARTIAL | src/scoring/layer_b.py not found in scan (direction_scorer imports LayerBScore but file missing) — grep returned no layer_b.py in repo (no matches)
Zero LLM imports in scoring folder | VERIFIED | repo grep for LLM-related keywords under src/scoring returned no matches
Seven-session hand-validation test | BUILT-NOT-RUN | tests/test_direction_scorer.py exists but pytest collection/run was prevented by missing test deps in this workspace (see component 11)

## 6. What's Remaining, Specific to This Component Only
- Add or locate src/scoring/layer_b.py: direction_scorer imports LayerBScore but layer_b.py was not found in the scanned source — clarify where Layer B lives or restore it so the scorer can be executed end-to-end.
- Run the seven-session regression test in a fully provisioned environment and paste numeric pass/fail outputs into this file (required for downstream trust).

## 7. Last Verified
2026-07-26 — commit aabcce72ac767f99149bda30dac255721c784e3b

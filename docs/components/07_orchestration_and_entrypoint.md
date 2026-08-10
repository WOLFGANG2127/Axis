# Component 07 — Orchestration and Entrypoint

## 1. What This Component Is For (plain language, 2-3 sentences)
Wires the LangGraph state-machine and provides the CLI entrypoint to run single-symbol or multi-symbol cycles. Ensures the calendar, lock, verification, risk, dedup and Telegram dispatch nodes run in the precise sequence defined by the compiled graph.

## 2. Files in This Component
- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/graph/graph.py (58 lines)
  - One-line purpose: Build the StateGraph by adding nodes and edges (calendar→lock→data_verification→direction_scorer→structure_gate→strategy_activation→analyst→verifier→risk→dedup→telegram→END).
  - STATUS: VERIFIED — evidence: read build_graph() and edges (lines 24–54).

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/graph/nodes.py (455 lines)
  - One-line purpose: Implementation of each graph node as an async function that returns a partial dict of changed keys (not the full AxisState).
  - Key functions: calendar_gate_node, lock_acquire_node, data_verification_node, direction_scorer_node, structure_gate_node, strategy_activation_node, analyst_node, verifier_node, risk_check_node, dedup_node, telegram_dispatch_node.
  - STATUS: VERIFIED — evidence: node functions return dicts like {"calendar_open": opened} and {"direction_score": score} (see functions returning single-key dicts).

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/graph/state.py (38 lines)
  - One-line purpose: AxisState pydantic model with Optional[...] fields used by the graph; fields are Optional by design.
  - STATUS: VERIFIED — evidence: AxisState model fields declared Optional and model_config set.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/main.py (316 lines)
  - One-line purpose: CLI entrypoint, run_cycle and run_all_symbols_cycle orchestration with PRS/calendar/lock gates and multi-symbol fan-out and correlation handling.
  - STATUS: VERIFIED — evidence: main.py run_cycle and run_all_symbols_cycle functions read and inspected.

## 3. How It Actually Works (the real internal logic, step by step)
Call chain (exact as wired in build_graph, indented tree):

- START
  - calendar_gate (calendar_gate_node)  # returns {"calendar_open": bool}
    - lock_acquire (lock_acquire_node)  # returns {"lock_acquired": bool}
      - data_verification (data_verification_node)  # returns {"data_quality": {...}, "degraded_mode": bool}
        - direction_scorer (direction_scorer_node)  # returns {"direction_score": int}
          - structure_gate (structure_gate_node)  # returns {"structure_confirmed": bool}
            - strategy_activation (strategy_activation_node)  # returns {"active_strategy": dict | None}
              - analyst_node (analyst_node)  # returns {"analyst_opinion": dict | None}
                - verifier_node (verifier_node)  # returns {"verifier_verdict": dict}
                  - conditional: verifier_route(verifier_verdict) -> "BLOCK" => END; "PROCEED" => risk
                    - risk (risk_check_node)  # returns {"risk_approved": bool}
                      - dedup (dedup_node)  # returns {"dedup_status": str}
                        - telegram (telegram_dispatch_node)  # returns {"alert_sent": bool}
                          - END

Notes on behavior seen in code:
- Every node returns a dict with only the keys it sets/changes (e.g., calendar_gate_node returns {"calendar_open": opened}); nodes do not return the full AxisState object. STATUS: VERIFIED — evidence: node functions return small dicts (src/graph/nodes.py).
- AxisState fields are Optional[...] in the pydantic model (src/graph/state.py), confirming the "later node populates Optional fields" design. STATUS: VERIFIED.
- Multi-strategy fan-out vs single-strategy design: main.py implements run_all_symbols_cycle that sequentially runs both VALID_SYMBOLS (NIFTY then BANKNIFTY) inside one process, collects results, then applies apply_same_cycle_correlation(results) which can modify candidate lots (haircut). Thus the execution shape is multi-symbol aware and includes same-cycle correlation. STATUS: VERIFIED — evidence: main.py lines 246–295 and apply_same_cycle_correlation.

## 4. Connections — What This Depends On, What Depends On This
- Upstream: calendar and lock manager (src/scheduling) to permit execution; get_supabase_client to read DB-driven gates.
- Downstream: The active_strategy/verifier verdict flows into risk/dedup/telegram nodes and ultimately into send_telegram_alert and DB inserts (macro_regime_flags, paper_trades, trade_outcomes).
- External dependencies: langgraph StateGraph class used at build_graph compile time.

## 5. Current Status — What's Actually Working vs. Not
sub-feature | status label | evidence
---|---|---
LangGraph wiring and node order | VERIFIED | src/graph/graph.py shows exact nodes and edges
Nodes return only partial dicts, not full state | VERIFIED | node functions return small dicts (e.g., {"direction_score": score}) in src/graph/nodes.py
AxisState fields Optional[...] interface | VERIFIED | src/graph/state.py Optional field declarations
Single-symbol vs multi-symbol execution shape | VERIFIED | main.py has run_cycle and run_all_symbols_cycle and apply_same_cycle_correlation logic
All later-node-populated fields declared Optional | VERIFIED | AxisState fields are Optional in pydantic model

## 6. What's Remaining, Specific to This Component Only
- Confirm that every node always returns only changed keys in practice (unit tests should assert no node returns full AxisState). Some tests exist (tests/test_axis_graph.py) but pytest collection failed in this workspace; see component 11 for test run status.

## 7. Last Verified
2026-07-26 — commit aabcce72ac767f99149bda30dac255721c784e3b

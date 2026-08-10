# Component 04 — Strategy Layer

## 1. What This Component Is For (plain language, 2-3 sentences)
Encapsulates deterministic strategy checklists that read AxisState and market_context and return a small dict with at least ``passed`` and identifying fields. The registry loads active strategies from the database and the graph activation node iterates registered strategies to find the first passing one.

## 2. Files in This Component
- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/strategies/base.py (16 lines)
  - One-line purpose: Abstract BaseStrategy contract requiring check_conditions(self, state: AxisState) -> dict
  - Key classes: BaseStrategy with abstract method check_conditions
  - STATUS: VERIFIED — evidence: read src/strategies/base.py

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/strategies/gvof.py (231 lines)
  - One-line purpose: GVOF strategy implementation (Golden Zone + Volume Profile + Order Flow), uses many constants from src/config/constants and enforces time and structure checks.
  - Key functions/classes: GVOFStrategy.check_conditions(state) performs IB initial balance detection, direction resolution, expiry variants, entry/stop/target computation, cascade handling for negative GEX.
  - STATUS: VERIFIED — evidence: read src/strategies/gvof.py lines including constants usage and gating logic.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/strategies/registry.py (45 lines)
  - One-line purpose: Load active strategies from DB (strategies table where status='active'), import module src.strategies.{strategy_id} and instantiate class {CapitalizeParts}Strategy.
  - Key functions/classes: load_strategy_registry(force=False, db=None) -> StrategyRegistrySnapshot; reset_strategy_registry_cache()
  - STATUS: VERIFIED — evidence: read src/strategies/registry.py that queries db.table('strategies').select('*').eq('status','active').execute()

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/strategies/wyckoff_mean_reversion.py (157 lines)
  - One-line purpose: Concrete Wyckoff Mean Reversion strategy implementation that returns full passed dict with entry, stop_loss, targets, and metadata (volume/order flow checks).
  - STATUS: VERIFIED — evidence: read file showing WyckoffMeanReversionStrategy.check_conditions returns passed True with strategy fields.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/migrations/022_seed_wyckoff_mean_reversion_strategy.sql (seed)
  - One-line purpose: Inserts 'wyckoff_mean_reversion' into strategies with status 'active' and writes strategy_configs for NIFTY/BANKNIFTY
  - STATUS: VERIFIED — evidence: migration file contains INSERT INTO strategies ... status 'active'

## 3. How It Actually Works (the real internal logic, step by step)
1. Strategy registry (load_strategy_registry) queries the strategies table for rows where status='active'. For each strategy_id row it does: importlib.import_module(f'src.strategies.{sid}') and instantiate the class {SidCapitalized}Strategy() — requiring the module to exist and the class to inherit BaseStrategy.
2. The graph's strategy_activation_node (src/graph/nodes.py) iterates STRATEGIES (module-level list defaulting to [GVOFStrategy()]) or the registry-loaded snapshot, calling strategy.check_conditions(state) and returning the first result where result.get('passed') is True as active_strategy.
3. Strategies are pure python checklists: they read AxisState.market_context, check structure_confirmed, scoring/direction, entry zone criteria, compute stop/targets, and return a compact dict describing the proposed trade or failure reason.

## 4. Connections — What This Depends On, What Depends On This
- Upstream: market_context fields (direction_score, structure_confirmed, candles, chain_data), constants from src/config/constants, strategy_configs from DB (registry loads them into configs snapshot), and Supabase for active strategy rows.
- Downstream: active_strategy dict is consumed by graph verifier_node, risk checks, dedup and eventual telegram alert builder (alert_builder uses strategy fields when composing messages).
- External dependencies: registry uses Supabase DB access; live registry state requires DB.

## 5. Current Status — What's Actually Working vs. Not
sub-feature | status label | evidence
---|---|---
BaseStrategy interface | VERIFIED | src/strategies/base.py
GVOF strategy implementation | VERIFIED | src/strategies/gvof.py inspected
Wyckoff Mean Reversion implementation file present | VERIFIED | src/strategies/wyckoff_mean_reversion.py
Strategy registry runtime loading from DB | VERIFIED (code exists) / UNABLE TO QUERY LIVE DB (runtime count) | src/strategies/registry.py queries DB for status='active' but this workspace cannot query live DB
Number of active strategies right now | UNABLE TO QUERY LIVE DB (Offline Workspace Scan) | registry requires a live Supabase client; not executed here
Original four Wyckoff stubs status | PARTIALLY PRESENT / CLAIMED-NOT-SHOWN | only wyckoff_mean_reversion exists and is seeded; other three planned Wyckoff stubs are not present in src/strategies directory (grep only found one)

## 6. What's Remaining, Specific to This Component Only
- Query the live registry (Supabase) to report the exact number of active strategies and their strategy_id list.
- Confirm that every registered strategy module implements BaseStrategy and that AST security-scan metadata referenced in migrations matches deployed registry (migration claims security scan passed for wyckoff seed — verify in deployment logs).
- If additional Wyckoff stubs are expected, add placeholder modules or update the seed/migrations to match the actual strategy modules present.

## 7. Last Verified
2026-07-26 — commit aabcce72ac767f99149bda30dac255721c784e3b

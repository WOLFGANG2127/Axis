# AXIS Tier 1 Strategy Import Policy

Tier 1 strategy modules may import only Python standard-library modules and these AXIS interfaces:
`src.scoring`, `src.math`, `src.graph.state`, and `src.strategies.base`.

Third-party libraries including `numpy`, `pandas`, and `scipy` are deliberately rejected. This is a safety boundary: a submitted strategy executes within the production process, so its dependency surface must be reviewed centrally rather than declared by the strategy itself. Pattern-detection requiring a third-party library must be implemented in a reviewed shared scoring module, then supplied to `AxisState` as already-fetched, trust-tagged data.

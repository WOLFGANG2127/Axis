# AXIS Strategy Gate Reconciliation

This document separates three decisions that must never share one threshold.

| Gate | Governs | Current AXIS threshold / owner |
| --- | --- | --- |
| SHADOW → ENFORCE promotion gate | Whether a strategy's governance gates switch from logging-only to actually blocking. | Minimum 3 calendar days in SHADOW plus at least 15 strategy signals, then manual trader promotion only. No cron/auto-promotion. |
| Per-symbol shadow gate | Whether a symbol is considered sufficiently observed for a specific strategy/symbol pair. | Symbol-level criteria such as session count, expiry-cycle coverage, profit factor, win rate, drawdown, and manual fill-realism audit. This is stricter than SHADOW → ENFORCE and can differ for NIFTY vs BANKNIFTY. |
| Live-capital go/no-go gate | Whether real capital is risked system-wide. | Months of consistent paper data, positive EV, per-strategy and per-symbol evidence, and explicit human approval. This is the highest bar and is not satisfied by governance ENFORCE mode. |

Passing the first gate does not mean the strategy is good. Passing the first gate does not mean real capital is allowed. Strategy #2 may be active in the runtime registry while its governance gates remain SHADOW and its live-capital status remains paper-only.


#!/usr/bin/env bash
# AXIS Master Blueprint v11 -- Unified Verification Script
set -uo pipefail
echo "AXIS VERIFICATION -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo ""; echo "=== STEP ZERO: the single most load-bearing check in this document ==="
wc -l src/scoring/layer_b.py src/memory/ingest.py src/memory/recall.py 2>&1
echo "EXPECTED: 30, 71, 35 -- if this fails, treat every S1-CITED claim in Section 3 as unconfirmed."

echo ""; echo "=== SMOKE TEST: does the graph import cleanly? ==="
python -c "from src.graph.graph import graph; print('GRAPH IMPORTS CLEANLY')" 2>&1

echo ""; echo "=== D-001: IS THE SCORING PIPELINE WIRED? (single-sourced -- confirm carefully) ==="
grep -rn "score_layer_a\|score_layer_b\|score_layer_c" main.py src/graph/ src/data/ 2>/dev/null \
  || echo "NO CALL SITE FOUND OUTSIDE src/scoring/ ITSELF -- D-001 CONFIRMED"

echo ""; echo "=== D-004: /ready command present ==="
grep -rn "/ready" src/ 2>/dev/null || echo "NOT FOUND -- D-004 OPEN"

echo ""; echo "=== D-005: _log DEFINITION ==="
grep -n "^import logging\|_log = logging" src/graph/nodes.py 2>/dev/null || echo "_log NEVER DEFINED"

echo ""; echo "=== D-007: ohlc_writer.py ==="
find . -iname "ohlc_writer.py" 2>/dev/null || echo "NOT FOUND"

echo ""; echo "=== D-008: SINGLE-LOCATION CROSS-SYMBOL LOGIC ==="
grep -n "macro_regime_flags\|apply_same_cycle_correlation\|cross_symbol_correlation" main.py 2>/dev/null
grep -n "macro_regime_flags" src/graph/nodes.py 2>/dev/null
echo "EXPECTED: nodes.py grep returns NOTHING -- correlation logic lives only in main.py"

echo ""; echo "=== D-009: CRASH ALERT WIRING ==="
grep -n "__main__" main.py 2>/dev/null
grep -n "_run_cli\|_amain" main.py 2>/dev/null

echo ""; echo "=== D-010: Procfile / server.py ==="
cat Procfile 2>/dev/null; cat server.py 2>/dev/null

echo ""; echo "=== D-011: CORE-TIER LIVE DATABASE TABLES (7) -- run in Supabase SQL editor ==="
cat <<'SQL'
SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;
SELECT count(*) FROM signals; SELECT count(*) FROM active_position;
SELECT count(*) FROM system_paused; SELECT count(*) FROM telegram_updates_processed;
SELECT count(*) FROM trader_session_state; SELECT count(*) FROM cycle_summaries;
SELECT count(*) FROM macro_regime_flags;
SQL

echo ""; echo "=== D-012: STRATEGY REGISTRATION ==="
grep -n "STRATEGIES" src/graph/nodes.py 2>/dev/null
echo "EXPECTED: both GVOFStrategy() and WyckoffMeanReversionStrategy() listed"

echo ""; echo "=== D-013: AxisState FIELD CONTRACT ==="
grep -n "candidate_signals\|active_position\|is_backtest" main.py src/graph/state.py 2>/dev/null

echo ""; echo "=== D-045: STALE-DATA CHECK ==="
grep -n "stale\|timestamp" src/data/market_snapshot.py 2>/dev/null || echo "NOT FOUND -- D-045 OPEN"

echo ""; echo "=== D-047: NSE BLOCK DETECTION ==="
grep -n "403\|NSE_BLOCKED" src/data/nse_fetcher.py 2>/dev/null || echo "NOT FOUND -- D-047 OPEN"

echo ""; echo "=== D-048: TELEGRAM DELIVERY PERSISTENCE ==="
grep -n "telegram_sent" src/delivery/*.py src/graph/nodes.py 2>/dev/null || echo "NOT FOUND -- D-048 OPEN"

echo ""; echo "=== D-049: DEDUP HORIZON ==="
grep -n "60\|dedup" src/graph/nodes.py 2>/dev/null

echo ""; echo "=== D-050: ACTIVE POSITION TRACKING ==="
grep -rn "active_position" src/ 2>/dev/null || echo "NOT FOUND -- D-050 OPEN"

echo ""; echo "=== D-051: GH ACTIONS CONCURRENCY GROUP ==="
grep -n "concurrency:" .github/workflows/main_pipeline.yml 2>/dev/null || echo "NOT FOUND -- D-051 OPEN"

echo ""; echo "=== D-052: KILL SWITCH FAIL MODE ==="
grep -n "is_system_paused\|is_paused" src/scheduling/calendar_gate.py 2>/dev/null
echo "MANUAL CHECK: simulate a DB read failure, confirm it returns True (paused), not False"

echo ""; echo "=== D-046: /record REJECTS A DUPLICATE OPEN POSITION ==="
grep -rn "active_position" src/commands/ 2>/dev/null \
  || echo "NOT FOUND -- /record may not check for an existing open position, D-046 not fully closed"

echo ""; echo "=== D-055: INBOUND COMMAND ENDPOINT (NEW in v11) ==="
grep -rn "telegram/webhook\|X-Telegram-Bot-Api-Secret-Token" server.py src/commands/ 2>/dev/null \
  || echo "NOT FOUND -- D-055 OPEN"
grep -rn "telegram_updates_processed" src/commands/ 2>/dev/null \
  || echo "NOT FOUND -- update_id dedup missing, D-055 not fully closed"

echo ""; echo "=== D-055 INTEGRITY TEST (requires a staging deploy -- run manually, not part of the grep pass) ==="
cat <<'CURL'
# 1. Wrong secret must be rejected before anything else runs:
curl -s -o /dev/null -w "wrong-token status: %{http_code}\n" -X POST \
  https://<your-render-app>.onrender.com/telegram/webhook \
  -H "X-Telegram-Bot-Api-Secret-Token: wrong-token" \
  -d '{"update_id": 900001, "message": {"text": "/ready"}}'
# EXPECTED: 401

# 2. Correct secret, a FRESH update_id, must apply the effect:
curl -s -o /dev/null -w "fresh-update status: %{http_code}\n" -X POST \
  https://<your-render-app>.onrender.com/telegram/webhook \
  -H "X-Telegram-Bot-Api-Secret-Token: <real TELEGRAM_WEBHOOK_SECRET>" \
  -d '{"update_id": 900002, "message": {"text": "/ready"}}'
# EXPECTED: 200, and SELECT is_ready FROM trader_session_state WHERE session_date=current_date; -> true

# 3. Correct secret, the SAME update_id repeated, must be a no-op:
curl -s -o /dev/null -w "repeated-update status: %{http_code}\n" -X POST \
  https://<your-render-app>.onrender.com/telegram/webhook \
  -H "X-Telegram-Bot-Api-Secret-Token: <real TELEGRAM_WEBHOOK_SECRET>" \
  -d '{"update_id": 900002, "message": {"text": "/ready"}}'
# EXPECTED: 200, and no additional side effect -- 900002 is already in
# telegram_updates_processed from step 2, so this call should be a pure no-op.
CURL

echo ""; echo "=== D-T5: COGNEE GHOST DEPENDENCY ==="
grep -n "cognee" requirements.txt 2>/dev/null
echo "EXPECTED AFTER FIX: no output"

echo ""; echo "=== TEST SUITE ==="
gh run list --limit 10 2>/dev/null || echo "gh CLI not available; check Actions tab manually"
find . -name "test_*.py" -size 0 2>/dev/null
pytest --ignore=tests/smoke -q 2>&1 | tail -30

#!/usr/bin/env bash
if [ ! -d ".git" ]; then
  echo "FATAL: not a git repository — run from repo root, not a worktree."
  exit 1
fi
if [ ! -f "AXIS_STATE_LEDGER.md" ]; then
  echo "FATAL: AXIS_STATE_LEDGER.md not found."
  exit 1
fi
if [ ! -f "AXIS_MASTER_v11.md" ]; then
  echo "FATAL: AXIS_MASTER_v11.md not found at repo root."
  exit 1
fi

echo "=== D-001: is scoring wired into the live loop? ==="
grep -rn "from src.scoring import\|import src.scoring\|score_layer_" --include="*.py" \
  --exclude-dir={.git,venv,.venv,.swarm_venv,node_modules,__pycache__} src/ main.py 2>/dev/null \
  | grep -v "def score_layer" | grep -v "__pycache__"
echo "(empty = confirmed disconnected)"

echo "=== D-011: migration or schema files? ==="
find . \( -iname "*migration*" -o -iname "*schema*.sql" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/.swarm_venv/*" 2>/dev/null

echo "=== D-010: Procfile ==="
cat Procfile 2>/dev/null || echo "NO PROCFILE FOUND"

echo "=== D-055: inbound telegram webhook route? ==="
grep -rn "telegram/webhook\|@app.route\|@app.post" --include="*.py" \
  --exclude-dir={.git,venv,.venv,.swarm_venv,node_modules,__pycache__} . 2>/dev/null

echo "=== BASELINE HASHES (scope-creep detection) ==="
sha256sum main.py server.py src/data/market_snapshot.py src/graph/nodes.py \
  src/scoring/layer_a.py src/scoring/layer_b.py src/scoring/layer_c.py 2>/dev/null \
  || echo "(some files missing — note which ones, that's signal on its own)"
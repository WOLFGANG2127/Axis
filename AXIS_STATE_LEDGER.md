## RULES OF ENGAGEMENT

*** AXIS SWARM RULES OF ENGAGEMENT ***
1. Native MCP tool calls only — see the CBM Cheat Sheet (§0.3).
2. ALWAYS rebase onto origin/main before starting your first task of every
   session — whether or not you've seen a "[TO ALL BUILDERS]" broadcast.
3. Ledger writes happen inside YOUR OWN worktree/branch, never against
   origin/main directly (only Agent 6 pushes to main).
4. If `git pull --rebase` conflicts: `git rebase --abort` → plain `git pull` →
   re-read the ledger fresh before retrying. If the plain pull ALSO conflicts
   on AXIS_STATE_LEDGER.md, do not hand-resolve `<<<<<<<` markers — accept
   `--theirs` for that file (main is your source of truth), commit, push,
   then re-apply just your one intended status line as a follow-up commit.
   NOTE: this rule is for BUILDERS only — Agent 6 has its own, different
   conflict rule for its push-retry path (see Agent 6's dossier, §5).
5. If you add a third-party library — including test-only ones — update
   requirements.txt in the SAME commit.
6. NEVER write placeholder comments like `# ... rest unchanged ...` into a
   real file. Output complete files, character for character.
7. Preserve AXIS_STATE_LEDGER.md's exact Markdown structure.
8. NEVER put realistic-looking secrets/JWTs in test code — dummy strings only.
9. Any Supabase client for backend writes uses SUPABASE_SERVICE_ROLE_KEY,
   never anon — RLS silently blocks anon writes.
10. No third-party tool outside this stack (GitHub, Render, Netlify, Supabase,
    Gemini, Telegram, Dhan/NSE) gets added without a human's written, dated
    sign-off recorded in this ledger's changelog.
11. FILE LOCKS BLOCK CONCURRENT WRITES, NOT DIFFERENT TASKS. A lock on
    `server.py` for one task means no other agent may edit `server.py` at
    the same time — it does NOT mean a different, later task touching the
    same file is blocked once that lock is cleared or expired. Only the
    Task Board's status (`🔴 TODO` vs `🟣 PENDING QA` etc.) decides whether
    a task can be started; a lock is a same-moment write-conflict guard,
    not a standing task-level permission.
12. PRE-PUSH SANITY CHECK: before touching anything locally, run
    `git fetch origin main` (read-only — does not touch your working
    directory, so nothing can go wrong here even if you're mid-conflict on
    something else) and check your own task ID specifically:
    `git show origin/main:AXIS_STATE_LEDGER.md | grep "D-XXX"` (use your
    real task ID). If that line shows `REJECTED` or
    `[HUMAN INTERVENTION REQUIRED]` — set by Agent 5 or 6 while you were
    still working — STOP here, before any pull or push. Discard only your
    local ledger edit (`git checkout -- AXIS_STATE_LEDGER.md` — keeps your
    code changes intact), read the attached bug report, and restart the
    task from `🔴 TODO`. If your task ID's line is still what you expect,
    proceed with `git pull --rebase origin main` and push as normal (Rule 4
    applies if the rebase conflicts) — you've already confirmed there's
    nothing to overwrite, so Rule 4's ordinary flow is safe from here.
13. LEDGER TASK-BOARD ROW ISOLATION: when updating your task's status in
    the Task Board table, touch ONLY the exact row for your own D-XXX/D-TXX
    ID. Do not reorder rows, fix typos in other rows, or touch headers —
    treat every other Task Board row as read-only. (This is scoped to the
    Task Board specifically; File Locks and Agent Communicator already have
    their own append/clear rules defined elsewhere in this playbook.)
    MECHANICAL INSTRUCTION, not just a behavioral one — LLMs tend to
    "helpfully" regenerate an entire table when editing any part of it,
    which reformats every row and causes unnecessary merge conflicts with
    other agents who touched the same file. Use a targeted string
    replacement on the exact line — e.g. replace the literal text
    `| D-XXX | 🔴 TODO |` with `| D-XXX | 🟣 PENDING QA |` — never read the
    whole table and write it back. If your editing tool can't do a targeted
    replacement without reformatting the rest of the file, append your
    status update to the Agent Communicator section instead and say so
    explicitly, rather than risk corrupting the table.

## GATE 0 OUTPUT

=== D-001: is scoring wired into the live loop? ===
src/scoring/structure_gate.py:7:from src.scoring.layer_c import score_layer_c
src/scoring/structure_gate.py:26:    layer_c = score_layer_c(candle_rows, payload)
(empty = confirmed disconnected)
=== D-011: migration or schema files? ===
./migrations
=== D-010: Procfile ===
web: uvicorn server:app --host 0.0.0.0 --port 10000
=== D-055: inbound telegram webhook route? ===
=== BASELINE HASHES (scope-creep detection) ===
dc0871e40904ca022dc2b2bad23522bd75ec7cc928cfc8571aa27b320b814469  main.py
4aff29cc7da902d4a3b13b9ca11124341580e47a474e03dda782544acb95da4c  server.py
9d764ccfc51dc95157aaa3d941fdeb9eabe79525d3dfadde27ee07995ba276a9  src/graph/nodes.py
fb9ef6e8d97d9eea97daafef72824fe1bda20c98e226afa449ddbe536e723757  src/scoring/layer_a.py
369bd55555fdc1b00ddc8381b7f19703649a651e762837ed589c92296a1a92f7  src/scoring/layer_b.py
0119f24ecb9d0cfb38080c96ccf85219385c31a9f8e92b9806716b23c7707898  src/scoring/layer_c.py
(some files missing — note which ones, that's signal on its own)

## DATABASE VERIFICATION
D-011: 🟢 VERIFIED
(flip to "🟢 VERIFIED" only after personally applying and checking the
migration live in Supabase — all 7 tables, Section 3.3)

## TASK BOARD
- D-011: 🟢 DONE
- D-001: 🟢 DONE
- D-045: 🟢 DONE
- D-047: 🟢 DONE
- D-012: 🟢 DONE
- D-T6: 🟢 DONE
- D-018: 🟢 DONE
- D-010: 🟢 DONE
- D-051: 🟢 DONE
- D-055: 🟢 DONE
- D-004: 🟢 DONE
- D-048: 🟢 DONE
- D-005: Agent 5 PASS
- D-009: Agent 5 PASS
- D-008: Agent 5 PASS
- D-049: Agent 5 PASS
- D-050: Agent 5 PASS
- D-052: Agent 5 PASS

## FILE LOCKS

## AGENT COMMUNICATOR
(append-only; Agent 6 deletes a task's resolved lines only when it hits 🟢 DONE)
- Agent 3 (DevOps) completed D-010, D-051, D-055, D-004, D-048, D-050 (EOD cleanup component). Status set to 🟣 PENDING QA. Ready for Agent 5 QA review.
  Files touched:
  - Procfile
  - server.py
  - .github/workflows/main_pipeline.yml
  - src/commands/router.py
  - src/commands/__init__.py
  - src/scheduling/no_trade_summary.py
  - tests/test_agent3_devops.py
  - tests/test_track_e_devops.py
  - AXIS_STATE_LEDGER.md
- Agent 4 (System Orchestrator) completed D-005, D-009, D-008, D-049, D-050 (core active-position tracking), and D-052. Status set to 🟣 PENDING QA. Ready for Agent 5 QA review.
  Files touched:
  - main.py
  - src/graph/graph.py
  - src/graph/nodes.py
  - src/scheduling/calendar_gate.py
  - tests/test_agent4_orchestration.py
  - AXIS_STATE_LEDGER.md
- Agent 5 (QA Auditor) completed final structural and functional QA audit for D-005, D-009, D-008, D-049, D-050, and D-052. All checks PASSED (Agent 5 PASS). Cleared all active file locks for Agent 4's files. Authorized Agent 6 (Gatekeeper) to execute final merge into main.

## ACTIVITY LOG
(Agent 6 appends one line per merge — task ID, timestamp, commit hash)
- D-011, D-001, D-045, D-047 merged from agent1-dev at 2026-08-09T01:36:19Z (commit 37d2fe36)
- D-012, D-T6, D-018 merged from agent2-dev at 2026-08-09T13:58:52Z (commit 8b5c9a5c)
- D-010, D-051, D-055, D-004, D-048 merged from agent3-dev at 2026-08-09T17:22:23Z (commit ed4b0afb)

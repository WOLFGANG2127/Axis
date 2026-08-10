# Component 09 — Scheduling, Infrastructure, and Deployment

## 1. What This Component Is For (plain language, 2-3 sentences)
Hosts the calendar and lock gates, schedules token refresh and background pipeline tasks, and provides a small Cloud Web Wrapper for health checks and to spawn a background pipeline process in the deployed container. This component is responsible for run-lock vs infrastructure-lock separation, renewing Dhan tokens, and the GitHub Actions deployment/cron wiring.

## 2. Files in This Component
- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/server.py (17 lines)
  - One-line purpose: FastAPI health endpoints and a subprocess.Popen call that starts a background pipeline module at import time.
  - Key lines: subprocess.Popen([sys.executable, "-m", "src.scheduling.no_trade_summary"]) executed at module import. Health endpoints at / and /api/health.
  - STATUS: VERIFIED — evidence: file read.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/Procfile (1 line, binary-encoded)
  - One-line purpose: In deployment (Heroku/Render style) start uvicorn app from src.main:app on port 10000.
  - STATUS: VERIFIED — evidence: Procfile content shows "uvicorn src.main:app --host 0.0.0.0 --port 10000" (file contains text with non-UTF characters but the command is present).

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/requirements.txt
  - One-line purpose: Declares runtime dependencies including uvicorn, fastapi and lancedb/litellm/groq/cognee and others.
  - STATUS: VERIFIED — evidence: file read; contains uvicorn and many heavy dependencies that increase memory footprint.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/scheduling/token_refresher.py (75 lines)
  - One-line purpose: Renew Dhan token using renew_token() first and on exception generate_access_token(pin, totp) fallback; used by a GitHub Actions workflow scheduled regularly.
  - STATUS: VERIFIED — evidence: token refresh logic inspected; .github/workflows/token_refresh.yml references refresh schedule.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/.github/workflows/token_refresh.yml (20 lines)
  - One-line purpose: Cron schedule for token refresh (every 8 hours) and job to run the refresh_if_needed entrypoint.
  - STATUS: VERIFIED — evidence: workflow present and inspected.

## 3. How It Actually Works (the real internal logic, step by step)
1. Cloud Web Wrapper (server.py): on module import the file executes subprocess.Popen([sys.executable, "-m", "src.scheduling.no_trade_summary"]). This launches the module src.scheduling.no_trade_summary as a background Python module in a child process and then the FastAPI app exposes / and /api/health paths. The wrapper does not set up explicit signal handlers for the child or adopt process-group behavior. (Verified in server.py.)
2. Procfile: the Procfile command is "uvicorn src.main:app --host 0.0.0.0 --port 10000" (present in file). The process model therefore runs uvicorn which imports src.main (the app) — that app will itself create background threads/processes as coded (see server.py approach). The Procfile is used by Render/Heroku-style builders to start the process.
3. Dhan Token Refresh: token_refresher.refresh_if_needed() prefers renew_token(); on exception it calls generate_access_token(pin, totp) as fallback. The GitHub Actions workflow schedules refresh every 8 hours.
4. Run locks vs Infrastructure locks: src/scheduling/lock_manager.py implements acquire_run_lock() (short-lived per-cycle), and acquire_infrastructure_lock() (longer-lived for infra actions). Both functions call distinct RPCs/names in the DB allowing separation of concerns. (See file for distinct function names and usage sites.)

## 4. Connections — What This Depends On, What Depends On This
- Upstream: deployment environment variables (TELEGRAM_BOT_TOKEN, DATABASE_URL, TZ if set), and the Supabase/Postgres instance for lock acquisition.
- Downstream: background pipeline started by the subprocess (src.scheduling.no_trade_summary) is expected to run scheduling tasks and periodic summaries and may spawn further workers.
- External dependencies: heavy Python packages in requirements.txt which increase resident RAM; uvicorn/gunicorn used for HTTP serving.

## 5. Current Status — What's Actually Working vs. Not
sub-feature | status label | evidence
---|---|---
Cloud Web Wrapper present (server.py spawns subprocess) | VERIFIED | subprocess.Popen call in server.py at import
Subprocess execution target (module executed) | VERIFIED | target is "src.scheduling.no_trade_summary" (module executed with -m) per server.py
Procfile startup command | VERIFIED | Procfile contains uvicorn src.main:app --host 0.0.0.0 --port 10000
TZ=Asia/Kolkata environment variable configuration | CLAIMED-NOT-SHOWN | Code uses ZoneInfo("Asia/Kolkata") widely (ZoneInfo usage VERIFIED), but no deployment environment file or Procfile sets TZ=Asia/Kolkata — cannot confirm runtime environment sets TZ
SIGTERM / child process handling on container restart | BUILT-NOT-RUN | server.py does not register explicit SIGTERM handlers or process-group termination; behavior in container restarts (Render/Heroku) not tested here
512MB memory / OOM risk on Render free-tier | BUILT-NOT-RUN | requirements.txt includes heavy deps (lancedb, groq, langchain, numpy) indicating potential high memory usage; cannot verify actual OOM behavior without deployment
Subprocess target is not primary trading loop | VERIFIED (potential launch-blocker) | server.py launches "src.scheduling.no_trade_summary" (a summary task) rather than a main trading loop — per addendum this is flagged as a CRITICAL LAUNCH-BLOCKER to confirm intended behavior in deployment

## 6. What's Remaining, Specific to This Component Only
- Confirm whether starting src.scheduling.no_trade_summary as the container background subprocess is intentional (it may be a one-off summary script rather than the long-running trading loop). This is a CRITICAL LAUNCH-BLOCKER for live deployments and must be verified in the deployment manifest or with the team.
- Add robust SIGTERM forwarding / process-group management so that when the parent uvicorn process receives SIGTERM the child subprocess is also terminated cleanly (avoid orphaned children and stuck CPU usage). The code currently lacks this; it should be addressed in deployment run scripts (not in this read-only audit).
- Explicitly set TZ=Asia/Kolkata in the Render/Procfile or environment settings if the system relies on IST for date boundaries; code uses ZoneInfo("Asia/Kolkata") but environment-level TZ is not present in the repo.
- Evaluate memory usage by building a small runtime image and load-testing under 512MB to check OOM risk (requires a deployed test environment).

## 7. Last Verified
2026-07-26 — commit aabcce72ac767f99149bda30dac255721c784e3b

CRITICAL NOTE (from addendum): server.py spawns "src.scheduling.no_trade_summary" via subprocess at import. This exact target must be reconciled with intended deployment behavior: if the intended background process is the primary trading loop, launching the summary module is a serious launch-blocker and must be corrected in deployment configuration before live runs.

"""Temporary Step 1 test: settings must fail loudly when a key is missing."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

VALID_ENV_LINES = [
    "GOOGLE_API_KEY=test-google-key",
    "GROQ_API_KEY=test-groq-key",
    "ZAI_API_KEY=test-zai-key",
    "TELEGRAM_BOT_TOKEN=123456789:AAFakeTokenForStep1Test",
    "TELEGRAM_CHAT_ID=-1001234567890",
    "DHAN_CLIENT_ID=1107426122",
    "DHAN_ACCESS_TOKEN=test-dhan-access-token",
    "SUPABASE_URL=https://example.supabase.co",
    "SUPABASE_ANON_KEY=test-anon-key",
    "SUPABASE_SERVICE_ROLE_KEY=test-service-role-key",
]

IMPORT_SNIPPET = "from src.config.settings import settings; print('import ok')"


def run_settings_import(env_file: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["AXIS_ENV_FILE"] = str(env_file)
    return subprocess.run(
        [sys.executable, "-c", IMPORT_SNIPPET],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


def write_env_file(lines: list[str]) -> Path:
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".env",
        delete=False,
        encoding="utf-8",
    )
    with handle:
        handle.write("\n".join(lines) + "\n")
        return Path(handle.name)


def main() -> None:
    print("=== Step 1: missing GOOGLE_API_KEY ===")
    broken_lines = [line for line in VALID_ENV_LINES if not line.startswith("GOOGLE_API_KEY=")]
    broken_env = write_env_file(broken_lines)
    try:
        missing_key_result = run_settings_import(broken_env)
        combined_output = missing_key_result.stdout + missing_key_result.stderr
        print(f"exit code: {missing_key_result.returncode}")
        print(combined_output)
        if missing_key_result.returncode == 0:
            raise SystemExit("FAIL: import succeeded but should have failed")
        if "GOOGLE_API_KEY" not in combined_output:
            raise SystemExit("FAIL: error output did not name GOOGLE_API_KEY")
        print("PASS: import failed immediately and named GOOGLE_API_KEY")
    finally:
        broken_env.unlink(missing_ok=True)

    print("\n=== Step 1: all required keys present ===")
    valid_env = write_env_file(VALID_ENV_LINES)
    try:
        valid_result = run_settings_import(valid_env)
        combined_output = valid_result.stdout + valid_result.stderr
        print(f"exit code: {valid_result.returncode}")
        print(combined_output)
        if valid_result.returncode != 0:
            raise SystemExit("FAIL: valid env import should succeed")
        if "import ok" not in valid_result.stdout:
            raise SystemExit("FAIL: settings import did not complete")
        print("PASS: import succeeded with complete env")
    finally:
        valid_env.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

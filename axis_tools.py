import httpx
import subprocess

GATEWAY_URL = "http://127.0.0.1:8420"

# 1. TDAI Temporal Tools
def tdai_context_offload(task_id: str, task_logs: str) -> str:
    """Offloads massive pytest errors or tracebacks to TencentDB. Returns a Node ID."""
    payload = {"logs": task_logs, "session_key": task_id}
    response = httpx.post(f"{GATEWAY_URL}/capture", json=payload, timeout=15.0)
    response.raise_for_status()
    return f"Logs offloaded. Node ID: {response.json().get('node_id')}"

def tdai_memory_recall(node_id: str) -> str:
    """Retrieves the full raw text of an offloaded log using its Node ID."""
    response = httpx.get(f"{GATEWAY_URL}/recall/{node_id}", timeout=10.0)
    response.raise_for_status()
    return response.text

# 2. Shell Execution Tool (For Git and Pytest)
def execute_shell_command(command: str, worktree_path: str = ".") -> str:
    """Executes a shell command (git, pytest) in a specific directory and returns the output."""
    try:
        result = subprocess.run(
            command, shell=True, cwd=worktree_path, text=True, 
            capture_output=True, timeout=60
        )
        return result.stdout if result.returncode == 0 else f"ERROR:\n{result.stderr}"
    except Exception as e:
        return f"EXECUTION FAILED: {str(e)}"

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TencentDB_Memory_Bridge")
GATEWAY_URL = "http://127.0.0.1:8420"

@mcp.tool()
def tdai_context_offload(task_id: str, task_logs: str) -> str:
    """Offloads massive logs to TDAI. task_id MUST be exact ledger ID (e.g., 'D-011')."""
    payload = {"logs": task_logs, "session_key": task_id}
    try:
        response = httpx.post(f"{GATEWAY_URL}/capture", json=payload, timeout=15.0)
        response.raise_for_status()
        node_id = response.json().get('node_id', 'UNKNOWN')
        return f"SUCCESS: Logs offloaded. Write this in Communicator: [See Node ID: {node_id}]"
    except Exception as e:
        return f"ERROR: Could not offload memory: {str(e)}"

@mcp.tool()
def tdai_memory_recall(node_id: str) -> str:
    """Retrieves full raw text of an offloaded log using Node ID."""
    try:
        response = httpx.get(f"{GATEWAY_URL}/recall/{node_id}", timeout=10.0)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"ERROR: Could not recall memory: {str(e)}"

@mcp.tool()
def tdai_memory_search(query: str, task_id: str = "GLOBAL_SOP") -> str:
    """Searches long-term Persona and Scenario memory for past agent constraints."""
    payload = {"query": query, "session_key": task_id}
    try:
        response = httpx.post(f"{GATEWAY_URL}/search", json=payload, timeout=15.0)
        response.raise_for_status()
        return response.json().get("answer", "No relevant memory found.")
    except Exception as e:
        return f"ERROR: Memory search failed: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')

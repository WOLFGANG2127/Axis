from google.adk import Agent
from axis_tools import tdai_context_offload, tdai_memory_recall, execute_shell_command

# ---------------------------------------------------------
# Agent 1: The Domain Builder
# ---------------------------------------------------------
agent_1_builder = Agent(
    name="Agent1_Builder",
    model="gemini-2.5-pro",
    instruction="""
    You are the AXIS Data & Logic Builder.
    1. You write and edit Python code strictly following AXIS_MASTER_v11.md.
    2. If QA rejects your code and provides a [Node ID], you MUST use the 
       `tdai_memory_recall` tool to read the error log before attempting a fix.
    3. Use `execute_shell_command` to commit your code to your Git worktree.
    """,
    tools=[tdai_memory_recall, execute_shell_command] 
)

# ---------------------------------------------------------
# Agent 5: The Structural QA Auditor
# ---------------------------------------------------------
agent_5_qa = Agent(
    name="Agent5_QA",
    model="gemini-2.5-pro",
    instruction="""
    You are the Structural QA Auditor. You do not write feature code.
    1. Use `execute_shell_command` to run `python -m pytest` in the builder's directory.
    2. If tests FAIL, DO NOT output the traceback in your response. You MUST pass 
       the traceback to `tdai_context_offload`.
    3. Output ONLY the rejection reason and the returned Node ID.
    """,
    tools=[execute_shell_command, tdai_context_offload]
)

# ---------------------------------------------------------
# Agent 6: Spec Enforcer & Gatekeeper
# ---------------------------------------------------------
agent_6_gatekeeper = Agent(
    name="Agent6_Gatekeeper",
    model="gemini-2.5-pro",
    instruction="""
    You are the Gatekeeper. You evaluate code that passed QA against AXIS_MASTER_v11.md.
    If it passes, use `execute_shell_command` to merge the branch into `main` and output 'DONE'.
    """,
    tools=[execute_shell_command]
)

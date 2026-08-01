import os
from google.adk import Workflow
from axis_agents import agent_1_builder, agent_5_qa, agent_6_gatekeeper

# Set up your API key for ADK
os.environ["GOOGLE_API_KEY"] = "AQ.Ab8RN6KFrUGRVF6IRaXBfV87-RvT8NZghnxls4d3ldxFIWnkwQ"

def route_qa_output(state):
    """
    Dynamic routing logic based on Agent 5's output.
    If Agent 5 offloaded an error, route back to Builder.
    If tests passed, route to Gatekeeper.
    """
    output_text = state.get("output", "")
    if "Node ID" in output_text or "FAIL" in output_text:
        print("❌ QA Failed. Looping back to Agent 1...")
        return agent_1_builder
    
    print("✅ QA Passed. Routing to Agent 6 Gatekeeper...")
    return agent_6_gatekeeper

# The ADK framework strictly looks for a variable named 'root_agent'
root_agent = Workflow(
    name="AXIS_Autonomous_Pipeline",
    edges=[
        ("START", agent_1_builder),
        (agent_1_builder, agent_5_qa),
        (agent_5_qa, route_qa_output)
    ]
)

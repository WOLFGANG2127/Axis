import os
from google.adk import Workflow
from axis_agents import agent_1_builder, agent_5_qa, agent_6_gatekeeper

# Set up your API key for ADK
os.environ["GOOGLE_API_KEY"] = "AQ.Ab8RN6KFrUGRVF6IRaXBfV87-RvT8NZghnxls4d3ldxFIWnkwQ"

def route_qa_output(state):
    """
    Dynamic routing logic based on Agent 5's output.
    If Agent 5 offloaded an error (Node ID present), route back to Builder.
    If tests passed, route to Gatekeeper.
    """
    output_text = state.get("output", "")
    if "Node ID" in output_text or "FAIL" in output_text:
        print("❌ QA Failed. Looping back to Agent 1...")
        return agent_1_builder
    
    print("✅ QA Passed. Routing to Agent 6 Gatekeeper...")
    return agent_6_gatekeeper

# Define the Directed Acyclic Graph (DAG) for the Swarm
axis_swarm = Workflow(
    name="AXIS_Autonomous_Pipeline",
    edges=[
        # 1. Start the workflow by handing the task to the Builder
        ("START", agent_1_builder),
        
        # 2. When the Builder finishes, pass the code to QA
        (agent_1_builder, agent_5_qa),
        
        # 3. Dynamic Router: Loop back to Builder OR go to Gatekeeper
        (agent_5_qa, route_qa_output)
    ]
)

if __name__ == "__main__":
    print("🚀 Booting AXIS Autonomous Swarm via Google ADK...")
    
    # Input the specific Task from the v11 Ledger
    task_input = """
    Execute Task D-001 (Wire the scoring pipeline). 
    Build fetch_and_score_market_data in src/data/market_snapshot.py. 
    Ensure you use tests/fixtures/dhan_sample.json for mocks.
    """
    
    # FIX IS HERE: Changed input_data to input
    result = axis_swarm.run(input=task_input)
    print("\n🏁 Swarm Execution Completed. Final State:")
    print(result)

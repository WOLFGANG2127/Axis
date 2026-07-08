from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    message: str


def collect(state: State):
    print("Running Collect Node")
    return {"message": state["message"] + " -> Collect"}


def analyze(state: State):
    print("Running Analyze Node")
    return {"message": state["message"] + " -> Analyze"}


builder = StateGraph(State)

builder.add_node("collect", collect)
builder.add_node("analyze", analyze)

builder.add_edge(START, "collect")
builder.add_edge("collect", "analyze")
builder.add_edge("analyze", END)

graph = builder.compile()

result = graph.invoke(
    {
        "message": "START"
    }
)

print("\n========================")
print("Final State")
print("========================")
print(result)
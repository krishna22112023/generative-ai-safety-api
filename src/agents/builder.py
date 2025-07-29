from langgraph.graph import StateGraph, START
from src.agents.types import State

def build_graph():
    """Build and return the agent workflow graph."""

    from src.agents.nodes import agent_node
    builder = StateGraph(State)
    builder.add_edge(START, "agent")
    builder.add_node("agent", agent_node)
    return builder.compile()
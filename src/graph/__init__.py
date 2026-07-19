"""AXIS graph package."""


def build_graph():
    """Lazily import the graph to avoid strategy/state import cycles."""
    from src.graph.graph import build_graph as _build_graph
    return _build_graph()

__all__ = ["build_graph"]

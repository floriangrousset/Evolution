"""Main LangGraph orchestration for Evolution simulator."""

from langgraph.graph import StateGraph, END

from ..state.types import EvolutionState
from .nodes import (
    age_children_node,
    find_mates_node,
    reproduce_node,
    update_singles_node,
    increment_cycle_node,
)


def should_continue_mating(state: EvolutionState) -> str:
    """Decide whether to continue with mating or skip it.

    If population has reached the limit, skip mating and reproduction.

    Args:
        state: Current evolution state.

    Returns:
        "find_mates" if under population limit, "update_singles" otherwise.
    """
    if len(state["population"]) >= state["config"].max_population:
        return "update_singles"
    return "find_mates"


def create_evolution_graph():
    """Create the main evolution simulation graph.

    The graph flow:
    1. age_children: Transition children to adults based on age
    2. Conditional: Check if population limit reached
       - If under limit: find_mates -> reproduce -> update_singles
       - If at limit: update_singles (skip mating)
    3. increment_cycle: Update cycle counter
    4. END

    Returns:
        Compiled StateGraph ready for execution.
    """
    # Create graph with EvolutionState
    graph = StateGraph(EvolutionState)

    # Add nodes
    graph.add_node("age_children", age_children_node)
    graph.add_node("find_mates", find_mates_node)
    graph.add_node("reproduce", reproduce_node)
    graph.add_node("update_singles", update_singles_node)
    graph.add_node("increment_cycle", increment_cycle_node)

    # Set entry point
    graph.set_entry_point("age_children")

    # Add edges
    # After aging, check if we should continue with mating
    graph.add_conditional_edges(
        "age_children",
        should_continue_mating,
        {
            "find_mates": "find_mates",
            "update_singles": "update_singles",
        },
    )

    # Normal flow when under population limit
    graph.add_edge("find_mates", "reproduce")
    graph.add_edge("reproduce", "update_singles")

    # After updating singles, increment cycle and end
    graph.add_edge("update_singles", "increment_cycle")
    graph.add_edge("increment_cycle", END)

    # Compile graph
    return graph.compile()

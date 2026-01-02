"""Main LangGraph orchestration for Evolution simulator."""

from langgraph.graph import StateGraph, END

from ..state.types import EvolutionState
from .nodes import (
    age_children_node,
    find_mates_node,
    llm_speed_dating_node,
    reproduce_node,
    update_singles_node,
    capture_trait_snapshot_node,
    increment_cycle_node,
)


def route_to_mating(state: EvolutionState) -> str:
    """Route to appropriate mating strategy based on configuration.

    If population has reached the limit, skip mating and reproduction.
    Otherwise, route to LLM speed dating or deterministic matching based on config.

    Args:
        state: Current evolution state.

    Returns:
        "llm_speed_dating" if LLM mating enabled and under population limit,
        "find_mates" if deterministic mating and under population limit,
        "update_singles" if at population limit.
    """
    if len(state["population"]) >= state["config"].max_population:
        return "update_singles"

    if state["config"].enable_llm_mating:
        return "llm_speed_dating"
    else:
        return "find_mates"


def create_evolution_graph():
    """Create the main evolution simulation graph.

    The graph flow:
    1. age_children: Transition children to adults based on age
    2. Conditional: Route to mating strategy
       - If at population limit: update_singles (skip mating)
       - If LLM mating enabled: llm_speed_dating -> reproduce -> update_singles
       - If deterministic mating: find_mates -> reproduce -> update_singles
    3. capture_trait_snapshot: Record trait evolution
    4. increment_cycle: Update cycle counter
    5. END

    Returns:
        Compiled StateGraph ready for execution.
    """
    # Create graph with EvolutionState
    graph = StateGraph(EvolutionState)

    # Add nodes
    graph.add_node("age_children", age_children_node)
    graph.add_node("find_mates", find_mates_node)
    graph.add_node("llm_speed_dating", llm_speed_dating_node)
    graph.add_node("reproduce", reproduce_node)
    graph.add_node("update_singles", update_singles_node)
    graph.add_node("capture_trait_snapshot", capture_trait_snapshot_node)
    graph.add_node("increment_cycle", increment_cycle_node)

    # Set entry point
    graph.set_entry_point("age_children")

    # Add edges
    # After aging, route to appropriate mating strategy
    graph.add_conditional_edges(
        "age_children",
        route_to_mating,
        {
            "llm_speed_dating": "llm_speed_dating",
            "find_mates": "find_mates",
            "update_singles": "update_singles",
        },
    )

    # Both mating strategies lead to reproduction
    graph.add_edge("find_mates", "reproduce")
    graph.add_edge("llm_speed_dating", "reproduce")
    graph.add_edge("reproduce", "update_singles")

    # After updating singles, capture trait snapshot
    graph.add_edge("update_singles", "capture_trait_snapshot")

    # Then increment cycle and end
    graph.add_edge("capture_trait_snapshot", "increment_cycle")
    graph.add_edge("increment_cycle", END)

    # Compile graph
    return graph.compile()

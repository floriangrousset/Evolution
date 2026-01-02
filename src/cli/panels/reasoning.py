"""Reasoning panel for displaying agent decision-making."""

from rich.panel import Panel
from rich.text import Text

from ...state.types import EvolutionState


def create_reasoning_panel(state: EvolutionState, max_show: int = 3) -> Panel:
    """Show agent reasoning for recent matches.

    Args:
        state: Current evolution state.
        max_show: Maximum number of reasoning entries to display.

    Returns:
        Panel containing agent reasoning.
    """
    if not state["conversation_transcripts"]:
        return Panel(
            "No reasoning available yet. Speed dating will begin once adults are paired.",
            title="🧠 Agent Reasoning",
            border_style="magenta",
        )

    recent = state["conversation_transcripts"][-max_show:]
    text = Text()

    for i, result in enumerate(reversed(recent)):
        # Male's reasoning
        text.append(f"🧠 {result.male.name}", style="bold cyan")
        text.append(f" (score: {result.male_score}/100)\n", style="dim")
        text.append(f"{result.male_reasoning}\n\n")

        # Female's reasoning
        text.append(f"🧠 {result.female.name}", style="bold magenta")
        text.append(f" (score: {result.female_score}/100)\n", style="dim")
        text.append(f"{result.female_reasoning}\n")

        # Add spacing between entries
        if i < len(recent) - 1:
            text.append("\n---\n\n")

    return Panel(text, title="🧠 Agent Reasoning", border_style="magenta")

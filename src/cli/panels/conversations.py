"""Conversation panel for displaying speed dating transcripts."""

from rich.panel import Panel
from rich.text import Text

from ...state.types import EvolutionState


def create_conversations_panel(
    state: EvolutionState, max_show: int = 3
) -> Panel:
    """Show recent speed dating conversations.

    Args:
        state: Current evolution state.
        max_show: Maximum number of conversations to display.

    Returns:
        Panel containing conversation transcripts.
    """
    if not state["conversation_transcripts"]:
        return Panel(
            "No conversations yet. Speed dating will begin once adults are paired.",
            title="💬 Recent Conversations",
            border_style="cyan",
        )

    recent = state["conversation_transcripts"][-max_show:]
    text = Text()

    for i, result in enumerate(reversed(recent)):
        # Header with names and score
        text.append(f"{result.male.name}", style="bold cyan")
        text.append(" ♥ ", style="red")
        text.append(f"{result.female.name}", style="bold magenta")
        text.append(f" (Score: {result.final_score:.0f}/100)\n", style="yellow")

        # Show all 4 turns
        for msg in result.messages:
            # Alternate speaker icons
            if msg.speaker_id == result.male.id:
                icon = "👨"
                style = "cyan"
            else:
                icon = "👩"
                style = "magenta"

            text.append(f"{icon} {msg.speaker_name}: ", style=f"bold {style}")
            text.append(f'"{msg.content}"\n')

        # Show individual scores
        text.append(f"  {result.male.name}: {result.male_score}/100 | ", style="dim")
        text.append(f"{result.female.name}: {result.female_score}/100\n", style="dim")

        # Add spacing between conversations
        if i < len(recent) - 1:
            text.append("\n")

    return Panel(text, title="💬 Recent Conversations", border_style="cyan")

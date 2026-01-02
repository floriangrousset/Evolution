"""CLI display and visualization using Rich."""

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..state.types import AgentMessage, EvolutionState, calculate_population_stats
from .panels.conversations import create_conversations_panel
from .panels.reasoning import create_reasoning_panel
from .panels.evolution_graphs import create_trait_evolution_panel
from .panels.inspector import create_inspector_panel


# Tool icons
TOOL_ICONS = {
    "stone-tools": "🔧",
    "fire": "🔥",
    "calculator": "📊",
    "memory": "📚",
}


class Display:
    """Handles all CLI display and visualization."""

    def __init__(self):
        """Initialize the display."""
        self.console = Console()
        self.recent_messages = []
        self.max_messages = 10

    def get_tool_icons(self, tools: list[str]) -> str:
        """Convert tool names to icons.

        Args:
            tools: List of tool names.

        Returns:
            String of tool icons or "-" if no tools.
        """
        if not tools:
            return "-"
        return "".join(TOOL_ICONS.get(tool, "?") for tool in tools)

    def create_population_grid(self, state: EvolutionState) -> Table:
        """Create a table showing the population grid.

        Args:
            state: Current evolution state.

        Returns:
            Rich Table with population grid.
        """
        table = Table(title="Population Grid", show_header=False, show_edge=True)

        population = state["population"]
        if not population:
            table.add_row("No population yet")
            return table

        # Sort by generation, then by age stage (adults first)
        sorted_pop = sorted(
            population, key=lambda p: (p.generation, p.age_stage == "child")
        )

        # Create grid (4 persons per row)
        persons_per_row = 4
        for i in range(0, len(sorted_pop), persons_per_row):
            row_persons = sorted_pop[i : i + persons_per_row]

            # Build person display strings
            person_strs = []
            tool_strs = []

            for person in row_persons:
                # Color code by gender and age
                if person.gender == "male":
                    color = "blue" if person.age_stage == "adult" else "cyan"
                else:
                    color = "magenta" if person.age_stage == "adult" else "pink"

                # Add heart if coupled
                couple_symbol = " ♥" if person.partner_id else ""

                person_text = Text()
                person_text.append(
                    f"{person.get_short_name()}{couple_symbol}", style=color
                )
                person_strs.append(person_text)

                # Tools
                tool_text = Text()
                tool_text.append(f"[{self.get_tool_icons(person.tools)}]", style="dim")
                tool_strs.append(tool_text)

            # Add row with person info
            table.add_row(*[str(p) for p in person_strs])
            # Add row with tools
            table.add_row(*[str(t) for t in tool_strs])
            # Add spacer
            if i + persons_per_row < len(sorted_pop):
                table.add_row(*["" for _ in range(len(row_persons))])

        return table

    def create_statistics_panel(self, state: EvolutionState) -> Panel:
        """Create a panel showing population statistics.

        Args:
            state: Current evolution state.

        Returns:
            Rich Panel with statistics.
        """
        stats = calculate_population_stats(state)

        # Build statistics text
        text = Text()
        text.append(f"Total Population: ", style="bold")
        text.append(f"{stats['total_population']}\n")

        text.append(f"Adults: ", style="bold")
        text.append(f"{stats['num_adults']} ")
        text.append("| ", style="dim")
        text.append(f"Children: ", style="bold")
        text.append(f"{stats['num_children']}\n")

        text.append(f"Males: ", style="bold blue")
        text.append(f"{stats['num_males']} ")
        text.append("| ", style="dim")
        text.append(f"Females: ", style="bold magenta")
        text.append(f"{stats['num_females']}\n")

        text.append(f"Couples: ", style="bold red")
        text.append(f"{stats['num_couples']}\n\n")

        # Generation breakdown
        text.append("Generations: ", style="bold")
        for gen in sorted(stats["generations"].keys()):
            text.append(f"G{gen}:{stats['generations'][gen]} ")
        text.append("\n\n")

        # Average traits
        text.append("Avg Traits: ", style="bold")
        traits = stats["avg_traits"]
        text.append(
            f"O:{traits['openness']:.1f} "
            f"C:{traits['conscientiousness']:.1f} "
            f"E:{traits['extraversion']:.1f} "
            f"A:{traits['agreeableness']:.1f} "
            f"N:{traits['neuroticism']:.1f}"
        )

        return Panel(text, title="Statistics", border_style="green")

    def create_events_panel(self, messages: list[AgentMessage]) -> Panel:
        """Create a panel showing recent events.

        Args:
            messages: List of recent messages.

        Returns:
            Rich Panel with events.
        """
        if not messages:
            return Panel("No events yet", title="Recent Events", border_style="yellow")

        text = Text()
        # Show last N messages
        recent = messages[-self.max_messages :]

        for msg in recent:
            if msg.type == "birth":
                icon = "👶"
                style = "green"
            elif msg.type == "adult":
                icon = "🎓"
                style = "blue"
            elif msg.type == "couple":
                icon = "💑"
                style = "red"
            else:
                icon = "ℹ️"
                style = "white"

            text.append(f"{icon} ", style=style)
            text.append(f"{msg.content}\n")

        return Panel(text, title="Recent Events", border_style="yellow")

    def create_header(self, state: EvolutionState) -> Panel:
        """Create header panel with cycle and generation info.

        Args:
            state: Current evolution state.

        Returns:
            Rich Panel with header info.
        """
        text = Text()
        text.append("EVOLUTION SIMULATOR", style="bold cyan")
        text.append("\n\n")
        text.append(f"Generation: ", style="bold")
        text.append(f"{state['generation_number']} ")
        text.append("| ", style="dim")
        text.append(f"Cycle: ", style="bold")
        text.append(f"{state['cycle_count']}")

        return Panel(text, border_style="cyan")

    def render_full_display(self, state: EvolutionState):
        """Render the complete display with all panels.

        Args:
            state: Current evolution state.
        """
        self.console.clear()

        # Create header
        header = self.create_header(state)
        self.console.print(header)

        # Create statistics
        stats = self.create_statistics_panel(state)
        self.console.print(stats)

        # Create population grid
        grid = self.create_population_grid(state)
        self.console.print(grid)

        # NEW PANELS: LLM Mating Features
        # Only show if LLM mating is enabled
        if state["config"].enable_llm_mating:
            # Show recent conversations
            conversations = create_conversations_panel(state)
            self.console.print(conversations)

            # Show agent reasoning
            reasoning = create_reasoning_panel(state)
            self.console.print(reasoning)

            # Show trait evolution graphs
            evolution = create_trait_evolution_panel(state)
            self.console.print(evolution)

            # Show agent inspector (most recent couple)
            inspector = create_inspector_panel(state)
            self.console.print(inspector)

        # Create events
        events = self.create_events_panel(state["messages"])
        self.console.print(events)

        # Legend
        legend = Panel(
            "M/F = Male/Female | G# = Generation | A/C = Adult/Child | ♥ = Coupled\n"
            "🔥 = fire | 🔧 = stone-tools | 📊 = calculator | 📚 = memory",
            title="Legend",
            border_style="dim",
        )
        self.console.print(legend)

    def print_event(self, message: AgentMessage):
        """Print a single event message.

        Args:
            message: The message to print.
        """
        if message.type == "birth":
            self.console.print(f"[green]👶 {message.content}[/green]")
        elif message.type == "adult":
            self.console.print(f"[blue]🎓 {message.content}[/blue]")
        elif message.type == "couple":
            self.console.print(f"[red]💑 {message.content}[/red]")
        else:
            self.console.print(f"[white]ℹ️ {message.content}[/white]")

    def print_welcome(self):
        """Print welcome message."""
        welcome_text = Text()
        welcome_text.append("=" * 60 + "\n", style="cyan")
        welcome_text.append("EVOLUTION SIMULATOR\n", style="bold cyan")
        welcome_text.append("=" * 60 + "\n", style="cyan")
        welcome_text.append(
            "\nSimulating life evolution with personality-based mate selection\n\n",
            style="white",
        )
        welcome_text.append("Press Ctrl+C to stop\n\n", style="yellow")

        self.console.print(welcome_text)

    def print_goodbye(self, state: EvolutionState):
        """Print goodbye message with final statistics.

        Args:
            state: Final state.
        """
        stats = calculate_population_stats(state)

        goodbye_text = Text()
        goodbye_text.append("\n" + "=" * 60 + "\n", style="cyan")
        goodbye_text.append("SIMULATION ENDED\n", style="bold cyan")
        goodbye_text.append("=" * 60 + "\n", style="cyan")
        goodbye_text.append(
            f"\nFinal Population: {stats['total_population']}\n", style="white"
        )
        goodbye_text.append(
            f"Generations: {max(stats['generations'].keys()) + 1 if stats['generations'] else 0}\n",
            style="white",
        )
        goodbye_text.append(f"Cycles: {state['cycle_count']}\n\n", style="white")

        self.console.print(goodbye_text)

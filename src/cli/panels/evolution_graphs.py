"""Evolution graphs panel for displaying trait trends over time."""

from rich.panel import Panel
from rich.text import Text

from ...state.types import EvolutionState


def ascii_sparkline(values: list[float], width: int = 40, height: int = 5) -> str:
    """Generate a simple ASCII sparkline chart.

    Args:
        values: List of values to plot.
        width: Width of the chart in characters.
        height: Height of the chart in lines.

    Returns:
        ASCII art string representing the sparkline.
    """
    if not values or len(values) < 2:
        return "Not enough data"

    # Normalize values to 0-1 range
    min_val = min(values)
    max_val = max(values)
    val_range = max_val - min_val

    if val_range == 0:
        normalized = [0.5] * len(values)
    else:
        normalized = [(v - min_val) / val_range for v in values]

    # Sample values to fit width
    if len(values) > width:
        step = len(values) / width
        sampled = [values[int(i * step)] for i in range(width)]
        sampled_norm = [(v - min_val) / val_range for v in sampled]
    else:
        sampled = values
        sampled_norm = normalized

    # Build chart line by line from top to bottom
    lines = []
    for row in range(height):
        line = ""
        threshold = 1.0 - (row / (height - 1))
        for val in sampled_norm:
            if val >= threshold:
                line += "█"
            else:
                line += " "
        lines.append(line)

    # Add value labels
    chart = f"{max_val:5.1f} │{lines[0]}\n"
    for line in lines[1:-1]:
        chart += f"      │{line}\n"
    chart += f"{min_val:5.1f} │{lines[-1]}"

    return chart


def create_trait_evolution_panel(state: EvolutionState) -> Panel:
    """Show ASCII charts of trait evolution over time.

    Args:
        state: Current evolution state.

    Returns:
        Panel containing trait evolution graphs.
    """
    history = state["trait_history"]

    if len(history) < 2:
        return Panel(
            "Not enough data yet. Trait evolution will be tracked over generations.",
            title="📈 Trait Evolution",
            border_style="green",
        )

    text = Text()

    # Extract trait values
    traits = {
        "Openness": [h.avg_openness for h in history],
        "Conscientiousness": [h.avg_conscientiousness for h in history],
        "Extraversion": [h.avg_extraversion for h in history],
        "Agreeableness": [h.avg_agreeableness for h in history],
        "Neuroticism": [h.avg_neuroticism for h in history],
    }

    # Generation range
    gen_start = history[0].generation
    gen_end = history[-1].generation
    text.append(f"Generations {gen_start} → {gen_end}\n\n", style="bold")

    # Show sparkline for each trait
    for trait_name, values in traits.items():
        text.append(f"{trait_name}:\n", style="bold yellow")
        chart = ascii_sparkline(values, width=50, height=4)
        text.append(f"{chart}\n\n")

    # Population size trend
    pop_sizes = [h.population_size for h in history]
    text.append("Population Size:\n", style="bold yellow")
    chart = ascii_sparkline(pop_sizes, width=50, height=4)
    text.append(f"{chart}\n")

    return Panel(text, title="📈 Trait Evolution", border_style="green")

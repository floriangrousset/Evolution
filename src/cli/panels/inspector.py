"""Inspector panel for detailed agent information."""

from rich.panel import Panel
from rich.text import Text

from ...agents.base import Person, find_person_by_id
from ...state.types import EvolutionState


def create_inspector_panel(
    state: EvolutionState, person_id: str | None = None
) -> Panel:
    """Detailed view of a single agent.

    Args:
        state: Current evolution state.
        person_id: ID of person to inspect. If None, shows most recent couple.

    Returns:
        Panel with detailed agent information.
    """
    # If no person_id specified, show most recent couple
    if person_id is None:
        if state["conversation_transcripts"]:
            result = state["conversation_transcripts"][-1]
            return _create_couple_inspector(state, result.male, result.female)
        else:
            return Panel(
                "No agents to inspect yet. Speed dating will begin once adults are paired.",
                title="🔍 Agent Inspector",
                border_style="yellow",
            )

    # Find specified person
    person = find_person_by_id(state["population"], person_id)
    if not person:
        return Panel(
            f"Person with ID {person_id} not found.",
            title="🔍 Agent Inspector",
            border_style="yellow",
        )

    return _create_single_inspector(state, person)


def _create_single_inspector(state: EvolutionState, person: Person) -> Panel:
    """Create inspector panel for a single person.

    Args:
        state: Current evolution state.
        person: Person to inspect.

    Returns:
        Panel with person details.
    """
    text = Text()

    # Basic info
    text.append(f"{person.name}\n", style="bold yellow")
    text.append(f"{'─' * 40}\n", style="dim")
    text.append(f"Gender: {person.gender.title()} | ", style="dim")
    text.append(f"Generation: {person.generation} | ", style="dim")
    text.append(f"Age: {person.age_stage.title()}\n", style="dim")

    # Partner status
    if person.partner_id:
        partner = find_person_by_id(state["population"], person.partner_id)
        partner_name = partner.name if partner else "Unknown"
        text.append(f"Partner: {partner_name}\n\n", style="green")
    else:
        text.append("Status: Single\n\n", style="red")

    # Personality (Big Five)
    text.append("PERSONALITY:\n", style="bold")
    text.append(f"  Openness:          {person.openness:.1f}/10.0\n", style="cyan")
    text.append(
        f"  Conscientiousness: {person.conscientiousness:.1f}/10.0\n", style="cyan"
    )
    text.append(f"  Extraversion:      {person.extraversion:.1f}/10.0\n", style="cyan")
    text.append(
        f"  Agreeableness:     {person.agreeableness:.1f}/10.0\n", style="cyan"
    )
    text.append(f"  Neuroticism:       {person.neuroticism:.1f}/10.0\n\n", style="cyan")

    # Skills
    text.append("SKILLS:\n", style="bold")
    if person.skills:
        for skill, proficiency in person.skills.items():
            text.append(f"  {skill}: {proficiency:.1f}/10.0\n", style="green")
    else:
        text.append("  None\n", style="dim")
    text.append("\n")

    # Tools
    text.append("TOOLS:\n", style="bold")
    if person.tools:
        text.append(f"  {', '.join(person.tools)}\n\n", style="magenta")
    else:
        text.append("  None\n\n", style="dim")

    # Conversation history
    conversations = [
        t
        for t in state["conversation_transcripts"]
        if t.male.id == person.id or t.female.id == person.id
    ]
    text.append(f"CONVERSATIONS: {len(conversations)}\n", style="bold")
    if conversations:
        for conv in conversations[-3:]:  # Show last 3
            partner = conv.female if conv.male.id == person.id else conv.male
            score = conv.male_score if conv.male.id == person.id else conv.female_score
            text.append(f"  • {partner.name}: {score}/100\n", style="dim")

    return Panel(text, title="🔍 Agent Inspector", border_style="yellow")


def _create_couple_inspector(
    state: EvolutionState, male: Person, female: Person
) -> Panel:
    """Create inspector panel showing a couple side-by-side.

    Args:
        state: Current evolution state.
        male: Male in couple.
        female: Female in couple.

    Returns:
        Panel with couple details.
    """
    text = Text()

    # Header
    text.append(f"{male.name}", style="bold cyan")
    text.append(" ♥ ", style="red")
    text.append(f"{female.name}\n", style="bold magenta")
    text.append(f"{'─' * 60}\n\n", style="dim")

    # Personalities side-by-side
    text.append("PERSONALITIES:\n", style="bold")
    traits = [
        ("Openness", male.openness, female.openness),
        ("Conscientiousness", male.conscientiousness, female.conscientiousness),
        ("Extraversion", male.extraversion, female.extraversion),
        ("Agreeableness", male.agreeableness, female.agreeableness),
        ("Neuroticism", male.neuroticism, female.neuroticism),
    ]
    for trait_name, male_val, female_val in traits:
        text.append(f"  {trait_name:18}", style="dim")
        text.append(f"{male_val:.1f}", style="cyan")
        text.append("  vs  ")
        text.append(f"{female_val:.1f}\n", style="magenta")

    text.append("\n")

    # Skills
    text.append("SKILLS:\n", style="bold")
    all_skills = set(male.skills.keys()) | set(female.skills.keys())
    if all_skills:
        for skill in sorted(all_skills):
            male_prof = male.skills.get(skill, 0.0)
            female_prof = female.skills.get(skill, 0.0)
            text.append(f"  {skill:18}", style="dim")
            text.append(f"{male_prof:.1f}", style="cyan" if male_prof > 0 else "dim")
            text.append("  vs  ")
            text.append(
                f"{female_prof:.1f}\n", style="magenta" if female_prof > 0 else "dim"
            )
    else:
        text.append("  None\n", style="dim")

    text.append("\n")

    # Tools
    text.append("TOOLS:\n", style="bold")
    shared_tools = set(male.tools) & set(female.tools)
    male_only = set(male.tools) - shared_tools
    female_only = set(female.tools) - shared_tools

    if shared_tools:
        text.append(f"  Shared: {', '.join(sorted(shared_tools))}\n", style="green")
    if male_only:
        text.append(f"  {male.name}: {', '.join(sorted(male_only))}\n", style="cyan")
    if female_only:
        text.append(
            f"  {female.name}: {', '.join(sorted(female_only))}\n", style="magenta"
        )
    if not male.tools and not female.tools:
        text.append("  None\n", style="dim")

    return Panel(text, title="🔍 Agent Inspector", border_style="yellow")

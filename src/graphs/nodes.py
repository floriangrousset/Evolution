"""Graph node implementations for Evolution simulator."""

import asyncio
import random
import time
from collections import defaultdict

from ..agents.base import Person, find_person_by_id, get_children, get_singles
from ..agents.traits import (
    inherit_big_five_traits,
    inherit_skills,
    inherit_tools,
)
from ..state.types import AgentMessage, EvolutionState, TraitSnapshot, calculate_population_stats
from .attraction import greedy_matching, calculate_trait_distance


async def age_children_node(state: EvolutionState) -> dict:
    """Check all children and transition them to adults if old enough.

    Args:
        state: Current evolution state.

    Returns:
        Dictionary with updated messages.
    """
    messages = []
    current_time = time.time()
    aging_seconds = state["config"].aging_seconds

    # Get all children
    children = get_children(state["population"])

    # Check each child's age
    for child in children:
        age_seconds = current_time - child.birth_time
        if age_seconds >= aging_seconds:
            # Transition to adult
            child.become_adult()
            messages.append(
                AgentMessage(
                    type="adult",
                    content=f"{child.name} ({child.get_short_name()}) has matured to adulthood",
                    timestamp=current_time,
                    person_id=child.id,
                )
            )

    return {"messages": messages}


async def find_mates_node(state: EvolutionState) -> dict:
    """Find mates for unpaired adults using attraction algorithm.

    Args:
        state: Current evolution state.

    Returns:
        Dictionary with updated couples, singles, and messages.
    """
    messages = []
    current_time = time.time()

    # Check population limit
    if len(state["population"]) >= state["config"].max_population:
        messages.append(
            AgentMessage(
                type="system",
                content=f"Population limit ({state['config'].max_population}) reached. No new couples formed.",
                timestamp=current_time,
                person_id=None,
            )
        )
        return {"messages": messages}

    # Get unpaired adults - returns Person objects, not IDs
    singles = get_singles(state["population"])
    males = singles["male"]  # List of Person objects
    females = singles["female"]  # List of Person objects

    # Find best matches using greedy algorithm
    matches = greedy_matching(males, females, min_compatibility=30.0)

    # Form couples and update state
    new_couples = []
    for male, female, score in matches:
        # Set partners
        male.set_partner(female.id)
        female.set_partner(male.id)

        # Add to couples list (as IDs)
        new_couples.append((male.id, female.id))

        # Log event
        messages.append(
            AgentMessage(
                type="couple",
                content=f"{male.name} ♥ {female.name} formed a couple (compatibility: {score:.1f})",
                timestamp=current_time,
                person_id=male.id,
            )
        )

    # Update singles lists - convert remaining unpaired Person objects to IDs
    paired_male_ids = {male.id for male, _, _ in matches}
    paired_female_ids = {female.id for _, female, _ in matches}

    updated_singles = {
        "male": [p.id for p in males if p.id not in paired_male_ids],
        "female": [p.id for p in females if p.id not in paired_female_ids],
    }

    return {
        "couples": state["couples"] + new_couples,
        "singles": updated_singles,
        "messages": messages,
    }


async def reproduce_node(state: EvolutionState) -> dict:
    """Create offspring for all couples.

    Args:
        state: Current evolution state.

    Returns:
        Dictionary with new population members and messages.
    """
    messages = []
    new_children = []
    current_time = time.time()
    mutation_rate = state["config"].mutation_rate

    # Check population limit
    if len(state["population"]) >= state["config"].max_population:
        return {"messages": [], "population": []}

    # For each couple, create 1-3 children
    for father_id, mother_id in state["couples"]:
        father = find_person_by_id(state["population"], father_id)
        mother = find_person_by_id(state["population"], mother_id)

        if not father or not mother:
            continue

        # Random number of children (1-3)
        num_children = random.randint(1, 3)

        # Check if we'd exceed population limit
        remaining_capacity = state["config"].max_population - len(
            state["population"]
        ) - len(new_children)
        num_children = min(num_children, remaining_capacity)

        if num_children <= 0:
            break

        for _ in range(num_children):
            # Randomly determine child gender
            child_gender = random.choice(["male", "female"])

            # Inherit traits from parents
            inherited_traits = inherit_big_five_traits(
                father, mother, mutation_rate
            )

            # Inherit skills
            inherited_skills = inherit_skills(father, mother, mutation_rate)

            # Inherit tools
            inherited_tools = inherit_tools(father, mother)

            # Create child
            child = Person(
                gender=child_gender,
                age_stage="child",
                generation=state["generation_number"] + 1,
                birth_time=current_time,
                parent_ids=(father.id, mother.id),
                openness=inherited_traits["openness"],
                conscientiousness=inherited_traits["conscientiousness"],
                extraversion=inherited_traits["extraversion"],
                agreeableness=inherited_traits["agreeableness"],
                neuroticism=inherited_traits["neuroticism"],
                skills=inherited_skills,
                tools=inherited_tools,
            )

            # Add child to parents' children lists
            father.add_child(child.id)
            mother.add_child(child.id)

            new_children.append(child)

            # Log birth event
            messages.append(
                AgentMessage(
                    type="birth",
                    content=f"{child.name} ({child.get_short_name()}) born to {father.name} ♥ {mother.name}",
                    timestamp=current_time,
                    person_id=child.id,
                )
            )

    return {
        "population": new_children,
        "messages": messages,
        "generation_number": state["generation_number"] + 1
        if new_children
        else state["generation_number"],
    }


async def update_singles_node(state: EvolutionState) -> dict:
    """Rebuild singles pool from current population.

    Args:
        state: Current evolution state.

    Returns:
        Dictionary with updated singles.
    """
    # Recalculate singles from scratch
    singles = get_singles(state["population"])

    # Convert Person objects to IDs
    singles_ids = {
        "male": [p.id for p in singles["male"]],
        "female": [p.id for p in singles["female"]],
    }

    return {"singles": singles_ids}


async def increment_cycle_node(state: EvolutionState) -> dict:
    """Increment cycle counter and update timing.

    Args:
        state: Current evolution state.

    Returns:
        Dictionary with updated cycle_count and last_cycle_time.
    """
    return {"cycle_count": state["cycle_count"] + 1, "last_cycle_time": time.time()}


def limit_conversations_per_person(
    matches: list[tuple[Person, Person]], max_per_person: int
) -> list[tuple[Person, Person]]:
    """Cap conversations to prevent popular agents from monopolizing.

    Args:
        matches: List of (male, female) potential pairs.
        max_per_person: Maximum dates per person.

    Returns:
        Filtered list of pairs where no person exceeds max_per_person dates.
    """
    counts = defaultdict(int)
    limited = []
    for m, f in matches:
        if counts[m.id] < max_per_person and counts[f.id] < max_per_person:
            limited.append((m, f))
            counts[m.id] += 1
            counts[f.id] += 1
    return limited


def chunks(lst: list, n: int):
    """Yield successive n-sized chunks from lst.

    Args:
        lst: List to chunk.
        n: Chunk size.

    Yields:
        Chunks of size n.
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def llm_speed_dating_node(state: EvolutionState) -> dict:
    """LLM-powered speed dating conversations for mate selection.

    This node replaces deterministic matching with conversational agents.
    Each person becomes a LangChain agent that engages in 4-turn speed dating
    conversations, then independently scores compatibility.

    Performance optimizations:
    - Pre-filter potential pairs by trait distance
    - Limit conversations per person per cycle
    - Run conversations in parallel batches

    Args:
        state: Current evolution state.

    Returns:
        Dictionary with updated couples, singles, messages, and conversation_transcripts.
    """
    from ...agents.conversations.conversation_manager import conduct_speed_date

    # Get singles
    singles = get_singles(state["population"])
    males = [p for p in singles if p.gender == "male"]
    females = [p for p in singles if p.gender == "female"]

    if not males or not females:
        return {
            "messages": [
                AgentMessage(
                    type="system",
                    content="No eligible singles for speed dating.",
                    timestamp=time.time(),
                )
            ]
        }

    # Pre-filter with trait distance (performance optimization)
    potential_pairs = [
        (m, f)
        for m in males
        for f in females
        if calculate_trait_distance(m, f) < state["config"].pre_filter_trait_distance
    ]

    # Limit conversations per person
    capped_pairs = limit_conversations_per_person(
        potential_pairs, state["config"].max_dates_per_cycle
    )

    if not capped_pairs:
        return {
            "messages": [
                AgentMessage(
                    type="system",
                    content="No compatible pairs found after pre-filtering.",
                    timestamp=time.time(),
                )
            ]
        }

    # Run conversations in parallel batches
    all_results = []
    batch_size = state["config"].max_parallel_conversations

    for batch in chunks(capped_pairs, batch_size):
        results = await asyncio.gather(
            *[conduct_speed_date(m, f, state["config"]) for m, f in batch]
        )
        all_results.extend(results)

    # Sort by final score (average of both agents' scores)
    all_results.sort(key=lambda r: r.final_score, reverse=True)

    # Greedy matching: pair highest scoring couples first
    new_couples = []
    paired_males = set()
    paired_females = set()
    messages = []

    for result in all_results:
        # Skip if either person is already paired
        if result.male.id in paired_males or result.female.id in paired_females:
            continue

        # Skip if below minimum compatibility threshold
        if result.final_score < state["config"].min_compatibility:
            continue

        # Form couple
        result.male.set_partner(result.female.id)
        result.female.set_partner(result.male.id)
        new_couples.append((result.male.id, result.female.id))
        paired_males.add(result.male.id)
        paired_females.add(result.female.id)

        # Log the match
        messages.append(
            AgentMessage(
                type="couple",
                content=f"{result.male.name} ♥ {result.female.name} (compatibility: {result.final_score:.0f}/100)",
                timestamp=time.time(),
            )
        )

    # Update singles pool
    all_person_ids = {p.id for p in state["population"]}
    coupled_ids = {pid for couple in state["couples"] + new_couples for pid in couple}
    single_ids = all_person_ids - coupled_ids

    singles_by_gender = {"male": [], "female": []}
    for person in state["population"]:
        if person.id in single_ids:
            singles_by_gender[person.gender].append(person.id)

    return {
        "couples": state["couples"] + new_couples,
        "singles": singles_by_gender,
        "messages": messages,
        "conversation_transcripts": all_results,
    }


async def capture_trait_snapshot_node(state: EvolutionState) -> dict:
    """Capture current population trait averages for evolution tracking.

    Args:
        state: Current evolution state.

    Returns:
        Dictionary with new trait snapshot appended to trait_history.
    """
    stats = calculate_population_stats(state)

    snapshot = TraitSnapshot(
        generation=state["generation_number"],
        timestamp=time.time(),
        avg_openness=stats["avg_traits"]["openness"],
        avg_conscientiousness=stats["avg_traits"]["conscientiousness"],
        avg_extraversion=stats["avg_traits"]["extraversion"],
        avg_agreeableness=stats["avg_traits"]["agreeableness"],
        avg_neuroticism=stats["avg_traits"]["neuroticism"],
        population_size=stats["total_population"],
    )

    return {"trait_history": state["trait_history"] + [snapshot]}

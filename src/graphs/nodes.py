"""Graph node implementations for Evolution simulator."""

import random
import time

from ..agents.base import Person, find_person_by_id, get_children, get_singles
from ..agents.traits import (
    inherit_big_five_traits,
    inherit_skills,
    inherit_tools,
)
from ..state.types import AgentMessage, EvolutionState
from .attraction import greedy_matching


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

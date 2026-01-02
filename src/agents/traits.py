"""Trait inheritance and mutation system for Evolution simulator."""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Person


# Big Five Trait Names
BIG_FIVE_TRAITS = [
    "openness",
    "conscientiousness",
    "extraversion",
    "agreeableness",
    "neuroticism",
]


def inherit_trait(
    parent1_val: float, parent2_val: float, mutation_rate: float = 1.0
) -> float:
    """Inherit a trait value from two parents with Gaussian mutation.

    The child's trait is the average of both parents' values plus a random
    mutation from a Gaussian distribution (mean=0, stdev=mutation_rate).

    Args:
        parent1_val: First parent's trait value (0-10).
        parent2_val: Second parent's trait value (0-10).
        mutation_rate: Standard deviation for Gaussian mutation (default 1.0).

    Returns:
        Child's trait value, clamped to valid range [0, 10].
    """
    avg = (parent1_val + parent2_val) / 2
    mutation = random.gauss(0, mutation_rate)
    child_val = avg + mutation
    return max(0.0, min(10.0, child_val))


def inherit_big_five_traits(
    father: "Person", mother: "Person", mutation_rate: float = 1.0
) -> dict[str, float]:
    """Inherit Big Five personality traits from both parents.

    Args:
        father: Father person.
        mother: Mother person.
        mutation_rate: Standard deviation for mutations.

    Returns:
        Dictionary of trait names to values for the child.
    """
    return {
        "openness": inherit_trait(father.openness, mother.openness, mutation_rate),
        "conscientiousness": inherit_trait(
            father.conscientiousness, mother.conscientiousness, mutation_rate
        ),
        "extraversion": inherit_trait(
            father.extraversion, mother.extraversion, mutation_rate
        ),
        "agreeableness": inherit_trait(
            father.agreeableness, mother.agreeableness, mutation_rate
        ),
        "neuroticism": inherit_trait(
            father.neuroticism, mother.neuroticism, mutation_rate
        ),
    }


def inherit_skills(
    father: "Person", mother: "Person", mutation_rate: float = 1.0
) -> dict[str, float]:
    """Inherit skills from both parents with some variation.

    Child receives a subset of parent skills, with proficiency inherited
    from the parent who has that skill (or averaged if both have it).

    Args:
        father: Father person.
        mother: Mother person.
        mutation_rate: Standard deviation for skill proficiency mutations.

    Returns:
        Dictionary of skill names to proficiency values for the child.
    """
    child_skills = {}

    # Combine all skills from both parents
    all_skills = set(father.skills.keys()) | set(mother.skills.keys())

    for skill in all_skills:
        # Randomly decide if child inherits this skill (70% chance)
        if random.random() < 0.7:
            father_prof = father.skills.get(skill, 0)
            mother_prof = mother.skills.get(skill, 0)

            # If both have the skill, average them
            if father_prof > 0 and mother_prof > 0:
                child_prof = inherit_trait(father_prof, mother_prof, mutation_rate * 0.5)
            # Otherwise, use the parent who has it
            elif father_prof > 0:
                child_prof = father_prof + random.gauss(0, mutation_rate * 0.5)
            else:
                child_prof = mother_prof + random.gauss(0, mutation_rate * 0.5)

            child_skills[skill] = max(0.0, min(10.0, child_prof))

    return child_skills


def inherit_tools(father: "Person", mother: "Person") -> list[str]:
    """Inherit tools from both parents.

    Child has access to all tools that either parent has, representing
    knowledge transfer.

    Args:
        father: Father person.
        mother: Mother person.

    Returns:
        List of tool names the child has access to.
    """
    # Combine tools from both parents (union)
    child_tools = list(set(father.tools) | set(mother.tools))
    return child_tools


def generate_random_skills(
    available_skills: list[str], num_skills: int = 3
) -> dict[str, float]:
    """Generate random skills for initial population.

    Args:
        available_skills: List of possible skill names.
        num_skills: Number of skills to assign (default 3).

    Returns:
        Dictionary of skill names to random proficiency values (3-9 range).
    """
    if not available_skills:
        return {}

    # Select random skills
    num_skills = min(num_skills, len(available_skills))
    selected_skills = random.sample(available_skills, num_skills)

    # Assign random proficiency (favor mid-to-high values)
    return {skill: random.uniform(3.0, 9.0) for skill in selected_skills}


def generate_random_tools(available_tools: list[str], num_tools: int = 2) -> list[str]:
    """Generate random tools for initial population.

    Args:
        available_tools: List of possible tool names.
        num_tools: Number of tools to assign (default 2).

    Returns:
        List of tool names.
    """
    if not available_tools:
        return []

    num_tools = min(num_tools, len(available_tools))
    return random.sample(available_tools, num_tools)


def mutate_trait(value: float, mutation_rate: float = 1.0) -> float:
    """Apply mutation to a single trait value.

    Args:
        value: Original trait value.
        mutation_rate: Standard deviation for mutation.

    Returns:
        Mutated value, clamped to [0, 10].
    """
    mutation = random.gauss(0, mutation_rate)
    new_value = value + mutation
    return max(0.0, min(10.0, new_value))


def calculate_trait_distance(person1: "Person", person2: "Person") -> float:
    """Calculate Euclidean distance between two persons' Big Five traits.

    Lower distance means more similar personalities.

    Args:
        person1: First person.
        person2: Second person.

    Returns:
        Euclidean distance in 5D trait space.
    """
    traits1 = person1.get_traits_vector()
    traits2 = person2.get_traits_vector()

    squared_diffs = [(t1 - t2) ** 2 for t1, t2 in zip(traits1, traits2)]
    return sum(squared_diffs) ** 0.5


def get_trait_summary(person: "Person") -> str:
    """Get a human-readable summary of a person's Big Five traits.

    Args:
        person: Person to summarize.

    Returns:
        String summary like "O:7.2 C:5.1 E:8.3 A:6.4 N:3.2"
    """
    return (
        f"O:{person.openness:.1f} C:{person.conscientiousness:.1f} "
        f"E:{person.extraversion:.1f} A:{person.agreeableness:.1f} "
        f"N:{person.neuroticism:.1f}"
    )

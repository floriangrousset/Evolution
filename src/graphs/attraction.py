"""Attraction algorithm and mate selection for Evolution simulator."""

from typing import TYPE_CHECKING

from ..agents.traits import calculate_trait_distance

if TYPE_CHECKING:
    from ..agents.base import Person


def calculate_compatibility(person_a: "Person", person_b: "Person") -> float:
    """Calculate compatibility score (0-100) between two persons.

    Compatibility is based on three factors:
    1. Trait similarity (60% weight): Lower trait distance = higher score
    2. Skill complementarity (25% weight): Different skills = higher score
    3. Tool overlap (15% weight): Shared tools = higher score

    Args:
        person_a: First person.
        person_b: Second person.

    Returns:
        Compatibility score from 0 to 100.
    """
    # Must be opposite genders
    if person_a.gender == person_b.gender:
        return 0.0

    # 1. Trait similarity score
    # Euclidean distance in 5D space ranges from 0 (identical) to ~22 (max difference)
    # We want lower distance to give higher score
    trait_distance = calculate_trait_distance(person_a, person_b)
    trait_score = max(0, 100 - trait_distance * 10)  # Scale so max distance ~0 score

    # 2. Skill complementarity score
    # Partners with different skills are more valuable (complementary)
    skills_a = set(person_a.skills.keys())
    skills_b = set(person_b.skills.keys())
    shared_skills = skills_a & skills_b
    unique_skills = len(skills_a) + len(skills_b) - len(shared_skills)
    skill_score = unique_skills * 5  # Each unique skill adds 5 points

    # 3. Tool overlap score
    # Shared tools indicate compatible lifestyles/knowledge
    tools_a = set(person_a.tools)
    tools_b = set(person_b.tools)
    shared_tools = tools_a & tools_b
    tool_score = len(shared_tools) * 10  # Each shared tool adds 10 points

    # Weighted combination
    total_score = trait_score * 0.6 + skill_score * 0.25 + tool_score * 0.15

    # Clamp to valid range
    return min(100.0, max(0.0, total_score))


def find_best_matches(
    males: list["Person"], females: list["Person"]
) -> list[tuple["Person", "Person", float]]:
    """Find best matches between males and females using greedy algorithm.

    Args:
        males: List of male persons.
        females: List of female persons.

    Returns:
        List of (male, female, compatibility_score) tuples, sorted by score descending.
    """
    if not males or not females:
        return []

    # Calculate all pairwise compatibility scores
    matches = []
    for male in males:
        for female in females:
            score = calculate_compatibility(male, female)
            matches.append((male, female, score))

    # Sort by compatibility score (highest first)
    matches.sort(key=lambda x: x[2], reverse=True)

    return matches


def greedy_matching(
    males: list["Person"], females: list["Person"], min_compatibility: float = 0.0
) -> list[tuple["Person", "Person", float]]:
    """Perform greedy matching to form couples.

    Iteratively pairs the highest-scoring unpaired male-female combination
    until no more valid pairs can be formed.

    Args:
        males: List of unpaired male persons.
        females: List of unpaired female persons.
        min_compatibility: Minimum compatibility score required (default 0.0).

    Returns:
        List of (male, female, compatibility_score) tuples representing couples.
    """
    if not males or not females:
        return []

    couples = []
    available_males = set(m.id for m in males)
    available_females = set(f.id for f in females)

    # Get all possible matches sorted by score
    all_matches = find_best_matches(males, females)

    # Greedily select best available matches
    for male, female, score in all_matches:
        # Skip if below minimum compatibility
        if score < min_compatibility:
            break

        # Skip if either person is already paired
        if male.id not in available_males or female.id not in available_females:
            continue

        # Pair them
        couples.append((male, female, score))
        available_males.remove(male.id)
        available_females.remove(female.id)

        # Stop if no more people to pair
        if not available_males or not available_females:
            break

    return couples


def get_compatibility_stats(
    matches: list[tuple["Person", "Person", float]]
) -> dict[str, float]:
    """Calculate statistics about compatibility scores.

    Args:
        matches: List of (male, female, score) tuples.

    Returns:
        Dictionary with min, max, average, and median compatibility scores.
    """
    if not matches:
        return {"min": 0.0, "max": 0.0, "avg": 0.0, "median": 0.0}

    scores = [score for _, _, score in matches]
    scores.sort()

    return {
        "min": scores[0],
        "max": scores[-1],
        "avg": sum(scores) / len(scores),
        "median": scores[len(scores) // 2],
    }

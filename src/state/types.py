"""State type definitions for Evolution simulator using LangGraph."""

import operator
from dataclasses import dataclass
from typing import Annotated, Literal, TypedDict

from ..agents.base import Person
from ..config import SimulationConfig


@dataclass
class AgentMessage:
    """Message representing a lifecycle event or agent action."""

    type: Literal["birth", "adult", "couple", "system"]
    content: str
    timestamp: float
    person_id: str | None = None


@dataclass
class SpeedDatingMessage:
    """Message in a speed dating conversation."""

    speaker_id: str
    speaker_name: str
    content: str
    timestamp: float
    turn_number: int  # 1-4


@dataclass
class SpeedDatingResult:
    """Result of a speed dating conversation between two persons."""

    male: Person
    female: Person
    messages: list[SpeedDatingMessage]
    male_score: int  # 0-100
    female_score: int  # 0-100
    final_score: float  # Average of both scores
    male_reasoning: str
    female_reasoning: str
    timestamp: float


@dataclass
class TraitSnapshot:
    """Snapshot of population trait averages at a point in time."""

    generation: int
    timestamp: float
    avg_openness: float
    avg_conscientiousness: float
    avg_extraversion: float
    avg_agreeableness: float
    avg_neuroticism: float
    population_size: int


def add_persons(existing: list[Person], new: list[Person]) -> list[Person]:
    """State reducer to accumulate persons in population.

    Args:
        existing: Current population list.
        new: New persons to add.

    Returns:
        Combined list of all persons.
    """
    return existing + new


def add_messages(
    existing: list[AgentMessage], new: list[AgentMessage]
) -> list[AgentMessage]:
    """State reducer to accumulate messages.

    Args:
        existing: Current message list.
        new: New messages to add.

    Returns:
        Combined list of all messages.
    """
    return existing + new


class EvolutionState(TypedDict):
    """State for the Evolution simulation graph.

    This state is passed through all nodes in the LangGraph and tracks
    the complete simulation state including population, relationships,
    and lifecycle events.
    """

    # Population
    population: Annotated[list[Person], add_persons]

    # Couples (stored as tuples of person IDs)
    couples: list[tuple[str, str]]  # [(father_id, mother_id), ...]

    # Singles (grouped by gender)
    singles: dict[str, list[str]]  # {"male": [id1, id2], "female": [id3, id4]}

    # Generation tracking
    generation_number: int
    cycle_count: int

    # Timing
    simulation_start_time: float
    last_cycle_time: float

    # Messages/Events
    messages: Annotated[list[AgentMessage], add_messages]

    # LLM Mating - Conversation Transcripts
    conversation_transcripts: list[SpeedDatingResult]

    # LLM Mating - Trait Evolution History
    trait_history: list[TraitSnapshot]

    # Configuration
    config: SimulationConfig


class PopulationStats(TypedDict):
    """Statistics about the current population."""

    total_population: int
    num_adults: int
    num_children: int
    num_males: int
    num_females: int
    num_couples: int
    generations: dict[int, int]  # generation_number -> count
    avg_traits: dict[str, float]  # trait_name -> average value


def calculate_population_stats(state: EvolutionState) -> PopulationStats:
    """Calculate statistics about the population.

    Args:
        state: Current evolution state.

    Returns:
        PopulationStats with calculated values.
    """
    population = state["population"]

    # Basic counts
    total_population = len(population)
    num_adults = sum(1 for p in population if p.age_stage == "adult")
    num_children = total_population - num_adults
    num_males = sum(1 for p in population if p.gender == "male")
    num_females = sum(1 for p in population if p.gender == "female")
    num_couples = len(state["couples"])

    # Generation breakdown
    generations: dict[int, int] = {}
    for person in population:
        gen = person.generation
        generations[gen] = generations.get(gen, 0) + 1

    # Average traits
    if total_population > 0:
        avg_traits = {
            "openness": sum(p.openness for p in population) / total_population,
            "conscientiousness": sum(p.conscientiousness for p in population)
            / total_population,
            "extraversion": sum(p.extraversion for p in population) / total_population,
            "agreeableness": sum(p.agreeableness for p in population)
            / total_population,
            "neuroticism": sum(p.neuroticism for p in population) / total_population,
        }
    else:
        avg_traits = {
            "openness": 0.0,
            "conscientiousness": 0.0,
            "extraversion": 0.0,
            "agreeableness": 0.0,
            "neuroticism": 0.0,
        }

    return {
        "total_population": total_population,
        "num_adults": num_adults,
        "num_children": num_children,
        "num_males": num_males,
        "num_females": num_females,
        "num_couples": num_couples,
        "generations": generations,
        "avg_traits": avg_traits,
    }

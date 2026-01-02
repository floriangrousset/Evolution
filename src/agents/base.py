"""Base agent model for Evolution simulator."""

import random
import time
from dataclasses import dataclass, field
from typing import Literal, Optional
from uuid import uuid4

import names


@dataclass
class Person:
    """Represents a person in the Evolution simulation.

    Each person has unique personality traits (Big Five), skills, and tools.
    Traits are inherited from parents with mutation for genetic diversity.
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = field(default_factory=lambda: names.get_full_name())
    gender: Literal["male", "female"] = "male"

    # Lifecycle
    age_stage: Literal["child", "adult"] = "child"
    generation: int = 0
    birth_time: float = field(default_factory=time.time)
    parent_ids: Optional[tuple[str, str]] = None  # (father_id, mother_id)

    # Big Five Personality Traits (0-10 scale)
    openness: float = field(default_factory=lambda: random.uniform(0, 10))
    conscientiousness: float = field(default_factory=lambda: random.uniform(0, 10))
    extraversion: float = field(default_factory=lambda: random.uniform(0, 10))
    agreeableness: float = field(default_factory=lambda: random.uniform(0, 10))
    neuroticism: float = field(default_factory=lambda: random.uniform(0, 10))

    # Skills (0-10 proficiency)
    skills: dict[str, float] = field(default_factory=dict)

    # Tools access
    tools: list[str] = field(default_factory=list)

    # Relationship tracking
    partner_id: Optional[str] = None
    children_ids: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate person attributes after initialization."""
        self._validate_traits()
        self._validate_skills()

    def _validate_traits(self):
        """Ensure all traits are within valid range (0-10)."""
        traits = [
            "openness",
            "conscientiousness",
            "extraversion",
            "agreeableness",
            "neuroticism",
        ]
        for trait in traits:
            value = getattr(self, trait)
            if not (0 <= value <= 10):
                setattr(self, trait, max(0, min(10, value)))

    def _validate_skills(self):
        """Ensure all skill values are within valid range (0-10)."""
        for skill, value in self.skills.items():
            if not (0 <= value <= 10):
                self.skills[skill] = max(0, min(10, value))

    def get_traits_vector(self) -> list[float]:
        """Return Big Five traits as a vector for distance calculations.

        Returns:
            List of trait values: [openness, conscientiousness, extraversion,
                                   agreeableness, neuroticism]
        """
        return [
            self.openness,
            self.conscientiousness,
            self.extraversion,
            self.agreeableness,
            self.neuroticism,
        ]

    def get_age_seconds(self) -> float:
        """Calculate person's age in seconds since birth.

        Returns:
            Age in seconds.
        """
        return time.time() - self.birth_time

    def add_child(self, child_id: str):
        """Add a child to this person's children list.

        Args:
            child_id: UUID of the child.
        """
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)

    def set_partner(self, partner_id: str):
        """Set this person's partner.

        Args:
            partner_id: UUID of the partner.
        """
        self.partner_id = partner_id

    def remove_partner(self):
        """Remove this person's partner (e.g., after breakup)."""
        self.partner_id = None

    def become_adult(self):
        """Transition from child to adult age stage."""
        self.age_stage = "adult"

    def __repr__(self) -> str:
        """Return a human-readable representation of the person."""
        tools_str = ",".join(self.tools) if self.tools else "none"
        return (
            f"{self.name} ({self.gender[0].upper()}-G{self.generation}-"
            f"{self.age_stage[0].upper()}) [Tools: {tools_str}]"
        )

    def get_short_name(self) -> str:
        """Return a short identifier for display purposes.

        Returns:
            Short name like "M-G0-A" for Male-Generation0-Adult
        """
        gender_char = self.gender[0].upper()
        age_char = self.age_stage[0].upper()
        return f"{gender_char}-G{self.generation}-{age_char}"


def find_person_by_id(population: list[Person], person_id: str) -> Optional[Person]:
    """Find a person in the population by their ID.

    Args:
        population: List of all persons.
        person_id: UUID to search for.

    Returns:
        The Person object if found, None otherwise.
    """
    for person in population:
        if person.id == person_id:
            return person
    return None


def get_adults(population: list[Person]) -> list[Person]:
    """Filter population to return only adults.

    Args:
        population: List of all persons.

    Returns:
        List of adults only.
    """
    return [p for p in population if p.age_stage == "adult"]


def get_children(population: list[Person]) -> list[Person]:
    """Filter population to return only children.

    Args:
        population: List of all persons.

    Returns:
        List of children only.
    """
    return [p for p in population if p.age_stage == "child"]


def get_singles(population: list[Person]) -> dict[str, list[Person]]:
    """Get all unpaired adults grouped by gender.

    Args:
        population: List of all persons.

    Returns:
        Dictionary with "male" and "female" keys, each containing list of
        unpaired adults of that gender.
    """
    adults = get_adults(population)
    singles = {"male": [], "female": []}

    for person in adults:
        if person.partner_id is None:
            singles[person.gender].append(person)

    return singles


def get_couples(population: list[Person]) -> list[tuple[Person, Person]]:
    """Get all coupled persons as (male, female) tuples.

    Args:
        population: List of all persons.

    Returns:
        List of (male, female) tuples for all couples.
    """
    couples = []
    processed = set()

    for person in population:
        if person.partner_id and person.id not in processed:
            partner = find_person_by_id(population, person.partner_id)
            if partner:
                if person.gender == "male":
                    couples.append((person, partner))
                else:
                    couples.append((partner, person))
                processed.add(person.id)
                processed.add(partner.id)

    return couples

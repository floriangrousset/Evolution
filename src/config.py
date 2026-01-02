"""Configuration management for Evolution simulator."""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class SimulationConfig:
    """Configuration for the Evolution simulation."""

    # API Configuration
    anthropic_api_key: str
    model_name: str = "claude-opus-4-5-20250514"

    # Timing Configuration
    generation_cycle_seconds: int = 60  # CHANGED from 10 for LLM mating
    aging_seconds: int = 10

    # Population Configuration
    max_population: int = 50

    # Genetics Configuration
    mutation_rate: float = 1.0

    # LLM Mating Configuration
    enable_llm_mating: bool = True
    max_dates_per_cycle: int = 5
    max_parallel_conversations: int = 10
    min_compatibility: float = 40.0
    max_conversation_turns: int = 2
    pre_filter_trait_distance: float = 10.0

    # Skills and Tools
    available_skills: list[str] = None
    available_tools: list[str] = None

    def __post_init__(self):
        """Set default values for list fields."""
        if self.available_skills is None:
            self.available_skills = [
                "hunting",
                "gathering",
                "crafting",
                "communication",
                "innovation",
                "teaching",
            ]

        if self.available_tools is None:
            self.available_tools = ["stone-tools", "fire", "calculator", "memory"]


def load_config() -> SimulationConfig:
    """Load configuration from environment variables.

    Returns:
        SimulationConfig: The loaded configuration.

    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get required API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is required. "
            "Please set it in your .env file or environment."
        )

    # Get optional configuration with defaults
    model_name = os.getenv("MODEL_NAME", "claude-opus-4-5-20250514")

    generation_cycle_seconds = int(os.getenv("GENERATION_CYCLE_SECONDS", "60"))
    aging_seconds = int(os.getenv("AGING_SECONDS", "10"))
    max_population = int(os.getenv("MAX_POPULATION", "50"))
    mutation_rate = float(os.getenv("MUTATION_RATE", "1.0"))

    # LLM Mating Configuration
    enable_llm_mating = os.getenv("ENABLE_LLM_MATING", "true").lower() in ("true", "1", "yes")
    max_dates_per_cycle = int(os.getenv("MAX_DATES_PER_CYCLE", "5"))
    max_parallel_conversations = int(os.getenv("MAX_PARALLEL_CONVERSATIONS", "10"))
    min_compatibility = float(os.getenv("MIN_COMPATIBILITY", "40.0"))
    max_conversation_turns = int(os.getenv("MAX_CONVERSATION_TURNS", "2"))
    pre_filter_trait_distance = float(os.getenv("PRE_FILTER_TRAIT_DISTANCE", "10.0"))

    # Parse skills and tools from comma-separated strings
    skills_str = os.getenv("AVAILABLE_SKILLS", "")
    tools_str = os.getenv("AVAILABLE_TOOLS", "")

    available_skills = (
        [s.strip() for s in skills_str.split(",") if s.strip()]
        if skills_str
        else None
    )
    available_tools = (
        [t.strip() for t in tools_str.split(",") if t.strip()] if tools_str else None
    )

    return SimulationConfig(
        anthropic_api_key=api_key,
        model_name=model_name,
        generation_cycle_seconds=generation_cycle_seconds,
        aging_seconds=aging_seconds,
        max_population=max_population,
        mutation_rate=mutation_rate,
        enable_llm_mating=enable_llm_mating,
        max_dates_per_cycle=max_dates_per_cycle,
        max_parallel_conversations=max_parallel_conversations,
        min_compatibility=min_compatibility,
        max_conversation_turns=max_conversation_turns,
        pre_filter_trait_distance=pre_filter_trait_distance,
        available_skills=available_skills,
        available_tools=available_tools,
    )


def validate_config(config: SimulationConfig) -> None:
    """Validate configuration values.

    Args:
        config: The configuration to validate.

    Raises:
        ValueError: If any configuration value is invalid.
    """
    if config.generation_cycle_seconds <= 0:
        raise ValueError("generation_cycle_seconds must be positive")

    if config.aging_seconds <= 0:
        raise ValueError("aging_seconds must be positive")

    if config.max_population <= 0:
        raise ValueError("max_population must be positive")

    if config.mutation_rate < 0:
        raise ValueError("mutation_rate must be non-negative")

    # LLM Mating Configuration Validation
    if config.max_dates_per_cycle <= 0:
        raise ValueError("max_dates_per_cycle must be positive")

    if config.max_parallel_conversations <= 0:
        raise ValueError("max_parallel_conversations must be positive")

    if not (0 <= config.min_compatibility <= 100):
        raise ValueError("min_compatibility must be between 0 and 100")

    if config.max_conversation_turns <= 0:
        raise ValueError("max_conversation_turns must be positive")

    if config.pre_filter_trait_distance < 0:
        raise ValueError("pre_filter_trait_distance must be non-negative")

    if not config.available_skills:
        raise ValueError("available_skills cannot be empty")

    if not config.available_tools:
        raise ValueError("available_tools cannot be empty")

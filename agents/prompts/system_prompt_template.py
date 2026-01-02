"""System prompt template generator for Evolution agents."""

import os
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from ...src.agents.base import Person

# Load personality descriptors
_DESCRIPTORS_PATH = Path(__file__).parent / "personality_descriptors.yaml"
with open(_DESCRIPTORS_PATH, "r") as f:
    PERSONALITY_DESCRIPTORS = yaml.safe_load(f)


def get_trait_level(value: float) -> str:
    """Determine trait level from numerical value.

    Args:
        value: Trait value (0-10).

    Returns:
        'low', 'medium', or 'high'.
    """
    if value < 3.5:
        return "low"
    elif value < 7.0:
        return "medium"
    else:
        return "high"


def generate_personality_block(person: "Person") -> str:
    """Generate natural language personality description.

    Args:
        person: Person to describe.

    Returns:
        Multi-line string describing personality traits.
    """
    traits = {
        "Openness": (person.openness, "openness"),
        "Conscientiousness": (person.conscientiousness, "conscientiousness"),
        "Extraversion": (person.extraversion, "extraversion"),
        "Agreeableness": (person.agreeableness, "agreeableness"),
        "Neuroticism": (person.neuroticism, "neuroticism"),
    }

    lines = []
    for trait_name, (value, key) in traits.items():
        level = get_trait_level(value)
        description = PERSONALITY_DESCRIPTORS[key][level]
        lines.append(f"  • {trait_name}: {description}")

    return "\n".join(lines)


def format_skills(skills: dict[str, float]) -> str:
    """Format skills dictionary for display.

    Args:
        skills: Dictionary of skill names to proficiency values.

    Returns:
        Comma-separated string of skills with proficiency levels.
    """
    if not skills:
        return "None"

    skill_strs = []
    for skill, prof in skills.items():
        if prof >= 7.0:
            level = "expert"
        elif prof >= 4.0:
            level = "proficient"
        else:
            level = "novice"
        skill_strs.append(f"{skill} ({level})")

    return ", ".join(skill_strs)


def format_tools(tools: list[str]) -> str:
    """Format tools list for display.

    Args:
        tools: List of tool names.

    Returns:
        Comma-separated string of tools.
    """
    if not tools:
        return "None"
    return ", ".join(tools)


def generate_system_prompt(person: "Person") -> str:
    """Generate complete system prompt for a Person agent.

    Args:
        person: Person to create prompt for.

    Returns:
        System prompt string ready for LLM.
    """
    personality_block = generate_personality_block(person)
    skills_str = format_skills(person.skills)
    tools_str = format_tools(person.tools)

    prompt = f"""You are {person.name}, a {person.age_stage} {person.gender} from Generation {person.generation}.

PERSONALITY:
{personality_block}

BACKGROUND:
  • Skills: {skills_str}
  • Tools: {tools_str}
  • Age Stage: {person.age_stage}

CURRENT SITUATION:
You're participating in a speed dating event to find a compatible life partner. This is a brief conversation where you'll exchange a few messages to get to know each other. Be authentic to your personality - respond naturally based on your traits, interests, and experiences.

GUIDELINES:
- Keep responses concise (2-3 sentences)
- Be genuine and true to your personality
- Show interest by asking questions or sharing relevant experiences
- Consider compatibility based on shared interests and complementary traits
- Respond naturally without over-explaining your personality
"""

    return prompt

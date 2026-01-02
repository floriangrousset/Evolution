"""Conversation manager for speed dating interactions."""

import time
from typing import TYPE_CHECKING

from ...state.types import SpeedDatingMessage, SpeedDatingResult
from .agent_factory import create_agent_for_person
from .scoring import get_compatibility_score_with_reasoning

if TYPE_CHECKING:
    from ..base import Person
    from ...config import SimulationConfig


async def conduct_speed_date(
    male: "Person", female: "Person", config: "SimulationConfig"
) -> SpeedDatingResult:
    """Conduct a speed dating conversation between two persons.

    The conversation follows this structure:
    - Turn 1: Male initiates
    - Turn 2: Female responds
    - Turn 3: Male responds
    - Turn 4: Female closes
    - Both agents then independently score the interaction

    Args:
        male: Male person in the conversation.
        female: Female person in the conversation.
        config: Simulation configuration.

    Returns:
        SpeedDatingResult with conversation and scores.
    """
    start_time = time.time()

    # Create agents
    male_agent = create_agent_for_person(male, config)
    female_agent = create_agent_for_person(female, config)

    messages = []

    # Turn 1: Male initiates
    male_intro_prompt = f"You're meeting {female.name} at a speed dating event. Introduce yourself and start the conversation naturally. Keep it brief (2-3 sentences)."
    msg1_content = await male_agent.ainvoke(male_intro_prompt)
    messages.append(
        SpeedDatingMessage(
            speaker_id=male.id,
            speaker_name=male.name,
            content=msg1_content,
            timestamp=time.time(),
            turn_number=1,
        )
    )

    # Turn 2: Female responds
    female_response_prompt = f"{male.name} says: \"{msg1_content}\"\n\nRespond to {male.name} naturally. Show interest and share something about yourself. Keep it brief (2-3 sentences)."
    msg2_content = await female_agent.ainvoke(female_response_prompt)
    messages.append(
        SpeedDatingMessage(
            speaker_id=female.id,
            speaker_name=female.name,
            content=msg2_content,
            timestamp=time.time(),
            turn_number=2,
        )
    )

    # Turn 3: Male responds
    male_response_prompt = f"{female.name} says: \"{msg2_content}\"\n\nRespond to {female.name} naturally. Ask a question or share more about yourself. Keep it brief (2-3 sentences)."
    msg3_content = await male_agent.ainvoke(male_response_prompt)
    messages.append(
        SpeedDatingMessage(
            speaker_id=male.id,
            speaker_name=male.name,
            content=msg3_content,
            timestamp=time.time(),
            turn_number=3,
        )
    )

    # Turn 4: Female closes
    female_closing_prompt = f"{male.name} says: \"{msg3_content}\"\n\nThis is the last exchange. Respond naturally and wrap up the conversation. Keep it brief (2-3 sentences)."
    msg4_content = await female_agent.ainvoke(female_closing_prompt)
    messages.append(
        SpeedDatingMessage(
            speaker_id=female.id,
            speaker_name=female.name,
            content=msg4_content,
            timestamp=time.time(),
            turn_number=4,
        )
    )

    # Get independent compatibility scores
    male_score, male_reasoning = await get_compatibility_score_with_reasoning(
        male_agent, female.name
    )
    female_score, female_reasoning = await get_compatibility_score_with_reasoning(
        female_agent, male.name
    )

    # Calculate final score (average of both)
    final_score = (male_score + female_score) / 2.0

    return SpeedDatingResult(
        male=male,
        female=female,
        messages=messages,
        male_score=male_score,
        female_score=female_score,
        final_score=final_score,
        male_reasoning=male_reasoning,
        female_reasoning=female_reasoning,
        timestamp=start_time,
    )

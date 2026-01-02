"""Scoring extraction and validation for compatibility assessment."""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent_factory import ConversationalAgent


def extract_reasoning(response: str) -> str:
    """Extract reasoning from scoring response.

    Args:
        response: Full response text from agent.

    Returns:
        Reasoning text, or default message if not found.
    """
    # Try to find REASONING: section
    reasoning_match = re.search(
        r"REASONING:\s*(.+?)(?=SCORE:|$)", response, re.DOTALL | re.IGNORECASE
    )

    if reasoning_match:
        reasoning = reasoning_match.group(1).strip()
        return reasoning

    # Fallback: use entire response if formatted incorrectly
    return response.strip()


def extract_score(response: str) -> int:
    """Extract numerical score from scoring response.

    Args:
        response: Full response text from agent.

    Returns:
        Score from 0-100, or 50 (neutral) if not found.
    """
    # Try to find SCORE: section with number
    score_match = re.search(r"SCORE:\s*(\d+)", response, re.IGNORECASE)

    if score_match:
        score = int(score_match.group(1))
        # Clamp to valid range
        return max(0, min(100, score))

    # Try to find any number in the response
    number_match = re.search(r"\b(\d+)\b", response)
    if number_match:
        score = int(number_match.group(1))
        # Only use if it looks like a score (0-100)
        if 0 <= score <= 100:
            return score

    # Default to neutral if parsing fails
    return 50


async def get_compatibility_score_with_reasoning(
    agent: "ConversationalAgent", partner_name: str
) -> tuple[int, str]:
    """Get compatibility score and reasoning from an agent.

    Args:
        agent: ConversationalAgent to query.
        partner_name: Name of the partner being assessed.

    Returns:
        Tuple of (score, reasoning).
    """
    from ..prompts.scoring_prompt import generate_scoring_prompt

    # Generate scoring prompt
    scoring_prompt = generate_scoring_prompt(partner_name)

    # Get response
    response = await agent.ainvoke(scoring_prompt)

    # Extract score and reasoning
    score = extract_score(response)
    reasoning = extract_reasoning(response)

    return score, reasoning


def validate_score(score: int) -> int:
    """Validate and clamp score to valid range.

    Args:
        score: Score to validate.

    Returns:
        Clamped score (0-100).
    """
    return max(0, min(100, score))

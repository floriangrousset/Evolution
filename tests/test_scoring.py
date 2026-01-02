"""Unit tests for scoring extraction and validation."""

import pytest
from unittest.mock import AsyncMock, Mock
from agents.conversations.scoring import (
    extract_reasoning,
    extract_score,
    validate_score,
    get_compatibility_score_with_reasoning,
)


def test_extract_reasoning_with_proper_format():
    """Test extracting reasoning from properly formatted response."""
    response = """REASONING: Alice has great communication skills and shares my interest in technology. We had a natural conversation flow and similar values.

SCORE: 78"""

    reasoning = extract_reasoning(response)
    assert "Alice has great communication skills" in reasoning
    assert "SCORE:" not in reasoning


def test_extract_reasoning_with_improper_format():
    """Test extracting reasoning when format is incorrect (fallback)."""
    response = "I think we're compatible because we both like coding. Maybe 75?"

    reasoning = extract_reasoning(response)
    assert reasoning == response.strip()


def test_extract_score_with_proper_format():
    """Test extracting score from properly formatted response."""
    response = """REASONING: Great match!

SCORE: 85"""

    score = extract_score(response)
    assert score == 85


def test_extract_score_with_standalone_number():
    """Test extracting score when only a number is present."""
    response = "I'd rate this 67 out of 100."

    score = extract_score(response)
    assert score == 67


def test_extract_score_with_invalid_number():
    """Test score extraction with number outside 0-100 range."""
    response = "SCORE: 150"

    score = extract_score(response)
    assert score == 100  # Clamped to max


def test_extract_score_with_no_number():
    """Test score extraction fallback when no number found."""
    response = "This was a great conversation!"

    score = extract_score(response)
    assert score == 50  # Default neutral score


def test_validate_score_within_range():
    """Test score validation for valid scores."""
    assert validate_score(0) == 0
    assert validate_score(50) == 50
    assert validate_score(100) == 100


def test_validate_score_clamping():
    """Test score validation clamps out-of-range values."""
    assert validate_score(-10) == 0
    assert validate_score(150) == 100
    assert validate_score(101) == 100


@pytest.mark.asyncio
async def test_get_compatibility_score_with_reasoning():
    """Test getting score and reasoning from agent."""
    # Mock agent
    mock_agent = AsyncMock()
    mock_agent.ainvoke.return_value = """REASONING: Bob is intelligent and kind. We share similar goals and values. The conversation was engaging.

SCORE: 82"""

    score, reasoning = await get_compatibility_score_with_reasoning(mock_agent, "Bob")

    # Verify results
    assert score == 82
    assert "Bob is intelligent and kind" in reasoning
    assert "SCORE:" not in reasoning

    # Verify agent was called with scoring prompt
    mock_agent.ainvoke.assert_called_once()
    call_args = mock_agent.ainvoke.call_args[0][0]
    assert "Bob" in call_args
    assert "compatibility" in call_args.lower()


def test_extract_score_edge_cases():
    """Test score extraction with various edge cases."""
    # Multiple numbers - should use first in SCORE: format
    response1 = "REASONING: 25 things I liked. SCORE: 75"
    assert extract_score(response1) == 75

    # Number at boundary
    response2 = "SCORE: 0"
    assert extract_score(response2) == 0

    # Whitespace handling
    response3 = "SCORE:    85   "
    assert extract_score(response3) == 85

    # Case insensitive
    response4 = "score: 65"
    assert extract_score(response4) == 65


def test_extract_reasoning_edge_cases():
    """Test reasoning extraction with various edge cases."""
    # Empty reasoning
    response1 = "REASONING:\n\nSCORE: 50"
    reasoning1 = extract_reasoning(response1)
    assert reasoning1 == ""

    # Multi-paragraph reasoning
    response2 = """REASONING: First paragraph about compatibility.

Second paragraph about shared interests.

Third paragraph about concerns.

SCORE: 68"""
    reasoning2 = extract_reasoning(response2)
    assert "First paragraph" in reasoning2
    assert "Second paragraph" in reasoning2
    assert "Third paragraph" in reasoning2
    assert "SCORE:" not in reasoning2

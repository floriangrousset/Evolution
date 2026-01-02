"""Unit tests for conversation manager and speed dating."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from agents.conversations.conversation_manager import conduct_speed_date
from src.agents.base import Person
from src.config import SimulationConfig
from src.state.types import SpeedDatingResult


@pytest.mark.asyncio
async def test_conduct_speed_date_basic_flow():
    """Test basic speed dating conversation flow."""
    # Create test persons
    male = Person(
        id="male-1",
        name="Tom",
        gender="male",
        generation=0,
        openness=7.0,
        conscientiousness=6.0,
        extraversion=8.0,
        agreeableness=7.5,
        neuroticism=4.0,
        skills={"python": 8.0},
        tools=["calculator"],
        age_stage="adult",
        birth_time=0.0,
    )

    female = Person(
        id="female-1",
        name="Sarah",
        gender="female",
        generation=0,
        openness=7.5,
        conscientiousness=6.5,
        extraversion=7.0,
        agreeableness=8.0,
        neuroticism=3.5,
        skills={"python": 7.0},
        tools=["calculator"],
        age_stage="adult",
        birth_time=0.0,
    )

    config = SimulationConfig(
        anthropic_api_key="test-key",
        model_name="claude-sonnet-4-5-20250929",
    )

    # Mock agent responses
    with patch("agents.conversations.conversation_manager.create_agent_for_person") as mock_create:
        # Mock male agent
        male_agent = AsyncMock()
        male_agent.ainvoke = AsyncMock()
        male_agent.ainvoke.side_effect = [
            "Hi Sarah! I'm Tom. I love programming and problem solving.",  # Turn 1
            "That's great! I work with data analysis too. What languages do you prefer?",  # Turn 3
            "REASONING: Sarah is intelligent and shares my technical interests. Great conversation flow.\n\nSCORE: 85",  # Male scoring
        ]

        # Mock female agent
        female_agent = AsyncMock()
        female_agent.ainvoke = AsyncMock()
        female_agent.ainvoke.side_effect = [
            "Hello Tom! Nice to meet you. I'm Sarah, I enjoy coding and data science.",  # Turn 2
            "I primarily use Python and R. It was nice chatting with you!",  # Turn 4
            "REASONING: Tom seems very knowledgeable and we have common interests in tech.\n\nSCORE: 82",  # Female scoring
        ]

        # Mock agent creation to return our mocked agents
        mock_create.side_effect = [male_agent, female_agent]

        # Conduct speed date
        result = await conduct_speed_date(male, female, config)

    # Verify result structure
    assert isinstance(result, SpeedDatingResult)
    assert result.male == male
    assert result.female == female

    # Verify 4 messages (4-turn conversation)
    assert len(result.messages) == 4
    assert result.messages[0].turn_number == 1
    assert result.messages[0].speaker_id == male.id
    assert result.messages[1].turn_number == 2
    assert result.messages[1].speaker_id == female.id
    assert result.messages[2].turn_number == 3
    assert result.messages[2].speaker_id == male.id
    assert result.messages[3].turn_number == 4
    assert result.messages[3].speaker_id == female.id

    # Verify scores
    assert result.male_score == 85
    assert result.female_score == 82
    assert result.final_score == 83.5  # Average

    # Verify reasoning
    assert "intelligent" in result.male_reasoning.lower()
    assert "knowledgeable" in result.female_reasoning.lower()


@pytest.mark.asyncio
async def test_conduct_speed_date_low_compatibility():
    """Test speed dating with low compatibility scores."""
    male = Person(
        id="male-2",
        name="Alex",
        gender="male",
        generation=0,
        openness=2.0,
        conscientiousness=9.0,
        extraversion=3.0,
        agreeableness=5.0,
        neuroticism=7.0,
        skills={},
        tools=[],
        age_stage="adult",
        birth_time=0.0,
    )

    female = Person(
        id="female-2",
        name="Emma",
        gender="female",
        generation=0,
        openness=9.0,
        conscientiousness=3.0,
        extraversion=9.0,
        agreeableness=8.0,
        neuroticism=2.0,
        skills={},
        tools=[],
        age_stage="adult",
        birth_time=0.0,
    )

    config = SimulationConfig(
        anthropic_api_key="test-key",
        model_name="claude-sonnet-4-5-20250929",
    )

    with patch("agents.conversations.conversation_manager.create_agent_for_person") as mock_create:
        # Mock agents with incompatible responses
        male_agent = AsyncMock()
        male_agent.ainvoke = AsyncMock()
        male_agent.ainvoke.side_effect = [
            "Hello.",
            "I prefer routine.",
            "REASONING: We seem to have very different personalities and interests.\n\nSCORE: 25",
        ]

        female_agent = AsyncMock()
        female_agent.ainvoke = AsyncMock()
        female_agent.ainvoke.side_effect = [
            "Hi! I love adventure and spontaneity!",
            "That's fine.",
            "REASONING: Alex seems too reserved for my liking. Not much chemistry.\n\nSCORE: 30",
        ]

        mock_create.side_effect = [male_agent, female_agent]

        result = await conduct_speed_date(male, female, config)

    # Verify low compatibility
    assert result.male_score == 25
    assert result.female_score == 30
    assert result.final_score == 27.5
    assert "different" in result.male_reasoning.lower()
    assert "reserved" in result.female_reasoning.lower()


@pytest.mark.asyncio
async def test_conduct_speed_date_high_compatibility():
    """Test speed dating with high compatibility scores."""
    male = Person(
        id="male-3",
        name="James",
        gender="male",
        generation=0,
        openness=8.5,
        conscientiousness=7.0,
        extraversion=8.0,
        agreeableness=9.0,
        neuroticism=3.0,
        skills={"music": 9.0, "art": 8.0},
        tools=["fire", "calculator"],
        age_stage="adult",
        birth_time=0.0,
    )

    female = Person(
        id="female-3",
        name="Olivia",
        gender="female",
        generation=0,
        openness=9.0,
        conscientiousness=7.5,
        extraversion=7.5,
        agreeableness=8.5,
        neuroticism=3.5,
        skills={"music": 8.5, "art": 9.0},
        tools=["fire", "calculator"],
        age_stage="adult",
        birth_time=0.0,
    )

    config = SimulationConfig(
        anthropic_api_key="test-key",
        model_name="claude-sonnet-4-5-20250929",
    )

    with patch("agents.conversations.conversation_manager.create_agent_for_person") as mock_create:
        # Mock agents with highly compatible responses
        male_agent = AsyncMock()
        male_agent.ainvoke = AsyncMock()
        male_agent.ainvoke.side_effect = [
            "Hi Olivia! I'm passionate about music and art. Do you share these interests?",
            "That's wonderful! I play guitar and paint as well. We have so much in common!",
            "REASONING: Olivia is incredibly creative and we share the same passions. Excellent chemistry and conversation.\n\nSCORE: 92",
        ]

        female_agent = AsyncMock()
        female_agent.ainvoke = AsyncMock()
        female_agent.ainvoke.side_effect = [
            "Hi James! Yes, I love music and art! I play piano and do watercolor painting.",
            "This has been such a delightful conversation! I'd love to continue getting to know you.",
            "REASONING: James is creative, warm, and we connect on multiple levels. Very excited about this match.\n\nSCORE: 95",
        ]

        mock_create.side_effect = [male_agent, female_agent]

        result = await conduct_speed_date(male, female, config)

    # Verify high compatibility
    assert result.male_score == 92
    assert result.female_score == 95
    assert result.final_score == 93.5
    assert len(result.messages) == 4
    assert "creative" in result.male_reasoning.lower()
    assert "excited" in result.female_reasoning.lower()


def test_speed_dating_message_structure():
    """Test that speed dating messages have correct structure."""
    from src.state.types import SpeedDatingMessage

    msg = SpeedDatingMessage(
        speaker_id="test-id",
        speaker_name="Test Name",
        content="Test content",
        timestamp=123.456,
        turn_number=1,
    )

    assert msg.speaker_id == "test-id"
    assert msg.speaker_name == "Test Name"
    assert msg.content == "Test content"
    assert msg.timestamp == 123.456
    assert msg.turn_number == 1

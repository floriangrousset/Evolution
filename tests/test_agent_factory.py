"""Unit tests for agent factory and conversational agents."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from agents.conversations.agent_factory import ConversationalAgent, create_agent_for_person
from agents.prompts.system_prompt_template import generate_system_prompt
from src.agents.base import Person
from src.config import SimulationConfig


def test_generate_system_prompt():
    """Test system prompt generation from Person traits."""
    person = Person(
        id="test-1",
        name="Alice",
        gender="female",
        generation=0,
        openness=8.5,
        conscientiousness=3.0,
        extraversion=6.5,
        agreeableness=9.0,
        neuroticism=2.5,
        skills={"python": 7.5, "cooking": 5.0},
        tools=["fire", "calculator"],
        age_stage="adult",
        birth_time=0.0,
    )

    prompt = generate_system_prompt(person)

    # Verify prompt contains key elements
    assert "Alice" in prompt
    assert "female" in prompt
    assert "Generation 0" in prompt
    assert "python" in prompt
    assert "cooking" in prompt
    assert "fire" in prompt
    assert "calculator" in prompt

    # Verify personality descriptors are included (high openness, low conscientiousness, etc.)
    assert "creative" in prompt.lower() or "curious" in prompt.lower()


def test_create_agent_for_person():
    """Test agent creation from Person object."""
    person = Person(
        id="test-2",
        name="Bob",
        gender="male",
        generation=0,
        openness=5.0,
        conscientiousness=5.0,
        extraversion=5.0,
        agreeableness=5.0,
        neuroticism=5.0,
        skills={},
        tools=[],
        age_stage="adult",
        birth_time=0.0,
    )

    config = SimulationConfig(
        anthropic_api_key="test-key",
        model_name="claude-sonnet-4-5-20250929",
    )

    agent = create_agent_for_person(person, config)

    # Verify agent properties
    assert isinstance(agent, ConversationalAgent)
    assert agent.person == person
    assert "Bob" in agent.system_prompt
    assert agent.llm is not None
    assert agent.conversation_history == []


@pytest.mark.asyncio
async def test_conversational_agent_ainvoke():
    """Test ConversationalAgent message handling."""
    person = Person(
        id="test-3",
        name="Charlie",
        gender="male",
        generation=0,
        openness=5.0,
        conscientiousness=5.0,
        extraversion=5.0,
        agreeableness=5.0,
        neuroticism=5.0,
        skills={},
        tools=[],
        age_stage="adult",
        birth_time=0.0,
    )

    # Mock LLM
    mock_llm = AsyncMock()
    mock_response = Mock()
    mock_response.content = "Hello! Nice to meet you."
    mock_llm.ainvoke.return_value = mock_response

    agent = ConversationalAgent(
        person=person,
        system_prompt="You are Charlie.",
        llm=mock_llm,
    )

    # Send message
    response = await agent.ainvoke("Hi there!")

    # Verify response
    assert response == "Hello! Nice to meet you."
    assert len(agent.conversation_history) == 2  # User message + AI response
    mock_llm.ainvoke.assert_called_once()


def test_conversational_agent_clear_history():
    """Test clearing conversation history."""
    person = Person(
        id="test-4",
        name="Diana",
        gender="female",
        generation=0,
        openness=5.0,
        conscientiousness=5.0,
        extraversion=5.0,
        agreeableness=5.0,
        neuroticism=5.0,
        skills={},
        tools=[],
        age_stage="adult",
        birth_time=0.0,
    )

    mock_llm = Mock()
    agent = ConversationalAgent(
        person=person,
        system_prompt="You are Diana.",
        llm=mock_llm,
    )

    # Add some history
    agent.conversation_history = ["message1", "message2"]

    # Clear history
    agent.clear_history()

    assert agent.conversation_history == []

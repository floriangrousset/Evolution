"""Agent factory for creating LangChain conversational agents from Person objects."""

from typing import TYPE_CHECKING

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

if TYPE_CHECKING:
    from ...src.agents.base import Person
    from ...src.config import SimulationConfig


class ConversationalAgent:
    """Wrapper for LangChain conversational agent."""

    def __init__(
        self,
        person: "Person",
        system_prompt: str,
        llm: ChatAnthropic,
    ):
        """Initialize conversational agent.

        Args:
            person: Person this agent represents.
            system_prompt: System prompt defining personality.
            llm: LangChain LLM instance.
        """
        self.person = person
        self.system_prompt = system_prompt
        self.llm = llm
        self.conversation_history = []

    async def ainvoke(self, user_message: str) -> str:
        """Send message and get response.

        Args:
            user_message: Message from other agent or system.

        Returns:
            Agent's response as string.
        """
        messages = [SystemMessage(content=self.system_prompt)]

        # Add conversation history
        for msg in self.conversation_history:
            messages.append(msg)

        # Add new user message
        messages.append(HumanMessage(content=user_message))

        # Get response
        response = await self.llm.ainvoke(messages)
        response_text = response.content

        # Update history
        self.conversation_history.append(HumanMessage(content=user_message))
        self.conversation_history.append(response)

        return response_text

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


def create_agent_for_person(
    person: "Person", config: "SimulationConfig"
) -> ConversationalAgent:
    """Create a conversational agent for a Person.

    Args:
        person: Person to create agent for.
        config: Simulation configuration with model settings.

    Returns:
        ConversationalAgent instance ready for conversation.
    """
    from ..prompts.system_prompt_template import generate_system_prompt

    # Generate personality-based system prompt
    system_prompt = generate_system_prompt(person)

    # Create LLM
    llm = ChatAnthropic(
        model=config.model_name,
        anthropic_api_key=config.anthropic_api_key,
        temperature=0.7,  # Some personality variability
        max_tokens=200,  # Keep responses concise
    )

    return ConversationalAgent(person=person, system_prompt=system_prompt, llm=llm)

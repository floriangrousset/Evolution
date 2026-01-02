"""Main entry point for Evolution simulator."""

import asyncio
import random
import sys
import time

from .agents.base import Person
from .agents.traits import generate_random_skills, generate_random_tools
from .cli.display import Display
from .config import load_config, validate_config
from .graphs.main_graph import create_evolution_graph
from .state.types import EvolutionState


def initialize_adam_and_eve(config) -> tuple[Person, Person]:
    """Create the first two people: Adam and Eve.

    Args:
        config: Simulation configuration.

    Returns:
        Tuple of (Adam, Eve).
    """
    # Generate random skills and tools for initial population
    adam_skills = generate_random_skills(config.available_skills, num_skills=3)
    eve_skills = generate_random_skills(config.available_skills, num_skills=3)

    adam_tools = generate_random_tools(config.available_tools, num_tools=2)
    eve_tools = generate_random_tools(config.available_tools, num_tools=2)

    adam = Person(
        name="Adam",
        gender="male",
        age_stage="adult",
        generation=0,
        birth_time=time.time(),
        parent_ids=None,
        openness=random.uniform(3, 9),
        conscientiousness=random.uniform(3, 9),
        extraversion=random.uniform(3, 9),
        agreeableness=random.uniform(3, 9),
        neuroticism=random.uniform(3, 9),
        skills=adam_skills,
        tools=adam_tools,
    )

    eve = Person(
        name="Eve",
        gender="female",
        age_stage="adult",
        generation=0,
        birth_time=time.time(),
        parent_ids=None,
        openness=random.uniform(3, 9),
        conscientiousness=random.uniform(3, 9),
        extraversion=random.uniform(3, 9),
        agreeableness=random.uniform(3, 9),
        neuroticism=random.uniform(3, 9),
        skills=eve_skills,
        tools=eve_tools,
    )

    return adam, eve


def initialize_state(config, adam: Person, eve: Person) -> EvolutionState:
    """Initialize the simulation state.

    Args:
        config: Simulation configuration.
        adam: First male person.
        eve: First female person.

    Returns:
        Initial EvolutionState.
    """
    current_time = time.time()

    return {
        "population": [adam, eve],
        "couples": [],
        "singles": {"male": [adam.id], "female": [eve.id]},
        "generation_number": 0,
        "cycle_count": 0,
        "simulation_start_time": current_time,
        "last_cycle_time": current_time,
        "messages": [],
        "config": config,
    }


async def run_simulation():
    """Main simulation loop."""
    # Load configuration
    try:
        config = load_config()
        validate_config(config)
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Initialize display
    display = Display()
    display.print_welcome()

    # Initialize Adam and Eve
    adam, eve = initialize_adam_and_eve(config)
    state = initialize_state(config, adam, eve)

    # Create evolution graph
    graph = create_evolution_graph()

    # Main simulation loop
    try:
        while True:
            # Run one cycle of the graph
            state = await graph.ainvoke(state)

            # Display current state
            display.render_full_display(state)

            # Wait for next cycle
            await asyncio.sleep(config.generation_cycle_seconds)

    except KeyboardInterrupt:
        display.print_goodbye(state)
        sys.exit(0)
    except Exception as e:
        print(f"\nError during simulation: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def main():
    """Entry point for the application."""
    asyncio.run(run_simulation())


if __name__ == "__main__":
    main()

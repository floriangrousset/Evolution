# Evolution

An agentic AI life evolution simulator using LangChain/LangGraph that demonstrates generational evolution through male/female agent interactions, reproduction, and trait inheritance.

## Overview

Evolution is a command-line application that simulates the evolution of a population of agents with distinct personalities, skills, and tools. The simulation demonstrates how traits are inherited and mutated across generations, how agents form couples based on compatibility, and how populations grow over time.

### Key Features

- **Agent-Based Simulation**: Each agent has unique Big Five personality traits (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism)
- **Genetic Inheritance**: Children inherit traits from both parents with natural mutation
- **Attraction Algorithm**: Agents form couples based on personality compatibility, skill complementarity, and tool overlap
- **Lifecycle Management**: Agents transition from child to adult, seek mates, and reproduce
- **ASCII Art Visualization**: Beautiful command-line interface with population grid and statistics
- **Configurable Parameters**: Customize generation cycles, aging duration, population limits, and mutation rates

## Tech Stack

- **Python** >= 3.11
- **LangGraph** >= 0.2.0 (orchestration framework)
- **LangChain** >= 0.3.0 (agent framework)
- **Anthropic** >= 0.40.0 (Claude AI integration)
- **Rich** >= 13.9.0 (CLI visualization)
- **Pydantic** >= 2.9.0 (data validation)

## Installation

### Prerequisites

- Python 3.11 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Setup

1. Clone the repository:
```bash
git clone https://github.com/floriangrousset/Evolution.git
cd Evolution
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Edit `.env` and add your Anthropic API key:
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

Run the simulation:
```bash
python -m src.main
```

The simulation will start with Adam and Eve (Generation 0) and display:
- Population grid showing all agents with their gender, generation, and age
- Lifecycle events (births, aging, couple formation)
- Statistics (population count, generation breakdown, couple count)

Press `Ctrl+C` to stop the simulation.

### Configuration

You can customize the simulation by editing the `.env` file:

```bash
# Timing
GENERATION_CYCLE_SECONDS=10  # Time between reproduction cycles
AGING_SECONDS=10             # Time for children to become adults

# Population
MAX_POPULATION=50            # Maximum population before mating stops

# Genetics
MUTATION_RATE=1.0           # Standard deviation for trait mutations

# Skills and Tools
AVAILABLE_SKILLS=hunting,gathering,crafting,communication,innovation,teaching
AVAILABLE_TOOLS=stone-tools,fire,calculator,memory
```

## Architecture

```
src/
├── main.py              # Entry point and event loop
├── config.py            # Configuration management
├── state/
│   └── types.py         # State definitions (TypedDict + Pydantic)
├── agents/
│   ├── base.py          # Person model
│   ├── prompts.py       # LLM prompt templates
│   └── traits.py        # Trait inheritance logic
├── graphs/
│   ├── main_graph.py    # LangGraph orchestration
│   ├── nodes.py         # Graph node implementations
│   └── attraction.py    # Compatibility scoring
├── lifecycle/
│   └── aging.py         # Age transition logic
└── cli/
    └── display.py       # ASCII art rendering
```

## How It Works

### Lifecycle

1. **Aging**: Children become adults after `AGING_SECONDS`
2. **Mate Selection**: Unpaired adults are matched based on compatibility scores
3. **Reproduction**: Couples create 1-3 children with inherited traits
4. **Trait Mutation**: Children's traits are averaged from parents with Gaussian mutation

### Attraction Algorithm

Compatibility is calculated using three factors:

- **Personality Similarity (60%)**: Euclidean distance in 5D Big Five trait space
- **Skill Complementarity (25%)**: Different skills increase compatibility
- **Tool Overlap (15%)**: Shared tools increase compatibility

### State Management

The simulation uses LangGraph for orchestration with TypedDict state management and custom reducers for accumulating population and messages across cycles.

## Development Status

**Current Phase**: Phase 1 - Foundation & Repository Setup ✅

### Completed
- ✅ Repository structure
- ✅ Configuration management
- ✅ Dependencies setup

### In Progress
- 🚧 Phase 2: Core Data Models & State Management
- 🚧 Phase 3: Attraction Algorithm & Mating Logic
- 🚧 Phase 4: Lifecycle Management
- 🚧 Phase 5: LangGraph Orchestration
- 🚧 Phase 6: ASCII Art Visualization

## Future Enhancements

- **Death Mechanism**: Implement lifespan and natural population turnover
- **LLM Integration**: Personality-based decision making via Claude
- **Environmental Factors**: Resource scarcity, disasters, seasons
- **Trait Evolution Tracking**: Charts showing trait distributions over time
- **Family Tree Visualization**: Detailed lineage tracking
- **Save/Load State**: Checkpoint simulation for pause/resume
- **Web Interface**: Gradio or Streamlit dashboard

## Contributing

Contributions are welcome! Please follow the gitflow branching model:
- `main` branch for releases
- `develop` branch for active development
- Feature branches off `develop`

## License

MIT License - See LICENSE file for details

## Acknowledgments

Inspired by the [Revolution](https://github.com/floriangrousset/Revolution) project and built with LangGraph for robust agent orchestration.

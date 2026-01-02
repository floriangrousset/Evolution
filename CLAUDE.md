# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Evolution is an agentic AI life evolution simulator that demonstrates generational evolution through agent interactions, reproduction, and trait inheritance. It uses LangGraph for orchestration and Claude AI via the Anthropic API.

## Essential Commands

### Running the Simulation
```bash
# Run the main simulation
python -m src.main

# Stop the simulation
Ctrl+C
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Then edit .env to add ANTHROPIC_API_KEY
```

## Architecture Overview

### State-Driven LangGraph Orchestration

The simulation uses LangGraph as its core orchestration framework with **TypedDict-based state management** (not Pydantic models for state). This is critical:

- **State Container**: `EvolutionState` (TypedDict) in `src/state/types.py` contains all simulation state
- **Custom Reducers**: Uses `add_persons` and `add_messages` reducers with `Annotated` types to accumulate population and messages across graph cycles
- **Immutable Updates**: Nodes return partial state updates that get merged via reducers

### Graph Flow (src/graphs/main_graph.py)

```
age_children → [conditional: population check]
                ├─> find_mates → reproduce → update_singles
                └─> update_singles (if at max population)
                     ↓
               increment_cycle → END
```

The graph runs continuously in an async loop, with each cycle:
1. Aging children to adults based on `AGING_SECONDS`
2. Matching unpaired adults into couples (if under `MAX_POPULATION`)
3. Reproduction: couples create 1-3 children with inherited traits
4. Updating singles lists

### Data Models

**Person (src/agents/base.py)**: Pydantic dataclass representing an agent with:
- Big Five personality traits (0-10 scale): openness, conscientiousness, extraversion, agreeableness, neuroticism
- Skills dictionary (0-10 proficiency)
- Tools list
- Lifecycle: age_stage ("child"/"adult"), generation, birth_time
- Relationships: partner_id, parent_ids, children_ids

**Important**: State uses TypedDict, but Person agents use dataclasses.

### Trait Inheritance (src/agents/traits.py)

Children inherit traits from both parents:
- Average of parent values with Gaussian mutation (`MUTATION_RATE` std dev)
- Skills: Inherit union of parent skills, averaged with mutation
- Tools: Probabilistically inherit each parent's tools (70% chance per tool)

### Attraction Algorithm (src/graphs/attraction.py)

Compatibility scoring (0-100) uses weighted factors:
- **60%**: Personality similarity (Euclidean distance in 5D trait space)
- **25%**: Skill complementarity (different skills = higher score)
- **15%**: Tool overlap (shared tools = higher score)

Couples form via greedy matching: highest-scoring unpaired male-female pairs.

## Configuration

All settings via `.env` file or environment variables (see `.env.example`):

- `ANTHROPIC_API_KEY` (required): Claude API key
- `MODEL_NAME`: Default "claude-opus-4-5-20250514"
- `GENERATION_CYCLE_SECONDS`: Time between reproduction cycles (default 10)
- `AGING_SECONDS`: Time for children to become adults (default 10)
- `MAX_POPULATION`: Population cap before mating stops (default 50)
- `MUTATION_RATE`: Std dev for trait mutations (default 1.0)
- `AVAILABLE_SKILLS`: Comma-separated skills list
- `AVAILABLE_TOOLS`: Comma-separated tools list

Config loaded in `src/config.py` via `load_config()`.

## Key Implementation Notes

### State Management
- Always return partial state updates from nodes (e.g., `{"population": [new_child]}`)
- Reducers handle accumulation automatically
- Never mutate state directly - LangGraph handles immutability

### Person Lifecycle
- Children born as age_stage="child" with generation = parent_generation + 1
- Aging handled in `src/lifecycle/aging.py` by checking `get_age_seconds()` against `AGING_SECONDS`
- Adults transition to singles pool when unpaired

### Finding Entities
- Use helper functions from `src/agents/base.py`: `find_person_by_id()`, `get_adults()`, `get_children()`, `get_singles()`, `get_couples()`
- Population is a flat list; relationships tracked via IDs

### CLI Visualization
- `src/cli/display.py` handles all terminal rendering using Rich library
- ASCII art grid shows agents with gender/generation/age indicators
- Real-time stats display

## Module Structure

```
src/
├── main.py              # Entry point: async event loop
├── config.py            # Environment config loading/validation
├── state/
│   └── types.py         # EvolutionState (TypedDict), reducers, stats
├── agents/
│   ├── base.py          # Person dataclass, helper functions
│   ├── traits.py        # Trait inheritance, mutation logic
│   └── prompts.py       # LLM prompt templates (unused currently)
├── graphs/
│   ├── main_graph.py    # LangGraph definition and flow
│   ├── nodes.py         # Node implementations (age/mate/reproduce)
│   └── attraction.py    # Compatibility scoring algorithms
├── lifecycle/
│   └── aging.py         # Age transition logic
└── cli/
    └── display.py       # Terminal UI with Rich
```

## Development Notes

- Python 3.11+ required
- No tests currently exist (tests/ directory is empty)
- LangGraph state must use TypedDict, not Pydantic BaseModel
- The simulator is currently fully functional with all phases complete (Phases 1-8)
- Future enhancements planned: death mechanism, LLM-driven decisions, environmental factors

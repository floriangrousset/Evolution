# 🧬 Evolution

> **Watch AI agents fall in love, have children, and evolve across generations!** 💕

An agentic AI life evolution simulator where each person is a **conversational LLM agent** with unique personality traits. Watch them go on speed dates, form couples based on real conversations, and create offspring that inherit their traits!

---

## 🎬 See It In Action!

<div align="center">

### 💬 Speed Dating Conversations
<a href="doc/Screenshot 2026-01-01 at 10.48.53 PM.png"><img src="doc/Screenshot 2026-01-01 at 10.48.53 PM.png" width="400" alt="Speed Dating Conversations"></a>

*Adam and Eve discuss their skills and interests in a natural conversation*

### 🧠 Agent Reasoning & Decision Making
<a href="doc/Screenshot 2026-01-01 at 10.49.01 PM.png"><img src="doc/Screenshot 2026-01-01 at 10.49.01 PM.png" width="400" alt="Agent Reasoning"></a>

*See why each agent scored their compatibility the way they did*

### 📊 Full Dashboard View
<a href="doc/Screenshot 2026-01-01 at 10.50.01 PM.png"><img src="doc/Screenshot 2026-01-01 at 10.50.01 PM.png" width="400" alt="Full Dashboard"></a>

*Real-time population stats, conversations, reasoning, and trait evolution*

### 🔍 Agent Inspector
<a href="doc/Screenshot 2026-01-01 at 10.49.51 PM.png"><img src="doc/Screenshot 2026-01-01 at 10.49.51 PM.png" width="400" alt="Agent Inspector"></a>

*Deep dive into any agent's personality, skills, tools, and relationship history*

### 📈 Trait Evolution Over Generations
<a href="doc/Screenshot 2026-01-01 at 10.49.36 PM.png"><img src="doc/Screenshot 2026-01-01 at 10.49.36 PM.png" width="400" alt="Trait Evolution"></a>

*Watch how personality traits shift across generations*

### 👥 Population Grid
<a href="doc/Screenshot 2026-01-01 at 10.50.24 PM.png"><img src="doc/Screenshot 2026-01-01 at 10.50.24 PM.png" width="400" alt="Population Grid"></a>

*Visual overview of all agents with their generation, gender, and tools*

</div>

---

## 🌟 What Makes This Special?

### 🤖 Real AI Conversations
Each person is powered by **Claude Sonnet 4.5** and has their own personality based on the Big Five traits:
- 🎨 **Openness**: Creative and curious vs. practical and conventional
- 📋 **Conscientiousness**: Organized and disciplined vs. spontaneous and flexible
- 🎤 **Extraversion**: Outgoing and energetic vs. reserved and introspective
- 🤝 **Agreeableness**: Compassionate and cooperative vs. analytical and detached
- 😰 **Neuroticism**: Anxious and sensitive vs. calm and resilient

### 💘 Speed Dating System
Agents engage in **4-turn conversations** to get to know each other:
1. **Male initiates** - Introduces himself and starts the conversation
2. **Female responds** - Shares about herself and shows interest
3. **Male responds** - Asks questions or shares more
4. **Female closes** - Wraps up the conversation naturally

Then they **independently score** each other (0-100) with detailed reasoning!

### 🧬 Genetic Inheritance
Children inherit:
- 📊 **Personality traits**: Averaged from parents with Gaussian mutation
- 🛠️ **Skills**: Randomly inherited from either parent with potential upgrades
- 🔧 **Tools**: Inherited from either parent with chance of learning new ones

### 🎯 Smart Matching Algorithm
The system uses:
- 🔍 **Pre-filtering**: Only compatible pairs (trait distance < threshold) have conversations
- ⚖️ **Conversation limiting**: Max 5 dates per person per cycle to prevent monopolization
- 🚀 **Parallel processing**: Up to 10 conversations run simultaneously
- 💯 **Greedy matching**: Highest scoring pairs form couples first

---

## 🚀 Quick Start

### Prerequisites
- 🐍 Python 3.11+
- 🔑 [Anthropic API key](https://console.anthropic.com/)

### Installation

```bash
# 1️⃣ Clone the repo
git clone https://github.com/floriangrousset/Evolution.git
cd Evolution

# 2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Configure your API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here
```

### 🎮 Run the Simulation

**With LLM-powered conversational agents (v2.0):**
```bash
ENABLE_LLM_MATING=true python -m src.main
```

**Classic deterministic mode (v1.0):**
```bash
ENABLE_LLM_MATING=false python -m src.main
```

Watch the magic happen! Press `Ctrl+C` to stop.

---

## ⚙️ Configuration

Customize your simulation in `.env`:

```bash
# 🤖 LLM Agent Settings (v2.0)
ENABLE_LLM_MATING=true              # Use conversational agents
MODEL_NAME=claude-sonnet-4-5-20250929  # AI model
MAX_DATES_PER_CYCLE=5               # Max dates per person per cycle
MAX_PARALLEL_CONVERSATIONS=10       # Conversations to run simultaneously
MIN_COMPATIBILITY=40.0              # Min score to form a couple (0-100)
PRE_FILTER_TRAIT_DISTANCE=10.0      # Max trait distance for pre-filtering

# ⏰ Timing
GENERATION_CYCLE_SECONDS=60         # Time between reproduction cycles
AGING_SECONDS=10                    # Time for children to become adults

# 👥 Population
MAX_POPULATION=50                   # Stop mating at this limit

# 🧬 Genetics
MUTATION_RATE=1.0                   # Trait mutation standard deviation

# 🎯 Skills & Tools
AVAILABLE_SKILLS=hunting,gathering,crafting,communication,innovation,teaching
AVAILABLE_TOOLS=stone-tools,fire,calculator,memory
```

---

## 🏗️ Architecture

```
src/
├── 🎯 main.py                    # Entry point
├── ⚙️ config.py                   # Configuration
├── 📦 state/
│   └── types.py                  # State & data models
├── 🤖 agents/
│   ├── base.py                   # Person model
│   ├── traits.py                 # Inheritance & mutation
│   ├── 💬 conversations/          # LLM agent system (v2.0)
│   │   ├── agent_factory.py      # Create LangChain agents
│   │   ├── conversation_manager.py  # Speed dating orchestration
│   │   └── scoring.py            # Score extraction
│   └── 📝 prompts/                # Personality system
│       ├── system_prompt_template.py   # Dynamic prompts
│       ├── personality_descriptors.yaml # Trait → description
│       └── scoring_prompt.py     # Compatibility scoring
├── 🔄 graphs/
│   ├── main_graph.py             # LangGraph orchestration
│   ├── nodes.py                  # Graph nodes
│   └── attraction.py             # Compatibility algorithm
└── 🖥️ cli/
    ├── display.py                # Main display
    └── 📊 panels/                 # Dashboard panels (v2.0)
        ├── conversations.py      # Conversation transcripts
        ├── reasoning.py          # Agent reasoning
        ├── evolution_graphs.py   # Trait evolution charts
        └── inspector.py          # Agent detail view
```

---

## 🎮 How It Works

### 🔄 Lifecycle Loop

```
1️⃣ Age Children → 2️⃣ Speed Dating → 3️⃣ Form Couples → 4️⃣ Reproduce → 5️⃣ Update Singles → 🔁 Repeat
```

**In Detail:**

1. **👶 → 👤 Aging**: Children become adults after `AGING_SECONDS`
2. **💬 Speed Dating (LLM Mode)**:
   - Pre-filter compatible pairs by trait distance
   - Run parallel 4-turn conversations
   - Both agents independently score compatibility
   - Highest mutual scores form couples
3. **💑 Form Couples**: Agents with scores ≥ `MIN_COMPATIBILITY` pair up
4. **👶 Reproduction**: Couples create 1-3 children with inherited traits
5. **📊 Update**: Recalculate singles pool and trait statistics

### 🧮 Compatibility Scoring

**Deterministic Mode (v1.0):**
- 60% Personality Similarity (Euclidean distance in Big Five space)
- 25% Skill Complementarity (different skills = higher score)
- 15% Tool Overlap (shared tools = higher score)

**LLM Mode (v2.0):**
- Agents score each other (0-100) based on their conversation
- Both must score high for a couple to form
- Final score = average of both agents' scores

---

## 🎨 Dashboard Features

### 💬 Conversation Transcripts
See the actual LLM-generated conversations between agents during speed dating!

### 🧠 Agent Reasoning
Read the detailed reasoning behind each agent's compatibility score.

### 📈 Trait Evolution Graphs
Watch how population traits shift over generations (ASCII charts).

### 🔍 Agent Inspector
Deep dive into any agent:
- Personality traits (Big Five)
- Skills and proficiency levels
- Tools possessed
- Relationship history
- Conversation count

### 📊 Population Statistics
- Total population & generation breakdown
- Gender distribution
- Couple count
- Average trait values

---

## 💰 Cost & Performance

### 💵 Costs (Claude Sonnet 4.5)
- **Per conversation**: ~800 tokens × $3/1M = **$0.0024**
- **20 agents** (10M, 10F): ~25 conversations = **$0.06/cycle**
- **40 agents** (20M, 20F): ~100 conversations = **$0.24/cycle**
- **Per hour** (40 agents, 60s cycles): **~$14.40/hour**

### ⚡ Performance
- **20 agents**: ~15 seconds per cycle ✅
- **40 agents**: ~50 seconds per cycle ✅
- **80 agents**: ~120 seconds per cycle (may need 120s cycle time)

### 🚀 Optimizations
- Pre-filtering reduces O(N²) to O(N×5)
- Parallel batching (10 conversations at once)
- Conversation limiting (5 dates max per person per cycle)
- Fast model (Sonnet vs Opus = 3x faster, 5x cheaper)

---

## 🎯 Development Status

### ✅ Completed Features

- ✅ **v1.0**: Deterministic mate selection with mathematical compatibility
- ✅ **v2.0**: LLM conversational agents with personality-driven dialogue
- ✅ Speed dating system (4-turn conversations)
- ✅ Enhanced dashboard with 4 new panels
- ✅ Trait inheritance with mutation
- ✅ Lifecycle management (child → adult)
- ✅ Population limits and controls
- ✅ Real-time ASCII art visualization
- ✅ Parallel conversation processing

### 🚀 Future Ideas

- 💀 **Death Mechanism**: Natural lifespan and population turnover
- 🌍 **Environmental Factors**: Resource scarcity, disasters, seasons
- 🌳 **Family Tree Visualization**: Interactive lineage tracking
- 💾 **Save/Load**: Checkpoint simulation state
- 🌐 **Web Interface**: Gradio or Streamlit dashboard
- 🎭 **Personality Development**: Agents evolve traits based on experiences
- 🏆 **Social Dynamics**: Friendships, rivalries, community events
- 📱 **Multi-Modal**: Voice conversations between agents

---

## 🤝 Contributing

Want to make Evolution even better? We'd love your help!

**Workflow:**
1. Fork the repo
2. Create a feature branch from `develop`
3. Make your changes
4. Submit a PR to `develop`

**Branch Structure:**
- `main` → Production releases
- `develop` → Active development
- `feature/*` → New features

---

## 📜 License

MIT License - Feel free to use this for learning, teaching, or creating your own simulations!

---

## 🙏 Acknowledgments

- Inspired by [Revolution](https://github.com/floriangrousset/Revolution)
- Built with ❤️ using [LangGraph](https://github.com/langchain-ai/langgraph) and [LangChain](https://github.com/langchain-ai/langchain)
- Powered by [Claude](https://www.anthropic.com/claude) (Anthropic)
- CLI magic by [Rich](https://github.com/Textualize/rich)

---

<div align="center">

### 🌟 Star this repo if you like watching AI fall in love! 🌟

**Have fun evolving! 🧬💕**

</div>

# Contributing to Evolution

Thank you for your interest in contributing to Evolution! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branch Strategy](#branch-strategy)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Testing](#testing)
- [Questions?](#questions)

## Getting Started

1. **Fork the repository** to your own GitHub account
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Evolution.git
   cd Evolution
   ```
3. **Set up the upstream remote**:
   ```bash
   git remote add upstream https://github.com/floriangrousset/Evolution.git
   ```
4. **Set up your development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env to add your ANTHROPIC_API_KEY
   ```

## Development Workflow

We follow **Git Flow** for branch management:

```
main (production-ready releases)
  ↑
develop (integration branch)
  ↑
feature/*, bugfix/*, hotfix/* (your work)
```

### Branch Strategy

- **`main`**: Production-ready code. Protected - requires PRs to merge.
- **`develop`**: Active development branch. Protected - requires PRs to merge.
- **`feature/*`**: New features (e.g., `feature/death-mechanism`)
- **`bugfix/*`**: Bug fixes (e.g., `bugfix/fix-trait-mutation`)
- **`hotfix/*`**: Urgent fixes for production (e.g., `hotfix/critical-crash`)
- **`docs/*`**: Documentation updates (e.g., `docs/update-readme`)
- **`refactor/*`**: Code refactoring (e.g., `refactor/simplify-scoring`)

### Creating a Feature Branch

Always create your branch from `develop`:

```bash
# Make sure you're on develop and it's up to date
git checkout develop
git pull upstream develop

# Create your feature branch
git checkout -b feature/your-feature-name

# Make your changes...
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

## Commit Guidelines

We follow conventional commit messages:

- **`feat:`** - New feature
- **`fix:`** - Bug fix
- **`docs:`** - Documentation changes
- **`refactor:`** - Code refactoring
- **`test:`** - Adding or updating tests
- **`chore:`** - Maintenance tasks
- **`perf:`** - Performance improvements

Examples:
```bash
git commit -m "feat: add death mechanism for agents"
git commit -m "fix: correct trait inheritance calculation"
git commit -m "docs: update installation instructions"
git commit -m "refactor: simplify compatibility scoring algorithm"
```

## Pull Request Process

1. **Create your feature branch** from `develop` (see above)

2. **Make your changes** following the code style guidelines

3. **Test your changes**:
   ```bash
   # Run the simulation to ensure it works
   python -m src.main
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**:
   - Go to the [Evolution repository](https://github.com/floriangrousset/Evolution)
   - Click "Pull requests" → "New pull request"
   - Click "compare across forks"
   - Set:
     - **Base repository**: `floriangrousset/Evolution`
     - **Base branch**: `develop` ⚠️ **Important: PRs go to `develop`, not `main`**
     - **Head repository**: `YOUR_USERNAME/Evolution`
     - **Compare branch**: `feature/your-feature-name`
   - Fill out the PR template with:
     - Clear description of what you changed
     - Why the change is needed
     - Screenshots/examples if applicable
     - Testing steps

6. **Respond to feedback** - maintainers may request changes

7. **After merge**:
   ```bash
   # Update your develop branch
   git checkout develop
   git pull upstream develop

   # Delete your feature branch
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

## Code Style

- **Python 3.11+** syntax
- Follow **PEP 8** style guidelines
- Use **type hints** where appropriate
- Keep functions focused and modular
- Add docstrings for complex functions
- Use descriptive variable names

### File Organization

When adding new features:
- Place models in `src/agents/` or `src/state/`
- Add graph nodes in `src/graphs/nodes.py`
- Put LLM prompts in `src/agents/prompts/`
- Add UI components in `src/cli/panels/`
- Update `src/config.py` for new configuration options

## Testing

While we don't have automated tests yet, please:

1. **Manual Testing**: Run the simulation with your changes
   ```bash
   # Test deterministic mode
   ENABLE_LLM_MATING=false python -m src.main

   # Test LLM mode
   ENABLE_LLM_MATING=true python -m src.main
   ```

2. **Edge Cases**: Test with different configurations in `.env`
   - Small populations (5-10 agents)
   - Large populations (40+ agents)
   - Different timing settings
   - Edge cases (e.g., single agent, no adults, etc.)

3. **Performance**: Ensure your changes don't significantly slow down the simulation

## What to Contribute

### Good First Issues

- Documentation improvements
- Bug fixes
- UI/CLI enhancements
- Configuration options
- Code refactoring

### Feature Ideas

- Death mechanism with natural lifespan
- Family tree visualization
- Environmental factors (resources, seasons)
- Save/load simulation state
- Web interface (Gradio/Streamlit)
- Personality development over time
- Social dynamics (friendships, rivalries)
- Multi-modal features (voice conversations)

### Before Starting Large Features

For significant features (new systems, major refactors), please:
1. Open an **issue** first to discuss the approach
2. Wait for feedback from maintainers
3. Get agreement on the design before implementing

This prevents duplicate work and ensures alignment with project goals.

## Questions?

- **Issues**: Use [GitHub Issues](https://github.com/floriangrousset/Evolution/issues) for bug reports and feature requests
- **Discussions**: Use [GitHub Discussions](https://github.com/floriangrousset/Evolution/discussions) for questions and ideas
- **Repository Owner**: [@floriangrousset](https://github.com/floriangrousset)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Evolution! 🧬💕**

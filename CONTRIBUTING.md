# Contributing to Base Agent Toolkit

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/base-agent-toolkit/base-agent-toolkit.git
   cd base-agent-toolkit
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or .venv\Scripts\activate  # Windows
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[all]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Code Style

- We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Line length limit: 100 characters
- Type hints are required for all public functions
- Docstrings follow Google style

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=base_agent_toolkit

# Run specific test file
pytest tests/test_wallet.py -v
```

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat(scope):` — New feature
- `fix(scope):` — Bug fix
- `docs:` — Documentation only
- `test(scope):` — Adding tests
- `refactor(scope):` — Code refactoring
- `ci:` — CI/CD changes
- `chore:` — Maintenance

Examples:
```
feat(wallet): add HD wallet derivation from mnemonic
fix(provider): handle RPC timeout with exponential backoff
docs: update B20 integration guide
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with appropriate tests
3. Ensure all tests pass and linting is clean
4. Submit a PR with a clear description

## Project Structure

```
src/base_agent_toolkit/
├── __init__.py          # Package exports
├── constants.py         # Chain config, addresses
├── types.py             # Type aliases
├── exceptions.py        # Custom exceptions
├── config.py            # Configuration loader
├── logging.py           # Structured logging
├── wallet/              # Wallet management
├── provider/            # RPC providers
├── b20/                 # B20 token standard
├── defi/                # DeFi integrations
├── agent/               # Agent framework
├── x402/                # x402 payments
└── cli/                 # CLI interface
```

## Questions?

Open an issue or start a discussion on GitHub.

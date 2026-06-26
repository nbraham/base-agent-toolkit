# Base Agent Toolkit — Development Commands

.PHONY: install test lint format typecheck clean docs

# Install development dependencies
install:
	pip install -e ".[dev]"

# Run all tests
test:
	pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	pytest tests/ -v --tb=short --cov=src/base_agent_toolkit --cov-report=term-missing

# Lint code
lint:
	ruff check src/ tests/

# Auto-fix lint issues
fix:
	ruff check --fix src/ tests/

# Format code
format:
	ruff format src/ tests/

# Type checking
typecheck:
	mypy src/base_agent_toolkit

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Quick check (lint + test)
check: lint test

# Full CI check
ci: lint typecheck test

"""Shared test fixtures for Base Agent Toolkit."""

import os

import pytest

from base_agent_toolkit.agent.base import AgentConfig, BaseAgent


# ============================================================
# Environment fixtures
# ============================================================


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Ensure tests don't use real credentials."""
    monkeypatch.delenv("BAT_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("BAT_RPC_URL", raising=False)


@pytest.fixture
def test_private_key():
    """Deterministic test private key (NOT for real use)."""
    return "0x" + "a" * 64


@pytest.fixture
def test_address():
    """Known address for testing."""
    return "0x4200000000000000000000000000000000000006"


# ============================================================
# Agent fixtures
# ============================================================


@pytest.fixture
def dry_run_agent():
    """Agent in dry-run mode."""
    config = AgentConfig(
        name="test-agent",
        dry_run=True,
        daily_budget_wei=10**18,  # 1 ETH
    )
    return BaseAgent(config)


@pytest.fixture
def live_agent():
    """Agent in live mode (for testing, no wallet)."""
    config = AgentConfig(
        name="live-test-agent",
        dry_run=False,
    )
    return BaseAgent(config)


# ============================================================
# Token fixtures
# ============================================================


@pytest.fixture
def usdc_address():
    """USDC on Base mainnet."""
    return "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"


@pytest.fixture
def weth_address():
    """WETH on Base mainnet."""
    return "0x4200000000000000000000000000000000000006"

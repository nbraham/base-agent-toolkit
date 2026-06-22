"""Shared test fixtures for Base Agent Toolkit."""

from __future__ import annotations

import pytest

from base_agent_toolkit.config import Settings
from base_agent_toolkit.types import Network


@pytest.fixture
def settings() -> Settings:
    """Create test settings with Sepolia network."""
    return Settings(
        network=Network.SEPOLIA,
        rpc_url="https://sepolia.base.org",
        private_key="ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
        dry_run=True,
        log_level="DEBUG",
    )


@pytest.fixture
def mainnet_settings() -> Settings:
    """Create test settings for mainnet (dry-run only)."""
    return Settings(
        network=Network.MAINNET,
        dry_run=True,
        log_level="DEBUG",
    )


# Well-known test addresses
TEST_ADDRESS_1 = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
TEST_ADDRESS_2 = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
TEST_PRIVATE_KEY = "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest

from base_agent_toolkit.config import Settings, load_settings
from base_agent_toolkit.constants import BASE_MAINNET_CHAIN_ID, BASE_SEPOLIA_CHAIN_ID
from base_agent_toolkit.types import Network


class TestSettings:
    """Tests for Settings class."""

    def test_default_network(self):
        settings = Settings()
        assert settings.network == Network.MAINNET

    def test_chain_id_mainnet(self):
        settings = Settings(network=Network.MAINNET)
        assert settings.chain_id == BASE_MAINNET_CHAIN_ID

    def test_chain_id_sepolia(self):
        settings = Settings(network=Network.SEPOLIA)
        assert settings.chain_id == BASE_SEPOLIA_CHAIN_ID

    def test_rpc_urls_default(self):
        settings = Settings()
        urls = settings.rpc_urls
        assert len(urls) > 0
        assert "base.org" in urls[0]

    def test_rpc_urls_custom(self):
        settings = Settings(rpc_url="https://custom.rpc.com")
        assert settings.rpc_urls[0] == "https://custom.rpc.com"

    def test_rpc_fallbacks_parsing(self):
        settings = Settings(rpc_fallbacks=["https://a.com", "https://b.com"])
        assert len(settings.rpc_fallbacks) == 2

    def test_private_key_normalization(self):
        settings = Settings(private_key="0xabc123")
        assert settings.private_key == "abc123"

    def test_private_key_no_prefix(self):
        settings = Settings(private_key="abc123")
        assert settings.private_key == "abc123"

    def test_dry_run_default(self):
        settings = Settings()
        assert settings.dry_run is False

    def test_from_env(self):
        with patch.dict(os.environ, {"BAT_NETWORK": "sepolia", "BAT_DRY_RUN": "true"}):
            settings = Settings()
            assert settings.network == Network.SEPOLIA
            assert settings.dry_run is True


class TestLoadSettings:
    def test_load_default(self):
        settings = load_settings()
        assert isinstance(settings, Settings)

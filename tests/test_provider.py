"""Tests for provider module."""

from unittest.mock import MagicMock, patch

import pytest

from base_agent_toolkit.provider.base import BaseProvider
from base_agent_toolkit.provider.manager import ProviderManager
from base_agent_toolkit.exceptions import AllProvidersFailedError, ProviderError


class TestBaseProvider:
    """Tests for BaseProvider."""

    def test_default_rpc_url(self):
        """Test provider uses default URL when none provided."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                provider = BaseProvider(chain_id=8453)
                assert "base.org" in provider.rpc_url

    def test_custom_rpc_url(self):
        """Test provider uses custom URL."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                provider = BaseProvider(rpc_url="https://custom.rpc.com")
                assert provider.rpc_url == "https://custom.rpc.com"

    def test_invalid_chain_id(self):
        """Test provider raises for unknown chain ID."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                with pytest.raises(ProviderError):
                    BaseProvider(chain_id=99999)

    def test_repr(self):
        """Test provider repr."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                provider = BaseProvider(rpc_url="https://test.com", chain_id=8453)
                assert "test.com" in repr(provider)


class TestProviderManager:
    """Tests for ProviderManager."""

    def test_init_with_urls(self):
        """Test manager init with multiple URLs."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                manager = ProviderManager(
                    rpc_urls=["https://a.com", "https://b.com"],
                    chain_id=8453,
                )
                assert manager.provider_count == 2

    def test_no_urls_raises(self):
        """Test manager raises when no URLs available."""
        with pytest.raises(ProviderError):
            ProviderManager(rpc_urls=[], chain_id=99999)

    def test_current_provider(self):
        """Test getting current provider."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                manager = ProviderManager(
                    rpc_urls=["https://a.com"],
                    chain_id=8453,
                )
                assert isinstance(manager.current, BaseProvider)

    def test_repr(self):
        """Test manager repr."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                manager = ProviderManager(
                    rpc_urls=["https://a.com"],
                    chain_id=8453,
                )
                assert "ProviderManager" in repr(manager)

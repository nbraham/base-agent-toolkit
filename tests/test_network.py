"""Tests for network configuration."""

import pytest

from base_agent_toolkit.network import (
    MAINNET,
    SEPOLIA,
    get_network,
    resolve_network,
)


class TestNetworkConfig:
    """Tests for network configuration."""

    def test_mainnet_chain_id(self):
        assert MAINNET.chain_id == 8453
        assert not MAINNET.is_testnet

    def test_sepolia_chain_id(self):
        assert SEPOLIA.chain_id == 84532
        assert SEPOLIA.is_testnet

    def test_explorer_links(self):
        link = MAINNET.tx_link("0xabc123")
        assert "basescan.org" in link
        assert "0xabc123" in link

    def test_address_link(self):
        link = SEPOLIA.address_link("0xdef456")
        assert "sepolia.basescan.org" in link

    def test_get_network_mainnet(self):
        net = get_network(8453)
        assert net.name == "Base Mainnet"

    def test_get_network_sepolia(self):
        net = get_network(84532)
        assert net.name == "Base Sepolia"

    def test_get_network_unknown(self):
        with pytest.raises(ValueError, match="Unsupported"):
            get_network(1)

    def test_resolve_by_name(self):
        assert resolve_network("mainnet").chain_id == 8453
        assert resolve_network("sepolia").chain_id == 84532
        assert resolve_network("base").chain_id == 8453

    def test_resolve_by_id(self):
        assert resolve_network(8453).chain_id == 8453

    def test_resolve_unknown_name(self):
        with pytest.raises(ValueError, match="Unknown"):
            resolve_network("polygon")

"""Integration tests for provider connectivity.

These tests connect to actual Base RPC endpoints.
Skip if no network is available.
"""

import pytest

try:
    import httpx
    HAS_NETWORK = True
except ImportError:
    HAS_NETWORK = False


@pytest.mark.skipif(not HAS_NETWORK, reason="No network/httpx")
class TestProviderConnectivity:
    """Test real RPC connectivity."""

    def test_base_mainnet_reachable(self):
        """Verify Base mainnet RPC is reachable."""
        response = httpx.post(
            "https://mainnet.base.org",
            json={
                "jsonrpc": "2.0",
                "method": "eth_chainId",
                "params": [],
                "id": 1,
            },
            timeout=10,
        )
        assert response.status_code == 200
        data = response.json()
        # 0x2105 = 8453 (Base mainnet)
        assert data["result"] == "0x2105"

    def test_base_sepolia_reachable(self):
        """Verify Base Sepolia RPC is reachable."""
        response = httpx.post(
            "https://sepolia.base.org",
            json={
                "jsonrpc": "2.0",
                "method": "eth_chainId",
                "params": [],
                "id": 1,
            },
            timeout=10,
        )
        assert response.status_code == 200
        data = response.json()
        # 0x14a34 = 84532 (Base Sepolia)
        assert data["result"] == "0x14a34"

    def test_block_number(self):
        """Fetch current block number."""
        response = httpx.post(
            "https://mainnet.base.org",
            json={
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 1,
            },
            timeout=10,
        )
        assert response.status_code == 200
        data = response.json()
        block = int(data["result"], 16)
        assert block > 0

"""Network configuration and chain resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .constants import (
    BASE_MAINNET_CHAIN_ID,
    BASE_SEPOLIA_CHAIN_ID,
    DEFAULT_RPC_URLS,
)


@dataclass
class NetworkConfig:
    """Configuration for a Base network."""

    name: str
    chain_id: int
    rpc_urls: list[str]
    explorer_url: str
    is_testnet: bool

    @property
    def explorer_tx_url(self) -> str:
        """Base URL for transaction links."""
        return f"{self.explorer_url}/tx"

    @property
    def explorer_address_url(self) -> str:
        """Base URL for address links."""
        return f"{self.explorer_url}/address"

    def tx_link(self, tx_hash: str) -> str:
        """Get explorer link for a transaction."""
        return f"{self.explorer_tx_url}/{tx_hash}"

    def address_link(self, address: str) -> str:
        """Get explorer link for an address."""
        return f"{self.explorer_address_url}/{address}"


# Pre-defined networks
MAINNET = NetworkConfig(
    name="Base Mainnet",
    chain_id=BASE_MAINNET_CHAIN_ID,
    rpc_urls=DEFAULT_RPC_URLS[BASE_MAINNET_CHAIN_ID],
    explorer_url="https://basescan.org",
    is_testnet=False,
)

SEPOLIA = NetworkConfig(
    name="Base Sepolia",
    chain_id=BASE_SEPOLIA_CHAIN_ID,
    rpc_urls=DEFAULT_RPC_URLS[BASE_SEPOLIA_CHAIN_ID],
    explorer_url="https://sepolia.basescan.org",
    is_testnet=True,
)

NETWORKS = {
    BASE_MAINNET_CHAIN_ID: MAINNET,
    BASE_SEPOLIA_CHAIN_ID: SEPOLIA,
}


def get_network(chain_id: int) -> NetworkConfig:
    """Get network configuration by chain ID.

    Args:
        chain_id: Chain ID.

    Returns:
        NetworkConfig instance.

    Raises:
        ValueError: If chain ID is not supported.
    """
    if chain_id not in NETWORKS:
        raise ValueError(
            f"Unsupported chain ID: {chain_id}. "
            f"Supported: {list(NETWORKS.keys())}"
        )
    return NETWORKS[chain_id]


def resolve_network(name_or_id: str | int) -> NetworkConfig:
    """Resolve a network from name or chain ID.

    Args:
        name_or_id: "mainnet", "sepolia", or chain ID.

    Returns:
        NetworkConfig instance.
    """
    if isinstance(name_or_id, int):
        return get_network(name_or_id)

    name = name_or_id.lower().strip()
    mapping = {
        "mainnet": MAINNET,
        "base": MAINNET,
        "base-mainnet": MAINNET,
        "sepolia": SEPOLIA,
        "base-sepolia": SEPOLIA,
        "testnet": SEPOLIA,
    }

    if name not in mapping:
        raise ValueError(f"Unknown network: {name}")

    return mapping[name]

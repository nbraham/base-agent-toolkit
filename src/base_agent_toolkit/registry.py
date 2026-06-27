"""Token registry for Base chain.

Pre-populated registry of well-known tokens on Base mainnet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .constants import (
    CBETH_ADDRESS,
    DAI_ADDRESS,
    USDC_ADDRESS,
    USDT_ADDRESS,
    WETH_ADDRESS,
)


@dataclass
class RegisteredToken:
    """A token in the registry."""

    address: str
    symbol: str
    name: str
    decimals: int
    is_stablecoin: bool = False
    coingecko_id: str = ""


# Well-known tokens on Base mainnet
BASE_TOKEN_REGISTRY: dict[str, RegisteredToken] = {
    "ETH": RegisteredToken(
        address="0x0000000000000000000000000000000000000000",
        symbol="ETH",
        name="Ether",
        decimals=18,
        coingecko_id="ethereum",
    ),
    "WETH": RegisteredToken(
        address=WETH_ADDRESS,
        symbol="WETH",
        name="Wrapped Ether",
        decimals=18,
        coingecko_id="weth",
    ),
    "USDC": RegisteredToken(
        address=USDC_ADDRESS,
        symbol="USDC",
        name="USD Coin",
        decimals=6,
        is_stablecoin=True,
        coingecko_id="usd-coin",
    ),
    "USDT": RegisteredToken(
        address=USDT_ADDRESS,
        symbol="USDT",
        name="Tether USD",
        decimals=6,
        is_stablecoin=True,
        coingecko_id="tether",
    ),
    "DAI": RegisteredToken(
        address=DAI_ADDRESS,
        symbol="DAI",
        name="Dai Stablecoin",
        decimals=18,
        is_stablecoin=True,
        coingecko_id="dai",
    ),
    "cbETH": RegisteredToken(
        address=CBETH_ADDRESS,
        symbol="cbETH",
        name="Coinbase Wrapped Staked ETH",
        decimals=18,
        coingecko_id="coinbase-wrapped-staked-eth",
    ),
}


def get_token(symbol: str) -> RegisteredToken | None:
    """Look up a token by symbol.

    Args:
        symbol: Token symbol (case-insensitive).

    Returns:
        RegisteredToken or None.
    """
    return BASE_TOKEN_REGISTRY.get(symbol.upper())


def get_token_by_address(address: str) -> RegisteredToken | None:
    """Look up a token by address.

    Args:
        address: Token contract address (case-insensitive).

    Returns:
        RegisteredToken or None.
    """
    addr = address.lower()
    for token in BASE_TOKEN_REGISTRY.values():
        if token.address.lower() == addr:
            return token
    return None


def list_stablecoins() -> list[RegisteredToken]:
    """Get all registered stablecoins."""
    return [t for t in BASE_TOKEN_REGISTRY.values() if t.is_stablecoin]


def list_all_tokens() -> list[RegisteredToken]:
    """Get all registered tokens."""
    return list(BASE_TOKEN_REGISTRY.values())

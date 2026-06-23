"""B20 token types and configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..types import Address


class B20TokenType(str, Enum):
    """B20 token variant types."""

    ASSET = "asset"
    STABLECOIN = "stablecoin"


class B20Role(str, Enum):
    """B20 role identifiers.

    Roles control access to privileged operations like
    minting, burning, freezing, and pausing.
    """

    ADMIN = "admin"
    MINTER = "minter"
    BURNER = "burner"
    FREEZER = "freezer"
    PAUSER = "pauser"

    @property
    def role_hash(self) -> bytes:
        """Get the keccak256 hash of the role name."""
        from web3 import Web3
        return Web3.keccak(text=self.value.upper() + "_ROLE")


@dataclass
class B20TokenConfig:
    """Configuration for deploying a new B20 token.

    Args:
        name: Token name (e.g., "My Token").
        symbol: Token symbol (e.g., "MTK").
        token_type: Asset or Stablecoin variant.
        admin: Admin address (receives all roles initially).
        decimals: Token decimals (6-18 for Asset, fixed 6 for Stablecoin).
        supply_cap: Maximum supply (0 = unlimited).
        currency_code: ISO 4217 code (Stablecoin only, e.g., "USD").
    """

    name: str
    symbol: str
    token_type: B20TokenType = B20TokenType.ASSET
    admin: Address = ""
    decimals: int = 18
    supply_cap: int = 0
    currency_code: str = ""

    def __post_init__(self):
        """Validate configuration."""
        if not self.name:
            raise ValueError("Token name is required")
        if not self.symbol:
            raise ValueError("Token symbol is required")

        if self.token_type == B20TokenType.STABLECOIN:
            self.decimals = 6  # Fixed for stablecoins
            if not self.currency_code:
                raise ValueError("Currency code required for stablecoin (e.g., 'USD')")
        else:
            if not (6 <= self.decimals <= 18):
                raise ValueError(f"Decimals must be 6-18, got {self.decimals}")


@dataclass
class B20TokenInfo:
    """Information about a deployed B20 token."""

    address: Address
    name: str
    symbol: str
    decimals: int
    token_type: B20TokenType
    total_supply: int = 0
    supply_cap: int = 0
    paused: bool = False
    currency_code: str = ""

    @property
    def has_supply_cap(self) -> bool:
        """Whether the token has a supply cap."""
        return self.supply_cap > 0

    @property
    def remaining_mintable(self) -> int:
        """How many more tokens can be minted."""
        if not self.has_supply_cap:
            return -1  # unlimited
        return max(0, self.supply_cap - self.total_supply)

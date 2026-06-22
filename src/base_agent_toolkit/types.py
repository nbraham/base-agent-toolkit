"""Common type aliases and data structures for Base Agent Toolkit."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, TypeAlias

# ============================================================
# Primitive Type Aliases
# ============================================================
Address: TypeAlias = str  # Ethereum address (0x-prefixed, checksummed)
TxHash: TypeAlias = str  # Transaction hash (0x-prefixed)
BlockNumber: TypeAlias = int  # Block number
Wei: TypeAlias = int  # Amount in wei
Gwei: TypeAlias = float  # Amount in gwei
HexBytes: TypeAlias = bytes  # Raw bytes data


class Network(str, Enum):
    """Supported networks."""

    MAINNET = "mainnet"
    SEPOLIA = "sepolia"


class TokenStandard(str, Enum):
    """Token standards."""

    ERC20 = "erc20"
    B20_ASSET = "b20_asset"
    B20_STABLECOIN = "b20_stablecoin"


# ============================================================
# Data Structures
# ============================================================
@dataclass(frozen=True)
class TokenAmount:
    """Represents a token amount with decimals handling."""

    raw: int  # Raw amount in smallest unit
    decimals: int
    symbol: str = ""

    @property
    def ether(self) -> Decimal:
        """Human-readable amount."""
        return Decimal(self.raw) / Decimal(10**self.decimals)

    @property
    def formatted(self) -> str:
        """Formatted string with symbol."""
        val = f"{self.ether:.{min(self.decimals, 8)}f}"
        return f"{val} {self.symbol}" if self.symbol else val

    @classmethod
    def from_ether(cls, amount: float | Decimal | str, decimals: int = 18, symbol: str = "") -> "TokenAmount":
        """Create from human-readable amount."""
        dec_amount = Decimal(str(amount))
        raw = int(dec_amount * Decimal(10**decimals))
        return cls(raw=raw, decimals=decimals, symbol=symbol)

    def __str__(self) -> str:
        return self.formatted


@dataclass(frozen=True)
class TransactionResult:
    """Result of a submitted transaction."""

    hash: TxHash
    block_number: int | None = None
    gas_used: int | None = None
    status: bool | None = None  # True = success, False = reverted, None = pending
    logs: list[dict[str, Any]] | None = None

    @property
    def success(self) -> bool:
        return self.status is True

    @property
    def explorer_url(self) -> str:
        from .constants import BASE_MAINNET_CHAIN_ID, EXPLORER_URLS

        base_url = EXPLORER_URLS.get(BASE_MAINNET_CHAIN_ID, "https://basescan.org")
        return f"{base_url}/tx/{self.hash}"


@dataclass(frozen=True)
class GasEstimate:
    """Gas estimation for a transaction."""

    gas_limit: int
    max_fee_per_gas: int  # in wei
    max_priority_fee_per_gas: int  # in wei
    estimated_cost_wei: int

    @property
    def estimated_cost_gwei(self) -> float:
        return self.estimated_cost_wei / 1e9

    @property
    def estimated_cost_ether(self) -> Decimal:
        return Decimal(self.estimated_cost_wei) / Decimal(10**18)


@dataclass(frozen=True)
class TokenInfo:
    """Information about a token."""

    address: Address
    name: str
    symbol: str
    decimals: int
    standard: TokenStandard = TokenStandard.ERC20
    total_supply: int | None = None


@dataclass(frozen=True)
class WalletBalance:
    """Complete wallet balance information."""

    address: Address
    eth_balance: TokenAmount
    token_balances: dict[Address, TokenAmount]

    @property
    def total_eth(self) -> Decimal:
        return self.eth_balance.ether

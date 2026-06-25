"""Type definitions for Base Agent Toolkit."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any

# ============================================================
# Type Aliases
# ============================================================
Address = str
TxHash = str
Wei = int
BlockNumber = int


class Network(str, Enum):
    """Supported networks."""

    MAINNET = "mainnet"
    SEPOLIA = "sepolia"

    @property
    def chain_id(self) -> int:
        return 8453 if self == Network.MAINNET else 84532


# ============================================================
# Data Classes
# ============================================================

@dataclass
class TokenAmount:
    """Represents a token amount with formatting.

    Handles conversion between raw (on-chain) and human-readable amounts.
    """

    raw: int
    decimals: int = 18
    symbol: str = ""

    @property
    def formatted(self) -> str:
        """Human-readable amount with symbol."""
        human = Decimal(self.raw) / Decimal(10**self.decimals)
        if self.symbol:
            return f"{human:.{min(self.decimals, 8)}f} {self.symbol}"
        return f"{human:.{min(self.decimals, 8)}f}"

    @property
    def human(self) -> Decimal:
        """Human-readable decimal value."""
        return Decimal(self.raw) / Decimal(10**self.decimals)

    def __str__(self) -> str:
        return self.formatted

    def __repr__(self) -> str:
        return f"TokenAmount({self.formatted})"


@dataclass
class TokenInfo:
    """Token metadata."""

    address: Address
    name: str
    symbol: str
    decimals: int
    total_supply: int = 0


@dataclass
class GasEstimate:
    """Gas estimation result."""

    gas_limit: int
    max_fee_per_gas: int
    max_priority_fee_per_gas: int
    estimated_cost_wei: int

    @property
    def estimated_cost_eth(self) -> Decimal:
        """Estimated cost in ETH."""
        return Decimal(self.estimated_cost_wei) / Decimal(10**18)

    @property
    def estimated_cost_gwei(self) -> Decimal:
        """Estimated cost in gwei."""
        return Decimal(self.estimated_cost_wei) / Decimal(10**9)


@dataclass
class TransactionResult:
    """Result of sending a transaction."""

    hash: TxHash
    block_number: int | None = None
    gas_used: int | None = None
    status: bool | None = None  # True = success, False = reverted, None = pending
    logs: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_pending(self) -> bool:
        """Whether the transaction is still pending."""
        return self.status is None

    @property
    def is_success(self) -> bool:
        """Whether the transaction succeeded."""
        return self.status is True


@dataclass
class WalletBalance:
    """Combined wallet balance summary."""

    address: Address
    eth_balance: TokenAmount
    token_balances: list[TokenAmount] = field(default_factory=list)

    @property
    def has_eth(self) -> bool:
        return self.eth_balance.raw > 0

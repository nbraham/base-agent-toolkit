"""Token swap utilities and routing."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any

from ..types import Address

class SwapProtocol(str, Enum):
    """Supported swap protocols."""
    AERODROME = "aerodrome"
    UNISWAP_V3 = "uniswap_v3"


@dataclass
class SwapQuote:
    """Quote for a token swap."""

    protocol: SwapProtocol
    token_in: Address
    token_out: Address
    amount_in: int
    amount_out: int
    price_impact: float  # as percentage (e.g., 0.5 = 0.5%)
    gas_estimate: int
    route: list[Address]

    @property
    def exchange_rate(self) -> Decimal:
        """Exchange rate (amount_out / amount_in)."""
        if self.amount_in == 0:
            return Decimal(0)
        return Decimal(self.amount_out) / Decimal(self.amount_in)

    @property
    def is_acceptable(self) -> bool:
        """Whether price impact is acceptable (< 5%)."""
        return self.price_impact < 5.0


@dataclass
class SwapResult:
    """Result of an executed swap."""

    tx_hash: str
    amount_in: int
    amount_out: int
    protocol: SwapProtocol
    gas_used: int | None = None


def calculate_min_amount_out(
    amount_out: int,
    slippage_percent: float = 0.5,
) -> int:
    """Calculate minimum output amount with slippage protection.

    Args:
        amount_out: Expected output amount.
        slippage_percent: Maximum acceptable slippage (e.g., 0.5 = 0.5%).

    Returns:
        Minimum acceptable output amount.
    """
    slippage_factor = 1 - (slippage_percent / 100)
    return int(amount_out * slippage_factor)


def swap_tokens(
    token_in: Address,
    token_out: Address,
    amount_in: int,
    slippage: float = 0.5,
) -> SwapQuote:
    """Get the best swap quote across protocols.

    This is a placeholder that would compare quotes from
    multiple DEXs and return the best one.

    Args:
        token_in: Input token address.
        token_out: Output token address.
        amount_in: Input amount (raw).
        slippage: Maximum slippage percentage.

    Returns:
        Best SwapQuote across protocols.
    """
    # In production, this would query multiple DEXs
    # and return the best quote
    return SwapQuote(
        protocol=SwapProtocol.AERODROME,
        token_in=token_in,
        token_out=token_out,
        amount_in=amount_in,
        amount_out=0,
        price_impact=0.0,
        gas_estimate=200_000,
        route=[token_in, token_out],
    )

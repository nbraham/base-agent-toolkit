"""Portfolio tracking for Base DeFi positions."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, TokenAmount
from ..wallet.erc20 import ERC20Token

logger = get_logger(__name__)


@dataclass
class TokenPosition:
    """Single token position in a portfolio."""

    address: Address
    symbol: str
    balance: TokenAmount
    usd_value: Decimal | None = None

    @property
    def formatted(self) -> str:
        if self.usd_value:
            return f"{self.balance.formatted} (${self.usd_value:.2f})"
        return self.balance.formatted


@dataclass
class PortfolioSnapshot:
    """Complete portfolio snapshot."""

    wallet_address: Address
    eth_balance: TokenAmount
    token_positions: list[TokenPosition] = field(default_factory=list)
    block_number: int = 0
    timestamp: int = 0

    @property
    def total_positions(self) -> int:
        return len(self.token_positions) + (1 if self.eth_balance.raw > 0 else 0)

    def get_non_zero(self) -> list[TokenPosition]:
        """Get only positions with non-zero balance."""
        return [p for p in self.token_positions if p.balance.raw > 0]


class PortfolioTracker:
    """Track token holdings across a Base wallet.

    Args:
        provider: BaseProvider instance.
        tracked_tokens: List of token addresses to track.
    """

    def __init__(
        self,
        provider: BaseProvider,
        tracked_tokens: list[Address] | None = None,
    ):
        self._provider = provider
        self._tracked_tokens = tracked_tokens or []

    def add_token(self, token_address: Address) -> None:
        """Add a token to the tracking list."""
        if token_address not in self._tracked_tokens:
            self._tracked_tokens.append(token_address)

    def remove_token(self, token_address: Address) -> None:
        """Remove a token from the tracking list."""
        self._tracked_tokens = [
            t for t in self._tracked_tokens if t != token_address
        ]

    def get_snapshot(self, wallet_address: Address) -> PortfolioSnapshot:
        """Get a complete portfolio snapshot.

        Args:
            wallet_address: Wallet to snapshot.

        Returns:
            PortfolioSnapshot with all tracked balances.
        """
        # ETH balance
        eth_raw = self._provider.get_balance(wallet_address)
        eth_balance = TokenAmount(raw=eth_raw, decimals=18, symbol="ETH")

        # Token balances
        positions = []
        for token_addr in self._tracked_tokens:
            try:
                token = ERC20Token(token_addr, self._provider)
                info = token.get_info()
                balance = token.balance_of(wallet_address)
                positions.append(
                    TokenPosition(
                        address=token_addr,
                        symbol=info.symbol,
                        balance=balance,
                    )
                )
            except Exception as e:
                logger.warning(
                    "portfolio.token_error",
                    token=token_addr,
                    error=str(e),
                )

        block_number = self._provider.get_block_number()

        snapshot = PortfolioSnapshot(
            wallet_address=wallet_address,
            eth_balance=eth_balance,
            token_positions=positions,
            block_number=block_number,
        )

        logger.info(
            "portfolio.snapshot",
            address=wallet_address[:10],
            eth=str(eth_balance),
            tokens=len(positions),
        )

        return snapshot

    def compare_snapshots(
        self,
        old: PortfolioSnapshot,
        new: PortfolioSnapshot,
    ) -> dict[str, Any]:
        """Compare two portfolio snapshots.

        Args:
            old: Previous snapshot.
            new: Current snapshot.

        Returns:
            Dictionary with changes per token.
        """
        changes = {}

        # ETH change
        eth_diff = new.eth_balance.raw - old.eth_balance.raw
        if eth_diff != 0:
            changes["ETH"] = {
                "old": str(old.eth_balance),
                "new": str(new.eth_balance),
                "diff_raw": eth_diff,
            }

        # Token changes
        old_map = {p.address: p for p in old.token_positions}
        new_map = {p.address: p for p in new.token_positions}

        all_tokens = set(old_map.keys()) | set(new_map.keys())
        for addr in all_tokens:
            old_pos = old_map.get(addr)
            new_pos = new_map.get(addr)
            old_raw = old_pos.balance.raw if old_pos else 0
            new_raw = new_pos.balance.raw if new_pos else 0
            diff = new_raw - old_raw

            if diff != 0:
                symbol = (new_pos or old_pos).symbol
                changes[symbol] = {
                    "address": addr,
                    "old_raw": old_raw,
                    "new_raw": new_raw,
                    "diff_raw": diff,
                }

        return changes

    def __repr__(self) -> str:
        return f"PortfolioTracker(tokens={len(self._tracked_tokens)})"

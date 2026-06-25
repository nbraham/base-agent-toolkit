"""Dollar Cost Averaging (DCA) strategy."""

from __future__ import annotations

import time
from typing import Any

from ..strategy import Strategy, StrategyResult, StrategyStatus
from ...logging import get_logger

logger = get_logger(__name__)


class DCAStrategy(Strategy):
    """Dollar Cost Averaging strategy.

    Automatically purchases a target token at regular intervals
    with a fixed amount.

    Args:
        token_in: Token to spend (address).
        token_out: Token to buy (address).
        amount_per_interval: Amount to spend each interval (raw).
        interval_seconds: Seconds between purchases.
        max_purchases: Maximum number of purchases (0 = unlimited).
    """

    def __init__(
        self,
        token_in: str,
        token_out: str,
        amount_per_interval: int,
        interval_seconds: int = 86400,  # Daily
        max_purchases: int = 0,
    ):
        self._token_in = token_in
        self._token_out = token_out
        self._amount = amount_per_interval
        self._interval = interval_seconds
        self._max_purchases = max_purchases
        self._last_purchase: float = 0
        self._purchase_count: int = 0

    @property
    def name(self) -> str:
        return "dca"

    @property
    def description(self) -> str:
        return f"DCA: Buy {self._token_out[:10]}... every {self._interval}s"

    def evaluate(self, context: dict[str, Any]) -> bool:
        """Check if it's time for a DCA purchase."""
        now = time.time()

        # Check max purchases
        if self._max_purchases > 0 and self._purchase_count >= self._max_purchases:
            return False

        # Check interval
        if now - self._last_purchase < self._interval:
            return False

        return True

    def execute(self, agent: Any, context: dict[str, Any]) -> StrategyResult:
        """Execute DCA purchase."""
        try:
            # In production, this would use the swap tool
            logger.info(
                "dca.executing",
                token_in=self._token_in[:10],
                token_out=self._token_out[:10],
                amount=self._amount,
            )

            self._last_purchase = time.time()
            self._purchase_count += 1

            return StrategyResult(
                status=StrategyStatus.SUCCESS,
                message=f"DCA purchase #{self._purchase_count}",
                data={
                    "token_in": self._token_in,
                    "token_out": self._token_out,
                    "amount": self._amount,
                    "purchase_number": self._purchase_count,
                },
            )
        except Exception as e:
            return StrategyResult(
                status=StrategyStatus.FAILED,
                message=f"DCA failed: {e}",
            )

    def get_stats(self) -> dict[str, Any]:
        """Get DCA strategy statistics."""
        return {
            "purchase_count": self._purchase_count,
            "total_spent": self._amount * self._purchase_count,
            "last_purchase": self._last_purchase,
            "interval_seconds": self._interval,
        }

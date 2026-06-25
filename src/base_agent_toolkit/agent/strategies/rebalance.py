"""Portfolio rebalancing strategy."""

from __future__ import annotations

from typing import Any

from ..strategy import Strategy, StrategyResult, StrategyStatus
from ...logging import get_logger

logger = get_logger(__name__)


class RebalanceStrategy(Strategy):
    """Portfolio rebalancing strategy.

    Maintains target allocation percentages across tokens.
    When allocations drift beyond a threshold, triggers
    rebalancing trades.

    Args:
        targets: Dict of token address → target percentage (0-100).
        threshold_percent: Minimum drift to trigger rebalance.
    """

    def __init__(
        self,
        targets: dict[str, float],
        threshold_percent: float = 5.0,
    ):
        self._targets = targets
        self._threshold = threshold_percent

        # Validate targets sum to 100
        total = sum(targets.values())
        if abs(total - 100) > 0.01:
            raise ValueError(f"Target allocations must sum to 100, got {total}")

    @property
    def name(self) -> str:
        return "rebalance"

    @property
    def description(self) -> str:
        return f"Rebalance portfolio ({len(self._targets)} tokens, {self._threshold}% threshold)"

    def validate(self, context: dict[str, Any]) -> list[str]:
        """Validate context has required portfolio data."""
        errors = []
        if "portfolio" not in context:
            errors.append("Missing 'portfolio' in context")
        return errors

    def evaluate(self, context: dict[str, Any]) -> bool:
        """Check if rebalancing is needed."""
        portfolio = context.get("portfolio", {})

        # Calculate current allocations
        total_value = sum(portfolio.values())
        if total_value == 0:
            return False

        for token, target_pct in self._targets.items():
            current_value = portfolio.get(token, 0)
            current_pct = (current_value / total_value) * 100
            drift = abs(current_pct - target_pct)

            if drift > self._threshold:
                logger.info(
                    "rebalance.drift_detected",
                    token=token[:10],
                    current=f"{current_pct:.1f}%",
                    target=f"{target_pct:.1f}%",
                    drift=f"{drift:.1f}%",
                )
                return True

        return False

    def execute(self, agent: Any, context: dict[str, Any]) -> StrategyResult:
        """Execute rebalancing trades."""
        portfolio = context.get("portfolio", {})
        total_value = sum(portfolio.values())

        trades = []
        for token, target_pct in self._targets.items():
            current_value = portfolio.get(token, 0)
            target_value = total_value * (target_pct / 100)
            diff = target_value - current_value

            if abs(diff) > total_value * (self._threshold / 100):
                trades.append({
                    "token": token,
                    "action": "buy" if diff > 0 else "sell",
                    "amount_value": abs(diff),
                })

        logger.info(
            "rebalance.executing",
            trades=len(trades),
        )

        return StrategyResult(
            status=StrategyStatus.SUCCESS,
            message=f"Planned {len(trades)} rebalancing trades",
            data={"trades": trades, "total_value": total_value},
        )

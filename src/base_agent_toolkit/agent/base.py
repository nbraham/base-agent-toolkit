"""Base agent implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address
from ..wallet.wallet import BaseWallet

logger = get_logger(__name__)


@dataclass
class AgentConfig:
    """Configuration for a Base AI agent.

    Args:
        name: Agent display name.
        description: Brief description of what the agent does.
        wallet: BaseWallet for chain interactions.
        provider: BaseProvider for RPC access.
        max_gas_per_tx: Maximum gas per transaction (wei).
        daily_budget_wei: Daily spending budget in wei.
        dry_run: If True, simulate but don't send transactions.
        allowed_protocols: List of allowed DeFi protocols.
    """

    name: str
    description: str = ""
    wallet: BaseWallet | None = None
    provider: BaseProvider | None = None
    max_gas_per_tx: int = 1_000_000
    daily_budget_wei: int = 0  # 0 = unlimited
    dry_run: bool = False
    allowed_protocols: list[str] = field(default_factory=list)


class BaseAgent:
    """AI agent that interacts with Base chain.

    The BaseAgent provides a high-level interface for AI models
    to interact with Base, including wallet management, DeFi,
    and x402 payments.

    Args:
        config: AgentConfig instance.
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self._spent_today_wei: int = 0
        self._tx_count: int = 0
        self._actions_log: list[dict[str, Any]] = []

        logger.info(
            "agent.initialized",
            name=config.name,
            dry_run=config.dry_run,
        )

    @property
    def name(self) -> str:
        """Agent name."""
        return self.config.name

    @property
    def wallet(self) -> BaseWallet | None:
        """Agent's wallet."""
        return self.config.wallet

    @property
    def provider(self) -> BaseProvider | None:
        """Agent's provider."""
        return self.config.provider

    @property
    def is_dry_run(self) -> bool:
        """Whether agent is in dry-run mode."""
        return self.config.dry_run

    @property
    def spent_today(self) -> int:
        """Total wei spent today."""
        return self._spent_today_wei

    @property
    def tx_count(self) -> int:
        """Number of transactions sent."""
        return self._tx_count

    def check_budget(self, cost_wei: int) -> bool:
        """Check if a transaction is within budget.

        Args:
            cost_wei: Expected transaction cost in wei.

        Returns:
            True if within budget.
        """
        if self.config.daily_budget_wei == 0:
            return True  # Unlimited
        return (self._spent_today_wei + cost_wei) <= self.config.daily_budget_wei

    def record_spend(self, amount_wei: int, description: str = "") -> None:
        """Record a spending event.

        Args:
            amount_wei: Amount spent in wei.
            description: Description of the spend.
        """
        self._spent_today_wei += amount_wei
        self._tx_count += 1
        self._actions_log.append({
            "type": "spend",
            "amount_wei": amount_wei,
            "description": description,
            "tx_count": self._tx_count,
        })

        logger.info(
            "agent.spend_recorded",
            amount_wei=amount_wei,
            total_today=self._spent_today_wei,
            description=description,
        )

    def reset_daily_budget(self) -> None:
        """Reset the daily spending counter."""
        self._spent_today_wei = 0
        logger.info("agent.budget_reset")

    def get_actions_log(self) -> list[dict[str, Any]]:
        """Get the agent's action history."""
        return list(self._actions_log)

    def get_status(self) -> dict[str, Any]:
        """Get agent status summary.

        Returns:
            Dictionary with agent state.
        """
        status = {
            "name": self.config.name,
            "dry_run": self.config.dry_run,
            "tx_count": self._tx_count,
            "spent_today_wei": self._spent_today_wei,
            "budget_remaining_wei": (
                self.config.daily_budget_wei - self._spent_today_wei
                if self.config.daily_budget_wei > 0
                else "unlimited"
            ),
        }

        if self.wallet:
            status["address"] = self.wallet.address
        if self.provider:
            status["connected"] = self.provider.is_connected()

        return status

    def __repr__(self) -> str:
        return f"BaseAgent(name={self.config.name!r}, dry_run={self.config.dry_run})"

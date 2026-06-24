"""Strategy framework for agent decision-making."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StrategyStatus(str, Enum):
    """Status of a strategy execution."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PARTIAL = "partial"


@dataclass
class StrategyResult:
    """Result of executing a strategy.

    Attributes:
        status: Execution status.
        message: Human-readable result message.
        data: Strategy-specific result data.
        transactions: List of transaction hashes executed.
        gas_used: Total gas used.
    """

    status: StrategyStatus
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    transactions: list[str] = field(default_factory=list)
    gas_used: int = 0

    @property
    def is_success(self) -> bool:
        return self.status == StrategyStatus.SUCCESS

    @property
    def tx_count(self) -> int:
        return len(self.transactions)


class Strategy(ABC):
    """Abstract base class for agent strategies.

    A strategy encapsulates a specific behavior or trading logic
    that an agent can execute. Strategies should be stateless
    and produce deterministic results given the same inputs.

    Example:
        class DCAStrategy(Strategy):
            def evaluate(self, context):
                # Check if it's time to buy
                ...
                return True

            def execute(self, agent, context):
                # Execute the DCA purchase
                ...
                return StrategyResult(status=StrategyStatus.SUCCESS)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name for identification."""
        ...

    @property
    def description(self) -> str:
        """Optional description of what this strategy does."""
        return ""

    @abstractmethod
    def evaluate(self, context: dict[str, Any]) -> bool:
        """Evaluate whether this strategy should execute.

        Args:
            context: Current market/agent context.

        Returns:
            True if the strategy should execute.
        """
        ...

    @abstractmethod
    def execute(
        self,
        agent: Any,
        context: dict[str, Any],
    ) -> StrategyResult:
        """Execute the strategy.

        Args:
            agent: BaseAgent instance.
            context: Current market/agent context.

        Returns:
            StrategyResult with execution details.
        """
        ...

    def validate(self, context: dict[str, Any]) -> list[str]:
        """Validate that context has required data.

        Override this to add custom validation.

        Args:
            context: Context to validate.

        Returns:
            List of validation error messages (empty = valid).
        """
        return []

    def __repr__(self) -> str:
        return f"Strategy({self.name!r})"

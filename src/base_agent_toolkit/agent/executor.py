"""Agent executor for running strategies."""

from __future__ import annotations

import time
from typing import Any

from ..logging import get_logger
from .base import BaseAgent
from .strategy import Strategy, StrategyResult, StrategyStatus

logger = get_logger(__name__)


class AgentExecutor:
    """Executes strategies on behalf of an agent.

    The executor manages the lifecycle of strategy execution,
    including evaluation, execution, and result recording.

    Args:
        agent: BaseAgent instance.
        strategies: List of strategies to run.
    """

    def __init__(
        self,
        agent: BaseAgent,
        strategies: list[Strategy] | None = None,
    ):
        self._agent = agent
        self._strategies = strategies or []
        self._results: list[dict[str, Any]] = []

    def add_strategy(self, strategy: Strategy) -> None:
        """Add a strategy to the executor."""
        self._strategies.append(strategy)
        logger.info("executor.strategy_added", name=strategy.name)

    def remove_strategy(self, name: str) -> None:
        """Remove a strategy by name."""
        self._strategies = [s for s in self._strategies if s.name != name]

    def run_once(self, context: dict[str, Any] | None = None) -> list[StrategyResult]:
        """Run all strategies once.

        Args:
            context: Shared context for all strategies.

        Returns:
            List of StrategyResult for each strategy.
        """
        context = context or {}
        results = []

        for strategy in self._strategies:
            result = self._execute_strategy(strategy, context)
            results.append(result)

        return results

    def _execute_strategy(
        self,
        strategy: Strategy,
        context: dict[str, Any],
    ) -> StrategyResult:
        """Execute a single strategy with error handling.

        Args:
            strategy: Strategy to execute.
            context: Execution context.

        Returns:
            StrategyResult.
        """
        start_time = time.monotonic()

        # Validate
        errors = strategy.validate(context)
        if errors:
            result = StrategyResult(
                status=StrategyStatus.SKIPPED,
                message=f"Validation failed: {', '.join(errors)}",
            )
            self._record_result(strategy, result, time.monotonic() - start_time)
            return result

        # Evaluate
        try:
            should_run = strategy.evaluate(context)
        except Exception as e:
            result = StrategyResult(
                status=StrategyStatus.FAILED,
                message=f"Evaluation error: {e}",
            )
            self._record_result(strategy, result, time.monotonic() - start_time)
            return result

        if not should_run:
            result = StrategyResult(
                status=StrategyStatus.SKIPPED,
                message="Strategy conditions not met",
            )
            self._record_result(strategy, result, time.monotonic() - start_time)
            return result

        # Execute
        try:
            if self._agent.is_dry_run:
                result = StrategyResult(
                    status=StrategyStatus.SUCCESS,
                    message="[DRY RUN] Would have executed",
                )
            else:
                result = strategy.execute(self._agent, context)
        except Exception as e:
            result = StrategyResult(
                status=StrategyStatus.FAILED,
                message=f"Execution error: {e}",
            )

        elapsed = time.monotonic() - start_time
        self._record_result(strategy, result, elapsed)
        return result

    def _record_result(
        self,
        strategy: Strategy,
        result: StrategyResult,
        elapsed_seconds: float,
    ) -> None:
        """Record a strategy execution result."""
        record = {
            "strategy": strategy.name,
            "status": result.status.value,
            "message": result.message,
            "tx_count": result.tx_count,
            "gas_used": result.gas_used,
            "elapsed_seconds": round(elapsed_seconds, 3),
        }
        self._results.append(record)

        logger.info(
            "executor.strategy_completed",
            strategy=strategy.name,
            status=result.status.value,
            elapsed=f"{elapsed_seconds:.3f}s",
        )

    def get_history(self) -> list[dict[str, Any]]:
        """Get execution history."""
        return list(self._results)

    def get_summary(self) -> dict[str, Any]:
        """Get execution summary.

        Returns:
            Summary with counts per status.
        """
        total = len(self._results)
        by_status = {}
        for r in self._results:
            status = r["status"]
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total_executions": total,
            "by_status": by_status,
            "strategies": [s.name for s in self._strategies],
        }

    def __repr__(self) -> str:
        return f"AgentExecutor(strategies={len(self._strategies)})"

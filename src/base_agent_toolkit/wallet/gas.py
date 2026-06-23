"""Gas price oracle and estimation for Base chain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..constants import (
    DEFAULT_MAX_GAS_PRICE_GWEI,
    DEFAULT_PRIORITY_FEE_GWEI,
    EIP1559_BASE_FEE_MULTIPLIER,
)
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import GasEstimate

logger = get_logger(__name__)


@dataclass
class GasPriceInfo:
    """Current gas price information."""

    base_fee_gwei: float
    priority_fee_gwei: float
    gas_price_gwei: float
    block_number: int

    @property
    def max_fee_gwei(self) -> float:
        """Recommended max fee per gas (base * 1.25 + priority)."""
        return self.base_fee_gwei * EIP1559_BASE_FEE_MULTIPLIER + self.priority_fee_gwei

    @property
    def max_fee_wei(self) -> int:
        return int(self.max_fee_gwei * 1e9)

    @property
    def priority_fee_wei(self) -> int:
        return int(self.priority_fee_gwei * 1e9)


class GasOracle:
    """Gas price oracle for Base chain.

    Provides current gas price information and EIP-1559
    fee recommendations.

    Args:
        provider: BaseProvider instance.
        max_gas_price_gwei: Maximum acceptable gas price.
    """

    def __init__(
        self,
        provider: BaseProvider,
        max_gas_price_gwei: float = DEFAULT_MAX_GAS_PRICE_GWEI,
    ):
        self._provider = provider
        self.max_gas_price_gwei = max_gas_price_gwei

    def get_gas_price(self) -> GasPriceInfo:
        """Get current gas price information.

        Returns:
            GasPriceInfo with base fee and priority fee.
        """
        latest = self._provider.get_block("latest")
        base_fee_wei = latest.get("baseFeePerGas", 0)
        gas_price_wei = self._provider.get_gas_price()
        block_number = latest.get("number", 0)

        base_fee_gwei = base_fee_wei / 1e9
        gas_price_gwei = gas_price_wei / 1e9
        priority_fee_gwei = max(
            gas_price_gwei - base_fee_gwei,
            DEFAULT_PRIORITY_FEE_GWEI,
        )

        info = GasPriceInfo(
            base_fee_gwei=base_fee_gwei,
            priority_fee_gwei=priority_fee_gwei,
            gas_price_gwei=gas_price_gwei,
            block_number=block_number,
        )

        logger.debug(
            "gas_oracle.price",
            base_fee=f"{base_fee_gwei:.4f} gwei",
            priority_fee=f"{priority_fee_gwei:.4f} gwei",
            max_fee=f"{info.max_fee_gwei:.4f} gwei",
        )

        return info

    def estimate_transaction_cost(
        self,
        gas_units: int,
        gas_price_info: GasPriceInfo | None = None,
    ) -> GasEstimate:
        """Estimate the cost of a transaction in ETH.

        Args:
            gas_units: Gas units required.
            gas_price_info: Optional pre-fetched gas price info.

        Returns:
            GasEstimate with cost breakdown.
        """
        if gas_price_info is None:
            gas_price_info = self.get_gas_price()

        max_fee_wei = gas_price_info.max_fee_wei
        priority_fee_wei = gas_price_info.priority_fee_wei
        estimated_cost = gas_units * max_fee_wei

        return GasEstimate(
            gas_limit=gas_units,
            max_fee_per_gas=max_fee_wei,
            max_priority_fee_per_gas=priority_fee_wei,
            estimated_cost_wei=estimated_cost,
        )

    def is_gas_acceptable(self, gas_price_info: GasPriceInfo | None = None) -> bool:
        """Check if current gas price is below the maximum threshold.

        Args:
            gas_price_info: Optional pre-fetched gas price info.

        Returns:
            True if gas price is acceptable.
        """
        if gas_price_info is None:
            gas_price_info = self.get_gas_price()
        return gas_price_info.gas_price_gwei <= self.max_gas_price_gwei

    def wait_for_low_gas(
        self,
        target_gwei: float | None = None,
        timeout_seconds: int = 300,
        poll_interval: float = 5.0,
    ) -> GasPriceInfo:
        """Wait until gas price drops below a target.

        Args:
            target_gwei: Target gas price in gwei.
            timeout_seconds: Maximum wait time.
            poll_interval: Seconds between checks.

        Returns:
            GasPriceInfo when target is reached.

        Raises:
            TimeoutError: If gas price doesn't drop within timeout.
        """
        import time

        target = target_gwei or self.max_gas_price_gwei
        start = time.monotonic()

        while True:
            info = self.get_gas_price()
            if info.gas_price_gwei <= target:
                return info

            elapsed = time.monotonic() - start
            if elapsed >= timeout_seconds:
                raise TimeoutError(
                    f"Gas price ({info.gas_price_gwei:.2f} gwei) didn't drop "
                    f"below {target:.2f} gwei within {timeout_seconds}s"
                )

            logger.debug(
                "gas_oracle.waiting",
                current=f"{info.gas_price_gwei:.2f} gwei",
                target=f"{target:.2f} gwei",
            )
            time.sleep(poll_interval)

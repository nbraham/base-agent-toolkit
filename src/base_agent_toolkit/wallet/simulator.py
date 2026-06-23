"""Transaction simulation (dry-run) support."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web3 import Web3

from ..exceptions import TransactionError
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, GasEstimate, Wei

logger = get_logger(__name__)


@dataclass
class SimulationResult:
    """Result of a transaction simulation."""

    success: bool
    gas_used: int
    return_data: bytes | None = None
    error_message: str | None = None
    gas_estimate: GasEstimate | None = None

    @property
    def would_revert(self) -> bool:
        """Whether the transaction would revert on-chain."""
        return not self.success


def simulate_transaction(
    provider: BaseProvider,
    from_address: Address,
    to: Address,
    value: Wei = 0,
    data: bytes = b"",
) -> SimulationResult:
    """Simulate a transaction using eth_call without sending it.

    This is useful for:
    - Checking if a transaction would succeed before sending
    - Getting the return value of a write function
    - Estimating gas accurately

    Args:
        provider: BaseProvider instance.
        from_address: Sender address.
        to: Destination address.
        value: ETH value in wei.
        data: Transaction data.

    Returns:
        SimulationResult with success status and gas info.
    """
    tx: dict[str, Any] = {
        "from": Web3.to_checksum_address(from_address),
        "to": Web3.to_checksum_address(to),
        "value": value,
    }
    if data:
        tx["data"] = data

    try:
        # eth_call simulates without state change
        return_data = provider.call(tx)

        # Also estimate gas
        gas_used = provider.estimate_gas(tx)

        logger.info(
            "simulator.success",
            to=to,
            gas_used=gas_used,
        )

        return SimulationResult(
            success=True,
            gas_used=gas_used,
            return_data=return_data,
        )

    except Exception as e:
        error_msg = str(e)
        logger.warning(
            "simulator.would_revert",
            to=to,
            error=error_msg,
        )

        return SimulationResult(
            success=False,
            gas_used=0,
            error_message=error_msg,
        )


def simulate_contract_call(
    provider: BaseProvider,
    from_address: Address,
    contract_address: Address,
    function_abi: dict[str, Any],
    *args: Any,
    value: Wei = 0,
) -> SimulationResult:
    """Simulate a contract function call.

    Args:
        provider: BaseProvider instance.
        from_address: Sender address.
        contract_address: Contract address.
        function_abi: ABI of the function to call.
        *args: Function arguments.
        value: ETH value in wei.

    Returns:
        SimulationResult.
    """
    contract = provider.w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=[function_abi],
    )

    fn_name = function_abi["name"]
    fn = contract.functions[fn_name]
    data = fn(*args)._encode_transaction_data()

    return simulate_transaction(
        provider=provider,
        from_address=from_address,
        to=contract_address,
        value=value,
        data=bytes.fromhex(data[2:]) if isinstance(data, str) else data,
    )

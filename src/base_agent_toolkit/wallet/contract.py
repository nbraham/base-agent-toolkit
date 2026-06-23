"""Generic smart contract interaction wrapper."""

from __future__ import annotations

from typing import Any

from web3 import Web3
from web3.contract import Contract

from ..exceptions import ContractError, ContractNotFoundError
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, TransactionResult

logger = get_logger(__name__)


class ContractWrapper:
    """Wrapper for generic smart contract interactions.

    Provides simplified read/write methods for any contract
    given its ABI.

    Args:
        address: Contract address.
        abi: Contract ABI (list of function/event definitions).
        provider: BaseProvider instance.
    """

    def __init__(
        self,
        address: Address,
        abi: list[dict[str, Any]],
        provider: BaseProvider,
    ):
        self._address = Web3.to_checksum_address(address)
        self._provider = provider
        self._abi = abi

        # Verify contract exists
        code = provider.w3.eth.get_code(self._address)
        if code == b"" or code == b"0x":
            raise ContractNotFoundError(
                f"No contract found at {self._address}",
                details={"address": self._address},
            )

        self._contract: Contract = provider.w3.eth.contract(
            address=self._address,
            abi=abi,
        )

        logger.debug("contract.loaded", address=self._address)

    @property
    def address(self) -> Address:
        """Contract address."""
        return self._address

    @property
    def contract(self) -> Contract:
        """Web3 Contract instance."""
        return self._contract

    def read(self, function_name: str, *args: Any) -> Any:
        """Call a read-only contract function.

        Args:
            function_name: Name of the contract function.
            *args: Function arguments.

        Returns:
            Function return value.

        Raises:
            ContractError: If the call fails.
        """
        try:
            fn = self._contract.functions[function_name]
            result = fn(*args).call()
            logger.debug(
                "contract.read",
                address=self._address,
                function=function_name,
                args=args,
            )
            return result
        except Exception as e:
            raise ContractError(
                f"Failed to call {function_name}: {e}",
                details={
                    "address": self._address,
                    "function": function_name,
                    "args": args,
                },
            )

    def build_tx(
        self,
        function_name: str,
        *args: Any,
        value: int = 0,
        gas: int | None = None,
    ) -> dict[str, Any]:
        """Build an unsigned transaction for a write function.

        Args:
            function_name: Name of the contract function.
            *args: Function arguments.
            value: ETH value in wei to send with the call.
            gas: Optional gas limit.

        Returns:
            Unsigned transaction dictionary.
        """
        try:
            fn = self._contract.functions[function_name]
            tx_params: dict[str, Any] = {"value": value}
            if gas:
                tx_params["gas"] = gas
            return fn(*args).build_transaction(tx_params)
        except Exception as e:
            raise ContractError(
                f"Failed to build tx for {function_name}: {e}",
                details={
                    "address": self._address,
                    "function": function_name,
                    "args": args,
                },
            )

    def get_events(
        self,
        event_name: str,
        from_block: int | str = "latest",
        to_block: int | str = "latest",
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Get past events from the contract.

        Args:
            event_name: Name of the event.
            from_block: Start block.
            to_block: End block.
            filters: Event argument filters.

        Returns:
            List of event log dictionaries.
        """
        try:
            event = self._contract.events[event_name]
            event_filter = event.create_filter(
                fromBlock=from_block,
                toBlock=to_block,
                argument_filters=filters or {},
            )
            entries = event_filter.get_all_entries()
            return [dict(entry) for entry in entries]
        except Exception as e:
            raise ContractError(
                f"Failed to get events for {event_name}: {e}",
                details={
                    "address": self._address,
                    "event": event_name,
                },
            )

    def __repr__(self) -> str:
        return f"ContractWrapper({self._address})"

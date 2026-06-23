"""Transaction builder for constructing complex transactions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from web3 import Web3

from ..logging import get_logger
from ..types import Address, Wei

logger = get_logger(__name__)


@dataclass
class TransactionRequest:
    """Represents a single transaction to be sent."""

    to: Address
    value: Wei = 0
    data: bytes = b""
    gas: int | None = None
    description: str = ""


class TransactionBuilder:
    """Builder for constructing and batching transactions.

    Provides a fluent interface for building transactions
    with automatic gas estimation and nonce management.

    Example:
        builder = TransactionBuilder(wallet)
        builder.add_eth_transfer("0x...", amount_wei=1000)
        builder.add_contract_call(contract, "transfer", to, amount)
        results = builder.execute_all()
    """

    def __init__(self, wallet: Any):
        self._wallet = wallet
        self._transactions: list[TransactionRequest] = []

    def add_eth_transfer(
        self,
        to: Address,
        amount_wei: Wei,
        description: str = "",
    ) -> "TransactionBuilder":
        """Add an ETH transfer to the batch.

        Args:
            to: Recipient address.
            amount_wei: Amount in wei.
            description: Optional description for logging.

        Returns:
            Self for chaining.
        """
        self._transactions.append(
            TransactionRequest(
                to=to,
                value=amount_wei,
                description=description or f"Send {amount_wei} wei to {to}",
            )
        )
        return self

    def add_contract_call(
        self,
        contract_address: Address,
        data: bytes,
        value: Wei = 0,
        gas: int | None = None,
        description: str = "",
    ) -> "TransactionBuilder":
        """Add a contract call to the batch.

        Args:
            contract_address: Contract address.
            data: Encoded function call data.
            value: ETH value in wei.
            gas: Optional gas limit.
            description: Optional description.

        Returns:
            Self for chaining.
        """
        self._transactions.append(
            TransactionRequest(
                to=contract_address,
                value=value,
                data=data,
                gas=gas,
                description=description or f"Call {contract_address}",
            )
        )
        return self

    def clear(self) -> None:
        """Clear all pending transactions."""
        self._transactions.clear()

    @property
    def count(self) -> int:
        """Number of pending transactions."""
        return len(self._transactions)

    def preview(self) -> list[dict[str, Any]]:
        """Preview all pending transactions.

        Returns:
            List of transaction summaries.
        """
        previews = []
        for i, tx in enumerate(self._transactions):
            previews.append({
                "index": i,
                "to": tx.to,
                "value": tx.value,
                "has_data": len(tx.data) > 0,
                "gas": tx.gas,
                "description": tx.description,
            })
        return previews

    def execute_all(self) -> list[dict[str, Any]]:
        """Execute all pending transactions sequentially.

        Returns:
            List of results with tx_hash and status.
        """
        results = []
        for i, tx_req in enumerate(self._transactions):
            logger.info(
                "tx_builder.executing",
                index=i,
                total=len(self._transactions),
                description=tx_req.description,
            )

            try:
                result = self._wallet.send_eth(
                    to=tx_req.to,
                    amount_wei=tx_req.value,
                )
                results.append({
                    "index": i,
                    "tx_hash": result.hash,
                    "status": "sent",
                    "description": tx_req.description,
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "status": "failed",
                    "error": str(e),
                    "description": tx_req.description,
                })
                logger.error(
                    "tx_builder.failed",
                    index=i,
                    error=str(e),
                )

        self.clear()
        return results

    def __repr__(self) -> str:
        return f"TransactionBuilder(pending={self.count})"

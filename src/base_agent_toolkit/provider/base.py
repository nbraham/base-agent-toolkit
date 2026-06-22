"""Base RPC provider implementation."""

from __future__ import annotations

import asyncio
from typing import Any

from web3 import AsyncWeb3, Web3
from web3.providers import AsyncHTTPProvider, HTTPProvider

from ..constants import DEFAULT_RPC_URLS, RPC_REQUEST_TIMEOUT_SECONDS
from ..exceptions import ProviderError
from ..logging import get_logger
from ..types import Address, BlockNumber, Network, Wei

logger = get_logger(__name__)


class BaseProvider:
    """RPC provider for Base chain with sync and async support.

    Provides a thin wrapper around web3.py with Base-specific defaults
    and convenient helper methods.

    Args:
        rpc_url: RPC endpoint URL.
        chain_id: Chain ID (8453 for mainnet, 84532 for sepolia).
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        rpc_url: str | None = None,
        chain_id: int = 8453,
        timeout: int = RPC_REQUEST_TIMEOUT_SECONDS,
    ):
        self.chain_id = chain_id
        self.timeout = timeout

        if rpc_url is None:
            urls = DEFAULT_RPC_URLS.get(chain_id, [])
            if not urls:
                raise ProviderError(f"No default RPC URL for chain {chain_id}")
            rpc_url = urls[0]

        self.rpc_url = rpc_url
        self._w3 = Web3(HTTPProvider(rpc_url, request_kwargs={"timeout": timeout}))
        self._async_w3 = AsyncWeb3(
            AsyncHTTPProvider(rpc_url, request_kwargs={"timeout": timeout})
        )

        logger.info("provider.initialized", rpc_url=rpc_url, chain_id=chain_id)

    @property
    def w3(self) -> Web3:
        """Get the synchronous Web3 instance."""
        return self._w3

    @property
    def async_w3(self) -> AsyncWeb3:
        """Get the asynchronous Web3 instance."""
        return self._async_w3

    def get_balance(self, address: Address) -> Wei:
        """Get ETH balance of an address.

        Args:
            address: Ethereum address to check.

        Returns:
            Balance in wei.
        """
        checksum = Web3.to_checksum_address(address)
        return self._w3.eth.get_balance(checksum)

    async def async_get_balance(self, address: Address) -> Wei:
        """Async version of get_balance."""
        checksum = Web3.to_checksum_address(address)
        return await self._async_w3.eth.get_balance(checksum)

    def get_block(self, block_id: BlockNumber | str = "latest") -> dict[str, Any]:
        """Get block by number or tag.

        Args:
            block_id: Block number or tag ('latest', 'pending', etc.)

        Returns:
            Block data dictionary.
        """
        return dict(self._w3.eth.get_block(block_id))

    def get_block_number(self) -> BlockNumber:
        """Get the latest block number."""
        return self._w3.eth.block_number

    async def async_get_block_number(self) -> BlockNumber:
        """Async version of get_block_number."""
        return await self._async_w3.eth.block_number

    def get_transaction(self, tx_hash: str) -> dict[str, Any]:
        """Get transaction by hash.

        Args:
            tx_hash: Transaction hash.

        Returns:
            Transaction data dictionary.
        """
        return dict(self._w3.eth.get_transaction(tx_hash))

    def get_transaction_receipt(self, tx_hash: str) -> dict[str, Any] | None:
        """Get transaction receipt.

        Args:
            tx_hash: Transaction hash.

        Returns:
            Receipt dictionary or None if not yet mined.
        """
        try:
            receipt = self._w3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt) if receipt else None
        except Exception:
            return None

    def get_gas_price(self) -> Wei:
        """Get current gas price in wei."""
        return self._w3.eth.gas_price

    def estimate_gas(self, transaction: dict[str, Any]) -> int:
        """Estimate gas for a transaction.

        Args:
            transaction: Transaction dictionary.

        Returns:
            Estimated gas units.
        """
        return self._w3.eth.estimate_gas(transaction)

    def get_nonce(self, address: Address) -> int:
        """Get transaction count (nonce) for an address.

        Args:
            address: Ethereum address.

        Returns:
            Current nonce.
        """
        checksum = Web3.to_checksum_address(address)
        return self._w3.eth.get_transaction_count(checksum)

    def call(self, transaction: dict[str, Any]) -> bytes:
        """Execute a call (read-only, no state change).

        Args:
            transaction: Transaction dictionary.

        Returns:
            Call result bytes.
        """
        return self._w3.eth.call(transaction)

    def is_connected(self) -> bool:
        """Check if provider is connected to the network."""
        try:
            return self._w3.is_connected()
        except Exception:
            return False

    def __repr__(self) -> str:
        return f"BaseProvider(rpc_url={self.rpc_url!r}, chain_id={self.chain_id})"

"""Wrapped ETH (WETH) helper for Base."""

from __future__ import annotations

from typing import Any

from web3 import Web3

from ..constants import WETH_ADDRESS
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, TokenAmount, Wei
from .abi import WETH_ABI

logger = get_logger(__name__)


class WETHHelper:
    """Helper for wrapping and unwrapping ETH on Base.

    Many DeFi protocols require WETH instead of native ETH.
    This helper simplifies the wrap/unwrap process.

    Args:
        provider: BaseProvider instance.
        weth_address: Override WETH address.
    """

    def __init__(
        self,
        provider: BaseProvider,
        weth_address: Address = WETH_ADDRESS,
    ):
        self._provider = provider
        self._address = Web3.to_checksum_address(weth_address)
        self._contract = provider.w3.eth.contract(
            address=self._address,
            abi=WETH_ABI,
        )

    def get_balance(self, address: Address) -> TokenAmount:
        """Get WETH balance of an address.

        Args:
            address: Address to check.

        Returns:
            TokenAmount with WETH balance.
        """
        raw = self._contract.functions.balanceOf(
            Web3.to_checksum_address(address)
        ).call()
        return TokenAmount(raw=raw, decimals=18, symbol="WETH")

    def build_wrap_tx(self, amount_wei: Wei) -> dict[str, Any]:
        """Build a transaction to wrap ETH → WETH.

        Args:
            amount_wei: Amount of ETH to wrap (in wei).

        Returns:
            Unsigned transaction with value.
        """
        tx = self._contract.functions.deposit().build_transaction(
            {"value": amount_wei, "gas": 50_000}
        )

        logger.info("weth.wrap_tx_built", amount_wei=amount_wei)
        return tx

    def build_unwrap_tx(self, amount_wei: Wei) -> dict[str, Any]:
        """Build a transaction to unwrap WETH → ETH.

        Args:
            amount_wei: Amount of WETH to unwrap (in wei).

        Returns:
            Unsigned transaction dictionary.
        """
        tx = self._contract.functions.withdraw(amount_wei).build_transaction(
            {"gas": 50_000}
        )

        logger.info("weth.unwrap_tx_built", amount_wei=amount_wei)
        return tx

    def __repr__(self) -> str:
        return f"WETHHelper({self._address})"

"""Uniswap V3 integration for Base."""

from __future__ import annotations

from typing import Any

from web3 import Web3

from ..constants import UNISWAP_V3_QUOTER, UNISWAP_V3_ROUTER
from ..exceptions import DeFiError
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address
from .abi import UNISWAP_V3_QUOTER_ABI, UNISWAP_V3_ROUTER_ABI
from .swap import SwapProtocol, SwapQuote

logger = get_logger(__name__)

# Common fee tiers
FEE_LOWEST = 100    # 0.01%
FEE_LOW = 500       # 0.05%
FEE_MEDIUM = 3000   # 0.3%
FEE_HIGH = 10000    # 1%


class UniswapV3Router:
    """Interface to Uniswap V3 on Base.

    Supports exact input single-hop and multi-hop swaps.

    Args:
        provider: BaseProvider instance.
        router_address: Override router address.
        quoter_address: Override quoter address.
    """

    def __init__(
        self,
        provider: BaseProvider,
        router_address: Address = UNISWAP_V3_ROUTER,
        quoter_address: Address = UNISWAP_V3_QUOTER,
    ):
        self._provider = provider
        self._router_address = Web3.to_checksum_address(router_address)
        self._quoter_address = Web3.to_checksum_address(quoter_address)

        self._router = provider.w3.eth.contract(
            address=self._router_address,
            abi=UNISWAP_V3_ROUTER_ABI,
        )
        self._quoter = provider.w3.eth.contract(
            address=self._quoter_address,
            abi=UNISWAP_V3_QUOTER_ABI,
        )

        logger.debug("uniswap_v3.initialized")

    def get_quote(
        self,
        token_in: Address,
        token_out: Address,
        amount_in: int,
        fee: int = FEE_MEDIUM,
    ) -> SwapQuote:
        """Get a swap quote from Uniswap V3.

        Args:
            token_in: Input token address.
            token_out: Output token address.
            amount_in: Input amount (raw).
            fee: Pool fee tier (100, 500, 3000, or 10000).

        Returns:
            SwapQuote with expected output.
        """
        token_in_cs = Web3.to_checksum_address(token_in)
        token_out_cs = Web3.to_checksum_address(token_out)

        params = (
            token_in_cs,
            token_out_cs,
            amount_in,
            fee,
            0,  # sqrtPriceLimitX96 (0 = no limit)
        )

        try:
            result = self._quoter.functions.quoteExactInputSingle(
                params
            ).call()
            amount_out = result[0]
            gas_estimate = result[3] if len(result) > 3 else 200_000
        except Exception as e:
            raise DeFiError(f"Uniswap V3 quote failed: {e}")

        quote = SwapQuote(
            protocol=SwapProtocol.UNISWAP_V3,
            token_in=token_in_cs,
            token_out=token_out_cs,
            amount_in=amount_in,
            amount_out=amount_out,
            price_impact=0.0,
            gas_estimate=gas_estimate,
            route=[token_in_cs, token_out_cs],
        )

        logger.info(
            "uniswap_v3.quote",
            amount_in=amount_in,
            amount_out=amount_out,
            fee=fee,
        )

        return quote

    def build_swap_exact_input_tx(
        self,
        token_in: Address,
        token_out: Address,
        amount_in: int,
        recipient: Address,
        fee: int = FEE_MEDIUM,
        amount_out_min: int = 0,
    ) -> dict[str, Any]:
        """Build an exact input single swap transaction.

        Args:
            token_in: Input token address.
            token_out: Output token address.
            amount_in: Exact input amount (raw).
            recipient: Address to receive output.
            fee: Pool fee tier.
            amount_out_min: Minimum output (slippage protection).

        Returns:
            Unsigned transaction dictionary.
        """
        params = (
            Web3.to_checksum_address(token_in),
            Web3.to_checksum_address(token_out),
            fee,
            Web3.to_checksum_address(recipient),
            amount_in,
            amount_out_min,
            0,  # sqrtPriceLimitX96
        )

        tx = self._router.functions.exactInputSingle(params).build_transaction(
            {"gas": 300_000}
        )

        logger.info(
            "uniswap_v3.swap_tx_built",
            amount_in=amount_in,
            min_out=amount_out_min,
            fee=fee,
        )

        return tx

    def find_best_fee(
        self,
        token_in: Address,
        token_out: Address,
        amount_in: int,
    ) -> tuple[int, int]:
        """Find the best fee tier for a swap.

        Queries all fee tiers and returns the one with the best output.

        Args:
            token_in: Input token address.
            token_out: Output token address.
            amount_in: Input amount (raw).

        Returns:
            Tuple of (best_fee, best_amount_out).
        """
        best_fee = FEE_MEDIUM
        best_out = 0

        for fee in [FEE_LOWEST, FEE_LOW, FEE_MEDIUM, FEE_HIGH]:
            try:
                quote = self.get_quote(token_in, token_out, amount_in, fee)
                if quote.amount_out > best_out:
                    best_out = quote.amount_out
                    best_fee = fee
            except DeFiError:
                continue

        logger.info(
            "uniswap_v3.best_fee",
            fee=best_fee,
            amount_out=best_out,
        )

        return best_fee, best_out

    def __repr__(self) -> str:
        return f"UniswapV3Router({self._router_address})"

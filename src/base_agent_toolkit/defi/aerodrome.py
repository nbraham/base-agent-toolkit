"""Aerodrome DEX integration for Base.

Aerodrome is the primary DEX on Base, using the ve(3,3) model.
It serves as Base's liquidity backbone with over $160M in revenue.
"""

from __future__ import annotations

import time
from typing import Any

from web3 import Web3

from ..constants import AERODROME_FACTORY, AERODROME_ROUTER, WETH_ADDRESS
from ..exceptions import DeFiError, SlippageExceededError
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, Wei
from .abi import AERODROME_ROUTER_ABI
from .swap import SwapProtocol, SwapQuote, calculate_min_amount_out

logger = get_logger(__name__)


class AerodromeRouter:
    """Interface to Aerodrome DEX router on Base.

    Provides swap functionality through Aerodrome's liquidity pools.

    Args:
        provider: BaseProvider instance.
        router_address: Override router address.
    """

    def __init__(
        self,
        provider: BaseProvider,
        router_address: Address = AERODROME_ROUTER,
    ):
        self._provider = provider
        self._address = Web3.to_checksum_address(router_address)
        self._contract = provider.w3.eth.contract(
            address=self._address,
            abi=AERODROME_ROUTER_ABI,
        )
        logger.debug("aerodrome.initialized", router=self._address)

    def get_quote(
        self,
        token_in: Address,
        token_out: Address,
        amount_in: int,
        stable: bool = False,
    ) -> SwapQuote:
        """Get a swap quote from Aerodrome.

        Args:
            token_in: Input token address.
            token_out: Output token address.
            amount_in: Input amount (raw).
            stable: Use stable pool (for stablecoins) or volatile pool.

        Returns:
            SwapQuote with expected output.
        """
        token_in_cs = Web3.to_checksum_address(token_in)
        token_out_cs = Web3.to_checksum_address(token_out)

        routes = [(
            token_in_cs,
            token_out_cs,
            stable,
            Web3.to_checksum_address(AERODROME_FACTORY),
        )]

        try:
            amounts = self._contract.functions.getAmountsOut(
                amount_in, routes
            ).call()
            amount_out = amounts[-1]
        except Exception as e:
            raise DeFiError(f"Aerodrome quote failed: {e}")

        # Calculate price impact (simplified)
        price_impact = 0.0  # Would need pool reserves for accurate calculation

        quote = SwapQuote(
            protocol=SwapProtocol.AERODROME,
            token_in=token_in_cs,
            token_out=token_out_cs,
            amount_in=amount_in,
            amount_out=amount_out,
            price_impact=price_impact,
            gas_estimate=250_000,
            route=[token_in_cs, token_out_cs],
        )

        logger.info(
            "aerodrome.quote",
            token_in=token_in_cs[:10],
            token_out=token_out_cs[:10],
            amount_in=amount_in,
            amount_out=amount_out,
        )

        return quote

    def build_swap_tx(
        self,
        token_in: Address,
        token_out: Address,
        amount_in: int,
        recipient: Address,
        slippage_percent: float = 0.5,
        stable: bool = False,
        deadline_seconds: int = 300,
    ) -> dict[str, Any]:
        """Build a swap transaction on Aerodrome.

        Args:
            token_in: Input token address.
            token_out: Output token address.
            amount_in: Input amount (raw).
            recipient: Address to receive output tokens.
            slippage_percent: Maximum slippage.
            stable: Use stable pool.
            deadline_seconds: Transaction deadline in seconds from now.

        Returns:
            Unsigned transaction dictionary.
        """
        # Get quote first
        quote = self.get_quote(token_in, token_out, amount_in, stable)

        # Apply slippage
        min_amount_out = calculate_min_amount_out(
            quote.amount_out, slippage_percent
        )

        deadline = int(time.time()) + deadline_seconds

        routes = [(
            Web3.to_checksum_address(token_in),
            Web3.to_checksum_address(token_out),
            stable,
            Web3.to_checksum_address(AERODROME_FACTORY),
        )]

        tx = self._contract.functions.swapExactTokensForTokens(
            amount_in,
            min_amount_out,
            routes,
            Web3.to_checksum_address(recipient),
            deadline,
        ).build_transaction({"gas": 300_000})

        logger.info(
            "aerodrome.swap_tx_built",
            amount_in=amount_in,
            min_out=min_amount_out,
            slippage=f"{slippage_percent}%",
        )

        return tx

    def __repr__(self) -> str:
        return f"AerodromeRouter({self._address})"

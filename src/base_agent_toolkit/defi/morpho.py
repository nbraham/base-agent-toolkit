"""Morpho Blue lending protocol integration for Base."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web3 import Web3

from ..constants import MORPHO_BLUE
from ..exceptions import DeFiError
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, TokenAmount
from .abi import MORPHO_BLUE_ABI

logger = get_logger(__name__)


@dataclass
class MorphoMarket:
    """Represents a Morpho Blue lending market."""

    loan_token: Address
    collateral_token: Address
    oracle: Address
    irm: Address  # Interest Rate Model
    lltv: int  # Liquidation LTV (in 1e18)

    @property
    def params_tuple(self) -> tuple:
        """Market params as a tuple for contract calls."""
        return (
            Web3.to_checksum_address(self.loan_token),
            Web3.to_checksum_address(self.collateral_token),
            Web3.to_checksum_address(self.oracle),
            Web3.to_checksum_address(self.irm),
            self.lltv,
        )


@dataclass
class MorphoPosition:
    """User's position in a Morpho market."""

    supply_shares: int
    borrow_shares: int
    collateral: int

    @property
    def is_supplier(self) -> bool:
        return self.supply_shares > 0

    @property
    def is_borrower(self) -> bool:
        return self.borrow_shares > 0

    @property
    def has_collateral(self) -> bool:
        return self.collateral > 0


class MorphoClient:
    """Interface to Morpho Blue lending protocol on Base.

    Morpho Blue is a minimal, efficient lending protocol that
    enables permissionless market creation.

    Args:
        provider: BaseProvider instance.
        morpho_address: Override Morpho Blue contract address.
    """

    def __init__(
        self,
        provider: BaseProvider,
        morpho_address: Address = MORPHO_BLUE,
    ):
        self._provider = provider
        self._address = Web3.to_checksum_address(morpho_address)
        self._contract = provider.w3.eth.contract(
            address=self._address,
            abi=MORPHO_BLUE_ABI,
        )
        logger.debug("morpho.initialized", address=self._address)

    def get_position(
        self,
        market: MorphoMarket,
        user: Address,
    ) -> MorphoPosition:
        """Get a user's position in a Morpho market.

        Args:
            market: MorphoMarket instance.
            user: User address.

        Returns:
            MorphoPosition with supply, borrow, and collateral info.
        """
        # Market ID is keccak256 of the market params
        market_id = Web3.keccak(
            Web3.codec.encode(
                ["address", "address", "address", "address", "uint256"],
                list(market.params_tuple),
            )
        )

        try:
            result = self._contract.functions.position(
                market_id,
                Web3.to_checksum_address(user),
            ).call()

            return MorphoPosition(
                supply_shares=result[0],
                borrow_shares=result[1],
                collateral=result[2],
            )
        except Exception as e:
            raise DeFiError(f"Failed to get Morpho position: {e}")

    def build_supply_tx(
        self,
        market: MorphoMarket,
        assets: int,
        on_behalf_of: Address,
    ) -> dict[str, Any]:
        """Build a supply (lend) transaction.

        Args:
            market: MorphoMarket to supply to.
            assets: Amount of loan token to supply (raw).
            on_behalf_of: Address to credit the supply to.

        Returns:
            Unsigned transaction dictionary.
        """
        tx = self._contract.functions.supply(
            market.params_tuple,
            assets,
            0,  # shares (0 = specify by assets)
            Web3.to_checksum_address(on_behalf_of),
            b"",  # callback data
        ).build_transaction({"gas": 300_000})

        logger.info(
            "morpho.supply_tx_built",
            market_loan=market.loan_token[:10],
            assets=assets,
        )

        return tx

    def build_withdraw_tx(
        self,
        market: MorphoMarket,
        assets: int,
        on_behalf_of: Address,
        receiver: Address,
    ) -> dict[str, Any]:
        """Build a withdraw transaction.

        Args:
            market: MorphoMarket to withdraw from.
            assets: Amount to withdraw (raw).
            on_behalf_of: Address that supplied.
            receiver: Address to receive withdrawn tokens.

        Returns:
            Unsigned transaction dictionary.
        """
        tx = self._contract.functions.withdraw(
            market.params_tuple,
            assets,
            0,  # shares
            Web3.to_checksum_address(on_behalf_of),
            Web3.to_checksum_address(receiver),
        ).build_transaction({"gas": 300_000})

        logger.info(
            "morpho.withdraw_tx_built",
            assets=assets,
        )

        return tx

    def __repr__(self) -> str:
        return f"MorphoClient({self._address})"

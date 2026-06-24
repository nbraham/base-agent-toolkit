"""Token approval management for DeFi protocols."""

from __future__ import annotations

from typing import Any

from web3 import Web3

from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address
from ..wallet.erc20 import ERC20Token

logger = get_logger(__name__)

MAX_UINT256 = 2**256 - 1


class ApprovalManager:
    """Manage token approvals for DeFi protocol interactions.

    Handles checking, granting, and revoking token approvals
    with safety features.

    Args:
        provider: BaseProvider instance.
    """

    def __init__(self, provider: BaseProvider):
        self._provider = provider

    def check_allowance(
        self,
        token_address: Address,
        owner: Address,
        spender: Address,
    ) -> int:
        """Check current token allowance.

        Args:
            token_address: Token contract address.
            owner: Token owner.
            spender: Approved spender.

        Returns:
            Current allowance (raw amount).
        """
        token = ERC20Token(token_address, self._provider)
        allowance = token.allowance(owner, spender)
        return allowance.raw

    def needs_approval(
        self,
        token_address: Address,
        owner: Address,
        spender: Address,
        amount: int,
    ) -> bool:
        """Check if an approval is needed.

        Args:
            token_address: Token contract address.
            owner: Token owner.
            spender: Spender address.
            amount: Required amount.

        Returns:
            True if current allowance is less than amount.
        """
        current = self.check_allowance(token_address, owner, spender)
        return current < amount

    def build_approve_tx(
        self,
        token_address: Address,
        spender: Address,
        amount: int | None = None,
        unlimited: bool = False,
    ) -> dict[str, Any]:
        """Build an approval transaction.

        Args:
            token_address: Token contract address.
            spender: Address to approve.
            amount: Specific amount to approve.
            unlimited: If True, approve max uint256.

        Returns:
            Unsigned transaction dictionary.
        """
        if unlimited:
            amount = MAX_UINT256
        elif amount is None:
            raise ValueError("Must specify amount or unlimited=True")

        token = ERC20Token(token_address, self._provider)
        tx = token.build_approve_tx(spender, amount)

        logger.info(
            "approval.approve_tx_built",
            token=token_address[:10],
            spender=spender[:10],
            unlimited=unlimited,
        )

        return tx

    def build_revoke_tx(
        self,
        token_address: Address,
        spender: Address,
    ) -> dict[str, Any]:
        """Build a revoke (set to 0) transaction.

        Args:
            token_address: Token contract address.
            spender: Spender to revoke.

        Returns:
            Unsigned transaction dictionary.
        """
        token = ERC20Token(token_address, self._provider)
        tx = token.build_approve_tx(spender, 0)

        logger.info(
            "approval.revoke_tx_built",
            token=token_address[:10],
            spender=spender[:10],
        )

        return tx

    def ensure_approval(
        self,
        token_address: Address,
        owner: Address,
        spender: Address,
        amount: int,
    ) -> dict[str, Any] | None:
        """Build approval tx only if needed.

        Args:
            token_address: Token contract address.
            owner: Token owner.
            spender: Spender address.
            amount: Required amount.

        Returns:
            Unsigned transaction if approval needed, None otherwise.
        """
        if self.needs_approval(token_address, owner, spender, amount):
            return self.build_approve_tx(token_address, spender, amount=amount)
        return None

    def __repr__(self) -> str:
        return "ApprovalManager()"

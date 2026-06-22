"""Token operations for BaseWallet."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from web3 import Web3

from ..constants import USDC_ADDRESS, USDC_DECIMALS, WETH_ADDRESS
from ..exceptions import InsufficientFundsError, TransactionError
from ..logging import get_logger
from ..types import Address, TokenAmount, TransactionResult, Wei
from .erc20 import ERC20Token

if TYPE_CHECKING:
    from .wallet import BaseWallet

logger = get_logger(__name__)


class TokenOperationsMixin:
    """Mixin providing token operations for BaseWallet.

    Adds methods for ERC20 token transfers, approvals,
    and balance checking.
    """

    def get_token_balance(self: "BaseWallet", token_address: Address) -> TokenAmount:
        """Get balance of an ERC20 token.

        Args:
            token_address: Token contract address.

        Returns:
            TokenAmount with the balance.
        """
        token = ERC20Token(token_address, self._provider)
        return token.balance_of(self.address)

    def get_token_info(self: "BaseWallet", token_address: Address) -> dict:
        """Get token metadata.

        Args:
            token_address: Token contract address.

        Returns:
            Dictionary with name, symbol, decimals, totalSupply.
        """
        token = ERC20Token(token_address, self._provider)
        info = token.get_info()
        return {
            "address": info.address,
            "name": info.name,
            "symbol": info.symbol,
            "decimals": info.decimals,
            "total_supply": info.total_supply,
        }

    def send_token(
        self: "BaseWallet",
        token_address: Address,
        to: Address,
        amount: int | None = None,
        amount_human: float | Decimal | None = None,
    ) -> TransactionResult:
        """Send ERC20 tokens to an address.

        Args:
            token_address: Token contract address.
            to: Recipient address.
            amount: Raw token amount (mutually exclusive with amount_human).
            amount_human: Human-readable amount (e.g., 10.5 USDC).

        Returns:
            TransactionResult with transaction hash.
        """
        token = ERC20Token(token_address, self._provider)
        info = token.get_info()

        if amount is None and amount_human is None:
            raise TransactionError("Must specify either amount or amount_human")
        if amount is not None and amount_human is not None:
            raise TransactionError("Cannot specify both amount and amount_human")

        if amount_human is not None:
            amount = int(Decimal(str(amount_human)) * Decimal(10**info.decimals))

        # Check balance
        balance = token.balance_of(self.address)
        if balance.raw < amount:
            raise InsufficientFundsError(
                required=amount, available=balance.raw, token=info.symbol
            )

        # Build and sign transaction
        tx = token.build_transfer_tx(to, amount)
        tx["chainId"] = self._provider.chain_id
        tx["nonce"] = self._next_nonce()
        tx["from"] = self.address

        signed = self._account.sign_transaction(tx)
        tx_hash = self._provider.w3.eth.send_raw_transaction(signed.raw_transaction)

        logger.info(
            "wallet.send_token",
            token=info.symbol,
            to=to,
            amount=amount,
            tx_hash=tx_hash.hex(),
        )

        return TransactionResult(hash=tx_hash.hex())

    def approve_token(
        self: "BaseWallet",
        token_address: Address,
        spender: Address,
        amount: int | None = None,
        unlimited: bool = False,
    ) -> TransactionResult:
        """Approve a spender to use tokens.

        Args:
            token_address: Token contract address.
            spender: Address to approve.
            amount: Raw amount to approve.
            unlimited: If True, approve max uint256.

        Returns:
            TransactionResult with transaction hash.
        """
        if unlimited:
            amount = 2**256 - 1
        elif amount is None:
            raise TransactionError("Must specify amount or unlimited=True")

        token = ERC20Token(token_address, self._provider)
        tx = token.build_approve_tx(spender, amount)
        tx["chainId"] = self._provider.chain_id
        tx["nonce"] = self._next_nonce()
        tx["from"] = self.address

        signed = self._account.sign_transaction(tx)
        tx_hash = self._provider.w3.eth.send_raw_transaction(signed.raw_transaction)

        logger.info(
            "wallet.approve_token",
            token=token_address,
            spender=spender,
            amount=amount,
            tx_hash=tx_hash.hex(),
        )

        return TransactionResult(hash=tx_hash.hex())

    def get_token_allowance(
        self: "BaseWallet",
        token_address: Address,
        spender: Address,
    ) -> TokenAmount:
        """Check token allowance for a spender.

        Args:
            token_address: Token contract address.
            spender: Spender address to check.

        Returns:
            TokenAmount with the allowance.
        """
        token = ERC20Token(token_address, self._provider)
        return token.allowance(self.address, spender)

    def revoke_approval(
        self: "BaseWallet",
        token_address: Address,
        spender: Address,
    ) -> TransactionResult:
        """Revoke token approval for a spender (set to 0).

        Args:
            token_address: Token contract address.
            spender: Spender address to revoke.

        Returns:
            TransactionResult.
        """
        return self.approve_token(token_address, spender, amount=0)

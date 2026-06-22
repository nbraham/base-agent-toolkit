"""Core wallet implementation for Base chain."""

from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Any

from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3

from ..constants import DEFAULT_GAS_LIMIT, ETH_DECIMALS
from ..exceptions import (
    InsufficientFundsError,
    TransactionError,
    TransactionTimeoutError,
    WalletError,
)
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, GasEstimate, TokenAmount, TransactionResult, TxHash, Wei

logger = get_logger(__name__)


class BaseWallet:
    """Wallet for Base chain interactions.

    Supports creating wallets, loading from private keys or mnemonics,
    sending ETH, and signing transactions.

    Args:
        account: eth_account LocalAccount instance.
        provider: BaseProvider for chain interactions.
    """

    def __init__(self, account: LocalAccount, provider: BaseProvider):
        self._account = account
        self._provider = provider
        self._nonce: int | None = None

        logger.info(
            "wallet.initialized",
            address=self.address,
            chain_id=provider.chain_id,
        )

    @classmethod
    def create(cls, provider: BaseProvider) -> "BaseWallet":
        """Create a new random wallet.

        Args:
            provider: BaseProvider for chain interactions.

        Returns:
            New BaseWallet instance.
        """
        account = Account.create()
        logger.info("wallet.created", address=account.address)
        return cls(account=account, provider=provider)

    @classmethod
    def from_private_key(cls, private_key: str, provider: BaseProvider) -> "BaseWallet":
        """Load wallet from a private key.

        Args:
            private_key: Private key (with or without 0x prefix).
            provider: BaseProvider for chain interactions.

        Returns:
            BaseWallet instance.
        """
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"
        try:
            account = Account.from_key(private_key)
        except Exception as e:
            raise WalletError(f"Invalid private key: {e}")
        return cls(account=account, provider=provider)

    @classmethod
    def from_mnemonic(
        cls,
        mnemonic: str,
        provider: BaseProvider,
        account_index: int = 0,
    ) -> "BaseWallet":
        """Load wallet from a BIP39 mnemonic phrase.

        Args:
            mnemonic: BIP39 mnemonic phrase.
            provider: BaseProvider for chain interactions.
            account_index: HD derivation index (default: 0).

        Returns:
            BaseWallet instance.
        """
        Account.enable_unaudited_hdwallet_features()
        try:
            account = Account.from_mnemonic(
                mnemonic,
                account_path=f"m/44'/60'/0'/0/{account_index}",
            )
        except Exception as e:
            raise WalletError(f"Invalid mnemonic: {e}")
        return cls(account=account, provider=provider)

    @property
    def address(self) -> Address:
        """Wallet address (checksummed)."""
        return self._account.address

    @property
    def private_key(self) -> str:
        """Private key (hex string with 0x prefix)."""
        return self._account.key.hex()

    @property
    def provider(self) -> BaseProvider:
        """The connected provider."""
        return self._provider

    def get_balance(self) -> TokenAmount:
        """Get ETH balance of this wallet.

        Returns:
            TokenAmount representing the ETH balance.
        """
        balance_wei = self._provider.get_balance(self.address)
        return TokenAmount(raw=balance_wei, decimals=ETH_DECIMALS, symbol="ETH")

    def get_nonce(self) -> int:
        """Get the current nonce for this wallet."""
        return self._provider.get_nonce(self.address)

    def _next_nonce(self) -> int:
        """Get and increment the nonce, using cache when possible."""
        if self._nonce is None:
            self._nonce = self.get_nonce()
        nonce = self._nonce
        self._nonce += 1
        return nonce

    def reset_nonce(self) -> None:
        """Reset the cached nonce (fetch fresh from chain on next tx)."""
        self._nonce = None

    def estimate_gas(self, to: Address, value: Wei = 0, data: bytes = b"") -> GasEstimate:
        """Estimate gas for a transaction.

        Args:
            to: Destination address.
            value: ETH value in wei.
            data: Transaction data.

        Returns:
            GasEstimate with gas limit and fee information.
        """
        tx = {
            "from": self.address,
            "to": Web3.to_checksum_address(to),
            "value": value,
        }
        if data:
            tx["data"] = data

        gas_limit = self._provider.estimate_gas(tx)
        gas_price = self._provider.get_gas_price()

        # EIP-1559 fee estimation
        latest_block = self._provider.get_block("latest")
        base_fee = latest_block.get("baseFeePerGas", gas_price)
        max_priority_fee = max(gas_price - base_fee, 100_000_000)  # min 0.1 gwei
        max_fee = int(base_fee * 1.25) + max_priority_fee

        return GasEstimate(
            gas_limit=gas_limit,
            max_fee_per_gas=max_fee,
            max_priority_fee_per_gas=max_priority_fee,
            estimated_cost_wei=gas_limit * max_fee,
        )

    def send_eth(
        self,
        to: Address,
        amount_wei: Wei | None = None,
        amount_ether: float | Decimal | None = None,
        gas_limit: int | None = None,
    ) -> TransactionResult:
        """Send ETH to an address.

        Args:
            to: Recipient address.
            amount_wei: Amount in wei (mutually exclusive with amount_ether).
            amount_ether: Amount in ether (mutually exclusive with amount_wei).
            gas_limit: Optional gas limit override.

        Returns:
            TransactionResult with hash and status.

        Raises:
            InsufficientFundsError: If wallet doesn't have enough ETH.
            TransactionError: If transaction fails.
        """
        if amount_wei is None and amount_ether is None:
            raise WalletError("Must specify either amount_wei or amount_ether")
        if amount_wei is not None and amount_ether is not None:
            raise WalletError("Cannot specify both amount_wei and amount_ether")

        if amount_ether is not None:
            amount_wei = int(Decimal(str(amount_ether)) * Decimal(10**18))

        # Check balance
        balance = self._provider.get_balance(self.address)
        if balance < amount_wei:
            raise InsufficientFundsError(
                required=amount_wei, available=balance, token="ETH"
            )

        to_checksum = Web3.to_checksum_address(to)
        nonce = self._next_nonce()

        # Build EIP-1559 transaction
        gas_est = self.estimate_gas(to_checksum, amount_wei)
        tx = {
            "type": 2,
            "chainId": self._provider.chain_id,
            "nonce": nonce,
            "to": to_checksum,
            "value": amount_wei,
            "gas": gas_limit or gas_est.gas_limit,
            "maxFeePerGas": gas_est.max_fee_per_gas,
            "maxPriorityFeePerGas": gas_est.max_priority_fee_per_gas,
        }

        logger.info(
            "wallet.send_eth",
            to=to_checksum,
            amount_wei=amount_wei,
            nonce=nonce,
        )

        # Sign and send
        signed = self._account.sign_transaction(tx)
        tx_hash = self._provider.w3.eth.send_raw_transaction(signed.raw_transaction)
        tx_hash_hex = tx_hash.hex()

        logger.info("wallet.tx_sent", tx_hash=tx_hash_hex)

        return TransactionResult(hash=tx_hash_hex)

    def wait_for_transaction(
        self,
        tx_hash: TxHash,
        timeout: int = 120,
        poll_interval: float = 2.0,
    ) -> TransactionResult:
        """Wait for a transaction to be mined.

        Args:
            tx_hash: Transaction hash to wait for.
            timeout: Maximum wait time in seconds.
            poll_interval: Seconds between polling attempts.

        Returns:
            TransactionResult with receipt data.

        Raises:
            TransactionTimeoutError: If transaction isn't mined within timeout.
        """
        try:
            receipt = self._provider.w3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=timeout, poll_latency=poll_interval
            )
        except Exception as e:
            raise TransactionTimeoutError(
                f"Transaction {tx_hash} not mined within {timeout}s: {e}",
                tx_hash=tx_hash,
            )

        return TransactionResult(
            hash=tx_hash,
            block_number=receipt.get("blockNumber"),
            gas_used=receipt.get("gasUsed"),
            status=receipt.get("status") == 1,
            logs=[dict(log) for log in receipt.get("logs", [])],
        )

    def sign_message(self, message: str) -> str:
        """Sign a message with the wallet's private key.

        Args:
            message: Message to sign.

        Returns:
            Signature hex string.
        """
        from eth_account.messages import encode_defunct

        msg = encode_defunct(text=message)
        signed = self._account.sign_message(msg)
        return signed.signature.hex()

    def sign_typed_data(self, domain: dict, types: dict, value: dict) -> str:
        """Sign EIP-712 typed data.

        Args:
            domain: EIP-712 domain separator.
            types: Type definitions.
            value: Data to sign.

        Returns:
            Signature hex string.
        """
        from eth_account.messages import encode_typed_data

        signed = self._account.sign_message(
            encode_typed_data(
                domain_data=domain,
                message_types=types,
                message_data=value,
            )
        )
        return signed.signature.hex()

    def __repr__(self) -> str:
        return f"BaseWallet(address={self.address})"

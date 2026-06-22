"""Phase 2: Wallet & Core Chain Interaction - Commits 21-40"""
import subprocess, os

ROOT = "/work/projects/base-agent-toolkit"
os.chdir(ROOT)

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)

def commit(msg):
    subprocess.run(["git", "add", "-A"], check=True, cwd=ROOT)
    subprocess.run(["git", "commit", "-m", msg], check=True, cwd=ROOT)
    print(f"  ✓ {msg}")

# --- Commit 21: Provider base class ---
write("src/base_agent_toolkit/provider/__init__.py", '''"""RPC provider module for Base chain interactions."""

from .base import BaseProvider
from .manager import ProviderManager

__all__ = ["BaseProvider", "ProviderManager"]
''')

write("src/base_agent_toolkit/provider/base.py", '''"""Base RPC provider implementation."""

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
''')

commit("feat(provider): create BaseProvider with RPC interaction methods")

# --- Commit 22: Provider manager with failover ---
write("src/base_agent_toolkit/provider/manager.py", '''"""Provider manager with failover and rate limiting."""

from __future__ import annotations

import time
from threading import Lock
from typing import Any, Callable, TypeVar

from ..constants import DEFAULT_RPC_URLS, RPC_REQUEST_TIMEOUT_SECONDS
from ..exceptions import AllProvidersFailedError, ProviderError, RateLimitError
from ..logging import get_logger
from .base import BaseProvider

logger = get_logger(__name__)

T = TypeVar("T")


class ProviderManager:
    """Manages multiple RPC providers with automatic failover and rate limiting.

    If the primary provider fails, automatically switches to the next available
    fallback. Implements basic rate limiting to avoid hitting provider limits.

    Args:
        rpc_urls: List of RPC endpoint URLs (first is primary).
        chain_id: Chain ID for the network.
        max_retries: Maximum retries per request across all providers.
        requests_per_second: Rate limit for requests.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        rpc_urls: list[str] | None = None,
        chain_id: int = 8453,
        max_retries: int = 3,
        requests_per_second: float = 10.0,
        timeout: int = RPC_REQUEST_TIMEOUT_SECONDS,
    ):
        if rpc_urls is None:
            rpc_urls = DEFAULT_RPC_URLS.get(chain_id, [])

        if not rpc_urls:
            raise ProviderError(f"No RPC URLs provided for chain {chain_id}")

        self.chain_id = chain_id
        self.max_retries = max_retries
        self.min_interval = 1.0 / requests_per_second
        self._last_request_time = 0.0
        self._lock = Lock()
        self._current_index = 0

        self._providers = [
            BaseProvider(rpc_url=url, chain_id=chain_id, timeout=timeout)
            for url in rpc_urls
        ]

        logger.info(
            "provider_manager.initialized",
            provider_count=len(self._providers),
            chain_id=chain_id,
        )

    @property
    def current(self) -> BaseProvider:
        """Get the currently active provider."""
        return self._providers[self._current_index]

    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self._last_request_time = time.monotonic()

    def _rotate_provider(self) -> None:
        """Switch to the next available provider."""
        old_index = self._current_index
        self._current_index = (self._current_index + 1) % len(self._providers)
        logger.warning(
            "provider_manager.rotated",
            from_url=self._providers[old_index].rpc_url,
            to_url=self._providers[self._current_index].rpc_url,
        )

    def execute(self, method: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a provider method with failover and rate limiting.

        Args:
            method: Name of the BaseProvider method to call.
            *args: Positional arguments for the method.
            **kwargs: Keyword arguments for the method.

        Returns:
            Result from the provider method.

        Raises:
            AllProvidersFailedError: If all providers fail.
        """
        errors: list[str] = []

        for attempt in range(self.max_retries):
            self._rate_limit()
            provider = self.current

            try:
                fn = getattr(provider, method)
                result = fn(*args, **kwargs)
                return result
            except Exception as e:
                error_msg = f"{provider.rpc_url}: {e}"
                errors.append(error_msg)
                logger.warning(
                    "provider_manager.request_failed",
                    provider=provider.rpc_url,
                    method=method,
                    attempt=attempt + 1,
                    error=str(e),
                )
                self._rotate_provider()

        raise AllProvidersFailedError(
            f"All providers failed after {self.max_retries} attempts: "
            + "; ".join(errors)
        )

    def get_healthy_provider(self) -> BaseProvider | None:
        """Find the first connected provider.

        Returns:
            A connected BaseProvider, or None if all are down.
        """
        for provider in self._providers:
            if provider.is_connected():
                return provider
        return None

    @property
    def provider_count(self) -> int:
        """Number of configured providers."""
        return len(self._providers)

    def __repr__(self) -> str:
        return (
            f"ProviderManager(providers={self.provider_count}, "
            f"current={self.current.rpc_url!r})"
        )
''')

commit("feat(provider): add ProviderManager with failover and rate limiting")

# --- Commit 23: Wallet module ---
write("src/base_agent_toolkit/wallet/__init__.py", '''"""Wallet module for Base chain interactions."""

from .wallet import BaseWallet

__all__ = ["BaseWallet"]
''')

write("src/base_agent_toolkit/wallet/wallet.py", '''"""Core wallet implementation for Base chain."""

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
''')

commit("feat(wallet): implement BaseWallet with key management and ETH transfers")

# --- Commit 24: ERC20 token interactions ---
write("src/base_agent_toolkit/wallet/erc20.py", '''"""ERC20 token interaction helpers."""

from __future__ import annotations

from typing import Any

from web3 import Web3

from ..constants import ETH_DECIMALS
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, TokenAmount, TokenInfo, TransactionResult

logger = get_logger(__name__)

# Standard ERC20 ABI (minimal)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
        ],
        "name": "transferFrom",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
]


class ERC20Token:
    """Helper for interacting with ERC20 tokens on Base.

    Args:
        address: Token contract address.
        provider: BaseProvider instance.
        abi: Optional custom ABI (defaults to standard ERC20).
    """

    def __init__(
        self,
        address: Address,
        provider: BaseProvider,
        abi: list[dict] | None = None,
    ):
        self._address = Web3.to_checksum_address(address)
        self._provider = provider
        self._contract = provider.w3.eth.contract(
            address=self._address,
            abi=abi or ERC20_ABI,
        )
        self._info: TokenInfo | None = None

    @property
    def address(self) -> Address:
        """Token contract address."""
        return self._address

    @property
    def contract(self):
        """Web3 contract instance."""
        return self._contract

    def get_info(self) -> TokenInfo:
        """Get token metadata (name, symbol, decimals).

        Returns:
            TokenInfo with token details.
        """
        if self._info is None:
            name = self._contract.functions.name().call()
            symbol = self._contract.functions.symbol().call()
            decimals = self._contract.functions.decimals().call()
            total_supply = self._contract.functions.totalSupply().call()

            self._info = TokenInfo(
                address=self._address,
                name=name,
                symbol=symbol,
                decimals=decimals,
                total_supply=total_supply,
            )

        return self._info

    def balance_of(self, address: Address) -> TokenAmount:
        """Get token balance of an address.

        Args:
            address: Address to check.

        Returns:
            TokenAmount with the balance.
        """
        checksum = Web3.to_checksum_address(address)
        raw_balance = self._contract.functions.balanceOf(checksum).call()
        info = self.get_info()
        return TokenAmount(
            raw=raw_balance,
            decimals=info.decimals,
            symbol=info.symbol,
        )

    def allowance(self, owner: Address, spender: Address) -> TokenAmount:
        """Get the allowance granted by owner to spender.

        Args:
            owner: Token owner address.
            spender: Approved spender address.

        Returns:
            TokenAmount with the allowance.
        """
        owner_cs = Web3.to_checksum_address(owner)
        spender_cs = Web3.to_checksum_address(spender)
        raw = self._contract.functions.allowance(owner_cs, spender_cs).call()
        info = self.get_info()
        return TokenAmount(raw=raw, decimals=info.decimals, symbol=info.symbol)

    def build_transfer_tx(self, to: Address, amount: int) -> dict[str, Any]:
        """Build a transfer transaction (unsigned).

        Args:
            to: Recipient address.
            amount: Raw token amount.

        Returns:
            Transaction dictionary ready for signing.
        """
        to_cs = Web3.to_checksum_address(to)
        return self._contract.functions.transfer(to_cs, amount).build_transaction(
            {"gas": 100_000}
        )

    def build_approve_tx(self, spender: Address, amount: int) -> dict[str, Any]:
        """Build an approval transaction (unsigned).

        Args:
            spender: Address to approve.
            amount: Raw token amount to approve.

        Returns:
            Transaction dictionary ready for signing.
        """
        spender_cs = Web3.to_checksum_address(spender)
        return self._contract.functions.approve(spender_cs, amount).build_transaction(
            {"gas": 60_000}
        )

    def __repr__(self) -> str:
        info = self._info
        if info:
            return f"ERC20Token({info.symbol} @ {self._address})"
        return f"ERC20Token({self._address})"
''')

commit("feat(wallet): add ERC20 token interaction helper")

# --- Commit 25: Wallet token operations ---
write("src/base_agent_toolkit/wallet/tokens.py", '''"""Token operations for BaseWallet."""

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
''')

commit("feat(wallet): add ERC20 token transfer and approval operations")

# --- Commit 26: HD wallet multi-account ---
write("src/base_agent_toolkit/wallet/hd.py", '''"""HD wallet derivation for multi-account support."""

from __future__ import annotations

from eth_account import Account

from ..logging import get_logger
from ..provider.base import BaseProvider
from .wallet import BaseWallet

logger = get_logger(__name__)


def derive_wallets(
    mnemonic: str,
    provider: BaseProvider,
    count: int = 5,
    start_index: int = 0,
) -> list[BaseWallet]:
    """Derive multiple wallets from a BIP39 mnemonic.

    Uses the standard Ethereum derivation path: m/44'/60'/0'/0/{index}

    Args:
        mnemonic: BIP39 mnemonic phrase (12 or 24 words).
        provider: BaseProvider for chain interactions.
        count: Number of wallets to derive.
        start_index: Starting derivation index.

    Returns:
        List of BaseWallet instances.
    """
    Account.enable_unaudited_hdwallet_features()
    wallets = []

    for i in range(start_index, start_index + count):
        wallet = BaseWallet.from_mnemonic(mnemonic, provider, account_index=i)
        wallets.append(wallet)
        logger.debug(
            "hd.derived",
            index=i,
            address=wallet.address,
        )

    logger.info(
        "hd.derived_batch",
        count=len(wallets),
        start_index=start_index,
        addresses=[w.address for w in wallets],
    )

    return wallets


def generate_mnemonic(strength: int = 128) -> str:
    """Generate a new BIP39 mnemonic phrase.

    Args:
        strength: Entropy bits (128 = 12 words, 256 = 24 words).

    Returns:
        Mnemonic phrase string.
    """
    Account.enable_unaudited_hdwallet_features()
    _, mnemonic = Account.create_with_mnemonic(num_words=strength // 32 * 3)
    return mnemonic
''')

commit("feat(wallet): implement HD wallet multi-account derivation")

# --- Commit 27: Contract interaction wrapper ---
write("src/base_agent_toolkit/wallet/contract.py", '''"""Generic smart contract interaction wrapper."""

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
''')

commit("feat(wallet): add generic smart contract interaction wrapper")

# --- Commit 28: Transaction builder ---
write("src/base_agent_toolkit/wallet/tx_builder.py", '''"""Transaction builder for constructing complex transactions."""

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
''')

commit("feat(wallet): implement batch transaction builder")

# --- Commit 29: Transaction simulation ---
write("src/base_agent_toolkit/wallet/simulator.py", '''"""Transaction simulation (dry-run) support."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web3 import Web3

from ..exceptions import TransactionError
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, GasEstimate, Wei

logger = get_logger(__name__)


@dataclass
class SimulationResult:
    """Result of a transaction simulation."""

    success: bool
    gas_used: int
    return_data: bytes | None = None
    error_message: str | None = None
    gas_estimate: GasEstimate | None = None

    @property
    def would_revert(self) -> bool:
        """Whether the transaction would revert on-chain."""
        return not self.success


def simulate_transaction(
    provider: BaseProvider,
    from_address: Address,
    to: Address,
    value: Wei = 0,
    data: bytes = b"",
) -> SimulationResult:
    """Simulate a transaction using eth_call without sending it.

    This is useful for:
    - Checking if a transaction would succeed before sending
    - Getting the return value of a write function
    - Estimating gas accurately

    Args:
        provider: BaseProvider instance.
        from_address: Sender address.
        to: Destination address.
        value: ETH value in wei.
        data: Transaction data.

    Returns:
        SimulationResult with success status and gas info.
    """
    tx: dict[str, Any] = {
        "from": Web3.to_checksum_address(from_address),
        "to": Web3.to_checksum_address(to),
        "value": value,
    }
    if data:
        tx["data"] = data

    try:
        # eth_call simulates without state change
        return_data = provider.call(tx)

        # Also estimate gas
        gas_used = provider.estimate_gas(tx)

        logger.info(
            "simulator.success",
            to=to,
            gas_used=gas_used,
        )

        return SimulationResult(
            success=True,
            gas_used=gas_used,
            return_data=return_data,
        )

    except Exception as e:
        error_msg = str(e)
        logger.warning(
            "simulator.would_revert",
            to=to,
            error=error_msg,
        )

        return SimulationResult(
            success=False,
            gas_used=0,
            error_message=error_msg,
        )


def simulate_contract_call(
    provider: BaseProvider,
    from_address: Address,
    contract_address: Address,
    function_abi: dict[str, Any],
    *args: Any,
    value: Wei = 0,
) -> SimulationResult:
    """Simulate a contract function call.

    Args:
        provider: BaseProvider instance.
        from_address: Sender address.
        contract_address: Contract address.
        function_abi: ABI of the function to call.
        *args: Function arguments.
        value: ETH value in wei.

    Returns:
        SimulationResult.
    """
    contract = provider.w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=[function_abi],
    )

    fn_name = function_abi["name"]
    fn = contract.functions[fn_name]
    data = fn(*args)._encode_transaction_data()

    return simulate_transaction(
        provider=provider,
        from_address=from_address,
        to=contract_address,
        value=value,
        data=bytes.fromhex(data[2:]) if isinstance(data, str) else data,
    )
''')

commit("feat(wallet): add transaction simulation (dry-run) support")

# --- Commit 30: Gas oracle ---
write("src/base_agent_toolkit/wallet/gas.py", '''"""Gas price oracle and estimation for Base chain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..constants import (
    DEFAULT_MAX_GAS_PRICE_GWEI,
    DEFAULT_PRIORITY_FEE_GWEI,
    EIP1559_BASE_FEE_MULTIPLIER,
)
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import GasEstimate

logger = get_logger(__name__)


@dataclass
class GasPriceInfo:
    """Current gas price information."""

    base_fee_gwei: float
    priority_fee_gwei: float
    gas_price_gwei: float
    block_number: int

    @property
    def max_fee_gwei(self) -> float:
        """Recommended max fee per gas (base * 1.25 + priority)."""
        return self.base_fee_gwei * EIP1559_BASE_FEE_MULTIPLIER + self.priority_fee_gwei

    @property
    def max_fee_wei(self) -> int:
        return int(self.max_fee_gwei * 1e9)

    @property
    def priority_fee_wei(self) -> int:
        return int(self.priority_fee_gwei * 1e9)


class GasOracle:
    """Gas price oracle for Base chain.

    Provides current gas price information and EIP-1559
    fee recommendations.

    Args:
        provider: BaseProvider instance.
        max_gas_price_gwei: Maximum acceptable gas price.
    """

    def __init__(
        self,
        provider: BaseProvider,
        max_gas_price_gwei: float = DEFAULT_MAX_GAS_PRICE_GWEI,
    ):
        self._provider = provider
        self.max_gas_price_gwei = max_gas_price_gwei

    def get_gas_price(self) -> GasPriceInfo:
        """Get current gas price information.

        Returns:
            GasPriceInfo with base fee and priority fee.
        """
        latest = self._provider.get_block("latest")
        base_fee_wei = latest.get("baseFeePerGas", 0)
        gas_price_wei = self._provider.get_gas_price()
        block_number = latest.get("number", 0)

        base_fee_gwei = base_fee_wei / 1e9
        gas_price_gwei = gas_price_wei / 1e9
        priority_fee_gwei = max(
            gas_price_gwei - base_fee_gwei,
            DEFAULT_PRIORITY_FEE_GWEI,
        )

        info = GasPriceInfo(
            base_fee_gwei=base_fee_gwei,
            priority_fee_gwei=priority_fee_gwei,
            gas_price_gwei=gas_price_gwei,
            block_number=block_number,
        )

        logger.debug(
            "gas_oracle.price",
            base_fee=f"{base_fee_gwei:.4f} gwei",
            priority_fee=f"{priority_fee_gwei:.4f} gwei",
            max_fee=f"{info.max_fee_gwei:.4f} gwei",
        )

        return info

    def estimate_transaction_cost(
        self,
        gas_units: int,
        gas_price_info: GasPriceInfo | None = None,
    ) -> GasEstimate:
        """Estimate the cost of a transaction in ETH.

        Args:
            gas_units: Gas units required.
            gas_price_info: Optional pre-fetched gas price info.

        Returns:
            GasEstimate with cost breakdown.
        """
        if gas_price_info is None:
            gas_price_info = self.get_gas_price()

        max_fee_wei = gas_price_info.max_fee_wei
        priority_fee_wei = gas_price_info.priority_fee_wei
        estimated_cost = gas_units * max_fee_wei

        return GasEstimate(
            gas_limit=gas_units,
            max_fee_per_gas=max_fee_wei,
            max_priority_fee_per_gas=priority_fee_wei,
            estimated_cost_wei=estimated_cost,
        )

    def is_gas_acceptable(self, gas_price_info: GasPriceInfo | None = None) -> bool:
        """Check if current gas price is below the maximum threshold.

        Args:
            gas_price_info: Optional pre-fetched gas price info.

        Returns:
            True if gas price is acceptable.
        """
        if gas_price_info is None:
            gas_price_info = self.get_gas_price()
        return gas_price_info.gas_price_gwei <= self.max_gas_price_gwei

    def wait_for_low_gas(
        self,
        target_gwei: float | None = None,
        timeout_seconds: int = 300,
        poll_interval: float = 5.0,
    ) -> GasPriceInfo:
        """Wait until gas price drops below a target.

        Args:
            target_gwei: Target gas price in gwei.
            timeout_seconds: Maximum wait time.
            poll_interval: Seconds between checks.

        Returns:
            GasPriceInfo when target is reached.

        Raises:
            TimeoutError: If gas price doesn't drop within timeout.
        """
        import time

        target = target_gwei or self.max_gas_price_gwei
        start = time.monotonic()

        while True:
            info = self.get_gas_price()
            if info.gas_price_gwei <= target:
                return info

            elapsed = time.monotonic() - start
            if elapsed >= timeout_seconds:
                raise TimeoutError(
                    f"Gas price ({info.gas_price_gwei:.2f} gwei) didn't drop "
                    f"below {target:.2f} gwei within {timeout_seconds}s"
                )

            logger.debug(
                "gas_oracle.waiting",
                current=f"{info.gas_price_gwei:.2f} gwei",
                target=f"{target:.2f} gwei",
            )
            time.sleep(poll_interval)
''')

commit("feat(wallet): implement gas price oracle with EIP-1559 support")

# --- Commit 31: Update wallet __init__ with all exports ---
write("src/base_agent_toolkit/wallet/__init__.py", '''"""Wallet module for Base chain interactions."""

from .contract import ContractWrapper
from .erc20 import ERC20Token
from .gas import GasOracle, GasPriceInfo
from .hd import derive_wallets, generate_mnemonic
from .simulator import SimulationResult, simulate_transaction
from .tokens import TokenOperationsMixin
from .tx_builder import TransactionBuilder
from .wallet import BaseWallet

__all__ = [
    "BaseWallet",
    "ContractWrapper",
    "ERC20Token",
    "GasOracle",
    "GasPriceInfo",
    "SimulationResult",
    "TokenOperationsMixin",
    "TransactionBuilder",
    "derive_wallets",
    "generate_mnemonic",
    "simulate_transaction",
]
''')

commit("refactor(wallet): consolidate wallet module exports")

# --- Commit 32: Wallet tests ---
write("tests/test_wallet.py", '''"""Tests for wallet module."""

from unittest.mock import MagicMock, patch

import pytest

from base_agent_toolkit.wallet.wallet import BaseWallet
from base_agent_toolkit.wallet.erc20 import ERC20Token, ERC20_ABI
from base_agent_toolkit.wallet.gas import GasOracle, GasPriceInfo
from base_agent_toolkit.wallet.hd import generate_mnemonic
from base_agent_toolkit.wallet.tx_builder import TransactionBuilder
from base_agent_toolkit.exceptions import WalletError


class TestBaseWallet:
    """Tests for BaseWallet class."""

    def test_create_new_wallet(self):
        """Test creating a new random wallet."""
        provider = MagicMock()
        provider.chain_id = 8453
        wallet = BaseWallet.create(provider)
        assert wallet.address.startswith("0x")
        assert len(wallet.address) == 42

    def test_from_private_key(self):
        """Test loading wallet from private key."""
        provider = MagicMock()
        provider.chain_id = 8453
        pk = "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        wallet = BaseWallet.from_private_key(pk, provider)
        assert wallet.address == "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

    def test_from_private_key_with_prefix(self):
        """Test loading wallet with 0x prefix."""
        provider = MagicMock()
        provider.chain_id = 8453
        pk = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        wallet = BaseWallet.from_private_key(pk, provider)
        assert wallet.address.startswith("0x")

    def test_invalid_private_key(self):
        """Test that invalid private key raises error."""
        provider = MagicMock()
        provider.chain_id = 8453
        with pytest.raises(WalletError, match="Invalid private key"):
            BaseWallet.from_private_key("invalid", provider)

    def test_wallet_repr(self):
        """Test wallet string representation."""
        provider = MagicMock()
        provider.chain_id = 8453
        wallet = BaseWallet.create(provider)
        assert "BaseWallet" in repr(wallet)
        assert wallet.address in repr(wallet)

    def test_nonce_reset(self):
        """Test nonce cache reset."""
        provider = MagicMock()
        provider.chain_id = 8453
        wallet = BaseWallet.create(provider)
        wallet._nonce = 5
        wallet.reset_nonce()
        assert wallet._nonce is None


class TestGasPriceInfo:
    """Tests for GasPriceInfo."""

    def test_max_fee_calculation(self):
        info = GasPriceInfo(
            base_fee_gwei=1.0,
            priority_fee_gwei=0.1,
            gas_price_gwei=1.1,
            block_number=1000,
        )
        # max_fee = 1.0 * 1.25 + 0.1 = 1.35
        assert abs(info.max_fee_gwei - 1.35) < 0.01

    def test_wei_conversion(self):
        info = GasPriceInfo(
            base_fee_gwei=1.0,
            priority_fee_gwei=0.1,
            gas_price_gwei=1.1,
            block_number=1000,
        )
        assert info.priority_fee_wei == 100_000_000  # 0.1 gwei


class TestTransactionBuilder:
    """Tests for TransactionBuilder."""

    def test_add_eth_transfer(self):
        wallet = MagicMock()
        builder = TransactionBuilder(wallet)
        builder.add_eth_transfer("0x1234", amount_wei=1000)
        assert builder.count == 1

    def test_clear(self):
        wallet = MagicMock()
        builder = TransactionBuilder(wallet)
        builder.add_eth_transfer("0x1234", amount_wei=1000)
        builder.clear()
        assert builder.count == 0

    def test_preview(self):
        wallet = MagicMock()
        builder = TransactionBuilder(wallet)
        builder.add_eth_transfer("0x1234", amount_wei=1000, description="Test")
        preview = builder.preview()
        assert len(preview) == 1
        assert preview[0]["description"] == "Test"

    def test_chaining(self):
        wallet = MagicMock()
        builder = TransactionBuilder(wallet)
        result = (
            builder
            .add_eth_transfer("0x1234", amount_wei=1000)
            .add_eth_transfer("0x5678", amount_wei=2000)
        )
        assert result is builder
        assert builder.count == 2


class TestMnemonic:
    """Tests for mnemonic generation."""

    def test_generate_12_words(self):
        mnemonic = generate_mnemonic(128)
        words = mnemonic.split()
        assert len(words) == 12

    def test_generate_24_words(self):
        mnemonic = generate_mnemonic(256)
        words = mnemonic.split()
        assert len(words) == 24
''')

commit("test(wallet): add unit tests for wallet, gas oracle, and transaction builder")

# --- Commit 33: Provider tests ---
write("tests/test_provider.py", '''"""Tests for provider module."""

from unittest.mock import MagicMock, patch

import pytest

from base_agent_toolkit.provider.base import BaseProvider
from base_agent_toolkit.provider.manager import ProviderManager
from base_agent_toolkit.exceptions import AllProvidersFailedError, ProviderError


class TestBaseProvider:
    """Tests for BaseProvider."""

    def test_default_rpc_url(self):
        """Test provider uses default URL when none provided."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                provider = BaseProvider(chain_id=8453)
                assert "base.org" in provider.rpc_url

    def test_custom_rpc_url(self):
        """Test provider uses custom URL."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                provider = BaseProvider(rpc_url="https://custom.rpc.com")
                assert provider.rpc_url == "https://custom.rpc.com"

    def test_invalid_chain_id(self):
        """Test provider raises for unknown chain ID."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                with pytest.raises(ProviderError):
                    BaseProvider(chain_id=99999)

    def test_repr(self):
        """Test provider repr."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                provider = BaseProvider(rpc_url="https://test.com", chain_id=8453)
                assert "test.com" in repr(provider)


class TestProviderManager:
    """Tests for ProviderManager."""

    def test_init_with_urls(self):
        """Test manager init with multiple URLs."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                manager = ProviderManager(
                    rpc_urls=["https://a.com", "https://b.com"],
                    chain_id=8453,
                )
                assert manager.provider_count == 2

    def test_no_urls_raises(self):
        """Test manager raises when no URLs available."""
        with pytest.raises(ProviderError):
            ProviderManager(rpc_urls=[], chain_id=99999)

    def test_current_provider(self):
        """Test getting current provider."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                manager = ProviderManager(
                    rpc_urls=["https://a.com"],
                    chain_id=8453,
                )
                assert isinstance(manager.current, BaseProvider)

    def test_repr(self):
        """Test manager repr."""
        with patch("base_agent_toolkit.provider.base.Web3"):
            with patch("base_agent_toolkit.provider.base.AsyncWeb3"):
                manager = ProviderManager(
                    rpc_urls=["https://a.com"],
                    chain_id=8453,
                )
                assert "ProviderManager" in repr(manager)
''')

commit("test(provider): add tests for BaseProvider and ProviderManager")

# --- Commit 34: Update main package exports ---
write("src/base_agent_toolkit/__init__.py", '''"""Base Agent Toolkit - Python SDK for building AI agents on Base L2.

A comprehensive toolkit for:
- Wallet management with HD derivation
- B20 native token standard (Beryl upgrade)
- DeFi protocol integrations (Aerodrome, Morpho, Uniswap)
- x402 HTTP payment protocol
- AI agent framework with strategies
- CLI interface
"""

__version__ = "0.1.0"

from .config import Settings, load_settings
from .constants import (
    BASE_MAINNET_CHAIN_ID,
    BASE_SEPOLIA_CHAIN_ID,
    B20_FACTORY,
)
from .exceptions import (
    BaseAgentError,
    ContractError,
    InsufficientFundsError,
    ProviderError,
    TransactionError,
    WalletError,
)
from .logging import get_logger, setup_logging
from .provider import BaseProvider, ProviderManager
from .types import (
    Address,
    GasEstimate,
    Network,
    TokenAmount,
    TokenInfo,
    TransactionResult,
    TxHash,
    WalletBalance,
    Wei,
)
from .wallet import BaseWallet, ERC20Token, GasOracle, ContractWrapper

__all__ = [
    # Version
    "__version__",
    # Config
    "Settings",
    "load_settings",
    # Constants
    "BASE_MAINNET_CHAIN_ID",
    "BASE_SEPOLIA_CHAIN_ID",
    "B20_FACTORY",
    # Exceptions
    "BaseAgentError",
    "ContractError",
    "InsufficientFundsError",
    "ProviderError",
    "TransactionError",
    "WalletError",
    # Logging
    "get_logger",
    "setup_logging",
    # Provider
    "BaseProvider",
    "ProviderManager",
    # Types
    "Address",
    "GasEstimate",
    "Network",
    "TokenAmount",
    "TokenInfo",
    "TransactionResult",
    "TxHash",
    "WalletBalance",
    "Wei",
    # Wallet
    "BaseWallet",
    "ERC20Token",
    "GasOracle",
    "ContractWrapper",
]
''')

commit("refactor: update package exports with wallet and provider modules")

print("\\n=== Phase 2 complete! ===")
result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True, cwd=ROOT)
lines = result.stdout.strip().splitlines()
print(f"Total commits: {len(lines)}")

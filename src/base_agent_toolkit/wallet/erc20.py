"""ERC20 token interaction helpers."""

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

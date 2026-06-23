"""B20 Token interaction class."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from web3 import Web3

from ..exceptions import B20Error, B20PermissionError
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, TokenAmount
from .abi import B20_TOKEN_ABI
from .types import B20Role, B20TokenInfo, B20TokenType

logger = get_logger(__name__)


class B20Token:
    """Interface for interacting with a deployed B20 token.

    B20 tokens are ERC-20 compatible with additional features:
    - Transfer with memo
    - Role-based access control (admin, minter, burner, freezer, pauser)
    - Mint and burn operations
    - Freeze/unfreeze addresses
    - Granular pause
    - Supply caps
    - ERC-2612 permit (gasless approvals)

    Args:
        address: Deployed B20 token address.
        provider: BaseProvider instance.
    """

    def __init__(self, address: Address, provider: BaseProvider):
        self._address = Web3.to_checksum_address(address)
        self._provider = provider
        self._contract = provider.w3.eth.contract(
            address=self._address,
            abi=B20_TOKEN_ABI,
        )
        self._info: B20TokenInfo | None = None

    @property
    def address(self) -> Address:
        """Token contract address."""
        return self._address

    # ============================================================
    # Standard ERC-20 Methods
    # ============================================================

    def name(self) -> str:
        """Get token name."""
        return self._contract.functions.name().call()

    def symbol(self) -> str:
        """Get token symbol."""
        return self._contract.functions.symbol().call()

    def decimals(self) -> int:
        """Get token decimals."""
        return self._contract.functions.decimals().call()

    def total_supply(self) -> int:
        """Get total supply (raw)."""
        return self._contract.functions.totalSupply().call()

    def balance_of(self, address: Address) -> TokenAmount:
        """Get token balance of an address.

        Args:
            address: Address to check.

        Returns:
            TokenAmount with balance.
        """
        checksum = Web3.to_checksum_address(address)
        raw = self._contract.functions.balanceOf(checksum).call()
        return TokenAmount(
            raw=raw,
            decimals=self.decimals(),
            symbol=self.symbol(),
        )

    def allowance(self, owner: Address, spender: Address) -> TokenAmount:
        """Get allowance from owner to spender."""
        raw = self._contract.functions.allowance(
            Web3.to_checksum_address(owner),
            Web3.to_checksum_address(spender),
        ).call()
        return TokenAmount(raw=raw, decimals=self.decimals(), symbol=self.symbol())

    def build_transfer_tx(self, to: Address, amount: int) -> dict[str, Any]:
        """Build transfer transaction."""
        return self._contract.functions.transfer(
            Web3.to_checksum_address(to), amount
        ).build_transaction({"gas": 100_000})

    def build_approve_tx(self, spender: Address, amount: int) -> dict[str, Any]:
        """Build approval transaction."""
        return self._contract.functions.approve(
            Web3.to_checksum_address(spender), amount
        ).build_transaction({"gas": 60_000})

    # ============================================================
    # B20 Extensions
    # ============================================================

    def build_transfer_with_memo_tx(
        self, to: Address, amount: int, memo: str
    ) -> dict[str, Any]:
        """Build transfer with memo transaction.

        Args:
            to: Recipient address.
            amount: Raw token amount.
            memo: Memo string attached to the transfer.

        Returns:
            Unsigned transaction dictionary.
        """
        return self._contract.functions.transferWithMemo(
            Web3.to_checksum_address(to), amount, memo
        ).build_transaction({"gas": 120_000})

    def build_mint_tx(self, to: Address, amount: int) -> dict[str, Any]:
        """Build mint transaction (requires MINTER role).

        Args:
            to: Recipient of minted tokens.
            amount: Raw amount to mint.

        Returns:
            Unsigned transaction dictionary.
        """
        return self._contract.functions.mint(
            Web3.to_checksum_address(to), amount
        ).build_transaction({"gas": 100_000})

    def build_burn_tx(self, amount: int) -> dict[str, Any]:
        """Build burn transaction (requires BURNER role).

        Args:
            amount: Raw amount to burn from caller's balance.

        Returns:
            Unsigned transaction dictionary.
        """
        return self._contract.functions.burn(amount).build_transaction(
            {"gas": 80_000}
        )

    def supply_cap(self) -> int:
        """Get the token supply cap (0 = unlimited)."""
        return self._contract.functions.supplyCap().call()

    # ============================================================
    # Role Management
    # ============================================================

    def has_role(self, role: B20Role, account: Address) -> bool:
        """Check if an account has a specific role.

        Args:
            role: B20Role to check.
            account: Address to check.

        Returns:
            True if account has the role.
        """
        return self._contract.functions.hasRole(
            role.role_hash, Web3.to_checksum_address(account)
        ).call()

    def build_grant_role_tx(self, role: B20Role, account: Address) -> dict[str, Any]:
        """Build grant role transaction (requires ADMIN role)."""
        return self._contract.functions.grantRole(
            role.role_hash, Web3.to_checksum_address(account)
        ).build_transaction({"gas": 80_000})

    def build_revoke_role_tx(self, role: B20Role, account: Address) -> dict[str, Any]:
        """Build revoke role transaction (requires ADMIN role)."""
        return self._contract.functions.revokeRole(
            role.role_hash, Web3.to_checksum_address(account)
        ).build_transaction({"gas": 80_000})

    # ============================================================
    # Freeze / Compliance
    # ============================================================

    def is_frozen(self, account: Address) -> bool:
        """Check if an address is frozen."""
        return self._contract.functions.isFrozen(
            Web3.to_checksum_address(account)
        ).call()

    def build_freeze_tx(self, account: Address) -> dict[str, Any]:
        """Build freeze transaction (requires FREEZER role)."""
        return self._contract.functions.freeze(
            Web3.to_checksum_address(account)
        ).build_transaction({"gas": 60_000})

    def build_unfreeze_tx(self, account: Address) -> dict[str, Any]:
        """Build unfreeze transaction (requires FREEZER role)."""
        return self._contract.functions.unfreeze(
            Web3.to_checksum_address(account)
        ).build_transaction({"gas": 60_000})

    def build_burn_blocked_tx(self, account: Address) -> dict[str, Any]:
        """Build burn-blocked transaction (seize from frozen address)."""
        return self._contract.functions.burnBlocked(
            Web3.to_checksum_address(account)
        ).build_transaction({"gas": 80_000})

    # ============================================================
    # Pause
    # ============================================================

    def is_paused(self) -> bool:
        """Check if the token is paused."""
        return self._contract.functions.paused().call()

    def build_pause_tx(self) -> dict[str, Any]:
        """Build pause transaction (requires PAUSER role)."""
        return self._contract.functions.pause().build_transaction({"gas": 60_000})

    def build_unpause_tx(self) -> dict[str, Any]:
        """Build unpause transaction (requires PAUSER role)."""
        return self._contract.functions.unpause().build_transaction({"gas": 60_000})

    # ============================================================
    # Token Info
    # ============================================================

    def get_info(self) -> B20TokenInfo:
        """Get comprehensive token information.

        Returns:
            B20TokenInfo with all token details.
        """
        if self._info is None:
            name = self.name()
            symbol = self.symbol()
            decimals = self.decimals()
            total = self.total_supply()
            cap = self.supply_cap()
            paused = self.is_paused()

            # Determine token type from decimals
            token_type = (
                B20TokenType.STABLECOIN if decimals == 6
                else B20TokenType.ASSET
            )

            self._info = B20TokenInfo(
                address=self._address,
                name=name,
                symbol=symbol,
                decimals=decimals,
                token_type=token_type,
                total_supply=total,
                supply_cap=cap,
                paused=paused,
            )

        return self._info

    # ============================================================
    # ERC-2612 Permit
    # ============================================================

    def get_nonce(self, owner: Address) -> int:
        """Get permit nonce for an address."""
        return self._contract.functions.nonces(
            Web3.to_checksum_address(owner)
        ).call()

    def get_domain_separator(self) -> bytes:
        """Get EIP-712 domain separator."""
        return self._contract.functions.DOMAIN_SEPARATOR().call()

    def __repr__(self) -> str:
        info = self._info
        if info:
            return f"B20Token({info.symbol} @ {self._address})"
        return f"B20Token({self._address})"

"""Phase 3: B20 Token Standard Integration - Commits 35-55"""
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

# --- Commit 35: B20 ABI definitions ---
write("src/base_agent_toolkit/b20/__init__.py", '''"""B20 native token standard module (Beryl upgrade).

B20 is Base's native token standard — ERC-20 compatible tokens
implemented as Rust precompiles. Supports stablecoin, RWA,
and general-purpose token issuance.
"""

from .token import B20Token
from .factory import B20Factory
from .types import B20TokenType, B20Role, B20TokenConfig

__all__ = [
    "B20Token",
    "B20Factory",
    "B20TokenType",
    "B20Role",
    "B20TokenConfig",
]
''')

write("src/base_agent_toolkit/b20/abi.py", '''"""B20 token standard ABI definitions.

These ABIs define the interface for B20 tokens as specified in
the Base Standard Library (base-std). B20 is a superset of ERC-20.
"""

# B20 Factory precompile ABI
B20_FACTORY_ABI = [
    {
        "inputs": [
            {"name": "name", "type": "string"},
            {"name": "symbol", "type": "string"},
            {"name": "decimals", "type": "uint8"},
            {"name": "admin", "type": "address"},
            {"name": "supplyCap", "type": "uint256"},
        ],
        "name": "deployAsset",
        "outputs": [{"name": "token", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "name", "type": "string"},
            {"name": "symbol", "type": "string"},
            {"name": "admin", "type": "address"},
            {"name": "currencyCode", "type": "string"},
            {"name": "supplyCap", "type": "uint256"},
        ],
        "name": "deployStablecoin",
        "outputs": [{"name": "token", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "index", "type": "uint256"}],
        "name": "getToken",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "tokenCount",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# B20 Token ABI (superset of ERC-20)
B20_TOKEN_ABI = [
    # === Standard ERC-20 ===
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "transferFrom",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    # === B20 Extensions ===
    # Transfer with memo
    {
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "memo", "type": "string"},
        ],
        "name": "transferWithMemo",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    # Mint
    {
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    # Burn
    {
        "inputs": [{"name": "amount", "type": "uint256"}],
        "name": "burn",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    # Burn from blocked address (compliance)
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "burnBlocked",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    # Supply cap
    {
        "inputs": [],
        "name": "supplyCap",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    # Roles
    {
        "inputs": [
            {"name": "role", "type": "bytes32"},
            {"name": "account", "type": "address"},
        ],
        "name": "grantRole",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "role", "type": "bytes32"},
            {"name": "account", "type": "address"},
        ],
        "name": "revokeRole",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "role", "type": "bytes32"},
            {"name": "account", "type": "address"},
        ],
        "name": "hasRole",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    # Freeze / Unfreeze
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "freeze",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "unfreeze",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "isFrozen",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    # Pause
    {
        "inputs": [],
        "name": "pause",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "unpause",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "paused",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    # ERC-2612 Permit
    {
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "deadline", "type": "uint256"},
            {"name": "v", "type": "uint8"},
            {"name": "r", "type": "bytes32"},
            {"name": "s", "type": "bytes32"},
        ],
        "name": "permit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "nonces",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "DOMAIN_SEPARATOR",
        "outputs": [{"name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# Transfer event (shared by ERC-20 and B20)
TRANSFER_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "from", "type": "address"},
        {"indexed": True, "name": "to", "type": "address"},
        {"indexed": False, "name": "value", "type": "uint256"},
    ],
    "name": "Transfer",
    "type": "event",
}

# Approval event
APPROVAL_EVENT_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "owner", "type": "address"},
        {"indexed": True, "name": "spender", "type": "address"},
        {"indexed": False, "name": "value", "type": "uint256"},
    ],
    "name": "Approval",
    "type": "event",
}
''')

commit("feat(b20): add B20 token ABI and interface definitions")

# --- Commit 36: B20 types ---
write("src/base_agent_toolkit/b20/types.py", '''"""B20 token types and configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..types import Address


class B20TokenType(str, Enum):
    """B20 token variant types."""

    ASSET = "asset"
    STABLECOIN = "stablecoin"


class B20Role(str, Enum):
    """B20 role identifiers.

    Roles control access to privileged operations like
    minting, burning, freezing, and pausing.
    """

    ADMIN = "admin"
    MINTER = "minter"
    BURNER = "burner"
    FREEZER = "freezer"
    PAUSER = "pauser"

    @property
    def role_hash(self) -> bytes:
        """Get the keccak256 hash of the role name."""
        from web3 import Web3
        return Web3.keccak(text=self.value.upper() + "_ROLE")


@dataclass
class B20TokenConfig:
    """Configuration for deploying a new B20 token.

    Args:
        name: Token name (e.g., "My Token").
        symbol: Token symbol (e.g., "MTK").
        token_type: Asset or Stablecoin variant.
        admin: Admin address (receives all roles initially).
        decimals: Token decimals (6-18 for Asset, fixed 6 for Stablecoin).
        supply_cap: Maximum supply (0 = unlimited).
        currency_code: ISO 4217 code (Stablecoin only, e.g., "USD").
    """

    name: str
    symbol: str
    token_type: B20TokenType = B20TokenType.ASSET
    admin: Address = ""
    decimals: int = 18
    supply_cap: int = 0
    currency_code: str = ""

    def __post_init__(self):
        """Validate configuration."""
        if not self.name:
            raise ValueError("Token name is required")
        if not self.symbol:
            raise ValueError("Token symbol is required")

        if self.token_type == B20TokenType.STABLECOIN:
            self.decimals = 6  # Fixed for stablecoins
            if not self.currency_code:
                raise ValueError("Currency code required for stablecoin (e.g., 'USD')")
        else:
            if not (6 <= self.decimals <= 18):
                raise ValueError(f"Decimals must be 6-18, got {self.decimals}")


@dataclass
class B20TokenInfo:
    """Information about a deployed B20 token."""

    address: Address
    name: str
    symbol: str
    decimals: int
    token_type: B20TokenType
    total_supply: int = 0
    supply_cap: int = 0
    paused: bool = False
    currency_code: str = ""

    @property
    def has_supply_cap(self) -> bool:
        """Whether the token has a supply cap."""
        return self.supply_cap > 0

    @property
    def remaining_mintable(self) -> int:
        """How many more tokens can be minted."""
        if not self.has_supply_cap:
            return -1  # unlimited
        return max(0, self.supply_cap - self.total_supply)
''')

commit("feat(b20): add B20 types, roles, and token configuration")

# --- Commit 37: B20 Factory ---
write("src/base_agent_toolkit/b20/factory.py", '''"""B20Factory interaction for deploying B20 tokens."""

from __future__ import annotations

from typing import Any

from web3 import Web3

from ..constants import B20_FACTORY
from ..exceptions import B20DeploymentError, B20Error
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, TransactionResult
from .abi import B20_FACTORY_ABI
from .types import B20TokenConfig, B20TokenType

logger = get_logger(__name__)


class B20Factory:
    """Interface to the B20Factory precompile for deploying B20 tokens.

    The B20Factory is a singleton precompile at address 0x...0B20
    that deploys new B20 tokens as Rust precompiles.

    Args:
        provider: BaseProvider instance.
        factory_address: Override factory address (default: B20_FACTORY).
    """

    def __init__(
        self,
        provider: BaseProvider,
        factory_address: Address = B20_FACTORY,
    ):
        self._provider = provider
        self._address = Web3.to_checksum_address(factory_address)
        self._contract = provider.w3.eth.contract(
            address=self._address,
            abi=B20_FACTORY_ABI,
        )

        logger.debug("b20_factory.initialized", address=self._address)

    def build_deploy_asset_tx(
        self,
        config: B20TokenConfig,
    ) -> dict[str, Any]:
        """Build transaction to deploy a B20 Asset token.

        Args:
            config: Token configuration.

        Returns:
            Unsigned transaction dictionary.

        Raises:
            B20DeploymentError: If config is invalid for Asset type.
        """
        if config.token_type != B20TokenType.ASSET:
            raise B20DeploymentError(
                f"Expected ASSET type, got {config.token_type}"
            )

        admin = Web3.to_checksum_address(config.admin)
        return self._contract.functions.deployAsset(
            config.name,
            config.symbol,
            config.decimals,
            admin,
            config.supply_cap,
        ).build_transaction({"gas": 500_000})

    def build_deploy_stablecoin_tx(
        self,
        config: B20TokenConfig,
    ) -> dict[str, Any]:
        """Build transaction to deploy a B20 Stablecoin token.

        Args:
            config: Token configuration.

        Returns:
            Unsigned transaction dictionary.

        Raises:
            B20DeploymentError: If config is invalid for Stablecoin type.
        """
        if config.token_type != B20TokenType.STABLECOIN:
            raise B20DeploymentError(
                f"Expected STABLECOIN type, got {config.token_type}"
            )

        admin = Web3.to_checksum_address(config.admin)
        return self._contract.functions.deployStablecoin(
            config.name,
            config.symbol,
            admin,
            config.currency_code,
            config.supply_cap,
        ).build_transaction({"gas": 500_000})

    def build_deploy_tx(self, config: B20TokenConfig) -> dict[str, Any]:
        """Build deploy transaction for any B20 token type.

        Args:
            config: Token configuration.

        Returns:
            Unsigned transaction dictionary.
        """
        if config.token_type == B20TokenType.STABLECOIN:
            return self.build_deploy_stablecoin_tx(config)
        return self.build_deploy_asset_tx(config)

    def get_token_count(self) -> int:
        """Get the total number of deployed B20 tokens.

        Returns:
            Number of deployed tokens.
        """
        return self._contract.functions.tokenCount().call()

    def get_token_address(self, index: int) -> Address:
        """Get a deployed token address by index.

        Args:
            index: Token index (0-based).

        Returns:
            Token contract address.
        """
        return self._contract.functions.getToken(index).call()

    def list_tokens(self, limit: int = 100) -> list[Address]:
        """List all deployed B20 token addresses.

        Args:
            limit: Maximum number of tokens to return.

        Returns:
            List of token addresses.
        """
        count = min(self.get_token_count(), limit)
        tokens = []
        for i in range(count):
            addr = self.get_token_address(i)
            tokens.append(addr)
        return tokens

    def __repr__(self) -> str:
        return f"B20Factory({self._address})"
''')

commit("feat(b20): implement B20Factory for token deployment")

# --- Commit 38: B20 Token class ---
write("src/base_agent_toolkit/b20/token.py", '''"""B20 Token interaction class."""

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
''')

commit("feat(b20): implement B20Token class with full ERC-20 and B20 extensions")

# --- Commit 39: B20 permit helper ---
write("src/base_agent_toolkit/b20/permit.py", '''"""ERC-2612 permit signing for B20 tokens."""

from __future__ import annotations

import time
from typing import Any

from web3 import Web3

from ..logging import get_logger
from ..types import Address
from .token import B20Token

logger = get_logger(__name__)

# EIP-712 Permit type definition
PERMIT_TYPES = {
    "Permit": [
        {"name": "owner", "type": "address"},
        {"name": "spender", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ]
}


def build_permit_signature(
    token: B20Token,
    owner_private_key: str,
    spender: Address,
    value: int,
    deadline: int | None = None,
    chain_id: int = 8453,
) -> dict[str, Any]:
    """Build an ERC-2612 permit signature for gasless approval.

    This allows a user to sign an off-chain message that authorizes
    a spender to use their tokens, without needing to send a transaction.

    Args:
        token: B20Token instance.
        owner_private_key: Private key of the token owner.
        spender: Address to approve.
        value: Amount to approve (raw).
        deadline: Unix timestamp deadline (default: 1 hour from now).
        chain_id: Chain ID for EIP-712 domain.

    Returns:
        Dictionary with v, r, s signature components and parameters.
    """
    from eth_account import Account
    from eth_account.messages import encode_typed_data

    if deadline is None:
        deadline = int(time.time()) + 3600  # 1 hour from now

    # Get owner address
    if not owner_private_key.startswith("0x"):
        owner_private_key = f"0x{owner_private_key}"
    account = Account.from_key(owner_private_key)
    owner = account.address

    # Get permit nonce
    nonce = token.get_nonce(owner)

    # Build EIP-712 domain
    domain = {
        "name": token.name(),
        "version": "1",
        "chainId": chain_id,
        "verifyingContract": token.address,
    }

    # Build message
    message = {
        "owner": owner,
        "spender": Web3.to_checksum_address(spender),
        "value": value,
        "nonce": nonce,
        "deadline": deadline,
    }

    # Sign
    signable = encode_typed_data(
        domain_data=domain,
        message_types=PERMIT_TYPES,
        message_data=message,
    )
    signed = account.sign_message(signable)

    logger.info(
        "permit.signed",
        token=token.address,
        owner=owner,
        spender=spender,
        value=value,
        deadline=deadline,
    )

    return {
        "owner": owner,
        "spender": Web3.to_checksum_address(spender),
        "value": value,
        "deadline": deadline,
        "v": signed.v,
        "r": signed.r.to_bytes(32, "big"),
        "s": signed.s.to_bytes(32, "big"),
    }


def build_permit_tx(
    token: B20Token,
    permit_data: dict[str, Any],
) -> dict[str, Any]:
    """Build a permit transaction from signed permit data.

    This submits the permit on-chain so the approval takes effect.
    Any address can submit this transaction.

    Args:
        token: B20Token instance.
        permit_data: Output from build_permit_signature().

    Returns:
        Unsigned transaction dictionary.
    """
    return token._contract.functions.permit(
        permit_data["owner"],
        permit_data["spender"],
        permit_data["value"],
        permit_data["deadline"],
        permit_data["v"],
        permit_data["r"],
        permit_data["s"],
    ).build_transaction({"gas": 80_000})
''')

commit("feat(b20): implement ERC-2612 permit signing for gasless approvals")

# --- Commit 40: B20 event listener ---
write("src/base_agent_toolkit/b20/events.py", '''"""B20 token event listener and parser."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web3 import Web3

from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address
from .abi import B20_TOKEN_ABI

logger = get_logger(__name__)


@dataclass
class B20TransferEvent:
    """Parsed B20/ERC-20 Transfer event."""

    token_address: Address
    from_address: Address
    to_address: Address
    amount: int
    block_number: int
    tx_hash: str
    log_index: int

    @property
    def is_mint(self) -> bool:
        """True if this is a mint (from zero address)."""
        return self.from_address == "0x0000000000000000000000000000000000000000"

    @property
    def is_burn(self) -> bool:
        """True if this is a burn (to zero address)."""
        return self.to_address == "0x0000000000000000000000000000000000000000"


@dataclass
class B20ApprovalEvent:
    """Parsed B20/ERC-20 Approval event."""

    token_address: Address
    owner: Address
    spender: Address
    amount: int
    block_number: int
    tx_hash: str


class B20EventListener:
    """Listen for and parse B20 token events.

    Args:
        token_address: B20 token contract address.
        provider: BaseProvider instance.
    """

    def __init__(self, token_address: Address, provider: BaseProvider):
        self._token_address = Web3.to_checksum_address(token_address)
        self._provider = provider
        self._contract = provider.w3.eth.contract(
            address=self._token_address,
            abi=B20_TOKEN_ABI,
        )

    def get_transfers(
        self,
        from_block: int | str = "latest",
        to_block: int | str = "latest",
        from_address: Address | None = None,
        to_address: Address | None = None,
    ) -> list[B20TransferEvent]:
        """Get Transfer events for the token.

        Args:
            from_block: Start block number or 'latest'.
            to_block: End block number or 'latest'.
            from_address: Filter by sender address.
            to_address: Filter by recipient address.

        Returns:
            List of B20TransferEvent objects.
        """
        filters: dict[str, Any] = {}
        if from_address:
            filters["from"] = Web3.to_checksum_address(from_address)
        if to_address:
            filters["to"] = Web3.to_checksum_address(to_address)

        try:
            event_filter = self._contract.events.Transfer.create_filter(
                fromBlock=from_block,
                toBlock=to_block,
                argument_filters=filters if filters else None,
            )
            entries = event_filter.get_all_entries()
        except Exception as e:
            logger.warning("b20_events.transfer_query_failed", error=str(e))
            return []

        events = []
        for entry in entries:
            events.append(
                B20TransferEvent(
                    token_address=self._token_address,
                    from_address=entry.args.get("from", ""),
                    to_address=entry.args.get("to", ""),
                    amount=entry.args.get("value", 0),
                    block_number=entry.blockNumber,
                    tx_hash=entry.transactionHash.hex(),
                    log_index=entry.logIndex,
                )
            )

        logger.info(
            "b20_events.transfers_found",
            token=self._token_address,
            count=len(events),
        )
        return events

    def get_approvals(
        self,
        from_block: int | str = "latest",
        to_block: int | str = "latest",
        owner: Address | None = None,
    ) -> list[B20ApprovalEvent]:
        """Get Approval events for the token.

        Args:
            from_block: Start block number.
            to_block: End block number.
            owner: Filter by token owner.

        Returns:
            List of B20ApprovalEvent objects.
        """
        filters: dict[str, Any] = {}
        if owner:
            filters["owner"] = Web3.to_checksum_address(owner)

        try:
            event_filter = self._contract.events.Approval.create_filter(
                fromBlock=from_block,
                toBlock=to_block,
                argument_filters=filters if filters else None,
            )
            entries = event_filter.get_all_entries()
        except Exception as e:
            logger.warning("b20_events.approval_query_failed", error=str(e))
            return []

        events = []
        for entry in entries:
            events.append(
                B20ApprovalEvent(
                    token_address=self._token_address,
                    owner=entry.args.get("owner", ""),
                    spender=entry.args.get("spender", ""),
                    amount=entry.args.get("value", 0),
                    block_number=entry.blockNumber,
                    tx_hash=entry.transactionHash.hex(),
                )
            )

        return events

    def get_recent_activity(
        self,
        blocks_back: int = 1000,
    ) -> dict[str, Any]:
        """Get recent token activity summary.

        Args:
            blocks_back: Number of blocks to look back.

        Returns:
            Summary dictionary with transfer and approval counts.
        """
        current_block = self._provider.get_block_number()
        from_block = max(0, current_block - blocks_back)

        transfers = self.get_transfers(from_block=from_block, to_block="latest")
        approvals = self.get_approvals(from_block=from_block, to_block="latest")

        mints = [t for t in transfers if t.is_mint]
        burns = [t for t in transfers if t.is_burn]
        regular = [t for t in transfers if not t.is_mint and not t.is_burn]

        return {
            "token": self._token_address,
            "from_block": from_block,
            "to_block": current_block,
            "total_transfers": len(transfers),
            "mints": len(mints),
            "burns": len(burns),
            "regular_transfers": len(regular),
            "approvals": len(approvals),
            "total_minted": sum(m.amount for m in mints),
            "total_burned": sum(b.amount for b in burns),
        }
''')

commit("feat(b20): add event listener for Transfer and Approval events")

# --- Commit 41: B20 batch operations ---
write("src/base_agent_toolkit/b20/batch.py", '''"""Batch operations for B20 tokens."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web3 import Web3

from ..logging import get_logger
from ..types import Address
from .token import B20Token

logger = get_logger(__name__)


@dataclass
class MintRequest:
    """Single mint request in a batch."""

    to: Address
    amount: int


@dataclass
class TransferRequest:
    """Single transfer request in a batch."""

    to: Address
    amount: int
    memo: str = ""


class B20BatchOperations:
    """Batch operations for B20 tokens.

    Provides helpers for building multiple transactions
    for airdrops, batch minting, and multi-recipient transfers.

    Args:
        token: B20Token instance.
    """

    def __init__(self, token: B20Token):
        self._token = token

    def build_batch_mint_txs(
        self,
        requests: list[MintRequest],
    ) -> list[dict[str, Any]]:
        """Build multiple mint transactions.

        Args:
            requests: List of MintRequest objects.

        Returns:
            List of unsigned transaction dictionaries.
        """
        txs = []
        for req in requests:
            tx = self._token.build_mint_tx(req.to, req.amount)
            txs.append(tx)

        logger.info(
            "b20_batch.mint_prepared",
            count=len(txs),
            total_amount=sum(r.amount for r in requests),
        )
        return txs

    def build_batch_transfer_txs(
        self,
        requests: list[TransferRequest],
    ) -> list[dict[str, Any]]:
        """Build multiple transfer transactions.

        Args:
            requests: List of TransferRequest objects.

        Returns:
            List of unsigned transaction dictionaries.
        """
        txs = []
        for req in requests:
            if req.memo:
                tx = self._token.build_transfer_with_memo_tx(
                    req.to, req.amount, req.memo
                )
            else:
                tx = self._token.build_transfer_tx(req.to, req.amount)
            txs.append(tx)

        logger.info(
            "b20_batch.transfer_prepared",
            count=len(txs),
            total_amount=sum(r.amount for r in requests),
        )
        return txs

    def build_airdrop_txs(
        self,
        recipients: list[Address],
        amount_per_recipient: int,
        memo: str = "",
    ) -> list[dict[str, Any]]:
        """Build airdrop transactions (equal amount to each recipient).

        Args:
            recipients: List of recipient addresses.
            amount_per_recipient: Raw amount each recipient gets.
            memo: Optional memo for all transfers.

        Returns:
            List of unsigned transaction dictionaries.
        """
        requests = [
            TransferRequest(to=addr, amount=amount_per_recipient, memo=memo)
            for addr in recipients
        ]
        return self.build_batch_transfer_txs(requests)

    @staticmethod
    def parse_csv_recipients(csv_content: str) -> list[MintRequest]:
        """Parse CSV content into mint requests.

        Expected format: address,amount (one per line)

        Args:
            csv_content: CSV string content.

        Returns:
            List of MintRequest objects.
        """
        requests = []
        for line in csv_content.strip().split("\\n"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("address"):
                continue
            parts = line.split(",")
            if len(parts) >= 2:
                address = parts[0].strip()
                amount = int(parts[1].strip())
                requests.append(MintRequest(to=address, amount=amount))

        logger.info("b20_batch.csv_parsed", recipients=len(requests))
        return requests
''')

commit("feat(b20): add batch operations for airdrops and multi-mint")

# --- Commit 42: B20 tests ---
write("tests/test_b20.py", '''"""Tests for B20 token module."""

import pytest

from base_agent_toolkit.b20.types import (
    B20Role,
    B20TokenConfig,
    B20TokenInfo,
    B20TokenType,
)
from base_agent_toolkit.b20.batch import (
    B20BatchOperations,
    MintRequest,
    TransferRequest,
)
from base_agent_toolkit.b20.events import B20TransferEvent


class TestB20TokenConfig:
    """Tests for B20TokenConfig."""

    def test_asset_config(self):
        config = B20TokenConfig(
            name="Test Token",
            symbol="TST",
            token_type=B20TokenType.ASSET,
            admin="0x1234567890123456789012345678901234567890",
            decimals=18,
        )
        assert config.decimals == 18
        assert config.token_type == B20TokenType.ASSET

    def test_stablecoin_config(self):
        config = B20TokenConfig(
            name="Test USD",
            symbol="tUSD",
            token_type=B20TokenType.STABLECOIN,
            admin="0x1234567890123456789012345678901234567890",
            currency_code="USD",
        )
        assert config.decimals == 6  # Fixed for stablecoin
        assert config.currency_code == "USD"

    def test_stablecoin_requires_currency_code(self):
        with pytest.raises(ValueError, match="Currency code required"):
            B20TokenConfig(
                name="Test",
                symbol="TST",
                token_type=B20TokenType.STABLECOIN,
                admin="0x1234",
            )

    def test_invalid_decimals(self):
        with pytest.raises(ValueError, match="Decimals must be 6-18"):
            B20TokenConfig(
                name="Test",
                symbol="TST",
                token_type=B20TokenType.ASSET,
                admin="0x1234",
                decimals=2,
            )

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="name is required"):
            B20TokenConfig(name="", symbol="TST")


class TestB20Role:
    """Tests for B20Role."""

    def test_role_values(self):
        assert B20Role.ADMIN.value == "admin"
        assert B20Role.MINTER.value == "minter"
        assert B20Role.BURNER.value == "burner"

    def test_role_hash(self):
        """Role hashes should be 32 bytes."""
        for role in B20Role:
            assert len(role.role_hash) == 32


class TestB20TokenInfo:
    """Tests for B20TokenInfo."""

    def test_has_supply_cap(self):
        info = B20TokenInfo(
            address="0x1234",
            name="Test",
            symbol="TST",
            decimals=18,
            token_type=B20TokenType.ASSET,
            supply_cap=1_000_000,
            total_supply=500_000,
        )
        assert info.has_supply_cap is True
        assert info.remaining_mintable == 500_000

    def test_no_supply_cap(self):
        info = B20TokenInfo(
            address="0x1234",
            name="Test",
            symbol="TST",
            decimals=18,
            token_type=B20TokenType.ASSET,
            supply_cap=0,
        )
        assert info.has_supply_cap is False
        assert info.remaining_mintable == -1


class TestB20TransferEvent:
    """Tests for B20TransferEvent."""

    def test_regular_transfer(self):
        event = B20TransferEvent(
            token_address="0xtoken",
            from_address="0xsender",
            to_address="0xreceiver",
            amount=1000,
            block_number=100,
            tx_hash="0xhash",
            log_index=0,
        )
        assert not event.is_mint
        assert not event.is_burn

    def test_mint_event(self):
        event = B20TransferEvent(
            token_address="0xtoken",
            from_address="0x0000000000000000000000000000000000000000",
            to_address="0xreceiver",
            amount=1000,
            block_number=100,
            tx_hash="0xhash",
            log_index=0,
        )
        assert event.is_mint
        assert not event.is_burn

    def test_burn_event(self):
        event = B20TransferEvent(
            token_address="0xtoken",
            from_address="0xsender",
            to_address="0x0000000000000000000000000000000000000000",
            amount=1000,
            block_number=100,
            tx_hash="0xhash",
            log_index=0,
        )
        assert not event.is_mint
        assert event.is_burn


class TestBatchOperations:
    """Tests for batch CSV parsing."""

    def test_parse_csv(self):
        csv = """address,amount
0x1234567890123456789012345678901234567890,1000
0x0987654321098765432109876543210987654321,2000
"""
        requests = B20BatchOperations.parse_csv_recipients(csv)
        assert len(requests) == 2
        assert requests[0].amount == 1000
        assert requests[1].amount == 2000

    def test_parse_csv_skip_comments(self):
        csv = """# This is a comment
0x1234567890123456789012345678901234567890,1000
"""
        requests = B20BatchOperations.parse_csv_recipients(csv)
        assert len(requests) == 1
''')

commit("test(b20): add comprehensive tests for B20 types, events, and batch operations")

# --- Commit 43: B20 documentation ---
os.makedirs("docs/guides", exist_ok=True)
write("docs/guides/b20-tokens.md", '''# B20 Token Standard Guide

## Overview

B20 is Base's native token standard, introduced with the **Beryl upgrade** (June 25, 2026). Unlike traditional ERC-20 tokens deployed as smart contracts, B20 tokens are implemented as **Rust precompiles** — making them faster, cheaper, and more deeply integrated with the Base chain.

## Key Features

- **ERC-20 Compatible** — All existing ERC-20 tooling works with B20 tokens
- **Transfer with Memo** — Attach messages to transfers
- **Role-Based Access** — Admin, minter, burner, freezer, pauser roles
- **Supply Caps** — Optional maximum supply limits
- **Freeze/Seize** — Compliance features for regulated tokens
- **ERC-2612 Permit** — Gasless approvals via signatures
- **Two Variants** — Asset (configurable decimals) and Stablecoin (6 decimals, currency code)

## Quick Start

### Deploy a B20 Token

```python
from base_agent_toolkit.b20 import B20Factory, B20TokenConfig, B20TokenType
from base_agent_toolkit import BaseProvider, BaseWallet

# Connect
provider = BaseProvider(network="mainnet")
wallet = BaseWallet.from_private_key("0x...", provider)

# Configure token
config = B20TokenConfig(
    name="My Token",
    symbol="MTK",
    token_type=B20TokenType.ASSET,
    admin=wallet.address,
    decimals=18,
    supply_cap=1_000_000 * 10**18,  # 1M tokens
)

# Deploy via B20Factory
factory = B20Factory(provider)
tx = factory.build_deploy_tx(config)
# ... sign and send tx
```

### Deploy a Stablecoin

```python
config = B20TokenConfig(
    name="My USD",
    symbol="mUSD",
    token_type=B20TokenType.STABLECOIN,
    admin=wallet.address,
    currency_code="USD",
    supply_cap=0,  # unlimited
)
```

### Interact with a B20 Token

```python
from base_agent_toolkit.b20 import B20Token

token = B20Token("0xTokenAddress...", provider)

# Read operations
info = token.get_info()
balance = token.balance_of(wallet.address)
print(f"{info.name}: {balance}")

# Transfer with memo
tx = token.build_transfer_with_memo_tx(
    to="0xRecipient...",
    amount=1000 * 10**18,
    memo="Payment for services",
)

# Mint (requires MINTER role)
tx = token.build_mint_tx(to="0xRecipient...", amount=1000 * 10**18)
```

### Gasless Approvals with Permit

```python
from base_agent_toolkit.b20.permit import build_permit_signature, build_permit_tx

# Sign permit off-chain (no gas needed)
permit = build_permit_signature(
    token=token,
    owner_private_key="0x...",
    spender="0xDEX...",
    value=1000 * 10**18,
)

# Anyone can submit the permit on-chain
tx = build_permit_tx(token, permit)
```

### Batch Airdrop

```python
from base_agent_toolkit.b20.batch import B20BatchOperations

batch = B20BatchOperations(token)
txs = batch.build_airdrop_txs(
    recipients=["0xAddr1...", "0xAddr2...", "0xAddr3..."],
    amount_per_recipient=100 * 10**18,
    memo="Community airdrop",
)
```

## Role Management

| Role | Permissions |
|------|------------|
| ADMIN | Grant/revoke roles, full control |
| MINTER | Mint new tokens |
| BURNER | Burn tokens |
| FREEZER | Freeze/unfreeze addresses |
| PAUSER | Pause/unpause token operations |

```python
from base_agent_toolkit.b20 import B20Role

# Check role
has_minter = token.has_role(B20Role.MINTER, wallet.address)

# Grant role (requires ADMIN)
tx = token.build_grant_role_tx(B20Role.MINTER, "0xNewMinter...")
```

## Compliance Features

```python
# Freeze an address
tx = token.build_freeze_tx("0xSuspicious...")

# Check if frozen
is_frozen = token.is_frozen("0xAddress...")

# Seize tokens from frozen address
tx = token.build_burn_blocked_tx("0xFrozen...")
```

## Asset vs Stablecoin

| Feature | Asset | Stablecoin |
|---------|-------|------------|
| Decimals | 6-18 (configurable) | 6 (fixed) |
| Currency Code | No | Yes (e.g., "USD") |
| Rebase | Yes | No |
| Batch Issuance | Yes | No |
| Announcements | Yes | No |

## Reference

- [B20 Spec](https://docs.base.org/base-chain/specs/upgrades/beryl/b20)
- [Base Standard Library](https://github.com/base/base-std)
- [Beryl Upgrade Overview](https://docs.base.org/base-chain/specs/upgrades/beryl/overview)
''')

commit("docs(b20): write comprehensive B20 integration guide")

# --- Commit 44: B20 example script ---
os.makedirs("examples", exist_ok=True)
write("examples/b20_deploy.py", '''#!/usr/bin/env python3
"""Example: Deploy and manage a B20 token on Base.

This script demonstrates:
1. Deploying a B20 Asset token via B20Factory
2. Querying token information
3. Minting tokens
4. Transferring with memo
5. Managing roles

Requirements:
    pip install base-agent-toolkit

Usage:
    python examples/b20_deploy.py
"""

import asyncio
import os
from decimal import Decimal

# Note: In production, import from the installed package
# from base_agent_toolkit import BaseProvider, BaseWallet
# from base_agent_toolkit.b20 import B20Factory, B20Token, B20TokenConfig, B20TokenType, B20Role


def main():
    """Deploy and interact with a B20 token."""
    print("=" * 60)
    print("  B20 Token Deployment Example")
    print("  Base Agent Toolkit")
    print("=" * 60)

    # Configuration
    private_key = os.environ.get("BAT_PRIVATE_KEY", "")
    network = os.environ.get("BAT_NETWORK", "sepolia")

    if not private_key:
        print("\\n⚠️  Set BAT_PRIVATE_KEY environment variable")
        print("   export BAT_PRIVATE_KEY=your_private_key_here")
        print("\\nRunning in demo mode (no transactions will be sent)\\n")
        demo_mode()
        return

    print(f"\\n🔗 Network: {network}")
    print("🚀 Starting deployment...\\n")

    # In a real implementation:
    # provider = BaseProvider(network=network)
    # wallet = BaseWallet.from_private_key(private_key, provider)
    # factory = B20Factory(provider)
    #
    # config = B20TokenConfig(
    #     name="Demo Token",
    #     symbol="DEMO",
    #     token_type=B20TokenType.ASSET,
    #     admin=wallet.address,
    #     decimals=18,
    #     supply_cap=1_000_000 * 10**18,
    # )
    #
    # tx = factory.build_deploy_tx(config)
    # ... sign and send


def demo_mode():
    """Demonstrate B20 operations without sending transactions."""
    from base_agent_toolkit.b20.types import B20TokenConfig, B20TokenType, B20TokenInfo, B20Role

    # 1. Token Configuration
    print("📋 Step 1: Configure B20 Token")
    config = B20TokenConfig(
        name="Demo Token",
        symbol="DEMO",
        token_type=B20TokenType.ASSET,
        admin="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        decimals=18,
        supply_cap=1_000_000,
    )
    print(f"   Name: {config.name}")
    print(f"   Symbol: {config.symbol}")
    print(f"   Type: {config.token_type.value}")
    print(f"   Decimals: {config.decimals}")
    print(f"   Supply Cap: {config.supply_cap:,}")
    print()

    # 2. Token Info (simulated)
    print("📊 Step 2: Token Info (simulated)")
    info = B20TokenInfo(
        address="0x1234567890123456789012345678901234567890",
        name="Demo Token",
        symbol="DEMO",
        decimals=18,
        token_type=B20TokenType.ASSET,
        total_supply=100_000,
        supply_cap=1_000_000,
    )
    print(f"   Address: {info.address}")
    print(f"   Total Supply: {info.total_supply:,}")
    print(f"   Supply Cap: {info.supply_cap:,}")
    print(f"   Remaining Mintable: {info.remaining_mintable:,}")
    print(f"   Has Supply Cap: {info.has_supply_cap}")
    print()

    # 3. Roles
    print("🔑 Step 3: Available Roles")
    for role in B20Role:
        print(f"   {role.value.upper()}: {role.role_hash.hex()[:16]}...")
    print()

    # 4. Stablecoin variant
    print("💵 Step 4: Stablecoin Configuration")
    stable_config = B20TokenConfig(
        name="Demo USD",
        symbol="dUSD",
        token_type=B20TokenType.STABLECOIN,
        admin="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        currency_code="USD",
    )
    print(f"   Name: {stable_config.name}")
    print(f"   Currency: {stable_config.currency_code}")
    print(f"   Decimals: {stable_config.decimals} (fixed for stablecoin)")
    print()

    print("✅ Demo complete! Set BAT_PRIVATE_KEY to deploy for real.")


if __name__ == "__main__":
    main()
''')

commit("examples(b20): add example script for B20 token deployment and management")

# --- Commit 45: Update B20 __init__ with all exports ---
write("src/base_agent_toolkit/b20/__init__.py", '''"""B20 native token standard module (Beryl upgrade).

B20 is Base's native token standard — ERC-20 compatible tokens
implemented as Rust precompiles. Supports stablecoin, RWA,
and general-purpose token issuance.

Introduced with the Beryl upgrade on June 25, 2026.
"""

from .batch import B20BatchOperations, MintRequest, TransferRequest
from .events import B20EventListener, B20TransferEvent, B20ApprovalEvent
from .factory import B20Factory
from .permit import build_permit_signature, build_permit_tx
from .token import B20Token
from .types import B20Role, B20TokenConfig, B20TokenInfo, B20TokenType

__all__ = [
    "B20BatchOperations",
    "B20EventListener",
    "B20Factory",
    "B20Token",
    "B20TokenConfig",
    "B20TokenInfo",
    "B20TokenType",
    "B20Role",
    "B20TransferEvent",
    "B20ApprovalEvent",
    "MintRequest",
    "TransferRequest",
    "build_permit_signature",
    "build_permit_tx",
]
''')

commit("refactor(b20): consolidate B20 module exports")

print("\\n=== Phase 3 complete! ===")
result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True, cwd=ROOT)
lines = result.stdout.strip().splitlines()
print(f"Total commits: {len(lines)}")

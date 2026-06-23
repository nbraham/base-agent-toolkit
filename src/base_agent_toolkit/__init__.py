"""Base Agent Toolkit - Python SDK for building AI agents on Base L2.

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

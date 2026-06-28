"""Base Agent Toolkit — Python SDK for AI agents on Base L2.

Build autonomous AI agents that interact with the Base chain,
manage wallets, trade on DeFi protocols, deploy B20 tokens,
and make HTTP payments via x402.

Modules:
    - wallet: Key management, transactions, HD wallets
    - b20: B20 native token standard (Beryl upgrade)
    - defi: Aerodrome, Uniswap V3, Morpho Blue
    - agent: AI agent framework with strategies
    - x402: HTTP payment protocol
    - security: Key validation and encryption
    - cli: Command-line interface

Quick Start:
    >>> from base_agent_toolkit import BaseProvider
    >>> provider = BaseProvider(chain_id=8453)
"""

__version__ = "0.1.0"
__author__ = "nbraham"

from .provider.base import BaseProvider
from .provider.manager import ProviderManager
from .network import resolve_network, get_network
from .registry import get_token, list_all_tokens

__all__ = [
    "__version__",
    "BaseProvider",
    "ProviderManager",
    "resolve_network",
    "get_network",
    "get_token",
    "list_all_tokens",
]

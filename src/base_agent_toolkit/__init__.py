"""Base Agent Toolkit — Python SDK for AI agents on Base L2.

Build autonomous AI agents that interact with the Base chain,
manage wallets, trade on DeFi protocols, deploy B20 tokens,
and make HTTP payments via x402.

Quick Start:
    >>> from base_agent_toolkit import BaseProvider, BaseWallet
    >>> provider = BaseProvider(chain_id=8453)
    >>> wallet = BaseWallet.create(provider)
    >>> print(wallet.address)
"""

__version__ = "0.1.0"
__author__ = "nbraham"

from .provider.base import BaseProvider
from .provider.manager import ProviderManager

__all__ = [
    "__version__",
    "BaseProvider",
    "ProviderManager",
]

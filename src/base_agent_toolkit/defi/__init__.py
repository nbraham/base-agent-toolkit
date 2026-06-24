"""DeFi protocol integrations for Base chain.

Provides interfaces to major DeFi protocols on Base:
- Aerodrome (DEX)
- Uniswap V3 (DEX)
- Morpho (Lending)
- Moonwell (Lending)
"""

from .aerodrome import AerodromeRouter
from .uniswap import UniswapV3Router
from .morpho import MorphoClient
from .swap import SwapQuote, swap_tokens
from .approval import ApprovalManager

__all__ = [
    "AerodromeRouter",
    "UniswapV3Router",
    "MorphoClient",
    "SwapQuote",
    "swap_tokens",
    "ApprovalManager",
]

"""DeFi protocol integrations for Base chain.

Provides interfaces to major DeFi protocols on Base:
- Aerodrome (DEX) — Primary liquidity backbone
- Uniswap V3 (DEX) — Concentrated liquidity AMM
- Morpho Blue (Lending) — Efficient lending markets
- WETH Helper — ETH wrap/unwrap
- Portfolio Tracker — Track positions across protocols
- Approval Manager — Manage token approvals safely
"""

from .aerodrome import AerodromeRouter
from .approval import ApprovalManager
from .morpho import MorphoClient, MorphoMarket, MorphoPosition
from .portfolio import PortfolioSnapshot, PortfolioTracker, TokenPosition
from .swap import SwapProtocol, SwapQuote, SwapResult, calculate_min_amount_out
from .uniswap import UniswapV3Router
from .weth import WETHHelper

__all__ = [
    "AerodromeRouter",
    "ApprovalManager",
    "MorphoClient",
    "MorphoMarket",
    "MorphoPosition",
    "PortfolioSnapshot",
    "PortfolioTracker",
    "SwapProtocol",
    "SwapQuote",
    "SwapResult",
    "TokenPosition",
    "UniswapV3Router",
    "WETHHelper",
    "calculate_min_amount_out",
]

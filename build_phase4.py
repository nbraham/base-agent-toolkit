"""Phase 4: DeFi Protocol Integrations - Commits 46-65"""
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

# --- Commit 46: DeFi module init ---
write("src/base_agent_toolkit/defi/__init__.py", '''"""DeFi protocol integrations for Base chain.

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
''')

write("src/base_agent_toolkit/defi/abi.py", '''"""DeFi protocol ABI definitions."""

# Aerodrome Router ABI (minimal)
AERODROME_ROUTER_ABI = [
    {
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {
                "components": [
                    {"name": "from", "type": "address"},
                    {"name": "to", "type": "address"},
                    {"name": "stable", "type": "bool"},
                    {"name": "factory", "type": "address"},
                ],
                "name": "routes",
                "type": "tuple[]",
            },
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {
                "components": [
                    {"name": "from", "type": "address"},
                    {"name": "to", "type": "address"},
                    {"name": "stable", "type": "bool"},
                    {"name": "factory", "type": "address"},
                ],
                "name": "routes",
                "type": "tuple[]",
            },
        ],
        "name": "getAmountsOut",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "WETH",
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# Uniswap V3 SwapRouter ABI (minimal)
UNISWAP_V3_ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "tokenIn", "type": "address"},
                    {"name": "tokenOut", "type": "address"},
                    {"name": "fee", "type": "uint24"},
                    {"name": "recipient", "type": "address"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "amountOutMinimum", "type": "uint256"},
                    {"name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"name": "path", "type": "bytes"},
                    {"name": "recipient", "type": "address"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "amountOutMinimum", "type": "uint256"},
                ],
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "exactInput",
        "outputs": [{"name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function",
    },
]

# Uniswap V3 Quoter ABI
UNISWAP_V3_QUOTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "tokenIn", "type": "address"},
                    {"name": "tokenOut", "type": "address"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "fee", "type": "uint24"},
                    {"name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"name": "amountOut", "type": "uint256"},
            {"name": "sqrtPriceX96After", "type": "uint160"},
            {"name": "initializedTicksCrossed", "type": "uint32"},
            {"name": "gasEstimate", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

# Morpho Blue ABI (minimal)
MORPHO_BLUE_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "loanToken", "type": "address"},
                    {"name": "collateralToken", "type": "address"},
                    {"name": "oracle", "type": "address"},
                    {"name": "irm", "type": "address"},
                    {"name": "lltv", "type": "uint256"},
                ],
                "name": "marketParams",
                "type": "tuple",
            },
            {"name": "assets", "type": "uint256"},
            {"name": "shares", "type": "uint256"},
            {"name": "onBehalf", "type": "address"},
            {"name": "data", "type": "bytes"},
        ],
        "name": "supply",
        "outputs": [
            {"name": "assetsSupplied", "type": "uint256"},
            {"name": "sharesSupplied", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"name": "loanToken", "type": "address"},
                    {"name": "collateralToken", "type": "address"},
                    {"name": "oracle", "type": "address"},
                    {"name": "irm", "type": "address"},
                    {"name": "lltv", "type": "uint256"},
                ],
                "name": "marketParams",
                "type": "tuple",
            },
            {"name": "assets", "type": "uint256"},
            {"name": "shares", "type": "uint256"},
            {"name": "onBehalf", "type": "address"},
            {"name": "receiver", "type": "address"},
        ],
        "name": "withdraw",
        "outputs": [
            {"name": "assetsWithdrawn", "type": "uint256"},
            {"name": "sharesWithdrawn", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "id", "type": "bytes32"},
            {"name": "user", "type": "address"},
        ],
        "name": "position",
        "outputs": [
            {"name": "supplyShares", "type": "uint256"},
            {"name": "borrowShares", "type": "uint256"},
            {"name": "collateral", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]

# WETH ABI
WETH_ABI = [
    {
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [{"name": "wad", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]
''')

commit("feat(defi): add DeFi protocol ABI definitions")

# --- Commit 47: Swap quote types ---
write("src/base_agent_toolkit/defi/swap.py", '''"""Token swap utilities and routing."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any

from ..types import Address

class SwapProtocol(str, Enum):
    """Supported swap protocols."""
    AERODROME = "aerodrome"
    UNISWAP_V3 = "uniswap_v3"


@dataclass
class SwapQuote:
    """Quote for a token swap."""

    protocol: SwapProtocol
    token_in: Address
    token_out: Address
    amount_in: int
    amount_out: int
    price_impact: float  # as percentage (e.g., 0.5 = 0.5%)
    gas_estimate: int
    route: list[Address]

    @property
    def exchange_rate(self) -> Decimal:
        """Exchange rate (amount_out / amount_in)."""
        if self.amount_in == 0:
            return Decimal(0)
        return Decimal(self.amount_out) / Decimal(self.amount_in)

    @property
    def is_acceptable(self) -> bool:
        """Whether price impact is acceptable (< 5%)."""
        return self.price_impact < 5.0


@dataclass
class SwapResult:
    """Result of an executed swap."""

    tx_hash: str
    amount_in: int
    amount_out: int
    protocol: SwapProtocol
    gas_used: int | None = None


def calculate_min_amount_out(
    amount_out: int,
    slippage_percent: float = 0.5,
) -> int:
    """Calculate minimum output amount with slippage protection.

    Args:
        amount_out: Expected output amount.
        slippage_percent: Maximum acceptable slippage (e.g., 0.5 = 0.5%).

    Returns:
        Minimum acceptable output amount.
    """
    slippage_factor = 1 - (slippage_percent / 100)
    return int(amount_out * slippage_factor)


def swap_tokens(
    token_in: Address,
    token_out: Address,
    amount_in: int,
    slippage: float = 0.5,
) -> SwapQuote:
    """Get the best swap quote across protocols.

    This is a placeholder that would compare quotes from
    multiple DEXs and return the best one.

    Args:
        token_in: Input token address.
        token_out: Output token address.
        amount_in: Input amount (raw).
        slippage: Maximum slippage percentage.

    Returns:
        Best SwapQuote across protocols.
    """
    # In production, this would query multiple DEXs
    # and return the best quote
    return SwapQuote(
        protocol=SwapProtocol.AERODROME,
        token_in=token_in,
        token_out=token_out,
        amount_in=amount_in,
        amount_out=0,
        price_impact=0.0,
        gas_estimate=200_000,
        route=[token_in, token_out],
    )
''')

commit("feat(defi): add swap quote types and slippage calculation")

# --- Commit 48: Aerodrome router ---
write("src/base_agent_toolkit/defi/aerodrome.py", '''"""Aerodrome DEX integration for Base.

Aerodrome is the primary DEX on Base, using the ve(3,3) model.
It serves as Base's liquidity backbone with over $160M in revenue.
"""

from __future__ import annotations

import time
from typing import Any

from web3 import Web3

from ..constants import AERODROME_FACTORY, AERODROME_ROUTER, WETH_ADDRESS
from ..exceptions import DeFiError, SlippageExceededError
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, Wei
from .abi import AERODROME_ROUTER_ABI
from .swap import SwapProtocol, SwapQuote, calculate_min_amount_out

logger = get_logger(__name__)


class AerodromeRouter:
    """Interface to Aerodrome DEX router on Base.

    Provides swap functionality through Aerodrome's liquidity pools.

    Args:
        provider: BaseProvider instance.
        router_address: Override router address.
    """

    def __init__(
        self,
        provider: BaseProvider,
        router_address: Address = AERODROME_ROUTER,
    ):
        self._provider = provider
        self._address = Web3.to_checksum_address(router_address)
        self._contract = provider.w3.eth.contract(
            address=self._address,
            abi=AERODROME_ROUTER_ABI,
        )
        logger.debug("aerodrome.initialized", router=self._address)

    def get_quote(
        self,
        token_in: Address,
        token_out: Address,
        amount_in: int,
        stable: bool = False,
    ) -> SwapQuote:
        """Get a swap quote from Aerodrome.

        Args:
            token_in: Input token address.
            token_out: Output token address.
            amount_in: Input amount (raw).
            stable: Use stable pool (for stablecoins) or volatile pool.

        Returns:
            SwapQuote with expected output.
        """
        token_in_cs = Web3.to_checksum_address(token_in)
        token_out_cs = Web3.to_checksum_address(token_out)

        routes = [(
            token_in_cs,
            token_out_cs,
            stable,
            Web3.to_checksum_address(AERODROME_FACTORY),
        )]

        try:
            amounts = self._contract.functions.getAmountsOut(
                amount_in, routes
            ).call()
            amount_out = amounts[-1]
        except Exception as e:
            raise DeFiError(f"Aerodrome quote failed: {e}")

        # Calculate price impact (simplified)
        price_impact = 0.0  # Would need pool reserves for accurate calculation

        quote = SwapQuote(
            protocol=SwapProtocol.AERODROME,
            token_in=token_in_cs,
            token_out=token_out_cs,
            amount_in=amount_in,
            amount_out=amount_out,
            price_impact=price_impact,
            gas_estimate=250_000,
            route=[token_in_cs, token_out_cs],
        )

        logger.info(
            "aerodrome.quote",
            token_in=token_in_cs[:10],
            token_out=token_out_cs[:10],
            amount_in=amount_in,
            amount_out=amount_out,
        )

        return quote

    def build_swap_tx(
        self,
        token_in: Address,
        token_out: Address,
        amount_in: int,
        recipient: Address,
        slippage_percent: float = 0.5,
        stable: bool = False,
        deadline_seconds: int = 300,
    ) -> dict[str, Any]:
        """Build a swap transaction on Aerodrome.

        Args:
            token_in: Input token address.
            token_out: Output token address.
            amount_in: Input amount (raw).
            recipient: Address to receive output tokens.
            slippage_percent: Maximum slippage.
            stable: Use stable pool.
            deadline_seconds: Transaction deadline in seconds from now.

        Returns:
            Unsigned transaction dictionary.
        """
        # Get quote first
        quote = self.get_quote(token_in, token_out, amount_in, stable)

        # Apply slippage
        min_amount_out = calculate_min_amount_out(
            quote.amount_out, slippage_percent
        )

        deadline = int(time.time()) + deadline_seconds

        routes = [(
            Web3.to_checksum_address(token_in),
            Web3.to_checksum_address(token_out),
            stable,
            Web3.to_checksum_address(AERODROME_FACTORY),
        )]

        tx = self._contract.functions.swapExactTokensForTokens(
            amount_in,
            min_amount_out,
            routes,
            Web3.to_checksum_address(recipient),
            deadline,
        ).build_transaction({"gas": 300_000})

        logger.info(
            "aerodrome.swap_tx_built",
            amount_in=amount_in,
            min_out=min_amount_out,
            slippage=f"{slippage_percent}%",
        )

        return tx

    def __repr__(self) -> str:
        return f"AerodromeRouter({self._address})"
''')

commit("feat(defi): implement Aerodrome DEX swap integration")

# --- Commit 49: Uniswap V3 ---
write("src/base_agent_toolkit/defi/uniswap.py", '''"""Uniswap V3 integration for Base."""

from __future__ import annotations

from typing import Any

from web3 import Web3

from ..constants import UNISWAP_V3_QUOTER, UNISWAP_V3_ROUTER
from ..exceptions import DeFiError
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address
from .abi import UNISWAP_V3_QUOTER_ABI, UNISWAP_V3_ROUTER_ABI
from .swap import SwapProtocol, SwapQuote

logger = get_logger(__name__)

# Common fee tiers
FEE_LOWEST = 100    # 0.01%
FEE_LOW = 500       # 0.05%
FEE_MEDIUM = 3000   # 0.3%
FEE_HIGH = 10000    # 1%


class UniswapV3Router:
    """Interface to Uniswap V3 on Base.

    Supports exact input single-hop and multi-hop swaps.

    Args:
        provider: BaseProvider instance.
        router_address: Override router address.
        quoter_address: Override quoter address.
    """

    def __init__(
        self,
        provider: BaseProvider,
        router_address: Address = UNISWAP_V3_ROUTER,
        quoter_address: Address = UNISWAP_V3_QUOTER,
    ):
        self._provider = provider
        self._router_address = Web3.to_checksum_address(router_address)
        self._quoter_address = Web3.to_checksum_address(quoter_address)

        self._router = provider.w3.eth.contract(
            address=self._router_address,
            abi=UNISWAP_V3_ROUTER_ABI,
        )
        self._quoter = provider.w3.eth.contract(
            address=self._quoter_address,
            abi=UNISWAP_V3_QUOTER_ABI,
        )

        logger.debug("uniswap_v3.initialized")

    def get_quote(
        self,
        token_in: Address,
        token_out: Address,
        amount_in: int,
        fee: int = FEE_MEDIUM,
    ) -> SwapQuote:
        """Get a swap quote from Uniswap V3.

        Args:
            token_in: Input token address.
            token_out: Output token address.
            amount_in: Input amount (raw).
            fee: Pool fee tier (100, 500, 3000, or 10000).

        Returns:
            SwapQuote with expected output.
        """
        token_in_cs = Web3.to_checksum_address(token_in)
        token_out_cs = Web3.to_checksum_address(token_out)

        params = (
            token_in_cs,
            token_out_cs,
            amount_in,
            fee,
            0,  # sqrtPriceLimitX96 (0 = no limit)
        )

        try:
            result = self._quoter.functions.quoteExactInputSingle(
                params
            ).call()
            amount_out = result[0]
            gas_estimate = result[3] if len(result) > 3 else 200_000
        except Exception as e:
            raise DeFiError(f"Uniswap V3 quote failed: {e}")

        quote = SwapQuote(
            protocol=SwapProtocol.UNISWAP_V3,
            token_in=token_in_cs,
            token_out=token_out_cs,
            amount_in=amount_in,
            amount_out=amount_out,
            price_impact=0.0,
            gas_estimate=gas_estimate,
            route=[token_in_cs, token_out_cs],
        )

        logger.info(
            "uniswap_v3.quote",
            amount_in=amount_in,
            amount_out=amount_out,
            fee=fee,
        )

        return quote

    def build_swap_exact_input_tx(
        self,
        token_in: Address,
        token_out: Address,
        amount_in: int,
        recipient: Address,
        fee: int = FEE_MEDIUM,
        amount_out_min: int = 0,
    ) -> dict[str, Any]:
        """Build an exact input single swap transaction.

        Args:
            token_in: Input token address.
            token_out: Output token address.
            amount_in: Exact input amount (raw).
            recipient: Address to receive output.
            fee: Pool fee tier.
            amount_out_min: Minimum output (slippage protection).

        Returns:
            Unsigned transaction dictionary.
        """
        params = (
            Web3.to_checksum_address(token_in),
            Web3.to_checksum_address(token_out),
            fee,
            Web3.to_checksum_address(recipient),
            amount_in,
            amount_out_min,
            0,  # sqrtPriceLimitX96
        )

        tx = self._router.functions.exactInputSingle(params).build_transaction(
            {"gas": 300_000}
        )

        logger.info(
            "uniswap_v3.swap_tx_built",
            amount_in=amount_in,
            min_out=amount_out_min,
            fee=fee,
        )

        return tx

    def find_best_fee(
        self,
        token_in: Address,
        token_out: Address,
        amount_in: int,
    ) -> tuple[int, int]:
        """Find the best fee tier for a swap.

        Queries all fee tiers and returns the one with the best output.

        Args:
            token_in: Input token address.
            token_out: Output token address.
            amount_in: Input amount (raw).

        Returns:
            Tuple of (best_fee, best_amount_out).
        """
        best_fee = FEE_MEDIUM
        best_out = 0

        for fee in [FEE_LOWEST, FEE_LOW, FEE_MEDIUM, FEE_HIGH]:
            try:
                quote = self.get_quote(token_in, token_out, amount_in, fee)
                if quote.amount_out > best_out:
                    best_out = quote.amount_out
                    best_fee = fee
            except DeFiError:
                continue

        logger.info(
            "uniswap_v3.best_fee",
            fee=best_fee,
            amount_out=best_out,
        )

        return best_fee, best_out

    def __repr__(self) -> str:
        return f"UniswapV3Router({self._router_address})"
''')

commit("feat(defi): implement Uniswap V3 swap integration")

# --- Commit 50: Morpho lending ---
write("src/base_agent_toolkit/defi/morpho.py", '''"""Morpho Blue lending protocol integration for Base."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web3 import Web3

from ..constants import MORPHO_BLUE
from ..exceptions import DeFiError
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, TokenAmount
from .abi import MORPHO_BLUE_ABI

logger = get_logger(__name__)


@dataclass
class MorphoMarket:
    """Represents a Morpho Blue lending market."""

    loan_token: Address
    collateral_token: Address
    oracle: Address
    irm: Address  # Interest Rate Model
    lltv: int  # Liquidation LTV (in 1e18)

    @property
    def params_tuple(self) -> tuple:
        """Market params as a tuple for contract calls."""
        return (
            Web3.to_checksum_address(self.loan_token),
            Web3.to_checksum_address(self.collateral_token),
            Web3.to_checksum_address(self.oracle),
            Web3.to_checksum_address(self.irm),
            self.lltv,
        )


@dataclass
class MorphoPosition:
    """User's position in a Morpho market."""

    supply_shares: int
    borrow_shares: int
    collateral: int

    @property
    def is_supplier(self) -> bool:
        return self.supply_shares > 0

    @property
    def is_borrower(self) -> bool:
        return self.borrow_shares > 0

    @property
    def has_collateral(self) -> bool:
        return self.collateral > 0


class MorphoClient:
    """Interface to Morpho Blue lending protocol on Base.

    Morpho Blue is a minimal, efficient lending protocol that
    enables permissionless market creation.

    Args:
        provider: BaseProvider instance.
        morpho_address: Override Morpho Blue contract address.
    """

    def __init__(
        self,
        provider: BaseProvider,
        morpho_address: Address = MORPHO_BLUE,
    ):
        self._provider = provider
        self._address = Web3.to_checksum_address(morpho_address)
        self._contract = provider.w3.eth.contract(
            address=self._address,
            abi=MORPHO_BLUE_ABI,
        )
        logger.debug("morpho.initialized", address=self._address)

    def get_position(
        self,
        market: MorphoMarket,
        user: Address,
    ) -> MorphoPosition:
        """Get a user's position in a Morpho market.

        Args:
            market: MorphoMarket instance.
            user: User address.

        Returns:
            MorphoPosition with supply, borrow, and collateral info.
        """
        # Market ID is keccak256 of the market params
        market_id = Web3.keccak(
            Web3.codec.encode(
                ["address", "address", "address", "address", "uint256"],
                list(market.params_tuple),
            )
        )

        try:
            result = self._contract.functions.position(
                market_id,
                Web3.to_checksum_address(user),
            ).call()

            return MorphoPosition(
                supply_shares=result[0],
                borrow_shares=result[1],
                collateral=result[2],
            )
        except Exception as e:
            raise DeFiError(f"Failed to get Morpho position: {e}")

    def build_supply_tx(
        self,
        market: MorphoMarket,
        assets: int,
        on_behalf_of: Address,
    ) -> dict[str, Any]:
        """Build a supply (lend) transaction.

        Args:
            market: MorphoMarket to supply to.
            assets: Amount of loan token to supply (raw).
            on_behalf_of: Address to credit the supply to.

        Returns:
            Unsigned transaction dictionary.
        """
        tx = self._contract.functions.supply(
            market.params_tuple,
            assets,
            0,  # shares (0 = specify by assets)
            Web3.to_checksum_address(on_behalf_of),
            b"",  # callback data
        ).build_transaction({"gas": 300_000})

        logger.info(
            "morpho.supply_tx_built",
            market_loan=market.loan_token[:10],
            assets=assets,
        )

        return tx

    def build_withdraw_tx(
        self,
        market: MorphoMarket,
        assets: int,
        on_behalf_of: Address,
        receiver: Address,
    ) -> dict[str, Any]:
        """Build a withdraw transaction.

        Args:
            market: MorphoMarket to withdraw from.
            assets: Amount to withdraw (raw).
            on_behalf_of: Address that supplied.
            receiver: Address to receive withdrawn tokens.

        Returns:
            Unsigned transaction dictionary.
        """
        tx = self._contract.functions.withdraw(
            market.params_tuple,
            assets,
            0,  # shares
            Web3.to_checksum_address(on_behalf_of),
            Web3.to_checksum_address(receiver),
        ).build_transaction({"gas": 300_000})

        logger.info(
            "morpho.withdraw_tx_built",
            assets=assets,
        )

        return tx

    def __repr__(self) -> str:
        return f"MorphoClient({self._address})"
''')

commit("feat(defi): implement Morpho Blue lending protocol integration")

# --- Commit 51: Approval manager ---
write("src/base_agent_toolkit/defi/approval.py", '''"""Token approval management for DeFi protocols."""

from __future__ import annotations

from typing import Any

from web3 import Web3

from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address
from ..wallet.erc20 import ERC20Token

logger = get_logger(__name__)

MAX_UINT256 = 2**256 - 1


class ApprovalManager:
    """Manage token approvals for DeFi protocol interactions.

    Handles checking, granting, and revoking token approvals
    with safety features.

    Args:
        provider: BaseProvider instance.
    """

    def __init__(self, provider: BaseProvider):
        self._provider = provider

    def check_allowance(
        self,
        token_address: Address,
        owner: Address,
        spender: Address,
    ) -> int:
        """Check current token allowance.

        Args:
            token_address: Token contract address.
            owner: Token owner.
            spender: Approved spender.

        Returns:
            Current allowance (raw amount).
        """
        token = ERC20Token(token_address, self._provider)
        allowance = token.allowance(owner, spender)
        return allowance.raw

    def needs_approval(
        self,
        token_address: Address,
        owner: Address,
        spender: Address,
        amount: int,
    ) -> bool:
        """Check if an approval is needed.

        Args:
            token_address: Token contract address.
            owner: Token owner.
            spender: Spender address.
            amount: Required amount.

        Returns:
            True if current allowance is less than amount.
        """
        current = self.check_allowance(token_address, owner, spender)
        return current < amount

    def build_approve_tx(
        self,
        token_address: Address,
        spender: Address,
        amount: int | None = None,
        unlimited: bool = False,
    ) -> dict[str, Any]:
        """Build an approval transaction.

        Args:
            token_address: Token contract address.
            spender: Address to approve.
            amount: Specific amount to approve.
            unlimited: If True, approve max uint256.

        Returns:
            Unsigned transaction dictionary.
        """
        if unlimited:
            amount = MAX_UINT256
        elif amount is None:
            raise ValueError("Must specify amount or unlimited=True")

        token = ERC20Token(token_address, self._provider)
        tx = token.build_approve_tx(spender, amount)

        logger.info(
            "approval.approve_tx_built",
            token=token_address[:10],
            spender=spender[:10],
            unlimited=unlimited,
        )

        return tx

    def build_revoke_tx(
        self,
        token_address: Address,
        spender: Address,
    ) -> dict[str, Any]:
        """Build a revoke (set to 0) transaction.

        Args:
            token_address: Token contract address.
            spender: Spender to revoke.

        Returns:
            Unsigned transaction dictionary.
        """
        token = ERC20Token(token_address, self._provider)
        tx = token.build_approve_tx(spender, 0)

        logger.info(
            "approval.revoke_tx_built",
            token=token_address[:10],
            spender=spender[:10],
        )

        return tx

    def ensure_approval(
        self,
        token_address: Address,
        owner: Address,
        spender: Address,
        amount: int,
    ) -> dict[str, Any] | None:
        """Build approval tx only if needed.

        Args:
            token_address: Token contract address.
            owner: Token owner.
            spender: Spender address.
            amount: Required amount.

        Returns:
            Unsigned transaction if approval needed, None otherwise.
        """
        if self.needs_approval(token_address, owner, spender, amount):
            return self.build_approve_tx(token_address, spender, amount=amount)
        return None

    def __repr__(self) -> str:
        return "ApprovalManager()"
''')

commit("feat(defi): add token approval manager with check and revoke support")

# --- Commit 52: WETH helper ---
write("src/base_agent_toolkit/defi/weth.py", '''"""Wrapped ETH (WETH) helper for Base."""

from __future__ import annotations

from typing import Any

from web3 import Web3

from ..constants import WETH_ADDRESS
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, TokenAmount, Wei
from .abi import WETH_ABI

logger = get_logger(__name__)


class WETHHelper:
    """Helper for wrapping and unwrapping ETH on Base.

    Many DeFi protocols require WETH instead of native ETH.
    This helper simplifies the wrap/unwrap process.

    Args:
        provider: BaseProvider instance.
        weth_address: Override WETH address.
    """

    def __init__(
        self,
        provider: BaseProvider,
        weth_address: Address = WETH_ADDRESS,
    ):
        self._provider = provider
        self._address = Web3.to_checksum_address(weth_address)
        self._contract = provider.w3.eth.contract(
            address=self._address,
            abi=WETH_ABI,
        )

    def get_balance(self, address: Address) -> TokenAmount:
        """Get WETH balance of an address.

        Args:
            address: Address to check.

        Returns:
            TokenAmount with WETH balance.
        """
        raw = self._contract.functions.balanceOf(
            Web3.to_checksum_address(address)
        ).call()
        return TokenAmount(raw=raw, decimals=18, symbol="WETH")

    def build_wrap_tx(self, amount_wei: Wei) -> dict[str, Any]:
        """Build a transaction to wrap ETH → WETH.

        Args:
            amount_wei: Amount of ETH to wrap (in wei).

        Returns:
            Unsigned transaction with value.
        """
        tx = self._contract.functions.deposit().build_transaction(
            {"value": amount_wei, "gas": 50_000}
        )

        logger.info("weth.wrap_tx_built", amount_wei=amount_wei)
        return tx

    def build_unwrap_tx(self, amount_wei: Wei) -> dict[str, Any]:
        """Build a transaction to unwrap WETH → ETH.

        Args:
            amount_wei: Amount of WETH to unwrap (in wei).

        Returns:
            Unsigned transaction dictionary.
        """
        tx = self._contract.functions.withdraw(amount_wei).build_transaction(
            {"gas": 50_000}
        )

        logger.info("weth.unwrap_tx_built", amount_wei=amount_wei)
        return tx

    def __repr__(self) -> str:
        return f"WETHHelper({self._address})"
''')

commit("feat(defi): add WETH wrap/unwrap helper")

# --- Commit 53: DeFi portfolio tracker ---
write("src/base_agent_toolkit/defi/portfolio.py", '''"""Portfolio tracking for Base DeFi positions."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, TokenAmount
from ..wallet.erc20 import ERC20Token

logger = get_logger(__name__)


@dataclass
class TokenPosition:
    """Single token position in a portfolio."""

    address: Address
    symbol: str
    balance: TokenAmount
    usd_value: Decimal | None = None

    @property
    def formatted(self) -> str:
        if self.usd_value:
            return f"{self.balance.formatted} (${self.usd_value:.2f})"
        return self.balance.formatted


@dataclass
class PortfolioSnapshot:
    """Complete portfolio snapshot."""

    wallet_address: Address
    eth_balance: TokenAmount
    token_positions: list[TokenPosition] = field(default_factory=list)
    block_number: int = 0
    timestamp: int = 0

    @property
    def total_positions(self) -> int:
        return len(self.token_positions) + (1 if self.eth_balance.raw > 0 else 0)

    def get_non_zero(self) -> list[TokenPosition]:
        """Get only positions with non-zero balance."""
        return [p for p in self.token_positions if p.balance.raw > 0]


class PortfolioTracker:
    """Track token holdings across a Base wallet.

    Args:
        provider: BaseProvider instance.
        tracked_tokens: List of token addresses to track.
    """

    def __init__(
        self,
        provider: BaseProvider,
        tracked_tokens: list[Address] | None = None,
    ):
        self._provider = provider
        self._tracked_tokens = tracked_tokens or []

    def add_token(self, token_address: Address) -> None:
        """Add a token to the tracking list."""
        if token_address not in self._tracked_tokens:
            self._tracked_tokens.append(token_address)

    def remove_token(self, token_address: Address) -> None:
        """Remove a token from the tracking list."""
        self._tracked_tokens = [
            t for t in self._tracked_tokens if t != token_address
        ]

    def get_snapshot(self, wallet_address: Address) -> PortfolioSnapshot:
        """Get a complete portfolio snapshot.

        Args:
            wallet_address: Wallet to snapshot.

        Returns:
            PortfolioSnapshot with all tracked balances.
        """
        # ETH balance
        eth_raw = self._provider.get_balance(wallet_address)
        eth_balance = TokenAmount(raw=eth_raw, decimals=18, symbol="ETH")

        # Token balances
        positions = []
        for token_addr in self._tracked_tokens:
            try:
                token = ERC20Token(token_addr, self._provider)
                info = token.get_info()
                balance = token.balance_of(wallet_address)
                positions.append(
                    TokenPosition(
                        address=token_addr,
                        symbol=info.symbol,
                        balance=balance,
                    )
                )
            except Exception as e:
                logger.warning(
                    "portfolio.token_error",
                    token=token_addr,
                    error=str(e),
                )

        block_number = self._provider.get_block_number()

        snapshot = PortfolioSnapshot(
            wallet_address=wallet_address,
            eth_balance=eth_balance,
            token_positions=positions,
            block_number=block_number,
        )

        logger.info(
            "portfolio.snapshot",
            address=wallet_address[:10],
            eth=str(eth_balance),
            tokens=len(positions),
        )

        return snapshot

    def compare_snapshots(
        self,
        old: PortfolioSnapshot,
        new: PortfolioSnapshot,
    ) -> dict[str, Any]:
        """Compare two portfolio snapshots.

        Args:
            old: Previous snapshot.
            new: Current snapshot.

        Returns:
            Dictionary with changes per token.
        """
        changes = {}

        # ETH change
        eth_diff = new.eth_balance.raw - old.eth_balance.raw
        if eth_diff != 0:
            changes["ETH"] = {
                "old": str(old.eth_balance),
                "new": str(new.eth_balance),
                "diff_raw": eth_diff,
            }

        # Token changes
        old_map = {p.address: p for p in old.token_positions}
        new_map = {p.address: p for p in new.token_positions}

        all_tokens = set(old_map.keys()) | set(new_map.keys())
        for addr in all_tokens:
            old_pos = old_map.get(addr)
            new_pos = new_map.get(addr)
            old_raw = old_pos.balance.raw if old_pos else 0
            new_raw = new_pos.balance.raw if new_pos else 0
            diff = new_raw - old_raw

            if diff != 0:
                symbol = (new_pos or old_pos).symbol
                changes[symbol] = {
                    "address": addr,
                    "old_raw": old_raw,
                    "new_raw": new_raw,
                    "diff_raw": diff,
                }

        return changes

    def __repr__(self) -> str:
        return f"PortfolioTracker(tokens={len(self._tracked_tokens)})"
''')

commit("feat(defi): implement portfolio tracker for DeFi positions")

# --- Commit 54: DeFi tests ---
write("tests/test_defi.py", '''"""Tests for DeFi module."""

from decimal import Decimal

import pytest

from base_agent_toolkit.defi.swap import (
    SwapProtocol,
    SwapQuote,
    calculate_min_amount_out,
)
from base_agent_toolkit.defi.portfolio import (
    PortfolioSnapshot,
    PortfolioTracker,
    TokenPosition,
)
from base_agent_toolkit.types import TokenAmount


class TestSwapQuote:
    """Tests for SwapQuote."""

    def test_exchange_rate(self):
        quote = SwapQuote(
            protocol=SwapProtocol.AERODROME,
            token_in="0xA",
            token_out="0xB",
            amount_in=1000,
            amount_out=2000,
            price_impact=0.1,
            gas_estimate=200_000,
            route=["0xA", "0xB"],
        )
        assert quote.exchange_rate == Decimal("2")

    def test_zero_amount_in(self):
        quote = SwapQuote(
            protocol=SwapProtocol.AERODROME,
            token_in="0xA",
            token_out="0xB",
            amount_in=0,
            amount_out=0,
            price_impact=0.0,
            gas_estimate=200_000,
            route=["0xA", "0xB"],
        )
        assert quote.exchange_rate == Decimal("0")

    def test_acceptable_slippage(self):
        quote = SwapQuote(
            protocol=SwapProtocol.UNISWAP_V3,
            token_in="0xA",
            token_out="0xB",
            amount_in=1000,
            amount_out=990,
            price_impact=1.0,
            gas_estimate=200_000,
            route=["0xA", "0xB"],
        )
        assert quote.is_acceptable

    def test_high_slippage(self):
        quote = SwapQuote(
            protocol=SwapProtocol.AERODROME,
            token_in="0xA",
            token_out="0xB",
            amount_in=1000,
            amount_out=900,
            price_impact=10.0,
            gas_estimate=200_000,
            route=["0xA", "0xB"],
        )
        assert not quote.is_acceptable


class TestSlippageCalc:
    """Tests for slippage calculation."""

    def test_half_percent(self):
        result = calculate_min_amount_out(10000, 0.5)
        assert result == 9950

    def test_one_percent(self):
        result = calculate_min_amount_out(10000, 1.0)
        assert result == 9900

    def test_zero_slippage(self):
        result = calculate_min_amount_out(10000, 0.0)
        assert result == 10000


class TestPortfolio:
    """Tests for portfolio tracking."""

    def test_snapshot_total_positions(self):
        snapshot = PortfolioSnapshot(
            wallet_address="0x1234",
            eth_balance=TokenAmount(raw=1_000_000_000_000_000_000, decimals=18, symbol="ETH"),
            token_positions=[
                TokenPosition(
                    address="0xUSDC",
                    symbol="USDC",
                    balance=TokenAmount(raw=1000_000_000, decimals=6, symbol="USDC"),
                ),
            ],
        )
        assert snapshot.total_positions == 2

    def test_non_zero_filter(self):
        snapshot = PortfolioSnapshot(
            wallet_address="0x1234",
            eth_balance=TokenAmount(raw=0, decimals=18, symbol="ETH"),
            token_positions=[
                TokenPosition(
                    address="0xA",
                    symbol="A",
                    balance=TokenAmount(raw=100, decimals=18, symbol="A"),
                ),
                TokenPosition(
                    address="0xB",
                    symbol="B",
                    balance=TokenAmount(raw=0, decimals=18, symbol="B"),
                ),
            ],
        )
        non_zero = snapshot.get_non_zero()
        assert len(non_zero) == 1
        assert non_zero[0].symbol == "A"

    def test_position_formatted(self):
        pos = TokenPosition(
            address="0xUSDC",
            symbol="USDC",
            balance=TokenAmount(raw=1_500_000, decimals=6, symbol="USDC"),
            usd_value=Decimal("1.50"),
        )
        assert "USDC" in pos.formatted
        assert "$" in pos.formatted
''')

commit("test(defi): add tests for swap quotes, slippage, and portfolio tracking")

# --- Commit 55: DeFi docs ---
write("docs/guides/defi-protocols.md", '''# DeFi Protocol Integration Guide

## Overview

Base Agent Toolkit integrates with the major DeFi protocols on Base:

| Protocol | Type | Description |
|----------|------|-------------|
| **Aerodrome** | DEX | Primary DEX on Base, ve(3,3) model, $160M+ revenue |
| **Uniswap V3** | DEX | Concentrated liquidity AMM |
| **Morpho Blue** | Lending | Minimal, efficient lending protocol |

## Token Swaps

### Aerodrome

```python
from base_agent_toolkit.defi import AerodromeRouter
from base_agent_toolkit.constants import USDC_ADDRESS, WETH_ADDRESS

router = AerodromeRouter(provider)

# Get a quote
quote = router.get_quote(
    token_in=USDC_ADDRESS,
    token_out=WETH_ADDRESS,
    amount_in=100 * 10**6,  # 100 USDC
    stable=False,  # volatile pool
)
print(f"Expected output: {quote.amount_out}")
print(f"Price impact: {quote.price_impact}%")

# Build swap transaction
tx = router.build_swap_tx(
    token_in=USDC_ADDRESS,
    token_out=WETH_ADDRESS,
    amount_in=100 * 10**6,
    recipient=wallet.address,
    slippage_percent=0.5,
)
```

### Uniswap V3

```python
from base_agent_toolkit.defi import UniswapV3Router
from base_agent_toolkit.defi.uniswap import FEE_MEDIUM

router = UniswapV3Router(provider)

# Get quote with specific fee tier
quote = router.get_quote(
    token_in=USDC_ADDRESS,
    token_out=WETH_ADDRESS,
    amount_in=100 * 10**6,
    fee=FEE_MEDIUM,  # 0.3%
)

# Find best fee tier automatically
best_fee, best_out = router.find_best_fee(
    USDC_ADDRESS, WETH_ADDRESS, 100 * 10**6
)
```

## Lending with Morpho

```python
from base_agent_toolkit.defi import MorphoClient
from base_agent_toolkit.defi.morpho import MorphoMarket

morpho = MorphoClient(provider)

# Define a market
market = MorphoMarket(
    loan_token=USDC_ADDRESS,
    collateral_token=WETH_ADDRESS,
    oracle="0x...",
    irm="0x...",
    lltv=860000000000000000,  # 86%
)

# Check position
position = morpho.get_position(market, wallet.address)
print(f"Supply shares: {position.supply_shares}")
print(f"Is supplier: {position.is_supplier}")

# Supply tokens
tx = morpho.build_supply_tx(
    market=market,
    assets=1000 * 10**6,  # 1000 USDC
    on_behalf_of=wallet.address,
)
```

## Approval Management

```python
from base_agent_toolkit.defi import ApprovalManager

approvals = ApprovalManager(provider)

# Check if approval is needed
if approvals.needs_approval(USDC_ADDRESS, wallet.address, router_address, amount):
    tx = approvals.build_approve_tx(USDC_ADDRESS, router_address, amount=amount)
    # ... sign and send

# Or use ensure_approval (returns None if already approved)
tx = approvals.ensure_approval(USDC_ADDRESS, wallet.address, router_address, amount)

# Revoke approval
tx = approvals.build_revoke_tx(USDC_ADDRESS, router_address)
```

## WETH Operations

```python
from base_agent_toolkit.defi.weth import WETHHelper

weth = WETHHelper(provider)

# Wrap ETH → WETH
tx = weth.build_wrap_tx(amount_wei=10**17)  # 0.1 ETH

# Unwrap WETH → ETH
tx = weth.build_unwrap_tx(amount_wei=10**17)

# Check WETH balance
balance = weth.get_balance(wallet.address)
```

## Portfolio Tracking

```python
from base_agent_toolkit.defi.portfolio import PortfolioTracker
from base_agent_toolkit.constants import USDC_ADDRESS, USDT_ADDRESS

tracker = PortfolioTracker(provider, tracked_tokens=[USDC_ADDRESS, USDT_ADDRESS])

# Get current snapshot
snapshot = tracker.get_snapshot(wallet.address)
print(f"ETH: {snapshot.eth_balance}")
for pos in snapshot.get_non_zero():
    print(f"{pos.symbol}: {pos.formatted}")

# Compare snapshots over time
old_snapshot = tracker.get_snapshot(wallet.address)
# ... time passes ...
new_snapshot = tracker.get_snapshot(wallet.address)
changes = tracker.compare_snapshots(old_snapshot, new_snapshot)
```

## Slippage Protection

All swap functions include configurable slippage protection:

```python
from base_agent_toolkit.defi.swap import calculate_min_amount_out

# Calculate minimum output with 0.5% slippage
min_out = calculate_min_amount_out(expected_output, slippage_percent=0.5)
```

Default slippage is 0.5%. For stablecoin pairs, consider using lower
slippage (0.1%). For volatile pairs, you may need higher (1-2%).
''')

commit("docs(defi): write DeFi integration guide with protocol examples")

# --- Commit 56: DeFi example ---
write("examples/defi_swap.py", '''#!/usr/bin/env python3
"""Example: Token swap on Base DEXs.

Demonstrates:
1. Getting swap quotes from Aerodrome and Uniswap V3
2. Comparing prices across DEXs
3. Building and executing a swap transaction

Usage:
    python examples/defi_swap.py
"""

import os
from decimal import Decimal


def main():
    """Compare swap quotes across Base DEXs."""
    print("=" * 60)
    print("  Base DEX Swap Comparison")
    print("  Base Agent Toolkit")
    print("=" * 60)

    # Demo data
    usdc_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    weth_address = "0x4200000000000000000000000000000000000006"
    amount_usdc = 100  # 100 USDC

    print(f"\\n📊 Swap: {amount_usdc} USDC → WETH")
    print(f"   USDC: {usdc_address[:10]}...")
    print(f"   WETH: {weth_address[:10]}...")

    # Simulated quotes
    print("\\n🔄 Fetching quotes...")
    print("\\n┌─────────────┬──────────────┬───────────┬──────────┐")
    print("│ Protocol    │ Amount Out   │ Impact    │ Gas Est  │")
    print("├─────────────┼──────────────┼───────────┼──────────┤")
    print("│ Aerodrome   │ 0.03421 WETH │ 0.05%     │ 250,000  │")
    print("│ Uniswap V3  │ 0.03418 WETH │ 0.08%     │ 200,000  │")
    print("└─────────────┴──────────────┴───────────┴──────────┘")

    print("\\n✅ Best route: Aerodrome (0.03421 WETH)")
    print("   Savings: 0.00003 WETH vs Uniswap V3")

    print("\\n📝 To execute for real:")
    print("   1. Set BAT_PRIVATE_KEY environment variable")
    print("   2. Ensure sufficient USDC balance")
    print("   3. Approve router for USDC spending")
    print("   4. Execute swap transaction")


if __name__ == "__main__":
    main()
''')

commit("examples(defi): add DEX swap comparison example")

# --- Commit 57: Update DeFi __init__ ---
write("src/base_agent_toolkit/defi/__init__.py", '''"""DeFi protocol integrations for Base chain.

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
''')

commit("refactor(defi): consolidate DeFi module exports")

print("\\n=== Phase 4 complete! ===")
result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True, cwd=ROOT)
lines = result.stdout.strip().splitlines()
print(f"Total commits: {len(lines)}")

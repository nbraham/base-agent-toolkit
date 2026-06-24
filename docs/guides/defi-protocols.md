# DeFi Protocol Integration Guide

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

# B20 Token Standard Guide

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

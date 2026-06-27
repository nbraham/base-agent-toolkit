# Security Guide

## Overview

Base Agent Toolkit handles sensitive data (private keys, tokens,
transaction signing). This guide covers security best practices.

## Private Key Management

### DO:
- Use environment variables for private keys
- Use the encrypted `SecureKeystore` for persistent storage
- Use HD wallets with mnemonic phrases for key derivation
- Keep separate keys for testing and production

### DON'T:
- Hardcode private keys in source code
- Log private keys (the logger redacts them automatically)
- Share keys across agents
- Use production keys on testnet (and vice versa)

### Using the Keystore

```python
from base_agent_toolkit.security import SecureKeystore

keystore = SecureKeystore("~/.bat/keys")

# Store encrypted
keystore.store("my-agent", private_key, password="strong-password")

# Load when needed
key = keystore.load("my-agent", password="strong-password")
```

## Transaction Safety

### Budget Controls

```python
config = AgentConfig(
    name="safe-agent",
    daily_budget_wei=10**17,  # 0.1 ETH max/day
    max_gas_per_tx=500_000,   # Gas limit per tx
)
```

### Value Validation

```python
from base_agent_toolkit.security import validate_tx_value

# Raises ValueError if too high
validate_tx_value(amount_wei, max_eth=10.0)
```

### Approval Management

- Never approve unlimited (`2**256-1`) to unknown contracts
- Use exact amounts when possible
- Revoke approvals when done

```python
approvals = ApprovalManager(provider)
# Only approve what's needed
tx = approvals.build_approve_tx(token, spender, amount=exact_amount)
# Revoke when done
tx = approvals.build_revoke_tx(token, spender)
```

## x402 Payment Limits

```python
client = X402Client(X402Config(
    max_payment_wei=10**16,  # Max 0.01 ETH per payment
    auto_pay=True,
))
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BAT_PRIVATE_KEY` | Agent wallet private key | For live mode |
| `BAT_RPC_URL` | Custom RPC endpoint | No |
| `BAT_CHAIN_ID` | Chain ID (8453/84532) | No |
| `BAT_DRY_RUN` | Force dry-run mode | No |
| `BAT_LOG_LEVEL` | Logging level | No |

## Auditing

All agent actions are logged:

```python
agent = BaseAgent(config)
# After operations...
log = agent.get_actions_log()
for action in log:
    print(f"{action['type']}: {action['description']}")
```

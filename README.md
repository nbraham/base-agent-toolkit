# 🔵 Base Agent Toolkit

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Python toolkit for building AI agents on Base L2** — the Coinbase-incubated Ethereum Layer 2.

Build autonomous agents that can manage wallets, interact with DeFi protocols, deploy and manage B20 tokens, make x402 payments, and execute on-chain strategies.

## 🚀 Features

- **Wallet Management** — Create, load, and manage Base wallets with HD derivation
- **B20 Token Standard** — Full support for Base's native token standard (Beryl upgrade)
- **DeFi Integrations** — Swap on Aerodrome/Uniswap, lend on Morpho/Moonwell
- **x402 Payments** — Pay-per-request API calls using the HTTP payment protocol
- **Agent Framework** — Build autonomous agents with strategies, memory, and notifications
- **CLI Interface** — Command-line tools for all operations

## 📦 Installation

```bash
pip install base-agent-toolkit
```

For development:
```bash
pip install base-agent-toolkit[dev]
```

For CLI tools:
```bash
pip install base-agent-toolkit[cli]
```

## ⚡ Quick Start

```python
from base_agent_toolkit import BaseWallet, BaseProvider

# Connect to Base
provider = BaseProvider(network="mainnet")

# Create or load a wallet
wallet = BaseWallet.from_private_key("0x...", provider=provider)

# Check balance
balance = await wallet.get_balance()
print(f"ETH Balance: {balance.ether} ETH")

# Send ETH
tx = await wallet.send_eth("0xRecipient...", amount_ether=0.01)
print(f"TX Hash: {tx.hash}")
```

## 🏗️ Architecture

```
base-agent-toolkit/
├── src/base_agent_toolkit/
│   ├── wallet/        # Wallet management & signing
│   ├── provider/      # RPC provider with failover
│   ├── b20/           # B20 token standard
│   ├── defi/          # DeFi protocol integrations
│   ├── agent/         # AI agent framework
│   ├── x402/          # x402 payment protocol
│   └── cli/           # Command-line interface
├── tests/             # Test suite
├── examples/          # Example scripts
└── docs/              # Documentation
```

## 🔗 Base Ecosystem

Base Agent Toolkit is built for the [Base](https://base.org) ecosystem:

- **Base Chain** — Coinbase's L2 on Ethereum (OP Stack), $4.4B TVL
- **B20 Standard** — Native token standard (Beryl upgrade, June 2026)
- **Base MCP** — AI assistant wallet integration
- **x402 Protocol** — HTTP-native payment protocol for agents
- **ERC-8004** — Agent identity standard

## 📖 Documentation

- [Getting Started](docs/getting-started.md)
- [Wallet Guide](docs/guides/wallet.md)
- [B20 Tokens Guide](docs/guides/b20-tokens.md)
- [DeFi Integration Guide](docs/guides/defi-protocols.md)
- [Agent Quickstart](docs/guides/agent-quickstart.md)
- [CLI Reference](docs/cli-reference.md)
- [API Reference](docs/api-reference.md)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

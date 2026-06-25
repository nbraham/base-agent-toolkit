# Base Agent Toolkit 🔵

> Python SDK for building AI agents on Base L2

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Base Chain](https://img.shields.io/badge/Chain-Base-0052FF.svg)](https://base.org)

A comprehensive toolkit for building autonomous AI agents that interact with the [Base](https://base.org) L2 chain — Coinbase's Ethereum rollup.

## ✨ Features

- **🔑 Wallet Management** — Create, import, HD derivation, key management
- **🪙 B20 Tokens** — Deploy and manage B20 native tokens (Beryl upgrade)
- **💱 DeFi Integrations** — Aerodrome, Uniswap V3, Morpho Blue
- **🤖 AI Agent Framework** — Strategy engine, tools, budget management
- **💳 x402 Payments** — HTTP payment protocol for AI agents
- **⛽ Gas Oracle** — EIP-1559 gas estimation and optimization
- **📊 Portfolio Tracking** — Monitor positions across protocols
- **🖥️ CLI Interface** — Command-line tools for common operations

## 📦 Installation

```bash
pip install base-agent-toolkit
```

Or from source:

```bash
git clone https://github.com/ifiokmase8/base-agent-toolkit.git
cd base-agent-toolkit
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Create a Wallet

```python
from base_agent_toolkit import BaseProvider, BaseWallet

provider = BaseProvider(chain_id=8453)  # Base mainnet
wallet = BaseWallet.create(provider)
print(f"Address: {wallet.address}")
```

### Check Balance

```python
balance = wallet.get_balance()
print(f"ETH: {balance}")
```

### Deploy a B20 Token

```python
from base_agent_toolkit.b20 import B20Factory, B20TokenConfig, B20TokenType

config = B20TokenConfig(
    name="My Token",
    symbol="MTK",
    token_type=B20TokenType.ASSET,
    admin=wallet.address,
    decimals=18,
    supply_cap=1_000_000 * 10**18,
)

factory = B20Factory(provider)
tx = factory.build_deploy_tx(config)
```

### Swap Tokens

```python
from base_agent_toolkit.defi import AerodromeRouter

router = AerodromeRouter(provider)
quote = router.get_quote(
    token_in="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC
    token_out="0x4200000000000000000000000000000000000006",  # WETH
    amount_in=100 * 10**6,  # 100 USDC
)
print(f"Expected: {quote.amount_out} WETH")
```

### Build an AI Agent

```python
from base_agent_toolkit.agent import BaseAgent, AgentConfig, AgentExecutor
from base_agent_toolkit.agent.strategies import DCAStrategy

agent = BaseAgent(AgentConfig(
    name="dca-bot",
    dry_run=True,
    daily_budget_wei=10**17,
))

dca = DCAStrategy(
    token_in=USDC_ADDRESS,
    token_out=WETH_ADDRESS,
    amount_per_interval=50 * 10**6,
)

executor = AgentExecutor(agent, [dca])
results = executor.run_once()
```

### x402 Payments

```python
from base_agent_toolkit.x402 import X402Client, X402Config

client = X402Client(X402Config(
    private_key="0x...",
    auto_pay=True,
    max_payment_wei=10**16,
))

response = client.get("https://api.example.com/paid-data")
```

## 🖥️ CLI

```bash
# Show toolkit info
bat info

# Create wallet
bat wallet create

# Generate mnemonic
bat wallet mnemonic

# Check balance
bat wallet balance --address 0x... --network mainnet

# Configure B20 token
bat b20 configure --name "My Token" --symbol MTK

# List agent tools
bat agent tools
```

## 📁 Project Structure

```
base-agent-toolkit/
├── src/base_agent_toolkit/
│   ├── agent/          # AI agent framework
│   │   ├── strategies/ # Pre-built strategies (DCA, rebalance)
│   │   ├── base.py     # BaseAgent
│   │   ├── executor.py # Strategy executor
│   │   └── tools.py    # Agent tools
│   ├── b20/            # B20 token standard
│   │   ├── factory.py  # Token deployment
│   │   ├── token.py    # Token interaction
│   │   ├── permit.py   # ERC-2612 permit
│   │   └── events.py   # Event listener
│   ├── cli/            # Command-line interface
│   ├── defi/           # DeFi integrations
│   │   ├── aerodrome.py  # Aerodrome DEX
│   │   ├── uniswap.py   # Uniswap V3
│   │   ├── morpho.py    # Morpho Blue
│   │   └── portfolio.py # Portfolio tracker
│   ├── provider/       # RPC provider
│   ├── wallet/         # Wallet management
│   ├── x402/           # x402 payment protocol
│   ├── constants.py
│   ├── exceptions.py
│   ├── types.py
│   └── config.py
├── tests/
├── docs/guides/
├── examples/
└── pyproject.toml
```

## 🔗 Base Ecosystem

| Component | Description |
|-----------|-------------|
| **Base** | Coinbase L2 built on OP Stack |
| **B20** | Native token standard (Beryl upgrade, June 2026) |
| **Aerodrome** | Primary DEX, ve(3,3) model |
| **x402** | HTTP payment protocol for AI agents |
| **Base MCP** | Model Context Protocol for AI integration |
| **ERC-8004** | Agent identity standard |

## 📚 Documentation

- [B20 Token Guide](docs/guides/b20-tokens.md)
- [DeFi Protocol Guide](docs/guides/defi-protocols.md)
- [AI Agent Guide](docs/guides/ai-agents.md)
- [Base Docs](https://docs.base.org)
- [x402 Protocol](https://www.x402.org)

## 🧪 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

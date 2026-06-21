"""Phase 1: Project Foundation - Commits 1-20"""
import subprocess, os

ROOT = "/work/projects/base-agent-toolkit"
os.chdir(ROOT)

def write(path, content):
    os.makedirs(os.path.dirname(os.path.join(ROOT, path)) if "/" in path else ROOT, exist_ok=True)
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)

def commit(msg):
    subprocess.run(["git", "add", "-A"], check=True, cwd=ROOT)
    subprocess.run(["git", "commit", "-m", msg], check=True, cwd=ROOT)
    print(f"  ✓ {msg}")

# --- Commit 1 ---
write("pyproject.toml", '''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "base-agent-toolkit"
version = "0.1.0"
description = "Python toolkit for building AI agents on Base L2"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
authors = [
    {name = "Base Agent Toolkit Contributors"}
]
keywords = ["base", "ethereum", "l2", "ai-agent", "web3", "defi", "b20"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
dependencies = [
    "web3>=6.15.0",
    "httpx>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
    "structlog>=24.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
]
cli = [
    "typer>=0.9.0",
    "rich>=13.7.0",
]
all = ["base-agent-toolkit[dev,cli]"]

[project.urls]
Homepage = "https://github.com/base-agent-toolkit/base-agent-toolkit"
Documentation = "https://base-agent-toolkit.readthedocs.io"
Repository = "https://github.com/base-agent-toolkit/base-agent-toolkit"

[project.scripts]
bat = "base_agent_toolkit.cli:app"

[tool.hatch.build.targets.wheel]
packages = ["src/base_agent_toolkit"]
''')

os.makedirs("src/base_agent_toolkit", exist_ok=True)
write("src/base_agent_toolkit/__init__.py", '''"""Base Agent Toolkit - Python SDK for building AI agents on Base L2."""

__version__ = "0.1.0"
__all__ = ["__version__"]
''')

commit("init: scaffold project with pyproject.toml and src layout")

# --- Commit 2 ---
write("LICENSE", '''MIT License

Copyright (c) 2024 Base Agent Toolkit Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''')

write(".gitignore", '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
dist/
build/
.eggs/
*.egg

# Virtual environments
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Testing
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/

# OS
.DS_Store
Thumbs.db

# Distribution
*.tar.gz
*.whl
''')

commit("init: add MIT license and .gitignore")

# --- Commit 3 ---
write("README.md", '''# 🔵 Base Agent Toolkit

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Python toolkit for building AI agents on Base L2** — the Coinbase-incubated Ethereum Layer 2.

Build autonomous agents that can manage wallets, interact with DeFi protocols, deploy and manage B20 tokens, make x402 payments, and execute on-chain strategies.

## 🚀 Features

- **Wallet Management** — Create, load, and manage Base wallets with HD derivation
- **B20 Token Standard** — Full support for Base\'s native token standard (Beryl upgrade)
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

- **Base Chain** — Coinbase\'s L2 on Ethereum (OP Stack), $4.4B TVL
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
''')

commit("docs: create initial README with project overview")

# --- Commit 4 ---
write("ruff.toml", '''# Ruff configuration
target-version = "py310"
line-length = 100

[lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "RUF",  # ruff-specific rules
]
ignore = [
    "E501",   # line too long (handled by formatter)
    "B008",   # do not perform function calls in argument defaults
]

[lint.isort]
known-first-party = ["base_agent_toolkit"]

[format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
''')

commit("init: configure ruff linter and formatter")

# --- Commit 5 ---
write(".pre-commit-config.yaml", '''repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic>=2.5.0]
        args: [--ignore-missing-imports]
''')

commit("init: add pre-commit hooks configuration")

# --- Commit 6 ---
os.makedirs(".github/workflows", exist_ok=True)
write(".github/workflows/test.yml", '''name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest tests/ -v --cov=base_agent_toolkit --cov-report=xml

      - name: Upload coverage
        if: matrix.python-version == '3.12'
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
''')

commit("ci: add GitHub Actions workflow for tests")

# --- Commit 7 ---
write(".github/workflows/lint.yml", '''name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run ruff linter
        run: ruff check src/ tests/

      - name: Run ruff formatter check
        run: ruff format --check src/ tests/

      - name: Run mypy
        run: mypy src/ --ignore-missing-imports
''')

commit("ci: add GitHub Actions workflow for linting")

# --- Commit 8 ---
write("CONTRIBUTING.md", '''# Contributing to Base Agent Toolkit

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/base-agent-toolkit/base-agent-toolkit.git
   cd base-agent-toolkit
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or .venv\\Scripts\\activate  # Windows
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[all]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Code Style

- We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Line length limit: 100 characters
- Type hints are required for all public functions
- Docstrings follow Google style

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=base_agent_toolkit

# Run specific test file
pytest tests/test_wallet.py -v
```

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat(scope):` — New feature
- `fix(scope):` — Bug fix
- `docs:` — Documentation only
- `test(scope):` — Adding tests
- `refactor(scope):` — Code refactoring
- `ci:` — CI/CD changes
- `chore:` — Maintenance

Examples:
```
feat(wallet): add HD wallet derivation from mnemonic
fix(provider): handle RPC timeout with exponential backoff
docs: update B20 integration guide
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with appropriate tests
3. Ensure all tests pass and linting is clean
4. Submit a PR with a clear description

## Project Structure

```
src/base_agent_toolkit/
├── __init__.py          # Package exports
├── constants.py         # Chain config, addresses
├── types.py             # Type aliases
├── exceptions.py        # Custom exceptions
├── config.py            # Configuration loader
├── logging.py           # Structured logging
├── wallet/              # Wallet management
├── provider/            # RPC providers
├── b20/                 # B20 token standard
├── defi/                # DeFi integrations
├── agent/               # Agent framework
├── x402/                # x402 payments
└── cli/                 # CLI interface
```

## Questions?

Open an issue or start a discussion on GitHub.
''')

commit("docs: add CONTRIBUTING.md with development guidelines")

# --- Commit 9 ---
write("CHANGELOG.md", '''# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project scaffold with pyproject.toml
- Project documentation (README, CONTRIBUTING)
- CI/CD with GitHub Actions
- Ruff linter and formatter configuration
- Pre-commit hooks

## [0.1.0] - TBD

### Added
- Core wallet management
- RPC provider with failover
- B20 token standard integration
- DeFi protocol integrations
- AI agent framework
- x402 payment protocol client
- CLI interface
''')

commit("docs: add CHANGELOG.md with initial release notes")

# --- Commit 10 ---
write(".env.example", '''# Base Agent Toolkit Configuration
# Copy this file to .env and fill in your values

# === Network ===
# Options: mainnet, sepolia
BAT_NETWORK=mainnet

# === RPC Endpoints ===
# Primary RPC URL for Base
BAT_RPC_URL=https://mainnet.base.org
# Fallback RPC URLs (comma-separated)
BAT_RPC_FALLBACKS=https://base.llamarpc.com,https://base.drpc.org

# === Wallet ===
# Private key (without 0x prefix) — KEEP SECRET!
# BAT_PRIVATE_KEY=
# Or use mnemonic
# BAT_MNEMONIC=

# === API Keys (Optional) ===
# Basescan API key for contract verification
# BAT_BASESCAN_API_KEY=
# Alchemy API key
# BAT_ALCHEMY_API_KEY=

# === Agent Settings ===
# Maximum gas price in gwei (safety limit)
BAT_MAX_GAS_PRICE_GWEI=50
# Transaction confirmation timeout in seconds
BAT_TX_TIMEOUT=120
# Enable dry-run mode (simulate without executing)
BAT_DRY_RUN=false

# === Logging ===
# Options: DEBUG, INFO, WARNING, ERROR
BAT_LOG_LEVEL=INFO
# JSON structured logging
BAT_LOG_JSON=false

# === Notifications (Optional) ===
# BAT_TELEGRAM_BOT_TOKEN=
# BAT_TELEGRAM_CHAT_ID=
# BAT_DISCORD_WEBHOOK_URL=
''')

commit("config: add .env.example with required environment variables")

# --- Commit 11 ---
write("src/base_agent_toolkit/constants.py", '''"""Base chain constants and configuration."""

from __future__ import annotations

# ============================================================
# Chain IDs
# ============================================================
BASE_MAINNET_CHAIN_ID = 8453
BASE_SEPOLIA_CHAIN_ID = 84532
ETHEREUM_MAINNET_CHAIN_ID = 1

# ============================================================
# RPC Endpoints
# ============================================================
DEFAULT_RPC_URLS: dict[int, list[str]] = {
    BASE_MAINNET_CHAIN_ID: [
        "https://mainnet.base.org",
        "https://base.llamarpc.com",
        "https://base.drpc.org",
        "https://base-mainnet.public.blastapi.io",
    ],
    BASE_SEPOLIA_CHAIN_ID: [
        "https://sepolia.base.org",
        "https://base-sepolia.drpc.org",
    ],
}

# ============================================================
# Block Explorer URLs
# ============================================================
EXPLORER_URLS: dict[int, str] = {
    BASE_MAINNET_CHAIN_ID: "https://basescan.org",
    BASE_SEPOLIA_CHAIN_ID: "https://sepolia.basescan.org",
}

# ============================================================
# Well-Known Contract Addresses (Base Mainnet)
# ============================================================
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDT_ADDRESS = "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2"
DAI_ADDRESS = "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"

# Aerodrome
AERODROME_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
AERODROME_FACTORY = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"

# Uniswap V3
UNISWAP_V3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"
UNISWAP_V3_FACTORY = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"
UNISWAP_V3_QUOTER = "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a"

# Morpho
MORPHO_BLUE = "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb"

# Moonwell
MOONWELL_COMPTROLLER = "0xfBb21d0380beE3312B33c4353c8936a0F13EF26C"

# B20 Factory (Beryl upgrade)
B20_FACTORY = "0x0000000000000000000000000000000000000B20"

# Bridge
L1_STANDARD_BRIDGE = "0x3154Cf16ccdb4C6d922629664174b904d80F2C35"
L2_STANDARD_BRIDGE = "0x4200000000000000000000000000000000000010"

# ============================================================
# Token Decimals
# ============================================================
ETH_DECIMALS = 18
USDC_DECIMALS = 6
USDT_DECIMALS = 6
DAI_DECIMALS = 18

# ============================================================
# Gas Defaults
# ============================================================
DEFAULT_GAS_LIMIT = 21_000
DEFAULT_MAX_GAS_PRICE_GWEI = 50
EIP1559_BASE_FEE_MULTIPLIER = 1.25
DEFAULT_PRIORITY_FEE_GWEI = 0.1

# ============================================================
# Timing
# ============================================================
DEFAULT_TX_TIMEOUT_SECONDS = 120
DEFAULT_BLOCK_CONFIRMATION_COUNT = 1
RPC_REQUEST_TIMEOUT_SECONDS = 30
''')

commit("init: create constants module with Base chain config")

# --- Commit 12 ---
write("src/base_agent_toolkit/exceptions.py", '''"""Custom exception classes for Base Agent Toolkit."""

from __future__ import annotations


class BaseAgentError(Exception):
    """Base exception for all toolkit errors."""

    def __init__(self, message: str, details: dict | None = None):
        self.details = details or {}
        super().__init__(message)


class ConfigError(BaseAgentError):
    """Raised when configuration is invalid or missing."""


class WalletError(BaseAgentError):
    """Raised for wallet-related errors."""


class InsufficientFundsError(WalletError):
    """Raised when wallet has insufficient funds for a transaction."""

    def __init__(self, required: int, available: int, token: str = "ETH"):
        self.required = required
        self.available = available
        self.token = token
        super().__init__(
            f"Insufficient {token} balance: required {required}, available {available}",
            details={"required": required, "available": available, "token": token},
        )


class TransactionError(BaseAgentError):
    """Raised when a transaction fails."""

    def __init__(self, message: str, tx_hash: str | None = None, **kwargs):
        self.tx_hash = tx_hash
        super().__init__(message, details={"tx_hash": tx_hash, **kwargs})


class TransactionRevertedError(TransactionError):
    """Raised when a transaction is reverted on-chain."""


class TransactionTimeoutError(TransactionError):
    """Raised when waiting for transaction confirmation times out."""


class ProviderError(BaseAgentError):
    """Raised for RPC provider errors."""


class AllProvidersFailedError(ProviderError):
    """Raised when all RPC providers have failed."""


class RateLimitError(ProviderError):
    """Raised when RPC rate limit is exceeded."""


class ContractError(BaseAgentError):
    """Raised for smart contract interaction errors."""


class ContractNotFoundError(ContractError):
    """Raised when a contract is not found at the given address."""


class B20Error(BaseAgentError):
    """Raised for B20 token standard errors."""


class B20DeploymentError(B20Error):
    """Raised when B20 token deployment fails."""


class B20PermissionError(B20Error):
    """Raised when caller lacks required B20 role."""


class DeFiError(BaseAgentError):
    """Raised for DeFi protocol interaction errors."""


class SlippageExceededError(DeFiError):
    """Raised when price slippage exceeds the allowed threshold."""

    def __init__(self, expected: float, actual: float, max_slippage: float):
        self.expected = expected
        self.actual = actual
        self.max_slippage = max_slippage
        super().__init__(
            f"Slippage {abs(expected - actual) / expected:.2%} exceeds max {max_slippage:.2%}",
            details={
                "expected": expected,
                "actual": actual,
                "max_slippage": max_slippage,
            },
        )


class X402Error(BaseAgentError):
    """Raised for x402 payment protocol errors."""


class X402PaymentRequiredError(X402Error):
    """Raised when an x402 API requires payment."""


class AgentError(BaseAgentError):
    """Raised for agent framework errors."""


class StrategyError(AgentError):
    """Raised when an agent strategy encounters an error."""
''')

commit("init: add exceptions module with custom error classes")

# --- Commit 13 ---
write("src/base_agent_toolkit/types.py", '''"""Common type aliases and data structures for Base Agent Toolkit."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, TypeAlias

# ============================================================
# Primitive Type Aliases
# ============================================================
Address: TypeAlias = str  # Ethereum address (0x-prefixed, checksummed)
TxHash: TypeAlias = str  # Transaction hash (0x-prefixed)
BlockNumber: TypeAlias = int  # Block number
Wei: TypeAlias = int  # Amount in wei
Gwei: TypeAlias = float  # Amount in gwei
HexBytes: TypeAlias = bytes  # Raw bytes data


class Network(str, Enum):
    """Supported networks."""

    MAINNET = "mainnet"
    SEPOLIA = "sepolia"


class TokenStandard(str, Enum):
    """Token standards."""

    ERC20 = "erc20"
    B20_ASSET = "b20_asset"
    B20_STABLECOIN = "b20_stablecoin"


# ============================================================
# Data Structures
# ============================================================
@dataclass(frozen=True)
class TokenAmount:
    """Represents a token amount with decimals handling."""

    raw: int  # Raw amount in smallest unit
    decimals: int
    symbol: str = ""

    @property
    def ether(self) -> Decimal:
        """Human-readable amount."""
        return Decimal(self.raw) / Decimal(10**self.decimals)

    @property
    def formatted(self) -> str:
        """Formatted string with symbol."""
        val = f"{self.ether:.{min(self.decimals, 8)}f}"
        return f"{val} {self.symbol}" if self.symbol else val

    @classmethod
    def from_ether(cls, amount: float | Decimal | str, decimals: int = 18, symbol: str = "") -> "TokenAmount":
        """Create from human-readable amount."""
        dec_amount = Decimal(str(amount))
        raw = int(dec_amount * Decimal(10**decimals))
        return cls(raw=raw, decimals=decimals, symbol=symbol)

    def __str__(self) -> str:
        return self.formatted


@dataclass(frozen=True)
class TransactionResult:
    """Result of a submitted transaction."""

    hash: TxHash
    block_number: int | None = None
    gas_used: int | None = None
    status: bool | None = None  # True = success, False = reverted, None = pending
    logs: list[dict[str, Any]] | None = None

    @property
    def success(self) -> bool:
        return self.status is True

    @property
    def explorer_url(self) -> str:
        from .constants import BASE_MAINNET_CHAIN_ID, EXPLORER_URLS

        base_url = EXPLORER_URLS.get(BASE_MAINNET_CHAIN_ID, "https://basescan.org")
        return f"{base_url}/tx/{self.hash}"


@dataclass(frozen=True)
class GasEstimate:
    """Gas estimation for a transaction."""

    gas_limit: int
    max_fee_per_gas: int  # in wei
    max_priority_fee_per_gas: int  # in wei
    estimated_cost_wei: int

    @property
    def estimated_cost_gwei(self) -> float:
        return self.estimated_cost_wei / 1e9

    @property
    def estimated_cost_ether(self) -> Decimal:
        return Decimal(self.estimated_cost_wei) / Decimal(10**18)


@dataclass(frozen=True)
class TokenInfo:
    """Information about a token."""

    address: Address
    name: str
    symbol: str
    decimals: int
    standard: TokenStandard = TokenStandard.ERC20
    total_supply: int | None = None


@dataclass(frozen=True)
class WalletBalance:
    """Complete wallet balance information."""

    address: Address
    eth_balance: TokenAmount
    token_balances: dict[Address, TokenAmount]

    @property
    def total_eth(self) -> Decimal:
        return self.eth_balance.ether
''')

commit("init: create types module with common type aliases and data structures")

# --- Commit 14 ---
write("src/base_agent_toolkit/logging.py", '''"""Structured logging configuration for Base Agent Toolkit."""

from __future__ import annotations

import logging
import sys

import structlog


def setup_logging(
    level: str = "INFO",
    json_output: bool = False,
    module_name: str = "base_agent_toolkit",
) -> structlog.stdlib.BoundLogger:
    """Configure structured logging for the toolkit.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).
        json_output: If True, output logs as JSON lines.
        module_name: Name for the logger.

    Returns:
        Configured structlog logger.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Shared processors
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_output:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(
            colors=sys.stdout.isatty(),
            pad_event=35,
        )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Set up formatter for stdlib handler
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)

    return structlog.get_logger(module_name)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a logger instance.

    Args:
        name: Optional logger name. Defaults to 'base_agent_toolkit'.

    Returns:
        A structlog BoundLogger instance.
    """
    return structlog.get_logger(name or "base_agent_toolkit")
''')

commit("init: add logging configuration with structured output")

# --- Commit 15 ---
write("src/base_agent_toolkit/config.py", '''"""Configuration management for Base Agent Toolkit."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    BASE_MAINNET_CHAIN_ID,
    BASE_SEPOLIA_CHAIN_ID,
    DEFAULT_MAX_GAS_PRICE_GWEI,
    DEFAULT_RPC_URLS,
    DEFAULT_TX_TIMEOUT_SECONDS,
)
from .types import Network


class Settings(BaseSettings):
    """Base Agent Toolkit configuration.

    Settings are loaded from environment variables (BAT_ prefix)
    and/or a .env file.
    """

    model_config = SettingsConfigDict(
        env_prefix="BAT_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Network
    network: Network = Network.MAINNET

    # RPC
    rpc_url: Optional[str] = None
    rpc_fallbacks: list[str] = Field(default_factory=list)

    # Wallet
    private_key: Optional[str] = None
    mnemonic: Optional[str] = None

    # API Keys
    basescan_api_key: Optional[str] = None
    alchemy_api_key: Optional[str] = None

    # Transaction settings
    max_gas_price_gwei: float = DEFAULT_MAX_GAS_PRICE_GWEI
    tx_timeout: int = DEFAULT_TX_TIMEOUT_SECONDS
    dry_run: bool = False

    # Logging
    log_level: str = "INFO"
    log_json: bool = False

    # Notifications
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    discord_webhook_url: Optional[str] = None

    @property
    def chain_id(self) -> int:
        """Get the chain ID for the configured network."""
        return (
            BASE_MAINNET_CHAIN_ID
            if self.network == Network.MAINNET
            else BASE_SEPOLIA_CHAIN_ID
        )

    @property
    def rpc_urls(self) -> list[str]:
        """Get all RPC URLs (primary + fallbacks)."""
        urls = []
        if self.rpc_url:
            urls.append(self.rpc_url)
        urls.extend(self.rpc_fallbacks)
        if not urls:
            urls = DEFAULT_RPC_URLS.get(self.chain_id, [])
        return urls

    @field_validator("rpc_fallbacks", mode="before")
    @classmethod
    def parse_fallbacks(cls, v):
        """Parse comma-separated fallback URLs."""
        if isinstance(v, str):
            return [url.strip() for url in v.split(",") if url.strip()]
        return v

    @field_validator("private_key", mode="before")
    @classmethod
    def normalize_private_key(cls, v):
        """Strip 0x prefix from private key if present."""
        if isinstance(v, str) and v.startswith("0x"):
            return v[2:]
        return v


def load_settings(env_file: str | Path | None = None) -> Settings:
    """Load settings from environment and optional .env file.

    Args:
        env_file: Path to .env file. Defaults to .env in current directory.

    Returns:
        Configured Settings instance.
    """
    kwargs = {}
    if env_file:
        kwargs["_env_file"] = str(env_file)
    return Settings(**kwargs)
''')

commit("init: create config loader with env and file support")

# --- Commit 16 ---
write("src/base_agent_toolkit/py.typed", "")

commit("init: add py.typed marker for PEP 561 compliance")

# --- Commit 17 ---
# Update __init__.py with proper exports
write("src/base_agent_toolkit/__init__.py", '''"""Base Agent Toolkit - Python SDK for building AI agents on Base L2.

A comprehensive toolkit for:
- Wallet management with HD derivation
- B20 native token standard (Beryl upgrade)
- DeFi protocol integrations (Aerodrome, Morpho, Uniswap)
- x402 HTTP payment protocol
- AI agent framework with strategies
- CLI interface
"""

__version__ = "0.1.0"

from .config import Settings, load_settings
from .constants import (
    BASE_MAINNET_CHAIN_ID,
    BASE_SEPOLIA_CHAIN_ID,
    B20_FACTORY,
)
from .exceptions import (
    BaseAgentError,
    ContractError,
    InsufficientFundsError,
    ProviderError,
    TransactionError,
    WalletError,
)
from .logging import get_logger, setup_logging
from .types import (
    Address,
    GasEstimate,
    Network,
    TokenAmount,
    TokenInfo,
    TransactionResult,
    TxHash,
    WalletBalance,
    Wei,
)

__all__ = [
    # Version
    "__version__",
    # Config
    "Settings",
    "load_settings",
    # Constants
    "BASE_MAINNET_CHAIN_ID",
    "BASE_SEPOLIA_CHAIN_ID",
    "B20_FACTORY",
    # Exceptions
    "BaseAgentError",
    "ContractError",
    "InsufficientFundsError",
    "ProviderError",
    "TransactionError",
    "WalletError",
    # Logging
    "get_logger",
    "setup_logging",
    # Types
    "Address",
    "GasEstimate",
    "Network",
    "TokenAmount",
    "TokenInfo",
    "TransactionResult",
    "TxHash",
    "WalletBalance",
    "Wei",
]
''')

commit("init: add package exports and public API surface")

# --- Commit 18 ---
os.makedirs("tests", exist_ok=True)
write("tests/__init__.py", "")
write("tests/conftest.py", '''"""Shared test fixtures for Base Agent Toolkit."""

from __future__ import annotations

import pytest

from base_agent_toolkit.config import Settings
from base_agent_toolkit.types import Network


@pytest.fixture
def settings() -> Settings:
    """Create test settings with Sepolia network."""
    return Settings(
        network=Network.SEPOLIA,
        rpc_url="https://sepolia.base.org",
        private_key="ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
        dry_run=True,
        log_level="DEBUG",
    )


@pytest.fixture
def mainnet_settings() -> Settings:
    """Create test settings for mainnet (dry-run only)."""
    return Settings(
        network=Network.MAINNET,
        dry_run=True,
        log_level="DEBUG",
    )


# Well-known test addresses
TEST_ADDRESS_1 = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
TEST_ADDRESS_2 = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
TEST_PRIVATE_KEY = "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
''')

commit("test: add test configuration and shared fixtures")

# --- Commit 19 ---
write("tests/test_types.py", '''"""Tests for type aliases and data structures."""

from decimal import Decimal

from base_agent_toolkit.types import (
    GasEstimate,
    Network,
    TokenAmount,
    TokenInfo,
    TokenStandard,
    TransactionResult,
)


class TestTokenAmount:
    """Tests for TokenAmount dataclass."""

    def test_from_wei(self):
        amount = TokenAmount(raw=1_000_000_000_000_000_000, decimals=18, symbol="ETH")
        assert amount.ether == Decimal("1")

    def test_from_ether(self):
        amount = TokenAmount.from_ether("1.5", decimals=18, symbol="ETH")
        assert amount.raw == 1_500_000_000_000_000_000

    def test_usdc_decimals(self):
        amount = TokenAmount(raw=1_000_000, decimals=6, symbol="USDC")
        assert amount.ether == Decimal("1")

    def test_formatted_output(self):
        amount = TokenAmount(raw=1_500_000, decimals=6, symbol="USDC")
        assert "1.5" in str(amount)
        assert "USDC" in str(amount)

    def test_from_ether_small_amount(self):
        amount = TokenAmount.from_ether("0.001", decimals=18, symbol="ETH")
        assert amount.raw == 1_000_000_000_000_000

    def test_zero_amount(self):
        amount = TokenAmount(raw=0, decimals=18, symbol="ETH")
        assert amount.ether == Decimal("0")


class TestTransactionResult:
    def test_success(self):
        result = TransactionResult(
            hash="0x1234",
            block_number=100,
            gas_used=21000,
            status=True,
        )
        assert result.success is True

    def test_failed(self):
        result = TransactionResult(hash="0x1234", status=False)
        assert result.success is False

    def test_pending(self):
        result = TransactionResult(hash="0x1234")
        assert result.success is False
        assert result.status is None

    def test_explorer_url(self):
        result = TransactionResult(hash="0xabc123")
        assert "basescan.org" in result.explorer_url
        assert "0xabc123" in result.explorer_url


class TestGasEstimate:
    def test_cost_calculation(self):
        estimate = GasEstimate(
            gas_limit=21000,
            max_fee_per_gas=1_000_000_000,  # 1 gwei
            max_priority_fee_per_gas=100_000_000,
            estimated_cost_wei=21_000_000_000_000,
        )
        assert estimate.estimated_cost_gwei == 21000.0

    def test_cost_in_ether(self):
        estimate = GasEstimate(
            gas_limit=21000,
            max_fee_per_gas=1_000_000_000,
            max_priority_fee_per_gas=100_000_000,
            estimated_cost_wei=21_000_000_000_000,
        )
        assert estimate.estimated_cost_ether == Decimal("0.000021")


class TestNetwork:
    def test_mainnet(self):
        assert Network.MAINNET.value == "mainnet"

    def test_sepolia(self):
        assert Network.SEPOLIA.value == "sepolia"


class TestTokenInfo:
    def test_creation(self):
        info = TokenInfo(
            address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            name="USD Coin",
            symbol="USDC",
            decimals=6,
        )
        assert info.symbol == "USDC"
        assert info.standard == TokenStandard.ERC20
''')

commit("test: add unit tests for types module")

# --- Commit 20 ---
write("tests/test_config.py", '''"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest

from base_agent_toolkit.config import Settings, load_settings
from base_agent_toolkit.constants import BASE_MAINNET_CHAIN_ID, BASE_SEPOLIA_CHAIN_ID
from base_agent_toolkit.types import Network


class TestSettings:
    """Tests for Settings class."""

    def test_default_network(self):
        settings = Settings()
        assert settings.network == Network.MAINNET

    def test_chain_id_mainnet(self):
        settings = Settings(network=Network.MAINNET)
        assert settings.chain_id == BASE_MAINNET_CHAIN_ID

    def test_chain_id_sepolia(self):
        settings = Settings(network=Network.SEPOLIA)
        assert settings.chain_id == BASE_SEPOLIA_CHAIN_ID

    def test_rpc_urls_default(self):
        settings = Settings()
        urls = settings.rpc_urls
        assert len(urls) > 0
        assert "base.org" in urls[0]

    def test_rpc_urls_custom(self):
        settings = Settings(rpc_url="https://custom.rpc.com")
        assert settings.rpc_urls[0] == "https://custom.rpc.com"

    def test_rpc_fallbacks_parsing(self):
        settings = Settings(rpc_fallbacks=["https://a.com", "https://b.com"])
        assert len(settings.rpc_fallbacks) == 2

    def test_private_key_normalization(self):
        settings = Settings(private_key="0xabc123")
        assert settings.private_key == "abc123"

    def test_private_key_no_prefix(self):
        settings = Settings(private_key="abc123")
        assert settings.private_key == "abc123"

    def test_dry_run_default(self):
        settings = Settings()
        assert settings.dry_run is False

    def test_from_env(self):
        with patch.dict(os.environ, {"BAT_NETWORK": "sepolia", "BAT_DRY_RUN": "true"}):
            settings = Settings()
            assert settings.network == Network.SEPOLIA
            assert settings.dry_run is True


class TestLoadSettings:
    def test_load_default(self):
        settings = load_settings()
        assert isinstance(settings, Settings)
''')

commit("test: add unit tests for configuration module")

print(f"\\n=== Phase 1 complete! ===")
result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True, cwd=ROOT)
print(result.stdout)
print(f"Total commits: {len(result.stdout.strip().splitlines())}")

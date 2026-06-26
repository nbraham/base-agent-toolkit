# Changelog

All notable changes to Base Agent Toolkit will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] — 2026-06-28

### Added

#### Core
- Project structure with `pyproject.toml`, CI/CD, Docker support
- Comprehensive type system (`TokenAmount`, `GasEstimate`, `TransactionResult`)
- Structured logging with module-level loggers
- Configuration loader with environment variable support
- Custom exception hierarchy for all modules

#### Wallet
- `BaseWallet` — key management, ETH transfers, message signing
- `ERC20Token` — token balance, transfer, approval operations
- `HDWallet` — BIP39 mnemonic, BIP44 derivation, multi-account
- `ContractWrapper` — generic contract interaction
- `TransactionBuilder` — EIP-1559 transaction construction
- `GasOracle` — dynamic gas estimation with fee history

#### B20 Token Standard
- `B20Factory` — deploy asset and stablecoin B20 tokens
- `B20Token` — full ERC-20 + B20 extensions (roles, pause, cap)
- ERC-2612 permit support (gasless approvals)
- Event listener for Transfer/Approval events
- Batch operations (airdrop, multi-mint)

#### DeFi Integrations
- `AerodromeRouter` — swap quotes and transactions on Aerodrome
- `UniswapV3Router` — Uniswap V3 swaps with fee tier optimization
- `MorphoClient` — supply/withdraw on Morpho Blue lending
- `ApprovalManager` — check, grant, and revoke token approvals
- `WETHHelper` — wrap/unwrap ETH ↔ WETH
- `PortfolioTracker` — track balances across tokens

#### AI Agent Framework
- `BaseAgent` — core agent with budget management and action logging
- `AgentExecutor` — run strategies with evaluation and error handling
- `DCAStrategy` — dollar cost averaging implementation
- `RebalanceStrategy` — portfolio rebalancing with drift detection
- Pre-built tools: balance check, transfer, swap

#### x402 Payment Protocol
- `X402Client` — HTTP client with automatic 402 payment handling
- `X402Middleware` — server-side payment verification
- Payment header construction and signature verification

#### Security
- Address and private key validation
- Transaction value guards
- Encrypted keystore for key storage

#### CLI
- `bat info` — show toolkit info
- `bat wallet create/balance/mnemonic` — wallet operations
- `bat b20 configure` — preview B20 token config
- `bat agent status/tools` — agent management

#### Infrastructure
- GitHub Actions CI (Python 3.10-3.12)
- Docker support (production + dev stages)
- Comprehensive test suite (6 test modules)
- Documentation guides (B20, DeFi, AI Agents)
- Code examples (swap, agent, x402, B20)

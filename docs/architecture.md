# Architecture

## Overview

Base Agent Toolkit is organized as a layered Python SDK:

```
┌─────────────────────────────────────────┐
│              CLI / Examples             │
├─────────────────────────────────────────┤
│         Agent Framework + x402          │
├──────────┬──────────┬───────────────────┤
│   DeFi   │   B20    │     Security      │
├──────────┴──────────┴───────────────────┤
│         Wallet / Transaction            │
├─────────────────────────────────────────┤
│        Provider / Network / Utils       │
├─────────────────────────────────────────┤
│             Types / Constants           │
└─────────────────────────────────────────┘
```

## Module Responsibilities

### Provider Layer (`provider/`)
- RPC connection management
- Failover across multiple endpoints
- Rate limiting and retry logic

### Wallet Layer (`wallet/`)
- Key management and signing
- ERC-20 token operations
- HD wallet derivation (BIP39/BIP44)
- Transaction building and gas estimation

### B20 Layer (`b20/`)
- B20 token deployment and management
- Role-based access control
- ERC-2612 permit support
- Event monitoring

### DeFi Layer (`defi/`)
- DEX integration (Aerodrome, Uniswap V3)
- Lending (Morpho Blue)
- Token approvals
- Portfolio tracking

### Agent Layer (`agent/`)
- Base agent with budget controls
- Strategy pattern for trading logic
- Executor for strategy orchestration
- Pre-built tools for AI models

### x402 Layer (`x402/`)
- HTTP client with payment support
- Payment header construction
- Server-side verification middleware

## Design Principles

1. **Composable** — Use only the modules you need
2. **Type-safe** — Full type annotations, PEP 561 compliant
3. **Testable** — Dry-run mode, mock-friendly interfaces
4. **Secure** — Key encryption, value guards, approval management
5. **Observable** — Structured logging throughout

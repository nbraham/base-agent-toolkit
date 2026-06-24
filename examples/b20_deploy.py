#!/usr/bin/env python3
"""Example: Deploy and manage a B20 token on Base.

This script demonstrates:
1. Deploying a B20 Asset token via B20Factory
2. Querying token information
3. Minting tokens
4. Transferring with memo
5. Managing roles

Requirements:
    pip install base-agent-toolkit

Usage:
    python examples/b20_deploy.py
"""

import asyncio
import os
from decimal import Decimal

# Note: In production, import from the installed package
# from base_agent_toolkit import BaseProvider, BaseWallet
# from base_agent_toolkit.b20 import B20Factory, B20Token, B20TokenConfig, B20TokenType, B20Role


def main():
    """Deploy and interact with a B20 token."""
    print("=" * 60)
    print("  B20 Token Deployment Example")
    print("  Base Agent Toolkit")
    print("=" * 60)

    # Configuration
    private_key = os.environ.get("BAT_PRIVATE_KEY", "")
    network = os.environ.get("BAT_NETWORK", "sepolia")

    if not private_key:
        print("\n⚠️  Set BAT_PRIVATE_KEY environment variable")
        print("   export BAT_PRIVATE_KEY=your_private_key_here")
        print("\nRunning in demo mode (no transactions will be sent)\n")
        demo_mode()
        return

    print(f"\n🔗 Network: {network}")
    print("🚀 Starting deployment...\n")

    # In a real implementation:
    # provider = BaseProvider(network=network)
    # wallet = BaseWallet.from_private_key(private_key, provider)
    # factory = B20Factory(provider)
    #
    # config = B20TokenConfig(
    #     name="Demo Token",
    #     symbol="DEMO",
    #     token_type=B20TokenType.ASSET,
    #     admin=wallet.address,
    #     decimals=18,
    #     supply_cap=1_000_000 * 10**18,
    # )
    #
    # tx = factory.build_deploy_tx(config)
    # ... sign and send


def demo_mode():
    """Demonstrate B20 operations without sending transactions."""
    from base_agent_toolkit.b20.types import B20TokenConfig, B20TokenType, B20TokenInfo, B20Role

    # 1. Token Configuration
    print("📋 Step 1: Configure B20 Token")
    config = B20TokenConfig(
        name="Demo Token",
        symbol="DEMO",
        token_type=B20TokenType.ASSET,
        admin="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        decimals=18,
        supply_cap=1_000_000,
    )
    print(f"   Name: {config.name}")
    print(f"   Symbol: {config.symbol}")
    print(f"   Type: {config.token_type.value}")
    print(f"   Decimals: {config.decimals}")
    print(f"   Supply Cap: {config.supply_cap:,}")
    print()

    # 2. Token Info (simulated)
    print("📊 Step 2: Token Info (simulated)")
    info = B20TokenInfo(
        address="0x1234567890123456789012345678901234567890",
        name="Demo Token",
        symbol="DEMO",
        decimals=18,
        token_type=B20TokenType.ASSET,
        total_supply=100_000,
        supply_cap=1_000_000,
    )
    print(f"   Address: {info.address}")
    print(f"   Total Supply: {info.total_supply:,}")
    print(f"   Supply Cap: {info.supply_cap:,}")
    print(f"   Remaining Mintable: {info.remaining_mintable:,}")
    print(f"   Has Supply Cap: {info.has_supply_cap}")
    print()

    # 3. Roles
    print("🔑 Step 3: Available Roles")
    for role in B20Role:
        print(f"   {role.value.upper()}: {role.role_hash.hex()[:16]}...")
    print()

    # 4. Stablecoin variant
    print("💵 Step 4: Stablecoin Configuration")
    stable_config = B20TokenConfig(
        name="Demo USD",
        symbol="dUSD",
        token_type=B20TokenType.STABLECOIN,
        admin="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        currency_code="USD",
    )
    print(f"   Name: {stable_config.name}")
    print(f"   Currency: {stable_config.currency_code}")
    print(f"   Decimals: {stable_config.decimals} (fixed for stablecoin)")
    print()

    print("✅ Demo complete! Set BAT_PRIVATE_KEY to deploy for real.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Example: Deploy a B20 token on Base.

Demonstrates:
1. Configuring a B20 token
2. Deploying via B20Factory
3. Managing roles and permissions
4. Minting and transferring tokens

Usage:
    python examples/b20_deploy.py
"""


def main():
    """Demo B20 token deployment."""
    print("=" * 60)
    print("  B20 Token Deployment Guide")
    print("  Base Native Token Standard (Beryl Upgrade)")
    print("=" * 60)

    print("\n📋 What is B20?")
    print("   B20 is Base's native token standard introduced in")
    print("   the Beryl upgrade (June 2026). It provides:")
    print("   • Gas-efficient via Rust precompiles")
    print("   • Built-in role management (admin, minter, pauser)")
    print("   • ERC-2612 permit support")
    print("   • Optional supply cap")
    print("   • Stablecoin variant with currency code")

    print("\n🔧 Step 1: Configure Token")
    print("   config = B20TokenConfig(")
    print("       name='My Token',")
    print("       symbol='MTK',")
    print("       token_type=B20TokenType.ASSET,")
    print("       admin=wallet.address,")
    print("       decimals=18,")
    print("       supply_cap=1_000_000 * 10**18,")
    print("   )")

    print("\n🏭 Step 2: Deploy via Factory")
    print("   factory = B20Factory(provider)")
    print("   tx = factory.build_deploy_tx(config)")
    print("   result = wallet.sign_and_send(tx)")

    print("\n🔑 Step 3: Manage Roles")
    print("   token = B20Token(token_address, provider)")
    print("   token.grant_role(MINTER_ROLE, minter_address)")

    print("\n💰 Step 4: Mint Tokens")
    print("   token.mint(recipient, 1000 * 10**18)")

    print("\n✅ Token deployed and ready for use!")


if __name__ == "__main__":
    main()

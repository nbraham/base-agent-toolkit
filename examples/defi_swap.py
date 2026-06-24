#!/usr/bin/env python3
"""Example: Token swap on Base DEXs.

Demonstrates:
1. Getting swap quotes from Aerodrome and Uniswap V3
2. Comparing prices across DEXs
3. Building and executing a swap transaction

Usage:
    python examples/defi_swap.py
"""

import os
from decimal import Decimal


def main():
    """Compare swap quotes across Base DEXs."""
    print("=" * 60)
    print("  Base DEX Swap Comparison")
    print("  Base Agent Toolkit")
    print("=" * 60)

    # Demo data
    usdc_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    weth_address = "0x4200000000000000000000000000000000000006"
    amount_usdc = 100  # 100 USDC

    print(f"\n📊 Swap: {amount_usdc} USDC → WETH")
    print(f"   USDC: {usdc_address[:10]}...")
    print(f"   WETH: {weth_address[:10]}...")

    # Simulated quotes
    print("\n🔄 Fetching quotes...")
    print("\n┌─────────────┬──────────────┬───────────┬──────────┐")
    print("│ Protocol    │ Amount Out   │ Impact    │ Gas Est  │")
    print("├─────────────┼──────────────┼───────────┼──────────┤")
    print("│ Aerodrome   │ 0.03421 WETH │ 0.05%     │ 250,000  │")
    print("│ Uniswap V3  │ 0.03418 WETH │ 0.08%     │ 200,000  │")
    print("└─────────────┴──────────────┴───────────┴──────────┘")

    print("\n✅ Best route: Aerodrome (0.03421 WETH)")
    print("   Savings: 0.00003 WETH vs Uniswap V3")

    print("\n📝 To execute for real:")
    print("   1. Set BAT_PRIVATE_KEY environment variable")
    print("   2. Ensure sufficient USDC balance")
    print("   3. Approve router for USDC spending")
    print("   4. Execute swap transaction")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Example: Track a portfolio on Base.

Demonstrates the portfolio tracker with the token registry.

Usage:
    python examples/portfolio_track.py
"""

from base_agent_toolkit.registry import list_all_tokens, list_stablecoins, get_token


def main():
    """Demo portfolio tracking."""
    print("=" * 60)
    print("  Base Portfolio Tracker")
    print("=" * 60)

    print("\n📋 Registered Tokens on Base:")
    print("┌──────────┬────────────────────────────────────────────────┬──────────┐")
    print("│ Symbol   │ Address                                      │ Decimals │")
    print("├──────────┼────────────────────────────────────────────────┼──────────┤")
    for token in list_all_tokens():
        addr = token.address[:20] + "..." if len(token.address) > 20 else token.address
        print(f"│ {token.symbol:<8} │ {addr:<46} │ {token.decimals:<8} │")
    print("└──────────┴────────────────────────────────────────────────┴──────────┘")

    print("\n💲 Stablecoins:")
    for sc in list_stablecoins():
        print(f"   • {sc.symbol} ({sc.name})")

    print("\n🔍 Token Lookup:")
    usdc = get_token("USDC")
    if usdc:
        print(f"   USDC address: {usdc.address}")
        print(f"   Decimals:     {usdc.decimals}")
        print(f"   CoinGecko:    {usdc.coingecko_id}")

    print("\n📊 Portfolio Tracking:")
    print("   from base_agent_toolkit.defi.portfolio import PortfolioTracker")
    print("   tracker = PortfolioTracker(provider, [USDC, WETH])")
    print("   snapshot = tracker.get_snapshot(wallet_address)")


if __name__ == "__main__":
    main()

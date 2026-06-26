#!/usr/bin/env python3
"""Example: x402 HTTP payment flow.

Demonstrates the x402 payment protocol:
1. Making a request to a paid API
2. Handling 402 Payment Required
3. Signing and attaching payment
4. Reviewing payment history

Usage:
    python examples/x402_payment.py
"""


def main():
    """Demo x402 payment flow."""
    print("=" * 60)
    print("  x402 Payment Protocol Demo")
    print("=" * 60)

    print("\n📋 x402 Flow:")
    print("   1. Agent sends HTTP request to paid resource")
    print("   2. Server responds: 402 Payment Required")
    print("   3. Agent signs payment authorization")
    print("   4. Agent retries with X-PAYMENT header")
    print("   5. Server verifies and returns resource")

    print("\n🔐 Payment Requirements (example):")
    print("   ┌──────────────────────────────────────┐")
    print("   │ Scheme:   exact                      │")
    print("   │ Network:  base                       │")
    print("   │ Amount:   0.001 ETH                  │")
    print("   │ Pay To:   0x7890...abcd               │")
    print("   │ Resource: /api/v1/market-data         │")
    print("   └──────────────────────────────────────┘")

    print("\n📝 Usage:")
    print("   from base_agent_toolkit.x402 import X402Client, X402Config")
    print("   ")
    print("   client = X402Client(X402Config(")
    print("       private_key='0x...',")
    print("       auto_pay=True,")
    print("       max_payment_wei=10**16,  # Max 0.01 ETH")
    print("   ))")
    print("   ")
    print("   # Automatically handles 402 responses")
    print("   response = client.get('https://api.example.com/data')")

    print("\n✅ x402 enables AI agents to access paid resources")
    print("   without manual payment setup!")


if __name__ == "__main__":
    main()

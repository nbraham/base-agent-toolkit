"""Formatting utilities for display and logging."""

from __future__ import annotations

from decimal import Decimal


def format_wei(wei: int, decimals: int = 18) -> str:
    """Format a wei amount to human-readable string.

    Args:
        wei: Raw amount in wei.
        decimals: Token decimals (18 for ETH).

    Returns:
        Formatted string (e.g., "1.234567" ETH).
    """
    if decimals == 0:
        return str(wei)

    human = Decimal(wei) / Decimal(10**decimals)

    # Use appropriate precision
    if human == 0:
        return "0"
    elif human < Decimal("0.000001"):
        return f"{human:.18f}".rstrip("0").rstrip(".")
    elif human < Decimal("1"):
        return f"{human:.8f}".rstrip("0").rstrip(".")
    elif human < Decimal("1000"):
        return f"{human:.6f}".rstrip("0").rstrip(".")
    else:
        return f"{human:,.4f}".rstrip("0").rstrip(".")


def format_address(address: str, chars: int = 6) -> str:
    """Shorten an address for display.

    Args:
        address: Full Ethereum address.
        chars: Number of chars to show on each end.

    Returns:
        Shortened address (e.g., "0x1234...5678").
    """
    if len(address) <= chars * 2 + 4:
        return address
    return f"{address[:chars + 2]}...{address[-chars:]}"


def format_tx_hash(tx_hash: str) -> str:
    """Shorten a transaction hash for display.

    Args:
        tx_hash: Full transaction hash.

    Returns:
        Shortened hash (e.g., "0xabcd...ef12").
    """
    return format_address(tx_hash, chars=8)


def format_gas_price(gwei: float) -> str:
    """Format a gas price in gwei.

    Args:
        gwei: Gas price in gwei.

    Returns:
        Formatted string (e.g., "12.5 gwei").
    """
    if gwei < 0.01:
        return f"{gwei:.4f} gwei"
    elif gwei < 1:
        return f"{gwei:.3f} gwei"
    else:
        return f"{gwei:.2f} gwei"


def format_usd(amount: float | Decimal) -> str:
    """Format a USD amount.

    Args:
        amount: USD amount.

    Returns:
        Formatted string (e.g., "$1,234.56").
    """
    if isinstance(amount, Decimal):
        amount = float(amount)

    if amount < 0.01:
        return f"${amount:.6f}"
    elif amount < 1:
        return f"${amount:.4f}"
    else:
        return f"${amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a percentage value.

    Args:
        value: Percentage (e.g., 5.5 = 5.5%).
        decimals: Decimal places.

    Returns:
        Formatted string (e.g., "5.50%").
    """
    return f"{value:.{decimals}f}%"

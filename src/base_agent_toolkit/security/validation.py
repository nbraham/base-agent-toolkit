"""Input validation and security checks."""

from __future__ import annotations

import re
from typing import Any

from web3 import Web3

from ..exceptions import WalletError
from ..logging import get_logger

logger = get_logger(__name__)

# Known phishing / honeypot contract patterns
BLACKLISTED_METHODS = {
    "0x095ea7b3",  # approve (not blacklisted, but monitored)
}

# Maximum transaction value guards
MAX_ETH_PER_TX = 100  # ETH
MAX_TOKEN_APPROVAL = 2**128  # Reasonable max approval


def validate_address(address: str) -> str:
    """Validate and checksum an Ethereum address.

    Args:
        address: Raw address string.

    Returns:
        Checksummed address.

    Raises:
        ValueError: If address is invalid.
    """
    if not address:
        raise ValueError("Address cannot be empty")

    if not re.match(r"^0x[0-9a-fA-F]{40}$", address):
        raise ValueError(f"Invalid address format: {address}")

    try:
        return Web3.to_checksum_address(address)
    except ValueError as e:
        raise ValueError(f"Invalid checksum: {e}")


def validate_private_key(key: str) -> str:
    """Validate a private key format.

    Args:
        key: Private key string.

    Returns:
        Normalized private key (with 0x prefix).

    Raises:
        ValueError: If key is invalid.
    """
    if not key:
        raise ValueError("Private key cannot be empty")

    clean = key.strip()
    if not clean.startswith("0x"):
        clean = f"0x{clean}"

    if not re.match(r"^0x[0-9a-fA-F]{64}$", clean):
        raise ValueError("Invalid private key format (expected 64 hex chars)")

    return clean


def validate_tx_value(
    value_wei: int,
    max_eth: float = MAX_ETH_PER_TX,
) -> bool:
    """Validate a transaction value is within safe limits.

    Args:
        value_wei: Transaction value in wei.
        max_eth: Maximum allowed value in ETH.

    Returns:
        True if within limits.

    Raises:
        ValueError: If value exceeds limit.
    """
    max_wei = int(max_eth * 10**18)
    if value_wei > max_wei:
        raise ValueError(
            f"Transaction value {value_wei / 10**18:.4f} ETH "
            f"exceeds maximum {max_eth} ETH"
        )
    if value_wei < 0:
        raise ValueError("Transaction value cannot be negative")
    return True


def is_contract_address(
    address: str,
    provider: Any,
) -> bool:
    """Check if an address is a contract (has code).

    Args:
        address: Address to check.
        provider: BaseProvider instance.

    Returns:
        True if address has code deployed.
    """
    checksummed = validate_address(address)
    code = provider.w3.eth.get_code(checksummed)
    return len(code) > 0


def sanitize_calldata(data: bytes | str) -> str:
    """Sanitize transaction calldata for logging.

    Masks potentially sensitive data while preserving
    the function selector for debugging.

    Args:
        data: Raw calldata.

    Returns:
        Sanitized string representation.
    """
    if isinstance(data, bytes):
        data = data.hex()

    if not data or data == "0x":
        return "0x (empty)"

    selector = data[:10] if len(data) >= 10 else data
    return f"{selector}...({len(data) // 2} bytes)"

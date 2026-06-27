"""ABI encoding and decoding helpers."""

from __future__ import annotations

from typing import Any

from web3 import Web3


def encode_function_call(
    function_signature: str,
    args: list[Any],
) -> bytes:
    """Encode a function call from its signature.

    Args:
        function_signature: e.g., "transfer(address,uint256)"
        args: Function arguments.

    Returns:
        Encoded calldata.

    Example:
        data = encode_function_call(
            "transfer(address,uint256)",
            ["0x1234...", 1000]
        )
    """
    selector = Web3.keccak(text=function_signature)[:4]
    # Simple encoding for common types
    w3 = Web3()
    encoded_args = w3.codec.encode(
        _parse_types(function_signature),
        args,
    )
    return selector + encoded_args


def decode_function_result(
    output_types: list[str],
    data: bytes,
) -> tuple:
    """Decode function return data.

    Args:
        output_types: List of Solidity types (e.g., ["uint256", "address"]).
        data: Raw return data.

    Returns:
        Decoded values as a tuple.
    """
    w3 = Web3()
    return w3.codec.decode(output_types, data)


def _parse_types(signature: str) -> list[str]:
    """Extract parameter types from a function signature.

    Args:
        signature: e.g., "transfer(address,uint256)"

    Returns:
        List of type strings.
    """
    params_str = signature.split("(")[1].rstrip(")")
    if not params_str:
        return []
    return [t.strip() for t in params_str.split(",")]


def compute_selector(function_signature: str) -> str:
    """Compute the 4-byte function selector.

    Args:
        function_signature: e.g., "transfer(address,uint256)"

    Returns:
        Hex string of selector (e.g., "0xa9059cbb").
    """
    return Web3.keccak(text=function_signature)[:4].hex()


def compute_event_topic(event_signature: str) -> str:
    """Compute the topic hash for an event.

    Args:
        event_signature: e.g., "Transfer(address,address,uint256)"

    Returns:
        Hex string of the topic (32 bytes).
    """
    return Web3.keccak(text=event_signature).hex()

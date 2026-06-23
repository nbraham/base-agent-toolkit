"""ERC-2612 permit signing for B20 tokens."""

from __future__ import annotations

import time
from typing import Any

from web3 import Web3

from ..logging import get_logger
from ..types import Address
from .token import B20Token

logger = get_logger(__name__)

# EIP-712 Permit type definition
PERMIT_TYPES = {
    "Permit": [
        {"name": "owner", "type": "address"},
        {"name": "spender", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
    ]
}


def build_permit_signature(
    token: B20Token,
    owner_private_key: str,
    spender: Address,
    value: int,
    deadline: int | None = None,
    chain_id: int = 8453,
) -> dict[str, Any]:
    """Build an ERC-2612 permit signature for gasless approval.

    This allows a user to sign an off-chain message that authorizes
    a spender to use their tokens, without needing to send a transaction.

    Args:
        token: B20Token instance.
        owner_private_key: Private key of the token owner.
        spender: Address to approve.
        value: Amount to approve (raw).
        deadline: Unix timestamp deadline (default: 1 hour from now).
        chain_id: Chain ID for EIP-712 domain.

    Returns:
        Dictionary with v, r, s signature components and parameters.
    """
    from eth_account import Account
    from eth_account.messages import encode_typed_data

    if deadline is None:
        deadline = int(time.time()) + 3600  # 1 hour from now

    # Get owner address
    if not owner_private_key.startswith("0x"):
        owner_private_key = f"0x{owner_private_key}"
    account = Account.from_key(owner_private_key)
    owner = account.address

    # Get permit nonce
    nonce = token.get_nonce(owner)

    # Build EIP-712 domain
    domain = {
        "name": token.name(),
        "version": "1",
        "chainId": chain_id,
        "verifyingContract": token.address,
    }

    # Build message
    message = {
        "owner": owner,
        "spender": Web3.to_checksum_address(spender),
        "value": value,
        "nonce": nonce,
        "deadline": deadline,
    }

    # Sign
    signable = encode_typed_data(
        domain_data=domain,
        message_types=PERMIT_TYPES,
        message_data=message,
    )
    signed = account.sign_message(signable)

    logger.info(
        "permit.signed",
        token=token.address,
        owner=owner,
        spender=spender,
        value=value,
        deadline=deadline,
    )

    return {
        "owner": owner,
        "spender": Web3.to_checksum_address(spender),
        "value": value,
        "deadline": deadline,
        "v": signed.v,
        "r": signed.r.to_bytes(32, "big"),
        "s": signed.s.to_bytes(32, "big"),
    }


def build_permit_tx(
    token: B20Token,
    permit_data: dict[str, Any],
) -> dict[str, Any]:
    """Build a permit transaction from signed permit data.

    This submits the permit on-chain so the approval takes effect.
    Any address can submit this transaction.

    Args:
        token: B20Token instance.
        permit_data: Output from build_permit_signature().

    Returns:
        Unsigned transaction dictionary.
    """
    return token._contract.functions.permit(
        permit_data["owner"],
        permit_data["spender"],
        permit_data["value"],
        permit_data["deadline"],
        permit_data["v"],
        permit_data["r"],
        permit_data["s"],
    ).build_transaction({"gas": 80_000})

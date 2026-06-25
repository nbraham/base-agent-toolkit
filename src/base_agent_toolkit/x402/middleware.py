"""x402 middleware for server-side payment verification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from web3 import Web3

from ..logging import get_logger
from .payment import PaymentHeader, PaymentRequirements

logger = get_logger(__name__)


@dataclass
class PaymentVerification:
    """Result of verifying an x402 payment."""

    valid: bool
    payer: str = ""
    amount: int = 0
    error: str = ""


class X402Middleware:
    """Server-side middleware for accepting x402 payments.

    Verifies payment signatures from x402 clients and
    facilitates on-chain settlement.

    Args:
        pay_to: Address to receive payments.
        chain_id: Expected chain ID.
    """

    def __init__(self, pay_to: str, chain_id: int = 8453):
        self._pay_to = Web3.to_checksum_address(pay_to)
        self._chain_id = chain_id

    def create_requirements(
        self,
        resource: str,
        amount: int,
        description: str = "",
        mime_type: str = "application/json",
    ) -> PaymentRequirements:
        """Create payment requirements for a 402 response.

        Args:
            resource: URL of the paid resource.
            amount: Required payment amount (raw wei).
            description: Human-readable description.
            mime_type: Content type of the resource.

        Returns:
            PaymentRequirements to include in 402 response.
        """
        return PaymentRequirements(
            scheme="exact",
            network="base",
            max_amount_required=amount,
            resource=resource,
            description=description,
            mime_type=mime_type,
            pay_to=self._pay_to,
        )

    def verify_payment(
        self,
        payment_header_value: str,
        expected_resource: str,
        min_amount: int = 0,
    ) -> PaymentVerification:
        """Verify an x402 payment header.

        Args:
            payment_header_value: Value of the X-PAYMENT header.
            expected_resource: Expected resource URL.
            min_amount: Minimum payment amount.

        Returns:
            PaymentVerification result.
        """
        try:
            data = json.loads(payment_header_value)
        except json.JSONDecodeError:
            return PaymentVerification(valid=False, error="Invalid JSON in payment header")

        payload = data.get("payload", {})
        signature = data.get("signature", "")

        # Verify resource matches
        if payload.get("resource") != expected_resource:
            return PaymentVerification(
                valid=False,
                error=f"Resource mismatch: {payload.get('resource')} != {expected_resource}",
            )

        # Verify pay_to matches
        if payload.get("payTo", "").lower() != self._pay_to.lower():
            return PaymentVerification(
                valid=False,
                error="Pay-to address mismatch",
            )

        # Verify chain ID
        if payload.get("chainId") != self._chain_id:
            return PaymentVerification(
                valid=False,
                error=f"Chain ID mismatch: {payload.get('chainId')} != {self._chain_id}",
            )

        # Verify amount
        amount = int(payload.get("amount", "0"))
        if amount < min_amount:
            return PaymentVerification(
                valid=False,
                error=f"Insufficient amount: {amount} < {min_amount}",
            )

        # Verify signature
        from eth_account import Account
        from eth_account.messages import encode_defunct

        message = json.dumps(payload, sort_keys=True)
        msg_hash = encode_defunct(text=message)

        try:
            signer = Account.recover_message(
                msg_hash, signature=bytes.fromhex(signature)
            )
        except Exception as e:
            return PaymentVerification(
                valid=False,
                error=f"Invalid signature: {e}",
            )

        logger.info(
            "x402_middleware.payment_verified",
            payer=signer,
            amount=amount,
            resource=expected_resource,
        )

        return PaymentVerification(
            valid=True,
            payer=signer,
            amount=amount,
        )

    def __repr__(self) -> str:
        return f"X402Middleware(pay_to={self._pay_to})"

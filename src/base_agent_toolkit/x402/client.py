"""x402 HTTP client for AI agent payments."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from ..exceptions import X402Error, X402PaymentError
from ..logging import get_logger
from ..types import Address
from .payment import PaymentHeader, PaymentRequirements

logger = get_logger(__name__)


@dataclass
class X402Config:
    """Configuration for x402 client.

    Args:
        private_key: Wallet private key for signing payments.
        chain_id: Chain ID (default: 8453 for Base mainnet).
        max_payment_wei: Maximum automatic payment amount.
        auto_pay: Automatically pay 402 responses.
    """

    private_key: str
    chain_id: int = 8453
    max_payment_wei: int = 10**16  # 0.01 ETH default max
    auto_pay: bool = True


class X402Client:
    """HTTP client with x402 payment support.

    Wraps standard HTTP requests and automatically handles
    402 Payment Required responses by signing payments.

    Args:
        config: X402Config instance.
    """

    def __init__(self, config: X402Config):
        self._config = config
        self._payments_made: list[dict[str, Any]] = []

        logger.info(
            "x402.client_initialized",
            chain_id=config.chain_id,
            auto_pay=config.auto_pay,
            max_payment=f"{config.max_payment_wei / 1e18:.4f} ETH",
        )

    def get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Make a GET request with x402 payment support.

        If the server responds with 402 and auto_pay is enabled,
        automatically signs a payment and retries.

        Args:
            url: Target URL.
            **kwargs: Additional request parameters.

        Returns:
            Response data dictionary.

        Raises:
            X402PaymentError: If payment fails or is rejected.
        """
        import httpx

        headers = kwargs.pop("headers", {})

        # First request
        response = httpx.get(url, headers=headers, **kwargs)

        if response.status_code == 402:
            if not self._config.auto_pay:
                raise X402PaymentError(
                    "Payment required but auto_pay is disabled",
                    requirements=self._parse_requirements(response),
                )

            # Parse requirements
            requirements = self._parse_requirements(response)

            # Check amount limit
            if requirements.max_amount_required > self._config.max_payment_wei:
                raise X402PaymentError(
                    f"Payment amount ({requirements.amount_eth:.6f} ETH) "
                    f"exceeds max ({self._config.max_payment_wei / 1e18:.6f} ETH)",
                    requirements=requirements,
                )

            # Sign payment
            payment_header = self._sign_payment(requirements)

            # Retry with payment header
            headers.update(payment_header.as_dict)
            response = httpx.get(url, headers=headers, **kwargs)

            if response.status_code == 402:
                raise X402PaymentError(
                    "Payment rejected by server",
                    requirements=requirements,
                )

            # Record payment
            self._record_payment(url, requirements)

        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "data": response.text,
        }

    def post(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Make a POST request with x402 payment support.

        Args:
            url: Target URL.
            **kwargs: Additional request parameters.

        Returns:
            Response data dictionary.
        """
        import httpx

        headers = kwargs.pop("headers", {})
        response = httpx.post(url, headers=headers, **kwargs)

        if response.status_code == 402 and self._config.auto_pay:
            requirements = self._parse_requirements(response)
            if requirements.max_amount_required <= self._config.max_payment_wei:
                payment_header = self._sign_payment(requirements)
                headers.update(payment_header.as_dict)
                response = httpx.post(url, headers=headers, **kwargs)
                self._record_payment(url, requirements)

        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "data": response.text,
        }

    def _parse_requirements(self, response: Any) -> PaymentRequirements:
        """Parse payment requirements from 402 response."""
        return PaymentRequirements.from_response_headers(dict(response.headers))

    def _sign_payment(self, requirements: PaymentRequirements) -> PaymentHeader:
        """Sign a payment authorization.

        Args:
            requirements: Server's payment requirements.

        Returns:
            PaymentHeader with signed authorization.
        """
        from eth_account import Account
        from eth_account.messages import encode_defunct

        timestamp = int(time.time())

        payload = {
            "scheme": requirements.scheme,
            "network": requirements.network,
            "resource": requirements.resource,
            "amount": str(requirements.max_amount_required),
            "payTo": requirements.pay_to,
            "timestamp": timestamp,
            "chainId": self._config.chain_id,
        }

        # Sign the payload
        message = json.dumps(payload, sort_keys=True)
        msg_hash = encode_defunct(text=message)

        pk = self._config.private_key
        if not pk.startswith("0x"):
            pk = f"0x{pk}"
        account = Account.from_key(pk)
        signed = account.sign_message(msg_hash)

        logger.info(
            "x402.payment_signed",
            resource=requirements.resource,
            amount=requirements.max_amount_required,
            pay_to=requirements.pay_to,
        )

        return PaymentHeader(
            scheme=requirements.scheme,
            network=requirements.network,
            payload=payload,
            signature=signed.signature.hex(),
        )

    def _record_payment(
        self,
        url: str,
        requirements: PaymentRequirements,
    ) -> None:
        """Record a successful payment."""
        self._payments_made.append({
            "url": url,
            "amount_wei": requirements.max_amount_required,
            "pay_to": requirements.pay_to,
            "timestamp": int(time.time()),
        })

    @property
    def total_paid_wei(self) -> int:
        """Total amount paid via x402."""
        return sum(p["amount_wei"] for p in self._payments_made)

    @property
    def payment_count(self) -> int:
        """Number of x402 payments made."""
        return len(self._payments_made)

    def get_payment_history(self) -> list[dict[str, Any]]:
        """Get full payment history."""
        return list(self._payments_made)

    def __repr__(self) -> str:
        return (
            f"X402Client(chain_id={self._config.chain_id}, "
            f"auto_pay={self._config.auto_pay})"
        )

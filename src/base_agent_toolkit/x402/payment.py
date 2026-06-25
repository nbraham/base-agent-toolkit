"""x402 payment types and header construction."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from web3 import Web3

from ..logging import get_logger

logger = get_logger(__name__)


@dataclass
class PaymentRequirements:
    """Payment requirements from a 402 response.

    Parsed from the server's 402 Payment Required response.

    Attributes:
        scheme: Payment scheme (e.g., "exact").
        network: Network identifier (e.g., "base").
        max_amount_required: Maximum payment amount (raw).
        resource: URL of the paid resource.
        description: Human-readable description.
        mime_type: Content type of the resource.
        pay_to: Address to send payment to.
        extra: Additional scheme-specific data.
    """

    scheme: str
    network: str
    max_amount_required: int
    resource: str
    description: str = ""
    mime_type: str = ""
    pay_to: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_response_headers(cls, headers: dict[str, str]) -> "PaymentRequirements":
        """Parse payment requirements from HTTP response headers.

        Args:
            headers: HTTP response headers.

        Returns:
            PaymentRequirements instance.
        """
        # Parse X-PAYMENT header or WWW-Authenticate
        payment_info = headers.get("X-PAYMENT", "")
        if not payment_info:
            payment_info = headers.get("WWW-Authenticate", "")

        try:
            data = json.loads(payment_info) if payment_info else {}
        except json.JSONDecodeError:
            data = {}

        return cls(
            scheme=data.get("scheme", "exact"),
            network=data.get("network", "base"),
            max_amount_required=int(data.get("maxAmountRequired", "0")),
            resource=data.get("resource", ""),
            description=data.get("description", ""),
            mime_type=data.get("mimeType", ""),
            pay_to=data.get("payTo", ""),
            extra={
                k: v for k, v in data.items()
                if k not in {
                    "scheme", "network", "maxAmountRequired",
                    "resource", "description", "mimeType", "payTo",
                }
            },
        )

    @property
    def amount_eth(self) -> float:
        """Max amount in ETH."""
        return self.max_amount_required / 1e18


@dataclass
class PaymentHeader:
    """Constructed X-PAYMENT header for request.

    Contains the signed payment authorization that the agent
    includes in retried requests.

    Attributes:
        scheme: Payment scheme.
        network: Network identifier.
        payload: Signed payment payload.
        signature: Payment signature.
    """

    scheme: str
    network: str
    payload: dict[str, Any]
    signature: str

    def to_header_value(self) -> str:
        """Serialize to X-PAYMENT header value.

        Returns:
            JSON string for the X-PAYMENT header.
        """
        data = {
            "scheme": self.scheme,
            "network": self.network,
            "payload": self.payload,
            "signature": self.signature,
        }
        return json.dumps(data)

    @property
    def as_dict(self) -> dict[str, str]:
        """Get as HTTP headers dictionary."""
        return {"X-PAYMENT": self.to_header_value()}

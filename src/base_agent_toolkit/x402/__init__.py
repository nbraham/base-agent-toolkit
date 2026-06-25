"""x402 HTTP payment protocol for AI agents.

x402 enables AI agents to access paid resources by including
payment headers in HTTP requests. It uses the HTTP 402 Payment
Required status code.

Protocol flow:
1. Agent makes HTTP request to a paid resource
2. Server responds with 402 and payment requirements
3. Agent signs a payment authorization
4. Agent retries request with X-PAYMENT header
5. Server facilitates payment on-chain and returns resource

See: https://www.x402.org/
"""

from .client import X402Client, X402Config
from .payment import PaymentHeader, PaymentRequirements

__all__ = [
    "X402Client",
    "X402Config",
    "PaymentHeader",
    "PaymentRequirements",
]

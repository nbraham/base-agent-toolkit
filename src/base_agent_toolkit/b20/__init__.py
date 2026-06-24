"""B20 native token standard module (Beryl upgrade).

B20 is Base's native token standard — ERC-20 compatible tokens
implemented as Rust precompiles. Supports stablecoin, RWA,
and general-purpose token issuance.

Introduced with the Beryl upgrade on June 25, 2026.
"""

from .batch import B20BatchOperations, MintRequest, TransferRequest
from .events import B20EventListener, B20TransferEvent, B20ApprovalEvent
from .factory import B20Factory
from .permit import build_permit_signature, build_permit_tx
from .token import B20Token
from .types import B20Role, B20TokenConfig, B20TokenInfo, B20TokenType

__all__ = [
    "B20BatchOperations",
    "B20EventListener",
    "B20Factory",
    "B20Token",
    "B20TokenConfig",
    "B20TokenInfo",
    "B20TokenType",
    "B20Role",
    "B20TransferEvent",
    "B20ApprovalEvent",
    "MintRequest",
    "TransferRequest",
    "build_permit_signature",
    "build_permit_tx",
]

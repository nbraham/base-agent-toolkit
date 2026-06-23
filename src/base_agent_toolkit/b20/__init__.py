"""B20 native token standard module (Beryl upgrade).

B20 is Base's native token standard — ERC-20 compatible tokens
implemented as Rust precompiles. Supports stablecoin, RWA,
and general-purpose token issuance.
"""

from .token import B20Token
from .factory import B20Factory
from .types import B20TokenType, B20Role, B20TokenConfig

__all__ = [
    "B20Token",
    "B20Factory",
    "B20TokenType",
    "B20Role",
    "B20TokenConfig",
]

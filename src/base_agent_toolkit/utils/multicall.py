"""Multicall3 batching for efficient RPC calls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web3 import Web3

from ..logging import get_logger
from ..provider.base import BaseProvider

logger = get_logger(__name__)

# Multicall3 on Base
MULTICALL3_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"

MULTICALL3_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "target", "type": "address"},
                    {"name": "allowFailure", "type": "bool"},
                    {"name": "callData", "type": "bytes"},
                ],
                "name": "calls",
                "type": "tuple[]",
            }
        ],
        "name": "aggregate3",
        "outputs": [
            {
                "components": [
                    {"name": "success", "type": "bool"},
                    {"name": "returnData", "type": "bytes"},
                ],
                "name": "returnData",
                "type": "tuple[]",
            }
        ],
        "stateMutability": "payable",
        "type": "function",
    },
]


@dataclass
class MulticallResult:
    """Result of a single call within a multicall batch."""
    success: bool
    return_data: bytes
    decoded: Any = None


class Multicall:
    """Batch multiple contract calls into a single RPC request.

    Uses Multicall3 contract to reduce RPC calls and latency.

    Args:
        provider: BaseProvider instance.
    """

    def __init__(self, provider: BaseProvider):
        self._provider = provider
        self._contract = provider.w3.eth.contract(
            address=Web3.to_checksum_address(MULTICALL3_ADDRESS),
            abi=MULTICALL3_ABI,
        )
        self._calls: list[tuple[str, bool, bytes]] = []

    def add_call(
        self,
        target: str,
        calldata: bytes,
        allow_failure: bool = True,
    ) -> "Multicall":
        """Add a call to the batch.

        Args:
            target: Contract address to call.
            calldata: Encoded function call data.
            allow_failure: If True, don't revert on failure.

        Returns:
            Self for chaining.
        """
        self._calls.append((
            Web3.to_checksum_address(target),
            allow_failure,
            calldata,
        ))
        return self

    def execute(self) -> list[MulticallResult]:
        """Execute all batched calls.

        Returns:
            List of MulticallResult for each call.
        """
        if not self._calls:
            return []

        logger.info("multicall.executing", calls=len(self._calls))

        results_raw = self._contract.functions.aggregate3(
            self._calls
        ).call()

        results = [
            MulticallResult(
                success=r[0],
                return_data=r[1],
            )
            for r in results_raw
        ]

        successful = sum(1 for r in results if r.success)
        logger.info(
            "multicall.complete",
            total=len(results),
            successful=successful,
        )

        # Clear calls
        self._calls = []

        return results

    def __len__(self) -> int:
        return len(self._calls)

    def __repr__(self) -> str:
        return f"Multicall(pending={len(self._calls)})"

"""B20 token event listener and parser."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web3 import Web3

from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address
from .abi import B20_TOKEN_ABI

logger = get_logger(__name__)


@dataclass
class B20TransferEvent:
    """Parsed B20/ERC-20 Transfer event."""

    token_address: Address
    from_address: Address
    to_address: Address
    amount: int
    block_number: int
    tx_hash: str
    log_index: int

    @property
    def is_mint(self) -> bool:
        """True if this is a mint (from zero address)."""
        return self.from_address == "0x0000000000000000000000000000000000000000"

    @property
    def is_burn(self) -> bool:
        """True if this is a burn (to zero address)."""
        return self.to_address == "0x0000000000000000000000000000000000000000"


@dataclass
class B20ApprovalEvent:
    """Parsed B20/ERC-20 Approval event."""

    token_address: Address
    owner: Address
    spender: Address
    amount: int
    block_number: int
    tx_hash: str


class B20EventListener:
    """Listen for and parse B20 token events.

    Args:
        token_address: B20 token contract address.
        provider: BaseProvider instance.
    """

    def __init__(self, token_address: Address, provider: BaseProvider):
        self._token_address = Web3.to_checksum_address(token_address)
        self._provider = provider
        self._contract = provider.w3.eth.contract(
            address=self._token_address,
            abi=B20_TOKEN_ABI,
        )

    def get_transfers(
        self,
        from_block: int | str = "latest",
        to_block: int | str = "latest",
        from_address: Address | None = None,
        to_address: Address | None = None,
    ) -> list[B20TransferEvent]:
        """Get Transfer events for the token.

        Args:
            from_block: Start block number or 'latest'.
            to_block: End block number or 'latest'.
            from_address: Filter by sender address.
            to_address: Filter by recipient address.

        Returns:
            List of B20TransferEvent objects.
        """
        filters: dict[str, Any] = {}
        if from_address:
            filters["from"] = Web3.to_checksum_address(from_address)
        if to_address:
            filters["to"] = Web3.to_checksum_address(to_address)

        try:
            event_filter = self._contract.events.Transfer.create_filter(
                fromBlock=from_block,
                toBlock=to_block,
                argument_filters=filters if filters else None,
            )
            entries = event_filter.get_all_entries()
        except Exception as e:
            logger.warning("b20_events.transfer_query_failed", error=str(e))
            return []

        events = []
        for entry in entries:
            events.append(
                B20TransferEvent(
                    token_address=self._token_address,
                    from_address=entry.args.get("from", ""),
                    to_address=entry.args.get("to", ""),
                    amount=entry.args.get("value", 0),
                    block_number=entry.blockNumber,
                    tx_hash=entry.transactionHash.hex(),
                    log_index=entry.logIndex,
                )
            )

        logger.info(
            "b20_events.transfers_found",
            token=self._token_address,
            count=len(events),
        )
        return events

    def get_approvals(
        self,
        from_block: int | str = "latest",
        to_block: int | str = "latest",
        owner: Address | None = None,
    ) -> list[B20ApprovalEvent]:
        """Get Approval events for the token.

        Args:
            from_block: Start block number.
            to_block: End block number.
            owner: Filter by token owner.

        Returns:
            List of B20ApprovalEvent objects.
        """
        filters: dict[str, Any] = {}
        if owner:
            filters["owner"] = Web3.to_checksum_address(owner)

        try:
            event_filter = self._contract.events.Approval.create_filter(
                fromBlock=from_block,
                toBlock=to_block,
                argument_filters=filters if filters else None,
            )
            entries = event_filter.get_all_entries()
        except Exception as e:
            logger.warning("b20_events.approval_query_failed", error=str(e))
            return []

        events = []
        for entry in entries:
            events.append(
                B20ApprovalEvent(
                    token_address=self._token_address,
                    owner=entry.args.get("owner", ""),
                    spender=entry.args.get("spender", ""),
                    amount=entry.args.get("value", 0),
                    block_number=entry.blockNumber,
                    tx_hash=entry.transactionHash.hex(),
                )
            )

        return events

    def get_recent_activity(
        self,
        blocks_back: int = 1000,
    ) -> dict[str, Any]:
        """Get recent token activity summary.

        Args:
            blocks_back: Number of blocks to look back.

        Returns:
            Summary dictionary with transfer and approval counts.
        """
        current_block = self._provider.get_block_number()
        from_block = max(0, current_block - blocks_back)

        transfers = self.get_transfers(from_block=from_block, to_block="latest")
        approvals = self.get_approvals(from_block=from_block, to_block="latest")

        mints = [t for t in transfers if t.is_mint]
        burns = [t for t in transfers if t.is_burn]
        regular = [t for t in transfers if not t.is_mint and not t.is_burn]

        return {
            "token": self._token_address,
            "from_block": from_block,
            "to_block": current_block,
            "total_transfers": len(transfers),
            "mints": len(mints),
            "burns": len(burns),
            "regular_transfers": len(regular),
            "approvals": len(approvals),
            "total_minted": sum(m.amount for m in mints),
            "total_burned": sum(b.amount for b in burns),
        }

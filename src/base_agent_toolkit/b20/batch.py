"""Batch operations for B20 tokens."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web3 import Web3

from ..logging import get_logger
from ..types import Address
from .token import B20Token

logger = get_logger(__name__)


@dataclass
class MintRequest:
    """Single mint request in a batch."""

    to: Address
    amount: int


@dataclass
class TransferRequest:
    """Single transfer request in a batch."""

    to: Address
    amount: int
    memo: str = ""


class B20BatchOperations:
    """Batch operations for B20 tokens.

    Provides helpers for building multiple transactions
    for airdrops, batch minting, and multi-recipient transfers.

    Args:
        token: B20Token instance.
    """

    def __init__(self, token: B20Token):
        self._token = token

    def build_batch_mint_txs(
        self,
        requests: list[MintRequest],
    ) -> list[dict[str, Any]]:
        """Build multiple mint transactions.

        Args:
            requests: List of MintRequest objects.

        Returns:
            List of unsigned transaction dictionaries.
        """
        txs = []
        for req in requests:
            tx = self._token.build_mint_tx(req.to, req.amount)
            txs.append(tx)

        logger.info(
            "b20_batch.mint_prepared",
            count=len(txs),
            total_amount=sum(r.amount for r in requests),
        )
        return txs

    def build_batch_transfer_txs(
        self,
        requests: list[TransferRequest],
    ) -> list[dict[str, Any]]:
        """Build multiple transfer transactions.

        Args:
            requests: List of TransferRequest objects.

        Returns:
            List of unsigned transaction dictionaries.
        """
        txs = []
        for req in requests:
            if req.memo:
                tx = self._token.build_transfer_with_memo_tx(
                    req.to, req.amount, req.memo
                )
            else:
                tx = self._token.build_transfer_tx(req.to, req.amount)
            txs.append(tx)

        logger.info(
            "b20_batch.transfer_prepared",
            count=len(txs),
            total_amount=sum(r.amount for r in requests),
        )
        return txs

    def build_airdrop_txs(
        self,
        recipients: list[Address],
        amount_per_recipient: int,
        memo: str = "",
    ) -> list[dict[str, Any]]:
        """Build airdrop transactions (equal amount to each recipient).

        Args:
            recipients: List of recipient addresses.
            amount_per_recipient: Raw amount each recipient gets.
            memo: Optional memo for all transfers.

        Returns:
            List of unsigned transaction dictionaries.
        """
        requests = [
            TransferRequest(to=addr, amount=amount_per_recipient, memo=memo)
            for addr in recipients
        ]
        return self.build_batch_transfer_txs(requests)

    @staticmethod
    def parse_csv_recipients(csv_content: str) -> list[MintRequest]:
        """Parse CSV content into mint requests.

        Expected format: address,amount (one per line)

        Args:
            csv_content: CSV string content.

        Returns:
            List of MintRequest objects.
        """
        requests = []
        for line in csv_content.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("address"):
                continue
            parts = line.split(",")
            if len(parts) >= 2:
                address = parts[0].strip()
                amount = int(parts[1].strip())
                requests.append(MintRequest(to=address, amount=amount))

        logger.info("b20_batch.csv_parsed", recipients=len(requests))
        return requests

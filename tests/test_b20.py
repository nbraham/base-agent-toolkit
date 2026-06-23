"""Tests for B20 token module."""

import pytest

from base_agent_toolkit.b20.types import (
    B20Role,
    B20TokenConfig,
    B20TokenInfo,
    B20TokenType,
)
from base_agent_toolkit.b20.batch import (
    B20BatchOperations,
    MintRequest,
    TransferRequest,
)
from base_agent_toolkit.b20.events import B20TransferEvent


class TestB20TokenConfig:
    """Tests for B20TokenConfig."""

    def test_asset_config(self):
        config = B20TokenConfig(
            name="Test Token",
            symbol="TST",
            token_type=B20TokenType.ASSET,
            admin="0x1234567890123456789012345678901234567890",
            decimals=18,
        )
        assert config.decimals == 18
        assert config.token_type == B20TokenType.ASSET

    def test_stablecoin_config(self):
        config = B20TokenConfig(
            name="Test USD",
            symbol="tUSD",
            token_type=B20TokenType.STABLECOIN,
            admin="0x1234567890123456789012345678901234567890",
            currency_code="USD",
        )
        assert config.decimals == 6  # Fixed for stablecoin
        assert config.currency_code == "USD"

    def test_stablecoin_requires_currency_code(self):
        with pytest.raises(ValueError, match="Currency code required"):
            B20TokenConfig(
                name="Test",
                symbol="TST",
                token_type=B20TokenType.STABLECOIN,
                admin="0x1234",
            )

    def test_invalid_decimals(self):
        with pytest.raises(ValueError, match="Decimals must be 6-18"):
            B20TokenConfig(
                name="Test",
                symbol="TST",
                token_type=B20TokenType.ASSET,
                admin="0x1234",
                decimals=2,
            )

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="name is required"):
            B20TokenConfig(name="", symbol="TST")


class TestB20Role:
    """Tests for B20Role."""

    def test_role_values(self):
        assert B20Role.ADMIN.value == "admin"
        assert B20Role.MINTER.value == "minter"
        assert B20Role.BURNER.value == "burner"

    def test_role_hash(self):
        """Role hashes should be 32 bytes."""
        for role in B20Role:
            assert len(role.role_hash) == 32


class TestB20TokenInfo:
    """Tests for B20TokenInfo."""

    def test_has_supply_cap(self):
        info = B20TokenInfo(
            address="0x1234",
            name="Test",
            symbol="TST",
            decimals=18,
            token_type=B20TokenType.ASSET,
            supply_cap=1_000_000,
            total_supply=500_000,
        )
        assert info.has_supply_cap is True
        assert info.remaining_mintable == 500_000

    def test_no_supply_cap(self):
        info = B20TokenInfo(
            address="0x1234",
            name="Test",
            symbol="TST",
            decimals=18,
            token_type=B20TokenType.ASSET,
            supply_cap=0,
        )
        assert info.has_supply_cap is False
        assert info.remaining_mintable == -1


class TestB20TransferEvent:
    """Tests for B20TransferEvent."""

    def test_regular_transfer(self):
        event = B20TransferEvent(
            token_address="0xtoken",
            from_address="0xsender",
            to_address="0xreceiver",
            amount=1000,
            block_number=100,
            tx_hash="0xhash",
            log_index=0,
        )
        assert not event.is_mint
        assert not event.is_burn

    def test_mint_event(self):
        event = B20TransferEvent(
            token_address="0xtoken",
            from_address="0x0000000000000000000000000000000000000000",
            to_address="0xreceiver",
            amount=1000,
            block_number=100,
            tx_hash="0xhash",
            log_index=0,
        )
        assert event.is_mint
        assert not event.is_burn

    def test_burn_event(self):
        event = B20TransferEvent(
            token_address="0xtoken",
            from_address="0xsender",
            to_address="0x0000000000000000000000000000000000000000",
            amount=1000,
            block_number=100,
            tx_hash="0xhash",
            log_index=0,
        )
        assert not event.is_mint
        assert event.is_burn


class TestBatchOperations:
    """Tests for batch CSV parsing."""

    def test_parse_csv(self):
        csv = """address,amount
0x1234567890123456789012345678901234567890,1000
0x0987654321098765432109876543210987654321,2000
"""
        requests = B20BatchOperations.parse_csv_recipients(csv)
        assert len(requests) == 2
        assert requests[0].amount == 1000
        assert requests[1].amount == 2000

    def test_parse_csv_skip_comments(self):
        csv = """# This is a comment
0x1234567890123456789012345678901234567890,1000
"""
        requests = B20BatchOperations.parse_csv_recipients(csv)
        assert len(requests) == 1

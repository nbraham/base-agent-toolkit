"""Tests for DeFi module."""

from decimal import Decimal

import pytest

from base_agent_toolkit.defi.swap import (
    SwapProtocol,
    SwapQuote,
    calculate_min_amount_out,
)
from base_agent_toolkit.defi.portfolio import (
    PortfolioSnapshot,
    PortfolioTracker,
    TokenPosition,
)
from base_agent_toolkit.types import TokenAmount


class TestSwapQuote:
    """Tests for SwapQuote."""

    def test_exchange_rate(self):
        quote = SwapQuote(
            protocol=SwapProtocol.AERODROME,
            token_in="0xA",
            token_out="0xB",
            amount_in=1000,
            amount_out=2000,
            price_impact=0.1,
            gas_estimate=200_000,
            route=["0xA", "0xB"],
        )
        assert quote.exchange_rate == Decimal("2")

    def test_zero_amount_in(self):
        quote = SwapQuote(
            protocol=SwapProtocol.AERODROME,
            token_in="0xA",
            token_out="0xB",
            amount_in=0,
            amount_out=0,
            price_impact=0.0,
            gas_estimate=200_000,
            route=["0xA", "0xB"],
        )
        assert quote.exchange_rate == Decimal("0")

    def test_acceptable_slippage(self):
        quote = SwapQuote(
            protocol=SwapProtocol.UNISWAP_V3,
            token_in="0xA",
            token_out="0xB",
            amount_in=1000,
            amount_out=990,
            price_impact=1.0,
            gas_estimate=200_000,
            route=["0xA", "0xB"],
        )
        assert quote.is_acceptable

    def test_high_slippage(self):
        quote = SwapQuote(
            protocol=SwapProtocol.AERODROME,
            token_in="0xA",
            token_out="0xB",
            amount_in=1000,
            amount_out=900,
            price_impact=10.0,
            gas_estimate=200_000,
            route=["0xA", "0xB"],
        )
        assert not quote.is_acceptable


class TestSlippageCalc:
    """Tests for slippage calculation."""

    def test_half_percent(self):
        result = calculate_min_amount_out(10000, 0.5)
        assert result == 9950

    def test_one_percent(self):
        result = calculate_min_amount_out(10000, 1.0)
        assert result == 9900

    def test_zero_slippage(self):
        result = calculate_min_amount_out(10000, 0.0)
        assert result == 10000


class TestPortfolio:
    """Tests for portfolio tracking."""

    def test_snapshot_total_positions(self):
        snapshot = PortfolioSnapshot(
            wallet_address="0x1234",
            eth_balance=TokenAmount(raw=1_000_000_000_000_000_000, decimals=18, symbol="ETH"),
            token_positions=[
                TokenPosition(
                    address="0xUSDC",
                    symbol="USDC",
                    balance=TokenAmount(raw=1000_000_000, decimals=6, symbol="USDC"),
                ),
            ],
        )
        assert snapshot.total_positions == 2

    def test_non_zero_filter(self):
        snapshot = PortfolioSnapshot(
            wallet_address="0x1234",
            eth_balance=TokenAmount(raw=0, decimals=18, symbol="ETH"),
            token_positions=[
                TokenPosition(
                    address="0xA",
                    symbol="A",
                    balance=TokenAmount(raw=100, decimals=18, symbol="A"),
                ),
                TokenPosition(
                    address="0xB",
                    symbol="B",
                    balance=TokenAmount(raw=0, decimals=18, symbol="B"),
                ),
            ],
        )
        non_zero = snapshot.get_non_zero()
        assert len(non_zero) == 1
        assert non_zero[0].symbol == "A"

    def test_position_formatted(self):
        pos = TokenPosition(
            address="0xUSDC",
            symbol="USDC",
            balance=TokenAmount(raw=1_500_000, decimals=6, symbol="USDC"),
            usd_value=Decimal("1.50"),
        )
        assert "USDC" in pos.formatted
        assert "$" in pos.formatted

"""Tests for type aliases and data structures."""

from decimal import Decimal

from base_agent_toolkit.types import (
    GasEstimate,
    Network,
    TokenAmount,
    TokenInfo,
    TokenStandard,
    TransactionResult,
)


class TestTokenAmount:
    """Tests for TokenAmount dataclass."""

    def test_from_wei(self):
        amount = TokenAmount(raw=1_000_000_000_000_000_000, decimals=18, symbol="ETH")
        assert amount.ether == Decimal("1")

    def test_from_ether(self):
        amount = TokenAmount.from_ether("1.5", decimals=18, symbol="ETH")
        assert amount.raw == 1_500_000_000_000_000_000

    def test_usdc_decimals(self):
        amount = TokenAmount(raw=1_000_000, decimals=6, symbol="USDC")
        assert amount.ether == Decimal("1")

    def test_formatted_output(self):
        amount = TokenAmount(raw=1_500_000, decimals=6, symbol="USDC")
        assert "1.5" in str(amount)
        assert "USDC" in str(amount)

    def test_from_ether_small_amount(self):
        amount = TokenAmount.from_ether("0.001", decimals=18, symbol="ETH")
        assert amount.raw == 1_000_000_000_000_000

    def test_zero_amount(self):
        amount = TokenAmount(raw=0, decimals=18, symbol="ETH")
        assert amount.ether == Decimal("0")


class TestTransactionResult:
    def test_success(self):
        result = TransactionResult(
            hash="0x1234",
            block_number=100,
            gas_used=21000,
            status=True,
        )
        assert result.success is True

    def test_failed(self):
        result = TransactionResult(hash="0x1234", status=False)
        assert result.success is False

    def test_pending(self):
        result = TransactionResult(hash="0x1234")
        assert result.success is False
        assert result.status is None

    def test_explorer_url(self):
        result = TransactionResult(hash="0xabc123")
        assert "basescan.org" in result.explorer_url
        assert "0xabc123" in result.explorer_url


class TestGasEstimate:
    def test_cost_calculation(self):
        estimate = GasEstimate(
            gas_limit=21000,
            max_fee_per_gas=1_000_000_000,  # 1 gwei
            max_priority_fee_per_gas=100_000_000,
            estimated_cost_wei=21_000_000_000_000,
        )
        assert estimate.estimated_cost_gwei == 21000.0

    def test_cost_in_ether(self):
        estimate = GasEstimate(
            gas_limit=21000,
            max_fee_per_gas=1_000_000_000,
            max_priority_fee_per_gas=100_000_000,
            estimated_cost_wei=21_000_000_000_000,
        )
        assert estimate.estimated_cost_ether == Decimal("0.000021")


class TestNetwork:
    def test_mainnet(self):
        assert Network.MAINNET.value == "mainnet"

    def test_sepolia(self):
        assert Network.SEPOLIA.value == "sepolia"


class TestTokenInfo:
    def test_creation(self):
        info = TokenInfo(
            address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            name="USD Coin",
            symbol="USDC",
            decimals=6,
        )
        assert info.symbol == "USDC"
        assert info.standard == TokenStandard.ERC20

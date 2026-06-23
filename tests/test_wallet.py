"""Tests for wallet module."""

from unittest.mock import MagicMock, patch

import pytest

from base_agent_toolkit.wallet.wallet import BaseWallet
from base_agent_toolkit.wallet.erc20 import ERC20Token, ERC20_ABI
from base_agent_toolkit.wallet.gas import GasOracle, GasPriceInfo
from base_agent_toolkit.wallet.hd import generate_mnemonic
from base_agent_toolkit.wallet.tx_builder import TransactionBuilder
from base_agent_toolkit.exceptions import WalletError


class TestBaseWallet:
    """Tests for BaseWallet class."""

    def test_create_new_wallet(self):
        """Test creating a new random wallet."""
        provider = MagicMock()
        provider.chain_id = 8453
        wallet = BaseWallet.create(provider)
        assert wallet.address.startswith("0x")
        assert len(wallet.address) == 42

    def test_from_private_key(self):
        """Test loading wallet from private key."""
        provider = MagicMock()
        provider.chain_id = 8453
        pk = "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        wallet = BaseWallet.from_private_key(pk, provider)
        assert wallet.address == "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

    def test_from_private_key_with_prefix(self):
        """Test loading wallet with 0x prefix."""
        provider = MagicMock()
        provider.chain_id = 8453
        pk = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        wallet = BaseWallet.from_private_key(pk, provider)
        assert wallet.address.startswith("0x")

    def test_invalid_private_key(self):
        """Test that invalid private key raises error."""
        provider = MagicMock()
        provider.chain_id = 8453
        with pytest.raises(WalletError, match="Invalid private key"):
            BaseWallet.from_private_key("invalid", provider)

    def test_wallet_repr(self):
        """Test wallet string representation."""
        provider = MagicMock()
        provider.chain_id = 8453
        wallet = BaseWallet.create(provider)
        assert "BaseWallet" in repr(wallet)
        assert wallet.address in repr(wallet)

    def test_nonce_reset(self):
        """Test nonce cache reset."""
        provider = MagicMock()
        provider.chain_id = 8453
        wallet = BaseWallet.create(provider)
        wallet._nonce = 5
        wallet.reset_nonce()
        assert wallet._nonce is None


class TestGasPriceInfo:
    """Tests for GasPriceInfo."""

    def test_max_fee_calculation(self):
        info = GasPriceInfo(
            base_fee_gwei=1.0,
            priority_fee_gwei=0.1,
            gas_price_gwei=1.1,
            block_number=1000,
        )
        # max_fee = 1.0 * 1.25 + 0.1 = 1.35
        assert abs(info.max_fee_gwei - 1.35) < 0.01

    def test_wei_conversion(self):
        info = GasPriceInfo(
            base_fee_gwei=1.0,
            priority_fee_gwei=0.1,
            gas_price_gwei=1.1,
            block_number=1000,
        )
        assert info.priority_fee_wei == 100_000_000  # 0.1 gwei


class TestTransactionBuilder:
    """Tests for TransactionBuilder."""

    def test_add_eth_transfer(self):
        wallet = MagicMock()
        builder = TransactionBuilder(wallet)
        builder.add_eth_transfer("0x1234", amount_wei=1000)
        assert builder.count == 1

    def test_clear(self):
        wallet = MagicMock()
        builder = TransactionBuilder(wallet)
        builder.add_eth_transfer("0x1234", amount_wei=1000)
        builder.clear()
        assert builder.count == 0

    def test_preview(self):
        wallet = MagicMock()
        builder = TransactionBuilder(wallet)
        builder.add_eth_transfer("0x1234", amount_wei=1000, description="Test")
        preview = builder.preview()
        assert len(preview) == 1
        assert preview[0]["description"] == "Test"

    def test_chaining(self):
        wallet = MagicMock()
        builder = TransactionBuilder(wallet)
        result = (
            builder
            .add_eth_transfer("0x1234", amount_wei=1000)
            .add_eth_transfer("0x5678", amount_wei=2000)
        )
        assert result is builder
        assert builder.count == 2


class TestMnemonic:
    """Tests for mnemonic generation."""

    def test_generate_12_words(self):
        mnemonic = generate_mnemonic(128)
        words = mnemonic.split()
        assert len(words) == 12

    def test_generate_24_words(self):
        mnemonic = generate_mnemonic(256)
        words = mnemonic.split()
        assert len(words) == 24

"""Tests for security module."""

import pytest

from base_agent_toolkit.security.validation import (
    validate_address,
    validate_private_key,
    validate_tx_value,
    sanitize_calldata,
)


class TestValidateAddress:
    """Tests for address validation."""

    def test_valid_address(self):
        addr = "0x4200000000000000000000000000000000000006"
        result = validate_address(addr)
        assert result.startswith("0x")
        assert len(result) == 42

    def test_empty_address(self):
        with pytest.raises(ValueError, match="empty"):
            validate_address("")

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid"):
            validate_address("not-an-address")

    def test_too_short(self):
        with pytest.raises(ValueError, match="Invalid"):
            validate_address("0x1234")


class TestValidatePrivateKey:
    """Tests for private key validation."""

    def test_valid_key_with_prefix(self):
        key = "0x" + "a" * 64
        result = validate_private_key(key)
        assert result.startswith("0x")
        assert len(result) == 66

    def test_valid_key_without_prefix(self):
        key = "b" * 64
        result = validate_private_key(key)
        assert result == "0x" + "b" * 64

    def test_empty_key(self):
        with pytest.raises(ValueError, match="empty"):
            validate_private_key("")

    def test_invalid_length(self):
        with pytest.raises(ValueError, match="Invalid"):
            validate_private_key("0x1234")


class TestValidateTxValue:
    """Tests for transaction value validation."""

    def test_valid_value(self):
        assert validate_tx_value(10**18)  # 1 ETH

    def test_exceeds_max(self):
        with pytest.raises(ValueError, match="exceeds"):
            validate_tx_value(101 * 10**18)  # 101 ETH > 100 max

    def test_negative_value(self):
        with pytest.raises(ValueError, match="negative"):
            validate_tx_value(-1)

    def test_zero(self):
        assert validate_tx_value(0)


class TestSanitizeCalldata:
    """Tests for calldata sanitization."""

    def test_empty_data(self):
        assert "empty" in sanitize_calldata("0x")

    def test_with_selector(self):
        data = "0x095ea7b3" + "0" * 128
        result = sanitize_calldata(data)
        assert "0x095ea7b3" in result
        assert "bytes" in result

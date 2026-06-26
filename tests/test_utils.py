"""Tests for utility modules."""

import time

import pytest

from base_agent_toolkit.utils.rate_limiter import RateLimiter
from base_agent_toolkit.utils.retry import retry_with_backoff
from base_agent_toolkit.utils.formatting import (
    format_wei,
    format_address,
    format_tx_hash,
    format_gas_price,
    format_usd,
    format_percentage,
)


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_allows_within_limit(self):
        rl = RateLimiter(max_calls=5, window_seconds=1.0)
        for _ in range(5):
            wait = rl.acquire()
            assert wait == 0.0

    def test_remaining_count(self):
        rl = RateLimiter(max_calls=3, window_seconds=1.0)
        assert rl.remaining == 3
        rl.acquire()
        assert rl.remaining == 2

    def test_can_proceed(self):
        rl = RateLimiter(max_calls=1, window_seconds=1.0)
        assert rl.can_proceed()
        rl.acquire()
        assert not rl.can_proceed()

    def test_reset(self):
        rl = RateLimiter(max_calls=1, window_seconds=10.0)
        rl.acquire()
        assert rl.remaining == 0
        rl.reset()
        assert rl.remaining == 1


class TestRetry:
    """Tests for retry_with_backoff."""

    def test_no_retry_on_success(self):
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def success():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = success()
        assert result == "ok"
        assert call_count == 1

    def test_retries_on_failure(self):
        call_count = 0

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("fail")
            return "ok"

        result = fails_twice()
        assert result == "ok"
        assert call_count == 3

    def test_exhausted_retries(self):
        @retry_with_backoff(max_retries=1, base_delay=0.01)
        def always_fails():
            raise RuntimeError("always fails")

        with pytest.raises(RuntimeError, match="always fails"):
            always_fails()


class TestFormatting:
    """Tests for formatting utilities."""

    def test_format_wei_eth(self):
        result = format_wei(10**18)
        assert result == "1"

    def test_format_wei_small(self):
        result = format_wei(1000)
        assert "0.00" in result

    def test_format_wei_zero(self):
        assert format_wei(0) == "0"

    def test_format_wei_usdc(self):
        result = format_wei(1_500_000, decimals=6)
        assert "1.5" in result

    def test_format_address(self):
        addr = "0x4200000000000000000000000000000000000006"
        result = format_address(addr)
        assert result.startswith("0x4200")
        assert result.endswith("0006")
        assert "..." in result

    def test_format_gas_price(self):
        assert "gwei" in format_gas_price(12.5)

    def test_format_usd(self):
        assert "$" in format_usd(1234.56)

    def test_format_percentage(self):
        result = format_percentage(5.5)
        assert result == "5.50%"

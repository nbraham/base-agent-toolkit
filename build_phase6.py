"""Phase 6: Security, Utils, Examples, Polish - Commits 76-90"""
import subprocess, os

ROOT = "/work/projects/base-agent-toolkit"
os.chdir(ROOT)

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)

def commit(msg):
    subprocess.run(["git", "add", "-A"], check=True, cwd=ROOT)
    subprocess.run(["git", "commit", "-m", msg], check=True, cwd=ROOT)
    print(f"  ✓ {msg}")

# --- Commit 76: Security module ---
write("src/base_agent_toolkit/security/__init__.py", '''"""Security utilities for Base Agent Toolkit.

Provides key management, input validation, and security helpers.
"""

from .validation import (
    validate_address,
    validate_private_key,
    validate_tx_value,
    is_contract_address,
)
from .keystore import SecureKeystore

__all__ = [
    "validate_address",
    "validate_private_key",
    "validate_tx_value",
    "is_contract_address",
    "SecureKeystore",
]
''')

write("src/base_agent_toolkit/security/validation.py", '''"""Input validation and security checks."""

from __future__ import annotations

import re
from typing import Any

from web3 import Web3

from ..exceptions import WalletError
from ..logging import get_logger

logger = get_logger(__name__)

# Known phishing / honeypot contract patterns
BLACKLISTED_METHODS = {
    "0x095ea7b3",  # approve (not blacklisted, but monitored)
}

# Maximum transaction value guards
MAX_ETH_PER_TX = 100  # ETH
MAX_TOKEN_APPROVAL = 2**128  # Reasonable max approval


def validate_address(address: str) -> str:
    """Validate and checksum an Ethereum address.

    Args:
        address: Raw address string.

    Returns:
        Checksummed address.

    Raises:
        ValueError: If address is invalid.
    """
    if not address:
        raise ValueError("Address cannot be empty")

    if not re.match(r"^0x[0-9a-fA-F]{40}$", address):
        raise ValueError(f"Invalid address format: {address}")

    try:
        return Web3.to_checksum_address(address)
    except ValueError as e:
        raise ValueError(f"Invalid checksum: {e}")


def validate_private_key(key: str) -> str:
    """Validate a private key format.

    Args:
        key: Private key string.

    Returns:
        Normalized private key (with 0x prefix).

    Raises:
        ValueError: If key is invalid.
    """
    if not key:
        raise ValueError("Private key cannot be empty")

    clean = key.strip()
    if not clean.startswith("0x"):
        clean = f"0x{clean}"

    if not re.match(r"^0x[0-9a-fA-F]{64}$", clean):
        raise ValueError("Invalid private key format (expected 64 hex chars)")

    return clean


def validate_tx_value(
    value_wei: int,
    max_eth: float = MAX_ETH_PER_TX,
) -> bool:
    """Validate a transaction value is within safe limits.

    Args:
        value_wei: Transaction value in wei.
        max_eth: Maximum allowed value in ETH.

    Returns:
        True if within limits.

    Raises:
        ValueError: If value exceeds limit.
    """
    max_wei = int(max_eth * 10**18)
    if value_wei > max_wei:
        raise ValueError(
            f"Transaction value {value_wei / 10**18:.4f} ETH "
            f"exceeds maximum {max_eth} ETH"
        )
    if value_wei < 0:
        raise ValueError("Transaction value cannot be negative")
    return True


def is_contract_address(
    address: str,
    provider: Any,
) -> bool:
    """Check if an address is a contract (has code).

    Args:
        address: Address to check.
        provider: BaseProvider instance.

    Returns:
        True if address has code deployed.
    """
    checksummed = validate_address(address)
    code = provider.w3.eth.get_code(checksummed)
    return len(code) > 0


def sanitize_calldata(data: bytes | str) -> str:
    """Sanitize transaction calldata for logging.

    Masks potentially sensitive data while preserving
    the function selector for debugging.

    Args:
        data: Raw calldata.

    Returns:
        Sanitized string representation.
    """
    if isinstance(data, bytes):
        data = data.hex()

    if not data or data == "0x":
        return "0x (empty)"

    selector = data[:10] if len(data) >= 10 else data
    return f"{selector}...({len(data) // 2} bytes)"
''')

commit("feat(security): add address and private key validation utilities")

# --- Commit 77: Secure keystore ---
write("src/base_agent_toolkit/security/keystore.py", '''"""Encrypted keystore for private keys."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..logging import get_logger

logger = get_logger(__name__)


@dataclass
class KeystoreEntry:
    """A single keystore entry."""

    name: str
    address: str
    encrypted_key: str
    created_at: str


class SecureKeystore:
    """Encrypted keystore for managing private keys.

    Stores private keys encrypted on disk. Keys are only
    decrypted when needed for signing.

    Args:
        keystore_dir: Directory to store encrypted keys.
    """

    def __init__(self, keystore_dir: str = "~/.base-agent-toolkit/keys"):
        self._dir = Path(os.path.expanduser(keystore_dir))
        self._dir.mkdir(parents=True, exist_ok=True)
        logger.debug("keystore.initialized", path=str(self._dir))

    def store(
        self,
        name: str,
        private_key: str,
        password: str,
    ) -> str:
        """Store a private key encrypted with a password.

        Args:
            name: Key name/label.
            private_key: Private key to encrypt.
            password: Encryption password.

        Returns:
            Address derived from the key.
        """
        from eth_account import Account

        # Derive address
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"
        account = Account.from_key(private_key)
        address = account.address

        # Encrypt with web3 keystore format
        encrypted = Account.encrypt(private_key, password)

        # Save to file
        keyfile = self._dir / f"{name}.json"
        with open(keyfile, "w") as f:
            json.dump(
                {
                    "name": name,
                    "address": address,
                    "keystore": encrypted,
                },
                f,
                indent=2,
            )

        logger.info(
            "keystore.stored",
            name=name,
            address=address[:10],
        )

        return address

    def load(self, name: str, password: str) -> str:
        """Load and decrypt a private key.

        Args:
            name: Key name/label.
            password: Decryption password.

        Returns:
            Decrypted private key.

        Raises:
            FileNotFoundError: If key not found.
            ValueError: If password is wrong.
        """
        from eth_account import Account

        keyfile = self._dir / f"{name}.json"
        if not keyfile.exists():
            raise FileNotFoundError(f"Key '{name}' not found")

        with open(keyfile) as f:
            data = json.load(f)

        try:
            private_key = Account.decrypt(data["keystore"], password)
            return f"0x{private_key.hex()}"
        except ValueError:
            raise ValueError(f"Wrong password for key '{name}'")

    def list_keys(self) -> list[dict[str, str]]:
        """List all stored keys (without private key data).

        Returns:
            List of {name, address} dicts.
        """
        keys = []
        for keyfile in self._dir.glob("*.json"):
            try:
                with open(keyfile) as f:
                    data = json.load(f)
                keys.append({
                    "name": data.get("name", keyfile.stem),
                    "address": data.get("address", "unknown"),
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return keys

    def delete(self, name: str) -> bool:
        """Delete a stored key.

        Args:
            name: Key name to delete.

        Returns:
            True if deleted, False if not found.
        """
        keyfile = self._dir / f"{name}.json"
        if keyfile.exists():
            keyfile.unlink()
            logger.info("keystore.deleted", name=name)
            return True
        return False

    def __repr__(self) -> str:
        count = len(list(self._dir.glob("*.json")))
        return f"SecureKeystore(keys={count})"
''')

commit("feat(security): implement encrypted keystore for private key management")

# --- Commit 78: Rate limiter utility ---
write("src/base_agent_toolkit/utils/__init__.py", '''"""Utility modules for Base Agent Toolkit."""

from .rate_limiter import RateLimiter
from .retry import retry_with_backoff
from .formatting import format_wei, format_address, format_tx_hash

__all__ = [
    "RateLimiter",
    "retry_with_backoff",
    "format_wei",
    "format_address",
    "format_tx_hash",
]
''')

write("src/base_agent_toolkit/utils/rate_limiter.py", '''"""Rate limiter for API and RPC calls."""

from __future__ import annotations

import time
from collections import deque
from threading import Lock

from ..logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter.

    Limits the number of calls within a sliding time window.

    Args:
        max_calls: Maximum number of calls per window.
        window_seconds: Time window in seconds.
    """

    def __init__(self, max_calls: int = 10, window_seconds: float = 1.0):
        self._max_calls = max_calls
        self._window = window_seconds
        self._calls: deque[float] = deque()
        self._lock = Lock()

    def acquire(self) -> float:
        """Acquire a rate limit token.

        Blocks until a call is allowed.

        Returns:
            Wait time in seconds (0 if immediate).
        """
        with self._lock:
            now = time.monotonic()

            # Remove expired entries
            while self._calls and self._calls[0] <= now - self._window:
                self._calls.popleft()

            if len(self._calls) < self._max_calls:
                self._calls.append(now)
                return 0.0

            # Need to wait
            wait_until = self._calls[0] + self._window
            wait_time = wait_until - now

        if wait_time > 0:
            time.sleep(wait_time)

        with self._lock:
            self._calls.append(time.monotonic())

        return wait_time

    def can_proceed(self) -> bool:
        """Check if a call can proceed without blocking.

        Returns:
            True if within rate limit.
        """
        with self._lock:
            now = time.monotonic()
            while self._calls and self._calls[0] <= now - self._window:
                self._calls.popleft()
            return len(self._calls) < self._max_calls

    @property
    def remaining(self) -> int:
        """Number of remaining calls in current window."""
        with self._lock:
            now = time.monotonic()
            while self._calls and self._calls[0] <= now - self._window:
                self._calls.popleft()
            return max(0, self._max_calls - len(self._calls))

    def reset(self) -> None:
        """Reset the rate limiter."""
        with self._lock:
            self._calls.clear()

    def __repr__(self) -> str:
        return f"RateLimiter(max={self._max_calls}, window={self._window}s)"
''')

commit("feat(utils): add token bucket rate limiter")

# --- Commit 79: Retry utility ---
write("src/base_agent_toolkit/utils/retry.py", '''"""Retry utilities with exponential backoff."""

from __future__ import annotations

import functools
import random
import time
from typing import Any, Callable, Type

from ..logging import get_logger

logger = get_logger(__name__)


def retry_with_backoff(
    func: Callable | None = None,
    *,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[Type[Exception], ...] = (Exception,),
) -> Any:
    """Retry a function with exponential backoff.

    Can be used as a decorator or called directly.

    Args:
        func: Function to retry.
        max_retries: Maximum number of retries.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay in seconds.
        exponential_base: Base for exponential calculation.
        jitter: Add random jitter to prevent thundering herd.
        retryable_exceptions: Exception types to retry on.

    Returns:
        Decorated function or wrapper.

    Example:
        @retry_with_backoff(max_retries=5)
        def flaky_call():
            ...
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            "retry.exhausted",
                            function=fn.__name__,
                            attempts=attempt + 1,
                            error=str(e),
                        )
                        raise

                    # Calculate delay
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay,
                    )

                    if jitter:
                        delay = delay * (0.5 + random.random())

                    logger.warning(
                        "retry.attempt",
                        function=fn.__name__,
                        attempt=attempt + 1,
                        delay=f"{delay:.2f}s",
                        error=str(e),
                    )

                    time.sleep(delay)

            raise last_exception  # Should not reach here

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
''')

commit("feat(utils): add retry with exponential backoff and jitter")

# --- Commit 80: Formatting utilities ---
write("src/base_agent_toolkit/utils/formatting.py", '''"""Formatting utilities for display and logging."""

from __future__ import annotations

from decimal import Decimal


def format_wei(wei: int, decimals: int = 18) -> str:
    """Format a wei amount to human-readable string.

    Args:
        wei: Raw amount in wei.
        decimals: Token decimals (18 for ETH).

    Returns:
        Formatted string (e.g., "1.234567" ETH).
    """
    if decimals == 0:
        return str(wei)

    human = Decimal(wei) / Decimal(10**decimals)

    # Use appropriate precision
    if human == 0:
        return "0"
    elif human < Decimal("0.000001"):
        return f"{human:.18f}".rstrip("0").rstrip(".")
    elif human < Decimal("1"):
        return f"{human:.8f}".rstrip("0").rstrip(".")
    elif human < Decimal("1000"):
        return f"{human:.6f}".rstrip("0").rstrip(".")
    else:
        return f"{human:,.4f}".rstrip("0").rstrip(".")


def format_address(address: str, chars: int = 6) -> str:
    """Shorten an address for display.

    Args:
        address: Full Ethereum address.
        chars: Number of chars to show on each end.

    Returns:
        Shortened address (e.g., "0x1234...5678").
    """
    if len(address) <= chars * 2 + 4:
        return address
    return f"{address[:chars + 2]}...{address[-chars:]}"


def format_tx_hash(tx_hash: str) -> str:
    """Shorten a transaction hash for display.

    Args:
        tx_hash: Full transaction hash.

    Returns:
        Shortened hash (e.g., "0xabcd...ef12").
    """
    return format_address(tx_hash, chars=8)


def format_gas_price(gwei: float) -> str:
    """Format a gas price in gwei.

    Args:
        gwei: Gas price in gwei.

    Returns:
        Formatted string (e.g., "12.5 gwei").
    """
    if gwei < 0.01:
        return f"{gwei:.4f} gwei"
    elif gwei < 1:
        return f"{gwei:.3f} gwei"
    else:
        return f"{gwei:.2f} gwei"


def format_usd(amount: float | Decimal) -> str:
    """Format a USD amount.

    Args:
        amount: USD amount.

    Returns:
        Formatted string (e.g., "$1,234.56").
    """
    if isinstance(amount, Decimal):
        amount = float(amount)

    if amount < 0.01:
        return f"${amount:.6f}"
    elif amount < 1:
        return f"${amount:.4f}"
    else:
        return f"${amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a percentage value.

    Args:
        value: Percentage (e.g., 5.5 = 5.5%).
        decimals: Decimal places.

    Returns:
        Formatted string (e.g., "5.50%").
    """
    return f"{value:.{decimals}f}%"
''')

commit("feat(utils): add formatting helpers for wei, addresses, and gas prices")

# --- Commit 81: Security tests ---
write("tests/test_security.py", '''"""Tests for security module."""

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
''')

commit("test(security): add tests for validation and sanitization utilities")

# --- Commit 82: Utils tests ---
write("tests/test_utils.py", '''"""Tests for utility modules."""

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
''')

commit("test(utils): add tests for rate limiter, retry, and formatting helpers")

# --- Commit 83: Example - Full Agent Setup ---
write("examples/full_agent.py", '''#!/usr/bin/env python3
"""Example: Complete AI agent setup on Base.

Demonstrates:
1. Creating an agent with budget controls
2. Registering strategies
3. Running the executor
4. Tracking results

Usage:
    python examples/full_agent.py
"""

from base_agent_toolkit.agent import (
    AgentConfig,
    AgentExecutor,
    BaseAgent,
)
from base_agent_toolkit.agent.strategies import DCAStrategy
from base_agent_toolkit.agent.tools import list_tools


def main():
    """Run a complete agent demo."""
    print("=" * 60)
    print("  Base Agent Toolkit — Full Agent Demo")
    print("=" * 60)

    # 1. Create agent
    config = AgentConfig(
        name="demo-agent",
        description="Demo trading agent for Base L2",
        dry_run=True,
        daily_budget_wei=10**17,  # 0.1 ETH
    )
    agent = BaseAgent(config)

    print(f"\n🤖 Agent: {agent.name}")
    print(f"   Dry Run: {agent.is_dry_run}")
    print(f"   Budget:  0.1 ETH/day")

    # 2. List available tools
    print("\n🔧 Available Tools:")
    for tool in list_tools():
        print(f"   • {tool['name']}: {tool['description']}")

    # 3. Set up DCA strategy
    dca = DCAStrategy(
        token_in="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC
        token_out="0x4200000000000000000000000000000000000006",  # WETH
        amount_per_interval=50 * 10**6,  # 50 USDC
        interval_seconds=86400,  # Daily
    )

    print(f"\n📈 Strategy: {dca.name}")
    print(f"   {dca.description}")

    # 4. Run executor
    executor = AgentExecutor(agent, [dca])
    results = executor.run_once()

    print("\n📊 Execution Results:")
    for result in results:
        status_emoji = "✅" if result.is_success else "❌"
        print(f"   {status_emoji} {result.message}")

    # 5. Summary
    summary = executor.get_summary()
    print(f"\n📋 Summary:")
    print(f"   Total executions: {summary['total_executions']}")
    for status, count in summary["by_status"].items():
        print(f"   {status}: {count}")

    # 6. Agent status
    status = agent.get_status()
    print(f"\n🔍 Agent Status:")
    print(f"   TX Count:   {status['tx_count']}")
    print(f"   Spent:      {status['spent_today_wei']} wei")
    print(f"   Budget:     {status['budget_remaining_wei']}")


if __name__ == "__main__":
    main()
''')

commit("examples(agent): add complete AI agent setup and execution demo")

# --- Commit 84: Example - x402 payment ---
write("examples/x402_payment.py", '''#!/usr/bin/env python3
"""Example: x402 HTTP payment flow.

Demonstrates the x402 payment protocol:
1. Making a request to a paid API
2. Handling 402 Payment Required
3. Signing and attaching payment
4. Reviewing payment history

Usage:
    python examples/x402_payment.py
"""


def main():
    """Demo x402 payment flow."""
    print("=" * 60)
    print("  x402 Payment Protocol Demo")
    print("=" * 60)

    print("\\n📋 x402 Flow:")
    print("   1. Agent sends HTTP request to paid resource")
    print("   2. Server responds: 402 Payment Required")
    print("   3. Agent signs payment authorization")
    print("   4. Agent retries with X-PAYMENT header")
    print("   5. Server verifies and returns resource")

    print("\\n🔐 Payment Requirements (example):")
    print("   ┌──────────────────────────────────────┐")
    print("   │ Scheme:   exact                      │")
    print("   │ Network:  base                       │")
    print("   │ Amount:   0.001 ETH                  │")
    print("   │ Pay To:   0x7890...abcd               │")
    print("   │ Resource: /api/v1/market-data         │")
    print("   └──────────────────────────────────────┘")

    print("\\n📝 Usage:")
    print("   from base_agent_toolkit.x402 import X402Client, X402Config")
    print("   ")
    print("   client = X402Client(X402Config(")
    print("       private_key='0x...',")
    print("       auto_pay=True,")
    print("       max_payment_wei=10**16,  # Max 0.01 ETH")
    print("   ))")
    print("   ")
    print("   # Automatically handles 402 responses")
    print("   response = client.get('https://api.example.com/data')")

    print("\\n✅ x402 enables AI agents to access paid resources")
    print("   without manual payment setup!")


if __name__ == "__main__":
    main()
''')

commit("examples(x402): add x402 payment protocol demo")

# --- Commit 85: Example - B20 token deployment ---
write("examples/b20_deploy.py", '''#!/usr/bin/env python3
"""Example: Deploy a B20 token on Base.

Demonstrates:
1. Configuring a B20 token
2. Deploying via B20Factory
3. Managing roles and permissions
4. Minting and transferring tokens

Usage:
    python examples/b20_deploy.py
"""


def main():
    """Demo B20 token deployment."""
    print("=" * 60)
    print("  B20 Token Deployment Guide")
    print("  Base Native Token Standard (Beryl Upgrade)")
    print("=" * 60)

    print("\\n📋 What is B20?")
    print("   B20 is Base's native token standard introduced in")
    print("   the Beryl upgrade (June 2026). It provides:")
    print("   • Gas-efficient via Rust precompiles")
    print("   • Built-in role management (admin, minter, pauser)")
    print("   • ERC-2612 permit support")
    print("   • Optional supply cap")
    print("   • Stablecoin variant with currency code")

    print("\\n🔧 Step 1: Configure Token")
    print("   config = B20TokenConfig(")
    print("       name='My Token',")
    print("       symbol='MTK',")
    print("       token_type=B20TokenType.ASSET,")
    print("       admin=wallet.address,")
    print("       decimals=18,")
    print("       supply_cap=1_000_000 * 10**18,")
    print("   )")

    print("\\n🏭 Step 2: Deploy via Factory")
    print("   factory = B20Factory(provider)")
    print("   tx = factory.build_deploy_tx(config)")
    print("   result = wallet.sign_and_send(tx)")

    print("\\n🔑 Step 3: Manage Roles")
    print("   token = B20Token(token_address, provider)")
    print("   token.grant_role(MINTER_ROLE, minter_address)")

    print("\\n💰 Step 4: Mint Tokens")
    print("   token.mint(recipient, 1000 * 10**18)")

    print("\\n✅ Token deployed and ready for use!")


if __name__ == "__main__":
    main()
''')

commit("examples(b20): add B20 token deployment walkthrough")

# --- Commit 86: conftest.py for tests ---
write("tests/conftest.py", '''"""Shared test fixtures for Base Agent Toolkit."""

import os

import pytest

from base_agent_toolkit.agent.base import AgentConfig, BaseAgent


# ============================================================
# Environment fixtures
# ============================================================


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Ensure tests don't use real credentials."""
    monkeypatch.delenv("BAT_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("BAT_RPC_URL", raising=False)


@pytest.fixture
def test_private_key():
    """Deterministic test private key (NOT for real use)."""
    return "0x" + "a" * 64


@pytest.fixture
def test_address():
    """Known address for testing."""
    return "0x4200000000000000000000000000000000000006"


# ============================================================
# Agent fixtures
# ============================================================


@pytest.fixture
def dry_run_agent():
    """Agent in dry-run mode."""
    config = AgentConfig(
        name="test-agent",
        dry_run=True,
        daily_budget_wei=10**18,  # 1 ETH
    )
    return BaseAgent(config)


@pytest.fixture
def live_agent():
    """Agent in live mode (for testing, no wallet)."""
    config = AgentConfig(
        name="live-test-agent",
        dry_run=False,
    )
    return BaseAgent(config)


# ============================================================
# Token fixtures
# ============================================================


@pytest.fixture
def usdc_address():
    """USDC on Base mainnet."""
    return "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"


@pytest.fixture
def weth_address():
    """WETH on Base mainnet."""
    return "0x4200000000000000000000000000000000000006"
''')

commit("test: add shared conftest.py with common test fixtures")

# --- Commit 87: Makefile ---
write("Makefile", '''# Base Agent Toolkit — Development Commands

.PHONY: install test lint format typecheck clean docs

# Install development dependencies
install:
	pip install -e ".[dev]"

# Run all tests
test:
	pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	pytest tests/ -v --tb=short --cov=src/base_agent_toolkit --cov-report=term-missing

# Lint code
lint:
	ruff check src/ tests/

# Auto-fix lint issues
fix:
	ruff check --fix src/ tests/

# Format code
format:
	ruff format src/ tests/

# Type checking
typecheck:
	mypy src/base_agent_toolkit

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Quick check (lint + test)
check: lint test

# Full CI check
ci: lint typecheck test
''')

commit("build: add Makefile with development workflow commands")

# --- Commit 88: Docker support ---
write("Dockerfile", '''# Base Agent Toolkit — Docker Image

FROM python:3.12-slim AS base

# Metadata
LABEL maintainer="nbraham"
LABEL description="Base Agent Toolkit — Python SDK for AI agents on Base L2"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \\
    apt-get install -y --no-install-recommends gcc && \\
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy source
COPY src/ src/
COPY examples/ examples/

# Default command
ENTRYPOINT ["python", "-m", "base_agent_toolkit.cli.main"]
CMD ["info"]

# ---
# Development stage
FROM base AS dev

COPY tests/ tests/
COPY Makefile .

RUN pip install --no-cache-dir -e ".[dev]"

CMD ["pytest", "-v"]
''')

write(".dockerignore", '''__pycache__
*.pyc
.git
.env
.venv
.mypy_cache
.pytest_cache
.ruff_cache
dist
build
*.egg-info
''')

commit("build: add Dockerfile and .dockerignore for containerized deployment")

# --- Commit 89: GitHub Actions ---
write(".github/workflows/ci.yml", '''name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint with ruff
        run: ruff check src/ tests/

      - name: Type check with mypy
        run: mypy src/base_agent_toolkit --ignore-missing-imports
        continue-on-error: true

      - name: Run tests
        run: pytest tests/ -v --tb=short

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check src/ tests/
      - run: ruff format --check src/ tests/
''')

commit("ci: add GitHub Actions workflow for multi-version testing and linting")

# --- Commit 90: CHANGELOG update ---
write("CHANGELOG.md", '''# Changelog

All notable changes to Base Agent Toolkit will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] — 2026-06-28

### Added

#### Core
- Project structure with `pyproject.toml`, CI/CD, Docker support
- Comprehensive type system (`TokenAmount`, `GasEstimate`, `TransactionResult`)
- Structured logging with module-level loggers
- Configuration loader with environment variable support
- Custom exception hierarchy for all modules

#### Wallet
- `BaseWallet` — key management, ETH transfers, message signing
- `ERC20Token` — token balance, transfer, approval operations
- `HDWallet` — BIP39 mnemonic, BIP44 derivation, multi-account
- `ContractWrapper` — generic contract interaction
- `TransactionBuilder` — EIP-1559 transaction construction
- `GasOracle` — dynamic gas estimation with fee history

#### B20 Token Standard
- `B20Factory` — deploy asset and stablecoin B20 tokens
- `B20Token` — full ERC-20 + B20 extensions (roles, pause, cap)
- ERC-2612 permit support (gasless approvals)
- Event listener for Transfer/Approval events
- Batch operations (airdrop, multi-mint)

#### DeFi Integrations
- `AerodromeRouter` — swap quotes and transactions on Aerodrome
- `UniswapV3Router` — Uniswap V3 swaps with fee tier optimization
- `MorphoClient` — supply/withdraw on Morpho Blue lending
- `ApprovalManager` — check, grant, and revoke token approvals
- `WETHHelper` — wrap/unwrap ETH ↔ WETH
- `PortfolioTracker` — track balances across tokens

#### AI Agent Framework
- `BaseAgent` — core agent with budget management and action logging
- `AgentExecutor` — run strategies with evaluation and error handling
- `DCAStrategy` — dollar cost averaging implementation
- `RebalanceStrategy` — portfolio rebalancing with drift detection
- Pre-built tools: balance check, transfer, swap

#### x402 Payment Protocol
- `X402Client` — HTTP client with automatic 402 payment handling
- `X402Middleware` — server-side payment verification
- Payment header construction and signature verification

#### Security
- Address and private key validation
- Transaction value guards
- Encrypted keystore for key storage

#### CLI
- `bat info` — show toolkit info
- `bat wallet create/balance/mnemonic` — wallet operations
- `bat b20 configure` — preview B20 token config
- `bat agent status/tools` — agent management

#### Infrastructure
- GitHub Actions CI (Python 3.10-3.12)
- Docker support (production + dev stages)
- Comprehensive test suite (6 test modules)
- Documentation guides (B20, DeFi, AI Agents)
- Code examples (swap, agent, x402, B20)
''')

commit("docs: update CHANGELOG with complete v0.1.0 release notes")

print("\\n=== Phase 6 complete! ===")
result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True, cwd=ROOT)
lines = result.stdout.strip().splitlines()
print(f"Total commits: {len(lines)}")

"""Rate limiter for API and RPC calls."""

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

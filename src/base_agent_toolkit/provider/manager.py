"""Provider manager with failover and rate limiting."""

from __future__ import annotations

import time
from threading import Lock
from typing import Any, Callable, TypeVar

from ..constants import DEFAULT_RPC_URLS, RPC_REQUEST_TIMEOUT_SECONDS
from ..exceptions import AllProvidersFailedError, ProviderError, RateLimitError
from ..logging import get_logger
from .base import BaseProvider

logger = get_logger(__name__)

T = TypeVar("T")


class ProviderManager:
    """Manages multiple RPC providers with automatic failover and rate limiting.

    If the primary provider fails, automatically switches to the next available
    fallback. Implements basic rate limiting to avoid hitting provider limits.

    Args:
        rpc_urls: List of RPC endpoint URLs (first is primary).
        chain_id: Chain ID for the network.
        max_retries: Maximum retries per request across all providers.
        requests_per_second: Rate limit for requests.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        rpc_urls: list[str] | None = None,
        chain_id: int = 8453,
        max_retries: int = 3,
        requests_per_second: float = 10.0,
        timeout: int = RPC_REQUEST_TIMEOUT_SECONDS,
    ):
        if rpc_urls is None:
            rpc_urls = DEFAULT_RPC_URLS.get(chain_id, [])

        if not rpc_urls:
            raise ProviderError(f"No RPC URLs provided for chain {chain_id}")

        self.chain_id = chain_id
        self.max_retries = max_retries
        self.min_interval = 1.0 / requests_per_second
        self._last_request_time = 0.0
        self._lock = Lock()
        self._current_index = 0

        self._providers = [
            BaseProvider(rpc_url=url, chain_id=chain_id, timeout=timeout)
            for url in rpc_urls
        ]

        logger.info(
            "provider_manager.initialized",
            provider_count=len(self._providers),
            chain_id=chain_id,
        )

    @property
    def current(self) -> BaseProvider:
        """Get the currently active provider."""
        return self._providers[self._current_index]

    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self._last_request_time = time.monotonic()

    def _rotate_provider(self) -> None:
        """Switch to the next available provider."""
        old_index = self._current_index
        self._current_index = (self._current_index + 1) % len(self._providers)
        logger.warning(
            "provider_manager.rotated",
            from_url=self._providers[old_index].rpc_url,
            to_url=self._providers[self._current_index].rpc_url,
        )

    def execute(self, method: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a provider method with failover and rate limiting.

        Args:
            method: Name of the BaseProvider method to call.
            *args: Positional arguments for the method.
            **kwargs: Keyword arguments for the method.

        Returns:
            Result from the provider method.

        Raises:
            AllProvidersFailedError: If all providers fail.
        """
        errors: list[str] = []

        for attempt in range(self.max_retries):
            self._rate_limit()
            provider = self.current

            try:
                fn = getattr(provider, method)
                result = fn(*args, **kwargs)
                return result
            except Exception as e:
                error_msg = f"{provider.rpc_url}: {e}"
                errors.append(error_msg)
                logger.warning(
                    "provider_manager.request_failed",
                    provider=provider.rpc_url,
                    method=method,
                    attempt=attempt + 1,
                    error=str(e),
                )
                self._rotate_provider()

        raise AllProvidersFailedError(
            f"All providers failed after {self.max_retries} attempts: "
            + "; ".join(errors)
        )

    def get_healthy_provider(self) -> BaseProvider | None:
        """Find the first connected provider.

        Returns:
            A connected BaseProvider, or None if all are down.
        """
        for provider in self._providers:
            if provider.is_connected():
                return provider
        return None

    @property
    def provider_count(self) -> int:
        """Number of configured providers."""
        return len(self._providers)

    def __repr__(self) -> str:
        return (
            f"ProviderManager(providers={self.provider_count}, "
            f"current={self.current.rpc_url!r})"
        )

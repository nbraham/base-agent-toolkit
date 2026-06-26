"""Retry utilities with exponential backoff."""

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

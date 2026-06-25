"""Custom exceptions for Base Agent Toolkit."""

from __future__ import annotations

from typing import Any


class BaseAgentError(Exception):
    """Base exception for all toolkit errors."""

    def __init__(self, message: str = "", details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


# ============================================================
# Provider Errors
# ============================================================

class ProviderError(BaseAgentError):
    """RPC provider error."""
    pass


class AllProvidersFailedError(ProviderError):
    """All configured providers failed."""
    pass


class RateLimitError(ProviderError):
    """Provider rate limit exceeded."""
    pass


# ============================================================
# Wallet Errors
# ============================================================

class WalletError(BaseAgentError):
    """Wallet-related error."""
    pass


class InsufficientFundsError(WalletError):
    """Insufficient funds for a transaction."""

    def __init__(
        self,
        required: int = 0,
        available: int = 0,
        token: str = "ETH",
        **kwargs: Any,
    ):
        self.required = required
        self.available = available
        self.token = token
        message = f"Insufficient {token}: need {required}, have {available}"
        super().__init__(message, **kwargs)


# ============================================================
# Transaction Errors
# ============================================================

class TransactionError(BaseAgentError):
    """Transaction-related error."""
    pass


class TransactionTimeoutError(TransactionError):
    """Transaction was not mined within timeout."""

    def __init__(self, message: str = "", tx_hash: str = "", **kwargs: Any):
        self.tx_hash = tx_hash
        super().__init__(message, **kwargs)


class TransactionRevertedError(TransactionError):
    """Transaction reverted on-chain."""

    def __init__(
        self, message: str = "", tx_hash: str = "", reason: str = "", **kwargs: Any
    ):
        self.tx_hash = tx_hash
        self.reason = reason
        super().__init__(message, **kwargs)


# ============================================================
# Contract Errors
# ============================================================

class ContractError(BaseAgentError):
    """Smart contract interaction error."""
    pass


class ContractNotFoundError(ContractError):
    """No contract found at address."""
    pass


# ============================================================
# B20 Errors
# ============================================================

class B20Error(BaseAgentError):
    """B20 token standard error."""
    pass


class B20DeploymentError(B20Error):
    """B20 token deployment error."""
    pass


class B20PermissionError(B20Error):
    """B20 role/permission error."""
    pass


# ============================================================
# DeFi Errors
# ============================================================

class DeFiError(BaseAgentError):
    """DeFi protocol interaction error."""
    pass


class SlippageExceededError(DeFiError):
    """Swap slippage exceeded limit."""

    def __init__(
        self,
        expected: int = 0,
        actual: int = 0,
        slippage_percent: float = 0,
        **kwargs: Any,
    ):
        self.expected = expected
        self.actual = actual
        self.slippage_percent = slippage_percent
        message = (
            f"Slippage exceeded: expected {expected}, got {actual} "
            f"({slippage_percent:.2f}% slippage)"
        )
        super().__init__(message, **kwargs)


# ============================================================
# x402 Errors
# ============================================================

class X402Error(BaseAgentError):
    """x402 payment protocol error."""
    pass


class X402PaymentError(X402Error):
    """x402 payment failed or rejected."""

    def __init__(self, message: str = "", requirements: Any = None, **kwargs: Any):
        self.requirements = requirements
        super().__init__(message, **kwargs)

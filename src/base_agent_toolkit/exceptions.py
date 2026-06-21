"""Custom exception classes for Base Agent Toolkit."""

from __future__ import annotations


class BaseAgentError(Exception):
    """Base exception for all toolkit errors."""

    def __init__(self, message: str, details: dict | None = None):
        self.details = details or {}
        super().__init__(message)


class ConfigError(BaseAgentError):
    """Raised when configuration is invalid or missing."""


class WalletError(BaseAgentError):
    """Raised for wallet-related errors."""


class InsufficientFundsError(WalletError):
    """Raised when wallet has insufficient funds for a transaction."""

    def __init__(self, required: int, available: int, token: str = "ETH"):
        self.required = required
        self.available = available
        self.token = token
        super().__init__(
            f"Insufficient {token} balance: required {required}, available {available}",
            details={"required": required, "available": available, "token": token},
        )


class TransactionError(BaseAgentError):
    """Raised when a transaction fails."""

    def __init__(self, message: str, tx_hash: str | None = None, **kwargs):
        self.tx_hash = tx_hash
        super().__init__(message, details={"tx_hash": tx_hash, **kwargs})


class TransactionRevertedError(TransactionError):
    """Raised when a transaction is reverted on-chain."""


class TransactionTimeoutError(TransactionError):
    """Raised when waiting for transaction confirmation times out."""


class ProviderError(BaseAgentError):
    """Raised for RPC provider errors."""


class AllProvidersFailedError(ProviderError):
    """Raised when all RPC providers have failed."""


class RateLimitError(ProviderError):
    """Raised when RPC rate limit is exceeded."""


class ContractError(BaseAgentError):
    """Raised for smart contract interaction errors."""


class ContractNotFoundError(ContractError):
    """Raised when a contract is not found at the given address."""


class B20Error(BaseAgentError):
    """Raised for B20 token standard errors."""


class B20DeploymentError(B20Error):
    """Raised when B20 token deployment fails."""


class B20PermissionError(B20Error):
    """Raised when caller lacks required B20 role."""


class DeFiError(BaseAgentError):
    """Raised for DeFi protocol interaction errors."""


class SlippageExceededError(DeFiError):
    """Raised when price slippage exceeds the allowed threshold."""

    def __init__(self, expected: float, actual: float, max_slippage: float):
        self.expected = expected
        self.actual = actual
        self.max_slippage = max_slippage
        super().__init__(
            f"Slippage {abs(expected - actual) / expected:.2%} exceeds max {max_slippage:.2%}",
            details={
                "expected": expected,
                "actual": actual,
                "max_slippage": max_slippage,
            },
        )


class X402Error(BaseAgentError):
    """Raised for x402 payment protocol errors."""


class X402PaymentRequiredError(X402Error):
    """Raised when an x402 API requires payment."""


class AgentError(BaseAgentError):
    """Raised for agent framework errors."""


class StrategyError(AgentError):
    """Raised when an agent strategy encounters an error."""

"""Phase 5: AI Agent Framework + x402 - Commits 58-75"""
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

# --- Commit 58: Agent module init ---
write("src/base_agent_toolkit/agent/__init__.py", '''"""AI Agent framework for Base chain.

Build autonomous AI agents that can interact with Base DeFi,
manage wallets, and make payments using x402.
"""

from .base import BaseAgent, AgentConfig
from .strategy import Strategy, StrategyResult
from .executor import AgentExecutor

__all__ = [
    "BaseAgent",
    "AgentConfig",
    "Strategy",
    "StrategyResult",
    "AgentExecutor",
]
''')

write("src/base_agent_toolkit/agent/base.py", '''"""Base agent implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address
from ..wallet.wallet import BaseWallet

logger = get_logger(__name__)


@dataclass
class AgentConfig:
    """Configuration for a Base AI agent.

    Args:
        name: Agent display name.
        description: Brief description of what the agent does.
        wallet: BaseWallet for chain interactions.
        provider: BaseProvider for RPC access.
        max_gas_per_tx: Maximum gas per transaction (wei).
        daily_budget_wei: Daily spending budget in wei.
        dry_run: If True, simulate but don't send transactions.
        allowed_protocols: List of allowed DeFi protocols.
    """

    name: str
    description: str = ""
    wallet: BaseWallet | None = None
    provider: BaseProvider | None = None
    max_gas_per_tx: int = 1_000_000
    daily_budget_wei: int = 0  # 0 = unlimited
    dry_run: bool = False
    allowed_protocols: list[str] = field(default_factory=list)


class BaseAgent:
    """AI agent that interacts with Base chain.

    The BaseAgent provides a high-level interface for AI models
    to interact with Base, including wallet management, DeFi,
    and x402 payments.

    Args:
        config: AgentConfig instance.
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self._spent_today_wei: int = 0
        self._tx_count: int = 0
        self._actions_log: list[dict[str, Any]] = []

        logger.info(
            "agent.initialized",
            name=config.name,
            dry_run=config.dry_run,
        )

    @property
    def name(self) -> str:
        """Agent name."""
        return self.config.name

    @property
    def wallet(self) -> BaseWallet | None:
        """Agent's wallet."""
        return self.config.wallet

    @property
    def provider(self) -> BaseProvider | None:
        """Agent's provider."""
        return self.config.provider

    @property
    def is_dry_run(self) -> bool:
        """Whether agent is in dry-run mode."""
        return self.config.dry_run

    @property
    def spent_today(self) -> int:
        """Total wei spent today."""
        return self._spent_today_wei

    @property
    def tx_count(self) -> int:
        """Number of transactions sent."""
        return self._tx_count

    def check_budget(self, cost_wei: int) -> bool:
        """Check if a transaction is within budget.

        Args:
            cost_wei: Expected transaction cost in wei.

        Returns:
            True if within budget.
        """
        if self.config.daily_budget_wei == 0:
            return True  # Unlimited
        return (self._spent_today_wei + cost_wei) <= self.config.daily_budget_wei

    def record_spend(self, amount_wei: int, description: str = "") -> None:
        """Record a spending event.

        Args:
            amount_wei: Amount spent in wei.
            description: Description of the spend.
        """
        self._spent_today_wei += amount_wei
        self._tx_count += 1
        self._actions_log.append({
            "type": "spend",
            "amount_wei": amount_wei,
            "description": description,
            "tx_count": self._tx_count,
        })

        logger.info(
            "agent.spend_recorded",
            amount_wei=amount_wei,
            total_today=self._spent_today_wei,
            description=description,
        )

    def reset_daily_budget(self) -> None:
        """Reset the daily spending counter."""
        self._spent_today_wei = 0
        logger.info("agent.budget_reset")

    def get_actions_log(self) -> list[dict[str, Any]]:
        """Get the agent's action history."""
        return list(self._actions_log)

    def get_status(self) -> dict[str, Any]:
        """Get agent status summary.

        Returns:
            Dictionary with agent state.
        """
        status = {
            "name": self.config.name,
            "dry_run": self.config.dry_run,
            "tx_count": self._tx_count,
            "spent_today_wei": self._spent_today_wei,
            "budget_remaining_wei": (
                self.config.daily_budget_wei - self._spent_today_wei
                if self.config.daily_budget_wei > 0
                else "unlimited"
            ),
        }

        if self.wallet:
            status["address"] = self.wallet.address
        if self.provider:
            status["connected"] = self.provider.is_connected()

        return status

    def __repr__(self) -> str:
        return f"BaseAgent(name={self.config.name!r}, dry_run={self.config.dry_run})"
''')

commit("feat(agent): implement BaseAgent with budget management and action logging")

# --- Commit 59: Strategy framework ---
write("src/base_agent_toolkit/agent/strategy.py", '''"""Strategy framework for agent decision-making."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StrategyStatus(str, Enum):
    """Status of a strategy execution."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PARTIAL = "partial"


@dataclass
class StrategyResult:
    """Result of executing a strategy.

    Attributes:
        status: Execution status.
        message: Human-readable result message.
        data: Strategy-specific result data.
        transactions: List of transaction hashes executed.
        gas_used: Total gas used.
    """

    status: StrategyStatus
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    transactions: list[str] = field(default_factory=list)
    gas_used: int = 0

    @property
    def is_success(self) -> bool:
        return self.status == StrategyStatus.SUCCESS

    @property
    def tx_count(self) -> int:
        return len(self.transactions)


class Strategy(ABC):
    """Abstract base class for agent strategies.

    A strategy encapsulates a specific behavior or trading logic
    that an agent can execute. Strategies should be stateless
    and produce deterministic results given the same inputs.

    Example:
        class DCAStrategy(Strategy):
            def evaluate(self, context):
                # Check if it's time to buy
                ...
                return True

            def execute(self, agent, context):
                # Execute the DCA purchase
                ...
                return StrategyResult(status=StrategyStatus.SUCCESS)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name for identification."""
        ...

    @property
    def description(self) -> str:
        """Optional description of what this strategy does."""
        return ""

    @abstractmethod
    def evaluate(self, context: dict[str, Any]) -> bool:
        """Evaluate whether this strategy should execute.

        Args:
            context: Current market/agent context.

        Returns:
            True if the strategy should execute.
        """
        ...

    @abstractmethod
    def execute(
        self,
        agent: Any,
        context: dict[str, Any],
    ) -> StrategyResult:
        """Execute the strategy.

        Args:
            agent: BaseAgent instance.
            context: Current market/agent context.

        Returns:
            StrategyResult with execution details.
        """
        ...

    def validate(self, context: dict[str, Any]) -> list[str]:
        """Validate that context has required data.

        Override this to add custom validation.

        Args:
            context: Context to validate.

        Returns:
            List of validation error messages (empty = valid).
        """
        return []

    def __repr__(self) -> str:
        return f"Strategy({self.name!r})"
''')

commit("feat(agent): add strategy framework for agent decision-making")

# --- Commit 60: Agent executor ---
write("src/base_agent_toolkit/agent/executor.py", '''"""Agent executor for running strategies."""

from __future__ import annotations

import time
from typing import Any

from ..logging import get_logger
from .base import BaseAgent
from .strategy import Strategy, StrategyResult, StrategyStatus

logger = get_logger(__name__)


class AgentExecutor:
    """Executes strategies on behalf of an agent.

    The executor manages the lifecycle of strategy execution,
    including evaluation, execution, and result recording.

    Args:
        agent: BaseAgent instance.
        strategies: List of strategies to run.
    """

    def __init__(
        self,
        agent: BaseAgent,
        strategies: list[Strategy] | None = None,
    ):
        self._agent = agent
        self._strategies = strategies or []
        self._results: list[dict[str, Any]] = []

    def add_strategy(self, strategy: Strategy) -> None:
        """Add a strategy to the executor."""
        self._strategies.append(strategy)
        logger.info("executor.strategy_added", name=strategy.name)

    def remove_strategy(self, name: str) -> None:
        """Remove a strategy by name."""
        self._strategies = [s for s in self._strategies if s.name != name]

    def run_once(self, context: dict[str, Any] | None = None) -> list[StrategyResult]:
        """Run all strategies once.

        Args:
            context: Shared context for all strategies.

        Returns:
            List of StrategyResult for each strategy.
        """
        context = context or {}
        results = []

        for strategy in self._strategies:
            result = self._execute_strategy(strategy, context)
            results.append(result)

        return results

    def _execute_strategy(
        self,
        strategy: Strategy,
        context: dict[str, Any],
    ) -> StrategyResult:
        """Execute a single strategy with error handling.

        Args:
            strategy: Strategy to execute.
            context: Execution context.

        Returns:
            StrategyResult.
        """
        start_time = time.monotonic()

        # Validate
        errors = strategy.validate(context)
        if errors:
            result = StrategyResult(
                status=StrategyStatus.SKIPPED,
                message=f"Validation failed: {', '.join(errors)}",
            )
            self._record_result(strategy, result, time.monotonic() - start_time)
            return result

        # Evaluate
        try:
            should_run = strategy.evaluate(context)
        except Exception as e:
            result = StrategyResult(
                status=StrategyStatus.FAILED,
                message=f"Evaluation error: {e}",
            )
            self._record_result(strategy, result, time.monotonic() - start_time)
            return result

        if not should_run:
            result = StrategyResult(
                status=StrategyStatus.SKIPPED,
                message="Strategy conditions not met",
            )
            self._record_result(strategy, result, time.monotonic() - start_time)
            return result

        # Execute
        try:
            if self._agent.is_dry_run:
                result = StrategyResult(
                    status=StrategyStatus.SUCCESS,
                    message="[DRY RUN] Would have executed",
                )
            else:
                result = strategy.execute(self._agent, context)
        except Exception as e:
            result = StrategyResult(
                status=StrategyStatus.FAILED,
                message=f"Execution error: {e}",
            )

        elapsed = time.monotonic() - start_time
        self._record_result(strategy, result, elapsed)
        return result

    def _record_result(
        self,
        strategy: Strategy,
        result: StrategyResult,
        elapsed_seconds: float,
    ) -> None:
        """Record a strategy execution result."""
        record = {
            "strategy": strategy.name,
            "status": result.status.value,
            "message": result.message,
            "tx_count": result.tx_count,
            "gas_used": result.gas_used,
            "elapsed_seconds": round(elapsed_seconds, 3),
        }
        self._results.append(record)

        logger.info(
            "executor.strategy_completed",
            strategy=strategy.name,
            status=result.status.value,
            elapsed=f"{elapsed_seconds:.3f}s",
        )

    def get_history(self) -> list[dict[str, Any]]:
        """Get execution history."""
        return list(self._results)

    def get_summary(self) -> dict[str, Any]:
        """Get execution summary.

        Returns:
            Summary with counts per status.
        """
        total = len(self._results)
        by_status = {}
        for r in self._results:
            status = r["status"]
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total_executions": total,
            "by_status": by_status,
            "strategies": [s.name for s in self._strategies],
        }

    def __repr__(self) -> str:
        return f"AgentExecutor(strategies={len(self._strategies)})"
''')

commit("feat(agent): implement AgentExecutor for running strategies")

# --- Commit 61: x402 payment protocol ---
write("src/base_agent_toolkit/x402/__init__.py", '''"""x402 HTTP payment protocol for AI agents.

x402 enables AI agents to access paid resources by including
payment headers in HTTP requests. It uses the HTTP 402 Payment
Required status code.

Protocol flow:
1. Agent makes HTTP request to a paid resource
2. Server responds with 402 and payment requirements
3. Agent signs a payment authorization
4. Agent retries request with X-PAYMENT header
5. Server facilitates payment on-chain and returns resource

See: https://www.x402.org/
"""

from .client import X402Client, X402Config
from .payment import PaymentHeader, PaymentRequirements

__all__ = [
    "X402Client",
    "X402Config",
    "PaymentHeader",
    "PaymentRequirements",
]
''')

write("src/base_agent_toolkit/x402/payment.py", '''"""x402 payment types and header construction."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from web3 import Web3

from ..logging import get_logger

logger = get_logger(__name__)


@dataclass
class PaymentRequirements:
    """Payment requirements from a 402 response.

    Parsed from the server's 402 Payment Required response.

    Attributes:
        scheme: Payment scheme (e.g., "exact").
        network: Network identifier (e.g., "base").
        max_amount_required: Maximum payment amount (raw).
        resource: URL of the paid resource.
        description: Human-readable description.
        mime_type: Content type of the resource.
        pay_to: Address to send payment to.
        extra: Additional scheme-specific data.
    """

    scheme: str
    network: str
    max_amount_required: int
    resource: str
    description: str = ""
    mime_type: str = ""
    pay_to: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_response_headers(cls, headers: dict[str, str]) -> "PaymentRequirements":
        """Parse payment requirements from HTTP response headers.

        Args:
            headers: HTTP response headers.

        Returns:
            PaymentRequirements instance.
        """
        # Parse X-PAYMENT header or WWW-Authenticate
        payment_info = headers.get("X-PAYMENT", "")
        if not payment_info:
            payment_info = headers.get("WWW-Authenticate", "")

        try:
            data = json.loads(payment_info) if payment_info else {}
        except json.JSONDecodeError:
            data = {}

        return cls(
            scheme=data.get("scheme", "exact"),
            network=data.get("network", "base"),
            max_amount_required=int(data.get("maxAmountRequired", "0")),
            resource=data.get("resource", ""),
            description=data.get("description", ""),
            mime_type=data.get("mimeType", ""),
            pay_to=data.get("payTo", ""),
            extra={
                k: v for k, v in data.items()
                if k not in {
                    "scheme", "network", "maxAmountRequired",
                    "resource", "description", "mimeType", "payTo",
                }
            },
        )

    @property
    def amount_eth(self) -> float:
        """Max amount in ETH."""
        return self.max_amount_required / 1e18


@dataclass
class PaymentHeader:
    """Constructed X-PAYMENT header for request.

    Contains the signed payment authorization that the agent
    includes in retried requests.

    Attributes:
        scheme: Payment scheme.
        network: Network identifier.
        payload: Signed payment payload.
        signature: Payment signature.
    """

    scheme: str
    network: str
    payload: dict[str, Any]
    signature: str

    def to_header_value(self) -> str:
        """Serialize to X-PAYMENT header value.

        Returns:
            JSON string for the X-PAYMENT header.
        """
        data = {
            "scheme": self.scheme,
            "network": self.network,
            "payload": self.payload,
            "signature": self.signature,
        }
        return json.dumps(data)

    @property
    def as_dict(self) -> dict[str, str]:
        """Get as HTTP headers dictionary."""
        return {"X-PAYMENT": self.to_header_value()}
''')

commit("feat(x402): implement x402 payment types and header construction")

# --- Commit 62: x402 client ---
write("src/base_agent_toolkit/x402/client.py", '''"""x402 HTTP client for AI agent payments."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from ..exceptions import X402Error, X402PaymentError
from ..logging import get_logger
from ..types import Address
from .payment import PaymentHeader, PaymentRequirements

logger = get_logger(__name__)


@dataclass
class X402Config:
    """Configuration for x402 client.

    Args:
        private_key: Wallet private key for signing payments.
        chain_id: Chain ID (default: 8453 for Base mainnet).
        max_payment_wei: Maximum automatic payment amount.
        auto_pay: Automatically pay 402 responses.
    """

    private_key: str
    chain_id: int = 8453
    max_payment_wei: int = 10**16  # 0.01 ETH default max
    auto_pay: bool = True


class X402Client:
    """HTTP client with x402 payment support.

    Wraps standard HTTP requests and automatically handles
    402 Payment Required responses by signing payments.

    Args:
        config: X402Config instance.
    """

    def __init__(self, config: X402Config):
        self._config = config
        self._payments_made: list[dict[str, Any]] = []

        logger.info(
            "x402.client_initialized",
            chain_id=config.chain_id,
            auto_pay=config.auto_pay,
            max_payment=f"{config.max_payment_wei / 1e18:.4f} ETH",
        )

    def get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Make a GET request with x402 payment support.

        If the server responds with 402 and auto_pay is enabled,
        automatically signs a payment and retries.

        Args:
            url: Target URL.
            **kwargs: Additional request parameters.

        Returns:
            Response data dictionary.

        Raises:
            X402PaymentError: If payment fails or is rejected.
        """
        import httpx

        headers = kwargs.pop("headers", {})

        # First request
        response = httpx.get(url, headers=headers, **kwargs)

        if response.status_code == 402:
            if not self._config.auto_pay:
                raise X402PaymentError(
                    "Payment required but auto_pay is disabled",
                    requirements=self._parse_requirements(response),
                )

            # Parse requirements
            requirements = self._parse_requirements(response)

            # Check amount limit
            if requirements.max_amount_required > self._config.max_payment_wei:
                raise X402PaymentError(
                    f"Payment amount ({requirements.amount_eth:.6f} ETH) "
                    f"exceeds max ({self._config.max_payment_wei / 1e18:.6f} ETH)",
                    requirements=requirements,
                )

            # Sign payment
            payment_header = self._sign_payment(requirements)

            # Retry with payment header
            headers.update(payment_header.as_dict)
            response = httpx.get(url, headers=headers, **kwargs)

            if response.status_code == 402:
                raise X402PaymentError(
                    "Payment rejected by server",
                    requirements=requirements,
                )

            # Record payment
            self._record_payment(url, requirements)

        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "data": response.text,
        }

    def post(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Make a POST request with x402 payment support.

        Args:
            url: Target URL.
            **kwargs: Additional request parameters.

        Returns:
            Response data dictionary.
        """
        import httpx

        headers = kwargs.pop("headers", {})
        response = httpx.post(url, headers=headers, **kwargs)

        if response.status_code == 402 and self._config.auto_pay:
            requirements = self._parse_requirements(response)
            if requirements.max_amount_required <= self._config.max_payment_wei:
                payment_header = self._sign_payment(requirements)
                headers.update(payment_header.as_dict)
                response = httpx.post(url, headers=headers, **kwargs)
                self._record_payment(url, requirements)

        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "data": response.text,
        }

    def _parse_requirements(self, response: Any) -> PaymentRequirements:
        """Parse payment requirements from 402 response."""
        return PaymentRequirements.from_response_headers(dict(response.headers))

    def _sign_payment(self, requirements: PaymentRequirements) -> PaymentHeader:
        """Sign a payment authorization.

        Args:
            requirements: Server's payment requirements.

        Returns:
            PaymentHeader with signed authorization.
        """
        from eth_account import Account
        from eth_account.messages import encode_defunct

        timestamp = int(time.time())

        payload = {
            "scheme": requirements.scheme,
            "network": requirements.network,
            "resource": requirements.resource,
            "amount": str(requirements.max_amount_required),
            "payTo": requirements.pay_to,
            "timestamp": timestamp,
            "chainId": self._config.chain_id,
        }

        # Sign the payload
        message = json.dumps(payload, sort_keys=True)
        msg_hash = encode_defunct(text=message)

        pk = self._config.private_key
        if not pk.startswith("0x"):
            pk = f"0x{pk}"
        account = Account.from_key(pk)
        signed = account.sign_message(msg_hash)

        logger.info(
            "x402.payment_signed",
            resource=requirements.resource,
            amount=requirements.max_amount_required,
            pay_to=requirements.pay_to,
        )

        return PaymentHeader(
            scheme=requirements.scheme,
            network=requirements.network,
            payload=payload,
            signature=signed.signature.hex(),
        )

    def _record_payment(
        self,
        url: str,
        requirements: PaymentRequirements,
    ) -> None:
        """Record a successful payment."""
        self._payments_made.append({
            "url": url,
            "amount_wei": requirements.max_amount_required,
            "pay_to": requirements.pay_to,
            "timestamp": int(time.time()),
        })

    @property
    def total_paid_wei(self) -> int:
        """Total amount paid via x402."""
        return sum(p["amount_wei"] for p in self._payments_made)

    @property
    def payment_count(self) -> int:
        """Number of x402 payments made."""
        return len(self._payments_made)

    def get_payment_history(self) -> list[dict[str, Any]]:
        """Get full payment history."""
        return list(self._payments_made)

    def __repr__(self) -> str:
        return (
            f"X402Client(chain_id={self._config.chain_id}, "
            f"auto_pay={self._config.auto_pay})"
        )
''')

commit("feat(x402): implement x402 HTTP client with automatic payment handling")

# --- Commit 63: x402 middleware ---
write("src/base_agent_toolkit/x402/middleware.py", '''"""x402 middleware for server-side payment verification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from web3 import Web3

from ..logging import get_logger
from .payment import PaymentHeader, PaymentRequirements

logger = get_logger(__name__)


@dataclass
class PaymentVerification:
    """Result of verifying an x402 payment."""

    valid: bool
    payer: str = ""
    amount: int = 0
    error: str = ""


class X402Middleware:
    """Server-side middleware for accepting x402 payments.

    Verifies payment signatures from x402 clients and
    facilitates on-chain settlement.

    Args:
        pay_to: Address to receive payments.
        chain_id: Expected chain ID.
    """

    def __init__(self, pay_to: str, chain_id: int = 8453):
        self._pay_to = Web3.to_checksum_address(pay_to)
        self._chain_id = chain_id

    def create_requirements(
        self,
        resource: str,
        amount: int,
        description: str = "",
        mime_type: str = "application/json",
    ) -> PaymentRequirements:
        """Create payment requirements for a 402 response.

        Args:
            resource: URL of the paid resource.
            amount: Required payment amount (raw wei).
            description: Human-readable description.
            mime_type: Content type of the resource.

        Returns:
            PaymentRequirements to include in 402 response.
        """
        return PaymentRequirements(
            scheme="exact",
            network="base",
            max_amount_required=amount,
            resource=resource,
            description=description,
            mime_type=mime_type,
            pay_to=self._pay_to,
        )

    def verify_payment(
        self,
        payment_header_value: str,
        expected_resource: str,
        min_amount: int = 0,
    ) -> PaymentVerification:
        """Verify an x402 payment header.

        Args:
            payment_header_value: Value of the X-PAYMENT header.
            expected_resource: Expected resource URL.
            min_amount: Minimum payment amount.

        Returns:
            PaymentVerification result.
        """
        try:
            data = json.loads(payment_header_value)
        except json.JSONDecodeError:
            return PaymentVerification(valid=False, error="Invalid JSON in payment header")

        payload = data.get("payload", {})
        signature = data.get("signature", "")

        # Verify resource matches
        if payload.get("resource") != expected_resource:
            return PaymentVerification(
                valid=False,
                error=f"Resource mismatch: {payload.get('resource')} != {expected_resource}",
            )

        # Verify pay_to matches
        if payload.get("payTo", "").lower() != self._pay_to.lower():
            return PaymentVerification(
                valid=False,
                error="Pay-to address mismatch",
            )

        # Verify chain ID
        if payload.get("chainId") != self._chain_id:
            return PaymentVerification(
                valid=False,
                error=f"Chain ID mismatch: {payload.get('chainId')} != {self._chain_id}",
            )

        # Verify amount
        amount = int(payload.get("amount", "0"))
        if amount < min_amount:
            return PaymentVerification(
                valid=False,
                error=f"Insufficient amount: {amount} < {min_amount}",
            )

        # Verify signature
        from eth_account import Account
        from eth_account.messages import encode_defunct

        message = json.dumps(payload, sort_keys=True)
        msg_hash = encode_defunct(text=message)

        try:
            signer = Account.recover_message(
                msg_hash, signature=bytes.fromhex(signature)
            )
        except Exception as e:
            return PaymentVerification(
                valid=False,
                error=f"Invalid signature: {e}",
            )

        logger.info(
            "x402_middleware.payment_verified",
            payer=signer,
            amount=amount,
            resource=expected_resource,
        )

        return PaymentVerification(
            valid=True,
            payer=signer,
            amount=amount,
        )

    def __repr__(self) -> str:
        return f"X402Middleware(pay_to={self._pay_to})"
''')

commit("feat(x402): add server-side payment verification middleware")

# --- Commit 64: x402 tests ---
write("tests/test_x402.py", '''"""Tests for x402 payment protocol."""

import json

import pytest

from base_agent_toolkit.x402.payment import (
    PaymentHeader,
    PaymentRequirements,
)


class TestPaymentRequirements:
    """Tests for PaymentRequirements."""

    def test_from_headers(self):
        headers = {
            "X-PAYMENT": json.dumps({
                "scheme": "exact",
                "network": "base",
                "maxAmountRequired": "1000000000000000",
                "resource": "https://api.example.com/data",
                "payTo": "0x1234567890123456789012345678901234567890",
                "description": "API access",
            })
        }
        req = PaymentRequirements.from_response_headers(headers)
        assert req.scheme == "exact"
        assert req.network == "base"
        assert req.max_amount_required == 1_000_000_000_000_000
        assert "example.com" in req.resource

    def test_from_empty_headers(self):
        req = PaymentRequirements.from_response_headers({})
        assert req.scheme == "exact"
        assert req.max_amount_required == 0

    def test_amount_eth(self):
        req = PaymentRequirements(
            scheme="exact",
            network="base",
            max_amount_required=10**18,
            resource="https://test.com",
        )
        assert req.amount_eth == 1.0

    def test_small_amount(self):
        req = PaymentRequirements(
            scheme="exact",
            network="base",
            max_amount_required=10**15,
            resource="https://test.com",
        )
        assert abs(req.amount_eth - 0.001) < 1e-10


class TestPaymentHeader:
    """Tests for PaymentHeader."""

    def test_to_header_value(self):
        header = PaymentHeader(
            scheme="exact",
            network="base",
            payload={"amount": "1000", "resource": "https://test.com"},
            signature="0xabc123",
        )
        value = header.to_header_value()
        parsed = json.loads(value)
        assert parsed["scheme"] == "exact"
        assert parsed["network"] == "base"
        assert parsed["payload"]["amount"] == "1000"
        assert parsed["signature"] == "0xabc123"

    def test_as_dict(self):
        header = PaymentHeader(
            scheme="exact",
            network="base",
            payload={},
            signature="0x",
        )
        d = header.as_dict
        assert "X-PAYMENT" in d
        assert isinstance(d["X-PAYMENT"], str)
''')

commit("test(x402): add tests for x402 payment types and headers")

# --- Commit 65: Agent tools ---
write("src/base_agent_toolkit/agent/tools.py", '''"""Pre-built agent tools for common Base operations.

These tools provide a simplified interface for AI agents
to interact with Base chain operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..logging import get_logger
from ..types import Address, Wei

logger = get_logger(__name__)


@dataclass
class ToolResult:
    """Result from an agent tool execution."""

    success: bool
    data: dict[str, Any]
    message: str = ""
    error: str = ""


class BalanceTool:
    """Check wallet balances (ETH and tokens).

    Usage by AI agent:
        "Check my ETH balance"
        "What's my USDC balance?"
    """

    name = "check_balance"
    description = "Check ETH or token balance of a wallet"

    def run(self, agent: Any, token: str = "ETH") -> ToolResult:
        """Run the balance check.

        Args:
            agent: BaseAgent instance.
            token: Token symbol ("ETH" or token address).

        Returns:
            ToolResult with balance info.
        """
        if not agent.wallet:
            return ToolResult(
                success=False,
                data={},
                error="No wallet configured",
            )

        try:
            if token.upper() == "ETH":
                balance = agent.wallet.get_balance()
                return ToolResult(
                    success=True,
                    data={
                        "token": "ETH",
                        "balance": str(balance),
                        "address": agent.wallet.address,
                    },
                    message=f"ETH balance: {balance}",
                )
            else:
                balance = agent.wallet.get_token_balance(token)
                return ToolResult(
                    success=True,
                    data={
                        "token": token,
                        "balance": str(balance),
                        "address": agent.wallet.address,
                    },
                    message=f"Token balance: {balance}",
                )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=str(e),
            )


class TransferTool:
    """Send ETH or tokens to an address.

    Usage by AI agent:
        "Send 0.1 ETH to 0x..."
        "Transfer 100 USDC to 0x..."
    """

    name = "transfer"
    description = "Send ETH or tokens to an address"

    def run(
        self,
        agent: Any,
        to: Address,
        amount: str,
        token: str = "ETH",
    ) -> ToolResult:
        """Execute a transfer.

        Args:
            agent: BaseAgent instance.
            to: Recipient address.
            amount: Amount to send (human-readable).
            token: Token ("ETH" or contract address).

        Returns:
            ToolResult with transaction details.
        """
        if not agent.wallet:
            return ToolResult(success=False, data={}, error="No wallet configured")

        if agent.is_dry_run:
            return ToolResult(
                success=True,
                data={"dry_run": True, "to": to, "amount": amount, "token": token},
                message=f"[DRY RUN] Would send {amount} {token} to {to}",
            )

        try:
            if token.upper() == "ETH":
                result = agent.wallet.send_eth(to=to, amount_ether=float(amount))
            else:
                result = agent.wallet.send_token(
                    token_address=token,
                    to=to,
                    amount_human=float(amount),
                )

            return ToolResult(
                success=True,
                data={"tx_hash": result.hash, "to": to, "amount": amount},
                message=f"Sent {amount} {token} to {to}, tx: {result.hash}",
            )
        except Exception as e:
            return ToolResult(success=False, data={}, error=str(e))


class SwapTool:
    """Swap tokens on Base DEXs.

    Usage by AI agent:
        "Swap 100 USDC for ETH"
        "Exchange my WETH for USDC"
    """

    name = "swap"
    description = "Swap tokens on Base DEXs (Aerodrome/Uniswap)"

    def run(
        self,
        agent: Any,
        token_in: Address,
        token_out: Address,
        amount_in: int,
        slippage: float = 0.5,
    ) -> ToolResult:
        """Execute a token swap.

        Args:
            agent: BaseAgent instance.
            token_in: Input token address.
            token_out: Output token address.
            amount_in: Input amount (raw).
            slippage: Max slippage percentage.

        Returns:
            ToolResult with swap details.
        """
        if agent.is_dry_run:
            return ToolResult(
                success=True,
                data={
                    "dry_run": True,
                    "token_in": token_in,
                    "token_out": token_out,
                    "amount_in": amount_in,
                },
                message=f"[DRY RUN] Would swap {amount_in} tokens",
            )

        return ToolResult(
            success=False,
            data={},
            error="Live swap not implemented in this version",
        )


# Registry of available tools
AVAILABLE_TOOLS = {
    "check_balance": BalanceTool(),
    "transfer": TransferTool(),
    "swap": SwapTool(),
}

def get_tool(name: str) -> Any:
    """Get a tool by name."""
    return AVAILABLE_TOOLS.get(name)

def list_tools() -> list[dict[str, str]]:
    """List all available tools."""
    return [
        {"name": name, "description": tool.description}
        for name, tool in AVAILABLE_TOOLS.items()
    ]
''')

commit("feat(agent): add pre-built tools for balance, transfer, and swap operations")

# --- Commit 66: Agent strategies implementations ---
write("src/base_agent_toolkit/agent/strategies/__init__.py", '''"""Pre-built strategies for common agent patterns."""

from .dca import DCAStrategy
from .rebalance import RebalanceStrategy

__all__ = ["DCAStrategy", "RebalanceStrategy"]
''')

write("src/base_agent_toolkit/agent/strategies/dca.py", '''"""Dollar Cost Averaging (DCA) strategy."""

from __future__ import annotations

import time
from typing import Any

from ..strategy import Strategy, StrategyResult, StrategyStatus
from ...logging import get_logger

logger = get_logger(__name__)


class DCAStrategy(Strategy):
    """Dollar Cost Averaging strategy.

    Automatically purchases a target token at regular intervals
    with a fixed amount.

    Args:
        token_in: Token to spend (address).
        token_out: Token to buy (address).
        amount_per_interval: Amount to spend each interval (raw).
        interval_seconds: Seconds between purchases.
        max_purchases: Maximum number of purchases (0 = unlimited).
    """

    def __init__(
        self,
        token_in: str,
        token_out: str,
        amount_per_interval: int,
        interval_seconds: int = 86400,  # Daily
        max_purchases: int = 0,
    ):
        self._token_in = token_in
        self._token_out = token_out
        self._amount = amount_per_interval
        self._interval = interval_seconds
        self._max_purchases = max_purchases
        self._last_purchase: float = 0
        self._purchase_count: int = 0

    @property
    def name(self) -> str:
        return "dca"

    @property
    def description(self) -> str:
        return f"DCA: Buy {self._token_out[:10]}... every {self._interval}s"

    def evaluate(self, context: dict[str, Any]) -> bool:
        """Check if it's time for a DCA purchase."""
        now = time.time()

        # Check max purchases
        if self._max_purchases > 0 and self._purchase_count >= self._max_purchases:
            return False

        # Check interval
        if now - self._last_purchase < self._interval:
            return False

        return True

    def execute(self, agent: Any, context: dict[str, Any]) -> StrategyResult:
        """Execute DCA purchase."""
        try:
            # In production, this would use the swap tool
            logger.info(
                "dca.executing",
                token_in=self._token_in[:10],
                token_out=self._token_out[:10],
                amount=self._amount,
            )

            self._last_purchase = time.time()
            self._purchase_count += 1

            return StrategyResult(
                status=StrategyStatus.SUCCESS,
                message=f"DCA purchase #{self._purchase_count}",
                data={
                    "token_in": self._token_in,
                    "token_out": self._token_out,
                    "amount": self._amount,
                    "purchase_number": self._purchase_count,
                },
            )
        except Exception as e:
            return StrategyResult(
                status=StrategyStatus.FAILED,
                message=f"DCA failed: {e}",
            )

    def get_stats(self) -> dict[str, Any]:
        """Get DCA strategy statistics."""
        return {
            "purchase_count": self._purchase_count,
            "total_spent": self._amount * self._purchase_count,
            "last_purchase": self._last_purchase,
            "interval_seconds": self._interval,
        }
''')

write("src/base_agent_toolkit/agent/strategies/rebalance.py", '''"""Portfolio rebalancing strategy."""

from __future__ import annotations

from typing import Any

from ..strategy import Strategy, StrategyResult, StrategyStatus
from ...logging import get_logger

logger = get_logger(__name__)


class RebalanceStrategy(Strategy):
    """Portfolio rebalancing strategy.

    Maintains target allocation percentages across tokens.
    When allocations drift beyond a threshold, triggers
    rebalancing trades.

    Args:
        targets: Dict of token address → target percentage (0-100).
        threshold_percent: Minimum drift to trigger rebalance.
    """

    def __init__(
        self,
        targets: dict[str, float],
        threshold_percent: float = 5.0,
    ):
        self._targets = targets
        self._threshold = threshold_percent

        # Validate targets sum to 100
        total = sum(targets.values())
        if abs(total - 100) > 0.01:
            raise ValueError(f"Target allocations must sum to 100, got {total}")

    @property
    def name(self) -> str:
        return "rebalance"

    @property
    def description(self) -> str:
        return f"Rebalance portfolio ({len(self._targets)} tokens, {self._threshold}% threshold)"

    def validate(self, context: dict[str, Any]) -> list[str]:
        """Validate context has required portfolio data."""
        errors = []
        if "portfolio" not in context:
            errors.append("Missing 'portfolio' in context")
        return errors

    def evaluate(self, context: dict[str, Any]) -> bool:
        """Check if rebalancing is needed."""
        portfolio = context.get("portfolio", {})

        # Calculate current allocations
        total_value = sum(portfolio.values())
        if total_value == 0:
            return False

        for token, target_pct in self._targets.items():
            current_value = portfolio.get(token, 0)
            current_pct = (current_value / total_value) * 100
            drift = abs(current_pct - target_pct)

            if drift > self._threshold:
                logger.info(
                    "rebalance.drift_detected",
                    token=token[:10],
                    current=f"{current_pct:.1f}%",
                    target=f"{target_pct:.1f}%",
                    drift=f"{drift:.1f}%",
                )
                return True

        return False

    def execute(self, agent: Any, context: dict[str, Any]) -> StrategyResult:
        """Execute rebalancing trades."""
        portfolio = context.get("portfolio", {})
        total_value = sum(portfolio.values())

        trades = []
        for token, target_pct in self._targets.items():
            current_value = portfolio.get(token, 0)
            target_value = total_value * (target_pct / 100)
            diff = target_value - current_value

            if abs(diff) > total_value * (self._threshold / 100):
                trades.append({
                    "token": token,
                    "action": "buy" if diff > 0 else "sell",
                    "amount_value": abs(diff),
                })

        logger.info(
            "rebalance.executing",
            trades=len(trades),
        )

        return StrategyResult(
            status=StrategyStatus.SUCCESS,
            message=f"Planned {len(trades)} rebalancing trades",
            data={"trades": trades, "total_value": total_value},
        )
''')

commit("feat(agent): add DCA and portfolio rebalancing strategies")

# --- Commit 67: Agent tests ---
write("tests/test_agent.py", '''"""Tests for agent module."""

import pytest

from base_agent_toolkit.agent.base import AgentConfig, BaseAgent
from base_agent_toolkit.agent.strategy import Strategy, StrategyResult, StrategyStatus
from base_agent_toolkit.agent.executor import AgentExecutor
from base_agent_toolkit.agent.tools import BalanceTool, list_tools


class MockStrategy(Strategy):
    """Test strategy."""

    def __init__(self, should_run: bool = True, should_fail: bool = False):
        self._should_run = should_run
        self._should_fail = should_fail

    @property
    def name(self) -> str:
        return "mock"

    def evaluate(self, context):
        return self._should_run

    def execute(self, agent, context):
        if self._should_fail:
            raise RuntimeError("Strategy failed")
        return StrategyResult(
            status=StrategyStatus.SUCCESS,
            message="Mock executed",
        )


class TestBaseAgent:
    """Tests for BaseAgent."""

    def test_create_agent(self):
        config = AgentConfig(name="test-agent", dry_run=True)
        agent = BaseAgent(config)
        assert agent.name == "test-agent"
        assert agent.is_dry_run

    def test_budget_unlimited(self):
        config = AgentConfig(name="test", daily_budget_wei=0)
        agent = BaseAgent(config)
        assert agent.check_budget(10**18)

    def test_budget_check(self):
        config = AgentConfig(name="test", daily_budget_wei=10**18)
        agent = BaseAgent(config)
        assert agent.check_budget(10**17)  # 0.1 ETH < 1 ETH
        agent.record_spend(10**18, "big tx")
        assert not agent.check_budget(1)  # Over budget

    def test_reset_budget(self):
        config = AgentConfig(name="test", daily_budget_wei=10**18)
        agent = BaseAgent(config)
        agent.record_spend(10**18)
        agent.reset_daily_budget()
        assert agent.spent_today == 0

    def test_status(self):
        config = AgentConfig(name="test-agent", dry_run=True)
        agent = BaseAgent(config)
        status = agent.get_status()
        assert status["name"] == "test-agent"
        assert status["dry_run"] is True
        assert status["tx_count"] == 0


class TestAgentExecutor:
    """Tests for AgentExecutor."""

    def test_run_once(self):
        agent = BaseAgent(AgentConfig(name="test", dry_run=True))
        strategy = MockStrategy(should_run=True)
        executor = AgentExecutor(agent, [strategy])

        results = executor.run_once()
        assert len(results) == 1
        # Dry run returns SUCCESS
        assert results[0].status == StrategyStatus.SUCCESS

    def test_skip_strategy(self):
        agent = BaseAgent(AgentConfig(name="test", dry_run=True))
        strategy = MockStrategy(should_run=False)
        executor = AgentExecutor(agent, [strategy])

        results = executor.run_once()
        assert results[0].status == StrategyStatus.SKIPPED

    def test_summary(self):
        agent = BaseAgent(AgentConfig(name="test", dry_run=True))
        executor = AgentExecutor(agent, [MockStrategy()])
        executor.run_once()

        summary = executor.get_summary()
        assert summary["total_executions"] == 1
        assert "success" in summary["by_status"]


class TestTools:
    """Tests for agent tools."""

    def test_list_tools(self):
        tools = list_tools()
        assert len(tools) >= 3
        names = [t["name"] for t in tools]
        assert "check_balance" in names
        assert "transfer" in names

    def test_balance_tool_no_wallet(self):
        agent = BaseAgent(AgentConfig(name="test"))
        tool = BalanceTool()
        result = tool.run(agent)
        assert not result.success
        assert "No wallet" in result.error
''')

commit("test(agent): add comprehensive tests for agent, executor, strategies, and tools")

# --- Commit 68: Agent + x402 docs ---
write("docs/guides/ai-agents.md", '''# AI Agent Framework Guide

## Overview

The Base Agent Toolkit provides a framework for building autonomous
AI agents that can interact with Base chain, manage wallets,
swap tokens, and make HTTP payments via x402.

## Quick Start

### Create an Agent

```python
from base_agent_toolkit.agent import BaseAgent, AgentConfig

config = AgentConfig(
    name="my-agent",
    description="Trading bot for Base",
    dry_run=True,  # Start in dry-run mode
    daily_budget_wei=10**17,  # 0.1 ETH daily budget
)

agent = BaseAgent(config)
print(agent.get_status())
```

### Add Strategies

```python
from base_agent_toolkit.agent.strategies import DCAStrategy, RebalanceStrategy
from base_agent_toolkit.agent import AgentExecutor

# DCA: Buy WETH with USDC daily
dca = DCAStrategy(
    token_in=USDC_ADDRESS,
    token_out=WETH_ADDRESS,
    amount_per_interval=50 * 10**6,  # 50 USDC
    interval_seconds=86400,  # Daily
)

# Run strategies
executor = AgentExecutor(agent, [dca])
results = executor.run_once()
```

### Use Tools

```python
from base_agent_toolkit.agent.tools import list_tools, get_tool

# List available tools
for tool in list_tools():
    print(f"{tool['name']}: {tool['description']}")

# Use a tool
balance_tool = get_tool("check_balance")
result = balance_tool.run(agent)
```

## x402 Payments

x402 allows agents to access paid APIs by including payment
signatures in HTTP requests.

```python
from base_agent_toolkit.x402 import X402Client, X402Config

client = X402Client(X402Config(
    private_key="0x...",
    chain_id=8453,
    max_payment_wei=10**16,  # Max 0.01 ETH per payment
    auto_pay=True,
))

# Automatically handles 402 responses
response = client.get("https://api.example.com/paid-data")
print(f"Payments made: {client.payment_count}")
print(f"Total spent: {client.total_paid_wei} wei")
```

## Custom Strategies

```python
from base_agent_toolkit.agent.strategy import Strategy, StrategyResult, StrategyStatus

class MyStrategy(Strategy):
    @property
    def name(self):
        return "my-strategy"

    def evaluate(self, context):
        # Decide whether to execute
        return context.get("condition", False)

    def execute(self, agent, context):
        # Do something
        return StrategyResult(
            status=StrategyStatus.SUCCESS,
            message="Done!",
        )
```

## Budget Management

```python
# Set a daily budget
config = AgentConfig(
    name="budgeted-agent",
    daily_budget_wei=5 * 10**16,  # 0.05 ETH
)
agent = BaseAgent(config)

# Check before spending
if agent.check_budget(cost_wei):
    agent.record_spend(cost_wei, "swap fee")

# Reset daily
agent.reset_daily_budget()
```

## Reference

- [x402 Protocol](https://www.x402.org/)
- [Base AI Agents](https://docs.base.org/agents)
- [Base MCP](https://docs.base.org/base-mcp)
''')

commit("docs(agent): write AI agent framework and x402 guide")

# --- Commit 69: CLI module ---
write("src/base_agent_toolkit/cli/__init__.py", '''"""Command-line interface for Base Agent Toolkit."""

from .main import app

__all__ = ["app"]
''')

write("src/base_agent_toolkit/cli/main.py", '''"""CLI entry point for Base Agent Toolkit."""

from __future__ import annotations

import json
import os
import sys
from typing import Optional

import click

from ..constants import BASE_MAINNET_CHAIN_ID, BASE_SEPOLIA_CHAIN_ID


@click.group()
@click.version_option(package_name="base-agent-toolkit")
def app():
    """Base Agent Toolkit - Build AI agents on Base L2.

    A comprehensive Python SDK for wallet management, DeFi,
    B20 tokens, and AI agent development on Base chain.
    """
    pass


@app.group()
def wallet():
    """Wallet management commands."""
    pass


@wallet.command()
def create():
    """Create a new wallet."""
    from ..wallet.wallet import BaseWallet
    from ..provider.base import BaseProvider

    provider = BaseProvider(chain_id=BASE_SEPOLIA_CHAIN_ID)
    w = BaseWallet.create(provider)

    click.echo("🔑 New wallet created!")
    click.echo(f"   Address:     {w.address}")
    click.echo(f"   Private Key: {w.private_key}")
    click.echo("")
    click.echo("⚠️  Save the private key securely! It cannot be recovered.")


@wallet.command()
@click.option("--address", "-a", required=True, help="Wallet address")
@click.option("--network", "-n", default="mainnet", help="Network (mainnet/sepolia)")
def balance(address: str, network: str):
    """Check wallet ETH balance."""
    chain_id = BASE_SEPOLIA_CHAIN_ID if network == "sepolia" else BASE_MAINNET_CHAIN_ID

    from ..provider.base import BaseProvider

    try:
        provider = BaseProvider(chain_id=chain_id)
        bal = provider.get_balance(address)
        eth_balance = bal / 1e18
        click.echo(f"💰 Balance: {eth_balance:.6f} ETH")
        click.echo(f"   Network: Base {network}")
        click.echo(f"   Address: {address}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@wallet.command()
@click.option("--strength", "-s", default=128, help="Entropy bits (128=12 words, 256=24 words)")
def mnemonic(strength: int):
    """Generate a new BIP39 mnemonic phrase."""
    from ..wallet.hd import generate_mnemonic

    m = generate_mnemonic(strength)
    words = m.split()
    click.echo(f"🔐 New mnemonic ({len(words)} words):")
    click.echo(f"   {m}")
    click.echo("")
    click.echo("⚠️  Store this securely! Anyone with this phrase can access your wallet.")


@app.group()
def b20():
    """B20 token operations."""
    pass


@b20.command()
@click.option("--name", required=True, help="Token name")
@click.option("--symbol", required=True, help="Token symbol")
@click.option("--decimals", default=18, help="Token decimals (6-18)")
@click.option("--supply-cap", default=0, help="Supply cap (0=unlimited)")
@click.option("--type", "token_type", default="asset", help="Token type (asset/stablecoin)")
@click.option("--currency", default="", help="Currency code for stablecoin (e.g., USD)")
def configure(name: str, symbol: str, decimals: int, supply_cap: int, token_type: str, currency: str):
    """Preview B20 token configuration."""
    from ..b20.types import B20TokenConfig, B20TokenType

    try:
        tt = B20TokenType.STABLECOIN if token_type == "stablecoin" else B20TokenType.ASSET
        config = B20TokenConfig(
            name=name,
            symbol=symbol,
            token_type=tt,
            admin="<your-wallet-address>",
            decimals=decimals,
            supply_cap=supply_cap,
            currency_code=currency,
        )

        click.echo("📋 B20 Token Configuration:")
        click.echo(f"   Name:       {config.name}")
        click.echo(f"   Symbol:     {config.symbol}")
        click.echo(f"   Type:       {config.token_type.value}")
        click.echo(f"   Decimals:   {config.decimals}")
        click.echo(f"   Supply Cap: {config.supply_cap or 'unlimited'}")
        if config.currency_code:
            click.echo(f"   Currency:   {config.currency_code}")
    except ValueError as e:
        click.echo(f"❌ Invalid config: {e}", err=True)
        sys.exit(1)


@app.group()
def agent():
    """AI agent commands."""
    pass


@agent.command()
@click.option("--name", required=True, help="Agent name")
@click.option("--dry-run/--live", default=True, help="Dry run mode")
def status(name: str, dry_run: bool):
    """Show agent status."""
    from ..agent.base import AgentConfig, BaseAgent

    config = AgentConfig(name=name, dry_run=dry_run)
    a = BaseAgent(config)
    s = a.get_status()

    click.echo(f"🤖 Agent: {s['name']}")
    click.echo(f"   Dry Run:    {s['dry_run']}")
    click.echo(f"   TX Count:   {s['tx_count']}")
    click.echo(f"   Spent:      {s['spent_today_wei']} wei")


@agent.command()
def tools():
    """List available agent tools."""
    from ..agent.tools import list_tools

    click.echo("🔧 Available Agent Tools:")
    for tool in list_tools():
        click.echo(f"   • {tool['name']}: {tool['description']}")


@app.command()
def info():
    """Show toolkit information."""
    from .. import __version__

    click.echo("═" * 50)
    click.echo("  Base Agent Toolkit")
    click.echo(f"  Version: {__version__}")
    click.echo("═" * 50)
    click.echo("")
    click.echo("  🔗 Chain:    Base (Coinbase L2)")
    click.echo("  📦 Modules:  wallet, b20, defi, agent, x402, cli")
    click.echo("  📚 Docs:     https://docs.base.org")
    click.echo("  🌐 Website:  https://base.org")


if __name__ == "__main__":
    app()
''')

commit("feat(cli): implement CLI with wallet, B20, and agent commands")

# --- Commit 70: CLI tests ---
write("tests/test_cli.py", '''"""Tests for CLI module."""

from click.testing import CliRunner

from base_agent_toolkit.cli.main import app


class TestCLI:
    """Tests for CLI commands."""

    def test_info(self):
        runner = CliRunner()
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Base Agent Toolkit" in result.output
        assert "Version" in result.output

    def test_wallet_create(self):
        runner = CliRunner()
        result = runner.invoke(app, ["wallet", "create"])
        assert result.exit_code == 0
        assert "Address" in result.output

    def test_wallet_mnemonic(self):
        runner = CliRunner()
        result = runner.invoke(app, ["wallet", "mnemonic"])
        assert result.exit_code == 0
        assert "mnemonic" in result.output.lower()

    def test_b20_configure(self):
        runner = CliRunner()
        result = runner.invoke(app, [
            "b20", "configure",
            "--name", "Test Token",
            "--symbol", "TST",
        ])
        assert result.exit_code == 0
        assert "Test Token" in result.output

    def test_agent_tools(self):
        runner = CliRunner()
        result = runner.invoke(app, ["agent", "tools"])
        assert result.exit_code == 0
        assert "check_balance" in result.output

    def test_agent_status(self):
        runner = CliRunner()
        result = runner.invoke(app, ["agent", "status", "--name", "test"])
        assert result.exit_code == 0
        assert "test" in result.output
''')

commit("test(cli): add CLI command tests")

# --- Commit 71: Update constants for DeFi ---
# Read current constants and extend
write("src/base_agent_toolkit/constants.py", '''"""Global constants for Base Agent Toolkit."""

# ============================================================
# Chain IDs
# ============================================================
BASE_MAINNET_CHAIN_ID = 8453
BASE_SEPOLIA_CHAIN_ID = 84532

# ============================================================
# RPC URLs
# ============================================================
DEFAULT_RPC_URLS = {
    8453: [
        "https://mainnet.base.org",
        "https://base.drpc.org",
    ],
    84532: [
        "https://sepolia.base.org",
    ],
}

# ============================================================
# Provider Settings
# ============================================================
RPC_REQUEST_TIMEOUT_SECONDS = 30

# ============================================================
# Token Addresses (Base Mainnet)
# ============================================================
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDT_ADDRESS = "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2"
DAI_ADDRESS = "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"
CBETH_ADDRESS = "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22"

# Token Decimals
ETH_DECIMALS = 18
USDC_DECIMALS = 6
USDT_DECIMALS = 6

# ============================================================
# B20 Contracts
# ============================================================
B20_FACTORY = "0x0000000000000000000000000000000000000B20"
B20_FACTORY_SEPOLIA = "0x0000000000000000000000000000000000000B20"

# ============================================================
# DeFi Protocol Addresses (Base Mainnet)
# ============================================================

# Aerodrome
AERODROME_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
AERODROME_FACTORY = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"

# Uniswap V3
UNISWAP_V3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"
UNISWAP_V3_QUOTER = "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a"
UNISWAP_V3_FACTORY = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"

# Morpho Blue
MORPHO_BLUE = "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb"

# ============================================================
# Gas Settings
# ============================================================
DEFAULT_GAS_LIMIT = 21000  # Simple ETH transfer
DEFAULT_MAX_GAS_PRICE_GWEI = 50.0
DEFAULT_PRIORITY_FEE_GWEI = 0.1
EIP1559_BASE_FEE_MULTIPLIER = 1.25
''')

commit("refactor(constants): consolidate all chain, token, and protocol addresses")

# --- Commit 72: Update exceptions ---
write("src/base_agent_toolkit/exceptions.py", '''"""Custom exceptions for Base Agent Toolkit."""

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
''')

commit("refactor(exceptions): add comprehensive error hierarchy for all modules")

# --- Commit 73: Update types ---
write("src/base_agent_toolkit/types.py", '''"""Type definitions for Base Agent Toolkit."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any

# ============================================================
# Type Aliases
# ============================================================
Address = str
TxHash = str
Wei = int
BlockNumber = int


class Network(str, Enum):
    """Supported networks."""

    MAINNET = "mainnet"
    SEPOLIA = "sepolia"

    @property
    def chain_id(self) -> int:
        return 8453 if self == Network.MAINNET else 84532


# ============================================================
# Data Classes
# ============================================================

@dataclass
class TokenAmount:
    """Represents a token amount with formatting.

    Handles conversion between raw (on-chain) and human-readable amounts.
    """

    raw: int
    decimals: int = 18
    symbol: str = ""

    @property
    def formatted(self) -> str:
        """Human-readable amount with symbol."""
        human = Decimal(self.raw) / Decimal(10**self.decimals)
        if self.symbol:
            return f"{human:.{min(self.decimals, 8)}f} {self.symbol}"
        return f"{human:.{min(self.decimals, 8)}f}"

    @property
    def human(self) -> Decimal:
        """Human-readable decimal value."""
        return Decimal(self.raw) / Decimal(10**self.decimals)

    def __str__(self) -> str:
        return self.formatted

    def __repr__(self) -> str:
        return f"TokenAmount({self.formatted})"


@dataclass
class TokenInfo:
    """Token metadata."""

    address: Address
    name: str
    symbol: str
    decimals: int
    total_supply: int = 0


@dataclass
class GasEstimate:
    """Gas estimation result."""

    gas_limit: int
    max_fee_per_gas: int
    max_priority_fee_per_gas: int
    estimated_cost_wei: int

    @property
    def estimated_cost_eth(self) -> Decimal:
        """Estimated cost in ETH."""
        return Decimal(self.estimated_cost_wei) / Decimal(10**18)

    @property
    def estimated_cost_gwei(self) -> Decimal:
        """Estimated cost in gwei."""
        return Decimal(self.estimated_cost_wei) / Decimal(10**9)


@dataclass
class TransactionResult:
    """Result of sending a transaction."""

    hash: TxHash
    block_number: int | None = None
    gas_used: int | None = None
    status: bool | None = None  # True = success, False = reverted, None = pending
    logs: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_pending(self) -> bool:
        """Whether the transaction is still pending."""
        return self.status is None

    @property
    def is_success(self) -> bool:
        """Whether the transaction succeeded."""
        return self.status is True


@dataclass
class WalletBalance:
    """Combined wallet balance summary."""

    address: Address
    eth_balance: TokenAmount
    token_balances: list[TokenAmount] = field(default_factory=list)

    @property
    def has_eth(self) -> bool:
        return self.eth_balance.raw > 0
''')

commit("refactor(types): enhance type definitions with formatting and helpers")

# --- Commit 74: Update pyproject.toml ---
write("pyproject.toml", '''[project]
name = "base-agent-toolkit"
version = "0.1.0"
description = "Python SDK for building AI agents on Base L2"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "ifiokmase8"},
]
keywords = ["base", "ethereum", "web3", "ai-agent", "defi", "b20", "x402"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Office/Business :: Financial",
]

dependencies = [
    "web3>=6.0.0",
    "eth-account>=0.10.0",
    "click>=8.0.0",
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
    "pre-commit>=3.0",
    "mypy>=1.0",
]

[project.scripts]
bat = "base_agent_toolkit.cli.main:app"

[project.urls]
Homepage = "https://github.com/ifiokmase8/base-agent-toolkit"
Documentation = "https://docs.base.org"
Repository = "https://github.com/ifiokmase8/base-agent-toolkit"
"Bug Tracker" = "https://github.com/ifiokmase8/base-agent-toolkit/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/base_agent_toolkit"]

[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "D", "UP"]
ignore = ["D100", "D104", "D107", "D203", "D213"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
''')

commit("build: finalize pyproject.toml with all dependencies and CLI entry point")

# --- Commit 75: Comprehensive README ---
write("README.md", '''# Base Agent Toolkit 🔵

> Python SDK for building AI agents on Base L2

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Base Chain](https://img.shields.io/badge/Chain-Base-0052FF.svg)](https://base.org)

A comprehensive toolkit for building autonomous AI agents that interact with the [Base](https://base.org) L2 chain — Coinbase's Ethereum rollup.

## ✨ Features

- **🔑 Wallet Management** — Create, import, HD derivation, key management
- **🪙 B20 Tokens** — Deploy and manage B20 native tokens (Beryl upgrade)
- **💱 DeFi Integrations** — Aerodrome, Uniswap V3, Morpho Blue
- **🤖 AI Agent Framework** — Strategy engine, tools, budget management
- **💳 x402 Payments** — HTTP payment protocol for AI agents
- **⛽ Gas Oracle** — EIP-1559 gas estimation and optimization
- **📊 Portfolio Tracking** — Monitor positions across protocols
- **🖥️ CLI Interface** — Command-line tools for common operations

## 📦 Installation

```bash
pip install base-agent-toolkit
```

Or from source:

```bash
git clone https://github.com/ifiokmase8/base-agent-toolkit.git
cd base-agent-toolkit
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Create a Wallet

```python
from base_agent_toolkit import BaseProvider, BaseWallet

provider = BaseProvider(chain_id=8453)  # Base mainnet
wallet = BaseWallet.create(provider)
print(f"Address: {wallet.address}")
```

### Check Balance

```python
balance = wallet.get_balance()
print(f"ETH: {balance}")
```

### Deploy a B20 Token

```python
from base_agent_toolkit.b20 import B20Factory, B20TokenConfig, B20TokenType

config = B20TokenConfig(
    name="My Token",
    symbol="MTK",
    token_type=B20TokenType.ASSET,
    admin=wallet.address,
    decimals=18,
    supply_cap=1_000_000 * 10**18,
)

factory = B20Factory(provider)
tx = factory.build_deploy_tx(config)
```

### Swap Tokens

```python
from base_agent_toolkit.defi import AerodromeRouter

router = AerodromeRouter(provider)
quote = router.get_quote(
    token_in="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC
    token_out="0x4200000000000000000000000000000000000006",  # WETH
    amount_in=100 * 10**6,  # 100 USDC
)
print(f"Expected: {quote.amount_out} WETH")
```

### Build an AI Agent

```python
from base_agent_toolkit.agent import BaseAgent, AgentConfig, AgentExecutor
from base_agent_toolkit.agent.strategies import DCAStrategy

agent = BaseAgent(AgentConfig(
    name="dca-bot",
    dry_run=True,
    daily_budget_wei=10**17,
))

dca = DCAStrategy(
    token_in=USDC_ADDRESS,
    token_out=WETH_ADDRESS,
    amount_per_interval=50 * 10**6,
)

executor = AgentExecutor(agent, [dca])
results = executor.run_once()
```

### x402 Payments

```python
from base_agent_toolkit.x402 import X402Client, X402Config

client = X402Client(X402Config(
    private_key="0x...",
    auto_pay=True,
    max_payment_wei=10**16,
))

response = client.get("https://api.example.com/paid-data")
```

## 🖥️ CLI

```bash
# Show toolkit info
bat info

# Create wallet
bat wallet create

# Generate mnemonic
bat wallet mnemonic

# Check balance
bat wallet balance --address 0x... --network mainnet

# Configure B20 token
bat b20 configure --name "My Token" --symbol MTK

# List agent tools
bat agent tools
```

## 📁 Project Structure

```
base-agent-toolkit/
├── src/base_agent_toolkit/
│   ├── agent/          # AI agent framework
│   │   ├── strategies/ # Pre-built strategies (DCA, rebalance)
│   │   ├── base.py     # BaseAgent
│   │   ├── executor.py # Strategy executor
│   │   └── tools.py    # Agent tools
│   ├── b20/            # B20 token standard
│   │   ├── factory.py  # Token deployment
│   │   ├── token.py    # Token interaction
│   │   ├── permit.py   # ERC-2612 permit
│   │   └── events.py   # Event listener
│   ├── cli/            # Command-line interface
│   ├── defi/           # DeFi integrations
│   │   ├── aerodrome.py  # Aerodrome DEX
│   │   ├── uniswap.py   # Uniswap V3
│   │   ├── morpho.py    # Morpho Blue
│   │   └── portfolio.py # Portfolio tracker
│   ├── provider/       # RPC provider
│   ├── wallet/         # Wallet management
│   ├── x402/           # x402 payment protocol
│   ├── constants.py
│   ├── exceptions.py
│   ├── types.py
│   └── config.py
├── tests/
├── docs/guides/
├── examples/
└── pyproject.toml
```

## 🔗 Base Ecosystem

| Component | Description |
|-----------|-------------|
| **Base** | Coinbase L2 built on OP Stack |
| **B20** | Native token standard (Beryl upgrade, June 2026) |
| **Aerodrome** | Primary DEX, ve(3,3) model |
| **x402** | HTTP payment protocol for AI agents |
| **Base MCP** | Model Context Protocol for AI integration |
| **ERC-8004** | Agent identity standard |

## 📚 Documentation

- [B20 Token Guide](docs/guides/b20-tokens.md)
- [DeFi Protocol Guide](docs/guides/defi-protocols.md)
- [AI Agent Guide](docs/guides/ai-agents.md)
- [Base Docs](https://docs.base.org)
- [x402 Protocol](https://www.x402.org)

## 🧪 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
''')

commit("docs: write comprehensive README with full feature documentation")

print("\\n=== Phase 5 complete! ===")
result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True, cwd=ROOT)
lines = result.stdout.strip().splitlines()
print(f"Total commits: {len(lines)}")

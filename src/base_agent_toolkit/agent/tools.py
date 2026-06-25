"""Pre-built agent tools for common Base operations.

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

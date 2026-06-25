# AI Agent Framework Guide

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

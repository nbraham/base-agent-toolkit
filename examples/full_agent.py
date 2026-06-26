#!/usr/bin/env python3
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

    print(f"
🤖 Agent: {agent.name}")
    print(f"   Dry Run: {agent.is_dry_run}")
    print(f"   Budget:  0.1 ETH/day")

    # 2. List available tools
    print("
🔧 Available Tools:")
    for tool in list_tools():
        print(f"   • {tool['name']}: {tool['description']}")

    # 3. Set up DCA strategy
    dca = DCAStrategy(
        token_in="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC
        token_out="0x4200000000000000000000000000000000000006",  # WETH
        amount_per_interval=50 * 10**6,  # 50 USDC
        interval_seconds=86400,  # Daily
    )

    print(f"
📈 Strategy: {dca.name}")
    print(f"   {dca.description}")

    # 4. Run executor
    executor = AgentExecutor(agent, [dca])
    results = executor.run_once()

    print("
📊 Execution Results:")
    for result in results:
        status_emoji = "✅" if result.is_success else "❌"
        print(f"   {status_emoji} {result.message}")

    # 5. Summary
    summary = executor.get_summary()
    print(f"
📋 Summary:")
    print(f"   Total executions: {summary['total_executions']}")
    for status, count in summary["by_status"].items():
        print(f"   {status}: {count}")

    # 6. Agent status
    status = agent.get_status()
    print(f"
🔍 Agent Status:")
    print(f"   TX Count:   {status['tx_count']}")
    print(f"   Spent:      {status['spent_today_wei']} wei")
    print(f"   Budget:     {status['budget_remaining_wei']}")


if __name__ == "__main__":
    main()

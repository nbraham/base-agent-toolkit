"""Tests for agent module."""

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

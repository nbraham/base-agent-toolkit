"""Tests for CLI module."""

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

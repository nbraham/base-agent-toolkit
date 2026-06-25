"""CLI entry point for Base Agent Toolkit."""

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

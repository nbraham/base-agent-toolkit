"""Configuration management for Base Agent Toolkit."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    BASE_MAINNET_CHAIN_ID,
    BASE_SEPOLIA_CHAIN_ID,
    DEFAULT_MAX_GAS_PRICE_GWEI,
    DEFAULT_RPC_URLS,
    DEFAULT_TX_TIMEOUT_SECONDS,
)
from .types import Network


class Settings(BaseSettings):
    """Base Agent Toolkit configuration.

    Settings are loaded from environment variables (BAT_ prefix)
    and/or a .env file.
    """

    model_config = SettingsConfigDict(
        env_prefix="BAT_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Network
    network: Network = Network.MAINNET

    # RPC
    rpc_url: Optional[str] = None
    rpc_fallbacks: list[str] = Field(default_factory=list)

    # Wallet
    private_key: Optional[str] = None
    mnemonic: Optional[str] = None

    # API Keys
    basescan_api_key: Optional[str] = None
    alchemy_api_key: Optional[str] = None

    # Transaction settings
    max_gas_price_gwei: float = DEFAULT_MAX_GAS_PRICE_GWEI
    tx_timeout: int = DEFAULT_TX_TIMEOUT_SECONDS
    dry_run: bool = False

    # Logging
    log_level: str = "INFO"
    log_json: bool = False

    # Notifications
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    discord_webhook_url: Optional[str] = None

    @property
    def chain_id(self) -> int:
        """Get the chain ID for the configured network."""
        return (
            BASE_MAINNET_CHAIN_ID
            if self.network == Network.MAINNET
            else BASE_SEPOLIA_CHAIN_ID
        )

    @property
    def rpc_urls(self) -> list[str]:
        """Get all RPC URLs (primary + fallbacks)."""
        urls = []
        if self.rpc_url:
            urls.append(self.rpc_url)
        urls.extend(self.rpc_fallbacks)
        if not urls:
            urls = DEFAULT_RPC_URLS.get(self.chain_id, [])
        return urls

    @field_validator("rpc_fallbacks", mode="before")
    @classmethod
    def parse_fallbacks(cls, v):
        """Parse comma-separated fallback URLs."""
        if isinstance(v, str):
            return [url.strip() for url in v.split(",") if url.strip()]
        return v

    @field_validator("private_key", mode="before")
    @classmethod
    def normalize_private_key(cls, v):
        """Strip 0x prefix from private key if present."""
        if isinstance(v, str) and v.startswith("0x"):
            return v[2:]
        return v


def load_settings(env_file: str | Path | None = None) -> Settings:
    """Load settings from environment and optional .env file.

    Args:
        env_file: Path to .env file. Defaults to .env in current directory.

    Returns:
        Configured Settings instance.
    """
    kwargs = {}
    if env_file:
        kwargs["_env_file"] = str(env_file)
    return Settings(**kwargs)

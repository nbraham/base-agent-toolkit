"""B20Factory interaction for deploying B20 tokens."""

from __future__ import annotations

from typing import Any

from web3 import Web3

from ..constants import B20_FACTORY
from ..exceptions import B20DeploymentError, B20Error
from ..logging import get_logger
from ..provider.base import BaseProvider
from ..types import Address, TransactionResult
from .abi import B20_FACTORY_ABI
from .types import B20TokenConfig, B20TokenType

logger = get_logger(__name__)


class B20Factory:
    """Interface to the B20Factory precompile for deploying B20 tokens.

    The B20Factory is a singleton precompile at address 0x...0B20
    that deploys new B20 tokens as Rust precompiles.

    Args:
        provider: BaseProvider instance.
        factory_address: Override factory address (default: B20_FACTORY).
    """

    def __init__(
        self,
        provider: BaseProvider,
        factory_address: Address = B20_FACTORY,
    ):
        self._provider = provider
        self._address = Web3.to_checksum_address(factory_address)
        self._contract = provider.w3.eth.contract(
            address=self._address,
            abi=B20_FACTORY_ABI,
        )

        logger.debug("b20_factory.initialized", address=self._address)

    def build_deploy_asset_tx(
        self,
        config: B20TokenConfig,
    ) -> dict[str, Any]:
        """Build transaction to deploy a B20 Asset token.

        Args:
            config: Token configuration.

        Returns:
            Unsigned transaction dictionary.

        Raises:
            B20DeploymentError: If config is invalid for Asset type.
        """
        if config.token_type != B20TokenType.ASSET:
            raise B20DeploymentError(
                f"Expected ASSET type, got {config.token_type}"
            )

        admin = Web3.to_checksum_address(config.admin)
        return self._contract.functions.deployAsset(
            config.name,
            config.symbol,
            config.decimals,
            admin,
            config.supply_cap,
        ).build_transaction({"gas": 500_000})

    def build_deploy_stablecoin_tx(
        self,
        config: B20TokenConfig,
    ) -> dict[str, Any]:
        """Build transaction to deploy a B20 Stablecoin token.

        Args:
            config: Token configuration.

        Returns:
            Unsigned transaction dictionary.

        Raises:
            B20DeploymentError: If config is invalid for Stablecoin type.
        """
        if config.token_type != B20TokenType.STABLECOIN:
            raise B20DeploymentError(
                f"Expected STABLECOIN type, got {config.token_type}"
            )

        admin = Web3.to_checksum_address(config.admin)
        return self._contract.functions.deployStablecoin(
            config.name,
            config.symbol,
            admin,
            config.currency_code,
            config.supply_cap,
        ).build_transaction({"gas": 500_000})

    def build_deploy_tx(self, config: B20TokenConfig) -> dict[str, Any]:
        """Build deploy transaction for any B20 token type.

        Args:
            config: Token configuration.

        Returns:
            Unsigned transaction dictionary.
        """
        if config.token_type == B20TokenType.STABLECOIN:
            return self.build_deploy_stablecoin_tx(config)
        return self.build_deploy_asset_tx(config)

    def get_token_count(self) -> int:
        """Get the total number of deployed B20 tokens.

        Returns:
            Number of deployed tokens.
        """
        return self._contract.functions.tokenCount().call()

    def get_token_address(self, index: int) -> Address:
        """Get a deployed token address by index.

        Args:
            index: Token index (0-based).

        Returns:
            Token contract address.
        """
        return self._contract.functions.getToken(index).call()

    def list_tokens(self, limit: int = 100) -> list[Address]:
        """List all deployed B20 token addresses.

        Args:
            limit: Maximum number of tokens to return.

        Returns:
            List of token addresses.
        """
        count = min(self.get_token_count(), limit)
        tokens = []
        for i in range(count):
            addr = self.get_token_address(i)
            tokens.append(addr)
        return tokens

    def __repr__(self) -> str:
        return f"B20Factory({self._address})"

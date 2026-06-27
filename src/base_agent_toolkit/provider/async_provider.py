"""Async provider for non-blocking RPC calls.

Placeholder for async/await support using httpx or aiohttp.
"""

from __future__ import annotations

from typing import Any

from ..logging import get_logger

logger = get_logger(__name__)


class AsyncBaseProvider:
    """Async RPC provider for Base chain.

    Non-blocking provider for use in async applications.
    Uses httpx for HTTP/2 support and connection pooling.

    Args:
        rpc_url: Base RPC endpoint URL.
        chain_id: Chain ID (8453 for mainnet).

    Example:
        async with AsyncBaseProvider("https://mainnet.base.org") as provider:
            balance = await provider.get_balance("0x...")
    """

    def __init__(
        self,
        rpc_url: str = "https://mainnet.base.org",
        chain_id: int = 8453,
    ):
        self._rpc_url = rpc_url
        self._chain_id = chain_id
        self._client = None
        self._request_id = 0

    async def __aenter__(self) -> "AsyncBaseProvider":
        """Enter async context."""
        import httpx
        self._client = httpx.AsyncClient(
            base_url=self._rpc_url,
            http2=True,
            timeout=30.0,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _rpc_call(self, method: str, params: list[Any] | None = None) -> Any:
        """Make an async JSON-RPC call.

        Args:
            method: RPC method name.
            params: Method parameters.

        Returns:
            RPC result.
        """
        if not self._client:
            raise RuntimeError("Provider not initialized. Use 'async with' context.")

        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": self._request_id,
        }

        response = await self._client.post("/", json=payload)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise RuntimeError(f"RPC error: {data['error']}")

        return data.get("result")

    async def get_balance(self, address: str) -> int:
        """Get ETH balance of an address.

        Args:
            address: Ethereum address.

        Returns:
            Balance in wei.
        """
        result = await self._rpc_call("eth_getBalance", [address, "latest"])
        return int(result, 16)

    async def get_block_number(self) -> int:
        """Get the latest block number.

        Returns:
            Current block number.
        """
        result = await self._rpc_call("eth_blockNumber")
        return int(result, 16)

    async def get_chain_id(self) -> int:
        """Get the chain ID.

        Returns:
            Chain ID.
        """
        result = await self._rpc_call("eth_chainId")
        return int(result, 16)

    async def get_gas_price(self) -> int:
        """Get current gas price.

        Returns:
            Gas price in wei.
        """
        result = await self._rpc_call("eth_gasPrice")
        return int(result, 16)

    def __repr__(self) -> str:
        return f"AsyncBaseProvider({self._rpc_url})"

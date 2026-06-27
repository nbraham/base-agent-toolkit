"""Tests for token registry."""

from base_agent_toolkit.registry import (
    get_token,
    get_token_by_address,
    list_all_tokens,
    list_stablecoins,
)


class TestTokenRegistry:
    """Tests for token registry lookups."""

    def test_get_known_token(self):
        usdc = get_token("USDC")
        assert usdc is not None
        assert usdc.symbol == "USDC"
        assert usdc.decimals == 6
        assert usdc.is_stablecoin

    def test_get_token_case_insensitive(self):
        assert get_token("usdc") is not None
        assert get_token("Weth") is not None

    def test_get_unknown_token(self):
        assert get_token("UNKNOWN") is None

    def test_get_by_address(self):
        token = get_token_by_address(
            "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        )
        assert token is not None
        assert token.symbol == "USDC"

    def test_get_by_address_case_insensitive(self):
        token = get_token_by_address(
            "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
        )
        assert token is not None

    def test_list_all(self):
        tokens = list_all_tokens()
        assert len(tokens) >= 5
        symbols = [t.symbol for t in tokens]
        assert "ETH" in symbols
        assert "USDC" in symbols

    def test_list_stablecoins(self):
        stables = list_stablecoins()
        assert len(stables) >= 2
        for s in stables:
            assert s.is_stablecoin

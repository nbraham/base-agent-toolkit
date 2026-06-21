"""Base chain constants and configuration."""

from __future__ import annotations

# ============================================================
# Chain IDs
# ============================================================
BASE_MAINNET_CHAIN_ID = 8453
BASE_SEPOLIA_CHAIN_ID = 84532
ETHEREUM_MAINNET_CHAIN_ID = 1

# ============================================================
# RPC Endpoints
# ============================================================
DEFAULT_RPC_URLS: dict[int, list[str]] = {
    BASE_MAINNET_CHAIN_ID: [
        "https://mainnet.base.org",
        "https://base.llamarpc.com",
        "https://base.drpc.org",
        "https://base-mainnet.public.blastapi.io",
    ],
    BASE_SEPOLIA_CHAIN_ID: [
        "https://sepolia.base.org",
        "https://base-sepolia.drpc.org",
    ],
}

# ============================================================
# Block Explorer URLs
# ============================================================
EXPLORER_URLS: dict[int, str] = {
    BASE_MAINNET_CHAIN_ID: "https://basescan.org",
    BASE_SEPOLIA_CHAIN_ID: "https://sepolia.basescan.org",
}

# ============================================================
# Well-Known Contract Addresses (Base Mainnet)
# ============================================================
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDT_ADDRESS = "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2"
DAI_ADDRESS = "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"

# Aerodrome
AERODROME_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
AERODROME_FACTORY = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"

# Uniswap V3
UNISWAP_V3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"
UNISWAP_V3_FACTORY = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"
UNISWAP_V3_QUOTER = "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a"

# Morpho
MORPHO_BLUE = "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb"

# Moonwell
MOONWELL_COMPTROLLER = "0xfBb21d0380beE3312B33c4353c8936a0F13EF26C"

# B20 Factory (Beryl upgrade)
B20_FACTORY = "0x0000000000000000000000000000000000000B20"

# Bridge
L1_STANDARD_BRIDGE = "0x3154Cf16ccdb4C6d922629664174b904d80F2C35"
L2_STANDARD_BRIDGE = "0x4200000000000000000000000000000000000010"

# ============================================================
# Token Decimals
# ============================================================
ETH_DECIMALS = 18
USDC_DECIMALS = 6
USDT_DECIMALS = 6
DAI_DECIMALS = 18

# ============================================================
# Gas Defaults
# ============================================================
DEFAULT_GAS_LIMIT = 21_000
DEFAULT_MAX_GAS_PRICE_GWEI = 50
EIP1559_BASE_FEE_MULTIPLIER = 1.25
DEFAULT_PRIORITY_FEE_GWEI = 0.1

# ============================================================
# Timing
# ============================================================
DEFAULT_TX_TIMEOUT_SECONDS = 120
DEFAULT_BLOCK_CONFIRMATION_COUNT = 1
RPC_REQUEST_TIMEOUT_SECONDS = 30

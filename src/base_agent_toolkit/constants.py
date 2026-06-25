"""Global constants for Base Agent Toolkit."""

# ============================================================
# Chain IDs
# ============================================================
BASE_MAINNET_CHAIN_ID = 8453
BASE_SEPOLIA_CHAIN_ID = 84532

# ============================================================
# RPC URLs
# ============================================================
DEFAULT_RPC_URLS = {
    8453: [
        "https://mainnet.base.org",
        "https://base.drpc.org",
    ],
    84532: [
        "https://sepolia.base.org",
    ],
}

# ============================================================
# Provider Settings
# ============================================================
RPC_REQUEST_TIMEOUT_SECONDS = 30

# ============================================================
# Token Addresses (Base Mainnet)
# ============================================================
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDT_ADDRESS = "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2"
DAI_ADDRESS = "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb"
CBETH_ADDRESS = "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22"

# Token Decimals
ETH_DECIMALS = 18
USDC_DECIMALS = 6
USDT_DECIMALS = 6

# ============================================================
# B20 Contracts
# ============================================================
B20_FACTORY = "0x0000000000000000000000000000000000000B20"
B20_FACTORY_SEPOLIA = "0x0000000000000000000000000000000000000B20"

# ============================================================
# DeFi Protocol Addresses (Base Mainnet)
# ============================================================

# Aerodrome
AERODROME_ROUTER = "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
AERODROME_FACTORY = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"

# Uniswap V3
UNISWAP_V3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"
UNISWAP_V3_QUOTER = "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a"
UNISWAP_V3_FACTORY = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"

# Morpho Blue
MORPHO_BLUE = "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb"

# ============================================================
# Gas Settings
# ============================================================
DEFAULT_GAS_LIMIT = 21000  # Simple ETH transfer
DEFAULT_MAX_GAS_PRICE_GWEI = 50.0
DEFAULT_PRIORITY_FEE_GWEI = 0.1
EIP1559_BASE_FEE_MULTIPLIER = 1.25

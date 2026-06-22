"""HD wallet derivation for multi-account support."""

from __future__ import annotations

from eth_account import Account

from ..logging import get_logger
from ..provider.base import BaseProvider
from .wallet import BaseWallet

logger = get_logger(__name__)


def derive_wallets(
    mnemonic: str,
    provider: BaseProvider,
    count: int = 5,
    start_index: int = 0,
) -> list[BaseWallet]:
    """Derive multiple wallets from a BIP39 mnemonic.

    Uses the standard Ethereum derivation path: m/44'/60'/0'/0/{index}

    Args:
        mnemonic: BIP39 mnemonic phrase (12 or 24 words).
        provider: BaseProvider for chain interactions.
        count: Number of wallets to derive.
        start_index: Starting derivation index.

    Returns:
        List of BaseWallet instances.
    """
    Account.enable_unaudited_hdwallet_features()
    wallets = []

    for i in range(start_index, start_index + count):
        wallet = BaseWallet.from_mnemonic(mnemonic, provider, account_index=i)
        wallets.append(wallet)
        logger.debug(
            "hd.derived",
            index=i,
            address=wallet.address,
        )

    logger.info(
        "hd.derived_batch",
        count=len(wallets),
        start_index=start_index,
        addresses=[w.address for w in wallets],
    )

    return wallets


def generate_mnemonic(strength: int = 128) -> str:
    """Generate a new BIP39 mnemonic phrase.

    Args:
        strength: Entropy bits (128 = 12 words, 256 = 24 words).

    Returns:
        Mnemonic phrase string.
    """
    Account.enable_unaudited_hdwallet_features()
    _, mnemonic = Account.create_with_mnemonic(num_words=strength // 32 * 3)
    return mnemonic

"""Encrypted keystore for private keys."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..logging import get_logger

logger = get_logger(__name__)


@dataclass
class KeystoreEntry:
    """A single keystore entry."""

    name: str
    address: str
    encrypted_key: str
    created_at: str


class SecureKeystore:
    """Encrypted keystore for managing private keys.

    Stores private keys encrypted on disk. Keys are only
    decrypted when needed for signing.

    Args:
        keystore_dir: Directory to store encrypted keys.
    """

    def __init__(self, keystore_dir: str = "~/.base-agent-toolkit/keys"):
        self._dir = Path(os.path.expanduser(keystore_dir))
        self._dir.mkdir(parents=True, exist_ok=True)
        logger.debug("keystore.initialized", path=str(self._dir))

    def store(
        self,
        name: str,
        private_key: str,
        password: str,
    ) -> str:
        """Store a private key encrypted with a password.

        Args:
            name: Key name/label.
            private_key: Private key to encrypt.
            password: Encryption password.

        Returns:
            Address derived from the key.
        """
        from eth_account import Account

        # Derive address
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"
        account = Account.from_key(private_key)
        address = account.address

        # Encrypt with web3 keystore format
        encrypted = Account.encrypt(private_key, password)

        # Save to file
        keyfile = self._dir / f"{name}.json"
        with open(keyfile, "w") as f:
            json.dump(
                {
                    "name": name,
                    "address": address,
                    "keystore": encrypted,
                },
                f,
                indent=2,
            )

        logger.info(
            "keystore.stored",
            name=name,
            address=address[:10],
        )

        return address

    def load(self, name: str, password: str) -> str:
        """Load and decrypt a private key.

        Args:
            name: Key name/label.
            password: Decryption password.

        Returns:
            Decrypted private key.

        Raises:
            FileNotFoundError: If key not found.
            ValueError: If password is wrong.
        """
        from eth_account import Account

        keyfile = self._dir / f"{name}.json"
        if not keyfile.exists():
            raise FileNotFoundError(f"Key '{name}' not found")

        with open(keyfile) as f:
            data = json.load(f)

        try:
            private_key = Account.decrypt(data["keystore"], password)
            return f"0x{private_key.hex()}"
        except ValueError:
            raise ValueError(f"Wrong password for key '{name}'")

    def list_keys(self) -> list[dict[str, str]]:
        """List all stored keys (without private key data).

        Returns:
            List of {name, address} dicts.
        """
        keys = []
        for keyfile in self._dir.glob("*.json"):
            try:
                with open(keyfile) as f:
                    data = json.load(f)
                keys.append({
                    "name": data.get("name", keyfile.stem),
                    "address": data.get("address", "unknown"),
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return keys

    def delete(self, name: str) -> bool:
        """Delete a stored key.

        Args:
            name: Key name to delete.

        Returns:
            True if deleted, False if not found.
        """
        keyfile = self._dir / f"{name}.json"
        if keyfile.exists():
            keyfile.unlink()
            logger.info("keystore.deleted", name=name)
            return True
        return False

    def __repr__(self) -> str:
        count = len(list(self._dir.glob("*.json")))
        return f"SecureKeystore(keys={count})"

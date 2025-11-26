"""Token encryption utilities using Fernet (symmetric encryption).

This module provides functions to encrypt and decrypt AI API tokens
for secure storage in the database.
"""

import base64
import logging

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Raised when encryption/decryption fails."""

    pass


def get_cipher() -> Fernet:
    """Get Fernet cipher with key from settings.

    Returns:
        Fernet: Configured cipher instance

    Raises:
        EncryptionError: If encryption key is not configured
    """
    key = settings.ai.token_encryption_key

    if not key:
        raise EncryptionError("AI_TOKEN_ENCRYPTION_KEY is not configured. " 'Generate one using: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')

    try:
        # Ensure key is bytes
        if isinstance(key, str):
            key = key.encode()
        return Fernet(key)
    except Exception as e:
        logger.error(f"Failed to create Fernet cipher: {e}")
        raise EncryptionError(f"Invalid encryption key: {e}")


def encrypt_token(token: str) -> str:
    """Encrypt API token for storage.

    Args:
        token: Plain text API token

    Returns:
        str: Base64-encoded encrypted token

    Raises:
        EncryptionError: If encryption fails
    """
    if not token:
        raise EncryptionError("Cannot encrypt empty token")

    try:
        cipher = get_cipher()
        encrypted_bytes = cipher.encrypt(token.encode())
        encrypted_b64 = base64.b64encode(encrypted_bytes).decode()
        return encrypted_b64
    except Exception as e:
        logger.error(f"Token encryption failed: {e}")
        raise EncryptionError(f"Failed to encrypt token: {e}")


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt stored API token.

    Args:
        encrypted_token: Base64-encoded encrypted token

    Returns:
        str: Plain text API token

    Raises:
        EncryptionError: If decryption fails
    """
    if not encrypted_token:
        raise EncryptionError("Cannot decrypt empty token")

    try:
        cipher = get_cipher()
        encrypted_bytes = base64.b64decode(encrypted_token)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()
    except InvalidToken:
        logger.error("Token decryption failed: Invalid token or key")
        raise EncryptionError("Invalid encrypted token or encryption key has changed")
    except Exception as e:
        logger.error(f"Token decryption failed: {e}")
        raise EncryptionError(f"Failed to decrypt token: {e}")


def generate_encryption_key() -> str:
    """Generate a new Fernet encryption key.

    Returns:
        str: New Fernet key (base64-encoded)

    Note:
        This is a utility function for generating keys.
        Use from command line:
        python -c "from app.modules.ai.utils.encryption import generate_encryption_key; print(generate_encryption_key())"
    """
    return Fernet.generate_key().decode()

"""
Enterprise Data Encryption Module

This module provides symmetric encryption for protecting Personal Identifiable Information (PII)
like National IDs, Phone Numbers, or exact dates of birth before storing them in the database.
"""

import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


import logging

logger = logging.getLogger("EncryptionService")


class EncryptionService:
    def __init__(self, key: str | None = None):
        raw_key = key or os.getenv("ENCRYPTION_KEY")
        valid_cipher = None

        if raw_key and raw_key != "replace-with-32-byte-fernet-key":
            try:
                valid_cipher = Fernet(raw_key.strip().encode("utf-8"))
            except Exception as e:
                logger.warning(
                    f"Provided ENCRYPTION_KEY is invalid ({e}). Generating fallback key."
                )

        if valid_cipher is None:
            fallback_key = Fernet.generate_key()
            valid_cipher = Fernet(fallback_key)
            logger.info("Using active cryptographic key for session.")

        self.cipher_suite = valid_cipher


    def encrypt(self, plain_text: str) -> str:
        """Encrypt a string and return the encrypted payload as a string."""
        if not plain_text:
            return ""
        encrypted_bytes = self.cipher_suite.encrypt(plain_text.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt the payload back to plain text."""
        if not encrypted_text:
            return ""
        decrypted_bytes = self.cipher_suite.decrypt(encrypted_text.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")


encryption_service = EncryptionService()

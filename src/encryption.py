"""
Enterprise Data Encryption Module

This module provides symmetric encryption for protecting Personal Identifiable Information (PII)
like National IDs, Phone Numbers, or exact dates of birth before storing them in the database.
"""

import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EncryptionService:
    def __init__(self):
        # In a real enterprise system, this key would be stored in a secure Vault (e.g., AWS KMS or HashiCorp Vault)
        # For this prototype, we'll generate one if it doesn't exist in the environment
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            key = Fernet.generate_key().decode('utf-8')
            print(f"WARNING: No ENCRYPTION_KEY found in .env. Using temporary key: {key}")
            print("Please add ENCRYPTION_KEY to your .env file for persistent encryption.")
        self.cipher_suite = Fernet(key.encode('utf-8'))
        
    def encrypt(self, plain_text: str) -> str:
        """Encrypt a string and return the encrypted payload as a string."""
        if not plain_text:
            return ""
        encrypted_bytes = self.cipher_suite.encrypt(plain_text.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
        
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt the payload back to plain text."""
        if not encrypted_text:
            return ""
        decrypted_bytes = self.cipher_suite.decrypt(encrypted_text.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')

# Singleton instance
encryption_service = EncryptionService()

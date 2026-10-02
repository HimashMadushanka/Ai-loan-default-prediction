import pytest
from src.encryption import EncryptionService, encryption_service


def test_encryption_decryption_cycle():
    text = "applicant-ssn-123-45-6789"
    encrypted = encryption_service.encrypt(text)
    assert encrypted != text
    assert len(encrypted) > 0

    decrypted = encryption_service.decrypt(encrypted)
    assert decrypted == text


def test_empty_string_encryption():
    assert encryption_service.encrypt("") == ""
    assert encryption_service.decrypt("") == ""


def test_invalid_key_safe_fallback():
    
    bad_service = EncryptionService(key="replace-with-32-byte-fernet-key")
    encrypted = bad_service.encrypt("test-data")
    assert bad_service.decrypt(encrypted) == "test-data"

    corrupted_service = EncryptionService(key="completely-invalid-key")
    encrypted2 = corrupted_service.encrypt("secure-info")
    assert corrupted_service.decrypt(encrypted2) == "secure-info"

"""
Test suite for vault-specific operations and encrypted data handling.

Tests verify encrypted data storage, retrieval, and metadata tracking including:
- Production-grade AES-256-GCM encryption (industry standard for password managers)
- Secure data storage in vault_records table
- Metadata and record type tracking
- Key management for encrypted data

Encryption Standard: AES-256-GCM
- Used by: Keeper Security, 1Password, LastPass, Bitwarden
- FIPS 140-2 compliant
- Provides both encryption and authentication
- Prevents tampering and replay attacks
"""

import os
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from framework.base_test import BaseTest

class TestVaultOperations(BaseTest):
    """Test class for validating vault operations and AES-256-GCM encrypted data management."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generate 256-bit (32 byte) encryption key for AES-256
        self.encryption_key = AESGCM.generate_key(bit_length=256)
        self.aesgcm = AESGCM(self.encryption_key)
    
    def _encrypt_data(self, plaintext):
        """
        Encrypt data using AES-256-GCM - production-grade authenticated encryption.
        ... (docstring unchanged) ...
        """
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode(), None)
        return ciphertext.hex(), nonce.hex()
    
    def _decrypt_data(self, encrypted_hex, nonce_hex):
        """
        Decrypt and verify data using AES-256-GCM.
        ... (docstring unchanged) ...
        """
        ciphertext = bytes.fromhex(encrypted_hex)
        nonce = bytes.fromhex(nonce_hex)
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
    
    def test_sql_004_encrypted_data_storage(self):
        """
        SQL-004: AES-256-GCM Encrypted Data Storage
        ... (docstring unchanged) ...
        """
        logging.info("SQL-004: Creating user 'vaultuser'")
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('vaultuser', 'vault@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('vaultuser',))
        user_id = user[0][0]
        logging.info("SQL-004: Created user_id=%s", user_id)
        
        plaintext = "MySecretPassword123!"
        encrypted_hex, nonce_hex = self._encrypt_data(plaintext)
        logging.info("SQL-004: Encrypted plaintext. Encrypted(hex)=%s, Nonce(hex)=%s", encrypted_hex, nonce_hex)
        
        self.assertNotEqual(encrypted_hex, plaintext)
        self.assertGreater(len(encrypted_hex), len(plaintext))
        
        combined_data = f"{nonce_hex}:{encrypted_hex}"
        logging.info("SQL-004: Storing encrypted data in vault_records")
        self.db.execute_query(
            "INSERT INTO vault_records (user_id, title, encrypted_data, record_type) VALUES (%s, %s, %s, %s)",
            (user_id, 'Bank Login', combined_data, 'password')
        )
        
        result = self.db.execute_query(
            "SELECT encrypted_data FROM vault_records WHERE title = %s",
            ('Bank Login',)
        )
        retrieved_data = result[0][0]
        stored_nonce_hex, stored_encrypted_hex = retrieved_data.split(':')
        logging.info("SQL-004: Retrieved encrypted data: %s", retrieved_data)
        
        decrypted = self._decrypt_data(stored_encrypted_hex, stored_nonce_hex)
        logging.info("SQL-004: Decrypted data: %s", decrypted)
        
        self.assertEqual(decrypted, plaintext)
        self.assertNotEqual(stored_encrypted_hex, plaintext)
        logging.info("SQL-004: Encryption and decryption verified successfully.")

    def test_sql_005_vault_record_metadata(self):
        """
        SQL-005: Vault Record Metadata Tracking
        ... (docstring unchanged) ...
        """
        logging.info("SQL-005: Creating user 'metauser'")
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('metauser', 'meta@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('metauser',))
        user_id = user[0][0]
        logging.info("SQL-005: Created user_id=%s", user_id)
        
        encrypted_hex, nonce_hex = self._encrypt_data('sensitive_data')
        combined_data = f"{nonce_hex}:{encrypted_hex}"
        logging.info("SQL-005: Encrypted data for metadata test.")
        
        self.db.execute_query(
            "INSERT INTO vault_records (user_id, title, encrypted_data, record_type) VALUES (%s, %s, %s, %s)",
            (user_id, 'Test Record', combined_data, 'login')
        )
        
        result = self.db.execute_query("""
            SELECT record_type, created_at, updated_at 
            FROM vault_records 
            WHERE title = %s
        """, ('Test Record',))
        logging.info("SQL-005: Metadata query result: %s", result)
        
        self.assertEqual(result[0][0], 'login')
        self.assertIsNotNone(result[0][1])
        self.assertIsNotNone(result[0][2])
        logging.info("SQL-005: Metadata tracking verified successfully.")

    def test_sql_006_encryption_key_isolation(self):
        """
        SQL-006: Encryption Key Isolation
        ... (docstring unchanged) ...
        """
        plaintext = "SensitiveData"
        encrypted1_hex, nonce1_hex = self._encrypt_data(plaintext)
        logging.info("SQL-006: Encrypted with key1: %s", encrypted1_hex)
        
        different_key = AESGCM.generate_key(bit_length=256)
        different_aesgcm = AESGCM(different_key)
        nonce2 = os.urandom(12)
        encrypted2 = different_aesgcm.encrypt(nonce2, plaintext.encode(), None)
        logging.info("SQL-006: Encrypted with key2: %s", encrypted2.hex())
        
        self.assertNotEqual(encrypted1_hex, encrypted2.hex())
        logging.info("SQL-006: Verified ciphertexts are different for different keys.")
        
        with self.assertRaises(Exception):
            self.aesgcm.decrypt(nonce2, encrypted2, None)
        logging.info("SQL-006: Decryption with wrong key failed as expected.")

    def test_sql_007_tampering_detection(self):
        """
        SQL-007: Tampering Detection with GCM Authentication Tag
        ... (docstring unchanged) ...
        """
        plaintext = "ImportantData"
        encrypted_hex, nonce_hex = self._encrypt_data(plaintext)
        logging.info("SQL-007: Encrypted data for tampering test: %s", encrypted_hex)
        
        encrypted_bytes = bytes.fromhex(encrypted_hex)
        tampered = bytearray(encrypted_bytes)
        tampered[0] ^= 0xFF  # Flip bits in first byte
        logging.info("SQL-007: Tampered encrypted data (first byte flipped).")
        
        with self.assertRaises(Exception):
            self.aesgcm.decrypt(bytes.fromhex(nonce_hex), bytes(tampered), None)
        logging.info("SQL-007: Tampering detected and decryption failed as expected.")
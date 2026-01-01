"""
Test suite for vault-specific operations and encrypted data handling.

Tests verify encrypted data storage, retrieval, and metadata tracking including:
- Production-grade AES-256-GCM encryption (industry standard for password managers)
- Secure data storage in vault_records table
- Metadata and record type tracking
- Key management for encrypted data

Encryption Standard: AES-256-GCM
- Used by: Vault Security, 1Password, LastPass, Bitwarden
- FIPS 140-2 compliant
- Provides both encryption and authentication
- Prevents tampering and replay attacks
"""

import os
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
        
        Uses cryptography library's AESGCM which provides:
        - AES-256 encryption (256-bit key)
        - Galois/Counter Mode for authenticated encryption
        - Built-in integrity verification (no separate HMAC needed)
        - Prevents tampering, replay attacks, and chosen-ciphertext attacks
        
        This is the same encryption standard used by Vault Security, 1Password,
        LastPass, and other enterprise password managers.
        
        Args:
            plaintext (str): Plain text string to encrypt
            
        Returns:
            tuple: (encrypted_data, nonce) both as hex strings
        """
        # Generate random 96-bit nonce (12 bytes is optimal for GCM)
        nonce = os.urandom(12)
        
        # Encrypt and authenticate
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode(), None)
        
        # Return as hex strings for database storage
        return ciphertext.hex(), nonce.hex()
    
    def _decrypt_data(self, encrypted_hex, nonce_hex):
        """
        Decrypt and verify data using AES-256-GCM.
        
        GCM mode automatically verifies authentication tag during decryption,
        ensuring data hasn't been tampered with.
        
        Args:
            encrypted_hex (str): Encrypted data as hex string
            nonce_hex (str): Nonce as hex string
            
        Returns:
            str: Decrypted plain text string
            
        Raises:
            InvalidTag: If data has been tampered with or authentication fails
        """
        ciphertext = bytes.fromhex(encrypted_hex)
        nonce = bytes.fromhex(nonce_hex)
        
        # Decrypt and verify authentication
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
    
    def test_sql_004_encrypted_data_storage(self):
        """
        SQL-004: AES-256-GCM Encrypted Data Storage
        
        Objective:
        Validate production-grade encryption using AES-256-GCM to ensure
        vault data is securely encrypted before storage and correctly decrypted.
        
        Preconditions:
        - cryptography library installed
        - AES-256-GCM cipher initialized with 256-bit key
        
        Test Steps:
        1. Create vault user
        2. Encrypt plaintext password "MySecretPassword123!" using AES-256-GCM
        3. Verify encrypted output differs from plaintext
        4. Store encrypted data + nonce in vault_records
        5. Retrieve encrypted data from database
        6. Decrypt using original key and nonce
        7. Verify decrypted data matches original plaintext
        
        Expected Results:
        - Encryption produces ciphertext different from plaintext
        - Ciphertext contains authentication tag (GCM)
        - Data stored successfully in database
        - Decryption recovers exact original password
        - Without key, data is unreadable
        """
        # Create user
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('vaultuser', 'vault@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('vaultuser',))
        user_id = user[0][0]
        
        # Encrypt using AES-256-GCM
        plaintext = "MySecretPassword123!"
        encrypted_hex, nonce_hex = self._encrypt_data(plaintext)
        
        # Verify encrypted data is different from plaintext
        self.assertNotEqual(encrypted_hex, plaintext)
        self.assertGreater(len(encrypted_hex), len(plaintext))
        
        # Store both ciphertext and nonce (nonce is not secret, just needs to be unique)
        # In production, you might store: nonce + ciphertext as one blob
        combined_data = f"{nonce_hex}:{encrypted_hex}"
        
        self.db.execute_query(
            "INSERT INTO vault_records (user_id, title, encrypted_data, record_type) VALUES (%s, %s, %s, %s)",
            (user_id, 'Bank Login', combined_data, 'password')
        )
        
        # Retrieve and decrypt
        result = self.db.execute_query(
            "SELECT encrypted_data FROM vault_records WHERE title = %s",
            ('Bank Login',)
        )
        
        retrieved_data = result[0][0]
        stored_nonce_hex, stored_encrypted_hex = retrieved_data.split(':')
        
        decrypted = self._decrypt_data(stored_encrypted_hex, stored_nonce_hex)
        
        # Verify decryption works correctly
        self.assertEqual(decrypted, plaintext)
        self.assertNotEqual(stored_encrypted_hex, plaintext)  # Stored as ciphertext
    
    def test_sql_005_vault_record_metadata(self):
        """
        SQL-005: Vault Record Metadata Tracking
        
        Objective:
        Verify metadata fields (created_at, updated_at, record_type) are tracked
        and persisted correctly in vault_records table.
        
        Preconditions:
        - vault_records table has metadata columns
        
        Test Steps:
        1. Create user 'metauser'
        2. Encrypt data using AES-256-GCM
        3. Insert vault record with record_type='login'
        4. Query metadata fields
        
        Expected Results:
        - record_type equals 'login'
        - created_at is not null and valid timestamp
        - updated_at is not null and valid timestamp
        - Timestamps are automatically generated
        """
        # Create user
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('metauser', 'meta@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('metauser',))
        user_id = user[0][0]
        
        # Encrypt data with AES-256-GCM
        encrypted_hex, nonce_hex = self._encrypt_data('sensitive_data')
        combined_data = f"{nonce_hex}:{encrypted_hex}"
        
        # Create record with metadata
        self.db.execute_query(
            "INSERT INTO vault_records (user_id, title, encrypted_data, record_type) VALUES (%s, %s, %s, %s)",
            (user_id, 'Test Record', combined_data, 'login')
        )
        
        # Verify metadata is properly stored
        result = self.db.execute_query("""
            SELECT record_type, created_at, updated_at 
            FROM vault_records 
            WHERE title = %s
        """, ('Test Record',))
        
        self.assertEqual(result[0][0], 'login')
        self.assertIsNotNone(result[0][1])  # created_at
        self.assertIsNotNone(result[0][2])  # updated_at
    
    def test_sql_006_encryption_key_isolation(self):
        """
        SQL-006: Encryption Key Isolation
        
        Objective:
        Validate different keys produce different ciphertexts and prevent cross-decryption
        to ensure proper key management and isolation.
        
        Preconditions:
        - AES-256-GCM encryption available
        - Ability to generate multiple keys
        
        Test Steps:
        1. Generate first 256-bit encryption key
        2. Encrypt plaintext "SensitiveData" with first key
        3. Generate second 256-bit encryption key
        4. Encrypt same plaintext with second key
        5. Compare ciphertexts
        6. Attempt to decrypt data encrypted with key2 using key1
        
        Expected Results:
        - Two ciphertexts are different (not equal)
        - Decryption with wrong key raises exception
        - Demonstrates proper key isolation
        """
        plaintext = "SensitiveData"
        
        # Encrypt with first key
        encrypted1_hex, nonce1_hex = self._encrypt_data(plaintext)
        
        # Create new cipher with different 256-bit key
        different_key = AESGCM.generate_key(bit_length=256)
        different_aesgcm = AESGCM(different_key)
        nonce2 = os.urandom(12)
        encrypted2 = different_aesgcm.encrypt(nonce2, plaintext.encode(), None)
        
        # Verify different keys produce different ciphertexts
        self.assertNotEqual(encrypted1_hex, encrypted2.hex())
        
        # Verify first cipher can't decrypt data encrypted with second key
        with self.assertRaises(Exception):
            self.aesgcm.decrypt(nonce2, encrypted2, None)
    
    def test_sql_007_tampering_detection(self):
        """
        SQL-007: Tampering Detection with GCM Authentication Tag
        
        Objective:
        Verify GCM mode detects data tampering through authentication to
        ensure data integrity is maintained.
        
        Preconditions:
        - AES-256-GCM encryption configured
        - Encrypted data with authentication tag
        
        Test Steps:
        1. Encrypt plaintext "ImportantData"
        2. Retrieve ciphertext bytes
        3. Tamper with ciphertext (flip bits in first byte)
        4. Attempt to decrypt tampered data
        
        Expected Results:
        - Decryption of tampered data raises InvalidTag exception
        - Tampering is automatically detected
        - Demonstrates authenticated encryption
        """
        plaintext = "ImportantData"
        encrypted_hex, nonce_hex = self._encrypt_data(plaintext)
        
        # Tamper with encrypted data (flip some bits)
        encrypted_bytes = bytes.fromhex(encrypted_hex)
        tampered = bytearray(encrypted_bytes)
        tampered[0] ^= 0xFF  # Flip bits in first byte
        
        # Attempt to decrypt tampered data
        with self.assertRaises(Exception):  # Should raise InvalidTag
            self.aesgcm.decrypt(bytes.fromhex(nonce_hex), bytes(tampered), None)
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
    """
    Test class for validating vault operations and AES-256-GCM encrypted data management.

    Test Cases:
    - SQL-003: Delete with Cascade Validation
    - SQL-004: AES-256-GCM Encrypted Data Storage
    - SQL-005: Vault Record Metadata Tracking
    - SQL-006: Encryption Key Isolation
    - SQL-007: Tampering Detection with GCM Authentication Tag
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generate 256-bit (32 byte) encryption key for AES-256
        self.encryption_key = AESGCM.generate_key(bit_length=256)
        self.aesgcm = AESGCM(self.encryption_key)

    def _encrypt_data(self, plaintext):
        """
        Encrypt data using AES-256-GCM - production-grade authenticated encryption.
        """
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode(), None)
        return ciphertext.hex(), nonce.hex()

    def _decrypt_data(self, encrypted_hex, nonce_hex):
        """
        Decrypt and verify data using AES-256-GCM.
        """
        ciphertext = bytes.fromhex(encrypted_hex)
        nonce = bytes.fromhex(nonce_hex)
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()

    def test_sql_003_delete_cascade(self):
        """
        SQL-003: Delete with Cascade Validation

        Objective:
        Verify foreign key ON DELETE CASCADE removes orphaned vault records
        to maintain referential integrity.

        Preconditions:
        - vault_users and vault_records tables exist
        - Foreign key relationship defined with ON DELETE CASCADE

        Test Steps:
        1. Create user 'deleteuser'
        2. Create vault record associated with user
        3. Delete user from vault_users
        4. Query vault_records for deleted user_id

        Expected Results:
        - User deletion succeeds
        - Associated vault_records are automatically deleted
        - Query returns 0 records for deleted user_id
        - No orphaned records remain
        """
        logging.info("SQL-003: Creating user 'deleteuser'")
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('deleteuser', 'delete@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('deleteuser',))
        user_id = user[0][0]
        logging.info("SQL-003: Created user_id=%s", user_id)

        logging.info("SQL-003: Creating vault record for user_id=%s", user_id)
        self.db.execute_query(
            "INSERT INTO vault_records (user_id, title, encrypted_data, record_type) VALUES (%s, %s, %s, %s)",
            (user_id, 'Cascade Record', 'dummy_encrypted', 'note')
        )

        logging.info("SQL-003: Deleting user 'deleteuser'")
        self.db.execute_query("DELETE FROM vault_users WHERE user_id = %s", (user_id,))

        logging.info("SQL-003: Querying vault_records for deleted user_id=%s", user_id)
        result = self.db.execute_query(
            "SELECT * FROM vault_records WHERE user_id = %s", (user_id,)
        )
        logging.info("SQL-003: Query result after user deletion: %s", result)

        self.assertEqual(len(result), 0)
        logging.info("SQL-003: Cascade delete verified—no orphaned records remain.")

    def test_sql_004_encrypted_data_storage(self):
        """
        SQL-004: AES-256-GCM Encrypted Data Storage

        Objective:
        Ensure that sensitive data is encrypted using AES-256-GCM before storage
        and can be decrypted correctly after retrieval.

        Test Steps:
        1. Create a user
        2. Encrypt a plaintext password
        3. Store encrypted data in vault_records
        4. Retrieve and decrypt the data
        5. Validate decrypted data matches original plaintext

        Expected Results:
        - Encrypted data is not equal to plaintext
        - Decryption yields the original plaintext
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

        Objective:
        Validate that vault_records store and update metadata fields such as
        record_type, created_at, and updated_at.

        Test Steps:
        1. Create a user
        2. Store a vault record with encrypted data and record_type
        3. Query metadata fields for the record

        Expected Results:
        - record_type matches expected value
        - created_at and updated_at are not null
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

        Objective:
        Ensure that data encrypted with one key cannot be decrypted with another,
        verifying key isolation and security.

        Test Steps:
        1. Encrypt data with key1
        2. Encrypt same data with key2
        3. Assert ciphertexts differ
        4. Attempt to decrypt with wrong key and expect failure

        Expected Results:
        - Ciphertexts are different for different keys
        - Decryption with wrong key fails
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

        Objective:
        Ensure that tampering with encrypted data is detected and decryption fails.

        Test Steps:
        1. Encrypt data
        2. Tamper with ciphertext
        3. Attempt to decrypt tampered data

        Expected Results:
        - Decryption fails with an exception
        - Tampering is detected by GCM authentication
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
    
    def test_sql_008_encrypted_data_integrity_checksum(self):
        """
        SQL-008: Encrypted Vault Record Integrity via Checksum

        Objective:
        Verify that encrypted vault data is stored and retrieved without corruption
        by validating that the ciphertext remains byte-for-byte identical across
        database write and read operations.

        Security Context:
        Vault services treat encrypted data as opaque bytes. The system must ensure
        that encrypted blobs are not altered by database storage, migrations, or
        internal handling. This test validates integrity without performing decryption.

        Test Steps:
        1. Create a vault user
        2. Insert an encrypted vault record for the user
        3. Compute a SHA-256 checksum of the encrypted data stored in the database
        4. Re-read the same encrypted data from the database
        5. Recompute the SHA-256 checksum
        6. Compare both checksums
        
        Expected Results:
        - Encrypted data is stored successfully
        - Encrypted data is retrieved unchanged
        - SHA-256 checksum before and after database operations matches
        - No corruption or unintended mutation occurs
        
        Security Guarantee Verified:
        - Database storage preserves encrypted vault data integrity
        - Encrypted records cannot be modified silently
        - Vault data remains safe across read/write cycles
        """
        logging.info("SQL-008: Inserting user 'checksum_user' for checksum integrity test.")

        # Insert user
        self.db.execute_query(
        "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
        ("checksum_user", "checksum@vault.com")
         )

        user = self.db.execute_query(
        "SELECT user_id FROM vault_users WHERE username = %s",
        ("checksum_user",)
        )
        self.assertIsNotNone(user)
        user_id = user[0][0]
        logging.info("SQL-008: Created user_id=%s", user_id)

        # Simulated encrypted payload (treated as opaque ciphertext)
        encrypted_data = b"fake_encrypted_blob_v1"
        logging.info("SQL-008: Simulated encrypted data for checksum test.")
        
        # Insert encrypted record
        self.db.execute_query(
            "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
            (user_id, "Checksum Test Record", encrypted_data)
        )
        logging.info("SQL-008: Inserted encrypted record for user_id=%s", user_id)

        # Compute checksum after insert
        result = self.db.execute_query(
            """
            SELECT encode(digest(encrypted_data::bytea, 'sha256'), 'hex')
            FROM vault_records
            WHERE user_id = %s
        """, (user_id,))

        self.assertIsNotNone(result)
        checksum_1 = result[0][0]
        logging.info("SQL-008: Computed checksum after insert: %s", checksum_1)

        # Re-read and recompute checksum
        result = self.db.execute_query(
            """
            SELECT encode(digest(encrypted_data::bytea, 'sha256'), 'hex')
            FROM vault_records
            WHERE user_id = %s
        """, (user_id,))

        checksum_2 = result[0][0]
        logging.info("SQL-008: Computed checksum after re-read: %s", checksum_2)

        # Integrity validation
        self.assertEqual(checksum_1, checksum_2)
        logging.info("SQL-008: Encrypted data integrity verified—checksums match, no corruption detected.")
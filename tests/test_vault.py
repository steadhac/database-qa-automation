import hashlib
import base64
from framework.base_test import BaseTest

class TestVaultOperations(BaseTest):
    
    def _encrypt_data(self, plaintext):
        """Simple encryption simulation for testing"""
        return base64.b64encode(plaintext.encode()).decode()
    
    def _decrypt_data(self, encrypted):
        """Simple decryption simulation for testing"""
        return base64.b64decode(encrypted.encode()).decode()
    
    def test_encrypted_data_storage(self):
        """Test storing and retrieving encrypted vault data"""
        # Create user
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('vaultuser', 'vault@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('vaultuser',))
        user_id = user[0][0]
        
        # Encrypt and store
        plaintext = "MySecretPassword123!"
        encrypted = self._encrypt_data(plaintext)
        
        self.db.execute_query(
            "INSERT INTO vault_records (user_id, title, encrypted_data, record_type) VALUES (%s, %s, %s, %s)",
            (user_id, 'Bank Login', encrypted, 'password')
        )
        
        # Retrieve and decrypt
        result = self.db.execute_query(
            "SELECT encrypted_data FROM vault_records WHERE title = %s",
            ('Bank Login',)
        )
        
        decrypted = self._decrypt_data(result[0][0])
        self.assertEqual(decrypted, plaintext)
    
    def test_vault_record_metadata(self):
        """Test vault record metadata is properly tracked"""
        # Create user
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('metauser', 'meta@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('metauser',))
        user_id = user[0][0]
        
        # Create record
        self.db.execute_query(
            "INSERT INTO vault_records (user_id, title, encrypted_data, record_type) VALUES (%s, %s, %s, %s)",
            (user_id, 'Test Record', 'encrypted', 'login')
        )
        
        # Verify metadata
        result = self.db.execute_query("""
            SELECT record_type, created_at, updated_at 
            FROM vault_records 
            WHERE title = %s
        """, ('Test Record',))
        
        self.assertEqual(result[0][0], 'login')
        self.assertIsNotNone(result[0][1])  # created_at
        self.assertIsNotNone(result[0][2])  # updated_at
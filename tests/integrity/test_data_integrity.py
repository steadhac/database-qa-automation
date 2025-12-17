"""
Test suite for data integrity validation.

Tests verify database constraints, data consistency, and referential integrity including:
- Unique constraints on username and email
- Foreign key constraints between users and records
- Data consistency across concurrent updates
"""

from framework.base_test import BaseTest

class TestDataIntegrity(BaseTest):
    """Test class for validating data integrity and constraint enforcement."""
    
    def test_int_001_unique_constraint_enforcement(self):
        """
        INT-001: Unique Constraint Enforcement
        
        Objective:
        Verify UNIQUE constraints on username and email prevent duplicates
        to maintain data integrity and prevent duplicate accounts.
        
        Preconditions:
        - vault_users table has UNIQUE constraints on username and email
        
        Test Steps:
        1. Insert user with username 'john' and email 'john@vault.com'
        2. Attempt to insert second user with same username 'john' but different email
        3. Catch exception
        
        Expected Results:
        - First insertion succeeds
        - Second insertion fails with constraint violation exception
        - Database rejects duplicate username
        """
        # Create first user
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('john', 'john@vault.com')
        )
        
        # Attempt duplicate username - should raise exception
        with self.assertRaises(Exception):
            self.db.execute_query(
                "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
                ('john', 'different@vault.com')
            )
    
    def test_int_002_foreign_key_constraint(self):
        """
        INT-002: Foreign Key Constraint Validation
        
        Objective:
        Prevent orphaned vault records through foreign key enforcement
        to ensure referential integrity between users and records.
        
        Preconditions:
        - Foreign key exists: vault_records.user_id → vault_users.user_id
        
        Test Steps:
        1. Attempt to insert vault_record with user_id=99999 (non-existent)
        2. Catch foreign key violation exception
        
        Expected Results:
        - INSERT fails with foreign key constraint violation
        - No orphaned record is created
        - Database maintains referential integrity
        """
        # Attempt to insert record with non-existent user_id
        with self.assertRaises(Exception):
            self.db.execute_query(
                "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
                (99999, 'Test', 'data')
            )
    
    def test_int_003_concurrent_update_consistency(self):
        """
        INT-003: Concurrent Update Consistency
        
        Objective:
        Validate data consistency after multiple sequential updates
        to ensure no duplicate records and final state is correct.
        
        Preconditions:
        - User and vault record exist
        
        Test Steps:
        1. Create user 'consistent'
        2. Create vault record with encrypted_data='v1'
        3. Perform 5 sequential UPDATE operations (v2, v3, v4, v5, v6)
        4. Query final state
        5. Verify record count
        
        Expected Results:
        - Final encrypted_data equals 'v6'
        - Only 1 record exists (no duplicates from updates)
        - All updates applied correctly
        """
        # Create user
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('consistent', 'consistent@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('consistent',))
        user_id = user[0][0]
        
        # Create record
        self.db.execute_query(
            "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
            (user_id, 'Login', 'v1')
        )
        
        # Multiple updates - simulating concurrent modifications
        for i in range(5):
            self.db.execute_query(
                "UPDATE vault_records SET encrypted_data = %s WHERE title = %s",
                (f'v{i+2}', 'Login')
            )
        
        # Verify final state
        result = self.db.execute_query("SELECT encrypted_data FROM vault_records WHERE title = %s", ('Login',))
        self.assertEqual(result[0][0], 'v6')
        
        # Verify count - ensure no duplicate records were created
        count = self.db.execute_query("SELECT COUNT(*) FROM vault_records WHERE user_id = %s", (user_id,))
        self.assertEqual(count[0][0], 1)
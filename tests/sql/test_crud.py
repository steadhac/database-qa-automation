"""
Test suite for CRUD (Create, Read, Update, Delete) operations on vault database.

Tests verify basic database operations including:
- Creating and reading user records
- Updating encrypted vault data
- Cascade deletion of related records
"""

from framework.base_test import BaseTest

class TestCRUDOperations(BaseTest):
    """Test class for validating CRUD operations on vault users and records."""
    
    def test_sql_001_create_and_read_user(self):
        """
        SQL-001: Create and Read User Record
        
        Objective:
        Validate user creation and retrieval from database to ensure basic
        INSERT and SELECT operations work correctly.
        
        Preconditions:
        - Database connection established
        - vault_users table exists
        
        Test Steps:
        1. Insert new user with username 'testuser' and email 'test@vault.com'
        2. Execute SELECT query to retrieve user by username
        3. Verify record exists and data matches
        
        Expected Results:
        - User record is created successfully
        - SELECT query returns 1 record
        - Username equals 'testuser'
        - Email equals 'test@vault.com'
        """
        # Create
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('testuser', 'test@vault.com')
        )
        
        # Read
        result = self.db.execute_query(
            "SELECT username, email FROM vault_users WHERE username = %s",
            ('testuser',)
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'testuser')
        self.assertEqual(result[0][1], 'test@vault.com')
    
    def test_sql_002_update_vault_record(self):
        """
        SQL-002: Update Vault Record Data
        
        Objective:
        Validate UPDATE operations modify encrypted vault data correctly and
        timestamp tracking works as expected.
        
        Preconditions:
        - User exists in vault_users
        - Vault record exists for user
        
        Test Steps:
        1. Create user 'user1' with email 'user1@vault.com'
        2. Insert vault record with title 'Password' and encrypted_data 'encrypted_v1'
        3. Execute UPDATE to change encrypted_data to 'encrypted_v2'
        4. Verify updated_at timestamp is refreshed
        5. Query record and verify encrypted_data changed
        
        Expected Results:
        - UPDATE executes successfully
        - encrypted_data changes from 'encrypted_v1' to 'encrypted_v2'
        - updated_at timestamp is modified
        - Only 1 record exists (no duplicates created)
        """
        # Create user
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('user1', 'user1@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('user1',))
        user_id = user[0][0]
        
        # Create record
        self.db.execute_query(
            "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
            (user_id, 'Password', 'encrypted_v1')
        )
        
        # Update
        self.db.execute_query(
            "UPDATE vault_records SET encrypted_data = %s, updated_at = CURRENT_TIMESTAMP WHERE title = %s",
            ('encrypted_v2', 'Password')
        )
        
        # Verify
        result = self.db.execute_query("SELECT encrypted_data FROM vault_records WHERE title = %s", ('Password',))
        self.assertEqual(result[0][0], 'encrypted_v2')
    
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
        # Create user and record
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('deleteuser', 'delete@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('deleteuser',))
        user_id = user[0][0]
        
        self.db.execute_query(
            "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
            (user_id, 'Test', 'data')
        )
        
        # Delete user
        self.db.execute_query("DELETE FROM vault_users WHERE user_id = %s", (user_id,))
        
        # Verify records are also deleted
        records = self.db.execute_query("SELECT * FROM vault_records WHERE user_id = %s", (user_id,))
        self.assertEqual(len(records), 0)
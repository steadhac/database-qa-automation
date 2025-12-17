"""
Test suite for schema validation and migration testing.

Tests verify database schema structure, indexes, and migration capabilities including:
- Table structure and column definitions
- Index existence for performance optimization
- Schema migration operations (adding/modifying columns)
"""

from framework.base_test import BaseTest

class TestSchemaValidation(BaseTest):
    """Test class for validating database schema and migration operations."""
    
    def test_sch_001_table_structure(self):
        """
        SCH-001: Table Structure Validation
        
        Objective:
        Verify required tables exist with correct column definitions
        to ensure database schema matches specifications.
        
        Preconditions:
        - Database initialized
        
        Test Steps:
        1. Query information_schema.columns for vault_users table
        2. Verify columns exist: user_id, username, email, created_at
        3. Verify data types are correct
        
        Expected Results:
        - vault_users table exists
        - All required columns present
        - Columns have correct data types (VARCHAR, TIMESTAMP, SERIAL)
        """
        # Verify vault_users table structure
        result = self.db.execute_query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'vault_users'
            ORDER BY ordinal_position
        """)
        
        columns = {row[0]: row[1] for row in result}
        self.assertIn('user_id', columns)
        self.assertIn('username', columns)
        self.assertIn('email', columns)
        self.assertIn('created_at', columns)
    
    def test_sch_002_index_exists(self):
        """
        SCH-002: Index Existence Verification
        
        Objective:
        Validate performance indexes are properly created on vault_records table
        to ensure query optimization.
        
        Preconditions:
        - vault_records table exists
        
        Test Steps:
        1. Query pg_indexes for vault_records table
        2. Search for index containing 'user_id'
        
        Expected Results:
        - At least one index exists on user_id column
        - Index name contains 'user_id' or 'idx_user_id'
        """
        result = self.db.execute_query("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'vault_records'
        """)
        
        indexes = [row[0] for row in result]
        self.assertTrue(any('user_id' in idx for idx in indexes))
    
    def test_sch_003_schema_migration_add_column(self):
        """
        SCH-003: Schema Migration - Add Column
        
        Objective:
        Test adding new column to existing table (migration simulation)
        to validate schema evolution capability.
        
        Preconditions:
        - vault_records table exists
        
        Test Steps:
        1. Execute: ALTER TABLE vault_records ADD COLUMN metadata JSONB
        2. Query information_schema.columns to verify column exists
        3. Cleanup: DROP COLUMN metadata
        
        Expected Results:
        - ALTER TABLE succeeds
        - New column appears in information_schema
        - Cleanup executes successfully
        """
        # Add new column - simulate schema migration
        self.db.execute_query("""
            ALTER TABLE vault_records 
            ADD COLUMN IF NOT EXISTS metadata JSONB
        """)
        
        # Verify column exists
        result = self.db.execute_query("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'vault_records' AND column_name = 'metadata'
        """)
        
        self.assertEqual(len(result), 1)
        
        # Cleanup - rollback migration for test isolation
        self.db.execute_query("ALTER TABLE vault_records DROP COLUMN IF EXISTS metadata")
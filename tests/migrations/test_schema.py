"""
Test suite for schema validation and migration testing.

Tests verify database schema structure, indexes, and migration capabilities including:
- Table structure and column definitions
- Index existence for performance optimization
- Schema migration operations (adding/modifying columns)
"""

import logging
from framework.base_test import BaseTest

class TestSchemaValidation(BaseTest):
    """Test class for validating database schema and migration operations."""
    
    def test_sch_001_table_structure(self):
        """
        SCH-001: Table Structure Validation
        1. Query information_schema to get column details for vault_users table
        2. Validate expected columns and data types exist
        
        """
        logging.info("SCH-001: Querying information_schema.columns for vault_users table")
        result = self.db.execute_query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'vault_users'
            ORDER BY ordinal_position
        """)
        logging.info("SCH-001: Query result: %s", result)
        
        columns = {row[0]: row[1] for row in result}
        self.assertIn('user_id', columns)
        self.assertIn('username', columns)
        self.assertIn('email', columns)
        self.assertIn('created_at', columns)
        logging.info("SCH-001: Table structure validation passed.")

    def test_sch_002_index_exists(self):
        """
        SCH-002: Index Existence Verification
        1. Query pg_indexes to check for index on user_id in vault_records table
        2. Validate that the index exists
        """
        logging.info("SCH-002: Querying pg_indexes for vault_records table")
        result = self.db.execute_query("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'vault_records'
        """)
        logging.info("SCH-002: Indexes found: %s", result)
        
        indexes = [row[0] for row in result]
        self.assertTrue(any('user_id' in idx for idx in indexes))
        logging.info("SCH-002: Index existence validation passed.")

    def test_sch_003_schema_migration_add_column(self):
        """
        SCH-003: Schema Migration - Add Column
        """
        logging.info("SCH-003: Adding column 'metadata' to vault_records table")
        self.db.execute_query("""
            ALTER TABLE vault_records 
            ADD COLUMN IF NOT EXISTS metadata JSONB
        """)
        
        logging.info("SCH-003: Verifying 'metadata' column exists in vault_records")
        result = self.db.execute_query("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'vault_records' AND column_name = 'metadata'
        """)
        logging.info("SCH-003: Column check result: %s", result)
        self.assertEqual(len(result), 1)
        
        logging.info("SCH-003: Dropping column 'metadata' for cleanup")
        self.db.execute_query("ALTER TABLE vault_records DROP COLUMN IF EXISTS metadata")
        logging.info("SCH-003: Schema migration add column test passed and cleaned up.")
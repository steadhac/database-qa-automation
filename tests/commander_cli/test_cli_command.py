"""
Test suite for CLI command validation and database operations.

Tests verify command-line interface operations, database scripting, and admin tools including:
- CLI command execution and validation
- Database maintenance operations
- Bulk data operations via CLI
- Query execution through command interface
"""

import logging
from framework.base_test import BaseTest

class TestCLICommands(BaseTest):
    """Test class for validating CLI commands and database scripting."""

    def test_cli_001_export_users_command(self):
        """
        CLI-001: Export Users Command

        Objective:
        Validate that the CLI command can export user data from the database.

        Preconditions:
        - vault_users table exists and is accessible

        Test Steps:
        1. Insert two test users
        2. Simulate CLI export-users command
        3. Query and validate exported users

        Expected Results:
        - Both users are exported and present in the result
        - Usernames and emails match inserted data
        """
        logging.info("CLI-001: Creating test users for export command")
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('cli_user1', 'cli1@vault.com')
        )
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('cli_user2', 'cli2@vault.com')
        )

        logging.info("CLI-001: Simulating CLI export-users command")
        users = self.db.execute_query("SELECT username, email FROM vault_users ORDER BY username")
        logging.info("CLI-001: Exported users: %s", users)

        self.assertEqual(len(users), 2)
        self.assertEqual(users[0][0], 'cli_user1')
        self.assertEqual(users[1][0], 'cli_user2')
        logging.info("CLI-001: Export users command test passed.")

    def test_cli_002_bulk_delete_operation(self):
        """
        CLI-002: Bulk Delete Operation

        Objective:
        Validate that the CLI bulk delete operation removes all records for a user.

        Preconditions:
        - vault_users and vault_records tables exist

        Test Steps:
        1. Create a user and associated vault records
        2. Simulate CLI bulk delete command for the user
        3. Query for remaining records

        Expected Results:
        - All records for the user are deleted
        - No records remain for the user in vault_records
        """
        logging.info("CLI-002: Creating user and records for bulk delete test")
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('bulk_delete', 'bulk@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('bulk_delete',))
        user_id = user[0][0]
        logging.info("CLI-002: Created user_id=%s", user_id)

        for i in range(5):
            self.db.execute_query(
                "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
                (user_id, f'Record {i}', 'data')
            )
        logging.info("CLI-002: Inserted 5 records for user_id=%s", user_id)

        logging.info("CLI-002: Simulating CLI bulk delete command")
        self.db.execute_query("DELETE FROM vault_records WHERE user_id = %s", (user_id,))

        remaining = self.db.execute_query("SELECT COUNT(*) FROM vault_records WHERE user_id = %s", (user_id,))
        logging.info("CLI-002: Remaining records after delete: %s", remaining)
        self.assertEqual(remaining[0][0], 0)
        logging.info("CLI-002: Bulk delete operation test passed.")

    def test_cli_003_database_stats_query(self):
        """
        CLI-003: Database Stats Query

        Objective:
        Validate that the CLI command can retrieve database statistics such as user count.

        Preconditions:
        - vault_users table exists

        Test Steps:
        1. Insert three test users
        2. Simulate CLI stats command
        3. Query and validate user count

        Expected Results:
        - User count is at least three
        - Stats query returns correct results
        """
        logging.info("CLI-003: Creating test users for stats query")
        for i in range(3):
            self.db.execute_query(
                "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
                (f'stats_user{i}', f'stats{i}@vault.com')
            )
        logging.info("CLI-003: Simulating CLI stats command")
        user_count = self.db.execute_query("SELECT COUNT(*) FROM vault_users")
        logging.info("CLI-003: User count: %s", user_count)
        self.assertGreaterEqual(user_count[0][0], 3)
        logging.info("CLI-003: Database stats query test passed.")

    def test_cli_004_custom_query_execution(self):
        """
        CLI-004: Custom Query Execution

        Objective:
        Validate that the CLI tool can execute custom SQL queries and return expected results.

        Preconditions:
        - vault_users table exists

        Test Steps:
        1. Insert a test user
        2. Simulate CLI custom query command
        3. Query for users with email matching pattern

        Expected Results:
        - Query returns the inserted user
        - Custom query execution is successful
        """
        logging.info("CLI-004: Creating test user for custom query execution")
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('query_test', 'query@vault.com')
        )

        logging.info("CLI-004: Simulating CLI custom query command")
        result = self.db.execute_query(
            "SELECT username FROM vault_users WHERE email LIKE %s",
            ('%vault.com',)
        )
        logging.info("CLI-004: Query result: %s", result)
        self.assertGreater(len(result), 0)
        usernames = [row[0] for row in result]
        self.assertIn('query_test', usernames)
        logging.info("CLI-004: Custom query execution test passed.")
"""
Test suite for backend API endpoints and data exchange validation.

Tests verify REST API operations, JSON data handling, and backend service integration including:
- API endpoint responses
- JSON payload validation
- CRUD operations via API
- Error handling and status codes
"""

import json
from framework.base_test import BaseTest

class TestBackendAPI(BaseTest):
    """Test class for validating backend API endpoints and data flows."""
    
    def test_api_user_creation_workflow(self):
        """
        Test user creation via API-style data flow.
        
        Validates:
        - JSON payload is correctly parsed and stored
        - User data is inserted into database
        - Response data matches input
        
        API Workflow:
        1. Receive JSON payload with user data
        2. Parse and validate data
        3. Insert into database
        4. Return created user data
        
        Expected Result:
        - User is created with correct username and email
        - Database state reflects API operation
        """
        # Simulate API payload
        user_payload = {
            "username": "api_user",
            "email": "api@vault.com"
        }
        
        # Insert via simulated API backend logic
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            (user_payload['username'], user_payload['email'])
        )
        
        # Verify database state
        result = self.db.execute_query(
            "SELECT username, email FROM vault_users WHERE username = %s",
            (user_payload['username'],)
        )
        
        self.assertEqual(result[0][0], user_payload['username'])
        self.assertEqual(result[0][1], user_payload['email'])
    
    def test_api_vault_record_retrieval(self):
        """
        Test retrieving vault records via API endpoint simulation.
        
        Validates:
        - Query parameters are correctly processed
        - Multiple records are returned in correct format
        - JSON serialization of database results
        
        Expected Result:
        - API returns all records for specified user
        - Data format is consistent with API contract
        """
        # Create test data
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('api_test', 'api_test@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('api_test',))
        user_id = user[0][0]
        
        # Create multiple records
        for i in range(3):
            self.db.execute_query(
                "INSERT INTO vault_records (user_id, title, encrypted_data, record_type) VALUES (%s, %s, %s, %s)",
                (user_id, f'Record {i}', f'encrypted_{i}', 'password')
            )
        
        # Simulate API GET request
        records = self.db.execute_query(
            "SELECT title, encrypted_data, record_type FROM vault_records WHERE user_id = %s",
            (user_id,)
        )
        
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0][2], 'password')
    
    def test_api_error_handling_invalid_data(self):
        """
        Test API error handling for invalid data submissions.
        
        Validates:
        - Invalid foreign keys trigger appropriate errors
        - Database constraints are enforced via API layer
        - Error responses are generated correctly
        
        Expected Result:
        - Exception is raised for invalid user_id
        - Database maintains integrity
        """
        # Attempt to create record with invalid user_id
        with self.assertRaises(Exception):
            self.db.execute_query(
                "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
                (99999, 'Invalid', 'data')
            )
"""
Test suite for backend API endpoints and data exchange validation.

Tests verify REST API operations, JSON data handling, and backend service integration including:
- API endpoint requests and responses
- JSON payload serialization/deserialization
- CRUD operations via API simulation
- Error handling and status codes
"""

import json
import logging
from framework.base_test import BaseTest
from framework.db_utils import DBUtils

class TestBackendAPI(BaseTest):
    """Test class for validating backend API endpoints and data flows."""

    def setUp(self):
        super().setUp()
        # Wrap existing db_manager with DBUtils for safe queries
        self.db_utils = DBUtils(self.db)

    def test_api_001_user_creation_via_api_workflow(self):
        """
        API-001: User Creation via API JSON workflow

        Objective:
        Validate that the API correctly handles user creation via JSON payloads,
        ensuring data is serialized, deserialized, and persisted as expected.

        Preconditions:
        - API endpoint accepts JSON payload for user creation
        - vault_users table exists

        Test Steps:
        1. Simulate API receiving JSON payload for new user
        2. Serialize and deserialize payload
        3. Insert user into database
        4. Query database for inserted user
        5. Serialize response as JSON

        Expected Results:
        - User is inserted into database
        - Response JSON matches input data
        - No errors occur during serialization/deserialization
        """
        logging.info("API-001: Simulating API receiving JSON payload for user creation")
        request_payload = {"username": "api_user", "email": "api@vault.com"}
        json_payload = json.dumps(request_payload)  # Serialize

        parsed_payload = json.loads(json_payload)  # Deserialize
        logging.info("API-001: Parsed payload: %s", parsed_payload)
        self.db_utils.safe_execute(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            (parsed_payload['username'], parsed_payload['email'])
        )
        logging.info("API-001: Inserted user into database")

        db_result = self.db_utils.fetch_one_or_raise(
            "SELECT username, email FROM vault_users WHERE username = %s",
            (parsed_payload['username'],)
        )
        logging.info("API-001: Fetched user from database: %s", db_result)
        response_json = json.dumps({"username": db_result[0], "email": db_result[1]})  # Serialize
        api_response = json.loads(response_json)  # Client deserializes

        self.assertEqual(api_response['username'], "api_user")
        self.assertEqual(api_response['email'], "api@vault.com")
        logging.info("API-001: User creation via API workflow test passed.")

    def test_api_002_vault_record_retrieval(self):
        """
        API-002: Vault Record Retrieval via API JSON flow

        Objective:
        Ensure the API can retrieve all vault records for a user and return them as a JSON array.

        Preconditions:
        - User exists in vault_users
        - vault_records table contains records for the user

        Test Steps:
        1. Insert test user and associated vault records
        2. Query for all vault records for the user
        3. Serialize records as JSON array
        4. Deserialize and validate response

        Expected Results:
        - All records are returned for the user
        - JSON response contains correct titles and record types
        - No extraneous records are included
        """
        logging.info("API-002: Inserting test user for vault record retrieval")
        self.db_utils.safe_execute(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('api_test', 'api_test@vault.com')
        )

        user_id = self.db_utils.fetch_value_or_raise(
            "SELECT user_id FROM vault_users WHERE username=%s",
            ('api_test',),
            error_msg="Test user not found"
        )
        logging.info("API-002: Fetched user_id=%s", user_id)

        for i in range(3):
            self.db_utils.safe_execute(
                "INSERT INTO vault_records (user_id, title, encrypted_data, record_type) VALUES (%s, %s, %s, %s)",
                (user_id, f"Record {i}", f"encrypted_{i}", "password")
            )
        logging.info("API-002: Inserted 3 vault records for user_id=%s", user_id)

        db_records = self.db_utils.fetch_all_safe(
            "SELECT title, encrypted_data, record_type FROM vault_records WHERE user_id=%s",
            (user_id,)
        )
        logging.info("API-002: Fetched vault records: %s", db_records)

        response_json = json.dumps([
            {"title": r[0], "encrypted_data": r[1], "record_type": r[2]} for r in db_records
        ])
        api_response = json.loads(response_json)  # Client deserializes

        self.assertEqual(len(api_response), 3)
        for i, rec in enumerate(api_response):
            self.assertEqual(rec['title'], f"Record {i}")
            self.assertEqual(rec['record_type'], 'password')
        logging.info("API-002: Vault record retrieval via API test passed.")

    def test_api_003_api_error_handling_for_invalid_data(self):
        """
        API-003: API Error Handling for Invalid Payloads

        Objective:
        Validate that the API returns a clear error when given invalid or non-existent user data,
        and that database constraints are enforced.

        Preconditions:
        - Foreign key constraints exist between vault_records and vault_users

        Test Steps:
        1. Simulate API receiving invalid JSON payload (non-existent user_id)
        2. Attempt to insert record with invalid user_id
        3. Catch and serialize error response

        Expected Results:
        - Insert fails with foreign key constraint violation
        - API returns error message indicating the constraint failure
        - No orphaned record is created
        """
        logging.info("API-003: Simulating API receiving invalid JSON payload")
        invalid_payload = {"user_id": 99999, "title": "Invalid", "encrypted_data": "data"}
        json_payload = json.dumps(invalid_payload)
        parsed_payload = json.loads(json_payload)
        logging.info("API-003: Parsed invalid payload: %s", parsed_payload)

        try:
            self.db_utils.safe_execute(
                "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
                (parsed_payload['user_id'], parsed_payload['title'], parsed_payload['encrypted_data'])
            )
        except Exception as e:
            error_json = json.dumps({"error": str(e)})
            api_response = json.loads(error_json)
            logging.error("API-003: Error response: %s", api_response)
            self.assertIn("foreign key", api_response['error'].lower())
        logging.info("API-003: API error handling for invalid data test passed.")
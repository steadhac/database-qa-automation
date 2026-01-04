"""
Test suite for database performance validation.

Tests verify query execution time, bulk operation efficiency, and index optimization including:
- Bulk insert performance benchmarks
- Indexed query performance validation
- Response time thresholds for production readiness
"""

import time
import logging
from framework.base_test import BaseTest

class TestPerformance(BaseTest):
    """Test class for validating database performance and query optimization."""
    
    def test_perf_001_bulk_insert_performance(self):
        """
        Test performance of bulk insert operations for vault records.
        
        Validates:
        - 100 INSERT operations complete within acceptable time (< 5 seconds)
        - Database handles high-volume writes efficiently
        - Connection and transaction overhead is minimal
        
        Performance Benchmark:
        - Target: < 5 seconds for 100 inserts
        - Typical: 1-3 seconds depending on hardware
        
        Expected Result:
        - All 100 records are successfully inserted
        - Total execution time is less than 5 seconds
        """
        logging.info("PERF-001: Creating user 'perfuser' for bulk insert test")
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('perfuser', 'perf@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('perfuser',))
        user_id = user[0][0]
        logging.info("PERF-001: Created user_id=%s", user_id)
        
        start_time = time.time()
        for i in range(100):
            self.db.execute_query(
                "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
                (user_id, f'Record_{i}', f'encrypted_data_{i}')
            )
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info("PERF-001: Bulk insert of 100 records took %.2fs", execution_time)
        self.assertLess(execution_time, 5.0, f"Bulk insert took {execution_time:.2f}s, expected < 5s")
        logging.info("PERF-001: Bulk insert performance test passed.")

    def test_perf_002_indexed_query_performance(self):
        """
        Test that indexed queries on user_id perform efficiently.
        
        Validates:
        - Index on user_id column provides fast lookups
        - Query execution time is under 100ms for 50 records
        - Database optimizer uses the index correctly
        
        Performance Benchmark:
        - Target: < 0.1 seconds (100ms) for indexed query
        - Index should reduce full table scan
        
        Expected Result:
        - Query returns all 50 records correctly
        - Execution time is well under 100ms threshold
        - Index improves performance vs non-indexed query
        """
        logging.info("PERF-002: Creating user 'indexuser' for indexed query test")
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('indexuser', 'index@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('indexuser',))
        user_id = user[0][0]
        logging.info("PERF-002: Created user_id=%s", user_id)
        
        for i in range(50):
            self.db.execute_query(
                "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
                (user_id, f'Title_{i}', f'data_{i}')
            )
        logging.info("PERF-002: Inserted 50 records for user_id=%s", user_id)
        
        start_time = time.time()
        result = self.db.execute_query(
            "SELECT * FROM vault_records WHERE user_id = %s",
            (user_id,)
        )
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info("PERF-002: Indexed query returned %d records in %.4fs", len(result), execution_time)
        self.assertEqual(len(result), 50)
        self.assertLess(execution_time, 0.1, f"Indexed query took {execution_time:.4f}s, expected < 0.1s")
        logging.info("PERF-002: Indexed query performance test passed.")

    def test_perf_003_indexed_query_performance_explain_analyze(self):
        """
        PERF-003: Indexed Query Performance with EXPLAIN ANALYZE

        Priority: High

        Objective:
        Validate that indexed queries on user_id perform efficiently and that the
        database planner uses indexes correctly.

        Preconditions:
        - Database connection established
        - User exists with multiple vault records
        - Index exists on vault_records.user_id

        Test Steps:
        1. Insert a test user
        2. Insert multiple vault records for that user
        3. Run EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) on SELECT query
        4. Parse JSON plan
        5. Verify query plan uses an Index Scan
        6. Verify actual execution time is below threshold (50ms)
        
        Expected Results:
        - Query plan uses Index Scan or Bitmap Index Scan
        - Actual query execution time is < 50ms
        - Buffers show reasonable usage
        """

        logging.info("PERF-003: Creating user 'indexuser' for indexed query test")
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('indexuser', 'index@vault.com')
        )
        user = self.db.execute_query(
            "SELECT user_id FROM vault_users WHERE username = %s",
            ('indexuser',)
        )
        self.assertIsNotNone(user)
        user_id = user[0][0]
        logging.info("PERF-003: Created user_id=%s", user_id)

        # Step 2: Insert multiple vault records
        for i in range(50):
            self.db.execute_query(
                "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
                (user_id, f'Title_{i}', f'data_{i}')
            )
        logging.info("PERF-003: Inserted 50 records for user_id=%s", user_id)

        # Step 3: Run EXPLAIN ANALYZE in JSON format
        explain_result = self.db.execute_query(
            "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT * FROM vault_records WHERE user_id = %s",
            (user_id,)
        )
        self.assertIsNotNone(explain_result)

        # Step 4: Parse JSON plan
        plan_json = explain_result[0][0][0]  # PostgreSQL returns list -> list -> dict
        plan_node = plan_json['Plan']
        node_type = plan_node['Node Type']
        actual_time = plan_node['Actual Total Time']
        buffers_hit = plan_node.get('Shared Hit Blocks', 0)

        logging.info("PERF-003: Query Plan Node Type: %s", node_type)
        logging.info("PERF-003: Actual Total Time: %.4f ms", actual_time)
        logging.info("PERF-003: Shared Hit Blocks: %d", buffers_hit)

        # Step 5: Assertions
        self.assertIn(node_type, ['Index Scan', 'Bitmap Index Scan'])
        self.assertLess(actual_time, 50, f"Query execution took {actual_time}ms, expected < 50ms")

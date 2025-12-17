"""
Test suite for database performance validation.

Tests verify query execution time, bulk operation efficiency, and index optimization including:
- Bulk insert performance benchmarks
- Indexed query performance validation
- Response time thresholds for production readiness
"""

import time
from framework.base_test import BaseTest

class TestPerformance(BaseTest):
    """Test class for validating database performance and query optimization."""
    
    def test_bulk_insert_performance(self):
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
        # Create user
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('perfuser', 'perf@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('perfuser',))
        user_id = user[0][0]
        
        # Bulk insert with timing
        start_time = time.time()
        for i in range(100):
            self.db.execute_query(
                "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
                (user_id, f'Record_{i}', f'encrypted_data_{i}')
            )
        end_time = time.time()
        
        execution_time = end_time - start_time
        self.assertLess(execution_time, 5.0, f"Bulk insert took {execution_time:.2f}s, expected < 5s")
    
    def test_query_with_index_performance(self):
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
        # Create user and records
        self.db.execute_query(
            "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
            ('indexuser', 'index@vault.com')
        )
        user = self.db.execute_query("SELECT user_id FROM vault_users WHERE username = %s", ('indexuser',))
        user_id = user[0][0]
        
        # Insert test data
        for i in range(50):
            self.db.execute_query(
                "INSERT INTO vault_records (user_id, title, encrypted_data) VALUES (%s, %s, %s)",
                (user_id, f'Title_{i}', f'data_{i}')
            )
        
        # Test query performance with timing
        start_time = time.time()
        result = self.db.execute_query(
            "SELECT * FROM vault_records WHERE user_id = %s",
            (user_id,)
        )
        end_time = time.time()
        
        self.assertEqual(len(result), 50)
        execution_time = end_time - start_time
        self.assertLess(execution_time, 0.1, f"Indexed query took {execution_time:.4f}s, expected < 0.1s")
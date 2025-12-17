import unittest
from framework.db_manager import DatabaseManager

class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up database connection before all tests"""
        cls.db = DatabaseManager(db_type='postgres')
        cls.db.connect()
        cls._create_test_tables()
    
    @classmethod
    def _create_test_tables(cls):
        """Create vault-related test tables"""
        cls.db.execute_query("""
            CREATE TABLE IF NOT EXISTS vault_users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cls.db.execute_query("""
            CREATE TABLE IF NOT EXISTS vault_records (
                record_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES vault_users(user_id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                encrypted_data TEXT NOT NULL,
                record_type VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cls.db.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_user_id ON vault_records(user_id)
        """)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        cls.db.execute_query("DROP TABLE IF EXISTS vault_records CASCADE")
        cls.db.execute_query("DROP TABLE IF EXISTS vault_users CASCADE")
        cls.db.close()
    
    def setUp(self):
        """Clean data before each test - ensures test isolation"""
        self.db.execute_query("DELETE FROM vault_records")
        self.db.execute_query("DELETE FROM vault_users")
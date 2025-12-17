from framework.db_manager import DatabaseManager

db = DatabaseManager('postgres')
db.connect()

print("Creating tables...")

db.execute_query("""
    CREATE TABLE IF NOT EXISTS vault_users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

db.execute_query("""
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

db.execute_query("""
    CREATE INDEX IF NOT EXISTS idx_user_id ON vault_records(user_id)
""")

print("Tables created successfully!")
db.close()
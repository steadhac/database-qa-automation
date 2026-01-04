"""
setup_db.py

This script initializes the PostgreSQL database for the Vault application.
It performs the following actions:
- Connects to the database using the DatabaseManager class.
- Enables the pgcrypto extension (required for cryptographic functions).
- Creates the vault_users and vault_records tables if they do not exist.
- Creates an index on the user_id column in the vault_records table.

Usage:
    python setup_db.py

setup_db.py

This script initializes the PostgreSQL database for the Vault application.
It enables the pgcrypto extension, creates tables, and sets up indexes.
"""

"""
setup_db.py

This script initializes the PostgreSQL database for the Vault application.
It handles role and database creation, then sets up tables and extensions.
"""

import os
import psycopg2
from framework.db_manager import DatabaseManager
from dotenv import load_dotenv

load_dotenv()

# Step 1: Create vault_admin role and vault_db database
print("Setting up vault_admin role and vault_db database...")
try:
    # Connect to postgres system database to create role and database
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database='postgres',
        user=os.getenv('POSTGRES_ADMIN_USER')
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Create vault_admin role
    try:
        cursor.execute(f"CREATE ROLE {os.getenv('POSTGRES_USER')} WITH LOGIN PASSWORD '{os.getenv('POSTGRES_PASSWORD')}';")
        print("✓ vault_admin role created.")
    except psycopg2.errors.DuplicateObject:
        print("✓ vault_admin role already exists.")

    # Create vault_db database
    try:
        cursor.execute(f"CREATE DATABASE {os.getenv('POSTGRES_DB')} OWNER {os.getenv('POSTGRES_USER')};")
        print("✓ vault_db database created.")
    except psycopg2.errors.DuplicateDatabase:
        print("✓ vault_db database already exists.")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error creating role/database: {e}")
    exit(1)

# Step 2: Connect to vault_db and create tables
print("\nConnecting to vault_db and creating tables...")
db = DatabaseManager('postgres')

try:
    db.connect()
    print("✓ Connected to vault_db.")

    # Enable pgcrypto extension
    try:
        db.execute_query("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        print("✓ pgcrypto extension enabled.")
    except Exception as e:
        print(f"Error enabling pgcrypto extension: {e}")

    # Create users table
    try:
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS vault_users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ vault_users table created.")
    except Exception as e:
        print(f"Error creating vault_users table: {e}")

    # Create records table
    try:
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
        print("✓ vault_records table created.")
    except Exception as e:
        print(f"Error creating vault_records table: {e}")

    # Create index
    try:
        db.execute_query("""
            CREATE INDEX IF NOT EXISTS idx_user_id ON vault_records(user_id)
        """)
        print("✓ Index idx_user_id created.")
    except Exception as e:
        print(f"Error creating index: {e}")

    print("\n✓ Setup completed successfully!")

except Exception as e:
    print(f"Database setup failed: {e}")

finally:
    db.close()
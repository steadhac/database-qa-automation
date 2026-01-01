from framework.db_manager import DatabaseManager

db = DatabaseManager('postgres')
db.connect()

print("Adding sample data...")

# Add users
db.execute_query(
    "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
    ('john_doe', 'john@vault.com')
)
db.execute_query(
    "INSERT INTO vault_users (username, email) VALUES (%s, %s)",
    ('jane_smith', 'jane@vault.com')
)

# Get user IDs
users = db.execute_query("SELECT user_id, username FROM vault_users")

# Add vault records
for user_id, username in users:
    db.execute_query(
        "INSERT INTO vault_records (user_id, title, encrypted_data, record_type) VALUES (%s, %s, %s, %s)",
        (user_id, f'{username}_password', 'encrypted_data_123', 'password')
    )

print("Sample data added!")
db.close()
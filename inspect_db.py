from framework.db_manager import DatabaseManager

db = DatabaseManager('postgres')
db.connect()

print("\n=== VAULT USERS ===")
users = db.execute_query("SELECT * FROM vault_users")
for user in users:
    print(user)

print("\n=== VAULT RECORDS ===")
records = db.execute_query("SELECT * FROM vault_records")
for record in records:
    print(record)

print("\n=== COUNTS ===")
user_count = db.execute_query("SELECT COUNT(*) FROM vault_users")
record_count = db.execute_query("SELECT COUNT(*) FROM vault_records")
print(f"Users: {user_count[0][0]}")
print(f"Records: {record_count[0][0]}")

db.close()
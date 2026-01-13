# Test Cases - Database QA Automation Suite

## Document Information
- **Project**: Database QA Automation for Secure Vault Systems
- **Version**: 2.0
- **Author**: Caro Steadham
- **Date**: January 3, 2026
- **Total Test Cases**: 20

---

## Test Category 1: SQL Operations

### Test Suite: tests/sql/test_crud.py

#### SQL-001: Create and Read User Record
**Priority**: High  
**Objective**: Validate user creation and retrieval from database

**Preconditions**:
- Database connection established
- vault_users table exists

**Test Steps**:
1. Insert new user with username 'testuser' and email 'test@vault.com'
2. Execute SELECT query to retrieve user by username
3. Verify record exists and data matches

**Expected Results**:
- User record is created successfully
- SELECT query returns 1 record
- Username equals 'testuser'
- Email equals 'test@vault.com'

**Test Data**: username='testuser', email='test@vault.com'

**Status**: ✅ Pass

---

#### SQL-002: Update Vault Record Data
**Priority**: High  
**Objective**: Validate UPDATE operations modify encrypted vault data correctly

**Preconditions**: User exists in vault_users, Vault record exists for user

**Test Steps**:
1. Create user 'user1' with email 'user1@vault.com'
2. Insert vault record with title 'Password' and encrypted_data 'encrypted_v1'
3. Execute UPDATE to change encrypted_data to 'encrypted_v2'
4. Verify updated_at timestamp is refreshed
5. Query record and verify encrypted_data changed

**Expected Results**: UPDATE executes successfully, encrypted_data changes from 'encrypted_v1' to 'encrypted_v2', updated_at timestamp is modified, Only 1 record exists

**Status**: ✅ Pass

---

#### SQL-003: Delete with Cascade Validation
**Priority**: High  
**Objective**: Verify foreign key ON DELETE CASCADE removes orphaned vault records

**Preconditions**: vault_users and vault_records tables exist, Foreign key relationship defined with ON DELETE CASCADE

**Test Steps**:
1. Create user 'deleteuser'
2. Create vault record associated with user
3. Delete user from vault_users
4. Query vault_records for deleted user_id

**Expected Results**: User deletion succeeds, Associated vault_records are automatically deleted, Query returns 0 records for deleted user_id, No orphaned records remain

**Status**: ✅ Pass

---

### Test Suite: tests/sql/test_vault.py

#### SQL-004: AES-256-GCM Encrypted Data Storage
**Priority**: Critical  
**Objective**: Validate production-grade encryption using AES-256-GCM

**Preconditions**: cryptography library installed, AES-256-GCM cipher initialized with 256-bit key

**Test Steps**:
1. Create vault user
2. Encrypt plaintext password "MySecretPassword123!" using AES-256-GCM
3. Verify encrypted output differs from plaintext
4. Store encrypted data + nonce in vault_records
5. Retrieve encrypted data from database
6. Decrypt using original key and nonce
7. Verify decrypted data matches original plaintext

**Expected Results**: Encryption produces ciphertext different from plaintext, Ciphertext contains authentication tag (GCM), Data stored successfully in database, Decryption recovers exact original password, Without key data is unreadable

**Test Data**: plaintext="MySecretPassword123!", encryption=AES-256-GCM, key_size=256 bits, nonce_size=96 bits

**Status**: ✅ Pass

---

#### SQL-005: Vault Record Metadata Tracking
**Priority**: Medium  
**Objective**: Verify metadata fields (created_at, updated_at, record_type) are tracked

**Preconditions**: vault_records table has metadata columns

**Test Steps**:
1. Create user 'metauser'
2. Encrypt data using AES-256-GCM
3. Insert vault record with record_type='login'
4. Query metadata fields

**Expected Results**: record_type equals 'login', created_at is not null and valid timestamp, updated_at is not null and valid timestamp, Timestamps are automatically generated

**Status**: ✅ Pass

---

#### SQL-006: Encryption Key Isolation
**Priority**: High  
**Objective**: Validate different keys produce different ciphertexts and prevent cross-decryption

**Preconditions**: AES-256-GCM encryption available, Ability to generate multiple keys

**Test Steps**:
1. Generate first 256-bit encryption key
2. Encrypt plaintext "SensitiveData" with first key
3. Generate second 256-bit encryption key
4. Encrypt same plaintext with second key
5. Compare ciphertexts
6. Attempt to decrypt data encrypted with key2 using key1

**Expected Results**: Two ciphertexts are different, Decryption with wrong key raises exception, Demonstrates proper key isolation

**Status**: ✅ Pass

---

#### SQL-007: Tampering Detection with GCM Authentication Tag
**Priority**: High  
**Objective**: Verify GCM mode detects data tampering through authentication

**Preconditions**: AES-256-GCM encryption configured, Encrypted data with authentication tag

**Test Steps**:
1. Encrypt plaintext "ImportantData"
2. Retrieve ciphertext bytes
3. Tamper with ciphertext (flip bits in first byte)
4. Attempt to decrypt tampered data

**Expected Results**: Decryption of tampered data raises InvalidTag exception, Tampering is automatically detected, Demonstrates authenticated encryption

**Status**: ✅ Pass

#### SQL-008: Encrypted Data Integrity Checksum Verification
**Priority**: High  
**Objective**: Validate encrypted data integrity using SHA-256 checksums to detect corruption

**Preconditions**: pgcrypto extension enabled in PostgreSQL, digest() and encode() functions available

**Test Steps**:
1. Create user 'checksum_user' for integrity testing
2. Generate simulated encrypted data for checksum test
3. Insert vault record with encrypted data for user
4. Compute SHA-256 checksum of encrypted_data immediately after insert
5. Re-read encrypted_data from database
6. Compute SHA-256 checksum of re-read data
7. Compare checksums from insert and re-read operations

**Expected Results**: Initial checksum computed successfully after insert, Re-read checksum matches initial checksum exactly, Checksums are identical (no data corruption), Demonstrates data integrity through cryptographic hashing

**Test Data**: 
- Username: 'checksum_user'
- Encrypted data: simulated encrypted payload
- Hash algorithm: SHA-256
- Expected checksum format: 64-character hexadecimal string

**SQL Query Used**:
```sql
SELECT encode(digest(encrypted_data::bytea, 'sha256'), 'hex')
FROM vault_records
WHERE user_id = %s
```
---

## Test Category 2: Data Integrity

### Test Suite: tests/integrity/test_data_integrity.py

#### INT-001: Unique Constraint Enforcement
**Priority**: High  
**Objective**: Verify UNIQUE constraints on username and email prevent duplicates

**Preconditions**: vault_users table has UNIQUE constraints on username and email

**Test Steps**:
1. Insert user with username 'john' and email 'john@vault.com'
2. Attempt to insert second user with same username 'john' but different email
3. Catch exception

**Expected Results**: First insertion succeeds, Second insertion fails with constraint violation exception, Database rejects duplicate username

**Status**: ✅ Pass

---

#### INT-002: Foreign Key Constraint Validation
**Priority**: High  
**Objective**: Prevent orphaned vault records through foreign key enforcement

**Preconditions**: Foreign key exists vault_records.user_id to vault_users.user_id

**Test Steps**:
1. Attempt to insert vault_record with user_id=99999 (non-existent)
2. Catch foreign key violation exception

**Expected Results**: INSERT fails with foreign key constraint violation, No orphaned record is created, Database maintains referential integrity

**Status**: ✅ Pass

---

#### INT-003: Concurrent Update Consistency
**Priority**: Medium  
**Objective**: Validate data consistency after multiple sequential updates

**Preconditions**: User and vault record exist

**Test Steps**:
1. Create user 'consistent'
2. Create vault record with encrypted_data='v1'
3. Perform 5 sequential UPDATE operations (v2, v3, v4, v5, v6)
4. Query final state
5. Verify record count

**Expected Results**: Final encrypted_data equals 'v6', Only 1 record exists (no duplicates from updates), All updates applied correctly

**Status**: ✅ Pass

---

## Test Category 3: Performance

### Test Suite: tests/performance/test_performance.py

#### PERF-001: Bulk Insert Performance
**Priority**: High  
**Objective**: Validate 100 INSERT operations complete within 5 seconds

**Preconditions**: Database connection established, User exists for foreign key

**Test Steps**:
1. Create user 'perfuser'
2. Start timer
3. Insert 100 vault records in loop
4. Stop timer
5. Calculate execution time

**Expected Results**: All 100 records inserted successfully, Total execution time < 5 seconds, Typical performance 1-3 seconds

**Benchmark**: < 5 seconds  
**Status**: ✅ Pass

---

#### PERF-002: Indexed Query Performance
**Priority**: High  
**Objective**: Verify indexed queries execute in < 100ms

**Preconditions**: Index exists on vault_records.user_id, 50 test records exist

**Test Steps**:
1. Create user 'indexuser'
2. Insert 50 vault records
3. Start timer
4. Execute SELECT * FROM vault_records WHERE user_id = ?
5. Stop timer
6. Verify record count and execution time

**Expected Results**: Query returns all 50 records, Execution time < 100ms, Index is utilized

**Benchmark**: < 100ms  
**Status**: ✅ Pass

---

#### PERF-003: Indexed Query Performance with EXPLAIN ANALYZE
**Priority**: High
**Objective**: Validate that indexed queries on vault_records.user_id perform efficiently and that the PostgreSQL query planner uses indexes correctly.

**Preconditions**: Database connection established, vault_records.user_id column is indexed, User and vault_records tables exist, PostgreSQL query planner enabled (default)

**Test Steps**:
1. Create user indexuser
2. Insert 50 vault records associated with the user
3. Execute EXPLAIN ANALYZE on an indexed query:
```sql SELECT * FROM vault_records WHERE user_id = ? ```
4. Capture and parse the JSON query execution plan
5. Verify the plan uses an Index Scan or Bitmap Index Scan
6. Verify no Sequential Scan (Seq Scan) is present
7. Confirm actual total execution time is below threshold (e.g., <50ms)
8. Analyze buffer usage and cost metrics

**Expected Results**:

Query execution plan includes Index Scan or Bitmap Index Scan
No Seq Scan appears in the plan
PostgreSQL optimizer selects the optimal execution path
Query execution time is low and proportional to result set
Buffers usage is reasonable

**Benchmark**:
Index Scan: Required
Sequential Scan: Not Allowed
Execution cost: Low and proportional to result size
Execution time: <50ms

**Status**:
✅ Pass

---

## Test Category 4: Schema & Migrations

### Test Suite: tests/migrations/test_schema.py

#### SCH-001: Table Structure Validation
**Priority**: High  
**Objective**: Verify required tables exist with correct column definitions

**Preconditions**: Database initialized

**Test Steps**:
1. Query information_schema.columns for vault_users table
2. Verify columns exist user_id, username, email, created_at
3. Verify data types are correct

**Expected Results**: vault_users table exists, All required columns present, Columns have correct data types

**Status**: ✅ Pass

---

#### SCH-002: Index Existence Verification
**Priority**: High  
**Objective**: Validate performance indexes are created

**Preconditions**: vault_records table exists

**Test Steps**:
1. Query pg_indexes for vault_records table
2. Search for index containing 'user_id'

**Expected Results**: At least one index exists on user_id column, Index name contains 'user_id' or 'idx_user_id'

**Status**: ✅ Pass

---

#### SCH-003: Schema Migration Add Column
**Priority**: Medium  
**Objective**: Test adding new column to existing table

**Preconditions**: vault_records table exists

**Test Steps**:
1. Execute ALTER TABLE vault_records ADD COLUMN metadata JSONB
2. Query information_schema.columns to verify column exists
3. Cleanup DROP COLUMN metadata

**Expected Results**: ALTER TABLE succeeds, New column appears in information_schema, Cleanup executes successfully

**Status**: ✅ Pass

---

## Test Category 5: API Backend

### Test Suite: tests/api/test_backend_api.py

#### API-001: User Creation via API Workflow
**Priority**: High  
**Objective**: Simulate API endpoint creating user from JSON payload

**Preconditions**: Database connection available

**Test Steps**:
1. Create JSON payload username api_user email api@vault.com
2. Simulate backend parsing payload
3. Insert into database
4. Query to verify creation

**Expected Results**: User created with correct username and email, Database state reflects API operation, Data matches input payload

**Status**: ✅ Pass

---

#### API-002: Vault Record Retrieval
**Priority**: High  
**Objective**: Simulate API GET endpoint retrieving vault records

**Preconditions**: User with vault records exists

**Test Steps**:
1. Create user 'api_test'
2. Insert 3 vault records
3. Simulate API GET SELECT records WHERE user_id = ?
4. Verify response data

**Expected Results**: Query returns 3 records, All records have correct record_type='password', Data format suitable for JSON serialization

**Status**: ✅ Pass

---

#### API-003: API Error Handling for Invalid Data
**Priority**: Medium  
**Objective**: Validate API properly handles invalid foreign keys

**Preconditions**: Database enforces foreign keys

**Test Steps**:
1. Attempt to insert vault_record with user_id=99999 invalid
2. Catch exception

**Expected Results**: Exception raised for foreign key violation, Database integrity maintained, Error response would be generated by API layer

**Status**: ✅ Pass

---

## Test Category 6: CLI Commands

### Test Suite: tests/commander_cli/test_cli_commands.py

#### CLI-001: Export Users Command
**Priority**: Medium  
**Objective**: Simulate CLI tool exporting user data

**Preconditions**: Users exist in database

**Test Steps**:
1. Create 2 users cli_user1 cli_user2
2. Simulate CLI SELECT username email FROM vault_users ORDER BY username
3. Verify result count and data

**Expected Results**: 2 users returned, Data ordered correctly, Format suitable for CSV export

**Status**: ✅ Pass

---

#### CLI-002: Bulk Delete Operation
**Priority**: Medium  
**Objective**: Test CLI command for bulk deletion of records

**Preconditions**: User with multiple vault records exists

**Test Steps**:
1. Create user 'bulk_delete'
2. Insert 5 vault records
3. Simulate CLI DELETE FROM vault_records WHERE user_id = ?
4. Verify deletion

**Expected Results**: All 5 records deleted, Query returns 0 remaining records, User still exists

**Status**: ✅ Pass

---

#### CLI-003: Database Stats Query
**Priority**: Low  
**Objective**: Test CLI tool retrieving database statistics

**Preconditions**: Test data exists

**Test Steps**:
1. Create 3 users
2. Simulate CLI SELECT COUNT(*) FROM vault_users
3. Verify count

**Expected Results**: Count >= 3, Query executes successfully, Accurate statistics returned

**Status**: ✅ Pass

---

#### CLI-004: Custom Query Execution
**Priority**: Medium  
**Objective**: Validate CLI can execute custom SQL queries

**Preconditions**: User exists

**Test Steps**:
1. Create user 'query_test' with email 'query@vault.com'
2. Simulate CLI SELECT username FROM vault_users WHERE email LIKE '%vault.com'
3. Verify results

**Expected Results**: Query executes successfully, Returns records matching WHERE clause, query_test included in results

**Status**: ✅ Pass

---

## Test Execution Summary

### By Priority
- Critical: 1 test
- High: 14 tests
- Medium: 7 tests
- Low: 1 test

### By Category
- SQL Operations: 8 tests
- Data Integrity: 3 tests
- Performance: 3 tests
- Schema Migrations: 3 tests
- API Backend: 3 tests
- CLI Commands: 4 tests

### Overall Status
- Total Tests: 24
- Passed: 24
- Failed: 0
- Pass Rate: 100%

---

## Test Environment

Database: PostgreSQL 15 (Docker)  
Python Version: 3.9+  
Test Framework: pytest  
Encryption: AES-256-GCM  
Execution Time: < 5 minutes

---

## Notes

All tests use isolated transactions with automatic cleanup. Encryption tests use test-only keys. Performance benchmarks may vary based on hardware. Tests are CI/CD ready and containerized.

---

Document Version: 2.0  
Last Updated: January 3, 2026  
Author: Caro Steadham
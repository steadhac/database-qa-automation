# Debugging and Testing Guide

## Table of Contents
1. [Setup & Verification](#setup--verification)
2. [Common Errors](#common-errors)
3. [Testing Workflow](#testing-workflow)
4. [Debugging Techniques](#debugging-techniques)
5. [Database Inspection](#database-inspection)

---

## Setup & Verification

### Step 1: Verify Database Connection

**Check if PostgreSQL is running:**
```bash
docker-compose ps
```
Expected output:
```
CONTAINER ID   STATUS       PORTS
...            Up           5432/tcp
```
Start if not running:
```bash
docker-compose up -d
sleep 10  # Wait for PostgreSQL to initialize
```
Step 2: Initialize Database Schema
Create tables and extensions:
```bash
python setup_db.py
```
Expected output:

```
✅ Database connected
✅ pgcrypto extension enabled
✅ vault_users table created
✅ vault_records table created
✅ Index idx_user_id created
✅ Setup completed successfully!
```
Step 3: Verify Schema Creation
Check tables exist:
```bash
python inspect_db.py
```
Should display table structure and row counts.

---

## Common Errors
# Error 1: "role vault_admin does not exist"
Problem: PostgreSQL user not created

Solution:
```python
# Reset Docker
docker-compose down -v
docker-compose up -d
sleep 10

# Run setup
python setup_db.py
```
# Error 2: "relation vault_users does not exist"
Problem: Tables haven't been created yet

Solution:

``` python
python setup_db.py
```
Verify:
``` python
python inspect_db.py
```
# Error 3: "function digest(bytea, unknown) does not exist"
Problem: pgcrypto extension not enabled

Solution:
``` python
# setup_db.py should handle this, but manually:
psql -h localhost -U vault_admin -d vault_db -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
```
# Error 4: "connection to server failed"
Problem: Docker container not running or PostgreSQL not initialized

Solution:
``` bash
# Check status
docker-compose ps

# Restart
docker-compose down -v
docker-compose up -d
sleep 15  # Wait longer for initialization
python setup_db.py
```
# Error 5: "Python 3.13 not supported"
Problem: psycopg2-binary doesn't support Python 3.13 yet

Solution:
``` python
# Use Python 3.9-3.12
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### Testing Workflow
Full Test Suite
Run all tests:
``` python
pytest tests/ -v
```
With output:

```python
pytest tests/ -v -s
```
## Category-Specific Tests
SQL Operations (8 tests):
``` python
pytest tests/sql/ -v
```

Data Integrity (3 tests):
``` python
pytest tests/integrity/ -v
```
Performance (3 tests):
``` python
pytest tests/performance/ -v
```
Schema Validation (3 tests):
``` python
pytest tests/migrations/ -v
```
API Backend (3 tests):
``` python
pytest tests/api/ -v
```
CLI Commands (4 tests):
``` python
pytest tests/commander_cli/ -v
```
Single Test
``` python
pytest tests/sql/test_vault.py::TestVaultOperations::test_sql_008_encrypted_data_integrity_checksum -v
```

### Debugging Techniques
## 1. Check Current Database State
Before running tests:
``` sql
# Connect directly to database
psql -h localhost -U vault_admin -d vault_db

# In psql prompt:
SELECT * FROM vault_users;
SELECT COUNT(*) FROM vault_records;
SELECT * FROM vault_records WHERE user_id = 1;
```
## 2. Enable Verbose Logging
In your test file:
``` pyhton
import logging
logging.basicConfig(level=logging.DEBUG)
```
Run tests with logging:
``` python 
pytest tests/ -v --log-cli-level=DEBUG
```
## 3. Check Encryption Tests
SQL-004 to SQL-008 require proper encryption setup

Verify these work:
``` python
pytest tests/sql/test_vault.py::TestVaultOperations::test_sql_004_aes_256_gcm_encrypted_data_storage -v -s
```
If fails, check:

✅ cryptography library installed: pip list | grep cryptography
✅ pgcrypto extension enabled: psql ... -c "SELECT * FROM pg_extension;"

## 4. Check Performance Tests

PERF-002: Simple timing
```bash
pytest tests/performance/test_performance.py::TestPerformance::test_perf_002_indexed_query_performance -v -s
```
PERF-003: EXPLAIN ANALYZE
```bash
pytest tests/performance/test_performance.py::TestPerformance::test_perf_003_indexed_query_performance_explain_analyze -v -s
```
If PERF-003 fails:
# Test EXPLAIN ANALYZE manually
```bash
psql -h localhost -U vault_admin -d vault_db -c \
  "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT * FROM vault_records WHERE user_id = 1;"
```
5. Database Reset Between Tests
Clean up and restart:
```bash
docker-compose down -v
docker-compose up -d
sleep 15
python setup_db.py
pytest tests/ -v
```
Database Inspection
View All Tables
```bash
python inspect_db.py
```
Direct PostgreSQL Access
Connect to database:
```bash
psql -h localhost -U vault_admin -d vault_db
```
In psql:

-- List all tables
```bash
\dt

# -- View table structure
\d vault_users
\d vault_records

# -- Check indexes
\di

# -- Check extensions
SELECT * FROM pg_extension;

# -- Check constraints
\d vault_users
```
Common Queries
Count users:
```sql
SELECT COUNT(*) FROM vault_users;
```
Count records per user:
```sql
SELECT user_id, COUNT(*) FROM vault_records GROUP BY user_id;
```
Check encryption data:
```sql
SELECT user_id, title, LENGTH(encrypted_data) FROM vault_records LIMIT 5;
```
Verify index usage:
```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM vault_records WHERE user_id = 1;
```
Check pgcrypto available:
```sql
SELECT * FROM pg_proc WHERE proname = 'digest';
```
Quick Start Checklist
First time setup:

 Docker running: 
 ``` bash
 docker-compose up -d
 # Wait 10+ seconds for PostgreSQL
 
 # Create database: 
 python setup_db.py
 
 #Verify setup: 
 python inspect_db.py
 
 #Run tests: 
 pytest tests/ -v
 ```

Before running tests:

 Docker running: 
 ```bash 
 docker-compose ps

 #Tables exist: 
 python inspect_db.py
 
 #.env file present: 
 cat .env
```
After test failure:

 Check error message
 View database state:
 ```bash
python inspect_db.py
 # Reset if needed: 
 docker-compose down -v && docker-compose up -d
 
 # Re-initialize: 
 python setup_db.py
 ```
Troubleshooting Flowchart
``` text
Error occurs
    ↓
Read error message carefully
    ↓
Check if it's in "Common Errors" section
    ↓
No → Run python inspect_db.py
    ↓
No tables? → python setup_db.py
    ↓
Still failing? → docker-compose down -v && docker-compose up -d
    ↓
Still failing? → Check .env file exists with correct values
    ↓
Check requirements.txt installed: pip install -r requirements.txt
    ↓
Last resort: Check logs with pytest -v -s

```
Useful Commands Reference
``` bash
# Setup
docker-compose up -d                    # Start containers
python setup_db.py                      # Initialize database
python inspect_db.py                    # View database state

# Testing
pytest tests/ -v                        # Run all tests
pytest tests/sql/ -v                    # Run SQL tests
pytest tests/ -v -s                     # Show output
pytest tests/ --tb=short                # Short error format

# Database
psql -h localhost -U vault_admin -d vault_db   # Connect directly
python add_sample_data.py               # Add test data

# Cleanup
docker-compose down -v                  # Stop and remove volumes
docker-compose logs postgres            # View PostgreSQL logs
```
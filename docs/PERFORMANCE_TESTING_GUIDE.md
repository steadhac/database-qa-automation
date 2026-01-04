# Performance Testing Guide - EXPLAIN ANALYZE

## Overview

This guide explains how performance testing works in the database QA automation suite, focusing on PostgreSQL's `EXPLAIN ANALYZE` feature.

## What is EXPLAIN ANALYZE?

`EXPLAIN ANALYZE` shows how PostgreSQL executes a query:
- **Planning**: How PostgreSQL decides to run the query
- **Execution**: What actually happened when running the query
- **Performance**: Timing, rows processed, index usage

## Basic Query Plan Concepts

### Scan Types

**Index Scan** (Good 👍)
- Uses an index to find rows
- Faster for queries with WHERE clauses
- Example: `WHERE user_id = 1`

**Seq Scan** (Slower 👎)
- Reads entire table row by row
- Used when no index available or full scan faster
- Avoid for large tables

### Key Metrics

| Metric | Meaning |
|--------|---------|
| Rows | How many rows processed |
| Actual Rows | Rows actually returned |
| Execution Time | Time to run (ms) |
| Planning Time | Time to plan query (ms) |
| Buffer Hits | Data from memory cache |
| Buffer Reads | Data from disk |

## JSON Output Example

Your tests use `FORMAT JSON` to parse results programmatically:

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
SELECT * FROM vault_records WHERE user_id = 1
```

Output Structure:

```sql
[
  {
    "Plan": {
      "Node Type": "Index Scan",
      "Index Name": "idx_user_id",
      "Actual Rows": 50,
      "Rows Removed by Filter": 0,
      "Execution Time": 15.432,
      "Planning Time": 0.125,
      "Shared Hit Blocks": 50,
      "Shared Read Blocks": 2
    }
  }
]
```
## What to Look For:

Node Type: Should be "Index Scan" (not "Seq Scan")
Execution Time: Should be < 100ms for PERF-002, < 50ms for PERF-003
Shared Hit Blocks: High = good (data in memory)
Shared Read Blocks: Low = good (minimal disk reads)
Rows Removed by Filter: Should be 0 (index is selective)

## How Tests Use It

### PERF-002: Indexed Query Performance

```python
# Tests that indexed queries run fast (simple timing)
start_time = time.time()
result = self.db.execute_query(
    "SELECT * FROM vault_records WHERE user_id = ?", (user_id,)
)
execution_time = time.time() - start_time
```
Validates:

✅ Query executes in < 100ms
✅ Returns correct number of records (50)
✅ Index improves performance

PERF-003: Query Plan Analysis with EXPLAIN ANALYZE

# Deep dive: Analyze the query plan using EXPLAIN
```sql
explain_result = self.db.execute_query(
    "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
     SELECT * FROM vault_records WHERE user_id = ?", (user_id,)
)
plan_json = explain_result[0][0][0]  # Parse JSON
```

Validates:

✅ Index Scan is used (not Seq Scan)
✅ Actual execution time < 50ms
✅ Buffer hits are high (data in memory)
✅ Node Type is efficient

## Execution Time Breakdown

PERF-002 and PERF-003 measure different things, resulting in different timing values.

### What is Overhead?

**Overhead** = Extra time/resources used that aren't directly executing the query.

When you measure PERF-002 query time:

Total Time = Database Execution + Overhead
45ms = 8ms (actual query) + 37ms (overhead)

```table

**Overhead components:**

| Component | Time | What It Is |
|-----------|------|-----------|
| Network latency | 2-5ms | Data traveling to/from database server |
| Driver overhead (psycopg2) | 1-3ms | Library processing, format conversion |
| Python processing | 1-2ms | Variable creation, function calls |
| Data serialization | 1-2ms | Converting rows into Python objects (deserializing)|
| **Total overhead** | **~10-15ms** | Non-database time |

**Why overhead matters:**
- Real users experience the TOTAL time (45ms), including overhead
- Database only takes 8ms, but network/driver add 37ms
- When scaling: overhead stays ~15ms but database time grows with data volume
```
---

### PERF-002: End-to-End Timing (What Users Experience)

```python
start_time = time.time()           # ⏱️ START
result = self.db.execute_query(...)  # Python query execution
end_time = time.time()             # ⏱️ STOP
```
## what is included:
```table
Total Time (45-100ms)
├── Network latency (connection to DB)      2-5ms
├── Driver overhead (psycopg2)              1-3ms
├── Query planning (PostgreSQL)             0.1-1ms
├── Index Scan execution (PostgreSQL)       5-20ms
├── Result serialization                    1-2ms
└── Python processing                       1-2ms
```
Example: Query took 0.0452s = 45.2ms total

### PERF-003: PostgreSQL Internal Timing with EXPLAIN ANALYZE(Pure Database Performance)

# Deep dive: Analyze the query plan using EXPLAIN
```sql
explain_result = self.db.execute_query(
    "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
     SELECT * FROM vault_records WHERE user_id = ?", (user_id,)
)
plan_json = explain_result[0][0][0]  # Parse JSON
```
Validates:
✅ Index Scan is used (not Seq Scan)

### Why JSON Format?
## PostgreSQL serializes the query plan to JSON:

```
[{
  "Plan": {
    "Node Type": "Index Scan",
    "Actual Total Time": 8.432,
    "Shared Hit Blocks": 50
  }
}]
```
## Python test deserializes JSON to dictionary:
```python
plan_json = explain_result[0][0][0]  # Deserialize
node_type = plan_json['Plan']['Node Type']
execution_time = plan_json['Plan']['Actual Total Time']
```
### Benefits:

Structured format for automated validation
Easy to extract specific fields
Reliable across PostgreSQL versions
Enables repeatable testing

Validates:
✅ Index Scan is used (not Seq Scan)

## what is included:
```sql
Actual Total Time (8-20ms)
├── Query planning                 0.1-0.5ms
├── Index Scan execution           5-15ms
├── Retrieving/buffering results   1-3ms
└── NO network, NO driver, NO Python overhead
```
Example: Query took 8.432ms = pure database time

## Why Timing Differs

| Component | PERF-002 (End-to-End) | PERF-003 (Database Only) |
|-----------|----------------------|-------------------------|
| Network latency | ✅ Included | ❌ Excluded |
| Driver overhead (psycopg2) | ✅ Included | ❌ Excluded |
| Python processing | ✅ Included | ❌ Excluded |
| PostgreSQL execution | ✅ Included | ✅ Included |
| **Typical Time** | **45-100ms** | **8-20ms** |

## Which One Matters?

Both tests serve different purposes:

### PERF-002: SLA Validation (User-Facing)
**What**: Measures what real users experience (45ms total)
**Why**: Companies promise SLAs to users

Example SLA: "Search queries complete in < 100ms"
PERF-002 validates this promise is kept

```table
**Validates**: Real-world performance including all overhead

### PERF-003: Query Optimization (Technical)
**What**: Measures pure database performance (8ms)
**Why**: Ensures queries are well-optimized
```
Example question: "Is the index being used?"
PERF-003 shows: "Yes, Index Scan confirmed"
```table
**Validates**: Database efficiency and proper indexing

### Summary

| Test | For Whom | Measures | Validates |
|------|----------|----------|-----------|
| PERF-002 | Customers/SLA | User experience (45ms) | "Are users happy?" |
| PERF-003 | Engineers/DBAs | Database only (8ms) | "Is query optimized?" |

**Both are essential:** PERF-002 ensures speed, PERF-003 ensures quality.
```
## Example Analysis
The test with 50 records:
PERF-002: Query returned 50 records in 0.0452s (45.2ms)
PERF-003: Actual Total Time: 8.432 ms

## Breakdown for that specific run:

PostgreSQL: 8.4ms
Network round-trip: 2-3ms
Driver serialization: 1-2ms
Python overhead: 1-2ms
Total: ~45ms ✓

If you scaled to 1,000 records:

PostgreSQL: 8-10ms (index still efficient)
Overhead: 5-10ms (more data to transfer)
Total: 13-20ms still under 100ms ✓




## Common Issues

## Issue: Seq Scan Instead of Index Scan
Problem: Query uses table scan instead of index
Solution:

Verify index exists: \d vault_records
Check index is on user_id column
Rebuild index if needed

## Issue: High Buffer Reads
Problem: Data coming from disk, not memory
Solution:

Increase shared_buffers in PostgreSQL config
Ensure enough memory for caching
Normal for first run (cold cache)
Subsequent runs should hit memory
Tests run query multiple times to warm cache

## Issue: Execution Time Too Slow
Problem: Query exceeds benchmark threshold
Solution:

Verify index is used (not Seq Scan)
Check query WHERE clause is indexed column
Ensure enough test data exists for valid timing

### Quick Reference
```sql
# View indexes on a table
\d vault_records

# Manual EXPLAIN ANALYZE (for debugging)
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM vault_records WHERE user_id = 1;

# JSON format (what tests use)
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
SELECT * FROM vault_records WHERE user_id = 1;
```
### Related Tests

PERF-001: Bulk insert performance (not EXPLAIN)
PERF-002: Indexed query performance < 100ms
PERF-003: Query plan analysis < 50ms with JSON

### Resources

- [PostgreSQL EXPLAIN Documentation](https://www.postgresql.org/docs/current/sql-explain.html)
- [Query Planning Guide](https://www.postgresql.org/docs/current/planner.html)
- [Test Cases](TEST_CASES.md) - PERF-002 and PERF-003 specifications
- [Test Plan](TEST_PLAN.md) - Performance testing strategy
- [Performance Tests](../tests/performance/test_performance.py) - Actual test code

---

**Last Updated:** January 3, 2026
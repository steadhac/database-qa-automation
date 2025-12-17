# Database QA Automation Suite

## Overview
Comprehensive database testing framework for validating PostgreSQL and MySQL operations, data integrity, schema management, and performance benchmarks. Built to demonstrate database QA engineering capabilities for enterprise vault systems with production-grade AES-256-GCM encryption.

## Tech Stack
- **Languages**: Python 3.9+
- **Databases**: PostgreSQL 15, MySQL 8.0, Redis 7
- **Testing**: pytest, unittest
- **Encryption**: AES-256-GCM (industry standard for password managers)
- **Database Drivers**: psycopg2, PyMySQL
- **Containerization**: Docker, Docker Compose
- **Utilities**: python-dotenv, Faker, cryptography

## Project Structure
```
database-qa-automation/
├── framework/ # Test framework core
│ ├── init.py
│ ├── db_manager.py # Database connection management
│ └── base_test.py # Base test class with setup/teardown
├── tests/ # Test suites organized by category
│ ├── init.py
│ ├── sql/ # SQL operations
│ │ ├── init.py
│ │ ├── test_crud.py
│ │ └── test_vault.py
│ ├── integrity/ # Data integrity validation
│ │ ├── init.py
│ │ └── test_data_integrity.py
│ ├── performance/ # Performance benchmarks
│ │ ├── init.py
│ │ └── test_performance.py
│ ├── migrations/ # Schema validation
│ │ ├── init.py
│ │ └── test_schema.py
│ ├── api/ # Backend API testing
│ │ ├── init.py
│ │ └── test_backend_api.py
│ └── commander_cli/ # CLI command testing
│ ├── init.py
│ └── test_cli_commands.py
├── schemas/ # Database schema definitions
├── docs/ # Documentation
│ ├── README.md
│ ├── TEST_PLAN.md
│ └── blog_post.md
├── docker-compose.yml # Container orchestration
├── .env # Environment configuration
├── requirements.txt # Python dependencies
├── setup_db.py # Database schema setup
├── inspect_db.py # Database inspection tool
└── add_sample_data.py # Sample data generator

```

## Quick Start

### 1. Prerequisites
- Docker Desktop installed and running
- Python 3.9+
- Virtual environment recommended

### 2. Setup
```bash
# Clone and navigate to project
cd database-qa-automation

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r [requirements.txt](http://_vscodecontentref_/7)

# Start databases (PostgreSQL, MySQL, Redis)
docker-compose up -d

# Wait for containers to be healthy (10-15 seconds)
docker ps

# Create database schema
python [setup_db.py](http://_vscodecontentref_/8)
```

database-qa-automation/
├── framework/ # Test framework core
│ ├── init.py
│ ├── db_manager.py # Database connection management
│ └── base_test.py # Base test class with setup/teardown
├── tests/ # Test suites organized by category
│ ├── init.py
│ ├── sql/ # SQL operations
│ │ ├── init.py
│ │ ├── test_crud.py
│ │ └── test_vault.py
│ ├── integrity/ # Data integrity validation
│ │ ├── init.py
│ │ └── test_data_integrity.py
│ ├── performance/ # Performance benchmarks
│ │ ├── init.py
│ │ └── test_performance.py
│ ├── migrations/ # Schema validation
│ │ ├── init.py
│ │ └── test_schema.py
│ ├── api/ # Backend API testing
│ │ ├── init.py
│ │ └── test_backend_api.py
│ └── commander_cli/ # CLI command testing
│ ├── init.py
│ └── test_cli_commands.py
├── schemas/ # Database schema definitions
├── docs/ # Documentation
│ ├── README.md
│ ├── TEST_PLAN.md
│ └── blog_post.md
├── docker-compose.yml # Container orchestration
├── .env # Environment configuration
├── requirements.txt # Python dependencies
├── setup_db.py # Database schema setup
├── inspect_db.py # Database inspection tool
└── add_sample_data.py # Sample data generator

### 3. Run Tests

# Run all tests
```bash
pytest tests/ -v
```
# Run specific test category
```bash
pytest tests/sql/ -v              # CRUD and vault operations
pytest tests/integrity/ -v        # Data integrity tests
pytest tests/performance/ -v      # Performance benchmarks
pytest tests/migrations/ -v       # Schema validation
pytest tests/api/ -v             # API backend tests
pytest tests/commander_cli/ -v   # CLI command tests
```
# Generate HTML report
```bash
pytest tests/ -v --html=report.html --self-contained-html
```
# Run with coverage
```bash
pip install pytest-cov
pytest tests/ --cov=framework --cov-report=html
```
### Test Categories

### SQL Operations (tests/sql/)
## 5 tests - Core database operations
CRUD operations validation (create, read, update, delete)
AES-256-GCM encrypted vault data storage
Cascade delete verification
Encryption key isolation
Tampering detection with authenticated encryption

### Data Integrity (tests/integrity/)
## 3 tests - Database constraints and referential integrity
Unique constraint enforcement (username, email)
Foreign key constraint validation
Concurrent update consistency

### Performance (tests/performance/)
## 2 tests - Query optimization and benchmarks
Bulk insert benchmarks (100 records < 5 seconds)
Indexed query performance (< 100ms)

### Schema/Migrations (tests/migrations/)
## 3 tests - Database structure validation
Table structure verification
Index existence validation
Schema migration testing (add/drop columns)

### API Backend (tests/api/)
## 3 tests - Backend data flows
JSON payload handling and user creation
Vault record retrieval simulation
API error handling for invalid data

### CLI Commands (tests/commander_cli/)
## 4 tests - Command-line operations
Data export operations
Bulk delete commands
Database statistics queries
Custom SQL query execution

### Database Inspection
```bash
# View current database state
python inspect_db.py

# Add sample test data
python add_sample_data.py

# Connect to PostgreSQL directly via Docker
docker exec -it vault-postgres psql -U vault_admin -d vault_db
```
### Useful SQL Commands
```bash
-- List all tables
\dt

-- View table structure
\d vault_users
\d vault_records

-- Query data
SELECT * FROM vault_users;
SELECT * FROM vault_records;

-- Check counts
SELECT COUNT(*) FROM vault_users;
SELECT COUNT(*) FROM vault_records;

-- Exit
\q
```

### Configuration
Environment variables in .env:
```bash
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=vault_db
POSTGRES_USER=vault_admin
POSTGRES_PASSWORD=secure_password_123

# MySQL Configuration
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=vault_db
MYSQL_USER=vault_admin
MYSQL_PASSWORD=secure_password_123

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Test Configuration
ENABLE_PERFORMANCE_TESTS=true
ENABLE_AWS_TESTS=false
TEST_DATA_SIZE=1000
```
### Key Features
Security & Encryption
✅ AES-256-GCM encryption - Industry standard for password managers
✅ Authenticated encryption - Prevents tampering and replay attacks
✅ Key isolation testing - Validates proper key management
✅ Tampering detection - Verifies data integrity through authentication tags

Database Testing
✅ Automated schema validation and migration testing
✅ Data integrity enforcement (constraints, foreign keys)
✅ Performance benchmarking with concrete thresholds
✅ Index optimization verification
✅ Cascade delete and referential integrity validation

Test Quality

✅ Comprehensive test documentation
✅ Organized by functional category
✅ Isolated test data with automatic cleanup
✅ CI/CD ready with Docker containers
✅ HTML reporting and coverage analysis

Test Results
Total: 20+ test cases

SQL Operations: 5 tests
Data Integrity: 3 tests
Performance: 2 tests
Schema/Migrations: 3 tests
API Backend: 3 tests
CLI Commands: 4 tests
All tests validate critical database operations, security practices, and performance benchmarks required for enterprise vault systems.

### Docker Management
```bash
# Start all services
docker-compose up -d

# View running containers
docker ps

# View logs
docker-compose logs -f postgres

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v
```
### Troubleshooting
Database Connection Errors
```bash
# Ensure Docker is running
docker ps

# Restart containers
docker-compose down
docker-compose up -d

# Check container health
docker-compose ps
```
Test Failures
```bash
# Ensure database is initialized
python setup_db.py

# Clear test data
docker-compose down -v
docker-compose up -d
python setup_db.py
```
Import errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```
### Documentation
Test Plan: TEST_PLAN.md - Comprehensive test strategy
Blog Post: docs/blog_post.md - Project deep dive
This README: Project overview and setup

### Technologies Demonstrated
## Database Skills

PostgreSQL and MySQL expertise
Complex SQL queries for validation
Schema design and migration testing
Index optimization and performance tuning
Foreign keys and referential integrity

## Security & Encryption

AES-256-GCM authenticated encryption
Secure key generation and management
Cryptographic best practices
Data integrity verification

## Testing & QA

pytest framework and fixtures
Test isolation and cleanup
Performance benchmarking
CI/CD ready automation
Comprehensive documentation

## DevOps & Infrastructure

Docker containerization
docker-compose orchestration
Environment configuration management
Database health checks

### Use Cases
This testing framework demonstrates skills applicable to:

Password manager QA (Keeper Security, 1Password, LastPass, Bitwarden)
Enterprise vault systems testing
Database QA for SaaS platforms
Backend data integrity validation
Encrypted data storage testing
Compliance and security testing (FIPS, SOC2, ISO 27001)

### Future Enhancements
Advanced performance testing with EXPLAIN analysis
AWS RDS and Aurora cloud database testing
Stored procedures and triggers testing
Multi-node replication consistency validation
Chaos engineering and failure injection
Security scanning and compliance validation

---

## 📄 License

MIT License - See LICENSE file for details

## 📧 Contact

For questions or collaboration opportunities, please reach out through GitHub.

**Note**: This is a demonstration project created to showcase database QA automation skills for enterprise vault and privileged access management systems. Test scenarios utilize industry-standard encryption (AES-256-GCM) and follow best practices for security testing, data integrity validation, and performance benchmarking.

---

**Built with**: Python | pytest | PostgreSQL | MySQL | Docker | AES-256-GCM | Database Testing

**Author**: Carolina Steadham - Database QA Engineer specializing in security-critical systems


# Database QA Automation Test Suite

> A comprehensive automated testing framework demonstrating professional database quality assurance practices with production-grade encryption.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Overview

This project showcases enterprise-level database testing capabilities, including CRUD validation, data integrity checks, performance benchmarking, schema migrations, and AES-256-GCM encryption testing. Built with Python, Docker, and pytest, it demonstrates real-world QA engineering skills for database-driven applications.

---

## ✨ Key Features

### 🔐 Security & Encryption
- **AES-256-GCM** authenticated encryption implementation
- **Key isolation** validation and tampering detection
- **Nonce uniqueness** verification across operations

### 🗄️ Database Testing
- **Multi-database support** - PostgreSQL & MySQL
- **CRUD operations** validation with transaction handling
- **Data integrity** testing (constraints, foreign keys, concurrency)
- **Schema validation** and migration testing

### ⚡ Performance & Optimization
- **Bulk operation** benchmarks (10,000+ records)
- **Query optimization** testing with indexes
- **Response time** validation (<100ms for indexed queries)

### 🛠️ Professional Tooling
- **Docker containerization** for consistent environments
- **Automated test reporting** (HTML & Allure)
- **Code coverage** analysis
- **Database inspection** utilities

---

## 📁 Project Structure
```bash
database-qa-automation/
│
├── 📂 framework/ # Core testing framework
│ ├── base_test.py # Base test class with setup/teardown
│ └── db_manager.py # Database connection manager
│
├── 📂 tests/ # Test suite (22+ test cases)
│ ├── sql/ # CRUD & encryption (7 tests)
│ ├── integrity/ # Data integrity (3 tests)
│ ├── performance/ # Benchmarks (2 tests)
│ ├── migrations/ # Schema validation (3 tests)
│ ├── api/ # API workflows (3 tests)
│ └── commander_cli/ # CLI operations (4 tests)
│
├── 📂 docs/ # Documentation
│ ├── TEST_PLAN.md # Comprehensive test strategy
│ ├── TEST_CASES.md # Detailed specifications
│ └── blog_post.md # Technical deep-dive
│
├── 📄 docker-compose.yml # PostgreSQL, MySQL, Redis
├── 📄 setup_db.py # Database initialization
├── 📄 inspect_db.py # Database inspection tool
└── 📄 requirements.txt # Python dependencies
```

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:
- **Python 3.9+**
- **Docker Desktop**
- **Git**

### Installation Steps

**1️⃣ Clone & Navigate**
```bash
git clone https://github.com/YOUR_USERNAME/database-qa-automation.git
cd database-qa-automation
```
2️⃣ Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
4️⃣ Start Docker Containers
```bash
docker-compose up -d
```
5️⃣ Initialize Database
```bash
python setup_db.py
```
6️⃣ Run Tests
```bash
pytest tests/ -v
```
🧪 Test Execution
Run All Tests
```bash
pytest tests/ -v
```
Run Specific Category
```bash
pytest tests/sql/ -v              # SQL operations
pytest tests/integrity/ -v        # Data integrity
pytest tests/performance/ -v      # Performance benchmarks
```
Generate Reports
```bash
# HTML Report
pytest tests/ -v --html=report.html --self-contained-html

# Coverage Report
pytest tests/ --cov=framework --cov-report=html

# Allure Report
pytest tests/ --alluredir=allure-results
allure serve allure-results
```
## 📊 Test Coverage

| Category | Test Count | Description |
|----------|------------|-------------|
| **SQL Operations** | 7 | CRUD + AES-256-GCM encryption |
| **Data Integrity** | 3 | Constraints, FKs, concurrent access |
| **Performance** | 2 | Bulk ops & query optimization |
| **Schema/Migrations** | 3 | Structure, indexes, ALTER ops |
| **API Backend** | 3 | Data flow & error handling |
| **CLI Commands** | 4 | Export, delete, stats, queries |
| **Total** | **22+** | **Comprehensive coverage** |

---

## 🔐 Encryption Implementation

### AES-256-GCM Specifications

```python
Algorithm:     AES-256-GCM (Galois/Counter Mode)
Key Size:      256 bits (32 bytes)
Nonce:         96 bits (12 bytes) - unique per operation
Mode:          Authenticated Encryption with Associated Data (AEAD)
Storage:       Hex-encoded with prepended nonce
```
Security Validations
✅ Key Isolation - Data encrypted with one key cannot be decrypted with another
✅ Tampering Detection - Modified ciphertext fails authentication
✅ Nonce Uniqueness - Each encryption uses a unique nonce
✅ Metadata Tracking - Encryption algorithm, timestamp, key ID stored

🗄️ Database Schema
vault_users Table
```bash
CREATE TABLE vault_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
vault_records Table
```bash
CREATE TABLE vault_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES vault_users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    encrypted_data TEXT NOT NULL,
    encryption_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.9+ |
| **Test Framework** | pytest, unittest |
| **Databases** | PostgreSQL 15, MySQL 8.0 |
| **Caching** | Redis 7 |
| **Encryption** | AES-256-GCM (cryptography library) |
| **Containerization** | Docker, docker-compose |
| **DB Drivers** | psycopg2-binary, PyMySQL |
| **Reporting** | pytest-html, allure-pytest |
| **Benchmarking** | pytest-benchmark |
| **Utilities** | python-dotenv, Faker, coverage |

---

## 📈 Performance Benchmarks

| Benchmark | Threshold | Validates |
|-----------|-----------|-----------|
| **Bulk Insert** | < 5 seconds | 10,000 record insertion performance |
| **Indexed Query** | < 100ms | Query optimization with proper indexing |

---

## 🔍 Database Inspection

### View Current State
```bash
python inspect_db.py
```
Direct PostgreSQL Access
```bash
docker exec -it database-qa-automation-postgres-1 psql -U qauser -d qa_test_db
```
Query Examples
```bash
SELECT * FROM vault_users;
SELECT * FROM vault_records;
SELECT COUNT(*) FROM vault_records WHERE user_id = 1;
```
Debug Test Output
```bash
pytest tests/ -v -s  # -s flag shows print statements
```
📚 Documentation
TEST_PLAN.md - Comprehensive test strategy & scope
TEST_CASES.md - Detailed test specifications with IDs

🧹 Cleanup & Maintenance
Stop Containers
```bash
docker-compose down
```
Remove All Data (Reset)
```bash
docker-compose down -v
```
Restart Fresh
```bash
docker-compose down -v
docker-compose up -d
python setup_db.py
```
### 📝 Development Notes
## Adding New Tests
Create test file in appropriate category folder
Inherit from BaseTest class
Follow naming convention: test_{category}_{id}_{description}
Add test ID and structured docstring
Update TEST_CASES.md documentation

Environment Configuration
Edit .env file for custom database settings:
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=qa_test_db
POSTGRES_USER=qauser
POSTGRES_PASSWORD=qapass123
```

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

👤 Author
Carolina Steadham

GitHub: @steadhac
LinkedIn: Carolina Steadham


🌟 Acknowledgments
Built as a comprehensive demonstration of professional database QA practices, showcasing:

Enterprise-level test automation
Production-grade security implementation
Performance optimization techniques
Docker containerization best practices

<div align="center">

Built with ❤️ for Database Quality Assurance Excellence

Report Bug · Request Feature

</div>


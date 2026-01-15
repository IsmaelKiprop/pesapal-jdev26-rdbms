# Limitations - Pesapal RDBMS

This document outlines the intentional limitations of the Pesapal RDBMS implementation. These limitations were chosen to balance scope, clarity, and educational value for the challenge requirements.

## 🚫 SQL Language Limitations

### Supported Operations Only
The RDBMS implements a minimal SQL subset:

**✅ Supported:**
- `CREATE TABLE` with basic column definitions
- `INSERT INTO` with single or multiple row values
- `SELECT` with basic WHERE clauses
- `UPDATE` with SET clauses and WHERE conditions
- `DELETE` with WHERE conditions
- `INNER JOIN` with equality conditions

**❌ Not Supported:**
- Subqueries (nested SELECT statements)
- Aggregate functions (COUNT, SUM, AVG, etc.)
- GROUP BY and HAVING clauses
- ORDER BY for result sorting
- LIMIT and OFFSET for pagination
- UNION operations
- Complex JOIN types (LEFT, RIGHT, FULL OUTER)
- Self-joins
- CROSS JOIN
- Transaction control (BEGIN, COMMIT, ROLLBACK)

### WHERE Clause Limitations
Only basic comparison operations are supported:

**✅ Supported:**
- Equality: `column = value`
- Inequality: `column != value`
- Greater than: `column > value`
- Less than: `column < value`

**❌ Not Supported:**
- BETWEEN operator
- IN operator with lists
- LIKE operator for pattern matching
- Logical operators (AND, OR, NOT)
- Parentheses for expression grouping
- NULL comparisons (IS NULL, IS NOT NULL)

## 📊 Data Type Limitations

### Limited Type System
Only three basic data types are implemented:

**✅ Supported:**
- `INT`: Integer values
- `VARCHAR(n)`: String values with maximum length
- `BOOLEAN`: True/False values

**❌ Not Supported:**
- Floating point numbers (FLOAT, DECIMAL)
- Date and time types (DATE, TIME, TIMESTAMP)
- Large text types (TEXT, CLOB)
- Binary data types (BLOB)
- Enumerated types (ENUM)
- Array types
- JSON or XML types

### Type Coercion Limitations
Limited automatic type conversion:

**✅ Supported:**
- String to integer conversion
- String to boolean conversion ('true', 'false')
- Basic string length validation

**❌ Not Supported:**
- Float to integer conversion
- Date string parsing
- Complex type casting
- Precision and scale handling

## 🔧 Constraint Limitations

### Basic Constraint Support
Only fundamental constraints are implemented:

**✅ Supported:**
- PRIMARY KEY (uniqueness + non-null)
- UNIQUE constraints
- NOT NULL constraints

**❌ Not Supported:**
- Foreign key constraints (referential integrity)
- CHECK constraints (complex validation rules)
- DEFAULT values
- AUTO_INCREMENT/IDENTITY columns
- Composite primary keys
- Multi-column unique constraints

### Constraint Enforcement Limitations
Simplified constraint checking:

**✅ Supported:**
- Insert-time constraint validation
- Update-time constraint checking
- Basic error messages

**❌ Not Supported:**
- Deferred constraint checking
- Cascade delete/update rules
- Constraint violation details
- Partial indexes (filtered indexes)

## 📈 Performance Limitations

### Simple Indexing Strategy
Basic hash-based indexing only:

**✅ Supported:**
- Hash indexes for equality lookups
- Automatic indexing for primary keys
- Automatic indexing for unique columns

**❌ Not Supported:**
- B-tree indexes for range queries
- Composite indexes (multi-column)
- Full-text search indexes
- Index statistics and optimization
- Query plan optimization
- Index maintenance strategies

### Memory Storage Limitations
In-memory storage with basic persistence:

**✅ Supported:**
- In-memory row storage
- JSON file persistence
- Basic backup/restore

**❌ Not Supported:**
- Disk-based storage engines
- Memory management and garbage collection
- Large dataset handling (memory limits)
- Streaming query results
- Caching strategies
- Connection pooling

## 🔄 Concurrency Limitations

### Single-Threaded Design
No concurrency support implemented:

**✅ Supported:**
- Sequential query execution
- Atomic single operations

**❌ Not Supported:**
- Multi-threading support
- Concurrent query execution
- Locking mechanisms
- Deadlock detection
- Transaction isolation levels
- Connection management

## 🌐 Web Integration Limitations

### Basic Django Integration
Simple integration without advanced features:

**✅ Supported:**
- Basic CRUD operations
- JSON API endpoints
- Simple web interface

**❌ Not Supported:**
- Authentication and authorization
- Input validation and sanitization
- Rate limiting
- API versioning
- Error handling middleware
- Logging and monitoring

## 💾 Persistence Limitations

### JSON File Storage
Basic file-based persistence only:

**✅ Supported:**
- JSON serialization
- Manual save/load operations
- Basic backup functionality

**❌ Not Supported:**
- Incremental saves
- Write-ahead logging
- Point-in-time recovery
- Data compression
- Encryption at rest
- Multi-file storage

## 🔍 Query Optimization Limitations

### No Query Optimization
Simple execution without optimization:

**✅ Supported:**
- Direct statement execution
- Basic index usage

**❌ Not Supported:**
- Query plan generation
- Cost-based optimization
- Join order optimization
- Predicate pushdown
- Index selection algorithms
- Query caching

## 🧪 Testing Limitations

### Limited Test Coverage
Basic testing approach:

**✅ Supported:**
- Manual testing through REPL
- Basic web interface testing
- Simple integration tests

**❌ Not Supported:**
- Comprehensive unit test suite
- Performance benchmarking
- Load testing
- Regression testing
- Automated test pipelines

## 🛠️ Tooling Limitations

### Basic Development Tools
Minimal tooling support:

**✅ Supported:**
- Basic error messages
- Simple debugging output
- Manual database inspection

**❌ Not Supported:**
- Query execution plans
- Performance profiling tools
- Database migration tools
- Schema comparison tools
- Data import/export utilities

## 📏 Scale Limitations

### Small-Scale Design
Designed for demonstration, not production:

**✅ Supported:**
- Small datasets (hundreds of rows)
- Single user access
- Basic operations

**❌ Not Supported:**
- Large datasets (millions of rows)
- High concurrency
- Distributed deployment
- High availability
- Disaster recovery

## 🎯 Why These Limitations?

### Challenge Requirements
The limitations align with the challenge goals:
- **Educational Value**: Simple code demonstrates core concepts
- **Interview Readiness**: Clear, explainable implementation
- **Scope Management**: Achievable within time constraints
- **Focus on Fundamentals**: Emphasizes database basics over features

### Intentional Simplicity
Each limitation was a deliberate choice:
- **Clarity over Complexity**: Easy to understand and explain
- **Correctness over Features**: Working subset vs. broken full set
- **Learning over Performance**: Educational value over optimization
- **Maintainability over Completeness**: Manageable codebase

## 🔮 What Would Be Next?

If extending beyond the challenge scope, priorities would be:

1. **SQL Completeness**: Add missing SQL features
2. **Performance**: Implement query optimization
3. **Concurrency**: Add multi-threading support
4. **Storage**: Implement disk-based storage engine
5. **Testing**: Comprehensive test suite
6. **Tooling**: Development and debugging tools

These limitations make the system perfect for learning and demonstration while keeping the implementation manageable and interview-ready.

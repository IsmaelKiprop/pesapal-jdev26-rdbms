# Pesapal Junior Developer Challenge '26 - Custom RDBMS

A minimal but real relational database management system (RDBMS) implemented in Python with Django web integration.

## 🎯 Challenge Overview

This project demonstrates the implementation of a custom RDBMS from scratch without using external databases or Django ORM. The system provides SQL-like operations, constraint enforcement, indexing, and a complete Django web demo.

## ✨ What Works

### Core RDBMS Features
- **SQL-like Interface**: CREATE TABLE, INSERT, SELECT, UPDATE, DELETE
- **Schema Support**: INT, VARCHAR, BOOLEAN column types with constraints
- **Constraints**: PRIMARY KEY, UNIQUE, NOT NULL enforcement
- **Indexing**: Hash-based indexes for primary keys and unique columns
- **Storage**: In-memory storage with optional JSON persistence
- **JOIN Operations**: Basic INNER JOIN with equality conditions
- **REPL**: Interactive command-line interface

### Django Web Demo
- **Complete CRUD Operations**: Create, Read, Update, Delete for users and todos
- **No Django ORM**: Uses custom RDBMS directly from views
- **RESTful API**: JSON endpoints for all operations
- **Modern UI**: Clean, responsive web interface
- **JOIN Demonstration**: Shows user-todo relationships

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd pesapal-jdev26-rdbms
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
pip install -r web_demo/requirements.txt
```

### Running the RDBMS REPL

1. **Start the interactive shell**:
```bash
python -m rdbms.main
```

2. **With persistence** (optional):
```bash
python -m rdbms.main --persist data.json
```

3. **Try basic SQL commands**:
```sql
CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), active BOOLEAN)
INSERT INTO users (id, name, active) VALUES (1, 'Alice', TRUE)
SELECT * FROM users
```

### Running the Django Web Demo

1. **Start the Django development server**:
```bash
cd web_demo
python manage.py runserver
```

2. **Open your browser**:
Navigate to `http://localhost:8000` to access the demo interface.

## 📁 Project Structure

```
pesapal-jdev26-rdbms/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── rdbms/                    # Custom RDBMS implementation
│   ├── __init__.py
│   ├── main.py              # REPL entry point
│   ├── repl/                # Interactive shell
│   │   └── repl.py
│   ├── parser/              # SQL parser
│   │   └── sql_parser.py
│   ├── engine/              # Core database engine
│   │   ├── database.py
│   │   ├── table.py
│   │   ├── row.py
│   │   └── executor.py
│   ├── storage/             # Storage layer
│   │   └── memory_store.py
│   └── types/               # Type system
│       └── schema.py
├── web_demo/                # Django web application
│   ├── manage.py
│   ├── requirements.txt
│   ├── web_demo/
│   │   ├── settings.py      # DATABASES = {} (no Django ORM)
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── app/
│       ├── views.py         # Uses custom RDBMS directly
│       ├── urls.py
│       └── templates/
│           └── app/
│               └── index.html
└── docs/                    # Documentation
    ├── design.md
    ├── limitations.md
    └── future_work.md
```

## 🎮 Usage Examples

### REPL Commands

```sql
-- Create tables
CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(255) UNIQUE, active BOOLEAN)
CREATE TABLE todos (id INT PRIMARY KEY, user_id INT, title VARCHAR(200), completed BOOLEAN)

-- Insert data
INSERT INTO users (id, name, email, active) VALUES (1, 'Alice', 'alice@example.com', TRUE)
INSERT INTO todos (id, user_id, title, completed) VALUES (1, 1, 'Learn RDBMS', FALSE)

-- Query data
SELECT * FROM users WHERE active = TRUE
SELECT * FROM todos WHERE completed = FALSE

-- Update data
UPDATE todos SET completed = TRUE WHERE id = 1

-- Delete data
DELETE FROM todos WHERE completed = TRUE

-- Join tables
SELECT * FROM users INNER JOIN todos ON users.id = todos.user_id
```

### Special REPL Commands

- `help` - Show available commands
- `tables` - List all tables
- `schema [table]` - Show table schema
- `save` - Save to persistence file
- `clear` - Clear all data
- `stats` - Show database statistics
- `exit` - Exit the REPL

### Django API Endpoints

- `GET /api/users/` - List all users
- `POST /api/users/create/` - Create a new user
- `GET /api/todos/` - List all todos (with optional filtering)
- `POST /api/todos/create/` - Create a new todo
- `PUT /api/todos/<id>/update/` - Update a todo
- `DELETE /api/todos/<id>/delete/` - Delete a todo
- `GET /api/join-demo/` - Demonstrate JOIN operation
- `GET /api/stats/` - Database statistics

## 🏗️ Architecture Highlights

### Type System
- Strongly typed columns with validation
- Automatic type coercion (strings to ints/booleans)
- Null handling with nullable constraints

### Constraint Enforcement
- Primary key uniqueness enforced at insert/update
- Unique constraints with proper validation
- NOT NULL constraints enforced

### Indexing Strategy
- Hash-based indexes for O(1) lookups
- Automatic index creation for constrained columns
- Index maintenance during updates/deletes

### SQL Parser
- Recursive descent parser for SQL syntax
- Support for quoted strings and numeric literals
- Error handling with meaningful messages

### Storage Layer
- In-memory storage for performance
- Optional JSON persistence
- Atomic operations with rollback support

## 🎯 Design Philosophy

This implementation prioritizes:

1. **Clarity over cleverness**: Simple, readable code that's easy to understand
2. **Correctness**: Proper constraint enforcement and data integrity
3. **Learning value**: Demonstrates core database concepts clearly
4. **Interview readiness**: Clean code with good documentation
5. **Modularity**: Well-separated concerns and testable components

## ⚠️ What's Intentionally Limited

- **SQL Subset**: Only basic operations (no subqueries, aggregates, etc.)
- **Data Types**: Limited to INT, VARCHAR, BOOLEAN
- **Joins**: Only INNER JOIN with equality conditions
- **Transactions**: No multi-statement transactions
- **Concurrency**: No multi-threading support
- **Performance**: Optimized for clarity, not speed
- **Persistence**: JSON-based, not production-ready

## 🤖 AI Usage Disclosure

This project was developed with AI assistance for:

- Code structure and organization
- Implementation of database algorithms
- Django integration patterns
- Documentation and examples

The core concepts, architecture decisions, and implementation details were driven by the challenge requirements and database fundamentals.

## 📚 Learning Resources

The implementation demonstrates these computer science concepts:

- **Database Architecture**: Storage engines, query processing
- **Data Structures**: Hash tables, indexing strategies
- **Parsing Techniques**: Recursive descent parsing
- **Constraint Theory**: Primary keys, uniqueness, referential integrity
- **Software Design**: Separation of concerns, modular architecture

## 🧪 Testing the System

### REPL Testing
```bash
python -m rdbms.main
> CREATE TABLE test (id INT PRIMARY KEY, name VARCHAR(50))
> INSERT INTO test (id, name) VALUES (1, 'Hello')
> SELECT * FROM test
> UPDATE test SET name = 'World' WHERE id = 1
> DELETE FROM test WHERE id = 1
```

### Web Demo Testing
1. Start Django server: `python manage.py runserver`
2. Open `http://localhost:8000`
3. Try creating users and todos
4. Test the JOIN operation demo
5. Check database statistics

## 📄 License

This project is created for the Pesapal Junior Developer Challenge '26.

## 🙏 Acknowledgments

Built for the Pesapal Junior Developer Challenge '26. This implementation demonstrates fundamental database concepts while maintaining simplicity and educational value.
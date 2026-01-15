# Design Document - Pesapal RDBMS

## 🏗️ Architecture Overview

The Pesapal RDBMS is designed as a layered architecture with clear separation of concerns. Each layer has specific responsibilities and well-defined interfaces.

### Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   REPL Shell    │    │      Django Web Interface       │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Query Processing Layer                    │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   SQL Parser    │    │     Execution Engine           │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Database Engine                         │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │    Database     │    │         Table                   │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                            │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   Memory Store   │    │      Type System                │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Core Components

### 1. Type System (`types/schema.py`)

**Purpose**: Define data types and schema validation

**Key Classes**:
- `ColumnType`: Enum for supported types (INT, VARCHAR, BOOLEAN)
- `ColumnDefinition`: Column metadata with constraints
- `Schema`: Table schema with validation logic

**Design Decisions**:
- **Strong Typing**: All data is validated against column types
- **Type Coercion**: Automatic conversion from string inputs
- **Constraint Validation**: Built-in validation for constraints

**Tradeoffs**:
- Limited type set for simplicity vs. completeness
- Runtime validation vs. compile-time type checking

### 2. Row Representation (`engine/row.py`)

**Purpose**: Immutable row representation

**Key Features**:
- **Immutability**: Rows cannot be modified after creation
- **Value Access**: Dictionary-like interface with type safety
- **Projection Support**: Create new rows with selected columns

**Design Decisions**:
- Immutable rows prevent accidental data corruption
- Frozen dataclass ensures hashability for indexing
- Functional approach for modifications (create new instances)

### 3. Table Abstraction (`engine/table.py`)

**Purpose**: Core table operations and constraint enforcement

**Key Responsibilities**:
- Row storage and retrieval
- Constraint enforcement (PRIMARY KEY, UNIQUE)
- Index management
- CRUD operations

**Indexing Strategy**:
```python
# Hash-based index structure
_indexes: Dict[str, Dict[Any, Set[int]]]
# Column name -> Value -> Set of row indices
```

**Design Decisions**:
- **Hash Indexes**: O(1) lookup for equality conditions
- **Automatic Indexing**: Indexes created for constrained columns
- **Memory Storage**: Simple list storage with index overlays

### 4. Database Container (`engine/database.py`)

**Purpose**: Multi-table management and cross-table operations

**Key Features**:
- Table lifecycle management
- JOIN operations
- Query coordination
- Schema introspection

**JOIN Implementation**:
```python
def join_inner(self, left_table, right_table, left_column, right_column):
    # Build index for right table
    right_index = {}
    for row in right_table.select_all():
        key = row.get(right_column)
        if key not in right_index:
            right_index[key] = []
        right_index[key].append(row)
    
    # Perform join
    for left_row in left_table.select_all():
        left_key = left_row.get(left_column)
        if left_key in right_index:
            for right_row in right_index[left_key]:
                # Combine rows with qualified column names
```

### 5. SQL Parser (`parser/sql_parser.py`)

**Purpose**: Convert SQL strings to structured statements

**Parser Strategy**:
- **Regular Expression Based**: Simple pattern matching for clarity
- **Statement Objects**: Structured representation of SQL operations
- **Error Handling**: Meaningful error messages for syntax errors

**Supported Syntax**:
```sql
CREATE TABLE table_name (col1 TYPE [constraints], ...)
INSERT INTO table_name (cols) VALUES (vals)
SELECT [cols] FROM table [WHERE condition] [JOIN ...]
UPDATE table SET col = val [WHERE condition]
DELETE FROM table [WHERE condition]
```

**Design Tradeoffs**:
- Simple regex parser vs. full grammar parser
- Limited SQL subset for maintainability
- Clear error messages over comprehensive syntax support

### 6. Execution Engine (`engine/executor.py`)

**Purpose**: Bridge between parsed SQL and database operations

**Key Features**:
- Statement routing to appropriate database methods
- WHERE clause parsing and condition function generation
- Result formatting and error handling
- JOIN query coordination

**WHERE Clause Processing**:
```python
def _parse_where_clause(self, where_clause: str) -> Callable[[Row], bool]:
    if '=' in where_clause:
        left, right = where_clause.split('=', 1)
        column = left.strip()
        value = self._convert_value(right.strip())
        
        def condition(row: Row) -> bool:
            return row.get(column) == value
        
        return condition
```

### 7. Storage Layer (`storage/memory_store.py`)

**Purpose**: Data persistence and retrieval

**Features**:
- In-memory storage with JSON persistence
- Atomic operations
- Backup and restore functionality
- Metadata tracking

**Persistence Strategy**:
```python
{
    "metadata": {
        "saved_at": "2024-01-15T10:30:00",
        "version": "1.0"
    },
    "data": {
        "table_schemas": {...},
        "table_data": {...}
    }
}
```

## 🔄 Data Flow

### Query Execution Flow

1. **SQL Input** → Parser → **Statement Object**
2. **Statement Object** → Executor → **Database Operations**
3. **Database Operations** → Storage → **Results**
4. **Results** → Executor → **Formatted Response**

### Row Insertion Flow

1. **Row Data** → Schema Validation → **Validated Data**
2. **Validated Data** → Constraint Check → **Constraint-Verified Data**
3. **Constraint-Verified Data** → Index Update → **Stored Row**
4. **Stored Row** → Success Response

## 🎯 Design Principles

### 1. Separation of Concerns

Each component has a single, well-defined responsibility:
- Parser: Only parses SQL
- Engine: Only executes operations
- Storage: Only persists data
- Types: Only defines schemas

### 2. Immutability

Rows are immutable to ensure data integrity:
- Prevents accidental modification
- Enables safe sharing between components
- Simplifies indexing and caching

### 3. Type Safety

Strong typing throughout the system:
- Column type validation
- Automatic type coercion
- Runtime type checking

### 4. Error Handling

Comprehensive error handling at all levels:
- Parser syntax errors
- Constraint violations
- Type mismatches
- Storage failures

## 🔧 Implementation Tradeoffs

### Performance vs. Clarity

**Chosen**: Clarity and readability
- Simple data structures
- Clear algorithm implementations
- Comprehensive comments

**Not Chosen**: Maximum performance
- Complex optimizations
- Low-level memory management
- Advanced indexing strategies

### Completeness vs. Simplicity

**Chosen**: Simplicity and maintainability
- Limited SQL subset
- Basic data types
- Simple constraint system

**Not Chosen**: Full SQL compatibility
- Complex query optimization
- Advanced data types
- Sophisticated indexing

### Features vs. Correctness

**Chosen**: Correctness and reliability
- Proper constraint enforcement
- Comprehensive testing
- Robust error handling

**Not Chosen**: Feature completeness
- Advanced SQL features
- Performance optimizations
- Production-ready features

## 🧪 Testing Strategy

### Unit Testing Approach

Each component is designed for testability:
- Pure functions where possible
- Dependency injection
- Mockable interfaces
- Clear input/output contracts

### Integration Testing

End-to-end testing through:
- SQL command execution
- Django API endpoints
- REPL interactions
- Persistence operations

## 🔮 Extensibility

The architecture supports future extensions:

### Adding New Data Types
1. Extend `ColumnType` enum
2. Update validation logic in `Schema`
3. Add coercion rules
4. Update parser for new type syntax

### Adding New SQL Features
1. Extend parser with new patterns
2. Add new statement types
3. Implement execution logic
4. Update executor routing

### Adding Storage Backends
1. Implement storage interface
2. Update storage factory
3. Add configuration options
4. Maintain API compatibility

## 📊 Performance Characteristics

### Time Complexity

- **INSERT**: O(1) average case (with indexes)
- **SELECT by PK**: O(1) (hash index lookup)
- **SELECT with WHERE**: O(n) linear scan (or O(1) with index)
- **UPDATE**: O(n) for WHERE clause + O(1) per update
- **DELETE**: O(n) for WHERE clause + O(1) per delete
- **JOIN**: O(n + m) where n,m are table sizes

### Space Complexity

- **Storage**: O(n) where n is total number of rows
- **Indexes**: O(k) where k is number of unique values in indexed columns
- **Memory Overhead**: ~20-30% for indexes and metadata

## 🎓 Educational Value

This implementation demonstrates key database concepts:

1. **Storage Engines**: How data is stored and retrieved
2. **Query Processing**: Parsing and execution pipeline
3. **Indexing**: Hash-based indexing strategies
4. **Constraint Enforcement**: Maintaining data integrity
5. **Transaction Concepts**: Atomic operations (simplified)
6. **API Design**: Clean interfaces between components

The code is intentionally simple to facilitate learning while demonstrating real database principles.

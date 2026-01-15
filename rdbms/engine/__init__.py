"""
Database engine components for the custom RDBMS.

This package contains the core engine components including:
- Database: Main database container
- Table: Table abstraction with constraint enforcement
- Row: Immutable row representation
- Executor: SQL execution engine
"""

from .database import Database
from .table import Table
from .row import Row
from .executor import ExecutionEngine

__all__ = [
    "Database",
    "Table", 
    "Row",
    "ExecutionEngine"
]

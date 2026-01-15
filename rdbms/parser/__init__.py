"""
SQL parser for the custom RDBMS.

This package contains the SQL parser that converts SQL strings
into structured statement objects for execution.
"""

from .sql_parser import SQLParser, SQLStatement

__all__ = [
    "SQLParser",
    "SQLStatement"
]

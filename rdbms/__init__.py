"""
Custom RDBMS for Pesapal Junior Developer Challenge '26

A minimal but real relational database management system implemented in Python.
This package provides a SQL-like interface with in-memory storage and basic
relational operations.
"""

__version__ = "1.0.0"
__author__ = "Pesapal JDC '26 Participant"

from .types.schema import Schema, ColumnDefinition, ColumnType, create_schema

__all__ = [
    "Schema",
    "ColumnDefinition", 
    "ColumnType",
    "create_schema"
]

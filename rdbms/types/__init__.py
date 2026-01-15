"""
Type system for the custom RDBMS.

This package contains the schema and type definitions including:
- Schema: Table schema with column definitions
- ColumnDefinition: Individual column specifications
- ColumnType: Supported data types
"""

from .schema import Schema, ColumnDefinition, ColumnType, create_schema

__all__ = [
    "Schema",
    "ColumnDefinition",
    "ColumnType", 
    "create_schema"
]

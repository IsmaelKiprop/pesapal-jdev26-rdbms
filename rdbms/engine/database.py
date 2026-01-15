"""
Database implementation for the custom RDBMS.

This module implements the Database class which manages multiple tables,
provides SQL-like operations, and handles cross-table operations like joins.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from ..types.schema import Schema, create_schema
from .table import Table
from .row import Row


class Database:
    """
    Main database container that manages multiple tables.
    
    The Database class provides the primary interface for all SQL operations
    and coordinates between tables. It maintains table schemas and handles
    cross-table operations like joins.
    """
    
    def __init__(self, name: str = "database"):
        """
        Initialize a new database.
        
        Args:
            name: Database name for identification
        """
        self.name = name
        self._tables: Dict[str, Table] = {}
    
    def create_table(self, table_name: str, column_definitions: List[Dict[str, Any]]) -> Table:
        """
        Create a new table with the given column definitions.
        
        Args:
            table_name: Name of the table to create
            column_definitions: List of column definition dictionaries
            
        Returns:
            The created Table object
            
        Raises:
            ValueError: If table already exists or column definitions are invalid
        """
        if table_name in self._tables:
            raise ValueError(f"Table '{table_name}' already exists")
        
        # Create schema from column definitions
        schema = create_schema(table_name, column_definitions)
        
        # Create and store the table
        table = Table(schema)
        self._tables[table_name] = table
        
        return table
    
    def get_table(self, table_name: str) -> Table:
        """
        Get a table by name.
        
        Args:
            table_name: Name of the table to retrieve
            
        Returns:
            The Table object
            
        Raises:
            ValueError: If table doesn't exist
        """
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        return self._tables[table_name]
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        return table_name in self._tables
    
    def list_tables(self) -> List[str]:
        """Return list of all table names."""
        return list(self._tables.keys())
    
    def drop_table(self, table_name: str) -> None:
        """
        Drop a table from the database.
        
        Args:
            table_name: Name of the table to drop
            
        Raises:
            ValueError: If table doesn't exist
        """
        if table_name not in self._tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        del self._tables[table_name]
    
    def insert(self, table_name: str, row_data: Dict[str, Any]) -> Row:
        """
        Insert a row into the specified table.
        
        Args:
            table_name: Name of the table
            row_data: Dictionary of column names to values
            
        Returns:
            The inserted Row object
        """
        table = self.get_table(table_name)
        return table.insert(row_data)
    
    def select_all(self, table_name: str) -> List[Row]:
        """
        Select all rows from a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of all rows in the table
        """
        table = self.get_table(table_name)
        return table.select_all()
    
    def select_where(self, table_name: str, condition_func) -> List[Row]:
        """
        Select rows from a table matching a condition.
        
        Args:
            table_name: Name of the table
            condition_func: Function that takes a Row and returns boolean
            
        Returns:
            List of matching rows
        """
        table = self.get_table(table_name)
        return table.select_where(condition_func)
    
    def select_by_column(self, table_name: str, column_name: str, value: Any) -> List[Row]:
        """
        Select rows from a table where column equals value.
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
            value: Value to match
            
        Returns:
            List of matching rows
        """
        table = self.get_table(table_name)
        return table.select_by_column(column_name, value)
    
    def update_where(self, table_name: str, condition_func, updates: Dict[str, Any]) -> int:
        """
        Update rows in a table matching a condition.
        
        Args:
            table_name: Name of the table
            condition_func: Function that takes a Row and returns boolean
            updates: Dictionary of column names to new values
            
        Returns:
            Number of rows updated
        """
        table = self.get_table(table_name)
        return table.update_where(condition_func, updates)
    
    def delete_where(self, table_name: str, condition_func) -> int:
        """
        Delete rows from a table matching a condition.
        
        Args:
            table_name: Name of the table
            condition_func: Function that takes a Row and returns boolean
            
        Returns:
            Number of rows deleted
        """
        table = self.get_table(table_name)
        return table.delete_where(condition_func)
    
    def join_inner(self, left_table: str, right_table: str, 
                   left_column: str, right_column: str) -> List[Dict[str, Any]]:
        """
        Perform an inner join between two tables.
        
        Args:
            left_table: Name of the left table
            right_table: Name of the right table
            left_column: Column name from left table for join condition
            right_column: Column name from right table for join condition
            
        Returns:
            List of dictionaries representing joined rows
            
        Raises:
            ValueError: If tables or columns don't exist
        """
        # Validate tables exist
        if left_table not in self._tables:
            raise ValueError(f"Table '{left_table}' does not exist")
        if right_table not in self._tables:
            raise ValueError(f"Table '{right_table}' does not exist")
        
        left_tbl = self._tables[left_table]
        right_tbl = self._tables[right_table]
        
        # Validate columns exist
        if left_column not in left_tbl.schema.columns:
            raise ValueError(f"Column '{left_column}' does not exist in table '{left_table}'")
        if right_column not in right_tbl.schema.columns:
            raise ValueError(f"Column '{right_column}' does not exist in table '{right_table}'")
        
        # Perform the join
        joined_rows = []
        
        # Build index for right table for better performance
        right_index = {}
        for row in right_tbl.select_all():
            key = row.get(right_column)
            if key not in right_index:
                right_index[key] = []
            right_index[key].append(row)
        
        # Join rows
        for left_row in left_tbl.select_all():
            left_key = left_row.get(left_column)
            if left_key in right_index:
                for right_row in right_index[left_key]:
                    # Combine the rows
                    joined_data = {}
                    
                    # Add left table data with prefix
                    for col_name, value in left_row.items():
                        joined_data[f"{left_table}.{col_name}"] = value
                    
                    # Add right table data with prefix
                    for col_name, value in right_row.items():
                        joined_data[f"{right_table}.{col_name}"] = value
                    
                    joined_rows.append(joined_data)
        
        return joined_rows
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        table = self.get_table(table_name)
        schema = table.get_schema()
        
        return {
            "name": table_name,
            "row_count": table.count(),
            "columns": [
                {
                    "name": col_name,
                    "type": col_def.type.value,
                    "primary_key": col_def.primary_key,
                    "unique": col_def.unique,
                    "nullable": col_def.nullable,
                    "max_length": col_def.max_length
                }
                for col_name, col_def in schema.columns.items()
            ]
        }
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the entire database.
        
        Returns:
            Dictionary with database information
        """
        return {
            "name": self.name,
            "table_count": len(self._tables),
            "tables": [self.get_table_info(table_name) for table_name in self.list_tables()]
        }
    
    def clear_all_tables(self) -> None:
        """Remove all data from all tables (keeps table schemas)."""
        for table in self._tables.values():
            table._rows.clear()
            table._indexes.clear()
            table._build_constraint_indexes()
    
    def __str__(self) -> str:
        """String representation of the database."""
        return f"Database({self.name}, {len(self._tables)} tables)"
    
    def __repr__(self) -> str:
        """Detailed string representation of the database."""
        return f"Database(name='{self.name}', tables={list(self._tables.keys())})"

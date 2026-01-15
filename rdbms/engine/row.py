"""
Row representation for the custom RDBMS.

This module defines the Row class which represents a single record in a table.
Rows are immutable to ensure data integrity and provide consistent behavior
throughout the database system.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Row:
    """
    Represents a single row/record in a table.
    
    Rows are immutable to prevent accidental modification and ensure
    data integrity. All operations that modify data create new Row instances.
    """
    data: Dict[str, Any]
    
    def __post_init__(self):
        """Validate row after creation."""
        if not isinstance(self.data, dict):
            raise ValueError("Row data must be a dictionary")
    
    def get(self, column_name: str, default: Any = None) -> Any:
        """Get value for a column, with optional default."""
        return self.data.get(column_name, default)
    
    def __getitem__(self, column_name: str) -> Any:
        """Get value for a column using dictionary syntax."""
        return self.data[column_name]
    
    def __contains__(self, column_name: str) -> bool:
        """Check if column exists in row."""
        return column_name in self.data
    
    def keys(self):
        """Return column names in this row."""
        return self.data.keys()
    
    def values(self):
        """Return values in this row."""
        return self.data.values()
    
    def items(self):
        """Return (column_name, value) pairs."""
        return self.data.items()
    
    def with_value(self, column_name: str, value: Any) -> 'Row':
        """
        Create a new Row with a different value for the specified column.
        
        Args:
            column_name: Name of the column to update
            value: New value for the column
            
        Returns:
            New Row instance with updated value
        """
        new_data = self.data.copy()
        new_data[column_name] = value
        return Row(new_data)
    
    def without_column(self, column_name: str) -> 'Row':
        """
        Create a new Row without the specified column.
        
        Args:
            column_name: Name of the column to remove
            
        Returns:
            New Row instance without the column
        """
        new_data = self.data.copy()
        new_data.pop(column_name, None)
        return Row(new_data)
    
    def with_columns(self, column_mapping: Dict[str, Any]) -> 'Row':
        """
        Create a new Row with multiple column updates.
        
        Args:
            column_mapping: Dictionary of column names to new values
            
        Returns:
            New Row instance with updated columns
        """
        new_data = self.data.copy()
        new_data.update(column_mapping)
        return Row(new_data)
    
    def project(self, column_names: list[str]) -> 'Row':
        """
        Create a new Row with only the specified columns.
        
        Args:
            column_names: List of column names to keep
            
        Returns:
            New Row instance with only specified columns
        """
        new_data = {col: self.data[col] for col in column_names if col in self.data}
        return Row(new_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert row to dictionary."""
        return self.data.copy()
    
    def __str__(self) -> str:
        """String representation of the row."""
        values = [f"{k}={v}" for k, v in self.data.items()]
        return f"Row({', '.join(values)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the row."""
        return f"Row({self.data!r})"

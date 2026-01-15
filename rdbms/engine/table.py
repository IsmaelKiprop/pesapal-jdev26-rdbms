"""
Table implementation for the custom RDBMS.

This module implements the Table class which manages rows, enforces constraints,
and provides the core data manipulation operations for a single table.
"""

from typing import Any, Dict, List, Optional, Set, Callable
from ..types.schema import Schema, ColumnDefinition
from .row import Row


class Table:
    """
    Represents a single table in the database.
    
    A table stores rows of data according to a defined schema and enforces
    constraints like primary keys and unique columns. This implementation
    uses simple in-memory data structures for clarity and interview-readiness.
    """
    
    def __init__(self, schema: Schema):
        """
        Initialize a new table with the given schema.
        
        Args:
            schema: The table schema defining columns and constraints
        """
        self.schema = schema
        self._rows: List[Row] = []  # Main storage for rows
        self._indexes: Dict[str, Dict[Any, Set[int]]] = {}  # Column value -> row indices
        
        # Initialize indexes for constrained columns
        self._build_constraint_indexes()
    
    def _build_constraint_indexes(self) -> None:
        """Build indexes for primary key and unique columns."""
        for col_name, col_def in self.schema.columns.items():
            if col_def.primary_key or col_def.unique:
                self._indexes[col_name] = {}
    
    def insert(self, row_data: Dict[str, Any]) -> Row:
        """
        Insert a new row into the table.
        
        Args:
            row_data: Dictionary of column names to values
            
        Returns:
            The inserted Row object
            
        Raises:
            ValueError: If row violates schema constraints
        """
        # Validate and coerce the row data
        self.schema.validate_row(row_data)
        
        # Coerce values to appropriate types
        coerced_data = {}
        for col_name, value in row_data.items():
            col_def = self.schema.columns[col_name]
            coerced_data[col_name] = self.schema.coerce_value(value, col_def)
        
        # Check constraint violations
        self._check_constraint_violations(coerced_data)
        
        # Create and store the row
        row = Row(coerced_data)
        row_index = len(self._rows)
        self._rows.append(row)
        
        # Update indexes
        self._update_indexes(row, row_index)
        
        return row
    
    def _check_constraint_violations(self, row_data: Dict[str, Any]) -> None:
        """Check for primary key and unique constraint violations."""
        for col_name, value in row_data.items():
            if col_name in self._indexes and value is not None:
                if value in self._indexes[col_name]:
                    col_def = self.schema.columns[col_name]
                    if col_def.primary_key:
                        raise ValueError(f"Primary key violation: {col_name}={value} already exists")
                    else:
                        raise ValueError(f"Unique constraint violation: {col_name}={value} already exists")
    
    def _update_indexes(self, row: Row, row_index: int) -> None:
        """Update indexes with the new row."""
        for col_name in self._indexes:
            value = row.get(col_name)
            if value is not None:
                if value not in self._indexes[col_name]:
                    self._indexes[col_name][value] = set()
                self._indexes[col_name][value].add(row_index)
    
    def select_all(self) -> List[Row]:
        """Return all rows in the table."""
        return self._rows.copy()
    
    def select_where(self, condition: Callable[[Row], bool]) -> List[Row]:
        """
        Select rows that match the given condition.
        
        Args:
            condition: Function that takes a Row and returns boolean
            
        Returns:
            List of rows matching the condition
        """
        return [row for row in self._rows if condition(row)]
    
    def select_by_column(self, column_name: str, value: Any) -> List[Row]:
        """
        Select rows where column equals the given value.
        
        Args:
            column_name: Name of the column to search
            value: Value to match
            
        Returns:
            List of matching rows
        """
        if column_name not in self.schema.columns:
            raise ValueError(f"Unknown column: {column_name}")
        
        # Use index if available for better performance
        if column_name in self._indexes and value in self._indexes[column_name]:
            row_indices = self._indexes[column_name][value]
            return [self._rows[i] for i in row_indices]
        
        # Fall back to linear scan
        return [row for row in self._rows if row.get(column_name) == value]
    
    def update_where(self, condition: Callable[[Row], bool], updates: Dict[str, Any]) -> int:
        """
        Update rows matching the condition with new values.
        
        Args:
            condition: Function that takes a Row and returns boolean
            updates: Dictionary of column names to new values
            
        Returns:
            Number of rows updated
        """
        updated_count = 0
        
        # Find rows to update
        rows_to_update = []
        for i, row in enumerate(self._rows):
            if condition(row):
                rows_to_update.append((i, row))
        
        # Update each row
        for row_index, old_row in rows_to_update:
            # Create new row data
            new_data = old_row.to_dict()
            new_data.update(updates)
            
            # Validate the updated row
            self.schema.validate_row(new_data)
            
            # Coerce new values
            for col_name, value in updates.items():
                col_def = self.schema.columns[col_name]
                new_data[col_name] = self.schema.coerce_value(value, col_def)
            
            # Check constraint violations (excluding the row being updated)
            temp_row = Row(new_data)
            self._check_constraint_violations_for_update(old_row, temp_row)
            
            # Remove old row from indexes
            self._remove_from_indexes(old_row, row_index)
            
            # Create and store new row
            new_row = Row(new_data)
            self._rows[row_index] = new_row
            
            # Update indexes
            self._update_indexes(new_row, row_index)
            
            updated_count += 1
        
        return updated_count
    
    def _check_constraint_violations_for_update(self, old_row: Row, new_row: Row) -> None:
        """Check constraint violations for an update, excluding the current row."""
        for col_name in self._indexes:
            old_value = old_row.get(col_name)
            new_value = new_row.get(col_name)
            
            # Skip if value didn't change
            if old_value == new_value:
                continue
            
            if new_value is not None and new_value in self._indexes[col_name]:
                # Check if this is the only row with this value
                existing_indices = self._indexes[col_name][new_value]
                if len(existing_indices) > 1 or (len(existing_indices) == 1 and 
                                                  list(existing_indices)[0] != self._rows.index(old_row)):
                    col_def = self.schema.columns[col_name]
                    if col_def.primary_key:
                        raise ValueError(f"Primary key violation: {col_name}={new_value} already exists")
                    else:
                        raise ValueError(f"Unique constraint violation: {col_name}={new_value} already exists")
    
    def _remove_from_indexes(self, row: Row, row_index: int) -> None:
        """Remove a row from all indexes."""
        for col_name in self._indexes:
            value = row.get(col_name)
            if value is not None and value in self._indexes[col_name]:
                self._indexes[col_name][value].discard(row_index)
                # Clean up empty sets
                if not self._indexes[col_name][value]:
                    del self._indexes[col_name][value]
    
    def delete_where(self, condition: Callable[[Row], bool]) -> int:
        """
        Delete rows matching the condition.
        
        Args:
            condition: Function that takes a Row and returns boolean
            
        Returns:
            Number of rows deleted
        """
        # Find rows to delete (in reverse order to maintain indices)
        rows_to_delete = []
        for i, row in enumerate(self._rows):
            if condition(row):
                rows_to_delete.append(i)
        
        # Delete rows in reverse order
        deleted_count = 0
        for row_index in reversed(rows_to_delete):
            row = self._rows[row_index]
            
            # Remove from indexes
            self._remove_from_indexes(row, row_index)
            
            # Remove from main storage
            del self._rows[row_index]
            
            # Update indexes for rows after the deleted one
            for i in range(row_index, len(self._rows)):
                self._reindex_row(self._rows[i], i)
            
            deleted_count += 1
        
        return deleted_count
    
    def _reindex_row(self, row: Row, new_index: int) -> None:
        """Re-index a row after its position changes."""
        for col_name in self._indexes:
            value = row.get(col_name)
            if value is not None:
                # Remove old index entries
                for indices in self._indexes[col_name].values():
                    indices.discard(new_index)
                
                # Add new index entry
                if value not in self._indexes[col_name]:
                    self._indexes[col_name][value] = set()
                self._indexes[col_name][value].add(new_index)
    
    def count(self) -> int:
        """Return the number of rows in the table."""
        return len(self._rows)
    
    def is_empty(self) -> bool:
        """Check if the table is empty."""
        return len(self._rows) == 0
    
    def get_schema(self) -> Schema:
        """Return the table schema."""
        return self.schema
    
    def __str__(self) -> str:
        """String representation of the table."""
        return f"Table({self.schema.name}, {self.count()} rows)"
    
    def __repr__(self) -> str:
        """Detailed string representation of the table."""
        return f"Table(name='{self.schema.name}', rows={self.count()}, schema={self.schema})"

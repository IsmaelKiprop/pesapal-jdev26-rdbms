"""
Schema and column type definitions for the custom RDBMS.

This module defines the core data types and schema structures that form
the foundation of our relational database system. The design prioritizes
simplicity and correctness over completeness, making it interview-ready.
"""

from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass


class ColumnType(Enum):
    """Supported column types in our RDBMS."""
    INT = "INT"
    VARCHAR = "VARCHAR" 
    BOOLEAN = "BOOLEAN"


@dataclass
class ColumnDefinition:
    """Defines a column in a table schema."""
    name: str
    type: ColumnType
    primary_key: bool = False
    unique: bool = False
    nullable: bool = True
    max_length: Optional[int] = None  # For VARCHAR
    
    def __post_init__(self):
        """Validate column definition after creation."""
        if self.type == ColumnType.VARCHAR and self.max_length is None:
            # Default reasonable limit for VARCHAR
            self.max_length = 255
            
        if self.primary_key and self.nullable:
            # Primary keys cannot be null
            self.nullable = False
            
        if self.primary_key and not self.unique:
            # Primary keys are inherently unique
            self.unique = True


@dataclass
class Schema:
    """Table schema containing column definitions."""
    name: str
    columns: Dict[str, ColumnDefinition]
    
    def __post_init__(self):
        """Validate schema after creation."""
        if not self.columns:
            raise ValueError("Schema must have at least one column")
            
        # Check for exactly one primary key
        primary_keys = [col for col in self.columns.values() if col.primary_key]
        if len(primary_keys) > 1:
            raise ValueError("Schema can have at most one primary key")
    
    def get_primary_key_column(self) -> Optional[str]:
        """Return the name of the primary key column, or None if none exists."""
        for name, col_def in self.columns.items():
            if col_def.primary_key:
                return name
        return None
    
    def get_column_names(self) -> List[str]:
        """Return list of column names in definition order."""
        return list(self.columns.keys())
    
    def validate_row(self, row: Dict[str, Any]) -> None:
        """
        Validate a row against this schema.
        
        Args:
            row: Dictionary mapping column names to values
            
        Raises:
            ValueError: If row violates schema constraints
        """
        # Check for required columns
        for col_name, col_def in self.columns.items():
            if col_name not in row and not col_def.nullable:
                raise ValueError(f"Required column '{col_name}' is missing")
        
        # Check for extra columns
        for col_name in row:
            if col_name not in self.columns:
                raise ValueError(f"Unknown column '{col_name}'")
        
        # Validate each column value
        for col_name, col_def in self.columns.items():
            value = row.get(col_name)
            
            # Skip validation for missing nullable columns
            if value is None and col_def.nullable:
                continue
                
            # Type validation
            if not self._validate_column_type(value, col_def):
                raise ValueError(
                    f"Invalid value for column '{col_name}': "
                    f"expected {col_def.type.value}, got {type(value).__name__}"
                )
    
    def _validate_column_type(self, value: Any, col_def: ColumnDefinition) -> bool:
        """Validate a value against its column type definition."""
        if value is None:
            return col_def.nullable
            
        if col_def.type == ColumnType.INT:
            return isinstance(value, int)
        elif col_def.type == ColumnType.BOOLEAN:
            return isinstance(value, bool)
        elif col_def.type == ColumnType.VARCHAR:
            if not isinstance(value, str):
                return False
            if col_def.max_length and len(value) > col_def.max_length:
                return False
            return True
        
        return False
    
    def coerce_value(self, value: Any, col_def: ColumnDefinition) -> Any:
        """
        Coerce a value to the appropriate column type.
        
        Args:
            value: The value to coerce
            col_def: The column definition to coerce against
            
        Returns:
            The coerced value
            
        Raises:
            ValueError: If coercion is not possible
        """
        if value is None:
            if col_def.nullable:
                return None
            else:
                raise ValueError("Cannot coerce None to non-nullable column")
        
        # Try to convert string inputs to appropriate types
        if isinstance(value, str):
            if col_def.type == ColumnType.INT:
                try:
                    return int(value)
                except ValueError:
                    raise ValueError(f"Cannot convert '{value}' to INT")
            elif col_def.type == ColumnType.BOOLEAN:
                lower_val = value.lower()
                if lower_val in ('true', '1', 'yes', 'on'):
                    return True
                elif lower_val in ('false', '0', 'no', 'off'):
                    return False
                else:
                    raise ValueError(f"Cannot convert '{value}' to BOOLEAN")
            elif col_def.type == ColumnType.VARCHAR:
                if col_def.max_length and len(value) > col_def.max_length:
                    raise ValueError(f"String too long: max {col_def.max_length}")
                return value
        
        # For non-string inputs, check if they match the expected type
        if col_def.type == ColumnType.INT and isinstance(value, int):
            return value
        elif col_def.type == ColumnType.BOOLEAN and isinstance(value, bool):
            return value
        elif col_def.type == ColumnType.VARCHAR and isinstance(value, str):
            if col_def.max_length and len(value) > col_def.max_length:
                raise ValueError(f"String too long: max {col_def.max_length}")
            return value
        
        raise ValueError(f"Cannot coerce {type(value).__name__} to {col_def.type.value}")


def create_schema(name: str, column_defs: List[Dict[str, Any]]) -> Schema:
    """
    Factory function to create a Schema from a list of column definitions.
    
    Args:
        name: Table name
        column_defs: List of column definition dictionaries
        
    Returns:
        A Schema object
        
    Example:
        schema = create_schema("users", [
            {"name": "id", "type": "INT", "primary_key": True},
            {"name": "name", "type": "VARCHAR", "max_length": 100},
            {"name": "active", "type": "BOOLEAN", "nullable": False}
        ])
    """
    columns = {}
    
    for col_def in column_defs:
        # Convert string type to enum
        if isinstance(col_def["type"], str):
            col_type = ColumnType(col_def["type"].upper())
        else:
            col_type = col_def["type"]
        
        columns[col_def["name"]] = ColumnDefinition(
            name=col_def["name"],
            type=col_type,
            primary_key=col_def.get("primary_key", False),
            unique=col_def.get("unique", False),
            nullable=col_def.get("nullable", True),
            max_length=col_def.get("max_length")
        )
    
    return Schema(name=name, columns=columns)

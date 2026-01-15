"""
SQL parser for the custom RDBMS.

This module implements a simple SQL parser that handles basic SQL syntax
for CREATE TABLE, INSERT, SELECT, UPDATE, DELETE, and JOIN operations.
The parser is intentionally simple for clarity and interview-readiness.
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class CreateTableStatement:
    """Represents a CREATE TABLE SQL statement."""
    table_name: str
    columns: List[Dict[str, Any]]


@dataclass
class InsertStatement:
    """Represents an INSERT SQL statement."""
    table_name: str
    columns: List[str]
    values: List[List[Any]]


@dataclass
class SelectStatement:
    """Represents a SELECT SQL statement."""
    table_name: str
    columns: List[str]  # * or list of column names
    where_clause: Optional[str] = None
    join_clause: Optional[Dict[str, Any]] = None


@dataclass
class UpdateStatement:
    """Represents an UPDATE SQL statement."""
    table_name: str
    set_clause: Dict[str, Any]
    where_clause: Optional[str] = None


@dataclass
class DeleteStatement:
    """Represents a DELETE SQL statement."""
    table_name: str
    where_clause: Optional[str] = None


@dataclass
class JoinClause:
    """Represents a JOIN clause."""
    join_type: str  # INNER, LEFT, RIGHT, etc.
    right_table: str
    left_column: str
    right_column: str


# Union type for all statement types
SQLStatement = Union[
    CreateTableStatement,
    InsertStatement,
    SelectStatement,
    UpdateStatement,
    DeleteStatement
]


class SQLParser:
    """
    Simple SQL parser for basic operations.
    
    This parser handles a subset of SQL sufficient for the challenge requirements.
    It uses regular expressions for simplicity rather than building a full parser.
    """
    
    def __init__(self):
        """Initialize the parser."""
        # Pattern for matching quoted strings (single or double quotes)
        self.string_pattern = r'\'([^\']*)\'|"([^"]*)"'
        # Pattern for matching numbers
        self.number_pattern = r'\b\d+\b'
        # Pattern for matching boolean values
        self.boolean_pattern = r'\b(TRUE|FALSE|true|false)\b'
    
    def parse(self, sql: str) -> SQLStatement:
        """
        Parse a SQL statement into a structured representation.
        
        Args:
            sql: The SQL statement to parse
            
        Returns:
            A structured statement object
            
        Raises:
            ValueError: If the SQL cannot be parsed
        """
        sql = sql.strip()
        
        if sql.upper().startswith('CREATE TABLE'):
            return self._parse_create_table(sql)
        elif sql.upper().startswith('INSERT INTO'):
            return self._parse_insert(sql)
        elif sql.upper().startswith('SELECT'):
            return self._parse_select(sql)
        elif sql.upper().startswith('UPDATE'):
            return self._parse_update(sql)
        elif sql.upper().startswith('DELETE FROM'):
            return self._parse_delete(sql)
        else:
            raise ValueError(f"Unsupported SQL statement: {sql}")
    
    def _parse_create_table(self, sql: str) -> CreateTableStatement:
        """Parse CREATE TABLE statement."""
        pattern = r'CREATE\s+TABLE\s+(\w+)\s*\(\s*(.+?)\s*\)$'
        match = re.match(pattern, sql, re.IGNORECASE | re.DOTALL)
        
        if not match:
            raise ValueError(f"Invalid CREATE TABLE syntax: {sql}")
        
        table_name = match.group(1)
        columns_text = match.group(2)
        
        # Parse column definitions
        columns = self._parse_column_definitions(columns_text)
        
        return CreateTableStatement(table_name=table_name, columns=columns)
    
    def _parse_column_definitions(self, columns_text: str) -> List[Dict[str, Any]]:
        """Parse column definitions from CREATE TABLE statement."""
        columns = []
        
        # Split by comma, but handle nested parentheses
        column_defs = []
        paren_level = 0
        current_def = ""
        
        for char in columns_text:
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            elif char == ',' and paren_level == 0:
                if current_def.strip():
                    column_defs.append(current_def.strip())
                current_def = ""
                continue
            
            current_def += char
        
        if current_def.strip():
            column_defs.append(current_def.strip())
        
        for col_def in column_defs:
            column = self._parse_single_column_definition(col_def)
            columns.append(column)
        
        return columns
    
    def _parse_single_column_definition(self, col_def: str) -> Dict[str, Any]:
        """Parse a single column definition."""
        col_def = col_def.strip()
        
        # Basic pattern: name type [constraints...]
        parts = col_def.split()
        if len(parts) < 2:
            raise ValueError(f"Invalid column definition: {col_def}")
        
        name = parts[0]
        type_text = parts[1].upper()
        
        # Parse type
        column = {"name": name}
        
        if type_text == 'INT':
            column["type"] = "INT"
        elif type_text.startswith('VARCHAR'):
            # VARCHAR(255) -> VARCHAR with max_length
            match = re.match(r'VARCHAR\((\d+)\)', type_text)
            if match:
                column["type"] = "VARCHAR"
                column["max_length"] = int(match.group(1))
            else:
                column["type"] = "VARCHAR"
        elif type_text == 'BOOLEAN':
            column["type"] = "BOOLEAN"
        else:
            raise ValueError(f"Unsupported column type: {type_text}")
        
        # Parse constraints
        for part in parts[2:]:
            part_upper = part.upper()
            if part_upper == 'PRIMARY_KEY' or part_upper == 'PRIMARY KEY':
                column["primary_key"] = True
            elif part_upper == 'UNIQUE':
                column["unique"] = True
            elif part_upper == 'NOT_NULL' or part_upper == 'NOT NULL':
                column["nullable"] = False
            elif part_upper == 'NULL':
                column["nullable"] = True
        
        return column
    
    def _parse_insert(self, sql: str) -> InsertStatement:
        """Parse INSERT INTO statement."""
        # Handle INSERT INTO table (col1, col2) VALUES (val1, val2)
        pattern = r'INSERT\s+INTO\s+(\w+)(?:\s*\(\s*([^)]+)\s*\))?\s*VALUES\s+(.+)$'
        match = re.match(pattern, sql, re.IGNORECASE)
        
        if not match:
            raise ValueError(f"Invalid INSERT syntax: {sql}")
        
        table_name = match.group(1)
        columns_text = match.group(2)
        values_text = match.group(3)
        
        # Parse column names
        columns = []
        if columns_text:
            columns = [col.strip() for col in columns_text.split(',')]
        
        # Parse values (handle multiple value sets)
        values = self._parse_values(values_text)
        
        return InsertStatement(table_name=table_name, columns=columns, values=values)
    
    def _parse_values(self, values_text: str) -> List[List[Any]]:
        """Parse VALUES clause, handling multiple value sets."""
        values = []
        
        # Split by comma, but handle parentheses
        value_sets = []
        paren_level = 0
        current_set = ""
        
        for char in values_text:
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            elif char == ',' and paren_level == 0:
                if current_set.strip():
                    value_sets.append(current_set.strip())
                current_set = ""
                continue
            
            current_set += char
        
        if current_set.strip():
            value_sets.append(current_set.strip())
        
        # Parse each value set
        for value_set in value_sets:
            # Remove surrounding parentheses
            value_set = value_set.strip()
            if value_set.startswith('(') and value_set.endswith(')'):
                value_set = value_set[1:-1]
            
            # Parse individual values
            row_values = self._parse_value_list(value_set)
            values.append(row_values)
        
        return values
    
    def _parse_value_list(self, value_text: str) -> List[Any]:
        """Parse a comma-separated list of values."""
        values = []
        
        # Split by comma, but handle quoted strings
        parts = []
        in_quotes = False
        quote_char = None
        current_part = ""
        
        for char in value_text:
            if not in_quotes and char in ('"', "'"):
                in_quotes = True
                quote_char = char
                current_part += char
            elif in_quotes and char == quote_char:
                in_quotes = False
                quote_char = None
                current_part += char
            elif not in_quotes and char == ',':
                if current_part.strip():
                    parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        # Convert each part to appropriate type
        for part in parts:
            values.append(self._convert_value(part))
        
        return values
    
    def _convert_value(self, value: str) -> Any:
        """Convert a string value to appropriate Python type."""
        value = value.strip()
        
        # Handle quoted strings
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            return value[1:-1]  # Remove quotes
        
        # Handle numbers
        if re.match(r'^\d+$', value):
            return int(value)
        
        # Handle booleans
        if value.upper() in ('TRUE', 'FALSE'):
            return value.upper() == 'TRUE'
        
        # Handle NULL
        if value.upper() == 'NULL':
            return None
        
        # Default to string
        return value
    
    def _parse_select(self, sql: str) -> SelectStatement:
        """Parse SELECT statement."""
        # Basic SELECT pattern
        pattern = r'SELECT\s+(.+?)\s+FROM\s+(\w+)(?:\s+(.+))?$'
        match = re.match(pattern, sql, re.IGNORECASE)
        
        if not match:
            raise ValueError(f"Invalid SELECT syntax: {sql}")
        
        columns_text = match.group(1)
        table_name = match.group(2)
        remaining = match.group(3)
        
        # Parse columns
        if columns_text.strip() == '*':
            columns = ['*']
        else:
            columns = [col.strip() for col in columns_text.split(',')]
        
        # Parse WHERE and JOIN clauses
        where_clause = None
        join_clause = None
        
        if remaining:
            remaining = remaining.strip()
            
            # Check for JOIN first
            if 'JOIN' in remaining.upper():
                join_clause = self._parse_join_clause(remaining)
                # Remove JOIN part to check for WHERE
                remaining = re.sub(r'\s+(INNER\s+JOIN|JOIN)\s+.+?(?:\s+ON\s+.+)?$', '', remaining, flags=re.IGNORECASE).strip()
            
            # Check for WHERE
            if remaining.upper().startswith('WHERE'):
                where_clause = remaining[5:].strip()  # Remove 'WHERE'
        
        return SelectStatement(
            table_name=table_name,
            columns=columns,
            where_clause=where_clause,
            join_clause=join_clause
        )
    
    def _parse_join_clause(self, join_text: str) -> Dict[str, Any]:
        """Parse JOIN clause."""
        # Pattern: INNER JOIN table2 ON table1.col1 = table2.col2
        pattern = r'(?:INNER\s+)?JOIN\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
        match = re.search(pattern, join_text, re.IGNORECASE)
        
        if not match:
            raise ValueError(f"Invalid JOIN syntax: {join_text}")
        
        return {
            "type": "INNER",
            "right_table": match.group(1),
            "left_table": match.group(2),
            "left_column": match.group(3),
            "right_column": match.group(5)
        }
    
    def _parse_update(self, sql: str) -> UpdateStatement:
        """Parse UPDATE statement."""
        pattern = r'UPDATE\s+(\w+)\s+SET\s+(.+?)(?:\s+WHERE\s+(.+))?$'
        match = re.match(pattern, sql, re.IGNORECASE)
        
        if not match:
            raise ValueError(f"Invalid UPDATE syntax: {sql}")
        
        table_name = match.group(1)
        set_clause = match.group(2)
        where_clause = match.group(3)
        
        # Parse SET clause
        set_dict = self._parse_set_clause(set_clause)
        
        return UpdateStatement(
            table_name=table_name,
            set_clause=set_dict,
            where_clause=where_clause
        )
    
    def _parse_set_clause(self, set_text: str) -> Dict[str, Any]:
        """Parse SET clause from UPDATE statement."""
        set_dict = {}
        
        # Split by comma, but handle quoted strings
        assignments = []
        in_quotes = False
        quote_char = None
        current_assignment = ""
        
        for char in set_text:
            if not in_quotes and char in ('"', "'"):
                in_quotes = True
                quote_char = char
                current_assignment += char
            elif in_quotes and char == quote_char:
                in_quotes = False
                quote_char = None
                current_assignment += char
            elif not in_quotes and char == ',':
                if current_assignment.strip():
                    assignments.append(current_assignment.strip())
                current_assignment = ""
            else:
                current_assignment += char
        
        if current_assignment.strip():
            assignments.append(current_assignment.strip())
        
        # Parse each assignment (col = value)
        for assignment in assignments:
            if '=' not in assignment:
                raise ValueError(f"Invalid assignment: {assignment}")
            
            col, value = assignment.split('=', 1)
            col = col.strip()
            value = self._convert_value(value.strip())
            set_dict[col] = value
        
        return set_dict
    
    def _parse_delete(self, sql: str) -> DeleteStatement:
        """Parse DELETE statement."""
        pattern = r'DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?$'
        match = re.match(pattern, sql, re.IGNORECASE)
        
        if not match:
            raise ValueError(f"Invalid DELETE syntax: {sql}")
        
        table_name = match.group(1)
        where_clause = match.group(2)
        
        return DeleteStatement(table_name=table_name, where_clause=where_clause)

"""
SQL execution engine for the custom RDBMS.

This module implements the execution engine that takes parsed SQL statements
and executes them against the database. It bridges the parser and the database
layers.
"""

from typing import Any, Callable, Dict, List, Optional, Union
from ..parser.sql_parser import (
    SQLParser, SQLStatement, CreateTableStatement, InsertStatement,
    SelectStatement, UpdateStatement, DeleteStatement
)
from .database import Database
from .row import Row


class ExecutionEngine:
    """
    Executes SQL statements against the database.
    
    This engine takes parsed SQL statements and executes the appropriate
    database operations. It handles type conversion, constraint enforcement,
    and result formatting.
    """
    
    def __init__(self, database: Database):
        """
        Initialize the execution engine.
        
        Args:
            database: The database instance to execute against
        """
        self.database = database
        self.parser = SQLParser()
    
    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """
        Execute a SQL statement and return results.
        
        Args:
            sql: The SQL statement to execute
            
        Returns:
            Dictionary with execution results
            
        Raises:
            ValueError: If SQL execution fails
        """
        try:
            # Parse the SQL statement
            statement = self.parser.parse(sql)
            
            # Execute based on statement type
            if isinstance(statement, CreateTableStatement):
                return self._execute_create_table(statement)
            elif isinstance(statement, InsertStatement):
                return self._execute_insert(statement)
            elif isinstance(statement, SelectStatement):
                return self._execute_select(statement)
            elif isinstance(statement, UpdateStatement):
                return self._execute_update(statement)
            elif isinstance(statement, DeleteStatement):
                return self._execute_delete(statement)
            else:
                raise ValueError(f"Unsupported statement type: {type(statement)}")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "statement": sql
            }
    
    def _execute_create_table(self, stmt: CreateTableStatement) -> Dict[str, Any]:
        """Execute CREATE TABLE statement."""
        try:
            table = self.database.create_table(stmt.table_name, stmt.columns)
            
            return {
                "success": True,
                "message": f"Table '{stmt.table_name}' created successfully",
                "table_info": self.database.get_table_info(stmt.table_name)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "statement": f"CREATE TABLE {stmt.table_name}"
            }
    
    def _execute_insert(self, stmt: InsertStatement) -> Dict[str, Any]:
        """Execute INSERT statement."""
        try:
            inserted_rows = []
            
            for values in stmt.values:
                # Map values to column names
                if stmt.columns:
                    if len(stmt.columns) != len(values):
                        raise ValueError(f"Column count mismatch: {len(stmt.columns)} columns, {len(values)} values")
                    
                    row_data = dict(zip(stmt.columns, values))
                else:
                    # If no columns specified, assume all columns in order
                    table = self.database.get_table(stmt.table_name)
                    column_names = table.schema.get_column_names()
                    
                    if len(column_names) != len(values):
                        raise ValueError(f"Column count mismatch: table has {len(column_names)} columns, got {len(values)} values")
                    
                    row_data = dict(zip(column_names, values))
                
                # Insert the row
                row = self.database.insert(stmt.table_name, row_data)
                inserted_rows.append(row.to_dict())
            
            return {
                "success": True,
                "message": f"Inserted {len(inserted_rows)} row(s) into '{stmt.table_name}'",
                "inserted_rows": inserted_rows
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "statement": f"INSERT INTO {stmt.table_name}"
            }
    
    def _execute_select(self, stmt: SelectStatement) -> Dict[str, Any]:
        """Execute SELECT statement."""
        try:
            # Handle JOIN if present
            if stmt.join_clause:
                return self._execute_select_with_join(stmt)
            
            # Get base rows
            if stmt.where_clause:
                # Parse WHERE clause and create condition function
                condition_func = self._parse_where_clause(stmt.where_clause)
                rows = self.database.select_where(stmt.table_name, condition_func)
            else:
                rows = self.database.select_all(stmt.table_name)
            
            # Project columns
            if stmt.columns == ['*']:
                # Select all columns
                result_rows = [row.to_dict() for row in rows]
            else:
                # Select specific columns
                result_rows = []
                for row in rows:
                    row_dict = {}
                    for col in stmt.columns:
                        if col in row:
                            row_dict[col] = row[col]
                    result_rows.append(row_dict)
            
            return {
                "success": True,
                "message": f"Selected {len(result_rows)} row(s) from '{stmt.table_name}'",
                "rows": result_rows,
                "column_count": len(result_rows[0]) if result_rows else 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "statement": f"SELECT FROM {stmt.table_name}"
            }
    
    def _execute_select_with_join(self, stmt: SelectStatement) -> Dict[str, Any]:
        """Execute SELECT with JOIN."""
        try:
            join_info = stmt.join_clause
            
            # Perform the join
            joined_rows = self.database.join_inner(
                stmt.table_name,
                join_info["right_table"],
                join_info["left_column"],
                join_info["right_column"]
            )
            
            # Apply WHERE clause if present
            if stmt.where_clause:
                # For joined queries, we need to modify the WHERE clause
                # to handle qualified column names
                condition_func = self._parse_where_clause_for_joined(stmt.where_clause)
                joined_rows = [row for row in joined_rows if condition_func(row)]
            
            # Project columns
            if stmt.columns == ['*']:
                result_rows = joined_rows
            else:
                # Handle column selection with qualified names
                result_rows = []
                for row in joined_rows:
                    row_dict = {}
                    for col in stmt.columns:
                        if '.' in col:
                            # Qualified column name
                            if col in row:
                                row_dict[col] = row[col]
                        else:
                            # Unqualified column name - search in both tables
                            left_col = f"{stmt.table_name}.{col}"
                            right_col = f"{join_info['right_table']}.{col}"
                            if left_col in row:
                                row_dict[col] = row[left_col]
                            elif right_col in row:
                                row_dict[col] = row[right_col]
                    result_rows.append(row_dict)
            
            return {
                "success": True,
                "message": f"Selected {len(result_rows)} row(s) from joined tables",
                "rows": result_rows,
                "column_count": len(result_rows[0]) if result_rows else 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "statement": f"SELECT FROM {stmt.table_name} JOIN {stmt.join_clause['right_table']}"
            }
    
    def _execute_update(self, stmt: UpdateStatement) -> Dict[str, Any]:
        """Execute UPDATE statement."""
        try:
            # Parse WHERE clause if present
            if stmt.where_clause:
                condition_func = self._parse_where_clause(stmt.where_clause)
                updated_count = self.database.update_where(stmt.table_name, condition_func, stmt.set_clause)
            else:
                # Update all rows (create condition that always returns True)
                condition_func = lambda row: True
                updated_count = self.database.update_where(stmt.table_name, condition_func, stmt.set_clause)
            
            return {
                "success": True,
                "message": f"Updated {updated_count} row(s) in '{stmt.table_name}'",
                "updated_count": updated_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "statement": f"UPDATE {stmt.table_name}"
            }
    
    def _execute_delete(self, stmt: DeleteStatement) -> Dict[str, Any]:
        """Execute DELETE statement."""
        try:
            # Parse WHERE clause if present
            if stmt.where_clause:
                condition_func = self._parse_where_clause(stmt.where_clause)
                deleted_count = self.database.delete_where(stmt.table_name, condition_func)
            else:
                # Delete all rows (create condition that always returns True)
                condition_func = lambda row: True
                deleted_count = self.database.delete_where(stmt.table_name, condition_func)
            
            return {
                "success": True,
                "message": f"Deleted {deleted_count} row(s) from '{stmt.table_name}'",
                "deleted_count": deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "statement": f"DELETE FROM {stmt.table_name}"
            }
    
    def _parse_where_clause(self, where_clause: str) -> Callable[[Row], bool]:
        """
        Parse a WHERE clause into a condition function.
        
        This is a simplified parser that handles basic conditions.
        For the challenge, we'll support basic equality and comparison operations.
        """
        where_clause = where_clause.strip()
        
        # Handle simple equality: column = value
        if '=' in where_clause:
            left, right = where_clause.split('=', 1)
            column = left.strip()
            value = self._convert_value(right.strip())
            
            def condition(row: Row) -> bool:
                return row.get(column) == value
            
            return condition
        
        # Handle basic comparisons
        elif '!=' in where_clause:
            left, right = where_clause.split('!=', 1)
            column = left.strip()
            value = self._convert_value(right.strip())
            
            def condition(row: Row) -> bool:
                return row.get(column) != value
        
        elif '>' in where_clause:
            left, right = where_clause.split('>', 1)
            column = left.strip()
            value = self._convert_value(right.strip())
            
            def condition(row: Row) -> bool:
                return row.get(column) > value
        
        elif '<' in where_clause:
            left, right = where_clause.split('<', 1)
            column = left.strip()
            value = self._convert_value(right.strip())
            
            def condition(row: Row) -> bool:
                return row.get(column) < value
        
        else:
            raise ValueError(f"Unsupported WHERE clause: {where_clause}")
    
    def _parse_where_clause_for_joined(self, where_clause: str) -> Callable[[Dict[str, Any]], bool]:
        """
        Parse WHERE clause for joined queries (handles qualified column names).
        """
        where_clause = where_clause.strip()
        
        # Handle simple equality with potential qualified column names
        if '=' in where_clause:
            left, right = where_clause.split('=', 1)
            left_col = left.strip()
            right_val = self._convert_value(right.strip())
            
            def condition(row: Dict[str, Any]) -> bool:
                return row.get(left_col) == right_val
            
            return condition
        
        elif '!=' in where_clause:
            left, right = where_clause.split('!=', 1)
            left_col = left.strip()
            right_val = self._convert_value(right.strip())
            
            def condition(row: Dict[str, Any]) -> bool:
                return row.get(left_col) != right_val
        
        elif '>' in where_clause:
            left, right = where_clause.split('>', 1)
            left_col = left.strip()
            right_val = self._convert_value(right.strip())
            
            def condition(row: Dict[str, Any]) -> bool:
                return row.get(left_col) > right_val
        
        elif '<' in where_clause:
            left, right = where_clause.split('<', 1)
            left_col = left.strip()
            right_val = self._convert_value(right.strip())
            
            def condition(row: Dict[str, Any]) -> bool:
                return row.get(left_col) < right_val
        
        else:
            raise ValueError(f"Unsupported WHERE clause: {where_clause}")
    
    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate Python type."""
        value = value.strip()
        
        # Handle quoted strings
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            return value[1:-1]  # Remove quotes
        
        # Handle numbers
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Handle booleans
        if value.upper() in ('TRUE', 'FALSE'):
            return value.upper() == 'TRUE'
        
        # Handle NULL
        if value.upper() == 'NULL':
            return None
        
        # Default to string
        return value

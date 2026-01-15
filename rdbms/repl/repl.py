"""
Interactive REPL for the custom RDBMS.

This module provides a command-line interface for interacting with the database
using SQL-like commands. It's designed to be simple and interview-ready.
"""

import sys
import json
from typing import Optional
from ..engine.database import Database
from ..engine.executor import ExecutionEngine
from ..storage.memory_store import MemoryStore


class RDBMSREPL:
    """
    Interactive Read-Eval-Print Loop for the RDBMS.
    
    Provides a simple command-line interface for executing SQL commands
    and managing the database. Supports basic SQL operations and provides
    helpful feedback and error messages.
    """
    
    def __init__(self, persist_file: Optional[str] = None):
        """
        Initialize the REPL.
        
        Args:
            persist_file: Optional file for JSON persistence
        """
        self.database = Database("pesapal_rdbms")
        self.executor = ExecutionEngine(self.database)
        self.storage = MemoryStore(persist_file) if persist_file else None
        
        # Load any persisted data
        if self.storage:
            self._load_from_storage()
        
        self.running = True
        self.echo_commands = True
    
    def _load_from_storage(self) -> None:
        """Load database state from storage."""
        if not self.storage:
            return
        
        # Load table schemas
        schemas_data = self.storage.get("table_schemas", {})
        for table_name, schema_data in schemas_data.items():
            try:
                self.database.create_table(table_name, schema_data["columns"])
            except Exception as e:
                print(f"Warning: Failed to restore table '{table_name}': {e}")
        
        # Load table data
        tables_data = self.storage.get("table_data", {})
        for table_name, rows_data in tables_data.items():
            try:
                if self.database.table_exists(table_name):
                    table = self.database.get_table(table_name)
                    for row_data in rows_data:
                        table.insert(row_data)
            except Exception as e:
                print(f"Warning: Failed to restore data for table '{table_name}': {e}")
    
    def _save_to_storage(self) -> None:
        """Save database state to storage."""
        if not self.storage:
            return
        
        # Save table schemas
        schemas_data = {}
        tables_data = {}
        
        for table_name in self.database.list_tables():
            table_info = self.database.get_table_info(table_name)
            schemas_data[table_name] = {
                "columns": [
                    {
                        "name": col["name"],
                        "type": col["type"],
                        "primary_key": col["primary_key"],
                        "unique": col["unique"],
                        "nullable": col["nullable"],
                        "max_length": col["max_length"]
                    }
                    for col in table_info["columns"]
                ]
            }
            
            # Save table data
            rows = self.database.select_all(table_name)
            tables_data[table_name] = [row.to_dict() for row in rows]
        
        self.storage.set("table_schemas", schemas_data)
        self.storage.set("table_data", tables_data)
    
    def start(self) -> None:
        """Start the interactive REPL."""
        print("=== Pesapal RDBMS Interactive Shell ===")
        print("Type 'help' for available commands or 'exit' to quit.")
        print()
        
        while self.running:
            try:
                # Get user input
                command = input("rdbms> ").strip()
                
                # Skip empty commands
                if not command:
                    continue
                
                # Handle special commands
                if command.lower() in ('exit', 'quit'):
                    self._handle_exit()
                elif command.lower() == 'help':
                    self._show_help()
                elif command.lower() == 'tables':
                    self._show_tables()
                elif command.lower() == 'schema':
                    self._show_schema_command()
                elif command.lower().startswith('schema '):
                    table_name = command[7:].strip()
                    self._show_table_schema(table_name)
                elif command.lower() == 'save':
                    self._handle_save()
                elif command.lower() == 'clear':
                    self._handle_clear()
                elif command.lower() == 'stats':
                    self._show_stats()
                else:
                    # Execute SQL command
                    self._execute_command(command)
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit.")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _execute_command(self, command: str) -> None:
        """Execute a SQL command and display results."""
        if self.echo_commands:
            print(f"Executing: {command}")
        
        result = self.executor.execute_sql(command)
        
        if result["success"]:
            print(f"✓ {result['message']}")
            
            # Display rows for SELECT queries
            if "rows" in result and result["rows"]:
                self._display_rows(result["rows"])
            
            # Display detailed info for CREATE TABLE
            if "table_info" in result:
                self._display_table_info(result["table_info"])
                
        else:
            print(f"✗ Error: {result['error']}")
        
        print()
    
    def _display_rows(self, rows: list) -> None:
        """Display query results in a formatted table."""
        if not rows:
            print("No rows returned.")
            return
        
        # Get column names and calculate widths
        if isinstance(rows[0], dict):
            columns = list(rows[0].keys())
            widths = {col: max(len(str(col)), max(len(str(row.get(col, ""))) for row in rows)) for col in columns}
            
            # Print header
            header = " | ".join(str(col).ljust(widths[col]) for col in columns)
            print(header)
            print("-" * len(header))
            
            # Print rows
            for row in rows:
                row_str = " | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns)
                print(row_str)
        
        print(f"({len(rows)} rows)")
    
    def _display_table_info(self, table_info: dict) -> None:
        """Display table schema information."""
        print(f"\nTable: {table_info['name']}")
        print(f"Rows: {table_info['row_count']}")
        print("Columns:")
        
        for col in table_info['columns']:
            constraints = []
            if col['primary_key']:
                constraints.append('PRIMARY KEY')
            if col['unique']:
                constraints.append('UNIQUE')
            if not col['nullable']:
                constraints.append('NOT NULL')
            
            type_str = col['type']
            if col['max_length']:
                type_str += f"({col['max_length']})"
            
            constraint_str = f" {' '.join(constraints)}" if constraints else ""
            print(f"  {col['name']}: {type_str}{constraint_str}")
    
    def _show_help(self) -> None:
        """Display help information."""
        help_text = """
Available Commands:
==================

SQL Commands:
  CREATE TABLE table_name (col1 TYPE [constraints], ...)
  INSERT INTO table_name (col1, col2) VALUES (val1, val2)
  SELECT * FROM table_name [WHERE condition]
  SELECT col1, col2 FROM table_name [WHERE condition]
  UPDATE table_name SET col1 = val1, col2 = val2 [WHERE condition]
  DELETE FROM table_name [WHERE condition]
  SELECT * FROM table1 INNER JOIN table2 ON table1.col1 = table2.col2

Special Commands:
  help          - Show this help
  tables        - List all tables
  schema [table] - Show schema for all tables or specific table
  save          - Save database to file
  clear         - Clear all data from database
  stats         - Show database statistics
  exit/quit     - Exit the REPL

Data Types:
  INT           - Integer values
  VARCHAR(n)    - String values with max length n
  BOOLEAN       - True/False values

Constraints:
  PRIMARY KEY   - Unique, non-null identifier
  UNIQUE        - All values must be unique
  NOT NULL      - Column cannot be null
  NULL          - Column can be null (default)

Examples:
  CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), active BOOLEAN)
  INSERT INTO users (id, name, active) VALUES (1, 'Alice', TRUE)
  SELECT * FROM users WHERE active = TRUE
  UPDATE users SET active = FALSE WHERE id = 1
  DELETE FROM users WHERE active = FALSE
        """
        print(help_text)
    
    def _show_tables(self) -> None:
        """List all tables in the database."""
        tables = self.database.list_tables()
        if not tables:
            print("No tables exist.")
        else:
            print("Tables:")
            for table_name in tables:
                table = self.database.get_table(table_name)
                print(f"  {table_name} ({table.count()} rows)")
        print()
    
    def _show_schema_command(self) -> None:
        """Show schema for all tables."""
        tables = self.database.list_tables()
        if not tables:
            print("No tables exist.")
        else:
            for table_name in tables:
                table_info = self.database.get_table_info(table_name)
                self._display_table_info(table_info)
                print()
    
    def _show_table_schema(self, table_name: str) -> None:
        """Show schema for a specific table."""
        try:
            table_info = self.database.get_table_info(table_name)
            self._display_table_info(table_info)
            print()
        except ValueError as e:
            print(f"Error: {e}")
            print()
    
    def _show_stats(self) -> None:
        """Show database statistics."""
        db_info = self.database.get_database_info()
        
        print(f"Database: {db_info['name']}")
        print(f"Tables: {db_info['table_count']}")
        print(f"Total rows: {sum(table['row_count'] for table in db_info['tables'])}")
        
        if self.storage:
            storage_stats = self.storage.get_stats()
            print(f"Storage: {storage_stats['persist_file']}")
            print(f"Storage loaded: {storage_stats['loaded']}")
        
        print()
    
    def _handle_save(self) -> None:
        """Handle save command."""
        if self.storage:
            self._save_to_storage()
            print("Database saved to storage.")
        else:
            print("No persistence configured.")
        print()
    
    def _handle_clear(self) -> None:
        """Handle clear command."""
        confirm = input("Are you sure you want to clear all data? (yes/no): ").strip().lower()
        if confirm == 'yes':
            self.database.clear_all_tables()
            print("All data cleared.")
        else:
            print("Operation cancelled.")
        print()
    
    def _handle_exit(self) -> None:
        """Handle exit command."""
        if self.storage:
            self._save_to_storage()
            print("Database saved to storage.")
        print("Goodbye!")
        self.running = False


def main(persist_file: Optional[str] = None) -> None:
    """
    Main entry point for the REPL.
    
    Args:
        persist_file: Optional file for JSON persistence
    """
    repl = RDBMSREPL(persist_file)
    repl.start()


if __name__ == "__main__":
    # Check if persistence file was provided as command line argument
    persist_file = None
    if len(sys.argv) > 1:
        persist_file = sys.argv[1]
    
    main(persist_file)

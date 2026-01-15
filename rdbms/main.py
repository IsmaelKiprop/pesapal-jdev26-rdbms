"""
Main entry point for the Pesapal RDBMS.

This module provides the main entry point for running the RDBMS either
as an interactive REPL or as a library for use in other applications.
"""

import sys
import argparse
from .repl.repl import main as repl_main
from .engine.database import Database
from .engine.executor import ExecutionEngine


def create_database(name: str = "pesapal_rdbms") -> tuple[Database, ExecutionEngine]:
    """
    Create a new database instance with execution engine.
    
    Args:
        name: Name for the database
        
    Returns:
        Tuple of (Database, ExecutionEngine)
    """
    database = Database(name)
    executor = ExecutionEngine(database)
    return database, executor


def main() -> None:
    """Main entry point for the RDBMS application."""
    parser = argparse.ArgumentParser(
        description="Pesapal RDBMS - A minimal relational database management system"
    )
    parser.add_argument(
        "--persist", 
        type=str, 
        help="JSON file for data persistence"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="Pesapal RDBMS 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Start the REPL
    repl_main(args.persist)


if __name__ == "__main__":
    main()

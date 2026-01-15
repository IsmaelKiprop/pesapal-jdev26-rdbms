"""
Interactive REPL for the custom RDBMS.

This package contains the interactive command-line interface
for executing SQL commands and managing the database.
"""

from .repl import RDBMSREPL, main

__all__ = [
    "RDBMSREPL",
    "main"
]

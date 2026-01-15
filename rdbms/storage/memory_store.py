"""
Memory storage implementation for the custom RDBMS.

This module provides in-memory storage capabilities with optional JSON persistence.
The storage layer is abstracted to allow for future extensions (file-based, etc.).
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime


class MemoryStore:
    """
    In-memory storage with optional JSON persistence.
    
    This class provides a simple key-value store that can be persisted to JSON files.
    It's designed to be lightweight and interview-ready while maintaining data integrity.
    """
    
    def __init__(self, persist_file: Optional[str] = None):
        """
        Initialize the memory store.
        
        Args:
            persist_file: Optional JSON file path for persistence
        """
        self._data: Dict[str, Any] = {}
        self._persist_file = persist_file
        self._loaded = False
        
        if persist_file and os.path.exists(persist_file):
            self.load()
    
    def set(self, key: str, value: Any) -> None:
        """
        Store a value with the given key.
        
        Args:
            key: Storage key
            value: Value to store (must be JSON serializable)
        """
        self._data[key] = value
        if self._persist_file:
            self._save()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value by key.
        
        Args:
            key: Storage key
            default: Default value if key doesn't exist
            
        Returns:
            The stored value or default
        """
        return self._data.get(key, default)
    
    def delete(self, key: str) -> bool:
        """
        Delete a key-value pair.
        
        Args:
            key: Storage key to delete
            
        Returns:
            True if key was deleted, False if it didn't exist
        """
        if key in self._data:
            del self._data[key]
            if self._persist_file:
                self._save()
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        return key in self._data
    
    def keys(self) -> List[str]:
        """Return all keys in the store."""
        return list(self._data.keys())
    
    def clear(self) -> None:
        """Clear all data from the store."""
        self._data.clear()
        if self._persist_file:
            self._save()
    
    def size(self) -> int:
        """Return the number of stored items."""
        return len(self._data)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple key-value pairs at once.
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        self._data.update(updates)
        if self._persist_file:
            self._save()
    
    def _save(self) -> None:
        """Save data to JSON file."""
        if not self._persist_file:
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self._persist_file), exist_ok=True)
            
            # Prepare data for serialization
            serializable_data = {
                "metadata": {
                    "saved_at": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "data": self._data
            }
            
            with open(self._persist_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            # In a production system, we'd want better error handling
            print(f"Warning: Failed to save data to {self._persist_file}: {e}")
    
    def load(self) -> bool:
        """
        Load data from JSON file.
        
        Returns:
            True if data was loaded successfully, False otherwise
        """
        if not self._persist_file or not os.path.exists(self._persist_file):
            return False
        
        try:
            with open(self._persist_file, 'r', encoding='utf-8') as f:
                serializable_data = json.load(f)
            
            # Validate structure
            if not isinstance(serializable_data, dict) or "data" not in serializable_data:
                raise ValueError("Invalid file format")
            
            self._data = serializable_data["data"]
            self._loaded = True
            return True
            
        except Exception as e:
            print(f"Warning: Failed to load data from {self._persist_file}: {e}")
            return False
    
    def backup(self, backup_file: str) -> bool:
        """
        Create a backup of the current data.
        
        Args:
            backup_file: Path for the backup file
            
        Returns:
            True if backup was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            
            # Prepare data for serialization
            serializable_data = {
                "metadata": {
                    "backed_up_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "original_file": self._persist_file
                },
                "data": self._data
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Warning: Failed to create backup at {backup_file}: {e}")
            return False
    
    def restore(self, backup_file: str) -> bool:
        """
        Restore data from a backup file.
        
        Args:
            backup_file: Path to the backup file
            
        Returns:
            True if restore was successful, False otherwise
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                serializable_data = json.load(f)
            
            # Validate structure
            if not isinstance(serializable_data, dict) or "data" not in serializable_data:
                raise ValueError("Invalid backup file format")
            
            self._data = serializable_data["data"]
            
            # Save to main persistence file if configured
            if self._persist_file:
                self._save()
            
            return True
            
        except Exception as e:
            print(f"Warning: Failed to restore from {backup_file}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the store.
        
        Returns:
            Dictionary with store statistics
        """
        return {
            "item_count": len(self._data),
            "keys": list(self._data.keys()),
            "persist_file": self._persist_file,
            "loaded": self._loaded,
            "last_modified": datetime.now().isoformat()
        }
    
    def __str__(self) -> str:
        """String representation of the store."""
        return f"MemoryStore({len(self._data)} items, persist_file={self._persist_file})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the store."""
        return f"MemoryStore(items={len(self._data)}, keys={list(self._data.keys())[:5]}, persist_file='{self._persist_file}')"

"""
File-based storage backend for AgentMem.
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID

import joblib


class FileStorage:
    """
    File-based storage backend for memories.
    
    This class provides persistence by storing memories as files on disk,
    either as JSON or pickled objects (for more complex data structures).
    """
    
    def __init__(self, storage_dir: str, serialization_format: str = "json"):
        """
        Initialize file storage.
        
        Args:
            storage_dir: Directory to store memory files
            serialization_format: Format to use for storage ('json' or 'pickle')
        """
        self.storage_dir = Path(storage_dir)
        self.serialization_format = serialization_format.lower()
        
        if self.serialization_format not in ["json", "pickle"]:
            raise ValueError("Serialization format must be 'json' or 'pickle'")
        
        # Create storage directory if it doesn't exist
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different memory types
        self.semantic_dir = self.storage_dir / "semantic"
        self.episodic_dir = self.storage_dir / "episodic"
        self.procedural_dir = self.storage_dir / "procedural"
        
        for directory in [self.semantic_dir, self.episodic_dir, self.procedural_dir]:
            directory.mkdir(exist_ok=True)
        
        # Create index files to track stored memories
        self._initialize_indices()
    
    def _initialize_indices(self) -> None:
        """Initialize indices to track stored memories."""
        self.indices = {
            "semantic": set(),
            "episodic": set(),
            "procedural": set()
        }
        
        # Load existing indices if they exist
        for memory_type, index_set in self.indices.items():
            index_path = self.storage_dir / f"{memory_type}_index.json"
            if index_path.exists():
                with open(index_path, "r") as f:
                    self.indices[memory_type] = set(json.load(f))
    
    def _save_index(self, memory_type: str) -> None:
        """Save the index for a memory type."""
        index_path = self.storage_dir / f"{memory_type}_index.json"
        with open(index_path, "w") as f:
            json.dump(list(self.indices[memory_type]), f)
    
    def _get_path(self, memory_id: UUID, memory_type: str) -> Path:
        """Get the file path for a memory ID."""
        id_str = str(memory_id)
        if memory_type == "semantic":
            return self.semantic_dir / f"{id_str}.{self.serialization_format}"
        elif memory_type == "episodic":
            return self.episodic_dir / f"{id_str}.{self.serialization_format}"
        elif memory_type == "procedural":
            return self.procedural_dir / f"{id_str}.{self.serialization_format}"
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
    
    def save(self, memory_id: UUID, data: Dict[str, Any], memory_type: str) -> None:
        """
        Save memory data to a file.
        
        Args:
            memory_id: UUID of the memory
            data: Memory data to save
            memory_type: Type of memory ('semantic', 'episodic', or 'procedural')
        """
        if memory_type not in ["semantic", "episodic", "procedural"]:
            raise ValueError(f"Invalid memory type: {memory_type}")
        
        file_path = self._get_path(memory_id, memory_type)
        
        # Handle datetime objects for JSON serialization
        if self.serialization_format == "json":
            data_copy = {}
            for key, value in data.items():
                if isinstance(value, datetime):
                    data_copy[key] = value.isoformat()
                elif isinstance(value, UUID):
                    data_copy[key] = str(value)
                else:
                    data_copy[key] = value
            
            with open(file_path, "w") as f:
                json.dump(data_copy, f, indent=2)
        else:  # pickle format
            joblib.dump(data, file_path)
        
        # Update index
        self.indices[memory_type].add(str(memory_id))
        self._save_index(memory_type)
    
    def load(self, memory_id: UUID, memory_type: str) -> Dict[str, Any]:
        """
        Load memory data from a file.
        
        Args:
            memory_id: UUID of the memory
            memory_type: Type of memory ('semantic', 'episodic', or 'procedural')
            
        Returns:
            Dict[str, Any]: The loaded memory data
            
        Raises:
            FileNotFoundError: If memory file doesn't exist
        """
        if memory_type not in ["semantic", "episodic", "procedural"]:
            raise ValueError(f"Invalid memory type: {memory_type}")
        
        file_path = self._get_path(memory_id, memory_type)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Memory file not found: {file_path}")
        
        if self.serialization_format == "json":
            with open(file_path, "r") as f:
                data = json.load(f)
                
            # Convert string dates back to datetime if needed
            if memory_type == "episodic" and "timestamp" in data and isinstance(data["timestamp"], str):
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])
            
            # Convert string IDs back to UUID
            if "id" in data and isinstance(data["id"], str):
                data["id"] = UUID(data["id"])
                
            if "created_at" in data and isinstance(data["created_at"], str):
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                
            if "updated_at" in data and isinstance(data["updated_at"], str):
                data["updated_at"] = datetime.fromisoformat(data["updated_at"])
                
            return data
        else:  # pickle format
            return joblib.load(file_path)
    
    def delete(self, memory_id: UUID, memory_type: str) -> None:
        """
        Delete a memory file.
        
        Args:
            memory_id: UUID of the memory
            memory_type: Type of memory ('semantic', 'episodic', or 'procedural')
            
        Raises:
            FileNotFoundError: If memory file doesn't exist
        """
        if memory_type not in ["semantic", "episodic", "procedural"]:
            raise ValueError(f"Invalid memory type: {memory_type}")
        
        file_path = self._get_path(memory_id, memory_type)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Memory file not found: {file_path}")
        
        file_path.unlink()
        
        # Update index
        try:
            self.indices[memory_type].remove(str(memory_id))
            self._save_index(memory_type)
        except KeyError:
            pass  # Memory ID not in index
    
    def list_all(self, memory_type: str) -> List[UUID]:
        """
        List all memory IDs of a specific type.
        
        Args:
            memory_type: Type of memory ('semantic', 'episodic', or 'procedural')
            
        Returns:
            List[UUID]: List of memory IDs
        """
        if memory_type not in ["semantic", "episodic", "procedural"]:
            raise ValueError(f"Invalid memory type: {memory_type}")
        
        return [UUID(id_str) for id_str in self.indices[memory_type]]
    
    def clear_all(self, memory_type: Optional[str] = None) -> None:
        """
        Clear all memories, optionally of a specific type.
        
        Args:
            memory_type: Type of memory to clear (if None, clear all)
        """
        if memory_type is None:
            # Clear all memory types
            for dir_name in ["semantic", "episodic", "procedural"]:
                dir_path = self.storage_dir / dir_name
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                dir_path.mkdir(exist_ok=True)
                self.indices[dir_name] = set()
                self._save_index(dir_name)
        else:
            if memory_type not in ["semantic", "episodic", "procedural"]:
                raise ValueError(f"Invalid memory type: {memory_type}")
            
            dir_path = self.storage_dir / memory_type
            if dir_path.exists():
                shutil.rmtree(dir_path)
            dir_path.mkdir(exist_ok=True)
            self.indices[memory_type] = set()
            self._save_index(memory_type)
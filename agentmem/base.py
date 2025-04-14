"""
Base Memory classes for AgentMem.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

import warnings
import os

from agentmem.concurrency import lock_manager
from agentmem.storage.file_storage import FileStorage

# Import logging components (with warnings suppressed)
with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    try:
        from agentmem.logging import (
            get_logger,
            track_operation,
            OperationType,
            get_metrics_collector,
            get_memory_tracker,
            estimate_size
        )
        LOGGING_AVAILABLE = True
    except (ImportError, ValueError):
        # Create dummy logging functions if logging module is not available
        LOGGING_AVAILABLE = False
        
        def get_logger(name):
            class DummyLogger:
                def debug(self, *args, **kwargs): pass
                def info(self, *args, **kwargs): pass
                def warning(self, *args, **kwargs): pass
                def error(self, *args, **kwargs): pass
                def critical(self, *args, **kwargs): pass
            return DummyLogger()
        
        class OperationType:
            CREATE = "create"
            READ = "read"
            UPDATE = "update"
            DELETE = "delete"
            QUERY = "query"
            VECTOR_QUERY = "vector_query"
            SAVE = "save"
            LOAD = "load"
            CLEAR = "clear"
            
        def track_operation(operation, memory_type, details=None):
            class DummyContextManager:
                def __enter__(self): pass
                def __exit__(self, *args): pass
            return DummyContextManager()
            
        def get_metrics_collector(): return None
        def get_memory_tracker(): return None
        def estimate_size(obj): return 0

# Conditionally import VectorStorage with all warnings suppressed

# Set a flag to track vector search availability
VECTOR_SEARCH_AVAILABLE = False

# Suppress warnings during import
with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    try:
        # Direct import to avoid storage/__init__.py
        import agentmem.storage.vector_storage
        from agentmem.storage.vector_storage import VectorStorage
        VECTOR_SEARCH_AVAILABLE = True
    except (ImportError, TypeError, ValueError) as e:
        # Create a dummy VectorStorage class that raises informative errors
        class VectorStorage:
            def __init__(self, *args, **kwargs):
                raise ImportError(
                    "Vector storage is not available due to compatibility issues with your Python environment. "
                    "Try installing a compatible version of sentence-transformers and chromadb, "
                    "or use in-memory or file storage instead."
                )


class Memory(ABC):
    """
    Abstract base class for all memory types.
    
    Provides common interface and functionality for different memory implementations.
    """
    
    def __init__(
        self,
        persistence: Optional[str] = None,
        vector_search: bool = False,
        vector_db_path: Optional[str] = None,
        memory_type: str = None
    ):
        """
        Initialize the memory store.
        
        Args:
            persistence: Path to directory for persistent storage (None for in-memory only)
            vector_search: Whether to enable vector-based semantic search
            vector_db_path: Path to vector database (defaults to persistence path if None)
            memory_type: Type of memory ('semantic', 'episodic', or 'procedural')
        """
        # Initialize logger
        self.logger = get_logger(f"agentmem.{memory_type or 'memory'}")
        self.logger.info(f"Initializing {memory_type or 'memory'} store")
        
        # Initialize memory tracker and metrics
        if LOGGING_AVAILABLE:
            self._memory_tracker = get_memory_tracker()
            self._metrics = get_metrics_collector()
            
            # Register memory size tracker
            def get_memory_size():
                return estimate_size(self._storage)
            
            if memory_type:
                self._memory_tracker.register_memory_source(memory_type, get_memory_size)
        
        # Initialize in-memory storage
        self._storage = {}
        
        # Type of memory (set by subclasses)
        self._memory_type = memory_type
        
        # Set up persistence if requested
        self._persistence = None
        if persistence:
            self.logger.info(f"Setting up persistence at {persistence}")
            self._persistence = FileStorage(persistence)
        
        # Set up vector search if requested
        self._vector_search = None
        if vector_search:
            try:
                vector_path = vector_db_path or persistence or "./vector_db"
                self.logger.info(f"Setting up vector search at {vector_path}")
                
                if VECTOR_SEARCH_AVAILABLE:
                    self._vector_search = VectorStorage(vector_path)
                else:
                    # Only warn if vector search was explicitly requested
                    import warnings
                    warning_msg = (
                        "Vector search was requested but is not available due to compatibility issues. "
                        "Using standard search instead."
                    )
                    warnings.warn(warning_msg)
                    self.logger.warning(warning_msg)
            except (ImportError, TypeError) as e:
                error_msg = f"Could not initialize vector search: {str(e)}. Using standard search instead."
                import warnings
                warnings.warn(error_msg)
                self.logger.error(error_msg)
    
    def _save_to_persistence(self, memory_id: UUID, data: Dict[str, Any]) -> None:
        """Save memory to persistent storage if enabled."""
        if self._persistence and self._memory_type:
            with track_operation(OperationType.SAVE, self._memory_type, {'id': str(memory_id)}):
                with lock_manager.memory_id_lock(memory_id):
                    self._persistence.save(memory_id, data, self._memory_type)
                    self.logger.debug(f"Saved {self._memory_type} memory {memory_id} to persistence")
    
    def _load_from_persistence(self, memory_id: UUID) -> Dict[str, Any]:
        """Load memory from persistent storage if enabled."""
        if self._persistence and self._memory_type:
            with track_operation(OperationType.LOAD, self._memory_type, {'id': str(memory_id)}):
                with lock_manager.memory_id_lock(memory_id):
                    data = self._persistence.load(memory_id, self._memory_type)
                    self.logger.debug(f"Loaded {self._memory_type} memory {memory_id} from persistence")
                    return data
        error_msg = f"Memory with ID {memory_id} not found in persistence"
        self.logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    def _delete_from_persistence(self, memory_id: UUID) -> None:
        """Delete memory from persistent storage if enabled."""
        if self._persistence and self._memory_type:
            with track_operation(OperationType.DELETE, self._memory_type, {'id': str(memory_id)}):
                with lock_manager.memory_id_lock(memory_id):
                    self._persistence.delete(memory_id, self._memory_type)
                    self.logger.debug(f"Deleted {self._memory_type} memory {memory_id} from persistence")
    
    def _add_to_vector_search(self, memory_id: UUID, content: str, metadata: Dict[str, Any]) -> None:
        """Add memory to vector search if enabled."""
        if self._vector_search and self._memory_type:
            with track_operation(OperationType.CREATE, self._memory_type, {
                'id': str(memory_id),
                'vector_search': True
            }):
                with lock_manager.memory_id_lock(memory_id):
                    self._vector_search.add(memory_id, content, self._memory_type, metadata)
                    self.logger.debug(f"Added {self._memory_type} memory {memory_id} to vector search")
    
    def _remove_from_vector_search(self, memory_id: UUID) -> None:
        """Remove memory from vector search if enabled."""
        if self._vector_search and self._memory_type:
            with track_operation(OperationType.DELETE, self._memory_type, {
                'id': str(memory_id),
                'vector_search': True
            }):
                with lock_manager.memory_id_lock(memory_id):
                    self._vector_search.remove(memory_id, self._memory_type)
                    self.logger.debug(f"Removed {self._memory_type} memory {memory_id} from vector search")
    
    def _semantic_search(
        self,
        query: str,
        n_results: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[UUID, float]]:
        """
        Perform semantic search using vector database if enabled.
        
        Args:
            query: Query text to search for
            n_results: Maximum number of results to return
            metadata_filter: Filter by metadata fields
            
        Returns:
            List[Tuple[UUID, float]]: List of (memory_id, similarity) tuples
        """
        if self._vector_search and self._memory_type:
            with track_operation(OperationType.VECTOR_QUERY, self._memory_type, {
                'query': query,
                'n_results': n_results,
                'has_filter': metadata_filter is not None
            }):
                with lock_manager.memory_type_lock(self._memory_type):
                    results = self._vector_search.query(
                        query, self._memory_type, n_results, metadata_filter
                    )
                    self.logger.debug(
                        f"Vector search for '{query}' returned {len(results)} results "
                        f"from {self._memory_type} memory"
                    )
                    return results
        return []
    
    def save_all(self) -> None:
        """
        Save all memories to persistent storage.
        
        This ensures all in-memory data is synchronized with persistent storage.
        """
        if not self._persistence or not self._memory_type:
            return
        
        self.logger.info(f"Saving all {self._memory_type} memories to persistence")
        with track_operation(OperationType.SAVE, self._memory_type, {'operation': 'save_all'}):
            with lock_manager.memory_type_lock(self._memory_type):
                count = 0
                for memory_id, entry in self._storage.items():
                    memory_dict = self._entry_to_dict(entry)
                    # Use a transaction for atomic operations
                    with lock_manager.transaction(memory_ids={memory_id}):
                        self._save_to_persistence(memory_id, memory_dict)
                        count += 1
                
                self.logger.info(f"Saved {count} {self._memory_type} memories to persistence")
                
                # Update memory usage metrics
                if LOGGING_AVAILABLE:
                    self._memory_tracker.update_memory_usage(self._memory_type, force=True)
    
    def load_all(self) -> None:
        """
        Load all memories from persistent storage.
        
        This replaces in-memory data with data from persistent storage.
        """
        if not self._persistence or not self._memory_type:
            return
        
        self.logger.info(f"Loading all {self._memory_type} memories from persistence")
        with track_operation(OperationType.LOAD, self._memory_type, {'operation': 'load_all'}):
            with lock_manager.memory_type_lock(self._memory_type):
                # Clear in-memory storage
                self._storage = {}
                
                # Get all memory IDs from persistence
                memory_ids = self._persistence.list_all(self._memory_type)
                
                # Load each memory
                count = 0
                for memory_id in memory_ids:
                    with lock_manager.memory_id_lock(memory_id):
                        data = self._persistence.load(memory_id, self._memory_type)
                        entry = self._dict_to_entry(data)
                        self._storage[memory_id] = entry
                        count += 1
                
                self.logger.info(f"Loaded {count} {self._memory_type} memories from persistence")
                
                # Update memory usage metrics
                if LOGGING_AVAILABLE:
                    self._memory_tracker.update_memory_usage(self._memory_type, force=True)
    
    def clear_all(self) -> None:
        """
        Clear all memories from all storage backends.
        """
        if not self._memory_type:
            return
        
        self.logger.info(f"Clearing all {self._memory_type} memories from all storage backends")
        with track_operation(OperationType.CLEAR, self._memory_type, {'operation': 'clear_all'}):    
            with lock_manager.memory_type_lock(self._memory_type):
                # Count memories before clearing
                count = len(self._storage)
                
                # Clear in-memory storage
                self._storage = {}
                
                # Clear persistence if enabled
                if self._persistence:
                    self._persistence.clear_all(self._memory_type)
                
                # Clear vector search if enabled
                if self._vector_search:
                    self._vector_search.clear_all(self._memory_type)
                
                self.logger.info(f"Cleared {count} {self._memory_type} memories")
                
                # Update memory usage metrics
                if LOGGING_AVAILABLE:
                    self._memory_tracker.update_memory_usage(self._memory_type, force=True)
    
    @abstractmethod
    def create(self, content: Any, **kwargs) -> UUID:
        """
        Create a new memory entry.
        
        Args:
            content: The content to store in memory
            **kwargs: Additional metadata for the memory entry
            
        Returns:
            UUID: Unique identifier for the created memory
        """
        pass
    
    @abstractmethod
    def read(self, memory_id: UUID) -> Dict[str, Any]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: UUID of the memory to retrieve
            
        Returns:
            Dict[str, Any]: The memory entry
            
        Raises:
            KeyError: If memory_id doesn't exist
        """
        pass
    
    @abstractmethod
    def update(self, memory_id: UUID, content: Any, **kwargs) -> None:
        """
        Update an existing memory entry.
        
        Args:
            memory_id: UUID of the memory to update
            content: New content for the memory
            **kwargs: Additional metadata to update
            
        Raises:
            KeyError: If memory_id doesn't exist
        """
        pass
    
    @abstractmethod
    def delete(self, memory_id: UUID) -> None:
        """
        Delete a memory entry.
        
        Args:
            memory_id: UUID of the memory to delete
            
        Raises:
            KeyError: If memory_id doesn't exist
        """
        pass
    
    @abstractmethod
    def query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search memory based on a query.
        
        Args:
            query: The search query
            **kwargs: Additional search parameters
            
        Returns:
            List[Dict[str, Any]]: List of matching memory entries
        """
        pass
    
    @abstractmethod
    def _entry_to_dict(self, entry) -> Dict[str, Any]:
        """Convert memory entry to dictionary for storage."""
        pass
    
    @abstractmethod
    def _dict_to_entry(self, data: Dict[str, Any]):
        """Convert dictionary to memory entry."""
        pass


class MemoryEntry:
    """Base class for memory entries with common metadata."""
    
    def __init__(self, content: Any, **kwargs):
        """
        Initialize a new memory entry.
        
        Args:
            content: The content to store
            **kwargs: Additional metadata
        """
        self.id = kwargs.get("id", uuid4())
        self.content = content
        self.created_at = kwargs.get("created_at", datetime.now())
        self.updated_at = kwargs.get("updated_at", self.created_at)
        self.metadata = kwargs.get("metadata", {})
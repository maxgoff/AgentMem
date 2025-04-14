"""
Implementation of episodic memory for storing experience-based memories.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from agentmem.base import Memory, MemoryEntry


class EpisodicMemoryEntry(MemoryEntry):
    """Entry in episodic memory representing a specific event or experience."""
    
    def __init__(self, content: Any, **kwargs):
        """
        Initialize an episodic memory entry.
        
        Args:
            content: The event content to store
            **kwargs: Additional metadata including:
                - timestamp: When the event occurred (defaults to now)
                - context: Additional contextual information
                - importance: Subjective importance of the memory (1-10)
        """
        super().__init__(content, **kwargs)
        self.timestamp = kwargs.get("timestamp", datetime.now())
        self.context = kwargs.get("context", {})
        self.importance = kwargs.get("importance", 5)


class EpisodicMemory(Memory):
    """
    Episodic memory for storing experience-based memories.
    
    Episodic memory stores specific events and experiences tied to particular
    points in time. This is where an agent would store memories like
    "The user asked about file handling last week" or "I helped debug a
    recursive function yesterday".
    """
    
    def __init__(
        self,
        persistence: Optional[str] = None,
        vector_search: bool = False,
        vector_db_path: Optional[str] = None
    ):
        """
        Initialize a new episodic memory store.
        
        Args:
            persistence: Path to directory for persistent storage (None for in-memory only)
            vector_search: Whether to enable vector-based semantic search
            vector_db_path: Path to vector database (defaults to persistence path if None)
        """
        super().__init__(
            persistence=persistence,
            vector_search=vector_search,
            vector_db_path=vector_db_path,
            memory_type="episodic"
        )
        
        # Load data from persistence if available
        if persistence:
            self.load_all()
    
    def create(self, content: Any, **kwargs) -> UUID:
        """
        Create a new episodic memory entry.
        
        Args:
            content: The event content to store
            **kwargs: Additional metadata including:
                - timestamp: When the event occurred (defaults to now)
                - context: Additional contextual information
                - importance: Subjective importance (1-10)
                
        Returns:
            UUID: Unique identifier for the created memory
        """
        from agentmem.concurrency import lock_manager
        
        entry = EpisodicMemoryEntry(content, **kwargs)
        memory_id = entry.id
        
        # Use a transaction to ensure atomicity
        with lock_manager.transaction(memory_type=self._memory_type, memory_ids={memory_id}):
            # Add to in-memory storage
            self._storage[memory_id] = entry
            
            # Save to persistence if enabled
            if self._persistence:
                self._save_to_persistence(memory_id, self._entry_to_dict(entry))
            
            # Add to vector search if enabled
            if self._vector_search:
                # Prepare metadata for vector search
                timestamp_str = entry.timestamp.isoformat() if entry.timestamp else datetime.now().isoformat()
                context_str = str(entry.context) if entry.context else ""
                
                metadata = {
                    "importance": entry.importance,
                    "timestamp": timestamp_str,
                    "context_summary": context_str[:100] if len(context_str) > 100 else context_str,
                    "created_at": entry.created_at.isoformat()
                }
                
                self._add_to_vector_search(memory_id, str(content), metadata)
        
        return memory_id
    
    def read(self, memory_id: UUID) -> Dict[str, Any]:
        """
        Retrieve a specific episodic memory by ID.
        
        Args:
            memory_id: UUID of the memory to retrieve
            
        Returns:
            Dict[str, Any]: The memory entry
            
        Raises:
            KeyError: If memory_id doesn't exist
        """
        from agentmem.concurrency import lock_manager
        
        # Use a lock to ensure thread safety
        with lock_manager.memory_id_lock(memory_id):
            # Try in-memory storage first
            if memory_id in self._storage:
                entry = self._storage[memory_id]
                return self._entry_to_dict(entry)
            
            # Try persistence if enabled
            if self._persistence:
                try:
                    data = self._load_from_persistence(memory_id)
                    # Cache in memory
                    self._storage[memory_id] = self._dict_to_entry(data)
                    return data
                except FileNotFoundError:
                    pass
            
            raise KeyError(f"Memory with ID {memory_id} not found")
    
    def update(self, memory_id: UUID, content: Any = None, **kwargs) -> None:
        """
        Update an existing episodic memory entry.
        
        Args:
            memory_id: UUID of the memory to update
            content: New content for the memory (if None, content is not updated)
            **kwargs: Additional metadata to update including:
                - context: Updated contextual information
                - importance: Updated importance rating
                
        Raises:
            KeyError: If memory_id doesn't exist
        """
        from agentmem.concurrency import lock_manager
        
        # Use a transaction to ensure atomicity
        with lock_manager.memory_id_lock(memory_id):
            # Ensure memory exists
            if memory_id not in self._storage:
                if self._persistence:
                    try:
                        data = self._load_from_persistence(memory_id)
                        self._storage[memory_id] = self._dict_to_entry(data)
                    except FileNotFoundError:
                        raise KeyError(f"Memory with ID {memory_id} not found")
                else:
                    raise KeyError(f"Memory with ID {memory_id} not found")
            
            entry = self._storage[memory_id]
            
            # Update entry
            if content is not None:
                entry.content = content
                
            if "context" in kwargs:
                entry.context.update(kwargs["context"])
                
            if "importance" in kwargs:
                entry.importance = kwargs["importance"]
                
            if "metadata" in kwargs:
                entry.metadata.update(kwargs["metadata"])
                
            entry.updated_at = datetime.now()
            
            # Save to persistence if enabled
            if self._persistence:
                self._save_to_persistence(memory_id, self._entry_to_dict(entry))
            
            # Update vector search if enabled and content changed
            if self._vector_search and (content is not None or "context" in kwargs):
                # Prepare metadata for vector search
                timestamp_str = entry.timestamp.isoformat() if entry.timestamp else datetime.now().isoformat()
                context_str = str(entry.context) if entry.context else ""
                
                metadata = {
                    "importance": entry.importance,
                    "timestamp": timestamp_str,
                    "context_summary": context_str[:100] if len(context_str) > 100 else context_str,
                    "updated_at": entry.updated_at.isoformat()
                }
                
                self._add_to_vector_search(memory_id, str(entry.content), metadata)
    
    def delete(self, memory_id: UUID) -> None:
        """
        Delete an episodic memory entry.
        
        Args:
            memory_id: UUID of the memory to delete
            
        Raises:
            KeyError: If memory_id doesn't exist
        """
        from agentmem.concurrency import lock_manager
        
        # Use a transaction to ensure atomicity
        with lock_manager.memory_id_lock(memory_id):
            # Ensure memory exists
            if memory_id not in self._storage:
                if self._persistence:
                    try:
                        # Check if it exists in persistence
                        self._load_from_persistence(memory_id)
                    except FileNotFoundError:
                        raise KeyError(f"Memory with ID {memory_id} not found")
                else:
                    raise KeyError(f"Memory with ID {memory_id} not found")
            
            # Remove from in-memory storage
            if memory_id in self._storage:
                del self._storage[memory_id]
            
            # Remove from persistence if enabled
            if self._persistence:
                try:
                    self._delete_from_persistence(memory_id)
                except FileNotFoundError:
                    pass
            
            # Remove from vector search if enabled
            if self._vector_search:
                self._remove_from_vector_search(memory_id)
    
    def query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search episodic memory based on a query.
        
        Args:
            query: The search query
            **kwargs: Additional search parameters including:
                - start_time: Filter by earliest timestamp
                - end_time: Filter by latest timestamp
                - min_importance: Minimum importance level
                - context_keys: Required context keys
                - use_vector: Whether to use vector search (default: True if enabled)
                - n_results: Maximum number of results to return for vector search
                
        Returns:
            List[Dict[str, Any]]: List of matching memory entries
        """
        # Check for vector search
        use_vector = kwargs.get("use_vector", True)
        if self._vector_search and use_vector and query:
            return self._vector_query(query, **kwargs)
        else:
            return self._standard_query(query, **kwargs)
    
    def _standard_query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Perform a standard keyword-based query."""
        results = []
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")
        min_importance = kwargs.get("min_importance")
        context_keys = kwargs.get("context_keys", [])
        
        for memory_id, entry in self._storage.items():
            # Apply timestamp filters if specified
            if start_time and entry.timestamp < start_time:
                continue
                
            if end_time and entry.timestamp > end_time:
                continue
                
            # Apply importance filter if specified
            if min_importance is not None and entry.importance < min_importance:
                continue
                
            # Apply context key filter if specified
            if context_keys and not all(key in entry.context for key in context_keys):
                continue
                
            # Apply content search if query is provided
            if query:
                content_str = str(entry.content).lower()
                query_lower = query.lower()
                
                if query_lower in content_str:
                    results.append(self._entry_to_dict(entry))
            else:
                # If no query but filters match, include it
                results.append(self._entry_to_dict(entry))
        
        # Sort results by timestamp (most recent first)
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results
    
    def _vector_query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Perform a vector-based semantic search."""
        from agentmem.concurrency import lock_manager
        
        # Prepare metadata filter
        metadata_filter = {}
        
        if "min_importance" in kwargs:
            # Note: ChromaDB doesn't support range queries directly,
            # so we'll filter after getting results
            pass
            
        n_results = kwargs.get("n_results", 10)
        
        # Perform semantic search (already thread-safe from base class)
        matches = self._semantic_search(query, n_results, metadata_filter)
        
        if not matches:
            return []
        
        results = []
        with lock_manager.memory_type_lock(self._memory_type):
            for memory_id, score in matches:
                try:
                    # Get full memory data
                    memory_data = self.read(memory_id)
                    # Add score
                    memory_data["similarity_score"] = score
                    
                    # Apply additional filters that vector DB doesn't support
                    
                    # Timestamp filters
                    start_time = kwargs.get("start_time")
                    if start_time and memory_data["timestamp"] < start_time:
                        continue
                    
                    end_time = kwargs.get("end_time")
                    if end_time and memory_data["timestamp"] > end_time:
                        continue
                    
                    # Importance filter
                    min_importance = kwargs.get("min_importance")
                    if min_importance is not None and memory_data["importance"] < min_importance:
                        continue
                    
                    # Context keys filter
                    context_keys = kwargs.get("context_keys", [])
                    if context_keys and not all(key in memory_data["context"] for key in context_keys):
                        continue
                    
                    results.append(memory_data)
                except KeyError:
                    # Memory might have been deleted
                    continue
            
            # Sort results by timestamp (most recent first)
            results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results
        
    def query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search episodic memory based on a query.
        
        Args:
            query: The search query
            **kwargs: Additional search parameters including:
                - start_time: Filter by earliest timestamp
                - end_time: Filter by latest timestamp
                - min_importance: Minimum importance level
                - context_keys: Required context keys
                - use_vector: Whether to use vector search (default: True if enabled)
                - n_results: Maximum number of results to return for vector search
                
        Returns:
            List[Dict[str, Any]]: List of matching memory entries
        """
        from agentmem.concurrency import lock_manager
        
        # Use a memory type lock for the query operation
        with lock_manager.memory_type_lock(self._memory_type):
            # Check for vector search
            use_vector = kwargs.get("use_vector", True)
            if self._vector_search and use_vector and query:
                return self._vector_query(query, **kwargs)
            else:
                return self._standard_query(query, **kwargs)
    
    def _entry_to_dict(self, entry: EpisodicMemoryEntry) -> Dict[str, Any]:
        """Convert memory entry to dictionary for storage."""
        return {
            "id": entry.id,
            "content": entry.content,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
            "timestamp": entry.timestamp,
            "context": entry.context,
            "importance": entry.importance,
            "metadata": entry.metadata
        }
    
    def _dict_to_entry(self, data: Dict[str, Any]) -> EpisodicMemoryEntry:
        """Convert dictionary to memory entry."""
        return EpisodicMemoryEntry(
            content=data["content"],
            id=data["id"] if isinstance(data["id"], UUID) else UUID(data["id"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            timestamp=data["timestamp"],
            context=data["context"],
            importance=data["importance"],
            metadata=data["metadata"]
        )
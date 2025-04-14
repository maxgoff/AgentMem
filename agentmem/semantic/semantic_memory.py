"""
Implementation of semantic memory for storing factual knowledge.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from agentmem.base import Memory, MemoryEntry


class SemanticMemoryEntry(MemoryEntry):
    """Entry in semantic memory representing a fact or concept."""
    
    def __init__(self, content: Any, **kwargs):
        """
        Initialize a semantic memory entry.
        
        Args:
            content: The factual content to store
            **kwargs: Additional metadata including:
                - category: Optional categorization of the fact
                - tags: Optional list of tags for classification
        """
        super().__init__(content, **kwargs)
        self.category = kwargs.get("category", "general")
        self.tags = kwargs.get("tags", [])


class SemanticMemory(Memory):
    """
    Semantic memory for storing factual knowledge.
    
    Semantic memory stores general facts and concepts that are not tied
    to specific events or experiences. This is where an agent would store
    knowledge like "Paris is the capital of France" or "Python is a programming language".
    """
    
    def __init__(
        self,
        persistence: Optional[str] = None,
        vector_search: bool = False,
        vector_db_path: Optional[str] = None
    ):
        """
        Initialize a new semantic memory store.
        
        Args:
            persistence: Path to directory for persistent storage (None for in-memory only)
            vector_search: Whether to enable vector-based semantic search
            vector_db_path: Path to vector database (defaults to persistence path if None)
        """
        super().__init__(
            persistence=persistence,
            vector_search=vector_search,
            vector_db_path=vector_db_path,
            memory_type="semantic"
        )
        
        # Load data from persistence if available
        if persistence:
            self.load_all()
    
    def create(self, content: Any, **kwargs) -> UUID:
        """
        Create a new semantic memory entry.
        
        Args:
            content: The factual content to store
            **kwargs: Additional metadata including:
                - category: Optional categorization of the fact
                - tags: Optional list of tags for classification
                
        Returns:
            UUID: Unique identifier for the created memory
        """
        from agentmem.concurrency import lock_manager
        
        entry = SemanticMemoryEntry(content, **kwargs)
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
                metadata = {
                    "category": entry.category,
                    "tags": str(entry.tags),
                    "created_at": entry.created_at.isoformat()
                }
                self._add_to_vector_search(memory_id, str(content), metadata)
        
        return memory_id
    
    def read(self, memory_id: UUID) -> Dict[str, Any]:
        """
        Retrieve a specific semantic memory by ID.
        
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
        Update an existing semantic memory entry.
        
        Args:
            memory_id: UUID of the memory to update
            content: New content for the memory (if None, content is not updated)
            **kwargs: Additional metadata to update including:
                - category: Updated category
                - tags: Updated tags
                
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
                
            if "category" in kwargs:
                entry.category = kwargs["category"]
                
            if "tags" in kwargs:
                entry.tags = kwargs["tags"]
                
            if "metadata" in kwargs:
                entry.metadata.update(kwargs["metadata"])
                
            entry.updated_at = datetime.now()
            
            # Save to persistence if enabled
            if self._persistence:
                self._save_to_persistence(memory_id, self._entry_to_dict(entry))
            
            # Update vector search if enabled and content changed
            if self._vector_search and (content is not None or "category" in kwargs or "tags" in kwargs):
                metadata = {
                    "category": entry.category,
                    "tags": str(entry.tags),
                    "updated_at": entry.updated_at.isoformat()
                }
                self._add_to_vector_search(memory_id, str(entry.content), metadata)
    
    def delete(self, memory_id: UUID) -> None:
        """
        Delete a semantic memory entry.
        
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
        Search semantic memory based on a query.
        
        Args:
            query: The search query
            **kwargs: Additional search parameters including:
                - category: Filter by category
                - tags: Filter by one or more tags
                - exact_match: Whether to require exact match (default: False)
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
    
    def _standard_query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Perform a standard keyword-based query."""
        results = []
        category_filter = kwargs.get("category")
        tags_filter = kwargs.get("tags", [])
        exact_match = kwargs.get("exact_match", False)
        
        for memory_id, entry in self._storage.items():
            # Apply category filter if specified
            if category_filter and entry.category != category_filter:
                continue
                
            # Apply tags filter if specified
            if tags_filter and not all(tag in entry.tags for tag in tags_filter):
                continue
                
            # Apply content search if query is provided
            if query:
                content_str = str(entry.content).lower()
                query_lower = query.lower()
                
                if (exact_match and query_lower == content_str) or \
                   (not exact_match and query_lower in content_str):
                    results.append(self._entry_to_dict(entry))
            else:
                # If no query but filters match, include it
                results.append(self._entry_to_dict(entry))
                
        return results
    
    def _vector_query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Perform a vector-based semantic search."""
        # Prepare metadata filter
        metadata_filter = {}
        if "category" in kwargs:
            metadata_filter["category"] = kwargs["category"]
            
        n_results = kwargs.get("n_results", 10)
        
        # Perform semantic search
        matches = self._semantic_search(query, n_results, metadata_filter)
        
        if not matches:
            return []
        
        results = []
        for memory_id, score in matches:
            try:
                # Get full memory data
                memory_data = self.read(memory_id)
                # Add score
                memory_data["similarity_score"] = score
                
                # Check tag filter if specified
                tags_filter = kwargs.get("tags", [])
                if tags_filter and not all(tag in memory_data["tags"] for tag in tags_filter):
                    continue
                    
                results.append(memory_data)
            except KeyError:
                # Memory might have been deleted
                continue
        
        return results
    
    def _entry_to_dict(self, entry: SemanticMemoryEntry) -> Dict[str, Any]:
        """Convert memory entry to dictionary for storage."""
        return {
            "id": entry.id,
            "content": entry.content,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
            "category": entry.category,
            "tags": entry.tags,
            "metadata": entry.metadata
        }
    
    def _dict_to_entry(self, data: Dict[str, Any]) -> SemanticMemoryEntry:
        """Convert dictionary to memory entry."""
        return SemanticMemoryEntry(
            content=data["content"],
            id=data["id"] if isinstance(data["id"], UUID) else UUID(data["id"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            category=data["category"],
            tags=data["tags"],
            metadata=data["metadata"]
        )
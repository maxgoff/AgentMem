"""
Implementation of procedural memory for storing task-related knowledge.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from uuid import UUID

from agentmem.base import Memory, MemoryEntry


class ProceduralMemoryEntry(MemoryEntry):
    """Entry in procedural memory representing a skill or procedure."""
    
    def __init__(self, content: Any, **kwargs):
        """
        Initialize a procedural memory entry.
        
        Args:
            content: The procedure or skill content to store
            **kwargs: Additional metadata including:
                - task: The task this procedure accomplishes
                - steps: Sequence of steps in the procedure
                - prerequisites: Required conditions or resources
                - domains: Domains this procedure applies to
        """
        super().__init__(content, **kwargs)
        self.task = kwargs.get("task", "undefined")
        self.steps = kwargs.get("steps", [])
        self.prerequisites = kwargs.get("prerequisites", [])
        self.domains = kwargs.get("domains", ["general"])


class ProceduralMemory(Memory):
    """
    Procedural memory for storing task-related knowledge.
    
    Procedural memory stores knowledge about how to perform specific tasks
    or skills. This is where an agent would store knowledge like
    "How to create a file in Python" or "Steps to debug a recursive function".
    """
    
    def __init__(
        self,
        persistence: Optional[str] = None,
        vector_search: bool = False,
        vector_db_path: Optional[str] = None
    ):
        """
        Initialize a new procedural memory store.
        
        Args:
            persistence: Path to directory for persistent storage (None for in-memory only)
            vector_search: Whether to enable vector-based semantic search
            vector_db_path: Path to vector database (defaults to persistence path if None)
        """
        super().__init__(
            persistence=persistence,
            vector_search=vector_search,
            vector_db_path=vector_db_path,
            memory_type="procedural"
        )
        
        # Load data from persistence if available
        if persistence:
            self.load_all()
    
    def create(self, content: Any, **kwargs) -> UUID:
        """
        Create a new procedural memory entry.
        
        Args:
            content: The procedure or skill description
            **kwargs: Additional metadata including:
                - task: The task this procedure accomplishes
                - steps: Sequence of steps in the procedure
                - prerequisites: Required conditions or resources
                - domains: List of domains this procedure applies to
                
        Returns:
            UUID: Unique identifier for the created memory
        """
        from agentmem.concurrency import lock_manager
        
        entry = ProceduralMemoryEntry(content, **kwargs)
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
                # For procedural memory, combine task and steps into searchable text
                search_text = f"{content}\n{entry.task}\n" + "\n".join(entry.steps)
                
                # Prepare metadata for vector search
                metadata = {
                    "task": entry.task,
                    "domains": str(entry.domains),
                    "prerequisites": str(entry.prerequisites),
                    "steps_count": len(entry.steps),
                    "created_at": entry.created_at.isoformat()
                }
                
                self._add_to_vector_search(memory_id, search_text, metadata)
        
        return memory_id
    
    def read(self, memory_id: UUID) -> Dict[str, Any]:
        """
        Retrieve a specific procedural memory by ID.
        
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
        Update an existing procedural memory entry.
        
        Args:
            memory_id: UUID of the memory to update
            content: New content for the memory (if None, content is not updated)
            **kwargs: Additional metadata to update including:
                - task: Updated task description
                - steps: Updated sequence of steps
                - prerequisites: Updated prerequisites
                - domains: Updated list of applicable domains
                
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
            
            # Track if we need to update the vector search
            update_vector = False
            
            # Update entry
            if content is not None:
                entry.content = content
                update_vector = True
                
            if "task" in kwargs:
                entry.task = kwargs["task"]
                update_vector = True
                
            if "steps" in kwargs:
                entry.steps = kwargs["steps"]
                update_vector = True
                
            if "prerequisites" in kwargs:
                entry.prerequisites = kwargs["prerequisites"]
                update_vector = True
                
            if "domains" in kwargs:
                entry.domains = kwargs["domains"]
                update_vector = True
                
            if "metadata" in kwargs:
                entry.metadata.update(kwargs["metadata"])
                
            entry.updated_at = datetime.now()
            
            # Save to persistence if enabled
            if self._persistence:
                self._save_to_persistence(memory_id, self._entry_to_dict(entry))
            
            # Update vector search if enabled and content changed
            if self._vector_search and update_vector:
                # For procedural memory, combine task and steps into searchable text
                search_text = f"{entry.content}\n{entry.task}\n" + "\n".join(entry.steps)
                
                # Prepare metadata for vector search
                metadata = {
                    "task": entry.task,
                    "domains": str(entry.domains),
                    "prerequisites": str(entry.prerequisites),
                    "steps_count": len(entry.steps),
                    "updated_at": entry.updated_at.isoformat()
                }
                
                self._add_to_vector_search(memory_id, search_text, metadata)
    
    def delete(self, memory_id: UUID) -> None:
        """
        Delete a procedural memory entry.
        
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
        Search procedural memory based on a query.
        
        Args:
            query: The search query (task description or keywords)
            **kwargs: Additional search parameters including:
                - domain: Filter by specific domain
                - prerequisites: Filter by available prerequisites
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
        domain_filter = kwargs.get("domain")
        prereq_filter = kwargs.get("prerequisites", [])
        
        for memory_id, entry in self._storage.items():
            # Apply domain filter if specified
            if domain_filter and domain_filter not in entry.domains:
                continue
                
            # Apply prerequisites filter if specified
            if prereq_filter and not all(prereq in entry.prerequisites for prereq in prereq_filter):
                continue
                
            # Apply content search if query is provided
            if query:
                # Search in task, content, and steps
                task_match = query.lower() in entry.task.lower()
                content_match = query.lower() in str(entry.content).lower()
                steps_match = any(query.lower() in str(step).lower() for step in entry.steps)
                
                if task_match or content_match or steps_match:
                    results.append(self._entry_to_dict(entry))
            else:
                # If no query but filters match, include it
                results.append(self._entry_to_dict(entry))
                
        return results
    
    def _vector_query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Perform a vector-based semantic search."""
        from agentmem.concurrency import lock_manager
        
        # Prepare metadata filter
        metadata_filter = {}
        
        # Domain filter for vector search
        domain_filter = kwargs.get("domain")
        if domain_filter:
            # Note: ChromaDB doesn't support list membership queries directly,
            # so we'll filter the results after retrieval
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
                    
                    # Apply domain filter if specified
                    if domain_filter and domain_filter not in memory_data["domains"]:
                        continue
                    
                    # Apply prerequisites filter if specified
                    prereq_filter = kwargs.get("prerequisites", [])
                    if prereq_filter and not all(prereq in memory_data["prerequisites"] for prereq in prereq_filter):
                        continue
                    
                    results.append(memory_data)
                except KeyError:
                    # Memory might have been deleted
                    continue
        
        return results
    
    def _entry_to_dict(self, entry: ProceduralMemoryEntry) -> Dict[str, Any]:
        """Convert memory entry to dictionary for storage."""
        return {
            "id": entry.id,
            "content": entry.content,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
            "task": entry.task,
            "steps": entry.steps,
            "prerequisites": entry.prerequisites,
            "domains": entry.domains,
            "metadata": entry.metadata
        }
    
    def _dict_to_entry(self, data: Dict[str, Any]) -> ProceduralMemoryEntry:
        """Convert dictionary to memory entry."""
        return ProceduralMemoryEntry(
            content=data["content"],
            id=data["id"] if isinstance(data["id"], UUID) else UUID(data["id"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            task=data["task"],
            steps=data["steps"],
            prerequisites=data["prerequisites"],
            domains=data["domains"],
            metadata=data["metadata"]
        )
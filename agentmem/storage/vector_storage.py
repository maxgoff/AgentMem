"""
Vector database storage backend for AgentMem.

This module provides vector storage capabilities for semantic search.
"""
import os
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

# Disable posthog telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Temporarily suppress warnings for NumPy/torch imports
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    # Import chromadb with compatibility handling
    try:
        import chromadb
        import numpy as np
        from chromadb.config import Settings
    except TypeError:
        # This can happen with older Python versions and TypedDict compatibility issues
        import numpy as np
        import chromadb
        from chromadb.config import Settings
    
    # This import can cause NumPy 2.x compatibility warnings which we suppress
    from sentence_transformers import SentenceTransformer


class VectorStorage:
    """
    Vector database storage for semantic search capabilities.
    
    This class provides vector embedding and semantic search functionality
    using sentence transformers and ChromaDB for efficient similarity search.
    """
    
    def __init__(
        self,
        persist_directory: str,
        model_name: str = "all-MiniLM-L6-v2",
        collection_name: str = "memories"
    ):
        """
        Initialize vector storage.
        
        Args:
            persist_directory: Directory to persist the vector database
            model_name: Name of the sentence transformer model to use
            collection_name: Name of the collection in ChromaDB
        """
        self.persist_directory = persist_directory
        self.model_name = model_name
        self.collection_name = collection_name
        
        # Initialize the embedding model
        self.model = SentenceTransformer(model_name)
        
        # Set up the ChromaDB client with persistence and telemetry disabled
        try:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
        except TypeError:
            # Handle compatibility issues with different Python versions
            # by completely disabling telemetry
            os.environ["ANONYMIZED_TELEMETRY"] = "False"
            self.client = chromadb.PersistentClient(
                path=persist_directory
            )
        
        # Get or create collections for each memory type
        try:
            # Try with standard parameters
            self.semantic_collection = self.client.get_or_create_collection(
                name=f"{collection_name}_semantic"
            )
            self.episodic_collection = self.client.get_or_create_collection(
                name=f"{collection_name}_episodic"
            )
            self.procedural_collection = self.client.get_or_create_collection(
                name=f"{collection_name}_procedural"
            )
        except Exception as e:
            # Fall back to simpler method if the above fails due to version differences
            try:
                self.semantic_collection = self.client.get_collection(f"{collection_name}_semantic")
                self.episodic_collection = self.client.get_collection(f"{collection_name}_episodic")
                self.procedural_collection = self.client.get_collection(f"{collection_name}_procedural")
            except Exception:
                # Collections don't exist yet, create them
                self.semantic_collection = self.client.create_collection(f"{collection_name}_semantic")
                self.episodic_collection = self.client.create_collection(f"{collection_name}_episodic")
                self.procedural_collection = self.client.create_collection(f"{collection_name}_procedural")
    
    def _get_collection(self, memory_type: str):
        """Get the appropriate collection for a memory type."""
        if memory_type == "semantic":
            return self.semantic_collection
        elif memory_type == "episodic":
            return self.episodic_collection
        elif memory_type == "procedural":
            return self.procedural_collection
        else:
            raise ValueError(f"Invalid memory type: {memory_type}")
    
    def add(
        self,
        memory_id: UUID,
        content: str,
        memory_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a memory to the vector database.
        
        Args:
            memory_id: UUID of the memory
            content: Text content to embed
            memory_type: Type of memory ('semantic', 'episodic', or 'procedural')
            metadata: Additional metadata to store with the embedding
        """
        if memory_type not in ["semantic", "episodic", "procedural"]:
            raise ValueError(f"Invalid memory type: {memory_type}")
        
        # Get the appropriate collection
        collection = self._get_collection(memory_type)
        
        # Convert metadata values to strings for ChromaDB compatibility
        if metadata:
            string_metadata = {}
            for k, v in metadata.items():
                if isinstance(v, (list, dict)):
                    string_metadata[k] = str(v)
                else:
                    string_metadata[k] = v
        else:
            string_metadata = {}
        
        # Generate embedding and add to collection
        try:
            collection.add(
                ids=[str(memory_id)],
                documents=[content],
                metadatas=[string_metadata]
            )
        except ValueError as e:
            # Item might already exist, try to update it
            if "already exists" in str(e):
                collection.update(
                    ids=[str(memory_id)],
                    documents=[content],
                    metadatas=[string_metadata]
                )
            else:
                raise
    
    def remove(self, memory_id: UUID, memory_type: str) -> None:
        """
        Remove a memory from the vector database.
        
        Args:
            memory_id: UUID of the memory
            memory_type: Type of memory ('semantic', 'episodic', or 'procedural')
        """
        if memory_type not in ["semantic", "episodic", "procedural"]:
            raise ValueError(f"Invalid memory type: {memory_type}")
        
        # Get the appropriate collection
        collection = self._get_collection(memory_type)
        
        # Remove from collection
        try:
            collection.delete(ids=[str(memory_id)])
        except Exception:
            # Item might not exist
            pass
    
    def query(
        self,
        query_text: str,
        memory_type: str,
        n_results: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[UUID, float]]:
        """
        Query the vector database for similar memories.
        
        Args:
            query_text: Query text to search for
            memory_type: Type of memory to search
            n_results: Maximum number of results to return
            metadata_filter: Filter by metadata fields
            
        Returns:
            List[Tuple[UUID, float]]: List of (memory_id, similarity_score) tuples
        """
        if memory_type not in ["semantic", "episodic", "procedural"]:
            raise ValueError(f"Invalid memory type: {memory_type}")
        
        # Get the appropriate collection
        collection = self._get_collection(memory_type)
        
        # Prepare metadata filter if provided
        where = {}
        if metadata_filter:
            for k, v in metadata_filter.items():
                if isinstance(v, (list, dict)):
                    where[k] = {"$eq": str(v)}
                else:
                    where[k] = {"$eq": v}
        
        # Query the collection with error handling for different versions
        try:
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where if where else None
            )
        except TypeError:
            # Fallback for older versions or compatibility issues
            if where:
                # Give a warning but continue without filters if we can't apply them
                warnings.warn(f"Metadata filtering not supported in this chromadb version")
            
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
        
        # Process results
        if not results["ids"][0]:
            return []
        
        # Extract IDs and distances
        ids = results["ids"][0]
        distances = results["distances"][0] if "distances" in results else [1.0] * len(ids)
        
        # Convert distances to similarity scores (1.0 = perfect match, 0.0 = no match)
        similarities = [1.0 - min(dist, 1.0) for dist in distances]
        
        # Return list of (UUID, similarity) tuples
        return [(UUID(id_str), sim) for id_str, sim in zip(ids, similarities)]
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get the embedding vector for a piece of text.
        
        Args:
            text: Text to embed
            
        Returns:
            np.ndarray: Embedding vector
        """
        return self.model.encode(text)
    
    def clear_all(self, memory_type: Optional[str] = None) -> None:
        """
        Clear all vector embeddings, optionally of a specific type.
        
        Args:
            memory_type: Type of memory to clear (if None, clear all)
        """
        if memory_type is None:
            # Clear all collections
            self.semantic_collection.delete(where={})
            self.episodic_collection.delete(where={})
            self.procedural_collection.delete(where={})
        else:
            if memory_type not in ["semantic", "episodic", "procedural"]:
                raise ValueError(f"Invalid memory type: {memory_type}")
            
            collection = self._get_collection(memory_type)
            collection.delete(where={})
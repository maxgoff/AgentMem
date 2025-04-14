# AgentMem Common Patterns & Troubleshooting

## Integration Patterns

### Pattern 1: Comprehensive Agent Memory
```python
from agentmem.semantic import SemanticMemory
from agentmem.episodic import EpisodicMemory
from agentmem.procedural import ProceduralMemory

class Agent:
    def __init__(self):
        # Initialize all memory types with a common storage location
        self.semantic = SemanticMemory(storage_type="file", storage_path="./agent_memory")
        self.episodic = EpisodicMemory(storage_type="file", storage_path="./agent_memory")
        self.procedural = ProceduralMemory(storage_type="file", storage_path="./agent_memory")
    
    def process_input(self, user_input):
        # Record the interaction
        self.episodic.record_event("user_input", content=user_input)
        
        # Find relevant knowledge
        facts = self.semantic.vector_search(user_input, limit=3)
        
        # Find relevant procedures
        procedures = self.procedural.find_procedures(user_input, limit=2)
        
        # Generate response using facts and procedures
        response = self._generate_response(user_input, facts, procedures)
        
        # Record the response
        self.episodic.record_event("agent_response", content=response)
        
        return response
```

### Pattern 2: Vector-Powered Knowledge Base
```python
from agentmem.semantic import SemanticMemory

class KnowledgeBase:
    def __init__(self):
        self.memory = SemanticMemory(
            storage_type="vector",
            embedding_model="all-MiniLM-L6-v2",
            vector_db_url="chroma:///path/to/db"
        )
    
    def add_document(self, doc_id, content, metadata=None):
        # Split content into chunks for better retrieval
        chunks = self._chunk_document(content)
        
        # Store each chunk with reference to original document
        for i, chunk in enumerate(chunks):
            self.memory.add_fact(
                f"{doc_id}_chunk_{i}",
                chunk,
                metadata={"doc_id": doc_id, "chunk": i, **metadata}
            )
    
    def search(self, query, limit=5):
        # Retrieve relevant document chunks
        results = self.memory.vector_search(query, limit=limit)
        
        # Group by original document
        docs = {}
        for result in results:
            doc_id = result["metadata"]["doc_id"]
            if doc_id not in docs:
                docs[doc_id] = []
            docs[doc_id].append(result)
        
        return docs
```

### Pattern 3: Conversation Memory with Time Decay
```python
from agentmem.episodic import EpisodicMemory
from datetime import datetime, timedelta

class ConversationMemory:
    def __init__(self):
        self.memory = EpisodicMemory(storage_type="file", storage_path="./conversations")
    
    def add_message(self, user_id, content, role="user"):
        self.memory.record_event(
            event_type="message",
            content=content,
            metadata={
                "user_id": user_id,
                "role": role,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def get_conversation_context(self, user_id, hours=24, limit=10):
        # Get recent conversation within time window
        time_ago = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        events = self.memory.query_by_timeframe(
            start_time=time_ago,
            end_time=datetime.now().isoformat(),
            metadata_filter={"user_id": user_id},
            limit=limit
        )
        
        # Format as conversation
        return [{"role": e["metadata"]["role"], "content": e["content"]} for e in events]
```

## Quick Troubleshooting Guide

| Problem | Possible Cause | Solution |
|---------|----------------|----------|
| `StorageError: Unable to connect to vector database` | Vector DB not running or misconfigured | Check vector DB service is running and URL is correct |
| `MemoryError: Duplicate ID` | Attempting to add fact with existing ID | Use `update_fact()` or generate unique IDs |
| High latency with vector search | Large vector database or complex query | Reduce vector dimensions, add indices, or limit search scope |
| `LockTimeoutError` | Concurrent operations with extended locks | Reduce lock scope, implement retry logic, or review transaction design |
| Memory consumption too high | Large datasets in memory storage | Switch to file or vector storage, or implement data rotation |
| `FileNotFoundError` | Storage path does not exist | Create directory before initializing memory or use `mkdir=True` |

## Performance Optimization Tips

### 1. Vector Search Optimization
```python
# Pre-compute embeddings for frequently accessed data
precomputed_embeddings = model.encode(frequently_used_data)
semantic_mem.add_precomputed_embeddings(ids, precomputed_embeddings)

# Use namespace to partition vector space
semantic_mem.vector_search("query", namespace="user_data", limit=5)
```

### 2. Batch Operations
```python
# Batch add facts (more efficient than individual adds)
facts = [
    {"id": "fact1", "content": "Content 1"},
    {"id": "fact2", "content": "Content 2"}
]
semantic_mem.add_facts_batch(facts)

# Batch query
ids = ["fact1", "fact2", "fact3"]
results = semantic_mem.get_facts_batch(ids)
```

### 3. Memory Rotation for Episodic Memory
```python
# Set up automatic rotation of old events
episodic_mem = EpisodicMemory(
    storage_type="file",
    storage_path="./memory",
    retention_policy={
        "max_age_days": 30,  # Keep events for 30 days
        "max_events": 1000   # Keep maximum 1000 events
    }
)

# Manually rotate old events
episodic_mem.clear_events_before("2023-01-01T00:00:00")
```

### 4. Storage Selection
```python
# For small datasets: In-memory (fastest)
mem = SemanticMemory(storage_type="memory")

# For persistent but simple needs: File storage
mem = SemanticMemory(storage_type="file", storage_path="./data")

# For large datasets with similarity search: Vector storage
mem = SemanticMemory(storage_type="vector", vector_db_url="chroma:///path/to/db")

# For hybrid approach (fast + persistent)
mem = SemanticMemory(
    storage_type="hybrid",
    file_path="./data",
    cache_size=1000  # Keep 1000 most recent items in memory
)
```
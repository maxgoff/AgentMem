# AgentMem API Cheat Sheet

## Memory Types at a Glance

| Memory Type | Purpose | Primary Use Cases | Key Methods |
|-------------|---------|-------------------|-------------|
| **Semantic Memory** | Store factual knowledge | Knowledge bases, FAQs, persistent facts | `add_fact()`, `query_facts()`, `vector_search()` |
| **Episodic Memory** | Store temporal experiences | Conversation history, event logs, interactions | `record_event()`, `query_by_timeframe()`, `query_similar()` |
| **Procedural Memory** | Store task knowledge | Workflows, procedures, action sequences | `store_procedure()`, `retrieve_procedure()`, `execute_procedure()` |

## Common Operations

### Initialization

```python
# Semantic Memory
from agentmem.semantic import SemanticMemory
semantic_mem = SemanticMemory(storage_type="file", storage_path="./memory")

# Episodic Memory
from agentmem.episodic import EpisodicMemory
episodic_mem = EpisodicMemory(storage_type="file", storage_path="./memory")

# Procedural Memory
from agentmem.procedural import ProceduralMemory
procedural_mem = ProceduralMemory(storage_type="file", storage_path="./memory")
```

### Basic Operations

```python
# SEMANTIC MEMORY
# Add facts
semantic_mem.add_fact("capital_france", "Paris is the capital of France")
semantic_mem.add_fact("python_version", "Python 3.9 was released in 2020")

# Retrieve facts
fact = semantic_mem.get_fact("capital_france")
facts = semantic_mem.query_facts(query="capital", limit=5)
vector_results = semantic_mem.vector_search("What is the capital of France?", limit=3)

# Update and delete
semantic_mem.update_fact("python_version", "Python 3.9 was released in October 2020")
semantic_mem.delete_fact("old_fact_id")

# EPISODIC MEMORY
# Record events
episodic_mem.record_event(
    event_type="user_message",
    content="How do I install Python?",
    metadata={"user_id": "user123", "timestamp": "2023-04-15T10:30:00"}
)

# Query events
recent_events = episodic_mem.query_recent(limit=5)
timeframe_events = episodic_mem.query_by_timeframe(
    start_time="2023-04-15T00:00:00",
    end_time="2023-04-15T23:59:59"
)
similar_events = episodic_mem.query_similar("Python installation help", limit=3)

# Delete events
episodic_mem.delete_event("event_id_123")
episodic_mem.clear_events_before("2023-01-01T00:00:00")

# PROCEDURAL MEMORY
# Store procedures
procedural_mem.store_procedure(
    procedure_id="install_python",
    steps=[
        "Download Python from python.org",
        "Run the installer",
        "Check installation with 'python --version'"
    ],
    metadata={"difficulty": "beginner", "platform": "all"}
)

# Retrieve procedures
procedure = procedural_mem.retrieve_procedure("install_python")
matched_procedures = procedural_mem.find_procedures("installation", limit=3)

# Execute procedures (if supported)
result = procedural_mem.execute_procedure("install_python", context={"platform": "windows"})

# Update procedures
procedural_mem.update_procedure("install_python", new_steps=["Updated step 1", "Updated step 2"])
procedural_mem.delete_procedure("obsolete_procedure")
```

## Storage Backends

| Backend | Configuration | Best For |
|---------|---------------|----------|
| **In-Memory** | `storage_type="memory"` | Testing, temporary use |
| **File-Based** | `storage_type="file", storage_path="./path"` | Persistence, simple apps |
| **Vector DB** | `storage_type="vector", vector_db_url="..."` | Semantic search, large datasets |

## Vector Search Configuration

```python
# Initialize with sentence-transformers model
semantic_mem = SemanticMemory(
    storage_type="vector",
    embedding_model="all-MiniLM-L6-v2",
    vector_db_url="chroma:///path/to/db"
)

# Configure search parameters
results = semantic_mem.vector_search(
    query="Python installation guide",
    limit=5,
    threshold=0.75,  # Minimum similarity score
    namespace="documentation"  # Optional namespace
)
```

## Concurrency Management

```python
# Thread-safe operations
with semantic_mem.lock:
    semantic_mem.add_fact("protected_write", "This write is thread-safe")
    fact = semantic_mem.get_fact("protected_read")

# Transaction support
with semantic_mem.transaction() as txn:
    txn.add_fact("fact1", "First fact")
    txn.add_fact("fact2", "Second fact")
    # All changes committed at end of block if no exceptions
```

## Error Handling Patterns

```python
from agentmem.base import MemoryError, StorageError

try:
    result = semantic_mem.vector_search("query", limit=5)
except StorageError as e:
    print(f"Storage backend error: {e}")
except MemoryError as e:
    print(f"General memory error: {e}")
finally:
    # Cleanup code
    pass
```
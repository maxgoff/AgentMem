# Episodic Memory API

Episodic memory stores specific events and experiences tied to particular points in time. This is where an agent would store memories like "The user asked about file handling last week" or "I helped debug a recursive function yesterday".

## Class: `EpisodicMemory`

The `EpisodicMemory` class provides storage and retrieval for experience-based memories.

### Constructor

```python
EpisodicMemory(
    persistence: Optional[str] = None,
    vector_search: bool = False, 
    vector_db_path: Optional[str] = None
)
```

**Parameters:**
- `persistence`: Path to directory for persistent storage (None for in-memory only)
- `vector_search`: Whether to enable vector-based semantic search for more natural queries
- `vector_db_path`: Path to vector database (defaults to persistence path if None)

### Methods

#### create

```python
create(content: Any, **kwargs) -> UUID
```

Creates a new episodic memory entry.

**Parameters:**
- `content`: The event content to store
- `**kwargs`: Additional metadata including:
  - `timestamp`: When the event occurred (defaults to now)
  - `context`: Additional contextual information (default: {})
  - `importance`: Subjective importance of the memory (1-10, default: 5)

**Returns:**
- UUID: Unique identifier for the created memory

#### read

```python
read(memory_id: UUID) -> Dict[str, Any]
```

Retrieves a specific episodic memory by ID.

**Parameters:**
- `memory_id`: UUID of the memory to retrieve

**Returns:**
- Dict[str, Any]: The memory entry

**Raises:**
- KeyError: If memory_id doesn't exist

#### update

```python
update(memory_id: UUID, content: Any = None, **kwargs) -> None
```

Updates an existing episodic memory entry.

**Parameters:**
- `memory_id`: UUID of the memory to update
- `content`: New content for the memory (if None, content is not updated)
- `**kwargs`: Additional metadata to update including:
  - `context`: Updated contextual information
  - `importance`: Updated importance rating
  - `metadata`: Additional custom metadata

**Raises:**
- KeyError: If memory_id doesn't exist

#### delete

```python
delete(memory_id: UUID) -> None
```

Deletes an episodic memory entry.

**Parameters:**
- `memory_id`: UUID of the memory to delete

**Raises:**
- KeyError: If memory_id doesn't exist

#### query

```python
query(query: str, **kwargs) -> List[Dict[str, Any]]
```

Searches episodic memory based on a query.

**Parameters:**
- `query`: The search query
- `**kwargs`: Additional search parameters including:
  - `start_time`: Filter by earliest timestamp
  - `end_time`: Filter by latest timestamp
  - `min_importance`: Minimum importance level
  - `context_keys`: Required context keys
  - `use_vector`: Whether to use vector search (default: True if enabled)
  - `n_results`: Maximum number of results to return for vector search

**Returns:**
- List[Dict[str, Any]]: List of matching memory entries (sorted by timestamp, most recent first)

### Inherited Methods

The following methods are inherited from the base `Memory` class:

#### save_all

```python
save_all() -> None
```

Saves all memories to persistent storage, ensuring all in-memory data is synchronized with persistent storage.

#### load_all

```python
load_all() -> None
```

Loads all memories from persistent storage, replacing in-memory data with data from persistent storage.

#### clear_all

```python
clear_all() -> None
```

Clears all memories from all storage backends (in-memory, persistent storage, and vector search).

## Class: `EpisodicMemoryEntry`

The `EpisodicMemoryEntry` class represents a single entry in episodic memory.

### Constructor

```python
EpisodicMemoryEntry(content: Any, **kwargs)
```

**Parameters:**
- `content`: The event content to store
- `**kwargs`: Additional metadata including:
  - `timestamp`: When the event occurred (defaults to now)
  - `context`: Additional contextual information
  - `importance`: Subjective importance of the memory (1-10)
  - `id`: Optional UUID (generated if not provided)
  - `created_at`: Creation timestamp (defaults to now)
  - `updated_at`: Update timestamp (defaults to created_at)
  - `metadata`: Dictionary of additional metadata

### Attributes

- `id`: UUID identifying the memory entry
- `content`: The event content
- `timestamp`: When the event occurred
- `context`: Dictionary of contextual information
- `importance`: Subjective importance rating (1-10)
- `created_at`: Timestamp when the memory was created
- `updated_at`: Timestamp when the memory was last updated
- `metadata`: Dictionary of additional metadata

## Example Usage

```python
from agentmem.episodic import EpisodicMemory
from datetime import datetime, timedelta
from uuid import UUID

# Create an episodic memory store with file persistence
episodic_memory = EpisodicMemory(
    persistence="./memory_store",
    vector_search=True  # Enable semantic search
)

# Store an event
yesterday = datetime.now() - timedelta(days=1)
event_id = episodic_memory.create(
    content="User asked about file handling in Python",
    timestamp=yesterday,
    context={
        "conversation_id": "12345",
        "user_name": "Alice",
        "topic": "python-io"
    },
    importance=8
)

# Retrieve the event by ID
event = episodic_memory.read(event_id)
print(event["content"])  # "User asked about file handling in Python"

# Update the event
episodic_memory.update(
    event_id,
    context={
        "resolved": True,
        "satisfaction": "high"
    }
)

# Query for events about Python
results = episodic_memory.query(
    "python",
    min_importance=7,
    context_keys=["topic"]
)

# Delete the event
episodic_memory.delete(event_id)
```
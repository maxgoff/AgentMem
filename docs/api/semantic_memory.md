# Semantic Memory API

Semantic memory stores factual knowledge and concepts that are not tied to specific events or experiences. This is where an agent would store knowledge like "Paris is the capital of France" or "Python is a programming language".

## Class: `SemanticMemory`

The `SemanticMemory` class provides storage and retrieval for factual knowledge and concepts.

### Constructor

```python
SemanticMemory(
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

Creates a new semantic memory entry.

**Parameters:**
- `content`: The factual content to store
- `**kwargs`: Additional metadata including:
  - `category`: Optional categorization of the fact (default: "general")
  - `tags`: Optional list of tags for classification (default: [])

**Returns:**
- UUID: Unique identifier for the created memory

#### read

```python
read(memory_id: UUID) -> Dict[str, Any]
```

Retrieves a specific semantic memory by ID.

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

Updates an existing semantic memory entry.

**Parameters:**
- `memory_id`: UUID of the memory to update
- `content`: New content for the memory (if None, content is not updated)
- `**kwargs`: Additional metadata to update including:
  - `category`: Updated category
  - `tags`: Updated tags
  - `metadata`: Additional custom metadata

**Raises:**
- KeyError: If memory_id doesn't exist

#### delete

```python
delete(memory_id: UUID) -> None
```

Deletes a semantic memory entry.

**Parameters:**
- `memory_id`: UUID of the memory to delete

**Raises:**
- KeyError: If memory_id doesn't exist

#### query

```python
query(query: str, **kwargs) -> List[Dict[str, Any]]
```

Searches semantic memory based on a query.

**Parameters:**
- `query`: The search query
- `**kwargs`: Additional search parameters including:
  - `category`: Filter by category
  - `tags`: Filter by one or more tags
  - `exact_match`: Whether to require exact match (default: False)
  - `use_vector`: Whether to use vector search (default: True if enabled)
  - `n_results`: Maximum number of results to return for vector search

**Returns:**
- List[Dict[str, Any]]: List of matching memory entries

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

## Class: `SemanticMemoryEntry`

The `SemanticMemoryEntry` class represents a single entry in semantic memory.

### Constructor

```python
SemanticMemoryEntry(content: Any, **kwargs)
```

**Parameters:**
- `content`: The factual content to store
- `**kwargs`: Additional metadata including:
  - `category`: Optional categorization of the fact
  - `tags`: Optional list of tags for classification
  - `id`: Optional UUID (generated if not provided)
  - `created_at`: Creation timestamp (defaults to now)
  - `updated_at`: Update timestamp (defaults to created_at)
  - `metadata`: Dictionary of additional metadata

### Attributes

- `id`: UUID identifying the memory entry
- `content`: The factual content
- `category`: Category of the fact (default: "general")
- `tags`: List of tags for classification (default: [])
- `created_at`: Timestamp when the memory was created
- `updated_at`: Timestamp when the memory was last updated
- `metadata`: Dictionary of additional metadata

## Example Usage

```python
from agentmem.semantic import SemanticMemory
from uuid import UUID

# Create a semantic memory store with file persistence
semantic_memory = SemanticMemory(
    persistence="./memory_store",
    vector_search=True  # Enable semantic search
)

# Store a fact
fact_id = semantic_memory.create(
    content="Paris is the capital of France",
    category="geography",
    tags=["europe", "cities", "countries"]
)

# Retrieve the fact by ID
fact = semantic_memory.read(fact_id)
print(fact["content"])  # "Paris is the capital of France"

# Update the fact
semantic_memory.update(
    fact_id,
    tags=["europe", "cities", "countries", "capitals"]
)

# Query for facts about capitals
results = semantic_memory.query(
    "capital",
    category="geography"
)

# Delete the fact
semantic_memory.delete(fact_id)
```
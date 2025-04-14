# Base Memory API

The base memory components provide the foundation for all memory types in AgentMem. They define common interfaces and functionality shared across semantic, episodic, and procedural memory types.

## Class: `Memory`

The `Memory` class is an abstract base class that defines the common interface for all memory types. It provides a standard set of operations and handles persistence and vector search.

### Constructor

```python
Memory(
    persistence: Optional[str] = None,
    vector_search: bool = False,
    vector_db_path: Optional[str] = None,
    memory_type: str = None
)
```

**Parameters:**
- `persistence`: Path to directory for persistent storage (None for in-memory only)
- `vector_search`: Whether to enable vector-based semantic search
- `vector_db_path`: Path to vector database (defaults to persistence path if None)
- `memory_type`: Type of memory ('semantic', 'episodic', or 'procedural')

### Methods

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

### Abstract Methods

The following methods must be implemented by subclasses:

#### create

```python
@abstractmethod
create(content: Any, **kwargs) -> UUID
```

Creates a new memory entry.

**Parameters:**
- `content`: The content to store in memory
- `**kwargs`: Additional metadata for the memory entry

**Returns:**
- UUID: Unique identifier for the created memory

#### read

```python
@abstractmethod
read(memory_id: UUID) -> Dict[str, Any]
```

Retrieves a specific memory by ID.

**Parameters:**
- `memory_id`: UUID of the memory to retrieve

**Returns:**
- Dict[str, Any]: The memory entry

**Raises:**
- KeyError: If memory_id doesn't exist

#### update

```python
@abstractmethod
update(memory_id: UUID, content: Any, **kwargs) -> None
```

Updates an existing memory entry.

**Parameters:**
- `memory_id`: UUID of the memory to update
- `content`: New content for the memory
- `**kwargs`: Additional metadata to update

**Raises:**
- KeyError: If memory_id doesn't exist

#### delete

```python
@abstractmethod
delete(memory_id: UUID) -> None
```

Deletes a memory entry.

**Parameters:**
- `memory_id`: UUID of the memory to delete

**Raises:**
- KeyError: If memory_id doesn't exist

#### query

```python
@abstractmethod
query(query: str, **kwargs) -> List[Dict[str, Any]]
```

Searches memory based on a query.

**Parameters:**
- `query`: The search query
- `**kwargs`: Additional search parameters

**Returns:**
- List[Dict[str, Any]]: List of matching memory entries

#### _entry_to_dict

```python
@abstractmethod
_entry_to_dict(entry) -> Dict[str, Any]
```

Converts a memory entry to a dictionary for storage.

#### _dict_to_entry

```python
@abstractmethod
_dict_to_entry(data: Dict[str, Any])
```

Converts a dictionary to a memory entry.

### Protected Methods

The following methods are used internally by memory implementations:

#### _save_to_persistence

```python
_save_to_persistence(memory_id: UUID, data: Dict[str, Any]) -> None
```

Saves memory to persistent storage if enabled.

#### _load_from_persistence

```python
_load_from_persistence(memory_id: UUID) -> Dict[str, Any]
```

Loads memory from persistent storage if enabled.

#### _delete_from_persistence

```python
_delete_from_persistence(memory_id: UUID) -> None
```

Deletes memory from persistent storage if enabled.

#### _add_to_vector_search

```python
_add_to_vector_search(memory_id: UUID, content: str, metadata: Dict[str, Any]) -> None
```

Adds memory to vector search if enabled.

#### _remove_from_vector_search

```python
_remove_from_vector_search(memory_id: UUID) -> None
```

Removes memory from vector search if enabled.

#### _semantic_search

```python
_semantic_search(
    query: str,
    n_results: int = 5,
    metadata_filter: Optional[Dict[str, Any]] = None
) -> List[Tuple[UUID, float]]
```

Performs semantic search using vector database if enabled.

**Parameters:**
- `query`: Query text to search for
- `n_results`: Maximum number of results to return
- `metadata_filter`: Filter by metadata fields

**Returns:**
- List[Tuple[UUID, float]]: List of (memory_id, similarity) tuples

## Class: `MemoryEntry`

The `MemoryEntry` class is a base class for all memory entry types, providing common metadata attributes.

### Constructor

```python
MemoryEntry(content: Any, **kwargs)
```

**Parameters:**
- `content`: The content to store
- `**kwargs`: Additional metadata including:
  - `id`: Optional UUID (generated if not provided)
  - `created_at`: Creation timestamp (defaults to now)
  - `updated_at`: Update timestamp (defaults to created_at)
  - `metadata`: Dictionary of additional metadata

### Attributes

- `id`: UUID identifying the memory entry
- `content`: The stored content
- `created_at`: Timestamp when the memory was created
- `updated_at`: Timestamp when the memory was last updated
- `metadata`: Dictionary of additional metadata

## Logging Integration

The base Memory class integrates with the AgentMem logging system to provide:

1. **Operation Logging**: All memory operations are logged with appropriate levels
2. **Metrics Collection**: Memory operations are tracked for performance monitoring
3. **Memory Usage Tracking**: Memory size is tracked and reported

When the logging module is available, memory operations will be wrapped with metrics collection and tracking.

## Thread Safety

The base Memory class ensures thread safety through:

1. **Lock Management**: Uses memory-specific locks for operations
2. **Transactions**: Ensures atomicity for multi-step operations
3. **Concurrency Control**: Prevents race conditions in memory access
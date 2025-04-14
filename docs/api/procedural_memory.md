# Procedural Memory API

Procedural memory stores knowledge about how to perform specific tasks or skills. This is where an agent would store knowledge like "How to create a file in Python" or "Steps to debug a recursive function".

## Class: `ProceduralMemory`

The `ProceduralMemory` class provides storage and retrieval for task-related knowledge and procedures.

### Constructor

```python
ProceduralMemory(
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

Creates a new procedural memory entry.

**Parameters:**
- `content`: The procedure or skill description
- `**kwargs`: Additional metadata including:
  - `task`: The task this procedure accomplishes (default: "undefined")
  - `steps`: Sequence of steps in the procedure (default: [])
  - `prerequisites`: Required conditions or resources (default: [])
  - `domains`: List of domains this procedure applies to (default: ["general"])

**Returns:**
- UUID: Unique identifier for the created memory

#### read

```python
read(memory_id: UUID) -> Dict[str, Any]
```

Retrieves a specific procedural memory by ID.

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

Updates an existing procedural memory entry.

**Parameters:**
- `memory_id`: UUID of the memory to update
- `content`: New content for the memory (if None, content is not updated)
- `**kwargs`: Additional metadata to update including:
  - `task`: Updated task description
  - `steps`: Updated sequence of steps
  - `prerequisites`: Updated prerequisites
  - `domains`: Updated list of applicable domains
  - `metadata`: Additional custom metadata

**Raises:**
- KeyError: If memory_id doesn't exist

#### delete

```python
delete(memory_id: UUID) -> None
```

Deletes a procedural memory entry.

**Parameters:**
- `memory_id`: UUID of the memory to delete

**Raises:**
- KeyError: If memory_id doesn't exist

#### query

```python
query(query: str, **kwargs) -> List[Dict[str, Any]]
```

Searches procedural memory based on a query.

**Parameters:**
- `query`: The search query (task description or keywords)
- `**kwargs`: Additional search parameters including:
  - `domain`: Filter by specific domain
  - `prerequisites`: Filter by available prerequisites
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

## Class: `ProceduralMemoryEntry`

The `ProceduralMemoryEntry` class represents a single entry in procedural memory.

### Constructor

```python
ProceduralMemoryEntry(content: Any, **kwargs)
```

**Parameters:**
- `content`: The procedure or skill content to store
- `**kwargs`: Additional metadata including:
  - `task`: The task this procedure accomplishes
  - `steps`: Sequence of steps in the procedure
  - `prerequisites`: Required conditions or resources
  - `domains`: Domains this procedure applies to
  - `id`: Optional UUID (generated if not provided)
  - `created_at`: Creation timestamp (defaults to now)
  - `updated_at`: Update timestamp (defaults to created_at)
  - `metadata`: Dictionary of additional metadata

### Attributes

- `id`: UUID identifying the memory entry
- `content`: The procedure description
- `task`: The task this procedure accomplishes
- `steps`: List of steps in the procedure
- `prerequisites`: List of required conditions or resources
- `domains`: List of domains this procedure applies to
- `created_at`: Timestamp when the memory was created
- `updated_at`: Timestamp when the memory was last updated
- `metadata`: Dictionary of additional metadata

## Example Usage

```python
from agentmem.procedural import ProceduralMemory
from uuid import UUID

# Create a procedural memory store with file persistence
procedural_memory = ProceduralMemory(
    persistence="./memory_store",
    vector_search=True  # Enable semantic search
)

# Store a procedure
procedure_id = procedural_memory.create(
    content="How to create a file in Python",
    task="Create a new file",
    steps=[
        "Import the necessary modules",
        "Use the open() function with 'w' mode",
        "Write content to the file using write() method",
        "Close the file using close() method"
    ],
    prerequisites=["Python environment"],
    domains=["programming", "python", "file-handling"]
)

# Retrieve the procedure by ID
procedure = procedural_memory.read(procedure_id)
print(procedure["content"])  # "How to create a file in Python"

# Update the procedure
procedural_memory.update(
    procedure_id,
    steps=[
        "Import the necessary modules",
        "Use the open() function with 'w' mode",
        "Write content to the file using write() method",
        "Use a context manager (with statement) to automatically close the file",
        "Alternatively, close the file using close() method"
    ]
)

# Query for procedures about file handling
results = procedural_memory.query(
    "file",
    domain="python"
)

# Delete the procedure
procedural_memory.delete(procedure_id)
```
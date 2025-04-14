# Persistence Example

The [persistence_example.py](../examples/persistence_example.py) example demonstrates how to create persistent memory stores in AgentMem, allowing memories to be saved and retrieved across program restarts.

## What This Example Covers

- Creating memory instances with persistence enabled
- Saving memories to disk
- Loading memories from disk
- Managing memory persistence across sessions
- Combining persistence with vector search

## Key Code Sections

### 1. Creating Persistent Memory Stores

```python
# Create persistent memory stores
storage_dir = "./persistent_memory"
os.makedirs(storage_dir, exist_ok=True)

semantic_memory = SemanticMemory(
    persistence=storage_dir,
    vector_search=True
)

episodic_memory = EpisodicMemory(
    persistence=storage_dir,
    vector_search=True
)

procedural_memory = ProceduralMemory(
    persistence=storage_dir,
    vector_search=True
)
```

Memory instances are created with a specified persistence directory, which enables automatic saving and loading of memories.

### 2. Creating and Storing Memories

```python
# Create and store memories
fact_id = semantic_memory.create(
    content="The speed of light is approximately 299,792,458 meters per second",
    category="physics",
    tags=["light", "constants", "science"]
)

print(f"Created fact with ID: {fact_id}")
print(f"Fact: {semantic_memory.read(fact_id)['content']}")

# Memory is automatically saved to disk when created
```

When persistence is enabled, memories are automatically saved to disk when created.

### 3. Manual Save Operations

```python
# Update a memory
semantic_memory.update(
    fact_id,
    content="The speed of light in vacuum is exactly 299,792,458 meters per second",
    tags=["light", "constants", "science", "vacuum"]
)

# Manually save all memories (though individual updates are saved automatically)
semantic_memory.save_all()
print("All memories manually saved to disk")
```

While individual operations automatically save changes, the `save_all()` method ensures all memories are saved to disk.

### 4. Simulating Program Restart

```python
# Simulate program restart by creating new memory instances
print("\nSimulating program restart...\n")

new_semantic_memory = SemanticMemory(
    persistence=storage_dir,
    vector_search=True
)

# Memories are automatically loaded during initialization
print("Memories after restart:")
try:
    loaded_fact = new_semantic_memory.read(fact_id)
    print(f"Successfully loaded fact: {loaded_fact['content']}")
except KeyError:
    print(f"Failed to load fact with ID: {fact_id}")
```

This section demonstrates how memories persist across program restarts by creating new memory instances pointing to the same persistence directory.

### 5. Explicit Memory Loading

```python
# Explicitly reload all memories (though automatic during initialization)
new_semantic_memory.load_all()
print("All memories explicitly loaded from disk")

# Query memories after loading
physics_facts = new_semantic_memory.query("light", category="physics")
print(f"Found {len(physics_facts)} physics facts after loading")
```

While loading happens automatically during initialization, `load_all()` can be called explicitly to refresh the in-memory cache.

### 6. Vector Search with Persistence

```python
# Vector search also works with persistent memories
similar_facts = new_semantic_memory.query(
    "How fast does light travel?",
    use_vector=True
)

print("\nVector search results:")
for fact in similar_facts:
    print(f"- {fact['content']} (Score: {fact.get('similarity_score', 0):.2f})")
```

Persistent memories also support vector-based semantic search.

### 7. Clearing Memories

```python
# Clear all memories (from memory and disk)
print("\nClearing all memories...")
new_semantic_memory.clear_all()

try:
    loaded_fact = new_semantic_memory.read(fact_id)
    print(f"Fact still exists: {loaded_fact['content']}")
except KeyError:
    print(f"Fact with ID {fact_id} has been deleted from both memory and disk")
```

The `clear_all()` method removes memories from both in-memory storage and persistent storage.

## Expected Output

The example produces output similar to:

```
Created fact with ID: 123e4567-e89b-12d3-a456-426614174000
Fact: The speed of light is approximately 299,792,458 meters per second
All memories manually saved to disk

Simulating program restart...

Memories after restart:
Successfully loaded fact: The speed of light in vacuum is exactly 299,792,458 meters per second
All memories explicitly loaded from disk
Found 1 physics facts after loading

Vector search results:
- The speed of light in vacuum is exactly 299,792,458 meters per second (Score: 0.85)

Clearing all memories...
Fact with ID 123e4567-e89b-12d3-a456-426614174000 has been deleted from both memory and disk
```

This demonstrates the complete lifecycle of persistent memories.

## Persistence Directory Structure

When you use persistence, AgentMem creates the following directory structure:

```
./persistent_memory/
├── semantic/
│   └── [memory_id].json
├── episodic/
│   └── [memory_id].json
├── procedural/
│   └── [memory_id].json
└── vector_db/
    ├── chroma.sqlite3
    └── index/
```

Each memory type has its own subdirectory with individual JSON files for each memory entry. The vector database is stored separately for efficient similarity searching.

## Key Takeaways

1. **Automatic Persistence**: When the persistence parameter is provided, memories are automatically saved during CRUD operations.

2. **Transparent Loading**: Memories are automatically loaded from disk when needed.

3. **Memory Consistency**: The system ensures consistency between in-memory and on-disk representations.

4. **Vectors and Persistence**: Vector search capabilities work seamlessly with persistent storage.

5. **Complete Deletion**: The `clear_all()` method fully removes memories from both memory and disk.

## Next Steps

After understanding persistence, you might want to explore:

- [Agent Assistant Example](agent_assistant.md) to see how persistence enables agents to maintain knowledge across sessions
- [Logging Demo](logging_demo.md) to learn about monitoring memory operations and performance

For more detailed information about the AgentMem persistence API, see the [Storage API Reference](../api/storage.md) documentation.
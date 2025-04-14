# AgentMem Installation and Usage Guide

## Installation

### Basic Installation

```bash
pip install agentmem
```

### Development Installation

For development purposes, clone the repository and install in development mode:

```bash
git clone https://github.com/maxgoff/memory.git
cd memory/agentmem
pip install -e .
```

### Optional Dependencies

AgentMem has optional dependencies for different features:

```bash
# For vector search capabilities
pip install agentmem[vector]

# For development tools (testing, linting, etc.)
pip install agentmem[dev]

# For all optional dependencies
pip install agentmem[vector,dev]
```

## Quick Start

```python
from agentmem import SemanticMemory, EpisodicMemory, ProceduralMemory

# Create in-memory instances
semantic_mem = SemanticMemory()
episodic_mem = EpisodicMemory()
procedural_mem = ProceduralMemory()

# Store a fact in semantic memory
fact_id = semantic_mem.create(
    content="Paris is the capital of France",
    category="geography",
    tags=["cities", "countries", "europe"]
)

# Query semantic memory
paris_facts = semantic_mem.query("Paris")
```

## Using Persistence

Enable file-based persistence to maintain memory across sessions:

```python
from agentmem import SemanticMemory

# Create persistent memory
memory = SemanticMemory(persistence="./memory_data")

# Add some data
memory.create(content="Important fact to remember", category="general")

# The data will be automatically saved to disk
# When you create a new instance with the same persistence directory,
# it will load the previous data
memory2 = SemanticMemory(persistence="./memory_data")
# memory2 now contains the same data as memory
```

## Using Vector Search

Enable vector-based semantic search for more powerful retrieval:

```python
from agentmem import SemanticMemory

# Create memory with vector search
memory = SemanticMemory(
    persistence="./memory_data",
    vector_search=True,
    vector_db_path="./vector_db"
)

# Add some facts
memory.create(content="The Earth is the third planet from the Sun")
memory.create(content="Mars is the fourth planet from the Sun")

# Vector search will find conceptually related items,
# even when keywords don't exactly match
results = memory.query("celestial bodies in our solar system")
```

## Running the Examples

AgentMem includes several examples to help you get started:

### Basic Usage Example

```bash
python -m agentmem.examples.basic_usage
```

This example demonstrates basic operations with all three memory types.

### Agent Assistant Example

```bash
python -m agentmem.examples.agent_assistant
```

This example shows how to build a conversational agent that uses all three memory types with persistence and vector search.

## Performance Considerations

- In-memory storage is fastest but doesn't persist between sessions
- File persistence adds some latency but enables data to survive between sessions
- Vector search requires more resources but provides powerful semantic retrieval
- For large datasets, consider using batch operations for better performance

For applications with very large memory stores, you can run performance tests to evaluate different configurations:

```bash
python -m agentmem.tests.test_performance
```

## Concurrency Support

AgentMem provides built-in thread safety for multi-threaded applications:

```python
import threading
from agentmem import SemanticMemory

# Create a shared memory instance
shared_memory = SemanticMemory(persistence="./memory_data")

def worker_function(worker_id):
    # All operations are thread-safe
    # No need for external locks
    fact_id = shared_memory.create(
        content=f"Fact created by worker {worker_id}",
        category="threading"
    )
    
    # Read operation is also thread-safe
    fact = shared_memory.read(fact_id)
    print(f"Worker {worker_id} created: {fact['content']}")

# Create multiple threads
threads = []
for i in range(10):
    thread = threading.Thread(target=worker_function, args=(i,))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()
```

You can also access the lock manager directly for custom operations:

```python
from agentmem import lock_manager

# Create a transaction that ensures atomicity
with lock_manager.transaction(memory_type="semantic", memory_ids={fact_id1, fact_id2}):
    # All operations here are atomic
    # Either all succeed or none do
    memory.update(fact_id1, content="Updated content 1")
    memory.update(fact_id2, content="Updated content 2")
```

## Advanced Configuration

### Customizing Vector Search

```python
from agentmem import SemanticMemory

memory = SemanticMemory(
    persistence="./memory_data",
    vector_search=True,
    vector_db_path="./custom_vectors"
)

# When querying, you can:
# - Disable vector search for specific queries
results1 = memory.query("keyword search", use_vector=False)

# - Specify the number of results
results2 = memory.query("semantic search", n_results=10)
```

### Memory Management

Clearing all data:

```python
# Clear all data from memory and persistence
memory.clear_all()
```

Explicit save/load operations:

```python
# Force save all in-memory data to disk
memory.save_all()

# Force load all data from disk to memory
memory.load_all()
```

## Troubleshooting

### Import Errors

If you encounter import errors related to vector search components:

```
ImportError: No module named 'sentence_transformers'
```

Install the vector search dependencies:

```bash
pip install agentmem[vector]
```

### Performance Issues

If vector search is slow:
- Consider using a smaller model by configuring the VectorStorage directly
- Reduce the number of entries in the vector store
- Use more specific queries and metadata filters
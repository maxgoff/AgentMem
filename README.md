# AgentMem

A Python package for managing agent memory systems with persistence and semantic search capabilities.

## Overview

AgentMem provides implementations of three core memory types essential for AI agents:

- **Semantic Memory**: Long-term factual knowledge storage with categories and tags
- **Episodic Memory**: Storage of specific past events and experiences with timestamps and context
- **Procedural Memory**: Long-term storage of skills and procedures with steps and domains

Each memory type supports:
- In-memory storage for quick experimentation
- File-based persistence for long-term storage
- Vector-based semantic search using embeddings (for more powerful similarity-based retrieval)
- Thread-safety for concurrent operations in multi-threaded applications

## Installation

```bash
pip install agentmem
```

Or install from source:

```bash
git clone https://github.com/maxgoff/memory.git
cd memory/agentmem
pip install -e .
```

### Compatibility Notes

- **Python Support**: AgentMem is compatible with Python 3.8 through 3.12.
- **NumPy 2.x**: AgentMem works with NumPy 2.x but may display warnings related to the sentence-transformers package:
  - These warnings are non-fatal and are automatically suppressed during import
  - If you're concerned about the warnings, you can downgrade NumPy: `pip install "numpy<2"`
  - Alternatively, you can wait for the sentence-transformers package to be updated with NumPy 2.x compatibility
- **Vector Search**: The package gracefully handles environments where vector search can't be enabled:
  - If sentence-transformers or ChromaDB are incompatible with your environment, AgentMem will continue to work without vector search
  - A warning will be displayed only if vector search was explicitly requested
  - All other memory functionality continues to work normally
- **ChromaDB Compatibility**: The package includes fallback mechanisms for different versions of ChromaDB:
  - Telemetry is disabled to avoid TypedDict compatibility issues in older Python versions
  - Collection creation and querying have fallback implementations for API differences
- **Threading**: The thread lock implementation works with both Python 3.x threading implementations
- **Warning Suppression**: All compatibility warnings are automatically suppressed during import to avoid polluting your application logs
- **Robust Imports**: The package uses conditional imports and graceful error handling throughout

## Quick Start

```python
from agentmem import SemanticMemory, EpisodicMemory, ProceduralMemory

# Create in-memory instances
semantic_mem = SemanticMemory()
episodic_mem = EpisodicMemory()
procedural_mem = ProceduralMemory()

# Store semantic facts
fact_id = semantic_mem.create(
    content="Paris is the capital of France",
    category="geography",
    tags=["cities", "countries", "europe"]
)

# Store episodic experiences
event_id = episodic_mem.create(
    content="User asked about Python file handling",
    context={"user_id": "user123", "session": "abc456"},
    importance=7
)

# Store procedural knowledge
procedure_id = procedural_mem.create(
    content="Creating files in Python",
    task="Create a new file",
    steps=[
        "Use open() with 'w' mode to create a file",
        "Write content using the write() method",
        "Close the file using close() or with statement"
    ],
    domains=["programming", "python", "file operations"]
)

# Query memories
paris_facts = semantic_mem.query("Paris")
file_procedures = procedural_mem.query("file", domain="python")
recent_questions = episodic_mem.query("asked", min_importance=5)
```

## Memory Types

### Semantic Memory

Stores factual knowledge like "Paris is the capital of France".

```python
from agentmem import SemanticMemory

# Create with persistence and vector search
semantic_mem = SemanticMemory(
    persistence="./memory_data",  # Enable file persistence
    vector_search=True,           # Enable vector search
    vector_db_path="./vector_db"  # Vector database location
)

# Create facts
fact_id = semantic_mem.create(
    content="The Pacific Ocean is the largest ocean on Earth",
    category="geography",
    tags=["oceans", "earth", "water"]
)

# Read facts
fact = semantic_mem.read(fact_id)
print(fact["content"])  # "The Pacific Ocean is the largest ocean on Earth"

# Update facts
semantic_mem.update(
    fact_id,
    tags=["oceans", "earth", "water", "geography"]
)

# Delete facts
semantic_mem.delete(fact_id)

# Query facts
# Standard keyword search
ocean_facts = semantic_mem.query("ocean", category="geography")
# Vector semantic search (conceptually similar items)
water_bodies = semantic_mem.query("large bodies of water")
```

### Episodic Memory

Stores experiences and events with temporal context.

```python
from agentmem import EpisodicMemory
from datetime import datetime, timedelta

episodic_mem = EpisodicMemory(persistence="./memory_data")

# Create event memory
yesterday = datetime.now() - timedelta(days=1)
event_id = episodic_mem.create(
    content="User asked how to open files in Python",
    timestamp=yesterday,
    context={"user_id": "user123", "topic": "python_files"},
    importance=7
)

# Time-based queries
last_week = datetime.now() - timedelta(days=7)
recent_events = episodic_mem.query(
    "",  # Empty query matches all content
    start_time=last_week,
    end_time=datetime.now()
)

# Importance-based queries
important_events = episodic_mem.query("", min_importance=7)

# Context-based queries
user_events = episodic_mem.query(
    "Python",
    context_keys=["user_id", "topic"]
)
```

### Procedural Memory

Stores knowledge about how to perform tasks.

```python
from agentmem import ProceduralMemory

procedural_mem = ProceduralMemory(persistence="./memory_data")

# Create procedural memory
proc_id = procedural_mem.create(
    content="Installing a Python package",
    task="Install a package with pip",
    steps=[
        "Open a terminal or command prompt",
        "Run 'pip install package-name'",
        "Verify installation with 'pip list'"
    ],
    prerequisites=["Python installed", "Internet connection"],
    domains=["python", "package management"]
)

# Query by domain
python_procedures = procedural_mem.query("", domain="python")

# Query by content across steps
install_procedures = procedural_mem.query("pip install")

# Prerequisites filtering
internet_procedures = procedural_mem.query("", 
                                         prerequisites=["Internet connection"])
```

## Storage Backends

### In-memory Storage

Default storage that keeps all data in memory during runtime.

```python
# Default is in-memory
memory = SemanticMemory()
```

### File Persistence

Enables data to persist across application restarts.

```python
# With file persistence
memory = SemanticMemory(persistence="./data_directory")

# Memory will load existing data when created
# and save data automatically when modified

# Save all in-memory data to disk
memory.save_all()

# Load all data from disk to memory
memory.load_all()

# Clear all data (memory and persistence)
memory.clear_all()
```

### Vector Search

Enables semantic similarity search using vector embeddings.

```python
# With vector search
memory = SemanticMemory(
    vector_search=True,
    vector_db_path="./vector_db"
)

# Add facts
memory.create(content="The Earth is the third planet from the Sun")
memory.create(content="Jupiter is the largest planet in our solar system")

# Vector-based semantic search
# This can find conceptually related items even when keywords don't match
results = memory.query("celestial bodies in space")
for result in results:
    print(f"{result['similarity_score']:.2f}: {result['content']}")
```

## Examples

See the `examples` directory for full examples:

- `basic_usage.py`: Basic usage for all memory types
- `persistence_example.py`: Demonstrates file persistence and vector search
- `lock_monitoring_demo.py`: Demonstrates the lock monitoring system

## Concurrency and Thread-Safety

All memory operations in AgentMem are thread-safe and can be used safely in multi-threaded applications.

### Lock Monitoring

AgentMem includes a lock monitoring system to help diagnose performance issues and track lock contention in concurrent environments:

```python
from agentmem.concurrency import lock_manager

# Lock statistics
stats = lock_manager.get_lock_statistics()
print(f"Global lock contention: {stats.get('global', {}).get('contention_count', 0)}")

# Currently active locks
active_locks = lock_manager.get_active_locks()
for lock_name, (thread, acquisition_time) in active_locks.items():
    print(f"Lock {lock_name} held by {thread.name}")

# Reset monitoring metrics
lock_manager.reset_metrics()

# Disable monitoring for better performance
lock_manager.enable_monitoring(False)

# Re-enable monitoring
lock_manager.enable_monitoring(True)

# Get lock operation history
history = lock_manager.get_lock_history()
```

See the `examples/lock_monitoring_demo.py` for a full demonstration of the lock monitoring features.

## Performance

For large-scale applications, consider the performance characteristics:

- In-memory storage: Fastest for small to medium datasets
- File persistence: Good for long-term storage, adds some latency
- Vector search: Most powerful retrieval but higher resource usage
- Lock monitoring: Adds slight overhead, can be disabled for production

You can run performance tests with:

```bash
# From the root directory (memory/)
python -m tests.test_performance
```

Note: Do not use `python -m agentmem.tests.test_performance` as the tests module is not inside the agentmem package.

## Documentation

For detailed API documentation and examples, see the [full documentation](docs).

## License

MIT

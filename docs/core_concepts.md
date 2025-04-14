# Core Concepts

This document explains the core concepts and architecture of AgentMem.

## Memory Types

AgentMem implements three distinct memory types based on cognitive psychology:

### Semantic Memory

**Semantic memory** stores factual knowledge - information that is not tied to specific experiences or events.

**Key characteristics:**
- Stores facts, concepts, and general knowledge
- Organized with categories and tags
- Can be queried by content, category, or tags
- Supports semantic similarity search (with vector embeddings)

**Examples:**
- "Paris is the capital of France"
- "Python is a programming language"
- "Water boils at 100°C at sea level"

### Episodic Memory

**Episodic memory** stores specific events or experiences tied to particular times and contexts.

**Key characteristics:**
- Includes timestamps for when events occurred
- Contains contextual information about the event
- Allows for time-range queries
- Can be assigned importance levels

**Examples:**
- "User asked about Python lists on March 15th"
- "Agent failed to answer question about quantum physics yesterday"
- "User expressed satisfaction with response on budget planning"

### Procedural Memory

**Procedural memory** stores knowledge about how to perform specific tasks or procedures.

**Key characteristics:**
- Organizes information around tasks and steps
- Includes domains and prerequisites
- Focuses on action sequences and methods
- Helps an agent know "how to do things"

**Examples:**
- Steps to create a Python class
- Process for analyzing financial data
- Procedure for responding to specific user requests

## Storage Backends

AgentMem supports multiple storage backends:

### In-Memory Storage

- Default storage option
- Fastest performance
- Non-persistent (data is lost when the program ends)
- Good for testing and development

### File Persistence

- Stores memories in files on disk
- Enables persistence across program restarts
- Slower than in-memory but maintains state
- Automatically loads/saves memories

### Vector Storage

- Enables semantic similarity search
- Uses neural embeddings for concept matching
- Can find related information even when keywords don't match
- Requires additional dependencies (sentence-transformers, chromadb)

## Key Components

### Memory Base Class

All memory types inherit from the `Memory` base class, which provides:
- Common CRUD operations
- Persistence management
- Vector search integration
- Concurrency control

### Storage System

The storage system provides:
- Abstract interface for different backends
- File storage implementation
- Vector database integration
- Memory ID management

### Logging & Metrics

The logging system offers:
- Configurable logging levels
- Performance metrics collection
- Memory usage tracking
- Operation statistics

### Concurrency Management

Thread-safety features include:
- Lock hierarchy to prevent deadlocks
- Atomic transactions
- Lock contention monitoring
- Performance diagnostics

## Core Operations

### Create

All memory types support creating new memory entries with appropriate metadata:

```python
memory_id = memory.create(content="...", ...)
```

### Read

Retrieve memories by their unique identifiers:

```python
entry = memory.read(memory_id)
```

### Update

Modify existing memories:

```python
memory.update(memory_id, content="...", ...)
```

### Delete

Remove memories:

```python
memory.delete(memory_id)
```

### Query

Search for memories based on various criteria:

```python
results = memory.query("search term", ...)
```

## Memory Management

AgentMem provides several mechanisms for memory management:

### Persistence

Save and load memories to/from persistent storage:

```python
memory.save_all()  # Save all memories
memory.load_all()  # Load all memories
memory.clear_all() # Clear all memories
```

### Vector Search

When enabled, vector search allows semantic similarity matching:

```python
# Find conceptually similar items even without exact keyword matches
results = memory.query("concepts related to my search", use_vector=True)
```

### Threading Support

All memory operations are thread-safe, allowing for concurrent access:

```python
# Can be safely called from multiple threads
memory.create(...)
memory.query(...)
```

## Design Philosophy

AgentMem is designed with these principles in mind:

1. **Simple API**: Consistent interfaces across memory types
2. **Scalability**: From simple in-memory to vector databases
3. **Extensibility**: Easy to add new memory types or storage backends
4. **Performance**: Optimized for common operations
5. **Thread Safety**: Robust in multi-threaded environments
6. **Monitoring**: Built-in logging and metrics collection
# API Reference

Welcome to the AgentMem API reference documentation. This section provides detailed information about the classes, methods, and interfaces that make up the AgentMem package.

## Memory Types

AgentMem implements three core types of memory for AI agents:

- [**Semantic Memory**](semantic_memory.md): Long-term factual knowledge storage
  - Stores facts, concepts, and general knowledge
  - Example: "Paris is the capital of France"

- [**Episodic Memory**](episodic_memory.md): Storage of specific past events and experiences
  - Records temporal sequences and events with context
  - Example: "Last week, the user asked about Python file handling"

- [**Procedural Memory**](procedural_memory.md): Long-term storage of skills and procedures
  - Contains knowledge about how to perform specific tasks
  - Example: "To create a new file in Python, use the open() function with 'w' mode"

## Core Components

- [**Base Memory**](base_memory.md): Core memory interfaces and shared functionality
  - Defines common CRUD operations
  - Provides persistence and vector search integration
  - Implements thread safety and transaction support

## Storage Backends

AgentMem provides several storage backends for memory persistence:

- **In-Memory Storage**: Fast, non-persistent storage (default)
- **File Storage**: JSON-based persistent storage for all memory types
- **Vector Storage**: Semantic search capabilities using embeddings

## Utility Modules

- **Concurrency**: Thread safety and lock management for memory operations
- **Logging**: Comprehensive logging and metrics collection
- **Memory Usage Tracking**: Monitoring memory consumption and performance

## Complete Class Hierarchy

```
Memory (ABC)
├── SemanticMemory
│   └── SemanticMemoryEntry
├── EpisodicMemory
│   └── EpisodicMemoryEntry
└── ProceduralMemory
    └── ProceduralMemoryEntry
```

## Working with Memory

All memory types follow a similar pattern for working with memory entries:

1. **Create**: Add new memories with content and metadata
2. **Read**: Retrieve memories by their unique identifier
3. **Update**: Modify existing memories with new content or metadata
4. **Delete**: Remove memories that are no longer needed
5. **Query**: Search for memories based on content, metadata, or semantic similarity

Each memory type has specialized query capabilities tailored to its purpose and structure.
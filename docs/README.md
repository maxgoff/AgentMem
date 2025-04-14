# AgentMem Documentation

Welcome to the AgentMem documentation! AgentMem is a Python package that implements different types of memory for AI agents, making it easier to build agents that can remember, learn, and adapt.

## Memory Types

AgentMem implements three core types of memory for AI agents:

1. **Semantic Memory**: Long-term factual knowledge storage
   - Stores facts, concepts, and general knowledge
   - Supports retrieval of information without specific context
   - Example: "Paris is the capital of France"

2. **Episodic Memory**: Storage of specific past events and experiences
   - Records temporal sequences and events with context
   - Supports "remembering" specific interactions and conversations
   - Example: "Last week, the user asked about Python file handling"

3. **Procedural Memory**: Long-term storage of skills and procedures
   - Contains knowledge about how to perform specific tasks
   - Stores action sequences, workflows, and methodologies
   - Example: "To create a new file in Python, use the open() function with 'w' mode"

## Key Features

- **Flexible Storage Options**: In-memory, file-based, and vector database storage
- **Thread-Safe Operations**: Built-in concurrency management for safe multi-threaded use
- **Vector-Based Semantic Search**: Find memories based on meaning, not just keywords
- **Comprehensive Logging**: Detailed logging and metrics for monitoring and debugging
- **Persistent Storage**: Save and load memories across sessions
- **Simple, Intuitive API**: Easy-to-use interface for all memory operations

## Getting Started

- [Installation Guide](installation.md): How to install AgentMem and its dependencies
- [Quick Start Guide](quick_start.md): Get up and running with AgentMem quickly
- [Core Concepts](core_concepts.md): Learn the fundamental concepts of AgentMem
- [Cheat Sheets & Quick References](cheat_sheets/index.md): Quick reference guides and decision flowcharts

## Tutorials

- [Basic Usage Tutorial](tutorials/basic_usage.md): An introduction to AgentMem with simple examples
- [Semantic Memory Tutorial](tutorials/semantic_memory_tutorial.md): Learn how to store and retrieve factual knowledge
- [Episodic Memory Tutorial](tutorials/episodic_memory_tutorial.md): Learn how to record and query experience-based memories
- [Procedural Memory Tutorial](tutorials/procedural_memory_tutorial.md): Learn how to store and access task-related knowledge
- [Vector Search Tutorial](tutorials/vector_search.md): Leveraging semantic similarity for better memory retrieval

## API Reference

- [API Overview](api/index.md): Complete API reference
- [Semantic Memory API](api/semantic_memory.md): API for semantic memory
- [Episodic Memory API](api/episodic_memory.md): API for episodic memory
- [Procedural Memory API](api/procedural_memory.md): API for procedural memory
- [Base Memory API](api/base_memory.md): Core memory interfaces and shared functionality

## Examples

The [examples](examples/) directory contains complete examples showing AgentMem in action:

- [Basic Usage Example](examples/basic_usage.py): Simple usage of all memory types
- [Agent Assistant Example](examples/agent_assistant.py): Building a conversational agent with memory
- [Persistence Example](examples/persistence_example.py): Saving and loading memories
- [Lock Monitoring Demo](examples/lock_monitoring_demo.py): Thread safety and concurrency

## Contributing

We welcome contributions to AgentMem! Check out the [Contributing Guide](https://github.com/maxgoff/memory/blob/main/agentmem/CONTRIBUTING.md) to learn how you can help improve the project.

## License

AgentMem is released under the [MIT License](https://github.com/maxgoff/memory/blob/main/agentmem/LICENSE).
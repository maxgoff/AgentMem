# AgentMem

[![Python Tests](https://github.com/maxgoff/AgentMem/actions/workflows/python-tests.yml/badge.svg)](https://github.com/maxgoff/memory/actions/workflows/python-tests.yml)
[![PyPI version](https://badge.fury.io/py/agentmem.svg)](https://badge.fury.io/py/agentmem)
[![Python Versions](https://img.shields.io/pypi/pyversions/agentmem.svg)](https://pypi.org/project/agentmem/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
- Comprehensive logging and monitoring

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

## Documentation

For detailed documentation, examples, and guides, see the [full documentation](https://github.com/maxgoff/memory/blob/main/agentmem/README.md).

## Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

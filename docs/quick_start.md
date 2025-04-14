# Quick Start Guide

This guide will help you get started with AgentMem quickly.

## Installation

First, install AgentMem:

```bash
pip install agentmem
```

## Basic Usage

### Creating Memory Objects

Start by importing and creating memory objects:

```python
from agentmem import SemanticMemory, EpisodicMemory, ProceduralMemory

# Create in-memory only instances
semantic_mem = SemanticMemory()
episodic_mem = EpisodicMemory()
procedural_mem = ProceduralMemory()

# Or create with persistence
persistent_memory = SemanticMemory(persistence="./memory_data")

# Or create with vector search capabilities
vector_memory = SemanticMemory(
    persistence="./memory_data",
    vector_search=True,
    vector_db_path="./vector_db"
)
```

### Working with Semantic Memory

Semantic memory stores factual knowledge with categories and tags:

```python
# Create a fact
fact_id = semantic_mem.create(
    content="Paris is the capital of France",
    category="geography",
    tags=["cities", "countries", "europe"]
)

# Read a fact
fact = semantic_mem.read(fact_id)
print(fact["content"])  # "Paris is the capital of France"

# Update a fact
semantic_mem.update(
    fact_id,
    content="Paris is the capital and largest city of France",
    tags=["cities", "countries", "europe", "updated"]
)

# Query facts
results = semantic_mem.query("Paris")
results_by_category = semantic_mem.query("capital", category="geography")
results_by_tag = semantic_mem.query("", tags=["europe"])

# Vector search (if enabled)
similar_results = vector_memory.query("major European urban centers")
```

### Working with Episodic Memory

Episodic memory stores experiences and events with timestamps:

```python
from datetime import datetime, timedelta

# Create an event memory
yesterday = datetime.now() - timedelta(days=1)
event_id = episodic_mem.create(
    content="User asked how to use Python lists",
    timestamp=yesterday,
    context={"user_id": "user123", "topic": "python"},
    importance=7
)

# Query by time range
last_week = datetime.now() - timedelta(days=7)
recent_events = episodic_mem.query(
    "",  # Empty query matches all content
    start_time=last_week,
    end_time=datetime.now()
)

# Query by importance
important_events = episodic_mem.query("", min_importance=7)
```

### Working with Procedural Memory

Procedural memory stores knowledge about how to perform tasks:

```python
# Create procedural memory
proc_id = procedural_mem.create(
    content="How to create a list in Python",
    task="Create and use a list",
    steps=[
        "Define a list with square brackets: my_list = [1, 2, 3]",
        "Add items with append(): my_list.append(4)",
        "Access items with indexing: my_list[0]",
        "Slice lists with colon notation: my_list[1:3]"
    ],
    prerequisites=["Basic Python knowledge"],
    domains=["programming", "python", "data structures"]
)

# Query by domain
python_procedures = procedural_mem.query("", domain="python")

# Query by content across steps
list_procedures = procedural_mem.query("append")
```

## Working with Persistence

Save and load memories to/from disk:

```python
# Save all memories to disk
semantic_mem.save_all()

# Clear memory (in-memory only)
semantic_mem.clear_all()

# Load from disk
semantic_mem.load_all()
```

## Configure Logging

AgentMem includes a comprehensive logging system:

```python
from agentmem import configure_logging, LogLevel

# Configure logging with file output
configure_logging(
    log_level=LogLevel.DEBUG,
    log_file="./agentmem.log",
    console_output=True
)

# Get metrics after operations
from agentmem import get_metrics_collector

metrics = get_metrics_collector()
stats = metrics.get_operation_stats()
print(f"Query operations: {stats.get('semantic.query', {}).get('count', 0)}")
```

## Next Steps

- For more detailed examples, see the [Tutorials](tutorials/basic_usage.md)
- For API documentation, see the [API Reference](api/memory.md)
- For complete examples, see the [Examples](examples/ai_assistant.md)
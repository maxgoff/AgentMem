# Basic Usage Example

The [basic_usage.py](../examples/basic_usage.py) example demonstrates the fundamental operations for all three memory types in AgentMem: Semantic, Episodic, and Procedural.

## What This Example Covers

- Creating memory instances with different configurations
- Basic CRUD operations (Create, Read, Update, Delete)
- Querying memories using various search parameters
- Working with specific features of each memory type

## Key Code Sections

### 1. Memory Creation

```python
# Create memory instances
semantic_memory = SemanticMemory(vector_search=True)
episodic_memory = EpisodicMemory(vector_search=True)
procedural_memory = ProceduralMemory(vector_search=True)
```

Each memory type is instantiated with vector search enabled for semantic similarity searching.

### 2. Working with Semantic Memory

```python
# Create a semantic memory entry
fact_id = semantic_memory.create(
    content="Paris is the capital of France",
    category="geography",
    tags=["europe", "cities", "capitals"]
)

# Query semantic memory
results = semantic_memory.query("capital", category="geography")
```

Semantic memory stores factual information with categories and tags for organization.

### 3. Working with Episodic Memory

```python
# Create an episodic memory entry
experience_id = episodic_memory.create(
    content="User asked about Python file handling",
    timestamp=yesterday,
    context={"user": "John", "topic": "python-io"},
    importance=8
)

# Query episodic memory by time period
recent_experiences = episodic_memory.query(
    "",
    start_time=yesterday,
    end_time=today
)
```

Episodic memory stores time-based experiences with context and importance ratings.

### 4. Working with Procedural Memory

```python
# Create a procedural memory entry
procedure_id = procedural_memory.create(
    content="How to create a file in Python",
    task="Create and write to a file",
    steps=[
        "Use open() function with 'w' mode",
        "Write content with write() method",
        "Close the file with close()"
    ],
    prerequisites=["Python installed"],
    domains=["programming", "file-io"]
)

# Query procedural memory by domain
programming_procedures = procedural_memory.query("", domain="programming")
```

Procedural memory stores task-oriented knowledge with steps, prerequisites, and domains.

### 5. Vector Search

```python
# Semantic search using vector embeddings
semantic_results = semantic_memory.query(
    "What's the main city in France?",
    use_vector=True
)
```

When vector search is enabled, queries can use natural language to find similar content even when exact keywords don't match.

## Expected Output

The example prints the results of various operations to demonstrate how the memories are stored and retrieved.

Example output:

```
--- Semantic Memory ---
Created fact: Paris is the capital of France (ID: f8e7d6c5-...)
Read fact: {'id': 'f8e7d6c5-...', 'content': 'Paris is the capital of France', ...}
Geography facts: [{'content': 'Paris is the capital of France', 'category': 'geography', ...}]

--- Episodic Memory ---
Created experience about Python file handling (ID: a1b2c3d4-...)
Recent experiences: [{'content': 'User asked about Python file handling', 'timestamp': '2023-05-01T15:30:00', ...}]

--- Procedural Memory ---
Created procedure: How to create a file in Python (ID: 9i8u7y6t-...)
Programming procedures: [{'task': 'Create and write to a file', 'steps': ['Use open() function with 'w' mode', ...], ...}]
```

## Key Takeaways

1. Each memory type has specialized attributes for its purpose:
   - Semantic: categories and tags
   - Episodic: timestamps, context, and importance
   - Procedural: tasks, steps, prerequisites, and domains

2. The query interface is consistent across memory types, with type-specific parameters.

3. Vector search enables more natural, semantic queries beyond simple keyword matching.

## Next Steps

After understanding the basic operations, you may want to explore:

- [Persistence Example](persistence_example.md) to learn how to save memories across sessions
- [Agent Assistant Example](agent_assistant.md) to see how to combine memory types in an AI agent
- [Logging Demo](logging_demo.md) to understand how to monitor memory performance

For more detailed API information, see the [API Reference](../api/index.md) documentation.
# Vector Search Tutorial

This tutorial will guide you through using AgentMem's vector search capabilities to enable semantic similarity searches across all memory types.

## What is Vector Search?

Vector search allows agents to find memories based on semantic similarity rather than just keyword matching. This means the agent can find relevant information even when queries use different words than the stored memories. Vector search works by converting text into high-dimensional vectors (embeddings) that capture the semantic meaning, and then finding memories with similar vectors.

## Prerequisites

Vector search requires the following dependencies:

```
sentence-transformers>=2.2.0
chromadb>=0.4.0
```

You can install these with:

```bash
pip install "agentmem[vector]"
```

## Enabling Vector Search

Vector search can be enabled for any memory type by setting the `vector_search` parameter to `True` when creating a memory store:

```python
from agentmem.semantic import SemanticMemory
from agentmem.episodic import EpisodicMemory
from agentmem.procedural import ProceduralMemory

# Enable vector search for each memory type
semantic_memory = SemanticMemory(vector_search=True)
episodic_memory = EpisodicMemory(vector_search=True)
procedural_memory = ProceduralMemory(vector_search=True)
```

By default, vector databases are stored in memory. For persistence, provide a path:

```python
# With persistence
semantic_memory = SemanticMemory(
    persistence="./memory_data",
    vector_search=True,
    vector_db_path="./vector_db"  # Optional, defaults to persistence path
)
```

## How Vector Search Works

When vector search is enabled:

1. Each memory is converted to a numerical vector representation using a pre-trained language model
2. These vectors are stored in a vector database (ChromaDB by default)
3. When querying, the query text is converted to a vector as well
4. The system finds memories whose vectors are closest to the query vector
5. Results are returned with a similarity score indicating how closely they match

## Basic Vector Search Example

Let's see a simple example using semantic memory:

```python
from agentmem.semantic import SemanticMemory

# Create a memory store with vector search
memory = SemanticMemory(vector_search=True)

# Add some facts
memory.create(
    content="Paris is the capital city of France",
    category="geography"
)

memory.create(
    content="The Eiffel Tower is located in Paris",
    category="landmarks"
)

memory.create(
    content="Python is a high-level programming language",
    category="programming"
)

# Standard keyword search - only finds exact matches
results = memory.query("France")
print("Keyword search for 'France':")
for fact in results:
    print(f"- {fact['content']}")

# Vector search - finds semantically related content
# Note: use_vector=True is the default when vector_search is enabled
results = memory.query("What's the main city in France?", use_vector=True)
print("\nVector search for 'What's the main city in France?':")
for fact in results:
    print(f"- {fact['content']} (Score: {fact.get('similarity_score', 0):.2f})")
```

This will show that vector search finds the fact about Paris being the capital of France, even though the query uses "main city" instead of "capital" and is phrased as a question.

## Advanced Vector Search Features

### Filtering with Metadata

You can combine vector search with metadata filtering:

```python
# Add more facts with different categories
memory.create(
    content="Rome is the capital city of Italy",
    category="geography"
)

memory.create(
    content="The Colosseum is an ancient amphitheater in Rome",
    category="landmarks"
)

# Vector search only within a specific category
results = memory.query(
    "famous structures in European cities",
    category="landmarks",
    use_vector=True
)

print("Vector search for landmarks:")
for fact in results:
    print(f"- {fact['content']} (Score: {fact.get('similarity_score', 0):.2f})")
```

### Controlling Number of Results

You can specify the maximum number of results to return:

```python
# Get only the top 2 most similar results
results = memory.query(
    "European capitals",
    use_vector=True,
    n_results=2
)

print("Top 2 results for 'European capitals':")
for fact in results:
    print(f"- {fact['content']} (Score: {fact.get('similarity_score', 0):.2f})")
```

## Vector Search with Different Memory Types

### Episodic Memory

Vector search is particularly useful for episodic memory, where experiences may be described in various ways:

```python
from agentmem.episodic import EpisodicMemory
from datetime import datetime, timedelta

# Create episodic memory with vector search
episodic = EpisodicMemory(vector_search=True)

# Add some experiences
yesterday = datetime.now() - timedelta(days=1)
last_week = datetime.now() - timedelta(days=7)

episodic.create(
    content="User was confused about how to install Python packages",
    timestamp=yesterday,
    context={"topic": "package-management", "resolved": True}
)

episodic.create(
    content="Explained the difference between pip and conda",
    timestamp=last_week,
    context={"topic": "package-management", "tools": ["pip", "conda"]}
)

episodic.create(
    content="User needed help with a TypeError in their code",
    timestamp=yesterday,
    context={"topic": "debugging", "language": "Python"}
)

# Vector search for package management issues
results = episodic.query(
    "dependency management problems in Python",
    use_vector=True
)

print("Vector search for package management:")
for exp in results:
    print(f"- {exp['content']} (Score: {exp.get('similarity_score', 0):.2f})")
```

### Procedural Memory

Vector search helps find relevant procedures even when the task is described differently:

```python
from agentmem.procedural import ProceduralMemory

# Create procedural memory with vector search
procedural = ProceduralMemory(vector_search=True)

# Add some procedures
procedural.create(
    content="How to debug a memory leak in Python",
    task="Fix memory leaks",
    steps=[
        "Use tracemalloc to track allocations",
        "Take snapshots before and after operations",
        "Compare snapshots to find growing allocations"
    ],
    domains=["python", "debugging", "performance"]
)

procedural.create(
    content="How to profile Python code performance",
    task="Optimize code execution",
    steps=[
        "Use cProfile to measure function call times",
        "Sort results by cumulative time",
        "Identify hotspots in the code"
    ],
    domains=["python", "performance"]
)

# Vector search for optimization techniques
results = procedural.query(
    "make my Python code run faster",
    use_vector=True
)

print("Vector search for optimization:")
for proc in results:
    print(f"- {proc['task']}: {proc['content']} (Score: {proc.get('similarity_score', 0):.2f})")
```

## Combining Memory Types with Vector Search

In a complete agent, you might want to search across all memory types:

```python
def unified_search(query, semantic, episodic, procedural, n_results=3):
    """Search across all memory types and combine results"""
    # Search each memory type
    semantic_results = semantic.query(query, use_vector=True, n_results=n_results)
    episodic_results = episodic.query(query, use_vector=True, n_results=n_results)
    procedural_results = procedural.query(query, use_vector=True, n_results=n_results)
    
    # Add source information to each result
    for result in semantic_results:
        result["memory_type"] = "semantic"
    
    for result in episodic_results:
        result["memory_type"] = "episodic"
    
    for result in procedural_results:
        result["memory_type"] = "procedural"
    
    # Combine all results
    all_results = semantic_results + episodic_results + procedural_results
    
    # Sort by similarity score (highest first)
    all_results.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
    
    # Return top N results across all memory types
    return all_results[:n_results]

# Use this function to search across all memories
results = unified_search(
    "How can I make my Python application perform better?",
    semantic_memory,
    episodic_memory, 
    procedural_memory
)

print("\nUnified search results:")
for res in results:
    print(f"[{res['memory_type']}] {res.get('content', res.get('task', ''))} " 
          f"(Score: {res.get('similarity_score', 0):.2f})")
```

## Under the Hood

AgentMem uses the following components for vector search:

1. **Sentence Transformers**: Converts text to embeddings
2. **ChromaDB**: Stores and indexes the embeddings for efficient similarity search

The implementation gracefully degrades if these dependencies aren't available, falling back to standard keyword search.

## Performance Considerations

Vector search requires more resources than standard keyword search:

1. **Memory**: Embeddings take up significant memory
2. **Computation**: Generating embeddings can be CPU or GPU intensive
3. **Storage**: Persistent vector databases require disk space

For small agents, in-memory vector search works well. For larger applications, consider:

1. Using a separate storage path for vector databases
2. Implementing a caching strategy for frequently accessed memories
3. Periodically pruning the vector database of unused or outdated entries

## Conclusion

Vector search dramatically improves an agent's ability to find relevant memories by understanding the semantic meaning behind queries rather than just matching keywords. This allows for more natural interactions where users can ask questions in different ways and still get appropriate responses.

For more information about the memory types that support vector search, see:
- [Semantic Memory API](../api/semantic_memory.md)
- [Episodic Memory API](../api/episodic_memory.md)
- [Procedural Memory API](../api/procedural_memory.md)
# Basic Usage Tutorial

This tutorial will walk you through the basics of using AgentMem to implement memory for AI agents.

## Setup

First, install AgentMem:

```bash
pip install agentmem
```

## Creating Memory Instances

Let's start by creating instances of the three memory types:

```python
from agentmem import SemanticMemory, EpisodicMemory, ProceduralMemory

# Create basic in-memory instances
semantic_memory = SemanticMemory()
episodic_memory = EpisodicMemory()
procedural_memory = ProceduralMemory()

print("Memory instances created successfully!")
```

## Working with Semantic Memory

Semantic memory is used for storing factual knowledge:

```python
# Create several facts
fact1_id = semantic_memory.create(
    content="Python is a high-level programming language",
    category="programming",
    tags=["python", "languages", "coding"]
)

fact2_id = semantic_memory.create(
    content="Jupiter is the largest planet in our solar system",
    category="astronomy",
    tags=["planets", "solar system", "space"]
)

fact3_id = semantic_memory.create(
    content="The Great Barrier Reef is the world's largest coral reef system",
    category="geography",
    tags=["australia", "ocean", "ecosystems"]
)

# Retrieve a fact by ID
fact = semantic_memory.read(fact1_id)
print(f"Retrieved fact: {fact['content']}")
print(f"Category: {fact['category']}")
print(f"Tags: {', '.join(fact['tags'])}")

# Update a fact
semantic_memory.update(
    fact1_id,
    content="Python is a high-level, interpreted programming language",
    tags=["python", "languages", "coding", "interpreted"]
)

# Query facts
python_facts = semantic_memory.query("Python")
print(f"Found {len(python_facts)} facts about Python")

astronomy_facts = semantic_memory.query("", category="astronomy")
print(f"Found {len(astronomy_facts)} astronomy facts")

ocean_facts = semantic_memory.query("", tags=["ocean"])
print(f"Found {len(ocean_facts)} facts tagged with 'ocean'")
```

## Working with Episodic Memory

Episodic memory stores events or experiences with temporal context:

```python
from datetime import datetime, timedelta

# Create various events
now = datetime.now()
yesterday = now - timedelta(days=1)
last_week = now - timedelta(days=7)

event1_id = episodic_memory.create(
    content="User asked about Python loops",
    timestamp=yesterday,
    context={"user_id": "user123", "session": "abc456"},
    importance=7
)

event2_id = episodic_memory.create(
    content="User was confused about variable scope",
    timestamp=last_week,
    context={"user_id": "user123", "session": "def789"},
    importance=8
)

event3_id = episodic_memory.create(
    content="User successfully created their first function",
    timestamp=now,
    context={"user_id": "user123", "session": "abc456"},
    importance=9
)

# Retrieve an event
event = episodic_memory.read(event1_id)
print(f"Event: {event['content']}")
print(f"Timestamp: {event['timestamp']}")
print(f"Importance: {event['importance']}")

# Query events by time range
recent_events = episodic_memory.query(
    "",
    start_time=yesterday - timedelta(hours=1),
    end_time=now + timedelta(hours=1)
)
print(f"Found {len(recent_events)} recent events")

# Query events by importance
important_events = episodic_memory.query("", min_importance=8)
print(f"Found {len(important_events)} important events")

# Query events by content and context
python_events = episodic_memory.query(
    "Python", 
    context_filter={"user_id": "user123"}
)
print(f"Found {len(python_events)} Python-related events for user123")
```

## Working with Procedural Memory

Procedural memory stores information about how to perform tasks:

```python
# Create procedural memories
proc1_id = procedural_memory.create(
    content="How to create a Python function",
    task="Define and use a function",
    steps=[
        "Start with the 'def' keyword",
        "Choose a function name",
        "Add parameters in parentheses",
        "End the line with a colon",
        "Write the function body with indentation",
        "Use 'return' to provide output"
    ],
    prerequisites=["Basic Python syntax knowledge"],
    domains=["programming", "python", "functions"]
)

proc2_id = procedural_memory.create(
    content="How to use Python lists",
    task="Create and manipulate lists",
    steps=[
        "Define a list with square brackets: my_list = [1, 2, 3]",
        "Add items with append(): my_list.append(4)",
        "Remove items with remove(): my_list.remove(1)",
        "Access items with indexing: my_list[0]",
        "Slice lists: my_list[1:3]"
    ],
    prerequisites=["Basic Python knowledge"],
    domains=["programming", "python", "data structures"]
)

# Retrieve a procedure
procedure = procedural_memory.read(proc1_id)
print(f"Task: {procedure['task']}")
print("Steps:")
for i, step in enumerate(procedure['steps'], 1):
    print(f"  {i}. {step}")

# Query procedures by domain
python_procs = procedural_memory.query("", domain="python")
print(f"Found {len(python_procs)} Python procedures")

# Query procedures by content
function_procs = procedural_memory.query("function")
print(f"Found {len(function_procs)} procedures related to functions")
```

## Saving and Loading Memories

Let's see how to persist memories to disk:

```python
import os
import tempfile

# Create a temporary directory for persistence
persist_dir = os.path.join(tempfile.gettempdir(), "agentmem_tutorial")
os.makedirs(persist_dir, exist_ok=True)

# Create memory with persistence
persistent_memory = SemanticMemory(persistence=persist_dir)

# Add some facts
fact_id = persistent_memory.create(
    content="The Earth is the third planet from the Sun",
    category="astronomy",
    tags=["planets", "earth", "solar system"]
)

# Save to disk (this happens automatically, but can be called explicitly)
persistent_memory.save_all()
print("Memories saved to disk")

# Create a new instance that loads from the same directory
loaded_memory = SemanticMemory(persistence=persist_dir)
loaded_memory.load_all()

# Verify the data was loaded
fact = loaded_memory.read(fact_id)
print(f"Loaded fact: {fact['content']}")
```

## Using Vector Search

Let's try vector-based semantic search:

```python
import os
import tempfile

# Create directories for persistence and vector storage
base_dir = os.path.join(tempfile.gettempdir(), "agentmem_vector_tutorial")
persist_dir = os.path.join(base_dir, "persistence")
vector_dir = os.path.join(base_dir, "vector_db")
os.makedirs(persist_dir, exist_ok=True)
os.makedirs(vector_dir, exist_ok=True)

# Create memory with vector search
try:
    vector_memory = SemanticMemory(
        persistence=persist_dir,
        vector_search=True,
        vector_db_path=vector_dir
    )
    
    # Add some facts
    vector_memory.create(
        content="Machine learning is a subset of artificial intelligence",
        category="technology",
        tags=["AI", "ML", "computing"]
    )
    
    vector_memory.create(
        content="Neural networks are inspired by the human brain",
        category="technology",
        tags=["AI", "ML", "neural networks"]
    )
    
    vector_memory.create(
        content="Transformers have revolutionized natural language processing",
        category="technology",
        tags=["AI", "NLP", "transformers"]
    )
    
    # Standard keyword search
    keyword_results = vector_memory.query("neural networks", use_vector=False)
    print(f"Keyword search found {len(keyword_results)} results")
    
    # Vector semantic search
    semantic_results = vector_memory.query("brain-inspired AI architectures")
    print(f"Semantic search found {len(semantic_results)} results")
    
    for result in semantic_results:
        print(f"Result: {result['content']}")
        print(f"Similarity score: {result['similarity_score']:.2f}")
        print()
        
except ImportError as e:
    print(f"Vector search not available: {e}")
    print("To use vector search, install with: pip install agentmem[vector]")
```

## Conclusion

You've now learned the basics of using AgentMem for various memory types. This foundation will help you build more complex agent memory systems.

Next steps:
- Explore the [API documentation](../api/memory.md) for more details
- Try the specific tutorials for each memory type
- Check out the examples of complete agent implementations
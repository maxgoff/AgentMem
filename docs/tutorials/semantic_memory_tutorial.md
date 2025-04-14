# Semantic Memory Tutorial

This tutorial will guide you through using AgentMem's Semantic Memory module to store, retrieve, and query factual knowledge for AI agents.

## What is Semantic Memory?

Semantic memory stores factual knowledge and concepts that are not tied to specific events or experiences. This is the type of memory an agent would use to remember facts like "Paris is the capital of France" or "Python is a programming language." Unlike episodic memory, semantic memory doesn't track when the information was learned, just the knowledge itself.

## Setup

First, let's import the necessary components and create a semantic memory store:

```python
from agentmem.semantic import SemanticMemory
from uuid import UUID

# Create an in-memory semantic memory store (no persistence)
memory = SemanticMemory()

# Alternatively, create a persistent semantic memory store
# memory = SemanticMemory(persistence="./memory_data")

# With vector search for semantic similarity
# memory = SemanticMemory(persistence="./memory_data", vector_search=True)
```

## Storing Facts

Let's store some facts in semantic memory:

```python
# Store geographic facts
paris_id = memory.create(
    content="Paris is the capital of France",
    category="geography",
    tags=["europe", "cities", "capitals"]
)

tokyo_id = memory.create(
    content="Tokyo is the capital of Japan",
    category="geography",
    tags=["asia", "cities", "capitals"]
)

# Store facts about programming
python_id = memory.create(
    content="Python is a high-level, interpreted programming language",
    category="programming",
    tags=["languages", "python", "computer-science"]
)

# Store facts with additional metadata
javascript_id = memory.create(
    content="JavaScript is a scripting language used for web development",
    category="programming",
    tags=["languages", "javascript", "web-development"],
    metadata={
        "creator": "Brendan Eich", 
        "year": 1995
    }
)
```

## Retrieving Facts

You can retrieve facts using their unique ID:

```python
# Retrieve a specific fact
paris_fact = memory.read(paris_id)
print(f"ID: {paris_fact['id']}")
print(f"Content: {paris_fact['content']}")
print(f"Category: {paris_fact['category']}")
print(f"Tags: {paris_fact['tags']}")
print(f"Created: {paris_fact['created_at']}")
```

## Updating Facts

Facts can be updated when new information is available:

```python
# Update content
memory.update(
    python_id,
    content="Python is a high-level, interpreted programming language created by Guido van Rossum"
)

# Update metadata
memory.update(
    javascript_id,
    metadata={"popularity": "very high", "typing": "dynamic"}
)

# Update tags
memory.update(
    tokyo_id,
    tags=["asia", "cities", "capitals", "olympics"]
)
```

## Querying Facts

You can search for facts in various ways:

```python
# Simple keyword search
capital_facts = memory.query("capital")
print(f"Found {len(capital_facts)} facts about capitals")

# Filter by category
geography_facts = memory.query("", category="geography")
print(f"Found {len(geography_facts)} geography facts")

# Filter by tags
programming_langs = memory.query("", tags=["languages"])
print(f"Found {len(programming_langs)} programming language facts")

# Combine search query and filters
european_capitals = memory.query("capital", tags=["europe"])
print(f"Found {len(european_capitals)} European capital facts")
```

## Using Vector Search

If you've enabled vector search, you can perform semantic similarity searches that go beyond simple keyword matching:

```python
# Create a memory store with vector search enabled
semantic_memory = SemanticMemory(vector_search=True)

# Add some facts
semantic_memory.create(
    content="The Earth revolves around the Sun",
    category="astronomy"
)

semantic_memory.create(
    content="Saturn has distinctive rings visible from Earth",
    category="astronomy"
)

semantic_memory.create(
    content="Cats are carnivorous mammals with retractable claws",
    category="biology"
)

# Semantic search - this will find facts about planets without using the word "planet"
planet_facts = semantic_memory.query(
    "planets in our solar system", 
    use_vector=True,
    n_results=5
)

for fact in planet_facts:
    print(f"Content: {fact['content']}")
    if 'similarity_score' in fact:
        print(f"Similarity: {fact['similarity_score']:.2f}")
    print("-" * 30)
```

## Deleting Facts

When facts are no longer needed or become outdated:

```python
# Delete a fact
memory.delete(paris_id)

# Verify it's gone
try:
    memory.read(paris_id)
except KeyError:
    print("The fact has been successfully deleted")
```

## Persistence

If you created your memory store with persistence, you can save and load all memories:

```python
# Create a persistent memory store
persistent_memory = SemanticMemory(persistence="./memory_data")

# Add some facts
persistent_memory.create(
    content="Mercury is the closest planet to the Sun",
    category="astronomy"
)

# Save all memories to disk
persistent_memory.save_all()

# In a new session, load all memories from disk
persistent_memory.load_all()

# Or, memories are automatically loaded from persistence when available
# during initialization
```

## Practical Application

Let's see how semantic memory might be used in a simple agent:

```python
class KnowledgeAgent:
    def __init__(self):
        self.semantic_memory = SemanticMemory(persistence="./knowledge_base")
        
    def learn_fact(self, fact, category=None, tags=None):
        """Store a new fact in the agent's knowledge base"""
        fact_id = self.semantic_memory.create(
            content=fact,
            category=category or "general",
            tags=tags or []
        )
        return fact_id
        
    def recall_knowledge(self, topic):
        """Recall facts related to a topic"""
        facts = self.semantic_memory.query(topic)
        return [fact["content"] for fact in facts]
    
    def check_category(self, topic, category):
        """Check for facts in a specific category"""
        facts = self.semantic_memory.query(topic, category=category)
        return [fact["content"] for fact in facts]

# Create an agent and teach it some facts
agent = KnowledgeAgent()
agent.learn_fact(
    "The Great Wall of China is over 13,000 miles long", 
    category="landmarks", 
    tags=["china", "architecture"]
)
agent.learn_fact(
    "The Eiffel Tower is 330 meters tall", 
    category="landmarks", 
    tags=["france", "architecture"]
)

# Ask the agent what it knows about landmarks
print(agent.check_category("", "landmarks"))

# Ask specifically about China
print(agent.recall_knowledge("China"))
```

## Advanced Usage

### Categorization Schemes

For more sophisticated agents, you might want to implement a hierarchical categorization scheme:

```python
def add_hierarchical_fact(memory, content, hierarchy, tags=None):
    """Add a fact with hierarchical categorization"""
    # Example hierarchy: ["science", "physics", "mechanics"]
    category = hierarchy[0] if hierarchy else "general"
    
    # Create additional metadata with full hierarchy
    metadata = {
        "hierarchy": hierarchy,
        "hierarchy_level": len(hierarchy)
    }
    
    return memory.create(
        content=content,
        category=category,
        tags=tags or [],
        metadata=metadata
    )

# Usage
semantic_memory = SemanticMemory()
add_hierarchical_fact(
    semantic_memory,
    "Newton's First Law states that an object will remain at rest or in uniform motion unless acted upon by an external force",
    hierarchy=["science", "physics", "mechanics", "newton_laws"],
    tags=["newton", "motion", "physics"]
)
```

### Knowledge Graph Integration

Semantic memory can be combined with knowledge graph representations:

```python
def add_relationship(memory, subject, predicate, object, confidence=1.0):
    """Add a subject-predicate-object relationship to semantic memory"""
    fact_id = memory.create(
        content=f"{subject} {predicate} {object}",
        category="relationship",
        tags=[subject, object, predicate],
        metadata={
            "subject": subject,
            "predicate": predicate,
            "object": object,
            "confidence": confidence
        }
    )
    return fact_id

# Adding relationships
knowledge = SemanticMemory()
add_relationship(knowledge, "Paris", "is capital of", "France")
add_relationship(knowledge, "France", "is part of", "Europe")
add_relationship(knowledge, "Paris", "has landmark", "Eiffel Tower")

# Now we can query for relationships by entity
paris_facts = knowledge.query("Paris", tags=["Paris"])
for fact in paris_facts:
    print(fact["content"])
```

## Conclusion

Semantic memory provides a flexible way to store and retrieve factual knowledge for AI agents. By organizing information with categories, tags, and metadata, you can create sophisticated knowledge bases that support your agent's reasoning and response capabilities.

For more detailed information about the Semantic Memory API, see the [API Reference](../api/semantic_memory.md).
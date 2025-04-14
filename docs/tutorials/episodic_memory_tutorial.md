# Episodic Memory Tutorial

This tutorial will guide you through using AgentMem's Episodic Memory module to store, retrieve, and query experience-based memories for AI agents.

## What is Episodic Memory?

Episodic memory stores specific events and experiences tied to particular points in time. This is the type of memory an agent would use to remember interactions like "The user asked about file handling last week" or "I helped debug a recursive function yesterday." Unlike semantic memory which stores general knowledge, episodic memory captures the agent's personal experiences and the context in which they occurred.

## Setup

First, let's import the necessary components and create an episodic memory store:

```python
from agentmem.episodic import EpisodicMemory
from datetime import datetime, timedelta
from uuid import UUID

# Create an in-memory episodic memory store (no persistence)
memory = EpisodicMemory()

# Alternatively, create a persistent episodic memory store
# memory = EpisodicMemory(persistence="./memory_data")

# With vector search for semantic similarity
# memory = EpisodicMemory(persistence="./memory_data", vector_search=True)
```

## Storing Experiences

Let's store some experiences in episodic memory:

```python
# Store an interaction from today
today = datetime.now()
interaction_id = memory.create(
    content="User asked how to sort a list in Python",
    timestamp=today,
    context={
        "user_id": "user123",
        "conversation_id": "conv456",
        "platform": "web_interface"
    },
    importance=7
)

# Store an interaction from yesterday
yesterday = today - timedelta(days=1)
memory.create(
    content="Helped debug a recursive function that was causing a stack overflow",
    timestamp=yesterday,
    context={
        "user_id": "user456",
        "conversation_id": "conv789",
        "code_language": "JavaScript",
        "problem_type": "recursion"
    },
    importance=8
)

# Store an interaction from last week
last_week = today - timedelta(days=7)
memory.create(
    content="Explained the difference between lists and tuples in Python",
    timestamp=last_week,
    context={
        "user_id": "user123",
        "conversation_id": "conv123",
        "topic": "python-basics"
    },
    importance=5
)
```

## Retrieving Experiences

You can retrieve experiences using their unique ID:

```python
# Retrieve a specific experience
interaction = memory.read(interaction_id)
print(f"ID: {interaction['id']}")
print(f"Content: {interaction['content']}")
print(f"Timestamp: {interaction['timestamp']}")
print(f"Context: {interaction['context']}")
print(f"Importance: {interaction['importance']}")
```

## Updating Experiences

Experiences can be updated with additional context or to adjust their importance:

```python
# Update context with resolution information
memory.update(
    interaction_id,
    context={
        "resolved": True,
        "solution_provided": "Explained list.sort() method and sorted() function",
        "follow_up_required": False
    }
)

# Adjust importance based on new understanding
memory.update(
    interaction_id,
    importance=9  # This was more important than initially thought
)
```

## Querying Experiences

You can search for experiences in various ways:

```python
# Simple keyword search
python_interactions = memory.query("Python")
print(f"Found {len(python_interactions)} interactions about Python")

# Filter by time period
recent_interactions = memory.query(
    "",  # Empty string matches all
    start_time=today - timedelta(days=2),  # From 2 days ago
    end_time=today  # Up to now
)
print(f"Found {len(recent_interactions)} interactions in the last 2 days")

# Filter by importance level
important_interactions = memory.query(
    "",
    min_importance=7
)
print(f"Found {len(important_interactions)} important interactions")

# Filter by context keys
debugging_interactions = memory.query(
    "debug",
    context_keys=["problem_type"]
)
print(f"Found {len(debugging_interactions)} debugging interactions")

# Combining multiple filters
recent_important_python = memory.query(
    "Python",
    start_time=today - timedelta(days=3),
    min_importance=7
)
print(f"Found {len(recent_important_python)} recent important Python interactions")
```

## Using Vector Search

If you've enabled vector search, you can perform semantic similarity searches that go beyond simple keyword matching:

```python
# Create a memory store with vector search enabled
episodic_memory = EpisodicMemory(vector_search=True)

# Add some experiences
episodic_memory.create(
    content="User was confused about how inheritance works in object-oriented programming",
    context={"topic": "OOP", "language": "Python"}
)

episodic_memory.create(
    content="Explained polymorphism and method overriding in classes",
    context={"topic": "OOP", "language": "Java"}
)

episodic_memory.create(
    content="User needed help with file handling and exception management",
    context={"topic": "I/O", "language": "Python"}
)

# Semantic search - this will find experiences related to classes and objects
# even if they don't contain those exact words
oop_experiences = episodic_memory.query(
    "classes and objects in programming", 
    use_vector=True,
    n_results=5
)

for exp in oop_experiences:
    print(f"Content: {exp['content']}")
    if 'similarity_score' in exp:
        print(f"Similarity: {exp['similarity_score']:.2f}")
    print("-" * 30)
```

## Deleting Experiences

When experiences are no longer needed or must be forgotten:

```python
# Delete an experience
memory.delete(interaction_id)

# Verify it's gone
try:
    memory.read(interaction_id)
except KeyError:
    print("The experience has been successfully deleted")
```

## Persistence

If you created your memory store with persistence, you can save and load all memories:

```python
# Create a persistent memory store
persistent_memory = EpisodicMemory(persistence="./memory_data")

# Add an experience
persistent_memory.create(
    content="User requested help with deployment to AWS",
    context={"platform": "AWS", "service": "EC2"}
)

# Save all memories to disk
persistent_memory.save_all()

# In a new session, load all memories from disk
persistent_memory.load_all()

# Or, memories are automatically loaded from persistence when available
# during initialization
```

## Practical Application

Let's see how episodic memory might be used in a simple conversational agent:

```python
class ConversationalAgent:
    def __init__(self):
        self.episodic_memory = EpisodicMemory(persistence="./conversation_history")
        
    def record_interaction(self, user_id, message, **context):
        """Record a user interaction"""
        # Analyze importance based on content (simplified example)
        importance = 5  # Default importance
        if "urgent" in message.lower() or "problem" in message.lower():
            importance = 8
            
        # Store the interaction
        memory_id = self.episodic_memory.create(
            content=message,
            context={
                "user_id": user_id,
                "timestamp": datetime.now(),
                **context
            },
            importance=importance
        )
        return memory_id
        
    def get_conversation_history(self, user_id, days=7):
        """Get recent conversation history for a user"""
        start_time = datetime.now() - timedelta(days=days)
        
        # Query for interactions with this user in the specified time period
        interactions = self.episodic_memory.query(
            "",  # Empty query to match all content
            start_time=start_time,
            context_keys=["user_id"]
        )
        
        # Filter to specific user (done after query since context_keys just checks existence)
        user_interactions = [
            interaction for interaction in interactions 
            if interaction["context"]["user_id"] == user_id
        ]
        
        # Sort by timestamp (most recent first)
        user_interactions.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return user_interactions
    
    def recall_similar_topics(self, topic, n=3):
        """Find similar past topics discussed"""
        similar_interactions = self.episodic_memory.query(
            topic,
            use_vector=True,
            n_results=n
        )
        return similar_interactions

# Create an agent and record some interactions
agent = ConversationalAgent()
agent.record_interaction(
    "user123", 
    "I'm trying to connect my application to a MongoDB database",
    topic="databases", 
    resolved=False
)
agent.record_interaction(
    "user123", 
    "How do I use indexes to optimize my queries?",
    topic="database_optimization", 
    resolved=True
)

# Get conversation history for this user
history = agent.get_conversation_history("user123")
for interaction in history:
    print(f"User said: {interaction['content']}")
    print(f"Context: {interaction['context']}")
    print("-" * 30)

# Find similar past topics when user asks about PostgreSQL
similar = agent.recall_similar_topics("How do I connect to PostgreSQL?")
print("Similar past topics:")
for interaction in similar:
    print(f"- {interaction['content']}")
```

## Advanced Usage

### Temporal Patterns

Episodic memory can be used to detect patterns over time:

```python
def analyze_temporal_patterns(memory, user_id, topic=None, time_window_days=30):
    """Analyze how frequently a user discusses a particular topic"""
    start_time = datetime.now() - timedelta(days=time_window_days)
    
    # Get all interactions for this user in the time window
    query = topic if topic else ""
    interactions = memory.query(
        query,
        start_time=start_time
    )
    
    # Filter to the specific user
    user_interactions = [
        interaction for interaction in interactions 
        if interaction["context"].get("user_id") == user_id
    ]
    
    # Group by day
    interactions_by_day = {}
    for interaction in user_interactions:
        day = interaction["timestamp"].date()
        if day not in interactions_by_day:
            interactions_by_day[day] = []
        interactions_by_day[day].append(interaction)
    
    # Count interactions per day
    counts_by_day = {day: len(interactions) for day, interactions in interactions_by_day.items()}
    
    return {
        "total_interactions": len(user_interactions),
        "unique_days": len(interactions_by_day),
        "counts_by_day": counts_by_day,
        "average_per_day": len(user_interactions) / max(1, len(interactions_by_day))
    }
```

### Emotional Context Tracking

You can extend episodic memory to track emotional context:

```python
def record_emotional_interaction(memory, content, emotion, intensity, **context):
    """Record an interaction with emotional context"""
    return memory.create(
        content=content,
        context={
            **context,
            "emotion": emotion,
            "emotional_intensity": intensity
        },
        importance=min(10, 5 + intensity)  # Higher emotional intensity = higher importance
    )

# Usage
episodic_memory = EpisodicMemory()
record_emotional_interaction(
    episodic_memory,
    "User was frustrated because their code kept crashing",
    emotion="frustration",
    intensity=4,
    user_id="user123",
    topic="debugging"
)

# Query for emotionally charged interactions
frustrated_interactions = episodic_memory.query(
    "frustrated"
)
```

## Conclusion

Episodic memory provides a powerful way to store and retrieve an agent's experiences and interactions over time. By capturing not just what happened but also when it happened and the surrounding context, you can create agents that appear to remember past interactions and adapt their responses accordingly.

For more detailed information about the Episodic Memory API, see the [API Reference](../api/episodic_memory.md).
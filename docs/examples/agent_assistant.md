# Agent Assistant Example

The [agent_assistant.py](../examples/agent_assistant.py) example demonstrates how to build a conversational AI assistant that uses all three memory types to create a more intelligent and context-aware agent.

## What This Example Covers

- Creating an agent with integrated memory systems
- Storing and retrieving different types of knowledge
- Building conversational context using episodic memory
- Using procedural memory for response generation
- Leveraging semantic memory for factual knowledge

## Key Code Sections

### 1. Agent Architecture

```python
class MemoryEnabledAgent:
    def __init__(self, name="AgentMem Assistant", persistence_dir=None):
        """Initialize the agent with all memory types."""
        self.name = name
        self.semantic_memory = SemanticMemory(
            persistence=persistence_dir, 
            vector_search=True
        )
        self.episodic_memory = EpisodicMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        self.procedural_memory = ProceduralMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        self.conversation_history = []
```

The agent integrates all three memory types with vector search enabled for semantic understanding.

### 2. Knowledge Management

```python
def learn_fact(self, fact, category=None, tags=None):
    """Store a fact in semantic memory."""
    fact_id = self.semantic_memory.create(
        content=fact,
        category=category or "general",
        tags=tags or []
    )
    return fact_id

def remember_interaction(self, message, user="user", importance=5):
    """Record an interaction in episodic memory."""
    interaction_id = self.episodic_memory.create(
        content=message,
        context={
            "user": user,
            "conversation_id": self.conversation_id,
            "timestamp": datetime.now()
        },
        importance=importance
    )
    return interaction_id
```

The agent has specialized methods for storing different kinds of information in the appropriate memory type.

### 3. Response Generation

```python
def generate_response(self, user_input):
    """Generate a response based on user input and agent memory."""
    # Record this interaction
    self.remember_interaction(user_input)
    
    # Find relevant facts
    relevant_facts = self.semantic_memory.query(user_input, use_vector=True)
    
    # Find similar past interactions
    similar_interactions = self.episodic_memory.query(
        user_input, 
        use_vector=True,
        n_results=3
    )
    
    # Find relevant procedures
    relevant_procedures = self.procedural_memory.query(
        user_input,
        use_vector=True
    )
    
    # Use the retrieved knowledge to craft a response
    response = self._craft_response(
        user_input, 
        relevant_facts, 
        similar_interactions,
        relevant_procedures
    )
    
    # Remember the agent's response too
    self.remember_interaction(response, user=self.name)
    
    return response
```

The response generation process integrates information from all three memory types to create context-aware responses.

### 4. Knowledge Integration

```python
def _craft_response(self, query, facts, interactions, procedures):
    """Craft a response using retrieved memories."""
    # Simple response crafting for demonstration
    response_parts = []
    
    # Add factual knowledge if available
    if facts:
        response_parts.append(f"I know that: {facts[0]['content']}")
    
    # Reference similar past interactions if available
    if interactions:
        response_parts.append(
            f"I recall we discussed similar topics before: {interactions[0]['content']}"
        )
    
    # Include procedural knowledge if available
    if procedures:
        proc = procedures[0]
        response_parts.append(
            f"I can help with this. Here's how to {proc['task']}:"
        )
        for i, step in enumerate(proc['steps'], 1):
            response_parts.append(f"{i}. {step}")
    
    # If no specific knowledge, use a generic response
    if not response_parts:
        response_parts.append(
            "I don't have specific information about that yet. Can you tell me more?"
        )
    
    return "\n".join(response_parts)
```

The response crafting method integrates different types of knowledge into a coherent response.

### 5. Agent Initialization and Training

```python
# Initialize the agent with some knowledge
agent = MemoryEnabledAgent(persistence_dir="./agent_memory")

# Teach the agent some facts
agent.learn_fact(
    "Python is a high-level programming language created by Guido van Rossum",
    category="programming",
    tags=["python", "languages"]
)

# Teach the agent some procedures
agent.learn_procedure(
    "How to create a list in Python",
    steps=[
        "Define a list with square brackets: my_list = [1, 2, 3]",
        "Add items with append(): my_list.append(4)",
        "Access items with indexing: my_list[0]"
    ],
    domains=["programming", "python"]
)
```

The agent is initialized with some basic knowledge before interacting with users.

## Expected Output

The example demonstrates a conversation with the agent:

```
Agent: Hello! I'm AgentMem Assistant. How can I help you today?

User: What is Python?
Agent: I know that: Python is a high-level programming language created by Guido van Rossum

User: How do I create lists in Python?
Agent: I can help with this. Here's how to create a list in Python:
1. Define a list with square brackets: my_list = [1, 2, 3]
2. Add items with append(): my_list.append(4)
3. Access items with indexing: my_list[0]

User: Tell me more about Python
Agent: I know that: Python is a high-level programming language created by Guido van Rossum
I recall we discussed similar topics before: What is Python?
```

Notice how the agent incorporates both factual knowledge and the conversation history in its responses.

## Key Takeaways

1. **Integrated Memory**: Combining multiple memory types creates a more capable agent that can:
   - Recall factual knowledge (semantic memory)
   - Remember past interactions (episodic memory)
   - Know how to perform tasks (procedural memory)

2. **Context-Aware Responses**: The agent's responses improve as it gains more interaction history.

3. **Knowledge Management**: Different types of information are stored in appropriate memory structures.

4. **Persistence**: Agent knowledge can be saved and loaded between sessions.

## Next Steps

After exploring this example, you may want to enhance it by:

1. Adding more sophisticated response generation logic
2. Implementing memory prioritization based on relevance scores
3. Adding emotional context tracking in episodic memory
4. Creating a feedback loop to improve procedural knowledge

For more information on specific memory types, see their respective tutorials:
- [Semantic Memory Tutorial](../tutorials/semantic_memory_tutorial.md)
- [Episodic Memory Tutorial](../tutorials/episodic_memory_tutorial.md)
- [Procedural Memory Tutorial](../tutorials/procedural_memory_tutorial.md)
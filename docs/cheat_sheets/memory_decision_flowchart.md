# Memory Type Selection Flowchart

Use this flowchart to determine which type of memory is most appropriate for your use case.

```
                                    ┌───────────────────┐
                                    │ What are you      │
                                    │ trying to store?  │
                                    └─────────┬─────────┘
                                              │
              ┌───────────────────────────────┼───────────────────────────────┐
              │                               │                               │
              ▼                               ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐ ┌─────────────────────────────┐
│ Facts, information,         │ │ Events, experiences,         │ │ Steps, actions, workflows,  │
│ knowledge, relationships    │ │ interactions, conversations  │ │ how to perform tasks        │
└─────────────┬───────────────┘ └─────────────┬───────────────┘ └─────────────┬───────────────┘
              │                               │                               │
              ▼                               ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐ ┌─────────────────────────────┐
│ SEMANTIC MEMORY             │ │ EPISODIC MEMORY             │ │ PROCEDURAL MEMORY           │
└─────────────────────────────┘ └─────────────────────────────┘ └─────────────────────────────┘
              │                               │                               │
              ▼                               ▼                               ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐ ┌─────────────────────────────┐
│ • Knowledge bases           │ │ • Conversation history      │ │ • Task automation           │
│ • Reference information     │ │ • User interaction logs     │ │ • Step-by-step guides       │
│ • Facts & relationships     │ │ • Time-based experiences    │ │ • Action sequences          │
│ • Topic categorization      │ │ • Event timelines           │ │ • Skill repositories        │
└─────────────────────────────┘ └─────────────────────────────┘ └─────────────────────────────┘
```

## Detailed Decision Guide

### Use Semantic Memory when:
- You need to store factual knowledge that doesn't change frequently
- Information needs to be queried by content similarity
- You're building a knowledge base or reference system
- Relationships between concepts are important
- You need fast retrieval of facts by topic or similarity

### Use Episodic Memory when:
- Temporal context and sequence matter
- You need to track user interactions over time
- You're building a system that learns from past experiences
- You need to recall "what happened when"
- Context of past events influences current decisions
- You need to analyze patterns in historical interactions

### Use Procedural Memory when:
- You need to store instructions or workflows
- You want to codify "how to do something"
- You're creating task automation systems
- You need to retrieve or execute multi-step processes
- You're building systems that need to perform learned actions
- You want to store methods, not just data

### Use Multiple Memory Types when:
- Building complex AI assistants that require different types of knowledge
- Creating systems that learn from experience but also reference facts
- Implementing agents that need to know both what happened and how to respond
- Developing applications that need to remember facts, events, and procedures

## Common Use Case Examples

| Use Case | Recommended Memory Type | Example Implementation |
|----------|-------------------------|------------------------|
| Chatbot | Episodic + Semantic | Track conversation history + store user preferences |
| Knowledge Base | Semantic | Store structured information with vector search |
| Task Assistant | Procedural + Episodic | Store task procedures + remember past executions |
| Learning Agent | All Three Types | Facts + experiences + learned procedures |
| FAQ System | Semantic | Store question/answer pairs with similarity search |
| Process Automation | Procedural | Store step-by-step automation workflows |
| Customer Support | Episodic + Semantic | Track customer interactions + reference knowledge base |
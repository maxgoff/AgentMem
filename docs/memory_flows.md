# Memory Flows in AgentMem

This document illustrates how information flows through AgentMem's memory systems, demonstrating common patterns and use cases.

## Basic Memory Operations Flow

### Create Operation Flow

```
┌──────────────────┐
│ Client           │
│ create() call    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Memory subclass  │
│ implementation   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────┐
│ Create entry     │────►│ Generate UUID   │
│ instance         │     └─────────────────┘
└────────┬─────────┘
         │
         │                 ┌────────────────┐
         │                 │ Acquire lock   │
         │                 │ for operation  │
         ▼                 └────────┬───────┘
┌──────────────────┐              │
│ Enter transaction│◄─────────────┘
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Add to in-memory │
│ storage          │
└────────┬─────────┘
         │
         ├────────────────┬───────────────────┐
         │                │                   │
         ▼                ▼                   ▼
┌──────────────────┐   ┌─────────────────┐  ┌─────────────────┐
│ Save to          │   │ Add to vector   │  │ Add to logging  │
│ persistence      │   │ search          │  │ system          │
└────────┬─────────┘   └─────────┬───────┘  └─────────┬───────┘
         │                       │                    │
         └───────────────────────┼────────────────────┘
                                 │
                                 ▼
                         ┌─────────────────┐
                         │ Release lock    │
                         │ and commit      │
                         └─────────┬───────┘
                                   │
                                   ▼
                         ┌─────────────────┐
                         │ Return memory   │
                         │ ID to client    │
                         └─────────────────┘
```

### Read Operation Flow

```
┌──────────────────┐
│ Client           │
│ read() call      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────┐
│ Memory subclass  │────►│ Acquire lock    │
│ implementation   │     │ for memory ID   │
└────────┬─────────┘     └─────────┬───────┘
         │                         │
         └─────────────────────────┘
         │
         ▼
┌──────────────────┐
│ Check in-memory  │
│ storage          │
└────────┬─────────┘
         │
         │
         ├─────────Yes─┐
         │             ▼
    No   │    ┌─────────────────┐
         │    │ Return memory   │
         │    │ entry           │
         │    └─────────────────┘
         ▼
┌──────────────────┐
│ Check persistent │
│ storage          │
└────────┬─────────┘
         │
         │
         ├─────────Yes─┐
         │             ▼
    No   │    ┌─────────────────┐     ┌─────────────────┐
         │    │ Load from       │────►│ Cache in memory │
         │    │ persistence     │     └─────────┬───────┘
         │    └─────────────────┘               │
         │                                       │
         │                                       ▼
         │                              ┌─────────────────┐
         │                              │ Return memory   │
         │                              │ entry           │
         │                              └─────────────────┘
         ▼
┌──────────────────┐
│ Raise KeyError   │
└──────────────────┘
```

### Query Operation Flow

```
┌──────────────────┐
│ Client           │
│ query() call     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────┐
│ Memory subclass  │────►│ Acquire lock    │
│ implementation   │     │ for memory type │
└────────┬─────────┘     └─────────┬───────┘
         │                         │
         └─────────────────────────┘
         │
         ▼
┌──────────────────┐
│ Determine query  │
│ type             │
└────────┬─────────┘
         │
         ├────────────┬────────────────┐
         │            │                │
         ▼            ▼                ▼
┌──────────────┐ ┌────────────┐ ┌─────────────────┐
│Basic keyword │ │Category or │ │Vector-based     │
│search        │ │tag filter  │ │semantic search  │
└──────┬───────┘ └────┬───────┘ └────────┬────────┘
       │              │                  │
       └──────────────┼──────────────────┘
                      │
                      ▼
              ┌─────────────────┐
              │ Process results │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Apply additional│
              │ filters         │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Sort results    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Release lock    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Return results  │
              │ to client       │
              └─────────────────┘
```

## Memory Interaction Patterns

### Semantic Memory Use Flow

```
┌───────────────────────┐
│ Agent needs factual   │
│ information           │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Formulate query based │
│ on needed information │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Query semantic memory │
│ with search terms     │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Filter results based  │
│ on category or tags   │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Evaluate relevance of │
│ results to query      │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Integrate factual     │
│ information into      │
│ agent reasoning       │
└───────────────────────┘
```

### Episodic Memory Use Flow

```
┌───────────────────────┐
│ Agent encounters new  │
│ experience/interaction│
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Create episodic memory│
│ with context and time │
└───────────┬───────────┘
            │
            │
            │   ┌───────────────────────┐
            │   │ Agent needs to recall │
            │   │ past experience       │
            │   └───────────┬───────────┘
            │               │
            │               ▼
            │   ┌───────────────────────┐
            │   │ Formulate query based │
            │   │ on time or context    │
            │   └───────────┬───────────┘
            │               │
            ▼               ▼
┌───────────────────────┐   │
│ Update existing       │   │
│ episodic memories     │   │
└───────────┬───────────┘   │
            │               │
            ▼               ▼
┌───────────────────────┐   │
│ Analyze temporal      │   │
│ patterns in episodes  │   │
└───────────┬───────────┘   │
            │               │
            │               │
            │   ┌───────────▼───────────┐
            └──►│ Retrieve relevant     │
                │ episodic memories     │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ Use recalled context  │
                │ for better response   │
                └───────────────────────┘
```

### Procedural Memory Use Flow

```
┌───────────────────────┐
│ Agent learns how to   │
│ perform a task        │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Decompose task into   │
│ sequential steps      │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Create procedural     │
│ memory with steps     │
└───────────┬───────────┘
            │
            │
            │   ┌───────────────────────┐
            │   │ Agent needs to perform│
            │   │ a task                │
            │   └───────────┬───────────┘
            │               │
            │               ▼
            │   ┌───────────────────────┐
            │   │ Formulate query based │
            │   │ on task description   │
            │   └───────────┬───────────┘
            │               │
            ▼               ▼
┌───────────────────────┐   │
│ Refine procedure      │   │
│ based on experience   │   │
└───────────┬───────────┘   │
            │               │
            ▼               ▼
┌───────────────────────┐   │
│ Optimize steps for    │   │
│ better performance    │   │
└───────────┬───────────┘   │
            │               │
            │               │
            │   ┌───────────▼───────────┐
            └──►│ Retrieve procedure    │
                │ with execution steps  │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ Execute procedure     │
                │ steps in sequence     │
                └───────────────────────┘
```

## Advanced Memory Flows

### Vector Search Flow

```
┌───────────────────────┐
│ Client semantic query │
│ with vector_search=True
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Prepare query vector  │
│ using text embedding  │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Search vector DB for  │
│ similar content       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Get memory IDs with   │
│ similarity scores     │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Retrieve full memory  │
│ content for each ID   │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Apply additional      │
│ filters from query    │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Return results with   │
│ similarity scores     │
└───────────────────────┘
```

### Persistence Flow

```
┌───────────────────────┐
│ Memory operation      │
│ creates/updates entry │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Check if persistence  │
│ is enabled            │
└───────────┬───────────┘
            │
            │
       Yes  │
            │    No
            ├───────────────┐
            │               │
            ▼               │
┌───────────────────────┐   │
│ Convert entry to      │   │
│ serializable dict     │   │
└───────────┬───────────┘   │
            │               │
            ▼               │
┌───────────────────────┐   │
│ Determine file path   │   │
│ for entry             │   │
└───────────┬───────────┘   │
            │               │
            ▼               │
┌───────────────────────┐   │
│ Write JSON data       │   │
│ to file system        │   │
└───────────┬───────────┘   │
            │               │
            └───────────────┘
            │
            ▼
┌───────────────────────┐
│ Continue with memory  │
│ operation             │
└───────────────────────┘
```

### Concurrency Management Flow

```
┌───────────────────────┐
│ Memory operation      │
│ begins                │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Determine required    │
│ lock type             │
└───────────┬───────────┘
            │
            ├──────────────┬────────────────┐
            │              │                │
            ▼              ▼                ▼
┌──────────────────┐ ┌────────────┐ ┌─────────────────┐
│Memory ID lock    │ │Memory type │ │Transaction lock │
│(single entry)    │ │lock (all)  │ │(multiple IDs)   │
└──────┬───────────┘ └────┬───────┘ └────────┬────────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                  ┌─────────────────┐
                  │ Try to acquire  │
                  │ lock            │
                  └────────┬────────┘
                           │
                           │
                     Yes   │    No
                           ├──────────────┐
                           │              │
                           ▼              ▼
                  ┌─────────────────┐ ┌────────────────┐
                  │ Execute memory  │ │ Wait for lock  │
                  │ operation       │ │ with timeout   │
                  └────────┬────────┘ └────────┬───────┘
                           │                   │
                           ▼                   │
                  ┌─────────────────┐          │
                  │ Release lock    │◄─────────┘
                  │ when finished   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Return result   │
                  │ to caller       │
                  └─────────────────┘
```

## Agent Integration Patterns

### Adding Knowledge to Agent Memory

```
┌───────────────────────┐
│ Agent receives new    │
│ information           │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Classify information  │
│ type                  │
└───────────┬───────────┘
            │
            ├──────────────┬────────────────┐
            │              │                │
            ▼              ▼                ▼
┌──────────────────┐ ┌────────────┐ ┌─────────────────┐
│Factual knowledge │ │Experience  │ │Procedure/skill  │
│(semantic)        │ │(episodic)  │ │(procedural)     │
└──────┬───────────┘ └────┬───────┘ └────────┬────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────────┐ ┌────────────┐ ┌─────────────────┐
│Add category/tags │ │Add context │ │Extract steps &   │
│& metadata        │ │& metadata  │ │prerequisites     │
└──────┬───────────┘ └────┬───────┘ └────────┬────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────────┐ ┌────────────┐ ┌─────────────────┐
│semantic.create() │ │episodic.   │ │procedural.      │
│                  │ │create()    │ │create()         │
└──────┬───────────┘ └────┬───────┘ └────────┬────────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                   ┌────────────────┐
                   │Update agent's  │
                   │internal state  │
                   └────────────────┘
```

### Retrieving Memory for Agent Response

```
┌───────────────────────┐
│ Agent needs to        │
│ respond to input      │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Analyze what types of │
│ memory are relevant   │
└───────────┬───────────┘
            │
            ├─────────────────┬─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
┌────────────────────┐ ┌─────────────────┐ ┌────────────────┐
│Need facts or       │ │Need context from│ │Need to perform │
│knowledge? (semantic)│ │history?(episodic)│ │task?(procedural)│
└──────────┬─────────┘ └────────┬────────┘ └───────┬────────┘
           │                    │                  │
           ▼                    ▼                  ▼
┌────────────────────┐ ┌─────────────────┐ ┌────────────────┐
│semantic.query()    │ │episodic.query() │ │procedural.query()
│with vector search  │ │with time filters│ │with task match  │
└──────────┬─────────┘ └────────┬────────┘ └───────┬────────┘
           │                    │                  │
           └────────────────────┼──────────────────┘
                                │
                                ▼
                      ┌─────────────────────┐
                      │Integrate retrieved  │
                      │memories into response│
                      └─────────────────────┘
```

## End-to-End User Scenario

### Chatbot with Memory - User Interaction Flow

```
┌───────────────────────┐
│ User sends message    │
│ to chatbot            │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Agent processes       │
│ message content       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Record interaction in │
│ episodic memory       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Extract user facts    │
│ (if present)          │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Store facts in        │
│ semantic memory       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Query memory for      │
│ related information   │
└───────────┬───────────┘
            │
            ├───────────────┬───────────────┐
            │               │               │
            ▼               ▼               ▼
┌────────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│Retrieve relevant   │ │Recall previous  │ │Find relevant    │
│knowledge (semantic)│ │messages(episodic)│ │skills(procedural)│
└──────────┬─────────┘ └────────┬────────┘ └────────┬────────┘
           │                    │                   │
           └────────────────────┼───────────────────┘
                                │
                                ▼
                      ┌─────────────────────┐
                      │Generate personalized│
                      │response            │
                      └─────────┬───────────┘
                                │
                                ▼
                      ┌─────────────────────┐
                      │Record response in   │
                      │episodic memory      │
                      └─────────┬───────────┘
                                │
                                ▼
                      ┌─────────────────────┐
                      │Send response to user│
                      └─────────────────────┘
```

### Knowledge Base - Information Lookup Flow

```
┌───────────────────────┐
│ User queries          │
│ knowledge base        │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Process query into    │
│ structured form       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Record query in       │
│ episodic memory       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Execute semantic      │
│ query with vector     │
│ search enabled        │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Check for relevant    │
│ relationships         │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Apply inference rules │
│ from procedural memory│
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Prioritize results    │
│ based on confidence   │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Format response with  │
│ source information    │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Return results to user│
└───────────────────────┘
```

### Learning Agent - Task Execution Flow

```
┌───────────────────────┐
│ Agent receives        │
│ task to perform       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Search for relevant   │
│ procedural memories   │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Analyze past attempts │
│ in episodic memory    │
└───────────┬───────────┘
            │
            ├──────────Yes──┐
            │                ▼
┌───────────────────┐    ┌────────────────┐
│Determine if known │    │ Choose action  │
│skill exists       │    │ based on skill │
└───────┬───────────┘    └────────┬───────┘
        │ No                      │
        ▼                         │
┌───────────────────┐             │
│ Explore new       │             │
│ action            │             │
└───────┬───────────┘             │
        │                         │
        └─────────────────────────┘
        │
        ▼
┌───────────────────────┐
│ Execute chosen action │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Observe results and   │
│ success status        │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Record experience     │
│ in episodic memory    │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Update procedural     │
│ memory with results   │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Extract knowledge     │
│ into semantic memory  │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Adjust learning       │
│ parameters            │
└───────────────────────┘
```

These flow diagrams provide a comprehensive view of how information moves through AgentMem in various usage scenarios, from basic operations to complex agent integration patterns.
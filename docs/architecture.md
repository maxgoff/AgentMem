# AgentMem Architecture

This document provides architectural diagrams and explanations of AgentMem's components and how they interact.

## System Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                            AgentMem System                             │
│                                                                       │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────────────┐  │
│  │ Semantic Memory│    │ Episodic Memory│    │ Procedural Memory     │  │
│  │ (Facts)        │    │ (Experiences)  │    │ (Skills/Procedures)   │  │
│  └───────┬───────┘    └───────┬───────┘    └───────────┬───────────┘  │
│          │                    │                        │              │
│          └──────────┬─────────┴────────────┬──────────┘              │
│                     │                      │                         │
│              ┌──────▼──────────┐   ┌───────▼─────────┐               │
│              │  Memory Base     │   │  Concurrency    │               │
│              │  Infrastructure  │   │  Management     │               │
│              └──────┬──────────┘   └───────┬─────────┘               │
│                     │                      │                         │
│                     └──────────┬───────────┘                         │
│                                │                                     │
│                        ┌───────▼────────┐                            │
│                        │  Storage Layer  │                            │
│                        └───────┬────────┘                            │
│                                │                                     │
│           ┌────────────────────┼─────────────────────┐               │
│           │                    │                     │               │
│  ┌────────▼────────┐  ┌────────▼────────┐  ┌─────────▼───────┐       │
│  │  In-Memory      │  │  File           │  │  Vector         │       │
│  │  Storage        │  │  Storage        │  │  Storage        │       │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘       │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
  ┌───────────────────────────────────────────────────────────────────┐
  │                          Client Applications                       │
  └───────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Memory Types

AgentMem implements three core memory types:

1. **Semantic Memory**: Stores factual knowledge and concepts
   - Implemented as `SemanticMemory` class
   - Entries contain content, category, and tags
   - Optimized for fact retrieval and knowledge organization

2. **Episodic Memory**: Stores experience-based memories with temporal context
   - Implemented as `EpisodicMemory` class
   - Entries contain content, timestamp, context, and importance
   - Optimized for time-based and context-based retrieval

3. **Procedural Memory**: Stores task-related knowledge and procedures
   - Implemented as `ProceduralMemory` class
   - Entries contain task, steps, prerequisites, and domains
   - Optimized for skill and procedure retrieval

### Core Infrastructure

1. **Memory Base**: Abstract base class (`Memory`) that provides:
   - Common CRUD operations
   - Query interface
   - Standard metadata tracking
   - Integration with storage backends

2. **Concurrency Management**: Thread safety components:
   - Lock hierarchy to prevent deadlocks
   - Atomic transactions
   - ID-based and type-based locks
   - Lock monitoring facilities

3. **Storage Layer**: Storage system interface:
   - Abstract storage interface
   - Flexible backend implementations
   - Memory serialization and deserialization
   - Search capabilities

### Storage Backends

1. **In-Memory Storage**: Default storage mechanism
   - Fast, non-persistent dictionary-based storage
   - Suitable for temporary agents and testing

2. **File Storage**: Persistent file-based storage
   - JSON serialization of memory entries
   - Directory-based organization by memory type
   - Automatic load/save functionality

3. **Vector Storage**: Semantic similarity search
   - Embedding-based retrieval
   - Integration with sentence-transformers
   - Efficient similarity matching using ChromaDB

## Memory Flow

This diagram illustrates how information flows through the AgentMem system:

```
                        ┌─────────────────┐
                        │  Client Request │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Memory Type    │
                        │  Interface      │
                        └────────┬────────┘
                                 │
                     ┌───────────┴───────────┐
                     │                       │
                     ▼                       ▼
            ┌─────────────────┐     ┌─────────────────┐
            │  CRUD Operation │     │  Query Operation│
            └────────┬────────┘     └────────┬────────┘
                     │                       │
                     ▼                       ▼
            ┌─────────────────┐     ┌─────────────────┐
            │  Concurrency    │     │  Search         │
            │  Controls       │     │  Processing     │
            └────────┬────────┘     └────────┬────────┘
                     │                       │
                     ▼                       ▼
             ┌────────────────┐      ┌────────────────┐
             │ Storage Access │      │ Vector Search  │
             │ Operations     │      │ (Optional)     │
             └────────┬───────┘      └────────┬───────┘
                      │                       │
                      └───────────┬───────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │  Result         │
                        │  Processing     │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Client Response│
                        └─────────────────┘
```

## Memory Type Relationships

This diagram shows how the three memory types relate to each other:

```
                     ┌───────────────────────┐
                     │                       │
                     │    Knowledge Graph    │
                     │                       │
                     └───────────┬───────────┘
                                 │
                                 │ Contains
                                 │
          ┌────────────┬─────────┴────────────┬────────────┐
          │            │                      │            │
┌─────────▼────────┐   │                      │   ┌────────▼─────────┐
│                  │   │                      │   │                  │
│ Semantic Memory  │   │                      │   │ Procedural Memory│
│ (What)           │◄──┤                      ├──►│ (How)            │
│                  │   │                      │   │                  │
└─────────┬────────┘   │                      │   └────────┬─────────┘
          │            │                      │            │
          │ Provides   │                      │ Executes   │
          │ Context    │                      │ Skills     │
          │            │                      │            │
          │            │                      │            │
┌─────────▼────────┐   │                      │   ┌────────▼─────────┐
│                  │   │                      │   │                  │
│ Episodic Memory  │◄──┘                      └──►│ Agent Actions    │
│ (When/Where)     │      References               │ and Behaviors   │
│                  │                              │                  │
└──────────────────┘                              └──────────────────┘
```

## Data Structures

### MemoryEntry (Base Class)

```
┌─────────────────────────────────────┐
│ MemoryEntry                         │
├─────────────────────────────────────┤
│ id: UUID                            │
│ content: Any                        │
│ created_at: datetime                │
│ updated_at: datetime                │
│ metadata: Dict[str, Any]            │
└─────────────────────────────────────┘
```

### Memory Type Entries

```
┌─────────────────────────────────────┐
│ SemanticMemoryEntry                 │
├─────────────────────────────────────┤
│ Inherits from MemoryEntry           │
├─────────────────────────────────────┤
│ category: str                       │
│ tags: List[str]                     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ EpisodicMemoryEntry                 │
├─────────────────────────────────────┤
│ Inherits from MemoryEntry           │
├─────────────────────────────────────┤
│ timestamp: datetime                 │
│ context: Dict[str, Any]             │
│ importance: int                     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ProceduralMemoryEntry               │
├─────────────────────────────────────┤
│ Inherits from MemoryEntry           │
├─────────────────────────────────────┤
│ task: str                           │
│ steps: List[str]                    │
│ prerequisites: List[str]            │
│ domains: List[str]                  │
└─────────────────────────────────────┘
```

## Memory Interaction Patterns

### Semantic & Episodic Memory Integration

```
┌──────────────────────┐          ┌───────────────────────┐
│  Semantic Memory     │          │  Episodic Memory      │
│                      │          │                       │
│  - Facts             │          │  - Experiences        │
│  - Concepts          │          │  - Events             │
│  - Knowledge         │          │  - Interactions       │
└──────────┬───────────┘          └───────────┬───────────┘
           │                                  │
           │          ┌───────────┐           │
           └──────────► Context   ◄────────── ┘
                      │ Integration│                
                      └─────┬─────┘                
                            │                       
                            ▼                       
                  ┌───────────────────┐            
                  │  Enhanced Memory  │            
                  │  Retrieval        │            
                  └───────────────────┘            
```

### Memory & Action Integration

```
┌────────────────────┐       ┌────────────────────┐
│ Procedural Memory  │       │ Episodic Memory    │
│                    │       │                    │
│ - How to do tasks  │       │ - Past experiences │
└──────────┬─────────┘       └──────────┬─────────┘
           │                            │
           │                            │
           ▼                            ▼
┌────────────────────┐       ┌────────────────────┐
│ Action Selection   │◄──────┤ Context Evaluation │
└──────────┬─────────┘       └────────────────────┘
           │
           │
           ▼
┌────────────────────┐
│ Agent Behavior     │
└────────────────────┘
```

## Persistence Model

```
┌───────────────────────────────────────────────────────────┐
│                                                           │
│                     Memory Instances                      │
│                                                           │
└───────────────────────────┬───────────────────────────────┘
                            │
                            │ Serialization/Deserialization
                            ▼
┌───────────────────────────────────────────────────────────┐
│                                                           │
│                   Storage Backends                        │
│                                                           │
└───────────┬───────────────────┬───────────────────────────┘
            │                   │
            │                   │
┌───────────▼─────┐    ┌────────▼──────┐    ┌────────────────┐
│                 │    │                │    │                │
│ File System     │    │ Vector Database│    │ Future Backends│
│ (JSON files)    │    │ (ChromaDB)     │    │ (Databases)    │
│                 │    │                │    │                │
└─────────────────┘    └────────────────┘    └────────────────┘
```

## Concurrency Model

```
┌───────────────────────────────────────────────────────────┐
│                                                           │
│                      Lock Manager                         │
│                                                           │
└───────────┬───────────────────┬───────────────────────────┘
            │                   │
            │                   │
┌───────────▼─────┐    ┌────────▼──────┐    ┌────────────────┐
│                 │    │                │    │                │
│ Memory ID Locks │    │ Memory Type    │    │ Transaction    │
│ (Fine-grained)  │    │ Locks (Coarse) │    │ Locks          │
│                 │    │                │    │                │
└─────────────────┘    └────────────────┘    └────────────────┘
```

## Application Integration Example

This diagram shows how AgentMem integrates with a typical agent application:

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                     Agent Application                        │
│                                                              │
├──────────┬──────────────────────────────────┬───────────────┤
│          │                                  │               │
│ ┌────────▼───────┐      ┌──────────────────▼┐   ┌──────────▼─────────┐
│ │                │      │                   │   │                     │
│ │  Input         │      │  Reasoning        │   │  Output            │
│ │  Processing    │      │  Engine           │   │  Generation        │
│ │                │      │                   │   │                     │
│ └────────┬───────┘      └─────────┬─────────┘   └─────────┬───────────┘
│          │                        │                       │
└──────────┼────────────────────────┼───────────────────────┼────────────┘
           │                        │                       │
           │      ┌─────────────────▼─────────────────┐     │
           │      │                                   │     │
           └──────►            AgentMem               ◄─────┘
                  │                                   │
                  └───┬───────────────┬───────────────┘
                      │               │
                      │               │
         ┌────────────▼────┐   ┌──────▼───────────┐
         │                 │   │                  │
         │  Memory Store   │   │  Vector Search   │
         │                 │   │                  │
         └─────────────────┘   └──────────────────┘
```

## Vector Search Architecture

```
┌──────────────────────────────────┐
│                                  │
│          Query Text              │
│                                  │
└───────────────┬──────────────────┘
                │
                ▼
┌──────────────────────────────────┐
│                                  │
│     Sentence Transformer         │
│     (Text → Embeddings)          │
│                                  │
└───────────────┬──────────────────┘
                │
                ▼
┌──────────────────────────────────┐
│                                  │
│     Vector Database (ChromaDB)   │
│                                  │
└───────────────┬──────────────────┘
                │
                ▼
┌──────────────────────────────────┐
│                                  │
│     Similarity Matching          │
│     (Cosine Similarity)          │
│                                  │
└───────────────┬──────────────────┘
                │
                ▼
┌──────────────────────────────────┐
│                                  │
│    Memory ID + Similarity Score  │
│                                  │
└───────────────┬──────────────────┘
                │
                ▼
┌──────────────────────────────────┐
│                                  │
│    Memory Content Retrieval      │
│                                  │
└──────────────────────────────────┘
```

## End-to-End Flow Example

This diagram shows the end-to-end flow when an agent needs to retrieve information from memory:

```
┌──────────────────────┐
│ Agent receives input │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│Process and understand│
│ input                │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│Determine needed      │
│information (query)   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐    ┌─────────────────────┐
│Select memory type    │───►│ Semantic Memory     │
│based on query type   │    │ (facts & knowledge) │
│                      │    └─────────────────────┘
│                      │    ┌─────────────────────┐
│                      │───►│ Episodic Memory     │
│                      │    │ (past experiences)  │
│                      │    └─────────────────────┘
│                      │    ┌─────────────────────┐
│                      │───►│ Procedural Memory   │
└──────────┬───────────┘    │ (how to do things)  │
           │                └─────────────────────┘
           ▼
┌──────────────────────┐
│Apply query to        │
│selected memory       │
└──────────┬───────────┘
           │
           ├───────────────┐
           │               │
           ▼               ▼
┌──────────────────────┐  ┌─────────────────────┐
│Standard keyword      │  │Vector-based         │
│search                │  │semantic search      │
└──────────┬───────────┘  └─────────┬───────────┘
           │                        │
           └────────────┬───────────┘
                        │
                        ▼
┌──────────────────────────────────────┐
│Process retrieved memories            │
│(filter, sort, combine)               │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│Integrate retrieved information       │
│with agent's reasoning                │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│Generate response using               │
│retrieved memories                    │
└──────────────────────────────────────┘
```

This architecture documentation provides a comprehensive view of AgentMem's components, their relationships, and how they work together to provide memory capabilities for AI agents.
# Component Relationships in AgentMem

This document illustrates the relationships between AgentMem's components and how they work together to provide memory capabilities for AI agents.

## Core Component Hierarchy

```
                                  ┌────────────────┐
                                  │                │
                                  │    Memory      │
                                  │   (Abstract)   │
                                  │                │
                                  └───────┬────────┘
                                          │
                ┌────────────────────────┬┴─────────────────────────┐
                │                        │                          │
                │                        │                          │
       ┌────────▼─────────┐    ┌─────────▼──────────┐    ┌──────────▼─────────┐
       │                  │    │                    │    │                     │
       │  SemanticMemory  │    │  EpisodicMemory   │    │  ProceduralMemory   │
       │                  │    │                    │    │                     │
       └────────┬─────────┘    └─────────┬──────────┘    └──────────┬─────────┘
                │                        │                          │
                │                        │                          │
       ┌────────▼─────────┐    ┌─────────▼──────────┐    ┌──────────▼─────────┐
       │                  │    │                    │    │                     │
       │SemanticMemoryEntry│   │ EpisodicMemoryEntry│   │ProceduralMemoryEntry│
       │                  │    │                    │    │                     │
       └──────────────────┘    └────────────────────┘    └─────────────────────┘
```

## Storage System Relationships

```
                       ┌────────────────┐
                       │                │
                       │    Memory      │
                       │   (Abstract)   │
                       │                │
                       └───────┬────────┘
                               │
                               │ uses
                               │
                       ┌───────▼────────┐        ┌───────────────────┐
                       │                │        │                   │
                       │   Storage      │ uses   │   Concurrency     │
                       │   System       ├───────►│   Management      │
                       │                │        │                   │
                       └───────┬────────┘        └───────────────────┘
                               │
            ┌─────────────────┬┴───────────────────┐
            │                 │                    │
     ┌──────▼──────┐  ┌───────▼─────────┐  ┌───────▼────────┐
     │             │  │                 │  │                │
     │  In-Memory  │  │  FileStorage   │  │  VectorStorage │
     │  Dict       │  │                │  │                │
     │             │  │  JSON Files    │  │  ChromaDB      │
     │             │  │                │  │                │
     └─────────────┘  └─────────────────┘  └────────────────┘
```

## Memory Entry Relationships

```
                   ┌────────────────┐
                   │                │
                   │  MemoryEntry   │
                   │  (Base Class)  │
                   │                │
                   └───────┬────────┘
                           │ inherits
         ┌─────────────────┼───────────────────┐
         │                 │                   │
┌────────▼────────┐ ┌──────▼──────────┐ ┌──────▼───────────┐
│                 │ │                 │ │                  │
│SemanticMemoryEntry│ │EpisodicMemoryEntry│ │ProceduralMemoryEntry│
│                 │ │                 │ │                  │
│ content         │ │ content         │ │ content          │
│ category        │ │ timestamp       │ │ task             │
│ tags            │ │ context         │ │ steps            │
│                 │ │ importance      │ │ prerequisites    │
│                 │ │                 │ │ domains          │
└─────────────────┘ └─────────────────┘ └──────────────────┘
```

## Concurrency Management Relationships

```
                               ┌────────────────────┐
                               │                    │
                               │    LockManager     │
                               │                    │
                               └─────────┬──────────┘
                                         │
        ┌──────────────────────┬─────────┼─────────────────────┐
        │                      │         │                     │
┌───────▼─────────┐   ┌────────▼───────┐ │ ┌──────────────────▼┐
│                 │   │                │ │ │                   │
│  memory_id_lock │   │memory_type_lock│ │ │   transaction     │
│                 │   │                │ │ │                   │
└─────────────────┘   └────────────────┘ │ └───────────────────┘
                                         │                 
                                ┌────────▼──────────┐         
                                │                   │         
                                │   monitoring      │         
                                │                   │         
                                └───────────────────┘         
```

## Logging System Relationships

```
                        ┌────────────────┐
                        │                │
                        │  Memory        │
                        │  Operations    │
                        │                │
                        └───────┬────────┘
                                │
                                │ uses
                                ▼
             ┌───────────────────────────────────┐
             │                                   │
             │        Logging System             │
             │                                   │
             └──┬─────────────┬─────────────┬────┘
                │             │             │
        ┌───────▼────┐ ┌──────▼─────┐ ┌─────▼─────┐
        │            │ │            │ │           │
        │  Logger    │ │  Metrics   │ │  Memory   │
        │            │ │ Collector  │ │ Tracker   │
        │            │ │            │ │           │
        └────────────┘ └────────────┘ └───────────┘
```

## Operation Flow Relationships

```
                   ┌────────────────┐
                   │                │
                   │  Client Code   │
                   │                │
                   └───────┬────────┘
                           │
                           │ calls
                           ▼
                   ┌────────────────┐
                   │                │
                   │  Memory API    │
                   │                │
                   └───────┬────────┘
                           │
                           │ uses
        ┌─────────────────┬┴────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│               │ │               │ │               │
│ CRUD          │ │ Query         │ │ Vector        │
│ Operations    │ │ Operations    │ │ Operations    │
│               │ │               │ │               │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│               │ │               │ │               │
│ Storage       │ │ Filtering     │ │ Embedding     │
│ Access        │ │ & Sorting     │ │ & Similarity  │
│               │ │               │ │               │
└───────────────┘ └───────────────┘ └───────────────┘
```

## Memory Type Access Patterns

```
                  ┌────────────────────────┐
                  │                        │
                  │     Agent Application  │
                  │                        │
                  └────────────┬───────────┘
                               │
               ┌──────────────┴────────────┐
               │                           │
       ┌───────▼─────┐             ┌───────▼─────┐
       │             │ recommends  │             │
       │  Memory     │◄────────────┤  Query      │
       │  Selection  │             │  Analysis   │
       │             │             │             │
       └───────┬─────┘             └─────────────┘
               │
     ┌─────────┴──────┬────────────────┐
     │                │                │
     ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│              │ │              │ │              │
│ Semantic     │ │ Episodic     │ │ Procedural   │
│ Memory       │ │ Memory       │ │ Memory       │
│ (When?)      │ │ (What?)      │ │ (How?)       │
│              │ │              │ │              │
└──────┬───────┘ └────┬─────────┘ └────┬─────────┘
       │              │                │
       └──────────────┼────────────────┘
                      │
                      ▼
              ┌──────────────────┐
              │                  │
              │ Integrated       │
              │ Response         │
              │                  │
              └──────────────────┘
```

## Vector Search Component Relationships

```
                   ┌────────────────┐
                   │                │
                   │  Memory Query  │
                   │                │
                   └───────┬────────┘
                           │
                           │ uses if enabled
                           ▼
                   ┌────────────────┐
                   │                │
                   │ VectorStorage  │
                   │                │
                   └───────┬────────┘
                           │
               ┌───────────┴──────────┐
               │                      │
               │                      │
       ┌───────▼─────┐        ┌───────▼─────┐
       │             │        │             │
       │  Embedding  │        │  ChromaDB   │
       │  Model      │        │  Storage    │
       │             │        │             │
       └───────┬─────┘        └───────┬─────┘
               │                      │
               │                      │
               ▼                      ▼
       ┌───────────────┐      ┌───────────────┐
       │               │      │               │
       │ Text → Vector │      │ Vector Index  │
       │ Conversion    │      │ & Retrieval   │
       │               │      │               │
       └───────────────┘      └───────────────┘
```

## Persistence Flow Relationships

```
                 ┌────────────────────┐
                 │                    │
                 │  Memory Instance   │
                 │                    │
                 └──────────┬─────────┘
                            │
                            │ save/load
                            ▼
                 ┌────────────────────┐
                 │                    │
                 │  FileStorage       │
                 │                    │
                 └──────────┬─────────┘
                            │
                ┌───────────┴──────────┐
                │                      │
        ┌───────▼──────┐       ┌───────▼────────┐
        │              │       │                │
        │ Serialization│       │ File Path      │
        │ (JSON)       │       │ Determination  │
        │              │       │                │
        └───────┬──────┘       └───────┬────────┘
                │                      │
                │                      │
                ▼                      ▼
        ┌───────────────┐      ┌───────────────┐
        │               │      │               │
        │ Dict <-> JSON │      │ Directory &   │
        │ Conversion    │      │ File Creation │
        │               │      │               │
        └───────────────┘      └───────────────┘
```

## Agent Integration Relationships

```
                  ┌────────────────────────┐
                  │                        │
                  │     Agent Application  │
                  │                        │
                  └────────────┬───────────┘
                               │
                               │ uses
                               ▼
                  ┌────────────────────────┐
                  │                        │
                  │     AgentMem SDK       │
                  │                        │
                  └───┬────────────────┬───┘
                      │                │
          ┌───────────┴──┐        ┌────┴──────────┐
          │              │        │               │
┌─────────▼─────┐ ┌──────▼────┐  ┌▼───────────┐ ┌─▼─────────┐
│               │ │           │  │            │ │           │
│ Memory API    │ │ Storage   │  │ Concurrency│ │ Logging & │
│ Interfaces    │ │ Backend   │  │ Management │ │ Metrics   │
│               │ │           │  │            │ │           │
└───────────────┘ └───────────┘  └────────────┘ └───────────┘
```

## Application Use Case Relationships

```
                  ┌────────────────────────┐
                  │                        │
                  │      Agent Memory      │
                  │                        │
                  └────────────┬───────────┘
                               │
                               │ enables
            ┌──────────────────┼───────────────────┐
            │                  │                   │
    ┌───────▼─────┐    ┌───────▼─────┐    ┌────────▼───────┐
    │             │    │             │    │                │
    │  Chatbots   │    │ Knowledge   │    │ Learning       │
    │  & Assistants│    │ Bases      │    │ Agents         │
    │             │    │             │    │                │
    └───────┬─────┘    └───────┬─────┘    └────────┬───────┘
            │                  │                   │
            │                  │                   │
    ┌───────▼─────┐    ┌───────▼─────┐    ┌────────▼───────┐
    │             │    │             │    │                │
    │ Conversation│    │ Information │    │ Skill          │
    │ History     │    │ Retrieval   │    │ Acquisition    │
    │             │    │             │    │                │
    └─────────────┘    └─────────────┘    └────────────────┘
```

## Memory Type Usage Patterns

```
                    ┌────────────────────────┐
                    │                        │
                    │  Information Needs     │
                    │                        │
                    └────────────┬───────────┘
                                 │
                                 │ classified as
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼──────────┐     ┌───────▼─────────┐      ┌───────▼────────┐
│                  │     │                 │      │                │
│ Factual/Conceptual│     │ Temporal/Experiential│      │ Task/Procedural │
│ (What/Who)       │     │ (When/Where)    │      │ (How/Why)      │
│                  │     │                 │      │                │
└────────┬─────────┘     └─────────┬───────┘      └────────┬───────┘
         │                         │                       │
         │                         │                       │
         ▼                         ▼                       ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│ Use Semantic    │      │ Use Episodic    │      │ Use Procedural  │
│ Memory          │      │ Memory          │      │ Memory          │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Cross-Memory Integration

```
                    ┌────────────────────────┐
                    │                        │
                    │  Complex Agent Query   │
                    │                        │
                    └────────────┬───────────┘
                                 │
                                 │ requires
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼──────────┐     ┌───────▼─────────┐      ┌───────▼────────┐
│                  │     │                 │      │                │
│ Facts            │     │ Context         │      │ Actions        │
│ (Semantic)       │     │ (Episodic)      │      │ (Procedural)   │
│                  │     │                 │      │                │
└────────┬─────────┘     └─────────┬───────┘      └────────┬───────┘
         │                         │                       │
         │        integrated       │        informs        │
         └─────────────────────────┼───────────────────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │                    │
                         │  Integrated        │
                         │  Memory Response   │
                         │                    │
                         └────────────────────┘
```

## Logging and Metrics Relationships

```
                 ┌────────────────────────┐
                 │                        │
                 │    Memory Operations   │
                 │                        │
                 └─────────────┬──────────┘
                               │
                               │ tracked by
                ┌──────────────┴──────────────┐
                │                             │
        ┌───────▼─────────┐         ┌─────────▼─────────┐
        │                 │         │                   │
        │ Logger          │         │ Metrics Collector │
        │                 │         │                   │
        └─────┬───────────┘         └─────────┬─────────┘
              │                               │
     ┌────────┴────────┐           ┌──────────┴───────────┐
     │                 │           │                      │
┌────▼───┐  ┌──────────▼─┐    ┌────▼──────┐   ┌───────────▼──┐
│        │  │            │    │           │   │              │
│ Console│  │ File       │    │ Operation │   │ Memory Usage │
│ Output │  │ Output     │    │ Metrics   │   │ Tracking     │
│        │  │            │    │           │   │              │
└────────┘  └────────────┘    └───────────┘   └──────────────┘
```

## Vector Search Data Flow

```
                 ┌────────────────────────┐
                 │                        │
                 │    Query Text          │
                 │    "capital of France" │
                 └─────────────┬──────────┘
                               │
                               │ embeddings created
                               ▼
                 ┌────────────────────────┐
                 │                        │
                 │    Query Vector        │
                 │    [0.2, -0.5, 0.7...] │
                 └─────────────┬──────────┘
                               │
                               │ similarity search
                               ▼
            ┌─────────────────────────────────┐
            │                                 │
            │    Vector Database (ChromaDB)   │
            │                                 │
            └─────────────────┬───────────────┘
                              │
                              │ returns
                              ▼
            ┌─────────────────────────────────┐
            │                                 │
            │    Similar Vectors + Memory IDs │
            │    [(id1, 0.92), (id2, 0.87)]   │
            └─────────────────┬───────────────┘
                              │
                              │ lookup
                              ▼
            ┌─────────────────────────────────┐
            │                                 │
            │    Memory Content               │
            │    "Paris is the capital of..." │
            └─────────────────────────────────┘
```

These relationship diagrams provide a visual representation of how AgentMem's components interact and work together to provide memory capabilities for AI agents.
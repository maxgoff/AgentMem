"""
Basic usage examples for the AgentMem package.

This script demonstrates how to use the three main memory types:
- Semantic Memory: for factual knowledge
- Episodic Memory: for experience-based memories
- Procedural Memory: for task-related knowledge
"""

import uuid
from datetime import datetime, timedelta

from agentmem import SemanticMemory, EpisodicMemory, ProceduralMemory

def semantic_memory_demo():
    """Demonstrate semantic memory operations."""
    print("\n=== Semantic Memory Demo ===")
    
    # Create a semantic memory instance
    semantic_mem = SemanticMemory()
    
    # Store some facts
    fact1_id = semantic_mem.create(
        content="Paris is the capital of France",
        category="geography",
        tags=["cities", "countries", "europe"]
    )
    
    fact2_id = semantic_mem.create(
        content="Python is a programming language created by Guido van Rossum",
        category="technology",
        tags=["programming", "languages", "software"]
    )
    
    fact3_id = semantic_mem.create(
        content="The Pacific Ocean is the largest ocean on Earth",
        category="geography",
        tags=["oceans", "earth", "nature"]
    )
    
    # Read a fact
    paris_fact = semantic_mem.read(fact1_id)
    print(f"Fact: {paris_fact['content']}")
    print(f"Category: {paris_fact['category']}")
    print(f"Tags: {', '.join(paris_fact['tags'])}")
    
    # Update a fact
    semantic_mem.update(
        fact2_id,
        content="Python is a high-level programming language created by Guido van Rossum in 1991",
        tags=["programming", "languages", "software", "computer science"]
    )
    
    # Query semantic memory
    print("\nQuerying for 'ocean':")
    ocean_results = semantic_mem.query("ocean")
    for result in ocean_results:
        print(f"- {result['content']}")
    
    print("\nQuerying for geography category:")
    geography_results = semantic_mem.query("", category="geography")
    for result in geography_results:
        print(f"- {result['content']}")
    
    # Delete a fact
    semantic_mem.delete(fact3_id)
    
    print("\nAfter deletion, total facts:", len(semantic_mem._storage))


def episodic_memory_demo():
    """Demonstrate episodic memory operations."""
    print("\n=== Episodic Memory Demo ===")
    
    # Create an episodic memory instance
    episodic_mem = EpisodicMemory()
    
    # Store some events
    yesterday = datetime.now() - timedelta(days=1)
    last_week = datetime.now() - timedelta(days=7)
    
    event1_id = episodic_mem.create(
        content="User asked about Python file handling",
        timestamp=yesterday,
        context={"user_id": "user123", "topic": "programming"},
        importance=7
    )
    
    event2_id = episodic_mem.create(
        content="Explained recursive functions to the user",
        timestamp=last_week,
        context={"user_id": "user123", "topic": "programming"},
        importance=5
    )
    
    event3_id = episodic_mem.create(
        content="User requested information about climate change",
        timestamp=datetime.now(),
        context={"user_id": "user456", "topic": "science"},
        importance=8
    )
    
    # Read an event
    python_event = episodic_mem.read(event1_id)
    print(f"Event: {python_event['content']}")
    print(f"When: {python_event['timestamp']}")
    print(f"Importance: {python_event['importance']}/10")
    
    # Query episodic memory by time
    print("\nEvents from last week:")
    past_events = episodic_mem.query(
        "", 
        start_time=datetime.now() - timedelta(days=7),
        end_time=datetime.now()
    )
    for event in past_events:
        print(f"- {event['timestamp']}: {event['content']}")
    
    # Query by importance
    print("\nHigh importance events (>6):")
    important_events = episodic_mem.query("", min_importance=7)
    for event in important_events:
        print(f"- Importance {event['importance']}: {event['content']}")
    
    # Query by content and context
    print("\nProgramming-related events:")
    programming_events = episodic_mem.query(
        "Python",
        context_keys=["topic"]
    )
    for event in programming_events:
        print(f"- {event['content']} (Topic: {event['context']['topic']})")


def procedural_memory_demo():
    """Demonstrate procedural memory operations."""
    print("\n=== Procedural Memory Demo ===")
    
    # Create a procedural memory instance
    procedural_mem = ProceduralMemory()
    
    # Store some procedures
    proc1_id = procedural_mem.create(
        content="Creating files in Python",
        task="Create a new file",
        steps=[
            "Use open() with 'w' mode to create a file",
            "Write content using the write() method",
            "Close the file using close() or with statement"
        ],
        prerequisites=["Python installed", "Write permissions"],
        domains=["programming", "python", "file operations"]
    )
    
    proc2_id = procedural_mem.create(
        content="Installing a Python package",
        task="Install a package with pip",
        steps=[
            "Open a terminal or command prompt",
            "Run 'pip install package-name'",
            "Verify installation with 'pip list'"
        ],
        prerequisites=["Python installed", "pip installed", "Internet connection"],
        domains=["programming", "python", "package management"]
    )
    
    # Read a procedure
    file_proc = procedural_mem.read(proc1_id)
    print(f"Procedure: {file_proc['content']}")
    print(f"Task: {file_proc['task']}")
    print("Steps:")
    for i, step in enumerate(file_proc['steps'], 1):
        print(f"  {i}. {step}")
    
    # Query procedures
    print("\nProcedures related to 'file':")
    file_results = procedural_mem.query("file")
    for result in file_results:
        print(f"- {result['task']}")
    
    print("\nProcedures in the 'python' domain:")
    python_results = procedural_mem.query("", domain="python")
    for result in python_results:
        print(f"- {result['task']}")


if __name__ == "__main__":
    semantic_memory_demo()
    episodic_memory_demo()
    procedural_memory_demo()
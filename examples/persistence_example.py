"""
Example demonstrating persistent storage and vector search capabilities in AgentMem.

This script shows how to:
1. Create a semantic memory with file persistence
2. Store and retrieve facts with persistence across sessions
3. Use vector-based semantic search for more powerful retrieval
"""

import os
import shutil
import uuid
from datetime import datetime, timedelta

from agentmem import SemanticMemory


def setup_test_directories():
    """Set up test directories for persistence examples."""
    # Create temporary directories for this example
    persistence_dir = "./temp_memory_storage"
    vector_db_dir = "./temp_vector_db"
    
    # Clean up any existing directories
    for dir_path in [persistence_dir, vector_db_dir]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path)
    
    return persistence_dir, vector_db_dir


def file_persistence_demo(persistence_dir):
    """Demonstrate file-based persistence without vector search."""
    print("\n=== File Persistence Demo ===")
    
    # Create a semantic memory with file persistence
    print("Creating semantic memory with persistence...")
    semantic_mem = SemanticMemory(persistence=persistence_dir)
    
    # Add some facts that will be persisted
    print("Adding facts to semantic memory...")
    fact1_id = semantic_mem.create(
        content="Paris is the capital of France",
        category="geography",
        tags=["cities", "countries", "europe"]
    )
    
    fact2_id = semantic_mem.create(
        content="Python is a high-level programming language created by Guido van Rossum in 1991",
        category="technology",
        tags=["programming", "languages", "software"]
    )
    
    print(f"Added fact with ID: {fact1_id}")
    print(f"Added fact with ID: {fact2_id}")
    
    # Read facts to verify they're stored correctly
    fact = semantic_mem.read(fact1_id)
    print(f"\nStored fact: {fact['content']}")
    print(f"Category: {fact['category']}")
    print(f"Tags: {', '.join(fact['tags'])}")
    
    # Now, simulate restarting the application by creating a new memory instance
    print("\nSimulating application restart by creating new memory instance...")
    semantic_mem2 = SemanticMemory(persistence=persistence_dir)
    
    # Verify we can read the facts from the new instance
    fact = semantic_mem2.read(fact1_id)
    print(f"Retrieved fact after restart: {fact['content']}")
    
    # Update a fact in the new instance
    print("\nUpdating fact in new memory instance...")
    semantic_mem2.update(
        fact2_id, 
        content="Python is a high-level, interpreted programming language created by Guido van Rossum",
        tags=["programming", "languages", "software", "interpreted"]
    )
    
    # Read the updated fact
    updated_fact = semantic_mem2.read(fact2_id)
    print(f"Updated fact: {updated_fact['content']}")
    print(f"Updated tags: {', '.join(updated_fact['tags'])}")
    
    # Query by category
    print("\nQuerying by category 'geography':")
    geography_results = semantic_mem2.query("", category="geography")
    for result in geography_results:
        print(f"- {result['content']}")


def vector_search_demo(persistence_dir, vector_db_dir):
    """Demonstrate vector-based semantic search capabilities."""
    print("\n=== Vector Search Demo ===")
    
    # Create a semantic memory with both persistence and vector search
    print("Creating semantic memory with vector search...")
    semantic_mem = SemanticMemory(
        persistence=persistence_dir,
        vector_search=True,
        vector_db_path=vector_db_dir
    )
    
    # Add some facts for the vector search demo
    print("Adding facts to semantic memory...")
    facts = [
        {
            "content": "The Earth is the third planet from the Sun",
            "category": "astronomy",
            "tags": ["planets", "solar system", "space"]
        },
        {
            "content": "Jupiter is the largest planet in our solar system",
            "category": "astronomy",
            "tags": ["planets", "solar system", "space"]
        },
        {
            "content": "The Moon orbits the Earth and is our only natural satellite",
            "category": "astronomy", 
            "tags": ["moon", "earth", "space"]
        },
        {
            "content": "Water covers about 71% of Earth's surface",
            "category": "geography",
            "tags": ["earth", "water", "oceans"]
        },
        {
            "content": "Mount Everest is the highest mountain on Earth",
            "category": "geography",
            "tags": ["mountains", "earth", "geology"]
        },
        {
            "content": "The Pacific Ocean is the largest ocean on Earth",
            "category": "geography",
            "tags": ["oceans", "earth", "water"]
        }
    ]
    
    for fact in facts:
        semantic_mem.create(**fact)
    
    print(f"Added {len(facts)} facts to memory")
    
    # Perform a standard keyword search
    print("\nStandard keyword search for 'planet':")
    std_results = semantic_mem.query("planet", use_vector=False)
    for result in std_results:
        print(f"- {result['content']}")
    
    # Perform vector-based semantic search
    print("\nVector-based semantic search for 'celestial bodies':")
    vector_results = semantic_mem.query("celestial bodies")
    for result in vector_results:
        similarity = result.get("similarity_score", 0)
        print(f"- [{similarity:.2f}] {result['content']}")
    
    # Search with category filter
    print("\nVector search for 'water' in category 'geography':")
    filtered_results = semantic_mem.query("water", category="geography")
    for result in filtered_results:
        similarity = result.get("similarity_score", 0)
        print(f"- [{similarity:.2f}] {result['content']}")


def cleanup(persistence_dir, vector_db_dir):
    """Clean up temporary directories."""
    print("\nCleaning up temporary directories...")
    for dir_path in [persistence_dir, vector_db_dir]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)


if __name__ == "__main__":
    # Set up test directories
    persistence_dir, vector_db_dir = setup_test_directories()
    
    try:
        # Run demos
        file_persistence_demo(persistence_dir)
        vector_search_demo(persistence_dir, vector_db_dir)
    finally:
        # Clean up
        cleanup(persistence_dir, vector_db_dir)
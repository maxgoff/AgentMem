"""
Performance tests for the AgentMem package.

This script contains tests designed to evaluate the performance of
different memory types and storage backends under various loads.
"""
import os
import random
import shutil
import tempfile
import time
from datetime import datetime, timedelta

from agentmem import SemanticMemory, EpisodicMemory, ProceduralMemory


def generate_random_fact():
    """Generate a random factual statement for semantic memory testing."""
    subjects = ["The Earth", "Jupiter", "The Moon", "Mars", "Venus", "The Sun", 
                "The Milky Way", "Black holes", "Neutron stars", "Galaxies"]
    predicates = ["is", "has", "contains", "orbits", "exhibits", "possesses", 
                 "demonstrates", "shows", "reveals", "maintains"]
    objects = ["a rocky planet", "a gas giant", "a natural satellite", "a star", 
              "a celestial body", "an astronomical object", "a cosmic phenomenon",
              "a planetary feature", "an essential component", "a unique characteristic"]
    qualifiers = ["in our solar system", "in the universe", "known to science", 
                 "discovered so far", "studied by astronomers", "visible from Earth",
                 "according to recent research", "as evidenced by observations",
                 "based on current understanding", "supported by multiple studies"]
    
    return f"{random.choice(subjects)} {random.choice(predicates)} {random.choice(objects)} {random.choice(qualifiers)}"


def generate_random_event():
    """Generate a random event description for episodic memory testing."""
    actions = ["asked about", "inquired regarding", "requested information on", 
              "needed help with", "wanted to learn about", "was confused about",
              "sought clarification on", "expressed interest in", "was curious about",
              "needed assistance with"]
    topics = ["Python programming", "file handling", "data structures", "algorithms", 
             "machine learning", "database operations", "web development", 
             "network protocols", "system administration", "cloud computing"]
    details = ["basic concepts", "advanced techniques", "implementation details", 
              "best practices", "common pitfalls", "optimization strategies",
              "debugging approaches", "performance considerations", "security implications",
              "practical applications"]
    
    return f"User {random.choice(actions)} {random.choice(topics)} {random.choice(details)}"


def generate_random_procedure():
    """Generate a random procedure for procedural memory testing."""
    tasks = ["Create", "Implement", "Develop", "Design", "Build", "Construct", 
            "Establish", "Set up", "Configure", "Initialize"]
    objects = ["a file handling system", "a database connection", "an API endpoint", 
              "a machine learning model", "a web server", "a user authentication system",
              "a data processing pipeline", "a caching mechanism", "a logging framework",
              "a configuration manager"]
    
    steps = [
        f"Step 1: Define the requirements for the {random.choice(objects).split()[-1]}",
        f"Step 2: Set up the necessary environment",
        f"Step 3: Initialize the core components",
        f"Step 4: Implement the main functionality",
        f"Step 5: Add error handling and validation",
        f"Step 6: Test the implementation",
        f"Step 7: Optimize performance if needed",
        f"Step 8: Document the solution"
    ]
    
    # Randomly select 4-8 steps
    selected_steps = steps[:random.randint(4, 8)]
    
    return {
        "content": f"How to {random.choice(tasks).lower()} {random.choice(objects)}",
        "task": f"{random.choice(tasks)} {random.choice(objects)}",
        "steps": selected_steps,
        "domains": random.sample(["python", "programming", "software development", 
                               "computer science", "data engineering", "web development"], 
                               k=random.randint(1, 3))
    }


def test_semantic_memory_performance(num_entries=1000, print_interval=100):
    """
    Test semantic memory performance with a large number of entries.
    
    Args:
        num_entries: Number of entries to create
        print_interval: How often to print progress
    """
    print(f"\n=== Testing Semantic Memory Performance with {num_entries} entries ===")
    
    # Create a temporary directory for persistence
    temp_dir = tempfile.mkdtemp()
    persistence_dir = os.path.join(temp_dir, "persistence")
    vector_dir = os.path.join(temp_dir, "vector_db")
    
    try:
        # Test 1: In-memory storage
        print("\nTesting in-memory storage...")
        mem_only = SemanticMemory()
        
        # Measure creation time
        start_time = time.time()
        for i in range(num_entries):
            fact = generate_random_fact()
            category = random.choice(["astronomy", "physics", "geology", "science"])
            tags = random.sample(["space", "planets", "stars", "cosmos", "universe"], 
                                k=random.randint(1, 3))
            
            mem_only.create(content=fact, category=category, tags=tags)
            
            if (i + 1) % print_interval == 0:
                print(f"  Created {i + 1} entries")
        
        creation_time = time.time() - start_time
        print(f"Creation time for {num_entries} entries: {creation_time:.2f} seconds")
        
        # Measure query time
        start_time = time.time()
        query_results = mem_only.query("planet")
        query_time = time.time() - start_time
        print(f"Query time: {query_time:.4f} seconds, found {len(query_results)} results")
        
        # Test 2: Persistence storage
        print("\nTesting with file persistence...")
        persistent_mem = SemanticMemory(persistence=persistence_dir)
        
        # Measure creation time with persistence
        start_time = time.time()
        for i in range(num_entries // 10):  # Use fewer entries for persistence test
            fact = generate_random_fact()
            category = random.choice(["astronomy", "physics", "geology", "science"])
            tags = random.sample(["space", "planets", "stars", "cosmos", "universe"], 
                                k=random.randint(1, 3))
            
            persistent_mem.create(content=fact, category=category, tags=tags)
            
            if (i + 1) % (print_interval // 10) == 0:
                print(f"  Created {i + 1} entries")
        
        persistence_creation_time = time.time() - start_time
        print(f"Creation time with persistence for {num_entries // 10} entries: {persistence_creation_time:.2f} seconds")
        
        # Measure query time with persistence
        start_time = time.time()
        query_results = persistent_mem.query("planet")
        persistence_query_time = time.time() - start_time
        print(f"Query time with persistence: {persistence_query_time:.4f} seconds, found {len(query_results)} results")
        
        # Test 3: Vector search (with graceful fallback)
        print("\nTesting with vector search...")
        try:
            # Try to create with vector search
            from agentmem.base import VECTOR_SEARCH_AVAILABLE
            
            if not VECTOR_SEARCH_AVAILABLE:
                print("Vector search not available in this environment, skipping test.")
            else:
                vector_mem = SemanticMemory(
                    persistence=persistence_dir,
                    vector_search=True,
                    vector_db_path=vector_dir
                )
                
                if vector_mem._vector_search is None:
                    print("Vector search initialization failed, skipping test.")
                else:
                    # Measure creation time with vector search
                    start_time = time.time()
                    for i in range(num_entries // 20):  # Use even fewer entries for vector test
                        fact = generate_random_fact()
                        category = random.choice(["astronomy", "physics", "geology", "science"])
                        tags = random.sample(["space", "planets", "stars", "cosmos", "universe"], 
                                            k=random.randint(1, 3))
                        
                        vector_mem.create(content=fact, category=category, tags=tags)
                        
                        if (i + 1) % (print_interval // 20) == 0:
                            print(f"  Created {i + 1} entries")
                    
                    vector_creation_time = time.time() - start_time
                    print(f"Creation time with vector search for {num_entries // 20} entries: {vector_creation_time:.2f} seconds")
                    
                    # Measure standard query time
                    start_time = time.time()
                    query_results = vector_mem.query("planet", use_vector=False)
                    std_query_time = time.time() - start_time
                    print(f"Standard query time: {std_query_time:.4f} seconds, found {len(query_results)} results")
                    
                    # Measure vector query time
                    start_time = time.time()
                    query_results = vector_mem.query("celestial objects in space")
                    vector_query_time = time.time() - start_time
                    print(f"Vector query time: {vector_query_time:.4f} seconds, found {len(query_results)} results")
        except Exception as e:
            print(f"Error during vector search test: {str(e)}")
            print("This is expected on some environments due to compatibility issues.")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_episodic_memory_performance(num_entries=1000, print_interval=100):
    """
    Test episodic memory performance with a large number of entries.
    
    Args:
        num_entries: Number of entries to create
        print_interval: How often to print progress
    """
    print(f"\n=== Testing Episodic Memory Performance with {num_entries} entries ===")
    
    # Create a temporary directory for persistence
    temp_dir = tempfile.mkdtemp()
    persistence_dir = os.path.join(temp_dir, "persistence")
    
    try:
        # Test in-memory storage
        print("\nTesting in-memory storage...")
        memory = EpisodicMemory()
        
        # Generate a range of timestamps over the past month
        now = datetime.now()
        timestamps = [now - timedelta(days=random.randint(0, 30),
                                     hours=random.randint(0, 23),
                                     minutes=random.randint(0, 59))
                     for _ in range(num_entries)]
        
        # Measure creation time
        start_time = time.time()
        for i in range(num_entries):
            event = generate_random_event()
            timestamp = timestamps[i]
            importance = random.randint(1, 10)
            context = {
                "user_id": f"user{random.randint(100, 999)}",
                "topic": random.choice(["programming", "science", "math", "history"]),
                "session_id": f"session{random.randint(1000, 9999)}"
            }
            
            memory.create(content=event, timestamp=timestamp, 
                         importance=importance, context=context)
            
            if (i + 1) % print_interval == 0:
                print(f"  Created {i + 1} entries")
        
        creation_time = time.time() - start_time
        print(f"Creation time for {num_entries} entries: {creation_time:.2f} seconds")
        
        # Measure query by time range
        start_time = time.time()
        last_week = now - timedelta(days=7)
        query_results = memory.query("", start_time=last_week, end_time=now)
        time_query_time = time.time() - start_time
        print(f"Time range query: {time_query_time:.4f} seconds, found {len(query_results)} results")
        
        # Measure query by importance
        start_time = time.time()
        query_results = memory.query("", min_importance=8)
        importance_query_time = time.time() - start_time
        print(f"Importance query: {importance_query_time:.4f} seconds, found {len(query_results)} results")
        
        # Measure query by content
        start_time = time.time()
        query_results = memory.query("Python")
        content_query_time = time.time() - start_time
        print(f"Content query: {content_query_time:.4f} seconds, found {len(query_results)} results")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_procedural_memory_performance(num_entries=1000, print_interval=100):
    """
    Test procedural memory performance with a large number of entries.
    
    Args:
        num_entries: Number of entries to create
        print_interval: How often to print progress
    """
    print(f"\n=== Testing Procedural Memory Performance with {num_entries} entries ===")
    
    # Create a temporary directory for persistence
    temp_dir = tempfile.mkdtemp()
    persistence_dir = os.path.join(temp_dir, "persistence")
    
    try:
        # Test in-memory storage
        print("\nTesting in-memory storage...")
        memory = ProceduralMemory()
        
        # Measure creation time
        start_time = time.time()
        for i in range(num_entries):
            procedure = generate_random_procedure()
            memory.create(**procedure)
            
            if (i + 1) % print_interval == 0:
                print(f"  Created {i + 1} entries")
        
        creation_time = time.time() - start_time
        print(f"Creation time for {num_entries} entries: {creation_time:.2f} seconds")
        
        # Measure query by domain
        start_time = time.time()
        query_results = memory.query("", domain="python")
        domain_query_time = time.time() - start_time
        print(f"Domain query: {domain_query_time:.4f} seconds, found {len(query_results)} results")
        
        # Measure query by content
        start_time = time.time()
        query_results = memory.query("database")
        content_query_time = time.time() - start_time
        print(f"Content query: {content_query_time:.4f} seconds, found {len(query_results)} results")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # You can adjust these parameters based on your system's capabilities
    num_entries = 1000
    print_interval = 100
    
    test_semantic_memory_performance(num_entries, print_interval)
    test_episodic_memory_performance(num_entries, print_interval)
    test_procedural_memory_performance(num_entries, print_interval)
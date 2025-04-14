"""
Logging and Metrics Demo for AgentMem.

This example demonstrates how to use the logging and metrics 
systems to track performance, memory usage, and operations.
"""
import os
import random
import tempfile
import time
from datetime import datetime, timedelta

from agentmem import SemanticMemory
from agentmem.logging import (
    configure_logging,
    get_logger,
    LogLevel,
    get_metrics_collector,
    get_memory_tracker
)


def generate_random_facts(num_facts=100):
    """Generate a set of random facts for testing."""
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
    
    facts = []
    for _ in range(num_facts):
        fact = (
            f"{random.choice(subjects)} {random.choice(predicates)} "
            f"{random.choice(objects)} {random.choice(qualifiers)}"
        )
        category = random.choice(["astronomy", "physics", "geology", "science"])
        tags = random.sample(["space", "planets", "stars", "cosmos", "universe"], 
                            k=random.randint(1, 3))
        facts.append((fact, category, tags))
    
    return facts


def print_metrics_summary(metrics_collector):
    """Print a summary of collected metrics."""
    print("\n=== Metrics Summary ===")
    
    # Get operation statistics
    op_stats = metrics_collector.get_operation_stats()
    if op_stats:
        print("\nOperation Statistics:")
        for op_key, stats in op_stats.items():
            print(f"  {op_key}:")
            print(f"    Count: {stats['count']}")
            print(f"    Avg Duration: {stats['avg_duration']*1000:.2f} ms")
            print(f"    Max Duration: {stats['max_duration']*1000:.2f} ms")
            print(f"    Total Duration: {stats['total_duration']*1000:.2f} ms")
    
    # Get memory statistics
    mem_stats = metrics_collector.get_memory_stats()
    if mem_stats:
        print("\nMemory Statistics:")
        for mem_type, stats in mem_stats.items():
            print(f"  {mem_type}:")
            print(f"    Operation Count: {stats['operation_count']}")
            if stats['size_bytes'] > 0:
                size_kb = stats['size_bytes'] / 1024
                print(f"    Size: {size_kb:.2f} KB")
    
    # Get system metrics
    sys_metrics = metrics_collector.get_system_metrics()
    if sys_metrics:
        latest = sys_metrics[-1]
        print("\nLatest System Metrics:")
        print(f"  CPU Usage: {latest.get('cpu_percent', 'N/A')}%")
        print(f"  Memory RSS: {latest.get('memory_rss', 0) / (1024*1024):.2f} MB")
        print(f"  Threads: {latest.get('threads', 'N/A')}")


def main():
    """Run the logging and metrics demo."""
    print("=== AgentMem Logging and Metrics Demo ===")
    
    # Configure logging
    log_file = os.path.join(tempfile.gettempdir(), "agentmem_demo.log")
    configure_logging(
        log_level=LogLevel.DEBUG,
        log_file=log_file,
        console_output=True
    )
    
    logger = get_logger("demo")
    logger.info("Starting logging and metrics demo")
    print(f"Logging to file: {log_file}")
    
    # Create temporary directories for persistence and vector search
    temp_dir = tempfile.mkdtemp()
    persistence_dir = os.path.join(temp_dir, "persistence")
    vector_dir = os.path.join(temp_dir, "vector_db")
    os.makedirs(persistence_dir, exist_ok=True)
    os.makedirs(vector_dir, exist_ok=True)
    
    try:
        # Create semantic memory with all features enabled
        logger.info("Creating semantic memory with persistence and vector search")
        memory = SemanticMemory(
            persistence=persistence_dir,
            vector_search=True,
            vector_db_path=vector_dir
        )
        
        # Generate random facts
        logger.info("Generating random facts")
        facts = generate_random_facts(100)
        
        # Create memories
        logger.info("Creating memories")
        memory_ids = []
        for fact, category, tags in facts:
            memory_id = memory.create(
                content=fact,
                category=category,
                tags=tags
            )
            memory_ids.append(memory_id)
        
        # Perform various operations to generate metrics
        logger.info("Performing various operations")
        
        # Read operations
        for _ in range(20):
            memory_id = random.choice(memory_ids)
            memory.read(memory_id)
        
        # Update operations
        for _ in range(10):
            memory_id = random.choice(memory_ids)
            memory.update(
                memory_id,
                content=memory.read(memory_id)["content"] + " (updated)",
                tags=["updated"]
            )
        
        # Query operations
        for _ in range(15):
            query_terms = ["planet", "star", "cosmic", "universe", "Earth"]
            query = random.choice(query_terms)
            results = memory.query(query)
            logger.info(f"Query for '{query}' returned {len(results)} results")
        
        # Vector query operations
        for _ in range(5):
            query_texts = [
                "celestial bodies in space",
                "planetary phenomena",
                "astronomical discoveries",
                "cosmic events",
                "solar system objects"
            ]
            query = random.choice(query_texts)
            results = memory.query(query, use_vector=True)
            logger.info(f"Vector query for '{query}' returned {len(results)} results")
        
        # Save and load operations
        memory.save_all()
        memory.load_all()
        
        # Delete some memories
        for _ in range(5):
            memory_id = random.choice(memory_ids)
            memory.delete(memory_id)
            memory_ids.remove(memory_id)
        
        # Force memory usage update
        memory_tracker = get_memory_tracker()
        memory_tracker.update_memory_usage(force=True)
        
        # Get and print metrics
        metrics_collector = get_metrics_collector()
        print_metrics_summary(metrics_collector)
        
        # Print log file location
        print(f"\nFull logs are available at: {log_file}")
        
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        logger.info("Demo completed")


if __name__ == "__main__":
    main()
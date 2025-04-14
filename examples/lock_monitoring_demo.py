"""
Lock monitoring demo for AgentMem.

This example demonstrates how to use the lock monitoring system
to diagnose performance issues and track lock contention.
"""
import concurrent.futures
import os
import random
import tempfile
import threading
import time
import warnings
from uuid import UUID

# Suppress CoreAnalytics and other macOS system warnings
os.environ['no_proxy'] = '*'  # Helps with some connection warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*CoreAnalytics.*')
warnings.filterwarnings('ignore', message='.*context leak.*')

from agentmem import SemanticMemory, EpisodicMemory, ProceduralMemory
from agentmem.concurrency import lock_manager


def create_memory_entries(memory, num_entries=50):
    """Create a batch of memory entries."""
    memory_ids = []
    
    for i in range(num_entries):
        content = f"Test content {i}"
        category = random.choice(["category1", "category2", "category3"])
        tags = random.sample(["tag1", "tag2", "tag3", "tag4", "tag5"], 2)
        
        memory_id = memory.create(
            content=content,
            category=category,
            tags=tags
        )
        memory_ids.append(memory_id)
    
    return memory_ids


def simulate_high_contention_workload(memories, memory_ids, iterations=20):
    """Simulate a high-contention workload with multiple threads."""
    def worker(worker_id):
        """Worker function that performs memory operations."""
        for _ in range(iterations):
            # Randomly choose an operation
            operation = random.choice(["read", "update", "query"])
            memory_type = random.choice(["semantic", "episodic", "procedural"])
            memory = memories[memory_type]
            
            if operation == "read":
                # Read a random memory entry
                memory_id = random.choice(memory_ids[memory_type])
                memory.read(memory_id)
            
            elif operation == "update":
                # Update a random memory entry
                memory_id = random.choice(memory_ids[memory_type])
                memory.update(
                    memory_id,
                    content=f"Updated by worker {worker_id} at {time.time()}",
                    tags=["updated", f"worker-{worker_id}"]
                )
            
            elif operation == "query":
                # Perform a query
                query_terms = ["test", "content", "updated", "worker"]
                query = random.choice(query_terms)
                memory.query(query)
            
            # Small sleep to simulate thinking time
            time.sleep(random.uniform(0.001, 0.01))
    
    # Start multiple worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, i) for i in range(10)]
        concurrent.futures.wait(futures)


def print_lock_statistics(stats):
    """Print lock statistics in a readable format."""
    print("\n=== Lock Statistics ===")
    
    # Find all types of locks
    global_locks = sorted([name for name in stats.keys() if name.startswith("global")])
    type_locks = sorted([name for name in stats.keys() if name.startswith("type:")])
    id_locks = sorted([name for name in stats.keys() if name.startswith("id:")])
    transaction_locks = sorted([name for name in stats.keys() if name.startswith("transaction:")])
    
    # Print global lock statistics
    if global_locks:
        print("\nGlobal Locks:")
        for name in global_locks:
            print(f"  {name}:")
            print(f"    Contention count: {stats[name]['contention_count']}")
            if "avg_acquisition_time" in stats[name]:
                print(f"    Avg acquisition time: {stats[name]['avg_acquisition_time']*1000:.2f} ms")
                print(f"    Max acquisition time: {stats[name]['max_acquisition_time']*1000:.2f} ms")
            if "avg_hold_duration" in stats[name]:
                print(f"    Avg hold duration: {stats[name]['avg_hold_duration']*1000:.2f} ms")
                print(f"    Max hold duration: {stats[name]['max_hold_duration']*1000:.2f} ms")
    
    # Print memory type lock statistics
    if type_locks:
        print("\nMemory Type Locks:")
        for name in type_locks:
            memory_type = name.split(":", 1)[1]
            print(f"  {memory_type}:")
            print(f"    Contention count: {stats[name]['contention_count']}")
            if "avg_acquisition_time" in stats[name]:
                print(f"    Avg acquisition time: {stats[name]['avg_acquisition_time']*1000:.2f} ms")
                print(f"    Max acquisition time: {stats[name]['max_acquisition_time']*1000:.2f} ms")
            if "avg_hold_duration" in stats[name]:
                print(f"    Avg hold duration: {stats[name]['avg_hold_duration']*1000:.2f} ms")
                print(f"    Max hold duration: {stats[name]['max_hold_duration']*1000:.2f} ms")
    
    # Print ID lock statistics summary (could be too many to print individually)
    if id_locks:
        print(f"\nMemory ID Locks: {len(id_locks)} unique locks")
        
        # Calculate aggregated statistics for ID locks
        total_contention = sum(stats[name]['contention_count'] for name in id_locks)
        
        # Calculate acquisition time statistics if available
        acquisition_times = [stats[name].get('avg_acquisition_time', 0) for name in id_locks 
                           if 'avg_acquisition_time' in stats[name]]
        if acquisition_times:
            avg_acquisition = sum(acquisition_times) / len(acquisition_times)
            max_acquisition = max(stats[name].get('max_acquisition_time', 0) for name in id_locks
                                if 'max_acquisition_time' in stats[name])
            print(f"  Total contention count: {total_contention}")
            print(f"  Avg acquisition time: {avg_acquisition*1000:.2f} ms")
            print(f"  Max acquisition time: {max_acquisition*1000:.2f} ms")
        
        # Calculate hold duration statistics if available
        hold_durations = [stats[name].get('avg_hold_duration', 0) for name in id_locks
                        if 'avg_hold_duration' in stats[name]]
        if hold_durations:
            avg_hold = sum(hold_durations) / len(hold_durations)
            max_hold = max(stats[name].get('max_hold_duration', 0) for name in id_locks
                         if 'max_hold_duration' in stats[name])
            print(f"  Avg hold duration: {avg_hold*1000:.2f} ms")
            print(f"  Max hold duration: {max_hold*1000:.2f} ms")
    
    # Print transaction lock statistics summary
    if transaction_locks:
        print(f"\nTransaction Locks: {len(transaction_locks)} transactions")


def print_active_locks(active_locks):
    """Print currently active locks."""
    print("\n=== Active Locks ===")
    
    if not active_locks:
        print("No active locks")
        return
    
    for lock_name, (thread, acquisition_time) in active_locks.items():
        hold_duration = (time.time() - acquisition_time.timestamp())
        print(f"  {lock_name}: Held by {thread.name} for {hold_duration*1000:.2f} ms")


def main():
    """Run the lock monitoring demo."""
    print("=== AgentMem Lock Monitoring Demo ===")
    
    # Create temporary directories for persistence and vector storage
    temp_dir = tempfile.mkdtemp()
    persistence_dir = os.path.join(temp_dir, "persistence")
    vector_dir = os.path.join(temp_dir, "vector_db")
    os.makedirs(persistence_dir, exist_ok=True)
    os.makedirs(vector_dir, exist_ok=True)
    
    # Redirect stderr temporarily to suppress any warnings
    import sys
    original_stderr = sys.stderr
    null_stderr = open(os.devnull, 'w')
    sys.stderr = null_stderr
    
    # Check if vector search is available
    from agentmem.base import VECTOR_SEARCH_AVAILABLE
    
    try:
        # Enable lock monitoring
        print("\nInitializing memory systems with lock monitoring enabled...")
        
        # Create memory instances with vector search only if available
        # This avoids unnecessary warnings on platforms without vector search support
        use_vector_search = VECTOR_SEARCH_AVAILABLE
        
        # Restore stderr for normal output
        sys.stderr = original_stderr
        null_stderr.close()
        
        memories = {
            "semantic": SemanticMemory(
                persistence=os.path.join(persistence_dir, "semantic"),
                vector_search=use_vector_search,
                vector_db_path=os.path.join(vector_dir, "semantic")
            ),
            "episodic": EpisodicMemory(
                persistence=os.path.join(persistence_dir, "episodic"),
                vector_search=use_vector_search,
                vector_db_path=os.path.join(vector_dir, "episodic")
            ),
            "procedural": ProceduralMemory(
                persistence=os.path.join(persistence_dir, "procedural"),
                vector_search=use_vector_search,
                vector_db_path=os.path.join(vector_dir, "procedural")
            )
        }
        
        # Create initial memory entries
        print("\nCreating initial memory entries...")
        memory_ids = {
            memory_type: create_memory_entries(memory, 20)
            for memory_type, memory in memories.items()
        }
        
        # Reset metrics to clear initialization data
        lock_manager.reset_metrics()
        
        # Run a high-contention workload
        print("\nRunning high-contention workload with multiple threads...")
        simulate_high_contention_workload(memories, memory_ids)
        
        # Print lock statistics
        stats = lock_manager.get_lock_statistics()
        print_lock_statistics(stats)
        
        # Print active locks (should be none at this point)
        active_locks = lock_manager.get_active_locks()
        print_active_locks(active_locks)
        
        # Demonstrate a long-held lock
        print("\nDemonstrating a long-held lock...")
        
        def hold_lock_for_demo():
            with lock_manager.global_lock():
                print("Lock acquired. Press Enter to release...")
                # Auto-release after 1 second if running in non-interactive mode
                try:
                    # Set timeout on stdin 
                    import sys
                    import select
                    
                    # Wait for 1 second for input or auto-release
                    if sys.stdin.isatty() and select.select([sys.stdin], [], [], 1.0)[0]:
                        sys.stdin.readline()
                    else:
                        # Auto-release after 1 second for non-interactive environments
                        time.sleep(1.0)
                        print("Auto-releasing lock after 1 second (non-interactive mode)")
                except (EOFError, Exception) as e:
                    # Handle EOF and other errors gracefully
                    time.sleep(1.0)
                    print("Auto-releasing lock (error or non-interactive mode)")
        
        lock_thread = threading.Thread(name="lock-demo-thread", target=hold_lock_for_demo)
        lock_thread.start()
        
        # Small delay to ensure lock is acquired
        time.sleep(0.1)
        
        # Print active locks again
        active_locks = lock_manager.get_active_locks()
        print_active_locks(active_locks)
        
        # Wait for lock thread to complete with timeout
        lock_thread.join(timeout=5.0)
        
        # If thread is still alive after timeout, just continue
        if lock_thread.is_alive():
            print("Lock thread timed out, continuing demo anyway")
        
        print("\nLock monitoring demo completed.")
    
    finally:
        # Make sure we restore stderr
        if 'original_stderr' in locals() and sys.stderr != original_stderr:
            sys.stderr = original_stderr
            if 'null_stderr' in locals() and not null_stderr.closed:
                null_stderr.close()
            
        # Clean up temporary directories
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
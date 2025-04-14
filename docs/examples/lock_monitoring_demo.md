# Lock Monitoring Demo

The [lock_monitoring_demo.py](../examples/lock_monitoring_demo.py) example demonstrates AgentMem's thread safety features and lock monitoring capabilities in multi-threaded environments.

## What This Example Covers

- Thread-safe memory operations
- Lock acquisition and monitoring
- Concurrency patterns with memory systems
- Diagnosing and preventing lock contention
- Monitoring lock performance

## Key Code Sections

### 1. Setting Up Lock Monitoring

```python
from agentmem.concurrency import lock_manager

# Enable lock monitoring
lock_manager.enable_monitoring()
print("Lock monitoring enabled")

# Create memory instances
semantic_memory = SemanticMemory()
episodic_memory = EpisodicMemory()
```

The example begins by enabling lock monitoring, which tracks lock acquisition, contention, and release events.

### 2. Creating Worker Threads

```python
def worker(worker_id, memory, iterations):
    """Worker function that performs memory operations."""
    print(f"Worker {worker_id} starting")
    
    for i in range(iterations):
        # Create a memory
        content = f"Memory from worker {worker_id}, iteration {i}"
        memory_id = memory.create(content=content)
        
        # Read the memory
        result = memory.read(memory_id)
        
        # Update the memory
        memory.update(memory_id, content=f"Updated: {content}")
        
        # Query memories
        results = memory.query(f"worker {worker_id}")
        
        # Occasionally delete memories to avoid filling memory
        if i % 10 == 0 and i > 0:
            memory.delete(memory_id)
            
    print(f"Worker {worker_id} completed")
```

This function represents a worker thread that performs various memory operations in parallel with other threads.

### 3. Running Concurrent Operations

```python
# Create and start worker threads
threads = []
num_workers = 5
iterations = 20

for i in range(num_workers):
    thread = threading.Thread(
        target=worker, 
        args=(i, semantic_memory if i % 2 == 0 else episodic_memory, iterations)
    )
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()
```

Multiple worker threads are created and run concurrently, performing operations on the memory systems.

### 4. Displaying Lock Statistics

```python
# Get and display lock statistics
stats = lock_manager.get_lock_statistics()

print("\nLock Statistics:")
print(f"Total lock acquisitions: {stats['total_acquisitions']}")
print(f"Total lock releases: {stats['total_releases']}")
print(f"Current active locks: {stats['active_locks']}")
print(f"Lock contentions: {stats['contentions']}")
print(f"Max contention time: {stats['max_contention_time']:.6f} seconds")
print(f"Average lock hold time: {stats['avg_hold_time']:.6f} seconds")

# Display contention hotspots
print("\nLock Contention Hotspots:")
hotspots = stats['contention_hotspots']
for lock_id, count in sorted(hotspots.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"Lock {lock_id}: {count} contentions")
```

After the concurrent operations complete, the example retrieves and displays statistics about lock usage, including contentions and performance metrics.

### 5. Interactive Lock Inspection

```python
def interactive_lock_inspection():
    """Interactive function to inspect current locks."""
    while True:
        print("\nLock Inspector Commands:")
        print("1. Show active locks")
        print("2. Show lock statistics")
        print("3. Show contention hotspots")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            locks = lock_manager.get_active_locks()
            print(f"\nActive locks ({len(locks)}):")
            for i, lock_info in enumerate(locks, 1):
                print(f"{i}. {lock_info['lock_id']} - Held for {lock_info['held_time']:.6f} seconds")
                
        elif choice == "2":
            stats = lock_manager.get_lock_statistics()
            print("\nLock Statistics:")
            for key, value in stats.items():
                if key not in ['contention_hotspots', 'lock_hold_times']:
                    if isinstance(value, float):
                        print(f"{key}: {value:.6f}")
                    else:
                        print(f"{key}: {value}")
                        
        elif choice == "3":
            stats = lock_manager.get_lock_statistics()
            hotspots = stats['contention_hotspots']
            print("\nLock Contention Hotspots:")
            for lock_id, count in sorted(hotspots.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"Lock {lock_id}: {count} contentions")
                
        elif choice == "4":
            print("Exiting lock inspector")
            break
            
        else:
            print("Invalid choice, please try again")
```

An interactive component allows exploration of lock statistics and active locks in real-time.

## Expected Output

The example produces output similar to:

```
Lock monitoring enabled
Worker 0 starting
Worker 1 starting
Worker 2 starting
Worker 3 starting
Worker 4 starting
Worker 3 completed
Worker 1 completed
Worker 4 completed
Worker 0 completed
Worker 2 completed

Lock Statistics:
Total lock acquisitions: 687
Total lock releases: 687
Current active locks: 0
Lock contentions: 42
Max contention time: 0.002351 seconds
Average lock hold time: 0.000473 seconds

Lock Contention Hotspots:
Lock semantic_memory_type: 15 contentions
Lock episodic_memory_type: 12 contentions
Lock memory_id_73a2f8e9: 3 contentions
Lock memory_id_b1c4d2e5: 2 contentions
Lock memory_id_9f7e6d5c: 2 contentions

Lock Inspector Commands:
1. Show active locks
2. Show lock statistics
3. Show contention hotspots
4. Exit
Enter your choice (1-4):
```

The interactive portion then allows further exploration of lock statistics.

## Lock Types in AgentMem

AgentMem uses several types of locks to ensure thread safety:

1. **Memory ID Locks**: Protect specific memory entries during CRUD operations
2. **Memory Type Locks**: Protect memory type-specific operations like queries
3. **Transaction Locks**: Ensure atomicity for operations that span multiple steps

## Key Takeaways

1. **Thread Safety**: AgentMem operations are thread-safe by default, allowing concurrent access from multiple threads.

2. **Lock Monitoring**: The lock monitoring system provides insights into lock usage and contention.

3. **Performance Metrics**: Statistics about lock acquisitions, releases, and hold times help diagnose performance issues.

4. **Contention Hotspots**: Identifying which locks experience the most contention helps optimize concurrent access patterns.

5. **Interactive Debugging**: The interactive inspector allows real-time monitoring of lock behavior.

## Next Steps

After understanding the concurrency features, you might want to explore:

- [Logging Demo](logging_demo.md) to learn about comprehensive operation logging and metrics
- [Agent Assistant Example](agent_assistant.md) to see how concurrency enables responsive multi-user agent deployments

For more detailed information about the AgentMem concurrency API, see the [Concurrency API Reference](../api/concurrency.md) documentation.
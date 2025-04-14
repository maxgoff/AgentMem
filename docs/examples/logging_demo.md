# Logging Demo

The [logging_demo.py](../examples/logging_demo.py) example demonstrates AgentMem's comprehensive logging and metrics collection system, which helps monitor, debug, and optimize memory operations.

## What This Example Covers

- Configuring the logging system
- Capturing operation metrics
- Monitoring memory usage
- Tracking performance statistics
- Analyzing memory operations

## Key Code Sections

### 1. Configuring Logging

```python
from agentmem import configure_logging, LogLevel

# Configure logging with various options
configure_logging(
    log_level=LogLevel.DEBUG,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log_file="./agentmem.log",  # Output file for logs
    console_output=True,        # Whether to output to console
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

print("Logging configured at DEBUG level")
```

The example begins by configuring the logging system with the desired level, output options, and format.

### 2. Setting Up Memory and Metrics

```python
from agentmem import get_metrics_collector, get_memory_tracker
from agentmem.logging import OperationType
from agentmem.semantic import SemanticMemory

# Get metrics collector and memory tracker
metrics = get_metrics_collector()
memory_tracker = get_memory_tracker()

# Create a memory instance
memory = SemanticMemory(vector_search=True)
print("Created semantic memory with vector search")
```

Metrics collection tools are initialized alongside a semantic memory instance for demonstration.

### 3. Performing Memory Operations

```python
# Perform various operations to generate metrics
print("\nPerforming memory operations...")

# Track unique memory IDs
memory_ids = []

# Create memories
for i in range(10):
    memory_id = memory.create(
        content=f"Fact {i}: The sky is blue because of Rayleigh scattering",
        category="science",
        tags=["sky", "physics", "optics"]
    )
    memory_ids.append(memory_id)
    print(f"Created memory {i+1}/10")

# Read memories
for i, memory_id in enumerate(memory_ids):
    memory.read(memory_id)
    print(f"Read memory {i+1}/10")

# Update memories
for i, memory_id in enumerate(memory_ids[:5]):  # Update half of the memories
    memory.update(
        memory_id,
        content=f"Updated Fact {i}: The sky appears blue because air molecules scatter blue light more than red light",
        tags=["sky", "physics", "optics", "updated"]
    )
    print(f"Updated memory {i+1}/5")

# Perform queries
print("Performing queries...")
memory.query("sky", category="science")
memory.query("blue", tags=["physics"])
memory.query("light scattering", use_vector=True)

# Delete some memories
for i, memory_id in enumerate(memory_ids[:3]):  # Delete a few memories
    memory.delete(memory_id)
    print(f"Deleted memory {i+1}/3")
```

Various memory operations are performed to generate logging events and metrics.

### 4. Displaying Operation Metrics

```python
# Display operation metrics
print("\nOperation Metrics:")
stats = metrics.get_operation_stats()

print("\nOperation Counts:")
for op_type in [OperationType.CREATE, OperationType.READ, 
                OperationType.UPDATE, OperationType.DELETE,
                OperationType.QUERY, OperationType.VECTOR_QUERY]:
    op_name = f"semantic.{op_type}"
    count = stats.get(op_name, {}).get("count", 0)
    avg_time = stats.get(op_name, {}).get("avg_time", 0)
    print(f"{op_type.capitalize()}: {count} operations, Avg time: {avg_time:.6f} seconds")

# Calculate success rates
total_ops = sum(stats.get(f"semantic.{op}", {}).get("count", 0) 
                for op in [OperationType.CREATE, OperationType.READ, 
                          OperationType.UPDATE, OperationType.DELETE,
                          OperationType.QUERY, OperationType.VECTOR_QUERY])
                          
successful_ops = sum(stats.get(f"semantic.{op}", {}).get("success_count", 0) 
                    for op in [OperationType.CREATE, OperationType.READ, 
                              OperationType.UPDATE, OperationType.DELETE,
                              OperationType.QUERY, OperationType.VECTOR_QUERY])

if total_ops > 0:
    success_rate = (successful_ops / total_ops) * 100
    print(f"\nOverall Success Rate: {success_rate:.2f}%")
```

Operation metrics are retrieved and displayed, showing counts and average times for different operation types.

### 5. Analyzing Memory Usage

```python
# Display memory usage metrics
print("\nMemory Usage:")
memory_usage = memory_tracker.get_memory_usage()
for memory_type, usage in memory_usage.items():
    print(f"{memory_type}: {usage / 1024:.2f} KB")

# Get memory growth over time
memory_growth = memory_tracker.get_memory_growth("semantic")
print("\nMemory Growth (last 5 measurements):")
for timestamp, size in list(memory_growth.items())[-5:]:
    print(f"{timestamp}: {size / 1024:.2f} KB")
```

Memory usage statistics are retrieved and displayed, showing current usage and growth over time.

### 6. Performance Analysis

```python
# Display performance analysis
print("\nPerformance Analysis:")

# Get slowest operations
slowest_ops = metrics.get_slowest_operations(5)
print("\nSlowest Operations:")
for op_name, time_taken in slowest_ops:
    print(f"{op_name}: {time_taken:.6f} seconds")

# Get operation distribution
dist = metrics.get_operation_distribution()
print("\nOperation Distribution:")
for op_type, percentage in dist.items():
    print(f"{op_type}: {percentage:.2f}%")

# Get error rates
error_rates = metrics.get_error_rates()
print("\nError Rates:")
for op_type, rate in error_rates.items():
    print(f"{op_type}: {rate:.2f}%")
```

Performance metrics are analyzed, showing the slowest operations, operation distribution, and error rates.

### 7. Examining Log Output

```python
# Show where to find the detailed logs
print("\nDetailed logs are available in: ./agentmem.log")
print("Sample log entries:")

import os
if os.path.exists("./agentmem.log"):
    with open("./agentmem.log", "r") as f:
        # Read the last 5 lines
        lines = f.readlines()
        for line in lines[-5:]:
            print(line.strip())
```

The example concludes by showing where to find detailed logs and displaying a sample of log entries.

## Expected Output

The example produces output similar to:

```
Logging configured at DEBUG level
Created semantic memory with vector search

Performing memory operations...
Created memory 1/10
Created memory 2/10
...
Read memory 1/10
...
Updated memory 1/5
...
Performing queries...
Deleted memory 1/3
...

Operation Metrics:

Operation Counts:
Create: 10 operations, Avg time: 0.002431 seconds
Read: 10 operations, Avg time: 0.000328 seconds
Update: 5 operations, Avg time: 0.001953 seconds
Delete: 3 operations, Avg time: 0.001842 seconds
Query: 3 operations, Avg time: 0.003214 seconds
Vector_query: 1 operations, Avg time: 0.053672 seconds

Overall Success Rate: 100.00%

Memory Usage:
semantic: 14.56 KB

Memory Growth (last 5 measurements):
2023-05-02T15:30:12.123456: 4.21 KB
2023-05-02T15:30:12.234567: 8.45 KB
2023-05-02T15:30:12.345678: 12.78 KB
2023-05-02T15:30:12.456789: 14.56 KB
2023-05-02T15:30:12.567890: 14.56 KB

Performance Analysis:

Slowest Operations:
semantic.vector_query: 0.053672 seconds
semantic.query: 0.003982 seconds
semantic.create: 0.002983 seconds
semantic.update: 0.002341 seconds
semantic.delete: 0.001842 seconds

Operation Distribution:
Create: 31.25%
Read: 31.25%
Update: 15.63%
Delete: 9.38%
Query: 9.38%
Vector_query: 3.13%

Error Rates:
Create: 0.00%
Read: 0.00%
Update: 0.00%
Delete: 0.00%
Query: 0.00%
Vector_query: 0.00%

Detailed logs are available in: ./agentmem.log
Sample log entries:
2023-05-02 15:30:12,567 - agentmem.semantic - DEBUG - Created semantic memory entry with ID 8f7e6d5c
2023-05-02 15:30:12,568 - agentmem.semantic - DEBUG - Read semantic memory entry with ID 8f7e6d5c
2023-05-02 15:30:12,569 - agentmem.semantic - DEBUG - Updated semantic memory entry with ID 8f7e6d5c
2023-05-02 15:30:12,571 - agentmem.semantic - DEBUG - Query returned 7 results for 'light scattering'
2023-05-02 15:30:12,573 - agentmem.semantic - DEBUG - Deleted semantic memory entry with ID 8f7e6d5c
```

## Logging Components in AgentMem

AgentMem's logging system consists of several components:

1. **Logger**: Provides configurable logging at different levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
2. **Metrics Collector**: Tracks operation statistics including counts, timing, and success rates
3. **Memory Tracker**: Monitors memory usage and growth over time
4. **Operation Context Manager**: Tracks details of individual operations

## Key Takeaways

1. **Comprehensive Logging**: AgentMem provides detailed logging for all memory operations, aiding in debugging and understanding behavior.

2. **Performance Metrics**: The metrics system collects timing information to help identify slow operations and bottlenecks.

3. **Memory Monitoring**: Memory usage tracking helps prevent memory leaks and optimize resource utilization.

4. **Success Rate Tracking**: Error and success rates help measure system reliability.

5. **Log Analysis**: Log files provide a detailed record of operations for post-mortem analysis.

## Next Steps

After understanding the logging capabilities, you might want to explore:

- [Lock Monitoring Demo](lock_monitoring_demo.md) to see how logging complements thread safety monitoring
- [Agent Assistant Example](agent_assistant.md) to learn how logging helps debug complex agent behavior

For more detailed information about the AgentMem logging API, see the [Logging API Reference](../api/logging.md) documentation.
# AgentMem Examples

This section provides documentation for the example scripts included with AgentMem. These examples demonstrate real-world usage patterns and serve as reference implementations for common tasks.

## Available Examples

### [Basic Usage](../examples/basic_usage.py)

Demonstrates the fundamental operations for each memory type:
- Creating memory entries
- Reading memory by ID
- Updating existing memories
- Deleting memories
- Querying memories with various parameters

This is a great starting point for understanding how to use AgentMem.

### [Agent Assistant](../examples/agent_assistant.py)

Shows how to build a conversational agent that uses all three memory types:
- Semantic memory for storing factual knowledge
- Episodic memory for remembering interactions
- Procedural memory for storing response patterns

Learn how to create an AI assistant that remembers past interactions and uses that knowledge to provide better responses.

### [Persistence Example](../examples/persistence_example.py)

Demonstrates how to use persistent storage with AgentMem:
- Saving memories to disk
- Loading memories from disk
- Managing persistence across sessions
- Integrating with vector search for persistent similarity queries

Use this example to understand how to maintain memory across program restarts.

### [Lock Monitoring Demo](../examples/lock_monitoring_demo.py)

Illustrates the thread safety features of AgentMem:
- Concurrent memory operations
- Lock acquisition and management
- Deadlock prevention
- Performance monitoring for lock contention

This example is useful for understanding how AgentMem handles concurrency in multi-threaded applications.

### [Logging Demo](../examples/logging_demo.py)

Shows how to use AgentMem's logging and metrics collection:
- Configuring logging levels
- Capturing operation metrics
- Monitoring memory usage
- Analyzing performance statistics

Learn how to monitor and debug your AgentMem applications.

## Running the Examples

The examples can be run directly from the command line:

```bash
# Navigate to the agentmem directory
cd path/to/agentmem

# Run an example
python examples/basic_usage.py
```

## Example Code Structure

Each example follows a similar structure:

1. **Imports**: Import required AgentMem modules
2. **Setup**: Configure memory instances and any required parameters
3. **Demo Operations**: Demonstrate memory operations with practical examples
4. **Output**: Print results to demonstrate how the data is stored and retrieved

## Using Examples as Templates

Feel free to use these examples as starting points for your own applications. The code is designed to be modular and easily adaptable to different use cases.

For more detailed explanations of the AgentMem API, refer to the [API Reference](../api/index.md) documentation.
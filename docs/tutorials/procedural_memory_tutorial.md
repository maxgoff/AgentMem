# Procedural Memory Tutorial

This tutorial will guide you through using AgentMem's Procedural Memory module to store, retrieve, and query task-related knowledge for AI agents.

## What is Procedural Memory?

Procedural memory stores knowledge about how to perform specific tasks or skills. This is the type of memory an agent would use to remember procedures like "How to create a file in Python" or "Steps to debug a recursive function." Unlike semantic memory which stores factual knowledge, or episodic memory which stores experiences, procedural memory focuses on actionable knowledge - sequences of steps, techniques, and methods for accomplishing tasks.

## Setup

First, let's import the necessary components and create a procedural memory store:

```python
from agentmem.procedural import ProceduralMemory
from uuid import UUID

# Create an in-memory procedural memory store (no persistence)
memory = ProceduralMemory()

# Alternatively, create a persistent procedural memory store
# memory = ProceduralMemory(persistence="./memory_data")

# With vector search for semantic similarity
# memory = ProceduralMemory(persistence="./memory_data", vector_search=True)
```

## Storing Procedures

Let's store some procedures in procedural memory:

```python
# Store a programming procedure
python_file_id = memory.create(
    content="How to create a file in Python",
    task="Create and write to a file",
    steps=[
        "Import the necessary modules",
        "Use the open() function with 'w' mode to create a file object",
        "Write content using the write() method",
        "Close the file using the close() method",
        "Alternatively, use a context manager (with statement) to automatically close the file"
    ],
    prerequisites=["Python environment", "File system permissions"],
    domains=["programming", "python", "file-io"]
)

# Store a debugging procedure
debug_id = memory.create(
    content="How to debug a recursive function",
    task="Fix infinite recursion problems",
    steps=[
        "Check the base case condition",
        "Ensure the recursive call moves toward the base case",
        "Add print statements to track function calls and parameter values",
        "Use a debugger to step through the function execution",
        "Consider adding a maximum recursion depth guard"
    ],
    prerequisites=["Understanding of recursion", "Debugging tools"],
    domains=["programming", "debugging", "recursion"]
)

# Store a system administration procedure
backup_id = memory.create(
    content="How to create a database backup",
    task="Back up a PostgreSQL database",
    steps=[
        "Ensure sufficient disk space",
        "Use pg_dump command with appropriate flags",
        "Specify output file location",
        "Verify backup integrity",
        "Store backup securely"
    ],
    prerequisites=["PostgreSQL installed", "Database access credentials"],
    domains=["system-admin", "database", "postgresql"]
)
```

## Retrieving Procedures

You can retrieve procedures using their unique ID:

```python
# Retrieve a specific procedure
procedure = memory.read(python_file_id)
print(f"ID: {procedure['id']}")
print(f"Content: {procedure['content']}")
print(f"Task: {procedure['task']}")
print(f"Steps:")
for i, step in enumerate(procedure['steps'], 1):
    print(f"  {i}. {step}")
print(f"Prerequisites: {procedure['prerequisites']}")
print(f"Domains: {procedure['domains']}")
```

## Updating Procedures

Procedures can be updated when better methods are discovered or steps need refinement:

```python
# Update with a more modern approach
memory.update(
    python_file_id,
    steps=[
        "Import the necessary modules",
        "Use a context manager with the open() function to handle file closing automatically:",
        "    with open('filename.txt', 'w') as file:",
        "        file.write('content')",
        "This ensures the file is properly closed even if an exception occurs"
    ]
)

# Add more prerequisites
memory.update(
    debug_id,
    prerequisites=["Understanding of recursion", "Debugging tools", "Stack trace analysis skills"]
)

# Update domains
memory.update(
    backup_id,
    domains=["system-admin", "database", "postgresql", "backup-recovery"]
)
```

## Querying Procedures

You can search for procedures in various ways:

```python
# Simple keyword search
file_procedures = memory.query("file")
print(f"Found {len(file_procedures)} procedures related to files")

# Filter by domain
programming_procedures = memory.query(
    "",  # Empty string matches all
    domain="programming"
)
print(f"Found {len(programming_procedures)} programming procedures")

# Search for procedures matching available prerequisites
available_prereqs = ["Python environment", "Debugging tools"]
matching_procedures = memory.query(
    "",
    prerequisites=available_prereqs
)
print(f"Found {len(matching_procedures)} procedures matching available prerequisites")

# Combining search query and domain filter
python_debug_procedures = memory.query(
    "debug",
    domain="python"
)
print(f"Found {len(python_debug_procedures)} Python debugging procedures")
```

## Using Vector Search

If you've enabled vector search, you can perform semantic similarity searches that go beyond simple keyword matching:

```python
# Create a memory store with vector search enabled
procedural_memory = ProceduralMemory(vector_search=True)

# Add some procedures
procedural_memory.create(
    content="How to implement a binary search algorithm",
    task="Implement efficient searching",
    steps=[
        "Ensure the array is sorted",
        "Initialize low and high pointers",
        "Calculate the middle index",
        "Compare the middle element with the target",
        "Adjust search boundaries based on comparison",
        "Repeat until the element is found or boundaries cross"
    ],
    domains=["algorithms", "searching", "optimization"]
)

procedural_memory.create(
    content="How to merge two sorted arrays efficiently",
    task="Combine sorted data",
    steps=[
        "Initialize pointers at the beginning of both arrays",
        "Compare elements at both pointers",
        "Add the smaller element to the result",
        "Move the pointer in the array from which the element was taken",
        "Repeat until one array is exhausted",
        "Add remaining elements from the non-empty array"
    ],
    domains=["algorithms", "sorting", "arrays"]
)

# Semantic search - this will find procedures related to searching and sorting
# even if they don't contain the exact words
search_procedures = procedural_memory.query(
    "finding elements in a collection efficiently", 
    use_vector=True,
    n_results=5
)

for proc in search_procedures:
    print(f"Task: {proc['task']}")
    print(f"Content: {proc['content']}")
    if 'similarity_score' in proc:
        print(f"Similarity: {proc['similarity_score']:.2f}")
    print("-" * 30)
```

## Deleting Procedures

When procedures are no longer relevant or must be removed:

```python
# Delete a procedure
memory.delete(backup_id)

# Verify it's gone
try:
    memory.read(backup_id)
except KeyError:
    print("The procedure has been successfully deleted")
```

## Persistence

If you created your memory store with persistence, you can save and load all memories:

```python
# Create a persistent memory store
persistent_memory = ProceduralMemory(persistence="./memory_data")

# Add a procedure
persistent_memory.create(
    content="How to deploy a web application to AWS",
    task="Deploy web app",
    steps=["Create EC2 instance", "Configure security groups", "Install dependencies", "Transfer files", "Set up web server"]
)

# Save all memories to disk
persistent_memory.save_all()

# In a new session, load all memories from disk
persistent_memory.load_all()

# Or, memories are automatically loaded from persistence when available
# during initialization
```

## Practical Application

Let's see how procedural memory might be used in an agent that helps with technical tasks:

```python
class TechnicalAssistant:
    def __init__(self):
        self.procedural_memory = ProceduralMemory(persistence="./procedures")
        
    def learn_procedure(self, task, steps, prerequisites=None, domains=None):
        """Store a new procedure in the agent's knowledge base"""
        procedure_id = self.procedural_memory.create(
            content=task,
            task=task,
            steps=steps,
            prerequisites=prerequisites or [],
            domains=domains or ["general"]
        )
        return procedure_id
        
    def how_to(self, task_description, available_prerequisites=None, domain=None):
        """Retrieve procedures for how to perform a task"""
        kwargs = {}
        if domain:
            kwargs["domain"] = domain
        if available_prerequisites:
            kwargs["prerequisites"] = available_prerequisites
            
        procedures = self.procedural_memory.query(task_description, **kwargs)
        
        if not procedures:
            return "I don't know how to perform this task yet."
            
        # Sort procedures by how many steps they have (simpler first)
        procedures.sort(key=lambda x: len(x["steps"]))
        
        return procedures[0]
    
    def explain_procedure(self, procedure):
        """Format a procedure for explanation"""
        explanation = f"To {procedure['task']}:\n\n"
        
        if procedure['prerequisites']:
            explanation += "Prerequisites:\n"
            for prereq in procedure['prerequisites']:
                explanation += f"- {prereq}\n"
            explanation += "\n"
            
        explanation += "Steps:\n"
        for i, step in enumerate(procedure['steps'], 1):
            explanation += f"{i}. {step}\n"
            
        return explanation

# Create an assistant and teach it some procedures
assistant = TechnicalAssistant()
assistant.learn_procedure(
    "Set up a virtual environment in Python",
    steps=[
        "Install virtualenv if not installed: pip install virtualenv",
        "Navigate to your project directory",
        "Create a virtual environment: virtualenv venv",
        "Activate the environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)",
        "Install required packages: pip install -r requirements.txt"
    ],
    prerequisites=["Python installed", "pip installed"],
    domains=["python", "environment-setup"]
)

assistant.learn_procedure(
    "Debug a memory leak in Python",
    steps=[
        "Import the tracemalloc module",
        "Start tracking memory allocations: tracemalloc.start()",
        "Run your code",
        "Get the current and peak memory usage",
        "Take snapshots before and after suspected leaky operations",
        "Compare snapshots to identify growing allocations",
        "Look for objects that aren't being garbage collected"
    ],
    prerequisites=["Python installed", "Understanding of memory management"],
    domains=["python", "debugging", "performance"]
)

# Ask how to set up a Python environment
procedure = assistant.how_to("set up Python environment")
print(assistant.explain_procedure(procedure))

# Ask how to debug a memory issue with specific prerequisites
procedure = assistant.how_to(
    "fix memory problems", 
    available_prerequisites=["Python installed"], 
    domain="debugging"
)
print(assistant.explain_procedure(procedure))
```

## Advanced Usage

### Procedure Composition

You can create higher-level procedures that reference other procedures:

```python
def create_composite_procedure(memory, task, subtasks, prerequisites=None, domains=None):
    """Create a procedure composed of other procedures"""
    # Retrieve the referenced procedures
    steps = []
    all_prerequisites = set(prerequisites or [])
    
    for subtask in subtasks:
        # Find procedures matching this subtask
        candidates = memory.query(subtask)
        if candidates:
            # Use the best match
            best_match = candidates[0]
            steps.append(f"Subtask: {best_match['task']}")
            steps.append(f"Procedure ID: {best_match['id']}")
            for i, step in enumerate(best_match['steps'], 1):
                steps.append(f"  {i}. {step}")
            
            # Add prerequisites from this subtask
            all_prerequisites.update(best_match['prerequisites'])
    
    # Create the composite procedure
    return memory.create(
        content=task,
        task=task,
        steps=steps,
        prerequisites=list(all_prerequisites),
        domains=domains or ["composite"]
    )
```

### Versioning Procedures

You can implement versioning to track procedure evolution:

```python
def update_procedure_with_versioning(memory, procedure_id, **updates):
    """Update a procedure while preserving version history"""
    # Get the current procedure
    current = memory.read(procedure_id)
    
    # Store version information
    if "metadata" not in current or not current["metadata"]:
        current["metadata"] = {"versions": []}
    
    # Create version record
    version = {
        "timestamp": datetime.now().isoformat(),
        "content": current["content"],
        "task": current["task"],
        "steps": current["steps"].copy(),
        "prerequisites": current["prerequisites"].copy(),
        "domains": current["domains"].copy()
    }
    
    # Add to version history
    versions = current["metadata"].get("versions", [])
    versions.append(version)
    
    # Update with new version number
    updates["metadata"] = {
        "versions": versions,
        "version": len(versions),
        "last_updated": datetime.now().isoformat()
    }
    
    # Perform the update
    memory.update(procedure_id, **updates)
    
    return len(versions)
```

## Conclusion

Procedural memory provides a structured way to store and retrieve knowledge about how to perform tasks. By organizing procedures with steps, prerequisites, and domains, you can create agents that can learn, recall, and explain complex procedures to users.

For more detailed information about the Procedural Memory API, see the [API Reference](../api/procedural_memory.md).
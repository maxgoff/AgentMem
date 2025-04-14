# AgentMem Troubleshooting Guide

This guide addresses common issues you might encounter when using AgentMem, along with solutions, performance optimization techniques, and best practices.

## Common Issues and Solutions

### Installation Problems

#### Vector Search Dependencies Failed to Install

**Symptoms:**
- Error messages about missing `sentence-transformers` or `chromadb`
- Import errors when trying to use vector search
- `ModuleNotFoundError` for vector search components

**Solutions:**

1. Install vector dependencies explicitly:
   ```bash
   pip install "sentence-transformers>=2.2.0" "chromadb>=0.4.0"
   ```

2. Check for conflicts with existing packages:
   ```bash
   pip list | grep -E 'sentence|chroma|transformers'
   ```

3. Try creating a fresh environment:
   ```bash
   python -m venv agentmem_env
   source agentmem_env/bin/activate  # On Windows: agentmem_env\Scripts\activate
   pip install "agentmem[vector]"
   ```

#### NumPy Version Conflicts

**Symptoms:**
- Warnings about NumPy compiled with a different version
- Errors about incompatible NumPy versions
- Performance issues with vector operations

**Solutions:**

1. Check your NumPy version:
   ```bash
   pip show numpy
   ```

2. For NumPy 2.x compatibility issues, try adding this to your code:
   ```python
   import warnings
   warnings.filterwarnings("ignore", category=UserWarning)
   ```

3. Alternatively, downgrade to NumPy 1.x:
   ```bash
   pip install "numpy<2.0.0"
   ```

### Memory Access Issues

#### KeyError When Reading Memory

**Symptoms:**
- `KeyError` when trying to read a memory entry
- Memory entry seems to be missing despite being created
- Inconsistent access to memory entries

**Solutions:**

1. Verify memory ID format:
   ```python
   # Make sure you're using the correct UUID format
   memory_id = uuid.UUID(memory_id_str)  # Convert string to UUID if needed
   result = memory.read(memory_id)
   ```

2. Check if memory was properly created:
   ```python
   # Print all memory IDs to check existence
   all_memories = memory.query("")
   print([str(m['id']) for m in all_memories])
   ```

3. Ensure persistence is working if using it:
   ```python
   # Explicitly save and load memories
   memory.save_all()
   memory.load_all()
   ```

#### Multiple Instances Not Sharing Data

**Symptoms:**
- Creating multiple memory instances doesn't share data
- Changes made to one instance aren't visible in others
- Memory seems to be "forgotten" between runs

**Solutions:**

1. Use the same persistence directory across instances:
   ```python
   mem1 = SemanticMemory(persistence="./memory_data")
   mem2 = SemanticMemory(persistence="./memory_data")
   
   # Always load data when initializing
   mem2.load_all()
   ```

2. Ensure you're saving data after changes:
   ```python
   # After making changes
   memory.save_all()
   ```

3. Check file permissions on the persistence directory:
   ```bash
   ls -la ./memory_data/
   # Make sure permissions allow read/write
   ```

### Vector Search Issues

#### Vector Search Not Working

**Symptoms:**
- Query returns no results despite using vector search
- Missing similarity scores in results
- Error about missing embeddings or vectors

**Solutions:**

1. Check if vector search is enabled:
   ```python
   memory = SemanticMemory(vector_search=True)
   ```

2. Verify the query is using vector search:
   ```python
   results = memory.query("your query", use_vector=True)
   ```

3. Test with explicit vector DB path:
   ```python
   memory = SemanticMemory(
       vector_search=True,
       vector_db_path="./vector_db"  # Specify explicit path
   )
   ```

4. Check if you have enough content for meaningful vector search:
   ```python
   # Add more diverse content
   for i in range(10):
       memory.create(content=f"Example content {i} with varied terms and phrases")
   ```

#### Invalid Dimensions in Vector Storage

**Symptoms:**
- Errors about inconsistent embedding dimensions
- Vector search fails after working previously
- "Dimension mismatch" errors

**Solutions:**

1. Clear the vector database and rebuild it:
   ```python
   import shutil
   import os
   
   # Clear the vector database
   if os.path.exists("./vector_db"):
       shutil.rmtree("./vector_db")
   
   # Reinitialize with fresh vector storage
   memory = SemanticMemory(vector_search=True)
   ```

2. Make sure you're not mixing incompatible embedding models:
   ```python
   # Set a specific model for consistency
   import os
   os.environ["AGENTMEM_EMBEDDING_MODEL"] = "all-MiniLM-L6-v2"
   ```

### Concurrency Issues

#### Deadlocks or Hanging Operations

**Symptoms:**
- Operations seem to hang indefinitely
- Multiple threads appear to be waiting for each other
- No progress in multi-threaded applications

**Solutions:**

1. Use a transaction timeout:
   ```python
   from agentmem.concurrency import lock_manager
   
   # Set a global timeout
   lock_manager.set_lock_timeout(5.0)  # 5 second timeout
   ```

2. Avoid nested locks in your application code:
   ```python
   # Incorrect - potential deadlock
   def update_multiple(memory, ids):
       for id in ids:
           with lock_manager.memory_id_lock(id):
               # Do work
               
   # Better approach
   def update_multiple(memory, ids):
       with lock_manager.transaction(memory_ids=set(ids)):
           for id in ids:
               # Do work without additional locks
   ```

3. Enable lock monitoring for debugging:
   ```python
   from agentmem.concurrency import lock_manager
   
   # Enable monitoring
   lock_manager.enable_monitoring()
   
   # Later, check lock statistics
   stats = lock_manager.get_lock_statistics()
   print("Lock contentions:", stats["contentions"])
   print("Max contention time:", stats["max_contention_time"])
   ```

#### Race Conditions

**Symptoms:**
- Inconsistent data states
- Occasionally missing updates
- Different results with the same code

**Solutions:**

1. Always use the proper lock for your operation:
   ```python
   from agentmem.concurrency import lock_manager
   
   # For single memory operations
   with lock_manager.memory_id_lock(memory_id):
       # Safe to access/modify this memory entry
   
   # For type-wide operations
   with lock_manager.memory_type_lock(memory_type):
       # Safe to perform operations affecting all memories of this type
   
   # For operations spanning multiple memories
   with lock_manager.transaction(memory_ids={id1, id2, id3}):
       # Safe to perform operations on multiple memories
   ```

2. Avoid mixing direct storage access with API calls:
   ```python
   # Incorrect - bypassing locks
   memory._storage[memory_id] = new_value
   
   # Correct - using proper API
   memory.update(memory_id, content=new_value)
   ```

### Persistence Issues

#### Data Not Saving Properly

**Symptoms:**
- Memory entries disappear after restart
- Changes aren't visible after reloading
- Persistence directory is empty or incomplete

**Solutions:**

1. Verify the persistence directory exists and is writable:
   ```python
   import os
   
   persistence_dir = "./memory_data"
   os.makedirs(persistence_dir, exist_ok=True)
   
   # Check permissions
   assert os.access(persistence_dir, os.W_OK), "Directory not writable"
   ```

2. Explicitly call save operations:
   ```python
   # After creating or updating entries
   memory.save_all()
   ```

3. Check if errors are being suppressed during save:
   ```python
   import logging
   
   # Configure logging to see errors
   logging.basicConfig(level=logging.DEBUG)
   
   # Then try saving
   memory.save_all()
   ```

#### Corrupted Storage Files

**Symptoms:**
- JSON decode errors when loading
- KeyError or TypeError when accessing loaded data
- Truncated or empty files in the persistence directory

**Solutions:**

1. Inspect and repair storage files manually:
   ```python
   import json
   import os
   
   # Check specific file
   file_path = "./memory_data/semantic/problematic_uuid.json"
   try:
       with open(file_path, 'r') as f:
           data = json.load(f)
       print("File is valid JSON")
   except json.JSONDecodeError as e:
       print(f"Invalid JSON: {e}")
       # Consider removing corrupted file or restoring from backup
   ```

2. Create a backup before trying fixes:
   ```bash
   cp -r ./memory_data ./memory_data_backup
   ```

3. Reset and rebuild if necessary:
   ```python
   import os
   import shutil
   
   # Backup first!
   if os.path.exists("./memory_data_backup"):
       print("Using existing backup")
   else:
       shutil.copytree("./memory_data", "./memory_data_backup")
   
   # Clear problematic storage
   shutil.rmtree("./memory_data")
   os.makedirs("./memory_data")
   
   # Reinitialize
   memory = SemanticMemory(persistence="./memory_data")
   ```

## Performance Optimization

### Memory Usage Optimization

#### Reducing Memory Footprint

**Technique 1: Selective Loading**
```python
# Instead of loading all memories at initialization
memory = SemanticMemory(persistence="./memory_data")

# Only load memories on demand
memory = SemanticMemory(persistence="./memory_data")
# Don't call load_all() initially

# Load specific memories only when needed
try:
    # First try to read from in-memory
    result = memory.read(memory_id)
except KeyError:
    # If not found, it will automatically load from persistence
    result = memory.read(memory_id)
```

**Technique 2: Memory Cleanup**
```python
# Periodically clean up memory
import gc

# Delete memories you don't need anymore
memory.delete(old_memory_id)

# Clear in-memory cache for memories that can be reloaded later
memory._storage.clear()  # Be careful with this!

# Force garbage collection
gc.collect()
```

**Technique 3: Batched Operations**
```python
# Instead of many small operations
for item in large_list:
    memory.create(content=item)  # Creates many small objects

# Batch similar items
batch_size = 100
for i in range(0, len(large_list), batch_size):
    batch = large_list[i:i+batch_size]
    # Process batch together
    for item in batch:
        memory.create(content=item)
    
    # Clear unneeded references
    batch = None
    gc.collect()
```

#### Monitoring Memory Usage

**Using the Built-in Memory Tracker**
```python
from agentmem.logging import get_memory_tracker

# Get the memory tracker
memory_tracker = get_memory_tracker()

# Get current memory usage
memory_usage = memory_tracker.get_memory_usage()
print(f"Semantic memory: {memory_usage.get('semantic', 0) / 1024 / 1024:.2f} MB")

# Track memory growth over time
growth = memory_tracker.get_memory_growth("semantic")
for timestamp, size in growth.items():
    print(f"{timestamp}: {size / 1024 / 1024:.2f} MB")
```

**Using External Tools**
```python
# Using psutil for process-wide memory monitoring
import psutil
import os

def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss  # Resident Set Size in bytes

# Check memory before and after operations
before = get_process_memory()
memory.query("some large query operation")
after = get_process_memory()
print(f"Memory used: {(after - before) / 1024 / 1024:.2f} MB")
```

### Query Optimization

#### Optimizing Vector Search

**Technique 1: Limit Result Sets**
```python
# Set a reasonable limit on results
results = memory.query(
    "query terms",
    use_vector=True,
    n_results=10  # Only get top 10 matches
)
```

**Technique 2: Use Metadata Filters**
```python
# Filter before vector search when possible
results = memory.query(
    "query terms",
    category="specific_category",  # Filtered before vector search
    use_vector=True
)
```

**Technique 3: Strategic Vector Search Usage**
```python
# Avoid vector search for simple queries
if simple_keyword_query:
    results = memory.query(query, use_vector=False)
else:
    # Use vector search only for complex semantic matches
    results = memory.query(query, use_vector=True)
```

#### Efficient Filtering

**Technique 1: Most Restrictive Filters First**
```python
# Good approach - filters as much as possible early
results = memory.query(
    "",  # Empty query to match all content
    category="rare_category",  # Apply most restrictive filter first
    tags=["common_tag"]  # Then filter by more common criteria
)

# Combines vector search with pre-filtering
results = memory.query(
    "semantic query",
    category="specific_category",  # Pre-filter to reduce vector search scope
    use_vector=True
)
```

**Technique 2: Post-Processing Filtering**
```python
# Complex custom filtering
base_results = memory.query("base query")
filtered_results = [
    r for r in base_results
    if custom_filter_condition(r)
]

# Example custom filter
def custom_filter_condition(result):
    # Complex logic not available in standard filters
    return (
        len(result["content"]) > 100 and
        "important phrase" in result["content"].lower() and
        result["metadata"].get("review_score", 0) > 7
    )
```

### Concurrency Optimization

#### Optimizing Lock Usage

**Technique 1: Use Appropriate Lock Granularity**
```python
from agentmem.concurrency import lock_manager

# For single-entry operations, use memory_id_lock
with lock_manager.memory_id_lock(memory_id):
    # Operations on a single memory entry
    
# For operations affecting many entries, use memory_type_lock
with lock_manager.memory_type_lock("semantic"):
    # Operations affecting many semantic memories
    
# For complex multi-entry operations, use transaction
with lock_manager.transaction(memory_type="semantic", memory_ids={id1, id2, id3}):
    # Operations on a specific set of memories
```

**Technique 2: Minimize Lock Duration**
```python
# Bad approach - lock held during computation
with lock_manager.memory_id_lock(memory_id):
    data = memory.read(memory_id)
    # Expensive computation while holding lock
    processed_data = complex_processing(data)
    memory.update(memory_id, content=processed_data)

# Better approach - only lock for the critical sections
data = memory.read(memory_id)  # Uses lock internally
# Expensive computation outside lock
processed_data = complex_processing(data)
memory.update(memory_id, content=processed_data)  # Uses lock internally
```

**Technique 3: Lock Monitoring for Bottleneck Identification**
```python
from agentmem.concurrency import lock_manager

# Enable monitoring
lock_manager.enable_monitoring()

# Run your operations

# Analyze lock statistics
stats = lock_manager.get_lock_statistics()
print(f"Total acquisitions: {stats['total_acquisitions']}")
print(f"Lock contentions: {stats['contentions']}")
print(f"Average hold time: {stats['avg_hold_time']:.6f} seconds")

# Find contention hotspots
hotspots = stats['contention_hotspots']
for lock_id, count in sorted(hotspots.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"Lock {lock_id}: {count} contentions")
```

### Storage Optimization

#### Optimizing File Storage

**Technique 1: Compression for Large Data**
```python
import gzip
import json
import os

def compressed_save(memory_id, data, directory):
    """Save memory data with compression"""
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"{memory_id}.json.gz")
    
    with gzip.open(file_path, 'wt', encoding='utf-8') as f:
        json.dump(data, f)
    
    return file_path

def compressed_load(memory_id, directory):
    """Load compressed memory data"""
    file_path = os.path.join(directory, f"{memory_id}.json.gz")
    
    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
        data = json.load(f)
    
    return data
```

**Technique 2: Batched Persistence**
```python
# Instead of saving after every change
memory_ids_to_save = set()

# After each operation, mark for saving
memory_ids_to_save.add(memory_id)

# Periodically save in batch
if len(memory_ids_to_save) >= 100:
    for memory_id in memory_ids_to_save:
        entry = memory._storage.get(memory_id)
        if entry:
            memory._save_to_persistence(memory_id, memory._entry_to_dict(entry))
    memory_ids_to_save.clear()
```

**Technique 3: Selective Persistence**
```python
# Not all memory entries need to be persistent
# For transient data
transient_memory = SemanticMemory()  # No persistence

# For important data
persistent_memory = SemanticMemory(persistence="./critical_data")

# Choose where to store based on importance
def store_data(content, importance):
    if importance > 7:
        return persistent_memory.create(content=content, importance=importance)
    else:
        return transient_memory.create(content=content, importance=importance)
```

## Best Practices

### Memory Organization

#### Effective Categorization

**Practice 1: Consistent Category Hierarchy**
```python
# Define a standard set of top-level categories
CATEGORIES = {
    "factual": "Verified factual information",
    "conceptual": "Abstract concepts and ideas",
    "user_data": "User-specific information",
    "derived": "Information derived from other facts",
    "temporary": "Short-lived information"
}

# Use subcategories with colon notation
memory.create(
    content="Paris is the capital of France",
    category="factual:geography:cities"
)

memory.create(
    content="User prefers dark mode",
    category="user_data:preferences:ui"
)
```

**Practice 2: Tag-Based Multi-faceted Organization**
```python
# Use tags for cross-cutting concerns
memory.create(
    content="Python is a high-level programming language",
    category="factual:technology:languages",
    tags=["programming", "python", "beginner-friendly", "versatile"]
)

# Combine category and tag filtering
python_for_beginners = memory.query(
    "python",
    category="factual:technology",
    tags=["beginner-friendly"]
)
```

**Practice 3: Metadata for Custom Classification**
```python
# Use metadata for custom organization schemes
memory.create(
    content="The Earth orbits the Sun",
    category="factual:astronomy",
    metadata={
        "confidence": 1.0,
        "source": "scientific_fact",
        "last_verified": "2023-01-15",
        "taxonomies": {
            "bloom": "knowledge",
            "scientific_domain": "astronomy",
            "education_level": "elementary"
        }
    }
)

# Custom filtering in application code
results = memory.query("astronomy")
elementary_facts = [
    r for r in results
    if r.get("metadata", {}).get("taxonomies", {}).get("education_level") == "elementary"
]
```

#### Memory Type Selection

**Practice 1: Choose the Right Memory Type**

| When you need to... | Use this memory type |
|---------------------|----------------------|
| Store facts, knowledge, or concepts | Semantic Memory |
| Record events, experiences, or interactions | Episodic Memory |
| Store how-to information or process steps | Procedural Memory |

**Practice 2: Memory Type Integration**
```python
# Store a fact in semantic memory
fact_id = semantic_memory.create(
    content="Paris is the capital of France",
    category="geography",
    tags=["europe", "capitals"]
)

# Record learning this fact in episodic memory
episodic_memory.create(
    content="Learned about Paris being the capital of France",
    context={
        "related_semantic_id": str(fact_id),
        "learning_source": "geography_lesson",
        "confidence": 1.0
    }
)

# Store how to recall this information in procedural memory
procedural_memory.create(
    content="How to recall European capitals",
    task="Recall European capitals",
    steps=[
        "Query semantic memory with 'capital' tag and 'europe' tag",
        "Sort results alphabetically by country",
        "Present the capital city for each country"
    ],
    domains=["geography", "europe", "recall"]
)
```

### Thread Safety

#### Safe Multi-threaded Access

**Practice 1: Use High-Level Memory APIs**
```python
# Memory methods already handle locking internally
def worker_function(memory, data):
    # These operations are thread-safe
    memory.create(content=data)
    results = memory.query("some query")
    
    # No need for additional locks
```

**Practice 2: Use Transactions for Atomic Operations**
```python
from agentmem.concurrency import lock_manager

def update_related_entries(memory, main_id, related_ids):
    # Use a transaction to ensure all updates happen atomically
    with lock_manager.transaction(memory_ids={main_id, *related_ids}):
        # Update main entry
        main_data = memory.read(main_id)
        memory.update(main_id, content="Updated " + main_data["content"])
        
        # Update all related entries
        for related_id in related_ids:
            related_data = memory.read(related_id)
            memory.update(related_id, content="Related to " + main_data["content"])
```

**Practice 3: Avoid Nested Locks**
```python
# Problematic pattern - can lead to deadlocks
def process_memory_entries(memory, id_list):
    for memory_id in id_list:
        with lock_manager.memory_id_lock(memory_id):
            # If this function calls another function that acquires locks,
            # you might get deadlocks
            process_single_entry(memory, memory_id)

# Better approach
def process_memory_entries(memory, id_list):
    # Acquire all locks at once in a consistent order
    with lock_manager.transaction(memory_ids=set(id_list)):
        for memory_id in id_list:
            # No additional locks needed here
            process_single_entry_without_locks(memory, memory_id)
```

### Error Handling

#### Robust Error Recovery

**Practice 1: Graceful Fallbacks**
```python
def get_memory_with_fallback(memory, memory_id):
    try:
        return memory.read(memory_id)
    except KeyError:
        # Log the failed attempt
        print(f"Memory {memory_id} not found, using default")
        return {"content": "Default content", "metadata": {}}

def query_with_fallback(memory, query, **kwargs):
    try:
        results = memory.query(query, **kwargs)
        if results:
            return results
            
        # If vector search returned no results, try without it
        if kwargs.get("use_vector", False):
            kwargs["use_vector"] = False
            return memory.query(query, **kwargs)
            
        # Still no results
        return []
    except Exception as e:
        print(f"Query failed: {e}")
        return []
```

**Practice 2: Validation and Sanitization**
```python
def safe_create_memory(memory, content, **kwargs):
    # Validate content
    if content is None or content == "":
        raise ValueError("Content cannot be empty")
    
    # Sanitize and validate metadata
    if "metadata" in kwargs:
        # Remove potentially problematic values
        metadata = kwargs["metadata"].copy()
        for key in list(metadata.keys()):
            if not isinstance(key, str):
                del metadata[key]
            elif isinstance(metadata[key], (dict, list)):
                # Ensure JSON serializability by converting to string
                metadata[key] = str(metadata[key])
        kwargs["metadata"] = metadata
    
    # Attempt to create memory
    try:
        return memory.create(content=content, **kwargs)
    except Exception as e:
        print(f"Failed to create memory: {e}")
        # Fallback with minimal attributes
        return memory.create(content=content)
```

**Practice 3: Transaction Rollback**
```python
class MemoryTransaction:
    def __init__(self, memory):
        self.memory = memory
        self.operations = []
        self.created_ids = []
        
    def create(self, content, **kwargs):
        memory_id = self.memory.create(content, **kwargs)
        self.operations.append(("create", memory_id))
        self.created_ids.append(memory_id)
        return memory_id
        
    def update(self, memory_id, **kwargs):
        # Store current state for rollback
        try:
            current = self.memory.read(memory_id)
            self.operations.append(("update", memory_id, current))
            self.memory.update(memory_id, **kwargs)
        except KeyError:
            print(f"Warning: Cannot update non-existent memory {memory_id}")
            
    def delete(self, memory_id):
        try:
            current = self.memory.read(memory_id)
            self.operations.append(("delete", memory_id, current))
            self.memory.delete(memory_id)
        except KeyError:
            print(f"Warning: Cannot delete non-existent memory {memory_id}")
    
    def rollback(self):
        # Rollback in reverse order
        for op in reversed(self.operations):
            if op[0] == "create":
                try:
                    self.memory.delete(op[1])
                except:
                    pass
            elif op[0] == "update" or op[0] == "delete":
                memory_id, previous = op[1], op[2]
                try:
                    # Recreate deleted or restore updated
                    self.memory.create(
                        content=previous["content"],
                        id=memory_id,
                        **{k: v for k, v in previous.items() 
                           if k not in ["id", "content"]}
                    )
                except:
                    pass
        self.operations = []
        self.created_ids = []
```

### Memory Content Design

#### Optimal Content Storage

**Practice 1: Structured Content**
```python
# Instead of unstructured text
memory.create(
    content="Temperature in New York is 75°F and it's sunny"
)

# Use structured data
import json
memory.create(
    content=json.dumps({
        "location": "New York",
        "temperature": {
            "value": 75,
            "unit": "fahrenheit"
        },
        "conditions": "sunny"
    }),
    category="weather",
    tags=["weather", "new_york", "current"]
)

# When retrieving
weather_data = json.loads(memory.read(memory_id)["content"])
temp_celsius = (weather_data["temperature"]["value"] - 32) * 5/9
```

**Practice 2: Content Normalization**
```python
def normalize_text(text):
    """Normalize text for consistent storage and retrieval"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove excess whitespace
    text = " ".join(text.split())
    
    # Handle special characters
    text = text.replace("&", "and")
    
    return text

# Store with normalization
memory.create(
    content=normalize_text("The SKY is BLUE & Clear!!!"),
    metadata={"original": "The SKY is BLUE & Clear!!!"}
)
```

**Practice 3: Memory Segmentation**
```python
def store_large_document(memory, title, content, segment_size=1000):
    """Split large content into manageable segments"""
    segments = []
    
    # Split content into segments
    words = content.split()
    for i in range(0, len(words), segment_size):
        segment = " ".join(words[i:i+segment_size])
        segment_num = i // segment_size + 1
        
        # Store segment
        segment_id = memory.create(
            content=segment,
            category="document_segment",
            tags=["segment", title],
            metadata={
                "document_title": title,
                "segment_num": segment_num,
                "total_segments": (len(words) // segment_size) + 1
            }
        )
        segments.append(segment_id)
    
    # Store document index
    index_id = memory.create(
        content=f"Document: {title}",
        category="document_index",
        tags=["index", title],
        metadata={
            "title": title,
            "segment_ids": [str(s) for s in segments],
            "segment_count": len(segments),
            "word_count": len(words)
        }
    )
    
    return index_id, segments
```

## Advanced Debugging

### Debugging Vector Search

#### Diagnosing Vector Search Issues

**Technique 1: Test the Embedding Model**
```python
from sentence_transformers import SentenceTransformer

# Check if the model can be loaded
try:
    # Try with a small model first
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Test embedding generation
    sample = "This is a test sentence for embedding."
    embedding = model.encode(sample)
    
    print(f"Successfully created embedding with shape: {embedding.shape}")
except Exception as e:
    print(f"Error with embedding model: {e}")
```

**Technique 2: Verify ChromaDB Operations**
```python
import chromadb

# Try basic ChromaDB operations
try:
    # Create a client
    client = chromadb.Client()
    
    # Create a test collection
    collection = client.create_collection("test_collection")
    
    # Add a document
    collection.add(
        documents=["This is a test document."],
        metadatas=[{"source": "test"}],
        ids=["test1"]
    )
    
    # Query the collection
    results = collection.query(
        query_texts=["test document"],
        n_results=1
    )
    
    print(f"ChromaDB test successful, results: {results}")
except Exception as e:
    print(f"ChromaDB error: {e}")
```

**Technique 3: Compare Direct vs. API Results**
```python
# Test vector search directly vs. through AgentMem API
from sentence_transformers import SentenceTransformer
import numpy as np

def test_vector_search(memory, query):
    # Get results through normal API
    api_results = memory.query(query, use_vector=True)
    print(f"API returned {len(api_results)} results")
    
    # Get embedding model and vector DB from memory object (if possible)
    # Note: This is implementation-specific and might change
    if hasattr(memory, '_vector_search') and memory._vector_search:
        # Try direct similarity search
        model = SentenceTransformer('all-MiniLM-L6-v2')  # Use same model as AgentMem
        query_embedding = model.encode(query)
        
        # Check embedding values
        print(f"Query embedding shape: {query_embedding.shape}")
        print(f"First few values: {query_embedding[:5]}")
        
        # Check for NaN or zeros
        if np.isnan(query_embedding).any():
            print("Warning: Embedding contains NaN values")
        if not np.any(query_embedding):
            print("Warning: Embedding is all zeros")
            
        print("Vector search debugging complete")
    else:
        print("Vector search not enabled or accessible")
```

### Profile and Optimize

#### Performance Profiling

**Technique 1: Basic Timing Analysis**
```python
import time

def profile_operation(operation_name, func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    elapsed = end_time - start_time
    print(f"Operation '{operation_name}' took {elapsed:.6f} seconds")
    
    return result, elapsed

# Example usage
result, time_taken = profile_operation(
    "semantic query",
    memory.query,
    "complex query with vector search",
    use_vector=True
)
```

**Technique 2: Detailed Operation Breakdown**
```python
import time
from functools import wraps

# Decorator to profile memory operations
def profile_memory_op(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        
        # Track intermediate stages
        stages = {}
        original_methods = {}
        
        # Patch internal methods to track timing
        for method_name in ['_save_to_persistence', '_add_to_vector_search']:
            if hasattr(self, method_name):
                original_method = getattr(self, method_name)
                
                def create_timing_wrapper(name, orig_method):
                    @wraps(orig_method)
                    def method_wrapper(*m_args, **m_kwargs):
                        m_start = time.time()
                        result = orig_method(*m_args, **m_kwargs)
                        m_end = time.time()
                        stages[name] = (m_end - m_start)
                        return result
                    return method_wrapper
                
                original_methods[method_name] = original_method
                setattr(self, method_name, create_timing_wrapper(method_name, original_method))
        
        # Call the actual method
        result = func(self, *args, **kwargs)
        end_time = time.time()
        
        # Restore original methods
        for method_name, original_method in original_methods.items():
            setattr(self, method_name, original_method)
        
        # Print timing information
        total_time = end_time - start_time
        other_time = total_time - sum(stages.values())
        
        print(f"Operation {func.__name__} total time: {total_time:.6f} seconds")
        for stage, duration in stages.items():
            print(f"  - {stage}: {duration:.6f} seconds ({duration/total_time*100:.1f}%)")
        print(f"  - other operations: {other_time:.6f} seconds ({other_time/total_time*100:.1f}%)")
        
        return result
    return wrapper

# Apply to specific methods
from types import MethodType
memory.create = MethodType(profile_memory_op(memory.create.__func__), memory)
```

**Technique 3: Memory Profiling**
```python
# Using memory-profiler package (pip install memory-profiler)
from memory_profiler import profile as memory_profile

@memory_profile
def run_memory_intensive_operation(memory, query):
    # Create many entries
    for i in range(1000):
        memory.create(content=f"Test content {i}")
    
    # Perform vector search
    results = memory.query(query, use_vector=True)
    
    return results

# Run the profiled function
run_memory_intensive_operation(memory, "complex query")
```

## Common Error Messages

### Understanding Error Messages

#### "Cannot import name 'VectorStorage'"

**Cause**: Missing vector search dependencies or import error in vector_storage.py.

**Solutions**:
1. Install vector search dependencies: `pip install "agentmem[vector]"`
2. Check for package conflicts: `pip check`
3. Verify installation: `pip list | grep -E 'sentence|chroma'`

#### "Lock acquisition timed out"

**Cause**: A lock could not be acquired within the timeout period, likely due to deadlock or a hung operation.

**Solutions**:
1. Check for nested locks in your code
2. Use `lock_manager.set_lock_timeout(10.0)` to increase timeout
3. Enable lock monitoring with `lock_manager.enable_monitoring()` and check statistics

#### "Not implemented with vector_search=True"

**Cause**: Attempting to use vector search in a method that doesn't support it, or vector search dependencies are missing.

**Solutions**:
1. Check operation documentation to see if vector search is supported
2. Install vector search dependencies: `pip install "sentence-transformers>=2.2.0" "chromadb>=0.4.0"`
3. Try with `use_vector=False` as a fallback

#### "NoneType has no attribute 'encoding'"

**Cause**: Attempting to store None or invalid text data in vector storage.

**Solutions**:
1. Ensure all content passed to memory operations is valid text
2. Add validation: `if content is None or not isinstance(content, str): content = str(content)`
3. Check upstream data sources for null values

This troubleshooting guide covers the most common issues and best practices for using AgentMem effectively. For further assistance, refer to the API documentation or open an issue on GitHub.
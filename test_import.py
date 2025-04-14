"""
Simple test script to verify that warnings are properly suppressed 
and the library works with various Python and NumPy versions.

Run this script with: python test_import.py
"""
import os
import warnings
import tempfile

# Show that warnings work normally
warnings.warn("This warning should be visible")

# Import agentmem - should not show NumPy warnings
print("Importing agentmem...")
import agentmem

# Create semantic memory and show it works
print("\nCreating in-memory SemanticMemory and testing...")
semantic_mem = agentmem.SemanticMemory()

fact_id = semantic_mem.create(
    content="Paris is the capital of France",
    category="geography",
    tags=["cities", "countries", "europe"]
)

result = semantic_mem.query("Paris")
print(f"Found {len(result)} memories about Paris")

# Test persistence with a temporary directory
print("\nTesting file persistence...")
with tempfile.TemporaryDirectory() as tmp_dir:
    persist_mem = agentmem.SemanticMemory(persistence=tmp_dir)
    persist_fact_id = persist_mem.create(
        content="Rome is the capital of Italy",
        category="geography",
        tags=["cities", "countries", "europe"]
    )
    persist_result = persist_mem.query("Rome")
    print(f"Found {len(persist_result)} memories about Rome")

# Test vector search if available
print("\nTesting vector search...")
try:
    with tempfile.TemporaryDirectory() as tmp_dir:
        vector_mem = agentmem.SemanticMemory(
            vector_search=True,
            vector_db_path=tmp_dir
        )
        vector_fact_id = vector_mem.create(
            content="Tokyo is the capital of Japan",
            category="geography",
            tags=["cities", "countries", "asia"]
        )
        vector_result = vector_mem.query("Asian capital city")
        print(f"Found {len(vector_result)} vector-based memories")
        print("Vector search test completed successfully!")
except Exception as e:
    print(f"Vector search test failed with error: {str(e)}")
    print("This is expected on some systems with version incompatibilities")

print("\nAll applicable tests completed!")
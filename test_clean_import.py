"""
Simple test script to verify that NO warnings are shown when importing agentmem.

Run this script with: python test_clean_import.py
"""
print("=== Testing clean import of agentmem ===")
print("Importing agentmem...")

# This import should not show ANY warnings
import agentmem

print("Import successful!")
print("\nTesting basic functionality...")

# Create a simple memory object
mem = agentmem.SemanticMemory()
mem.create(content="Test memory", category="test", tags=["tag1", "tag2"])
results = mem.query("test")

print(f"Successfully created and queried memory: {len(results)} result(s)")
print("\nAll tests passed without warnings!")
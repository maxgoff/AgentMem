"""
Unit tests for SemanticMemory class.
"""
import unittest
from uuid import UUID

from agentmem import SemanticMemory


class TestSemanticMemory(unittest.TestCase):
    """Test cases for SemanticMemory class."""
    
    def setUp(self):
        """Set up a fresh SemanticMemory instance for each test."""
        self.memory = SemanticMemory()
        
        # Add some test data
        self.fact1_id = self.memory.create(
            content="Paris is the capital of France",
            category="geography",
            tags=["cities", "countries", "europe"]
        )
        
        self.fact2_id = self.memory.create(
            content="Python is a programming language",
            category="technology",
            tags=["programming", "languages", "software"]
        )
    
    def test_create(self):
        """Test creating a new memory entry."""
        fact_id = self.memory.create(
            content="The Earth orbits the Sun",
            category="astronomy",
            tags=["planets", "solar system"]
        )
        
        self.assertIsInstance(fact_id, UUID)
        self.assertEqual(len(self.memory._storage), 3)
    
    def test_read(self):
        """Test reading a memory entry."""
        fact = self.memory.read(self.fact1_id)
        
        self.assertEqual(fact["content"], "Paris is the capital of France")
        self.assertEqual(fact["category"], "geography")
        self.assertEqual(fact["tags"], ["cities", "countries", "europe"])
    
    def test_read_nonexistent(self):
        """Test reading a nonexistent memory raises KeyError."""
        with self.assertRaises(KeyError):
            self.memory.read(UUID('00000000-0000-0000-0000-000000000000'))
    
    def test_update(self):
        """Test updating a memory entry."""
        self.memory.update(
            self.fact2_id,
            content="Python is a high-level programming language",
            tags=["programming", "languages", "software", "high-level"]
        )
        
        updated_fact = self.memory.read(self.fact2_id)
        self.assertEqual(updated_fact["content"], "Python is a high-level programming language")
        self.assertEqual(updated_fact["tags"], ["programming", "languages", "software", "high-level"])
        self.assertEqual(updated_fact["category"], "technology")  # Unchanged
    
    def test_update_nonexistent(self):
        """Test updating a nonexistent memory raises KeyError."""
        with self.assertRaises(KeyError):
            self.memory.update(
                UUID('00000000-0000-0000-0000-000000000000'),
                content="This doesn't exist"
            )
    
    def test_delete(self):
        """Test deleting a memory entry."""
        self.memory.delete(self.fact1_id)
        
        self.assertEqual(len(self.memory._storage), 1)
        with self.assertRaises(KeyError):
            self.memory.read(self.fact1_id)
    
    def test_delete_nonexistent(self):
        """Test deleting a nonexistent memory raises KeyError."""
        with self.assertRaises(KeyError):
            self.memory.delete(UUID('00000000-0000-0000-0000-000000000000'))
    
    def test_query_by_content(self):
        """Test querying memory by content."""
        results = self.memory.query("Paris")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "Paris is the capital of France")
    
    def test_query_by_category(self):
        """Test querying memory by category."""
        results = self.memory.query("", category="geography")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["category"], "geography")
    
    def test_query_by_tags(self):
        """Test querying memory by tags."""
        results = self.memory.query("", tags=["programming"])
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "Python is a programming language")
    
    def test_query_exact_match(self):
        """Test querying with exact match option."""
        # This should not match
        results = self.memory.query("Paris", exact_match=True)
        self.assertEqual(len(results), 0)
        
        # This should match
        results = self.memory.query("Paris is the capital of France", exact_match=True)
        self.assertEqual(len(results), 1)


if __name__ == '__main__':
    unittest.main()
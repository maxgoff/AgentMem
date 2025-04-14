"""
Unit tests for EpisodicMemory class.
"""
import unittest
from datetime import datetime, timedelta
from uuid import UUID

from agentmem import EpisodicMemory


class TestEpisodicMemory(unittest.TestCase):
    """Test cases for EpisodicMemory class."""
    
    def setUp(self):
        """Set up a fresh EpisodicMemory instance for each test."""
        self.memory = EpisodicMemory()
        
        # Add some test data
        self.now = datetime.now()
        self.yesterday = self.now - timedelta(days=1)
        self.last_week = self.now - timedelta(days=7)
        
        self.event1_id = self.memory.create(
            content="User asked about Python file handling",
            timestamp=self.yesterday,
            context={"user_id": "user123", "topic": "programming"},
            importance=7
        )
        
        self.event2_id = self.memory.create(
            content="Explained recursive functions to the user",
            timestamp=self.last_week,
            context={"user_id": "user123", "topic": "programming"},
            importance=5
        )
    
    def test_create(self):
        """Test creating a new memory entry."""
        event_id = self.memory.create(
            content="User requested information about climate change",
            timestamp=self.now,
            context={"user_id": "user456", "topic": "science"},
            importance=8
        )
        
        self.assertIsInstance(event_id, UUID)
        self.assertEqual(len(self.memory._storage), 3)
    
    def test_read(self):
        """Test reading a memory entry."""
        event = self.memory.read(self.event1_id)
        
        self.assertEqual(event["content"], "User asked about Python file handling")
        self.assertEqual(event["timestamp"], self.yesterday)
        self.assertEqual(event["importance"], 7)
    
    def test_read_nonexistent(self):
        """Test reading a nonexistent memory raises KeyError."""
        with self.assertRaises(KeyError):
            self.memory.read(UUID('00000000-0000-0000-0000-000000000000'))
    
    def test_update(self):
        """Test updating a memory entry."""
        self.memory.update(
            self.event1_id,
            content="User asked about Python file I/O operations",
            importance=8
        )
        
        updated_event = self.memory.read(self.event1_id)
        self.assertEqual(updated_event["content"], "User asked about Python file I/O operations")
        self.assertEqual(updated_event["importance"], 8)
        self.assertEqual(updated_event["timestamp"], self.yesterday)  # Unchanged
    
    def test_update_nonexistent(self):
        """Test updating a nonexistent memory raises KeyError."""
        with self.assertRaises(KeyError):
            self.memory.update(
                UUID('00000000-0000-0000-0000-000000000000'),
                content="This doesn't exist"
            )
    
    def test_delete(self):
        """Test deleting a memory entry."""
        self.memory.delete(self.event1_id)
        
        self.assertEqual(len(self.memory._storage), 1)
        with self.assertRaises(KeyError):
            self.memory.read(self.event1_id)
    
    def test_delete_nonexistent(self):
        """Test deleting a nonexistent memory raises KeyError."""
        with self.assertRaises(KeyError):
            self.memory.delete(UUID('00000000-0000-0000-0000-000000000000'))
    
    def test_query_by_content(self):
        """Test querying memory by content."""
        results = self.memory.query("Python")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "User asked about Python file handling")
    
    def test_query_by_time_range(self):
        """Test querying memory by time range."""
        # Query for events in the last 2 days
        recent_results = self.memory.query(
            "",
            start_time=self.now - timedelta(days=2),
            end_time=self.now
        )
        
        self.assertEqual(len(recent_results), 1)
        self.assertEqual(recent_results[0]["content"], "User asked about Python file handling")
        
        # Query for all events in the last week
        all_results = self.memory.query(
            "",
            start_time=self.now - timedelta(days=8),
            end_time=self.now
        )
        
        self.assertEqual(len(all_results), 2)
    
    def test_query_by_importance(self):
        """Test querying memory by importance."""
        results = self.memory.query("", min_importance=6)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "User asked about Python file handling")
    
    def test_query_by_context_keys(self):
        """Test querying memory by context keys."""
        results = self.memory.query("", context_keys=["user_id", "topic"])
        
        self.assertEqual(len(results), 2)  # Both have these keys


if __name__ == '__main__':
    unittest.main()
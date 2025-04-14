"""
Unit tests for ProceduralMemory class.
"""
import unittest
from uuid import UUID

from agentmem import ProceduralMemory


class TestProceduralMemory(unittest.TestCase):
    """Test cases for ProceduralMemory class."""
    
    def setUp(self):
        """Set up a fresh ProceduralMemory instance for each test."""
        self.memory = ProceduralMemory()
        
        # Add some test data
        self.proc1_id = self.memory.create(
            content="Creating files in Python",
            task="Create a new file",
            steps=[
                "Use open() with 'w' mode to create a file",
                "Write content using the write() method",
                "Close the file using close() or with statement"
            ],
            prerequisites=["Python installed", "Write permissions"],
            domains=["programming", "python", "file operations"]
        )
        
        self.proc2_id = self.memory.create(
            content="Installing a Python package",
            task="Install a package with pip",
            steps=[
                "Open a terminal or command prompt",
                "Run 'pip install package-name'",
                "Verify installation with 'pip list'"
            ],
            prerequisites=["Python installed", "pip installed", "Internet connection"],
            domains=["programming", "python", "package management"]
        )
    
    def test_create(self):
        """Test creating a new memory entry."""
        proc_id = self.memory.create(
            content="Debugging a recursive function",
            task="Debug recursion issues",
            steps=[
                "Add print statements to trace execution",
                "Check base case handling",
                "Verify recursive calls reduce problem size"
            ],
            domains=["programming", "debugging"]
        )
        
        self.assertIsInstance(proc_id, UUID)
        self.assertEqual(len(self.memory._storage), 3)
    
    def test_read(self):
        """Test reading a memory entry."""
        proc = self.memory.read(self.proc1_id)
        
        self.assertEqual(proc["content"], "Creating files in Python")
        self.assertEqual(proc["task"], "Create a new file")
        self.assertEqual(len(proc["steps"]), 3)
        self.assertEqual(proc["domains"], ["programming", "python", "file operations"])
    
    def test_read_nonexistent(self):
        """Test reading a nonexistent memory raises KeyError."""
        with self.assertRaises(KeyError):
            self.memory.read(UUID('00000000-0000-0000-0000-000000000000'))
    
    def test_update(self):
        """Test updating a memory entry."""
        self.memory.update(
            self.proc1_id,
            content="Creating and writing to files in Python",
            steps=[
                "Use open() with 'w' mode to create a file",
                "Write content using the write() method",
                "Use flush() to ensure data is written",
                "Close the file using close() or with statement"
            ]
        )
        
        updated_proc = self.memory.read(self.proc1_id)
        self.assertEqual(updated_proc["content"], "Creating and writing to files in Python")
        self.assertEqual(len(updated_proc["steps"]), 4)
        self.assertEqual(updated_proc["task"], "Create a new file")  # Unchanged
    
    def test_update_nonexistent(self):
        """Test updating a nonexistent memory raises KeyError."""
        with self.assertRaises(KeyError):
            self.memory.update(
                UUID('00000000-0000-0000-0000-000000000000'),
                content="This doesn't exist"
            )
    
    def test_delete(self):
        """Test deleting a memory entry."""
        self.memory.delete(self.proc1_id)
        
        self.assertEqual(len(self.memory._storage), 1)
        with self.assertRaises(KeyError):
            self.memory.read(self.proc1_id)
    
    def test_delete_nonexistent(self):
        """Test deleting a nonexistent memory raises KeyError."""
        with self.assertRaises(KeyError):
            self.memory.delete(UUID('00000000-0000-0000-0000-000000000000'))
    
    def test_query_by_content(self):
        """Test querying memory by content."""
        results = self.memory.query("file")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "Creating files in Python")
    
    def test_query_by_domain(self):
        """Test querying memory by domain."""
        results = self.memory.query("", domain="python")
        
        self.assertEqual(len(results), 2)  # Both have python domain
    
    def test_query_by_prerequisites(self):
        """Test querying memory by prerequisites."""
        results = self.memory.query("", prerequisites=["Python installed"])
        
        self.assertEqual(len(results), 2)  # Both have this prerequisite
        
        results = self.memory.query("", prerequisites=["Internet connection"])
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["task"], "Install a package with pip")
    
    def test_query_in_steps(self):
        """Test querying for text in steps."""
        results = self.memory.query("pip")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["task"], "Install a package with pip")


if __name__ == '__main__':
    unittest.main()
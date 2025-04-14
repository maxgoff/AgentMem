"""
Integration tests for AgentMem package.

These tests verify that different components of the package work together
correctly and test end-to-end workflows involving multiple memory types
and storage backends.
"""
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta
from uuid import UUID

from agentmem import (EpisodicMemory, ProceduralMemory, SemanticMemory,
                     FileStorage, VectorStorage)


class TestStoragePersistence(unittest.TestCase):
    """Test file-based persistence across memory types."""
    
    def setUp(self):
        """Set up temporary test directories."""
        self.temp_dir = tempfile.mkdtemp()
        self.persistence_dir = os.path.join(self.temp_dir, "persistence")
        self.vector_dir = os.path.join(self.temp_dir, "vector_db")
        os.makedirs(self.persistence_dir, exist_ok=True)
        os.makedirs(self.vector_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)
    
    def test_file_persistence(self):
        """Test persistence across memory instances."""
        # Create memories with persistence
        semantic_mem = SemanticMemory(persistence=self.persistence_dir)
        episodic_mem = EpisodicMemory(persistence=self.persistence_dir)
        procedural_mem = ProceduralMemory(persistence=self.persistence_dir)
        
        # Add entries to each memory type
        fact_id = semantic_mem.create(
            content="Paris is the capital of France",
            category="geography",
            tags=["cities", "europe"]
        )
        
        event_id = episodic_mem.create(
            content="User asked about file handling",
            timestamp=datetime.now(),
            importance=7
        )
        
        proc_id = procedural_mem.create(
            content="How to create a file in Python",
            task="Create a file",
            steps=["Open with 'w' mode", "Write content", "Close the file"]
        )
        
        # Create new instances and verify data persists
        semantic_mem2 = SemanticMemory(persistence=self.persistence_dir)
        episodic_mem2 = EpisodicMemory(persistence=self.persistence_dir)
        procedural_mem2 = ProceduralMemory(persistence=self.persistence_dir)
        
        # Verify semantic memory persistence
        fact = semantic_mem2.read(fact_id)
        self.assertEqual(fact["content"], "Paris is the capital of France")
        self.assertEqual(fact["category"], "geography")
        
        # Verify episodic memory persistence
        event = episodic_mem2.read(event_id)
        self.assertEqual(event["content"], "User asked about file handling")
        self.assertEqual(event["importance"], 7)
        
        # Verify procedural memory persistence
        proc = procedural_mem2.read(proc_id)
        self.assertEqual(proc["content"], "How to create a file in Python")
        self.assertEqual(len(proc["steps"]), 3)
        
        # Test updating through second instance
        semantic_mem2.update(fact_id, tags=["cities", "europe", "countries"])
        updated_fact = semantic_mem.read(fact_id)  # Read from first instance
        self.assertEqual(len(updated_fact["tags"]), 3)
        
        # Test deletion through second instance
        episodic_mem2.delete(event_id)
        with self.assertRaises(KeyError):
            episodic_mem.read(event_id)  # Should be gone from first instance too


class TestVectorSearch(unittest.TestCase):
    """Test vector search capabilities."""
    
    def setUp(self):
        """Set up temporary test directories."""
        self.temp_dir = tempfile.mkdtemp()
        self.persistence_dir = os.path.join(self.temp_dir, "persistence")
        self.vector_dir = os.path.join(self.temp_dir, "vector_db")
        os.makedirs(self.persistence_dir, exist_ok=True)
        os.makedirs(self.vector_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)
    
    def test_semantic_vector_search(self):
        """Test semantic search with vector database."""
        # Create semantic memory with vector search
        memory = SemanticMemory(
            persistence=self.persistence_dir,
            vector_search=True,
            vector_db_path=self.vector_dir
        )
        
        # Add test facts about different topics
        space_facts = [
            "The Earth is the third planet from the Sun",
            "Jupiter is the largest planet in our solar system",
            "The Moon orbits the Earth and is our only natural satellite"
        ]
        
        ocean_facts = [
            "The Pacific Ocean is the largest ocean on Earth",
            "Oceans cover about 71% of Earth's surface",
            "The Mariana Trench is the deepest part of the world's oceans"
        ]
        
        # Add facts to memory with appropriate categories
        for fact in space_facts:
            memory.create(content=fact, category="astronomy")
            
        for fact in ocean_facts:
            memory.create(content=fact, category="oceanography")
        
        # Test standard keyword search
        planet_results = memory.query("planet", use_vector=False)
        self.assertEqual(len(planet_results), 2)  # Should find 2 planet facts
        
        # Test vector search for conceptually related items
        celestial_results = memory.query("celestial objects in space")
        self.assertGreaterEqual(len(celestial_results), 2)
        
        # Test category filtering with vector search
        water_results = memory.query("water bodies", category="oceanography")
        self.assertGreaterEqual(len(water_results), 1)
        
        # Make sure category filter works (no astronomy results when filtering for oceanography)
        for result in water_results:
            self.assertEqual(result["category"], "oceanography")


class TestMultiMemoryWorkflow(unittest.TestCase):
    """Test workflows involving multiple memory types."""
    
    def setUp(self):
        """Create memory instances."""
        self.semantic_mem = SemanticMemory()
        self.episodic_mem = EpisodicMemory()
        self.procedural_mem = ProceduralMemory()
    
    def test_agent_learning_workflow(self):
        """
        Test a workflow that simulates an agent learning from interactions.
        
        This test simulates:
        1. Agent stores factual knowledge in semantic memory
        2. Agent has interactions stored in episodic memory
        3. Agent learns procedures and stores them in procedural memory
        4. Agent retrieves relevant information across memory types
        """
        # Step 1: Agent learns facts about Python
        python_fact_id = self.semantic_mem.create(
            content="Python is a high-level programming language",
            category="programming",
            tags=["languages", "python", "coding"]
        )
        
        file_fact_id = self.semantic_mem.create(
            content="Files in Python are opened using the open() function",
            category="programming",
            tags=["python", "files", "io"]
        )
        
        # Step 2: Agent has interactions with a user about Python files
        yesterday = datetime.now() - timedelta(days=1)
        
        interaction1_id = self.episodic_mem.create(
            content="User asked how to open files in Python",
            timestamp=yesterday,
            context={"user_id": "user123", "topic": "python_files"},
            importance=7
        )
        
        interaction2_id = self.episodic_mem.create(
            content="Explained file modes (read, write, append) to User",
            timestamp=yesterday + timedelta(hours=1),
            context={"user_id": "user123", "topic": "python_files"},
            importance=6
        )
        
        # Step 3: Agent develops procedural knowledge
        procedure_id = self.procedural_mem.create(
            content="Opening and writing to files in Python",
            task="Write data to a file",
            steps=[
                "Open the file using open(filename, 'w')",
                "Use file.write() to write data",
                "Close the file using file.close() or with statement"
            ],
            domains=["python", "file handling"]
        )
        
        # Step 4: Agent retrieves relevant information across memory types
        # Simulate receiving a query about Python files
        
        # First check episodic memory for past interactions on the topic
        past_interactions = self.episodic_mem.query(
            "file",
            context_keys=["topic"]
        )
        
        # Agent should find the past interactions about Python files
        self.assertGreaterEqual(len(past_interactions), 2)
        
        # Then check semantic memory for facts about Python files
        file_facts = self.semantic_mem.query("file", tags=["python"])
        self.assertGreaterEqual(len(file_facts), 1)
        
        # Finally, retrieve procedural knowledge about file handling
        file_procedures = self.procedural_mem.query("file", domain="python")
        self.assertGreaterEqual(len(file_procedures), 1)
        
        # Verify procedure steps are intact
        procedure = self.procedural_mem.read(procedure_id)
        self.assertEqual(len(procedure["steps"]), 3)


if __name__ == "__main__":
    unittest.main()
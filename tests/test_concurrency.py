"""
Tests for concurrency support in AgentMem.

This module contains tests for thread-safety and concurrent operations
on memory systems.
"""
import concurrent.futures
import os
import random
import shutil
import tempfile
import threading
import time
import unittest
from typing import List
from uuid import UUID

from agentmem import SemanticMemory
from agentmem.concurrency import lock_manager


class TestConcurrency(unittest.TestCase):
    """Test cases for concurrency support."""
    
    def setUp(self):
        """Set up test environment with temporary directories."""
        self.temp_dir = tempfile.mkdtemp()
        self.persistence_dir = os.path.join(self.temp_dir, "persistence")
        self.vector_dir = os.path.join(self.temp_dir, "vector_db")
        os.makedirs(self.persistence_dir, exist_ok=True)
        os.makedirs(self.vector_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)
    
    def test_concurrent_create(self):
        """Test concurrent creation of memory entries."""
        num_threads = 10
        entries_per_thread = 10
        
        memory = SemanticMemory(
            persistence=self.persistence_dir,
            vector_search=True,
            vector_db_path=self.vector_dir
        )
        
        # Shared list to store created memory IDs
        memory_ids = []
        lock = threading.Lock()
        
        def create_entries(thread_id: int) -> None:
            """Create multiple entries from a single thread."""
            for i in range(entries_per_thread):
                content = f"Test fact {thread_id}-{i}"
                category = random.choice(["test", "concurrency", "threading"])
                tags = random.sample(["thread-safe", "concurrent", "atomic", "locked"], 2)
                
                # Create memory entry
                memory_id = memory.create(
                    content=content,
                    category=category,
                    tags=tags
                )
                
                # Add to shared list
                with lock:
                    memory_ids.append(memory_id)
        
        # Create and start threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=create_entries, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all entries were created correctly
        self.assertEqual(len(memory_ids), num_threads * entries_per_thread)
        
        # Verify each entry can be read
        for memory_id in memory_ids:
            data = memory.read(memory_id)
            self.assertIn("content", data)
            self.assertIn("category", data)
            self.assertIn("tags", data)
    
    def test_concurrent_read_update(self):
        """Test concurrent reading and updating of memory entries."""
        # Create memory instance
        memory = SemanticMemory(
            persistence=self.persistence_dir
        )
        
        # Create test entries
        memory_ids = []
        for i in range(5):
            memory_id = memory.create(
                content=f"Original fact {i}",
                category="original",
                tags=["initial", "unmodified"]
            )
            memory_ids.append(memory_id)
        
        # Function to update entries
        def update_entries(memory_ids: List[UUID]) -> None:
            """Update memory entries."""
            for memory_id in memory_ids:
                memory.update(
                    memory_id,
                    content=f"Updated fact {random.randint(1000, 9999)}",
                    tags=["modified", "updated", str(random.randint(1, 100))]
                )
                # Small delay to increase chance of concurrency issues
                time.sleep(0.01)
        
        # Function to read entries
        def read_entries(memory_ids: List[UUID]) -> None:
            """Read memory entries."""
            for memory_id in memory_ids:
                data = memory.read(memory_id)
                self.assertIn("content", data)
                self.assertIn("tags", data)
                # Small delay to increase chance of concurrency issues
                time.sleep(0.01)
        
        # Run update and read concurrently using thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            # Submit multiple read and update tasks
            futures = []
            for _ in range(5):
                futures.append(executor.submit(update_entries, memory_ids[:]))
                futures.append(executor.submit(read_entries, memory_ids[:]))
            
            # Wait for all tasks to complete
            for future in concurrent.futures.as_completed(futures):
                # This will raise any exceptions that occurred in the threads
                future.result()
    
    def test_lock_reentry(self):
        """Test that locks are reentrant."""
        # Test memory type lock reentry
        with lock_manager.memory_type_lock("semantic"):
            # This should not deadlock
            with lock_manager.memory_type_lock("semantic"):
                pass
        
        # Test memory ID lock reentry
        test_id = UUID('00000000-0000-0000-0000-000000000000')
        with lock_manager.memory_id_lock(test_id):
            # This should not deadlock
            with lock_manager.memory_id_lock(test_id):
                pass
        
        # Test transaction reentry
        with lock_manager.transaction(memory_type="semantic", memory_ids={test_id}):
            # This should not deadlock
            with lock_manager.memory_id_lock(test_id):
                pass


if __name__ == "__main__":
    unittest.main()
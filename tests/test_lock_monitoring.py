"""
Tests for lock monitoring in AgentMem.

This module contains tests for the lock contention monitoring system.
"""
import concurrent.futures
import threading
import time
import unittest
from uuid import UUID

from agentmem.concurrency import MemoryLock, lock_manager


class TestLockMonitoring(unittest.TestCase):
    """Test cases for lock monitoring system."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a clean lock manager for each test with monitoring enabled
        self.test_lock_manager = MemoryLock(enable_monitoring=True, max_history=100)
    
    def test_metrics_collection(self):
        """Test that metrics are collected properly."""
        # Perform some lock operations
        with self.test_lock_manager.global_lock():
            time.sleep(0.01)  # Small delay to ensure measurable duration
        
        with self.test_lock_manager.memory_type_lock("semantic"):
            time.sleep(0.01)
        
        test_id = UUID('00000000-0000-0000-0000-000000000000')
        with self.test_lock_manager.memory_id_lock(test_id):
            time.sleep(0.01)
        
        # Get statistics
        stats = self.test_lock_manager.get_lock_statistics()
        
        # Verify that metrics were collected
        self.assertIn("global", stats)
        self.assertIn("type:semantic", stats)
        self.assertIn("id:00000000-0000-0000-0000-000000000000", stats)
        
        # Verify structure of statistics
        for lock_name in ["global", "type:semantic", 
                         "id:00000000-0000-0000-0000-000000000000"]:
            self.assertIn("avg_acquisition_time", stats[lock_name])
            self.assertIn("max_acquisition_time", stats[lock_name])
            self.assertIn("min_acquisition_time", stats[lock_name])
            self.assertIn("avg_hold_duration", stats[lock_name])
            self.assertIn("max_hold_duration", stats[lock_name])
            self.assertIn("min_hold_duration", stats[lock_name])
            self.assertIn("contention_count", stats[lock_name])
    
    def test_history_tracking(self):
        """Test that lock operation history is tracked properly."""
        # Perform some lock operations
        with self.test_lock_manager.global_lock():
            pass
        
        with self.test_lock_manager.memory_type_lock("semantic"):
            pass
        
        test_id = UUID('00000000-0000-0000-0000-000000000000')
        with self.test_lock_manager.memory_id_lock(test_id):
            pass
        
        # Get history
        history = self.test_lock_manager.get_lock_history()
        
        # Verify history content
        self.assertEqual(len(history), 6)  # 3 acquisitions, 3 releases
        
        # Verify history format
        for entry in history:
            self.assertEqual(len(entry), 4)  # timestamp, lock name, action, duration
            timestamp, lock_name, action, duration = entry
            self.assertIn(action, ["acquire", "release"])
            self.assertGreaterEqual(duration, 0)
    
    def test_active_locks_tracking(self):
        """Test tracking of active locks."""
        # Acquire a lock and check active locks
        lock_event = threading.Event()
        lock_acquired = threading.Event()
        
        def hold_lock():
            with self.test_lock_manager.global_lock():
                lock_acquired.set()
                # Wait for signal to release lock
                lock_event.wait()
        
        # Start thread that holds a lock
        thread = threading.Thread(target=hold_lock)
        thread.start()
        
        # Wait for lock to be acquired
        lock_acquired.wait()
        
        # Check active locks
        active_locks = self.test_lock_manager.get_active_locks()
        self.assertIn("global", active_locks)
        self.assertEqual(active_locks["global"][0].name, thread.name)
        
        # Signal thread to release lock
        lock_event.set()
        thread.join()
        
        # Check that lock is no longer active
        active_locks = self.test_lock_manager.get_active_locks()
        self.assertNotIn("global", active_locks)
    
    def test_contention_tracking(self):
        """Test tracking of lock contention."""
        # This test will create artificial contention by having multiple
        # threads try to acquire the same lock simultaneously
        
        lock_held = threading.Event()
        threads_ready = threading.Event()
        lock_released = threading.Event()
        
        def first_holder():
            # First thread acquires and holds the lock
            with self.test_lock_manager.global_lock():
                lock_held.set()
                # Wait for other threads to be ready
                threads_ready.wait()
                # Hold the lock for a while to ensure contention
                time.sleep(0.1)
            lock_released.set()
        
        def contender():
            # Wait for first thread to acquire lock
            lock_held.wait()
            # Signal ready
            threads_ready.set()
            # Try to acquire the lock (will be contention)
            with self.test_lock_manager.global_lock():
                pass
        
        # Start first thread to hold the lock
        first_thread = threading.Thread(target=first_holder)
        first_thread.start()
        
        # Wait for it to acquire the lock
        lock_held.wait()
        
        # Start multiple contender threads
        contender_threads = []
        for _ in range(3):
            thread = threading.Thread(target=contender)
            contender_threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        first_thread.join()
        for thread in contender_threads:
            thread.join()
        
        # Check contention statistics
        stats = self.test_lock_manager.get_lock_statistics()
        self.assertIn("global", stats)
        
        # Note: Contention might be underreported because threads might
        # wait for each other before even attempting to acquire the lock
        # But we should have at least some contention
        self.assertGreaterEqual(stats["global"]["contention_count"], 1)
    
    def test_disable_monitoring(self):
        """Test enabling and disabling monitoring."""
        # Start with monitoring enabled
        self.assertTrue(self.test_lock_manager._enable_monitoring)
        
        # Perform an operation with monitoring enabled
        with self.test_lock_manager.global_lock():
            pass
        
        # Verify that metrics were collected
        stats_before = self.test_lock_manager.get_lock_statistics()
        self.assertIn("global", stats_before)
        
        # Disable monitoring
        self.test_lock_manager.enable_monitoring(False)
        self.assertFalse(self.test_lock_manager._enable_monitoring)
        
        # Perform an operation with monitoring disabled
        with self.test_lock_manager.global_lock():
            pass
        
        # Verify that no new metrics were collected
        stats_after = self.test_lock_manager.get_lock_statistics()
        self.assertEqual(stats_after, {})
        
        # Re-enable monitoring
        self.test_lock_manager.enable_monitoring(True)
        self.assertTrue(self.test_lock_manager._enable_monitoring)
        
        # Perform an operation with monitoring re-enabled
        with self.test_lock_manager.global_lock():
            pass
        
        # Verify that metrics are collected again
        stats_final = self.test_lock_manager.get_lock_statistics()
        self.assertIn("global", stats_final)
    
    def test_reset_metrics(self):
        """Test resetting metrics."""
        # Perform some lock operations
        with self.test_lock_manager.global_lock():
            pass
        
        # Verify that metrics were collected
        stats_before = self.test_lock_manager.get_lock_statistics()
        self.assertIn("global", stats_before)
        
        # Reset metrics
        self.test_lock_manager.reset_metrics()
        
        # Verify that metrics were reset
        stats_after = self.test_lock_manager.get_lock_statistics()
        self.assertEqual(len(stats_after), 0)
        
        # Perform operations again to verify metrics collection still works
        with self.test_lock_manager.global_lock():
            pass
        
        # Verify that new metrics are collected
        stats_final = self.test_lock_manager.get_lock_statistics()
        self.assertIn("global", stats_final)
    
    def test_transaction_monitoring(self):
        """Test monitoring of transactions."""
        # Perform a transaction operation
        test_id1 = UUID('00000000-0000-0000-0000-000000000001')
        test_id2 = UUID('00000000-0000-0000-0000-000000000002')
        
        with self.test_lock_manager.transaction(
            memory_type="semantic", 
            memory_ids={test_id1, test_id2}
        ):
            time.sleep(0.01)
        
        # Get history
        history = self.test_lock_manager.get_lock_history()
        
        # Verify transaction locks were recorded
        transaction_entries = [entry for entry in history if "transaction:" in entry[1]]
        self.assertGreaterEqual(len(transaction_entries), 6)  # At least 6 entries (3 locks acquired, 3 locks released)


if __name__ == "__main__":
    unittest.main()
"""
Concurrency support for AgentMem.

This module provides thread-safety mechanisms for memory operations 
in multi-threaded environments, along with monitoring capabilities
to track lock contention and performance metrics.
"""
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, Optional, Set, Type, List, Tuple
from uuid import UUID


class LockMetrics:
    """
    Tracks metrics for lock usage and contention.
    
    This class collects data on lock acquisition times, holding durations,
    contention, and other performance metrics to help diagnose bottlenecks
    in concurrent memory operations.
    """
    
    def __init__(self, max_history: int = 1000):
        """Initialize the metrics collector.
        
        Args:
            max_history: Maximum number of lock events to store in history
        """
        self._lock = threading.RLock()
        self._max_history = max_history
        
        # Metrics storage
        self._acquisition_times: Dict[str, List[float]] = {}  # Lock name -> list of acquisition times
        self._hold_durations: Dict[str, List[float]] = {}     # Lock name -> list of lock holding durations
        self._contention_counts: Dict[str, int] = {}          # Lock name -> count of contention events
        self._lock_history: List[Tuple[datetime, str, str, float]] = []  # Timestamp, lock type, action, duration
        
        # Lock status tracking
        self._active_locks: Dict[str, Tuple[threading.Thread, datetime]] = {}  # Lock name -> (thread, acquisition time)
    
    def record_acquisition_start(self, lock_name: str) -> None:
        """Record the start of a lock acquisition attempt.
        
        Args:
            lock_name: Name/identifier of the lock being acquired
        """
        with self._lock:
            thread = threading.current_thread()
            self._active_locks[lock_name] = (thread, datetime.now())
    
    def record_acquisition_end(self, lock_name: str, success: bool = True, duration: float = 0.0) -> None:
        """Record the end of a lock acquisition attempt.
        
        Args:
            lock_name: Name/identifier of the lock
            success: Whether the acquisition was successful
            duration: Time taken to acquire the lock
        """
        with self._lock:
            if success:
                if lock_name not in self._acquisition_times:
                    self._acquisition_times[lock_name] = []
                
                self._acquisition_times[lock_name].append(duration)
                self._acquisition_times[lock_name] = self._acquisition_times[lock_name][-self._max_history:]
                
                # Record the event in history
                self._lock_history.append((datetime.now(), lock_name, "acquire", duration))
                self._lock_history = self._lock_history[-self._max_history:]
            else:
                # Record contention
                self._contention_counts[lock_name] = self._contention_counts.get(lock_name, 0) + 1
    
    def record_release(self, lock_name: str) -> None:
        """Record the release of a lock.
        
        Args:
            lock_name: Name/identifier of the lock being released
        """
        with self._lock:
            if lock_name in self._active_locks:
                thread, acquisition_time = self._active_locks[lock_name]
                duration = (datetime.now() - acquisition_time).total_seconds()
                
                if lock_name not in self._hold_durations:
                    self._hold_durations[lock_name] = []
                
                self._hold_durations[lock_name].append(duration)
                self._hold_durations[lock_name] = self._hold_durations[lock_name][-self._max_history:]
                
                # Record the event in history
                self._lock_history.append((datetime.now(), lock_name, "release", duration))
                self._lock_history = self._lock_history[-self._max_history:]
                
                del self._active_locks[lock_name]
    
    def get_lock_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all locks.
        
        Returns:
            Dictionary of lock statistics, with keys being lock names and values
            being dictionaries of statistics
        """
        with self._lock:
            stats = {}
            
            for lock_name in set(list(self._acquisition_times.keys()) + 
                               list(self._hold_durations.keys()) + 
                               list(self._contention_counts.keys())):
                lock_stats = {}
                
                # Acquisition time statistics
                acquisition_times = self._acquisition_times.get(lock_name, [])
                if acquisition_times:
                    lock_stats["avg_acquisition_time"] = sum(acquisition_times) / len(acquisition_times)
                    lock_stats["max_acquisition_time"] = max(acquisition_times)
                    lock_stats["min_acquisition_time"] = min(acquisition_times)
                
                # Hold duration statistics
                hold_durations = self._hold_durations.get(lock_name, [])
                if hold_durations:
                    lock_stats["avg_hold_duration"] = sum(hold_durations) / len(hold_durations)
                    lock_stats["max_hold_duration"] = max(hold_durations)
                    lock_stats["min_hold_duration"] = min(hold_durations)
                
                # Contention statistics
                lock_stats["contention_count"] = self._contention_counts.get(lock_name, 0)
                
                stats[lock_name] = lock_stats
            
            return stats
    
    def get_history(self) -> List[Tuple[datetime, str, str, float]]:
        """Get the lock operation history.
        
        Returns:
            List of tuples (timestamp, lock name, action, duration)
        """
        with self._lock:
            return list(self._lock_history)
    
    def get_active_locks(self) -> Dict[str, Tuple[threading.Thread, datetime]]:
        """Get currently active locks.
        
        Returns:
            Dictionary of lock name -> (thread, acquisition time)
        """
        with self._lock:
            return dict(self._active_locks)


class MemoryLock:
    """
    Thread-safe locking mechanism for memory operations with monitoring.
    
    This class provides different levels of locking:
    - Global lock for operations that affect the entire memory system
    - Memory type locks for operations specific to memory types
    - Memory ID locks for operations on specific memory entries
    
    Thread safety is ensured with minimal contention by using
    a hierarchical locking strategy. Lock performance is monitored
    to help diagnose bottlenecks.
    """
    
    def __init__(self, enable_monitoring: bool = True, max_history: int = 1000):
        """Initialize the lock manager.
        
        Args:
            enable_monitoring: Whether to enable lock monitoring
            max_history: Maximum number of lock events to store in history
        """
        self._global_lock = threading.RLock()
        self._memory_type_locks: Dict[str, threading.RLock] = {}
        self._memory_id_locks: Dict[UUID, threading.RLock] = {}
        self._memory_id_locks_lock = threading.RLock()  # Lock for modifying _memory_id_locks
        
        # Lock monitoring
        self._enable_monitoring = enable_monitoring
        self._metrics = LockMetrics(max_history=max_history) if enable_monitoring else None
    
    @contextmanager
    def global_lock(self):
        """
        Acquire the global lock for operations affecting the entire memory system.
        
        This should be used for operations that need exclusive access to all
        memory resources, such as saving all memory to disk or clearing all memory.
        
        Usage:
            with lock_manager.global_lock():
                # Perform global operations
        """
        lock_name = "global"
        start_time = None
        
        # Record acquisition start if monitoring enabled
        if self._enable_monitoring and self._metrics:
            self._metrics.record_acquisition_start(lock_name)
            start_time = time.time()
        
        self._global_lock.acquire()
        
        # Record acquisition success if monitoring enabled
        if self._enable_monitoring and self._metrics and start_time is not None:
            duration = time.time() - start_time
            self._metrics.record_acquisition_end(lock_name, success=True, duration=duration)
        
        try:
            yield
        finally:
            # Record lock release if monitoring enabled
            if self._enable_monitoring and self._metrics:
                self._metrics.record_release(lock_name)
            
            self._global_lock.release()
    
    @contextmanager
    def memory_type_lock(self, memory_type: str):
        """
        Acquire a lock specific to a memory type.
        
        This should be used for operations affecting all entries of a specific
        memory type, such as querying all semantic memories.
        
        Args:
            memory_type: Type of memory to lock ('semantic', 'episodic', or 'procedural')
            
        Usage:
            with lock_manager.memory_type_lock('semantic'):
                # Perform operations on semantic memory
        """
        lock_name = f"type:{memory_type}"
        start_time = None
        
        # Record acquisition start if monitoring enabled
        if self._enable_monitoring and self._metrics:
            self._metrics.record_acquisition_start(lock_name)
            start_time = time.time()
            
        # Get or create the lock
        with self._global_lock:
            if memory_type not in self._memory_type_locks:
                self._memory_type_locks[memory_type] = threading.RLock()
            lock = self._memory_type_locks[memory_type]
        
        lock.acquire()
        
        # Record acquisition success if monitoring enabled
        if self._enable_monitoring and self._metrics and start_time is not None:
            duration = time.time() - start_time
            self._metrics.record_acquisition_end(lock_name, success=True, duration=duration)
        
        try:
            yield
        finally:
            # Record lock release if monitoring enabled
            if self._enable_monitoring and self._metrics:
                self._metrics.record_release(lock_name)
                
            lock.release()
    
    @contextmanager
    def memory_id_lock(self, memory_id: UUID):
        """
        Acquire a lock specific to a memory entry.
        
        This should be used for operations on specific memory entries,
        such as updating or deleting a specific memory.
        
        Args:
            memory_id: UUID of the memory entry to lock
            
        Usage:
            with lock_manager.memory_id_lock(memory_id):
                # Perform operations on a specific memory entry
        """
        lock_name = f"id:{memory_id}"
        start_time = None
        
        # Record acquisition start if monitoring enabled
        if self._enable_monitoring and self._metrics:
            self._metrics.record_acquisition_start(lock_name)
            start_time = time.time()
        
        # Get or create the lock
        with self._memory_id_locks_lock:
            if memory_id not in self._memory_id_locks:
                self._memory_id_locks[memory_id] = threading.RLock()
            lock = self._memory_id_locks[memory_id]
        
        lock.acquire()
        
        # Record acquisition success if monitoring enabled
        if self._enable_monitoring and self._metrics and start_time is not None:
            duration = time.time() - start_time
            self._metrics.record_acquisition_end(lock_name, success=True, duration=duration)
        
        try:
            yield
        finally:
            # Record lock release if monitoring enabled
            if self._enable_monitoring and self._metrics:
                self._metrics.record_release(lock_name)
            
            lock.release()
            
            # Clean up the lock if no longer needed
            with self._memory_id_locks_lock:
                try:
                    # For Python < 3.12
                    if hasattr(lock, '_RLock__count') and not lock._is_owned() and lock._RLock__count == 0:
                        del self._memory_id_locks[memory_id]
                    # For Python >= 3.12
                    elif hasattr(lock, '_count') and not lock._is_owned() and lock._count == 0:
                        del self._memory_id_locks[memory_id]
                except (AttributeError, TypeError):
                    # If can't determine lock count, safely keep the lock
                    pass
    
    @contextmanager
    def transaction(self, memory_type: Optional[str] = None, memory_ids: Optional[Set[UUID]] = None):
        """
        Create a transaction that locks multiple resources atomically.
        
        This method acquires multiple locks in a specific order to prevent deadlocks.
        The locking order is:
        1. Global lock (if needed)
        2. Memory type locks (if specified)
        3. Memory ID locks (if specified)
        
        Args:
            memory_type: Optional memory type to lock
            memory_ids: Optional set of memory IDs to lock
            
        Usage:
            with lock_manager.transaction(memory_type='semantic', memory_ids={id1, id2}):
                # Perform operations that need to be atomic
        """
        transaction_id = f"transaction:{time.time()}"
        lock_names = []
        locks_to_release = []
        start_times = {}
        
        try:
            # If no specific locks are requested, use the global lock
            if memory_type is None and (memory_ids is None or len(memory_ids) == 0):
                lock_name = "global"
                lock_names.append(lock_name)
                
                # Record acquisition start if monitoring enabled
                if self._enable_monitoring and self._metrics:
                    self._metrics.record_acquisition_start(f"{transaction_id}:{lock_name}")
                    start_times[lock_name] = time.time()
                
                self._global_lock.acquire()
                
                # Record acquisition success if monitoring enabled
                if self._enable_monitoring and self._metrics and lock_name in start_times:
                    duration = time.time() - start_times[lock_name]
                    self._metrics.record_acquisition_end(f"{transaction_id}:{lock_name}", 
                                                        success=True, duration=duration)
                
                locks_to_release.append((self._global_lock, lock_name))
                yield
                return
            
            # Acquire memory type lock if specified
            if memory_type is not None:
                lock_name = f"type:{memory_type}"
                lock_names.append(lock_name)
                
                # Record acquisition start if monitoring enabled
                if self._enable_monitoring and self._metrics:
                    self._metrics.record_acquisition_start(f"{transaction_id}:{lock_name}")
                    start_times[lock_name] = time.time()
                
                with self._global_lock:
                    if memory_type not in self._memory_type_locks:
                        self._memory_type_locks[memory_type] = threading.RLock()
                    type_lock = self._memory_type_locks[memory_type]
                
                type_lock.acquire()
                
                # Record acquisition success if monitoring enabled
                if self._enable_monitoring and self._metrics and lock_name in start_times:
                    duration = time.time() - start_times[lock_name]
                    self._metrics.record_acquisition_end(f"{transaction_id}:{lock_name}", 
                                                        success=True, duration=duration)
                
                locks_to_release.append((type_lock, lock_name))
            
            # Acquire memory ID locks if specified
            if memory_ids is not None and len(memory_ids) > 0:
                # Sort memory IDs to ensure consistent locking order
                sorted_ids = sorted(memory_ids, key=str)
                
                for memory_id in sorted_ids:
                    lock_name = f"id:{memory_id}"
                    lock_names.append(lock_name)
                    
                    # Record acquisition start if monitoring enabled
                    if self._enable_monitoring and self._metrics:
                        self._metrics.record_acquisition_start(f"{transaction_id}:{lock_name}")
                        start_times[lock_name] = time.time()
                    
                    with self._memory_id_locks_lock:
                        if memory_id not in self._memory_id_locks:
                            self._memory_id_locks[memory_id] = threading.RLock()
                        id_lock = self._memory_id_locks[memory_id]
                    
                    id_lock.acquire()
                    
                    # Record acquisition success if monitoring enabled
                    if self._enable_monitoring and self._metrics and lock_name in start_times:
                        duration = time.time() - start_times[lock_name]
                        self._metrics.record_acquisition_end(f"{transaction_id}:{lock_name}", 
                                                           success=True, duration=duration)
                    
                    locks_to_release.append((id_lock, lock_name))
            
            yield
            
        finally:
            # Release all locks in reverse order
            for lock, lock_name in reversed(locks_to_release):
                # Record lock release if monitoring enabled
                if self._enable_monitoring and self._metrics:
                    self._metrics.record_release(f"{transaction_id}:{lock_name}")
                
                lock.release()
                
                # Clean up ID locks
                if memory_ids is not None:
                    with self._memory_id_locks_lock:
                        for memory_id in memory_ids:
                            if memory_id in self._memory_id_locks:
                                id_lock = self._memory_id_locks[memory_id]
                                try:
                                    # For Python < 3.12
                                    if hasattr(id_lock, '_RLock__count') and not id_lock._is_owned() and id_lock._RLock__count == 0:
                                        del self._memory_id_locks[memory_id]
                                    # For Python >= 3.12
                                    elif hasattr(id_lock, '_count') and not id_lock._is_owned() and id_lock._count == 0:
                                        del self._memory_id_locks[memory_id]
                                except (AttributeError, TypeError):
                                    # If can't determine lock count, safely keep the lock
                                    pass


    def get_metrics(self) -> Optional[LockMetrics]:
        """Get the metrics collector instance.
        
        Returns:
            The LockMetrics instance if monitoring is enabled, None otherwise
        """
        return self._metrics if self._enable_monitoring else None
    
    def get_lock_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all locks.
        
        Returns:
            Dictionary of lock statistics
        """
        if self._enable_monitoring and self._metrics:
            return self._metrics.get_lock_statistics()
        return {}
    
    def get_active_locks(self) -> Dict[str, Tuple[threading.Thread, datetime]]:
        """Get currently active locks.
        
        Returns:
            Dictionary of lock name -> (thread, acquisition time)
        """
        if self._enable_monitoring and self._metrics:
            return self._metrics.get_active_locks()
        return {}
    
    def get_lock_history(self) -> List[Tuple[datetime, str, str, float]]:
        """Get the lock operation history.
        
        Returns:
            List of tuples (timestamp, lock name, action, duration)
        """
        if self._enable_monitoring and self._metrics:
            return self._metrics.get_history()
        return []
    
    def enable_monitoring(self, enable: bool = True) -> None:
        """Enable or disable lock monitoring.
        
        Args:
            enable: Whether to enable monitoring
        """
        if enable and not self._enable_monitoring:
            self._enable_monitoring = True
            self._metrics = LockMetrics()
        elif not enable and self._enable_monitoring:
            self._enable_monitoring = False
            self._metrics = None
    
    def reset_metrics(self) -> None:
        """Reset all metrics to zero/empty state."""
        if self._enable_monitoring:
            self._metrics = LockMetrics()


# Global lock manager instance
lock_manager = MemoryLock()
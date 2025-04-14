"""
Memory usage tracking for AgentMem.

This module provides utilities for tracking memory usage of
various components in the AgentMem system.
"""
import sys
import threading
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

from agentmem.logging.logger import get_logger
from agentmem.logging.metrics import get_metrics_collector, OperationType


def estimate_size(obj: Any) -> int:
    """Estimate the memory size of an object in bytes.
    
    Note: This is a rough approximation and may not be accurate for all objects.
    
    Args:
        obj: The object to measure
        
    Returns:
        Estimated size in bytes
    """
    # Get size of basic types directly
    if obj is None:
        return 8  # Pointer size
    elif isinstance(obj, (int, float, bool)):
        return 24  # Basic Python object overhead + value
    elif isinstance(obj, str):
        return sys.getsizeof(obj)
    
    # For collections, recursively sum the sizes
    elif isinstance(obj, (list, tuple, set)):
        return sys.getsizeof(obj) + sum(estimate_size(x) for x in obj)
    elif isinstance(obj, dict):
        return sys.getsizeof(obj) + sum(
            estimate_size(k) + estimate_size(v) for k, v in obj.items()
        )
    
    # For custom objects, use __dict__ if available
    elif hasattr(obj, "__dict__"):
        return sys.getsizeof(obj) + estimate_size(obj.__dict__)
    
    # Fall back to sys.getsizeof for other types
    else:
        try:
            return sys.getsizeof(obj)
        except (TypeError, AttributeError):
            # For objects that don't support sys.getsizeof
            return 64  # Estimated object overhead


@contextmanager
def track_operation(operation: OperationType, memory_type: str, details: Optional[Dict[str, Any]] = None):
    """Context manager to track a memory operation.
    
    Args:
        operation: The type of operation being performed
        memory_type: The type of memory being operated on
        details: Optional details about the operation
        
    Yields:
        None
    """
    metrics = get_metrics_collector()
    start_time = time.time()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        metrics.record_operation(operation, memory_type, duration, details)


class MemoryTracker:
    """Tracks memory usage of AgentMem components."""
    
    def __init__(self, update_interval_sec: float = 60.0):
        """Initialize the memory tracker.
        
        Args:
            update_interval_sec: How often to update memory usage statistics
        """
        self.logger = get_logger("agentmem.memory_tracker")
        self._lock = threading.RLock()
        self._metrics = get_metrics_collector()
        self._update_interval_sec = update_interval_sec
        self._last_update_time: Dict[str, float] = {}
        self._tracking_enabled = True
        self._memory_updaters: Dict[str, Callable[[], int]] = {}
    
    def register_memory_source(self, memory_type: str, size_getter: Callable[[], int]) -> None:
        """Register a function that returns the current size of a memory component.
        
        Args:
            memory_type: Type of memory 
            size_getter: Function that returns the current size in bytes
        """
        with self._lock:
            self._memory_updaters[memory_type] = size_getter
    
    def update_memory_usage(self, memory_type: Optional[str] = None, force: bool = False) -> None:
        """Update memory usage statistics.
        
        Args:
            memory_type: Specific memory type to update (None for all registered types)
            force: Whether to update even if the interval hasn't elapsed
        """
        if not self._tracking_enabled:
            return
        
        current_time = time.time()
        
        with self._lock:
            # Determine which memory types to update
            types_to_update = set()
            if memory_type is not None:
                if memory_type in self._memory_updaters:
                    types_to_update.add(memory_type)
                else:
                    self.logger.warning(f"Unknown memory type: {memory_type}")
                    return
            else:
                types_to_update = set(self._memory_updaters.keys())
            
            # Update each memory type if needed
            for mem_type in types_to_update:
                last_update = self._last_update_time.get(mem_type, 0)
                
                if force or (current_time - last_update >= self._update_interval_sec):
                    try:
                        size_bytes = self._memory_updaters[mem_type]()
                        self._metrics.update_memory_size(mem_type, size_bytes)
                        self._last_update_time[mem_type] = current_time
                        self.logger.debug(
                            f"Updated memory usage for {mem_type}: "
                            f"{size_bytes / (1024*1024):.2f} MB"
                        )
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to update memory usage for {mem_type}: {str(e)}"
                        )
    
    def enable_tracking(self, enabled: bool = True) -> None:
        """Enable or disable memory tracking.
        
        Args:
            enabled: Whether tracking should be enabled
        """
        with self._lock:
            self._tracking_enabled = enabled


# Global memory tracker
_MEMORY_TRACKER = None
_TRACKER_LOCK = threading.RLock()


def get_memory_tracker() -> MemoryTracker:
    """Get the global memory tracker.
    
    Returns:
        The global MemoryTracker instance
    """
    global _MEMORY_TRACKER
    
    with _TRACKER_LOCK:
        if _MEMORY_TRACKER is None:
            _MEMORY_TRACKER = MemoryTracker()
        
        return _MEMORY_TRACKER
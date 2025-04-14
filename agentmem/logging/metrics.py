"""
Metrics collection for AgentMem.

This module provides functionality for collecting and analyzing
performance metrics and memory usage statistics.
"""
import enum
import threading
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, DefaultDict, Set, Deque
import logging
import os
import psutil

from agentmem.logging.logger import get_logger

# Global metrics collector
_METRICS_COLLECTOR = None
_METRICS_LOCK = threading.RLock()


class OperationType(enum.Enum):
    """Types of memory operations."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"
    VECTOR_QUERY = "vector_query"
    SAVE = "save"
    LOAD = "load"
    CLEAR = "clear"


class MetricsCollector:
    """Collects performance metrics for memory operations."""
    
    def __init__(self, max_history: int = 1000, enable_system_metrics: bool = True):
        """Initialize the metrics collector.
        
        Args:
            max_history: Maximum number of operation records to keep
            enable_system_metrics: Whether to collect system metrics
        """
        self.logger = get_logger("agentmem.metrics")
        self._lock = threading.RLock()
        self._max_history = max_history
        self._enable_system_metrics = enable_system_metrics
        
        # Operation metrics
        self._operation_times: DefaultDict[str, List[float]] = defaultdict(list)
        self._operation_counts: DefaultDict[str, int] = defaultdict(int)
        self._history: Deque[Tuple[datetime, str, str, float]] = deque(maxlen=max_history)
        
        # Memory type metrics
        self._memory_type_counts: DefaultDict[str, int] = defaultdict(int)
        self._memory_type_sizes: DefaultDict[str, int] = defaultdict(int)
        
        # System metrics - collected only if enabled
        self._sys_metrics_history: List[Dict[str, Any]] = []
        self._sys_metrics_interval_sec = 60  # Collect every minute
        self._last_sys_metrics_time = 0
        
        # Start system metrics collection if enabled
        if enable_system_metrics:
            self._maybe_collect_system_metrics()
    
    def record_operation(
        self,
        operation: OperationType,
        memory_type: str,
        duration_sec: float,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a memory operation.
        
        Args:
            operation: Type of operation performed
            memory_type: Type of memory operated on
            duration_sec: Duration of the operation in seconds
            details: Additional details about the operation
        """
        with self._lock:
            op_key = f"{memory_type}.{operation.value}"
            
            # Update statistics
            self._operation_times[op_key].append(duration_sec)
            # Keep only the most recent entries
            if len(self._operation_times[op_key]) > self._max_history:
                self._operation_times[op_key] = self._operation_times[op_key][-self._max_history:]
            
            self._operation_counts[op_key] += 1
            self._memory_type_counts[memory_type] += 1
            
            # Record in history
            timestamp = datetime.now()
            self._history.append((timestamp, memory_type, operation.value, duration_sec))
            
            # Maybe update system metrics
            if self._enable_system_metrics:
                self._maybe_collect_system_metrics()
            
            # Log the operation
            if details:
                self.logger.debug(
                    f"Operation: {operation.value} on {memory_type}, "
                    f"duration: {duration_sec:.4f}s, details: {details}"
                )
            else:
                self.logger.debug(
                    f"Operation: {operation.value} on {memory_type}, "
                    f"duration: {duration_sec:.4f}s"
                )
    
    def update_memory_size(self, memory_type: str, size_bytes: int) -> None:
        """Update the size of a memory type.
        
        Args:
            memory_type: Type of memory
            size_bytes: Size in bytes
        """
        with self._lock:
            self._memory_type_sizes[memory_type] = size_bytes
    
    def _maybe_collect_system_metrics(self) -> None:
        """Collect system metrics if enough time has passed."""
        current_time = time.time()
        if current_time - self._last_sys_metrics_time >= self._sys_metrics_interval_sec:
            try:
                # Collect process info
                process = psutil.Process(os.getpid())
                memory_info = process.memory_info()
                
                metrics = {
                    "timestamp": datetime.now(),
                    "cpu_percent": process.cpu_percent(),
                    "memory_rss": memory_info.rss,  # Resident Set Size
                    "memory_vms": memory_info.vms,  # Virtual Memory Size
                    "threads": process.num_threads(),
                    "open_files": len(process.open_files()),
                    "connections": len(process.connections()),
                }
                
                self._sys_metrics_history.append(metrics)
                # Keep only recent history
                if len(self._sys_metrics_history) > self._max_history:
                    self._sys_metrics_history = self._sys_metrics_history[-self._max_history:]
                
                self._last_sys_metrics_time = current_time
                
                self.logger.debug(
                    f"System metrics: CPU: {metrics['cpu_percent']}%, "
                    f"Memory RSS: {metrics['memory_rss'] / (1024*1024):.2f} MB"
                )
            except Exception as e:
                self.logger.warning(f"Failed to collect system metrics: {str(e)}")
    
    def get_operation_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations.
        
        Returns:
            Dictionary of operation statistics by operation key
        """
        with self._lock:
            stats = {}
            
            for op_key, times in self._operation_times.items():
                if not times:
                    continue
                
                parts = op_key.split('.', 1)
                if len(parts) != 2:
                    continue
                
                memory_type, operation = parts
                
                stats[op_key] = {
                    "memory_type": memory_type,
                    "operation": operation,
                    "count": self._operation_counts[op_key],
                    "avg_duration": sum(times) / len(times) if times else 0,
                    "min_duration": min(times) if times else 0,
                    "max_duration": max(times) if times else 0,
                    "total_duration": sum(times),
                }
            
            return stats
    
    def get_memory_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all memory types.
        
        Returns:
            Dictionary of memory type statistics
        """
        with self._lock:
            stats = {}
            
            for memory_type in set(self._memory_type_counts.keys()) | set(self._memory_type_sizes.keys()):
                stats[memory_type] = {
                    "operation_count": self._memory_type_counts[memory_type],
                    "size_bytes": self._memory_type_sizes[memory_type],
                }
            
            return stats
    
    def get_system_metrics(self) -> List[Dict[str, Any]]:
        """Get system metrics history.
        
        Returns:
            List of system metric snapshots
        """
        with self._lock:
            return list(self._sys_metrics_history)
    
    def get_operation_history(self) -> List[Tuple[datetime, str, str, float]]:
        """Get the operation history.
        
        Returns:
            List of (timestamp, memory_type, operation, duration) tuples
        """
        with self._lock:
            return list(self._history)
    
    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._operation_times.clear()
            self._operation_counts.clear()
            self._history.clear()
            self._memory_type_counts.clear()
            self._memory_type_sizes.clear()
            self._sys_metrics_history.clear()
            self._last_sys_metrics_time = 0


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector.
    
    Returns:
        The global MetricsCollector instance
    """
    global _METRICS_COLLECTOR
    
    with _METRICS_LOCK:
        if _METRICS_COLLECTOR is None:
            _METRICS_COLLECTOR = MetricsCollector()
        
        return _METRICS_COLLECTOR
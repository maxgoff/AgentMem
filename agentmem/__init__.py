"""
AgentMem: A Python package for managing agent memory systems.
"""
import warnings
import os

# Temporarily suppress all warnings during import
original_filters = warnings.filters.copy()
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

try:
    from agentmem.base import Memory, VECTOR_SEARCH_AVAILABLE
    from agentmem.semantic import SemanticMemory
    from agentmem.episodic import EpisodicMemory
    from agentmem.procedural import ProceduralMemory
    from agentmem.storage import FileStorage
    from agentmem.concurrency import lock_manager
    
    # Import VectorStorage only if available
    if VECTOR_SEARCH_AVAILABLE:
        from agentmem.storage.vector_storage import VectorStorage
    
    # Import logging components
    from agentmem.logging import (
        get_logger,
        configure_logging,
        LogLevel,
        set_logging_enabled,
        get_metrics_collector,
        get_memory_tracker,
        OperationType
    )

finally:
    # Restore original warning filters after imports complete
    warnings.filters = original_filters
    if 'PYTHONWARNINGS' in os.environ:
        del os.environ['PYTHONWARNINGS']

__version__ = "0.1.0"
"""
Storage backends for AgentMem.
"""

import warnings
import os

# Temporarily suppress all warnings when importing storage backends
original_filters = warnings.filters.copy()
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

try:
    from agentmem.storage.file_storage import FileStorage
    
    # Conditionally import VectorStorage
    # Don't export it directly from __init__.py to avoid import errors
    # Base.py will import it directly when needed
    try:
        import agentmem.storage.vector_storage
        # We don't export it here to avoid import errors
    except (ImportError, TypeError, ValueError) as e:
        # Silently ignore vector_storage import errors
        pass
        
finally:
    # Restore original warning filters after imports complete
    warnings.filters = original_filters
    if 'PYTHONWARNINGS' in os.environ:
        del os.environ['PYTHONWARNINGS']
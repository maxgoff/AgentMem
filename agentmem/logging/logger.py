"""
Logging system for AgentMem.

This module provides a configurable logging system that works
across different Python environments and integrates with the
standard Python logging module.
"""
import datetime
import enum
import logging
import os
import sys
import threading
from typing import Dict, Optional, Union, List, Any

# Global state
_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_DEFAULT_LOG_LEVEL = logging.INFO
_LOGGERS: Dict[str, logging.Logger] = {}
_LOGGING_CONFIGURED = False
_LOGGING_ENABLED = True
_LOCK = threading.RLock()


class LogLevel(enum.Enum):
    """Log levels for AgentMem logging."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


def logging_enabled() -> bool:
    """Check if logging is enabled.
    
    Returns:
        bool: True if logging is enabled, False otherwise
    """
    return _LOGGING_ENABLED


def set_logging_enabled(enabled: bool) -> None:
    """Enable or disable logging.
    
    Args:
        enabled: Whether to enable logging
    """
    global _LOGGING_ENABLED
    with _LOCK:
        _LOGGING_ENABLED = enabled


def configure_logging(
    log_level: Union[LogLevel, str, int] = LogLevel.INFO,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
    console_output: bool = True,
    capture_warnings: bool = True,
) -> None:
    """Configure the AgentMem logging system.
    
    Args:
        log_level: Minimum log level to record
        log_format: Format string for log messages
        log_file: Path to log file (None for no file logging)
        console_output: Whether to output logs to console
        capture_warnings: Whether to capture Python warnings in logs
    """
    global _LOGGING_CONFIGURED, _LOG_FORMAT
    
    # Convert log level to int if needed
    if isinstance(log_level, LogLevel):
        level = log_level.value
    elif isinstance(log_level, str):
        level = getattr(logging, log_level.upper(), _DEFAULT_LOG_LEVEL)
    else:
        level = log_level
    
    with _LOCK:
        # Use provided format or default
        if log_format:
            _LOG_FORMAT = log_format
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Remove existing handlers
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
        
        # Create formatter
        formatter = logging.Formatter(_LOG_FORMAT)
        
        # Add console handler if requested
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # Add file handler if log file specified
        if log_file:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Capture warnings if requested
        if capture_warnings:
            logging.captureWarnings(True)
        
        _LOGGING_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the specified name.
    
    Args:
        name: Name of the logger
        
    Returns:
        A Logger instance
    """
    global _LOGGERS
    
    # Configure logging with defaults if not already configured
    if not _LOGGING_CONFIGURED:
        configure_logging()
    
    with _LOCK:
        # Return cached logger if it exists
        if name in _LOGGERS:
            return _LOGGERS[name]
        
        # Create new logger
        logger = logging.getLogger(name)
        _LOGGERS[name] = logger
        return logger


class LoggingContext:
    """Context manager for temporarily changing log level."""
    
    def __init__(self, logger: logging.Logger, level: Union[LogLevel, int, str]):
        """Initialize the context manager.
        
        Args:
            logger: The logger to modify
            level: The temporary log level
        """
        self.logger = logger
        
        # Convert level to int if needed
        if isinstance(level, LogLevel):
            self.level = level.value
        elif isinstance(level, str):
            self.level = getattr(logging, level.upper(), _DEFAULT_LOG_LEVEL)
        else:
            self.level = level
            
        self.previous_level = logger.level
    
    def __enter__(self):
        """Set temporary log level."""
        self.logger.setLevel(self.level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original log level."""
        self.logger.setLevel(self.previous_level)
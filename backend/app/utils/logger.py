"""
Logging Utility
================
Centralized logging configuration for CyberGuardX.
Replaces scattered print() statements with proper structured logging.

Usage:
    from app.utils.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Processing request")
    logger.error("Failed to connect", exc_info=True)
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger with consistent formatting.
    
    Args:
        name: Logger name (typically __name__)
        level: Optional log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        # Console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Format: [2026-02-10 14:30:45] [INFO] [app.routes.email] Email check requested
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Set level
        if level:
            logger.setLevel(getattr(logging, level.upper()))
        else:
            logger.setLevel(logging.INFO)
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger


def setup_file_logging(log_dir: Path, log_level: str = "INFO") -> None:
    """
    Configure file-based logging for production environments.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create file handler
    log_file = log_dir / "cyberguardx.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Detailed format for file logs
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)-8s] [%(name)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))


# Convenience functions for common logging patterns
def log_request(logger: logging.Logger, endpoint: str, details: str = "") -> None:
    """Log an incoming API request."""
    logger.info(f"Request to {endpoint}" + (f" — {details}" if details else ""))


def log_error(logger: logging.Logger, operation: str, error: Exception) -> None:
    """Log an error with exception details."""
    logger.error(f"Error in {operation}: {str(error)}", exc_info=True)


def log_security_event(logger: logging.Logger, event: str, details: dict) -> None:
    """Log a security-related event."""
    logger.warning(f"Security event: {event} — {details}")

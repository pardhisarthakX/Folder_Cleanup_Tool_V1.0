"""
logger.py
Structured logging setup for the Folder Cleanup Tool.

Provides a consistent logging interface with timestamps, levels,
and optional rotating file handler. Replaces the ad-hoc print()
statements used throughout the original codebase.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

# Default log directory relative to the project root
DEFAULT_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
DEFAULT_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "folder_cleanup.log")

# Log format: timestamp, level, module, message
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = DEFAULT_LOG_FILE,
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 5,
    console: bool = True,
) -> logging.Logger:
    """
    Configure the root logger with console and rotating file handlers.

    Args:
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR).
        log_file: Path to the log file. If None, no file handler is added.
        max_bytes: Max size of a single log file before rotation.
        backup_count: Number of rotated log files to keep.
        console: Whether to also log to stdout.

    Returns:
        The configured root logger.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove any existing handlers to avoid duplicates on re-config
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger for the given name."""
    return logging.getLogger(name)

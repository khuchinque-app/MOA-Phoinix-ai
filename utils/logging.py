"""
logging.py — Structured logging for MoA Swarm

Provides consistent, structured logging across all components.
Supports JSON and text log formats.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import logging
import json
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from core.config import get_config, MoASwarmConfig


# ─── Custom Formatter ─────────────────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data
        
        return json.dumps(log_entry, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Text log formatter for human-readable output."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as text."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        level = record.levelname.ljust(8)
        logger = record.name
        message = record.getMessage()
        
        log_line = f"{timestamp} | {level} | {logger} | {message}"
        
        # Add exception info if present
        if record.exc_info and record.exc_info[0]:
            log_line += f"\n{self.formatException(record.exc_info)}"
        
        return log_line


# ─── Logger Setup ─────────────────────────────────────────────────────────────

class SwarmLogger:
    """
    Centralized logger for the MoA swarm.
    
    Provides:
    - Consistent logging across all components
    - JSON and text format support
    - File and console output
    - Component-specific loggers
    """
    
    def __init__(self, config: Optional[MoASwarmConfig] = None):
        """
        Initialize the Swarm Logger.
        
        Args:
            config: MoASwarmConfig instance (uses default if not provided)
        """
        self.config = config or get_config()
        self._loggers: Dict[str, logging.Logger] = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self) -> None:
        """Setup the root logger with configured handlers."""
        root_logger = logging.getLogger("moa_swarm")
        
        # Set log level
        log_level = getattr(logging, self.config.logging.log_level.upper(), logging.INFO)
        root_logger.setLevel(log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter based on config
        if self.config.logging.log_format == "json":
            formatter = JSONFormatter()
        else:
            formatter = TextFormatter()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (if log file is configured)
        if self.config.logging.log_file:
            log_path = Path(self.config.logging.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        self._loggers["root"] = root_logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger for a specific component.
        
        Args:
            name: Logger name (e.g., "router", "browser", "vision")
        
        Returns:
            Logger instance
        """
        if name not in self._loggers:
            # Create child logger under moa_swarm
            logger = logging.getLogger(f"moa_swarm.{name}")
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    # ─── Convenience Methods ──────────────────────────────────────────────────
    
    def debug(self, message: str, component: str = "root", **kwargs) -> None:
        """Log a debug message."""
        logger = self.get_logger(component)
        logger.debug(message, extra={"extra_data": kwargs} if kwargs else None)
    
    def info(self, message: str, component: str = "root", **kwargs) -> None:
        """Log an info message."""
        logger = self.get_logger(component)
        logger.info(message, extra={"extra_data": kwargs} if kwargs else None)
    
    def warning(self, message: str, component: str = "root", **kwargs) -> None:
        """Log a warning message."""
        logger = self.get_logger(component)
        logger.warning(message, extra={"extra_data": kwargs} if kwargs else None)
    
    def error(self, message: str, component: str = "root", **kwargs) -> None:
        """Log an error message."""
        logger = self.get_logger(component)
        logger.error(message, extra={"extra_data": kwargs} if kwargs else None)
    
    def critical(self, message: str, component: str = "root", **kwargs) -> None:
        """Log a critical message."""
        logger = self.get_logger(component)
        logger.critical(message, extra={"extra_data": kwargs} if kwargs else None)
    
    def exception(self, message: str, component: str = "root", **kwargs) -> None:
        """Log an exception with traceback."""
        logger = self.get_logger(component)
        logger.exception(message, extra={"extra_data": kwargs} if kwargs else None)


# ─── Singleton Logger ─────────────────────────────────────────────────────────

_logger_instance: Optional[SwarmLogger] = None


def get_logger() -> SwarmLogger:
    """
    Get the singleton logger instance.
    
    Returns:
        SwarmLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SwarmLogger()
    return _logger_instance


def setup_logging(config: Optional[MoASwarmConfig] = None) -> SwarmLogger:
    """
    Setup logging with the given configuration.
    
    Args:
        config: MoASwarmConfig instance
    
    Returns:
        SwarmLogger instance
    """
    global _logger_instance
    _logger_instance = SwarmLogger(config)
    return _logger_instance


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Setup logging
    logger = setup_logging()
    
    # Log some messages
    logger.info("MoA Swarm starting up", component="main")
    logger.debug("Loading configuration", component="config")
    logger.warning("API key not set", component="api", key="OPENAI_API_KEY")
    
    # Log with exception
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception("An error occurred", component="test")
    
    # Get component-specific logger
    router_logger = logger.get_logger("router")
    router_logger.info("Router initialized")
    
    print("\nLogging setup complete!")
    print(f"Log level: {logger.config.logging.log_level}")
    print(f"Log format: {logger.config.logging.log_format}")
    print(f"Log file: {logger.config.logging.log_file}")

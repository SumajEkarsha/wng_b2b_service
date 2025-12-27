"""
Comprehensive Logging Configuration for WellNest B2B Service

This module provides:
- Structured JSON logging for production
- Human-readable console logging for development
- Request/Response logging middleware
- Contextual logging with request IDs
- Performance logging utilities
"""

import logging
import sys
import json
from datetime import datetime
from typing import Optional, Any
from pathlib import Path
import uuid
from contextvars import ContextVar

from app.core.config import settings

# Context variable for request ID (thread-safe)
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging in production.
    Outputs logs in JSON format for easy parsing by log aggregators
    (e.g., ELK Stack, Datadog, CloudWatch).
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if provided
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data
            
        return json.dumps(log_data, default=str)


class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for development.
    Makes it easy to visually identify log levels.
    """
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    def format(self, record: logging.LogRecord) -> str:
        # Get color for log level
        color = self.COLORS.get(record.levelname, "")
        
        # Add request ID if available
        request_id = request_id_var.get()
        request_id_str = f"[{request_id[:8]}] " if request_id else ""
        
        # Format the base message
        level_str = f"{color}{self.BOLD}[{record.levelname:8}]{self.RESET}"
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        formatted = f"{time_str} {level_str} {request_id_str}{record.name}: {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
            
        return formatted


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the application configuration.
    
    Usage:
        from app.core.logging_config import get_logger
        logger = get_logger(__name__)
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # With extra context
        logger.info("User logged in", extra={"extra_data": {"user_id": "123"}})
    """
    return logging.getLogger(name)


def setup_logging() -> None:
    """
    Configure the root logger and application loggers.
    Call this once at application startup.
    """
    # Determine log level from environment
    log_level_name = getattr(settings, "LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Use JSON formatter for production, colored for development
    is_production = getattr(settings, "ENVIRONMENT", "development") == "production"
    
    if is_production:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())
    
    root_logger.addHandler(console_handler)
    
    # Optional: File handler for production
    if is_production:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
    
    # Configure third-party loggers to be less verbose
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Log startup message
    app_logger = get_logger("app")
    app_logger.info(
        f"Logging configured - Level: {log_level_name}, "
        f"Environment: {getattr(settings, 'ENVIRONMENT', 'development')}"
    )


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that automatically includes context data.
    Useful for adding request-specific information.
    """
    
    def process(self, msg: str, kwargs: dict) -> tuple:
        # Add extra context from adapter
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


def get_request_logger(
    name: str, 
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    school_id: Optional[str] = None
) -> LoggerAdapter:
    """
    Get a logger adapter with request context.
    
    Usage:
        logger = get_request_logger(
            __name__, 
            request_id="abc-123",
            user_id="user-456"
        )
        logger.info("Processing request")  # Will include request context
    """
    logger = get_logger(name)
    context = {}
    
    if request_id:
        context["request_id"] = request_id
    if user_id:
        context["user_id"] = user_id
    if school_id:
        context["school_id"] = school_id
        
    return LoggerAdapter(logger, {"extra_data": context})


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function entry and exit with timing.
    
    Usage:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            pass
    """
    import functools
    import time
    
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            logger.debug(f"Entering {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                elapsed = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Exiting {func.__name__} - took {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - start_time) * 1000
                logger.error(
                    f"Error in {func.__name__} after {elapsed:.2f}ms: {str(e)}",
                    exc_info=True
                )
                raise
                
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            logger.debug(f"Entering {func.__name__}")
            try:
                result = func(*args, **kwargs)
                elapsed = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Exiting {func.__name__} - took {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - start_time) * 1000
                logger.error(
                    f"Error in {func.__name__} after {elapsed:.2f}ms: {str(e)}",
                    exc_info=True
                )
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context."""
    request_id_var.set(request_id)


def get_request_id() -> str:
    """Get the current request ID."""
    return request_id_var.get()

"""
Logging configuration for the Flyde documentation scraper.
"""
import logging
import sys
from pathlib import Path
from typing import Dict, Any

import structlog
from structlog.stdlib import LoggerFactory

from .settings import settings


def configure_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO if not settings.debug else logging.DEBUG
    )
    
    # Create file handler for persistent logs
    log_file = Path(settings.logs_dir) / "flyde_scraper.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Add file handler to root logger
    logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Logging levels for different components
LOGGING_LEVELS: Dict[str, str] = {
    "scrapers": "INFO",
    "mcp_servers": "DEBUG",
    "web_ui": "INFO",
    "data_processor": "INFO",
    "monitoring": "INFO"
}


def configure_component_logging(component: str) -> None:
    """Configure logging for a specific component."""
    level = LOGGING_LEVELS.get(component, "INFO")
    logging.getLogger(component).setLevel(getattr(logging, level.upper()))


# Initialize logging on import
configure_logging()
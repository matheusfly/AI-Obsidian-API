#!/usr/bin/env python3
"""
Logging Configuration for Data Vault Obsidian
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any

class LoggingConfig:
    """Centralized logging configuration"""
    
    def __init__(self):
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "json")
        self.log_file = os.getenv("LOG_FILE", "logs/data_vault_obsidian.log")
        self.max_log_size = int(os.getenv("MAX_LOG_SIZE", "10485760"))  # 10MB
        self.backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))
        self.enable_console = os.getenv("ENABLE_CONSOLE_LOGGING", "true").lower() == "true"
        self.enable_file = os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true"
        self.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.metrics_interval = int(os.getenv("METRICS_INTERVAL", "60"))  # seconds
        
    def get_logging_config(self) -> Dict[str, Any]:
        """Get complete logging configuration"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "json": {
                    "()": "structlog.stdlib.ProcessorFormatter",
                    "processor": "structlog.dev.ConsoleRenderer"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.log_level,
                    "formatter": "standard" if self.log_format == "standard" else "json",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.log_level,
                    "formatter": "standard" if self.log_format == "standard" else "json",
                    "filename": self.log_file,
                    "maxBytes": self.max_log_size,
                    "backupCount": self.backup_count
                }
            },
            "loggers": {
                "data_vault_obsidian": {
                    "level": self.log_level,
                    "handlers": self._get_handlers(),
                    "propagate": False
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": self._get_handlers(),
                    "propagate": False
                },
                "fastapi": {
                    "level": "INFO", 
                    "handlers": self._get_handlers(),
                    "propagate": False
                }
            },
            "root": {
                "level": "WARNING",
                "handlers": self._get_handlers()
            }
        }
    
    def _get_handlers(self) -> list:
        """Get list of handlers based on configuration"""
        handlers = []
        if self.enable_console:
            handlers.append("console")
        if self.enable_file:
            handlers.append("file")
        return handlers
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        config = self.get_logging_config()
        logging.config.dictConfig(config)
        
        return config

# Global configuration instance
config = LoggingConfig()

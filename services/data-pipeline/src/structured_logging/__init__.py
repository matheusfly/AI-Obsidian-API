"""
Structured Logging Module for Data Vault Obsidian
"""

from .structured_logger import (
    StructuredLogger,
    logger,
    log_query_start,
    log_search_start,
    log_search_completed,
    log_gemini_start,
    log_gemini_completed,
    log_query_completed,
    log_error,
    get_analytics
)

__all__ = [
    "StructuredLogger",
    "logger",
    "log_query_start",
    "log_search_start", 
    "log_search_completed",
    "log_gemini_start",
    "log_gemini_completed",
    "log_query_completed",
    "log_error",
    "get_analytics"
]

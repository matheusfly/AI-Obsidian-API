"""
Admin Dashboard Module for Data Vault Obsidian
"""

from .api import app, get_system_health, get_analytics, get_recent_queries
from .models import SystemHealth, AnalyticsSummary, QueryMetrics, SystemMetrics

__all__ = [
    "app",
    "get_system_health", 
    "get_analytics",
    "get_recent_queries",
    "SystemHealth",
    "AnalyticsSummary", 
    "QueryMetrics",
    "SystemMetrics"
]

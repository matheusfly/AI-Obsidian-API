#!/usr/bin/env python3
"""
Pydantic Models for Admin Dashboard API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class SystemMetrics(BaseModel):
    """System metrics model"""
    timestamp: datetime
    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    memory_used_gb: float = Field(..., description="Memory used in GB")
    memory_available_gb: float = Field(..., description="Memory available in GB")
    disk_usage_percent: float = Field(..., description="Disk usage percentage")
    disk_free_gb: float = Field(..., description="Disk free space in GB")
    network_sent_mb: float = Field(..., description="Network sent in MB/s")
    network_recv_mb: float = Field(..., description="Network received in MB/s")
    process_count: int = Field(..., description="Number of running processes")
    load_average: List[float] = Field(..., description="System load average")

class QueryMetrics(BaseModel):
    """Query performance metrics model"""
    timestamp: datetime
    query: str = Field(..., description="Search query")
    search_time_ms: float = Field(..., description="Search time in milliseconds")
    gemini_time_ms: float = Field(..., description="Gemini processing time in milliseconds")
    total_time_ms: float = Field(..., description="Total query time in milliseconds")
    results_count: int = Field(..., description="Number of results returned")
    success: bool = Field(..., description="Whether query was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")

class SystemHealth(BaseModel):
    """System health status model"""
    status: str = Field(..., description="Overall system status")
    uptime_seconds: float = Field(..., description="System uptime in seconds")
    current_metrics: SystemMetrics = Field(..., description="Current system metrics")
    health_score: float = Field(..., description="Overall health score (0-100)")
    alerts: List[str] = Field(default_factory=list, description="Active alerts")
    last_updated: datetime = Field(..., description="Last update timestamp")

class AnalyticsSummary(BaseModel):
    """Analytics summary model"""
    uptime_seconds: float = Field(..., description="System uptime in seconds")
    total_queries: int = Field(..., description="Total queries processed")
    recent_queries_count: int = Field(..., description="Queries in last hour")
    success_rate: float = Field(..., description="Query success rate percentage")
    avg_search_time_ms: float = Field(..., description="Average search time in milliseconds")
    avg_gemini_time_ms: float = Field(..., description="Average Gemini time in milliseconds")
    avg_total_time_ms: float = Field(..., description="Average total time in milliseconds")
    system_metrics: Dict[str, Any] = Field(..., description="System metrics summary")
    query_trends: Dict[str, Any] = Field(..., description="Query trend analysis")

class QueryTrends(BaseModel):
    """Query trends analysis model"""
    queries_per_minute: float = Field(..., description="Queries per minute rate")
    avg_results_per_query: float = Field(..., description="Average results per query")
    error_rate: float = Field(..., description="Error rate percentage")
    peak_query_time: Optional[datetime] = Field(None, description="Peak query time")
    most_common_queries: List[str] = Field(default_factory=list, description="Most common queries")

class HealthAlert(BaseModel):
    """Health alert model"""
    level: str = Field(..., description="Alert level (info, warning, error, critical)")
    message: str = Field(..., description="Alert message")
    timestamp: datetime = Field(..., description="Alert timestamp")
    component: str = Field(..., description="Affected component")
    resolved: bool = Field(default=False, description="Whether alert is resolved")

class DashboardData(BaseModel):
    """Complete dashboard data model"""
    system_health: SystemHealth = Field(..., description="System health status")
    analytics: AnalyticsSummary = Field(..., description="Analytics summary")
    recent_queries: List[QueryMetrics] = Field(..., description="Recent query metrics")
    system_metrics_history: List[SystemMetrics] = Field(..., description="System metrics history")
    alerts: List[HealthAlert] = Field(default_factory=list, description="Active alerts")
    last_updated: datetime = Field(..., description="Last update timestamp")

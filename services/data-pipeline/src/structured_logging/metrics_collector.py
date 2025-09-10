#!/usr/bin/env python3
"""
Metrics Collection System for Data Vault Obsidian
Real-time system and application metrics collection
"""

import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import deque
import json
import threading
from pathlib import Path

@dataclass
class SystemMetrics:
    """System metrics data structure"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_available_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    load_average: List[float]

@dataclass
class QueryMetrics:
    """Query performance metrics data structure"""
    timestamp: datetime
    query: str
    search_time_ms: float
    gemini_time_ms: float
    total_time_ms: float
    results_count: int
    success: bool
    error_message: Optional[str] = None

class MetricsCollector:
    """Real-time metrics collection and storage"""
    
    def __init__(self, max_history: int = 1000, collection_interval: int = 60):
        self.max_history = max_history
        self.collection_interval = collection_interval
        self.system_metrics_history = deque(maxlen=max_history)
        self.query_metrics_history = deque(maxlen=max_history)
        self.is_collecting = False
        self.collection_task = None
        self.start_time = time.time()
        
        # Network metrics tracking
        self.last_network_sent = 0
        self.last_network_recv = 0
        self.last_network_time = time.time()
        
    def get_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network metrics (delta calculation)
            network = psutil.net_io_counters()
            current_time = time.time()
            
            if self.last_network_time > 0:
                time_delta = current_time - self.last_network_time
                network_sent_mb = (network.bytes_sent - self.last_network_sent) / (1024 * 1024) / time_delta
                network_recv_mb = (network.bytes_recv - self.last_network_recv) / (1024 * 1024) / time_delta
            else:
                network_sent_mb = 0
                network_recv_mb = 0
            
            # Update network tracking
            self.last_network_sent = network.bytes_sent
            self.last_network_recv = network.bytes_recv
            self.last_network_time = current_time
            
            # Process count and load average
            process_count = len(psutil.pids())
            try:
                load_avg = list(psutil.getloadavg())
            except (OSError, AttributeError):
                load_avg = [0.0, 0.0, 0.0]
            
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_gb=memory.used / (1024**3),
                memory_available_gb=memory.available / (1024**3),
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / (1024**3),
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                process_count=process_count,
                load_average=load_avg
            )
        except Exception as e:
            # Return default metrics on error
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_gb=0.0,
                memory_available_gb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                process_count=0,
                load_average=[0.0, 0.0, 0.0]
            )
    
    def add_query_metrics(self, query: str, search_time_ms: float, gemini_time_ms: float, 
                         total_time_ms: float, results_count: int, success: bool, 
                         error_message: Optional[str] = None):
        """Add query performance metrics"""
        metrics = QueryMetrics(
            timestamp=datetime.utcnow(),
            query=query,
            search_time_ms=search_time_ms,
            gemini_time_ms=gemini_time_ms,
            total_time_ms=total_time_ms,
            results_count=results_count,
            success=success,
            error_message=error_message
        )
        self.query_metrics_history.append(metrics)
    
    def start_collection(self):
        """Start background metrics collection"""
        if not self.is_collecting:
            self.is_collecting = True
            self.collection_task = asyncio.create_task(self._collect_metrics_loop())
    
    def stop_collection(self):
        """Stop background metrics collection"""
        self.is_collecting = False
        if self.collection_task:
            self.collection_task.cancel()
    
    async def _collect_metrics_loop(self):
        """Background metrics collection loop"""
        while self.is_collecting:
            try:
                metrics = self.get_system_metrics()
                self.system_metrics_history.append(metrics)
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                print(f"Error collecting metrics: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def get_recent_system_metrics(self, minutes: int = 5) -> List[SystemMetrics]:
        """Get recent system metrics within specified minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [m for m in self.system_metrics_history if m.timestamp >= cutoff_time]
    
    def get_recent_query_metrics(self, minutes: int = 5) -> List[QueryMetrics]:
        """Get recent query metrics within specified minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [m for m in self.query_metrics_history if m.timestamp >= cutoff_time]
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        recent_queries = self.get_recent_query_metrics(60)  # Last hour
        recent_system = self.get_recent_system_metrics(60)  # Last hour
        
        if not recent_queries:
            current_metrics = self.get_system_metrics()
            return {
                "uptime_seconds": time.time() - self.start_time,
                "total_queries": len(self.query_metrics_history),
                "success_rate": 0.0,
                "avg_search_time_ms": 0.0,
                "avg_gemini_time_ms": 0.0,
                "avg_total_time_ms": 0.0,
                "system_metrics": {
                    "avg_cpu_percent": current_metrics.cpu_percent,
                    "avg_memory_percent": current_metrics.memory_percent,
                    "avg_disk_usage_percent": current_metrics.disk_usage_percent,
                    "current": {
                        k: v.isoformat() if hasattr(v, 'isoformat') else v 
                        for k, v in current_metrics.__dict__.items()
                    }
                },
                "query_trends": {
                    "queries_per_minute": 0,
                    "avg_results_per_query": 0,
                    "error_rate": 0
                },
                "recent_queries_count": 0
            }
        
        successful_queries = [q for q in recent_queries if q.success]
        success_rate = len(successful_queries) / len(recent_queries) * 100
        
        avg_search_time = sum(q.search_time_ms for q in recent_queries) / len(recent_queries)
        avg_gemini_time = sum(q.gemini_time_ms for q in recent_queries) / len(recent_queries)
        avg_total_time = sum(q.total_time_ms for q in recent_queries) / len(recent_queries)
        
        # System metrics averages
        if recent_system:
            avg_cpu = sum(m.cpu_percent for m in recent_system) / len(recent_system)
            avg_memory = sum(m.memory_percent for m in recent_system) / len(recent_system)
            avg_disk = sum(m.disk_usage_percent for m in recent_system) / len(recent_system)
        else:
            current_metrics = self.get_system_metrics()
            avg_cpu = current_metrics.cpu_percent
            avg_memory = current_metrics.memory_percent
            avg_disk = current_metrics.disk_usage_percent
        
        return {
            "uptime_seconds": time.time() - self.start_time,
            "total_queries": len(self.query_metrics_history),
            "recent_queries_count": len(recent_queries),
            "success_rate": success_rate,
            "avg_search_time_ms": avg_search_time,
            "avg_gemini_time_ms": avg_gemini_time,
            "avg_total_time_ms": avg_total_time,
            "system_metrics": {
                "avg_cpu_percent": avg_cpu,
                "avg_memory_percent": avg_memory,
                "avg_disk_usage_percent": avg_disk,
                "current": {
                    k: v.isoformat() if hasattr(v, 'isoformat') else v 
                    for k, v in self.get_system_metrics().__dict__.items()
                }
            },
            "query_trends": {
                "queries_per_minute": len(recent_queries) / 60 if recent_queries else 0,
                "avg_results_per_query": sum(q.results_count for q in recent_queries) / len(recent_queries) if recent_queries else 0,
                "error_rate": (len(recent_queries) - len(successful_queries)) / len(recent_queries) * 100 if recent_queries else 0
            }
        }
    
    def export_metrics(self, output_file: str = "logs/metrics_export.json") -> str:
        """Export all metrics to JSON file"""
        try:
            data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "system_metrics": [m.__dict__ for m in self.system_metrics_history],
                "query_metrics": [m.__dict__ for m in self.query_metrics_history],
                "analytics_summary": self.get_analytics_summary()
            }
            
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            return output_file
        except Exception as e:
            print(f"Error exporting metrics: {e}")
            return None

# Global metrics collector instance
metrics_collector = MetricsCollector()

#!/usr/bin/env python3
"""
Standard Prometheus Metrics for Data Pipeline Service
Includes HTTP request metrics and process metrics
"""

import time
import psutil
import logging
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class StandardMetrics:
    """Standard Prometheus metrics for HTTP requests and process monitoring"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        
        # HTTP Request Metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        # Process Metrics
        self.process_cpu_seconds_total = Counter(
            'process_cpu_seconds_total',
            'Total CPU time consumed by the process',
            registry=self.registry
        )
        
        self.process_resident_memory_bytes = Gauge(
            'process_resident_memory_bytes',
            'Resident memory size in bytes',
            registry=self.registry
        )
        
        # Custom Metrics for Data Pipeline
        self.files_processed_total = Counter(
            'files_processed_total',
            'Total number of files processed',
            ['status'],
            registry=self.registry
        )
        
        self.search_queries_total = Counter(
            'search_queries_total',
            'Total number of search queries',
            ['query_type', 'status'],
            registry=self.registry
        )
        
        # Start process monitoring
        self._start_process_monitoring()
    
    def _start_process_monitoring(self):
        """Start monitoring process metrics"""
        try:
            import threading
            def update_process_metrics():
                while True:
                    try:
                        process = psutil.Process()
                        # Update CPU time
                        cpu_times = process.cpu_times()
                        total_cpu_time = cpu_times.user + cpu_times.system
                        self.process_cpu_seconds_total._value._value = total_cpu_time
                        
                        # Update memory usage
                        memory_info = process.memory_info()
                        self.process_resident_memory_bytes.set(memory_info.rss)
                        
                        time.sleep(5)  # Update every 5 seconds
                    except Exception as e:
                        logger.error(f"Error updating process metrics: {e}")
                        time.sleep(10)
            
            thread = threading.Thread(target=update_process_metrics, daemon=True)
            thread.start()
            logger.info("Process metrics monitoring started")
        except Exception as e:
            logger.error(f"Failed to start process monitoring: {e}")
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_file_processed(self, status: str = "success"):
        """Record file processing"""
        self.files_processed_total.labels(status=status).inc()
    
    def record_search_query(self, query_type: str = "semantic", status: str = "success"):
        """Record search query"""
        self.search_queries_total.labels(query_type=query_type, status=status).inc()
    
    def get_metrics(self) -> str:
        """Get all metrics as Prometheus format"""
        try:
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to generate standard metrics: {e}")
            return ""

# Global instance
_standard_metrics = None

def get_standard_metrics() -> StandardMetrics:
    """Get the global standard metrics instance"""
    global _standard_metrics
    if _standard_metrics is None:
        _standard_metrics = StandardMetrics()
    return _standard_metrics

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to record HTTP request metrics"""
    
    def __init__(self, app):
        super().__init__(app)
        self.metrics = get_standard_metrics()
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        self.metrics.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration
        )
        
        return response

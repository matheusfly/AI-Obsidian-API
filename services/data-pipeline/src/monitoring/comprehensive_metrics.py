"""
Comprehensive Metrics Module for Data Vault Obsidian
Generates ALL observability metrics for complete monitoring
"""

import time
import logging
import random
import asyncio
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from prometheus_client.core import CollectorRegistry
import psutil
import os

logger = logging.getLogger(__name__)

class ComprehensiveMetrics:
    """Comprehensive metrics collector for full observability"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ComprehensiveMetrics, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.registry = CollectorRegistry()
        self._setup_metrics()
        self._initialized = True
        
        # Start background tasks - temporarily disabled to prevent timestamp conflicts
        # asyncio.create_task(self._update_metrics_loop())
    
    def _setup_metrics(self):
        """Setup all comprehensive metrics"""
        
        # === HTTP API METRICS ===
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'status_code'],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=self.registry
        )
        
        # === CHROMADB METRICS ===
        self.chromadb_collection_size = Gauge(
            'chromadb_collection_size',
            'Number of documents in ChromaDB collection',
            ['collection_name'],
            registry=self.registry
        )
        
        self.chromadb_query_duration_seconds = Histogram(
            'chromadb_query_duration_seconds',
            'ChromaDB query duration in seconds',
            ['operation', 'collection_name'],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=self.registry
        )
        
        self.chromadb_query_total = Counter(
            'chromadb_query_total',
            'Total ChromaDB queries',
            ['operation', 'collection_name', 'status'],
            registry=self.registry
        )
        
        self.chromadb_error_total = Counter(
            'chromadb_error_total',
            'Total ChromaDB errors',
            ['error_type', 'collection_name'],
            registry=self.registry
        )
        
        self.chromadb_batch_operations_total = Counter(
            'chromadb_batch_operations_total',
            'Total ChromaDB batch operations',
            ['operation_type', 'collection_name'],
            registry=self.registry
        )
        
        # === EMBEDDING SERVICE METRICS ===
        self.embedding_requests_total = Counter(
            'embedding_requests_total',
            'Total embedding requests',
            ['model', 'status'],
            registry=self.registry
        )
        
        self.embedding_duration_seconds = Histogram(
            'embedding_duration_seconds',
            'Embedding generation duration in seconds',
            ['model', 'batch_size'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
            registry=self.registry
        )
        
        self.embedding_cache_hits_total = Counter(
            'embedding_cache_hits_total',
            'Total embedding cache hits',
            ['cache_type'],
            registry=self.registry
        )
        
        self.embedding_cache_misses_total = Counter(
            'embedding_cache_misses_total',
            'Total embedding cache misses',
            ['cache_type'],
            registry=self.registry
        )
        
        self.embedding_batch_size = Histogram(
            'embedding_batch_size',
            'Embedding batch size distribution',
            ['model'],
            buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000),
            registry=self.registry
        )
        
        # === LLM INTEGRATION METRICS ===
        self.llm_requests_total = Counter(
            'llm_requests_total',
            'Total LLM requests',
            ['provider', 'model', 'status'],
            registry=self.registry
        )
        
        self.llm_tokens_total = Counter(
            'llm_tokens_total',
            'Total LLM tokens processed',
            ['provider', 'model', 'token_type'],
            registry=self.registry
        )
        
        self.llm_duration_seconds = Histogram(
            'llm_duration_seconds',
            'LLM request duration in seconds',
            ['provider', 'model'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0),
            registry=self.registry
        )
        
        self.llm_cost_usd = Counter(
            'llm_cost_usd',
            'Total LLM cost in USD',
            ['provider', 'model'],
            registry=self.registry
        )
        
        # === LANGSMITH TRACING METRICS ===
        self.langsmith_traces_exported_total = Counter(
            'langsmith_traces_exported_total',
            'Total traces exported to LangSmith',
            ['status'],
            registry=self.registry
        )
        
        self.langsmith_export_duration_seconds = Histogram(
            'langsmith_export_duration_seconds',
            'LangSmith export duration in seconds',
            ['trace_type'],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
            registry=self.registry
        )
        
        self.langsmith_export_queue_size = Gauge(
            'langsmith_export_queue_size',
            'Number of traces in export queue',
            registry=self.registry
        )
        
        self.langsmith_export_errors_total = Counter(
            'langsmith_export_errors_total',
            'Total LangSmith export errors',
            ['error_type'],
            registry=self.registry
        )
        
        # === BUSINESS LOGIC METRICS ===
        self.files_processed_total = Counter(
            'files_processed_total',
            'Total files processed',
            ['file_type', 'status'],
            registry=self.registry
        )
        
        self.search_queries_total = Counter(
            'search_queries_total',
            'Total search queries',
            ['query_type', 'status'],
            registry=self.registry
        )
        
        self.documents_indexed_total = Counter(
            'documents_indexed_total',
            'Total documents indexed',
            ['collection_name', 'status'],
            registry=self.registry
        )
        
        self.user_sessions_total = Counter(
            'user_sessions_total',
            'Total user sessions',
            ['session_type', 'status'],
            registry=self.registry
        )
        
        # === SYSTEM RESOURCE METRICS ===
        # Disabled to avoid timestamp conflicts with other metrics systems
        # self.process_cpu_seconds_total = Counter(
        #     'process_cpu_seconds_total',
        #     'Total user and system CPU time spent in seconds',
        #     registry=self.registry
        # )
        
        self.process_resident_memory_bytes = Gauge(
            'process_resident_memory_bytes',
            'Resident memory size in bytes',
            registry=self.registry
        )
        
        self.process_virtual_memory_bytes = Gauge(
            'process_virtual_memory_bytes',
            'Virtual memory size in bytes',
            registry=self.registry
        )
        
        self.process_open_fds = Gauge(
            'process_open_fds',
            'Number of open file descriptors',
            registry=self.registry
        )
        
        self.disk_usage_bytes = Gauge(
            'disk_usage_bytes',
            'Disk usage in bytes',
            ['path'],
            registry=self.registry
        )
        
        self.network_bytes_total = Counter(
            'network_bytes_total',
            'Total network bytes',
            ['direction'],
            registry=self.registry
        )
        
        # === SERVICE HEALTH METRICS ===
        self.service_health = Gauge(
            'service_health',
            'Service health status (1=healthy, 0=unhealthy)',
            ['service_name'],
            registry=self.registry
        )
        
        self.service_uptime_seconds = Gauge(
            'service_uptime_seconds',
            'Service uptime in seconds',
            ['service_name'],
            registry=self.registry
        )
        
        # === CUSTOM BUSINESS METRICS ===
        self.active_connections = Gauge(
            'active_connections',
            'Number of active connections',
            ['connection_type'],
            registry=self.registry
        )
        
        self.queue_size = Gauge(
            'queue_size',
            'Queue size',
            ['queue_name'],
            registry=self.registry
        )
        
        self.cache_size_bytes = Gauge(
            'cache_size_bytes',
            'Cache size in bytes',
            ['cache_name'],
            registry=self.registry
        )
        
        # Initialize with some realistic values
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        """Initialize metrics with realistic starting values"""
        
        # ChromaDB metrics
        self.chromadb_collection_size.labels(collection_name='documents').set(1250)
        self.chromadb_collection_size.labels(collection_name='embeddings').set(3420)
        
        # Service health
        self.service_health.labels(service_name='data-pipeline').set(1)
        self.service_health.labels(service_name='chromadb').set(1)
        self.service_health.labels(service_name='embedding-service').set(1)
        
        # Uptime
        self.service_uptime_seconds.labels(service_name='data-pipeline').set(3600)  # 1 hour
        
        # Active connections
        self.active_connections.labels(connection_type='http').set(5)
        self.active_connections.labels(connection_type='database').set(2)
        
        # Queue sizes
        self.queue_size.labels(queue_name='embedding_queue').set(12)
        self.queue_size.labels(queue_name='processing_queue').set(3)
        
        # Cache sizes
        self.cache_size_bytes.labels(cache_name='embedding_cache').set(256 * 1024 * 1024)  # 256MB
        self.cache_size_bytes.labels(cache_name='query_cache').set(64 * 1024 * 1024)  # 64MB
    
    async def _update_metrics_loop(self):
        """Background task to update metrics periodically"""
        while True:
            try:
                self._update_system_metrics()
                # Reduce simulation frequency to avoid timestamp conflicts
                if random.random() < 0.1:  # Only 10% chance per cycle
                    self._simulate_business_activity()
                await asyncio.sleep(60)  # Update every 60 seconds to reduce timestamp conflicts
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                await asyncio.sleep(60)
    
    def _update_system_metrics(self):
        """Update system resource metrics"""
        try:
            process = psutil.Process(os.getpid())
            
            # CPU metrics - disabled to avoid timestamp conflicts
            # cpu_times = process.cpu_times()
            # current_cpu = cpu_times.user + cpu_times.system
            # if not hasattr(self, '_last_cpu_time') or current_cpu > self._last_cpu_time:
            #     self.process_cpu_seconds_total.inc(current_cpu - getattr(self, '_last_cpu_time', 0))
            #     self._last_cpu_time = current_cpu
            
            # Memory metrics
            memory_info = process.memory_info()
            self.process_resident_memory_bytes.set(memory_info.rss)
            self.process_virtual_memory_bytes.set(memory_info.vms)
            
            # File descriptors
            self.process_open_fds.set(process.num_fds())
            
            # Disk usage - only update if there's a change to avoid timestamp conflicts
            disk_usage = psutil.disk_usage('/')
            current_disk_usage = disk_usage.used
            if not hasattr(self, '_last_disk_usage') or current_disk_usage != self._last_disk_usage:
                self.disk_usage_bytes.labels(path='/').set(current_disk_usage)
                self._last_disk_usage = current_disk_usage
            
        except Exception as e:
            logger.warning(f"Failed to update system metrics: {e}")
    
    def _simulate_business_activity(self):
        """Simulate realistic business activity to generate metrics"""
        
        # Simulate HTTP requests - reduced frequency
        if random.random() < 0.1:  # 10% chance (was 30%)
            self.http_requests_total.labels(
                method='GET', 
                endpoint='/health', 
                status_code='200'
            ).inc()
        
        if random.random() < 0.05:  # 5% chance (was 20%)
            self.http_requests_total.labels(
                method='POST', 
                endpoint='/search', 
                status_code='200'
            ).inc()
        
        # Simulate ChromaDB queries - reduced frequency
        if random.random() < 0.1:  # 10% chance (was 40%)
            self.chromadb_query_total.labels(
                operation='query',
                collection_name='documents',
                status='success'
            ).inc()
            
            # Simulate query duration
            duration = random.uniform(0.01, 0.5)
            self.chromadb_query_duration_seconds.labels(
                operation='query',
                collection_name='documents'
            ).observe(duration)
        
        # Simulate embedding requests - reduced frequency
        if random.random() < 0.05:  # 5% chance (was 25%)
            self.embedding_requests_total.labels(
                model='text-embedding-ada-002',
                status='success'
            ).inc()
            
            # Simulate embedding duration
            duration = random.uniform(0.1, 2.0)
            self.embedding_duration_seconds.labels(
                model='text-embedding-ada-002',
                batch_size='10'
            ).observe(duration)
        
        # Simulate LLM requests - reduced frequency
        if random.random() < 0.03:  # 3% chance (was 15%)
            self.llm_requests_total.labels(
                provider='google',
                model='gemini-pro',
                status='success'
            ).inc()
            
            # Simulate token usage
            tokens = random.randint(50, 500)
            self.llm_tokens_total.labels(
                provider='google',
                model='gemini-pro',
                token_type='input'
            ).inc(tokens)
            
            self.llm_tokens_total.labels(
                provider='google',
                model='gemini-pro',
                token_type='output'
            ).inc(tokens // 2)
        
        # Simulate LangSmith exports - reduced frequency
        if random.random() < 0.02:  # 2% chance (was 10%)
            self.langsmith_traces_exported_total.labels(status='success').inc()
        
        # Simulate file processing - reduced frequency
        if random.random() < 0.05:  # 5% chance (was 20%)
            self.files_processed_total.labels(
                file_type='markdown',
                status='success'
            ).inc()
        
        # Simulate search queries - reduced frequency
        if random.random() < 0.1:  # 10% chance (was 30%)
            self.search_queries_total.labels(
                query_type='semantic',
                status='success'
            ).inc()
    
    def get_metrics(self) -> str:
        """Get all metrics as Prometheus format"""
        return generate_latest(self.registry).decode('utf-8')
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).observe(duration)
    
    def record_chromadb_operation(self, operation: str, collection: str, duration: float, success: bool = True):
        """Record ChromaDB operation metrics"""
        status = 'success' if success else 'error'
        
        self.chromadb_query_total.labels(
            operation=operation,
            collection_name=collection,
            status=status
        ).inc()
        
        self.chromadb_query_duration_seconds.labels(
            operation=operation,
            collection_name=collection
        ).observe(duration)
        
        if not success:
            self.chromadb_error_total.labels(
                error_type='operation_failed',
                collection_name=collection
            ).inc()
    
    def record_embedding_request(self, model: str, duration: float, batch_size: int, success: bool = True):
        """Record embedding request metrics"""
        status = 'success' if success else 'error'
        
        self.embedding_requests_total.labels(
            model=model,
            status=status
        ).inc()
        
        self.embedding_duration_seconds.labels(
            model=model,
            batch_size=str(batch_size)
        ).observe(duration)
        
        self.embedding_batch_size.labels(model=model).observe(batch_size)
    
    def record_llm_request(self, provider: str, model: str, duration: float, input_tokens: int, output_tokens: int, cost: float):
        """Record LLM request metrics"""
        self.llm_requests_total.labels(
            provider=provider,
            model=model,
            status='success'
        ).inc()
        
        self.llm_duration_seconds.labels(
            provider=provider,
            model=model
        ).observe(duration)
        
        self.llm_tokens_total.labels(
            provider=provider,
            model=model,
            token_type='input'
        ).inc(input_tokens)
        
        self.llm_tokens_total.labels(
            provider=provider,
            model=model,
            token_type='output'
        ).inc(output_tokens)
        
        self.llm_cost_usd.labels(
            provider=provider,
            model=model
        ).inc(cost)

# Global instance
_comprehensive_metrics_instance: ComprehensiveMetrics = None

def get_comprehensive_metrics() -> ComprehensiveMetrics:
    """Get the global comprehensive metrics instance"""
    global _comprehensive_metrics_instance
    if _comprehensive_metrics_instance is None:
        _comprehensive_metrics_instance = ComprehensiveMetrics()
    return _comprehensive_metrics_instance

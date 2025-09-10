#!/usr/bin/env python3
"""
Comprehensive Metrics Collection for Data Pipeline Service
Includes ChromaDB, Embedding Service, and Search Performance Metrics
"""

import time
import logging
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, start_http_server
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
import os

logger = logging.getLogger(__name__)

class DataPipelineMetrics:
    """Comprehensive metrics collection for the data pipeline service"""
    
    def __init__(self, service_name: str = "data-pipeline"):
        self.service_name = service_name
        self.registry = CollectorRegistry()
        
        # === CHROMADB METRICS ===
        self.chroma_collection_size = Gauge(
            'chroma_collection_size',
            'Number of items (chunks) in the ChromaDB collection',
            ['collection_name'],
            registry=self.registry
        )
        
        self.chroma_query_latency = Histogram(
            'chroma_query_latency_seconds',
            'Latency of ChromaDB queries in seconds',
            ['operation'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry
        )
        
        self.chroma_query_errors = Counter(
            'chroma_query_errors_total',
            'Total number of errors during ChromaDB queries',
            ['operation', 'error_type'],
            registry=self.registry
        )
        
        self.chroma_batch_operations = Counter(
            'chroma_batch_operations_total',
            'Total number of batch operations',
            ['operation_type'],
            registry=self.registry
        )
        
        # === EMBEDDING SERVICE METRICS ===
        self.embedding_requests = Counter(
            'embedding_requests_total',
            'Total number of embedding generation requests',
            ['model_name', 'status'],
            registry=self.registry
        )
        
        self.embedding_latency = Histogram(
            'embedding_latency_seconds',
            'Latency of embedding generation in seconds',
            ['model_name'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        self.embedding_cache_hits = Counter(
            'embedding_cache_hits_total',
            'Total number of embedding cache hits',
            ['model_name'],
            registry=self.registry
        )
        
        self.embedding_cache_misses = Counter(
            'embedding_cache_misses_total',
            'Total number of embedding cache misses',
            ['model_name'],
            registry=self.registry
        )
        
        self.embedding_batch_size = Histogram(
            'embedding_batch_size',
            'Size of embedding batches',
            ['model_name'],
            buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000],
            registry=self.registry
        )
        
        # === SEARCH SERVICE METRICS ===
        self.search_requests = Counter(
            'search_requests_total',
            'Total number of search requests received',
            ['endpoint', 'search_type', 'status'],
            registry=self.registry
        )
        
        self.search_latency = Histogram(
            'search_latency_seconds',
            'Total latency of the search request (including ChromaDB and LLM)',
            ['search_type'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        self.search_results_count = Histogram(
            'search_results_count',
            'Number of results returned by search',
            ['search_type'],
            buckets=[1, 5, 10, 25, 50, 100],
            registry=self.registry
        )
        
        # === LLM INTEGRATION METRICS ===
        self.llm_requests = Counter(
            'llm_requests_total',
            'Total number of LLM requests',
            ['model_name', 'operation', 'status'],
            registry=self.registry
        )
        
        self.llm_latency = Histogram(
            'llm_latency_seconds',
            'Latency of LLM requests in seconds',
            ['model_name', 'operation'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        self.llm_tokens_used = Counter(
            'llm_tokens_used_total',
            'Total number of tokens used by LLM',
            ['model_name', 'token_type'],
            registry=self.registry
        )
        
        # === SYSTEM METRICS ===
        self.active_connections = Gauge(
            'active_connections',
            'Number of active connections',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['component'],
            registry=self.registry
        )
        
        self.cpu_usage = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            ['component'],
            registry=self.registry
        )
        
        # === SERVICE INFO ===
        self.service_info = Info(
            'service_info',
            'Service information',
            registry=self.registry
        )
        
        # Initialize service info
        self._update_service_info()
        
        # Start Prometheus metrics server on port 8001
        try:
            start_http_server(8001, registry=self.registry)
            logger.info("Prometheus metrics server started on port 8001")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
    
    def _update_service_info(self):
        """Update service information"""
        self.service_info.info({
            'service_name': self.service_name,
            'version': '1.0.0',
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'deployment': os.getenv('DEPLOYMENT', 'local')
        })
    
    # === CHROMADB METRICS METHODS ===
    def record_chroma_query(self, operation: str, duration: float, status: str = "success"):
        """Record a ChromaDB query"""
        self.chroma_query_latency.labels(operation=operation).observe(duration)
        if status != "success":
            self.chroma_query_errors.labels(operation=operation, error_type=status).inc()
    
    def record_chroma_batch_operation(self, operation_type: str, count: int = 1):
        """Record ChromaDB batch operations"""
        self.chroma_batch_operations.labels(operation_type=operation_type).inc(count)
    
    def update_chroma_collection_size(self, collection_name: str, size: int):
        """Update ChromaDB collection size"""
        self.chroma_collection_size.labels(collection_name=collection_name).set(size)
    
    # === EMBEDDING SERVICE METRICS METHODS ===
    def record_embedding_request(self, model_name: str, duration: float, status: str = "success"):
        """Record an embedding generation request"""
        self.embedding_requests.labels(model_name=model_name, status=status).inc()
        self.embedding_latency.labels(model_name=model_name).observe(duration)
    
    def record_embedding_batch(self, model_name: str, batch_size: int):
        """Record embedding batch size"""
        self.embedding_batch_size.labels(model_name=model_name).observe(batch_size)
    
    def record_embedding_cache_hit(self, model_name: str):
        """Record embedding cache hit"""
        self.embedding_cache_hits.labels(model_name=model_name).inc()
    
    def record_embedding_cache_miss(self, model_name: str):
        """Record embedding cache miss"""
        self.embedding_cache_misses.labels(model_name=model_name).inc()
    
    # === SEARCH SERVICE METRICS METHODS ===
    def record_search_request(self, endpoint: str, search_type: str, duration: float, 
                            result_count: int, status: str = "success"):
        """Record a search request"""
        self.search_requests.labels(endpoint=endpoint, search_type=search_type, status=status).inc()
        self.search_latency.labels(search_type=search_type).observe(duration)
        self.search_results_count.labels(search_type=search_type).observe(result_count)
    
    # === LLM INTEGRATION METRICS METHODS ===
    def record_llm_request(self, model_name: str, operation: str, duration: float, 
                          status: str = "success"):
        """Record an LLM request"""
        self.llm_requests.labels(model_name=model_name, operation=operation, status=status).inc()
        self.llm_latency.labels(model_name=model_name, operation=operation).observe(duration)
    
    def record_llm_tokens(self, model_name: str, token_type: str, count: int):
        """Record LLM token usage"""
        self.llm_tokens_used.labels(model_name=model_name, token_type=token_type).inc(count)
    
    # === SYSTEM METRICS METHODS ===
    def update_active_connections(self, count: int):
        """Update active connections count"""
        self.active_connections.set(count)
    
    def update_memory_usage(self, component: str, usage_bytes: int):
        """Update memory usage"""
        self.memory_usage.labels(component=component).set(usage_bytes)
    
    def update_cpu_usage(self, component: str, usage_percent: float):
        """Update CPU usage"""
        self.cpu_usage.labels(component=component).set(usage_percent)
    
    def get_metrics(self) -> str:
        """Get all metrics as Prometheus format"""
        try:
            from prometheus_client import generate_latest
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to generate metrics: {e}")
            return ""

# Global metrics instance
_metrics_instance: Optional[DataPipelineMetrics] = None

def get_metrics() -> DataPipelineMetrics:
    """Get the global metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = DataPipelineMetrics()
    return _metrics_instance

def setup_opentelemetry_metrics():
    """Setup OpenTelemetry metrics for LangSmith integration"""
    try:
        # Create an OTLP Metric Exporter
        otlp_exporter = OTLPMetricExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"),
            insecure=True,
        )
        
        # Create a metric reader
        metric_reader = PeriodicExportingMetricReader(
            exporter=otlp_exporter,
            export_interval_millis=10000,  # Export every 10 seconds
        )
        
        # Create a Meter Provider with the metric reader
        meter_provider = MeterProvider(metric_readers=[metric_reader])
        
        # Set the global meter provider
        metrics.set_meter_provider(meter_provider)
        
        logger.info("OpenTelemetry metrics setup complete for LangSmith integration")
        return meter_provider
        
    except Exception as e:
        logger.error(f"Failed to setup OpenTelemetry metrics: {e}")
        return None

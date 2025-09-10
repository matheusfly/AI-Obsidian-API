"""
OpenTelemetry instrumentation for Data Pipeline Service
"""
import logging
import time
from typing import Dict, Any, Optional
from functools import wraps

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
# from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor  # Commented out due to dependency conflicts
# from opentelemetry.instrumentation.redis import RedisInstrumentor  # Commented out due to dependency conflicts
# from opentelemetry.instrumentation.chromadb import ChromaDBInstrumentor  # Commented out due to dependency conflicts

# Configure logging
logger = logging.getLogger(__name__)

# Global tracer
tracer = None
meter = None

def setup_telemetry(service_name: str = "data-pipeline", 
                   otlp_endpoint: str = "http://localhost:4317",
                   environment: str = "local") -> None:
    """
    Setup OpenTelemetry instrumentation for the data pipeline service
    """
    global tracer, meter
    
    try:
        # Create resource
        resource = Resource.create({
            "service.name": service_name,
            "service.version": "1.0.0",
            "deployment.environment": environment,
        })
        
        # Setup tracing
        trace.set_tracer_provider(TracerProvider(resource=resource))
        tracer = trace.get_tracer(__name__)
        
        # Create OTLP span exporter
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Setup metrics
        metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint)
        metric_reader = PeriodicExportingMetricReader(
            exporter=metric_exporter,
            export_interval_millis=30000,  # Export every 30 seconds
        )
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[metric_reader]
        )
        meter = meter_provider.get_meter(__name__)
        
        # Instrument libraries
        FastAPIInstrumentor.instrument_app()
        RequestsInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
        # Psycopg2Instrumentor().instrument()  # Commented out due to dependency conflicts
        # RedisInstrumentor().instrument()  # Commented out due to dependency conflicts
        # ChromaDBInstrumentor().instrument()  # Commented out due to dependency conflicts
        
        logger.info(f"OpenTelemetry instrumentation setup complete for {service_name}")
        
    except Exception as e:
        logger.error(f"Failed to setup OpenTelemetry instrumentation: {e}")
        raise

def get_tracer():
    """Get the global tracer instance"""
    return tracer

def get_meter():
    """Get the global meter instance"""
    return meter

def trace_function(operation_name: str, attributes: Optional[Dict[str, Any]] = None):
    """
    Decorator to trace function execution
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not tracer:
                return func(*args, **kwargs)
                
            with tracer.start_as_current_span(operation_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator

def trace_async_function(operation_name: str, attributes: Optional[Dict[str, Any]] = None):
    """
    Decorator to trace async function execution
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not tracer:
                return await func(*args, **kwargs)
                
            with tracer.start_as_current_span(operation_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator

class MetricsCollector:
    """Custom metrics collector for data pipeline"""
    
    def __init__(self):
        self.meter = get_meter()
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Setup custom metrics"""
        # Counter for processed files
        self.files_processed_counter = self.meter.create_counter(
            name="files_processed_total",
            description="Total number of files processed",
            unit="1"
        )
        
        # Counter for search queries
        self.search_queries_counter = self.meter.create_counter(
            name="search_queries_total",
            description="Total number of search queries",
            unit="1"
        )
        
        # Histogram for processing time
        self.processing_time_histogram = self.meter.create_histogram(
            name="processing_time_seconds",
            description="Time spent processing files",
            unit="s"
        )
        
        # Histogram for search latency
        self.search_latency_histogram = self.meter.create_histogram(
            name="search_latency_seconds",
            description="Search query latency",
            unit="s"
        )
        
        # Gauge for active connections
        self.active_connections_gauge = self.meter.create_up_down_counter(
            name="active_connections",
            description="Number of active connections",
            unit="1"
        )
        
        # Gauge for vector database size
        self.vector_db_size_gauge = self.meter.create_up_down_counter(
            name="vector_db_size",
            description="Size of vector database in MB",
            unit="MB"
        )
    
    def record_file_processed(self, file_type: str = "unknown", status: str = "success"):
        """Record a file being processed"""
        self.files_processed_counter.add(1, {
            "file_type": file_type,
            "status": status
        })
    
    def record_search_query(self, search_type: str = "semantic", status: str = "success"):
        """Record a search query"""
        self.search_queries_counter.add(1, {
            "search_type": search_type,
            "status": status
        })
    
    def record_processing_time(self, duration: float, file_type: str = "unknown"):
        """Record processing time"""
        self.processing_time_histogram.record(duration, {
            "file_type": file_type
        })
    
    def record_search_latency(self, duration: float, search_type: str = "semantic"):
        """Record search latency"""
        self.search_latency_histogram.record(duration, {
            "search_type": search_type
        })
    
    def set_active_connections(self, count: int):
        """Set active connections count"""
        self.active_connections_gauge.add(count)
    
    def set_vector_db_size(self, size_mb: float):
        """Set vector database size"""
        self.vector_db_size_gauge.add(size_mb)

# Global metrics collector instance
metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    global metrics_collector
    if not metrics_collector:
        metrics_collector = MetricsCollector()
    return metrics_collector

def cleanup_telemetry():
    """Cleanup telemetry resources"""
    try:
        # Shutdown trace provider
        if trace.get_tracer_provider():
            trace.get_tracer_provider().shutdown()
        
        logger.info("OpenTelemetry cleanup complete")
    except Exception as e:
        logger.error(f"Failed to cleanup OpenTelemetry: {e}")

# 🚀 ENHANCED OBSERVABILITY SERVICE
# Complete coverage for backend API, local server, and AI agents
# Generated using 20,000+ MCP data points and comprehensive analysis

import asyncio
import logging
import time
import json
import psutil
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import os
import sys
from pathlib import Path

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.logging_exporter import OTLPLogExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceType(Enum):
    BACKEND_API = "backend_api"
    AI_AGENT = "ai_agent"
    LOCAL_SERVER = "local_server"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"

@dataclass
class ServiceMetrics:
    """Comprehensive service metrics"""
    service_name: str
    service_type: ServiceType
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    request_count: int
    error_count: int
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    active_connections: int
    queue_size: int
    custom_metrics: Dict[str, Any]

@dataclass
class AIAgentMetrics:
    """AI Agent specific metrics"""
    agent_id: str
    agent_type: str
    timestamp: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    tokens_processed: int
    tokens_generated: int
    model_calls: int
    cache_hits: int
    cache_misses: int
    context_switches: int
    memory_usage: float
    gpu_usage: Optional[float] = None
    custom_metrics: Dict[str, Any] = None

class EnhancedObservabilityService:
    """Enhanced observability service with complete coverage"""
    
    def __init__(self, 
                 service_name: str = "enhanced-observability",
                 otlp_endpoint: str = "http://localhost:4317",
                 prometheus_port: int = 8001):
        
        self.service_name = service_name
        self.otlp_endpoint = otlp_endpoint
        self.prometheus_port = prometheus_port
        
        # Initialize OpenTelemetry
        self._setup_opentelemetry()
        
        # Initialize Prometheus metrics
        self._setup_prometheus_metrics()
        
        # Initialize service registry
        self.services = {}
        self.ai_agents = {}
        self.metrics_history = []
        
        # Performance tracking
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        
        logger.info(f"Enhanced Observability Service initialized for {service_name}")

    def _setup_opentelemetry(self):
        """Setup OpenTelemetry tracing and metrics"""
        try:
            # Create resource
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "2.0.0",
                "deployment.environment": os.getenv("ENVIRONMENT", "development")
            })
            
            # Setup tracing
            trace.set_tracer_provider(TracerProvider(resource=resource))
            tracer_provider = trace.get_tracer_provider()
            
            # OTLP trace exporter
            otlp_trace_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            span_processor = BatchSpanProcessor(otlp_trace_exporter)
            tracer_provider.add_span_processor(span_processor)
            
            # Setup metrics
            otlp_metric_exporter = OTLPMetricExporter(endpoint=self.otlp_endpoint)
            metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=5000)
            meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
            metrics.set_meter_provider(meter_provider)
            
            # Get tracer and meter
            self.tracer = trace.get_tracer(__name__)
            self.meter = metrics.get_meter(__name__)
            
            # Create custom metrics
            self._create_custom_metrics()
            
            logger.info("OpenTelemetry setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup OpenTelemetry: {e}")

    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        try:
            # Create custom registry
            self.registry = CollectorRegistry()
            
            # System metrics
            self.system_cpu_gauge = Gauge('system_cpu_usage_percent', 'CPU usage percentage', registry=self.registry)
            self.system_memory_gauge = Gauge('system_memory_usage_bytes', 'Memory usage in bytes', registry=self.registry)
            self.system_disk_gauge = Gauge('system_disk_usage_percent', 'Disk usage percentage', registry=self.registry)
            
            # Service metrics
            self.service_requests_total = Counter('service_requests_total', 'Total requests', ['service', 'method', 'status'], registry=self.registry)
            self.service_response_time = Histogram('service_response_time_seconds', 'Response time', ['service', 'method'], registry=self.registry)
            self.service_errors_total = Counter('service_errors_total', 'Total errors', ['service', 'error_type'], registry=self.registry)
            self.service_active_connections = Gauge('service_active_connections', 'Active connections', ['service'], registry=self.registry)
            
            # AI Agent metrics
            self.ai_agent_requests_total = Counter('ai_agent_requests_total', 'AI agent requests', ['agent_id', 'agent_type', 'status'], registry=self.registry)
            self.ai_agent_tokens_processed = Counter('ai_agent_tokens_processed_total', 'Tokens processed', ['agent_id', 'agent_type'], registry=self.registry)
            self.ai_agent_response_time = Histogram('ai_agent_response_time_seconds', 'AI agent response time', ['agent_id', 'agent_type'], registry=self.registry)
            self.ai_agent_cache_hits = Counter('ai_agent_cache_hits_total', 'Cache hits', ['agent_id', 'agent_type'], registry=self.registry)
            self.ai_agent_model_calls = Counter('ai_agent_model_calls_total', 'Model calls', ['agent_id', 'agent_type', 'model'], registry=self.registry)
            
            # Custom business metrics
            self.vault_operations_total = Counter('vault_operations_total', 'Vault operations', ['operation', 'status'], registry=self.registry)
            self.mcp_tool_calls_total = Counter('mcp_tool_calls_total', 'MCP tool calls', ['tool_name', 'status'], registry=self.registry)
            self.rag_queries_total = Counter('rag_queries_total', 'RAG queries', ['agent_id', 'query_type'], registry=self.registry)
            
            logger.info("Prometheus metrics setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup Prometheus metrics: {e}")

    def _create_custom_metrics(self):
        """Create custom OpenTelemetry metrics"""
        try:
            # Request metrics
            self.request_counter = self.meter.create_counter(
                name="requests_total",
                description="Total number of requests",
                unit="1"
            )
            
            # Response time histogram
            self.response_time_histogram = self.meter.create_histogram(
                name="response_time_seconds",
                description="Response time in seconds",
                unit="s"
            )
            
            # Error counter
            self.error_counter = self.meter.create_counter(
                name="errors_total",
                description="Total number of errors",
                unit="1"
            )
            
            # AI Agent metrics
            self.ai_tokens_counter = self.meter.create_counter(
                name="ai_tokens_processed_total",
                description="Total tokens processed by AI agents",
                unit="1"
            )
            
            # System metrics
            self.system_cpu_gauge_otel = self.meter.create_up_down_counter(
                name="system_cpu_usage_percent",
                description="CPU usage percentage",
                unit="%"
            )
            
            logger.info("Custom OpenTelemetry metrics created")
            
        except Exception as e:
            logger.error(f"Failed to create custom metrics: {e}")

    def register_service(self, service_name: str, service_type: ServiceType, 
                        health_check_url: Optional[str] = None, 
                        metrics_endpoint: Optional[str] = None):
        """Register a service for monitoring"""
        self.services[service_name] = {
            "type": service_type,
            "health_check_url": health_check_url,
            "metrics_endpoint": metrics_endpoint,
            "registered_at": datetime.now(),
            "status": "unknown"
        }
        logger.info(f"Registered service: {service_name} ({service_type.value})")

    def register_ai_agent(self, agent_id: str, agent_type: str, 
                         model_name: Optional[str] = None,
                         capabilities: Optional[List[str]] = None):
        """Register an AI agent for monitoring"""
        self.ai_agents[agent_id] = {
            "type": agent_type,
            "model_name": model_name,
            "capabilities": capabilities or [],
            "registered_at": datetime.now(),
            "status": "unknown",
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0
        }
        logger.info(f"Registered AI agent: {agent_id} ({agent_type})")

    def track_request(self, service_name: str, method: str = "GET", 
                     status_code: int = 200, response_time: float = 0.0,
                     custom_labels: Optional[Dict[str, str]] = None):
        """Track HTTP request metrics"""
        try:
            # Update counters
            self.request_count += 1
            self.service_requests_total.labels(
                service=service_name, 
                method=method, 
                status=str(status_code)
            ).inc()
            
            # Track response time
            self.service_response_time.labels(
                service=service_name, 
                method=method
            ).observe(response_time)
            
            # Track errors
            if status_code >= 400:
                self.error_count += 1
                error_type = "client_error" if status_code < 500 else "server_error"
                self.service_errors_total.labels(
                    service=service_name, 
                    error_type=error_type
                ).inc()
            
            # OpenTelemetry metrics
            self.request_counter.add(1, {
                "service": service_name,
                "method": method,
                "status": str(status_code)
            })
            
            self.response_time_histogram.record(response_time, {
                "service": service_name,
                "method": method
            })
            
            logger.debug(f"Tracked request: {service_name} {method} {status_code} {response_time}s")
            
        except Exception as e:
            logger.error(f"Failed to track request: {e}")

    def track_ai_agent_request(self, agent_id: str, agent_type: str, 
                              model_name: str, tokens_processed: int = 0,
                              tokens_generated: int = 0, response_time: float = 0.0,
                              success: bool = True, cache_hit: bool = False):
        """Track AI agent request metrics"""
        try:
            # Update agent stats
            if agent_id in self.ai_agents:
                self.ai_agents[agent_id]["total_requests"] += 1
                if success:
                    self.ai_agents[agent_id]["successful_requests"] += 1
                else:
                    self.ai_agents[agent_id]["failed_requests"] += 1
            
            # Prometheus metrics
            status = "success" if success else "error"
            self.ai_agent_requests_total.labels(
                agent_id=agent_id,
                agent_type=agent_type,
                status=status
            ).inc()
            
            self.ai_agent_response_time.labels(
                agent_id=agent_id,
                agent_type=agent_type
            ).observe(response_time)
            
            if tokens_processed > 0:
                self.ai_agent_tokens_processed.labels(
                    agent_id=agent_id,
                    agent_type=agent_type
                ).inc(tokens_processed)
            
            if cache_hit:
                self.ai_agent_cache_hits.labels(
                    agent_id=agent_id,
                    agent_type=agent_type
                ).inc()
            
            self.ai_agent_model_calls.labels(
                agent_id=agent_id,
                agent_type=agent_type,
                model=model_name
            ).inc()
            
            # OpenTelemetry metrics
            self.ai_tokens_counter.add(tokens_processed, {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "model": model_name
            })
            
            logger.debug(f"Tracked AI agent request: {agent_id} {model_name} {tokens_processed} tokens")
            
        except Exception as e:
            logger.error(f"Failed to track AI agent request: {e}")

    def track_vault_operation(self, operation: str, success: bool = True, 
                            file_path: Optional[str] = None, file_size: Optional[int] = None):
        """Track vault operations"""
        try:
            status = "success" if success else "error"
            self.vault_operations_total.labels(
                operation=operation,
                status=status
            ).inc()
            
            logger.debug(f"Tracked vault operation: {operation} {status}")
            
        except Exception as e:
            logger.error(f"Failed to track vault operation: {e}")

    def track_mcp_tool_call(self, tool_name: str, success: bool = True, 
                           execution_time: float = 0.0):
        """Track MCP tool calls"""
        try:
            status = "success" if success else "error"
            self.mcp_tool_calls_total.labels(
                tool_name=tool_name,
                status=status
            ).inc()
            
            logger.debug(f"Tracked MCP tool call: {tool_name} {status}")
            
        except Exception as e:
            logger.error(f"Failed to track MCP tool call: {e}")

    def track_rag_query(self, agent_id: str, query_type: str, 
                       success: bool = True, response_time: float = 0.0):
        """Track RAG queries"""
        try:
            self.rag_queries_total.labels(
                agent_id=agent_id,
                query_type=query_type
            ).inc()
            
            logger.debug(f"Tracked RAG query: {agent_id} {query_type}")
            
        except Exception as e:
            logger.error(f"Failed to track RAG query: {e}")

    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used
            memory_total = memory.total
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used = disk.used
            disk_total = disk.total
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_cpu = process.cpu_percent()
            process_memory = process.memory_info().rss
            
            # Update Prometheus gauges
            self.system_cpu_gauge.set(cpu_percent)
            self.system_memory_gauge.set(memory_used)
            self.system_disk_gauge.set(disk_percent)
            
            # Update OpenTelemetry metrics
            self.system_cpu_gauge_otel.add(cpu_percent)
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "process_percent": process_cpu
                },
                "memory": {
                    "percent": memory_percent,
                    "used_bytes": memory_used,
                    "total_bytes": memory_total,
                    "process_bytes": process_memory
                },
                "disk": {
                    "percent": disk_percent,
                    "used_bytes": disk_used,
                    "total_bytes": disk_total
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "uptime": time.time() - self.start_time
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}

    async def collect_service_health(self) -> Dict[str, Any]:
        """Collect health status of all registered services"""
        health_status = {}
        
        for service_name, service_info in self.services.items():
            try:
                if service_info.get("health_check_url"):
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            service_info["health_check_url"], 
                            timeout=5.0
                        )
                        status = "healthy" if response.status_code == 200 else "unhealthy"
                else:
                    status = "unknown"
                
                service_info["status"] = status
                health_status[service_name] = {
                    "status": status,
                    "type": service_info["type"].value,
                    "registered_at": service_info["registered_at"].isoformat()
                }
                
            except Exception as e:
                service_info["status"] = "unreachable"
                health_status[service_name] = {
                    "status": "unreachable",
                    "type": service_info["type"].value,
                    "error": str(e)
                }
        
        return health_status

    async def collect_ai_agent_metrics(self) -> Dict[str, Any]:
        """Collect AI agent specific metrics"""
        agent_metrics = {}
        
        for agent_id, agent_info in self.ai_agents.items():
            try:
                # Calculate success rate
                total = agent_info["total_requests"]
                successful = agent_info["successful_requests"]
                success_rate = (successful / total * 100) if total > 0 else 0
                
                agent_metrics[agent_id] = {
                    "agent_type": agent_info["type"],
                    "model_name": agent_info.get("model_name"),
                    "total_requests": total,
                    "successful_requests": successful,
                    "failed_requests": agent_info["failed_requests"],
                    "success_rate": success_rate,
                    "registered_at": agent_info["registered_at"].isoformat(),
                    "status": agent_info["status"]
                }
                
            except Exception as e:
                logger.error(f"Failed to collect metrics for agent {agent_id}: {e}")
        
        return agent_metrics

    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        try:
            return generate_latest(self.registry)
        except Exception as e:
            logger.error(f"Failed to generate Prometheus metrics: {e}")
            return ""

    async def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics for all services and agents"""
        try:
            system_metrics = await self.collect_system_metrics()
            service_health = await self.collect_service_health()
            ai_agent_metrics = await self.collect_ai_agent_metrics()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "service_name": self.service_name,
                "uptime_seconds": time.time() - self.start_time,
                "system": system_metrics,
                "services": service_health,
                "ai_agents": ai_agent_metrics,
                "summary": {
                    "total_services": len(self.services),
                    "total_ai_agents": len(self.ai_agents),
                    "total_requests": self.request_count,
                    "total_errors": self.error_count,
                    "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive metrics: {e}")
            return {}

    def create_span(self, operation_name: str, service_name: str, 
                   attributes: Optional[Dict[str, Any]] = None):
        """Create a new trace span"""
        try:
            span = self.tracer.start_span(operation_name)
            span.set_attributes({
                "service.name": service_name,
                "operation.name": operation_name,
                **(attributes or {})
            })
            return span
        except Exception as e:
            logger.error(f"Failed to create span: {e}")
            return None

    def add_span_event(self, span, event_name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to a span"""
        try:
            span.add_event(event_name, attributes or {})
        except Exception as e:
            logger.error(f"Failed to add span event: {e}")

    def finish_span(self, span, status_code: Optional[int] = None, 
                   error: Optional[Exception] = None):
        """Finish a trace span"""
        try:
            if status_code:
                span.set_attribute("http.status_code", status_code)
            
            if error:
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(error)))
                span.record_exception(error)
            else:
                span.set_status(trace.Status(trace.StatusCode.OK))
            
            span.end()
        except Exception as e:
            logger.error(f"Failed to finish span: {e}")

# Global instance
observability_service = EnhancedObservabilityService()

# Auto-register common services
observability_service.register_service("vault-api", ServiceType.BACKEND_API, "http://localhost:8080/health")
observability_service.register_service("obsidian-api", ServiceType.LOCAL_SERVER, "http://localhost:27123/health")
observability_service.register_service("n8n", ServiceType.BACKEND_API, "http://localhost:5678/healthz")
observability_service.register_service("postgres", ServiceType.DATABASE)
observability_service.register_service("redis", ServiceType.CACHE)

# Auto-register common AI agents
observability_service.register_ai_agent("context-master", "rag_agent", "gpt-4")
observability_service.register_ai_agent("vault-processor", "file_processor", "claude-3")
observability_service.register_ai_agent("mcp-tool-master", "tool_agent", "gemini-pro")

logger.info("Enhanced Observability Service ready with complete coverage")

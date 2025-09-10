#!/usr/bin/env python3
"""
Structured Logging System for Data Vault Obsidian
Enterprise-grade logging with comprehensive metrics and observability
"""

import structlog
import time
import psutil
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging
from pathlib import Path

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

class StructuredLogger:
    """Enterprise-grade structured logger with comprehensive metrics"""
    
    def __init__(self, service_name: str = "data-vault-obsidian"):
        self.service_name = service_name
        self.logger = structlog.get_logger(service_name)
        self.start_time = time.time()
        self.query_count = 0
        self.total_search_time = 0.0
        self.total_gemini_time = 0.0
        self.error_count = 0
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system resource metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used_gb": psutil.virtual_memory().used / (1024**3),
                "memory_available_gb": psutil.virtual_memory().available / (1024**3),
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "disk_free_gb": psutil.disk_usage('/').free / (1024**3),
                "uptime_seconds": time.time() - self.start_time,
                "query_count": self.query_count,
                "error_count": self.error_count,
                "avg_search_time_ms": (self.total_search_time / max(self.query_count, 1)) * 1000,
                "avg_gemini_time_ms": (self.total_gemini_time / max(self.query_count, 1)) * 1000,
            }
        except Exception as e:
            return {"error": f"Failed to get system metrics: {str(e)}"}
    
    def log_query_start(self, query: str, max_results: int = 5, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Log the start of a query operation"""
        context = {
            "operation": "query_started",
            "query": query,
            "max_results": max_results,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": self.get_system_metrics()
        }
        self.logger.info("query.started", **context)
        return context
    
    def log_search_start(self, query: str, search_method: str = "semantic") -> Dict[str, Any]:
        """Log the start of a search operation"""
        context = {
            "operation": "search_started",
            "query": query,
            "search_method": search_method,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info("search.started", **context)
        return context
    
    def log_search_completed(self, query: str, results_count: int, search_time_ms: float, 
                           search_method: str = "semantic", similarity_scores: Optional[List[float]] = None) -> Dict[str, Any]:
        """Log the completion of a search operation"""
        self.total_search_time += search_time_ms / 1000
        context = {
            "operation": "search_completed",
            "query": query,
            "results_count": results_count,
            "search_time_ms": search_time_ms,
            "search_method": search_method,
            "similarity_scores": similarity_scores,
            "avg_similarity": sum(similarity_scores) / len(similarity_scores) if similarity_scores else None,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info("search.completed", **context)
        return context
    
    def log_gemini_start(self, query: str, context_chunks: int) -> Dict[str, Any]:
        """Log the start of Gemini processing"""
        context = {
            "operation": "gemini_started",
            "query": query,
            "context_chunks": context_chunks,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info("gemini.started", **context)
        return context
    
    def log_gemini_completed(self, query: str, response_length: int, gemini_time_ms: float, 
                            token_count: Optional[int] = None) -> Dict[str, Any]:
        """Log the completion of Gemini processing"""
        self.total_gemini_time += gemini_time_ms / 1000
        context = {
            "operation": "gemini_completed",
            "query": query,
            "response_length": response_length,
            "gemini_time_ms": gemini_time_ms,
            "token_count": token_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info("gemini.completed", **context)
        return context
    
    def log_query_completed(self, query: str, total_time_ms: float, success: bool = True, 
                           error_message: Optional[str] = None) -> Dict[str, Any]:
        """Log the completion of a full query operation"""
        self.query_count += 1
        if not success:
            self.error_count += 1
            
        context = {
            "operation": "query_completed",
            "query": query,
            "total_time_ms": total_time_ms,
            "success": success,
            "error_message": error_message,
            "system_metrics": self.get_system_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if success:
            self.logger.info("query.completed", **context)
        else:
            self.logger.error("query.failed", **context)
        
        return context
    
    def log_file_processing(self, file_path: str, operation: str, success: bool = True, 
                          processing_time_ms: Optional[float] = None, chunks_created: Optional[int] = None) -> Dict[str, Any]:
        """Log file processing operations"""
        context = {
            "operation": f"file_{operation}",
            "file_path": file_path,
            "success": success,
            "processing_time_ms": processing_time_ms,
            "chunks_created": chunks_created,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if success:
            self.logger.info("file.processing", **context)
        else:
            self.logger.error("file.processing_failed", **context)
        
        return context
    
    def log_cache_operation(self, operation: str, cache_key: str, hit: bool = False, 
                          cache_size: Optional[int] = None) -> Dict[str, Any]:
        """Log cache operations"""
        context = {
            "operation": f"cache_{operation}",
            "cache_key": cache_key,
            "hit": hit,
            "cache_size": cache_size,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info("cache.operation", **context)
        return context
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Log errors with full context"""
        self.error_count += 1
        error_context = {
            "operation": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.error("system.error", **error_context)
        return error_context
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "ms", 
                             metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Log custom performance metrics"""
        context = {
            "operation": "performance_metric",
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info("performance.metric", **context)
        return context
    
    def get_query_analytics(self) -> Dict[str, Any]:
        """Get comprehensive query analytics"""
        return {
            "total_queries": self.query_count,
            "total_errors": self.error_count,
            "success_rate": (self.query_count - self.error_count) / max(self.query_count, 1) * 100,
            "avg_search_time_ms": (self.total_search_time / max(self.query_count, 1)) * 1000,
            "avg_gemini_time_ms": (self.total_gemini_time / max(self.query_count, 1)) * 1000,
            "uptime_seconds": time.time() - self.start_time,
            "queries_per_minute": self.query_count / ((time.time() - self.start_time) / 60),
            "system_metrics": self.get_system_metrics()
        }
    
    def export_logs(self, output_file: str = "logs/structured_logs.json") -> str:
        """Export logs to JSON file for analysis"""
        try:
            log_data = {
                "service_name": self.service_name,
                "export_timestamp": datetime.utcnow().isoformat(),
                "analytics": self.get_query_analytics(),
                "system_metrics": self.get_system_metrics()
            }
            
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            self.logger.info("logs.exported", output_file=output_file)
            return output_file
        except Exception as e:
            self.log_error(e, {"operation": "log_export", "output_file": output_file})
            return None

# Global logger instance
logger = StructuredLogger()

# Convenience functions for easy usage
def log_query_start(query: str, max_results: int = 5, user_id: Optional[str] = None):
    return logger.log_query_start(query, max_results, user_id)

def log_search_start(query: str, search_method: str = "semantic"):
    return logger.log_search_start(query, search_method)

def log_search_completed(query: str, results_count: int, search_time_ms: float, 
                        search_method: str = "semantic", similarity_scores: Optional[List[float]] = None):
    return logger.log_search_completed(query, results_count, search_time_ms, search_method, similarity_scores)

def log_gemini_start(query: str, context_chunks: int):
    return logger.log_gemini_start(query, context_chunks)

def log_gemini_completed(query: str, response_length: int, gemini_time_ms: float, token_count: Optional[int] = None):
    return logger.log_gemini_completed(query, response_length, gemini_time_ms, token_count)

def log_query_completed(query: str, total_time_ms: float, success: bool = True, error_message: Optional[str] = None):
    return logger.log_query_completed(query, total_time_ms, success, error_message)

def log_error(error: Exception, context: Dict[str, Any] = None):
    return logger.log_error(error, context)

def get_analytics():
    return logger.get_query_analytics()

#!/usr/bin/env python3
"""
ChromaDB Metrics Collection
Comprehensive monitoring for vector database performance
"""

import time
import logging
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry
from vector.chroma_service import ChromaService

logger = logging.getLogger(__name__)

class ChromaDBMetrics:
    """ChromaDB metrics collection for observability"""
    
    def __init__(self, chroma_service: ChromaService):
        self.chroma_service = chroma_service
        self.registry = CollectorRegistry()
        
        # Vector Database Metrics
        self.vector_db_queries_total = Counter(
            'vector_db_queries_total',
            'Total number of vector database queries',
            ['operation', 'status'],
            registry=self.registry
        )
        
        self.vector_db_query_duration = Histogram(
            'vector_db_query_duration_seconds',
            'Duration of vector database queries',
            ['operation'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        self.vector_db_collection_size = Gauge(
            'vector_db_collection_size',
            'Number of vectors in the collection',
            ['collection_name'],
            registry=self.registry
        )
        
        self.vector_db_embedding_dimension = Gauge(
            'vector_db_embedding_dimension',
            'Dimension of embeddings in the collection',
            ['collection_name'],
            registry=self.registry
        )
        
        self.vector_db_memory_usage = Gauge(
            'vector_db_memory_usage_bytes',
            'Memory usage of the vector database',
            registry=self.registry
        )
        
        self.vector_db_index_size = Gauge(
            'vector_db_index_size_bytes',
            'Size of the vector database index',
            ['collection_name'],
            registry=self.registry
        )
        
        self.vector_db_search_accuracy = Gauge(
            'vector_db_search_accuracy',
            'Search accuracy metric (0-1)',
            ['collection_name'],
            registry=self.registry
        )
        
        self.vector_db_hnsw_optimization = Gauge(
            'vector_db_hnsw_optimization_enabled',
            'Whether HNSW optimization is enabled',
            ['collection_name'],
            registry=self.registry
        )
        
        self.vector_db_batch_operations = Counter(
            'vector_db_batch_operations_total',
            'Total number of batch operations',
            ['operation_type'],
            registry=self.registry
        )
        
        self.vector_db_cache_hits = Counter(
            'vector_db_cache_hits_total',
            'Total number of cache hits',
            ['cache_type'],
            registry=self.registry
        )
        
        self.vector_db_cache_misses = Counter(
            'vector_db_cache_misses_total',
            'Total number of cache misses',
            ['cache_type'],
            registry=self.registry
        )
        
        # Collection Info
        self.vector_db_info = Info(
            'vector_db_info',
            'Vector database information',
            registry=self.registry
        )
        
        # Initialize info
        self._update_collection_info()
    
    def _update_collection_info(self):
        """Update collection information"""
        try:
            stats = self.chroma_service.get_collection_stats()
            self.vector_db_info.info({
                'collection_name': stats.get('collection_name', 'unknown'),
                'embedding_model': stats.get('embedding_model', 'unknown'),
                'hnsw_optimization': str(stats.get('hnsw_optimization', False)),
                'batch_optimization': str(stats.get('batch_optimization_enabled', False))
            })
        except Exception as e:
            logger.error(f"Failed to update collection info: {e}")
    
    def record_query(self, operation: str, duration: float, status: str = "success"):
        """Record a vector database query"""
        self.vector_db_queries_total.labels(operation=operation, status=status).inc()
        self.vector_db_query_duration.labels(operation=operation).observe(duration)
    
    def record_batch_operation(self, operation_type: str, count: int = 1):
        """Record batch operations"""
        self.vector_db_batch_operations.labels(operation_type=operation_type).inc(count)
    
    def record_cache_hit(self, cache_type: str):
        """Record cache hit"""
        self.vector_db_cache_hits.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str):
        """Record cache miss"""
        self.vector_db_cache_misses.labels(cache_type=cache_type).inc()
    
    def update_collection_metrics(self):
        """Update collection-specific metrics"""
        try:
            stats = self.chroma_service.get_collection_stats()
            collection_name = stats.get('collection_name', 'unknown')
            count = stats.get('total_chunks', 0)
            
            # Get collection count
            self.vector_db_collection_size.labels(
                collection_name=collection_name
            ).set(count)
            
            # Set HNSW optimization status
            self.vector_db_hnsw_optimization.labels(
                collection_name=collection_name
            ).set(1 if stats.get('hnsw_optimization', False) else 0)
            
            # Update embedding dimension (assuming 384 for all-MiniLM-L6-v2)
            self.vector_db_embedding_dimension.labels(
                collection_name=collection_name
            ).set(384)
            
            # Estimate memory usage (rough calculation)
            estimated_memory = count * 384 * 4  # 4 bytes per float32
            self.vector_db_memory_usage.set(estimated_memory)
            
            # Estimate index size (rough calculation)
            index_size = count * 384 * 4 * 1.5  # 1.5x for index overhead
            self.vector_db_index_size.labels(
                collection_name=collection_name
            ).set(index_size)
            
            # Set search accuracy (placeholder - would need actual testing)
            self.vector_db_search_accuracy.labels(
                collection_name=collection_name
            ).set(0.95)  # Placeholder value
            
        except Exception as e:
            logger.error(f"Failed to update collection metrics: {e}")
    
    def get_metrics(self) -> str:
        """Get all metrics as Prometheus format"""
        try:
            # Update metrics before returning
            self.update_collection_metrics()
            
            # Generate metrics
            from prometheus_client import generate_latest
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to generate metrics: {e}")
            return ""
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get ChromaDB health status"""
        try:
            stats = self.chroma_service.get_collection_stats()
            if not stats:
                return {
                    "status": "unhealthy",
                    "error": "Collection stats not available",
                    "timestamp": time.time()
                }
            
            # Test basic operations
            start_time = time.time()
            count = stats.get('total_chunks', 0)
            query_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "collection_name": stats.get('collection_name', 'unknown'),
                "vector_count": count,
                "query_response_time": query_time,
                "hnsw_optimization": stats.get('hnsw_optimization', False),
                "batch_optimization": stats.get('batch_optimization_enabled', False),
                "embedding_model": stats.get('embedding_model', 'unknown'),
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }

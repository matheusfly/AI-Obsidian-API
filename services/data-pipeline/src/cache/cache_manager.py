#!/usr/bin/env python3
"""
Advanced Cache Manager for Query Embeddings and Search Results
Optimized for blazing-fast performance on high-end systems
"""

import hashlib
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    last_accessed: float = 0.0

class CacheManager:
    """Advanced cache manager for query embeddings and search results"""
    
    def __init__(self, 
                 query_embedding_ttl: int = 86400,  # 24 hours
                 search_result_ttl: int = 1800,     # 30 minutes
                 max_query_embeddings: int = 1000,
                 max_search_results: int = 5000):
        """
        Initialize the cache manager with optimized settings for high-end systems.
        
        Args:
            query_embedding_ttl: TTL for query embeddings in seconds (24 hours default)
            search_result_ttl: TTL for search results in seconds (30 minutes default)
            max_query_embeddings: Maximum number of query embeddings to cache
            max_search_results: Maximum number of search results to cache
        """
        self.query_embedding_ttl = query_embedding_ttl
        self.search_result_ttl = search_result_ttl
        self.max_query_embeddings = max_query_embeddings
        self.max_search_results = max_search_results
        
        # Separate caches for different data types
        self.query_embedding_cache: Dict[str, CacheEntry] = {}
        self.search_result_cache: Dict[str, CacheEntry] = {}
        
        # Statistics
        self.query_embedding_hits = 0
        self.query_embedding_misses = 0
        self.search_result_hits = 0
        self.search_result_misses = 0
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info(f"CacheManager initialized with query_embedding_ttl={query_embedding_ttl}s, search_result_ttl={search_result_ttl}s")
    
    def _generate_cache_key(self, query: str, prefix: str = "") -> str:
        """Generate a consistent cache key for a query"""
        cache_data = f"{prefix}:{query}"
        return hashlib.md5(cache_data.encode('utf-8')).hexdigest()
    
    def _is_cache_valid(self, entry: CacheEntry) -> bool:
        """Check if a cache entry is still valid"""
        current_time = time.time()
        return (current_time - entry.timestamp) < entry.ttl
    
    def _cleanup_expired_entries(self, cache: Dict[str, CacheEntry], max_entries: int):
        """Clean up expired entries and enforce size limits"""
        current_time = time.time()
        
        # Remove expired entries
        expired_keys = [
            key for key, entry in cache.items()
            if (current_time - entry.timestamp) >= entry.ttl
        ]
        
        for key in expired_keys:
            del cache[key]
            logger.debug(f"Removed expired cache entry: {key}")
        
        # If still over limit, remove least recently accessed entries
        if len(cache) > max_entries:
            sorted_entries = sorted(
                cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
            entries_to_remove = len(cache) - max_entries
            for key, _ in sorted_entries[:entries_to_remove]:
                del cache[key]
                logger.debug(f"Removed LRU cache entry: {key}")
    
    def cache_query_embedding(self, query: str, embedding: List[float], ttl: Optional[int] = None) -> None:
        """
        Cache a query embedding for blazing-fast performance.
        
        Args:
            query: The search query
            embedding: The generated embedding vector
            ttl: Optional TTL override (uses default if None)
        """
        with self._lock:
            cache_key = self._generate_cache_key(query, "query_embedding")
            ttl = ttl or self.query_embedding_ttl
            
            self.query_embedding_cache[cache_key] = CacheEntry(
                data=embedding,
                timestamp=time.time(),
                ttl=ttl,
                access_count=0,
                last_accessed=time.time()
            )
            
            # Cleanup if needed
            self._cleanup_expired_entries(self.query_embedding_cache, self.max_query_embeddings)
            
            logger.debug(f"Cached query embedding for: {query[:50]}...")
    
    def get_cached_query_embedding(self, query: str) -> Optional[List[float]]:
        """
        Get a cached query embedding if available and valid.
        
        Args:
            query: The search query
            
        Returns:
            Cached embedding if available and valid, None otherwise
        """
        with self._lock:
            cache_key = self._generate_cache_key(query, "query_embedding")
            cached_entry = self.query_embedding_cache.get(cache_key)
            
            if cached_entry and self._is_cache_valid(cached_entry):
                # Update access statistics
                cached_entry.access_count += 1
                cached_entry.last_accessed = time.time()
                self.query_embedding_hits += 1
                
                logger.debug(f"Cache hit for query embedding: {query[:50]}...")
                return cached_entry.data
            else:
                self.query_embedding_misses += 1
                if cached_entry:
                    logger.debug(f"Cache miss (expired) for query embedding: {query[:50]}...")
                else:
                    logger.debug(f"Cache miss (not found) for query embedding: {query[:50]}...")
                return None
    
    def cache_search_result(self, query: str, filters: Optional[Dict[str, Any]], 
                           n_results: int, results: List[Dict[str, Any]], 
                           ttl: Optional[int] = None) -> None:
        """
        Cache search results for performance optimization.
        
        Args:
            query: The search query
            filters: Optional metadata filters
            n_results: Number of results
            results: The search results to cache
            ttl: Optional TTL override (uses default if None)
        """
        with self._lock:
            cache_key = self._generate_cache_key(f"{query}:{filters}:{n_results}", "search_result")
            ttl = ttl or self.search_result_ttl
            
            self.search_result_cache[cache_key] = CacheEntry(
                data=results,
                timestamp=time.time(),
                ttl=ttl,
                access_count=0,
                last_accessed=time.time()
            )
            
            # Cleanup if needed
            self._cleanup_expired_entries(self.search_result_cache, self.max_search_results)
            
            logger.debug(f"Cached search results for: {query[:50]}...")
    
    def get_cached_search_result(self, query: str, filters: Optional[Dict[str, Any]], 
                                n_results: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached search results if available and valid.
        
        Args:
            query: The search query
            filters: Optional metadata filters
            n_results: Number of results
            
        Returns:
            Cached results if available and valid, None otherwise
        """
        with self._lock:
            cache_key = self._generate_cache_key(f"{query}:{filters}:{n_results}", "search_result")
            cached_entry = self.search_result_cache.get(cache_key)
            
            if cached_entry and self._is_cache_valid(cached_entry):
                # Update access statistics
                cached_entry.access_count += 1
                cached_entry.last_accessed = time.time()
                self.search_result_hits += 1
                
                logger.debug(f"Cache hit for search results: {query[:50]}...")
                return cached_entry.data
            else:
                self.search_result_misses += 1
                if cached_entry:
                    logger.debug(f"Cache miss (expired) for search results: {query[:50]}...")
                else:
                    logger.debug(f"Cache miss (not found) for search results: {query[:50]}...")
                return None
    
    def precompute_common_queries(self, common_queries: List[str], embedding_service) -> None:
        """
        Pre-compute embeddings for common queries to achieve blazing-fast performance.
        
        Args:
            common_queries: List of frequently asked questions
            embedding_service: The embedding service to use
        """
        logger.info(f"Pre-computing embeddings for {len(common_queries)} common queries...")
        
        for query in common_queries:
            # Check if already cached
            if self.get_cached_query_embedding(query) is None:
                try:
                    # Generate embedding
                    embedding = embedding_service.generate_embedding(query)
                    
                    # Cache it
                    self.cache_query_embedding(query, embedding)
                    
                    logger.debug(f"Pre-computed embedding for: {query}")
                except Exception as e:
                    logger.error(f"Failed to pre-compute embedding for '{query}': {e}")
        
        logger.info(f"Pre-computation complete. Cached {len(self.query_embedding_cache)} query embeddings.")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self._lock:
            total_query_requests = self.query_embedding_hits + self.query_embedding_misses
            total_search_requests = self.search_result_hits + self.search_result_misses
            
            query_hit_rate = (self.query_embedding_hits / total_query_requests * 100) if total_query_requests > 0 else 0
            search_hit_rate = (self.search_result_hits / total_search_requests * 100) if total_search_requests > 0 else 0
            
            return {
                "query_embedding_cache": {
                    "size": len(self.query_embedding_cache),
                    "hits": self.query_embedding_hits,
                    "misses": self.query_embedding_misses,
                    "hit_rate": f"{query_hit_rate:.2f}%",
                    "max_size": self.max_query_embeddings
                },
                "search_result_cache": {
                    "size": len(self.search_result_cache),
                    "hits": self.search_result_hits,
                    "misses": self.search_result_misses,
                    "hit_rate": f"{search_hit_rate:.2f}%",
                    "max_size": self.max_search_results
                },
                "total_requests": {
                    "query_embeddings": total_query_requests,
                    "search_results": total_search_requests
                }
            }
    
    def clear_query_embedding_cache(self) -> None:
        """Clear the query embedding cache"""
        with self._lock:
            self.query_embedding_cache.clear()
            self.query_embedding_hits = 0
            self.query_embedding_misses = 0
            logger.info("Query embedding cache cleared")
    
    def clear_search_result_cache(self) -> None:
        """Clear the search result cache"""
        with self._lock:
            self.search_result_cache.clear()
            self.search_result_hits = 0
            self.search_result_misses = 0
            logger.info("Search result cache cleared")
    
    def clear_all_caches(self) -> None:
        """Clear all caches"""
        with self._lock:
            self.clear_query_embedding_cache()
            self.clear_search_result_cache()
            logger.info("All caches cleared")
    
    def warm_up_cache(self, common_queries: List[str], embedding_service) -> None:
        """
        Warm up the cache with common queries for optimal performance.
        
        Args:
            common_queries: List of frequently asked questions
            embedding_service: The embedding service to use
        """
        logger.info("Warming up cache for optimal performance...")
        
        # Pre-compute common query embeddings
        self.precompute_common_queries(common_queries, embedding_service)
        
        logger.info("Cache warm-up complete!")

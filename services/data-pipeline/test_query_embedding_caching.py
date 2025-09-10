#!/usr/bin/env python3
"""
Test script for query embedding caching performance improvements
Demonstrates blazing-fast performance with cached query embeddings
"""
import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService
from src.search.search_service import SemanticSearchService
from src.cache.cache_manager import CacheManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QueryEmbeddingCachingTester:
    """Test class for query embedding caching performance"""
    
    def __init__(self):
        self.chroma_service = None
        self.embedding_service = None
        self.search_service = None
        self.cache_manager = None
    
    async def setup(self):
        """Initialize services with caching enabled"""
        try:
            logger.info("Setting up services with query embedding caching...")
            
            # Initialize ChromaDB service
            self.chroma_service = ChromaService()
            
            # Initialize embedding service
            self.embedding_service = EmbeddingService()
            
            # Initialize cache manager with optimized settings
            self.cache_manager = CacheManager(
                query_embedding_ttl=86400,  # 24 hours
                search_result_ttl=1800,     # 30 minutes
                max_query_embeddings=1000,
                max_search_results=5000
            )
            
            # Initialize search service with cache manager
            self.search_service = SemanticSearchService(
                chroma_service=self.chroma_service,
                embedding_service=self.embedding_service,
                cache_manager=self.cache_manager
            )
            
            logger.info("Services initialized successfully with query embedding caching")
            
        except Exception as e:
            logger.error(f"Error setting up services: {e}")
            raise
    
    async def test_query_embedding_caching_performance(self):
        """Test the performance improvement from query embedding caching"""
        logger.info("=" * 80)
        logger.info("TEST 1: QUERY EMBEDDING CACHING PERFORMANCE")
        logger.info("=" * 80)
        
        # Common queries that would benefit from caching
        common_queries = [
            "Python programming language",
            "machine learning algorithms",
            "data analysis techniques",
            "artificial intelligence overview",
            "database optimization methods",
            "API development best practices",
            "cloud computing services",
            "software architecture patterns",
            "debugging techniques",
            "performance testing strategies"
        ]
        
        # Test queries (mix of common and new)
        test_queries = common_queries + [
            "web development frameworks",
            "mobile app development",
            "cybersecurity best practices",
            "DevOps methodologies"
        ]
        
        logger.info(f"Testing with {len(test_queries)} queries (including {len(common_queries)} common queries)")
        
        # Phase 1: Pre-compute common queries
        logger.info("\n--- Phase 1: Pre-computing Common Queries ---")
        start_time = time.time()
        self.search_service.precompute_common_queries(common_queries)
        precompute_time = time.time() - start_time
        logger.info(f"Pre-computation completed in {precompute_time:.3f}s")
        
        # Phase 2: Test performance with cached vs non-cached queries
        logger.info("\n--- Phase 2: Performance Testing ---")
        
        cached_times = []
        non_cached_times = []
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"\nTesting query {i}/{len(test_queries)}: '{query}'")
            
            # Test with caching (should be fast for common queries)
            start_time = time.time()
            results_cached = await self.search_service.search_similar(
                query=query,
                n_results=3,
                expand_query=False  # Disable query expansion to focus on embedding caching
            )
            cached_time = time.time() - start_time
            cached_times.append(cached_time)
            
            logger.info(f"  Cached search: {cached_time:.3f}s, {len(results_cached)} results")
            
            # Test without caching (clear cache to force regeneration)
            self.cache_manager.clear_query_embedding_cache()
            start_time = time.time()
            results_non_cached = await self.search_service.search_similar(
                query=query,
                n_results=3,
                expand_query=False
            )
            non_cached_time = time.time() - start_time
            non_cached_times.append(non_cached_time)
            
            logger.info(f"  Non-cached search: {non_cached_time:.3f}s, {len(results_non_cached)} results")
            
            # Calculate performance improvement
            if non_cached_time > 0:
                improvement = ((non_cached_time - cached_time) / non_cached_time) * 100
                logger.info(f"  Performance improvement: {improvement:.1f}%")
        
        # Phase 3: Analyze results
        logger.info("\n--- Phase 3: Performance Analysis ---")
        
        avg_cached_time = sum(cached_times) / len(cached_times)
        avg_non_cached_time = sum(non_cached_times) / len(non_cached_times)
        overall_improvement = ((avg_non_cached_time - avg_cached_time) / avg_non_cached_time) * 100
        
        logger.info(f"Average cached search time: {avg_cached_time:.3f}s")
        logger.info(f"Average non-cached search time: {avg_non_cached_time:.3f}s")
        logger.info(f"Overall performance improvement: {overall_improvement:.1f}%")
        
        # Cache statistics
        cache_stats = self.search_service.get_cache_performance_stats()
        logger.info(f"Query embedding cache hit rate: {cache_stats['query_embedding_cache']['hit_rate']}")
        logger.info(f"Query embedding cache size: {cache_stats['query_embedding_cache']['size']}")
        
        return {
            "avg_cached_time": avg_cached_time,
            "avg_non_cached_time": avg_non_cached_time,
            "overall_improvement": overall_improvement,
            "cache_stats": cache_stats
        }
    
    async def test_cache_warm_up_performance(self):
        """Test cache warm-up performance"""
        logger.info("=" * 80)
        logger.info("TEST 2: CACHE WARM-UP PERFORMANCE")
        logger.info("=" * 80)
        
        # Clear all caches first
        self.search_service.clear_all_caches()
        
        # Define warm-up queries
        warm_up_queries = [
            "Python programming",
            "machine learning",
            "data science",
            "web development",
            "cloud computing",
            "artificial intelligence",
            "database design",
            "API development",
            "software testing",
            "DevOps practices"
        ]
        
        logger.info(f"Warming up cache with {len(warm_up_queries)} queries...")
        
        # Test warm-up performance
        start_time = time.time()
        self.search_service.warm_up_cache(warm_up_queries)
        warm_up_time = time.time() - start_time
        
        logger.info(f"Cache warm-up completed in {warm_up_time:.3f}s")
        
        # Test subsequent searches (should be blazing fast)
        test_queries = warm_up_queries[:5]  # Test first 5 queries
        
        logger.info(f"Testing subsequent searches with {len(test_queries)} queries...")
        
        search_times = []
        for query in test_queries:
            start_time = time.time()
            results = await self.search_service.search_similar(
                query=query,
                n_results=3,
                expand_query=False
            )
            search_time = time.time() - start_time
            search_times.append(search_time)
            logger.info(f"  '{query}': {search_time:.3f}s, {len(results)} results")
        
        avg_search_time = sum(search_times) / len(search_times)
        logger.info(f"Average search time after warm-up: {avg_search_time:.3f}s")
        
        return {
            "warm_up_time": warm_up_time,
            "avg_search_time": avg_search_time,
            "search_times": search_times
        }
    
    async def test_cache_efficiency(self):
        """Test cache efficiency and memory usage"""
        logger.info("=" * 80)
        logger.info("TEST 3: CACHE EFFICIENCY AND MEMORY USAGE")
        logger.info("=" * 80)
        
        # Test with many queries to see cache behavior
        test_queries = [
            f"query_{i}" for i in range(50)
        ]
        
        logger.info(f"Testing cache efficiency with {len(test_queries)} unique queries...")
        
        # First pass - all cache misses
        start_time = time.time()
        for query in test_queries:
            await self.search_service.search_similar(
                query=query,
                n_results=2,
                expand_query=False
            )
        first_pass_time = time.time() - start_time
        
        # Second pass - all cache hits
        start_time = time.time()
        for query in test_queries:
            await self.search_service.search_similar(
                query=query,
                n_results=2,
                expand_query=False
            )
        second_pass_time = time.time() - start_time
        
        # Third pass - mix of hits and misses (repeat first 25 queries)
        mixed_queries = test_queries[:25] + [f"new_query_{i}" for i in range(25)]
        start_time = time.time()
        for query in mixed_queries:
            await self.search_service.search_similar(
                query=query,
                n_results=2,
                expand_query=False
            )
        third_pass_time = time.time() - start_time
        
        # Get final cache statistics
        cache_stats = self.search_service.get_cache_performance_stats()
        
        logger.info(f"First pass (all misses): {first_pass_time:.3f}s")
        logger.info(f"Second pass (all hits): {second_pass_time:.3f}s")
        logger.info(f"Third pass (mixed): {third_pass_time:.3f}s")
        logger.info(f"Cache hit rate: {cache_stats['query_embedding_cache']['hit_rate']}")
        logger.info(f"Cache size: {cache_stats['query_embedding_cache']['size']}")
        
        # Calculate efficiency metrics
        hit_efficiency = (first_pass_time - second_pass_time) / first_pass_time * 100
        logger.info(f"Cache hit efficiency: {hit_efficiency:.1f}%")
        
        return {
            "first_pass_time": first_pass_time,
            "second_pass_time": second_pass_time,
            "third_pass_time": third_pass_time,
            "hit_efficiency": hit_efficiency,
            "cache_stats": cache_stats
        }
    
    async def run_all_tests(self):
        """Run all query embedding caching tests"""
        try:
            await self.setup()
            
            # Run performance tests
            perf_results = await self.test_query_embedding_caching_performance()
            warm_up_results = await self.test_cache_warm_up_performance()
            efficiency_results = await self.test_cache_efficiency()
            
            # Summary
            logger.info("=" * 80)
            logger.info("QUERY EMBEDDING CACHING TEST SUMMARY")
            logger.info("=" * 80)
            
            logger.info(f"Performance Improvement: {perf_results['overall_improvement']:.1f}%")
            logger.info(f"Average Cached Time: {perf_results['avg_cached_time']:.3f}s")
            logger.info(f"Average Non-Cached Time: {perf_results['avg_non_cached_time']:.3f}s")
            logger.info(f"Cache Hit Rate: {perf_results['cache_stats']['query_embedding_cache']['hit_rate']}")
            logger.info(f"Warm-up Time: {warm_up_results['warm_up_time']:.3f}s")
            logger.info(f"Post-Warm-up Search Time: {warm_up_results['avg_search_time']:.3f}s")
            logger.info(f"Cache Hit Efficiency: {efficiency_results['hit_efficiency']:.1f}%")
            
            logger.info("\n✅ All query embedding caching tests completed successfully!")
            
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            raise

async def main():
    """Main test function"""
    tester = QueryEmbeddingCachingTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

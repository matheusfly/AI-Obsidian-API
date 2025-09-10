#!/usr/bin/env python3
"""
FIXED Test script for query embedding caching performance improvements
Properly isolates query embedding caching from search result caching
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

class FixedQueryEmbeddingCachingTester:
    """FIXED Test class for query embedding caching performance"""
    
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
    
    async def test_embedding_generation_performance(self):
        """Test embedding generation performance with and without caching"""
        logger.info("=" * 80)
        logger.info("TEST 1: EMBEDDING GENERATION PERFORMANCE (FIXED)")
        logger.info("=" * 80)
        
        # Clear ALL caches to start fresh
        self.search_service.clear_all_caches()
        
        test_queries = [
            "Python programming language",
            "machine learning algorithms", 
            "data analysis techniques",
            "artificial intelligence overview",
            "database optimization methods"
        ]
        
        logger.info(f"Testing embedding generation with {len(test_queries)} queries")
        
        # Phase 1: Test embedding generation WITHOUT caching
        logger.info("\n--- Phase 1: Embedding Generation WITHOUT Caching ---")
        no_cache_times = []
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"Testing query {i}/{len(test_queries)}: '{query}'")
            
            # Clear embedding cache to force regeneration
            self.cache_manager.clear_query_embedding_cache()
            
            # Measure embedding generation time
            start_time = time.time()
            embedding = self.embedding_service.generate_embedding(query)
            embedding_time = time.time() - start_time
            no_cache_times.append(embedding_time)
            
            logger.info(f"  Embedding generation time: {embedding_time:.3f}s")
        
        # Phase 2: Pre-populate embedding cache
        logger.info("\n--- Phase 2: Pre-populating Embedding Cache ---")
        start_time = time.time()
        self.search_service.precompute_common_queries(test_queries)
        precompute_time = time.time() - start_time
        logger.info(f"Pre-computation completed in {precompute_time:.3f}s")
        
        # Phase 3: Test embedding retrieval WITH caching
        logger.info("\n--- Phase 3: Embedding Retrieval WITH Caching ---")
        cached_times = []
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"Testing query {i}/{len(test_queries)}: '{query}'")
            
            # Measure embedding retrieval time (should be from cache)
            start_time = time.time()
            cached_embedding = self.cache_manager.get_cached_query_embedding(query)
            retrieval_time = time.time() - start_time
            cached_times.append(retrieval_time)
            
            logger.info(f"  Embedding retrieval time: {retrieval_time:.3f}s")
            
            # Verify we got a cached embedding
            if cached_embedding is not None:
                logger.info(f"  ✅ Cache hit - embedding retrieved from cache")
            else:
                logger.warning(f"  ❌ Cache miss - embedding not found in cache")
        
        # Phase 4: Analyze results
        logger.info("\n--- Phase 4: Performance Analysis ---")
        
        avg_no_cache_time = sum(no_cache_times) / len(no_cache_times)
        avg_cached_time = sum(cached_times) / len(cached_times)
        
        # Calculate improvement (cached should be much faster)
        if avg_no_cache_time > 0:
            improvement = ((avg_no_cache_time - avg_cached_time) / avg_no_cache_time) * 100
        else:
            improvement = 0
        
        logger.info(f"Average embedding generation time (no cache): {avg_no_cache_time:.3f}s")
        logger.info(f"Average embedding retrieval time (cached): {avg_cached_time:.3f}s")
        logger.info(f"Performance improvement: {improvement:.1f}%")
        
        # Verify cache statistics
        cache_stats = self.cache_manager.get_cache_stats()
        logger.info(f"Query embedding cache size: {cache_stats['query_embedding_cache']['size']}")
        logger.info(f"Query embedding cache hit rate: {cache_stats['query_embedding_cache']['hit_rate']}")
        
        return {
            "avg_no_cache_time": avg_no_cache_time,
            "avg_cached_time": avg_cached_time,
            "improvement": improvement,
            "cache_stats": cache_stats
        }
    
    async def test_full_search_performance(self):
        """Test full search performance with proper cache isolation"""
        logger.info("=" * 80)
        logger.info("TEST 2: FULL SEARCH PERFORMANCE (FIXED)")
        logger.info("=" * 80)
        
        test_queries = [
            "Python programming",
            "machine learning",
            "data science",
            "web development",
            "cloud computing"
        ]
        
        logger.info(f"Testing full search performance with {len(test_queries)} queries")
        
        # Phase 1: Search WITHOUT any caching
        logger.info("\n--- Phase 1: Search WITHOUT Caching ---")
        self.search_service.clear_all_caches()
        
        no_cache_times = []
        for i, query in enumerate(test_queries, 1):
            logger.info(f"Testing query {i}/{len(test_queries)}: '{query}'")
            
            start_time = time.time()
            results = await self.search_service.search_similar(
                query=query,
                n_results=3,
                expand_query=False,
                use_cache=False  # Disable all caching
            )
            search_time = time.time() - start_time
            no_cache_times.append(search_time)
            
            logger.info(f"  Search time: {search_time:.3f}s, {len(results)} results")
        
        # Phase 2: Pre-populate caches
        logger.info("\n--- Phase 2: Pre-populating Caches ---")
        self.search_service.warm_up_cache(test_queries)
        
        # Phase 3: Search WITH caching
        logger.info("\n--- Phase 3: Search WITH Caching ---")
        cached_times = []
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"Testing query {i}/{len(test_queries)}: '{query}'")
            
            start_time = time.time()
            results = await self.search_service.search_similar(
                query=query,
                n_results=3,
                expand_query=False,
                use_cache=True  # Enable all caching
            )
            search_time = time.time() - start_time
            cached_times.append(search_time)
            
            logger.info(f"  Search time: {search_time:.3f}s, {len(results)} results")
        
        # Phase 4: Analyze results
        logger.info("\n--- Phase 4: Performance Analysis ---")
        
        avg_no_cache_time = sum(no_cache_times) / len(no_cache_times)
        avg_cached_time = sum(cached_times) / len(cached_times)
        
        if avg_no_cache_time > 0:
            improvement = ((avg_no_cache_time - avg_cached_time) / avg_no_cache_time) * 100
        else:
            improvement = 0
        
        logger.info(f"Average search time (no cache): {avg_no_cache_time:.3f}s")
        logger.info(f"Average search time (cached): {avg_cached_time:.3f}s")
        logger.info(f"Performance improvement: {improvement:.1f}%")
        
        # Get final cache statistics
        cache_stats = self.search_service.get_cache_performance_stats()
        logger.info(f"Query embedding cache hit rate: {cache_stats['query_embedding_cache']['hit_rate']}")
        logger.info(f"Search result cache hit rate: {cache_stats['search_result_cache']['hit_rate']}")
        
        return {
            "avg_no_cache_time": avg_no_cache_time,
            "avg_cached_time": avg_cached_time,
            "improvement": improvement,
            "cache_stats": cache_stats
        }
    
    async def run_all_tests(self):
        """Run all fixed query embedding caching tests"""
        try:
            await self.setup()
            
            # Run fixed performance tests
            embedding_results = await self.test_embedding_generation_performance()
            search_results = await self.test_full_search_performance()
            
            # Summary
            logger.info("=" * 80)
            logger.info("FIXED QUERY EMBEDDING CACHING TEST SUMMARY")
            logger.info("=" * 80)
            
            logger.info(f"Embedding Generation Improvement: {embedding_results['improvement']:.1f}%")
            logger.info(f"Full Search Improvement: {search_results['improvement']:.1f}%")
            logger.info(f"Embedding Cache Hit Rate: {embedding_results['cache_stats']['query_embedding_cache']['hit_rate']}")
            logger.info(f"Search Cache Hit Rate: {search_results['cache_stats']['search_result_cache']['hit_rate']}")
            
            logger.info("\n✅ All FIXED query embedding caching tests completed successfully!")
            
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            raise

async def main():
    """Main test function"""
    tester = FixedQueryEmbeddingCachingTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

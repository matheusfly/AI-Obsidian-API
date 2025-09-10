#!/usr/bin/env python3
"""
Comprehensive Test for Advanced Hybrid Search System
Demonstrates all hybrid search capabilities beyond basic requirements
"""

import asyncio
import logging
from typing import List, Dict, Any
import time

# Import our services
from src.search.search_service import SemanticSearchService
from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridSearchTester:
    """Comprehensive tester for hybrid search capabilities"""
    
    def __init__(self):
        """Initialize the hybrid search tester"""
        self.chroma_service = ChromaService(
            collection_name="obsidian_vault",
            optimize_for_large_vault=True
        )
        self.embedding_service = EmbeddingService()
        self.search_service = SemanticSearchService(
            chroma_service=self.chroma_service,
            embedding_service=self.embedding_service
        )
        
        logger.info("🔍 Initialized Comprehensive Hybrid Search Tester")

    async def test_basic_semantic_search(self):
        """Test basic semantic search functionality"""
        logger.info("\n📊 Testing Basic Semantic Search")
        logger.info("=" * 50)
        
        test_queries = [
            "artificial intelligence machine learning",
            "project management productivity",
            "data analysis visualization",
            "software development programming"
        ]
        
        for query in test_queries:
            start_time = time.time()
            results = self.search_service.search_similar(query, n_results=3)
            search_time = time.time() - start_time
            
            logger.info(f"Query: '{query}'")
            logger.info(f"  Results: {len(results)}")
            logger.info(f"  Search time: {search_time:.3f}s")
            
            if results:
                best_result = results[0]
                logger.info(f"  Best similarity: {best_result.get('similarity', 0):.3f}")
                logger.info(f"  Best content preview: {best_result.get('content', '')[:100]}...")
            
            logger.info("")

    async def test_keyword_filtering(self):
        """Test keyword filtering with where_document parameter"""
        logger.info("\n🔍 Testing Keyword Filtering (where_document)")
        logger.info("=" * 50)
        
        # Test semantic search with keyword filtering
        test_cases = [
            {
                "query": "machine learning",
                "keyword_filter": "Python",
                "description": "ML content containing 'Python'"
            },
            {
                "query": "data analysis",
                "keyword_filter": "visualization",
                "description": "Data analysis content containing 'visualization'"
            },
            {
                "query": "project management",
                "keyword_filter": "agile",
                "description": "Project management content containing 'agile'"
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"Test: {test_case['description']}")
            
            # Semantic search with keyword filter
            start_time = time.time()
            results = self.search_service.search_similar(
                query=test_case["query"],
                n_results=5,
                where_document={"$contains": test_case["keyword_filter"]}
            )
            search_time = time.time() - start_time
            
            logger.info(f"  Query: '{test_case['query']}' + keyword: '{test_case['keyword_filter']}'")
            logger.info(f"  Results: {len(results)}")
            logger.info(f"  Search time: {search_time:.3f}s")
            
            if results:
                for i, result in enumerate(results[:2]):
                    logger.info(f"    Result {i+1}: similarity={result.get('similarity', 0):.3f}")
                    logger.info(f"    Content preview: {result.get('content', '')[:80]}...")
            
            logger.info("")

    async def test_metadata_filtering(self):
        """Test metadata filtering capabilities"""
        logger.info("\n📋 Testing Metadata Filtering")
        logger.info("=" * 50)
        
        # Test various metadata filters
        metadata_tests = [
            {
                "filter": {"file_type": "dated_note"},
                "description": "Files from dated notes"
            },
            {
                "filter": {"path_year": 2025},
                "description": "Files from 2025"
            },
            {
                "filter": {"path_category": "Projects"},
                "description": "Files in Projects category"
            },
            {
                "filter": {"chunk_token_count": {"$gt": 200}},
                "description": "Large chunks (>200 tokens)"
            }
        ]
        
        for test in metadata_tests:
            logger.info(f"Test: {test['description']}")
            
            start_time = time.time()
            results = self.search_service.search_similar(
                query="technology development",
                n_results=3,
                where=test["filter"]
            )
            search_time = time.time() - start_time
            
            logger.info(f"  Filter: {test['filter']}")
            logger.info(f"  Results: {len(results)}")
            logger.info(f"  Search time: {search_time:.3f}s")
            
            if results:
                for i, result in enumerate(results[:2]):
                    metadata = result.get('metadata', {})
                    logger.info(f"    Result {i+1}: {metadata.get('file_name', 'N/A')}")
                    logger.info(f"    Similarity: {result.get('similarity', 0):.3f}")
            
            logger.info("")

    async def test_keyword_search(self):
        """Test dedicated keyword search functionality"""
        logger.info("\n🔤 Testing Keyword Search")
        logger.info("=" * 50)
        
        keyword_tests = [
            {
                "keywords": ["Python", "programming"],
                "description": "Python programming content"
            },
            {
                "keywords": ["machine", "learning", "AI"],
                "description": "Machine learning AI content"
            },
            {
                "keywords": ["data", "analysis", "visualization"],
                "description": "Data analysis visualization"
            }
        ]
        
        for test in keyword_tests:
            logger.info(f"Test: {test['description']}")
            
            start_time = time.time()
            results = self.search_service.search_by_keywords(
                keywords=test["keywords"],
                n_results=3
            )
            search_time = time.time() - start_time
            
            logger.info(f"  Keywords: {test['keywords']}")
            logger.info(f"  Results: {len(results)}")
            logger.info(f"  Search time: {search_time:.3f}s")
            
            if results:
                for i, result in enumerate(results[:2]):
                    keyword_score = result.get('keyword_score', 0)
                    logger.info(f"    Result {i+1}: keyword_score={keyword_score:.3f}")
                    logger.info(f"    Content preview: {result.get('content', '')[:80]}...")
            
            logger.info("")

    async def test_tag_search(self):
        """Test tag-based search functionality"""
        logger.info("\n🏷️ Testing Tag Search")
        logger.info("=" * 50)
        
        tag_tests = [
            {
                "tags": ["#python", "#programming"],
                "description": "Python programming tags"
            },
            {
                "tags": ["#ai", "#machine-learning"],
                "description": "AI and ML tags"
            },
            {
                "tags": ["#project", "#management"],
                "description": "Project management tags"
            }
        ]
        
        for test in tag_tests:
            logger.info(f"Test: {test['description']}")
            
            start_time = time.time()
            results = self.search_service.search_by_tags(
                tags=test["tags"],
                n_results=3
            )
            search_time = time.time() - start_time
            
            logger.info(f"  Tags: {test['tags']}")
            logger.info(f"  Results: {len(results)}")
            logger.info(f"  Search time: {search_time:.3f}s")
            
            if results:
                for i, result in enumerate(results[:2]):
                    logger.info(f"    Result {i+1}: {result.get('metadata', {}).get('file_name', 'N/A')}")
                    logger.info(f"    Search type: {result.get('search_type', 'N/A')}")
            
            logger.info("")

    async def test_comprehensive_hybrid_search(self):
        """Test the comprehensive hybrid search method"""
        logger.info("\n🚀 Testing Comprehensive Hybrid Search")
        logger.info("=" * 50)
        
        hybrid_tests = [
            {
                "query": "machine learning Python programming",
                "description": "ML + Python programming"
            },
            {
                "query": "data analysis visualization charts",
                "description": "Data analysis with visualization"
            },
            {
                "query": "project management agile methodology",
                "description": "Project management with agile"
            }
        ]
        
        for test in hybrid_tests:
            logger.info(f"Test: {test['description']}")
            
            start_time = time.time()
            results = self.search_service.hybrid_search(
                query=test["query"],
                n_results=5,
                include_keywords=True,
                include_tags=True
            )
            search_time = time.time() - start_time
            
            logger.info(f"  Query: '{test['query']}'")
            logger.info(f"  Results: {len(results)}")
            logger.info(f"  Search time: {search_time:.3f}s")
            
            if results:
                # Group results by search type
                search_types = {}
                for result in results:
                    search_type = result.get('search_type', 'unknown')
                    if search_type not in search_types:
                        search_types[search_type] = []
                    search_types[search_type].append(result)
                
                logger.info(f"  Search type breakdown:")
                for search_type, type_results in search_types.items():
                    logger.info(f"    {search_type}: {len(type_results)} results")
                
                # Show top results
                logger.info(f"  Top results:")
                for i, result in enumerate(results[:3]):
                    combined_score = result.get('combined_score', 0)
                    search_type = result.get('search_type', 'unknown')
                    logger.info(f"    {i+1}. {search_type} (score: {combined_score:.3f})")
                    logger.info(f"       {result.get('content', '')[:80]}...")
            
            logger.info("")

    async def test_search_performance(self):
        """Test search performance and caching"""
        logger.info("\n⚡ Testing Search Performance & Caching")
        logger.info("=" * 50)
        
        # Test caching performance
        test_query = "machine learning artificial intelligence"
        
        # First search (cache miss)
        start_time = time.time()
        results1 = self.search_service.search_similar(test_query, n_results=5, use_cache=True)
        time1 = time.time() - start_time
        
        # Second search (cache hit)
        start_time = time.time()
        results2 = self.search_service.search_similar(test_query, n_results=5, use_cache=True)
        time2 = time.time() - start_time
        
        # Get search stats
        stats = self.search_service.get_search_stats()
        
        logger.info(f"Query: '{test_query}'")
        logger.info(f"First search (cache miss): {time1:.3f}s")
        logger.info(f"Second search (cache hit): {time2:.3f}s")
        logger.info(f"Speed improvement: {time1/time2:.1f}x faster")
        logger.info(f"Cache stats: {stats}")
        
        # Test different search methods performance
        search_methods = [
            ("Semantic", lambda: self.search_service.search_similar(test_query, n_results=5)),
            ("Keyword", lambda: self.search_service.search_by_keywords(["machine", "learning"], n_results=5)),
            ("Hybrid", lambda: self.search_service.hybrid_search(test_query, n_results=5))
        ]
        
        logger.info(f"\nSearch method performance comparison:")
        for method_name, method_func in search_methods:
            start_time = time.time()
            try:
                method_func()
                method_time = time.time() - start_time
                logger.info(f"  {method_name}: {method_time:.3f}s")
            except Exception as e:
                logger.info(f"  {method_name}: Error - {e}")

    async def test_advanced_features(self):
        """Test advanced hybrid search features"""
        logger.info("\n🎯 Testing Advanced Features")
        logger.info("=" * 50)
        
        # Test query relevance scoring
        test_query = "Python machine learning"
        results = self.search_service.search_similar(test_query, n_results=3)
        
        logger.info(f"Query relevance scoring for: '{test_query}'")
        for i, result in enumerate(results):
            relevance = result.get('query_relevance', 0)
            preview = result.get('preview', '')
            logger.info(f"  Result {i+1}: relevance={relevance:.3f}")
            logger.info(f"    Preview: {preview}")
        
        # Test content preview generation
        logger.info(f"\nContent preview generation:")
        for i, result in enumerate(results[:2]):
            preview = result.get('preview', '')
            logger.info(f"  Result {i+1} preview: {preview}")
        
        # Test search metadata
        logger.info(f"\nSearch metadata:")
        for i, result in enumerate(results[:2]):
            search_timestamp = result.get('search_timestamp', 'N/A')
            search_type = result.get('search_type', 'N/A')
            logger.info(f"  Result {i+1}: type={search_type}, timestamp={search_timestamp}")

    async def run_comprehensive_test(self):
        """Run all hybrid search tests"""
        logger.info("🚀 Starting Comprehensive Hybrid Search Test Suite")
        logger.info("=" * 80)
        
        try:
            await self.test_basic_semantic_search()
            await self.test_keyword_filtering()
            await self.test_metadata_filtering()
            await self.test_keyword_search()
            await self.test_tag_search()
            await self.test_comprehensive_hybrid_search()
            await self.test_search_performance()
            await self.test_advanced_features()
            
            logger.info("\n🎉 All hybrid search tests completed successfully!")
            logger.info("=" * 80)
            
            # Final summary
            stats = self.search_service.get_search_stats()
            logger.info(f"Final search statistics: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Run comprehensive hybrid search tests"""
    tester = HybridSearchTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())

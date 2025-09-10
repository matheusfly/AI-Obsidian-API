#!/usr/bin/env python3
"""
Test Enhanced Search Features
Demonstrates advanced hybrid search capabilities beyond basic requirements
"""

import asyncio
import logging
from typing import List, Dict, Any

# Import our enhanced services
from src.search.enhanced_search_service import EnhancedSearchService
from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedSearchTester:
    """Tester for enhanced search features"""
    
    def __init__(self):
        """Initialize the enhanced search tester"""
        self.chroma_service = ChromaService(
            collection_name="obsidian_vault",
            optimize_for_large_vault=True
        )
        self.embedding_service = EmbeddingService()
        self.search_service = EnhancedSearchService(
            chroma_service=self.chroma_service,
            embedding_service=self.embedding_service
        )
        
        logger.info("🚀 Initialized Enhanced Search Feature Tester")

    async def test_fuzzy_search(self):
        """Test fuzzy search with typo tolerance"""
        logger.info("\n🔍 Testing Fuzzy Search (Typo Tolerance)")
        logger.info("=" * 60)
        
        # Test queries with intentional typos
        fuzzy_tests = [
            {
                "query": "machne lerning",  # Intentional typos
                "description": "Machine learning with typos"
            },
            {
                "query": "pythn programing",  # Intentional typos
                "description": "Python programming with typos"
            },
            {
                "query": "data anlysis vizualization",  # Intentional typos
                "description": "Data analysis visualization with typos"
            }
        ]
        
        for test in fuzzy_tests:
            logger.info(f"Test: {test['description']}")
            
            try:
                results = self.search_service.search_with_fuzzy_matching(
                    query=test["query"],
                    n_results=3,
                    fuzzy_threshold=0.7
                )
                
                logger.info(f"  Query: '{test['query']}'")
                logger.info(f"  Results: {len(results)}")
                
                for i, result in enumerate(results[:2]):
                    fuzzy_score = result.get('fuzzy_score', 0)
                    search_type = result.get('search_type', 'unknown')
                    logger.info(f"    Result {i+1}: {search_type} (fuzzy_score: {fuzzy_score:.3f})")
                
            except Exception as e:
                logger.error(f"  Error: {e}")
            
            logger.info("")

    async def test_query_expansion(self):
        """Test automatic query expansion"""
        logger.info("\n🔍 Testing Query Expansion")
        logger.info("=" * 60)
        
        expansion_tests = [
            {
                "query": "AI",
                "description": "AI query expansion"
            },
            {
                "query": "data analysis",
                "description": "Data analysis query expansion"
            },
            {
                "query": "python programming",
                "description": "Python programming query expansion"
            }
        ]
        
        for test in expansion_tests:
            logger.info(f"Test: {test['description']}")
            
            try:
                results = self.search_service.search_with_query_expansion(
                    query=test["query"],
                    n_results=3,
                    expand_synonyms=True,
                    expand_related=True
                )
                
                logger.info(f"  Original query: '{test['query']}'")
                logger.info(f"  Results: {len(results)}")
                
                # Show expanded queries used
                expanded_queries = set()
                for result in results:
                    expanded_query = result.get('expanded_query', '')
                    if expanded_query:
                        expanded_queries.add(expanded_query)
                
                logger.info(f"  Expanded queries: {list(expanded_queries)}")
                
                for i, result in enumerate(results[:2]):
                    expanded_query = result.get('expanded_query', 'N/A')
                    logger.info(f"    Result {i+1}: expanded from '{expanded_query}'")
                
            except Exception as e:
                logger.error(f"  Error: {e}")
            
            logger.info("")

    async def test_temporal_search(self):
        """Test temporal filtering"""
        logger.info("\n🕒 Testing Temporal Search")
        logger.info("=" * 60)
        
        temporal_tests = [
            {
                "query": "machine learning",
                "relative_days": 30,
                "description": "Recent ML content (last 30 days)"
            },
            {
                "query": "python programming",
                "relative_days": 7,
                "description": "Recent Python content (last 7 days)"
            },
            {
                "query": "data analysis",
                "relative_days": 90,
                "description": "Recent data analysis (last 90 days)"
            }
        ]
        
        for test in temporal_tests:
            logger.info(f"Test: {test['description']}")
            
            try:
                results = self.search_service.search_with_temporal_filtering(
                    query=test["query"],
                    n_results=3,
                    relative_days=test["relative_days"]
                )
                
                logger.info(f"  Query: '{test['query']}' (last {test['relative_days']} days)")
                logger.info(f"  Results: {len(results)}")
                
                for i, result in enumerate(results[:2]):
                    temporal_relevance = result.get('temporal_relevance', 0)
                    metadata = result.get('metadata', {})
                    file_name = metadata.get('file_name', 'N/A')
                    logger.info(f"    Result {i+1}: {file_name} (temporal_relevance: {temporal_relevance:.3f})")
                
            except Exception as e:
                logger.error(f"  Error: {e}")
            
            logger.info("")

    async def test_semantic_clustering(self):
        """Test semantic clustering of results"""
        logger.info("\n🔍 Testing Semantic Clustering")
        logger.info("=" * 60)
        
        clustering_tests = [
            {
                "query": "artificial intelligence",
                "description": "AI content clustering"
            },
            {
                "query": "project management",
                "description": "Project management clustering"
            },
            {
                "query": "data visualization",
                "description": "Data visualization clustering"
            }
        ]
        
        for test in clustering_tests:
            logger.info(f"Test: {test['description']}")
            
            try:
                results = self.search_service.search_with_semantic_clustering(
                    query=test["query"],
                    n_results=5,
                    cluster_threshold=0.6
                )
                
                logger.info(f"  Query: '{test['query']}'")
                logger.info(f"  Clustered results: {len(results)}")
                
                for i, result in enumerate(results[:3]):
                    cluster_size = result.get('cluster_size', 1)
                    similarity = result.get('similarity', 0)
                    logger.info(f"    Cluster {i+1}: {cluster_size} items (best similarity: {similarity:.3f})")
                
            except Exception as e:
                logger.error(f"  Error: {e}")
            
            logger.info("")

    async def test_auto_suggestions(self):
        """Test auto-suggestion system"""
        logger.info("\n💡 Testing Auto-Suggestions")
        logger.info("=" * 60)
        
        suggestion_tests = [
            {
                "partial": "mach",
                "description": "Suggestions for 'mach'"
            },
            {
                "partial": "pyth",
                "description": "Suggestions for 'pyth'"
            },
            {
                "partial": "data",
                "description": "Suggestions for 'data'"
            }
        ]
        
        for test in suggestion_tests:
            logger.info(f"Test: {test['description']}")
            
            try:
                suggestions = self.search_service.search_with_auto_suggestions(
                    partial_query=test["partial"],
                    max_suggestions=5
                )
                
                logger.info(f"  Partial query: '{test['partial']}'")
                logger.info(f"  Suggestions: {suggestions}")
                
            except Exception as e:
                logger.error(f"  Error: {e}")
            
            logger.info("")

    async def test_search_analytics(self):
        """Test search analytics and performance tracking"""
        logger.info("\n📊 Testing Search Analytics")
        logger.info("=" * 60)
        
        # Perform some searches to generate analytics
        test_queries = [
            "machine learning",
            "python programming",
            "data analysis",
            "artificial intelligence",
            "project management"
        ]
        
        logger.info("Performing test searches for analytics...")
        for query in test_queries:
            try:
                self.search_service.search_similar(query, n_results=2)
                logger.info(f"  Searched: '{query}'")
            except Exception as e:
                logger.error(f"  Error searching '{query}': {e}")
        
        # Get analytics
        try:
            analytics = self.search_service.get_search_analytics()
            
            logger.info("Search Analytics:")
            logger.info(f"  Total searches: {analytics.get('total_searches', 0)}")
            logger.info(f"  Unique queries: {analytics.get('unique_queries', 0)}")
            logger.info(f"  Popular queries: {analytics.get('popular_queries', [])}")
            
            cache_stats = analytics.get('search_cache_stats', {})
            logger.info(f"  Cache hit rate: {cache_stats.get('hit_rate', 0):.2%}")
            logger.info(f"  Cache size: {cache_stats.get('cache_size', 0)}")
            
        except Exception as e:
            logger.error(f"  Error getting analytics: {e}")

    async def run_enhanced_tests(self):
        """Run all enhanced search tests"""
        logger.info("🚀 Starting Enhanced Search Feature Test Suite")
        logger.info("=" * 80)
        
        try:
            await self.test_fuzzy_search()
            await self.test_query_expansion()
            await self.test_temporal_search()
            await self.test_semantic_clustering()
            await self.test_auto_suggestions()
            await self.test_search_analytics()
            
            logger.info("\n🎉 All enhanced search tests completed!")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ Enhanced tests failed: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Run enhanced search feature tests"""
    tester = EnhancedSearchTester()
    await tester.run_enhanced_tests()

if __name__ == "__main__":
    asyncio.run(main())

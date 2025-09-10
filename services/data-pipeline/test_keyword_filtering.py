#!/usr/bin/env python3
"""
Test script for keyword filtering hybrid search functionality
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService
from src.search.search_service import SemanticSearchService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KeywordFilteringTester:
    """Test class for keyword filtering functionality"""
    
    def __init__(self):
        self.chroma_service = None
        self.embedding_service = None
        self.search_service = None
    
    async def setup(self):
        """Initialize services"""
        try:
            logger.info("Setting up services...")
            
            # Initialize ChromaDB service (no async initialize needed)
            self.chroma_service = ChromaService()
            
            # Initialize embedding service
            self.embedding_service = EmbeddingService()
            
            # Initialize search service
            self.search_service = SemanticSearchService(
                chroma_service=self.chroma_service,
                embedding_service=self.embedding_service
            )
            
            logger.info("Services initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up services: {e}")
            raise
    
    async def test_basic_keyword_filtering(self):
        """Test basic keyword filtering functionality"""
        logger.info("=" * 60)
        logger.info("TEST 1: BASIC KEYWORD FILTERING")
        logger.info("=" * 60)
        
        test_cases = [
            {
                "query": "Python programming",
                "keyword_filter": "Python",
                "description": "Search for Python programming with Python keyword filter"
            },
            {
                "query": "machine learning algorithms",
                "keyword_filter": "algorithm",
                "description": "Search for ML with algorithm keyword filter"
            },
            {
                "query": "database optimization",
                "keyword_filter": "database",
                "description": "Search for database optimization with database keyword filter"
            },
            {
                "query": "API development",
                "keyword_filter": "API",
                "description": "Search for API development with API keyword filter"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n--- Test Case {i}: {test_case['description']} ---")
            
            try:
                # Test with keyword filter
                results_with_filter = await self.search_service.search_hybrid(
                    query=test_case["query"],
                    keyword_filter=test_case["keyword_filter"],
                    n_results=3,
                    expand_query=False  # Disable query expansion to avoid API quota issues
                )
                
                # Test without keyword filter for comparison
                results_without_filter = await self.search_service.search_similar(
                    query=test_case["query"],
                    n_results=3,
                    expand_query=False
                )
                
                logger.info(f"Query: '{test_case['query']}'")
                logger.info(f"Keyword Filter: '{test_case['keyword_filter']}'")
                logger.info(f"Results with filter: {len(results_with_filter)}")
                logger.info(f"Results without filter: {len(results_without_filter)}")
                
                # Display results with filter
                if results_with_filter:
                    logger.info("Results with keyword filter:")
                    for j, result in enumerate(results_with_filter, 1):
                        content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                        similarity = result.get('similarity', 0.0)
                        keyword_count = result.get('hybrid_metadata', {}).get('keyword_count', 0)
                        logger.info(f"  {j}. Similarity: {similarity:.3f}, Keyword count: {keyword_count}")
                        logger.info(f"     Content: {content_preview}")
                
                # Verify keyword filtering worked
                if results_with_filter:
                    for result in results_with_filter:
                        content_lower = result['content'].lower()
                        keyword_lower = test_case['keyword_filter'].lower()
                        if keyword_lower not in content_lower:
                            logger.warning(f"WARNING: Keyword '{test_case['keyword_filter']}' not found in result content")
                
            except Exception as e:
                logger.error(f"Error in test case {i}: {e}")
    
    async def test_keyword_filtering_effectiveness(self):
        """Test the effectiveness of keyword filtering"""
        logger.info("=" * 60)
        logger.info("TEST 2: KEYWORD FILTERING EFFECTIVENESS")
        logger.info("=" * 60)
        
        # Test with a specific query that should benefit from keyword filtering
        query = "Python requests library"
        keyword_filter = "requests"
        
        logger.info(f"Testing effectiveness with query: '{query}' and keyword filter: '{keyword_filter}'")
        
        try:
            # Get results with and without keyword filtering
            results_with_filter = await self.search_service.search_hybrid(
                query=query,
                keyword_filter=keyword_filter,
                n_results=5,
                expand_query=False
            )
            
            results_without_filter = await self.search_service.search_similar(
                query=query,
                n_results=5,
                expand_query=False
            )
            
            logger.info(f"Results with keyword filter: {len(results_with_filter)}")
            logger.info(f"Results without keyword filter: {len(results_without_filter)}")
            
            # Analyze keyword presence in results
            if results_with_filter:
                keyword_present_count = sum(1 for result in results_with_filter 
                                          if keyword_filter.lower() in result['content'].lower())
                logger.info(f"Results containing '{keyword_filter}': {keyword_present_count}/{len(results_with_filter)}")
                
                # Calculate average keyword density
                total_density = sum(result.get('hybrid_metadata', {}).get('keyword_density', 0) 
                                  for result in results_with_filter)
                avg_density = total_density / len(results_with_filter) if results_with_filter else 0
                logger.info(f"Average keyword density: {avg_density:.3f}")
            
            if results_without_filter:
                keyword_present_count = sum(1 for result in results_without_filter 
                                          if keyword_filter.lower() in result['content'].lower())
                logger.info(f"Results without filter containing '{keyword_filter}': {keyword_present_count}/{len(results_without_filter)}")
            
        except Exception as e:
            logger.error(f"Error in effectiveness test: {e}")
    
    async def test_metadata_combination(self):
        """Test combining keyword filtering with metadata filtering"""
        logger.info("=" * 60)
        logger.info("TEST 3: KEYWORD + METADATA FILTERING")
        logger.info("=" * 60)
        
        try:
            # Test with both keyword and metadata filters
            results = await self.search_service.search_hybrid(
                query="programming concepts",
                keyword_filter="Python",
                where={"file_extension": "md"},  # Only markdown files
                n_results=3,
                expand_query=False
            )
            
            logger.info(f"Results with keyword + metadata filters: {len(results)}")
            
            if results:
                logger.info("Combined filtering results:")
                for i, result in enumerate(results, 1):
                    content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                    similarity = result.get('similarity', 0.0)
                    metadata = result.get('metadata', {})
                    file_ext = metadata.get('file_extension', 'unknown')
                    logger.info(f"  {i}. Similarity: {similarity:.3f}, File: {file_ext}")
                    logger.info(f"     Content: {content_preview}")
            
        except Exception as e:
            logger.error(f"Error in metadata combination test: {e}")
    
    async def run_all_tests(self):
        """Run all keyword filtering tests"""
        try:
            await self.setup()
            
            await self.test_basic_keyword_filtering()
            await self.test_keyword_filtering_effectiveness()
            await self.test_metadata_combination()
            
            logger.info("=" * 60)
            logger.info("ALL KEYWORD FILTERING TESTS COMPLETED")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            raise

async def main():
    """Main test function"""
    tester = KeywordFilteringTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

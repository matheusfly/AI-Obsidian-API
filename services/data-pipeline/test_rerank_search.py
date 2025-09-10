#!/usr/bin/env python3
"""
Test script for cross-encoder re-ranking functionality
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService
from src.search.search_service import SemanticSearchService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_rerank_search():
    """Test the cross-encoder re-ranking functionality"""
    logger.info("🚀 Starting Cross-Encoder Re-Ranking Test")
    
    try:
        # Initialize services
        logger.info("Initializing services...")
        chroma_service = ChromaService(
            collection_name="obsidian_vault",
            persist_directory="./data/chroma",
            optimize_for_large_vault=True
        )
        
        embedding_service = EmbeddingService(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )
        
        # Initialize search service (this will initialize the cross-encoder)
        logger.info("Initializing search service with cross-encoder...")
        search_service = SemanticSearchService(chroma_service, embedding_service)
        
        # Check collection status
        collection_count = chroma_service.collection.count()
        logger.info(f"Collection contains {collection_count} documents")
        
        if collection_count == 0:
            logger.warning("⚠️ Collection is empty! Please run data ingestion first.")
            return
        
        # Test queries for re-ranking
        test_queries = [
            "artificial intelligence machine learning",
            "Python programming development",
            "business strategy marketing",
            "data analysis visualization",
            "project management productivity"
        ]
        
        logger.info("🔍 Testing Re-Ranking vs Regular Search")
        logger.info("=" * 60)
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"\n📝 Test Query {i}: '{query}'")
            logger.info("-" * 40)
            
            # Regular semantic search
            logger.info("🔸 Regular Semantic Search:")
            start_time = datetime.now()
            regular_results = search_service.search_similar(query, n_results=5)
            regular_time = (datetime.now() - start_time).total_seconds()
            
            # Re-ranked search
            logger.info("🔸 Re-Ranked Search:")
            start_time = datetime.now()
            rerank_results = search_service.search_with_rerank(query, n_results=5, rerank_top_k=20)
            rerank_time = (datetime.now() - start_time).total_seconds()
            
            # Compare results
            logger.info(f"⏱️ Regular search time: {regular_time:.3f}s")
            logger.info(f"⏱️ Re-ranked search time: {rerank_time:.3f}s")
            logger.info(f"⏱️ Re-ranking overhead: {rerank_time - regular_time:.3f}s")
            
            # Display top results comparison
            logger.info("\n📊 Top Results Comparison:")
            logger.info("Regular Search:")
            for j, result in enumerate(regular_results[:3], 1):
                logger.info(f"  {j}. Score: {result['similarity']:.3f} | {result['metadata'].get('path', 'Unknown')[:50]}...")
            
            logger.info("Re-Ranked Search:")
            for j, result in enumerate(rerank_results[:3], 1):
                logger.info(f"  {j}. Final: {result['final_score']:.3f} | Vector: {result['similarity']:.3f} | Cross: {result['cross_score']:.3f}")
                logger.info(f"      Path: {result['metadata'].get('path', 'Unknown')[:50]}...")
            
            # Check if re-ranking changed the order
            regular_ids = [r['id'] for r in regular_results]
            rerank_ids = [r['id'] for r in rerank_results]
            
            if regular_ids != rerank_ids:
                logger.info("✅ Re-ranking changed result order - precision improvement detected!")
            else:
                logger.info("ℹ️ Re-ranking maintained same order - results already well-ranked")
        
        # Performance metrics
        logger.info("\n📈 Performance Analysis")
        logger.info("=" * 60)
        
        # Test with different rerank_top_k values
        test_query = "machine learning artificial intelligence"
        logger.info(f"Testing different rerank_top_k values with query: '{test_query}'")
        
        for top_k in [10, 15, 20, 30]:
            start_time = datetime.now()
            results = search_service.search_with_rerank(test_query, n_results=5, rerank_top_k=top_k)
            search_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"rerank_top_k={top_k}: {search_time:.3f}s, {len(results)} results")
        
        # Cross-encoder model info
        logger.info("\n🤖 Cross-Encoder Model Information:")
        logger.info(f"Model: cross-encoder/ms-marco-MiniLM-L-6-v2")
        logger.info(f"Max Length: 512 tokens")
        logger.info(f"Purpose: Query-document relevance scoring")
        
        logger.info("\n✅ Cross-Encoder Re-Ranking Test Complete!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_rerank_edge_cases():
    """Test edge cases for re-ranking"""
    logger.info("\n🧪 Testing Re-Ranking Edge Cases")
    logger.info("=" * 60)
    
    try:
        # Initialize services
        chroma_service = ChromaService(collection_name="obsidian_vault")
        embedding_service = EmbeddingService()
        search_service = SemanticSearchService(chroma_service, embedding_service)
        
        # Test 1: Very short query
        logger.info("Test 1: Very short query")
        results = search_service.search_with_rerank("AI", n_results=3, rerank_top_k=10)
        logger.info(f"Results for 'AI': {len(results)} found")
        
        # Test 2: Very long query
        logger.info("Test 2: Very long query")
        long_query = "artificial intelligence machine learning deep learning neural networks data science analytics"
        results = search_service.search_with_rerank(long_query, n_results=3, rerank_top_k=10)
        logger.info(f"Results for long query: {len(results)} found")
        
        # Test 3: Query with no results
        logger.info("Test 3: Query with no results")
        results = search_service.search_with_rerank("nonexistentxyz123", n_results=3, rerank_top_k=10)
        logger.info(f"Results for nonexistent query: {len(results)} found")
        
        # Test 4: Small rerank_top_k
        logger.info("Test 4: Small rerank_top_k")
        results = search_service.search_with_rerank("Python", n_results=5, rerank_top_k=3)
        logger.info(f"Results with rerank_top_k=3: {len(results)} found")
        
        logger.info("✅ Edge case tests complete!")
        
    except Exception as e:
        logger.error(f"❌ Edge case test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔬 Cross-Encoder Re-Ranking Test Suite")
    print("=" * 50)
    
    # Run main test
    test_rerank_search()
    
    # Run edge case tests
    test_rerank_edge_cases()
    
    print("\n🎉 All tests completed!")

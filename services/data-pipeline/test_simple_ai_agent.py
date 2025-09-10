"""
Simple test for AI agent workflow
"""

import asyncio
import logging
from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService
from src.cache.cache_manager import CacheManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_ai_agent():
    """Simple test to isolate the issue"""
    logger.info("Testing simple AI agent workflow...")
    
    try:
        # Initialize services
        chroma_service = ChromaService()
        embedding_service = EmbeddingService()
        cache_manager = CacheManager()
        
        logger.info("Services initialized successfully")
        
        # Test basic embedding generation
        query = "API authentication implementation"
        embedding = await embedding_service.generate_embedding(query)
        logger.info(f"Embedding generated: {len(embedding)} dimensions")
        
        # Test basic ChromaDB query
        results = chroma_service.collection.query(
            query_embeddings=[embedding],
            n_results=5
        )
        logger.info(f"ChromaDB query successful: {len(results['ids'][0])} results")
        
        # Test cache manager
        cache_manager.cache_query_embedding(query, embedding)
        cached_embedding = cache_manager.get_cached_query_embedding(query)
        logger.info(f"Cache test successful: {cached_embedding is not None}")
        
        logger.info("All basic tests passed!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_ai_agent())

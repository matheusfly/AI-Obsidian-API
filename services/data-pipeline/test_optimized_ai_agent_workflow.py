"""
Test Suite for Optimized AI Agent Workflow
"""

import asyncio
import time
import logging
from src.search.optimized_ai_agent_search_service import OptimizedAIAgentSearchService
from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService
from src.cache.cache_manager import CacheManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_optimized_ai_agent_workflow():
    """Test the optimized AI agent workflow"""
    logger.info("Testing optimized AI agent workflow...")
    
    # Initialize services
    chroma_service = ChromaService()
    embedding_service = EmbeddingService()
    cache_manager = CacheManager()
    
    search_service = OptimizedAIAgentSearchService(
        chroma_service=chroma_service,
        embedding_service=embedding_service,
        cache_manager=cache_manager
    )
    
    # Test query
    query = "API authentication implementation"
    
    # Test performance
    start_time = time.time()
    result = await search_service.search_for_ai_agent(
        query, performance_requirement="ultra_fast"
    )
    search_time = time.time() - start_time
    
    logger.info(f"Search completed in {search_time:.4f}s")
    logger.info(f"Strategy used: {result['ai_agent_metadata']['search_strategy']}")
    logger.info(f"Performance met: {result['ai_agent_metadata']['performance_validation']['performance_met']}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_optimized_ai_agent_workflow())
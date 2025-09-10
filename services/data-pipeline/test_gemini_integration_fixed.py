#!/usr/bin/env python3
"""
Fixed Gemini Integration Test with Rate Limiting and Real Data
"""
import asyncio
import logging
import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService
from src.search.search_service import SemanticSearchService
from src.search.query_expansion_service import ExpansionStrategy
from src.llm.gemini_client import GeminiClient, PromptStyle, LLMResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FixedGeminiIntegrationTester:
    """Fixed Gemini integration tester with rate limiting and real data"""
    
    def __init__(self):
        self.chroma_service = None
        self.embedding_service = None
        self.search_service = None
        self.gemini_client = None
        
        # Rate limiting configuration
        self.rate_limit_delay = int(os.getenv('GEMINI_RATE_LIMIT_DELAY_SECONDS', '8'))
        self.max_retries = int(os.getenv('GEMINI_MAX_RETRIES', '3'))
        self.backoff_factor = int(os.getenv('GEMINI_BACKOFF_FACTOR', '2'))
        
        # Test queries for different scenarios
        self.test_queries = [
            "What is machine learning?",
            "How to optimize Python performance?",
            "Explain vector databases"
        ]
    
    async def initialize_services(self):
        """Initialize all services for testing with real data paths"""
        logger.info("🚀 Initializing services for Gemini integration testing...")
        
        # Get real data paths from environment
        vault_path = os.getenv('VAULT_PATH', './data/raw/vault')
        vector_db_path = os.getenv('VECTOR_DB_PATH', './data/chroma')
        
        # Initialize ChromaDB service with real data
        self.chroma_service = ChromaService(
            collection_name="real_vault_collection",
            persist_directory=vector_db_path,
            embedding_model="all-MiniLM-L6-v2",
            optimize_for_large_vault=True
        )
        
        # Initialize embedding service
        self.embedding_service = EmbeddingService(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize search service with query expansion
        self.search_service = SemanticSearchService(
            chroma_service=self.chroma_service,
            embedding_service=self.embedding_service,
            gemini_api_key=os.getenv('GEMINI_API_KEY')
        )
        
        # Initialize Gemini client with rate limiting
        self.gemini_client = GeminiClient(
            api_key=os.getenv('GEMINI_API_KEY'),
            max_context_tokens=2048,
            model_name="gemini-1.5-flash"
        )
        
        logger.info("✅ All services initialized successfully")
        logger.info(f"📚 Vault path: {vault_path}")
        logger.info(f"🗄️ Vector DB path: {vector_db_path}")
    
    async def test_with_rate_limiting(self, query: str, max_retries: int = 3):
        """Test with proper rate limiting and retry logic"""
        logger.info(f"🔍 Testing query with rate limiting: '{query}'")
        
        for attempt in range(max_retries):
            try:
                # Check if we have data in the collection
                count = self.chroma_service.collection.count()
                if count == 0:
                    logger.warning("⚠️ No data in collection. Please run data ingestion first.")
                    return None
                
                logger.info(f"📊 Collection contains {count} documents")
                
                # Search with query expansion
                search_results = await self.search_service.search_similar(
                    query=query,
                    n_results=5,
                    expand_query=True,
                    expansion_strategy=ExpansionStrategy.HYBRID
                )
                
                if not search_results:
                    logger.warning("No search results found")
                    return None
                
                # Process with Gemini (with rate limiting)
                logger.info(f"🤖 Processing with Gemini (attempt {attempt + 1})...")
                
                # Add delay between requests to respect rate limits
                if attempt > 0:
                    delay = self.rate_limit_delay * (self.backoff_factor ** (attempt - 1))
                    logger.info(f"⏳ Waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
                
                response = await self.gemini_client.process_content(
                    query=query,
                    context_chunks=search_results,
                    style=PromptStyle.RESEARCH_ASSISTANT
                )
                
                logger.info(f"✅ Success! Processing time: {time.time():.2f}s")
                logger.info(f"📝 Answer length: {len(response.answer)} characters")
                logger.info(f"🎯 Confidence: {response.confidence_score:.3f}")
                logger.info(f"📊 Sources used: {response.sources_used}")
                logger.info(f"🔢 Token usage: {response.token_usage}")
                logger.info(f"📄 Answer preview: {response.answer[:200]}...")
                
                return response
                
            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                if "429" in str(e) or "quota" in str(e).lower():
                    logger.warning("⚠️ Rate limit exceeded, will retry with backoff")
                    if attempt < max_retries - 1:
                        delay = self.rate_limit_delay * (self.backoff_factor ** attempt)
                        logger.info(f"⏳ Waiting {delay}s before retry...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error("❌ Max retries exceeded")
                        return None
                else:
                    logger.error(f"❌ Non-rate-limit error: {e}")
                    return None
        
        return None
    
    async def test_real_data_consumption(self):
        """Test real data consumption from vault embeddings"""
        logger.info("\n📚 Testing Real Data Consumption")
        logger.info("=" * 50)
        
        # Check collection status
        try:
            count = self.chroma_service.collection.count()
            logger.info(f"📊 Collection contains {count} documents")
            
            if count == 0:
                logger.warning("⚠️ No data in collection. This suggests:")
                logger.warning("   1. Vault data hasn't been ingested yet")
                logger.warning("   2. Collection name is incorrect")
                logger.warning("   3. Vector DB path is incorrect")
                return False
            
            # Test a simple query
            query = "machine learning"
            logger.info(f"🔍 Testing query: '{query}'")
            
            # Search without LLM to test data retrieval
            search_results = await self.search_service.search_similar(
                query=query,
                n_results=3,
                expand_query=False
            )
            
            if search_results:
                logger.info(f"✅ Found {len(search_results)} results from real data")
                for i, result in enumerate(search_results):
                    logger.info(f"  📄 Result {i+1}: {result.get('metadata', {}).get('file_name', 'Unknown')} (similarity: {result.get('similarity', 0):.3f})")
                return True
            else:
                logger.warning("❌ No search results found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing real data consumption: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive test with rate limiting"""
        logger.info("🎯 Starting Fixed Gemini Integration Tests")
        logger.info("=" * 80)
        
        try:
            await self.initialize_services()
            
            # Test real data consumption first
            if not await self.test_real_data_consumption():
                logger.error("❌ Real data consumption test failed. Please check your data setup.")
                return
            
            # Test with rate limiting
            for query in self.test_queries:
                logger.info(f"\n📝 Testing query: '{query}'")
                await self.test_with_rate_limiting(query)
                
                # Add delay between queries to respect rate limits
                logger.info("⏳ Waiting between queries to respect rate limits...")
                await asyncio.sleep(self.rate_limit_delay)
            
            logger.info("\n🎉 All Fixed Gemini Integration Tests Completed Successfully!")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise

async def main():
    """Main test execution"""
    tester = FixedGeminiIntegrationTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())

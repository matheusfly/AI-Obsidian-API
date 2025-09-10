#!/usr/bin/env python3
"""
Test script for Gemini Integration and Response optimization
"""
import asyncio
import logging
import sys
import os
import time
from datetime import datetime

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

class GeminiIntegrationTester:
    """Comprehensive tester for Gemini integration"""
    
    def __init__(self):
        self.chroma_service = None
        self.embedding_service = None
        self.search_service = None
        self.gemini_client = None
        
        # Test queries for different scenarios
        self.test_queries = [
            "What is machine learning?",
            "How to optimize Python performance?",
            "Explain vector databases",
            "What are the best practices for API security?",
            "Summarize the content about cross-encoders"
        ]
    
    async def initialize_services(self):
        """Initialize all services for testing"""
        logger.info("🚀 Initializing services for Gemini integration testing...")
        
        # Initialize ChromaDB service
        self.chroma_service = ChromaService(
            collection_name="mock_test_collection",
            persist_directory="./test_mock_chroma",
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
        
        # Initialize Gemini client
        self.gemini_client = GeminiClient(
            api_key=os.getenv('GEMINI_API_KEY'),
            max_context_tokens=2048,
            model_name="gemini-1.5-flash"
        )
        
        logger.info("✅ All services initialized successfully")
    
    async def test_token_counting(self):
        """Test token counting functionality"""
        logger.info("\n🔢 Testing Token Counting")
        logger.info("=" * 50)
        
        test_texts = [
            "Hello world",
            "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.",
            "Python is a high-level programming language known for its simplicity and readability. It's widely used in data science, web development, and automation.",
            "Vector databases like ChromaDB enable efficient similarity search for embeddings. They use algorithms like HNSW to provide fast approximate nearest neighbor search for high-dimensional vectors."
        ]
        
        for text in test_texts:
            token_count = self.gemini_client.count_tokens(text)
            word_count = len(text.split())
            logger.info(f"Text: '{text[:50]}...'")
            logger.info(f"  Tokens: {token_count}, Words: {word_count}, Ratio: {token_count/word_count:.2f}")
    
    async def test_context_assembly(self):
        """Test context assembly with token counting"""
        logger.info("\n📚 Testing Context Assembly")
        logger.info("=" * 50)
        
        # Check if we have data in the collection
        try:
            count = self.chroma_service.collection.count()
            if count == 0:
                logger.warning("⚠️ No data in collection. Please run data ingestion first.")
                return
            logger.info(f"📊 Collection contains {count} documents")
        except Exception as e:
            logger.error(f"❌ Error checking collection: {e}")
            return
        
        # Test context assembly with different token limits
        query = "machine learning"
        search_results = await self.search_service.search_similar(query, n_results=10, expand_query=True)
        
        if not search_results:
            logger.warning("No search results found")
            return
        
        # Test different token limits
        token_limits = [500, 1000, 1500, 2000]
        
        for limit in token_limits:
            logger.info(f"\n📊 Testing with {limit} token limit:")
            context_text, used_chunks, total_tokens = self.gemini_client.assemble_context(search_results, limit)
            
            logger.info(f"  Context assembled: {len(used_chunks)} chunks")
            logger.info(f"  Total tokens: {total_tokens}")
            logger.info(f"  Token efficiency: {total_tokens/limit*100:.1f}%")
            logger.info(f"  Context preview: {context_text[:200]}...")
    
    async def test_prompt_styles(self):
        """Test different prompt styles"""
        logger.info("\n🎨 Testing Prompt Styles")
        logger.info("=" * 50)
        
        # Check if we have data in the collection
        try:
            count = self.chroma_service.collection.count()
            if count == 0:
                logger.warning("⚠️ No data in collection. Please run data ingestion first.")
                return
        except Exception as e:
            logger.error(f"❌ Error checking collection: {e}")
            return
        
        query = "What is machine learning?"
        search_results = await self.search_service.search_similar(query, n_results=5, expand_query=True)
        
        if not search_results:
            logger.warning("No search results found")
            return
        
        # Test different prompt styles
        styles = [
            (PromptStyle.RESEARCH_ASSISTANT, "Research Assistant"),
            (PromptStyle.TECHNICAL_EXPERT, "Technical Expert"),
            (PromptStyle.SUMMARIZER, "Summarizer"),
            (PromptStyle.ANALYST, "Analyst")
        ]
        
        for style, style_name in styles:
            logger.info(f"\n🎯 Testing {style_name} style:")
            
            try:
                start_time = time.time()
                response = await self.gemini_client.process_content(
                    query=query,
                    context_chunks=search_results,
                    style=style
                )
                processing_time = time.time() - start_time
                
                logger.info(f"  Processing time: {processing_time:.2f}s")
                logger.info(f"  Answer length: {len(response.answer)} characters")
                logger.info(f"  Sources used: {response.sources_used}")
                logger.info(f"  Confidence: {response.confidence_score:.3f}")
                logger.info(f"  Token usage: {response.token_usage}")
                logger.info(f"  Answer preview: {response.answer[:200]}...")
                
            except Exception as e:
                logger.error(f"  ❌ Error with {style_name} style: {e}")
    
    async def test_llm_processing_pipeline(self):
        """Test the complete LLM processing pipeline"""
        logger.info("\n🤖 Testing LLM Processing Pipeline")
        logger.info("=" * 50)
        
        # Check if we have data in the collection
        try:
            count = self.chroma_service.collection.count()
            if count == 0:
                logger.warning("⚠️ No data in collection. Please run data ingestion first.")
                return
        except Exception as e:
            logger.error(f"❌ Error checking collection: {e}")
            return
        
        for query in self.test_queries[:3]:  # Test first 3 queries
            logger.info(f"\n📝 Testing query: '{query}'")
            
            # Step 1: Search with query expansion
            logger.info("  🔍 Step 1: Semantic search with query expansion")
            start_time = time.time()
            search_results = await self.search_service.search_similar(
                query=query,
                n_results=8,
                expand_query=True,
                expansion_strategy=ExpansionStrategy.HYBRID
            )
            search_time = time.time() - start_time
            
            logger.info(f"    Search time: {search_time:.2f}s")
            logger.info(f"    Results: {len(search_results)}")
            
            if not search_results:
                logger.warning("    No search results found")
                continue
            
            # Step 2: Re-ranking
            logger.info("  🔄 Step 2: Re-ranking results")
            start_time = time.time()
            reranked_results = await self.search_service.search_with_rerank(
                query=query,
                n_results=5,
                rerank_top_k=8
            )
            rerank_time = time.time() - start_time
            
            logger.info(f"    Re-ranking time: {rerank_time:.2f}s")
            logger.info(f"    Re-ranked results: {len(reranked_results)}")
            
            # Step 3: LLM processing
            logger.info("  🤖 Step 3: LLM processing")
            start_time = time.time()
            llm_response = await self.gemini_client.process_content(
                query=query,
                context_chunks=reranked_results,
                style=PromptStyle.RESEARCH_ASSISTANT
            )
            llm_time = time.time() - start_time
            
            logger.info(f"    LLM processing time: {llm_time:.2f}s")
            logger.info(f"    Answer length: {len(llm_response.answer)} characters")
            logger.info(f"    Sources used: {llm_response.sources_used}")
            logger.info(f"    Confidence: {llm_response.confidence_score:.3f}")
            logger.info(f"    Token usage: {llm_response.token_usage}")
            logger.info(f"    Answer preview: {llm_response.answer[:300]}...")
            
            # Total pipeline time
            total_time = search_time + rerank_time + llm_time
            logger.info(f"  📊 Total pipeline time: {total_time:.2f}s")
    
    async def benchmark_performance(self):
        """Benchmark Gemini integration performance"""
        logger.info("\n⚡ Benchmarking Gemini Integration Performance")
        logger.info("=" * 60)
        
        # Check if we have data in the collection
        try:
            count = self.chroma_service.collection.count()
            if count == 0:
                logger.warning("⚠️ No data in collection. Please run data ingestion first.")
                return
        except Exception as e:
            logger.error(f"❌ Error checking collection: {e}")
            return
        
        # Benchmark different components
        query = "machine learning artificial intelligence"
        
        # Benchmark search + expansion
        logger.info("📊 Benchmarking search + expansion:")
        times = []
        for i in range(3):
            start_time = time.time()
            search_results = await self.search_service.search_similar(query, n_results=5, expand_query=True)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_search_time = sum(times) / len(times)
        logger.info(f"  Average search time: {avg_search_time:.2f}s")
        
        # Benchmark re-ranking
        logger.info("📊 Benchmarking re-ranking:")
        times = []
        for i in range(3):
            start_time = time.time()
            reranked_results = await self.search_service.search_with_rerank(query, n_results=3, rerank_top_k=5)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_rerank_time = sum(times) / len(times)
        logger.info(f"  Average re-ranking time: {avg_rerank_time:.2f}s")
        
        # Benchmark LLM processing
        logger.info("📊 Benchmarking LLM processing:")
        times = []
        token_usage = []
        
        for i in range(3):
            start_time = time.time()
            llm_response = await self.gemini_client.process_content(
                query=query,
                context_chunks=search_results,
                style=PromptStyle.RESEARCH_ASSISTANT
            )
            end_time = time.time()
            times.append(end_time - start_time)
            token_usage.append(sum(llm_response.token_usage.values()))
        
        avg_llm_time = sum(times) / len(times)
        avg_tokens = sum(token_usage) / len(token_usage)
        
        logger.info(f"  Average LLM time: {avg_llm_time:.2f}s")
        logger.info(f"  Average tokens used: {avg_tokens:.0f}")
        
        # Total pipeline benchmark
        total_pipeline_time = avg_search_time + avg_rerank_time + avg_llm_time
        logger.info(f"📈 Total pipeline time: {total_pipeline_time:.2f}s")
        logger.info(f"📈 Tokens per second: {avg_tokens/avg_llm_time:.1f}")
    
    async def run_comprehensive_test(self):
        """Run comprehensive Gemini integration tests"""
        logger.info("🎯 Starting Comprehensive Gemini Integration Tests")
        logger.info("=" * 80)
        
        try:
            await self.initialize_services()
            
            # Test token counting
            await self.test_token_counting()
            
            # Test context assembly
            await self.test_context_assembly()
            
            # Test prompt styles
            await self.test_prompt_styles()
            
            # Test LLM processing pipeline
            await self.test_llm_processing_pipeline()
            
            # Benchmark performance
            await self.benchmark_performance()
            
            logger.info("\n🎉 All Gemini Integration Tests Completed Successfully!")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise

async def main():
    """Main test execution"""
    tester = GeminiIntegrationTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())

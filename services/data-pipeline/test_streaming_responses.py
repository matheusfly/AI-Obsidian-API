#!/usr/bin/env python3
"""
Test script for Streaming Responses functionality
Validates real-time token generation and UX improvements
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
from src.llm.gemini_client import GeminiClient, PromptStyle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StreamingResponseTester:
    """Comprehensive tester for streaming responses"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not found. Using mock responses.")
            self.gemini_api_key = "mock_key"
        
        # Initialize services
        self.chroma_service = ChromaService()
        self.embedding_service = EmbeddingService()
        self.search_service = SemanticSearchService(
            chroma_service=self.chroma_service,
            embedding_service=self.embedding_service,
            gemini_api_key=self.gemini_api_key
        )
        self.gemini_client = GeminiClient(api_key=self.gemini_api_key)
        
        logger.info("✅ Streaming Response Tester initialized")
    
    async def test_streaming_vs_non_streaming(self):
        """Compare streaming vs non-streaming performance"""
        logger.info("🔄 Testing Streaming vs Non-Streaming Performance")
        
        # Mock context chunks for testing
        mock_chunks = [
            {
                "content": "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, machine learning, and automation.",
                "metadata": {"path": "python_basics.md", "heading": "Introduction", "chunk_index": 0},
                "similarity": 0.85,
                "final_score": 0.85
            },
            {
                "content": "Machine learning with Python involves libraries like scikit-learn, pandas, numpy, and tensorflow. These libraries provide powerful tools for data analysis and model building.",
                "metadata": {"path": "ml_python.md", "heading": "Libraries", "chunk_index": 1},
                "similarity": 0.72,
                "final_score": 0.72
            },
            {
                "content": "Performance optimization in Python includes using list comprehensions, avoiding global variables, using appropriate data structures, and profiling code to identify bottlenecks.",
                "metadata": {"path": "python_performance.md", "heading": "Optimization", "chunk_index": 2},
                "similarity": 0.68,
                "final_score": 0.68
            }
        ]
        
        query = "What is Python and how can I optimize its performance for machine learning?"
        
        # Test non-streaming
        logger.info("📊 Testing Non-Streaming Response:")
        start_time = time.time()
        try:
            non_streaming_response = await self.gemini_client.process_content(
                query, mock_chunks, PromptStyle.RESEARCH_ASSISTANT
            )
            non_streaming_time = time.time() - start_time
            logger.info(f"  ⏱️  Non-streaming time: {non_streaming_time:.3f}s")
            logger.info(f"  📝 Response length: {len(non_streaming_response.answer)} characters")
            logger.info(f"  🎯 Confidence: {non_streaming_response.confidence_score:.3f}")
            logger.info(f"  📊 Token usage: {non_streaming_response.token_usage}")
        except Exception as e:
            logger.error(f"  ❌ Non-streaming failed: {e}")
            non_streaming_time = 0
            non_streaming_response = None
        
        # Test streaming
        logger.info("📊 Testing Streaming Response:")
        start_time = time.time()
        streaming_chunks = []
        first_token_time = None
        total_tokens = 0
        
        try:
            async for chunk in self.gemini_client.stream_content(
                query, mock_chunks, PromptStyle.RESEARCH_ASSISTANT
            ):
                if first_token_time is None:
                    first_token_time = time.time()
                    time_to_first_token = first_token_time - start_time
                    logger.info(f"  ⚡ Time to first token: {time_to_first_token:.3f}s")
                
                streaming_chunks.append(chunk)
                total_tokens += len(chunk.split())
                
                # Simulate real-time display
                print(f"📝 {chunk}", end="", flush=True)
            
            streaming_time = time.time() - start_time
            streaming_response = "".join(streaming_chunks)
            
            print()  # New line after streaming
            logger.info(f"  ⏱️  Total streaming time: {streaming_time:.3f}s")
            logger.info(f"  📝 Response length: {len(streaming_response)} characters")
            logger.info(f"  🔢 Total tokens: {total_tokens}")
            
        except Exception as e:
            logger.error(f"  ❌ Streaming failed: {e}")
            streaming_time = 0
            streaming_response = ""
        
        # Performance comparison
        logger.info("📈 Performance Comparison:")
        if non_streaming_time > 0 and streaming_time > 0:
            time_difference = streaming_time - non_streaming_time
            percentage_diff = (time_difference / non_streaming_time) * 100
            logger.info(f"  ⏱️  Time difference: {time_difference:.3f}s ({percentage_diff:+.1f}%)")
            
            if first_token_time:
                perceived_speed_improvement = (non_streaming_time - (first_token_time - start_time)) / non_streaming_time * 100
                logger.info(f"  ⚡ Perceived speed improvement: {perceived_speed_improvement:.1f}%")
        
        return {
            "non_streaming_time": non_streaming_time,
            "streaming_time": streaming_time,
            "time_to_first_token": first_token_time - start_time if first_token_time else 0,
            "non_streaming_response": non_streaming_response.answer if non_streaming_response else "",
            "streaming_response": streaming_response
        }
    
    async def test_streaming_with_different_prompts(self):
        """Test streaming with different prompt styles"""
        logger.info("🎨 Testing Streaming with Different Prompt Styles")
        
        mock_chunks = [
            {
                "content": "Clean Architecture is a software design philosophy that separates concerns into distinct layers: presentation, application, domain, and infrastructure.",
                "metadata": {"path": "clean_architecture.md", "heading": "Overview", "chunk_index": 0},
                "similarity": 0.90,
                "final_score": 0.90
            }
        ]
        
        query = "Explain Clean Architecture principles"
        prompt_styles = [
            (PromptStyle.RESEARCH_ASSISTANT, "Research Assistant"),
            (PromptStyle.TECHNICAL_EXPERT, "Technical Expert"),
            (PromptStyle.SUMMARIZER, "Summarizer"),
            (PromptStyle.ANALYST, "Analyst")
        ]
        
        results = {}
        
        for style, name in prompt_styles:
            logger.info(f"  🎯 Testing {name} style:")
            start_time = time.time()
            chunks = []
            
            try:
                async for chunk in self.gemini_client.stream_content(query, mock_chunks, style):
                    chunks.append(chunk)
                    print(f"📝 {chunk}", end="", flush=True)
                
                response_time = time.time() - start_time
                response_text = "".join(chunks)
                
                print()  # New line
                logger.info(f"    ⏱️  Response time: {response_time:.3f}s")
                logger.info(f"    📝 Response length: {len(response_text)} characters")
                
                results[name] = {
                    "time": response_time,
                    "length": len(response_text),
                    "response": response_text
                }
                
            except Exception as e:
                logger.error(f"    ❌ {name} style failed: {e}")
                results[name] = {"error": str(e)}
        
        return results
    
    async def test_streaming_performance_metrics(self):
        """Test streaming performance with detailed metrics"""
        logger.info("📊 Testing Streaming Performance Metrics")
        
        # Test queries of different lengths
        test_queries = [
            ("Short query", "What is Python?"),
            ("Medium query", "How does machine learning work with Python libraries?"),
            ("Long query", "Explain the complete process of building a machine learning model using Python, including data preprocessing, feature engineering, model selection, training, validation, and deployment strategies.")
        ]
        
        mock_chunks = [
            {
                "content": "Python is a versatile programming language used in many domains including web development, data science, machine learning, and automation.",
                "metadata": {"path": "python_overview.md", "heading": "Introduction", "chunk_index": 0},
                "similarity": 0.85,
                "final_score": 0.85
            }
        ]
        
        metrics = {}
        
        for query_type, query in test_queries:
            logger.info(f"  🔍 Testing {query_type}:")
            
            start_time = time.time()
            first_token_time = None
            chunks = []
            token_counts = []
            
            try:
                async for chunk in self.gemini_client.stream_content(query, mock_chunks):
                    if first_token_time is None:
                        first_token_time = time.time()
                    
                    chunks.append(chunk)
                    token_count = len(chunk.split())
                    token_counts.append(token_count)
                    
                    # Simulate processing delay
                    await asyncio.sleep(0.01)
                
                total_time = time.time() - start_time
                time_to_first_token = first_token_time - start_time if first_token_time else 0
                
                metrics[query_type] = {
                    "total_time": total_time,
                    "time_to_first_token": time_to_first_token,
                    "total_tokens": sum(token_counts),
                    "chunk_count": len(chunks),
                    "avg_tokens_per_chunk": sum(token_counts) / len(chunks) if chunks else 0,
                    "tokens_per_second": sum(token_counts) / total_time if total_time > 0 else 0
                }
                
                logger.info(f"    ⏱️  Total time: {total_time:.3f}s")
                logger.info(f"    ⚡ Time to first token: {time_to_first_token:.3f}s")
                logger.info(f"    🔢 Total tokens: {sum(token_counts)}")
                logger.info(f"    📊 Tokens/second: {sum(token_counts) / total_time:.1f}")
                
            except Exception as e:
                logger.error(f"    ❌ {query_type} failed: {e}")
                metrics[query_type] = {"error": str(e)}
        
        return metrics
    
    async def run_comprehensive_test(self):
        """Run all streaming tests"""
        logger.info("🚀 Starting Comprehensive Streaming Response Test")
        logger.info("=" * 80)
        
        # Test 1: Streaming vs Non-streaming
        logger.info("📋 Test 1: Streaming vs Non-streaming Performance")
        comparison_results = await self.test_streaming_vs_non_streaming()
        
        logger.info("\n" + "=" * 80)
        
        # Test 2: Different prompt styles
        logger.info("📋 Test 2: Different Prompt Styles")
        prompt_results = await self.test_streaming_with_different_prompts()
        
        logger.info("\n" + "=" * 80)
        
        # Test 3: Performance metrics
        logger.info("📋 Test 3: Performance Metrics")
        performance_results = await self.test_streaming_performance_metrics()
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 STREAMING RESPONSE TEST SUMMARY")
        logger.info("=" * 80)
        
        logger.info("✅ Streaming vs Non-streaming:")
        logger.info(f"  Non-streaming time: {comparison_results['non_streaming_time']:.3f}s")
        logger.info(f"  Streaming time: {comparison_results['streaming_time']:.3f}s")
        logger.info(f"  Time to first token: {comparison_results['time_to_first_token']:.3f}s")
        
        logger.info("✅ Prompt Style Results:")
        for style, result in prompt_results.items():
            if "error" in result:
                logger.info(f"  {style}: ❌ {result['error']}")
            else:
                logger.info(f"  {style}: {result['time']:.3f}s, {result['length']} chars")
        
        logger.info("✅ Performance Metrics:")
        for query_type, metrics in performance_results.items():
            if "error" in metrics:
                logger.info(f"  {query_type}: ❌ {metrics['error']}")
            else:
                logger.info(f"  {query_type}: {metrics['total_time']:.3f}s, {metrics['tokens_per_second']:.1f} tokens/s")
        
        logger.info("\n🎉 Streaming Response Test Complete!")
        return {
            "comparison": comparison_results,
            "prompt_styles": prompt_results,
            "performance": performance_results
        }

async def main():
    """Main test function"""
    tester = StreamingResponseTester()
    results = await tester.run_comprehensive_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())

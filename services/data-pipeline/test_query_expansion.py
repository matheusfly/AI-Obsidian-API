#!/usr/bin/env python3
"""
Test script for Query Expansion and Understanding functionality
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
from src.search.query_expansion_service import QueryExpansionService, ExpansionStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QueryExpansionTester:
    """Comprehensive tester for query expansion functionality"""
    
    def __init__(self):
        self.chroma_service = None
        self.embedding_service = None
        self.search_service = None
        self.query_expansion_service = None
        
        # Test queries with different characteristics
        self.test_queries = [
            # Short and ambiguous
            "Python tips",
            "React help",
            "API security",
            "Docker setup",
            
            # How-to queries
            "how to debug React",
            "how to optimize performance",
            "how to deploy applications",
            
            # Technical terms
            "machine learning examples",
            "vector database similarity",
            "cross encoder relevance",
            
            # General queries
            "best practices",
            "troubleshooting guide",
            "configuration examples"
        ]
    
    async def initialize_services(self):
        """Initialize all services for testing"""
        logger.info("🚀 Initializing services for query expansion testing...")
        
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
            gemini_api_key=os.getenv('GEMINI_API_KEY')  # Optional
        )
        
        # Initialize query expansion service
        self.query_expansion_service = QueryExpansionService(
            gemini_api_key=os.getenv('GEMINI_API_KEY')  # Optional
        )
        
        logger.info("✅ All services initialized successfully")
    
    async def test_query_expansion_service(self):
        """Test the query expansion service directly"""
        logger.info("\n🔍 Testing Query Expansion Service")
        logger.info("=" * 60)
        
        for query in self.test_queries[:5]:  # Test first 5 queries
            logger.info(f"\n📝 Testing: '{query}'")
            
            # Test rule-based expansion
            logger.info("  📊 Rule-based expansion:")
            analysis = await self.query_expansion_service.expand_query(query, ExpansionStrategy.RULE_BASED)
            logger.info(f"    Original: '{analysis.original_query}'")
            logger.info(f"    Expanded: '{analysis.expanded_query}'")
            logger.info(f"    Intent: {analysis.intent}")
            logger.info(f"    Entities: {analysis.entities}")
            logger.info(f"    Confidence: {analysis.expansion_confidence:.2f}")
            logger.info(f"    Reasoning: {analysis.expansion_reasoning}")
            
            # Test LLM-based expansion (if available)
            if self.query_expansion_service.gemini_model:
                logger.info("  🤖 LLM-based expansion:")
                analysis_llm = await self.query_expansion_service.expand_query(query, ExpansionStrategy.LLM_BASED)
                logger.info(f"    Original: '{analysis_llm.original_query}'")
                logger.info(f"    Expanded: '{analysis_llm.expanded_query}'")
                logger.info(f"    Confidence: {analysis_llm.expansion_confidence:.2f}")
                logger.info(f"    Reasoning: {analysis_llm.expansion_reasoning}")
            
            # Test hybrid expansion
            logger.info("  🔄 Hybrid expansion:")
            analysis_hybrid = await self.query_expansion_service.expand_query(query, ExpansionStrategy.HYBRID)
            logger.info(f"    Original: '{analysis_hybrid.original_query}'")
            logger.info(f"    Expanded: '{analysis_hybrid.expanded_query}'")
            logger.info(f"    Strategy: {analysis_hybrid.strategy_used.value}")
            logger.info(f"    Confidence: {analysis_hybrid.expansion_confidence:.2f}")
    
    async def test_search_with_expansion(self):
        """Test search functionality with query expansion"""
        logger.info("\n🔍 Testing Search with Query Expansion")
        logger.info("=" * 60)
        
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
        
        for query in self.test_queries[:3]:  # Test first 3 queries
            logger.info(f"\n📝 Testing search: '{query}'")
            
            # Test search without expansion
            logger.info("  🔍 Search without expansion:")
            start_time = time.time()
            results_no_expansion = await self.search_service.search_similar(
                query, n_results=3, expand_query=False
            )
            time_no_expansion = time.time() - start_time
            
            logger.info(f"    Results: {len(results_no_expansion)}")
            logger.info(f"    Time: {time_no_expansion*1000:.1f}ms")
            if results_no_expansion:
                logger.info(f"    Top result: {results_no_expansion[0]['content'][:100]}...")
            
            # Test search with rule-based expansion
            logger.info("  📊 Search with rule-based expansion:")
            start_time = time.time()
            results_rule = await self.search_service.search_similar(
                query, n_results=3, expand_query=True, expansion_strategy=ExpansionStrategy.RULE_BASED
            )
            time_rule = time.time() - start_time
            
            logger.info(f"    Results: {len(results_rule)}")
            logger.info(f"    Time: {time_rule*1000:.1f}ms")
            if results_rule and 'query_analysis' in results_rule[0]:
                analysis = results_rule[0]['query_analysis']
                logger.info(f"    Expanded query: '{analysis['expanded_query']}'")
                logger.info(f"    Intent: {analysis['intent']}")
                logger.info(f"    Confidence: {analysis['expansion_confidence']:.2f}")
            
            # Test search with hybrid expansion
            logger.info("  🔄 Search with hybrid expansion:")
            start_time = time.time()
            results_hybrid = await self.search_service.search_similar(
                query, n_results=3, expand_query=True, expansion_strategy=ExpansionStrategy.HYBRID
            )
            time_hybrid = time.time() - start_time
            
            logger.info(f"    Results: {len(results_hybrid)}")
            logger.info(f"    Time: {time_hybrid*1000:.1f}ms")
            if results_hybrid and 'query_analysis' in results_hybrid[0]:
                analysis = results_hybrid[0]['query_analysis']
                logger.info(f"    Expanded query: '{analysis['expanded_query']}'")
                logger.info(f"    Strategy: {analysis['strategy_used']}")
                logger.info(f"    Confidence: {analysis['expansion_confidence']:.2f}")
    
    async def test_query_suggestions(self):
        """Test query suggestions functionality"""
        logger.info("\n💡 Testing Query Suggestions")
        logger.info("=" * 60)
        
        for query in self.test_queries[:3]:  # Test first 3 queries
            logger.info(f"\n📝 Testing suggestions for: '{query}'")
            
            suggestions = await self.search_service.get_query_suggestions(query)
            
            logger.info(f"  Original query: '{suggestions['original_query']}'")
            logger.info(f"  Expanded query: '{suggestions['expanded_query']}'")
            logger.info(f"  Intent: {suggestions['intent']}")
            logger.info(f"  Entities: {suggestions['entities']}")
            logger.info(f"  Confidence: {suggestions['expansion_confidence']:.2f}")
            logger.info(f"  Strategy: {suggestions['strategy_used']}")
            logger.info(f"  Reasoning: {suggestions['expansion_reasoning']}")
            logger.info(f"  Suggestions: {suggestions['suggestions']}")
    
    async def benchmark_expansion_performance(self):
        """Benchmark query expansion performance"""
        logger.info("\n⚡ Benchmarking Query Expansion Performance")
        logger.info("=" * 60)
        
        # Test different expansion strategies
        strategies = [
            (ExpansionStrategy.RULE_BASED, "Rule-based"),
            (ExpansionStrategy.LLM_BASED, "LLM-based"),
            (ExpansionStrategy.HYBRID, "Hybrid")
        ]
        
        results = {}
        
        for strategy, strategy_name in strategies:
            logger.info(f"\n📊 Testing {strategy_name} strategy:")
            
            times = []
            confidences = []
            
            for query in self.test_queries[:5]:  # Test first 5 queries
                start_time = time.time()
                analysis = await self.query_expansion_service.expand_query(query, strategy)
                end_time = time.time()
                
                expansion_time = end_time - start_time
                times.append(expansion_time)
                confidences.append(analysis.expansion_confidence)
                
                logger.info(f"  '{query}' → {expansion_time*1000:.1f}ms (confidence: {analysis.expansion_confidence:.2f})")
            
            # Calculate statistics
            avg_time = sum(times) / len(times)
            avg_confidence = sum(confidences) / len(confidences)
            
            results[strategy_name] = {
                "avg_time_ms": avg_time * 1000,
                "avg_confidence": avg_confidence,
                "total_queries": len(times)
            }
            
            logger.info(f"  📈 Average time: {avg_time*1000:.1f}ms")
            logger.info(f"  📈 Average confidence: {avg_confidence:.2f}")
        
        # Summary
        logger.info("\n📊 Performance Summary:")
        logger.info("-" * 40)
        for strategy_name, stats in results.items():
            logger.info(f"{strategy_name}: {stats['avg_time_ms']:.1f}ms avg, {stats['avg_confidence']:.2f} confidence")
    
    async def run_comprehensive_test(self):
        """Run comprehensive query expansion tests"""
        logger.info("🎯 Starting Comprehensive Query Expansion Tests")
        logger.info("=" * 80)
        
        try:
            await self.initialize_services()
            
            # Test query expansion service
            await self.test_query_expansion_service()
            
            # Test search with expansion
            await self.test_search_with_expansion()
            
            # Test query suggestions
            await self.test_query_suggestions()
            
            # Benchmark performance
            await self.benchmark_expansion_performance()
            
            logger.info("\n🎉 All Query Expansion Tests Completed Successfully!")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise

async def main():
    """Main test execution"""
    tester = QueryExpansionTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())

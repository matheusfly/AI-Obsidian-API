#!/usr/bin/env python3
"""
Comprehensive Performance Testing and Optimization Script
Tests cross-encoder re-ranking and other performance improvements
"""

import asyncio
import logging
import time
import json
import statistics
from pathlib import Path
from typing import List, Dict, Any, Tuple
import sys
import os

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.ingestion.filesystem_client import FilesystemVaultClient
from src.processing.hybrid_content_processor import HybridContentProcessor
from src.embeddings.embedding_service import EmbeddingService
from src.vector.chroma_service import ChromaService
from src.search.search_service import SemanticSearchService
from src.llm.gemini_client import GeminiClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceTester:
    """Comprehensive performance testing for data pipeline optimizations"""
    
    def __init__(self, vault_path: str, chroma_db_path: str = "./test_performance_chroma_db"):
        self.vault_path = vault_path
        self.chroma_db_path = chroma_db_path
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Initialize services
        self.filesystem_client = None
        self.content_processor = None
        self.embedding_service = None
        self.chroma_service = None
        self.search_service = None
        self.gemini_client = None
        
        # Test results storage
        self.test_results = {
            "baseline": {},
            "optimized": {},
            "comparisons": {}
        }
        
    async def setup_services(self):
        """Initialize all required services"""
        logger.info("Setting up services...")
        
        try:
            # Initialize filesystem client
            self.filesystem_client = FilesystemVaultClient(vault_path=self.vault_path)
            
            # Initialize content processor with hybrid chunking
            self.content_processor = HybridContentProcessor(
                max_chunk_size=512,
                chunk_overlap=128
            )
            
            # Initialize embedding service
            self.embedding_service = EmbeddingService(model_name=self.embedding_model)
            
            # Initialize ChromaDB service
            self.chroma_service = ChromaService(
                persist_directory=self.chroma_db_path,
                collection_name="performance_test",
                embedding_model=self.embedding_model
            )
            
            # Initialize search service with cross-encoder
            self.search_service = SemanticSearchService(
                chroma_service=self.chroma_service,
                embedding_service=self.embedding_service
            )
            
            # Initialize Gemini client (optional)
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                self.gemini_client = GeminiClient(api_key=gemini_api_key)
            
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up services: {e}")
            raise
    
    async def prepare_test_data(self, max_files: int = 10):
        """Prepare test data by processing sample files"""
        logger.info(f"Preparing test data from {max_files} files...")
        
        try:
            # Get sample files
            files = await self.filesystem_client.list_vault_files()
            test_files = files[:max_files]
            
            logger.info(f"Processing {len(test_files)} files...")
            
            all_chunks = []
            for file_info in test_files:
                file_path = file_info['path']
                file_data = await self.filesystem_client.get_file_content(file_path)
                
                # Process with hybrid chunking
                chunks = self.content_processor.chunk_content(
                    content=file_data['content'],
                    file_metadata=file_data['metadata'],
                    path=file_path
                )
                all_chunks.extend(chunks)
            
            logger.info(f"Generated {len(all_chunks)} chunks")
            
            # Generate embeddings
            chunk_texts = [chunk['content'] for chunk in all_chunks]
            embeddings = self.embedding_service.batch_generate_embeddings(chunk_texts)
            
            # Store in ChromaDB
            self.chroma_service.store_embeddings(all_chunks, embeddings)
            
            logger.info("Test data preparation complete")
            return len(all_chunks)
            
        except Exception as e:
            logger.error(f"Error preparing test data: {e}")
            raise
    
    async def test_baseline_search(self, test_queries: List[str]) -> Dict[str, Any]:
        """Test baseline search performance without re-ranking"""
        logger.info("Testing baseline search performance...")
        
        results = {
            "query_results": {},
            "performance_metrics": {},
            "quality_metrics": {}
        }
        
        search_times = []
        similarity_scores = []
        
        for query in test_queries:
            logger.info(f"Testing query: {query}")
            
            start_time = time.time()
            
            # Test regular semantic search
            search_results = await self.search_service.search_similar(
                query=query,
                n_results=5,
                use_cache=False
            )
            
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            # Calculate quality metrics
            if search_results:
                avg_similarity = statistics.mean([r['similarity'] for r in search_results])
                similarity_scores.append(avg_similarity)
                
                results["query_results"][query] = {
                    "search_time": search_time,
                    "num_results": len(search_results),
                    "avg_similarity": avg_similarity,
                    "results": search_results[:3]  # Store top 3 for analysis
                }
            else:
                results["query_results"][query] = {
                    "search_time": search_time,
                    "num_results": 0,
                    "avg_similarity": 0.0,
                    "results": []
                }
        
        # Calculate overall metrics
        results["performance_metrics"] = {
            "avg_search_time": statistics.mean(search_times),
            "min_search_time": min(search_times),
            "max_search_time": max(search_times),
            "total_queries": len(test_queries)
        }
        
        results["quality_metrics"] = {
            "avg_similarity": statistics.mean(similarity_scores) if similarity_scores else 0.0,
            "min_similarity": min(similarity_scores) if similarity_scores else 0.0,
            "max_similarity": max(similarity_scores) if similarity_scores else 0.0
        }
        
        logger.info(f"Baseline search complete. Avg time: {results['performance_metrics']['avg_search_time']:.3f}s")
        return results
    
    async def test_reranked_search(self, test_queries: List[str]) -> Dict[str, Any]:
        """Test search performance with cross-encoder re-ranking"""
        logger.info("Testing re-ranked search performance...")
        
        results = {
            "query_results": {},
            "performance_metrics": {},
            "quality_metrics": {}
        }
        
        search_times = []
        final_scores = []
        cross_scores = []
        
        for query in test_queries:
            logger.info(f"Testing re-ranked query: {query}")
            
            start_time = time.time()
            
            # Test re-ranked search
            search_results = self.search_service.search_with_rerank(
                query=query,
                n_results=5,
                rerank_top_k=20
            )
            
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            # Calculate quality metrics
            if search_results:
                avg_final_score = statistics.mean([r['final_score'] for r in search_results])
                avg_cross_score = statistics.mean([r['cross_score'] for r in search_results])
                final_scores.append(avg_final_score)
                cross_scores.append(avg_cross_score)
                
                results["query_results"][query] = {
                    "search_time": search_time,
                    "num_results": len(search_results),
                    "avg_final_score": avg_final_score,
                    "avg_cross_score": avg_cross_score,
                    "results": search_results[:3]  # Store top 3 for analysis
                }
            else:
                results["query_results"][query] = {
                    "search_time": search_time,
                    "num_results": 0,
                    "avg_final_score": 0.0,
                    "avg_cross_score": 0.0,
                    "results": []
                }
        
        # Calculate overall metrics
        results["performance_metrics"] = {
            "avg_search_time": statistics.mean(search_times),
            "min_search_time": min(search_times),
            "max_search_time": max(search_times),
            "total_queries": len(test_queries)
        }
        
        results["quality_metrics"] = {
            "avg_final_score": statistics.mean(final_scores) if final_scores else 0.0,
            "avg_cross_score": statistics.mean(cross_scores) if cross_scores else 0.0,
            "min_final_score": min(final_scores) if final_scores else 0.0,
            "max_final_score": max(final_scores) if final_scores else 0.0
        }
        
        logger.info(f"Re-ranked search complete. Avg time: {results['performance_metrics']['avg_search_time']:.3f}s")
        return results
    
    async def test_hybrid_search(self, test_queries: List[str]) -> Dict[str, Any]:
        """Test hybrid search performance"""
        logger.info("Testing hybrid search performance...")
        
        results = {
            "query_results": {},
            "performance_metrics": {},
            "quality_metrics": {}
        }
        
        search_times = []
        combined_scores = []
        
        for query in test_queries:
            logger.info(f"Testing hybrid query: {query}")
            
            start_time = time.time()
            
            # Test hybrid search
            search_results = self.search_service.hybrid_search(
                query=query,
                n_results=5,
                include_keywords=True,
                include_tags=True
            )
            
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            # Calculate quality metrics
            if search_results:
                avg_combined_score = statistics.mean([r.get('combined_score', 0) for r in search_results])
                combined_scores.append(avg_combined_score)
                
                results["query_results"][query] = {
                    "search_time": search_time,
                    "num_results": len(search_results),
                    "avg_combined_score": avg_combined_score,
                    "results": search_results[:3]  # Store top 3 for analysis
                }
            else:
                results["query_results"][query] = {
                    "search_time": search_time,
                    "num_results": 0,
                    "avg_combined_score": 0.0,
                    "results": []
                }
        
        # Calculate overall metrics
        results["performance_metrics"] = {
            "avg_search_time": statistics.mean(search_times),
            "min_search_time": min(search_times),
            "max_search_time": max(search_times),
            "total_queries": len(test_queries)
        }
        
        results["quality_metrics"] = {
            "avg_combined_score": statistics.mean(combined_scores) if combined_scores else 0.0,
            "min_combined_score": min(combined_scores) if combined_scores else 0.0,
            "max_combined_score": max(combined_scores) if combined_scores else 0.0
        }
        
        logger.info(f"Hybrid search complete. Avg time: {results['performance_metrics']['avg_search_time']:.3f}s")
        return results
    
    def compare_results(self, baseline: Dict, optimized: Dict) -> Dict[str, Any]:
        """Compare baseline and optimized results"""
        logger.info("Comparing baseline vs optimized results...")
        
        comparison = {
            "performance_improvement": {},
            "quality_improvement": {},
            "overall_improvement": {}
        }
        
        # Performance comparison
        baseline_time = baseline["performance_metrics"]["avg_search_time"]
        optimized_time = optimized["performance_metrics"]["avg_search_time"]
        
        time_improvement = ((baseline_time - optimized_time) / baseline_time) * 100
        
        comparison["performance_improvement"] = {
            "baseline_time": baseline_time,
            "optimized_time": optimized_time,
            "time_improvement_percent": time_improvement,
            "faster": optimized_time < baseline_time
        }
        
        # Quality comparison (if applicable)
        if "avg_similarity" in baseline["quality_metrics"] and "avg_final_score" in optimized["quality_metrics"]:
            baseline_quality = baseline["quality_metrics"]["avg_similarity"]
            optimized_quality = optimized["quality_metrics"]["avg_final_score"]
            
            quality_improvement = ((optimized_quality - baseline_quality) / baseline_quality) * 100
            
            comparison["quality_improvement"] = {
                "baseline_quality": baseline_quality,
                "optimized_quality": optimized_quality,
                "quality_improvement_percent": quality_improvement,
                "better": optimized_quality > baseline_quality
            }
        
        # Overall assessment
        comparison["overall_improvement"] = {
            "performance_better": comparison["performance_improvement"]["faster"],
            "quality_better": comparison["quality_improvement"].get("better", False),
            "recommendation": self._generate_recommendation(comparison)
        }
        
        return comparison
    
    def _generate_recommendation(self, comparison: Dict) -> str:
        """Generate recommendation based on comparison results"""
        perf_better = comparison["performance_improvement"]["faster"]
        quality_better = comparison["quality_improvement"].get("better", False)
        
        if perf_better and quality_better:
            return "EXCELLENT: Both performance and quality improved significantly"
        elif quality_better:
            return "GOOD: Quality improved, performance may have slight overhead"
        elif perf_better:
            return "ACCEPTABLE: Performance improved, quality maintained"
        else:
            return "REVIEW: Both performance and quality need improvement"
    
    async def run_comprehensive_test(self):
        """Run comprehensive performance test suite"""
        logger.info("Starting comprehensive performance test suite...")
        
        # Test queries covering different types
        test_queries = [
            "machine learning algorithms",
            "data analysis techniques",
            "python programming",
            "artificial intelligence",
            "database optimization",
            "performance testing",
            "API development",
            "cloud computing",
            "software architecture",
            "debugging techniques"
        ]
        
        try:
            # Setup services
            await self.setup_services()
            
            # Prepare test data
            num_chunks = await self.prepare_test_data(max_files=15)
            logger.info(f"Test data prepared: {num_chunks} chunks")
            
            # Test 1: Baseline search
            logger.info("\n" + "="*60)
            logger.info("TEST 1: BASELINE SEARCH PERFORMANCE")
            logger.info("="*60)
            baseline_results = await self.test_baseline_search(test_queries)
            self.test_results["baseline"] = baseline_results
            
            # Test 2: Re-ranked search
            logger.info("\n" + "="*60)
            logger.info("TEST 2: RE-RANKED SEARCH PERFORMANCE")
            logger.info("="*60)
            reranked_results = await self.test_reranked_search(test_queries)
            self.test_results["optimized"] = reranked_results
            
            # Test 3: Hybrid search
            logger.info("\n" + "="*60)
            logger.info("TEST 3: HYBRID SEARCH PERFORMANCE")
            logger.info("="*60)
            hybrid_results = await self.test_hybrid_search(test_queries)
            self.test_results["hybrid"] = hybrid_results
            
            # Compare results
            logger.info("\n" + "="*60)
            logger.info("PERFORMANCE COMPARISON")
            logger.info("="*60)
            comparison = self.compare_results(baseline_results, reranked_results)
            self.test_results["comparisons"] = comparison
            
            # Generate report
            self.generate_performance_report()
            
            logger.info("Comprehensive performance test complete!")
            
        except Exception as e:
            logger.error(f"Error in comprehensive test: {e}")
            raise
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        logger.info("Generating performance report...")
        
        report = {
            "test_summary": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "test_queries": len(self.test_results["baseline"]["query_results"]),
                "total_chunks": "N/A"  # Will be filled from test data
            },
            "baseline_performance": self.test_results["baseline"]["performance_metrics"],
            "optimized_performance": self.test_results["optimized"]["performance_metrics"],
            "hybrid_performance": self.test_results["hybrid"]["performance_metrics"],
            "comparison": self.test_results["comparisons"],
            "recommendations": self._generate_recommendations()
        }
        
        # Save report
        report_path = "performance_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Performance report saved to: {report_path}")
        
        # Print summary
        self._print_performance_summary(report)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        comparison = self.test_results["comparisons"]
        
        if comparison["performance_improvement"]["faster"]:
            recommendations.append("✅ Performance improved - continue using optimized search")
        else:
            recommendations.append("⚠️ Performance degraded - review optimization implementation")
        
        if comparison["quality_improvement"].get("better", False):
            recommendations.append("✅ Quality improved - cross-encoder re-ranking is effective")
        else:
            recommendations.append("⚠️ Quality needs improvement - consider tuning re-ranking weights")
        
        recommendations.append("🔧 Consider implementing caching for frequently accessed queries")
        recommendations.append("📊 Monitor memory usage with cross-encoder model")
        recommendations.append("🎯 Fine-tune re-ranking weights based on domain-specific data")
        
        return recommendations
    
    def _print_performance_summary(self, report: Dict):
        """Print performance summary to console"""
        print("\n" + "="*80)
        print("PERFORMANCE TEST SUMMARY")
        print("="*80)
        
        baseline = report["baseline_performance"]
        optimized = report["optimized_performance"]
        hybrid = report["hybrid_performance"]
        comparison = report["comparison"]
        
        print(f"\n📊 BASELINE PERFORMANCE:")
        print(f"   Average Search Time: {baseline['avg_search_time']:.3f}s")
        print(f"   Min Search Time: {baseline['min_search_time']:.3f}s")
        print(f"   Max Search Time: {baseline['max_search_time']:.3f}s")
        
        print(f"\n🚀 OPTIMIZED PERFORMANCE (Re-ranked):")
        print(f"   Average Search Time: {optimized['avg_search_time']:.3f}s")
        print(f"   Min Search Time: {optimized['min_search_time']:.3f}s")
        print(f"   Max Search Time: {optimized['max_search_time']:.3f}s")
        
        print(f"\n🔀 HYBRID PERFORMANCE:")
        print(f"   Average Search Time: {hybrid['avg_search_time']:.3f}s")
        print(f"   Min Search Time: {hybrid['min_search_time']:.3f}s")
        print(f"   Max Search Time: {hybrid['max_search_time']:.3f}s")
        
        print(f"\n📈 IMPROVEMENTS:")
        print(f"   Time Improvement: {comparison['performance_improvement']['time_improvement_percent']:.1f}%")
        print(f"   Performance Better: {comparison['performance_improvement']['faster']}")
        print(f"   Quality Better: {comparison['quality_improvement'].get('better', 'N/A')}")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"   {comparison['overall_improvement']['recommendation']}")
        
        print("\n" + "="*80)

async def main():
    """Main function to run performance tests"""
    # Configuration
    vault_path = "D:/Nomade Milionario"  # Update with your vault path
    chroma_db_path = "./test_performance_chroma_db"
    
    # Initialize tester
    tester = PerformanceTester(vault_path, chroma_db_path)
    
    try:
        # Run comprehensive test
        await tester.run_comprehensive_test()
        
    except Exception as e:
        logger.error(f"Performance test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

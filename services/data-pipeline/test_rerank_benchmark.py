#!/usr/bin/env python3
"""
Comprehensive benchmark for cross-encoder re-ranking functionality
"""
import asyncio
import logging
import sys
import os
import time
import statistics
from datetime import datetime
from typing import List, Dict, Any

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

class RerankBenchmark:
    """Comprehensive benchmark for re-ranking functionality"""
    
    def __init__(self):
        self.chroma_service = None
        self.embedding_service = None
        self.search_service = None
        self.test_queries = [
            "artificial intelligence machine learning",
            "data engineering pipeline architecture",
            "vector database embeddings similarity",
            "context engineering prompt optimization",
            "hybrid search semantic keyword",
            "cross-encoder re-ranking precision",
            "ChromaDB HNSW optimization",
            "batch processing performance",
            "metadata filtering enrichment",
            "content chunking strategies"
        ]
        
    async def initialize_services(self):
        """Initialize all services for benchmarking"""
        logger.info("🚀 Initializing services for re-ranking benchmark...")
        
        # Use the optimized collection from our previous tests
        self.chroma_service = ChromaService(
            collection_name="test_batch_200",  # Use the largest collection
            persist_directory="./test_chroma_db_optimized",
            embedding_model="all-MiniLM-L6-v2",
            optimize_for_large_vault=True
        )
        
        self.embedding_service = EmbeddingService(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.search_service = SemanticSearchService(
            chroma_service=self.chroma_service,
            embedding_service=self.embedding_service
        )
        
        logger.info("✅ Services initialized successfully")
        
    def check_collection_status(self):
        """Check the current collection status"""
        try:
            count = self.chroma_service.collection.count()
            logger.info(f"📊 Collection contains {count} documents")
            return count
        except Exception as e:
            logger.error(f"❌ Error checking collection status: {e}")
            return 0
            
    def benchmark_regular_search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Benchmark regular semantic search"""
        start_time = time.time()
        
        try:
            results = self.search_service.search_similar(query, n_results=n_results)
            search_time = time.time() - start_time
            
            return {
                "method": "regular_search",
                "query": query,
                "results_count": len(results),
                "search_time_ms": search_time * 1000,
                "results": results,
                "success": True
            }
        except Exception as e:
            logger.error(f"❌ Regular search failed for query '{query}': {e}")
            return {
                "method": "regular_search",
                "query": query,
                "results_count": 0,
                "search_time_ms": 0,
                "results": [],
                "success": False,
                "error": str(e)
            }
    
    def benchmark_rerank_search(self, query: str, n_results: int = 5, rerank_top_k: int = 20) -> Dict[str, Any]:
        """Benchmark re-ranked search"""
        start_time = time.time()
        
        try:
            results = self.search_service.search_with_rerank(
                query=query, 
                n_results=n_results, 
                rerank_top_k=rerank_top_k
            )
            search_time = time.time() - start_time
            
            return {
                "method": "rerank_search",
                "query": query,
                "results_count": len(results),
                "search_time_ms": search_time * 1000,
                "rerank_top_k": rerank_top_k,
                "results": results,
                "success": True
            }
        except Exception as e:
            logger.error(f"❌ Re-rank search failed for query '{query}': {e}")
            return {
                "method": "rerank_search",
                "query": query,
                "results_count": 0,
                "search_time_ms": 0,
                "rerank_top_k": rerank_top_k,
                "results": [],
                "success": False,
                "error": str(e)
            }
    
    def analyze_result_quality(self, regular_results: List[Dict], rerank_results: List[Dict]) -> Dict[str, Any]:
        """Analyze the quality difference between regular and re-ranked results"""
        if not regular_results or not rerank_results:
            return {"analysis": "insufficient_data"}
            
        # Extract similarity scores
        regular_scores = [r.get('similarity', 0) for r in regular_results]
        rerank_scores = [r.get('final_score', 0) for r in rerank_results]
        
        # Calculate statistics
        analysis = {
            "regular_search": {
                "avg_similarity": statistics.mean(regular_scores) if regular_scores else 0,
                "max_similarity": max(regular_scores) if regular_scores else 0,
                "min_similarity": min(regular_scores) if regular_scores else 0,
                "score_variance": statistics.variance(regular_scores) if len(regular_scores) > 1 else 0
            },
            "rerank_search": {
                "avg_final_score": statistics.mean(rerank_scores) if rerank_scores else 0,
                "max_final_score": max(rerank_scores) if rerank_scores else 0,
                "min_final_score": min(rerank_scores) if rerank_scores else 0,
                "score_variance": statistics.variance(rerank_scores) if len(rerank_scores) > 1 else 0
            }
        }
        
        # Calculate improvement metrics
        if analysis["regular_search"]["avg_similarity"] > 0:
            score_improvement = (
                analysis["rerank_search"]["avg_final_score"] - 
                analysis["regular_search"]["avg_similarity"]
            ) / analysis["regular_search"]["avg_similarity"] * 100
            analysis["score_improvement_percent"] = score_improvement
        else:
            analysis["score_improvement_percent"] = 0
            
        return analysis
    
    async def run_comprehensive_benchmark(self):
        """Run comprehensive benchmark comparing regular vs re-ranked search"""
        logger.info("🎯 Starting Comprehensive Re-Ranking Benchmark")
        logger.info("=" * 80)
        
        # Check collection status
        doc_count = self.check_collection_status()
        if doc_count == 0:
            logger.error("❌ No documents in collection. Cannot run benchmark.")
            return
            
        logger.info(f"📊 Testing with {len(self.test_queries)} queries against {doc_count} documents")
        
        # Initialize results storage
        benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "collection_size": doc_count,
            "test_queries": len(self.test_queries),
            "regular_search_results": [],
            "rerank_search_results": [],
            "comparison_analysis": []
        }
        
        # Run benchmarks for each query
        for i, query in enumerate(self.test_queries, 1):
            logger.info(f"\n🔍 Testing Query {i}/{len(self.test_queries)}: '{query}'")
            
            # Test regular search
            logger.info("  📊 Running regular search...")
            regular_result = self.benchmark_regular_search(query, n_results=5)
            benchmark_results["regular_search_results"].append(regular_result)
            
            # Test re-ranked search
            logger.info("  🎯 Running re-ranked search...")
            rerank_result = self.benchmark_rerank_search(query, n_results=5, rerank_top_k=20)
            benchmark_results["rerank_search_results"].append(rerank_result)
            
            # Analyze quality difference
            if regular_result["success"] and rerank_result["success"]:
                quality_analysis = self.analyze_result_quality(
                    regular_result["results"], 
                    rerank_result["results"]
                )
                benchmark_results["comparison_analysis"].append({
                    "query": query,
                    "analysis": quality_analysis
                })
                
                # Log results
                logger.info(f"    ✅ Regular: {regular_result['search_time_ms']:.2f}ms, {regular_result['results_count']} results")
                logger.info(f"    ✅ Re-rank: {rerank_result['search_time_ms']:.2f}ms, {rerank_result['results_count']} results")
                
                if "score_improvement_percent" in quality_analysis:
                    improvement = quality_analysis["score_improvement_percent"]
                    logger.info(f"    📈 Score improvement: {improvement:+.2f}%")
            else:
                logger.warning(f"    ⚠️  One or both searches failed for query: {query}")
        
        # Calculate overall statistics
        self.calculate_overall_statistics(benchmark_results)
        
        # Generate final report
        self.generate_benchmark_report(benchmark_results)
        
        return benchmark_results
    
    def calculate_overall_statistics(self, results: Dict[str, Any]):
        """Calculate overall benchmark statistics"""
        logger.info("\n📊 Calculating Overall Statistics")
        logger.info("=" * 50)
        
        # Regular search statistics
        regular_times = [r["search_time_ms"] for r in results["regular_search_results"] if r["success"]]
        regular_success_rate = len([r for r in results["regular_search_results"] if r["success"]]) / len(results["regular_search_results"]) * 100
        
        # Re-rank search statistics  
        rerank_times = [r["search_time_ms"] for r in results["rerank_search_results"] if r["success"]]
        rerank_success_rate = len([r for r in results["rerank_search_results"] if r["success"]]) / len(results["rerank_search_results"]) * 100
        
        # Performance comparison
        if regular_times and rerank_times:
            avg_regular_time = statistics.mean(regular_times)
            avg_rerank_time = statistics.mean(rerank_times)
            time_overhead = ((avg_rerank_time - avg_regular_time) / avg_regular_time) * 100
            
            logger.info(f"⏱️  Average Regular Search Time: {avg_regular_time:.2f}ms")
            logger.info(f"⏱️  Average Re-rank Search Time: {avg_rerank_time:.2f}ms")
            logger.info(f"📈 Time Overhead: {time_overhead:+.2f}%")
        
        # Success rates
        logger.info(f"✅ Regular Search Success Rate: {regular_success_rate:.1f}%")
        logger.info(f"✅ Re-rank Search Success Rate: {rerank_success_rate:.1f}%")
        
        # Quality improvements
        improvements = [a["analysis"].get("score_improvement_percent", 0) 
                       for a in results["comparison_analysis"] 
                       if "score_improvement_percent" in a["analysis"]]
        
        if improvements:
            avg_improvement = statistics.mean(improvements)
            max_improvement = max(improvements)
            min_improvement = min(improvements)
            
            logger.info(f"🎯 Average Score Improvement: {avg_improvement:+.2f}%")
            logger.info(f"🎯 Max Score Improvement: {max_improvement:+.2f}%")
            logger.info(f"🎯 Min Score Improvement: {min_improvement:+.2f}%")
        
        # Store statistics
        results["overall_statistics"] = {
            "regular_search": {
                "avg_time_ms": statistics.mean(regular_times) if regular_times else 0,
                "success_rate_percent": regular_success_rate
            },
            "rerank_search": {
                "avg_time_ms": statistics.mean(rerank_times) if rerank_times else 0,
                "success_rate_percent": rerank_success_rate
            },
            "performance": {
                "time_overhead_percent": time_overhead if regular_times and rerank_times else 0,
                "avg_score_improvement_percent": statistics.mean(improvements) if improvements else 0
            }
        }
    
    def generate_benchmark_report(self, results: Dict[str, Any]):
        """Generate comprehensive benchmark report"""
        logger.info("\n🎉 BENCHMARK REPORT")
        logger.info("=" * 80)
        
        stats = results.get("overall_statistics", {})
        
        logger.info(f"📅 Timestamp: {results['timestamp']}")
        logger.info(f"📊 Collection Size: {results['collection_size']} documents")
        logger.info(f"🔍 Test Queries: {results['test_queries']}")
        
        logger.info("\n📈 PERFORMANCE SUMMARY:")
        logger.info("-" * 40)
        
        if "regular_search" in stats:
            logger.info(f"Regular Search: {stats['regular_search']['avg_time_ms']:.2f}ms avg, {stats['regular_search']['success_rate_percent']:.1f}% success")
        
        if "rerank_search" in stats:
            logger.info(f"Re-rank Search: {stats['rerank_search']['avg_time_ms']:.2f}ms avg, {stats['rerank_search']['success_rate_percent']:.1f}% success")
        
        if "performance" in stats:
            perf = stats["performance"]
            logger.info(f"Time Overhead: {perf['time_overhead_percent']:+.2f}%")
            logger.info(f"Score Improvement: {perf['avg_score_improvement_percent']:+.2f}%")
        
        logger.info("\n🎯 RECOMMENDATIONS:")
        logger.info("-" * 40)
        
        if "performance" in stats:
            perf = stats["performance"]
            if perf["avg_score_improvement_percent"] > 5:
                logger.info("✅ SIGNIFICANT QUALITY IMPROVEMENT: Re-ranking provides substantial precision gains")
            elif perf["avg_score_improvement_percent"] > 0:
                logger.info("✅ MODERATE QUALITY IMPROVEMENT: Re-ranking provides modest precision gains")
            else:
                logger.info("⚠️  NO QUALITY IMPROVEMENT: Re-ranking may not be beneficial for this dataset")
            
            if perf["time_overhead_percent"] < 50:
                logger.info("✅ ACCEPTABLE PERFORMANCE OVERHEAD: Time cost is reasonable")
            elif perf["time_overhead_percent"] < 100:
                logger.info("⚠️  MODERATE PERFORMANCE OVERHEAD: Consider optimizing re-ranking parameters")
            else:
                logger.info("❌ HIGH PERFORMANCE OVERHEAD: Re-ranking may be too expensive for production use")

async def main():
    """Main benchmark execution"""
    benchmark = RerankBenchmark()
    
    try:
        await benchmark.initialize_services()
        results = await benchmark.run_comprehensive_benchmark()
        
        logger.info("\n🎉 BENCHMARK COMPLETED SUCCESSFULLY!")
        return results
        
    except Exception as e:
        logger.error(f"❌ Benchmark failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

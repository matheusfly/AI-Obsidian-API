#!/usr/bin/env python3
"""
CORRECTED Normalized Benchmark Script
Fixes all calculation issues and provides proper validation metrics
"""

import asyncio
import logging
import time
import json
import statistics
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
import sys
from datetime import datetime
from scipy import stats
import psutil
import os

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService
from src.search.search_service import SemanticSearchService
from src.search.improved_search_service import ImprovedSemanticSearchService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NormalizedBenchmark:
    """Corrected benchmark with proper quality score normalization and statistical validation"""
    
    def __init__(self, chroma_db_path: str = "./normalized_benchmark_chroma_db"):
        self.chroma_db_path = chroma_db_path
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Initialize services
        self.embedding_service = None
        self.chroma_service = None
        self.search_service = None
        self.improved_search_service = None
        
        # Benchmark results with proper metrics
        self.benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "normalized_comparisons": {},
            "statistical_validation": {},
            "ux_metrics": {},
            "cost_benefit_analysis": {},
            "recommendations": []
        }
        
        # Quality score normalization parameters
        self.quality_normalization = {
            "similarity": {"min": 0.0, "max": 1.0},
            "cross_encoder": {"min": -10.0, "max": 10.0},  # Estimated range
            "final_score": {"min": -10.0, "max": 10.0}     # Estimated range
        }
    
    def normalize_quality_score(self, raw_score: float, method_type: str) -> float:
        """Normalize quality scores to 0-1 scale for fair comparison"""
        if method_type == "similarity":
            return max(0.0, min(1.0, raw_score))  # Already 0-1, clamp to ensure range
        
        elif method_type in ["cross_encoder", "final_score"]:
            # Sigmoid normalization for cross-encoder scores
            normalized = 1 / (1 + np.exp(-raw_score))
            return max(0.0, min(1.0, normalized))
        
        else:
            logger.warning(f"Unknown method type: {method_type}, using raw score")
            return max(0.0, min(1.0, raw_score))
    
    def calculate_statistical_significance(self, baseline_scores: List[float], 
                                         improved_scores: List[float]) -> Dict[str, Any]:
        """Calculate statistical significance and confidence intervals"""
        try:
            # Paired t-test
            t_stat, p_value = stats.ttest_rel(baseline_scores, improved_scores)
            
            # Effect size (Cohen's d)
            pooled_std = np.sqrt((np.var(baseline_scores) + np.var(improved_scores)) / 2)
            cohens_d = (np.mean(improved_scores) - np.mean(baseline_scores)) / pooled_std
            
            # Confidence interval for mean difference
            diff_scores = np.array(improved_scores) - np.array(baseline_scores)
            mean_diff = np.mean(diff_scores)
            std_diff = np.std(diff_scores, ddof=1)
            n = len(diff_scores)
            se_diff = std_diff / np.sqrt(n)
            t_critical = stats.t.ppf(0.975, n-1)  # 95% confidence
            ci_lower = mean_diff - t_critical * se_diff
            ci_upper = mean_diff + t_critical * se_diff
            
            return {
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "effect_size": float(cohens_d),
                "mean_difference": float(mean_diff),
                "confidence_interval": [float(ci_lower), float(ci_upper)],
                "interpretation": self._interpret_effect_size(cohens_d)
            }
        except Exception as e:
            logger.error(f"Error calculating statistical significance: {e}")
            return {
                "p_value": 1.0,
                "significant": False,
                "effect_size": 0.0,
                "mean_difference": 0.0,
                "confidence_interval": [0.0, 0.0],
                "interpretation": "Error in calculation"
            }
    
    def _interpret_effect_size(self, cohens_d: float) -> str:
        """Interpret Cohen's d effect size"""
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"
    
    def calculate_ux_metrics(self, response_times: List[float]) -> Dict[str, Any]:
        """Calculate user experience metrics"""
        if not response_times:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "consistency": 0.0}
        
        response_times = np.array(response_times)
        
        return {
            "p50": float(np.percentile(response_times, 50)),  # Median
            "p95": float(np.percentile(response_times, 95)),  # 95th percentile
            "p99": float(np.percentile(response_times, 99)),  # 99th percentile
            "consistency": float(1 - (np.std(response_times) / np.mean(response_times))),
            "min_time": float(np.min(response_times)),
            "max_time": float(np.max(response_times)),
            "std_dev": float(np.std(response_times))
        }
    
    def calculate_memory_efficiency(self, memory_before: float, memory_after: float, 
                                  query_count: int) -> Dict[str, Any]:
        """Calculate memory efficiency metrics"""
        memory_used = memory_after - memory_before
        return {
            "memory_per_query": memory_used / query_count if query_count > 0 else 0,
            "total_memory_used": memory_used,
            "memory_efficiency": query_count / memory_used if memory_used > 0 else 0
        }
    
    def calculate_efficiency_ratio(self, quality_improvement: float, 
                                 performance_cost: float) -> float:
        """Calculate quality improvement per unit of performance cost"""
        if performance_cost <= 0:
            return float('inf') if quality_improvement > 0 else 0.0
        return quality_improvement / performance_cost
    
    async def setup_services(self):
        """Initialize all required services"""
        logger.info("Setting up normalized benchmark services...")
        
        try:
            # Initialize embedding service
            self.embedding_service = EmbeddingService(model_name=self.embedding_model)
            
            # Initialize ChromaDB service
            self.chroma_service = ChromaService(
                persist_directory=self.chroma_db_path,
                collection_name="normalized_benchmark",
                embedding_model=self.embedding_model
            )
            
            # Initialize standard search service
            self.search_service = SemanticSearchService(
                chroma_service=self.chroma_service,
                embedding_service=self.embedding_service
            )
            
            # Initialize improved search service
            self.improved_search_service = ImprovedSemanticSearchService(
                chroma_service=self.chroma_service,
                embedding_service=self.embedding_service
            )
            
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up services: {e}")
            raise
    
    async def prepare_test_data(self):
        """Prepare comprehensive test data"""
        logger.info("Preparing normalized benchmark test data...")
        
        # Comprehensive test documents
        test_documents = [
            {
                "content": "Machine learning algorithms are computational methods that enable computers to learn patterns from data without being explicitly programmed. Popular algorithms include linear regression, decision trees, random forests, support vector machines, and neural networks.",
                "path": "ml/algorithms.md",
                "heading": "Machine Learning Algorithms",
                "chunk_index": 0,
                "chunk_token_count": 45,
                "file_tags": "machine_learning,algorithms,ai",
                "file_modified": "2025-01-09",
                "topic": "machine_learning",
                "type": "algorithms"
            },
            {
                "content": "Python is a versatile programming language widely used in data science, machine learning, web development, and automation. Its simple syntax, extensive libraries, and strong community support make it ideal for both beginners and professionals.",
                "path": "programming/python.md",
                "heading": "Python Programming",
                "chunk_index": 0,
                "chunk_token_count": 35,
                "file_tags": "python,programming,data_science",
                "file_modified": "2025-01-09",
                "topic": "python",
                "type": "programming"
            },
            {
                "content": "Data analysis techniques involve collecting, cleaning, processing, and interpreting data to extract meaningful insights. Common techniques include statistical analysis, data visualization, exploratory data analysis, and predictive modeling.",
                "path": "data/analysis.md",
                "heading": "Data Analysis Techniques",
                "chunk_index": 0,
                "chunk_token_count": 30,
                "file_tags": "data_analysis,statistics,techniques",
                "file_modified": "2025-01-09",
                "topic": "data_analysis",
                "type": "techniques"
            },
            {
                "content": "Database optimization involves improving query performance, indexing strategies, and data storage efficiency. Key techniques include proper indexing, query optimization, database normalization, and caching strategies.",
                "path": "infrastructure/database.md",
                "heading": "Database Optimization",
                "chunk_index": 0,
                "chunk_token_count": 28,
                "file_tags": "database,optimization,performance",
                "file_modified": "2025-01-09",
                "topic": "database",
                "type": "optimization"
            },
            {
                "content": "API development requires understanding REST principles, authentication mechanisms, error handling, and documentation standards. Modern APIs use JSON for data exchange and implement proper HTTP status codes.",
                "path": "development/api.md",
                "heading": "API Development",
                "chunk_index": 0,
                "chunk_token_count": 25,
                "file_tags": "api,development,web_services",
                "file_modified": "2025-01-09",
                "topic": "api",
                "type": "development"
            }
        ]
        
        try:
            # Generate embeddings
            documents = [doc["content"] for doc in test_documents]
            embeddings = self.embedding_service.batch_generate_embeddings(documents)
            
            # Store in ChromaDB
            self.chroma_service.store_embeddings(test_documents, embeddings)
            
            logger.info(f"Stored {len(test_documents)} test documents")
            return len(test_documents)
            
        except Exception as e:
            logger.error(f"Error preparing test data: {e}")
            raise
    
    async def run_normalized_search_benchmark(self, test_name: str, search_func, 
                                            queries: List[str]) -> Dict[str, Any]:
        """Run a search benchmark with proper quality score normalization"""
        logger.info(f"Running {test_name} normalized benchmark...")
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        results = {
            "test_name": test_name,
            "queries": {},
            "performance": {},
            "quality": {},
            "ux_metrics": {},
            "memory_efficiency": {}
        }
        
        search_times = []
        quality_scores = []
        normalized_scores = []
        
        for query in queries:
            logger.info(f"Testing {test_name} query: {query}")
            
            start_time = time.time()
            
            # Run the search function
            search_results = await search_func(query)
            
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            if search_results:
                # Determine quality score type and normalize
                if 'final_score' in search_results[0]:
                    raw_scores = [r['final_score'] for r in search_results]
                    method_type = "final_score"
                elif 'cross_score' in search_results[0]:
                    raw_scores = [r['cross_score'] for r in search_results]
                    method_type = "cross_encoder"
                elif 'similarity' in search_results[0]:
                    raw_scores = [r['similarity'] for r in search_results]
                    method_type = "similarity"
                else:
                    raw_scores = [0.0] * len(search_results)
                    method_type = "unknown"
                
                # Calculate normalized quality scores
                normalized_query_scores = [self.normalize_quality_score(score, method_type) 
                                        for score in raw_scores]
                
                avg_quality = statistics.mean(raw_scores)
                avg_normalized = statistics.mean(normalized_query_scores)
                
                quality_scores.append(avg_quality)
                normalized_scores.append(avg_normalized)
                
                results["queries"][query] = {
                    "search_time": search_time,
                    "num_results": len(search_results),
                    "avg_quality_score": avg_quality,
                    "avg_normalized_score": avg_normalized,
                    "method_type": method_type,
                    "top_result": search_results[0]["content"][:100] + "..." if search_results else ""
                }
            else:
                quality_scores.append(0.0)
                normalized_scores.append(0.0)
                
                results["queries"][query] = {
                    "search_time": search_time,
                    "num_results": 0,
                    "avg_quality_score": 0.0,
                    "avg_normalized_score": 0.0,
                    "method_type": "none",
                    "top_result": ""
                }
        
        # Get final memory usage
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        
        # Calculate comprehensive metrics
        results["performance"] = {
            "avg_search_time": statistics.mean(search_times),
            "min_search_time": min(search_times),
            "max_search_time": max(search_times),
            "total_queries": len(queries)
        }
        
        results["quality"] = {
            "avg_quality_score": statistics.mean(quality_scores),
            "avg_normalized_score": statistics.mean(normalized_scores),
            "min_quality_score": min(quality_scores),
            "max_quality_score": max(quality_scores),
            "quality_consistency": 1 - (statistics.stdev(quality_scores) / statistics.mean(quality_scores)) if quality_scores else 0
        }
        
        results["ux_metrics"] = self.calculate_ux_metrics(search_times)
        results["memory_efficiency"] = self.calculate_memory_efficiency(
            memory_before, memory_after, len(queries)
        )
        
        logger.info(f"{test_name} complete. Avg time: {results['performance']['avg_search_time']:.3f}s, "
                   f"Avg normalized quality: {results['quality']['avg_normalized_score']:.3f}")
        return results
    
    async def run_normalized_benchmark(self):
        """Run comprehensive normalized benchmark"""
        logger.info("Starting normalized benchmark with proper quality score normalization...")
        
        # Test queries
        test_queries = [
            "machine learning algorithms",
            "python programming language",
            "data analysis techniques",
            "database optimization methods",
            "API development best practices"
        ]
        
        try:
            # Setup services
            await self.setup_services()
            await self.prepare_test_data()
            
            # Test 1: Baseline Search
            logger.info("\n" + "="*60)
            logger.info("TEST 1: BASELINE SEARCH (Normalized)")
            logger.info("="*60)
            baseline_results = await self.run_normalized_search_benchmark(
                "Baseline Search",
                lambda q: self.search_service.search_similar(q, n_results=5, use_cache=False, expand_query=False),
                test_queries
            )
            self.benchmark_results["tests"]["baseline"] = baseline_results
            
            # Test 2: Improved Re-ranked Search
            logger.info("\n" + "="*60)
            logger.info("TEST 2: IMPROVED RE-RANKED SEARCH (Normalized)")
            logger.info("="*60)
            improved_reranked_results = await self.run_normalized_search_benchmark(
                "Improved Re-ranked Search",
                lambda q: self.improved_search_service.search_with_improved_rerank(q, n_results=5, rerank_top_k=10),
                test_queries
            )
            self.benchmark_results["tests"]["improved_reranked"] = improved_reranked_results
            
            # Test 3: Hybrid Search
            logger.info("\n" + "="*60)
            logger.info("TEST 3: HYBRID SEARCH (Normalized)")
            logger.info("="*60)
            hybrid_results = await self.run_normalized_search_benchmark(
                "Hybrid Search",
                lambda q: self.search_service.hybrid_search(q, n_results=5, include_keywords=True, include_tags=True),
                test_queries
            )
            self.benchmark_results["tests"]["hybrid"] = hybrid_results
            
            # Calculate normalized comparisons
            self.benchmark_results["normalized_comparisons"] = self._calculate_normalized_comparisons()
            
            # Statistical validation
            self.benchmark_results["statistical_validation"] = self._calculate_statistical_validation()
            
            # UX metrics summary
            self.benchmark_results["ux_metrics"] = self._calculate_ux_summary()
            
            # Cost-benefit analysis
            self.benchmark_results["cost_benefit_analysis"] = self._calculate_cost_benefit()
            
            # Generate recommendations
            self.benchmark_results["recommendations"] = self._generate_normalized_recommendations()
            
            # Generate report
            self.generate_normalized_report()
            
            logger.info("Normalized benchmark complete!")
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _calculate_normalized_comparisons(self) -> Dict[str, Any]:
        """Calculate normalized comparisons between all methods"""
        logger.info("Calculating normalized comparisons...")
        
        comparisons = {}
        tests = self.benchmark_results["tests"]
        
        # Performance comparison
        performance_comparison = {}
        for test_name, test_results in tests.items():
            performance_comparison[test_name] = {
                "avg_search_time": test_results["performance"]["avg_search_time"],
                "avg_normalized_quality": test_results["quality"]["avg_normalized_score"],
                "ux_p95": test_results["ux_metrics"]["p95"],
                "memory_per_query": test_results["memory_efficiency"]["memory_per_query"]
            }
        
        # Quality comparison (now normalized!)
        quality_comparison = {}
        for test_name, test_results in tests.items():
            quality_comparison[test_name] = {
                "avg_normalized_score": test_results["quality"]["avg_normalized_score"],
                "quality_consistency": test_results["quality"]["quality_consistency"],
                "quality_range": test_results["quality"]["max_quality_score"] - test_results["quality"]["min_quality_score"]
            }
        
        # Efficiency ratio comparison
        efficiency_comparison = {}
        baseline = tests["baseline"]
        for test_name, test_results in tests.items():
            if test_name != "baseline":
                quality_improvement = (test_results["quality"]["avg_normalized_score"] - 
                                    baseline["quality"]["avg_normalized_score"])
                performance_cost = (test_results["performance"]["avg_search_time"] - 
                                 baseline["performance"]["avg_search_time"])
                
                efficiency_comparison[test_name] = {
                    "quality_improvement": quality_improvement,
                    "performance_cost": performance_cost,
                    "efficiency_ratio": self.calculate_efficiency_ratio(quality_improvement, performance_cost),
                    "better_than_baseline": quality_improvement > 0 and performance_cost < 0.1
                }
        
        comparisons = {
            "performance": performance_comparison,
            "quality": quality_comparison,
            "efficiency": efficiency_comparison
        }
        
        return comparisons
    
    def _calculate_statistical_validation(self) -> Dict[str, Any]:
        """Calculate statistical validation for all comparisons"""
        logger.info("Calculating statistical validation...")
        
        validation = {}
        tests = self.benchmark_results["tests"]
        
        # Compare each method against baseline
        baseline = tests["baseline"]
        baseline_scores = [baseline["queries"][q]["avg_normalized_score"] for q in baseline["queries"]]
        
        for test_name, test_results in tests.items():
            if test_name != "baseline":
                test_scores = [test_results["queries"][q]["avg_normalized_score"] for q in test_results["queries"]]
                
                validation[f"{test_name}_vs_baseline"] = self.calculate_statistical_significance(
                    baseline_scores, test_scores
                )
        
        return validation
    
    def _calculate_ux_summary(self) -> Dict[str, Any]:
        """Calculate UX metrics summary"""
        logger.info("Calculating UX metrics summary...")
        
        ux_summary = {}
        tests = self.benchmark_results["tests"]
        
        for test_name, test_results in tests.items():
            ux_summary[test_name] = {
                "median_response_time": test_results["ux_metrics"]["p50"],
                "p95_response_time": test_results["ux_metrics"]["p95"],
                "consistency": test_results["ux_metrics"]["consistency"],
                "memory_efficiency": test_results["memory_efficiency"]["memory_per_query"]
            }
        
        return ux_summary
    
    def _calculate_cost_benefit(self) -> Dict[str, Any]:
        """Calculate cost-benefit analysis"""
        logger.info("Calculating cost-benefit analysis...")
        
        cost_benefit = {}
        tests = self.benchmark_results["tests"]
        baseline = tests["baseline"]
        
        for test_name, test_results in tests.items():
            if test_name != "baseline":
                quality_improvement = (test_results["quality"]["avg_normalized_score"] - 
                                    baseline["quality"]["avg_normalized_score"])
                performance_cost = (test_results["performance"]["avg_search_time"] - 
                                 baseline["performance"]["avg_search_time"])
                memory_cost = test_results["memory_efficiency"]["memory_per_query"]
                
                # Simple cost-benefit calculation
                benefit_score = quality_improvement * 100  # Quality improvement value
                cost_score = (performance_cost * 10) + (memory_cost * 0.1)  # Performance + memory cost
                
                cost_benefit[test_name] = {
                    "quality_benefit": quality_improvement,
                    "performance_cost": performance_cost,
                    "memory_cost": memory_cost,
                    "benefit_score": benefit_score,
                    "cost_score": cost_score,
                    "roi": benefit_score / cost_score if cost_score > 0 else float('inf'),
                    "recommended": benefit_score > cost_score and quality_improvement > 0.01
                }
        
        return cost_benefit
    
    def _generate_normalized_recommendations(self) -> List[str]:
        """Generate recommendations based on normalized results"""
        recommendations = []
        tests = self.benchmark_results["tests"]
        comparisons = self.benchmark_results["normalized_comparisons"]
        validation = self.benchmark_results["statistical_validation"]
        cost_benefit = self.benchmark_results["cost_benefit_analysis"]
        
        # Find best performing methods
        best_quality = max(tests.items(), key=lambda x: x[1]["quality"]["avg_normalized_score"])
        fastest_test = min(tests.items(), key=lambda x: x[1]["performance"]["avg_search_time"])
        best_efficiency = max(comparisons["efficiency"].items(), key=lambda x: x[1]["efficiency_ratio"])
        
        recommendations.append(f"🏆 Best Quality: {best_quality[0]} (Normalized Score: {best_quality[1]['quality']['avg_normalized_score']:.3f})")
        recommendations.append(f"⚡ Fastest: {fastest_test[0]} (Time: {fastest_test[1]['performance']['avg_search_time']:.3f}s)")
        recommendations.append(f"💡 Most Efficient: {best_efficiency[0]} (Efficiency Ratio: {best_efficiency[1]['efficiency_ratio']:.3f})")
        
        # Statistical significance recommendations
        for comparison, stats in validation.items():
            if stats["significant"]:
                recommendations.append(f"✅ {comparison}: Statistically significant improvement (p={stats['p_value']:.3f})")
            else:
                recommendations.append(f"⚠️ {comparison}: Not statistically significant (p={stats['p_value']:.3f})")
        
        # Cost-benefit recommendations
        for method, cb in cost_benefit.items():
            if cb["recommended"]:
                recommendations.append(f"💰 {method}: Recommended for production (ROI: {cb['roi']:.2f})")
            else:
                recommendations.append(f"❌ {method}: Not recommended (ROI: {cb['roi']:.2f})")
        
        return recommendations
    
    def generate_normalized_report(self):
        """Generate normalized benchmark report"""
        logger.info("Generating normalized benchmark report...")
        
        # Save detailed report
        report_path = "normalized_benchmark_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.benchmark_results, f, indent=2)
        
        logger.info(f"Normalized report saved to: {report_path}")
        
        # Print executive summary
        self._print_normalized_summary()
    
    def _print_normalized_summary(self):
        """Print executive summary of normalized benchmark results"""
        print("\n" + "="*80)
        print("NORMALIZED BENCHMARK EXECUTIVE SUMMARY")
        print("="*80)
        
        tests = self.benchmark_results["tests"]
        comparisons = self.benchmark_results["normalized_comparisons"]
        validation = self.benchmark_results["statistical_validation"]
        
        print(f"\n📊 NORMALIZED PERFORMANCE OVERVIEW:")
        print(f"   Test Date: {self.benchmark_results['timestamp']}")
        print(f"   Total Tests: {len(tests)}")
        print(f"   Quality Scores: Normalized to 0-1 scale")
        print(f"   Statistical Validation: Included")
        
        print(f"\n🏆 NORMALIZED RESULTS:")
        for test_name, test_results in tests.items():
            print(f"   {test_name}:")
            print(f"     Time: {test_results['performance']['avg_search_time']:.3f}s")
            print(f"     Normalized Quality: {test_results['quality']['avg_normalized_score']:.3f}")
            print(f"     P95 Response Time: {test_results['ux_metrics']['p95']:.3f}s")
            print(f"     Memory/Query: {test_results['memory_efficiency']['memory_per_query']:.2f}MB")
        
        print(f"\n📈 STATISTICAL VALIDATION:")
        for comparison, stats in validation.items():
            significance = "✅ Significant" if stats["significant"] else "❌ Not Significant"
            print(f"   {comparison}: {significance} (p={stats['p_value']:.3f}, effect={stats['interpretation']})")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(self.benchmark_results["recommendations"], 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "="*80)

async def main():
    """Main function"""
    benchmark = NormalizedBenchmark()
    await benchmark.run_normalized_benchmark()

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Comprehensive Performance Benchmark Script
Tests multiple performance improvements and generates detailed reports
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
from datetime import datetime

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

class ComprehensivePerformanceBenchmark:
    """Comprehensive performance benchmark for data pipeline optimizations"""
    
    def __init__(self, chroma_db_path: str = "./comprehensive_benchmark_chroma_db"):
        self.chroma_db_path = chroma_db_path
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Initialize services
        self.embedding_service = None
        self.chroma_service = None
        self.search_service = None
        self.improved_search_service = None
        
        # Benchmark results
        self.benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "comparisons": {},
            "recommendations": []
        }
        
    async def setup_services(self):
        """Initialize all required services"""
        logger.info("Setting up comprehensive benchmark services...")
        
        try:
            # Initialize embedding service
            self.embedding_service = EmbeddingService(model_name=self.embedding_model)
            
            # Initialize ChromaDB service
            self.chroma_service = ChromaService(
                persist_directory=self.chroma_db_path,
                collection_name="comprehensive_benchmark",
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
    
    async def prepare_comprehensive_test_data(self):
        """Prepare comprehensive test data with diverse content"""
        logger.info("Preparing comprehensive test data...")
        
        # Comprehensive test documents covering various domains
        test_documents = [
            # Machine Learning & AI
            {
                "content": "Machine learning algorithms are computational methods that enable computers to learn patterns from data without being explicitly programmed. Popular algorithms include linear regression, decision trees, random forests, support vector machines, and neural networks. Each algorithm has specific strengths and use cases in different domains like healthcare, finance, and technology.",
                "path": "ml/ml_algorithms.md",
                "heading": "Machine Learning Algorithms",
                "chunk_index": 0,
                "chunk_token_count": 45,
                "file_tags": "machine_learning,algorithms,ai,data_science",
                "file_modified": "2025-01-09",
                "topic": "machine_learning",
                "type": "algorithms"
            },
            {
                "content": "Deep learning is a subset of machine learning that uses artificial neural networks with multiple layers to model and understand complex patterns in data. It has revolutionized fields like computer vision, natural language processing, and speech recognition. Popular frameworks include TensorFlow, PyTorch, and Keras for building and training deep learning models.",
                "path": "ml/deep_learning.md",
                "heading": "Deep Learning Fundamentals",
                "chunk_index": 0,
                "chunk_token_count": 42,
                "file_tags": "deep_learning,neural_networks,ai,ml",
                "file_modified": "2025-01-09",
                "topic": "deep_learning",
                "type": "fundamentals"
            },
            # Programming Languages
            {
                "content": "Python is a versatile programming language widely used in data science, machine learning, web development, and automation. Its simple syntax, extensive libraries like NumPy, Pandas, and Scikit-learn, and strong community support make it ideal for both beginners and professionals. Python's readability and flexibility have made it the go-to language for AI and data analysis projects.",
                "path": "programming/python.md",
                "heading": "Python Programming Language",
                "chunk_index": 0,
                "chunk_token_count": 42,
                "file_tags": "python,programming,data_science,web_development",
                "file_modified": "2025-01-09",
                "topic": "python",
                "type": "programming"
            },
            {
                "content": "JavaScript is a high-level programming language primarily used for web development, both on the client-side and server-side. It enables interactive web pages, mobile app development with frameworks like React Native, and server-side development with Node.js. Modern JavaScript includes ES6+ features, async/await, and powerful frameworks like React, Vue, and Angular.",
                "path": "programming/javascript.md",
                "heading": "JavaScript Development",
                "chunk_index": 0,
                "chunk_token_count": 38,
                "file_tags": "javascript,web_development,frontend,backend",
                "file_modified": "2025-01-09",
                "topic": "javascript",
                "type": "programming"
            },
            # Data Analysis
            {
                "content": "Data analysis techniques involve collecting, cleaning, processing, and interpreting data to extract meaningful insights. Common techniques include statistical analysis, data visualization, exploratory data analysis (EDA), hypothesis testing, and predictive modeling. Tools like R, Python, SQL, and specialized software help analysts uncover patterns and trends in complex datasets.",
                "path": "data/data_analysis.md",
                "heading": "Data Analysis Techniques",
                "chunk_index": 0,
                "chunk_token_count": 38,
                "file_tags": "data_analysis,statistics,techniques,insights",
                "file_modified": "2025-01-09",
                "topic": "data_analysis",
                "type": "techniques"
            },
            {
                "content": "Data visualization is the graphical representation of information and data using visual elements like charts, graphs, and maps. Effective data visualization helps communicate insights clearly and efficiently. Popular tools include Matplotlib, Seaborn, Plotly, D3.js, and Tableau. Good visualization principles include choosing appropriate chart types, using color effectively, and maintaining clarity.",
                "path": "data/data_visualization.md",
                "heading": "Data Visualization Best Practices",
                "chunk_index": 0,
                "chunk_token_count": 36,
                "file_tags": "data_visualization,charts,graphs,insights",
                "file_modified": "2025-01-09",
                "topic": "data_visualization",
                "type": "best_practices"
            },
            # Database & Infrastructure
            {
                "content": "Database optimization involves improving query performance, indexing strategies, and data storage efficiency. Key techniques include proper indexing, query optimization, database normalization, partitioning, and caching. Performance monitoring tools help identify bottlenecks and optimize database operations for better application speed and reliability.",
                "path": "infrastructure/database_optimization.md",
                "heading": "Database Optimization Methods",
                "chunk_index": 0,
                "chunk_token_count": 35,
                "file_tags": "database,optimization,performance,sql",
                "file_modified": "2025-01-09",
                "topic": "database",
                "type": "optimization"
            },
            {
                "content": "Cloud computing provides scalable computing resources over the internet, including Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS). Major providers like AWS, Azure, and Google Cloud offer various services for storage, computing, networking, and specialized AI/ML tools. Cloud adoption enables businesses to scale efficiently and reduce infrastructure costs.",
                "path": "infrastructure/cloud_computing.md",
                "heading": "Cloud Computing Services",
                "chunk_index": 0,
                "chunk_token_count": 39,
                "file_tags": "cloud,infrastructure,aws,azure,scalability",
                "file_modified": "2025-01-09",
                "topic": "cloud",
                "type": "infrastructure"
            },
            # Software Development
            {
                "content": "API development requires understanding REST principles, authentication mechanisms, error handling, and documentation standards. Modern APIs use JSON for data exchange, implement proper HTTP status codes, and follow RESTful design patterns. Security considerations include API keys, OAuth, rate limiting, and input validation for building robust web services.",
                "path": "development/api_development.md",
                "heading": "API Development Best Practices",
                "chunk_index": 0,
                "chunk_token_count": 37,
                "file_tags": "api,development,web_services,rest",
                "file_modified": "2025-01-09",
                "topic": "api",
                "type": "development"
            },
            {
                "content": "Software architecture defines the high-level structure of software systems, including components, relationships, and design patterns. Common architectural patterns include microservices, monolithic, serverless, and event-driven architectures. Good architecture principles include separation of concerns, modularity, scalability, and maintainability to guide development teams.",
                "path": "development/software_architecture.md",
                "heading": "Software Architecture Patterns",
                "chunk_index": 0,
                "chunk_token_count": 36,
                "file_tags": "architecture,design_patterns,software,scalability",
                "file_modified": "2025-01-09",
                "topic": "architecture",
                "type": "design"
            },
            # Testing & Quality
            {
                "content": "Debugging techniques include using debuggers, logging, unit testing, and systematic problem-solving approaches. Effective debugging involves reproducing issues, isolating problems, using breakpoints, examining variables, and testing hypotheses. Modern development tools provide advanced debugging features like step-through execution, call stack analysis, and performance profiling.",
                "path": "testing/debugging_techniques.md",
                "heading": "Debugging Techniques and Tools",
                "chunk_index": 0,
                "chunk_token_count": 34,
                "file_tags": "debugging,testing,tools,problem_solving",
                "file_modified": "2025-01-09",
                "topic": "debugging",
                "type": "techniques"
            },
            {
                "content": "Performance testing evaluates system behavior under various load conditions to ensure applications meet speed, scalability, and stability requirements. Types include load testing, stress testing, volume testing, and spike testing. Tools like JMeter, LoadRunner, and custom scripts help simulate user loads and measure system performance metrics.",
                "path": "testing/performance_testing.md",
                "heading": "Performance Testing Strategies",
                "chunk_index": 0,
                "chunk_token_count": 33,
                "file_tags": "testing,performance,load_testing,scalability",
                "file_modified": "2025-01-09",
                "topic": "testing",
                "type": "performance"
            }
        ]
        
        try:
            # Generate embeddings
            documents = [doc["content"] for doc in test_documents]
            embeddings = self.embedding_service.batch_generate_embeddings(documents)
            
            # Store in ChromaDB
            self.chroma_service.store_embeddings(test_documents, embeddings)
            
            logger.info(f"Stored {len(test_documents)} comprehensive test documents")
            return len(test_documents)
            
        except Exception as e:
            logger.error(f"Error preparing test data: {e}")
            raise
    
    async def run_search_benchmark(self, test_name: str, search_func, queries: List[str]) -> Dict[str, Any]:
        """Run a search benchmark test"""
        logger.info(f"Running {test_name} benchmark...")
        
        results = {
            "test_name": test_name,
            "queries": {},
            "performance": {},
            "quality": {}
        }
        
        search_times = []
        quality_scores = []
        
        for query in queries:
            logger.info(f"Testing {test_name} query: {query}")
            
            start_time = time.time()
            
            # Run the search function
            search_results = await search_func(query)
            
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            if search_results:
                # Calculate quality metrics based on available scores
                if 'final_score' in search_results[0]:
                    avg_quality = statistics.mean([r['final_score'] for r in search_results])
                elif 'similarity' in search_results[0]:
                    avg_quality = statistics.mean([r['similarity'] for r in search_results])
                else:
                    avg_quality = 0.0
                
                quality_scores.append(avg_quality)
                
                results["queries"][query] = {
                    "search_time": search_time,
                    "num_results": len(search_results),
                    "avg_quality_score": avg_quality,
                    "top_result": search_results[0]["content"][:100] + "..." if search_results else ""
                }
            else:
                results["queries"][query] = {
                    "search_time": search_time,
                    "num_results": 0,
                    "avg_quality_score": 0.0,
                    "top_result": ""
                }
        
        # Calculate overall metrics
        results["performance"] = {
            "avg_search_time": statistics.mean(search_times),
            "min_search_time": min(search_times),
            "max_search_time": max(search_times),
            "total_queries": len(queries)
        }
        
        results["quality"] = {
            "avg_quality_score": statistics.mean(quality_scores) if quality_scores else 0.0,
            "min_quality_score": min(quality_scores) if quality_scores else 0.0,
            "max_quality_score": max(quality_scores) if quality_scores else 0.0
        }
        
        logger.info(f"{test_name} complete. Avg time: {results['performance']['avg_search_time']:.3f}s, Avg quality: {results['quality']['avg_quality_score']:.3f}")
        return results
    
    async def run_comprehensive_benchmark(self):
        """Run comprehensive performance benchmark"""
        logger.info("Starting comprehensive performance benchmark...")
        
        # Test queries covering different domains
        test_queries = [
            "machine learning algorithms",
            "python programming language",
            "data analysis techniques",
            "artificial intelligence overview",
            "database optimization methods",
            "API development best practices",
            "cloud computing services",
            "software architecture patterns",
            "debugging techniques",
            "performance testing strategies"
        ]
        
        try:
            # Setup services
            await self.setup_services()
            await self.prepare_comprehensive_test_data()
            
            # Test 1: Baseline Search (no query expansion)
            logger.info("\n" + "="*60)
            logger.info("TEST 1: BASELINE SEARCH (No Query Expansion)")
            logger.info("="*60)
            baseline_results = await self.run_search_benchmark(
                "Baseline Search",
                lambda q: self.search_service.search_similar(q, n_results=5, use_cache=False, expand_query=False),
                test_queries
            )
            self.benchmark_results["tests"]["baseline"] = baseline_results
            
            # Test 2: Baseline Search with Query Expansion
            logger.info("\n" + "="*60)
            logger.info("TEST 2: BASELINE SEARCH (With Query Expansion)")
            logger.info("="*60)
            baseline_expanded_results = await self.run_search_benchmark(
                "Baseline Search (Expanded)",
                lambda q: self.search_service.search_similar(q, n_results=5, use_cache=False, expand_query=True),
                test_queries
            )
            self.benchmark_results["tests"]["baseline_expanded"] = baseline_expanded_results
            
            # Test 3: Standard Re-ranked Search
            logger.info("\n" + "="*60)
            logger.info("TEST 3: STANDARD RE-RANKED SEARCH")
            logger.info("="*60)
            standard_reranked_results = await self.run_search_benchmark(
                "Standard Re-ranked Search",
                lambda q: self.search_service.search_with_rerank(q, n_results=5, rerank_top_k=10),
                test_queries
            )
            self.benchmark_results["tests"]["standard_reranked"] = standard_reranked_results
            
            # Test 4: Improved Re-ranked Search
            logger.info("\n" + "="*60)
            logger.info("TEST 4: IMPROVED RE-RANKED SEARCH")
            logger.info("="*60)
            improved_reranked_results = await self.run_search_benchmark(
                "Improved Re-ranked Search",
                lambda q: self.improved_search_service.search_with_improved_rerank(q, n_results=5, rerank_top_k=10),
                test_queries
            )
            self.benchmark_results["tests"]["improved_reranked"] = improved_reranked_results
            
            # Test 5: Hybrid Search
            logger.info("\n" + "="*60)
            logger.info("TEST 5: HYBRID SEARCH")
            logger.info("="*60)
            hybrid_results = await self.run_search_benchmark(
                "Hybrid Search",
                lambda q: self.search_service.hybrid_search(q, n_results=5, include_keywords=True, include_tags=True),
                test_queries
            )
            self.benchmark_results["tests"]["hybrid"] = hybrid_results
            
            # Compare all results
            logger.info("\n" + "="*60)
            logger.info("COMPREHENSIVE COMPARISON")
            logger.info("="*60)
            self.benchmark_results["comparisons"] = self._compare_all_results()
            
            # Generate recommendations
            self.benchmark_results["recommendations"] = self._generate_recommendations()
            
            # Generate comprehensive report
            self.generate_comprehensive_report()
            
            logger.info("Comprehensive performance benchmark complete!")
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _compare_all_results(self) -> Dict[str, Any]:
        """Compare all benchmark results"""
        logger.info("Comparing all benchmark results...")
        
        comparisons = {}
        tests = self.benchmark_results["tests"]
        
        # Performance comparison
        performance_comparison = {}
        for test_name, test_results in tests.items():
            performance_comparison[test_name] = {
                "avg_search_time": test_results["performance"]["avg_search_time"],
                "avg_quality_score": test_results["quality"]["avg_quality_score"],
                "total_queries": test_results["performance"]["total_queries"]
            }
        
        # Quality comparison
        quality_comparison = {}
        for test_name, test_results in tests.items():
            quality_comparison[test_name] = {
                "avg_quality_score": test_results["quality"]["avg_quality_score"],
                "quality_range": test_results["quality"]["max_quality_score"] - test_results["quality"]["min_quality_score"]
            }
        
        # Speed comparison
        speed_comparison = {}
        baseline_time = tests["baseline"]["performance"]["avg_search_time"]
        for test_name, test_results in tests.items():
            test_time = test_results["performance"]["avg_search_time"]
            speed_comparison[test_name] = {
                "avg_search_time": test_time,
                "speed_ratio": test_time / baseline_time,
                "faster_than_baseline": test_time < baseline_time
            }
        
        comparisons = {
            "performance": performance_comparison,
            "quality": quality_comparison,
            "speed": speed_comparison
        }
        
        return comparisons
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations based on benchmark results"""
        recommendations = []
        tests = self.benchmark_results["tests"]
        comparisons = self.benchmark_results["comparisons"]
        
        # Find best performing tests
        best_quality = max(tests.items(), key=lambda x: x[1]["quality"]["avg_quality_score"])
        fastest_test = min(tests.items(), key=lambda x: x[1]["performance"]["avg_search_time"])
        
        recommendations.append(f"🏆 Best Quality: {best_quality[0]} (Score: {best_quality[1]['quality']['avg_quality_score']:.3f})")
        recommendations.append(f"⚡ Fastest: {fastest_test[0]} (Time: {fastest_test[1]['performance']['avg_search_time']:.3f}s)")
        
        # Performance vs Quality analysis
        baseline = tests["baseline"]
        improved_reranked = tests["improved_reranked"]
        
        quality_improvement = improved_reranked["quality"]["avg_quality_score"] - baseline["quality"]["avg_quality_score"]
        time_increase = improved_reranked["performance"]["avg_search_time"] - baseline["performance"]["avg_search_time"]
        
        if quality_improvement > 0.1 and time_increase < 0.5:
            recommendations.append("✅ Improved Re-ranked Search provides significant quality improvement with acceptable performance cost")
        elif quality_improvement > 0.05:
            recommendations.append("⚠️ Improved Re-ranked Search provides quality improvement but consider performance impact")
        else:
            recommendations.append("❌ Improved Re-ranked Search may not provide sufficient quality improvement")
        
        # Query expansion analysis
        baseline_expanded = tests["baseline_expanded"]
        expansion_benefit = baseline_expanded["quality"]["avg_quality_score"] - baseline["quality"]["avg_quality_score"]
        
        if expansion_benefit > 0.05:
            recommendations.append("✅ Query expansion provides measurable quality improvement")
        else:
            recommendations.append("⚠️ Query expansion may not provide significant benefit for this dataset")
        
        # Hybrid search analysis
        hybrid = tests["hybrid"]
        hybrid_benefit = hybrid["quality"]["avg_quality_score"] - baseline["quality"]["avg_quality_score"]
        
        if hybrid_benefit > 0.03:
            recommendations.append("✅ Hybrid search provides quality improvement over baseline")
        else:
            recommendations.append("⚠️ Hybrid search may not provide significant benefit")
        
        # General recommendations
        recommendations.append("🔧 Consider implementing caching for frequently accessed queries")
        recommendations.append("📊 Monitor memory usage with cross-encoder models")
        recommendations.append("🎯 Fine-tune re-ranking weights based on domain-specific data")
        recommendations.append("🚀 Consider using GPU acceleration for cross-encoder models in production")
        
        return recommendations
    
    def generate_comprehensive_report(self):
        """Generate comprehensive performance report"""
        logger.info("Generating comprehensive performance report...")
        
        # Save detailed report
        report_path = "comprehensive_performance_benchmark_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.benchmark_results, f, indent=2)
        
        logger.info(f"Detailed report saved to: {report_path}")
        
        # Print executive summary
        self._print_executive_summary()
    
    def _print_executive_summary(self):
        """Print executive summary of benchmark results"""
        print("\n" + "="*80)
        print("COMPREHENSIVE PERFORMANCE BENCHMARK EXECUTIVE SUMMARY")
        print("="*80)
        
        tests = self.benchmark_results["tests"]
        comparisons = self.benchmark_results["comparisons"]
        
        print(f"\n📊 PERFORMANCE OVERVIEW:")
        print(f"   Test Date: {self.benchmark_results['timestamp']}")
        print(f"   Total Tests: {len(tests)}")
        print(f"   Total Queries: {tests['baseline']['performance']['total_queries']}")
        
        print(f"\n🏆 TOP PERFORMERS:")
        for test_name, test_results in tests.items():
            print(f"   {test_name}:")
            print(f"     Time: {test_results['performance']['avg_search_time']:.3f}s")
            print(f"     Quality: {test_results['quality']['avg_quality_score']:.3f}")
        
        print(f"\n📈 KEY INSIGHTS:")
        baseline = tests["baseline"]
        improved_reranked = tests["improved_reranked"]
        
        quality_improvement = improved_reranked["quality"]["avg_quality_score"] - baseline["quality"]["avg_quality_score"]
        time_increase = improved_reranked["performance"]["avg_search_time"] - baseline["performance"]["avg_search_time"]
        
        print(f"   Quality Improvement: {quality_improvement:+.3f} ({quality_improvement/baseline['quality']['avg_quality_score']*100:+.1f}%)")
        print(f"   Time Increase: {time_increase:+.3f}s ({time_increase/baseline['performance']['avg_search_time']*100:+.1f}%)")
        print(f"   Quality/Time Ratio: {quality_improvement/time_increase:.3f}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(self.benchmark_results["recommendations"], 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "="*80)

async def main():
    """Main function"""
    benchmark = ComprehensivePerformanceBenchmark()
    await benchmark.run_comprehensive_benchmark()

if __name__ == "__main__":
    asyncio.run(main())

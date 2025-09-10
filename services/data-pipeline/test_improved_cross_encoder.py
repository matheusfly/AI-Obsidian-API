#!/usr/bin/env python3
"""
Improved Cross-Encoder Performance Testing Script
Tests optimized re-ranking functionality with better scoring
"""

import asyncio
import logging
import time
import json
import statistics
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService
from src.search.improved_search_service import ImprovedSemanticSearchService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImprovedCrossEncoderTester:
    """Test improved cross-encoder re-ranking performance"""
    
    def __init__(self, chroma_db_path: str = "./test_improved_cross_encoder_chroma_db"):
        self.chroma_db_path = chroma_db_path
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Initialize services
        self.embedding_service = None
        self.chroma_service = None
        self.search_service = None
        
        # Test results
        self.results = {}
        
    async def setup_services(self):
        """Initialize services"""
        logger.info("Setting up services...")
        
        try:
            # Initialize embedding service
            self.embedding_service = EmbeddingService(model_name=self.embedding_model)
            
            # Initialize ChromaDB service
            self.chroma_service = ChromaService(
                persist_directory=self.chroma_db_path,
                collection_name="improved_cross_encoder_test",
                embedding_model=self.embedding_model
            )
            
            # Initialize improved search service
            self.search_service = ImprovedSemanticSearchService(
                chroma_service=self.chroma_service,
                embedding_service=self.embedding_service
            )
            
            logger.info("Services initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up services: {e}")
            raise
    
    async def prepare_test_data(self):
        """Prepare test data with more diverse and relevant content"""
        logger.info("Preparing improved test data...")
        
        # More diverse and relevant test documents
        test_documents = [
            {
                "content": "Machine learning algorithms are computational methods that enable computers to learn patterns from data without being explicitly programmed. Popular algorithms include linear regression, decision trees, random forests, support vector machines, and neural networks. Each algorithm has specific strengths and use cases in different domains.",
                "path": "test/ml_algorithms.md",
                "heading": "Machine Learning Algorithms",
                "chunk_index": 0,
                "chunk_token_count": 45,
                "file_tags": "machine_learning,algorithms,ai",
                "file_modified": "2025-01-09",
                "topic": "machine_learning",
                "type": "algorithms"
            },
            {
                "content": "Python is a versatile programming language widely used in data science, machine learning, web development, and automation. Its simple syntax, extensive libraries like NumPy, Pandas, and Scikit-learn, and strong community support make it ideal for both beginners and professionals. Python's readability and flexibility have made it the go-to language for AI and data analysis projects.",
                "path": "test/python_programming.md",
                "heading": "Python Programming Language",
                "chunk_index": 0,
                "chunk_token_count": 42,
                "file_tags": "python,programming,data_science",
                "file_modified": "2025-01-09",
                "topic": "python",
                "type": "programming"
            },
            {
                "content": "Data analysis techniques involve collecting, cleaning, processing, and interpreting data to extract meaningful insights. Common techniques include statistical analysis, data visualization, exploratory data analysis (EDA), hypothesis testing, and predictive modeling. Tools like R, Python, SQL, and specialized software help analysts uncover patterns and trends in complex datasets.",
                "path": "test/data_analysis_techniques.md",
                "heading": "Data Analysis Techniques",
                "chunk_index": 0,
                "chunk_token_count": 38,
                "file_tags": "data_analysis,statistics,techniques",
                "file_modified": "2025-01-09",
                "topic": "data_analysis",
                "type": "techniques"
            },
            {
                "content": "Artificial intelligence (AI) is a broad field of computer science focused on creating systems that can perform tasks typically requiring human intelligence. AI encompasses machine learning, natural language processing, computer vision, robotics, and expert systems. Recent advances in deep learning and neural networks have revolutionized AI applications across industries.",
                "path": "test/ai_overview.md",
                "heading": "Artificial Intelligence Overview",
                "chunk_index": 0,
                "chunk_token_count": 40,
                "file_tags": "ai,artificial_intelligence,overview",
                "file_modified": "2025-01-09",
                "topic": "ai",
                "type": "overview"
            },
            {
                "content": "Database optimization involves improving query performance, indexing strategies, and data storage efficiency. Key techniques include proper indexing, query optimization, database normalization, partitioning, and caching. Performance monitoring tools help identify bottlenecks and optimize database operations for better application speed and reliability.",
                "path": "test/database_optimization.md",
                "heading": "Database Optimization Methods",
                "chunk_index": 0,
                "chunk_token_count": 35,
                "file_tags": "database,optimization,performance",
                "file_modified": "2025-01-09",
                "topic": "database",
                "type": "optimization"
            },
            {
                "content": "API development requires understanding REST principles, authentication mechanisms, error handling, and documentation standards. Modern APIs use JSON for data exchange, implement proper HTTP status codes, and follow RESTful design patterns. Security considerations include API keys, OAuth, rate limiting, and input validation for building robust web services.",
                "path": "test/api_development.md",
                "heading": "API Development Best Practices",
                "chunk_index": 0,
                "chunk_token_count": 37,
                "file_tags": "api,development,web_services",
                "file_modified": "2025-01-09",
                "topic": "api",
                "type": "development"
            },
            {
                "content": "Cloud computing provides scalable computing resources over the internet, including Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS). Major providers like AWS, Azure, and Google Cloud offer various services for storage, computing, networking, and specialized AI/ML tools. Cloud adoption enables businesses to scale efficiently and reduce infrastructure costs.",
                "path": "test/cloud_computing.md",
                "heading": "Cloud Computing Services",
                "chunk_index": 0,
                "chunk_token_count": 39,
                "file_tags": "cloud,infrastructure,aws,azure",
                "file_modified": "2025-01-09",
                "topic": "cloud",
                "type": "infrastructure"
            },
            {
                "content": "Software architecture defines the high-level structure of software systems, including components, relationships, and design patterns. Common architectural patterns include microservices, monolithic, serverless, and event-driven architectures. Good architecture principles include separation of concerns, modularity, scalability, and maintainability to guide development teams.",
                "path": "test/software_architecture.md",
                "heading": "Software Architecture Patterns",
                "chunk_index": 0,
                "chunk_token_count": 36,
                "file_tags": "architecture,design_patterns,software",
                "file_modified": "2025-01-09",
                "topic": "architecture",
                "type": "design"
            },
            {
                "content": "Debugging techniques include using debuggers, logging, unit testing, and systematic problem-solving approaches. Effective debugging involves reproducing issues, isolating problems, using breakpoints, examining variables, and testing hypotheses. Modern development tools provide advanced debugging features like step-through execution, call stack analysis, and performance profiling.",
                "path": "test/debugging_techniques.md",
                "heading": "Debugging Techniques and Tools",
                "chunk_index": 0,
                "chunk_token_count": 34,
                "file_tags": "debugging,testing,tools",
                "file_modified": "2025-01-09",
                "topic": "debugging",
                "type": "techniques"
            },
            {
                "content": "Performance testing evaluates system behavior under various load conditions to ensure applications meet speed, scalability, and stability requirements. Types include load testing, stress testing, volume testing, and spike testing. Tools like JMeter, LoadRunner, and custom scripts help simulate user loads and measure system performance metrics.",
                "path": "test/performance_testing.md",
                "heading": "Performance Testing Strategies",
                "chunk_index": 0,
                "chunk_token_count": 33,
                "file_tags": "testing,performance,load_testing",
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
            
            logger.info(f"Stored {len(test_documents)} improved test documents")
            return len(test_documents)
            
        except Exception as e:
            logger.error(f"Error preparing test data: {e}")
            raise
    
    async def test_baseline_search(self, queries: List[str]) -> Dict[str, Any]:
        """Test baseline search without re-ranking"""
        logger.info("Testing baseline search...")
        
        results = {
            "queries": {},
            "performance": {},
            "quality": {}
        }
        
        search_times = []
        similarity_scores = []
        
        for query in queries:
            logger.info(f"Testing baseline query: {query}")
            
            start_time = time.time()
            
            # Regular search without query expansion
            search_results = await self.search_service.search_similar(
                query=query,
                n_results=5,
                use_cache=False,
                expand_query=False
            )
            
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            if search_results:
                avg_similarity = statistics.mean([r['similarity'] for r in search_results])
                similarity_scores.append(avg_similarity)
                
                results["queries"][query] = {
                    "search_time": search_time,
                    "num_results": len(search_results),
                    "avg_similarity": avg_similarity,
                    "top_result": search_results[0]["content"][:100] + "..." if search_results else ""
                }
            else:
                results["queries"][query] = {
                    "search_time": search_time,
                    "num_results": 0,
                    "avg_similarity": 0.0,
                    "top_result": ""
                }
        
        # Calculate metrics
        results["performance"] = {
            "avg_search_time": statistics.mean(search_times),
            "min_search_time": min(search_times),
            "max_search_time": max(search_times)
        }
        
        results["quality"] = {
            "avg_similarity": statistics.mean(similarity_scores) if similarity_scores else 0.0,
            "min_similarity": min(similarity_scores) if similarity_scores else 0.0,
            "max_similarity": max(similarity_scores) if similarity_scores else 0.0
        }
        
        logger.info(f"Baseline search complete. Avg time: {results['performance']['avg_search_time']:.3f}s")
        return results
    
    async def test_improved_reranked_search(self, queries: List[str]) -> Dict[str, Any]:
        """Test improved re-ranked search with better scoring"""
        logger.info("Testing improved re-ranked search...")
        
        results = {
            "queries": {},
            "performance": {},
            "quality": {}
        }
        
        search_times = []
        final_scores = []
        cross_scores = []
        
        for query in queries:
            logger.info(f"Testing improved re-ranked query: {query}")
            
            start_time = time.time()
            
            # Improved re-ranked search
            search_results = await self.search_service.search_with_improved_rerank(
                query=query,
                n_results=5,
                rerank_top_k=10
            )
            
            search_time = time.time() - start_time
            search_times.append(search_time)
            
            if search_results:
                avg_final_score = statistics.mean([r['final_score'] for r in search_results])
                avg_cross_score = statistics.mean([r['cross_score'] for r in search_results])
                final_scores.append(avg_final_score)
                cross_scores.append(avg_cross_score)
                
                results["queries"][query] = {
                    "search_time": search_time,
                    "num_results": len(search_results),
                    "avg_final_score": avg_final_score,
                    "avg_cross_score": avg_cross_score,
                    "top_result": search_results[0]["content"][:100] + "..." if search_results else ""
                }
            else:
                results["queries"][query] = {
                    "search_time": search_time,
                    "num_results": 0,
                    "avg_final_score": 0.0,
                    "avg_cross_score": 0.0,
                    "top_result": ""
                }
        
        # Calculate metrics
        results["performance"] = {
            "avg_search_time": statistics.mean(search_times),
            "min_search_time": min(search_times),
            "max_search_time": max(search_times)
        }
        
        results["quality"] = {
            "avg_final_score": statistics.mean(final_scores) if final_scores else 0.0,
            "avg_cross_score": statistics.mean(cross_scores) if cross_scores else 0.0,
            "min_final_score": min(final_scores) if final_scores else 0.0,
            "max_final_score": max(final_scores) if final_scores else 0.0
        }
        
        logger.info(f"Improved re-ranked search complete. Avg time: {results['performance']['avg_search_time']:.3f}s")
        return results
    
    def compare_results(self, baseline: Dict, reranked: Dict) -> Dict[str, Any]:
        """Compare baseline vs re-ranked results"""
        logger.info("Comparing results...")
        
        comparison = {
            "performance": {},
            "quality": {},
            "recommendation": ""
        }
        
        # Performance comparison
        baseline_time = baseline["performance"]["avg_search_time"]
        reranked_time = reranked["performance"]["avg_search_time"]
        time_diff = reranked_time - baseline_time
        time_percent = (time_diff / baseline_time) * 100
        
        comparison["performance"] = {
            "baseline_time": baseline_time,
            "reranked_time": reranked_time,
            "time_difference": time_diff,
            "time_percent_change": time_percent,
            "slower": reranked_time > baseline_time
        }
        
        # Quality comparison
        baseline_quality = baseline["quality"]["avg_similarity"]
        reranked_quality = reranked["quality"]["avg_final_score"]
        quality_diff = reranked_quality - baseline_quality
        quality_percent = (quality_diff / baseline_quality) * 100 if baseline_quality > 0 else 0
        
        comparison["quality"] = {
            "baseline_quality": baseline_quality,
            "reranked_quality": reranked_quality,
            "quality_difference": quality_diff,
            "quality_percent_change": quality_percent,
            "better": reranked_quality > baseline_quality
        }
        
        # Generate recommendation
        if comparison["quality"]["better"] and not comparison["performance"]["slower"]:
            comparison["recommendation"] = "EXCELLENT: Quality improved with no performance penalty"
        elif comparison["quality"]["better"] and comparison["performance"]["slower"]:
            if time_percent < 200:  # Less than 2x slower
                comparison["recommendation"] = "GOOD: Quality improved with acceptable performance cost"
            else:
                comparison["recommendation"] = "ACCEPTABLE: Quality improved but significant performance cost"
        elif not comparison["quality"]["better"] and not comparison["performance"]["slower"]:
            comparison["recommendation"] = "ACCEPTABLE: Performance maintained, quality similar"
        else:
            comparison["recommendation"] = "REVIEW: Both quality and performance need improvement"
        
        return comparison
    
    async def run_test(self):
        """Run the complete test suite"""
        logger.info("Starting improved cross-encoder performance test...")
        
        # Test queries
        test_queries = [
            "machine learning algorithms",
            "python programming language",
            "data analysis techniques",
            "artificial intelligence overview",
            "database optimization methods"
        ]
        
        try:
            # Setup
            await self.setup_services()
            await self.prepare_test_data()
            
            # Test baseline
            logger.info("\n" + "="*50)
            logger.info("TESTING BASELINE SEARCH")
            logger.info("="*50)
            baseline_results = await self.test_baseline_search(test_queries)
            
            # Test improved re-ranked
            logger.info("\n" + "="*50)
            logger.info("TESTING IMPROVED RE-RANKED SEARCH")
            logger.info("="*50)
            reranked_results = await self.test_improved_reranked_search(test_queries)
            
            # Compare
            logger.info("\n" + "="*50)
            logger.info("COMPARING RESULTS")
            logger.info("="*50)
            comparison = self.compare_results(baseline_results, reranked_results)
            
            # Store results
            self.results = {
                "baseline": baseline_results,
                "reranked": reranked_results,
                "comparison": comparison
            }
            
            # Generate report
            self.generate_report()
            
            logger.info("Improved cross-encoder performance test complete!")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_report(self):
        """Generate performance report"""
        logger.info("Generating performance report...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_type": "improved_cross_encoder_performance",
            "baseline": self.results["baseline"],
            "reranked": self.results["reranked"],
            "comparison": self.results["comparison"]
        }
        
        # Save report
        report_path = "improved_cross_encoder_performance_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to: {report_path}")
        
        # Print summary
        self._print_summary()
    
    def _print_summary(self):
        """Print performance summary"""
        print("\n" + "="*70)
        print("IMPROVED CROSS-ENCODER PERFORMANCE TEST SUMMARY")
        print("="*70)
        
        baseline = self.results["baseline"]
        reranked = self.results["reranked"]
        comparison = self.results["comparison"]
        
        print(f"\n📊 BASELINE PERFORMANCE:")
        print(f"   Average Search Time: {baseline['performance']['avg_search_time']:.3f}s")
        print(f"   Average Similarity: {baseline['quality']['avg_similarity']:.3f}")
        
        print(f"\n🚀 IMPROVED RE-RANKED PERFORMANCE:")
        print(f"   Average Search Time: {reranked['performance']['avg_search_time']:.3f}s")
        print(f"   Average Final Score: {reranked['quality']['avg_final_score']:.3f}")
        print(f"   Average Cross Score: {reranked['quality']['avg_cross_score']:.3f}")
        
        print(f"\n📈 COMPARISON:")
        print(f"   Time Change: {comparison['performance']['time_percent_change']:+.1f}%")
        print(f"   Quality Change: {comparison['quality']['quality_percent_change']:+.1f}%")
        print(f"   Quality Better: {comparison['quality']['better']}")
        print(f"   Performance Slower: {comparison['performance']['slower']}")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"   {comparison['recommendation']}")
        
        print("\n" + "="*70)

async def main():
    """Main function"""
    tester = ImprovedCrossEncoderTester()
    await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main())

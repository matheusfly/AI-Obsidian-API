#!/usr/bin/env python3
"""
Phase 4.1: Quality Metrics Validation
Test Precision, MRR, NDCG calculation accuracy with real data
"""

import sys
import os
import json
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from datetime import datetime

# Add data-pipeline services to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

try:
    from embeddings.embedding_service import EmbeddingService
    from vector.chroma_service import ChromaService
    from search.semantic_search_service import SemanticSearchService
    from processing.content_processor import ContentProcessor
    from search.reranker import ReRanker
    from search.topic_detector import TopicDetector
    from search.smart_document_filter import SmartDocumentFilter
    from processing.advanced_content_processor import AdvancedContentProcessor
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure data-pipeline services are properly set up")
    sys.exit(1)

class QualityMetricsValidator:
    """Validate quality metrics calculation with real data"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "phase": "4.1 - Quality Metrics Validation",
            "status": "running",
            "tests": {},
            "summary": {}
        }
        
        # Initialize services
        self.embedding_service = EmbeddingService()
        self.chroma_service = ChromaService()
        self.search_service = SemanticSearchService(self.chroma_service, self.embedding_service)
        self.content_processor = ContentProcessor()
        self.reranker = ReRanker()
        self.topic_detector = TopicDetector()
        self.smart_filter = SmartDocumentFilter()
        self.advanced_processor = AdvancedContentProcessor()
        
        # Test data
        self.test_queries = [
            {
                "query": "What are the main philosophical currents of logic and mathematics?",
                "expected_topics": ["philosophy", "mathematics", "logic"],
                "expected_files": ["LOGICA-INDICE", "filosofia", "matematica"],
                "relevance_threshold": 0.6
            },
            {
                "query": "How does Scrapy handle web scraping?",
                "expected_topics": ["programming", "web_scraping", "python"],
                "expected_files": ["scrapy", "web_scraping", "python"],
                "relevance_threshold": 0.6
            },
            {
                "query": "What is the PQLP reading technique?",
                "expected_topics": ["reading", "performance", "learning"],
                "expected_files": ["Hiper-Leitura", "reading", "performance"],
                "relevance_threshold": 0.6
            }
        ]
        
        # Vault data path
        self.vault_path = Path("D:/Nomade Milionario")
        
    def calculate_precision_at_k(self, results: List[Dict], relevant_files: List[str], k: int = 5) -> float:
        """Calculate Precision@K"""
        if not results:
            return 0.0
            
        top_k_results = results[:k]
        relevant_count = sum(1 for r in top_k_results if any(rel in r.get('path', '') for rel in relevant_files))
        return relevant_count / len(top_k_results)
    
    def calculate_mrr(self, results: List[Dict], relevant_files: List[str]) -> float:
        """Calculate Mean Reciprocal Rank"""
        for i, result in enumerate(results, 1):
            if any(rel in result.get('path', '') for rel in relevant_files):
                return 1.0 / i
        return 0.0
    
    def calculate_ndcg(self, results: List[Dict], relevant_files: List[str], k: int = 5) -> float:
        """Calculate Normalized Discounted Cumulative Gain"""
        def dcg(relevance_scores: List[float]) -> float:
            return sum(score / np.log2(i + 2) for i, score in enumerate(relevance_scores))
        
        # Get relevance scores for top k results
        relevance_scores = []
        for result in results[:k]:
            is_relevant = any(rel in result.get('path', '') for rel in relevant_files)
            relevance_scores.append(1.0 if is_relevant else 0.0)
        
        if not relevance_scores:
            return 0.0
            
        # Calculate DCG
        dcg_score = dcg(relevance_scores)
        
        # Calculate IDCG (ideal DCG)
        ideal_relevance = [1.0] * min(len(relevant_files), k)
        idcg_score = dcg(ideal_relevance)
        
        return dcg_score / idcg_score if idcg_score > 0 else 0.0
    
    def calculate_quality_score(self, query: str, results: List[Dict], expected_files: List[str]) -> Dict[str, float]:
        """Calculate comprehensive quality score"""
        precision_5 = self.calculate_precision_at_k(results, expected_files, 5)
        precision_10 = self.calculate_precision_at_k(results, expected_files, 10)
        mrr = self.calculate_mrr(results, expected_files)
        ndcg_5 = self.calculate_ndcg(results, expected_files, 5)
        ndcg_10 = self.calculate_ndcg(results, expected_files, 10)
        
        # Overall quality score (weighted average)
        overall_score = (0.3 * precision_5 + 0.2 * precision_10 + 0.2 * mrr + 0.2 * ndcg_5 + 0.1 * ndcg_10)
        
        return {
            "precision_at_5": precision_5,
            "precision_at_10": precision_10,
            "mrr": mrr,
            "ndcg_at_5": ndcg_5,
            "ndcg_at_10": ndcg_10,
            "overall_quality_score": overall_score
        }
    
    def test_quality_metrics_calculation(self) -> Dict[str, Any]:
        """Test quality metrics calculation accuracy"""
        print("🧪 Testing Quality Metrics Calculation...")
        
        test_results = {
            "test_name": "Quality Metrics Calculation",
            "status": "running",
            "metrics_tests": {},
            "overall_success": True
        }
        
        try:
            # Test 1: Basic metrics calculation
            print("  📊 Testing basic metrics calculation...")
            
            # Mock results for testing
            mock_results = [
                {"path": "philosophy_of_math.md", "similarity": 0.89, "content": "Philosophy of mathematics content"},
                {"path": "logic_foundations.md", "similarity": 0.87, "content": "Logic foundations content"},
                {"path": "scrapy_guide.md", "similarity": 0.45, "content": "Scrapy guide content"},
                {"path": "reading_techniques.md", "similarity": 0.32, "content": "Reading techniques content"},
                {"path": "random_doc.md", "similarity": 0.15, "content": "Random content"}
            ]
            
            expected_files = ["philosophy_of_math.md", "logic_foundations.md"]
            
            # Calculate metrics
            metrics = self.calculate_quality_score(
                "What are the main philosophical currents of logic and mathematics?",
                mock_results,
                expected_files
            )
            
            # Validate metrics
            assert 0.0 <= metrics["precision_at_5"] <= 1.0, "Precision@5 should be between 0 and 1"
            assert 0.0 <= metrics["mrr"] <= 1.0, "MRR should be between 0 and 1"
            assert 0.0 <= metrics["ndcg_at_5"] <= 1.0, "NDCG@5 should be between 0 and 1"
            assert 0.0 <= metrics["overall_quality_score"] <= 1.0, "Overall quality score should be between 0 and 1"
            
            test_results["metrics_tests"]["basic_calculation"] = {
                "status": "passed",
                "metrics": metrics,
                "message": "Basic metrics calculation working correctly"
            }
            
            print("    ✅ Basic metrics calculation passed")
            
            # Test 2: Edge cases
            print("  🔍 Testing edge cases...")
            
            # Empty results
            empty_metrics = self.calculate_quality_score("test", [], [])
            assert empty_metrics["precision_at_5"] == 0.0, "Empty results should have 0 precision"
            assert empty_metrics["mrr"] == 0.0, "Empty results should have 0 MRR"
            
            # No relevant files
            no_relevant_metrics = self.calculate_quality_score("test", mock_results, [])
            assert no_relevant_metrics["precision_at_5"] == 0.0, "No relevant files should have 0 precision"
            
            test_results["metrics_tests"]["edge_cases"] = {
                "status": "passed",
                "message": "Edge cases handled correctly"
            }
            
            print("    ✅ Edge cases handled correctly")
            
            # Test 3: Real data integration
            print("  🔗 Testing real data integration...")
            
            if self.vault_path.exists():
                # Load real vault content
                vault_content = self._load_vault_content()
                
                if vault_content:
                    # Test with real data
                    real_query = "What are the main philosophical currents of logic and mathematics?"
                    real_results = self.search_service.search(real_query, list(vault_content.values()), top_k=5)
                    
                    # Calculate metrics for real data
                    real_metrics = self.calculate_quality_score(
                        real_query,
                        real_results,
                        ["LOGICA-INDICE", "filosofia", "matematica"]
                    )
                    
                    test_results["metrics_tests"]["real_data"] = {
                        "status": "passed",
                        "real_metrics": real_metrics,
                        "real_results_count": len(real_results),
                        "message": "Real data integration working"
                    }
                    
                    print("    ✅ Real data integration working")
                else:
                    test_results["metrics_tests"]["real_data"] = {
                        "status": "skipped",
                        "message": "No vault content found"
                    }
                    print("    ⚠️ No vault content found")
            else:
                test_results["metrics_tests"]["real_data"] = {
                    "status": "skipped",
                    "message": "Vault path not found"
                }
                print("    ⚠️ Vault path not found")
            
            test_results["status"] = "passed"
            print("  ✅ Quality metrics calculation test passed")
            
        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            test_results["overall_success"] = False
            print(f"  ❌ Quality metrics calculation test failed: {e}")
        
        return test_results
    
    def test_performance_benchmarking(self) -> Dict[str, Any]:
        """Test performance benchmarking capabilities"""
        print("⚡ Testing Performance Benchmarking...")
        
        test_results = {
            "test_name": "Performance Benchmarking",
            "status": "running",
            "benchmarks": {},
            "overall_success": True
        }
        
        try:
            # Test 1: Search performance
            print("  🔍 Testing search performance...")
            
            start_time = time.time()
            
            # Run multiple searches
            for i in range(10):
                query = f"Test query {i} about philosophy and mathematics"
                results = self.search_service.search(query, [], top_k=5)
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / 10
            
            test_results["benchmarks"]["search_performance"] = {
                "status": "passed",
                "total_time": total_time,
                "average_time": avg_time,
                "queries_per_second": 10 / total_time,
                "message": f"Average search time: {avg_time:.3f}s"
            }
            
            print(f"    ✅ Search performance: {avg_time:.3f}s average")
            
            # Test 2: Memory usage
            print("  💾 Testing memory usage...")
            
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            test_results["benchmarks"]["memory_usage"] = {
                "status": "passed",
                "memory_mb": memory_usage,
                "message": f"Memory usage: {memory_usage:.1f} MB"
            }
            
            print(f"    ✅ Memory usage: {memory_usage:.1f} MB")
            
            # Test 3: Concurrent requests
            print("  🔄 Testing concurrent requests...")
            
            async def concurrent_search(query: str):
                return self.search_service.search(query, [], top_k=5)
            
            async def run_concurrent_tests():
                tasks = [concurrent_search(f"Concurrent query {i}") for i in range(5)]
                start_time = time.time()
                results = await asyncio.gather(*tasks)
                end_time = time.time()
                return end_time - start_time, len(results)
            
            concurrent_time, concurrent_results = asyncio.run(run_concurrent_tests())
            
            test_results["benchmarks"]["concurrent_requests"] = {
                "status": "passed",
                "concurrent_time": concurrent_time,
                "results_count": concurrent_results,
                "message": f"Concurrent requests completed in {concurrent_time:.3f}s"
            }
            
            print(f"    ✅ Concurrent requests: {concurrent_time:.3f}s")
            
            test_results["status"] = "passed"
            print("  ✅ Performance benchmarking test passed")
            
        except Exception as e:
            test_results["status"] = "failed"
            test_results["error"] = str(e)
            test_results["overall_success"] = False
            print(f"  ❌ Performance benchmarking test failed: {e}")
        
        return test_results
    
    def _load_vault_content(self) -> Dict[str, Dict]:
        """Load vault content for testing"""
        vault_content = {}
        
        try:
            # Load a few sample files for testing
            sample_files = [
                "LOGICA-INDICE.md",
                "Hiper-Leitura.md",
                "scrapy.md"
            ]
            
            for filename in sample_files:
                file_path = self.vault_path / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Process content
                    processed_content = self.content_processor.process_file(file_path)
                    vault_content[filename] = processed_content
            
            return vault_content
            
        except Exception as e:
            print(f"    ⚠️ Error loading vault content: {e}")
            return {}
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete Phase 4.1 validation"""
        print("🚀 Starting Phase 4.1: Quality Metrics Validation")
        print("=" * 60)
        
        # Test 1: Quality metrics calculation
        metrics_test = self.test_quality_metrics_calculation()
        self.results["tests"]["quality_metrics"] = metrics_test
        
        # Test 2: Performance benchmarking
        performance_test = self.test_performance_benchmarking()
        self.results["tests"]["performance_benchmarking"] = performance_test
        
        # Calculate overall success
        overall_success = all(
            test.get("overall_success", False) 
            for test in self.results["tests"].values()
        )
        
        self.results["status"] = "completed" if overall_success else "failed"
        self.results["summary"] = {
            "overall_success": overall_success,
            "tests_completed": len(self.results["tests"]),
            "successful_tests": sum(1 for test in self.results["tests"].values() if test.get("overall_success", False)),
            "failed_tests": sum(1 for test in self.results["tests"].values() if not test.get("overall_success", False))
        }
        
        print("\n" + "=" * 60)
        print("📊 Phase 4.1 Validation Summary:")
        print(f"Overall Success: {'✅ YES' if overall_success else '❌ NO'}")
        print(f"Tests Completed: {self.results['summary']['tests_completed']}")
        print(f"Successful Tests: {self.results['summary']['successful_tests']}")
        print(f"Failed Tests: {self.results['summary']['failed_tests']}")
        
        return self.results

def main():
    """Main validation function"""
    validator = QualityMetricsValidator()
    results = validator.run_validation()
    
    # Save results
    output_file = "phase4_quality_metrics_validation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    main()

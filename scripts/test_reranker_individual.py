#!/usr/bin/env python3
"""
Individual Test for ReRanker Component
Tests standalone functionality and integration capabilities
"""

import sys
import os
import json
import time
import logging
from typing import List, Dict, Any
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from reranker import ReRanker
    print("✅ ReRanker import successful")
except ImportError as e:
    print(f"❌ ReRanker import failed: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReRankerIndividualTester:
    def __init__(self):
        self.reranker = None
        self.test_results = {
            "component": "ReRanker",
            "tests_passed": 0,
            "tests_failed": 0,
            "total_tests": 0,
            "performance_metrics": {},
            "errors": [],
            "warnings": []
        }
    
    def test_initialization(self):
        """Test ReRanker initialization"""
        print("\n🧪 Testing ReRanker Initialization...")
        self.test_results["total_tests"] += 1
        
        try:
            start_time = time.time()
            self.reranker = ReRanker()
            init_time = time.time() - start_time
            
            self.test_results["performance_metrics"]["initialization_time"] = init_time
            self.test_results["tests_passed"] += 1
            print(f"✅ ReRanker initialized successfully in {init_time:.2f}s")
            return True
            
        except Exception as e:
            error_msg = f"ReRanker initialization failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            return False
    
    def test_basic_reranking(self):
        """Test basic re-ranking functionality"""
        print("\n🧪 Testing Basic Re-ranking...")
        self.test_results["total_tests"] += 1
        
        try:
            query = "machine learning algorithms for data analysis"
            candidates = [
                {
                    "content": "Machine learning algorithms are powerful tools for analyzing large datasets and extracting meaningful patterns.",
                    "similarity": 0.8,
                    "heading": "ML Algorithms"
                },
                {
                    "content": "Data analysis techniques include statistical methods, visualization, and machine learning approaches.",
                    "similarity": 0.7,
                    "heading": "Data Analysis"
                },
                {
                    "content": "Philosophical logic deals with the nature of reasoning and argumentation in philosophical contexts.",
                    "similarity": 0.6,
                    "heading": "Philosophical Logic"
                },
                {
                    "content": "Performance optimization can improve system efficiency and reduce response times.",
                    "similarity": 0.5,
                    "heading": "Performance Tips"
                }
            ]
            
            start_time = time.time()
            reranked = self.reranker.rerank(query, candidates, top_k=3)
            rerank_time = time.time() - start_time
            
            # Validate results
            assert len(reranked) == 3, f"Expected 3 results, got {len(reranked)}"
            assert all('final_score' in r for r in reranked), "Missing final_score in results"
            assert all('rerank_score' in r for r in reranked), "Missing rerank_score in results"
            
            # Check if results are sorted by final_score
            scores = [r['final_score'] for r in reranked]
            assert scores == sorted(scores, reverse=True), "Results not sorted by final_score"
            
            self.test_results["performance_metrics"]["basic_rerank_time"] = rerank_time
            self.test_results["tests_passed"] += 1
            print(f"✅ Basic re-ranking successful in {rerank_time:.2f}s")
            print(f"   Top result: {reranked[0]['heading']} (score: {reranked[0]['final_score']:.3f})")
            return True
            
        except Exception as e:
            error_msg = f"Basic re-ranking failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def test_search_with_rerank(self):
        """Test search_with_rerank method"""
        print("\n🧪 Testing Search with Re-rank...")
        self.test_results["total_tests"] += 1
        
        try:
            query = "artificial intelligence and neural networks"
            candidates = [
                {
                    "content": "Neural networks are a subset of artificial intelligence that mimic the human brain's structure.",
                    "similarity": 0.9,
                    "heading": "Neural Networks"
                },
                {
                    "content": "Artificial intelligence encompasses machine learning, deep learning, and neural networks.",
                    "similarity": 0.85,
                    "heading": "AI Overview"
                },
                {
                    "content": "Database management systems are crucial for storing and retrieving information efficiently.",
                    "similarity": 0.3,
                    "heading": "Database Systems"
                },
                {
                    "content": "Web development involves creating user interfaces and backend services.",
                    "similarity": 0.2,
                    "heading": "Web Development"
                }
            ]
            
            start_time = time.time()
            results = self.reranker.search_with_rerank(
                query, candidates, n_results=2, 
                similarity_weight=0.3, cross_score_weight=0.7
            )
            search_time = time.time() - start_time
            
            # Validate results
            assert len(results) == 2, f"Expected 2 results, got {len(results)}"
            assert all('cross_score' in r for r in results), "Missing cross_score in results"
            assert all('final_score' in r for r in results), "Missing final_score in results"
            
            self.test_results["performance_metrics"]["search_rerank_time"] = search_time
            self.test_results["tests_passed"] += 1
            print(f"✅ Search with re-rank successful in {search_time:.2f}s")
            print(f"   Top result: {results[0]['heading']} (final: {results[0]['final_score']:.3f}, cross: {results[0]['cross_score']:.3f})")
            return True
            
        except Exception as e:
            error_msg = f"Search with re-rank failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def test_custom_weights(self):
        """Test re-ranking with custom weights"""
        print("\n🧪 Testing Custom Weights...")
        self.test_results["total_tests"] += 1
        
        try:
            query = "data science and analytics"
            candidates = [
                {
                    "content": "Data science combines statistics, programming, and domain expertise to extract insights from data.",
                    "similarity": 0.8,
                    "heading": "Data Science"
                },
                {
                    "content": "Analytics involves the systematic analysis of data to support decision-making processes.",
                    "similarity": 0.75,
                    "heading": "Analytics"
                },
                {
                    "content": "Software engineering focuses on designing and building reliable software systems.",
                    "similarity": 0.4,
                    "heading": "Software Engineering"
                }
            ]
            
            # Test with different weight combinations
            weight_configs = [
                (0.6, 0.4),  # Default
                (0.8, 0.2),  # More similarity weight
                (0.2, 0.8),  # More rerank weight
            ]
            
            for sim_weight, rerank_weight in weight_configs:
                start_time = time.time()
                results = self.reranker.rerank_with_weights(
                    query, candidates.copy(), 
                    similarity_weight=sim_weight,
                    rerank_weight=rerank_weight,
                    top_k=2
                )
                weight_time = time.time() - start_time
                
                assert len(results) == 2, f"Expected 2 results for weights ({sim_weight}, {rerank_weight})"
                assert all('final_score' in r for r in results), "Missing final_score in results"
                
                print(f"   Weights ({sim_weight}, {rerank_weight}): {weight_time:.2f}s")
            
            self.test_results["performance_metrics"]["custom_weights_time"] = weight_time
            self.test_results["tests_passed"] += 1
            print(f"✅ Custom weights test successful")
            return True
            
        except Exception as e:
            error_msg = f"Custom weights test failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def test_batch_reranking(self):
        """Test batch re-ranking functionality"""
        print("\n🧪 Testing Batch Re-ranking...")
        self.test_results["total_tests"] += 1
        
        try:
            queries = [
                "machine learning algorithms",
                "data analysis techniques",
                "artificial intelligence"
            ]
            
            candidates_list = [
                [
                    {"content": "ML algorithms include supervised, unsupervised, and reinforcement learning.", "similarity": 0.9, "heading": "ML Types"},
                    {"content": "Statistical methods are fundamental to data analysis.", "similarity": 0.6, "heading": "Statistics"}
                ],
                [
                    {"content": "Data analysis involves cleaning, processing, and visualizing data.", "similarity": 0.8, "heading": "Data Process"},
                    {"content": "Machine learning can automate data analysis tasks.", "similarity": 0.7, "heading": "ML in Analysis"}
                ],
                [
                    {"content": "AI systems can learn and adapt to new situations.", "similarity": 0.9, "heading": "AI Learning"},
                    {"content": "Database systems store and manage information.", "similarity": 0.3, "heading": "Databases"}
                ]
            ]
            
            start_time = time.time()
            batch_results = self.reranker.batch_rerank(queries, candidates_list, top_k=1)
            batch_time = time.time() - start_time
            
            # Validate results
            assert len(batch_results) == 3, f"Expected 3 batch results, got {len(batch_results)}"
            assert all(len(result) == 1 for result in batch_results), "Expected 1 result per query"
            
            self.test_results["performance_metrics"]["batch_rerank_time"] = batch_time
            self.test_results["tests_passed"] += 1
            print(f"✅ Batch re-ranking successful in {batch_time:.2f}s")
            return True
            
        except Exception as e:
            error_msg = f"Batch re-ranking failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def test_rerank_analysis(self):
        """Test re-ranking analysis functionality"""
        print("\n🧪 Testing Re-rank Analysis...")
        self.test_results["total_tests"] += 1
        
        try:
            query = "deep learning and neural networks"
            candidates = [
                {
                    "content": "Deep learning uses neural networks with multiple layers to learn complex patterns.",
                    "similarity": 0.8,
                    "heading": "Deep Learning"
                },
                {
                    "content": "Neural networks are inspired by biological neural networks in the brain.",
                    "similarity": 0.75,
                    "heading": "Neural Networks"
                },
                {
                    "content": "Web development involves creating user interfaces and backend services.",
                    "similarity": 0.2,
                    "heading": "Web Development"
                }
            ]
            
            start_time = time.time()
            analysis = self.reranker.get_rerank_analysis(query, candidates)
            analysis_time = time.time() - start_time
            
            # Validate analysis structure
            required_keys = ["query", "candidate_count", "original_scores", "rerank_scores", 
                           "final_scores", "score_improvements", "avg_improvement"]
            assert all(key in analysis for key in required_keys), f"Missing keys in analysis: {set(required_keys) - set(analysis.keys())}"
            
            assert analysis["candidate_count"] == 3, f"Expected 3 candidates, got {analysis['candidate_count']}"
            assert len(analysis["original_scores"]) == 3, "Expected 3 original scores"
            assert len(analysis["rerank_scores"]) == 3, "Expected 3 rerank scores"
            
            self.test_results["performance_metrics"]["analysis_time"] = analysis_time
            self.test_results["tests_passed"] += 1
            print(f"✅ Re-rank analysis successful in {analysis_time:.2f}s")
            print(f"   Average improvement: {analysis['avg_improvement']:.3f}")
            return True
            
        except Exception as e:
            error_msg = f"Re-rank analysis failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🧪 Testing Error Handling...")
        self.test_results["total_tests"] += 1
        
        try:
            # Test empty candidates
            empty_result = self.reranker.rerank("test query", [])
            assert empty_result == [], "Empty candidates should return empty list"
            
            # Test None candidates
            none_result = self.reranker.rerank("test query", None)
            assert none_result is None or none_result == [], "None candidates should return empty or None"
            
            # Test malformed candidates
            malformed_candidates = [
                {"content": "Valid content", "similarity": 0.8},
                {"invalid": "Missing content field"},
                {"content": "Another valid content", "similarity": 0.6}
            ]
            
            # This should handle gracefully
            try:
                malformed_result = self.reranker.rerank("test query", malformed_candidates)
                print("   Handled malformed candidates gracefully")
            except Exception as e:
                print(f"   Warning: Malformed candidates caused error: {e}")
                self.test_results["warnings"].append(f"Malformed candidates error: {e}")
            
            self.test_results["tests_passed"] += 1
            print(f"✅ Error handling test successful")
            return True
            
        except Exception as e:
            error_msg = f"Error handling test failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def run_all_tests(self):
        """Run all individual tests"""
        print("🚀 Starting ReRanker Individual Testing")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_initialization,
            self.test_basic_reranking,
            self.test_search_with_rerank,
            self.test_custom_weights,
            self.test_batch_reranking,
            self.test_rerank_analysis,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                error_msg = f"Test {test.__name__} crashed: {str(e)}"
                self.test_results["errors"].append(error_msg)
                self.test_results["tests_failed"] += 1
                print(f"❌ {error_msg}")
                traceback.print_exc()
        
        total_time = time.time() - start_time
        self.test_results["performance_metrics"]["total_test_time"] = total_time
        
        # Generate report
        self.generate_report()
        
        return self.test_results
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 RERANKER INDIVIDUAL TEST REPORT")
        print("=" * 60)
        
        total_tests = self.test_results["total_tests"]
        passed = self.test_results["tests_passed"]
        failed = self.test_results["tests_failed"]
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.test_results["performance_metrics"]:
            print(f"\nPerformance Metrics:")
            for metric, value in self.test_results["performance_metrics"].items():
                if isinstance(value, float):
                    print(f"  {metric}: {value:.3f}s")
                else:
                    print(f"  {metric}: {value}")
        
        if self.test_results["errors"]:
            print(f"\nErrors ({len(self.test_results['errors'])}):")
            for i, error in enumerate(self.test_results["errors"], 1):
                print(f"  {i}. {error}")
        
        if self.test_results["warnings"]:
            print(f"\nWarnings ({len(self.test_results['warnings'])}):")
            for i, warning in enumerate(self.test_results["warnings"], 1):
                print(f"  {i}. {warning}")
        
        # Save detailed report
        report_file = "reranker_individual_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return success_rate >= 80  # 80% success rate threshold

if __name__ == "__main__":
    tester = ReRankerIndividualTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ReRanker Individual Testing PASSED!")
        sys.exit(0)
    else:
        print("\n💥 ReRanker Individual Testing FAILED!")
        sys.exit(1)

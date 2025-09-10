#!/usr/bin/env python3
"""
File-based Validation Testing: Quality Scoring
"""

import sys
import numpy as np
from pathlib import Path
import logging
from typing import List, Dict, Any, Tuple
import math

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

class FileBasedQualityScoringMetrics:
    """File-based quality scoring metrics for retrieval performance evaluation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.output_file = Path("quality_scoring_test_results.txt")
    
    def calculate_retrieval_quality(self, query: str, results: List[Dict], relevant_files: List[str]) -> Dict[str, float]:
        """
        Calculate comprehensive quality score for retrieval results (0-1)
        
        Args:
            query: The search query
            results: List of retrieved results with similarity scores
            relevant_files: List of file names that should be relevant
            
        Returns:
            Dictionary with quality metrics
        """
        if not results:
            return {
                "precision_at_k": 0.0,
                "recall": 0.0,
                "mrr": 0.0,
                "ndcg": 0.0,
                "overall_quality": 0.0
            }
        
        # Calculate individual metrics
        precision_at_k = self._calculate_precision_at_k(results, relevant_files)
        recall = self._calculate_recall(results, relevant_files)
        mrr = self._calculate_mrr(results, relevant_files)
        ndcg = self._calculate_ndcg(results, relevant_files)
        
        # Calculate overall quality score
        overall_quality = (0.3 * precision_at_k + 0.3 * recall + 0.2 * mrr + 0.2 * ndcg)
        
        return {
            "precision_at_k": precision_at_k,
            "recall": recall,
            "mrr": mrr,
            "ndcg": ndcg,
            "overall_quality": overall_quality
        }
    
    def _calculate_precision_at_k(self, results: List[Dict], relevant_files: List[str], k: int = None) -> float:
        """Calculate Precision@K"""
        if k is None:
            k = len(results)
        
        k = min(k, len(results))
        if k == 0:
            return 0.0
        
        relevant_count = 0
        for i in range(k):
            result = results[i]
            if any(rel_file in result.get("path", "") for rel_file in relevant_files):
                relevant_count += 1
        
        return relevant_count / k
    
    def _calculate_recall(self, results: List[Dict], relevant_files: List[str]) -> float:
        """Calculate Recall"""
        if not relevant_files:
            return 1.0
        
        found_relevant = set()
        for result in results:
            for rel_file in relevant_files:
                if rel_file in result.get("path", ""):
                    found_relevant.add(rel_file)
        
        return len(found_relevant) / len(relevant_files)
    
    def _calculate_mrr(self, results: List[Dict], relevant_files: List[str]) -> float:
        """Calculate Mean Reciprocal Rank (MRR)"""
        for i, result in enumerate(results, 1):
            if any(rel_file in result.get("path", "") for rel_file in relevant_files):
                return 1.0 / i
        
        return 0.0
    
    def _calculate_ndcg(self, results: List[Dict], relevant_files: List[str]) -> float:
        """Calculate Normalized Discounted Cumulative Gain (NDCG)"""
        if not results:
            return 0.0
        
        # Calculate DCG
        dcg = 0.0
        for i, result in enumerate(results, 1):
            relevance = 1 if any(rel_file in result.get("path", "") for rel_file in relevant_files) else 0
            dcg += relevance / math.log2(i + 1)
        
        # Calculate IDCG (Ideal DCG)
        idcg = 0.0
        num_relevant = min(len(relevant_files), len(results))
        for i in range(1, num_relevant + 1):
            idcg += 1.0 / math.log2(i + 1)
        
        # Calculate NDCG
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def test_quality_scoring(self) -> Dict[str, Any]:
        """Test quality scoring metrics with various scenarios"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("🧪 Quality Scoring Metrics Test\n")
            f.write("=" * 40 + "\n")
            
            test_scenarios = [
                {
                    "name": "Perfect Retrieval",
                    "query": "machine learning algorithms",
                    "results": [
                        {"path": "ml_algorithms.md", "similarity": 0.95},
                        {"path": "data_analysis.md", "similarity": 0.90},
                        {"path": "python_guide.md", "similarity": 0.85}
                    ],
                    "relevant_files": ["ml_algorithms.md", "data_analysis.md"],
                    "expected_high_quality": True
                },
                {
                    "name": "Poor Retrieval",
                    "query": "philosophy of mathematics",
                    "results": [
                        {"path": "scrapy_guide.md", "similarity": 0.60},
                        {"path": "web_scraping.md", "similarity": 0.55},
                        {"path": "python_guide.md", "similarity": 0.50}
                    ],
                    "relevant_files": ["philosophy_math.md", "logic_foundations.md"],
                    "expected_high_quality": False
                },
                {
                    "name": "Partial Retrieval",
                    "query": "web scraping techniques",
                    "results": [
                        {"path": "scrapy_guide.md", "similarity": 0.85},
                        {"path": "python_guide.md", "similarity": 0.60},
                        {"path": "ml_algorithms.md", "similarity": 0.45}
                    ],
                    "relevant_files": ["scrapy_guide.md", "web_scraping_techniques.md"],
                    "expected_high_quality": False
                },
                {
                    "name": "Empty Results",
                    "query": "nonexistent topic",
                    "results": [],
                    "relevant_files": ["any_file.md"],
                    "expected_high_quality": False
                }
            ]
            
            total_tests = len(test_scenarios)
            passed_tests = 0
            
            for i, scenario in enumerate(test_scenarios, 1):
                f.write(f"\nTest {i}: {scenario['name']}\n")
                f.write(f"Query: '{scenario['query']}'\n")
                f.write(f"Relevant Files: {scenario['relevant_files']}\n")
                
                # Calculate quality metrics
                quality_metrics = self.calculate_retrieval_quality(
                    scenario["query"],
                    scenario["results"],
                    scenario["relevant_files"]
                )
                
                # Display metrics
                f.write(f"Precision@K: {quality_metrics['precision_at_k']:.3f}\n")
                f.write(f"Recall: {quality_metrics['recall']:.3f}\n")
                f.write(f"MRR: {quality_metrics['mrr']:.3f}\n")
                f.write(f"NDCG: {quality_metrics['ndcg']:.3f}\n")
                f.write(f"Overall Quality: {quality_metrics['overall_quality']:.3f}\n")
                
                # Determine if test passed
                is_high_quality = quality_metrics['overall_quality'] >= 0.7
                test_passed = (is_high_quality == scenario['expected_high_quality'])
                
                if test_passed:
                    passed_tests += 1
                    f.write("✅ PASS\n")
                else:
                    f.write("❌ FAIL\n")
                    f.write(f"Expected high quality: {scenario['expected_high_quality']}, Got: {is_high_quality}\n")
                
                # Show results
                f.write("Results:\n")
                for j, result in enumerate(scenario["results"], 1):
                    f.write(f"  {j}. {result['path']} (similarity: {result['similarity']:.3f})\n")
            
            # Summary
            success_rate = passed_tests / total_tests
            f.write(f"\n📊 Test Summary\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n")
            f.write(f"Failed: {total_tests - passed_tests}\n")
            f.write(f"Success Rate: {success_rate:.1%}\n")
            f.write(f"Overall Status: {'✅ PASS' if success_rate >= 0.8 else '❌ FAIL'}\n")
            
            return {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate,
                "passed": success_rate >= 0.8
            }
    
    def test_metric_consistency(self) -> Dict[str, Any]:
        """Test metric consistency across different result sets"""
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n🔄 Metric Consistency Test\n")
            f.write("-" * 30 + "\n")
            
            # Test with same relevant files but different result orders
            relevant_files = ["file1.md", "file2.md"]
            
            test_cases = [
                {
                    "name": "Best Order",
                    "results": [
                        {"path": "file1.md", "similarity": 0.95},
                        {"path": "file2.md", "similarity": 0.90},
                        {"path": "irrelevant.md", "similarity": 0.60}
                    ]
                },
                {
                    "name": "Worst Order",
                    "results": [
                        {"path": "irrelevant.md", "similarity": 0.60},
                        {"path": "file1.md", "similarity": 0.95},
                        {"path": "file2.md", "similarity": 0.90}
                    ]
                }
            ]
            
            metrics_comparison = []
            
            for test_case in test_cases:
                f.write(f"\n{test_case['name']}:\n")
                
                quality_metrics = self.calculate_retrieval_quality(
                    "test query",
                    test_case["results"],
                    relevant_files
                )
                
                f.write(f"  Precision@K: {quality_metrics['precision_at_k']:.3f}\n")
                f.write(f"  Recall: {quality_metrics['recall']:.3f}\n")
                f.write(f"  MRR: {quality_metrics['mrr']:.3f}\n")
                f.write(f"  NDCG: {quality_metrics['ndcg']:.3f}\n")
                f.write(f"  Overall: {quality_metrics['overall_quality']:.3f}\n")
                
                metrics_comparison.append(quality_metrics)
            
            # Check if metrics are consistent (best order should have better scores)
            best_order = metrics_comparison[0]
            worst_order = metrics_comparison[1]
            
            consistency_checks = [
                ("Precision@K", best_order['precision_at_k'] >= worst_order['precision_at_k']),
                ("MRR", best_order['mrr'] >= worst_order['mrr']),
                ("NDCG", best_order['ndcg'] >= worst_order['ndcg']),
                ("Overall", best_order['overall_quality'] >= worst_order['overall_quality'])
            ]
            
            f.write(f"\nConsistency Checks:\n")
            all_consistent = True
            for metric_name, is_consistent in consistency_checks:
                status = "✅" if is_consistent else "❌"
                f.write(f"  {metric_name}: {status}\n")
                if not is_consistent:
                    all_consistent = False
            
            f.write(f"\nOverall Consistency: {'✅ GOOD' if all_consistent else '❌ POOR'}\n")
            
            return {
                "all_consistent": all_consistent,
                "consistency_checks": consistency_checks
            }
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive quality scoring validation"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("🚀 Comprehensive Quality Scoring Validation\n")
            f.write("=" * 50 + "\n")
        
        # Run all tests
        scoring_results = self.test_quality_scoring()
        consistency_results = self.test_metric_consistency()
        
        # Calculate overall validation score
        scoring_score = scoring_results["success_rate"]
        consistency_score = 1.0 if consistency_results["all_consistent"] else 0.0
        
        overall_score = (scoring_score * 0.7 + consistency_score * 0.3)
        
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n🎯 Overall Validation Results\n")
            f.write("=" * 40 + "\n")
            f.write(f"Scoring Score: {scoring_score:.3f}\n")
            f.write(f"Consistency Score: {consistency_score:.3f}\n")
            f.write(f"Overall Score: {overall_score:.3f}\n")
            f.write(f"Status: {'✅ PASS' if overall_score >= 0.8 else '❌ FAIL'}\n")
        
        return {
            "overall_score": overall_score,
            "scoring_results": scoring_results,
            "consistency_results": consistency_results,
            "passed": overall_score >= 0.8
        }

# Test the quality scoring validator
if __name__ == "__main__":
    validator = FileBasedQualityScoringMetrics()
    results = validator.run_comprehensive_validation()
    
    print(f"Test completed. Check {validator.output_file} for results.")
    print(f"Final Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")

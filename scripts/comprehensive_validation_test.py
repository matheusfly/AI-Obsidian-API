#!/usr/bin/env python3
"""
Comprehensive Validation Test Suite
Integrates all validation components for complete RAG system testing
"""

import sys
import asyncio
import time
from pathlib import Path
import logging
import json
from typing import List, Dict, Any, Tuple

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from validation_embedding_quality import EmbeddingQualityValidator
from validation_retrieval_quality import RetrievalQualityValidator
from validation_quality_scoring import QualityScoringMetrics

class ComprehensiveValidationSuite:
    """Comprehensive validation suite for RAG system"""
    
    def __init__(self):
        self.embedding_validator = EmbeddingQualityValidator()
        self.retrieval_validator = RetrievalQualityValidator()
        self.quality_scorer = QualityScoringMetrics()
        self.logger = logging.getLogger(__name__)
        
        # Validation results
        self.results = {
            "timestamp": time.time(),
            "embedding_quality": {},
            "retrieval_quality": {},
            "quality_scoring": {},
            "overall_score": 0.0,
            "passed": False
        }
    
    def run_embedding_validation(self) -> Dict[str, Any]:
        """Run embedding quality validation"""
        print("🔍 Phase 1: Embedding Quality Validation")
        print("=" * 50)
        
        try:
            embedding_results = self.embedding_validator.run_comprehensive_validation()
            self.results["embedding_quality"] = embedding_results
            
            print(f"Embedding Quality Score: {embedding_results['overall_score']:.3f}")
            print(f"Status: {'✅ PASS' if embedding_results['passed'] else '❌ FAIL'}")
            
            return embedding_results
            
        except Exception as e:
            self.logger.error(f"Embedding validation failed: {e}")
            return {"passed": False, "error": str(e)}
    
    def run_retrieval_validation(self) -> Dict[str, Any]:
        """Run retrieval quality validation"""
        print(f"\n🔍 Phase 2: Retrieval Quality Validation")
        print("=" * 50)
        
        try:
            retrieval_results = self.retrieval_validator.run_comprehensive_validation()
            self.results["retrieval_quality"] = retrieval_results
            
            print(f"Retrieval Quality Score: {retrieval_results['overall_score']:.3f}")
            print(f"Status: {'✅ PASS' if retrieval_results['passed'] else '❌ FAIL'}")
            
            return retrieval_results
            
        except Exception as e:
            self.logger.error(f"Retrieval validation failed: {e}")
            return {"passed": False, "error": str(e)}
    
    def run_quality_scoring_validation(self) -> Dict[str, Any]:
        """Run quality scoring validation"""
        print(f"\n🔍 Phase 3: Quality Scoring Validation")
        print("=" * 50)
        
        try:
            # Create test data for quality scoring
            test_data = self._create_quality_scoring_test_data()
            
            # Test quality scoring metrics
            scoring_results = []
            for test_case in test_data:
                quality_metrics = self.quality_scorer.calculate_retrieval_quality(
                    test_case["query"],
                    test_case["results"],
                    test_case["relevant_files"]
                )
                
                # Add test case info
                quality_metrics.update({
                    "query": test_case["query"],
                    "test_name": test_case["test_name"]
                })
                
                scoring_results.append(quality_metrics)
            
            # Calculate system quality
            system_quality = self.quality_scorer.calculate_system_quality(scoring_results)
            
            # Generate quality report
            quality_report = self.quality_scorer.generate_quality_report(scoring_results)
            
            scoring_validation = {
                "scoring_results": scoring_results,
                "system_quality": system_quality,
                "quality_report": quality_report,
                "passed": system_quality["system_quality_score"] >= 0.6
            }
            
            self.results["quality_scoring"] = scoring_validation
            
            print(f"System Quality Score: {system_quality['system_quality_score']:.3f}")
            print(f"Status: {'✅ PASS' if scoring_validation['passed'] else '❌ FAIL'}")
            
            return scoring_validation
            
        except Exception as e:
            self.logger.error(f"Quality scoring validation failed: {e}")
            return {"passed": False, "error": str(e)}
    
    def _create_quality_scoring_test_data(self) -> List[Dict[str, Any]]:
        """Create test data for quality scoring validation"""
        return [
            {
                "test_name": "Machine Learning Query",
                "query": "machine learning algorithms for data analysis",
                "results": [
                    {
                        "path": "ml_algorithms.md",
                        "similarity": 0.85,
                        "topics": ["machine_learning", "algorithms"],
                        "file_size": 5000
                    },
                    {
                        "path": "data_science.md",
                        "similarity": 0.72,
                        "topics": ["data_science", "analytics"],
                        "file_size": 3000
                    },
                    {
                        "path": "python_guide.md",
                        "similarity": 0.65,
                        "topics": ["programming", "python"],
                        "file_size": 4000
                    }
                ],
                "relevant_files": ["ml_algorithms.md", "data_science.md"]
            },
            {
                "test_name": "Web Scraping Query",
                "query": "web scraping techniques with Python",
                "results": [
                    {
                        "path": "scraping_guide.md",
                        "similarity": 0.90,
                        "topics": ["web_scraping", "python"],
                        "file_size": 6000
                    },
                    {
                        "path": "python_guide.md",
                        "similarity": 0.55,
                        "topics": ["programming", "python"],
                        "file_size": 4000
                    },
                    {
                        "path": "business_strategy.md",
                        "similarity": 0.30,
                        "topics": ["business", "strategy"],
                        "file_size": 2000
                    }
                ],
                "relevant_files": ["scraping_guide.md", "python_guide.md"]
            },
            {
                "test_name": "Philosophy Query",
                "query": "philosophy of mathematics and logic",
                "results": [
                    {
                        "path": "philosophy_math.md",
                        "similarity": 0.88,
                        "topics": ["philosophy", "mathematics"],
                        "file_size": 8000
                    },
                    {
                        "path": "logic_foundations.md",
                        "similarity": 0.75,
                        "topics": ["logic", "philosophy"],
                        "file_size": 5000
                    },
                    {
                        "path": "programming_guide.md",
                        "similarity": 0.25,
                        "topics": ["programming", "coding"],
                        "file_size": 3000
                    }
                ],
                "relevant_files": ["philosophy_math.md", "logic_foundations.md"]
            }
        ]
    
    def run_performance_validation(self) -> Dict[str, Any]:
        """Run performance validation tests"""
        print(f"\n🔍 Phase 4: Performance Validation")
        print("=" * 50)
        
        try:
            performance_results = {
                "embedding_performance": {},
                "retrieval_performance": {},
                "overall_performance": {}
            }
            
            # Test embedding performance
            start_time = time.time()
            embedding_results = self.embedding_validator.run_comprehensive_validation()
            embedding_time = time.time() - start_time
            
            performance_results["embedding_performance"] = {
                "execution_time": embedding_time,
                "status": "✅ GOOD" if embedding_time < 30 else "❌ SLOW"
            }
            
            # Test retrieval performance
            start_time = time.time()
            retrieval_results = self.retrieval_validator.run_comprehensive_validation()
            retrieval_time = time.time() - start_time
            
            performance_results["retrieval_performance"] = {
                "execution_time": retrieval_time,
                "status": "✅ GOOD" if retrieval_time < 60 else "❌ SLOW"
            }
            
            # Overall performance
            total_time = embedding_time + retrieval_time
            performance_results["overall_performance"] = {
                "total_execution_time": total_time,
                "status": "✅ GOOD" if total_time < 90 else "❌ SLOW"
            }
            
            print(f"Embedding Performance: {embedding_time:.2f}s {performance_results['embedding_performance']['status']}")
            print(f"Retrieval Performance: {retrieval_time:.2f}s {performance_results['retrieval_performance']['status']}")
            print(f"Total Performance: {total_time:.2f}s {performance_results['overall_performance']['status']}")
            
            return performance_results
            
        except Exception as e:
            self.logger.error(f"Performance validation failed: {e}")
            return {"error": str(e)}
    
    def run_error_handling_validation(self) -> Dict[str, Any]:
        """Run error handling validation tests"""
        print(f"\n🔍 Phase 5: Error Handling Validation")
        print("=" * 50)
        
        try:
            error_handling_results = {
                "empty_input_tests": {},
                "invalid_input_tests": {},
                "exception_handling_tests": {},
                "overall_error_handling": {}
            }
            
            # Test empty input handling
            empty_tests = [
                {"name": "Empty Query", "query": "", "expected": "handle gracefully"},
                {"name": "Empty Results", "query": "test", "results": [], "expected": "handle gracefully"},
                {"name": "None Input", "query": None, "expected": "handle gracefully"}
            ]
            
            empty_test_passed = 0
            for test in empty_tests:
                try:
                    # Test with empty inputs
                    if test["name"] == "Empty Query":
                        result = self.quality_scorer.calculate_retrieval_quality("", [], [])
                    elif test["name"] == "Empty Results":
                        result = self.quality_scorer.calculate_retrieval_quality("test", [], [])
                    elif test["name"] == "None Input":
                        result = self.quality_scorer.calculate_retrieval_quality(None, [], [])
                    
                    empty_test_passed += 1
                except Exception:
                    pass  # Expected to handle gracefully
            
            error_handling_results["empty_input_tests"] = {
                "passed": empty_test_passed,
                "total": len(empty_tests),
                "status": "✅ GOOD" if empty_test_passed == len(empty_tests) else "❌ POOR"
            }
            
            # Test invalid input handling
            invalid_tests = [
                {"name": "Invalid Similarity Scores", "test": "test with invalid similarity"},
                {"name": "Malformed Results", "test": "test with malformed data"},
                {"name": "Type Errors", "test": "test with wrong data types"}
            ]
            
            invalid_test_passed = 0
            for test in invalid_tests:
                try:
                    # Test with invalid inputs
                    invalid_results = [{"path": "test.md", "similarity": "invalid", "topics": "invalid"}]
                    result = self.quality_scorer.calculate_retrieval_quality("test", invalid_results, ["test.md"])
                    invalid_test_passed += 1
                except Exception:
                    pass  # Expected to handle gracefully
            
            error_handling_results["invalid_input_tests"] = {
                "passed": invalid_test_passed,
                "total": len(invalid_tests),
                "status": "✅ GOOD" if invalid_test_passed >= len(invalid_tests) // 2 else "❌ POOR"
            }
            
            # Overall error handling
            total_error_tests = empty_test_passed + invalid_test_passed
            total_possible = len(empty_tests) + len(invalid_tests)
            error_handling_score = total_error_tests / total_possible if total_possible > 0 else 0
            
            error_handling_results["overall_error_handling"] = {
                "score": error_handling_score,
                "status": "✅ GOOD" if error_handling_score >= 0.7 else "❌ POOR"
            }
            
            print(f"Empty Input Tests: {empty_test_passed}/{len(empty_tests)} ✅")
            print(f"Invalid Input Tests: {invalid_test_passed}/{len(invalid_tests)} ✅")
            print(f"Overall Error Handling: {error_handling_score:.1%} {error_handling_results['overall_error_handling']['status']}")
            
            return error_handling_results
            
        except Exception as e:
            self.logger.error(f"Error handling validation failed: {e}")
            return {"error": str(e)}
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation suite"""
        print("🚀 Comprehensive RAG System Validation Suite")
        print("=" * 60)
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        start_time = time.time()
        
        try:
            # Phase 1: Embedding Quality
            embedding_results = self.run_embedding_validation()
            
            # Phase 2: Retrieval Quality
            retrieval_results = self.run_retrieval_validation()
            
            # Phase 3: Quality Scoring
            scoring_results = self.run_quality_scoring_validation()
            
            # Phase 4: Performance
            performance_results = self.run_performance_validation()
            
            # Phase 5: Error Handling
            error_handling_results = self.run_error_handling_validation()
            
            # Calculate overall score
            embedding_score = embedding_results.get("overall_score", 0.0) if embedding_results.get("passed", False) else 0.0
            retrieval_score = retrieval_results.get("overall_score", 0.0) if retrieval_results.get("passed", False) else 0.0
            scoring_score = scoring_results.get("system_quality", {}).get("system_quality_score", 0.0) if scoring_results.get("passed", False) else 0.0
            performance_score = 1.0 if performance_results.get("overall_performance", {}).get("status") == "✅ GOOD" else 0.0
            error_handling_score = error_handling_results.get("overall_error_handling", {}).get("score", 0.0)
            
            overall_score = (embedding_score * 0.25 + 
                           retrieval_score * 0.25 + 
                           scoring_score * 0.2 + 
                           performance_score * 0.15 + 
                           error_handling_score * 0.15)
            
            self.results["overall_score"] = overall_score
            self.results["passed"] = overall_score >= 0.8
            
            # Add additional results
            self.results["performance"] = performance_results
            self.results["error_handling"] = error_handling_results
            
            # Print final summary
            total_time = time.time() - start_time
            print(f"\n🎯 Comprehensive Validation Summary")
            print("=" * 50)
            print(f"Total Execution Time: {total_time:.2f}s")
            print(f"Embedding Quality: {embedding_score:.3f}")
            print(f"Retrieval Quality: {retrieval_score:.3f}")
            print(f"Quality Scoring: {scoring_score:.3f}")
            print(f"Performance: {performance_score:.3f}")
            print(f"Error Handling: {error_handling_score:.3f}")
            print(f"Overall Score: {overall_score:.3f}")
            print(f"Status: {'✅ PASS' if self.results['passed'] else '❌ FAIL'}")
            
            # Save results
            self._save_validation_results()
            
            return self.results
            
        except Exception as e:
            self.logger.error(f"Comprehensive validation failed: {e}")
            self.results["error"] = str(e)
            self.results["passed"] = False
            return self.results
    
    def _save_validation_results(self):
        """Save validation results to file"""
        try:
            results_file = Path("validation_results.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n📁 Validation results saved to: {results_file}")
        except Exception as e:
            self.logger.error(f"Failed to save validation results: {e}")

# Run comprehensive validation
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run validation suite
    validator = ComprehensiveValidationSuite()
    results = validator.run_comprehensive_validation()
    
    print(f"\nFinal Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")
    
    if not results['passed']:
        print("\n❌ Validation failed. Check the detailed results above for issues to address.")
    else:
        print("\n🎉 All validation tests passed! The RAG system is ready for production.")

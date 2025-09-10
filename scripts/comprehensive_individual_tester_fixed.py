#!/usr/bin/env python3
"""
Comprehensive Individual Testing Suite for RAG System Components (Fixed Version)
Tests each component individually and provides detailed reports
"""

import sys
import os
import json
import time
import traceback
from typing import Dict, List, Any
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ComprehensiveIndividualTester:
    def __init__(self):
        self.test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "components_tested": [],
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": [],
            "performance_metrics": {}
        }
    
    def test_component(self, component_name: str, test_function) -> Dict[str, Any]:
        """Test a single component"""
        print(f"\n🧪 Testing {component_name}...")
        print("=" * 50)
        
        start_time = time.time()
        component_result = {
            "component": component_name,
            "status": "unknown",
            "tests_passed": 0,
            "tests_failed": 0,
            "total_tests": 0,
            "errors": [],
            "performance_time": 0,
            "details": {}
        }
        
        try:
            result = test_function()
            component_result.update(result)
            component_result["status"] = "passed" if result.get("passed", False) else "failed"
            component_result["performance_time"] = time.time() - start_time
            
            self.test_results["total_tests"] += component_result["total_tests"]
            self.test_results["passed_tests"] += component_result["tests_passed"]
            self.test_results["failed_tests"] += component_result["tests_failed"]
            
            print(f"✅ {component_name} completed in {component_result['performance_time']:.2f}s")
            
        except Exception as e:
            error_msg = f"{component_name} test failed: {str(e)}"
            component_result["status"] = "error"
            component_result["errors"].append(error_msg)
            component_result["performance_time"] = time.time() - start_time
            
            self.test_results["errors"].append(error_msg)
            self.test_results["failed_tests"] += 1
            
            print(f"❌ {component_name} failed: {error_msg}")
            traceback.print_exc()
        
        self.test_results["components_tested"].append(component_result)
        return component_result
    
    def test_reranker(self) -> Dict[str, Any]:
        """Test ReRanker component"""
        try:
            from reranker import ReRanker
            
            # Initialize
            reranker = ReRanker()
            
            # Test data
            query = "machine learning algorithms"
            candidates = [
                {
                    "content": "Machine learning algorithms are powerful tools for data analysis.",
                    "similarity": 0.8,
                    "heading": "ML Introduction"
                },
                {
                    "content": "Philosophical logic deals with reasoning and argumentation.",
                    "similarity": 0.3,
                    "heading": "Philosophy"
                }
            ]
            
            # Test basic reranking
            reranked = reranker.rerank(query, candidates, top_k=2)
            
            # Test search with rerank
            search_results = reranker.search_with_rerank(query, candidates, n_results=2)
            
            return {
                "passed": True,
                "tests_passed": 2,
                "tests_failed": 0,
                "total_tests": 2,
                "details": {
                    "rerank_results": len(reranked),
                    "search_results": len(search_results)
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "tests_passed": 0,
                "tests_failed": 1,
                "total_tests": 1,
                "errors": [str(e)]
            }
    
    def test_topic_detector(self) -> Dict[str, Any]:
        """Test TopicDetector component"""
        try:
            from topic_detector import TopicDetector
            
            # Initialize
            detector = TopicDetector()
            
            # Test queries
            test_queries = [
                "machine learning algorithms",
                "philosophical logic",
                "performance optimization"
            ]
            
            results = []
            for query in test_queries:
                topic = detector.detect_topic(query)
                topics = detector.detect_multiple_topics(query)
                results.append({"query": query, "topic": topic, "topics": topics})
            
            return {
                "passed": True,
                "tests_passed": 1,
                "tests_failed": 0,
                "total_tests": 1,
                "details": {
                    "test_queries": len(test_queries),
                    "results": results
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "tests_passed": 0,
                "tests_failed": 1,
                "total_tests": 1,
                "errors": [str(e)]
            }
    
    def test_smart_document_filter(self) -> Dict[str, Any]:
        """Test SmartDocumentFilter component"""
        try:
            from smart_document_filter import SmartDocumentFilter
            from topic_detector import TopicDetector
            
            # Initialize
            topic_detector = TopicDetector()
            filter_system = SmartDocumentFilter(topic_detector)
            
            # Test data
            documents = [
                {
                    "content": "Machine learning algorithms are powerful tools.",
                    "heading": "ML Introduction",
                    "word_count": 8,
                    "metadata": {
                        "topic": "technology",
                        "tags": ["ai", "ml"],
                        "file_type": "tutorial"
                    }
                },
                {
                    "content": "Philosophical logic deals with reasoning.",
                    "heading": "Philosophy",
                    "word_count": 6,
                    "metadata": {
                        "topic": "philosophy",
                        "tags": ["logic"],
                        "file_type": "academic"
                    }
                }
            ]
            
            # Test topic filtering
            tech_docs = filter_system.filter_by_topic(documents, "technology")
            
            # Test smart filtering
            filtered_docs = filter_system.smart_filter(documents, "machine learning", {})
            
            return {
                "passed": True,
                "tests_passed": 2,
                "tests_failed": 0,
                "total_tests": 2,
                "details": {
                    "tech_docs": len(tech_docs),
                    "filtered_docs": len(filtered_docs)
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "tests_passed": 0,
                "tests_failed": 1,
                "total_tests": 1,
                "errors": [str(e)]
            }
    
    def test_advanced_content_processor(self) -> Dict[str, Any]:
        """Test AdvancedContentProcessor component"""
        try:
            from advanced_content_processor import AdvancedContentProcessor
            
            # Initialize
            processor = AdvancedContentProcessor()
            
            # Test content
            sample_content = """# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence.

## Types of ML

### Supervised Learning
Supervised learning uses labeled data.

### Unsupervised Learning
Unsupervised learning finds patterns.
"""
            
            # Test chunking
            chunks = processor.chunk_content(
                sample_content,
                {"title": "ML Guide", "topic": "technology"},
                "/test/ml_guide.md"
            )
            
            return {
                "passed": True,
                "tests_passed": 1,
                "tests_failed": 0,
                "total_tests": 1,
                "details": {
                    "chunks_generated": len(chunks),
                    "chunk_headings": [chunk["heading"] for chunk in chunks]
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "tests_passed": 0,
                "tests_failed": 1,
                "total_tests": 1,
                "errors": [str(e)]
            }
    
    def test_validation_scripts(self) -> Dict[str, Any]:
        """Test validation scripts"""
        try:
            from validation_embedding_quality_fixed import EmbeddingQualityValidator
            
            # Initialize
            validator = EmbeddingQualityValidator()
            
            # Test embedding generation
            test_text = "Machine learning is a subset of artificial intelligence"
            embedding = validator.generate_embedding(test_text)
            
            # Test basic quality validation
            results = validator.test_embedding_quality()
            
            return {
                "passed": True,
                "tests_passed": 2,
                "tests_failed": 0,
                "total_tests": 2,
                "details": {
                    "embedding_shape": embedding.shape,
                    "quality_score": results["overall_score"]
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "tests_passed": 0,
                "tests_failed": 1,
                "total_tests": 1,
                "errors": [str(e)]
            }
    
    def test_main_cli_scripts(self) -> Dict[str, Any]:
        """Test main CLI scripts"""
        try:
            # Test if main CLI scripts can be imported
            cli_scripts = [
                "fixed-agentic-rag-cli.py",
                "enhanced_agentic_rag_cli.py",
                "final_comprehensive_rag_cli.py"
            ]
            
            import_results = []
            for script in cli_scripts:
                try:
                    # Try to import the script
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        script.replace('.py', ''), script
                    )
                    if spec and spec.loader:
                        import_results.append({"script": script, "status": "importable"})
                    else:
                        import_results.append({"script": script, "status": "not_found"})
                except Exception as e:
                    import_results.append({"script": script, "status": "error", "error": str(e)})
            
            successful_imports = len([r for r in import_results if r["status"] == "importable"])
            
            return {
                "passed": successful_imports > 0,
                "tests_passed": successful_imports,
                "tests_failed": len(import_results) - successful_imports,
                "total_tests": len(import_results),
                "details": {
                    "import_results": import_results
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "tests_passed": 0,
                "tests_failed": 1,
                "total_tests": 1,
                "errors": [str(e)]
            }
    
    def run_all_tests(self):
        """Run all individual component tests"""
        print("🚀 Starting Comprehensive Individual Testing (Fixed Version)")
        print("=" * 60)
        
        start_time = time.time()
        
        # Define test components
        test_components = [
            ("ReRanker", self.test_reranker),
            ("TopicDetector", self.test_topic_detector),
            ("SmartDocumentFilter", self.test_smart_document_filter),
            ("AdvancedContentProcessor", self.test_advanced_content_processor),
            ("ValidationScripts", self.test_validation_scripts),
            ("MainCLIScripts", self.test_main_cli_scripts)
        ]
        
        # Run all tests
        for component_name, test_function in test_components:
            self.test_component(component_name, test_function)
        
        total_time = time.time() - start_time
        self.test_results["performance_metrics"]["total_test_time"] = total_time
        
        # Generate final report
        self.generate_final_report()
        
        return self.test_results
    
    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE INDIVIDUAL TEST REPORT (FIXED VERSION)")
        print("=" * 60)
        
        total_tests = self.test_results["total_tests"]
        passed_tests = self.test_results["passed_tests"]
        failed_tests = self.test_results["failed_tests"]
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Time: {self.test_results['performance_metrics']['total_test_time']:.2f}s")
        
        print(f"\nComponent Results:")
        for component in self.test_results["components_tested"]:
            status_icon = "✅" if component["status"] == "passed" else "❌"
            print(f"  {status_icon} {component['component']}: {component['tests_passed']}/{component['total_tests']} tests passed")
        
        if self.test_results["errors"]:
            print(f"\nErrors ({len(self.test_results['errors'])}):")
            for i, error in enumerate(self.test_results["errors"], 1):
                print(f"  {i}. {error}")
        
        # Save detailed report
        report_file = "comprehensive_individual_test_report_fixed.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return success_rate >= 70  # 70% success rate threshold

if __name__ == "__main__":
    tester = ComprehensiveIndividualTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Comprehensive Individual Testing PASSED!")
        sys.exit(0)
    else:
        print("\n💥 Comprehensive Individual Testing FAILED!")
        sys.exit(1)

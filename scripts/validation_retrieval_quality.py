#!/usr/bin/env python3
"""
Validation Testing: Retrieval Quality
Step 2: Test Retrieval Quality - Create a test suite for common query types
"""

import sys
import numpy as np
from pathlib import Path
import logging
from typing import List, Dict, Any, Tuple
import json
import tempfile
import os

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from topic_extractor import TopicExtractor
from enhanced_content_processor import EnhancedContentProcessor

class RetrievalQualityValidator:
    """Validator for retrieval quality and search performance"""
    
    def __init__(self):
        self.topic_extractor = TopicExtractor()
        self.processor = EnhancedContentProcessor()
        self.logger = logging.getLogger(__name__)
        
        # Test cases for retrieval validation
        self.test_cases = [
            {
                "query": "What are the main philosophical currents of logic and mathematics?",
                "expected_files": ["philosophy_of_math.md", "logic_foundations.md", "mathematical_philosophy.md"],
                "min_similarity": 0.6,
                "category": "philosophy",
                "description": "Philosophy and mathematics query"
            },
            {
                "query": "How does Scrapy handle web scraping?",
                "expected_files": ["scrapy_guide.md", "web_scraping_techniques.md", "python_scraping.md"],
                "min_similarity": 0.6,
                "category": "programming",
                "description": "Web scraping and Python query"
            },
            {
                "query": "What is the PQLP reading technique?",
                "expected_files": ["hyper_reading.md", "reading_techniques.md", "speed_reading.md"],
                "min_similarity": 0.6,
                "category": "learning",
                "description": "Reading techniques query"
            },
            {
                "query": "Machine learning algorithms for data analysis",
                "expected_files": ["ml_algorithms.md", "data_analysis.md", "machine_learning.md"],
                "min_similarity": 0.6,
                "category": "technical",
                "description": "Machine learning and data analysis query"
            },
            {
                "query": "Business strategy and competitive advantage",
                "expected_files": ["business_strategy.md", "competitive_analysis.md", "strategy_planning.md"],
                "min_similarity": 0.6,
                "category": "business",
                "description": "Business strategy query"
            },
            {
                "query": "Python programming best practices",
                "expected_files": ["python_guide.md", "programming_best_practices.md", "python_tips.md"],
                "min_similarity": 0.6,
                "category": "programming",
                "description": "Python programming query"
            }
        ]
        
        # Create test documents
        self.test_documents = self._create_test_documents()
    
    def _create_test_documents(self) -> Dict[str, str]:
        """Create test documents for validation"""
        documents = {
            "philosophy_of_math.md": """
            # Philosophy of Mathematics
            
            The philosophy of mathematics examines the nature of mathematical objects and truth.
            Main philosophical currents include:
            
            ## Platonism
            Mathematical objects exist independently of human thought and are discovered rather than invented.
            
            ## Formalism
            Mathematics is a game played with symbols according to formal rules.
            
            ## Intuitionism
            Mathematical truth is constructed through mental processes.
            
            ## Logicism
            Mathematics can be reduced to logic.
            """,
            
            "logic_foundations.md": """
            # Foundations of Logic
            
            Logic provides the foundation for mathematical reasoning and philosophical analysis.
            
            ## Propositional Logic
            Deals with simple statements and their logical relationships.
            
            ## Predicate Logic
            Extends propositional logic to include quantifiers and predicates.
            
            ## Modal Logic
            Studies necessity and possibility in logical contexts.
            
            ## Philosophical Logic
            Examines the nature of logical reasoning and argumentation.
            """,
            
            "scrapy_guide.md": """
            # Scrapy Web Scraping Guide
            
            Scrapy is a powerful Python framework for web scraping.
            
            ## Installation
            ```bash
            pip install scrapy
            ```
            
            ## Basic Usage
            ```python
            import scrapy
            
            class MySpider(scrapy.Spider):
                name = 'myspider'
                start_urls = ['http://example.com']
                
                def parse(self, response):
                    yield {'title': response.css('title::text').get()}
            ```
            
            ## Features
            - Built-in selectors
            - Automatic request handling
            - Data export capabilities
            - Middleware support
            """,
            
            "web_scraping_techniques.md": """
            # Web Scraping Techniques
            
            Various techniques for extracting data from websites.
            
            ## HTML Parsing
            - BeautifulSoup for HTML parsing
            - lxml for XML processing
            - Selector-based extraction
            
            ## API Scraping
            - REST API consumption
            - GraphQL queries
            - Rate limiting and authentication
            
            ## Anti-Scraping Measures
            - User agent rotation
            - Proxy usage
            - CAPTCHA solving
            - JavaScript rendering
            """,
            
            "hyper_reading.md": """
            # Hyper Reading Techniques
            
            Hyper reading is a method for processing large amounts of text efficiently.
            
            ## PQLP Method
            The PQLP (Preview, Question, Look, Ponder) technique:
            1. Preview the text structure
            2. Generate questions about the content
            3. Look for answers to your questions
            4. Ponder the implications
            
            ## Speed Reading
            - Eliminate subvocalization
            - Use peripheral vision
            - Practice with easy texts
            - Increase reading speed gradually
            
            ## Active Reading
            - Take notes while reading
            - Ask questions about the content
            - Connect new information to existing knowledge
            - Summarize key points
            """,
            
            "ml_algorithms.md": """
            # Machine Learning Algorithms
            
            Overview of machine learning algorithms for data analysis.
            
            ## Supervised Learning
            - Linear Regression
            - Decision Trees
            - Random Forests
            - Support Vector Machines
            - Neural Networks
            
            ## Unsupervised Learning
            - K-Means Clustering
            - Hierarchical Clustering
            - Principal Component Analysis
            - Autoencoders
            
            ## Deep Learning
            - Convolutional Neural Networks
            - Recurrent Neural Networks
            - Transformer Models
            - Generative Adversarial Networks
            """,
            
            "business_strategy.md": """
            # Business Strategy and Competitive Advantage
            
            Strategic planning for sustainable competitive advantage.
            
            ## Strategic Analysis
            - SWOT Analysis
            - Porter's Five Forces
            - Value Chain Analysis
            - Competitive Positioning
            
            ## Strategy Formulation
            - Vision and Mission
            - Strategic Objectives
            - Resource Allocation
            - Risk Assessment
            
            ## Implementation
            - Action Plans
            - Performance Metrics
            - Change Management
            - Continuous Monitoring
            """,
            
            "python_guide.md": """
            # Python Programming Guide
            
            Best practices and techniques for Python development.
            
            ## Code Style
            - Follow PEP 8 guidelines
            - Use meaningful variable names
            - Write docstrings for functions
            - Keep functions small and focused
            
            ## Performance
            - Use list comprehensions
            - Avoid global variables
            - Profile your code
            - Use appropriate data structures
            
            ## Testing
            - Write unit tests
            - Use pytest framework
            - Test edge cases
            - Maintain test coverage
            """
        }
        return documents
    
    def create_test_environment(self) -> Path:
        """Create a temporary test environment with documents"""
        temp_dir = Path(tempfile.mkdtemp(prefix="rag_validation_"))
        
        # Create test documents
        for filename, content in self.test_documents.items():
            file_path = temp_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return temp_dir
    
    def mock_search_service(self, query: str, documents: Dict[str, str], n_results: int = 5) -> List[Dict[str, Any]]:
        """Mock search service for testing (simplified version)"""
        # Generate query embedding
        query_embedding = self.topic_extractor.generate_embedding(query) if hasattr(self.topic_extractor, 'generate_embedding') else np.random.rand(384)
        
        results = []
        for filename, content in documents.items():
            # Generate document embedding
            doc_embedding = self.topic_extractor.generate_embedding(content) if hasattr(self.topic_extractor, 'generate_embedding') else np.random.rand(384)
            
            # Calculate similarity
            similarity = np.dot(query_embedding, doc_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding))
            
            results.append({
                "path": filename,
                "content": content[:200] + "...",
                "similarity": float(similarity),
                "file_size": len(content)
            })
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:n_results]
    
    def test_retrieval_quality(self) -> Dict[str, Any]:
        """Test retrieval quality for different query types"""
        print("🧪 Retrieval Quality Validation Test")
        print("=" * 50)
        
        # Create test environment
        test_dir = self.create_test_environment()
        
        try:
            results = {
                "total_tests": len(self.test_cases),
                "passed_tests": 0,
                "failed_tests": 0,
                "test_results": [],
                "overall_score": 0.0
            }
            
            for i, test_case in enumerate(self.test_cases, 1):
                print(f"\nTest {i}: {test_case['description']}")
                print(f"Query: '{test_case['query']}'")
                
                try:
                    # Perform search
                    search_results = self.mock_search_service(
                        test_case["query"], 
                        self.test_documents, 
                        n_results=5
                    )
                    
                    # Check if expected files are in results
                    found_expected = []
                    for result in search_results:
                        for expected_file in test_case["expected_files"]:
                            if expected_file in result["path"]:
                                found_expected.append(result)
                                break
                    
                    # Calculate metrics
                    precision_at_k = len(found_expected) / len(search_results)
                    recall = len(found_expected) / len(test_case["expected_files"])
                    
                    # Check similarity scores
                    highest_similarity = max(result["similarity"] for result in search_results) if search_results else 0
                    expected_similarity_met = highest_similarity >= test_case["min_similarity"]
                    
                    # Check if irrelevant files are ranked too high
                    irrelevant_results = [r for r in search_results if r not in found_expected]
                    irrelevant_similarity = max(r["similarity"] for r in irrelevant_results) if irrelevant_results else 0
                    irrelevant_ok = irrelevant_similarity < 0.5
                    
                    # Determine if test passed
                    test_passed = (len(found_expected) > 0 and 
                                 expected_similarity_met and 
                                 irrelevant_ok)
                    
                    test_result = {
                        "test_name": test_case["description"],
                        "query": test_case["query"],
                        "expected_files": test_case["expected_files"],
                        "found_expected": len(found_expected),
                        "total_expected": len(test_case["expected_files"]),
                        "precision_at_k": precision_at_k,
                        "recall": recall,
                        "highest_similarity": highest_similarity,
                        "irrelevant_similarity": irrelevant_similarity,
                        "passed": test_passed
                    }
                    
                    results["test_results"].append(test_result)
                    
                    if test_passed:
                        results["passed_tests"] += 1
                        print(f"✅ PASS - Found {len(found_expected)}/{len(test_case['expected_files'])} expected files")
                        print(f"   Precision@K: {precision_at_k:.3f}, Recall: {recall:.3f}")
                        print(f"   Highest Similarity: {highest_similarity:.3f}")
                    else:
                        results["failed_tests"] += 1
                        print(f"❌ FAIL - Found {len(found_expected)}/{len(test_case['expected_files'])} expected files")
                        print(f"   Precision@K: {precision_at_k:.3f}, Recall: {recall:.3f}")
                        print(f"   Highest Similarity: {highest_similarity:.3f}")
                        print(f"   Expected Similarity: {test_case['min_similarity']}")
                    
                    # Show top results
                    print("   Top Results:")
                    for j, result in enumerate(search_results[:3], 1):
                        print(f"     {j}. {result['path']} (similarity: {result['similarity']:.3f})")
                
                except Exception as e:
                    self.logger.error(f"Error in test {test_case['description']}: {e}")
                    results["failed_tests"] += 1
                    test_result = {
                        "test_name": test_case["description"],
                        "error": str(e),
                        "passed": False
                    }
                    results["test_results"].append(test_result)
                    print(f"❌ ERROR - {e}")
            
            # Calculate overall score
            results["overall_score"] = results["passed_tests"] / results["total_tests"]
            
            # Print summary
            print(f"\n📊 Test Summary")
            print(f"Total Tests: {results['total_tests']}")
            print(f"Passed: {results['passed_tests']}")
            print(f"Failed: {results['failed_tests']}")
            print(f"Success Rate: {results['overall_score']:.1%}")
            print(f"Overall Status: {'✅ PASS' if results['overall_score'] >= 0.8 else '❌ FAIL'}")
            
            return results
            
        finally:
            # Clean up test environment
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)
    
    def test_retrieval_consistency(self) -> Dict[str, Any]:
        """Test retrieval consistency for repeated queries"""
        print(f"\n🔄 Retrieval Consistency Test")
        print("-" * 40)
        
        test_query = "machine learning algorithms for data analysis"
        num_tests = 5
        
        # Create test environment
        test_dir = self.create_test_environment()
        
        try:
            results_list = []
            for i in range(num_tests):
                results = self.mock_search_service(test_query, self.test_documents, n_results=3)
                results_list.append(results)
            
            # Calculate consistency metrics
            similarities = []
            for i in range(len(results_list)):
                for j in range(i + 1, len(results_list)):
                    # Compare top result similarities
                    if results_list[i] and results_list[j]:
                        sim1 = results_list[i][0]["similarity"]
                        sim2 = results_list[j][0]["similarity"]
                        similarities.append(abs(sim1 - sim2))
            
            avg_consistency = 1.0 - np.mean(similarities) if similarities else 0.0
            max_variation = np.max(similarities) if similarities else 0.0
            
            print(f"Average Consistency: {avg_consistency:.3f}")
            print(f"Max Variation: {max_variation:.3f}")
            
            is_consistent = avg_consistency > 0.9 and max_variation < 0.1
            print(f"Consistency: {'✅ GOOD' if is_consistent else '❌ POOR'}")
            
            return {
                "avg_consistency": avg_consistency,
                "max_variation": max_variation,
                "is_consistent": is_consistent
            }
            
        finally:
            # Clean up test environment
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive retrieval quality validation"""
        print("🚀 Comprehensive Retrieval Quality Validation")
        print("=" * 60)
        
        # Run all tests
        quality_results = self.test_retrieval_quality()
        consistency_results = self.test_retrieval_consistency()
        
        # Calculate overall validation score
        quality_score = quality_results["overall_score"]
        consistency_score = 1.0 if consistency_results["is_consistent"] else 0.0
        
        overall_score = (quality_score * 0.7 + consistency_score * 0.3)
        
        print(f"\n🎯 Overall Validation Results")
        print("=" * 40)
        print(f"Quality Score: {quality_score:.3f}")
        print(f"Consistency Score: {consistency_score:.3f}")
        print(f"Overall Score: {overall_score:.3f}")
        print(f"Status: {'✅ PASS' if overall_score >= 0.8 else '❌ FAIL'}")
        
        return {
            "overall_score": overall_score,
            "quality_results": quality_results,
            "consistency_results": consistency_results,
            "passed": overall_score >= 0.8
        }

# Test the retrieval quality validator
if __name__ == "__main__":
    validator = RetrievalQualityValidator()
    results = validator.run_comprehensive_validation()
    
    print(f"\nFinal Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")

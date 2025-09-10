#!/usr/bin/env python3
"""
File-based Validation Testing: Retrieval Quality
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

class FileBasedRetrievalQualityValidator:
    """File-based validator for retrieval quality and search performance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.output_file = Path("retrieval_quality_test_results.txt")
        
        # Test cases for retrieval validation
        self.test_cases = [
            {
                "query": "What are the main philosophical currents of logic and mathematics?",
                "expected_files": ["philosophy_of_math.md", "logic_foundations.md"],
                "min_similarity": 0.6,
                "category": "philosophy",
                "description": "Philosophy and mathematics query"
            },
            {
                "query": "How does Scrapy handle web scraping?",
                "expected_files": ["scrapy_guide.md", "web_scraping_techniques.md"],
                "min_similarity": 0.6,
                "category": "programming",
                "description": "Web scraping and Python query"
            },
            {
                "query": "What is the PQLP reading technique?",
                "expected_files": ["hyper_reading.md", "reading_techniques.md"],
                "min_similarity": 0.6,
                "category": "learning",
                "description": "Reading techniques query"
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
            """
        }
        return documents
    
    def simple_embedding(self, text: str) -> np.ndarray:
        """Simple embedding using word frequency (for testing purposes)"""
        # Simple word frequency-based embedding
        words = text.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Create a simple vector (normalized)
        vector = np.zeros(100)  # Fixed size vector
        for i, (word, freq) in enumerate(word_freq.items()):
            if i < 100:  # Limit to first 100 words
                vector[i] = freq
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def mock_search_service(self, query: str, documents: Dict[str, str], n_results: int = 5) -> List[Dict[str, Any]]:
        """Mock search service for testing (simplified version)"""
        # Generate query embedding
        query_embedding = self.simple_embedding(query)
        
        results = []
        for filename, content in documents.items():
            # Generate document embedding
            doc_embedding = self.simple_embedding(content)
            
            # Calculate similarity (cosine similarity)
            similarity = np.dot(query_embedding, doc_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding) + 1e-8)
            
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
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("🧪 Retrieval Quality Validation Test\n")
            f.write("=" * 50 + "\n")
            
            results = {
                "total_tests": len(self.test_cases),
                "passed_tests": 0,
                "failed_tests": 0,
                "test_results": [],
                "overall_score": 0.0
            }
            
            for i, test_case in enumerate(self.test_cases, 1):
                f.write(f"\nTest {i}: {test_case['description']}\n")
                f.write(f"Query: '{test_case['query']}'\n")
                
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
                        f.write(f"✅ PASS - Found {len(found_expected)}/{len(test_case['expected_files'])} expected files\n")
                        f.write(f"   Precision@K: {precision_at_k:.3f}, Recall: {recall:.3f}\n")
                        f.write(f"   Highest Similarity: {highest_similarity:.3f}\n")
                    else:
                        results["failed_tests"] += 1
                        f.write(f"❌ FAIL - Found {len(found_expected)}/{len(test_case['expected_files'])} expected files\n")
                        f.write(f"   Precision@K: {precision_at_k:.3f}, Recall: {recall:.3f}\n")
                        f.write(f"   Highest Similarity: {highest_similarity:.3f}\n")
                        f.write(f"   Expected Similarity: {test_case['min_similarity']}\n")
                    
                    # Show top results
                    f.write("   Top Results:\n")
                    for j, result in enumerate(search_results[:3], 1):
                        f.write(f"     {j}. {result['path']} (similarity: {result['similarity']:.3f})\n")
                
                except Exception as e:
                    self.logger.error(f"Error in test {test_case['description']}: {e}")
                    results["failed_tests"] += 1
                    test_result = {
                        "test_name": test_case["description"],
                        "error": str(e),
                        "passed": False
                    }
                    results["test_results"].append(test_result)
                    f.write(f"❌ ERROR - {e}\n")
            
            # Calculate overall score
            results["overall_score"] = results["passed_tests"] / results["total_tests"]
            
            # Print summary
            f.write(f"\n📊 Test Summary\n")
            f.write(f"Total Tests: {results['total_tests']}\n")
            f.write(f"Passed: {results['passed_tests']}\n")
            f.write(f"Failed: {results['failed_tests']}\n")
            f.write(f"Success Rate: {results['overall_score']:.1%}\n")
            f.write(f"Overall Status: {'✅ PASS' if results['overall_score'] >= 0.8 else '❌ FAIL'}\n")
            
            return results
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive retrieval quality validation"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("🚀 Comprehensive Retrieval Quality Validation\n")
            f.write("=" * 60 + "\n")
        
        # Run all tests
        quality_results = self.test_retrieval_quality()
        
        # Calculate overall validation score
        quality_score = quality_results["overall_score"]
        
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n🎯 Overall Validation Results\n")
            f.write("=" * 40 + "\n")
            f.write(f"Quality Score: {quality_score:.3f}\n")
            f.write(f"Overall Score: {quality_score:.3f}\n")
            f.write(f"Status: {'✅ PASS' if quality_score >= 0.8 else '❌ FAIL'}\n")
        
        return {
            "overall_score": quality_score,
            "quality_results": quality_results,
            "passed": quality_score >= 0.8
        }

# Test the retrieval quality validator
if __name__ == "__main__":
    validator = FileBasedRetrievalQualityValidator()
    results = validator.run_comprehensive_validation()
    
    print(f"Test completed. Check {validator.output_file} for results.")
    print(f"Final Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")

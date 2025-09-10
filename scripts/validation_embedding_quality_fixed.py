#!/usr/bin/env python3
"""
Validation Testing: Embedding Quality (Fixed Version)
Step 1: Verify Embedding Quality - Test if embeddings capture semantic meaning correctly
"""

import sys
import numpy as np
from pathlib import Path
import logging
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

class EmbeddingQualityValidator:
    """Validator for embedding quality and semantic meaning capture"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Test cases for semantic validation
        self.test_cases = [
            {
                "name": "Philosophy vs Programming",
                "text1": "Philosophy of mathematics examines the nature of mathematical objects and truth",
                "text2": "Python programming involves writing code with functions and variables",
                "expected_similarity_range": (0.2, 0.8),
                "description": "Different academic domains should have moderate similarity"
            },
            {
                "name": "Philosophy Subfields",
                "text1": "Platonism asserts that mathematical objects exist independently of human thought",
                "text2": "Formalism views mathematics as a game played with symbols according to formal rules",
                "expected_similarity_range": (0.5, 0.95),
                "description": "Related philosophy topics should have high similarity"
            },
            {
                "name": "Technical vs Non-technical",
                "text1": "Machine learning algorithms use neural networks for pattern recognition",
                "text2": "The weather today is sunny with a chance of rain",
                "expected_similarity_range": (0.1, 0.6),
                "description": "Technical and non-technical content should have low similarity"
            },
            {
                "name": "Similar Technical Concepts",
                "text1": "Deep learning uses multiple layers of neural networks for complex pattern recognition",
                "text2": "Machine learning algorithms learn patterns from data without explicit programming",
                "expected_similarity_range": (0.6, 0.95),
                "description": "Similar technical concepts should have high similarity"
            },
            {
                "name": "Identical Content",
                "text1": "Artificial intelligence is the simulation of human intelligence in machines",
                "text2": "Artificial intelligence is the simulation of human intelligence in machines",
                "expected_similarity_range": (0.95, 1.0),
                "description": "Identical content should have very high similarity"
            },
            {
                "name": "Completely Different",
                "text1": "The cat sat on the mat",
                "text2": "Quantum mechanics describes the behavior of matter at atomic scales",
                "expected_similarity_range": (0.0, 0.4),
                "description": "Completely different content should have low similarity"
            }
        ]
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text using sentence transformers"""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model.encode(text)
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            return np.zeros(384)  # Fallback to zero vector
    
    def test_embedding_quality(self) -> Dict[str, Any]:
        """Test if embeddings capture semantic meaning correctly"""
        print("🧪 Embedding Quality Validation Test")
        print("=" * 50)
        
        results = {
            "total_tests": len(self.test_cases),
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": [],
            "overall_score": 0.0
        }
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\nTest {i}: {test_case['name']}")
            print(f"Description: {test_case['description']}")
            
            try:
                # Generate embeddings
                embedding1 = self.generate_embedding(test_case['text1'])
                embedding2 = self.generate_embedding(test_case['text2'])
                
                # Calculate similarity
                similarity = cosine_similarity([embedding1], [embedding2])[0][0]
                
                # Check if similarity is within expected range
                min_sim, max_sim = test_case['expected_similarity_range']
                is_within_range = min_sim <= similarity <= max_sim
                
                # Determine test result
                test_result = {
                    "test_name": test_case['name'],
                    "text1": test_case['text1'][:50] + "...",
                    "text2": test_case['text2'][:50] + "...",
                    "similarity": similarity,
                    "expected_range": test_case['expected_similarity_range'],
                    "passed": is_within_range,
                    "description": test_case['description']
                }
                
                results["test_results"].append(test_result)
                
                if is_within_range:
                    results["passed_tests"] += 1
                    print(f"✅ PASS - Similarity: {similarity:.3f} (expected: {min_sim:.3f}-{max_sim:.3f})")
                else:
                    results["failed_tests"] += 1
                    print(f"❌ FAIL - Similarity: {similarity:.3f} (expected: {min_sim:.3f}-{max_sim:.3f})")
                
            except Exception as e:
                self.logger.error(f"Error in test {test_case['name']}: {e}")
                results["failed_tests"] += 1
                test_result = {
                    "test_name": test_case['name'],
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
    
    def test_embedding_consistency(self) -> Dict[str, Any]:
        """Test embedding consistency for identical inputs"""
        print(f"\n🔄 Embedding Consistency Test")
        print("-" * 40)
        
        test_text = "Machine learning is a subset of artificial intelligence that focuses on algorithms"
        num_tests = 5
        
        embeddings = []
        for i in range(num_tests):
            embedding = self.generate_embedding(test_text)
            embeddings.append(embedding)
        
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                similarities.append(sim)
        
        avg_similarity = np.mean(similarities)
        min_similarity = np.min(similarities)
        max_similarity = np.max(similarities)
        
        print(f"Average Similarity: {avg_similarity:.6f}")
        print(f"Min Similarity: {min_similarity:.6f}")
        print(f"Max Similarity: {max_similarity:.6f}")
        
        # Consistency should be very high (>0.99)
        is_consistent = avg_similarity > 0.99 and min_similarity > 0.99
        
        print(f"Consistency: {'✅ GOOD' if is_consistent else '❌ POOR'}")
        
        return {
            "avg_similarity": avg_similarity,
            "min_similarity": min_similarity,
            "max_similarity": max_similarity,
            "is_consistent": is_consistent
        }
    
    def test_embedding_dimensionality(self) -> Dict[str, Any]:
        """Test embedding dimensionality and properties"""
        print(f"\n📐 Embedding Dimensionality Test")
        print("-" * 40)
        
        test_text = "This is a test text for dimensionality analysis"
        embedding = self.generate_embedding(test_text)
        
        # Check properties
        dimensionality = len(embedding)
        is_normalized = np.isclose(np.linalg.norm(embedding), 1.0, atol=1e-6)
        has_nan = np.any(np.isnan(embedding))
        has_inf = np.any(np.isinf(embedding))
        
        print(f"Dimensionality: {dimensionality}")
        print(f"Is Normalized: {is_normalized}")
        print(f"Has NaN: {has_nan}")
        print(f"Has Inf: {has_inf}")
        
        # Check if embedding is valid
        is_valid = (dimensionality > 0 and 
                   not has_nan and 
                   not has_inf and 
                   np.any(embedding != 0))  # Not all zeros
        
        print(f"Valid Embedding: {'✅ YES' if is_valid else '❌ NO'}")
        
        return {
            "dimensionality": dimensionality,
            "is_normalized": is_normalized,
            "has_nan": has_nan,
            "has_inf": has_inf,
            "is_valid": is_valid
        }
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive embedding quality validation"""
        print("🚀 Comprehensive Embedding Quality Validation")
        print("=" * 60)
        
        # Run all tests
        quality_results = self.test_embedding_quality()
        consistency_results = self.test_embedding_consistency()
        dimensionality_results = self.test_embedding_dimensionality()
        
        # Calculate overall validation score
        quality_score = quality_results["overall_score"]
        consistency_score = 1.0 if consistency_results["is_consistent"] else 0.0
        validity_score = 1.0 if dimensionality_results["is_valid"] else 0.0
        
        overall_score = (quality_score * 0.5 + consistency_score * 0.3 + validity_score * 0.2)
        
        print(f"\n🎯 Overall Validation Results")
        print("=" * 40)
        print(f"Quality Score: {quality_score:.3f}")
        print(f"Consistency Score: {consistency_score:.3f}")
        print(f"Validity Score: {validity_score:.3f}")
        print(f"Overall Score: {overall_score:.3f}")
        print(f"Status: {'✅ PASS' if overall_score >= 0.8 else '❌ FAIL'}")
        
        return {
            "overall_score": overall_score,
            "quality_results": quality_results,
            "consistency_results": consistency_results,
            "dimensionality_results": dimensionality_results,
            "passed": overall_score >= 0.8
        }

# Test the embedding quality validator
if __name__ == "__main__":
    validator = EmbeddingQualityValidator()
    results = validator.run_comprehensive_validation()
    
    print(f"\nFinal Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")

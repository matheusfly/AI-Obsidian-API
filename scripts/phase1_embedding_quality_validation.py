#!/usr/bin/env python3
"""
Phase 1.1 - Advanced Embedding Quality Validation
Tests semantic similarity accuracy, consistency, and dimensionality
"""

import sys
import numpy as np
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
import json

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_embedding_semantic_accuracy():
    """Test if embeddings capture semantic meaning correctly"""
    print("🧪 Phase 1.1 - Embedding Semantic Accuracy Test")
    print("=" * 55)
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Initialize model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test cases for semantic accuracy
        test_cases = [
            {
                "name": "Philosophy vs Programming",
                "text1": "Philosophy of mathematics examines the nature of mathematical objects and truth",
                "text2": "Python programming involves writing code with functions and variables",
                "expected_similarity_range": (0.1, 0.4),
                "description": "Different domains should have moderate similarity"
            },
            {
                "name": "Philosophy Subfields",
                "text1": "Platonism asserts that mathematical objects exist independently of human thought",
                "text2": "Formalism views mathematics as a game played with symbols according to formal rules",
                "expected_similarity_range": (0.3, 0.7),
                "description": "Related philosophy topics should have high similarity"
            },
            {
                "name": "Technical vs Business",
                "text1": "Machine learning algorithms use statistical methods to find patterns in data",
                "text2": "Business strategy focuses on competitive advantage and market positioning",
                "expected_similarity_range": (0.05, 0.3),
                "description": "Different domains should have low similarity"
            },
            {
                "name": "Identical Content",
                "text1": "The quick brown fox jumps over the lazy dog",
                "text2": "The quick brown fox jumps over the lazy dog",
                "expected_similarity_range": (0.99, 1.0),
                "description": "Identical content should have perfect similarity"
            }
        ]
        
        results = {
            "total_tests": len(test_cases),
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": [],
            "overall_accuracy": 0.0
        }
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['name']}")
            print(f"Description: {test_case['description']}")
            
            try:
                # Generate embeddings
                embeddings = model.encode([test_case['text1'], test_case['text2']])
                similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                
                # Check if similarity is within expected range
                min_expected, max_expected = test_case['expected_similarity_range']
                is_in_range = min_expected <= similarity <= max_expected
                
                test_result = {
                    "test_name": test_case['name'],
                    "text1": test_case['text1'][:50] + "...",
                    "text2": test_case['text2'][:50] + "...",
                    "similarity": float(similarity),
                    "expected_range": test_case['expected_similarity_range'],
                    "passed": is_in_range,
                    "description": test_case['description']
                }
                
                results["test_results"].append(test_result)
                
                if is_in_range:
                    results["passed_tests"] += 1
                    print(f"✅ PASS - Similarity: {similarity:.3f} (expected: {min_expected}-{max_expected})")
                else:
                    results["failed_tests"] += 1
                    print(f"❌ FAIL - Similarity: {similarity:.3f} (expected: {min_expected}-{max_expected})")
                
            except Exception as e:
                print(f"❌ ERROR - {e}")
                results["failed_tests"] += 1
                test_result = {
                    "test_name": test_case['name'],
                    "error": str(e),
                    "passed": False
                }
                results["test_results"].append(test_result)
        
        # Calculate overall accuracy
        results["overall_accuracy"] = results["passed_tests"] / results["total_tests"]
        
        print(f"\n📊 Embedding Accuracy Summary")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Accuracy: {results['overall_accuracy']:.1%}")
        print(f"Status: {'✅ PASS' if results['overall_accuracy'] >= 0.8 else '❌ FAIL'}")
        
        return results
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return {"error": str(e), "passed": False}

def test_embedding_consistency():
    """Test embedding consistency across multiple runs"""
    print(f"\n🔄 Phase 1.1 - Embedding Consistency Test")
    print("-" * 45)
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        test_text = "Machine learning algorithms use statistical methods to find patterns in data"
        
        # Generate embeddings multiple times
        num_runs = 5
        embeddings = []
        
        for i in range(num_runs):
            embedding = model.encode(test_text)
            embeddings.append(embedding)
        
        # Calculate consistency (similarity between runs)
        similarities = []
        for i in range(num_runs):
            for j in range(i + 1, num_runs):
                sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                similarities.append(sim)
        
        avg_consistency = np.mean(similarities)
        min_consistency = np.min(similarities)
        max_consistency = np.max(similarities)
        
        print(f"Average Consistency: {avg_consistency:.6f}")
        print(f"Min Consistency: {min_consistency:.6f}")
        print(f"Max Consistency: {max_consistency:.6f}")
        
        # Consistency should be very high (>0.999)
        is_consistent = avg_consistency > 0.999
        print(f"Consistency: {'✅ EXCELLENT' if is_consistent else '❌ POOR'}")
        
        return {
            "avg_consistency": avg_consistency,
            "min_consistency": min_consistency,
            "max_consistency": max_consistency,
            "is_consistent": is_consistent
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "is_consistent": False}

def test_embedding_dimensionality():
    """Test embedding dimensionality and vector properties"""
    print(f"\n📐 Phase 1.1 - Embedding Dimensionality Test")
    print("-" * 45)
    
    try:
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        test_texts = [
            "Short text",
            "This is a medium length text for testing embedding dimensionality",
            "This is a very long text that contains multiple sentences and should test the embedding model's ability to handle different text lengths and complexities while maintaining consistent dimensionality across all inputs"
        ]
        
        results = {
            "dimensionality_tests": [],
            "all_same_dimension": True,
            "expected_dimension": 384  # all-MiniLM-L6-v2 dimension
        }
        
        for i, text in enumerate(test_texts):
            embedding = model.encode(text)
            dimension = len(embedding)
            
            test_result = {
                "text_length": len(text),
                "embedding_dimension": dimension,
                "is_correct_dimension": dimension == results["expected_dimension"]
            }
            
            results["dimensionality_tests"].append(test_result)
            
            if dimension != results["expected_dimension"]:
                results["all_same_dimension"] = False
            
            print(f"Text {i+1} (length: {len(text)}): {dimension}D {'✅' if test_result['is_correct_dimension'] else '❌'}")
        
        print(f"\nExpected Dimension: {results['expected_dimension']}")
        print(f"All Same Dimension: {'✅ YES' if results['all_same_dimension'] else '❌ NO'}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "all_same_dimension": False}

def run_comprehensive_embedding_validation():
    """Run comprehensive embedding quality validation"""
    print("🚀 Phase 1.1 - Comprehensive Embedding Quality Validation")
    print("=" * 65)
    
    start_time = time.time()
    
    # Run all tests
    accuracy_results = test_embedding_semantic_accuracy()
    consistency_results = test_embedding_consistency()
    dimensionality_results = test_embedding_dimensionality()
    
    # Calculate overall score
    accuracy_score = accuracy_results.get('overall_accuracy', 0) if 'overall_accuracy' in accuracy_results else 0
    consistency_score = 1.0 if consistency_results.get('is_consistent', False) else 0.0
    dimensionality_score = 1.0 if dimensionality_results.get('all_same_dimension', False) else 0.0
    
    overall_score = (accuracy_score * 0.5 + consistency_score * 0.3 + dimensionality_score * 0.2)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n🎯 Phase 1.1 Overall Results")
    print("=" * 40)
    print(f"Accuracy Score: {accuracy_score:.3f}")
    print(f"Consistency Score: {consistency_score:.3f}")
    print(f"Dimensionality Score: {dimensionality_score:.3f}")
    print(f"Overall Score: {overall_score:.3f}")
    print(f"Duration: {duration:.2f}s")
    print(f"Status: {'✅ PASS' if overall_score >= 0.8 else '❌ FAIL'}")
    
    # Save results
    results = {
        "phase": "1.1",
        "test_name": "Embedding Quality Validation",
        "overall_score": overall_score,
        "accuracy_results": accuracy_results,
        "consistency_results": consistency_results,
        "dimensionality_results": dimensionality_results,
        "duration": duration,
        "passed": overall_score >= 0.8
    }
    
    # Convert numpy types to Python types for JSON serialization
    def convert_numpy_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {key: convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        return obj
    
    results_serializable = convert_numpy_types(results)
    
    with open("phase1_embedding_validation_results.json", "w") as f:
        json.dump(results_serializable, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_embedding_validation()
    print(f"\nFinal Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")

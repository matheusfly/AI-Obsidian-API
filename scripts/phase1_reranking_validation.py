#!/usr/bin/env python3
"""
Phase 1.4 - Advanced Cross-Encoder Re-ranking Validation
Tests precision improvement and relevance scoring
"""

import sys
import time
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_reranking_precision_improvement():
    """Test if re-ranking improves precision over raw vector similarity"""
    print("🧪 Phase 1.4 - Re-ranking Precision Improvement Test")
    print("=" * 55)
    
    try:
        from reranker import ReRanker
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Initialize components
        reranker = ReRanker()
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test query
        query = "Machine learning algorithms for data analysis"
        
        # Test documents with known relevance
        test_documents = [
            {
                "id": "doc_1",
                "content": "Machine learning algorithms use statistical methods to analyze data and make predictions. Popular algorithms include linear regression, decision trees, and neural networks.",
                "relevance": "high",
                "expected_rank": 1
            },
            {
                "id": "doc_2",
                "content": "Data analysis involves collecting, processing, and interpreting data to extract meaningful insights. Machine learning is often used as a tool for data analysis.",
                "relevance": "high", 
                "expected_rank": 2
            },
            {
                "id": "doc_3",
                "content": "Python programming language provides excellent libraries for machine learning and data analysis, including scikit-learn, pandas, and numpy.",
                "relevance": "medium",
                "expected_rank": 3
            },
            {
                "id": "doc_4",
                "content": "Web development involves creating websites and web applications using various programming languages and frameworks.",
                "relevance": "low",
                "expected_rank": 4
            },
            {
                "id": "doc_5",
                "content": "Cooking recipes require precise measurements and timing to achieve the desired culinary results.",
                "relevance": "lowest",
                "expected_rank": 5
            }
        ]
        
        # Generate initial vector similarities
        query_embedding = embedding_model.encode([query])
        doc_contents = [doc['content'] for doc in test_documents]
        doc_embeddings = embedding_model.encode(doc_contents)
        similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
        
        # Create initial results with vector similarity
        initial_results = []
        for i, doc in enumerate(test_documents):
            initial_results.append({
                "id": doc['id'],
                "content": doc['content'],
                "similarity": float(similarities[i]),
                "relevance": doc['relevance'],
                "expected_rank": doc['expected_rank']
            })
        
        # Sort by vector similarity
        initial_results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Apply re-ranking
        reranked_results = reranker.rerank(query, initial_results.copy(), top_k=5)
        
        # Calculate precision metrics
        def calculate_precision_at_k(results, k, relevant_threshold="medium"):
            relevant_count = 0
            for i, result in enumerate(results[:k]):
                if result['relevance'] in ["high", "medium"]:
                    relevant_count += 1
            return relevant_count / k
        
        initial_precision_3 = calculate_precision_at_k(initial_results, 3)
        reranked_precision_3 = calculate_precision_at_k(reranked_results, 3)
        
        initial_precision_5 = calculate_precision_at_k(initial_results, 5)
        reranked_precision_5 = calculate_precision_at_k(reranked_results, 5)
        
        # Calculate ranking improvement
        def calculate_ranking_improvement(initial, reranked):
            improvements = 0
            for i, result in enumerate(reranked):
                doc_id = result['id']
                initial_rank = next((j for j, r in enumerate(initial) if r['id'] == doc_id), len(initial))
                if i < initial_rank:  # Moved up in ranking
                    improvements += 1
            return improvements / len(reranked)
        
        ranking_improvement = calculate_ranking_improvement(initial_results, reranked_results)
        
        results = {
            "initial_precision_3": initial_precision_3,
            "reranked_precision_3": reranked_precision_3,
            "precision_improvement_3": reranked_precision_3 - initial_precision_3,
            "initial_precision_5": initial_precision_5,
            "reranked_precision_5": reranked_precision_5,
            "precision_improvement_5": reranked_precision_5 - initial_precision_5,
            "ranking_improvement": ranking_improvement,
            "reranking_effective": reranked_precision_3 > initial_precision_3
        }
        
        print(f"Precision@3 - Initial: {initial_precision_3:.3f}, Re-ranked: {reranked_precision_3:.3f}")
        print(f"Precision@5 - Initial: {initial_precision_5:.3f}, Re-ranked: {reranked_precision_5:.3f}")
        print(f"Precision Improvement@3: {results['precision_improvement_3']:.3f}")
        print(f"Precision Improvement@5: {results['precision_improvement_5']:.3f}")
        print(f"Ranking Improvement: {ranking_improvement:.3f}")
        print(f"Re-ranking Effective: {'✅ YES' if results['reranking_effective'] else '❌ NO'}")
        
        print(f"\nInitial Ranking (by vector similarity):")
        for i, result in enumerate(initial_results):
            print(f"  {i+1}. {result['id']} ({result['relevance']}) - {result['similarity']:.3f}")
        
        print(f"\nRe-ranked Results:")
        for i, result in enumerate(reranked_results):
            print(f"  {i+1}. {result['id']} ({result['relevance']}) - {result.get('final_score', result['similarity']):.3f}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "reranking_effective": False}

def test_reranking_relevance_scoring():
    """Test re-ranking relevance scoring accuracy"""
    print(f"\n🎯 Phase 1.4 - Re-ranking Relevance Scoring Test")
    print("-" * 50)
    
    try:
        from reranker import ReRanker
        
        reranker = ReRanker()
        
        # Test query
        query = "What are the benefits of machine learning in healthcare?"
        
        # Test documents with known relevance scores
        test_documents = [
            {
                "id": "doc_1",
                "content": "Machine learning in healthcare enables early disease detection, personalized treatment plans, and improved patient outcomes through predictive analytics.",
                "expected_relevance": "very_high",
                "expected_score_range": (0.8, 1.0)
            },
            {
                "id": "doc_2", 
                "content": "Healthcare applications of artificial intelligence include medical imaging analysis, drug discovery, and clinical decision support systems.",
                "expected_relevance": "high",
                "expected_score_range": (0.6, 0.8)
            },
            {
                "id": "doc_3",
                "content": "Machine learning algorithms can process large amounts of medical data to identify patterns and trends that humans might miss.",
                "expected_relevance": "high",
                "expected_score_range": (0.6, 0.8)
            },
            {
                "id": "doc_4",
                "content": "General machine learning techniques include supervised learning, unsupervised learning, and reinforcement learning approaches.",
                "expected_relevance": "medium",
                "expected_score_range": (0.3, 0.6)
            },
            {
                "id": "doc_5",
                "content": "Web development frameworks like React and Vue.js help developers build interactive user interfaces for web applications.",
                "expected_relevance": "low",
                "expected_score_range": (0.0, 0.3)
            }
        ]
        
        # Apply re-ranking
        reranked_results = reranker.rerank(query, test_documents.copy(), top_k=5)
        
        results = {
            "total_docs": len(test_documents),
            "correctly_scored": 0,
            "scoring_accuracy": 0.0,
            "score_analysis": []
        }
        
        for result in reranked_results:
            doc_id = result['id']
            original_doc = next(doc for doc in test_documents if doc['id'] == doc_id)
            
            rerank_score = result.get('rerank_score', 0)
            expected_min, expected_max = original_doc['expected_score_range']
            
            is_correctly_scored = expected_min <= rerank_score <= expected_max
            
            if is_correctly_scored:
                results["correctly_scored"] += 1
            
            score_analysis = {
                "doc_id": doc_id,
                "expected_relevance": original_doc['expected_relevance'],
                "expected_range": original_doc['expected_score_range'],
                "actual_score": rerank_score,
                "correctly_scored": is_correctly_scored
            }
            
            results["score_analysis"].append(score_analysis)
            
            print(f"{doc_id}: {rerank_score:.3f} (expected: {expected_min}-{expected_max}) {'✅' if is_correctly_scored else '❌'}")
        
        results["scoring_accuracy"] = results["correctly_scored"] / results["total_docs"]
        
        print(f"\nRelevance Scoring Accuracy: {results['scoring_accuracy']:.2f}")
        print(f"Correctly Scored: {results['correctly_scored']}/{results['total_docs']}")
        print(f"Scoring Quality: {'✅ GOOD' if results['scoring_accuracy'] >= 0.6 else '❌ POOR'}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "scoring_accuracy": 0}

def test_reranking_performance():
    """Test re-ranking performance and scalability"""
    print(f"\n⚡ Phase 1.4 - Re-ranking Performance Test")
    print("-" * 45)
    
    try:
        from reranker import ReRanker
        
        reranker = ReRanker()
        query = "Machine learning and artificial intelligence applications"
        
        # Test with different candidate sizes
        candidate_sizes = [5, 10, 20, 50, 100]
        
        results = {
            "performance_tests": [],
            "scalability_acceptable": True
        }
        
        for size in candidate_sizes:
            # Generate test candidates
            candidates = []
            for i in range(size):
                candidates.append({
                    "id": f"candidate_{i}",
                    "content": f"Document {i} about machine learning, artificial intelligence, and data science applications in various domains including healthcare, finance, and technology."
                })
            
            # Measure re-ranking performance
            start_time = time.time()
            reranked_results = reranker.rerank(query, candidates, top_k=min(5, size))
            end_time = time.time()
            
            processing_time = end_time - start_time
            candidates_per_second = size / processing_time if processing_time > 0 else 0
            
            performance_test = {
                "candidate_count": size,
                "processing_time": processing_time,
                "candidates_per_second": candidates_per_second,
                "performance_acceptable": candidates_per_second > 10  # At least 10 candidates/second
            }
            
            results["performance_tests"].append(performance_test)
            
            if not performance_test["performance_acceptable"]:
                results["scalability_acceptable"] = False
            
            print(f"Size {size}: {processing_time:.3f}s ({candidates_per_second:.0f} candidates/s) {'✅' if performance_test['performance_acceptable'] else '❌'}")
        
        print(f"\nRe-ranking Performance Summary:")
        print(f"Scalability: {'✅ ACCEPTABLE' if results['scalability_acceptable'] else '❌ POOR'}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "scalability_acceptable": False}

def test_reranking_weight_configuration():
    """Test different re-ranking weight configurations"""
    print(f"\n⚖️ Phase 1.4 - Re-ranking Weight Configuration Test")
    print("-" * 50)
    
    try:
        from reranker import ReRanker
        
        query = "Machine learning algorithms for data analysis"
        
        # Test documents
        test_documents = [
            {
                "id": "doc_1",
                "content": "Machine learning algorithms use statistical methods to analyze data and make predictions about future outcomes.",
                "relevance": "high"
            },
            {
                "id": "doc_2",
                "content": "Data analysis involves collecting, processing, and interpreting data to extract meaningful insights and patterns.",
                "relevance": "high"
            },
            {
                "id": "doc_3",
                "content": "Web development frameworks help developers build interactive user interfaces for web applications.",
                "relevance": "low"
            }
        ]
        
        # Test different weight configurations
        weight_configs = [
            {"similarity_weight": 0.3, "cross_score_weight": 0.7, "name": "Cross-encoder Heavy"},
            {"similarity_weight": 0.5, "cross_score_weight": 0.5, "name": "Balanced"},
            {"similarity_weight": 0.7, "cross_score_weight": 0.3, "name": "Similarity Heavy"}
        ]
        
        results = {
            "weight_tests": [],
            "best_configuration": None,
            "best_score": 0
        }
        
        for config in weight_configs:
            # Create reranker with custom weights
            reranker = ReRanker()
            
            # Apply re-ranking with custom weights
            reranked_results = reranker.search_with_rerank(
                query, 
                test_documents.copy(), 
                n_results=3,
                similarity_weight=config["similarity_weight"],
                cross_score_weight=config["cross_score_weight"]
            )
            
            # Calculate quality score (higher relevance docs should rank higher)
            quality_score = 0
            for i, result in enumerate(reranked_results):
                doc_id = result['id']
                original_doc = next(doc for doc in test_documents if doc['id'] == doc_id)
                relevance_score = 1.0 if original_doc['relevance'] == 'high' else 0.0
                position_weight = 1.0 / (i + 1)  # Higher weight for better positions
                quality_score += relevance_score * position_weight
            
            weight_test = {
                "configuration": config["name"],
                "similarity_weight": config["similarity_weight"],
                "cross_score_weight": config["cross_score_weight"],
                "quality_score": quality_score,
                "top_result": reranked_results[0]['id'] if reranked_results else None
            }
            
            results["weight_tests"].append(weight_test)
            
            if quality_score > results["best_score"]:
                results["best_score"] = quality_score
                results["best_configuration"] = config["name"]
            
            print(f"{config['name']}: Quality Score {quality_score:.3f}, Top: {weight_test['top_result']}")
        
        print(f"\nBest Configuration: {results['best_configuration']} (Score: {results['best_score']:.3f})")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "best_score": 0}

def run_comprehensive_reranking_validation():
    """Run comprehensive re-ranking validation"""
    print("🚀 Phase 1.4 - Comprehensive Cross-Encoder Re-ranking Validation")
    print("=" * 70)
    
    start_time = time.time()
    
    # Run all tests
    precision_results = test_reranking_precision_improvement()
    relevance_results = test_reranking_relevance_scoring()
    performance_results = test_reranking_performance()
    weight_results = test_reranking_weight_configuration()
    
    # Calculate overall score
    precision_score = 1.0 if precision_results.get('reranking_effective', False) else 0.0
    relevance_score = relevance_results.get('scoring_accuracy', 0)
    performance_score = 1.0 if performance_results.get('scalability_acceptable', False) else 0.0
    weight_score = min(1.0, weight_results.get('best_score', 0) * 2)  # Scale to 0-1
    
    overall_score = (precision_score * 0.4 + relevance_score * 0.3 + performance_score * 0.2 + weight_score * 0.1)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n🎯 Phase 1.4 Overall Results")
    print("=" * 40)
    print(f"Precision Score: {precision_score:.3f}")
    print(f"Relevance Score: {relevance_score:.3f}")
    print(f"Performance Score: {performance_score:.3f}")
    print(f"Weight Score: {weight_score:.3f}")
    print(f"Overall Score: {overall_score:.3f}")
    print(f"Duration: {duration:.2f}s")
    print(f"Status: {'✅ PASS' if overall_score >= 0.7 else '❌ FAIL'}")
    
    # Save results
    results = {
        "phase": "1.4",
        "test_name": "Cross-Encoder Re-ranking Validation",
        "overall_score": overall_score,
        "precision_results": precision_results,
        "relevance_results": relevance_results,
        "performance_results": performance_results,
        "weight_results": weight_results,
        "duration": duration,
        "passed": overall_score >= 0.7
    }
    
    with open("phase1_reranking_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_reranking_validation()
    print(f"\nFinal Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")

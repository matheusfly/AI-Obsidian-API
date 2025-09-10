#!/usr/bin/env python3
"""
Test Enhanced Re-Ranking with Cross-Encoder
Tests the new search_with_rerank method and weight configurations
"""

import asyncio
import sys
from pathlib import Path
import time

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from reranker import ReRanker

def test_enhanced_reranking():
    """Test the enhanced re-ranking functionality"""
    print("🔄 Enhanced Re-Ranking Test")
    print("=" * 50)
    
    # Initialize reranker
    reranker = ReRanker()
    
    # Test query
    query = "machine learning algorithms for data analysis"
    
    # Sample candidates with different relevance levels
    candidates = [
        {
            "content": "Machine learning algorithms are powerful tools for analyzing large datasets and extracting meaningful patterns from data. They can identify trends, make predictions, and automate decision-making processes.",
            "similarity": 0.8,
            "heading": "ML Algorithms Overview",
            "file_path": "ml_basics.md"
        },
        {
            "content": "Data analysis techniques include statistical methods, visualization, and machine learning approaches. These methods help researchers understand complex datasets and draw meaningful conclusions.",
            "similarity": 0.7,
            "heading": "Data Analysis Methods",
            "file_path": "data_analysis.md"
        },
        {
            "content": "Neural networks are a subset of machine learning algorithms inspired by biological neural networks. They excel at pattern recognition and can learn complex relationships in data.",
            "similarity": 0.6,
            "heading": "Neural Networks",
            "file_path": "neural_networks.md"
        },
        {
            "content": "Philosophical logic deals with the nature of reasoning and argumentation in philosophical contexts. It explores the principles of valid inference and logical structure.",
            "similarity": 0.5,
            "heading": "Philosophical Logic",
            "file_path": "philosophy.md"
        },
        {
            "content": "Performance optimization techniques can improve system efficiency and reduce response times. This includes algorithmic improvements, caching strategies, and resource management.",
            "similarity": 0.4,
            "heading": "Performance Tips",
            "file_path": "performance.md"
        },
        {
            "content": "Business strategy involves long-term planning and decision-making to achieve organizational goals. It includes market analysis, competitive positioning, and resource allocation.",
            "similarity": 0.3,
            "heading": "Business Strategy",
            "file_path": "business.md"
        }
    ]
    
    print(f"Query: '{query}'")
    print(f"Total candidates: {len(candidates)}")
    print()
    
    # Test 1: Basic search_with_rerank
    print("🧪 Test 1: Basic search_with_rerank")
    print("-" * 40)
    
    start_time = time.time()
    reranked_basic = reranker.search_with_rerank(
        query=query,
        candidates=candidates.copy(),
        n_results=3,
        rerank_top_k=6
    )
    basic_time = time.time() - start_time
    
    print(f"Results (n=3, top_k=6):")
    for i, result in enumerate(reranked_basic, 1):
        print(f"  {i}. Final Score: {result['final_score']:.3f} | "
              f"Original: {result['similarity']:.3f} | "
              f"Cross: {result['cross_score']:.3f}")
        print(f"     Heading: {result['heading']}")
        print(f"     Content: {result['content'][:80]}...")
        print()
    
    print(f"Processing time: {basic_time:.3f}s")
    print()
    
    # Test 2: Different weight configurations
    print("🧪 Test 2: Weight Configuration Comparison")
    print("-" * 45)
    
    weight_configs = [
        {"similarity_weight": 0.3, "cross_score_weight": 0.7, "name": "Cross-Encoder Heavy"},
        {"similarity_weight": 0.5, "cross_score_weight": 0.5, "name": "Balanced"},
        {"similarity_weight": 0.7, "cross_score_weight": 0.3, "name": "Similarity Heavy"},
        {"similarity_weight": 0.0, "cross_score_weight": 1.0, "name": "Cross-Encoder Only"}
    ]
    
    for config in weight_configs:
        print(f"\n{config['name']} (sim={config['similarity_weight']}, cross={config['cross_score_weight']}):")
        
        reranked = reranker.search_with_rerank(
            query=query,
            candidates=candidates.copy(),
            n_results=3,
            similarity_weight=config['similarity_weight'],
            cross_score_weight=config['cross_score_weight']
        )
        
        for i, result in enumerate(reranked, 1):
            print(f"  {i}. Final: {result['final_score']:.3f} | "
                  f"Sim: {result['similarity']:.3f} | "
                  f"Cross: {result['cross_score']:.3f} | "
                  f"{result['heading']}")
    
    # Test 3: Re-ranking analysis
    print(f"\n🧪 Test 3: Re-ranking Analysis")
    print("-" * 35)
    
    analysis = reranker.get_rerank_analysis(query, candidates)
    
    print(f"Query: {analysis['query']}")
    print(f"Candidate Count: {analysis['candidate_count']}")
    print(f"Average Improvement: {analysis['avg_improvement']:.3f}")
    print(f"Max Improvement: {analysis['max_improvement']:.3f}")
    print(f"Min Improvement: {analysis['min_improvement']:.3f}")
    
    print(f"\nScore Improvements:")
    for i, improvement in enumerate(analysis['score_improvements']):
        print(f"  Candidate {i+1}: {improvement:+.3f}")
    
    # Test 4: Performance with different candidate sizes
    print(f"\n🧪 Test 4: Performance Scaling")
    print("-" * 35)
    
    candidate_sizes = [5, 10, 15, 20]
    
    for size in candidate_sizes:
        test_candidates = candidates[:size] if size <= len(candidates) else candidates * (size // len(candidates) + 1)
        test_candidates = test_candidates[:size]
        
        start_time = time.time()
        reranked = reranker.search_with_rerank(
            query=query,
            candidates=test_candidates,
            n_results=3,
            rerank_top_k=size
        )
        processing_time = time.time() - start_time
        
        print(f"  {size:2d} candidates: {processing_time:.3f}s")
    
    # Test 5: Error handling
    print(f"\n🧪 Test 5: Error Handling")
    print("-" * 30)
    
    # Empty candidates
    empty_result = reranker.search_with_rerank(query, [], n_results=3)
    print(f"Empty candidates: {'✅' if len(empty_result) == 0 else '❌'}")
    
    # Single candidate
    single_result = reranker.search_with_rerank(query, [candidates[0]], n_results=3)
    print(f"Single candidate: {'✅' if len(single_result) == 1 else '❌'}")
    
    # More candidates than requested
    many_result = reranker.search_with_rerank(query, candidates, n_results=2, rerank_top_k=10)
    print(f"More candidates than requested: {'✅' if len(many_result) == 2 else '❌'}")
    
    # Test 6: Quality comparison
    print(f"\n🧪 Test 6: Quality Comparison")
    print("-" * 35)
    
    # Original similarity ranking
    original_ranking = sorted(candidates, key=lambda x: x['similarity'], reverse=True)[:3]
    
    # Re-ranked results
    reranked_quality = reranker.search_with_rerank(query, candidates, n_results=3)
    
    print("Original vs Re-ranked:")
    print("Rank | Original (Sim) | Re-ranked (Final) | Change")
    print("-" * 55)
    
    for i in range(3):
        orig_score = original_ranking[i]['similarity']
        rerank_score = reranked_quality[i]['final_score']
        change = "↑" if rerank_score > orig_score else "↓" if rerank_score < orig_score else "="
        
        print(f"  {i+1}  |     {orig_score:.3f}     |      {rerank_score:.3f}      |   {change}")
    
    # Final summary
    print(f"\n🎯 Test Summary")
    print("=" * 30)
    
    # Calculate quality metrics
    original_top_score = max(c['similarity'] for c in candidates)
    reranked_top_score = max(c['final_score'] for c in reranked_quality)
    improvement = reranked_top_score - original_top_score
    
    print(f"Top Score Improvement: {improvement:+.3f}")
    print(f"Average Processing Time: {basic_time:.3f}s")
    print(f"Re-ranking Effectiveness: {'✅ GOOD' if improvement > 0 else '❌ POOR'}")
    
    return improvement > 0

if __name__ == "__main__":
    success = test_enhanced_reranking()
    print(f"\nOverall Test Result: {'✅ PASS' if success else '❌ FAIL'}")

#!/usr/bin/env python3
"""
Re-Ranking Service for Enhanced RAG System
"""

from typing import List, Dict, Optional
from sentence_transformers import CrossEncoder
import numpy as np
import logging

class ReRanker:
    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2', max_length: int = 512):
        self.model = CrossEncoder(model_name, max_length=max_length)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Cross-encoder re-ranker initialized with {model_name}")
    
    def rerank(self, query: str, candidates: List[Dict], top_k: int = 5) -> List[Dict]:
        """Re-rank candidates using cross-encoder"""
        if not candidates:
            return candidates
        
        # Prepare query-document pairs
        pairs = [(query, candidate['content']) for candidate in candidates]
        
        # Get re-ranking scores
        rerank_scores = self.model.predict(pairs)
        
        # Update candidates with re-ranking scores
        for i, candidate in enumerate(candidates):
            candidate['rerank_score'] = float(rerank_scores[i])
            
            # Calculate final score combining original similarity and rerank score
            original_score = candidate.get('similarity', candidate.get('final_score', 0))
            candidate['final_score'] = (original_score * 0.6 + candidate['rerank_score'] * 0.4)
        
        # Sort by final score
        candidates.sort(key=lambda x: x['final_score'], reverse=True)
        
        return candidates[:top_k]
    
    def search_with_rerank(self, query: str, candidates: List[Dict], 
                          n_results: int = 5, rerank_top_k: int = 20,
                          similarity_weight: float = 0.3,
                          cross_score_weight: float = 0.7) -> List[Dict]:
        """
        Search with re-ranking for higher quality results
        Implements the exact method from the user's specification
        """
        if not candidates:
            return candidates
        
        # 1. Get more candidates if needed (already provided in candidates)
        if len(candidates) <= n_results:
            return candidates
        
        # 2. Create query-document pairs for cross-encoder
        pairs = [(query, result['content']) for result in candidates]
        
        try:
            # 3. Get cross-encoder relevance scores
            cross_scores = self.model.predict(pairs)
            
            # 4. Combine scores (70% cross-encoder, 30% vector similarity)
            for i, result in enumerate(candidates):
                result['cross_score'] = float(cross_scores[i])
                original_similarity = result.get('similarity', result.get('final_score', 0))
                result['final_score'] = (cross_score_weight * result['cross_score'] + 
                                       similarity_weight * original_similarity)
            
            # 5. Sort by final score and return top results
            candidates.sort(key=lambda x: x['final_score'], reverse=True)
            return candidates[:n_results]
            
        except Exception as e:
            self.logger.error(f"Cross-encoder re-ranking failed: {e}")
            # Fallback to original similarity sorting
            candidates.sort(key=lambda x: x.get('similarity', x.get('final_score', 0)), reverse=True)
            return candidates[:n_results]

    def rerank_with_weights(self, query: str, candidates: List[Dict], 
                          similarity_weight: float = 0.6, 
                          rerank_weight: float = 0.4,
                          top_k: int = 5) -> List[Dict]:
        """Re-rank with custom weights for similarity and rerank scores"""
        if not candidates:
            return candidates
        
        # Prepare query-document pairs
        pairs = [(query, candidate['content']) for candidate in candidates]
        
        # Get re-ranking scores
        rerank_scores = self.model.predict(pairs)
        
        # Update candidates with re-ranking scores
        for i, candidate in enumerate(candidates):
            candidate['rerank_score'] = float(rerank_scores[i])
            
            # Calculate final score with custom weights
            original_score = candidate.get('similarity', candidate.get('final_score', 0))
            candidate['final_score'] = (original_score * similarity_weight + 
                                      candidate['rerank_score'] * rerank_weight)
        
        # Sort by final score
        candidates.sort(key=lambda x: x['final_score'], reverse=True)
        
        return candidates[:top_k]
    
    def batch_rerank(self, queries: List[str], candidates_list: List[List[Dict]], 
                    top_k: int = 5) -> List[List[Dict]]:
        """Re-rank multiple queries in batch"""
        results = []
        
        for query, candidates in zip(queries, candidates_list):
            reranked = self.rerank(query, candidates, top_k)
            results.append(reranked)
        
        return results
    
    def get_rerank_analysis(self, query: str, candidates: List[Dict]) -> Dict[str, any]:
        """Get analysis of re-ranking results"""
        if not candidates:
            return {"error": "No candidates provided"}
        
        # Get original scores
        original_scores = [c.get('similarity', c.get('final_score', 0)) for c in candidates]
        
        # Re-rank
        reranked = self.rerank(query, candidates.copy())
        
        # Get rerank scores
        rerank_scores = [c['rerank_score'] for c in reranked]
        final_scores = [c['final_score'] for c in reranked]
        
        # Calculate improvements
        score_improvements = []
        for i, (orig, final) in enumerate(zip(original_scores, final_scores)):
            improvement = final - orig
            score_improvements.append(improvement)
        
        return {
            "query": query,
            "candidate_count": len(candidates),
            "original_scores": original_scores,
            "rerank_scores": rerank_scores,
            "final_scores": final_scores,
            "score_improvements": score_improvements,
            "avg_improvement": np.mean(score_improvements),
            "max_improvement": max(score_improvements) if score_improvements else 0,
            "min_improvement": min(score_improvements) if score_improvements else 0
        }

# Test the reranker
if __name__ == "__main__":
    reranker = ReRanker()
    
    # Sample query and candidates
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
    
    print("🔄 Re-Ranker Test")
    print("=" * 50)
    
    # Test basic reranking
    reranked = reranker.rerank(query, candidates, top_k=3)
    
    print(f"Query: '{query}'")
    print(f"\nRe-ranked results:")
    for i, result in enumerate(reranked, 1):
        print(f"  {i}. Final Score: {result['final_score']:.3f} | "
              f"Original: {result['similarity']:.3f} | "
              f"Rerank: {result['rerank_score']:.3f}")
        print(f"     Heading: {result['heading']}")
        print(f"     Content: {result['content'][:80]}...")
        print()
    
    # Test rerank analysis
    analysis = reranker.get_rerank_analysis(query, candidates)
    print(f"Re-rank Analysis:")
    print(f"  Average Improvement: {analysis['avg_improvement']:.3f}")
    print(f"  Max Improvement: {analysis['max_improvement']:.3f}")
    print(f"  Min Improvement: {analysis['min_improvement']:.3f}")

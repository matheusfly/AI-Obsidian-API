#!/usr/bin/env python3
"""
Validation Testing: Quality Scoring
Step 3: Implement Quality Scoring - Add quality metrics to track retrieval performance
"""

import sys
import numpy as np
from pathlib import Path
import logging
from typing import List, Dict, Any, Tuple
import math

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

class QualityScoringMetrics:
    """Quality scoring metrics for retrieval performance evaluation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
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
        overall_quality = (0.3 * precision_at_k + 
                          0.2 * recall + 
                          0.25 * mrr + 
                          0.25 * ndcg)
        
        return {
            "precision_at_k": precision_at_k,
            "recall": recall,
            "mrr": mrr,
            "ndcg": ndcg,
            "overall_quality": overall_quality
        }
    
    def _calculate_precision_at_k(self, results: List[Dict], relevant_files: List[str]) -> float:
        """Calculate Precision at K (how many top results are relevant)"""
        if not results:
            return 0.0
        
        relevant_count = sum(1 for r in results if any(rel in r.get("path", "") for rel in relevant_files))
        return relevant_count / len(results)
    
    def _calculate_recall(self, results: List[Dict], relevant_files: List[str]) -> float:
        """Calculate Recall (how many relevant files were found)"""
        if not relevant_files:
            return 1.0
        
        found_relevant = set()
        for r in results:
            for rel in relevant_files:
                if rel in r.get("path", ""):
                    found_relevant.add(rel)
        
        return len(found_relevant) / len(relevant_files)
    
    def _calculate_mrr(self, results: List[Dict], relevant_files: List[str]) -> float:
        """Calculate Mean Reciprocal Rank (how high relevant results appear)"""
        for i, r in enumerate(results, 1):
            if any(rel in r.get("path", "") for rel in relevant_files):
                return 1.0 / i
        
        return 0.0
    
    def _calculate_ndcg(self, results: List[Dict], relevant_files: List[str]) -> float:
        """Calculate Normalized Discounted Cumulative Gain"""
        if not results:
            return 0.0
        
        # Calculate DCG (Discounted Cumulative Gain)
        dcg = 0.0
        for i, r in enumerate(results, 1):
            relevance = 1 if any(rel in r.get("path", "") for rel in relevant_files) else 0
            dcg += relevance / math.log2(i + 1)
        
        # Calculate IDCG (Ideal DCG)
        idcg = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(relevant_files), len(results)) + 1))
        
        # Calculate NDCG
        if idcg > 0:
            return dcg / idcg
        else:
            return 0.0
    
    def calculate_similarity_quality(self, results: List[Dict]) -> Dict[str, float]:
        """Calculate quality metrics based on similarity scores"""
        if not results:
            return {
                "avg_similarity": 0.0,
                "similarity_std": 0.0,
                "similarity_range": 0.0,
                "high_similarity_ratio": 0.0
            }
        
        similarities = [r.get("similarity", 0.0) for r in results]
        
        avg_similarity = np.mean(similarities)
        similarity_std = np.std(similarities)
        similarity_range = np.max(similarities) - np.min(similarities)
        high_similarity_ratio = sum(1 for s in similarities if s > 0.7) / len(similarities)
        
        return {
            "avg_similarity": avg_similarity,
            "similarity_std": similarity_std,
            "similarity_range": similarity_range,
            "high_similarity_ratio": high_similarity_ratio
        }
    
    def calculate_diversity_metrics(self, results: List[Dict]) -> Dict[str, float]:
        """Calculate diversity metrics for retrieved results"""
        if not results:
            return {
                "topic_diversity": 0.0,
                "file_type_diversity": 0.0,
                "content_length_diversity": 0.0,
                "overall_diversity": 0.0
            }
        
        # Topic diversity (based on topics in results)
        topics = set()
        for r in results:
            result_topics = r.get("topics", [])
            if isinstance(result_topics, list):
                topics.update(result_topics)
            elif isinstance(result_topics, str):
                topics.add(result_topics)
        
        topic_diversity = len(topics) / len(results) if results else 0.0
        
        # File type diversity
        file_types = set()
        for r in results:
            path = r.get("path", "")
            if "." in path:
                file_type = path.split(".")[-1]
                file_types.add(file_type)
        
        file_type_diversity = len(file_types) / len(results) if results else 0.0
        
        # Content length diversity
        lengths = [r.get("file_size", 0) for r in results]
        if lengths:
            length_std = np.std(lengths)
            length_mean = np.mean(lengths)
            content_length_diversity = length_std / length_mean if length_mean > 0 else 0.0
        else:
            content_length_diversity = 0.0
        
        # Overall diversity (weighted average)
        overall_diversity = (0.4 * topic_diversity + 
                           0.3 * file_type_diversity + 
                           0.3 * content_length_diversity)
        
        return {
            "topic_diversity": topic_diversity,
            "file_type_diversity": file_type_diversity,
            "content_length_diversity": content_length_diversity,
            "overall_diversity": overall_diversity
        }
    
    def calculate_response_quality(self, query: str, response: str, retrieved_docs: List[Dict]) -> Dict[str, float]:
        """Calculate quality metrics for generated responses"""
        if not response:
            return {
                "response_length_score": 0.0,
                "query_coverage": 0.0,
                "source_utilization": 0.0,
                "coherence_score": 0.0,
                "overall_response_quality": 0.0
            }
        
        # Response length score (optimal range: 50-500 words)
        word_count = len(response.split())
        if word_count < 50:
            response_length_score = word_count / 50
        elif word_count <= 500:
            response_length_score = 1.0
        else:
            response_length_score = max(0.0, 1.0 - (word_count - 500) / 500)
        
        # Query coverage (how well response addresses the query)
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        query_coverage = len(query_words.intersection(response_words)) / len(query_words) if query_words else 0.0
        
        # Source utilization (how well response uses retrieved documents)
        if retrieved_docs:
            source_utilization = 1.0  # Simplified - in practice, would analyze how well sources are used
        else:
            source_utilization = 0.0
        
        # Coherence score (simplified - based on sentence structure)
        sentences = response.split('.')
        if len(sentences) > 1:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            coherence_score = min(1.0, avg_sentence_length / 20)  # Optimal: 15-20 words per sentence
        else:
            coherence_score = 0.5
        
        # Overall response quality
        overall_response_quality = (0.2 * response_length_score + 
                                  0.3 * query_coverage + 
                                  0.2 * source_utilization + 
                                  0.3 * coherence_score)
        
        return {
            "response_length_score": response_length_score,
            "query_coverage": query_coverage,
            "source_utilization": source_utilization,
            "coherence_score": coherence_score,
            "overall_response_quality": overall_response_quality
        }
    
    def calculate_system_quality(self, test_results: List[Dict]) -> Dict[str, float]:
        """Calculate overall system quality metrics from test results"""
        if not test_results:
            return {
                "avg_precision": 0.0,
                "avg_recall": 0.0,
                "avg_mrr": 0.0,
                "avg_ndcg": 0.0,
                "system_quality_score": 0.0
            }
        
        # Extract metrics from test results
        precisions = [r.get("precision_at_k", 0.0) for r in test_results]
        recalls = [r.get("recall", 0.0) for r in test_results]
        mrrs = [r.get("mrr", 0.0) for r in test_results]
        ndcgs = [r.get("ndcg", 0.0) for r in test_results]
        
        # Calculate averages
        avg_precision = np.mean(precisions)
        avg_recall = np.mean(recalls)
        avg_mrr = np.mean(mrrs)
        avg_ndcg = np.mean(ndcgs)
        
        # Calculate system quality score
        system_quality_score = (0.3 * avg_precision + 
                               0.2 * avg_recall + 
                               0.25 * avg_mrr + 
                               0.25 * avg_ndcg)
        
        return {
            "avg_precision": avg_precision,
            "avg_recall": avg_recall,
            "avg_mrr": avg_mrr,
            "avg_ndcg": avg_ndcg,
            "system_quality_score": system_quality_score
        }
    
    def generate_quality_report(self, test_results: List[Dict]) -> str:
        """Generate a comprehensive quality report"""
        if not test_results:
            return "No test results available for quality report generation."
        
        # Calculate system quality
        system_quality = self.calculate_system_quality(test_results)
        
        # Generate report
        report = f"""
# RAG System Quality Report

## Overall System Quality
- **System Quality Score**: {system_quality['system_quality_score']:.3f}
- **Average Precision@K**: {system_quality['avg_precision']:.3f}
- **Average Recall**: {system_quality['avg_recall']:.3f}
- **Average MRR**: {system_quality['avg_mrr']:.3f}
- **Average NDCG**: {system_quality['avg_ndcg']:.3f}

## Quality Classification
"""
        
        quality_score = system_quality['system_quality_score']
        if quality_score >= 0.9:
            classification = "Excellent"
        elif quality_score >= 0.8:
            classification = "Good"
        elif quality_score >= 0.6:
            classification = "Fair"
        else:
            classification = "Poor"
        
        report += f"- **Quality Level**: {classification}\n"
        report += f"- **Status**: {'✅ PASS' if quality_score >= 0.8 else '❌ FAIL'}\n\n"
        
        # Individual test results
        report += "## Individual Test Results\n\n"
        for i, result in enumerate(test_results, 1):
            report += f"### Test {i}\n"
            report += f"- **Query**: {result.get('query', 'N/A')}\n"
            report += f"- **Precision@K**: {result.get('precision_at_k', 0.0):.3f}\n"
            report += f"- **Recall**: {result.get('recall', 0.0):.3f}\n"
            report += f"- **MRR**: {result.get('mrr', 0.0):.3f}\n"
            report += f"- **NDCG**: {result.get('ndcg', 0.0):.3f}\n"
            report += f"- **Overall Quality**: {result.get('overall_quality', 0.0):.3f}\n"
            report += f"- **Status**: {'✅ PASS' if result.get('overall_quality', 0.0) >= 0.6 else '❌ FAIL'}\n\n"
        
        # Recommendations
        report += "## Recommendations\n\n"
        if system_quality['avg_precision'] < 0.6:
            report += "- Improve precision by better query understanding and document ranking\n"
        if system_quality['avg_recall'] < 0.6:
            report += "- Improve recall by expanding search scope and improving document coverage\n"
        if system_quality['avg_mrr'] < 0.6:
            report += "- Improve ranking by better similarity calculation and re-ranking\n"
        if system_quality['avg_ndcg'] < 0.6:
            report += "- Improve relevance scoring and document quality assessment\n"
        
        if quality_score >= 0.8:
            report += "- System quality is good. Consider fine-tuning for specific use cases.\n"
        
        return report

# Test the quality scoring metrics
if __name__ == "__main__":
    # Create test data
    test_results = [
        {
            "query": "machine learning algorithms",
            "results": [
                {"path": "ml_algorithms.md", "similarity": 0.85, "topics": ["machine_learning", "algorithms"]},
                {"path": "data_science.md", "similarity": 0.72, "topics": ["data_science", "analytics"]},
                {"path": "python_guide.md", "similarity": 0.65, "topics": ["programming", "python"]}
            ],
            "relevant_files": ["ml_algorithms.md", "data_science.md"]
        },
        {
            "query": "web scraping techniques",
            "results": [
                {"path": "scraping_guide.md", "similarity": 0.90, "topics": ["web_scraping", "techniques"]},
                {"path": "python_guide.md", "similarity": 0.55, "topics": ["programming", "python"]},
                {"path": "business_strategy.md", "similarity": 0.30, "topics": ["business", "strategy"]}
            ],
            "relevant_files": ["scraping_guide.md"]
        }
    ]
    
    # Calculate quality metrics
    scorer = QualityScoringMetrics()
    
    print("🧪 Quality Scoring Metrics Test")
    print("=" * 40)
    
    for i, test in enumerate(test_results, 1):
        print(f"\nTest {i}: {test['query']}")
        
        quality_metrics = scorer.calculate_retrieval_quality(
            test["query"], 
            test["results"], 
            test["relevant_files"]
        )
        
        print(f"  Precision@K: {quality_metrics['precision_at_k']:.3f}")
        print(f"  Recall: {quality_metrics['recall']:.3f}")
        print(f"  MRR: {quality_metrics['mrr']:.3f}")
        print(f"  NDCG: {quality_metrics['ndcg']:.3f}")
        print(f"  Overall Quality: {quality_metrics['overall_quality']:.3f}")
    
    # Generate quality report
    print(f"\n📊 Quality Report")
    print("=" * 30)
    report = scorer.generate_quality_report(test_results)
    print(report)

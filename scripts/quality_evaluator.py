#!/usr/bin/env python3
"""
Quality Evaluation System for RAG Responses
Phase 4: Quality Improvement with Evaluation Metrics and User Feedback
"""

import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import re
from collections import defaultdict, Counter
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class QualityEvaluator:
    """Comprehensive quality evaluation system for RAG responses"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.logger = logging.getLogger(__name__)
        
        # Quality metrics storage
        self.quality_history = []
        self.user_feedback = []
        self.quality_analytics = {
            'total_evaluations': 0,
            'avg_quality_score': 0.0,
            'feedback_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'common_issues': Counter(),
            'improvement_trends': []
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 0.8,
            'good': 0.6,
            'fair': 0.4,
            'poor': 0.0
        }
        
        self.logger.info("Quality Evaluator initialized")
    
    def evaluate_response(self, query: str, response: str, retrieved_docs: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive response quality evaluation
        
        Args:
            query: User query
            response: Generated response
            retrieved_docs: Retrieved documents used for response
            
        Returns:
            Dict with quality metrics and analysis
        """
        evaluation_start = time.time()
        
        # Basic metrics
        basic_metrics = self._evaluate_basic_metrics(query, response, retrieved_docs)
        
        # Semantic metrics
        semantic_metrics = self._evaluate_semantic_quality(query, response, retrieved_docs)
        
        # Relevance metrics
        relevance_metrics = self._evaluate_relevance(query, response, retrieved_docs)
        
        # Completeness metrics
        completeness_metrics = self._evaluate_completeness(query, response, retrieved_docs)
        
        # Coherence metrics
        coherence_metrics = self._evaluate_coherence(response)
        
        # Calculate overall quality score
        overall_score = self._calculate_overall_score({
            'basic': basic_metrics,
            'semantic': semantic_metrics,
            'relevance': relevance_metrics,
            'completeness': completeness_metrics,
            'coherence': coherence_metrics
        })
        
        # Quality level classification
        quality_level = self._classify_quality_level(overall_score)
        
        # Create evaluation result
        evaluation = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'retrieved_docs_count': len(retrieved_docs),
            'overall_score': overall_score,
            'quality_level': quality_level,
            'metrics': {
                'basic': basic_metrics,
                'semantic': semantic_metrics,
                'relevance': relevance_metrics,
                'completeness': completeness_metrics,
                'coherence': coherence_metrics
            },
            'evaluation_time': time.time() - evaluation_start,
            'recommendations': self._generate_improvement_recommendations(overall_score, {
                'basic': basic_metrics,
                'semantic': semantic_metrics,
                'relevance': relevance_metrics,
                'completeness': completeness_metrics,
                'coherence': coherence_metrics
            })
        }
        
        # Store evaluation
        self.quality_history.append(evaluation)
        self._update_analytics(evaluation)
        
        return evaluation
    
    def _evaluate_basic_metrics(self, query: str, response: str, retrieved_docs: List[Dict]) -> Dict[str, float]:
        """Evaluate basic response metrics"""
        query_keywords = set(query.lower().split())
        response_keywords = set(response.lower().split())
        
        # Keyword overlap (as specified in user requirements)
        keyword_overlap = len(query_keywords & response_keywords)
        keyword_coverage = keyword_overlap / len(query_keywords) if query_keywords else 0.0
        
        # Response length metrics
        response_length = len(response.split())
        optimal_length = 50  # Target response length
        length_score = 1.0 - abs(response_length - optimal_length) / optimal_length
        length_score = max(0.0, min(1.0, length_score))
        
        # Response completeness
        completeness_score = min(1.0, response_length / 20)  # At least 20 words
        
        return {
            'keyword_coverage': keyword_coverage,
            'length_score': length_score,
            'completeness_score': completeness_score,
            'response_length': response_length
        }
    
    def _evaluate_semantic_quality(self, query: str, response: str, retrieved_docs: List[Dict]) -> Dict[str, float]:
        """Evaluate semantic quality using embeddings"""
        try:
            # Encode query and response
            query_embedding = self.model.encode([query])
            response_embedding = self.model.encode([response])
            
            # Calculate semantic similarity
            semantic_similarity = cosine_similarity(query_embedding, response_embedding)[0][0]
            
            # Evaluate against retrieved documents
            doc_similarities = []
            for doc in retrieved_docs:
                doc_embedding = self.model.encode([doc['content']])
                doc_sim = cosine_similarity(query_embedding, doc_embedding)[0][0]
                doc_similarities.append(doc_sim)
            
            # Response should be similar to relevant documents
            avg_doc_similarity = np.mean(doc_similarities) if doc_similarities else 0.0
            doc_alignment = cosine_similarity(response_embedding, query_embedding)[0][0]
            
            return {
                'semantic_similarity': float(semantic_similarity),
                'doc_alignment': float(doc_alignment),
                'avg_doc_similarity': float(avg_doc_similarity),
                'semantic_consistency': float(min(semantic_similarity, doc_alignment))
            }
            
        except Exception as e:
            self.logger.error(f"Semantic evaluation failed: {e}")
            return {
                'semantic_similarity': 0.0,
                'doc_alignment': 0.0,
                'avg_doc_similarity': 0.0,
                'semantic_consistency': 0.0
            }
    
    def _evaluate_relevance(self, query: str, response: str, retrieved_docs: List[Dict]) -> Dict[str, float]:
        """Evaluate response relevance to query"""
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Direct query addressing
        query_mentions = sum(1 for word in query_lower.split() if word in response_lower)
        query_coverage = query_mentions / len(query_lower.split()) if query_lower.split() else 0.0
        
        # Question answering patterns
        question_patterns = [
            r'\?',  # Contains question marks
            r'what|how|why|when|where|who',  # Question words
            r'explain|describe|define',  # Explanation requests
        ]
        
        question_addressing = 0.0
        for pattern in question_patterns:
            if re.search(pattern, query_lower):
                if re.search(pattern, response_lower):
                    question_addressing += 1.0
        
        question_addressing = min(1.0, question_addressing / len(question_patterns))
        
        # Source utilization
        source_utilization = 0.0
        if retrieved_docs:
            doc_content = ' '.join([doc['content'] for doc in retrieved_docs])
            doc_words = set(doc_content.lower().split())
            response_words = set(response_lower.split())
            source_overlap = len(doc_words & response_words)
            source_utilization = min(1.0, source_overlap / len(response_words)) if response_words else 0.0
        
        return {
            'query_coverage': query_coverage,
            'question_addressing': question_addressing,
            'source_utilization': source_utilization,
            'overall_relevance': (query_coverage + question_addressing + source_utilization) / 3
        }
    
    def _evaluate_completeness(self, query: str, response: str, retrieved_docs: List[Dict]) -> Dict[str, float]:
        """Evaluate response completeness"""
        # Check if response addresses all aspects of the query
        query_aspects = self._extract_query_aspects(query)
        addressed_aspects = 0
        
        for aspect in query_aspects:
            if aspect.lower() in response.lower():
                addressed_aspects += 1
        
        aspect_coverage = addressed_aspects / len(query_aspects) if query_aspects else 1.0
        
        # Check for comprehensive information
        information_density = len(response.split()) / max(1, len(query.split()))
        density_score = min(1.0, information_density / 5.0)  # Target 5x query length
        
        # Check for specific details vs general statements
        specific_indicators = ['specifically', 'for example', 'in particular', 'namely', 'such as']
        general_indicators = ['generally', 'usually', 'often', 'typically', 'in general']
        
        specific_count = sum(1 for indicator in specific_indicators if indicator in response.lower())
        general_count = sum(1 for indicator in general_indicators if indicator in response.lower())
        
        specificity_score = specific_count / max(1, specific_count + general_count)
        
        return {
            'aspect_coverage': aspect_coverage,
            'information_density': density_score,
            'specificity_score': specificity_score,
            'overall_completeness': (aspect_coverage + density_score + specificity_score) / 3
        }
    
    def _evaluate_coherence(self, response: str) -> Dict[str, float]:
        """Evaluate response coherence and readability"""
        sentences = response.split('.')
        if len(sentences) < 2:
            return {
                'sentence_flow': 0.0,
                'readability': 0.0,
                'structure_score': 0.0,
                'overall_coherence': 0.0
            }
        
        # Sentence flow (check for transition words)
        transition_words = ['however', 'moreover', 'furthermore', 'additionally', 'consequently', 'therefore']
        transition_count = sum(1 for word in transition_words if word in response.lower())
        sentence_flow = min(1.0, transition_count / len(sentences))
        
        # Readability (simple word count and sentence length)
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        readability = 1.0 - min(1.0, (avg_sentence_length - 15) / 15)  # Target 15 words per sentence
        
        # Structure (check for logical organization)
        structure_indicators = ['first', 'second', 'third', 'finally', 'in conclusion', 'to summarize']
        structure_count = sum(1 for indicator in structure_indicators if indicator in response.lower())
        structure_score = min(1.0, structure_count / 3)  # At least 3 structure indicators
        
        return {
            'sentence_flow': sentence_flow,
            'readability': readability,
            'structure_score': structure_score,
            'overall_coherence': (sentence_flow + readability + structure_score) / 3
        }
    
    def _extract_query_aspects(self, query: str) -> List[str]:
        """Extract different aspects from the query"""
        aspects = []
        
        # Split by common conjunctions
        conjunctions = ['and', 'or', 'but', 'also', 'additionally']
        for conj in conjunctions:
            if conj in query.lower():
                parts = query.lower().split(conj)
                aspects.extend([part.strip() for part in parts])
                break
        
        # If no conjunctions, treat as single aspect
        if not aspects:
            aspects = [query.strip()]
        
        return aspects
    
    def _calculate_overall_score(self, metrics: Dict[str, Dict[str, float]]) -> float:
        """Calculate overall quality score from all metrics"""
        weights = {
            'basic': 0.2,
            'semantic': 0.25,
            'relevance': 0.25,
            'completeness': 0.15,
            'coherence': 0.15
        }
        
        overall_score = 0.0
        for category, weight in weights.items():
            if category in metrics:
                category_score = np.mean(list(metrics[category].values()))
                overall_score += weight * category_score
        
        return min(1.0, max(0.0, overall_score))
    
    def _classify_quality_level(self, score: float) -> str:
        """Classify quality level based on score"""
        if score >= self.quality_thresholds['excellent']:
            return 'excellent'
        elif score >= self.quality_thresholds['good']:
            return 'good'
        elif score >= self.quality_thresholds['fair']:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_improvement_recommendations(self, overall_score: float, metrics: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate improvement recommendations based on metrics"""
        recommendations = []
        
        if overall_score < 0.6:
            recommendations.append("Overall response quality needs improvement")
        
        # Basic metrics recommendations
        if metrics['basic']['keyword_coverage'] < 0.5:
            recommendations.append("Include more keywords from the user query")
        
        if metrics['basic']['length_score'] < 0.5:
            recommendations.append("Adjust response length for better balance")
        
        # Semantic recommendations
        if metrics['semantic']['semantic_similarity'] < 0.5:
            recommendations.append("Improve semantic alignment with the query")
        
        # Relevance recommendations
        if metrics['relevance']['query_coverage'] < 0.5:
            recommendations.append("Better address the specific query terms")
        
        if metrics['relevance']['source_utilization'] < 0.5:
            recommendations.append("Make better use of retrieved source material")
        
        # Completeness recommendations
        if metrics['completeness']['aspect_coverage'] < 0.5:
            recommendations.append("Address more aspects of the user's query")
        
        # Coherence recommendations
        if metrics['coherence']['overall_coherence'] < 0.5:
            recommendations.append("Improve response structure and flow")
        
        return recommendations
    
    def collect_user_feedback(self, query: str, response: str, feedback_type: str, 
                            additional_notes: str = "") -> Dict[str, Any]:
        """
        Collect user feedback on response quality
        
        Args:
            query: User query
            response: Generated response
            feedback_type: 'positive', 'negative', or 'neutral'
            additional_notes: Optional additional feedback notes
        """
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'feedback_type': feedback_type,
            'additional_notes': additional_notes
        }
        
        self.user_feedback.append(feedback)
        self.quality_analytics['feedback_distribution'][feedback_type] += 1
        
        # Log negative feedback for analysis
        if feedback_type == 'negative':
            self._log_misleading_response(query, response, additional_notes)
        
        self.logger.info(f"User feedback collected: {feedback_type}")
        return feedback
    
    def _log_misleading_response(self, query: str, response: str, notes: str):
        """Log misleading responses for analysis"""
        misleading_log = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'notes': notes,
            'type': 'misleading_response'
        }
        
        # Store in quality analytics
        self.quality_analytics['common_issues']['misleading_response'] += 1
        
        # Could save to file for further analysis
        log_file = Path("quality_issues_log.json")
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(misleading_log)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _update_analytics(self, evaluation: Dict[str, Any]):
        """Update quality analytics with new evaluation"""
        self.quality_analytics['total_evaluations'] += 1
        
        # Update average quality score
        total_score = sum(eval['overall_score'] for eval in self.quality_history)
        self.quality_analytics['avg_quality_score'] = total_score / len(self.quality_history)
        
        # Track improvement trends
        if len(self.quality_history) >= 10:  # Every 10 evaluations
            recent_scores = [eval['overall_score'] for eval in self.quality_history[-10:]]
            older_scores = [eval['overall_score'] for eval in self.quality_history[-20:-10]] if len(self.quality_history) >= 20 else []
            
            if older_scores:
                improvement = np.mean(recent_scores) - np.mean(older_scores)
                self.quality_analytics['improvement_trends'].append({
                    'timestamp': datetime.now().isoformat(),
                    'improvement': improvement,
                    'recent_avg': np.mean(recent_scores),
                    'older_avg': np.mean(older_scores)
                })
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        if not self.quality_history:
            return {"message": "No evaluations available"}
        
        recent_evaluations = self.quality_history[-10:] if len(self.quality_history) >= 10 else self.quality_history
        
        # Quality distribution
        quality_levels = [eval['quality_level'] for eval in recent_evaluations]
        quality_distribution = Counter(quality_levels)
        
        # Average scores by category
        avg_scores = {}
        for category in ['basic', 'semantic', 'relevance', 'completeness', 'coherence']:
            scores = [eval['metrics'][category] for eval in recent_evaluations if category in eval['metrics']]
            if scores:
                avg_scores[category] = {
                    key: np.mean([score[key] for score in scores if key in score])
                    for key in scores[0].keys()
                }
        
        return {
            'total_evaluations': self.quality_analytics['total_evaluations'],
            'avg_quality_score': self.quality_analytics['avg_quality_score'],
            'quality_distribution': dict(quality_distribution),
            'avg_scores_by_category': avg_scores,
            'feedback_distribution': self.quality_analytics['feedback_distribution'],
            'common_issues': dict(self.quality_analytics['common_issues']),
            'improvement_trends': self.quality_analytics['improvement_trends'][-5:],  # Last 5 trends
            'recommendations': self._generate_system_recommendations()
        }
    
    def _generate_system_recommendations(self) -> List[str]:
        """Generate system-level improvement recommendations"""
        recommendations = []
        
        if self.quality_analytics['avg_quality_score'] < 0.6:
            recommendations.append("Overall system quality needs improvement")
        
        if self.quality_analytics['feedback_distribution']['negative'] > self.quality_analytics['feedback_distribution']['positive']:
            recommendations.append("User feedback indicates quality issues - review response generation")
        
        if 'misleading_response' in self.quality_analytics['common_issues']:
            recommendations.append("Address misleading response issues")
        
        return recommendations

# Test the quality evaluator
if __name__ == "__main__":
    evaluator = QualityEvaluator()
    
    # Test evaluation
    query = "What are machine learning algorithms?"
    response = "Machine learning algorithms are computational methods that enable computers to learn patterns from data without being explicitly programmed. They include supervised learning, unsupervised learning, and reinforcement learning approaches."
    retrieved_docs = [
        {
            'content': 'Machine learning algorithms are powerful tools for data analysis and pattern recognition.',
            'similarity': 0.8
        },
        {
            'content': 'Supervised learning uses labeled data to train models for prediction tasks.',
            'similarity': 0.7
        }
    ]
    
    print("🧪 Quality Evaluator Test")
    print("=" * 50)
    
    evaluation = evaluator.evaluate_response(query, response, retrieved_docs)
    
    print(f"Query: {query}")
    print(f"Response: {response[:100]}...")
    print(f"Overall Score: {evaluation['overall_score']:.3f}")
    print(f"Quality Level: {evaluation['quality_level']}")
    print(f"Recommendations: {evaluation['recommendations']}")
    
    # Test user feedback
    feedback = evaluator.collect_user_feedback(query, response, 'positive', 'Very helpful response!')
    print(f"User Feedback: {feedback['feedback_type']}")
    
    # Generate quality report
    report = evaluator.get_quality_report()
    print(f"Quality Report: {report['total_evaluations']} evaluations, avg score: {report['avg_quality_score']:.3f}")

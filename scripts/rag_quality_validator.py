#!/usr/bin/env python3
"""
RAG Quality Validator - Systematic validation of retrieval quality
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class RAGQualityValidator:
    """Validate RAG system quality systematically"""
    
    def __init__(self):
        self.test_queries = {
            "philosophical currents of logic and mathematics": {
                "expected_topics": ["logic_mathematics", "philosophy"],
                "expected_keywords": ["logic", "mathematics", "philosophy", "reasoning", "mathematical", "logical"],
                "min_similarity": 0.3,
                "max_similarity": 0.9,
                "expected_file_types": ["academic", "philosophy", "mathematics"]
            },
            "performance optimization techniques": {
                "expected_topics": ["performance", "technology"],
                "expected_keywords": ["performance", "optimization", "speed", "efficiency", "tuning", "improvement"],
                "min_similarity": 0.3,
                "max_similarity": 0.9,
                "expected_file_types": ["technical", "performance", "optimization"]
            },
            "machine learning algorithms": {
                "expected_topics": ["machine_learning", "technology"],
                "expected_keywords": ["machine learning", "algorithms", "neural", "ai", "artificial intelligence", "deep learning"],
                "min_similarity": 0.3,
                "max_similarity": 0.9,
                "expected_file_types": ["technical", "ai", "machine_learning"]
            },
            "business strategy development": {
                "expected_topics": ["business", "strategy"],
                "expected_keywords": ["business", "strategy", "management", "planning", "development", "market"],
                "min_similarity": 0.3,
                "max_similarity": 0.9,
                "expected_file_types": ["business", "strategy", "management"]
            },
            "web development with Python": {
                "expected_topics": ["technology", "programming"],
                "expected_keywords": ["python", "web", "development", "programming", "django", "flask"],
                "min_similarity": 0.3,
                "max_similarity": 0.9,
                "expected_file_types": ["technical", "programming", "web"]
            }
        }
        
        self.validation_history = []
    
    def validate_search_quality(self, query: str, results: List[Dict]) -> Dict:
        """Validate search quality for a specific query"""
        if query not in self.test_queries:
            return {"status": "no_test_case", "message": "No test case for this query"}
        
        test_case = self.test_queries[query]
        validation_results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "total_results": len(results),
            "similarity_range_valid": True,
            "topic_classification_valid": True,
            "keyword_relevance_valid": True,
            "file_type_relevance_valid": True,
            "overall_quality_score": 0.0,
            "detailed_analysis": {}
        }
        
        if not results:
            validation_results["status"] = "no_results"
            validation_results["message"] = "No results returned for query"
            return validation_results
        
        # Detailed analysis
        analysis = self._analyze_results_detailed(query, results, test_case)
        validation_results["detailed_analysis"] = analysis
        
        # Check similarity range
        similarities = [r.get('similarity', 0) for r in results]
        min_sim = min(similarities) if similarities else 0
        max_sim = max(similarities) if similarities else 0
        
        if min_sim < test_case["min_similarity"] or max_sim > test_case["max_similarity"]:
            validation_results["similarity_range_valid"] = False
            validation_results["similarity_issues"] = {
                "min_similarity": min_sim,
                "max_similarity": max_sim,
                "expected_range": [test_case["min_similarity"], test_case["max_similarity"]]
            }
        
        # Check for 1.000 similarity scores (critical issue)
        perfect_similarities = [s for s in similarities if abs(s - 1.0) < 0.001]
        if perfect_similarities:
            validation_results["critical_issue"] = {
                "type": "perfect_similarity_scores",
                "count": len(perfect_similarities),
                "message": "Multiple results have similarity scores of 1.000 - this indicates a broken embedding pipeline"
            }
            validation_results["similarity_range_valid"] = False
        
        # Check topic classification
        topics = [r.get('metadata', {}).get('topic', '') for r in results]
        expected_topics = test_case["expected_topics"]
        topic_matches = sum(1 for topic in topics if topic in expected_topics)
        topic_match_percentage = (topic_matches / len(results)) * 100 if results else 0
        
        if topic_match_percentage < 50:  # At least 50% should match expected topics
            validation_results["topic_classification_valid"] = False
            validation_results["topic_issues"] = {
                "actual_topics": list(set(topics)),
                "expected_topics": expected_topics,
                "match_percentage": topic_match_percentage
            }
        
        # Check keyword relevance
        content_text = " ".join([r.get('content', '') for r in results])
        keyword_matches = sum(1 for keyword in test_case["expected_keywords"] 
                            if keyword.lower() in content_text.lower())
        keyword_match_percentage = (keyword_matches / len(test_case["expected_keywords"])) * 100
        
        if keyword_match_percentage < 30:  # At least 30% of keywords should match
            validation_results["keyword_relevance_valid"] = False
            validation_results["keyword_issues"] = {
                "matched_keywords": [kw for kw in test_case["expected_keywords"] 
                                   if kw.lower() in content_text.lower()],
                "expected_keywords": test_case["expected_keywords"],
                "match_percentage": keyword_match_percentage
            }
        
        # Check file type relevance
        file_types = [r.get('metadata', {}).get('file_type', '') for r in results]
        expected_file_types = test_case.get("expected_file_types", [])
        if expected_file_types:
            file_type_matches = sum(1 for ft in file_types if ft in expected_file_types)
            file_type_match_percentage = (file_type_matches / len(results)) * 100 if results else 0
            
            if file_type_match_percentage < 30:  # At least 30% should match expected file types
                validation_results["file_type_relevance_valid"] = False
                validation_results["file_type_issues"] = {
                    "actual_file_types": list(set(file_types)),
                    "expected_file_types": expected_file_types,
                    "match_percentage": file_type_match_percentage
                }
        
        # Calculate overall quality score
        quality_factors = [
            validation_results["similarity_range_valid"],
            validation_results["topic_classification_valid"],
            validation_results["keyword_relevance_valid"],
            validation_results["file_type_relevance_valid"]
        ]
        validation_results["overall_quality_score"] = sum(quality_factors) / len(quality_factors)
        
        # Determine status
        if validation_results["overall_quality_score"] > 0.8:
            validation_results["status"] = "excellent"
        elif validation_results["overall_quality_score"] > 0.6:
            validation_results["status"] = "good"
        elif validation_results["overall_quality_score"] > 0.4:
            validation_results["status"] = "fair"
        else:
            validation_results["status"] = "poor"
        
        # Store in history
        self.validation_history.append(validation_results)
        
        return validation_results
    
    def _analyze_results_detailed(self, query: str, results: List[Dict], test_case: Dict) -> Dict:
        """Perform detailed analysis of search results"""
        analysis = {
            "query_analysis": {
                "query_length": len(query.split()),
                "query_complexity": self._assess_query_complexity(query),
                "query_type": self._classify_query_type(query)
            },
            "result_analysis": {
                "total_results": len(results),
                "average_similarity": sum(r.get('similarity', 0) for r in results) / len(results) if results else 0,
                "similarity_distribution": self._analyze_similarity_distribution(results),
                "content_length_distribution": self._analyze_content_length_distribution(results),
                "topic_distribution": self._analyze_topic_distribution(results)
            },
            "relevance_analysis": {
                "keyword_coverage": self._analyze_keyword_coverage(query, results, test_case),
                "semantic_relevance": self._analyze_semantic_relevance(query, results),
                "content_quality": self._analyze_content_quality(results)
            }
        }
        
        return analysis
    
    def _assess_query_complexity(self, query: str) -> str:
        """Assess query complexity"""
        words = query.split()
        if len(words) <= 3:
            return "simple"
        elif len(words) <= 7:
            return "moderate"
        else:
            return "complex"
    
    def _classify_query_type(self, query: str) -> str:
        """Classify query type"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["what", "how", "why", "when", "where"]):
            return "question"
        elif any(word in query_lower for word in ["show", "find", "search", "get"]):
            return "search"
        elif any(word in query_lower for word in ["explain", "describe", "tell me about"]):
            return "explanation"
        else:
            return "general"
    
    def _analyze_similarity_distribution(self, results: List[Dict]) -> Dict:
        """Analyze similarity score distribution"""
        similarities = [r.get('similarity', 0) for r in results]
        
        if not similarities:
            return {"min": 0, "max": 0, "mean": 0, "std": 0, "range": 0}
        
        return {
            "min": min(similarities),
            "max": max(similarities),
            "mean": sum(similarities) / len(similarities),
            "std": self._calculate_std(similarities),
            "range": max(similarities) - min(similarities)
        }
    
    def _analyze_content_length_distribution(self, results: List[Dict]) -> Dict:
        """Analyze content length distribution"""
        lengths = [len(r.get('content', '')) for r in results]
        
        if not lengths:
            return {"min": 0, "max": 0, "mean": 0, "std": 0}
        
        return {
            "min": min(lengths),
            "max": max(lengths),
            "mean": sum(lengths) / len(lengths),
            "std": self._calculate_std(lengths)
        }
    
    def _analyze_topic_distribution(self, results: List[Dict]) -> Dict:
        """Analyze topic distribution"""
        topics = [r.get('metadata', {}).get('topic', 'unknown') for r in results]
        topic_counts = {}
        
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return {
            "unique_topics": len(topic_counts),
            "topic_counts": topic_counts,
            "most_common_topic": max(topic_counts.items(), key=lambda x: x[1])[0] if topic_counts else "none"
        }
    
    def _analyze_keyword_coverage(self, query: str, results: List[Dict], test_case: Dict) -> Dict:
        """Analyze keyword coverage in results"""
        expected_keywords = test_case["expected_keywords"]
        content_text = " ".join([r.get('content', '') for r in results]).lower()
        
        matched_keywords = [kw for kw in expected_keywords if kw.lower() in content_text]
        
        return {
            "expected_keywords": expected_keywords,
            "matched_keywords": matched_keywords,
            "coverage_percentage": (len(matched_keywords) / len(expected_keywords)) * 100 if expected_keywords else 0,
            "missing_keywords": [kw for kw in expected_keywords if kw.lower() not in content_text]
        }
    
    def _analyze_semantic_relevance(self, query: str, results: List[Dict]) -> Dict:
        """Analyze semantic relevance of results"""
        query_words = set(query.lower().split())
        
        relevance_scores = []
        for result in results:
            content_words = set(result.get('content', '').lower().split())
            word_overlap = len(query_words.intersection(content_words))
            relevance_score = word_overlap / len(query_words) if query_words else 0
            relevance_scores.append(relevance_score)
        
        return {
            "average_relevance": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0,
            "relevance_distribution": self._analyze_similarity_distribution([{"similarity": s} for s in relevance_scores])
        }
    
    def _analyze_content_quality(self, results: List[Dict]) -> Dict:
        """Analyze content quality of results"""
        quality_metrics = {
            "has_code_blocks": sum(1 for r in results if '```' in r.get('content', '')),
            "has_links": sum(1 for r in results if '[' in r.get('content', '') and ']' in r.get('content', '')),
            "has_headings": sum(1 for r in results if '#' in r.get('content', '')),
            "has_lists": sum(1 for r in results if '- ' in r.get('content', '') or '* ' in r.get('content', '')),
            "average_word_count": sum(len(r.get('content', '').split()) for r in results) / len(results) if results else 0
        }
        
        return quality_metrics
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) <= 1:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def get_validation_summary(self) -> Dict:
        """Get summary of all validations performed"""
        if not self.validation_history:
            return {"message": "No validations performed yet"}
        
        total_validations = len(self.validation_history)
        passed_validations = sum(1 for v in self.validation_history if v["status"] in ["excellent", "good"])
        
        return {
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "success_rate": (passed_validations / total_validations) * 100 if total_validations > 0 else 0,
            "average_quality_score": sum(v["overall_quality_score"] for v in self.validation_history) / total_validations,
            "recent_validations": self.validation_history[-5:]  # Last 5 validations
        }
    
    def export_validation_report(self, filename: str = None) -> str:
        """Export validation report to file"""
        if filename is None:
            filename = f"rag_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        
        report = {
            "validation_summary": self.get_validation_summary(),
            "validation_history": self.validation_history,
            "test_queries": self.test_queries,
            "generated_at": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filename

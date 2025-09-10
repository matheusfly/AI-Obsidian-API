#!/usr/bin/env python3
"""
Enhanced Search Service with Advanced Hybrid Search Features
Building upon our existing comprehensive hybrid search system
"""

import logging
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from collections import Counter
import difflib

from .search_service import SemanticSearchService

logger = logging.getLogger(__name__)

class EnhancedSearchService(SemanticSearchService):
    """
    Enhanced search service with advanced hybrid search features
    Extends our existing comprehensive hybrid search system
    """
    
    def __init__(self, chroma_service, embedding_service):
        super().__init__(chroma_service, embedding_service)
        self.search_analytics = {}
        self.query_expansion_cache = {}
        self.synonym_cache = {}
        
        logger.info("🚀 Initialized Enhanced Search Service with advanced features")

    def search_with_fuzzy_matching(self, query: str, n_results: int = 5, 
                                 fuzzy_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Enhanced search with fuzzy matching for typos and variations
        """
        logger.info(f"🔍 Fuzzy search for: '{query}'")
        
        # First try exact semantic search
        exact_results = self.search_similar(query, n_results=n_results)
        
        if len(exact_results) >= n_results:
            return exact_results
        
        # If not enough results, try fuzzy matching
        fuzzy_results = []
        query_words = query.lower().split()
        
        # Get more results to apply fuzzy matching
        extended_results = self.search_similar(query, n_results=n_results * 3)
        
        for result in extended_results:
            content_words = result['content'].lower().split()
            
            # Calculate fuzzy match score
            fuzzy_score = self._calculate_fuzzy_score(query_words, content_words, fuzzy_threshold)
            
            if fuzzy_score > fuzzy_threshold:
                result['fuzzy_score'] = fuzzy_score
                result['search_type'] = 'fuzzy'
                fuzzy_results.append(result)
        
        # Combine and rank results
        all_results = exact_results + fuzzy_results
        ranked_results = self._rank_fuzzy_results(all_results, query)
        
        logger.info(f"Found {len(exact_results)} exact + {len(fuzzy_results)} fuzzy results")
        return ranked_results[:n_results]

    def search_with_query_expansion(self, query: str, n_results: int = 5,
                                  expand_synonyms: bool = True,
                                  expand_related: bool = True) -> List[Dict[str, Any]]:
        """
        Enhanced search with automatic query expansion
        """
        logger.info(f"🔍 Query expansion for: '{query}'")
        
        # Generate expanded queries
        expanded_queries = self._generate_expanded_queries(query, expand_synonyms, expand_related)
        
        all_results = []
        for expanded_query in expanded_queries:
            results = self.search_similar(expanded_query, n_results=n_results)
            
            # Mark results with expansion info
            for result in results:
                result['expanded_query'] = expanded_query
                result['original_query'] = query
                result['search_type'] = 'expanded'
            
            all_results.extend(results)
        
        # Deduplicate and rank
        unique_results = self._deduplicate_results(all_results)
        ranked_results = self._rank_expanded_results(unique_results, query)
        
        logger.info(f"Generated {len(expanded_queries)} expanded queries, found {len(ranked_results)} unique results")
        return ranked_results[:n_results]

    def search_with_temporal_filtering(self, query: str, n_results: int = 5,
                                     date_range: Optional[Tuple[datetime, datetime]] = None,
                                     relative_days: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Enhanced search with temporal filtering
        """
        logger.info(f"🕒 Temporal search for: '{query}'")
        
        # Build temporal filter
        temporal_filter = self._build_temporal_filter(date_range, relative_days)
        
        # Perform search with temporal filter
        results = self.search_similar(
            query=query,
            n_results=n_results,
            where=temporal_filter
        )
        
        # Add temporal relevance scoring
        for result in results:
            result['temporal_relevance'] = self._calculate_temporal_relevance(
                result.get('metadata', {}), date_range, relative_days
            )
            result['search_type'] = 'temporal'
        
        logger.info(f"Found {len(results)} results with temporal filtering")
        return results

    def search_with_semantic_clustering(self, query: str, n_results: int = 5,
                                      cluster_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Enhanced search with semantic clustering of results
        """
        logger.info(f"🔍 Semantic clustering for: '{query}'")
        
        # Get more results for clustering
        extended_results = self.search_similar(query, n_results=n_results * 2)
        
        if len(extended_results) <= 1:
            return extended_results
        
        # Cluster results by semantic similarity
        clusters = self._cluster_results_semantically(extended_results, cluster_threshold)
        
        # Select best result from each cluster
        clustered_results = []
        for cluster in clusters:
            if cluster:
                # Sort cluster by similarity and take best
                cluster.sort(key=lambda x: x.get('similarity', 0), reverse=True)
                best_result = cluster[0]
                best_result['cluster_size'] = len(cluster)
                best_result['search_type'] = 'clustered'
                clustered_results.append(best_result)
        
        logger.info(f"Clustered {len(extended_results)} results into {len(clusters)} clusters")
        return clustered_results[:n_results]

    def search_with_auto_suggestions(self, partial_query: str, max_suggestions: int = 5) -> List[str]:
        """
        Generate auto-suggestions for partial queries
        """
        logger.info(f"💡 Auto-suggestions for: '{partial_query}'")
        
        # Get search analytics for popular queries
        popular_queries = self._get_popular_queries()
        
        # Find matching suggestions
        suggestions = []
        partial_lower = partial_query.lower()
        
        for query in popular_queries:
            if partial_lower in query.lower():
                suggestions.append(query)
        
        # Add fuzzy suggestions
        fuzzy_suggestions = difflib.get_close_matches(
            partial_query, popular_queries, n=max_suggestions, cutoff=0.6
        )
        
        # Combine and deduplicate
        all_suggestions = list(set(suggestions + fuzzy_suggestions))
        
        logger.info(f"Generated {len(all_suggestions)} suggestions")
        return all_suggestions[:max_suggestions]

    def get_search_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive search analytics
        """
        total_searches = sum(self.search_analytics.values())
        popular_queries = sorted(
            self.search_analytics.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            "total_searches": total_searches,
            "unique_queries": len(self.search_analytics),
            "popular_queries": popular_queries,
            "search_cache_stats": self.get_search_stats(),
            "query_expansion_cache_size": len(self.query_expansion_cache),
            "synonym_cache_size": len(self.synonym_cache)
        }

    def _calculate_fuzzy_score(self, query_words: List[str], content_words: List[str], 
                              threshold: float) -> float:
        """Calculate fuzzy matching score between query and content"""
        if not query_words or not content_words:
            return 0.0
        
        matches = 0
        for query_word in query_words:
            best_match = 0
            for content_word in content_words:
                # Use difflib for fuzzy string matching
                similarity = difflib.SequenceMatcher(None, query_word, content_word).ratio()
                best_match = max(best_match, similarity)
            
            if best_match >= threshold:
                matches += best_match
        
        return matches / len(query_words)

    def _generate_expanded_queries(self, query: str, expand_synonyms: bool, 
                                 expand_related: bool) -> List[str]:
        """Generate expanded queries with synonyms and related terms"""
        expanded_queries = [query]  # Original query
        
        if expand_synonyms:
            synonyms = self._get_synonyms(query)
            for synonym_query in synonyms:
                expanded_queries.append(synonym_query)
        
        if expand_related:
            related_terms = self._get_related_terms(query)
            for related_query in related_terms:
                expanded_queries.append(related_query)
        
        return expanded_queries

    def _get_synonyms(self, query: str) -> List[str]:
        """Get synonyms for query terms (simplified implementation)"""
        # Simple synonym mapping - in production, use NLP libraries
        synonym_map = {
            "ai": ["artificial intelligence", "machine intelligence"],
            "ml": ["machine learning", "machine learning algorithms"],
            "data": ["information", "dataset", "records"],
            "analysis": ["examination", "study", "investigation"],
            "visualization": ["charts", "graphs", "plots", "diagrams"],
            "programming": ["coding", "development", "software development"],
            "python": ["python programming", "python code"],
            "project": ["task", "assignment", "initiative"],
            "management": ["administration", "coordination", "oversight"]
        }
        
        synonyms = []
        query_lower = query.lower()
        
        for term, synonym_list in synonym_map.items():
            if term in query_lower:
                for synonym in synonym_list:
                    synonyms.append(query_lower.replace(term, synonym))
        
        return synonyms

    def _get_related_terms(self, query: str) -> List[str]:
        """Get related terms for query expansion"""
        # Simple related terms mapping
        related_map = {
            "machine learning": ["deep learning", "neural networks", "AI algorithms"],
            "data analysis": ["statistics", "data science", "analytics"],
            "python": ["programming languages", "software development", "coding"],
            "project management": ["agile", "scrum", "productivity", "teamwork"],
            "visualization": ["charts", "dashboards", "reports", "presentations"]
        }
        
        related_queries = []
        query_lower = query.lower()
        
        for term, related_list in related_map.items():
            if term in query_lower:
                for related in related_list:
                    related_queries.append(f"{query} {related}")
        
        return related_queries

    def _build_temporal_filter(self, date_range: Optional[Tuple[datetime, datetime]], 
                             relative_days: Optional[int]) -> Optional[Dict]:
        """Build temporal filter for ChromaDB query"""
        if not date_range and not relative_days:
            return None
        
        if relative_days:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=relative_days)
            date_range = (start_date, end_date)
        
        if date_range:
            start_timestamp = date_range[0].timestamp()
            end_timestamp = date_range[1].timestamp()
            
            return {
                "file_modified": {
                    "$gte": start_timestamp,
                    "$lte": end_timestamp
                }
            }
        
        return None

    def _calculate_temporal_relevance(self, metadata: Dict, date_range: Optional[Tuple], 
                                    relative_days: Optional[int]) -> float:
        """Calculate temporal relevance score"""
        if not metadata.get('file_modified'):
            return 0.0
        
        file_timestamp = metadata['file_modified']
        current_time = time.time()
        
        # Calculate recency score (more recent = higher score)
        age_days = (current_time - file_timestamp) / (24 * 3600)
        
        if relative_days:
            # Score based on relative time window
            if age_days <= relative_days:
                return 1.0 - (age_days / relative_days)
            else:
                return 0.0
        else:
            # Score based on absolute recency (exponential decay)
            return max(0.0, 1.0 - (age_days / 365))  # Decay over a year

    def _cluster_results_semantically(self, results: List[Dict], threshold: float) -> List[List[Dict]]:
        """Cluster results by semantic similarity"""
        if len(results) <= 1:
            return [results]
        
        clusters = []
        used_indices = set()
        
        for i, result1 in enumerate(results):
            if i in used_indices:
                continue
            
            cluster = [result1]
            used_indices.add(i)
            
            for j, result2 in enumerate(results[i+1:], i+1):
                if j in used_indices:
                    continue
                
                # Calculate semantic similarity between results
                similarity = self._calculate_result_similarity(result1, result2)
                
                if similarity >= threshold:
                    cluster.append(result2)
                    used_indices.add(j)
            
            clusters.append(cluster)
        
        return clusters

    def _calculate_result_similarity(self, result1: Dict, result2: Dict) -> float:
        """Calculate similarity between two search results"""
        # Use content similarity as proxy for semantic similarity
        content1 = result1.get('content', '').lower()
        content2 = result2.get('content', '').lower()
        
        # Simple word overlap similarity
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

    def _rank_fuzzy_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Rank results combining semantic and fuzzy scores"""
        for result in results:
            semantic_score = result.get('similarity', 0)
            fuzzy_score = result.get('fuzzy_score', 0)
            
            # Combine scores (semantic 70% + fuzzy 30%)
            combined_score = semantic_score * 0.7 + fuzzy_score * 0.3
            result['combined_score'] = combined_score
        
        results.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        return results

    def _rank_expanded_results(self, results: List[Dict], original_query: str) -> List[Dict]:
        """Rank expanded search results"""
        for result in results:
            semantic_score = result.get('similarity', 0)
            expanded_query = result.get('expanded_query', '')
            
            # Boost score if expanded query is close to original
            expansion_boost = 1.0
            if expanded_query != original_query:
                similarity = difflib.SequenceMatcher(None, original_query, expanded_query).ratio()
                expansion_boost = 0.8 + (similarity * 0.2)  # 0.8 to 1.0 range
            
            result['combined_score'] = semantic_score * expansion_boost
        
        results.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        return results

    def _get_popular_queries(self) -> List[str]:
        """Get popular queries from search analytics"""
        return list(self.search_analytics.keys())

    def _track_search_query(self, query: str):
        """Track search query for analytics"""
        self.search_analytics[query] = self.search_analytics.get(query, 0) + 1

"""
Improved Semantic search service with better cross-encoder re-ranking
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import re
from datetime import datetime
import asyncio
from sentence_transformers import CrossEncoder
from .query_expansion_service import QueryExpansionService, ExpansionStrategy

logger = logging.getLogger(__name__)


class ImprovedSemanticSearchService:
    """Improved service for semantic search with better cross-encoder re-ranking"""
    
    def __init__(self, chroma_service, embedding_service, gemini_api_key: Optional[str] = None):
        self.chroma_service = chroma_service
        self.embedding_service = embedding_service
        self.search_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Initialize a better cross-encoder for re-ranking
        logger.info("Initializing improved cross-encoder for re-ranking...")
        try:
            # Try a more general-purpose cross-encoder
            self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2', max_length=512)
            logger.info("Improved cross-encoder initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to load improved cross-encoder, falling back to default: {e}")
            self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
            logger.info("Fallback cross-encoder initialized")
        
        # Initialize query expansion service
        logger.info("Initializing query expansion service...")
        self.query_expansion_service = QueryExpansionService(gemini_api_key=gemini_api_key)
        logger.info("Query expansion service initialized successfully")
    
    def _generate_cache_key(self, query: str, filters: Optional[Dict[str, Any]] = None, n_results: int = 5) -> str:
        """Generate cache key for search query"""
        import hashlib
        cache_data = f"{query}:{filters}:{n_results}"
        return hashlib.md5(cache_data.encode('utf-8')).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any], ttl: int = 1800) -> bool:
        """Check if cache entry is still valid"""
        cache_time = cache_entry.get("timestamp", 0)
        current_time = datetime.utcnow().timestamp()
        return (current_time - cache_time) < ttl
    
    async def search_similar(self, query: str, n_results: int = 5, 
                      where: Optional[Dict] = None, 
                      where_document: Optional[Dict] = None,
                      use_cache: bool = True,
                      expand_query: bool = True,
                      expansion_strategy: ExpansionStrategy = ExpansionStrategy.HYBRID) -> List[Dict[str, Any]]:
        """
        Search for similar content with optional metadata and document content filters.
        """
        
        # Expand query if requested
        search_query = query
        query_analysis = None
        
        if expand_query:
            logger.info(f"Expanding query: '{query}' using strategy: {expansion_strategy.value}")
            query_analysis = await self.query_expansion_service.expand_query(query, expansion_strategy)
            search_query = query_analysis.expanded_query
            logger.info(f"Expanded query: '{query}' → '{search_query}' (confidence: {query_analysis.expansion_confidence:.2f})")
        
        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(search_query, where, n_results)
            if cache_key in self.search_cache:
                cache_entry = self.search_cache[cache_key]
                if self._is_cache_valid(cache_entry):
                    self.cache_hits += 1
                    logger.debug(f"Cache hit for query: {search_query[:50]}...")
                    cached_results = cache_entry["results"]
                    
                    # Add query analysis info to cached results
                    if query_analysis:
                        for result in cached_results:
                            result['query_analysis'] = {
                                'original_query': query_analysis.original_query,
                                'expanded_query': query_analysis.expanded_query,
                                'intent': query_analysis.intent,
                                'entities': query_analysis.entities,
                                'expansion_confidence': query_analysis.expansion_confidence,
                                'strategy_used': query_analysis.strategy_used.value,
                                'expansion_reasoning': query_analysis.expansion_reasoning
                            }
                    
                    return cached_results
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(search_query)
            
            # Search in ChromaDB with rich metadata filtering
            results = self.chroma_service.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity": 1 - results['distances'][0][i]  # Cosine similarity
                }
                
                # Add query analysis info if available
                if query_analysis:
                    result['query_analysis'] = {
                        'original_query': query_analysis.original_query,
                        'expanded_query': query_analysis.expanded_query,
                        'intent': query_analysis.intent,
                        'entities': query_analysis.entities,
                        'expansion_confidence': query_analysis.expansion_confidence,
                        'strategy_used': query_analysis.strategy_used.value,
                        'expansion_reasoning': query_analysis.expansion_reasoning
                    }
                
                formatted_results.append(result)
            
            # Enhance results with additional metadata
            enhanced_results = self._enhance_search_results(formatted_results, search_query)
            
            # Cache results
            if use_cache:
                cache_key = self._generate_cache_key(search_query, where, n_results)
                self.search_cache[cache_key] = {
                    "results": enhanced_results,
                    "timestamp": datetime.utcnow().timestamp()
                }
                self.cache_misses += 1
            
            logger.debug(f"Found {len(enhanced_results)} results for query: {query[:50]}...")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise
    
    async def search_with_improved_rerank(self, query: str, n_results: int = 5, rerank_top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Improved search with cross-encoder re-ranking for higher precision.
        """
        try:
            logger.info(f"Starting improved re-ranked search for query: {query[:50]}...")
            
            # Step 1: Get more candidates from ChromaDB (without query expansion to avoid API issues)
            initial_results = await self.search_similar(
                query=query, 
                n_results=rerank_top_k, 
                use_cache=False,
                expand_query=False  # Disable query expansion to avoid API quota issues
            )
            
            if len(initial_results) <= n_results:
                logger.info(f"Only {len(initial_results)} results found, returning without re-ranking")
                return initial_results
            
            logger.info(f"Re-ranking {len(initial_results)} initial results")
            
            # Step 2: Create pairs for the cross-encoder
            pairs = [(query, result['content']) for result in initial_results]
            
            # Step 3: Get cross-encoder scores
            logger.debug("Computing cross-encoder scores...")
            cross_scores = self.cross_encoder.predict(pairs)
            
            # Step 4: Improved score combination and enhance results
            for i, result in enumerate(initial_results):
                cross_score = float(cross_scores[i])
                
                # Improved scoring: normalize cross-encoder score and combine with similarity
                # Cross-encoder scores are typically in range [-10, 10], normalize to [0, 1]
                normalized_cross_score = (cross_score + 10) / 20  # Normalize to [0, 1]
                normalized_cross_score = max(0, min(1, normalized_cross_score))  # Clamp to [0, 1]
                
                # Better combination: 40% vector similarity + 60% cross-encoder score
                # This gives more weight to the cross-encoder while still considering vector similarity
                result['cross_score'] = cross_score
                result['normalized_cross_score'] = normalized_cross_score
                result['final_score'] = 0.4 * result['similarity'] + 0.6 * normalized_cross_score
                
                # Add re-ranking metadata
                result['search_type'] = 'improved_reranked'
                result['rerank_metadata'] = {
                    'vector_similarity': result['similarity'],
                    'cross_encoder_score': cross_score,
                    'normalized_cross_score': normalized_cross_score,
                    'final_score': result['final_score'],
                    'rerank_position': i + 1
                }
            
            # Step 5: Sort by the new final score and return top N
            initial_results.sort(key=lambda x: x['final_score'], reverse=True)
            final_results = initial_results[:n_results]
            
            logger.info(f"Improved re-ranking complete. Returning top {len(final_results)} results")
            
            # Log score distribution for analysis
            if final_results:
                scores = [r['final_score'] for r in final_results]
                logger.debug(f"Final score range: {min(scores):.3f} - {max(scores):.3f}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error in improved re-ranked search: {e}")
            # Fallback to regular search if re-ranking fails
            logger.warning("Falling back to regular semantic search")
            return await self.search_similar(query, n_results, expand_query=False)
    
    def _enhance_search_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Enhance search results with additional information"""
        enhanced_results = []
        
        for result in results:
            # Add query relevance score
            result["query_relevance"] = self._calculate_query_relevance(result["content"], query)
            
            # Add content preview
            result["preview"] = self._generate_content_preview(result["content"], query)
            
            # Add search metadata
            result["search_timestamp"] = datetime.utcnow().isoformat()
            result["search_type"] = "semantic"
            
            enhanced_results.append(result)
        
        return enhanced_results
    
    def _calculate_query_relevance(self, content: str, query: str) -> float:
        """Calculate relevance score between content and query"""
        content_lower = content.lower()
        query_lower = query.lower()
        
        # Count word matches
        query_words = query_lower.split()
        content_words = content_lower.split()
        
        matches = sum(1 for word in query_words if word in content_words)
        relevance = matches / len(query_words) if query_words else 0
        
        return relevance
    
    def _generate_content_preview(self, content: str, query: str, max_length: int = 200) -> str:
        """Generate content preview highlighting query terms"""
        if len(content) <= max_length:
            return content
        
        # Find query terms in content
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Find the best position to start the preview
        best_position = 0
        max_matches = 0
        
        for i in range(len(content) - max_length + 1):
            snippet = content_lower[i:i + max_length]
            matches = sum(1 for word in query_lower.split() if word in snippet)
            if matches > max_matches:
                max_matches = matches
                best_position = i
        
        # Generate preview
        preview = content[best_position:best_position + max_length]
        
        # Add ellipsis if needed
        if best_position > 0:
            preview = "..." + preview
        if best_position + max_length < len(content):
            preview = preview + "..."
        
        return preview
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search statistics"""
        cache_size = len(self.search_cache)
        total_searches = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_searches if total_searches > 0 else 0
        
        return {
            "cache_size": cache_size,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "total_searches": total_searches
        }
    
    def clear_search_cache(self):
        """Clear search cache"""
        self.search_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Search cache cleared")

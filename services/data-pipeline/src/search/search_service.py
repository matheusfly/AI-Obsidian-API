"""
Semantic search service combining vector and metadata search
"""
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
import re
from datetime import datetime
import asyncio
from sentence_transformers import CrossEncoder
from .query_expansion_service import QueryExpansionService, ExpansionStrategy
from cache.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """Service for semantic search combining vector and metadata search"""
    
    def __init__(self, chroma_service, embedding_service, gemini_api_key: Optional[str] = None, 
                 cache_manager: Optional[CacheManager] = None):
        self.chroma_service = chroma_service
        self.embedding_service = embedding_service
        self.cache_manager = cache_manager or CacheManager()
        self.search_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Initialize a lightweight cross-encoder for re-ranking
        logger.info("Initializing cross-encoder for re-ranking...")
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
        logger.info("Cross-encoder initialized successfully")
        
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
        Args:
            query (str): The user's search query.
            n_results (int): Number of results to return.
            where (Dict, optional): ChromaDB metadata filter (e.g., {"file_extension": "md", "chunk_token_count": {"$gt": 200}}).
            where_document (Dict, optional): ChromaDB document content filter (e.g., {"$contains": "Python"}).
            use_cache (bool): Whether to use caching.
            expand_query (bool): Whether to expand the query for better results.
            expansion_strategy (ExpansionStrategy): Strategy for query expansion.
        """
        
        start_time = time.time()
        status = "success"
        
        try:
            # Expand query if requested
            search_query = query
            query_analysis = None
            
            if expand_query:
                logger.info(f"Expanding query: '{query}' using strategy: {expansion_strategy.value}")
                query_analysis = await self.query_expansion_service.expand_query(query, expansion_strategy)
                search_query = query_analysis.expanded_query
                logger.info(f"Expanded query: '{query}' → '{search_query}' (confidence: {query_analysis.expansion_confidence:.2f})")
        except Exception as e:
            logger.warning(f"Query expansion failed: {e}")
            search_query = query
            query_analysis = None
        
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
            # Check for cached query embedding first (blazing-fast performance)
            query_embedding = self.cache_manager.get_cached_query_embedding(search_query)
            if query_embedding is None:
                # Generate new embedding and cache it
                query_embedding = self.embedding_service.generate_embedding(search_query)
                self.cache_manager.cache_query_embedding(search_query, query_embedding)
                logger.debug(f"Generated and cached new query embedding for: {search_query[:50]}...")
            else:
                logger.debug(f"Using cached query embedding for: {search_query[:50]}...")
            
            # Search in ChromaDB with rich metadata filtering
            results = self.chroma_service.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,          # ✅ Leverage rich metadata filtering
                where_document=where_document  # ✅ Leverage keyword filtering
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],  # Full 20-field metadata
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
            status = "error"
            logger.error(f"Error in semantic search: {e}")
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            try:
                from ..monitoring.metrics import get_metrics
                metrics = get_metrics()
                metrics.record_search_request("/search", "semantic", duration, len(enhanced_results) if 'enhanced_results' in locals() else 0, status)
            except Exception as e:
                logger.warning(f"Failed to record search metrics: {e}")
    
    async def get_query_suggestions(self, query: str) -> Dict[str, Any]:
        """
        Get query expansion suggestions without performing a search.
        Args:
            query (str): The user's search query.
        Returns:
            Dict[str, Any]: Query analysis and expansion suggestions.
        """
        try:
            # Analyze the query
            query_analysis = await self.query_expansion_service.expand_query(query, ExpansionStrategy.HYBRID)
            
            # Get expansion suggestions
            suggestions = self.query_expansion_service.get_expansion_suggestions(query)
            
            return {
                "original_query": query,
                "expanded_query": query_analysis.expanded_query,
                "intent": query_analysis.intent,
                "entities": query_analysis.entities,
                "expansion_confidence": query_analysis.expansion_confidence,
                "strategy_used": query_analysis.strategy_used.value,
                "expansion_reasoning": query_analysis.expansion_reasoning,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error getting query suggestions: {e}")
            return {
                "original_query": query,
                "expanded_query": query,
                "intent": "general",
                "entities": [],
                "expansion_confidence": 0.0,
                "strategy_used": "none",
                "expansion_reasoning": "Error occurred during expansion",
                "suggestions": []
            }
    
    def search_by_metadata(self, metadata_filter: Dict, n_results: int = 10) -> List[Dict[str, Any]]:
        """Helper method for complex metadata-only searches."""
        try:
            # Use collection.get() for metadata-only if you don't need semantic similarity
            results = self.chroma_service.collection.get(
                where=metadata_filter,
                limit=n_results,
                include=['documents', 'metadatas']
            )
            
            # Format results
            formatted_results = []
            if results and results['documents']:
                for i in range(len(results['documents'])):
                    formatted_results.append({
                        "id": results['ids'][i],
                        "content": results['documents'][i],
                        "metadata": results['metadatas'][i],
                        "similarity": 1.0,  # Perfect match for metadata search
                        "search_type": "metadata_search"
                    })
            
            logger.debug(f"Found {len(formatted_results)} results for metadata filter: {metadata_filter}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in metadata search: {e}")
            raise
    
    async def search_by_keywords(self, keywords: List[str], n_results: int = 5,
                          filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search by keywords using text matching"""
        try:
            # Create a text query from keywords
            query_text = " ".join(keywords)
            
            # Use semantic search with the keyword query
            results = await self.search_similar(query_text, n_results, filters)
            
            # Filter results by keyword presence
            keyword_results = []
            for result in results:
                content_lower = result["content"].lower()
                if any(keyword.lower() in content_lower for keyword in keywords):
                    # Add keyword match score
                    keyword_matches = sum(1 for keyword in keywords 
                                        if keyword.lower() in content_lower)
                    result["keyword_score"] = keyword_matches / len(keywords)
                    keyword_results.append(result)
            
            # Sort by keyword score
            keyword_results.sort(key=lambda x: x.get("keyword_score", 0), reverse=True)
            
            return keyword_results[:n_results]
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            raise
    
    async def search_by_tags(self, tags: List[str], n_results: int = 5) -> List[Dict[str, Any]]:
        """Search by tags"""
        try:
            # Search using metadata filters
            filters = {"tags": {"$in": tags}}
            results = self.chroma_service.search_by_metadata(filters, n_results)
            
            # Enhance results
            enhanced_results = []
            for result in results:
                enhanced_result = {
                    "id": result["id"],
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "similarity": 1.0,  # Perfect match for tag search
                    "search_type": "tag_search"
                }
                enhanced_results.append(enhanced_result)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error in tag search: {e}")
            raise
    
    def search_by_path(self, path_pattern: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search by file path pattern"""
        try:
            # Use regex pattern for path matching
            filters = {"path": {"$regex": path_pattern}}
            results = self.chroma_service.search_by_metadata(filters, n_results)
            
            # Enhance results
            enhanced_results = []
            for result in results:
                enhanced_result = {
                    "id": result["id"],
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "similarity": 1.0,  # Perfect match for path search
                    "search_type": "path_search"
                }
                enhanced_results.append(enhanced_result)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error in path search: {e}")
            raise
    
    async def hybrid_search(self, query: str, n_results: int = 5,
                     include_keywords: bool = True,
                     include_tags: bool = True,
                     filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Perform hybrid search combining multiple search methods"""
        try:
            all_results = []
            
            # Semantic search
            semantic_results = await self.search_similar(query, n_results, filters)
            for result in semantic_results:
                result["search_type"] = "semantic"
                result["search_score"] = result["similarity"]
            all_results.extend(semantic_results)
            
            # Keyword search
            if include_keywords:
                keywords = query.split()
                keyword_results = await self.search_by_keywords(keywords, n_results, filters)
                for result in keyword_results:
                    result["search_type"] = "keyword"
                    result["search_score"] = result.get("keyword_score", 0)
                all_results.extend(keyword_results)
            
            # Tag search (extract tags from query)
            if include_tags:
                tags = self._extract_tags_from_query(query)
                if tags:
                    tag_results = await self.search_by_tags(tags, n_results)
                    for result in tag_results:
                        result["search_type"] = "tag"
                        result["search_score"] = 1.0
                    all_results.extend(tag_results)
            
            # Remove duplicates and rank
            unique_results = self._deduplicate_results(all_results)
            ranked_results = self._rank_hybrid_results(unique_results, query)
            
            return ranked_results[:n_results]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            raise
    
    def _extract_tags_from_query(self, query: str) -> List[str]:
        """Extract tags from query text"""
        # Look for #tag patterns
        tag_pattern = r'#([a-zA-Z0-9_-]+)'
        tags = re.findall(tag_pattern, query)
        return tags
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on ID"""
        seen_ids = set()
        unique_results = []
        
        for result in results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                unique_results.append(result)
        
        return unique_results
    
    def _rank_hybrid_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rank hybrid search results"""
        for result in results:
            # Combine different scores
            semantic_score = result.get("similarity", 0)
            keyword_score = result.get("keyword_score", 0)
            tag_score = 1.0 if result.get("search_type") == "tag" else 0
            
            # Calculate combined score
            combined_score = (
                semantic_score * 0.6 +  # Semantic similarity weight
                keyword_score * 0.3 +    # Keyword match weight
                tag_score * 0.1          # Tag match weight
            )
            
            result["combined_score"] = combined_score
        
        # Sort by combined score
        results.sort(key=lambda x: x["combined_score"], reverse=True)
        return results
    
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
        """Get comprehensive search statistics including cache performance"""
        cache_size = len(self.search_cache)
        total_searches = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_searches if total_searches > 0 else 0
        
        # Get cache manager statistics
        cache_stats = self.cache_manager.get_cache_stats()
        
        return {
            "search_result_cache": {
                "cache_size": cache_size,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "hit_rate": hit_rate,
                "total_searches": total_searches
            },
            "query_embedding_cache": cache_stats["query_embedding_cache"],
            "total_performance": {
                "query_embedding_hit_rate": cache_stats["query_embedding_cache"]["hit_rate"],
                "search_result_hit_rate": f"{hit_rate:.2f}%",
                "total_query_requests": cache_stats["total_requests"]["query_embeddings"],
                "total_search_requests": cache_stats["total_requests"]["search_results"]
            }
        }
    
    async def search_with_rerank(self, query: str, n_results: int = 5, rerank_top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Search with cross-encoder re-ranking for higher precision.
        
        Args:
            query (str): The user's search query.
            n_results (int): Number of final results to return.
            rerank_top_k (int): Number of initial results to re-rank.
        
        Returns:
            List[Dict[str, Any]]: Re-ranked search results with cross-encoder scores.
        """
        try:
            logger.info(f"Starting re-ranked search for query: {query[:50]}...")
            
            # Step 1: Get more candidates from ChromaDB
            initial_results = await self.search_similar(query, n_results=rerank_top_k, use_cache=False)
            
            if len(initial_results) <= n_results:
                logger.info(f"Only {len(initial_results)} results found, returning without re-ranking")
                return initial_results
            
            logger.info(f"Re-ranking {len(initial_results)} initial results")
            
            # Step 2: Create pairs for the cross-encoder
            pairs = [(query, result['content']) for result in initial_results]
            
            # Step 3: Get cross-encoder scores
            logger.debug("Computing cross-encoder scores...")
            cross_scores = self.cross_encoder.predict(pairs)
            
            # Step 4: Combine scores and enhance results
            for i, result in enumerate(initial_results):
                result['cross_score'] = float(cross_scores[i])
                
                # Simple combination: final_score = 0.3 * vector_similarity + 0.7 * cross_score
                # This weighting can be tuned based on performance
                result['final_score'] = 0.3 * result['similarity'] + 0.7 * result['cross_score']
                
                # Add re-ranking metadata
                result['search_type'] = 'reranked'
                result['rerank_metadata'] = {
                    'vector_similarity': result['similarity'],
                    'cross_encoder_score': result['cross_score'],
                    'final_score': result['final_score'],
                    'rerank_position': i + 1
                }
            
            # Step 5: Sort by the new final score and return top N
            initial_results.sort(key=lambda x: x['final_score'], reverse=True)
            final_results = initial_results[:n_results]
            
            logger.info(f"Re-ranking complete. Returning top {len(final_results)} results")
            
            # Log score distribution for analysis
            if final_results:
                scores = [r['final_score'] for r in final_results]
                logger.debug(f"Final score range: {min(scores):.3f} - {max(scores):.3f}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error in re-ranked search: {e}")
            # Fallback to regular search if re-ranking fails
            logger.warning("Falling back to regular semantic search")
            return await self.search_similar(query, n_results)
    
    async def search_hybrid(self, query: str, n_results: int = 5, 
                           keyword_filter: Optional[str] = None,
                           where: Optional[Dict] = None,
                           use_cache: bool = True,
                           expand_query: bool = True,
                           expansion_strategy: ExpansionStrategy = ExpansionStrategy.HYBRID) -> List[Dict[str, Any]]:
        """
        True hybrid search combining semantic similarity with keyword filtering.
        
        Args:
            query (str): The user's search query.
            n_results (int): Number of results to return.
            keyword_filter (str, optional): Keyword to filter document content (e.g., "requests", "Python").
            where (Dict, optional): ChromaDB metadata filter.
            use_cache (bool): Whether to use caching.
            expand_query (bool): Whether to expand the query for better results.
            expansion_strategy (ExpansionStrategy): Strategy for query expansion.
            
        Returns:
            List[Dict[str, Any]]: Search results with both semantic similarity and keyword matching.
        """
        try:
            logger.info(f"Starting hybrid search for query: '{query}' with keyword filter: '{keyword_filter}'...")
            
            # Prepare where_document filter for keyword matching
            where_document = None
            if keyword_filter:
                where_document = {"$contains": keyword_filter}
                logger.info(f"Applying keyword filter: '{keyword_filter}'")
            
            # Use the existing search_similar method with keyword filtering
            results = await self.search_similar(
                query=query,
                n_results=n_results,
                where=where,
                where_document=where_document,
                use_cache=use_cache,
                expand_query=expand_query,
                expansion_strategy=expansion_strategy
            )
            
            # Enhance results with hybrid search metadata
            for result in results:
                result['search_type'] = 'hybrid'
                result['hybrid_metadata'] = {
                    'keyword_filter': keyword_filter,
                    'has_keyword_match': keyword_filter is not None,
                    'semantic_similarity': result.get('similarity', 0.0)
                }
                
                # Add keyword match score if keyword filter was used
                if keyword_filter:
                    content_lower = result['content'].lower()
                    keyword_lower = keyword_filter.lower()
                    keyword_count = content_lower.count(keyword_lower)
                    result['hybrid_metadata']['keyword_count'] = keyword_count
                    result['hybrid_metadata']['keyword_density'] = keyword_count / len(content_lower.split()) if content_lower else 0
            
            logger.info(f"Hybrid search complete. Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            # Fallback to regular semantic search if hybrid search fails
            logger.warning("Falling back to regular semantic search")
            return await self.search_similar(query, n_results, where, use_cache, expand_query, expansion_strategy)
    
    def precompute_common_queries(self, common_queries: List[str]) -> None:
        """
        Pre-compute embeddings for common queries to achieve blazing-fast performance.
        
        Args:
            common_queries: List of frequently asked questions
        """
        logger.info(f"Pre-computing embeddings for {len(common_queries)} common queries...")
        self.cache_manager.precompute_common_queries(common_queries, self.embedding_service)
        logger.info("Common query pre-computation complete!")
    
    def warm_up_cache(self, common_queries: List[str]) -> None:
        """
        Warm up the cache with common queries for optimal performance.
        
        Args:
            common_queries: List of frequently asked questions
        """
        logger.info("Warming up search cache for optimal performance...")
        self.cache_manager.warm_up_cache(common_queries, self.embedding_service)
        logger.info("Cache warm-up complete!")
    
    def get_cache_performance_stats(self) -> Dict[str, Any]:
        """Get detailed cache performance statistics"""
        return self.cache_manager.get_cache_stats()
    
    def clear_search_cache(self):
        """Clear search cache"""
        self.search_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Search cache cleared")
    
    def clear_all_caches(self):
        """Clear all caches including query embeddings"""
        self.clear_search_cache()
        self.cache_manager.clear_all_caches()
        logger.info("All caches cleared")

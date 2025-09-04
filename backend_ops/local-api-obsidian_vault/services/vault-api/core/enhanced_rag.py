"""Enhanced RAG with LangGraph Integration and Advanced Context Engineering"""
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import hashlib
import json
from .supabase_client import supabase_client

class AdvancedRAGEngine:
    def __init__(self):
        self.supabase = supabase_client
        self.context_cache = {}
        
    async def hierarchical_retrieval(self, query: str, agent_id: str, depth: int = 3) -> Dict[str, Any]:
        """Multi-level retrieval with context propagation"""
        try:
            # Level 1: Tag-based filtering
            tag_filtered = await self._tag_based_filter(query)
            
            # Level 2: Vector similarity search
            vector_results = await self._vector_search(query, tag_filtered)
            
            # Level 3: Graph-based expansion
            graph_expanded = await self._graph_expansion(vector_results, depth)
            
            # Context engineering with backlinks
            enriched_context = await self._enrich_with_backlinks(graph_expanded)
            
            # Store enhanced context
            await self.supabase.store_agent_context(agent_id, {
                "query": query,
                "retrieval_layers": len(enriched_context),
                "context_quality": self._calculate_context_quality(enriched_context),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": True,
                "results": enriched_context,
                "metadata": {
                    "retrieval_method": "hierarchical",
                    "layers_processed": 3,
                    "context_quality": self._calculate_context_quality(enriched_context)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def semantic_chunking(self, content: str, metadata: Dict) -> List[Dict]:
        """Advanced semantic-aware chunking for Obsidian notes"""
        chunks = []
        current_chunk = ""
        current_header = ""
        semantic_boundary_score = 0
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Track headers for context
            if line.startswith('#'):
                if current_chunk and semantic_boundary_score > 0.7:
                    chunks.append({
                        "content": f"{current_header}\n{current_chunk}".strip(),
                        "metadata": {**metadata, "header": current_header, "chunk_id": len(chunks)},
                        "semantic_score": semantic_boundary_score
                    })
                    current_chunk = ""
                current_header = line.strip()
                semantic_boundary_score = 1.0
            
            # Calculate semantic boundary
            if i > 0:
                semantic_boundary_score = self._calculate_semantic_boundary(lines[i-1], line)
            
            current_chunk += line + '\n'
            
            # Chunk if semantic boundary is strong or size limit reached
            if (semantic_boundary_score > 0.8 and len(current_chunk) > 200) or len(current_chunk) > 500:
                chunks.append({
                    "content": f"{current_header}\n{current_chunk}".strip(),
                    "metadata": {**metadata, "header": current_header, "chunk_id": len(chunks)},
                    "semantic_score": semantic_boundary_score
                })
                current_chunk = ""
        
        if current_chunk:
            chunks.append({
                "content": f"{current_header}\n{current_chunk}".strip(),
                "metadata": {**metadata, "header": current_header, "chunk_id": len(chunks)},
                "semantic_score": semantic_boundary_score
            })
        
        return chunks
    
    async def adaptive_query_expansion(self, query: str, context_history: List[str] = None) -> str:
        """Dynamic query expansion based on vault structure and history"""
        # Extract entities from query
        entities = self._extract_entities(query)
        
        # Get related concepts from previous queries
        if context_history:
            related_concepts = self._extract_related_concepts(context_history)
            entities.extend(related_concepts)
        
        # Add temporal context
        temporal_expansion = self._add_temporal_context(query)
        
        # Combine with semantic synonyms
        expanded = f"{query} {' '.join(entities)} {temporal_expansion}"
        
        return expanded.strip()
    
    async def multi_modal_fusion(self, text_results: List[Dict], graph_results: List[Dict]) -> List[Dict]:
        """Fuse results from multiple retrieval modalities"""
        # Reciprocal Rank Fusion with adaptive weights
        scores = {}
        
        # Weight text results (semantic similarity)
        for i, doc in enumerate(text_results):
            scores[doc["id"]] = (1/(i+1)) * 0.6
        
        # Weight graph results (structural relevance)
        for i, doc in enumerate(graph_results):
            doc_id = doc["id"]
            if doc_id in scores:
                scores[doc_id] += (1/(i+1)) * 0.4
            else:
                scores[doc_id] = (1/(i+1)) * 0.4
        
        # Sort and return top results
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [self._get_document_by_id(doc_id) for doc_id, _ in sorted_results[:10]]
    
    def _calculate_semantic_boundary(self, line1: str, line2: str) -> float:
        """Calculate semantic boundary strength between lines"""
        # Simple heuristic - can be enhanced with embeddings
        if line2.startswith('#'):
            return 1.0
        if line1.strip() == "" and line2.strip() != "":
            return 0.8
        if line1.endswith('.') and line2.startswith(('However', 'But', 'Therefore')):
            return 0.7
        return 0.3
    
    def _calculate_context_quality(self, context: List[Dict]) -> float:
        """Calculate overall context quality score"""
        if not context:
            return 0.0
        
        # Factors: diversity, relevance, completeness
        diversity = len(set(c.get("metadata", {}).get("folder", "") for c in context)) / len(context)
        avg_relevance = sum(c.get("score", 0) for c in context) / len(context)
        completeness = min(len(context) / 5, 1.0)  # Optimal around 5 chunks
        
        return (diversity * 0.3 + avg_relevance * 0.5 + completeness * 0.2)
    
    async def _tag_based_filter(self, query: str) -> List[str]:
        """Filter by relevant tags"""
        # Extract potential tags from query
        words = query.lower().split()
        return [f"#{word}" for word in words if len(word) > 3]
    
    async def _vector_search(self, query: str, tag_filter: List[str]) -> List[Dict]:
        """Perform vector similarity search"""
        # Placeholder - integrate with your vector DB
        return [{"id": f"doc_{i}", "score": 0.9-i*0.1, "content": f"Content for {query}"} for i in range(5)]
    
    async def _graph_expansion(self, results: List[Dict], depth: int) -> List[Dict]:
        """Expand results using graph relationships"""
        expanded = results.copy()
        for result in results[:3]:  # Expand top 3 results
            # Get linked documents
            linked = await self._get_linked_documents(result["id"])
            expanded.extend(linked[:2])  # Add top 2 linked docs
        return expanded
    
    async def _enrich_with_backlinks(self, results: List[Dict]) -> List[Dict]:
        """Enrich context with backlink information"""
        for result in results:
            backlinks = await self._get_backlinks(result["id"])
            result["backlink_context"] = backlinks[:3]  # Top 3 backlinks
        return results
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract entities from query"""
        # Simple implementation - can be enhanced with NER
        return [word for word in query.split() if word.istitle()]
    
    def _extract_related_concepts(self, history: List[str]) -> List[str]:
        """Extract related concepts from query history"""
        concepts = []
        for query in history[-3:]:  # Last 3 queries
            concepts.extend(self._extract_entities(query))
        return list(set(concepts))
    
    def _add_temporal_context(self, query: str) -> str:
        """Add temporal context to query"""
        temporal_terms = ["recent", "latest", "new", "today", "yesterday"]
        if any(term in query.lower() for term in temporal_terms):
            return f"date:{datetime.now().strftime('%Y-%m-%d')}"
        return ""
    
    async def _get_linked_documents(self, doc_id: str) -> List[Dict]:
        """Get documents linked to the given document"""
        # Placeholder - implement based on your link structure
        return []
    
    async def _get_backlinks(self, doc_id: str) -> List[Dict]:
        """Get documents that link to the given document"""
        # Placeholder - implement based on your backlink structure
        return []
    
    def _get_document_by_id(self, doc_id: str) -> Dict:
        """Retrieve full document by ID"""
        # Placeholder - implement based on your document storage
        return {"id": doc_id, "content": "Document content", "metadata": {}}

# Global instance
enhanced_rag = AdvancedRAGEngine()
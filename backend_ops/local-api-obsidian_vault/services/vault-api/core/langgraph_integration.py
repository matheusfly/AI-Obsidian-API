"""LangGraph Integration for Advanced Workflow Management"""
from typing import Dict, List, Any, TypedDict
import asyncio
from datetime import datetime
from .enhanced_rag import enhanced_rag
from .supabase_client import supabase_client

class ObsidianRAGState(TypedDict):
    query: str
    expanded_query: str
    context: List[Dict]
    answer: str
    search_depth: int
    relevant_notes: List[str]
    query_history: List[str]
    relevance_score: float
    needs_revision: bool
    agent_id: str
    performance_metrics: Dict[str, Any]

class LangGraphWorkflow:
    def __init__(self):
        self.rag_engine = enhanced_rag
        self.supabase = supabase_client
        
    async def query_expansion_node(self, state: ObsidianRAGState) -> Dict:
        """Enhanced query expansion with context awareness"""
        try:
            # Get agent context for personalization
            agent_context = await self.supabase.get_agent_context(state["agent_id"])
            
            # Adaptive query expansion
            expanded = await self.rag_engine.adaptive_query_expansion(
                state["query"], 
                state.get("query_history", [])
            )
            
            # Log expansion for analytics
            await self.supabase.log_agent_interaction(
                state["agent_id"], 
                "query_expansion", 
                {"original": state["query"], "expanded": expanded}
            )
            
            return {
                "expanded_query": expanded,
                "query_history": state.get("query_history", []) + [expanded],
                "search_depth": state.get("search_depth", 0) + 1
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def hierarchical_retrieval_node(self, state: ObsidianRAGState) -> Dict:
        """Multi-level retrieval with performance tracking"""
        start_time = datetime.utcnow()
        
        try:
            # Perform hierarchical retrieval
            results = await self.rag_engine.hierarchical_retrieval(
                state["expanded_query"],
                state["agent_id"],
                depth=3
            )
            
            # Calculate performance metrics
            end_time = datetime.utcnow()
            retrieval_time = (end_time - start_time).total_seconds()
            
            performance_metrics = {
                "retrieval_time": retrieval_time,
                "results_count": len(results.get("results", [])),
                "context_quality": results.get("metadata", {}).get("context_quality", 0)
            }
            
            return {
                "context": results.get("results", []),
                "relevant_notes": [r.get("metadata", {}).get("path", "") for r in results.get("results", [])],
                "performance_metrics": performance_metrics
            }
            
        except Exception as e:
            return {"error": str(e), "context": []}
    
    async def answer_generation_node(self, state: ObsidianRAGState) -> Dict:
        """Generate contextual answer with citations"""
        try:
            # Format context for generation
            formatted_context = self._format_context_for_generation(state["context"])
            
            # Generate answer (placeholder - integrate with your LLM)
            answer = await self._generate_answer_with_citations(
                state["query"],
                formatted_context
            )
            
            # Log generation
            await self.supabase.log_agent_interaction(
                state["agent_id"],
                "answer_generation",
                {
                    "query": state["query"],
                    "context_chunks": len(state["context"]),
                    "answer_length": len(answer)
                }
            )
            
            return {"answer": answer}
            
        except Exception as e:
            return {"error": str(e), "answer": ""}
    
    async def relevance_evaluation_node(self, state: ObsidianRAGState) -> Dict:
        """Evaluate answer relevance and determine next steps"""
        try:
            # Calculate relevance metrics
            relevance_score = await self._calculate_relevance(
                state["query"],
                state["context"],
                state["answer"]
            )
            
            # Determine if revision is needed
            needs_revision = (
                relevance_score < 0.7 or 
                state["search_depth"] < 2 or
                len(state["context"]) < 3
            )
            
            # Store evaluation results
            await self.supabase.log_agent_interaction(
                state["agent_id"],
                "relevance_evaluation",
                {
                    "relevance_score": relevance_score,
                    "needs_revision": needs_revision,
                    "search_depth": state["search_depth"]
                }
            )
            
            return {
                "relevance_score": relevance_score,
                "needs_revision": needs_revision and state["search_depth"] < 3
            }
            
        except Exception as e:
            return {"error": str(e), "needs_revision": False}
    
    def should_continue(self, state: ObsidianRAGState) -> str:
        """Determine workflow continuation logic"""
        if state.get("error"):
            return "END"
        if state["search_depth"] >= 3:
            return "END"
        if not state.get("needs_revision", False):
            return "END"
        return "query_expansion"
    
    async def _generate_answer_with_citations(self, query: str, context: str) -> str:
        """Generate answer with Obsidian-style citations"""
        # Placeholder implementation
        return f"Based on your notes: {context[:200]}... [[Note Reference]]"
    
    async def _calculate_relevance(self, query: str, context: List[Dict], answer: str) -> float:
        """Calculate answer relevance score"""
        # Simple heuristic - can be enhanced with ML models
        if not context or not answer:
            return 0.0
        
        # Check if answer references context
        context_terms = set()
        for ctx in context:
            context_terms.update(ctx.get("content", "").lower().split())
        
        answer_terms = set(answer.lower().split())
        overlap = len(context_terms.intersection(answer_terms))
        
        return min(overlap / max(len(context_terms), 1), 1.0)
    
    def _format_context_for_generation(self, context: List[Dict]) -> str:
        """Format retrieved context for answer generation"""
        formatted = []
        for i, ctx in enumerate(context[:5]):  # Top 5 results
            content = ctx.get("content", "")[:300]  # Truncate for efficiency
            metadata = ctx.get("metadata", {})
            path = metadata.get("path", f"Document {i+1}")
            
            formatted.append(f"[[{path}]]: {content}")
        
        return "\n\n".join(formatted)

# Global workflow instance
langgraph_workflow = LangGraphWorkflow()
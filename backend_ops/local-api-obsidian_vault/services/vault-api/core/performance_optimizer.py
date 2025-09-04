"""Performance Optimization Engine for RAG Operations"""
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json
from .supabase_client import supabase_client

class PerformanceOptimizer:
    def __init__(self):
        self.supabase = supabase_client
        self.cache = {}
        self.performance_metrics = {}
        
    async def intelligent_caching(self, query: str, agent_id: str, ttl_hours: int = 6) -> Optional[Dict]:
        """Intelligent caching with context awareness"""
        # Generate cache key with context
        cache_key = self._generate_cache_key(query, agent_id)
        
        # Check memory cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if self._is_cache_valid(cached_data, ttl_hours):
                await self._log_cache_hit(agent_id, "memory")
                return cached_data["data"]
        
        # Check Supabase cache
        supabase_cache = await self.supabase.get_cached_retrieval(cache_key, ttl_hours)
        if supabase_cache["success"]:
            # Store in memory for faster access
            self.cache[cache_key] = {
                "data": supabase_cache["data"],
                "timestamp": datetime.utcnow(),
                "access_count": 1
            }
            await self._log_cache_hit(agent_id, "supabase")
            return supabase_cache["data"]
        
        return None
    
    async def batch_processing(self, queries: List[str], agent_id: str, batch_size: int = 5) -> List[Dict]:
        """Process multiple queries in optimized batches"""
        results = []
        
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i + batch_size]
            
            # Process batch concurrently
            batch_tasks = [
                self._process_single_query(query, agent_id) 
                for query in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Filter successful results
            for result in batch_results:
                if isinstance(result, dict) and result.get("success"):
                    results.append(result)
            
            # Rate limiting between batches
            if i + batch_size < len(queries):
                await asyncio.sleep(0.1)
        
        return results
    
    async def adaptive_chunking(self, content: str, complexity_score: float) -> List[Dict]:
        """Adaptive chunking based on content complexity"""
        # Adjust chunk size based on complexity
        if complexity_score > 0.8:
            max_tokens = 200  # Smaller chunks for complex content
        elif complexity_score > 0.5:
            max_tokens = 350  # Medium chunks
        else:
            max_tokens = 500  # Larger chunks for simple content
        
        chunks = []
        current_chunk = ""
        current_complexity = 0
        
        sentences = content.split('. ')
        
        for sentence in sentences:
            sentence_complexity = self._calculate_sentence_complexity(sentence)
            
            # Check if adding sentence would exceed limits
            if (len(current_chunk) + len(sentence) > max_tokens or 
                current_complexity + sentence_complexity > 1.0):
                
                if current_chunk:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "complexity": current_complexity,
                        "token_count": len(current_chunk.split())
                    })
                
                current_chunk = sentence + '. '
                current_complexity = sentence_complexity
            else:
                current_chunk += sentence + '. '
                current_complexity = max(current_complexity, sentence_complexity)
        
        if current_chunk:
            chunks.append({
                "content": current_chunk.strip(),
                "complexity": current_complexity,
                "token_count": len(current_chunk.split())
            })
        
        return chunks
    
    async def query_optimization(self, query: str, performance_history: List[Dict]) -> str:
        """Optimize query based on performance history"""
        # Analyze successful query patterns
        successful_patterns = [
            h["query"] for h in performance_history 
            if h.get("relevance_score", 0) > 0.8
        ]
        
        # Extract successful terms
        successful_terms = set()
        for pattern in successful_patterns:
            successful_terms.update(pattern.lower().split())
        
        # Enhance query with successful terms
        query_terms = set(query.lower().split())
        enhancement_terms = successful_terms.intersection(query_terms)
        
        if enhancement_terms:
            enhanced_query = f"{query} {' '.join(enhancement_terms)}"
            return enhanced_query
        
        return query
    
    async def resource_monitoring(self) -> Dict[str, Any]:
        """Monitor system resources and performance"""
        import psutil
        
        # CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Cache statistics
        cache_stats = {
            "memory_cache_size": len(self.cache),
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "avg_response_time": self._calculate_avg_response_time()
        }
        
        # Performance recommendations
        recommendations = []
        if cpu_percent > 80:
            recommendations.append("Consider reducing batch size")
        if memory.percent > 85:
            recommendations.append("Clear memory cache")
        if cache_stats["cache_hit_rate"] < 0.3:
            recommendations.append("Increase cache TTL")
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "cache_stats": cache_stats,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def auto_scaling_logic(self, current_load: float) -> Dict[str, Any]:
        """Determine optimal scaling parameters based on load"""
        if current_load > 0.8:
            return {
                "batch_size": 3,
                "cache_ttl": 12,  # Longer cache for high load
                "concurrent_requests": 2,
                "recommendation": "scale_up"
            }
        elif current_load > 0.5:
            return {
                "batch_size": 5,
                "cache_ttl": 6,
                "concurrent_requests": 5,
                "recommendation": "maintain"
            }
        else:
            return {
                "batch_size": 8,
                "cache_ttl": 3,  # Shorter cache for fresh results
                "concurrent_requests": 10,
                "recommendation": "scale_down"
            }
    
    def _generate_cache_key(self, query: str, agent_id: str) -> str:
        """Generate unique cache key"""
        combined = f"{query}_{agent_id}_{datetime.now().strftime('%Y-%m-%d-%H')}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _is_cache_valid(self, cached_data: Dict, ttl_hours: int) -> bool:
        """Check if cached data is still valid"""
        timestamp = cached_data.get("timestamp")
        if not timestamp:
            return False
        
        age = datetime.utcnow() - timestamp
        return age < timedelta(hours=ttl_hours)
    
    async def _log_cache_hit(self, agent_id: str, cache_type: str):
        """Log cache hit for analytics"""
        await self.supabase.log_agent_interaction(
            agent_id,
            "cache_hit",
            {"cache_type": cache_type, "timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _process_single_query(self, query: str, agent_id: str) -> Dict:
        """Process a single query with error handling"""
        try:
            start_time = time.time()
            
            # Placeholder for actual query processing
            result = {"success": True, "query": query, "results": []}
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Store performance metrics
            self.performance_metrics[query] = {
                "processing_time": processing_time,
                "timestamp": datetime.utcnow(),
                "agent_id": agent_id
            }
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "query": query}
    
    def _calculate_sentence_complexity(self, sentence: str) -> float:
        """Calculate complexity score for a sentence"""
        # Simple heuristic based on length and punctuation
        word_count = len(sentence.split())
        punctuation_count = sum(1 for char in sentence if char in '.,;:!?')
        
        # Normalize to 0-1 scale
        complexity = min((word_count / 20) + (punctuation_count / 10), 1.0)
        return complexity
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if not hasattr(self, '_cache_hits'):
            self._cache_hits = 0
        if not hasattr(self, '_total_requests'):
            self._total_requests = 0
        
        if self._total_requests == 0:
            return 0.0
        
        return self._cache_hits / self._total_requests
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        if not self.performance_metrics:
            return 0.0
        
        times = [m["processing_time"] for m in self.performance_metrics.values()]
        return sum(times) / len(times)

# Global optimizer instance
performance_optimizer = PerformanceOptimizer()
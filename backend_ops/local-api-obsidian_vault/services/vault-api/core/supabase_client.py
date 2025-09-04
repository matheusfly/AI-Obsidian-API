"""Supabase client for AI agent retrieval logic (lazy + fault-tolerant)"""
import os
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.client = None  # created lazily
        self._init_error: Optional[str] = None

    def _ensure_client(self):
        if self.client or self._init_error:
            return
        if not self.url or not self.key:
            self._init_error = "Supabase not configured"
            return
        try:
            # Lazy import to avoid import-time crashes if deps are incompatible
            from supabase import create_client
            self.client = create_client(self.url, self.key)
        except Exception as e:
            self._init_error = str(e)

    def is_available(self) -> bool:
        self._ensure_client()
        return self.client is not None

    async def store_agent_context(self, agent_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Store AI agent context for retrieval"""
        self._ensure_client()
        if not self.client:
            return {"success": False, "error": self._init_error or "Supabase client unavailable"}
        try:
            data = {
                "agent_id": agent_id,
                "context": json.dumps(context),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            result = self.client.table("agent_contexts").upsert(data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_agent_context(self, agent_id: str) -> Dict[str, Any]:
        """Retrieve AI agent context"""
        self._ensure_client()
        if not self.client:
            return {"success": False, "error": self._init_error or "Supabase client unavailable"}
        try:
            result = self.client.table("agent_contexts").select("*").eq("agent_id", agent_id).execute()
            if result.data:
                context_data = result.data[0]
                context_data["context"] = json.loads(context_data.get("context", "{}"))
                return {"success": True, "data": context_data}
            else:
                return {"success": False, "error": "Agent context not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def store_retrieval_result(self, query: str, results: List[Dict], metadata: Dict = None) -> Dict[str, Any]:
        """Store retrieval results for caching"""
        self._ensure_client()
        if not self.client:
            return {"success": False, "error": self._init_error or "Supabase client unavailable"}
        try:
            data = {
                "query": query,
                "results": json.dumps(results),
                "metadata": json.dumps(metadata or {}),
                "created_at": datetime.utcnow().isoformat()
            }
            result = self.client.table("retrieval_cache").insert(data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_cached_retrieval(self, query: str, max_age_hours: int = 24) -> Dict[str, Any]:
        """Get cached retrieval results"""
        self._ensure_client()
        if not self.client:
            return {"success": False, "error": self._init_error or "Supabase client unavailable"}
        try:
            # Simple lookup by query (age filter omitted for simplicity to avoid tz issues)
            result = self.client.table("retrieval_cache").select("*").eq("query", query).order("created_at", desc=True).limit(1).execute()
            if result.data:
                cache_data = result.data[0]
                cache_data["results"] = json.loads(cache_data.get("results", "[]"))
                cache_data["metadata"] = json.loads(cache_data.get("metadata", "{}"))
                return {"success": True, "data": cache_data}
            else:
                return {"success": False, "error": "No cached results found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def log_agent_interaction(self, agent_id: str, interaction_type: str, data: Dict) -> Dict[str, Any]:
        """Log agent interactions for analytics"""
        self._ensure_client()
        if not self.client:
            return {"success": False, "error": self._init_error or "Supabase client unavailable"}
        try:
            log_data = {
                "agent_id": agent_id,
                "interaction_type": interaction_type,
                "data": json.dumps(data),
                "timestamp": datetime.utcnow().isoformat()
            }
            result = self.client.table("agent_logs").insert(log_data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global instance (lazy-initialized internally)
supabase_client = SupabaseClient()

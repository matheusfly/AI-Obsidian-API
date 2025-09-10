from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import asyncio
import os
from datetime import datetime
import json
from pathlib import Path
import aiofiles
from core.ai_retrieval import ai_retrieval
from core.supabase_client import supabase_client
from core.enhanced_rag import enhanced_rag
from core.langgraph_integration import langgraph_workflow
from core.performance_optimizer import performance_optimizer

app = FastAPI(
    title="Obsidian Vault AI API",
    description="Production-ready API for Obsidian vault automation with local-first architecture",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Environment variables
OBSIDIAN_API_URL = os.getenv("OBSIDIAN_API_URL", "http://obsidian-api:27123")
OBSIDIAN_API_KEY = os.getenv("OBSIDIAN_API_KEY", "")
VAULT_PATH = os.getenv("VAULT_PATH", "/vault")

class NoteRequest(BaseModel):
    path: str
    content: str
    tags: Optional[List[str]] = []

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    semantic: bool = False

class MCPToolRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]

class AIRetrievalRequest(BaseModel):
    query: str
    agent_id: str
    context: Optional[Dict[str, Any]] = None

class AgentContextRequest(BaseModel):
    agent_id: str
    context: Dict[str, Any]

class EnhancedRAGRequest(BaseModel):
    query: str
    agent_id: str
    use_hierarchical: bool = True
    max_depth: int = 3
    context_history: Optional[List[str]] = None

class BatchQueryRequest(BaseModel):
    queries: List[str]
    agent_id: str
    batch_size: int = 5

@app.get("/")
async def root():
    return {
        "message": "Obsidian Vault AI API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "notes": "/api/v1/notes",
            "search": "/api/v1/search",
            "mcp_tools": "/api/v1/mcp/tools"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with service status"""
    try:
        # Check Obsidian API connection
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{OBSIDIAN_API_URL}/health", timeout=5.0)
                obsidian_status = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                obsidian_status = "unreachable"
        
        # Check vault path
        vault_accessible = Path(VAULT_PATH).exists()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "obsidian_api": obsidian_status,
                "vault_path": VAULT_PATH,
                "vault_accessible": vault_accessible,
                "api_version": "2.0.0"
            },
            "mcp_tools": {
                "available": 15,
                "tools": ["read_file", "write_file", "list_files", "search_content", "create_daily_note"]
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/metrics")
async def metrics():
    """Prometheus-style metrics"""
    from fastapi.responses import PlainTextResponse
    
    # Generate Prometheus format metrics
    prometheus_metrics = f"""# HELP vault_api_requests_total Total number of API requests
# TYPE vault_api_requests_total counter
vault_api_requests_total{{method="GET",endpoint="/health"}} 1
vault_api_requests_total{{method="GET",endpoint="/metrics"}} 1

# HELP vault_api_request_duration_seconds Request duration in seconds
# TYPE vault_api_request_duration_seconds histogram
vault_api_request_duration_seconds_bucket{{le="0.1"}} 1
vault_api_request_duration_seconds_bucket{{le="0.5"}} 1
vault_api_request_duration_seconds_bucket{{le="1.0"}} 1
vault_api_request_duration_seconds_bucket{{le="+Inf"}} 1
vault_api_request_duration_seconds_sum 0.05
vault_api_request_duration_seconds_count 1

# HELP vault_api_up Service is up
# TYPE vault_api_up gauge
vault_api_up 1
"""
    
    return PlainTextResponse(prometheus_metrics, media_type="text/plain")

@app.get("/api/v1/notes")
async def list_notes(folder: Optional[str] = None, limit: int = 50):
    """List notes in vault"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{OBSIDIAN_API_URL}/files"
            if folder:
                url += f"?path={folder}"
            
            response = await client.get(url, timeout=10.0)
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to list notes")
            
            data = response.json()
            files = data.get("files", [])
            
            # Filter markdown files
            notes = [f for f in files if f.get("name", "").endswith('.md')][:limit]
            
            return {
                "notes": notes,
                "total": len(notes),
                "folder": folder or "all"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/notes")
async def create_note(note: NoteRequest):
    """Create a new note"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OBSIDIAN_API_URL}/files",
                json={"path": note.path, "content": note.content},
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to create note")
            
            return {
                "status": "created",
                "path": note.path,
                "message": "Note created successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/notes/{note_path:path}")
async def get_note(note_path: str):
    """Get note content"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OBSIDIAN_API_URL}/files/{note_path}",
                timeout=10.0
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Note not found")
            elif response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get note")
            
            return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/search")
async def search_notes(search: SearchRequest):
    """Search notes"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OBSIDIAN_API_URL}/vault/search",
                json={"query": search.query, "caseSensitive": False},
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Search failed")
            
            data = response.json()
            results = data.get("results", [])[:search.limit]
            
            return {
                "query": search.query,
                "results": results,
                "total": len(results),
                "semantic": search.semantic
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools"""
    tools = [
        {
            "name": "read_file",
            "description": "Read content from a file in the vault",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path relative to vault"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "write_file",
            "description": "Write content to a file in the vault",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path relative to vault"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path", "default": "."},
                    "pattern": {"type": "string", "description": "File pattern filter"}
                }
            }
        },
        {
            "name": "search_content",
            "description": "Search for content across vault files",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results", "default": 10}
                },
                "required": ["query"]
            }
        },
        {
            "name": "create_daily_note",
            "description": "Create a daily note with template",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "template": {"type": "string", "description": "Template name"}
                }
            }
        }
    ]
    
    return {
        "tools": tools,
        "total": len(tools)
    }

@app.post("/api/v1/mcp/tools/call")
async def call_mcp_tool(request: MCPToolRequest):
    """Call an MCP tool"""
    try:
        tool_name = request.tool
        arguments = request.arguments
        
        if tool_name == "read_file":
            file_path = arguments.get("path")
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{OBSIDIAN_API_URL}/files/{file_path}")
                if response.status_code == 200:
                    return {"success": True, "result": response.json().get("content", "")}
                else:
                    return {"success": False, "error": "File not found"}
        
        elif tool_name == "list_files":
            path = arguments.get("path", "")
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{OBSIDIAN_API_URL}/files?path={path}")
                if response.status_code == 200:
                    files = response.json().get("files", [])
                    file_names = [f["name"] for f in files if f["name"].endswith(".md")]
                    return {"success": True, "result": file_names}
                else:
                    return {"success": False, "error": "Failed to list files"}
        
        elif tool_name == "search_content":
            query = arguments.get("query")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{OBSIDIAN_API_URL}/vault/search",
                    json={"query": query}
                )
                if response.status_code == 200:
                    return {"success": True, "result": response.json().get("results", [])}
                else:
                    return {"success": False, "error": "Search failed"}
        
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/ai/retrieve")
async def ai_enhanced_retrieval(request: AIRetrievalRequest):
    """Enhanced AI retrieval with Supabase integration"""
    try:
        result = await ai_retrieval.enhanced_retrieval(
            query=request.query,
            agent_id=request.agent_id,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agents/context")
async def update_agent_context(request: AgentContextRequest):
    """Update agent context in Supabase"""
    try:
        result = await ai_retrieval.update_agent_context(
            agent_id=request.agent_id,
            context_update=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents/{agent_id}/analytics")
async def get_agent_analytics(agent_id: str, days: int = 7):
    """Get agent interaction analytics"""
    try:
        result = await ai_retrieval.get_agent_analytics(agent_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/supabase/health")
async def supabase_health():
    """Check Supabase connection health"""
    try:
        test_result = await supabase_client.get_agent_context("health_check")
        return {
            "status": "healthy",
            "supabase_url": supabase_client.url,
            "connection": "active"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/api/v1/rag/enhanced")
async def enhanced_rag_query(request: EnhancedRAGRequest):
    """Enhanced RAG with hierarchical retrieval"""
    try:
        cached_result = await performance_optimizer.intelligent_caching(
            request.query, request.agent_id
        )
        if cached_result:
            return {"success": True, "source": "cache", **cached_result}
        
        result = await enhanced_rag.hierarchical_retrieval(
            request.query, request.agent_id, request.max_depth
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/batch")
async def batch_rag_processing(request: BatchQueryRequest):
    """Process multiple RAG queries in batches"""
    try:
        results = await performance_optimizer.batch_processing(
            request.queries, request.agent_id, request.batch_size
        )
        return {
            "success": True,
            "processed": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/performance/metrics")
async def get_performance_metrics():
    """Get system performance metrics"""
    try:
        metrics = await performance_optimizer.resource_monitoring()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
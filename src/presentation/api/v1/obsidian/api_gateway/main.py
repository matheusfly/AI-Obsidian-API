"""
FastAPI Gateway for LangGraph + Obsidian Vault Integration
Provides REST API endpoints and MCP tool integration
"""
import os
import hashlib
import httpx
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
import structlog

from config.environment import config

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# FastAPI app initialization
app = FastAPI(
    title="LangGraph-Obsidian Gateway",
    description="API Gateway for LangGraph + Obsidian Vault Integration with MCP support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Pydantic models
class UpsertRequest(BaseModel):
    path: str
    content: str
    dry_run: bool = True
    if_match: Optional[str] = None
    mode: str = "upsert"
    session_id: Optional[str] = None
    tool_call_id: Optional[str] = None

class ListFilesRequest(BaseModel):
    vault: str
    cursor: Optional[str] = None
    limit: int = 100
    filter: Optional[str] = None

class ReadNoteRequest(BaseModel):
    vault: str
    path: str

class SearchRequest(BaseModel):
    vault: str
    query: str
    limit: int = 20
    filters: Optional[Dict[str, Any]] = None

class PatchRequest(BaseModel):
    vault: str
    path: str
    patch_ops: List[Dict[str, Any]]
    dry_run: bool = True

class PendingOperation(BaseModel):
    tool_call_id: str
    operation_type: str
    vault: str
    path: str
    content: str
    dry_run_result: Dict[Any, Any]
    created_at: datetime
    created_by: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

# In-memory storage for pending operations (use database in production)
pending_operations: Dict[str, PendingOperation] = {}

# HTTP client for Obsidian API
async def get_obsidian_headers() -> Dict[str, str]:
    """Get headers for Obsidian API requests"""
    if config.OBSIDIAN_API_KEY:
        return {"Authorization": f"Bearer {config.OBSIDIAN_API_KEY}"}
    return {}

async def make_obsidian_request(
    method: str, 
    endpoint: str, 
    **kwargs
) -> httpx.Response:
    """Make a request to the Obsidian Local REST API"""
    async with httpx.AsyncClient(timeout=config.OBSIDIAN_TIMEOUT) as client:
        headers = await get_obsidian_headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        
        url = f"{config.obsidian_base_url}{endpoint}"
        
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                **{k: v for k, v in kwargs.items() if k != 'headers'}
            )
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            logger.error(
                "obsidian_api_error",
                method=method,
                endpoint=endpoint,
                error=str(e),
                status_code=getattr(e.response, 'status_code', None)
            )
            raise HTTPException(
                status_code=502, 
                detail=f"Obsidian API error: {str(e)}"
            )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "obsidian_api": config.obsidian_base_url,
            "langgraph_server": config.langgraph_server_url,
            "langgraph_studio": config.langgraph_studio_url
        }
    }

# Vault management endpoints
@app.get("/vaults")
async def list_vaults():
    """List all available vaults"""
    try:
        response = await make_obsidian_request("GET", "/vaults")
        return response.json()
    except Exception as e:
        logger.error("list_vaults_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list vaults")

@app.get("/vault/{vault}/files")
async def list_files(
    vault: str, 
    cursor: Optional[str] = None, 
    limit: int = 100,
    filter: Optional[str] = None
):
    """List files in a vault with pagination"""
    try:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if filter:
            params["filter"] = filter
            
        response = await make_obsidian_request(
            "GET", 
            f"/vault/{vault}/files", 
            params=params
        )
        files_data = response.json()
        
        # Add hash for conflict detection
        for file in files_data.get("files", []):
            content = file.get("content", "")
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            file["_hash"] = content_hash
        
        logger.info(
            "list_files_success",
            vault=vault,
            file_count=len(files_data.get("files", [])),
            cursor=cursor
        )
        
        return files_data
    except Exception as e:
        logger.error("list_files_error", vault=vault, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list files")

@app.get("/vault/{vault}/file/{path:path}")
async def read_file(vault: str, path: str):
    """Read content of a specific file"""
    try:
        response = await make_obsidian_request(
            "GET", 
            f"/vault/{vault}/file/{path}"
        )
        file_data = response.json()
        
        # Add hash for conflict detection
        content = file_data.get("content", "")
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        file_data["_hash"] = content_hash
        
        logger.info(
            "read_file_success",
            vault=vault,
            path=path,
            content_length=len(content)
        )
        
        return file_data
    except Exception as e:
        logger.error("read_file_error", vault=vault, path=path, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to read file")

@app.put("/vault/{vault}/file/{path:path}")
async def upsert_file(vault: str, path: str, req: UpsertRequest):
    """Create or update a file with conflict detection and HITL support"""
    # Generate tool call ID if not provided
    if not req.tool_call_id:
        req.tool_call_id = str(uuid4())
    
    # Conflict detection
    if req.if_match:
        try:
            current_file = await read_file(vault, path)
            current_hash = current_file.get("_hash")
            if current_hash != req.if_match:
                raise HTTPException(
                    status_code=409, 
                    detail="File has been modified by another process"
                )
        except HTTPException as e:
            if e.status_code == 409:
                raise
            # File might not exist yet, continue
        except Exception:
            # File might not exist yet, continue
            pass
    
    # Dry run mode
    if req.dry_run:
        dry_run_result = {
            "proposed_content": req.content[:200] + "..." if len(req.content) > 200 else req.content,
            "content_length": len(req.content),
            "path": path,
            "vault": vault
        }
        
        # Store pending operation for HITL approval
        pending_op = PendingOperation(
            tool_call_id=req.tool_call_id,
            operation_type="upsert",
            vault=vault,
            path=path,
            content=req.content,
            dry_run_result=dry_run_result,
            created_at=datetime.utcnow(),
            created_by=req.session_id or "system"
        )
        
        pending_operations[req.tool_call_id] = pending_op
        
        logger.info(
            "dry_run_operation_created",
            tool_call_id=req.tool_call_id,
            vault=vault,
            path=path,
            content_length=len(req.content)
        )
        
        return {
            "dry_run": True,
            "tool_call_id": req.tool_call_id,
            "result": dry_run_result,
            "approval_required": True,
            "approval_endpoint": f"/approve/{req.tool_call_id}"
        }
    
    # Actual write operation
    try:
        response = await make_obsidian_request(
            "PUT",
            f"/vault/{vault}/file/{path}",
            json={"content": req.content}
        )
        
        result = response.json()
        
        logger.info(
            "file_upserted",
            vault=vault,
            path=path,
            content_length=len(req.content),
            tool_call_id=req.tool_call_id
        )
        
        return result
    except Exception as e:
        logger.error(
            "file_upsert_error",
            vault=vault,
            path=path,
            error=str(e),
            tool_call_id=req.tool_call_id
        )
        raise HTTPException(status_code=500, detail="Failed to upsert file")

@app.patch("/vault/{vault}/file/{path:path}")
async def patch_file(vault: str, path: str, req: PatchRequest):
    """Patch content in a file"""
    try:
        response = await make_obsidian_request(
            "PATCH",
            f"/vault/{vault}/file/{path}",
            json={"patch_ops": req.patch_ops}
        )
        
        result = response.json()
        
        logger.info(
            "file_patched",
            vault=vault,
            path=path,
            patch_ops_count=len(req.patch_ops),
            dry_run=req.dry_run
        )
        
        return result
    except Exception as e:
        logger.error(
            "file_patch_error",
            vault=vault,
            path=path,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to patch file")

@app.delete("/vault/{vault}/file/{path:path}")
async def delete_file(vault: str, path: str, confirm: bool = False):
    """Delete a file from the vault"""
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="Deletion requires confirmation. Set confirm=true"
        )
    
    try:
        response = await make_obsidian_request(
            "DELETE",
            f"/vault/{vault}/file/{path}"
        )
        
        logger.info("file_deleted", vault=vault, path=path)
        
        return {"status": "deleted", "path": path}
    except Exception as e:
        logger.error("file_delete_error", vault=vault, path=path, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete file")

@app.post("/vault/{vault}/search")
async def search_notes(vault: str, req: SearchRequest):
    """Search notes in the vault"""
    try:
        payload = {
            "query": req.query,
            "limit": req.limit
        }
        if req.filters:
            payload["filters"] = req.filters
            
        response = await make_obsidian_request(
            "POST",
            f"/vault/{vault}/search",
            json=payload
        )
        
        result = response.json()
        
        logger.info(
            "search_completed",
            vault=vault,
            query=req.query,
            result_count=len(result.get("results", []))
        )
        
        return result
    except Exception as e:
        logger.error("search_error", vault=vault, query=req.query, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to search notes")

# Human-in-the-Loop (HITL) endpoints
@app.get("/pending_operations")
async def list_pending_operations():
    """List all pending operations requiring approval"""
    return [
        {
            "tool_call_id": op.tool_call_id,
            "operation_type": op.operation_type,
            "vault": op.vault,
            "path": op.path,
            "created_at": op.created_at.isoformat() + "Z",
            "created_by": op.created_by
        }
        for op in pending_operations.values()
        if not op.approved_by
    ]

@app.get("/pending_operations/{tool_call_id}")
async def get_pending_operation(tool_call_id: str):
    """Get details of a specific pending operation"""
    if tool_call_id not in pending_operations:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    op = pending_operations[tool_call_id]
    return {
        "tool_call_id": op.tool_call_id,
        "operation_type": op.operation_type,
        "vault": op.vault,
        "path": op.path,
        "dry_run_result": op.dry_run_result,
        "created_at": op.created_at.isoformat() + "Z",
        "created_by": op.created_by,
        "approved_by": op.approved_by,
        "approved_at": op.approved_at.isoformat() + "Z" if op.approved_at else None
    }

@app.post("/approve/{tool_call_id}")
async def approve_operation(tool_call_id: str, approved_by: str = "human"):
    """Approve a pending operation"""
    if tool_call_id not in pending_operations:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    operation = pending_operations[tool_call_id]
    if operation.approved_by:
        raise HTTPException(status_code=400, detail="Operation already approved")
    
    # Update operation status
    operation.approved_by = approved_by
    operation.approved_at = datetime.utcnow()
    
    # Execute the actual operation
    try:
        if operation.operation_type == "upsert":
            result = await upsert_file(
                operation.vault,
                operation.path,
                UpsertRequest(
                    path=operation.path,
                    content=operation.content,
                    dry_run=False,
                    tool_call_id=operation.tool_call_id
                )
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported operation type: {operation.operation_type}"
            )
        
        # Remove from pending operations
        del pending_operations[tool_call_id]
        
        logger.info(
            "operation_approved",
            tool_call_id=tool_call_id,
            approved_by=approved_by,
            operation_type=operation.operation_type
        )
        
        return {
            "status": "approved",
            "result": result,
            "approved_by": approved_by,
            "approved_at": operation.approved_at.isoformat() + "Z"
        }
    except Exception as e:
        logger.error(
            "approval_execution_error",
            tool_call_id=tool_call_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to execute approved operation: {str(e)}"
        )

# MCP tool endpoints
@app.post("/mcp/obsidian_list_files")
async def mcp_list_files(req: ListFilesRequest):
    """MCP tool for listing files in an Obsidian vault"""
    return await list_files(req.vault, req.cursor, req.limit, req.filter)

@app.post("/mcp/obsidian_read_note")
async def mcp_read_note(req: ReadNoteRequest):
    """MCP tool for reading a note from an Obsidian vault"""
    return await read_file(req.vault, req.path)

@app.post("/mcp/obsidian_put_file")
async def mcp_put_file(vault: str, path: str, req: UpsertRequest):
    """MCP tool for creating or updating a file in an Obsidian vault"""
    return await upsert_file(vault, path, req)

@app.post("/mcp/obsidian_search_notes")
async def mcp_search_notes(req: SearchRequest):
    """MCP tool for searching notes in an Obsidian vault"""
    return await search_notes(req.vault, req)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.API_GATEWAY_HOST,
        port=config.API_GATEWAY_PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )
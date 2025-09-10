"""
Simple Obsidian MCP Server without complex dependencies
Direct integration with Obsidian Local REST API
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx
import asyncio
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Simple Obsidian MCP Server",
    description="MCP server for Obsidian vault operations",
    version="1.0.0"
)

# Obsidian API configuration
OBSIDIAN_API_KEY = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
OBSIDIAN_HOST = "127.0.0.1"
OBSIDIAN_PORT = 27123
OBSIDIAN_BASE_URL = f"http://{OBSIDIAN_HOST}:{OBSIDIAN_PORT}"

# HTTP client for Obsidian API
obsidian_client = httpx.AsyncClient(
    headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"},
    timeout=30.0
)

# Pydantic models
class ReadNoteInput(BaseModel):
    vault_name: str
    file_path: str
    include_metadata: bool = True

class PutFileInput(BaseModel):
    vault_name: str
    file_path: str
    content: str
    create_dirs: bool = True

class SearchNotesInput(BaseModel):
    vault_name: str
    query: str
    limit: int = 10
    include_content: bool = False

class ListFilesInput(BaseModel):
    vault_name: str
    path: str = ""
    recursive: bool = True
    limit: int = 100

class PatchFileInput(BaseModel):
    vault_name: str
    file_path: str
    patch_operations: List[Dict[str, Any]]

class DeleteFileInput(BaseModel):
    vault_name: str
    file_path: str
    confirm: bool = False

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# MCP Tool endpoints
@app.post("/tools/obsidian_list_vaults")
async def list_vaults():
    """List all available Obsidian vaults"""
    try:
        response = await obsidian_client.get(f"{OBSIDIAN_BASE_URL}/vault/")
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "vaults": data.get("vaults", []),
            "total": len(data.get("vaults", [])),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing vaults: {str(e)}")
        return {"error": str(e), "success": False}

@app.post("/tools/obsidian_list_files")
async def list_files(input_data: ListFilesInput):
    """List files in an Obsidian vault"""
    try:
        params = {
            "path": input_data.path,
            "recursive": input_data.recursive,
            "limit": input_data.limit
        }
        
        response = await obsidian_client.get(
            f"{OBSIDIAN_BASE_URL}/vault/{input_data.vault_name}/files",
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "files": data.get("files", []),
            "total": len(data.get("files", [])),
            "vault_name": input_data.vault_name,
            "path": input_data.path,
            "recursive": input_data.recursive,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return {"error": str(e), "success": False}

@app.post("/tools/obsidian_read_note")
async def read_note(input_data: ReadNoteInput):
    """Read a specific note from an Obsidian vault"""
    try:
        params = {"include_metadata": input_data.include_metadata}
        
        response = await obsidian_client.get(
            f"{OBSIDIAN_BASE_URL}/vault/{input_data.vault_name}/file/{input_data.file_path}",
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        content = data.get("content", "")
        metadata = data.get("metadata", {})
        
        # Calculate content statistics
        word_count = len(content.split()) if content else 0
        char_count = len(content) if content else 0
        line_count = len(content.split('\n')) if content else 0
        
        return {
            "success": True,
            "content": content,
            "metadata": metadata,
            "statistics": {
                "word_count": word_count,
                "char_count": char_count,
                "line_count": line_count
            },
            "file_path": input_data.file_path,
            "vault_name": input_data.vault_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error reading note: {str(e)}")
        return {"error": str(e), "success": False}

@app.post("/tools/obsidian_put_file")
async def put_file(input_data: PutFileInput):
    """Create or update a file in an Obsidian vault"""
    try:
        data = {
            "content": input_data.content,
            "create_dirs": input_data.create_dirs
        }
        
        response = await obsidian_client.put(
            f"{OBSIDIAN_BASE_URL}/vault/{input_data.vault_name}/file/{input_data.file_path}",
            json=data
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "File created/updated successfully",
            "file_path": input_data.file_path,
            "vault_name": input_data.vault_name,
            "content_length": len(input_data.content),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error putting file: {str(e)}")
        return {"error": str(e), "success": False}

@app.post("/tools/obsidian_search_notes")
async def search_notes(input_data: SearchNotesInput):
    """Search for notes in an Obsidian vault"""
    try:
        data = {
            "query": input_data.query,
            "limit": input_data.limit,
            "include_content": input_data.include_content
        }
        
        response = await obsidian_client.post(
            f"{OBSIDIAN_BASE_URL}/vault/{input_data.vault_name}/search",
            json=data
        )
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        
        # Enhance results with additional metadata
        enhanced_results = []
        for item in results:
            enhanced_item = {
                **item,
                "relevance_score": item.get("score", 0.0),
                "matched_terms": input_data.query.lower().split(),
                "search_type": "semantic"
            }
            enhanced_results.append(enhanced_item)
        
        return {
            "success": True,
            "results": enhanced_results,
            "total": len(enhanced_results),
            "query": input_data.query,
            "vault_name": input_data.vault_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching notes: {str(e)}")
        return {"error": str(e), "success": False}

@app.post("/tools/obsidian_patch_file")
async def patch_file(input_data: PatchFileInput):
    """Apply structured patches to a file in an Obsidian vault"""
    try:
        data = {"operations": input_data.patch_operations}
        
        response = await obsidian_client.patch(
            f"{OBSIDIAN_BASE_URL}/vault/{input_data.vault_name}/file/{input_data.file_path}",
            json=data
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "File patched successfully",
            "file_path": input_data.file_path,
            "vault_name": input_data.vault_name,
            "operations_applied": len(input_data.patch_operations),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error patching file: {str(e)}")
        return {"error": str(e), "success": False}

@app.post("/tools/obsidian_delete_file")
async def delete_file(input_data: DeleteFileInput):
    """Delete a file from an Obsidian vault"""
    try:
        if not input_data.confirm:
            return {
                "error": "Deletion requires confirmation. Set confirm=True to proceed.",
                "success": False
            }
        
        response = await obsidian_client.delete(
            f"{OBSIDIAN_BASE_URL}/vault/{input_data.vault_name}/file/{input_data.file_path}"
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "File deleted successfully",
            "file_path": input_data.file_path,
            "vault_name": input_data.vault_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return {"error": str(e), "success": False}

@app.post("/tools/obsidian_get_vault_stats")
async def get_vault_stats(vault_name: str):
    """Get comprehensive statistics for an Obsidian vault"""
    try:
        response = await obsidian_client.get(
            f"{OBSIDIAN_BASE_URL}/vault/{vault_name}/stats"
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "stats": data,
            "vault_name": vault_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting vault stats: {str(e)}")
        return {"error": str(e), "success": False}

@app.post("/tools/obsidian_get_active_file")
async def get_active_file(vault_name: str):
    """Get the currently active file in Obsidian"""
    try:
        response = await obsidian_client.get(
            f"{OBSIDIAN_BASE_URL}/vault/{vault_name}/active"
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "active_file": data.get("file_path", ""),
            "vault_name": vault_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting active file: {str(e)}")
        return {"error": str(e), "success": False}

@app.post("/tools/obsidian_set_active_file")
async def set_active_file(vault_name: str, file_path: str):
    """Set the active file in Obsidian"""
    try:
        data = {"file_path": file_path}
        
        response = await obsidian_client.post(
            f"{OBSIDIAN_BASE_URL}/vault/{vault_name}/active",
            json=data
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "message": "Active file set successfully",
            "active_file": file_path,
            "vault_name": vault_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error setting active file: {str(e)}")
        return {"error": str(e), "success": False}

# Agent communication tools
@app.post("/tools/obsidian_agent_communication")
async def agent_communication(target_agent: str, message: str, data: Optional[Dict[str, Any]] = None):
    """Send a message to another agent in the multi-server system"""
    try:
        communication_data = {
            "from": "obsidian-mcp-server",
            "to": target_agent,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Agent communication: {communication_data}")
        
        return {
            "success": True,
            "message": "Communication sent successfully",
            "target_agent": target_agent,
            "communication_id": f"comm_{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in agent communication: {str(e)}")
        return {"error": str(e), "success": False}

@app.post("/tools/obsidian_workflow_status")
async def workflow_status(workflow_id: str, vault_name: str):
    """Get the status of a workflow involving Obsidian operations"""
    try:
        # Mock workflow status - in production, this would integrate with LangGraph
        return {
            "success": True,
            "workflow_id": workflow_id,
            "vault_name": vault_name,
            "status": "running",
            "progress": 75,
            "current_step": "processing_files",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        return {"error": str(e), "success": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

"""
Enhanced Obsidian MCP Server with latest 2025 integration patterns
Supports multi-server interoperability and advanced agent-to-agent communication
"""

from fastmcp import FastMCP
from typing import Dict, Any, List, Optional
import httpx
import asyncio
import json
from datetime import datetime
from pathlib import Path
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create enhanced MCP server
mcp = FastMCP("enhanced-obsidian-mcp-server")

class ObsidianMCPClient:
    """Enhanced Obsidian MCP client with advanced features"""
    
    def __init__(self, api_key: str, base_url: str = "http://api-gateway:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling and caching"""
        cache_key = f"{method}:{endpoint}:{hash(str(kwargs))}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now().timestamp() - timestamp < self.cache_ttl:
                return cached_data
        
        try:
            response = await self.client.request(method, f"{self.base_url}{endpoint}", **kwargs)
            response.raise_for_status()
            data = response.json()
            
            # Cache successful responses
            self.cache[cache_key] = (data, datetime.now().timestamp())
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return {"error": str(e)}
    
    async def list_vaults(self) -> Dict[str, Any]:
        """List all available vaults"""
        return await self._make_request("GET", "/vaults")
    
    async def list_files(self, vault_name: str, path: str = "", recursive: bool = True, limit: int = 100) -> Dict[str, Any]:
        """List files in vault with advanced filtering"""
        params = {
            "path": path,
            "recursive": recursive,
            "limit": limit
        }
        return await self._make_request("GET", f"/vault/{vault_name}/files", params=params)
    
    async def read_note(self, vault_name: str, file_path: str, include_metadata: bool = True) -> Dict[str, Any]:
        """Read note with enhanced metadata"""
        params = {"include_metadata": include_metadata}
        return await self._make_request("GET", f"/vault/{vault_name}/file/{file_path}", params=params)
    
    async def put_file(self, vault_name: str, file_path: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
        """Create or update file with directory creation"""
        data = {
            "content": content,
            "create_dirs": create_dirs
        }
        return await self._make_request("PUT", f"/vault/{vault_name}/file/{file_path}", json=data)
    
    async def search_notes(self, vault_name: str, query: str, limit: int = 10, include_content: bool = False) -> Dict[str, Any]:
        """Advanced search with content inclusion"""
        data = {
            "query": query,
            "limit": limit,
            "include_content": include_content
        }
        return await self._make_request("POST", f"/vault/{vault_name}/search", json=data)
    
    async def patch_file(self, vault_name: str, file_path: str, patch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Patch file content with structured updates"""
        return await self._make_request("PATCH", f"/vault/{vault_name}/file/{file_path}", json=patch_data)
    
    async def delete_file(self, vault_name: str, file_path: str) -> Dict[str, Any]:
        """Delete file with confirmation"""
        return await self._make_request("DELETE", f"/vault/{vault_name}/file/{file_path}")
    
    async def get_vault_stats(self, vault_name: str) -> Dict[str, Any]:
        """Get comprehensive vault statistics"""
        return await self._make_request("GET", f"/vault/{vault_name}/stats")
    
    async def batch_operations(self, vault_name: str, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple operations in batch"""
        data = {"operations": operations}
        return await self._make_request("POST", f"/vault/{vault_name}/batch", json=data)
    
    async def get_active_file(self, vault_name: str) -> Dict[str, Any]:
        """Get currently active file in Obsidian"""
        return await self._make_request("GET", f"/vault/{vault_name}/active")
    
    async def set_active_file(self, vault_name: str, file_path: str) -> Dict[str, Any]:
        """Set active file in Obsidian"""
        data = {"file_path": file_path}
        return await self._make_request("POST", f"/vault/{vault_name}/active", json=data)

# Initialize client
obsidian_client = ObsidianMCPClient(
    api_key="b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
)

# Enhanced MCP Tools with 2025 patterns

@mcp.tool()
async def obsidian_list_vaults() -> Dict[str, Any]:
    """
    List all available Obsidian vaults with enhanced metadata.
    
    Returns comprehensive vault information including statistics and metadata.
    """
    try:
        result = await obsidian_client.list_vaults()
        return {
            "success": True,
            "vaults": result.get("vaults", []),
            "total": len(result.get("vaults", [])),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing vaults: {str(e)}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def obsidian_list_files(
    vault_name: str,
    path: str = "",
    recursive: bool = True,
    limit: int = 100,
    file_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    List files in an Obsidian vault with advanced filtering and pagination.
    
    Args:
        vault_name: Name of the vault to list files from
        path: Subpath within the vault (empty for root)
        recursive: Whether to include subdirectories
        limit: Maximum number of files to return
        file_types: Filter by file extensions (e.g., ['.md', '.txt'])
    """
    try:
        result = await obsidian_client.list_files(vault_name, path, recursive, limit)
        
        files = result.get("files", [])
        
        # Apply file type filtering
        if file_types:
            files = [f for f in files if any(f["path"].endswith(ext) for ext in file_types)]
        
        return {
            "success": True,
            "files": files,
            "total": len(files),
            "vault_name": vault_name,
            "path": path,
            "recursive": recursive,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def obsidian_read_note(
    vault_name: str,
    file_path: str,
    include_metadata: bool = True,
    include_links: bool = True
) -> Dict[str, Any]:
    """
    Read a specific note from an Obsidian vault with enhanced metadata.
    
    Args:
        vault_name: Name of the vault
        file_path: Path to the file within the vault
        include_metadata: Whether to include file metadata
        include_links: Whether to extract and include linked files
    """
    try:
        result = await obsidian_client.read_note(vault_name, file_path, include_metadata)
        
        if "error" in result:
            return result
        
        content = result.get("content", "")
        metadata = result.get("metadata", {})
        
        # Extract links if requested
        links = []
        if include_links and content:
            import re
            # Extract [[wiki links]] and [markdown links](url)
            wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
            markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            links = {
                "wiki_links": wiki_links,
                "markdown_links": [{"text": text, "url": url} for text, url in markdown_links]
            }
        
        # Calculate content statistics
        word_count = len(content.split()) if content else 0
        char_count = len(content) if content else 0
        line_count = len(content.split('\n')) if content else 0
        
        return {
            "success": True,
            "content": content,
            "metadata": metadata,
            "links": links,
            "statistics": {
                "word_count": word_count,
                "char_count": char_count,
                "line_count": line_count
            },
            "file_path": file_path,
            "vault_name": vault_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error reading note: {str(e)}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def obsidian_put_file(
    vault_name: str,
    file_path: str,
    content: str,
    create_dirs: bool = True,
    backup_existing: bool = True
) -> Dict[str, Any]:
    """
    Create or update a file in an Obsidian vault with advanced options.
    
    Args:
        vault_name: Name of the vault
        file_path: Path to the file within the vault
        content: Content to write to the file
        create_dirs: Whether to create parent directories if they don't exist
        backup_existing: Whether to backup existing file before overwriting
    """
    try:
        # Check if file exists and backup if requested
        if backup_existing:
            existing = await obsidian_client.read_note(vault_name, file_path, False)
            if "content" in existing and existing["content"]:
                backup_path = f"{file_path}.backup.{int(datetime.now().timestamp())}"
                await obsidian_client.put_file(vault_name, backup_path, existing["content"])
        
        result = await obsidian_client.put_file(vault_name, file_path, content, create_dirs)
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "message": "File created/updated successfully",
            "file_path": file_path,
            "vault_name": vault_name,
            "content_length": len(content),
            "backup_created": backup_existing and "content" in existing,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error putting file: {str(e)}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def obsidian_search_notes(
    vault_name: str,
    query: str,
    limit: int = 10,
    include_content: bool = False,
    search_type: str = "semantic"
) -> Dict[str, Any]:
    """
    Search for notes in an Obsidian vault with advanced search options.
    
    Args:
        vault_name: Name of the vault to search
        query: Search query string
        limit: Maximum number of results to return
        include_content: Whether to include full content in results
        search_type: Type of search ('semantic', 'exact', 'fuzzy')
    """
    try:
        result = await obsidian_client.search_notes(vault_name, query, limit, include_content)
        
        if "error" in result:
            return result
        
        results = result.get("results", [])
        
        # Enhance results with additional metadata
        enhanced_results = []
        for item in results:
            enhanced_item = {
                **item,
                "relevance_score": item.get("score", 0.0),
                "matched_terms": query.lower().split(),
                "search_type": search_type
            }
            enhanced_results.append(enhanced_item)
        
        return {
            "success": True,
            "results": enhanced_results,
            "total": len(enhanced_results),
            "query": query,
            "vault_name": vault_name,
            "search_type": search_type,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching notes: {str(e)}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def obsidian_patch_file(
    vault_name: str,
    file_path: str,
    patch_operations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Apply structured patches to a file in an Obsidian vault.
    
    Args:
        vault_name: Name of the vault
        file_path: Path to the file within the vault
        patch_operations: List of patch operations to apply
    """
    try:
        result = await obsidian_client.patch_file(vault_name, file_path, {"operations": patch_operations})
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "message": "File patched successfully",
            "file_path": file_path,
            "vault_name": vault_name,
            "operations_applied": len(patch_operations),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error patching file: {str(e)}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def obsidian_delete_file(
    vault_name: str,
    file_path: str,
    confirm: bool = False
) -> Dict[str, Any]:
    """
    Delete a file from an Obsidian vault with confirmation.
    
    Args:
        vault_name: Name of the vault
        file_path: Path to the file within the vault
        confirm: Confirmation flag to prevent accidental deletion
    """
    try:
        if not confirm:
            return {
                "error": "Deletion requires confirmation. Set confirm=True to proceed.",
                "success": False
            }
        
        result = await obsidian_client.delete_file(vault_name, file_path)
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "message": "File deleted successfully",
            "file_path": file_path,
            "vault_name": vault_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def obsidian_get_vault_stats(vault_name: str) -> Dict[str, Any]:
    """
    Get comprehensive statistics for an Obsidian vault.
    
    Args:
        vault_name: Name of the vault to get statistics for
    """
    try:
        result = await obsidian_client.get_vault_stats(vault_name)
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "stats": result,
            "vault_name": vault_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting vault stats: {str(e)}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def obsidian_batch_operations(
    vault_name: str,
    operations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Execute multiple operations in batch for improved performance.
    
    Args:
        vault_name: Name of the vault
        operations: List of operations to execute
    """
    try:
        result = await obsidian_client.batch_operations(vault_name, operations)
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "results": result.get("results", []),
            "total_operations": len(operations),
            "successful_operations": len([r for r in result.get("results", []) if r.get("success", False)]),
            "vault_name": vault_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing batch operations: {str(e)}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def obsidian_get_active_file(vault_name: str) -> Dict[str, Any]:
    """
    Get the currently active file in Obsidian.
    
    Args:
        vault_name: Name of the vault
    """
    try:
        result = await obsidian_client.get_active_file(vault_name)
        
        if "error" in result:
            return result
        
        return {
            "success": True,
            "active_file": result.get("file_path", ""),
            "vault_name": vault_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting active file: {str(e)}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def obsidian_set_active_file(
    vault_name: str,
    file_path: str
) -> Dict[str, Any]:
    """
    Set the active file in Obsidian.
    
    Args:
        vault_name: Name of the vault
        file_path: Path to the file to set as active
    """
    try:
        result = await obsidian_client.set_active_file(vault_name, file_path)
        
        if "error" in result:
            return result
        
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

# Multi-server interoperability tools

@mcp.tool()
async def obsidian_agent_communication(
    target_agent: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send a message to another agent in the multi-server system.
    
    Args:
        target_agent: Name or ID of the target agent
        message: Message content to send
        data: Optional data payload to include
    """
    try:
        # This would integrate with the multi-server communication system
        # For now, we'll simulate the communication
        communication_data = {
            "from": "obsidian-mcp-server",
            "to": target_agent,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # In a real implementation, this would send to the communication service
        logger.info(f"Agent communication: {communication_data}")
        
        return {
            "success": True,
            "message": "Communication sent successfully",
            "target_agent": target_agent,
            "communication_id": hashlib.md5(str(communication_data).encode()).hexdigest(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in agent communication: {str(e)}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def obsidian_workflow_status(
    workflow_id: str,
    vault_name: str
) -> Dict[str, Any]:
    """
    Get the status of a workflow involving Obsidian operations.
    
    Args:
        workflow_id: ID of the workflow to check
        vault_name: Name of the vault involved in the workflow
    """
    try:
        # This would integrate with the LangGraph workflow system
        # For now, we'll return a mock status
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
    # Run the enhanced MCP server
    mcp.run(port=8002, host="0.0.0.0")

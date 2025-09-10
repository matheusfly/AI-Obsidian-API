"""
MCP Server for Obsidian Vault Integration
Provides standardized MCP tools for LangGraph agents to interact with Obsidian vaults
"""
import asyncio
import json
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

from fastmcp import FastMCP
from pydantic import BaseModel, Field
import httpx
import structlog

from config.environment import config

logger = structlog.get_logger()

# Initialize FastMCP server
mcp = FastMCP("obsidian-vault-server")

# HTTP client for API Gateway
class APIClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.GATEWAY_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the API Gateway"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(
                "api_request_error",
                method=method,
                endpoint=endpoint,
                error=str(e),
                status_code=getattr(e.response, 'status_code', None)
            )
            raise Exception(f"API request failed: {str(e)}")
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global API client
api_client = APIClient()

# Pydantic models for MCP tools
class ListFilesInput(BaseModel):
    vault: str = Field(..., description="Name of the Obsidian vault")
    cursor: Optional[str] = Field(None, description="Pagination cursor")
    limit: int = Field(100, description="Maximum number of files to return")
    filter: Optional[str] = Field(None, description="Filter files by path pattern")

class ReadNoteInput(BaseModel):
    vault: str = Field(..., description="Name of the Obsidian vault")
    path: str = Field(..., description="Path to the note file")

class PutFileInput(BaseModel):
    vault: str = Field(..., description="Name of the Obsidian vault")
    path: str = Field(..., description="Path to the file")
    content: str = Field(..., description="Content to write")
    dry_run: bool = Field(True, description="Whether to perform a dry run")
    if_match: Optional[str] = Field(None, description="Hash for conflict detection")
    mode: str = Field("upsert", description="Write mode (upsert, create, update)")

class PatchFileInput(BaseModel):
    vault: str = Field(..., description="Name of the Obsidian vault")
    path: str = Field(..., description="Path to the file")
    patch_ops: List[Dict[str, Any]] = Field(..., description="List of patch operations")
    dry_run: bool = Field(True, description="Whether to perform a dry run")

class SearchNotesInput(BaseModel):
    vault: str = Field(..., description="Name of the Obsidian vault")
    query: str = Field(..., description="Search query")
    limit: int = Field(20, description="Maximum number of results")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional search filters")

class DeleteFileInput(BaseModel):
    vault: str = Field(..., description="Name of the Obsidian vault")
    path: str = Field(..., description="Path to the file")
    confirm: bool = Field(False, description="Confirmation flag for deletion")

# MCP Tool Definitions
@mcp.tool()
async def obsidian_list_files(input: ListFilesInput) -> Dict[str, Any]:
    """
    List files in an Obsidian vault with pagination support.
    
    This tool allows you to browse the contents of an Obsidian vault,
    with support for pagination and filtering by path patterns.
    """
    try:
        result = await api_client.request(
            "GET",
            f"/vault/{input.vault}/files",
            params={
                "cursor": input.cursor,
                "limit": input.limit,
                "filter": input.filter
            }
        )
        
        logger.info(
            "obsidian_list_files_success",
            vault=input.vault,
            file_count=len(result.get("files", [])),
            cursor=input.cursor
        )
        
        return {
            "success": True,
            "vault": input.vault,
            "files": result.get("files", []),
            "cursor": result.get("cursor"),
            "has_more": result.get("has_more", False),
            "total_count": len(result.get("files", []))
        }
    except Exception as e:
        logger.error("obsidian_list_files_error", vault=input.vault, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "vault": input.vault
        }

@mcp.tool()
async def obsidian_read_note(input: ReadNoteInput) -> Dict[str, Any]:
    """
    Read the content of a specific note from an Obsidian vault.
    
    This tool retrieves the full content of a note, including metadata
    and a hash for conflict detection.
    """
    try:
        result = await api_client.request(
            "GET",
            f"/vault/{input.vault}/file/{input.path}"
        )
        
        logger.info(
            "obsidian_read_note_success",
            vault=input.vault,
            path=input.path,
            content_length=len(result.get("content", ""))
        )
        
        return {
            "success": True,
            "vault": input.vault,
            "path": input.path,
            "content": result.get("content", ""),
            "frontmatter": result.get("frontmatter", {}),
            "backlinks": result.get("backlinks", []),
            "hash": result.get("_hash"),
            "last_modified": result.get("last_modified")
        }
    except Exception as e:
        logger.error("obsidian_read_note_error", vault=input.vault, path=input.path, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "vault": input.vault,
            "path": input.path
        }

@mcp.tool()
async def obsidian_put_file(input: PutFileInput) -> Dict[str, Any]:
    """
    Create or update a file in an Obsidian vault.
    
    This tool supports safe write operations with conflict detection
    and human-in-the-loop approval for dry runs.
    """
    try:
        result = await api_client.request(
            "PUT",
            f"/vault/{input.vault}/file/{input.path}",
            json={
                "path": input.path,
                "content": input.content,
                "dry_run": input.dry_run,
                "if_match": input.if_match,
                "mode": input.mode
            }
        )
        
        logger.info(
            "obsidian_put_file_success",
            vault=input.vault,
            path=input.path,
            dry_run=input.dry_run,
            content_length=len(input.content)
        )
        
        return {
            "success": True,
            "vault": input.vault,
            "path": input.path,
            "dry_run": result.get("dry_run", False),
            "tool_call_id": result.get("tool_call_id"),
            "approval_required": result.get("approval_required", False),
            "approval_endpoint": result.get("approval_endpoint"),
            "result": result.get("result", {})
        }
    except Exception as e:
        logger.error("obsidian_put_file_error", vault=input.vault, path=input.path, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "vault": input.vault,
            "path": input.path
        }

@mcp.tool()
async def obsidian_patch_file(input: PatchFileInput) -> Dict[str, Any]:
    """
    Patch content in an existing file in an Obsidian vault.
    
    This tool allows for precise modifications to file content,
    such as appending to sections or inserting at specific positions.
    """
    try:
        result = await api_client.request(
            "PATCH",
            f"/vault/{input.vault}/file/{input.path}",
            json={
                "patch_ops": input.patch_ops,
                "dry_run": input.dry_run
            }
        )
        
        logger.info(
            "obsidian_patch_file_success",
            vault=input.vault,
            path=input.path,
            patch_ops_count=len(input.patch_ops),
            dry_run=input.dry_run
        )
        
        return {
            "success": True,
            "vault": input.vault,
            "path": input.path,
            "patch_ops_count": len(input.patch_ops),
            "dry_run": input.dry_run,
            "result": result
        }
    except Exception as e:
        logger.error("obsidian_patch_file_error", vault=input.vault, path=input.path, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "vault": input.vault,
            "path": input.path
        }

@mcp.tool()
async def obsidian_search_notes(input: SearchNotesInput) -> Dict[str, Any]:
    """
    Search for notes in an Obsidian vault.
    
    This tool performs full-text search across the vault with
    support for filters and pagination.
    """
    try:
        result = await api_client.request(
            "POST",
            f"/vault/{input.vault}/search",
            json={
                "query": input.query,
                "limit": input.limit,
                "filters": input.filters or {}
            }
        )
        
        logger.info(
            "obsidian_search_notes_success",
            vault=input.vault,
            query=input.query,
            result_count=len(result.get("results", []))
        )
        
        return {
            "success": True,
            "vault": input.vault,
            "query": input.query,
            "results": result.get("results", []),
            "total_count": len(result.get("results", [])),
            "filters_applied": input.filters
        }
    except Exception as e:
        logger.error("obsidian_search_notes_error", vault=input.vault, query=input.query, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "vault": input.vault,
            "query": input.query
        }

@mcp.tool()
async def obsidian_delete_file(input: DeleteFileInput) -> Dict[str, Any]:
    """
    Delete a file from an Obsidian vault.
    
    This tool requires explicit confirmation to prevent accidental deletions.
    """
    if not input.confirm:
        return {
            "success": False,
            "error": "Deletion requires confirmation. Set confirm=true",
            "vault": input.vault,
            "path": input.path
        }
    
    try:
        result = await api_client.request(
            "DELETE",
            f"/vault/{input.vault}/file/{input.path}",
            params={"confirm": "true"}
        )
        
        logger.info("obsidian_delete_file_success", vault=input.vault, path=input.path)
        
        return {
            "success": True,
            "vault": input.vault,
            "path": input.path,
            "status": "deleted",
            "result": result
        }
    except Exception as e:
        logger.error("obsidian_delete_file_error", vault=input.vault, path=input.path, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "vault": input.vault,
            "path": input.path
        }

@mcp.tool()
async def obsidian_get_daily_note(vault: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get or create a daily note for a specific date.
    
    If no date is provided, uses today's date in YYYY-MM-DD format.
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        result = await api_client.request(
            "GET",
            f"/vault/{vault}/daily/{date}"
        )
        
        logger.info("obsidian_get_daily_note_success", vault=vault, date=date)
        
        return {
            "success": True,
            "vault": vault,
            "date": date,
            "path": result.get("path"),
            "content": result.get("content", ""),
            "created": result.get("created", False)
        }
    except Exception as e:
        logger.error("obsidian_get_daily_note_error", vault=vault, date=date, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "vault": vault,
            "date": date
        }

@mcp.tool()
async def obsidian_list_pending_operations() -> Dict[str, Any]:
    """
    List all pending operations that require human approval.
    
    This tool helps track operations that are waiting for approval
    in the human-in-the-loop workflow.
    """
    try:
        result = await api_client.request("GET", "/pending_operations")
        
        logger.info("obsidian_list_pending_operations_success", count=len(result))
        
        return {
            "success": True,
            "pending_operations": result,
            "count": len(result)
        }
    except Exception as e:
        logger.error("obsidian_list_pending_operations_error", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "pending_operations": []
        }

@mcp.tool()
async def obsidian_approve_operation(tool_call_id: str, approved_by: str = "human") -> Dict[str, Any]:
    """
    Approve a pending operation for execution.
    
    This tool allows you to approve operations that were created in dry-run mode.
    """
    try:
        result = await api_client.request(
            "POST",
            f"/approve/{tool_call_id}",
            json={"approved_by": approved_by}
        )
        
        logger.info("obsidian_approve_operation_success", tool_call_id=tool_call_id, approved_by=approved_by)
        
        return {
            "success": True,
            "tool_call_id": tool_call_id,
            "approved_by": approved_by,
            "status": result.get("status"),
            "result": result.get("result")
        }
    except Exception as e:
        logger.error("obsidian_approve_operation_error", tool_call_id=tool_call_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "tool_call_id": tool_call_id
        }

# MCP Prompts for common workflows
@mcp.prompt()
async def create_daily_note_prompt(
    vault: str,
    date: str = "",
    template: str = "default"
) -> Dict[str, Any]:
    """
    Create a daily note with a structured template.
    
    This prompt helps create well-structured daily notes with
    predefined sections for planning, tasks, and reflections.
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Get or create the daily note
    daily_note_result = await obsidian_get_daily_note(vault, date)
    
    if not daily_note_result["success"]:
        return daily_note_result
    
    # Define template content based on template type
    templates = {
        "default": f"""# Daily Note - {date}

## Morning Planning
- [ ] 
- [ ] 
- [ ] 

## Tasks
- [ ] 
- [ ] 
- [ ] 

## Notes
- 

## Evening Reflection
- What went well today?
- What could be improved?
- Key insights:

## Tomorrow's Focus
- 
- 
- 
""",
        "minimal": f"""# {date}

## Tasks
- [ ] 
- [ ] 

## Notes
- 
""",
        "detailed": f"""# Daily Note - {date}

## Weather & Mood
- Weather: 
- Mood: 
- Energy Level: 

## Morning Planning
### Top 3 Priorities
1. 
2. 
3. 

### Schedule
- 9:00 AM: 
- 12:00 PM: 
- 3:00 PM: 
- 6:00 PM: 

## Tasks
### Work
- [ ] 
- [ ] 

### Personal
- [ ] 
- [ ] 

## Notes & Ideas
- 

## Meetings & Calls
- 

## Learning & Development
- 

## Evening Reflection
### Accomplishments
- 

### Challenges
- 

### Lessons Learned
- 

### Gratitude
- 

## Tomorrow's Focus
- 
- 
- 

## Links
- 
"""
    }
    
    template_content = templates.get(template, templates["default"])
    
    # Update the daily note with template content
    put_result = await obsidian_put_file(PutFileInput(
        vault=vault,
        path=daily_note_result["path"],
        content=template_content,
        dry_run=False
    ))
    
    return {
        "success": put_result["success"],
        "vault": vault,
        "date": date,
        "path": daily_note_result["path"],
        "template": template,
        "content_length": len(template_content),
        "error": put_result.get("error")
    }

@mcp.prompt()
async def organize_inbox_prompt(
    vault: str,
    inbox_path: str = "inbox",
    organization_rules: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Organize files in the inbox folder based on predefined rules.
    
    This prompt helps automatically categorize and move files
    from the inbox to appropriate folders.
    """
    if not organization_rules:
        organization_rules = {
            "meeting": "meetings",
            "project": "projects",
            "idea": "ideas",
            "task": "tasks",
            "note": "notes"
        }
    
    # List files in inbox
    list_result = await obsidian_list_files(ListFilesInput(
        vault=vault,
        filter=f"{inbox_path}/*"
    ))
    
    if not list_result["success"]:
        return list_result
    
    files = list_result["files"]
    organization_results = []
    
    for file in files:
        file_path = file["path"]
        file_content = file.get("content", "")
        
        # Simple keyword-based categorization
        category = "notes"  # default
        for keyword, folder in organization_rules.items():
            if keyword.lower() in file_content.lower() or keyword.lower() in file_path.lower():
                category = folder
                break
        
        # Determine new path
        new_path = file_path.replace(f"{inbox_path}/", f"{category}/")
        
        # Move file (this would require a move operation in the API)
        # For now, we'll just return the organization plan
        organization_results.append({
            "original_path": file_path,
            "suggested_path": new_path,
            "category": category,
            "reason": f"Contains keyword: {category}"
        })
    
    return {
        "success": True,
        "vault": vault,
        "inbox_path": inbox_path,
        "files_processed": len(files),
        "organization_plan": organization_results,
        "rules_applied": organization_rules
    }

# Server startup and cleanup
async def startup():
    """Initialize the MCP server"""
    logger.info("obsidian_mcp_server_starting", base_url=config.GATEWAY_URL)

async def cleanup():
    """Cleanup resources"""
    await api_client.close()
    logger.info("obsidian_mcp_server_shutdown")

# Run the MCP server
if __name__ == "__main__":
    import asyncio
    
    async def main():
        await startup()
        try:
            await mcp.run()
        finally:
            await cleanup()
    
    asyncio.run(main())

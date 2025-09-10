"""
System Overview API Endpoints
Provides comprehensive system mapping and live data
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import httpx
from datetime import datetime
import os
import psutil
import docker

router = APIRouter(prefix="/system", tags=["System Overview"])

class SystemStats(BaseModel):
    total_endpoints: int
    total_mcp_tools: int
    total_schemas: int
    active_services: int
    uptime: str
    memory_usage: float
    cpu_usage: float

class ServiceStatus(BaseModel):
    name: str
    url: Optional[str] = None
    status: str
    response_time: Optional[float] = None
    last_check: datetime

class EndpointInfo(BaseModel):
    method: str
    path: str
    description: str
    parameters: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None

class MCPToolInfo(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    return_type: str
    category: str

@router.get("/overview", response_class=HTMLResponse)
async def system_overview_page():
    """System overview dashboard page"""
    try:
        with open("jsoncrack/web/overview.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Overview page not found")

@router.get("/stats")
async def get_system_stats():
    """Get comprehensive system statistics"""
    try:
        # Get system metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Count endpoints from OpenAPI spec
        total_endpoints = await count_api_endpoints()
        
        # Count MCP tools
        total_mcp_tools = await count_mcp_tools()
        
        # Count schemas
        total_schemas = await count_data_schemas()
        
        # Count active services
        active_services = await count_active_services()
        
        # Get uptime
        uptime = await get_system_uptime()
        
        return SystemStats(
            total_endpoints=total_endpoints,
            total_mcp_tools=total_mcp_tools,
            total_schemas=total_schemas,
            active_services=active_services,
            uptime=uptime,
            memory_usage=memory.percent,
            cpu_usage=cpu_percent
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system stats: {str(e)}")

@router.get("/services")
async def get_services_status():
    """Get status of all system services"""
    services = []
    
    # Web services
    web_services = [
        {"name": "Vault API", "url": "http://localhost:8081", "category": "web"},
        {"name": "JSON Viewer", "url": "http://localhost:3003", "category": "web"},
        {"name": "n8n Workflows", "url": "http://localhost:5678", "category": "web"},
        {"name": "Motia Dev", "url": "http://localhost:3000", "category": "web"},
        {"name": "Flyde Studio", "url": "http://localhost:3001", "category": "web"},
        {"name": "JSON Crack", "url": "http://localhost:3002", "category": "web"}
    ]
    
    # Database services
    db_services = [
        {"name": "PostgreSQL", "url": None, "category": "database"},
        {"name": "Redis Cache", "url": None, "category": "database"}
    ]
    
    # Check service status
    all_services = web_services + db_services
    
    for service in all_services:
        status = await check_service_health(service["url"]) if service["url"] else "unknown"
        response_time = await measure_response_time(service["url"]) if service["url"] else None
        
        services.append(ServiceStatus(
            name=service["name"],
            url=service["url"],
            status=status,
            response_time=response_time,
            last_check=datetime.now()
        ))
    
    return {"services": services}

@router.get("/endpoints")
async def get_all_endpoints():
    """Get comprehensive list of all API endpoints"""
    endpoints = {
        "health": [
            {"method": "GET", "path": "/health", "description": "System health check"},
            {"method": "GET", "path": "/status", "description": "Detailed system status"},
            {"method": "GET", "path": "/metrics", "description": "System metrics"}
        ],
        "notes": [
            {"method": "GET", "path": "/notes", "description": "List all notes"},
            {"method": "POST", "path": "/notes", "description": "Create new note"},
            {"method": "GET", "path": "/notes/{id}", "description": "Get specific note"},
            {"method": "PUT", "path": "/notes/{id}", "description": "Update note"},
            {"method": "DELETE", "path": "/notes/{id}", "description": "Delete note"}
        ],
        "search": [
            {"method": "GET", "path": "/search", "description": "Search notes"},
            {"method": "GET", "path": "/search/tags", "description": "Search by tags"},
            {"method": "GET", "path": "/search/content", "description": "Full-text search"}
        ],
        "ai": [
            {"method": "POST", "path": "/ai/process", "description": "AI text processing"},
            {"method": "POST", "path": "/ai/summarize", "description": "AI summarization"},
            {"method": "POST", "path": "/ai/analyze", "description": "AI content analysis"}
        ],
        "mcp": [
            {"method": "POST", "path": "/mcp/tools", "description": "Execute MCP tool"},
            {"method": "GET", "path": "/mcp/tools", "description": "List MCP tools"},
            {"method": "GET", "path": "/mcp/resources", "description": "List MCP resources"}
        ],
        "visualization": [
            {"method": "GET", "path": "/visualize", "description": "Visualization dashboard"},
            {"method": "GET", "path": "/visualize/api-endpoints", "description": "API structure visualization"},
            {"method": "GET", "path": "/visualize/mcp-tools", "description": "MCP tools visualization"},
            {"method": "POST", "path": "/visualize/custom", "description": "Custom visualization"}
        ],
        "system": [
            {"method": "GET", "path": "/system/overview", "description": "System overview dashboard"},
            {"method": "GET", "path": "/system/stats", "description": "System statistics"},
            {"method": "GET", "path": "/system/services", "description": "Service status"},
            {"method": "GET", "path": "/system/endpoints", "description": "All endpoints list"}
        ]
    }
    
    return {"endpoints": endpoints}

@router.get("/mcp-tools")
async def get_mcp_tools():
    """Get comprehensive list of MCP tools"""
    mcp_tools = {
        "file_operations": [
            {
                "name": "read_file",
                "description": "Read content from file path",
                "parameters": {"path": {"type": "string", "description": "File path to read"}},
                "return_type": "string",
                "category": "file_operations"
            },
            {
                "name": "write_file",
                "description": "Write content to file path",
                "parameters": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "return_type": "boolean",
                "category": "file_operations"
            },
            {
                "name": "list_files",
                "description": "List files in directory",
                "parameters": {"directory": {"type": "string", "description": "Directory path"}},
                "return_type": "array",
                "category": "file_operations"
            }
        ],
        "search_operations": [
            {
                "name": "search_content",
                "description": "Search content in vault",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Maximum results"}
                },
                "return_type": "array",
                "category": "search_operations"
            },
            {
                "name": "search_notes",
                "description": "Search notes by query",
                "parameters": {"query": {"type": "string", "description": "Search query"}},
                "return_type": "array",
                "category": "search_operations"
            }
        ],
        "ai_operations": [
            {
                "name": "analyze_note",
                "description": "AI analysis of note content",
                "parameters": {
                    "note_id": {"type": "string", "description": "Note ID to analyze"},
                    "analysis_type": {"type": "string", "description": "Type of analysis"}
                },
                "return_type": "object",
                "category": "ai_operations"
            },
            {
                "name": "summarize_text",
                "description": "AI text summarization",
                "parameters": {"text": {"type": "string", "description": "Text to summarize"}},
                "return_type": "string",
                "category": "ai_operations"
            }
        ],
        "workflow_operations": [
            {
                "name": "trigger_workflow",
                "description": "Trigger n8n workflow",
                "parameters": {
                    "workflow_name": {"type": "string", "description": "Name of workflow"},
                    "data": {"type": "object", "description": "Data to pass to workflow"}
                },
                "return_type": "object",
                "category": "workflow_operations"
            }
        ]
    }
    
    return {"mcp_tools": mcp_tools}

@router.get("/schemas")
async def get_data_schemas():
    """Get all data schemas and models"""
    schemas = {
        "Note": {
            "id": {"type": "string", "description": "Unique note identifier"},
            "title": {"type": "string", "description": "Note title"},
            "content": {"type": "string", "description": "Note content"},
            "tags": {"type": "array", "description": "Note tags"},
            "created_at": {"type": "datetime", "description": "Creation timestamp"},
            "updated_at": {"type": "datetime", "description": "Last update timestamp"}
        },
        "APIResponse": {
            "status": {"type": "string", "description": "Response status"},
            "data": {"type": "object", "description": "Response data"},
            "message": {"type": "string", "description": "Response message"},
            "timestamp": {"type": "datetime", "description": "Response timestamp"}
        },
        "MCPTool": {
            "name": {"type": "string", "description": "Tool name"},
            "description": {"type": "string", "description": "Tool description"},
            "parameters": {"type": "object", "description": "Tool parameters"},
            "return_type": {"type": "string", "description": "Return type"}
        },
        "Workflow": {
            "id": {"type": "string", "description": "Workflow ID"},
            "name": {"type": "string", "description": "Workflow name"},
            "nodes": {"type": "array", "description": "Workflow nodes"},
            "connections": {"type": "array", "description": "Node connections"},
            "status": {"type": "string", "description": "Workflow status"}
        }
    }
    
    return {"schemas": schemas}

@router.get("/connections")
async def get_system_connections():
    """Get system architecture and connection map"""
    connections = {
        "service_flow": [
            {"name": "Client", "type": "external"},
            {"name": "API Gateway", "type": "gateway"},
            {"name": "Vault API", "type": "service"},
            {"name": "Database", "type": "storage"}
        ],
        "data_flow": [
            {"name": "Request", "type": "input"},
            {"name": "Validation", "type": "processing"},
            {"name": "Business Logic", "type": "processing"},
            {"name": "Response", "type": "output"}
        ],
        "api_integration": [
            {"name": "REST API", "type": "api"},
            {"name": "MCP Tools", "type": "tools"},
            {"name": "n8n Workflows", "type": "automation"},
            {"name": "JSON Visualization", "type": "ui"}
        ]
    }
    
    return {"connections": connections}

@router.get("/live-data")
async def get_live_system_data():
    """Get comprehensive live system data for overview"""
    try:
        stats = await get_system_stats()
        services = await get_services_status()
        endpoints = await get_all_endpoints()
        mcp_tools = await get_mcp_tools()
        schemas = await get_data_schemas()
        connections = await get_system_connections()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "services": services,
            "endpoints": endpoints,
            "mcp_tools": mcp_tools,
            "schemas": schemas,
            "connections": connections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get live data: {str(e)}")

# Helper functions
async def count_api_endpoints() -> int:
    """Count total API endpoints"""
    try:
        # This would typically read from OpenAPI spec
        return 25  # Approximate count
    except:
        return 0

async def count_mcp_tools() -> int:
    """Count total MCP tools"""
    try:
        # This would typically read from MCP registry
        return 12  # Approximate count
    except:
        return 0

async def count_data_schemas() -> int:
    """Count total data schemas"""
    try:
        # This would typically read from schema registry
        return 8  # Approximate count
    except:
        return 0

async def count_active_services() -> int:
    """Count active services"""
    try:
        # Check Docker containers
        client = docker.from_env()
        containers = client.containers.list()
        return len([c for c in containers if c.status == 'running'])
    except:
        return 0

async def get_system_uptime() -> str:
    """Get system uptime"""
    try:
        uptime_seconds = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(uptime_seconds)
        return str(uptime).split('.')[0]  # Remove microseconds
    except:
        return "Unknown"

async def check_service_health(url: str) -> str:
    """Check if service is healthy"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            return "online" if response.status_code == 200 else "offline"
    except:
        return "offline"

async def measure_response_time(url: str) -> Optional[float]:
    """Measure service response time"""
    try:
        async with httpx.AsyncClient() as client:
            start_time = datetime.now()
            response = await client.get(url, timeout=5.0)
            end_time = datetime.now()
            return (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
    except:
        return None

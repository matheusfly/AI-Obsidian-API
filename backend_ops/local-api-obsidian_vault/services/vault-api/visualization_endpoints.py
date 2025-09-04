"""
JSON Crack Visualization Endpoints for Obsidian Vault API
Provides interactive visualization of all API data structures
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import httpx
from datetime import datetime
import os

router = APIRouter(prefix="/visualize", tags=["Visualization"])

# Configuration
JSONCRACK_URL = os.getenv("JSONCRACK_URL", "http://localhost:3001")
ENABLE_VISUALIZATION = os.getenv("ENABLE_VISUALIZATION", "true").lower() == "true"

class VisualizationRequest(BaseModel):
    data: Dict[str, Any]
    title: str = "API Data Visualization"
    layout: str = "hierarchical"  # hierarchical, force, circular
    theme: str = "light"  # light, dark
    show_metadata: bool = True

class APIVisualizationData(BaseModel):
    endpoint: str
    method: str
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}

@router.get("/", response_class=HTMLResponse)
async def visualization_dashboard():
    """Main visualization dashboard"""
    if not ENABLE_VISUALIZATION:
        raise HTTPException(status_code=503, detail="Visualization not enabled")
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Obsidian Vault API - JSON Crack Visualization</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: #fafafa; }
            .card h3 { margin-top: 0; color: #333; }
            .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
            .btn:hover { background: #0056b3; }
            .status { padding: 10px; border-radius: 4px; margin: 10px 0; }
            .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 Obsidian Vault API - JSON Crack Visualization</h1>
                <p>Interactive visualization of all API endpoints, MCP tools, and data structures</p>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>📊 API Endpoints</h3>
                    <p>Visualize all REST API endpoints and their data structures</p>
                    <a href="/visualize/api-endpoints" class="btn">View API Structure</a>
                    <a href="/visualize/api-schema" class="btn">View OpenAPI Schema</a>
                </div>
                
                <div class="card">
                    <h3>🔧 MCP Tools</h3>
                    <p>Explore Model Context Protocol tools and their configurations</p>
                    <a href="/visualize/mcp-tools" class="btn">View MCP Tools</a>
                    <a href="/visualize/mcp-schema" class="btn">View MCP Schema</a>
                </div>
                
                <div class="card">
                    <h3>⚡ n8n Workflows</h3>
                    <p>Visualize workflow configurations and execution data</p>
                    <a href="/visualize/workflows" class="btn">View Workflows</a>
                    <a href="/visualize/workflow-executions" class="btn">View Executions</a>
                </div>
                
                <div class="card">
                    <h3>📁 Vault Structure</h3>
                    <p>Explore Obsidian vault file structure and metadata</p>
                    <a href="/visualize/vault-structure" class="btn">View File Tree</a>
                    <a href="/visualize/vault-metadata" class="btn">View Metadata</a>
                </div>
                
                <div class="card">
                    <h3>🔄 Real-time Data</h3>
                    <p>Live visualization of API requests and responses</p>
                    <a href="/visualize/live-requests" class="btn">Live Requests</a>
                    <a href="/visualize/performance" class="btn">Performance Data</a>
                </div>
                
                <div class="card">
                    <h3>🎨 Custom Visualization</h3>
                    <p>Create custom visualizations with your own data</p>
                    <a href="/visualize/custom" class="btn">Custom Visualizer</a>
                    <a href="/visualize/embed" class="btn">Embed Widget</a>
                </div>
            </div>
            
            <div id="status" class="status" style="display: none;"></div>
        </div>
        
        <script>
            // Check JSON Crack status
            fetch('/visualize/status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('status');
                    statusDiv.style.display = 'block';
                    if (data.status === 'connected') {
                        statusDiv.className = 'status success';
                        statusDiv.textContent = '✅ JSON Crack is connected and ready';
                    } else {
                        statusDiv.className = 'status error';
                        statusDiv.textContent = '❌ JSON Crack connection failed: ' + data.error;
                    }
                })
                .catch(error => {
                    const statusDiv = document.getElementById('status');
                    statusDiv.style.display = 'block';
                    statusDiv.className = 'status error';
                    statusDiv.textContent = '❌ Failed to check JSON Crack status';
                });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/status")
async def check_jsoncrack_status():
    """Check JSON Crack service status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{JSONCRACK_URL}/api/health", timeout=5.0)
            if response.status_code == 200:
                return {"status": "connected", "url": JSONCRACK_URL}
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get("/api-endpoints")
async def visualize_api_endpoints():
    """Visualize all API endpoints structure"""
    if not ENABLE_VISUALIZATION:
        raise HTTPException(status_code=503, detail="Visualization not enabled")
    
    # Get all API endpoints from FastAPI app
    api_data = {
        "title": "Obsidian Vault API Endpoints",
        "version": "1.0.0",
        "endpoints": {
            "health": {
                "GET /health": {
                    "description": "Health check endpoint",
                    "response": {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
                }
            },
            "notes": {
                "GET /notes": {
                    "description": "List all notes",
                    "response": {"notes": [], "total": 0}
                },
                "POST /notes": {
                    "description": "Create new note",
                    "request": {"title": "string", "content": "string", "tags": ["string"]},
                    "response": {"id": "string", "title": "string", "created_at": "string"}
                },
                "GET /notes/{note_id}": {
                    "description": "Get specific note",
                    "response": {"id": "string", "title": "string", "content": "string"}
                }
            },
            "search": {
                "GET /search": {
                    "description": "Search notes",
                    "query_params": {"q": "string", "limit": "integer"},
                    "response": {"results": [], "total": 0}
                }
            },
            "ai": {
                "POST /ai/process": {
                    "description": "AI processing endpoint",
                    "request": {"text": "string", "action": "string"},
                    "response": {"result": "string", "confidence": "float"}
                }
            },
            "mcp": {
                "POST /mcp/tools": {
                    "description": "MCP tool execution",
                    "request": {"tool": "string", "arguments": {}},
                    "response": {"result": "any", "metadata": {}}
                }
            }
        }
    }
    
    return await send_to_jsoncrack(api_data, "API Endpoints Structure")

@router.get("/mcp-tools")
async def visualize_mcp_tools():
    """Visualize MCP tools structure"""
    if not ENABLE_VISUALIZATION:
        raise HTTPException(status_code=503, detail="Visualization not enabled")
    
    mcp_data = {
        "title": "Model Context Protocol Tools",
        "version": "1.0.0",
        "tools": {
            "file_operations": {
                "read_file": {
                    "description": "Read file content",
                    "arguments": {"path": "string"},
                    "response": {"content": "string", "metadata": {}}
                },
                "write_file": {
                    "description": "Write file content",
                    "arguments": {"path": "string", "content": "string"},
                    "response": {"success": "boolean", "path": "string"}
                }
            },
            "search_operations": {
                "search_content": {
                    "description": "Search content in vault",
                    "arguments": {"query": "string", "limit": "integer"},
                    "response": {"results": [], "total": 0}
                }
            },
            "ai_operations": {
                "analyze_note": {
                    "description": "AI analysis of note content",
                    "arguments": {"note_id": "string", "analysis_type": "string"},
                    "response": {"analysis": "string", "confidence": "float"}
                }
            }
        }
    }
    
    return await send_to_jsoncrack(mcp_data, "MCP Tools Structure")

@router.get("/workflows")
async def visualize_workflows():
    """Visualize n8n workflows"""
    if not ENABLE_VISUALIZATION:
        raise HTTPException(status_code=503, detail="Visualization not enabled")
    
    workflow_data = {
        "title": "n8n Workflows",
        "workflows": {
            "note_processing": {
                "name": "Note Processing Workflow",
                "nodes": [
                    {"id": "webhook", "type": "webhook", "name": "Receive Note"},
                    {"id": "ai_process", "type": "ai", "name": "AI Processing"},
                    {"id": "save_note", "type": "obsidian", "name": "Save to Vault"}
                ],
                "connections": [
                    {"from": "webhook", "to": "ai_process"},
                    {"from": "ai_process", "to": "save_note"}
                ]
            },
            "search_workflow": {
                "name": "Search Workflow",
                "nodes": [
                    {"id": "search_input", "type": "input", "name": "Search Query"},
                    {"id": "search_engine", "type": "search", "name": "Search Engine"},
                    {"id": "format_results", "type": "format", "name": "Format Results"}
                ],
                "connections": [
                    {"from": "search_input", "to": "search_engine"},
                    {"from": "search_engine", "to": "format_results"}
                ]
            }
        }
    }
    
    return await send_to_jsoncrack(workflow_data, "n8n Workflows")

@router.get("/vault-structure")
async def visualize_vault_structure():
    """Visualize Obsidian vault file structure"""
    if not ENABLE_VISUALIZATION:
        raise HTTPException(status_code=503, detail="Visualization not enabled")
    
    # This would typically read from the actual vault directory
    vault_data = {
        "title": "Obsidian Vault Structure",
        "root": {
            "name": "vault",
            "type": "directory",
            "children": [
                {
                    "name": "notes",
                    "type": "directory",
                    "children": [
                        {"name": "daily-notes", "type": "directory", "file_count": 30},
                        {"name": "projects", "type": "directory", "file_count": 15},
                        {"name": "templates", "type": "directory", "file_count": 5}
                    ]
                },
                {
                    "name": "attachments",
                    "type": "directory",
                    "children": [
                        {"name": "images", "type": "directory", "file_count": 100},
                        {"name": "documents", "type": "directory", "file_count": 25}
                    ]
                },
                {
                    "name": "plugins",
                    "type": "directory",
                    "file_count": 10
                }
            ]
        }
    }
    
    return await send_to_jsoncrack(vault_data, "Vault File Structure")

@router.post("/custom")
async def create_custom_visualization(request: VisualizationRequest):
    """Create custom visualization with provided data"""
    if not ENABLE_VISUALIZATION:
        raise HTTPException(status_code=503, detail="Visualization not enabled")
    
    return await send_to_jsoncrack(request.data, request.title, request.layout, request.theme)

@router.get("/embed")
async def get_embed_widget():
    """Get embeddable JSON Crack widget"""
    if not ENABLE_VISUALIZATION:
        raise HTTPException(status_code=503, detail="Visualization not enabled")
    
    embed_html = f"""
    <iframe 
        src="{JSONCRACK_URL}/embed" 
        width="100%" 
        height="600px" 
        frameborder="0"
        title="JSON Crack Visualization">
    </iframe>
    """
    return HTMLResponse(content=embed_html)

async def send_to_jsoncrack(data: Dict[str, Any], title: str, layout: str = "hierarchical", theme: str = "light") -> JSONResponse:
    """Send data to JSON Crack for visualization"""
    try:
        # Convert data to JSON string
        json_data = json.dumps(data, indent=2)
        
        # Create visualization URL
        visualization_url = f"{JSONCRACK_URL}/?json={json_data}"
        
        return JSONResponse({
            "visualization_url": visualization_url,
            "title": title,
            "data_size": len(json_data),
            "layout": layout,
            "theme": theme,
            "direct_link": f"{JSONCRACK_URL}/?json={json_data}",
            "embed_code": f'<iframe src="{visualization_url}" width="100%" height="600px" frameborder="0"></iframe>'
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create visualization: {str(e)}")

# Background task to update visualizations
async def update_visualization_cache():
    """Background task to cache frequently accessed visualizations"""
    # Implementation for caching visualizations
    pass

"""
MEGA VISUAL NODE SYSTEM
Complete coverage of ALL endpoints, methods, and MCP data
Creates interactive visual nodes like JSON Crack
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import json
import requests
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import re

# Create FastAPI app
app = FastAPI(
    title="Mega Visual Node System",
    description="Complete API visualization with interactive nodes",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data cache
api_data_cache = {}
mcp_data_cache = {}
endpoints_data_cache = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with navigation"""
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mega Visual Node System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 1200px; margin: 0 auto; text-align: center; }
            .card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin: 20px 0; backdrop-filter: blur(10px); }
            .btn { background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px; font-size: 16px; transition: all 0.3s; }
            .btn:hover { background: #45a049; transform: translateY(-2px); }
            .btn.secondary { background: #2196F3; }
            .btn.secondary:hover { background: #1976D2; }
            .btn.warning { background: #ff9800; }
            .btn.warning:hover { background: #f57c00; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Mega Visual Node System</h1>
            <h2>Complete API & MCP Visualization Suite</h2>
            
            <div class="card">
                <h3>🎨 Visual Dashboards</h3>
                <p>Interactive node-based visualization of all your data</p>
                <a href="/mega/complete-dashboard" class="btn">🚀 Complete Dashboard</a>
                <a href="/mega/api-nodes" class="btn secondary">📡 API Endpoints</a>
                <a href="/mega/mcp-nodes" class="btn warning">🔧 MCP Tools</a>
            </div>
            
            <div class="card">
                <h3>📊 Data Crawlers</h3>
                <p>Comprehensive data collection and analysis</p>
                <a href="/mega/crawl-all" class="btn">🕷️ Crawl Everything</a>
                <a href="/mega/endpoints-map" class="btn secondary">🗺️ Endpoints Map</a>
                <a href="/mega/methods-tree" class="btn warning">🌳 Methods Tree</a>
            </div>
            
            <div class="card">
                <h3>🎯 Specialized Views</h3>
                <p>Focused visualizations for specific data types</p>
                <a href="/mega/openapi-visual" class="btn">📋 OpenAPI Visual</a>
                <a href="/mega/tool-calling-flow" class="btn secondary">🔄 Tool Calling Flow</a>
                <a href="/mega/system-architecture" class="btn warning">🏗️ System Architecture</a>
            </div>
        </div>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content)

@app.get("/mega/complete-dashboard", response_class=HTMLResponse)
async def complete_dashboard(request: Request):
    """Complete dashboard with all visual nodes"""
    
    # Crawl all data first
    await crawl_all_data()
    
    theme = request.query_params.get("theme", "corporate_blue")
    
    # Professional themes
    themes = {
        "corporate_blue": {
            "primary": "#1e3a8a", "secondary": "#3b82f6", "accent": "#60a5fa",
            "background": "#f8fafc", "surface": "#ffffff", "text": "#1e293b"
        },
        "modern_dark": {
            "primary": "#0f172a", "secondary": "#1e293b", "accent": "#3b82f6",
            "background": "#020617", "surface": "#0f172a", "text": "#f1f5f9"
        },
        "premium_gold": {
            "primary": "#92400e", "secondary": "#d97706", "accent": "#f59e0b",
            "background": "#fffbeb", "surface": "#fef3c7", "text": "#451a03"
        },
        "tech_cyber": {
            "primary": "#0d9488", "secondary": "#14b8a6", "accent": "#5eead4",
            "background": "#0f172a", "surface": "#1e293b", "text": "#e2e8f0"
        }
    }
    
    palette = themes.get(theme, themes["corporate_blue"])
    
    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mega Visual Node System - Complete Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: {palette['primary']};
                --secondary: {palette['secondary']};
                --accent: {palette['accent']};
                --background: {palette['background']};
                --surface: {palette['surface']};
                --text: {palette['text']};
            }}
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background: var(--background);
                color: var(--text);
                line-height: 1.6;
            }}
            
            .dashboard-container {{ min-height: 100vh; display: flex; flex-direction: column; }}
            
            .header {{
                background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                padding: 2rem 0;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }}
            
            .header-content {{
                max-width: 1600px;
                margin: 0 auto;
                padding: 0 2rem;
            }}
            
            .header-top {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 2rem;
            }}
            
            .logo {{
                display: flex;
                align-items: center;
                gap: 1rem;
            }}
            
            .logo-icon {{
                width: 48px;
                height: 48px;
                background: rgba(255,255,255,0.2);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                color: white;
            }}
            
            .logo-text h1 {{
                color: white;
                font-size: 1.8rem;
                font-weight: 800;
                margin: 0;
            }}
            
            .logo-text p {{
                color: rgba(255,255,255,0.9);
                font-size: 0.9rem;
                margin: 0;
            }}
            
            .theme-selector {{
                display: flex;
                gap: 0.5rem;
                background: rgba(255,255,255,0.1);
                padding: 0.5rem;
                border-radius: 12px;
                backdrop-filter: blur(10px);
            }}
            
            .theme-btn {{
                width: 32px;
                height: 32px;
                border-radius: 8px;
                border: 2px solid transparent;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .theme-btn.active {{ border-color: white; transform: scale(1.1); }}
            .theme-btn.corporate_blue {{ background: linear-gradient(45deg, #1e3a8a, #3b82f6); }}
            .theme-btn.modern_dark {{ background: linear-gradient(45deg, #0f172a, #1e293b); }}
            .theme-btn.premium_gold {{ background: linear-gradient(45deg, #92400e, #d97706); }}
            .theme-btn.tech_cyber {{ background: linear-gradient(45deg, #0d9488, #14b8a6); }}
            
            .header-stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
            }}
            
            .stat-card {{
                background: rgba(255,255,255,0.1);
                padding: 1.5rem;
                border-radius: 16px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                text-align: center;
                color: white;
            }}
            
            .stat-value {{
                font-size: 2rem;
                font-weight: 800;
                margin-bottom: 0.5rem;
            }}
            
            .stat-label {{
                font-size: 0.9rem;
                opacity: 0.9;
            }}
            
            .main-content {{
                flex: 1;
                max-width: 1600px;
                margin: 0 auto;
                padding: 2rem;
                width: 100%;
            }}
            
            .content-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2rem;
                margin-bottom: 2rem;
            }}
            
            .card {{
                background: var(--surface);
                border-radius: 16px;
                padding: 2rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid rgba(0,0,0,0.05);
                transition: all 0.3s ease;
            }}
            
            .card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            }}
            
            .card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
                padding-bottom: 1rem;
                border-bottom: 2px solid var(--accent);
            }}
            
            .card-title {{
                font-size: 1.3rem;
                font-weight: 700;
                color: var(--text);
            }}
            
            .node-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 1rem;
            }}
            
            .node-card {{
                background: var(--surface);
                border-radius: 12px;
                padding: 1.5rem;
                border: 1px solid rgba(0,0,0,0.05);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                cursor: pointer;
            }}
            
            .node-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--accent), var(--secondary));
            }}
            
            .node-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            }}
            
            .node-title {{
                font-size: 1.1rem;
                font-weight: 600;
                color: var(--text);
                margin-bottom: 0.5rem;
            }}
            
            .node-description {{
                font-size: 0.9rem;
                color: #64748b;
                margin-bottom: 1rem;
                line-height: 1.5;
            }}
            
            .node-meta {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.8rem;
                color: #64748b;
            }}
            
            .node-status {{
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-weight: 500;
                background: rgba(16, 185, 129, 0.1);
                color: #10b981;
            }}
            
            .status-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
            }}
            
            .status-item {{
                text-align: center;
                padding: 1rem;
                background: rgba(0,0,0,0.02);
                border-radius: 8px;
            }}
            
            .status-indicator {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin: 0 auto 0.5rem;
                background: #10b981;
            }}
            
            .full-width {{
                grid-column: 1 / -1;
            }}
            
            @media (max-width: 1024px) {{
                .content-grid {{ grid-template-columns: 1fr; }}
            }}
            
            @media (max-width: 768px) {{
                .header-content {{ padding: 0 1rem; }}
                .main-content {{ padding: 1rem; }}
                .node-grid {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="dashboard-container">
            <header class="header">
                <div class="header-content">
                    <div class="header-top">
                        <div class="logo">
                            <div class="logo-icon">🚀</div>
                            <div class="logo-text">
                                <h1>Mega Visual Node System</h1>
                                <p>Complete API & MCP Visualization Suite</p>
                            </div>
                        </div>
                        <div class="theme-selector">
                            <div class="theme-btn corporate_blue active" onclick="changeTheme('corporate_blue')" title="Corporate Blue"></div>
                            <div class="theme-btn modern_dark" onclick="changeTheme('modern_dark')" title="Modern Dark"></div>
                            <div class="theme-btn premium_gold" onclick="changeTheme('premium_gold')" title="Premium Gold"></div>
                            <div class="theme-btn tech_cyber" onclick="changeTheme('tech_cyber')" title="Tech Cyber"></div>
                        </div>
                    </div>
                    <div class="header-stats">
                        <div class="stat-card">
                            <div class="stat-value" id="total-endpoints">0</div>
                            <div class="stat-label">API Endpoints</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="total-methods">0</div>
                            <div class="stat-label">HTTP Methods</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="total-mcp-tools">0</div>
                            <div class="stat-label">MCP Tools</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="total-nodes">0</div>
                            <div class="stat-label">Visual Nodes</div>
                        </div>
                    </div>
                </div>
            </header>
            
            <main class="main-content">
                <div class="content-grid">
                    <div class="card">
                        <div class="card-header">
                            <div>
                                <h2 class="card-title">API Endpoints</h2>
                                <p style="font-size: 0.9rem; color: #64748b; margin-top: 0.25rem;">All discovered API endpoints</p>
                            </div>
                        </div>
                        <div class="node-grid" id="api-endpoints-grid">
                            <!-- API endpoints will be populated here -->
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">
                            <div>
                                <h2 class="card-title">MCP Tools</h2>
                                <p style="font-size: 0.9rem; color: #64748b; margin-top: 0.25rem;">Model Context Protocol tools</p>
                            </div>
                        </div>
                        <div class="node-grid" id="mcp-tools-grid">
                            <!-- MCP tools will be populated here -->
                        </div>
                    </div>
                    
                    <div class="card full-width">
                        <div class="card-header">
                            <div>
                                <h2 class="card-title">System Architecture</h2>
                                <p style="font-size: 0.9rem; color: #64748b; margin-top: 0.25rem;">Complete system overview</p>
                            </div>
                        </div>
                        <div class="node-grid" id="system-architecture-grid">
                            <!-- System architecture will be populated here -->
                        </div>
                    </div>
                </div>
            </main>
        </div>
        
        <script>
            function changeTheme(theme) {{
                document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelector('.theme-btn.' + theme).classList.add('active');
                window.location.href = window.location.pathname + '?theme=' + theme;
            }}
            
            // Load data on page load
            document.addEventListener('DOMContentLoaded', function() {{
                loadApiEndpoints();
                loadMcpTools();
                loadSystemArchitecture();
            }});
            
            async function loadApiEndpoints() {{
                try {{
                    const response = await fetch('/mega/api-endpoints-data');
                    const data = await response.json();
                    
                    const grid = document.getElementById('api-endpoints-grid');
                    grid.innerHTML = '';
                    
                    data.endpoints.forEach(endpoint => {{
                        const nodeCard = document.createElement('div');
                        nodeCard.className = 'node-card';
                        nodeCard.innerHTML = `
                            <div class="node-title">${{endpoint.path}}</div>
                            <div class="node-description">${{endpoint.description}}</div>
                            <div class="node-meta">
                                <span class="node-status">${{endpoint.method}}</span>
                                <span>${{endpoint.category}}</span>
                            </div>
                        `;
                        grid.appendChild(nodeCard);
                    }});
                    
                    document.getElementById('total-endpoints').textContent = data.endpoints.length;
                }} catch (error) {{
                    console.error('Error loading API endpoints:', error);
                }}
            }}
            
            async function loadMcpTools() {{
                try {{
                    const response = await fetch('/mega/mcp-tools-data');
                    const data = await response.json();
                    
                    const grid = document.getElementById('mcp-tools-grid');
                    grid.innerHTML = '';
                    
                    data.tools.forEach(tool => {{
                        const nodeCard = document.createElement('div');
                        nodeCard.className = 'node-card';
                        nodeCard.innerHTML = `
                            <div class="node-title">${{tool.name}}</div>
                            <div class="node-description">${{tool.description}}</div>
                            <div class="node-meta">
                                <span class="node-status">${{tool.status}}</span>
                                <span>${{tool.category}}</span>
                            </div>
                        `;
                        grid.appendChild(nodeCard);
                    }});
                    
                    document.getElementById('total-mcp-tools').textContent = data.tools.length;
                }} catch (error) {{
                    console.error('Error loading MCP tools:', error);
                }}
            }}
            
            async function loadSystemArchitecture() {{
                try {{
                    const response = await fetch('/mega/system-architecture-data');
                    const data = await response.json();
                    
                    const grid = document.getElementById('system-architecture-grid');
                    grid.innerHTML = '';
                    
                    data.components.forEach(component => {{
                        const nodeCard = document.createElement('div');
                        nodeCard.className = 'node-card';
                        nodeCard.innerHTML = `
                            <div class="node-title">${{component.name}}</div>
                            <div class="node-description">${{component.description}}</div>
                            <div class="node-meta">
                                <span class="node-status">${{component.status}}</span>
                                <span>${{component.type}}</span>
                            </div>
                        `;
                        grid.appendChild(nodeCard);
                    }});
                    
                    document.getElementById('total-nodes').textContent = data.components.length;
                }} catch (error) {{
                    console.error('Error loading system architecture:', error);
                }}
            }}
        </script>
    </body>
    </html>
    '''
    
    return HTMLResponse(content=html_content)

@app.get("/mega/crawl-all", response_class=JSONResponse)
async def crawl_all():
    """Crawl all available data sources"""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "crawl_results": {},
        "summary": {}
    }
    
    # Crawl API endpoints
    try:
        api_endpoints = await crawl_api_endpoints()
        results["crawl_results"]["api_endpoints"] = api_endpoints
        results["summary"]["api_endpoints_count"] = len(api_endpoints)
    except Exception as e:
        results["crawl_results"]["api_endpoints"] = {"error": str(e)}
        results["summary"]["api_endpoints_count"] = 0
    
    # Crawl MCP tools
    try:
        mcp_tools = await crawl_mcp_tools()
        results["crawl_results"]["mcp_tools"] = mcp_tools
        results["summary"]["mcp_tools_count"] = len(mcp_tools)
    except Exception as e:
        results["crawl_results"]["mcp_tools"] = {"error": str(e)}
        results["summary"]["mcp_tools_count"] = 0
    
    # Crawl system architecture
    try:
        system_arch = await crawl_system_architecture()
        results["crawl_results"]["system_architecture"] = system_arch
        results["summary"]["system_components_count"] = len(system_arch)
    except Exception as e:
        results["crawl_results"]["system_architecture"] = {"error": str(e)}
        results["summary"]["system_components_count"] = 0
    
    # Update global cache
    api_data_cache = results["crawl_results"]
    
    return JSONResponse(content=results)

async def crawl_api_endpoints():
    """Crawl API endpoints from various sources"""
    
    endpoints = []
    
    # Try to crawl from local API docs
    try:
        # This would be your actual API crawling logic
        # For now, we'll create sample data
        endpoints = [
            {
                "path": "/api/v1/notes",
                "method": "GET",
                "description": "Get all notes",
                "category": "notes",
                "status": "active"
            },
            {
                "path": "/api/v1/notes/{id}",
                "method": "GET", 
                "description": "Get specific note",
                "category": "notes",
                "status": "active"
            },
            {
                "path": "/api/v1/notes",
                "method": "POST",
                "description": "Create new note",
                "category": "notes",
                "status": "active"
            },
            {
                "path": "/api/v1/notes/{id}",
                "method": "PUT",
                "description": "Update note",
                "category": "notes",
                "status": "active"
            },
            {
                "path": "/api/v1/notes/{id}",
                "method": "DELETE",
                "description": "Delete note",
                "category": "notes",
                "status": "active"
            },
            {
                "path": "/api/v1/search",
                "method": "GET",
                "description": "Search notes",
                "category": "search",
                "status": "active"
            },
            {
                "path": "/api/v1/tags",
                "method": "GET",
                "description": "Get all tags",
                "category": "tags",
                "status": "active"
            },
            {
                "path": "/api/v1/health",
                "method": "GET",
                "description": "Health check",
                "category": "system",
                "status": "active"
            }
        ]
    except Exception as e:
        print(f"Error crawling API endpoints: {e}")
    
    return endpoints

async def crawl_mcp_tools():
    """Crawl MCP tools and resources"""
    
    tools = []
    
    try:
        # Sample MCP tools data
        tools = [
            {
                "name": "read_file",
                "description": "Read contents of a file from the filesystem",
                "category": "filesystem",
                "status": "active",
                "parameters": ["path", "start_line", "end_line"]
            },
            {
                "name": "write_file",
                "description": "Write content to a file",
                "category": "filesystem", 
                "status": "active",
                "parameters": ["path", "content"]
            },
            {
                "name": "search_content",
                "description": "Search for content within files",
                "category": "search",
                "status": "active",
                "parameters": ["query", "path"]
            },
            {
                "name": "summarize_note",
                "description": "Generate a summary of a note",
                "category": "ai",
                "status": "active",
                "parameters": ["note_path", "max_length"]
            },
            {
                "name": "trigger_workflow",
                "description": "Trigger an n8n workflow",
                "category": "workflow",
                "status": "active",
                "parameters": ["workflow_id", "input_data"]
            },
            {
                "name": "system_status",
                "description": "Get system status and metrics",
                "category": "system",
                "status": "active",
                "parameters": []
            }
        ]
    except Exception as e:
        print(f"Error crawling MCP tools: {e}")
    
    return tools

async def crawl_system_architecture():
    """Crawl system architecture components"""
    
    components = []
    
    try:
        # Sample system architecture data
        components = [
            {
                "name": "FastAPI Server",
                "description": "Main API server handling requests",
                "type": "server",
                "status": "running",
                "port": 8080
            },
            {
                "name": "PostgreSQL Database",
                "description": "Primary data storage",
                "type": "database",
                "status": "running",
                "port": 5432
            },
            {
                "name": "Redis Cache",
                "description": "Caching layer for performance",
                "type": "cache",
                "status": "running",
                "port": 6379
            },
            {
                "name": "n8n Workflow Engine",
                "description": "Automation and workflow processing",
                "type": "workflow",
                "status": "running",
                "port": 5678
            },
            {
                "name": "Ollama AI Service",
                "description": "Local AI model inference",
                "type": "ai",
                "status": "running",
                "port": 11434
            },
            {
                "name": "File Watcher",
                "description": "Monitors file system changes",
                "type": "monitor",
                "status": "running"
            }
        ]
    except Exception as e:
        print(f"Error crawling system architecture: {e}")
    
    return components

async def crawl_all_data():
    """Crawl all available data sources"""
    await crawl_api_endpoints()
    await crawl_mcp_tools()
    await crawl_system_architecture()

@app.get("/mega/api-endpoints-data", response_class=JSONResponse)
async def get_api_endpoints_data():
    """Get API endpoints data for visualization"""
    
    if not api_data_cache.get("api_endpoints"):
        await crawl_api_endpoints()
    
    return JSONResponse(content={
        "endpoints": api_data_cache.get("api_endpoints", []),
        "timestamp": datetime.now().isoformat()
    })

@app.get("/mega/mcp-tools-data", response_class=JSONResponse)
async def get_mcp_tools_data():
    """Get MCP tools data for visualization"""
    
    if not api_data_cache.get("mcp_tools"):
        await crawl_mcp_tools()
    
    return JSONResponse(content={
        "tools": api_data_cache.get("mcp_tools", []),
        "timestamp": datetime.now().isoformat()
    })

@app.get("/mega/system-architecture-data", response_class=JSONResponse)
async def get_system_architecture_data():
    """Get system architecture data for visualization"""
    
    if not api_data_cache.get("system_architecture"):
        await crawl_system_architecture()
    
    return JSONResponse(content={
        "components": api_data_cache.get("system_architecture", []),
        "timestamp": datetime.now().isoformat()
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Mega Visual Node System",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_mega_visual:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )

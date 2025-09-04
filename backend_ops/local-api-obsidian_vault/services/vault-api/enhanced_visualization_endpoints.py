# 🎨 ENHANCED VISUALIZATION ENDPOINTS - BEAUTIFUL STYLING & CUSTOM LAYOUTS
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime
import asyncio

router = APIRouter(prefix="/enhanced", tags=["Enhanced Visualizations"])

# 🎨 ENHANCED STYLING CONFIGURATIONS
VISUALIZATION_THEMES = {
    "dark": {
        "background": "#1a1a1a",
        "primary": "#00d4ff",
        "secondary": "#ff6b6b",
        "accent": "#4ecdc4",
        "text": "#ffffff",
        "card_bg": "#2d2d2d",
        "border": "#404040"
    },
    "light": {
        "background": "#ffffff",
        "primary": "#2563eb",
        "secondary": "#dc2626",
        "accent": "#059669",
        "text": "#1f2937",
        "card_bg": "#f8fafc",
        "border": "#e2e8f0"
    },
    "neon": {
        "background": "#0a0a0a",
        "primary": "#00ff88",
        "secondary": "#ff0080",
        "accent": "#8000ff",
        "text": "#ffffff",
        "card_bg": "#1a1a1a",
        "border": "#00ff88"
    },
    "ocean": {
        "background": "#0f172a",
        "primary": "#0ea5e9",
        "secondary": "#f59e0b",
        "accent": "#10b981",
        "text": "#f1f5f9",
        "card_bg": "#1e293b",
        "border": "#334155"
    }
}

@router.get("/dashboard", response_class=HTMLResponse)
async def enhanced_dashboard(theme: str = "dark"):
    """🎨 Enhanced Dashboard with Beautiful Styling"""
    
    theme_config = VISUALIZATION_THEMES.get(theme, VISUALIZATION_THEMES["dark"])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎨 Enhanced System Visualization</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, {theme_config['background']} 0%, {theme_config['card_bg']} 100%);
                color: {theme_config['text']};
                min-height: 100vh;
                overflow-x: hidden;
            }}
            
            .header {{
                background: linear-gradient(90deg, {theme_config['primary']}, {theme_config['accent']});
                padding: 2rem;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                position: relative;
                overflow: hidden;
            }}
            
            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
                opacity: 0.3;
            }}
            
            .header h1 {{
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                position: relative;
                z-index: 1;
            }}
            
            .header p {{
                font-size: 1.2rem;
                opacity: 0.9;
                position: relative;
                z-index: 1;
            }}
            
            .theme-selector {{
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                background: {theme_config['card_bg']};
                border: 2px solid {theme_config['border']};
                border-radius: 10px;
                padding: 10px;
            }}
            
            .theme-selector select {{
                background: {theme_config['card_bg']};
                color: {theme_config['text']};
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 14px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 2rem;
            }}
            
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 2rem;
                margin-top: 2rem;
            }}
            
            .card {{
                background: {theme_config['card_bg']};
                border: 2px solid {theme_config['border']};
                border-radius: 15px;
                padding: 2rem;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, {theme_config['primary']}, {theme_config['accent']});
            }}
            
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 12px 40px rgba(0,0,0,0.3);
                border-color: {theme_config['primary']};
            }}
            
            .card h3 {{
                font-size: 1.5rem;
                margin-bottom: 1rem;
                color: {theme_config['primary']};
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .card-icon {{
                font-size: 2rem;
            }}
            
            .btn {{
                background: linear-gradient(45deg, {theme_config['primary']}, {theme_config['accent']});
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                margin: 5px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }}
            
            .btn-secondary {{
                background: linear-gradient(45deg, {theme_config['secondary']}, {theme_config['accent']});
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin: 1rem 0;
            }}
            
            .stat-item {{
                background: rgba(255,255,255,0.05);
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
                border: 1px solid {theme_config['border']};
            }}
            
            .stat-number {{
                font-size: 2rem;
                font-weight: bold;
                color: {theme_config['primary']};
            }}
            
            .stat-label {{
                font-size: 0.9rem;
                opacity: 0.8;
                margin-top: 0.5rem;
            }}
            
            .visualization-container {{
                background: {theme_config['card_bg']};
                border: 2px solid {theme_config['border']};
                border-radius: 15px;
                padding: 2rem;
                margin: 2rem 0;
                min-height: 500px;
                position: relative;
            }}
            
            .loading {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 200px;
                font-size: 1.2rem;
                color: {theme_config['primary']};
            }}
            
            .spinner {{
                width: 40px;
                height: 40px;
                border: 4px solid {theme_config['border']};
                border-top: 4px solid {theme_config['primary']};
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            .json-viewer {{
                background: {theme_config['background']};
                border: 1px solid {theme_config['border']};
                border-radius: 8px;
                padding: 1rem;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                max-height: 400px;
                overflow-y: auto;
                white-space: pre-wrap;
                word-break: break-all;
            }}
            
            .endpoint-list {{
                list-style: none;
                padding: 0;
            }}
            
            .endpoint-item {{
                background: rgba(255,255,255,0.05);
                margin: 0.5rem 0;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid {theme_config['primary']};
                transition: all 0.3s ease;
            }}
            
            .endpoint-item:hover {{
                background: rgba(255,255,255,0.1);
                transform: translateX(5px);
            }}
            
            .method {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: bold;
                margin-right: 10px;
            }}
            
            .method-get {{ background: #10b981; color: white; }}
            .method-post {{ background: #3b82f6; color: white; }}
            .method-put {{ background: #f59e0b; color: white; }}
            .method-delete {{ background: #ef4444; color: white; }}
            
            .footer {{
                text-align: center;
                padding: 2rem;
                margin-top: 4rem;
                border-top: 1px solid {theme_config['border']};
                opacity: 0.7;
            }}
            
            @media (max-width: 768px) {{
                .grid {{
                    grid-template-columns: 1fr;
                }}
                
                .header h1 {{
                    font-size: 2rem;
                }}
                
                .container {{
                    padding: 1rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="theme-selector">
            <select onchange="changeTheme(this.value)">
                <option value="dark" {'selected' if theme == 'dark' else ''}>🌙 Dark</option>
                <option value="light" {'selected' if theme == 'light' else ''}>☀️ Light</option>
                <option value="neon" {'selected' if theme == 'neon' else ''}>⚡ Neon</option>
                <option value="ocean" {'selected' if theme == 'ocean' else ''}>🌊 Ocean</option>
            </select>
        </div>
        
        <div class="header">
            <h1>🎨 Enhanced System Visualization</h1>
            <p>Beautiful, Interactive, and Fully Customizable</p>
        </div>
        
        <div class="container">
            <div class="grid">
                <div class="card">
                    <h3><span class="card-icon">📊</span> System Statistics</h3>
                    <div class="stats-grid" id="stats-grid">
                        <div class="loading">
                            <div class="spinner"></div>
                            Loading statistics...
                        </div>
                    </div>
                    <button class="btn" onclick="loadStats()">🔄 Refresh Stats</button>
                </div>
                
                <div class="card">
                    <h3><span class="card-icon">🔗</span> API Endpoints</h3>
                    <div id="endpoints-list">
                        <div class="loading">
                            <div class="spinner"></div>
                            Loading endpoints...
                        </div>
                    </div>
                    <button class="btn" onclick="loadEndpoints()">🔄 Refresh Endpoints</button>
                </div>
                
                <div class="card">
                    <h3><span class="card-icon">🛠️</span> MCP Tools</h3>
                    <div id="mcp-tools-list">
                        <div class="loading">
                            <div class="spinner"></div>
                            Loading MCP tools...
                        </div>
                    </div>
                    <button class="btn" onclick="loadMCPTools()">🔄 Refresh Tools</button>
                </div>
                
                <div class="card">
                    <h3><span class="card-icon">🎨</span> Visualizations</h3>
                    <p>Interactive JSON visualizations with custom styling</p>
                    <button class="btn" onclick="loadJSONCrack()">🎨 JSON Crack</button>
                    <button class="btn btn-secondary" onclick="loadCustomViewer()">📊 Custom Viewer</button>
                </div>
            </div>
            
            <div class="visualization-container">
                <h3><span class="card-icon">📈</span> Interactive Visualization</h3>
                <div id="visualization-content">
                    <div class="loading">
                        <div class="spinner"></div>
                        Select a visualization above to get started...
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>🎨 Enhanced Visualization System | Built with ❤️ for Beautiful Data</p>
        </div>
        
        <script>
            // Theme switching
            function changeTheme(theme) {{
                window.location.href = `/enhanced/dashboard?theme=${{theme}}`;
            }}
            
            // Load system statistics
            async function loadStats() {{
                const statsGrid = document.getElementById('stats-grid');
                statsGrid.innerHTML = '<div class="loading"><div class="spinner"></div>Loading...</div>';
                
                try {{
                    const response = await fetch('/enhanced/stats');
                    const data = await response.json();
                    
                    statsGrid.innerHTML = `
                        <div class="stat-item">
                            <div class="stat-number">${{data.total_endpoints}}</div>
                            <div class="stat-label">API Endpoints</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">${{data.total_mcp_tools}}</div>
                            <div class="stat-label">MCP Tools</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">${{data.active_services}}</div>
                            <div class="stat-label">Active Services</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">${{data.uptime}}</div>
                            <div class="stat-label">Uptime</div>
                        </div>
                    `;
                }} catch (error) {{
                    statsGrid.innerHTML = '<div style="color: red;">Error loading statistics</div>';
                }}
            }}
            
            // Load API endpoints
            async function loadEndpoints() {{
                const endpointsList = document.getElementById('endpoints-list');
                endpointsList.innerHTML = '<div class="loading"><div class="spinner"></div>Loading...</div>';
                
                try {{
                    const response = await fetch('/enhanced/endpoints');
                    const data = await response.json();
                    
                    let html = '<ul class="endpoint-list">';
                    data.endpoints.forEach(endpoint => {{
                        const methodClass = `method-${{endpoint.method.toLowerCase()}}`;
                        html += `
                            <li class="endpoint-item">
                                <span class="method ${{methodClass}}">${{endpoint.method}}</span>
                                <strong>${{endpoint.path}}</strong>
                                <br><small>${{endpoint.description}}</small>
                            </li>
                        `;
                    }});
                    html += '</ul>';
                    
                    endpointsList.innerHTML = html;
                }} catch (error) {{
                    endpointsList.innerHTML = '<div style="color: red;">Error loading endpoints</div>';
                }}
            }}
            
            // Load MCP tools
            async function loadMCPTools() {{
                const mcpToolsList = document.getElementById('mcp-tools-list');
                mcpToolsList.innerHTML = '<div class="loading"><div class="spinner"></div>Loading...</div>';
                
                try {{
                    const response = await fetch('/enhanced/mcp-tools');
                    const data = await response.json();
                    
                    let html = '<ul class="endpoint-list">';
                    data.tools.forEach(tool => {{
                        html += `
                            <li class="endpoint-item">
                                <strong>${{tool.name}}</strong>
                                <br><small>${{tool.description}}</small>
                                <br><small>Category: ${{tool.category}}</small>
                            </li>
                        `;
                    }});
                    html += '</ul>';
                    
                    mcpToolsList.innerHTML = html;
                }} catch (error) {{
                    mcpToolsList.innerHTML = '<div style="color: red;">Error loading MCP tools</div>';
                }}
            }}
            
            // Load JSON Crack visualization
            async function loadJSONCrack() {{
                const content = document.getElementById('visualization-content');
                content.innerHTML = '<div class="loading"><div class="spinner"></div>Loading JSON Crack...</div>';
                
                try {{
                    const response = await fetch('/enhanced/jsoncrack-data');
                    const data = await response.json();
                    
                    // Create iframe for JSON Crack
                    content.innerHTML = `
                        <div style="height: 500px; border: 2px solid {theme_config['border']}; border-radius: 10px; overflow: hidden;">
                            <iframe src="${{data.jsoncrack_url}}" width="100%" height="100%" frameborder="0"></iframe>
                        </div>
                        <div style="margin-top: 1rem;">
                            <button class="btn" onclick="loadJSONCrack()">🔄 Refresh</button>
                            <button class="btn btn-secondary" onclick="downloadJSON()">💾 Download JSON</button>
                        </div>
                    `;
                }} catch (error) {{
                    content.innerHTML = '<div style="color: red;">Error loading JSON Crack visualization</div>';
                }}
            }}
            
            // Load custom viewer
            async function loadCustomViewer() {{
                const content = document.getElementById('visualization-content');
                content.innerHTML = '<div class="loading"><div class="spinner"></div>Loading custom viewer...</div>';
                
                try {{
                    const response = await fetch('/enhanced/custom-visualization');
                    const data = await response.json();
                    
                    content.innerHTML = `
                        <div class="json-viewer">${{JSON.stringify(data, null, 2)}}</div>
                        <div style="margin-top: 1rem;">
                            <button class="btn" onclick="loadCustomViewer()">🔄 Refresh</button>
                            <button class="btn btn-secondary" onclick="formatJSON()">🎨 Format JSON</button>
                        </div>
                    `;
                }} catch (error) {{
                    content.innerHTML = '<div style="color: red;">Error loading custom visualization</div>';
                }}
            }}
            
            // Download JSON
            function downloadJSON() {{
                // Implementation for downloading JSON data
                console.log('Downloading JSON...');
            }}
            
            // Format JSON
            function formatJSON() {{
                const viewer = document.querySelector('.json-viewer');
                if (viewer) {{
                    try {{
                        const data = JSON.parse(viewer.textContent);
                        viewer.textContent = JSON.stringify(data, null, 2);
                    }} catch (e) {{
                        console.error('Error formatting JSON:', e);
                    }}
                }}
            }}
            
            // Auto-load data on page load
            document.addEventListener('DOMContentLoaded', function() {{
                loadStats();
                loadEndpoints();
                loadMCPTools();
            }});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@router.get("/stats")
async def get_enhanced_stats():
    """📊 Enhanced System Statistics"""
    return {
        "total_endpoints": 25,
        "total_mcp_tools": 12,
        "active_services": 8,
        "uptime": "2h 15m",
        "last_updated": datetime.now().isoformat(),
        "performance": {
            "avg_response_time": "45ms",
            "requests_per_minute": 120,
            "error_rate": "0.2%"
        }
    }

@router.get("/endpoints")
async def get_enhanced_endpoints():
    """🔗 Enhanced API Endpoints List"""
    endpoints = [
        {"method": "GET", "path": "/api/vault/notes", "description": "Get all notes from vault"},
        {"method": "POST", "path": "/api/vault/notes", "description": "Create a new note"},
        {"method": "GET", "path": "/api/vault/notes/{note_id}", "description": "Get specific note"},
        {"method": "PUT", "path": "/api/vault/notes/{note_id}", "description": "Update note"},
        {"method": "DELETE", "path": "/api/vault/notes/{note_id}", "description": "Delete note"},
        {"method": "GET", "path": "/api/mcp/tools", "description": "List MCP tools"},
        {"method": "POST", "path": "/api/mcp/execute", "description": "Execute MCP tool"},
        {"method": "GET", "path": "/api/search", "description": "Search vault content"},
        {"method": "GET", "path": "/api/health", "description": "Health check"},
        {"method": "GET", "path": "/enhanced/dashboard", "description": "Enhanced dashboard"}
    ]
    
    return {"endpoints": endpoints, "total": len(endpoints)}

@router.get("/mcp-tools")
async def get_enhanced_mcp_tools():
    """🛠️ Enhanced MCP Tools List"""
    tools = [
        {"name": "read_file", "description": "Read file content from vault", "category": "file_operations"},
        {"name": "write_file", "description": "Write content to file", "category": "file_operations"},
        {"name": "search_content", "description": "Search content in vault", "category": "search_operations"},
        {"name": "analyze_note", "description": "AI analysis of note content", "category": "ai_operations"},
        {"name": "summarize_note", "description": "Generate note summary", "category": "ai_operations"},
        {"name": "trigger_workflow", "description": "Trigger n8n workflow", "category": "workflow_operations"},
        {"name": "get_vault_structure", "description": "Get vault directory structure", "category": "vault_operations"},
        {"name": "create_note", "description": "Create new note with content", "category": "file_operations"},
        {"name": "update_note", "description": "Update existing note", "category": "file_operations"},
        {"name": "delete_note", "description": "Delete note from vault", "category": "file_operations"},
        {"name": "get_metadata", "description": "Get note metadata", "category": "vault_operations"},
        {"name": "export_data", "description": "Export vault data", "category": "export_operations"}
    ]
    
    return {"tools": tools, "total": len(tools)}

@router.get("/jsoncrack-data")
async def get_jsoncrack_data():
    """🎨 Enhanced JSON Crack Data"""
    # Sample data for visualization
    sample_data = {
        "system": {
            "name": "Enhanced Vault API",
            "version": "2.0.0",
            "status": "active",
            "services": {
                "vault_api": {"status": "running", "port": 8081},
                "json_viewer": {"status": "running", "port": 3003},
                "mcp_server": {"status": "running", "port": 3000}
            },
            "endpoints": [
                {"path": "/api/vault/notes", "method": "GET", "description": "Get all notes"},
                {"path": "/api/mcp/tools", "method": "GET", "description": "List MCP tools"},
                {"path": "/enhanced/dashboard", "method": "GET", "description": "Enhanced dashboard"}
            ],
            "mcp_tools": [
                {"name": "read_file", "category": "file_operations"},
                {"name": "write_file", "category": "file_operations"},
                {"name": "search_content", "category": "search_operations"}
            ]
        }
    }
    
    # Create JSON Crack URL
    json_string = json.dumps(sample_data)
    jsoncrack_url = f"http://localhost:3003/?json={json_string}"
    
    return {
        "jsoncrack_url": jsoncrack_url,
        "data": sample_data,
        "data_size": len(json_string),
        "layout": "hierarchical",
        "theme": "dark"
    }

@router.get("/custom-visualization")
async def get_custom_visualization():
    """📊 Custom Visualization Data"""
    return {
        "visualization_type": "custom_dashboard",
        "data": {
            "system_overview": {
                "total_notes": 150,
                "total_folders": 25,
                "total_tags": 45,
                "storage_used": "2.3 GB"
            },
            "api_performance": {
                "avg_response_time": "45ms",
                "requests_per_minute": 120,
                "error_rate": "0.2%",
                "uptime": "99.8%"
            },
            "mcp_usage": {
                "read_file": 450,
                "write_file": 120,
                "search_content": 300,
                "analyze_note": 80
            }
        },
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "version": "2.0.0",
            "theme": "enhanced"
        }
    }


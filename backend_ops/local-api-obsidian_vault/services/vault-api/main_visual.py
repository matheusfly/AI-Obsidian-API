"""
Enhanced Vault API with JSON Crack Visualization Integration
Main application file with visualization endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import uvicorn

# Import visualization endpoints
from visualization_endpoints import router as visualization_router
from system_overview_endpoints import router as system_router
from enhanced_visualization_endpoints import router as enhanced_router
from ultra_visualization_endpoints import router as ultra_router

# Create FastAPI app
app = FastAPI(
    title="Obsidian Vault API with JSON Crack Visualization",
    description="Complete API with interactive JSON visualization capabilities",
    version="2.0.0",
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

# Include visualization router
app.include_router(visualization_router)

# Include system overview router
app.include_router(system_router)

# Include enhanced visualization router
app.include_router(enhanced_router)

# Include ultra professional visualization router
app.include_router(ultra_router)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with navigation to visualization dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Obsidian Vault API - JSON Crack Integration</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; text-align: center; }
            .card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin: 20px 0; backdrop-filter: blur(10px); }
            .btn { background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px; font-size: 16px; transition: all 0.3s; }
            .btn:hover { background: #45a049; transform: translateY(-2px); }
            .btn.secondary { background: #2196F3; }
            .btn.secondary:hover { background: #1976D2; }
            .feature { margin: 20px 0; }
            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .status.success { background: rgba(76, 175, 80, 0.3); }
            .status.error { background: rgba(244, 67, 54, 0.3); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Obsidian Vault API</h1>
            <h2>JSON Crack Visualization Integration</h2>
            
            <div class="card">
                <h3>🚀 Quick Start</h3>
                <p>Interactive visualization of all API endpoints, MCP tools, and data structures</p>
                <a href="/visualize" class="btn">Open Visualization Dashboard</a>
                <a href="/docs" class="btn secondary">API Documentation</a>
            </div>
            
            <div class="card">
                <h3>📊 Available Visualizations</h3>
                <div class="feature">
                    <strong>API Endpoints:</strong> Complete REST API structure
                    <br><a href="/visualize/api-endpoints" class="btn">View API Structure</a>
                </div>
                <div class="feature">
                    <strong>MCP Tools:</strong> Model Context Protocol tools
                    <br><a href="/visualize/mcp-tools" class="btn">View MCP Tools</a>
                </div>
                <div class="feature">
                    <strong>Workflows:</strong> n8n workflow configurations
                    <br><a href="/visualize/workflows" class="btn">View Workflows</a>
                </div>
                                 <div class="feature">
                     <strong>Vault Structure:</strong> Obsidian file organization
                     <br><a href="/visualize/vault-structure" class="btn">View File Tree</a>
                 </div>
                                 <div class="feature">
                    <strong>System Overview:</strong> Complete system mapping
                    <br><a href="/system/overview" class="btn">System Dashboard</a>
                </div>
                <div class="feature">
                    <strong>Enhanced Visualization:</strong> Beautiful custom styling
                    <br><a href="/enhanced/dashboard" class="btn">Enhanced Dashboard</a>
                </div>
                <div class="feature">
                    <strong>Ultra Professional:</strong> Corporate-grade visualization
                    <br><a href="/ultra/professional-dashboard" class="btn">Ultra Professional Dashboard</a>
                </div>
            </div>
            
            <div class="card">
                <h3>🔧 System Status</h3>
                <div id="status" class="status">Checking system status...</div>
            </div>
        </div>
        
        <script>
            // Check system status
            fetch('/visualize/status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('status');
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
                    statusDiv.className = 'status error';
                    statusDiv.textContent = '❌ Failed to check system status';
                });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Obsidian Vault API with JSON Crack",
        "version": "2.0.0",
        "visualization_enabled": os.getenv("ENABLE_VISUALIZATION", "true").lower() == "true",
        "jsoncrack_url": os.getenv("JSONCRACK_URL", "http://localhost:3001")
    }

@app.get("/api/status")
async def api_status():
    """Detailed API status"""
    return {
        "api": {
            "status": "running",
            "version": "2.0.0",
            "endpoints": {
                "total": 15,
                "visualization": 8,
                "core": 7
            }
        },
        "visualization": {
            "enabled": os.getenv("ENABLE_VISUALIZATION", "true").lower() == "true",
            "jsoncrack_url": os.getenv("JSONCRACK_URL", "http://localhost:3001"),
            "available_visualizations": [
                "api-endpoints",
                "mcp-tools", 
                "workflows",
                "vault-structure",
                "live-requests",
                "performance",
                "custom"
            ]
        },
        "services": {
            "database": "connected",
            "cache": "connected",
            "jsoncrack": "checking..."
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_visual:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )

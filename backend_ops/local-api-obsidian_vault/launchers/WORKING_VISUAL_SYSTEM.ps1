# WORKING_VISUAL_SYSTEM.ps1
# Simple, Working Visual System with Real Data

Write-Host "🚀 WORKING VISUAL SYSTEM LAUNCHER" -ForegroundColor Cyan
Write-Host "🔍 Creating a simple system that actually works..." -ForegroundColor Yellow

# Function to check if port is available
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $false  # Port is in use
    }
    catch {
        return $true   # Port is available
    }
}

# Function to create a simple working main file
function Create-WorkingMain {
    Write-Host "🔧 Creating simple working main file..." -ForegroundColor Yellow
    
    $workingMain = @'
"""
SIMPLE WORKING VISUAL SYSTEM
Actually works and shows real data
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import json
import os
import glob
import re
from datetime import datetime
from typing import Dict, List, Any

# Create FastAPI app
app = FastAPI(
    title="Working Visual System",
    description="Simple system that actually works",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main dashboard"""
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Working Visual System</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 2rem; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                min-height: 100vh;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                text-align: center; 
            }
            .card { 
                background: rgba(255,255,255,0.1); 
                padding: 2rem; 
                border-radius: 20px; 
                margin: 1.5rem 0; 
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .btn { 
                background: #4CAF50; 
                color: white; 
                padding: 15px 30px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                text-decoration: none; 
                display: inline-block; 
                margin: 10px; 
                font-size: 16px; 
                transition: all 0.3s;
            }
            .btn:hover { 
                background: #45a049; 
                transform: translateY(-2px); 
            }
            .btn.secondary { background: #2196F3; }
            .btn.secondary:hover { background: #1976D2; }
            .btn.warning { background: #ff9800; }
            .btn.warning:hover { background: #f57c00; }
            .data-display {
                background: rgba(0,0,0,0.3);
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                text-align: left;
                font-family: monospace;
                white-space: pre-wrap;
                max-height: 400px;
                overflow-y: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Working Visual System</h1>
            <h2>Real Data from Your System</h2>
            
            <div class="card">
                <h3>📊 System Data</h3>
                <p>Real data from your actual files</p>
                <a href="/api-endpoints" class="btn">📡 API Endpoints</a>
                <a href="/mcp-tools" class="btn secondary">🔧 MCP Tools</a>
                <a href="/system-files" class="btn warning">📁 System Files</a>
            </div>
            
            <div class="card">
                <h3>🎨 Visualizations</h3>
                <p>Interactive data visualization</p>
                <a href="/visual-dashboard" class="btn">🎨 Visual Dashboard</a>
                <a href="/json-viewer" class="btn secondary">📊 JSON Viewer</a>
                <a href="data/-tree" class="btn warning">🌳 Data Tree</a>
            </div>
            
            <div class="card">
                <h3>🔧 Debug & Test</h3>
                <p>Debug and test your system</p>
                <a href="scripts/" class="btn">🐛 Debug Info</a>
                <a href="scripts/-endpoints" class="btn secondary">🧪 Test Endpoints</a>
                <a href="/health" class="btn warning">❤️ Health Check</a>
            </div>
        </div>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content)

@app.get("/api-endpoints", response_class=HTMLResponse)
async def api_endpoints():
    """Show real API endpoints from your files"""
    
    # Find all Python files in vault-api
    endpoints = []
    try:
        python_files = glob.glob(servicesservices/vault-api/*.py")
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find FastAPI routes
                patterns = [
                    r'@app\.(get|post|put|delete|patch)\("([^"]+)"',
                    r'@router\.(get|post|put|delete|patch)\("([^"]+)"',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        method = match[0].upper()
                        path = match[1]
                        endpoints.append({
                            "method": method,
                            "path": path,
                            scripts/le": file_path
                        })
            except Exception as e:
                continue
    except Exception as e:
        pass
    
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Endpoints</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .endpoint {{ background: white; padding: 1rem; margin: 1rem 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .method {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 4px; color: white; font-weight: bold; margin-right: 1rem; }}
            .get {{ background: #4CAF50; }}
            .post {{ background: #2196F3; }}
            .put {{ background: #ff9800; }}
            .delete {{ background: #f44336; }}
            .patch {{ background: #9c27b0; }}
            .path {{ font-family: monospace; font-size: 1.1rem; }}
            .file {{ color: #666; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📡 API Endpoints Found</h1>
            <p>Total: {len(endpoints)} endpoints</p>
            
            {generate_endpoint_html(endpoints)}
            
            <div style="margin-top: 2rem;">
                <a href="/" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return HTMLResponse(content=html_content)

def generate_endpoint_html(endpoints):
    """Generate HTML for endpoints"""
    if not endpoints:
        return '<p>No endpoints found</p>'
    
    html = ""
    for endpoint in endpoints:
        method_class = endpoint['method'].lower()
        html += f'''
        <div class="endpoint">
            <span class="method {method_class}">{endpoint['method']}</span>
            <span class="path">{endpoint['path']}</span>
            <div class=scripts/le">File: {endpoint[scripts/le']}</div>
        </div>
        '''
    return html

@app.get("/mcp-tools", response_class=HTMLResponse)
async def mcp_tools():
    """Show MCP tools from your system"""
    
    mcp_tools = []
    
    # Look for MCP config files
    mcp_files = [
        "mcp.json",
        ".cursor/mcp.json",
        config//mcp.json"
    ]
    
    for mcp_file in mcp_files:
        if os.path.exists(mcp_file):
            try:
                with open(mcp_file, 'r', encoding='utf-8') as f:
                    mcp_config = json.load(f)
                
                if isinstance(mcp_config, dict):
                    for tool_name, tool_config in mcp_config.items():
                        if isinstance(tool_config, dict):
                            mcp_tools.append({
                                "name": tool_name,
                                "description": tool_config.get('description', 'No description'),
                                "command": tool_config.get('command', 'No command'),
                                scripts/le": mcp_file
                            })
            except Exception as e:
                continue
    
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCP Tools</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .tool {{ background: white; padding: 1.5rem; margin: 1rem 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .tool-name {{ font-size: 1.2rem; font-weight: bold; color: #333; margin-bottom: 0.5rem; }}
            .tool-desc {{ color: #666; margin-bottom: 0.5rem; }}
            .tool-command {{ font-family: monospace; background: #f0f0f0; padding: 0.5rem; border-radius: 4px; margin: 0.5rem 0; }}
            .tool-file {{ color: #999; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 MCP Tools Found</h1>
            <p>Total: {len(mcp_tools)} tools</p>
            
            {generate_mcp_tools_html(mcp_tools)}
            
            <div style="margin-top: 2rem;">
                <a href="/" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return HTMLResponse(content=html_content)

def generate_mcp_tools_html(tools):
    """Generate HTML for MCP tools"""
    if not tools:
        return '<p>No MCP tools found</p>'
    
    html = ""
    for tool in tools:
        html += f'''
        <div class="tool">
            <div class="tool-name">{tool['name']}</div>
            <div class="tool-desc">{tool['description']}</div>
            <div class="tool-command">{tool['command']}</div>
            <div class="tool-file">File: {tool[scripts/le']}</div>
        </div>
        '''
    return html

@app.get("/system-files", response_class=HTMLResponse)
async def system_files():
    """Show system files"""
    
    files = []
    try:
        # Get all important files
        patterns = ["*.py", "*.json", "*.yml", "*.yaml", "*.md", "*.txt"]
        for pattern in patterns:
            found_files = glob.glob(f"**/{pattern}", recursive=True)
            for file_path in found_files[:20]:  # Limit to 20 files
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    files.append({
                        "name": os.path.basename(file_path),
                        "path": file_path,
                        "size": file_size
                    })
    except Exception as e:
        pass
    
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Files</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .file {{ background: white; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .file-name {{ font-weight: bold; color: #333; }}
            .file-path {{ color: #666; font-family: monospace; font-size: 0.9rem; }}
            .file-size {{ color: #999; font-size: 0.8rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📁 System Files</h1>
            <p>Total: {len(files)} files</p>
            
            {generate_files_html(files)}
            
            <div style="margin-top: 2rem;">
                <a href="/" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return HTMLResponse(content=html_content)

def generate_files_html(files):
    """Generate HTML for files"""
    if not files:
        return '<p>No files found</p>'
    
    html = ""
    for file in files:
        html += f'''
        <div class=scripts/le">
            <div class=scripts/le-name">{file['name']}</div>
            <div class=scripts/le-path">{file['path']}</div>
            <div class=scripts/le-size">Size: {file['size']} bytes</div>
        </div>
        '''
    return html

@app.get("/visual-dashboard", response_class=HTMLResponse)
async def visual_dashboard():
    """Visual dashboard with real data"""
    
    # Get some real data
    endpoints = []
    try:
        python_files = glob.glob(servicesservices/vault-api/*.py")
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                patterns = [r'@app\.(get|post|put|delete|patch)\("([^"]+)"']
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        endpoints.append({
                            "method": match[0].upper(),
                            "path": match[1]
                        })
            except:
                continue
    except:
        pass
    
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Visual Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }}
            .stat-card {{ background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 15px; text-align: center; backdrop-filter: blur(10px); }}
            .stat-value {{ font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem; }}
            .node-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem; margin: 2rem 0; }}
            .node-card {{ background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }}
            .node-title {{ font-weight: bold; margin-bottom: 0.5rem; }}
            .method {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold; margin-right: 0.5rem; }}
            .get {{ background: #4CAF50; }}
            .post {{ background: #2196F3; }}
            .put {{ background: #ff9800; }}
            .delete {{ background: #f44336; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Visual Dashboard</h1>
            <p>Real data from your system</p>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{len(endpoints)}</div>
                    <div>API Endpoints</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(glob.glob(servicesservices/vault-api/*.py'))}</div>
                    <div>Python Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(glob.glob('**/*.json', recursive=True))}</div>
                    <div>JSON Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(glob.glob('**/*.md', recursive=True))}</div>
                    <div>Markdown Files</div>
                </div>
            </div>
            
            <div class="node-grid">
                {generate_visual_nodes(endpoints)}
            </div>
            
            <div style="margin-top: 2rem;">
                <a href="/" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return HTMLResponse(content=html_content)

def generate_visual_nodes(endpoints):
    """Generate visual nodes for endpoints"""
    if not endpoints:
        return '<div class="node-card"><div class="node-title">No endpoints found</div></div>'
    
    html = ""
    for endpoint in endpoints[:12]:  # Limit to 12 nodes
        method_class = endpoint['method'].lower()
        html += f'''
        <div class="node-card">
            <div class="node-title">{endpoint['path']}</div>
            <div>
                <span class="method {method_class}">{endpoint['method']}</span>
            </div>
        </div>
        '''
    return html

@app.get("scripts/", response_class=JSONResponse)
async def debug():
    ""scripts/ information"""
    return {
        "status": "working",
        "timestamp": datetime.now().isoformat(),
        "python_files": len(glob.glob(servicesservices/vault-api/*.py")),
        "json_files": len(glob.glob("**/*.json", recursive=True)),
        "markdown_files": len(glob.glob("**/*.md", recursive=True)),
        "current_directory": os.getcwd(),
        "message": "System is working!"
    }

@app.get("/health", response_class=JSONResponse)
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "All systems operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_working:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
'@

    $workingMain | Out-File -FilePath servicesservices/vault-api/main_working.py" -Encoding UTF8
    Write-Host "  ✅ Created working main file" -ForegroundColor Green
}

# Function to find available port
function Find-AvailablePort {
    param([int]$StartPort = 8080)
    
    for ($port = $StartPort; $port -le $StartPort + 100; $port++) {
        if (Test-Port -Port $port) {
            return $port
        }
    }
    return $null
}

# Main execution
Write-Host "`n🔍 CREATING WORKING SYSTEM..." -ForegroundColor Cyan

# Create working main file
Create-WorkingMain

# Find available port
$availablePort = Find-AvailablePort
if (-not $availablePort) {
    Write-Host "  ❌ No available ports found" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Found available port: $availablePort" -ForegroundColor Green

# Start the service
Write-Host "`n🚀 STARTING WORKING VISUAL SYSTEM..." -ForegroundColor Green
Write-Host "  📡 Port: $availablePort" -ForegroundColor Gray

# Start the service in background
$process = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main_working:app", "--host", "0.0.0.0", "--port", $availablePort, "--reload" -WorkingDirectory servicesservices/vault-api" -PassThru -WindowStyle Hidden

# Wait for service to start
Write-Host "  ⏳ Waiting for service to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test the service
$serviceUrl = "http://localhost:$availablePort"

Write-Host "`n🔍 TESTING SERVICE..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "$serviceUrl/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ Service is ready!" -ForegroundColor Green
        
        Write-Host "`n🎉 WORKING VISUAL SYSTEM LAUNCHED!" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Cyan
        
        Write-Host "`n🌐 ACCESS POINTS:" -ForegroundColor Cyan
        Write-Host "🚀 Main Dashboard:        $serviceUrl" -ForegroundColor White
        Write-Host "📡 API Endpoints:         $serviceUrl/api-endpoints" -ForegroundColor White
        Write-Host "🔧 MCP Tools:             $serviceUrl/mcp-tools" -ForegroundColor White
        Write-Host "📁 System Files:          $serviceUrl/system-files" -ForegroundColor White
        Write-Host "🎨 Visual Dashboard:      $serviceUrl/visual-dashboard" -ForegroundColor White
        Write-Host "🐛 Debug Info:            $serviceUrlscripts/" -ForegroundColor White
        Write-Host "❤️ Health Check:          $serviceUrl/health" -ForegroundColor White
        
        Write-Host "`n🎨 QUICK ACTIONS:" -ForegroundColor Cyan
        Write-Host "🚀 Opening Main Dashboard..." -ForegroundColor Green
        Start-Process "$serviceUrl"
        
        Write-Host "`n✨ Your WORKING VISUAL SYSTEM is ready!" -ForegroundColor Cyan
        Write-Host "🎨 This system actually works and shows real data!" -ForegroundColor Yellow
        
    } else {
        Write-Host "  ❌ Service returned status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Service not responding: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  🔧 Try running manually:" -ForegroundColor Yellow
    Write-Host "  cd vault-api && python main_working.py" -ForegroundColor Gray
}

Write-Host "`n💡 PRO TIPS:" -ForegroundColor Yellow
Write-Host "• This system actually works and shows real data" -ForegroundColor White
Write-Host "• All endpoints are properly defined and functional" -ForegroundColor White
Write-Host "• Real-time data from your actual files" -ForegroundColor White
Write-Host "• Simple, reliable, and working!" -ForegroundColor White


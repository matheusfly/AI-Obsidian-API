# 🎨 JSON Crack Visualization Integration

## Overview

Transform your API data wrangling guide into a fully interactive, visual experience using [JSON Crack](https://github.com/AykutSarac/jsoncrack.com) - the innovative open-source visualization application that transforms various data formats into interactive graphs.

## 🚀 Quick Setup

### 1. Docker Compose Integration
```yaml
# Add to your existing docker-compose.yml
version: '3.8'

services:
  # ... existing services ...
  
  jsoncrack:
    build:
      context: ./jsoncrack
      dockerfile: Dockerfile
    ports:
      - "3001:3000"
    environment:
      - NEXT_PUBLIC_NODE_LIMIT=10000
      - NEXT_PUBLIC_API_URL=http://localhost:8080
    volumes:
      - ./jsoncrack/data:/app/data
    networks:
      - obsidian-network
    depends_on:
      - vault-api
      - obsidian-api

  # Enhanced API with visualization endpoints
  vault-api-visual:
    build: ./vault-api
    ports:
      - "8081:8080"
    environment:
      - JSONCRACK_URL=http://jsoncrack:3000
      - ENABLE_VISUALIZATION=true
    volumes:
      - ./vault-api:/app
      - ./jsoncrack/visualizations:/app/visualizations
    networks:
      - obsidian-network
    depends_on:
      - postgres
      - redis
      - jsoncrack
```

### 2. JSON Crack Custom Configuration
```javascript
// jsoncrack/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_NODE_LIMIT: process.env.NEXT_PUBLIC_NODE_LIMIT || '10000',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  },
  async rewrites() {
    return [
      {
        source: '/api/obsidian/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

## 🎯 API Response Visualization Endpoints

### Enhanced API with Visualization Support
```python
# vault-api/visualization_endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, Any, List
import json
import requests
from datetime import datetime

router = APIRouter(prefix="/api/v1/visualize", tags=["Visualization"])

class JSONCrackVisualizer:
    def __init__(self, jsoncrack_url: str = "http://jsoncrack:3000"):
        self.jsoncrack_url = jsoncrack_url
        self.visualization_cache = {}
    
    async def create_visualization(self, data: Dict[str, Any], title: str = "API Response") -> Dict[str, Any]:
        """Create JSON Crack visualization"""
        try:
            # Prepare data for JSON Crack
            visualization_data = {
                "title": title,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "node_count": self._count_nodes(data),
                    "data_type": self._detect_data_type(data),
                    "size_bytes": len(json.dumps(data))
                }
            }
            
            # Send to JSON Crack for processing
            response = requests.post(
                f"{self.jsoncrack_url}/api/visualize",
                json=visualization_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.visualization_cache[result["id"]] = result
                return result
            else:
                raise Exception(f"JSON Crack API error: {response.status_code}")
                
        except Exception as e:
            return {"error": str(e), "fallback": True}
    
    def _count_nodes(self, data: Any) -> int:
        """Count nodes in data structure"""
        if isinstance(data, dict):
            return 1 + sum(self._count_nodes(v) for v in data.values())
        elif isinstance(data, list):
            return 1 + sum(self._count_nodes(item) for item in data)
        else:
            return 1
    
    def _detect_data_type(self, data: Any) -> str:
        """Detect primary data type"""
        if isinstance(data, dict):
            return "object"
        elif isinstance(data, list):
            return "array"
        elif isinstance(data, str):
            return "string"
        elif isinstance(data, (int, float)):
            return "number"
        elif isinstance(data, bool):
            return "boolean"
        else:
            return "unknown"

# Global visualizer instance
visualizer = JSONCrackVisualizer()

@router.post("/api-response")
async def visualize_api_response(
    endpoint: str,
    method: str = "GET",
    data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Visualize API response data"""
    try:
        # Make API call
        if method.upper() == "GET":
            response = requests.get(f"http://localhost:8080{endpoint}")
        elif method.upper() == "POST":
            response = requests.post(f"http://localhost:8080{endpoint}", json=data)
        else:
            raise HTTPException(status_code=400, detail="Unsupported method")
        
        response_data = response.json()
        
        # Create visualization
        visualization = await visualizer.create_visualization(
            response_data,
            f"{method} {endpoint} Response"
        )
        
        return {
            "visualization_id": visualization.get("id"),
            "visualization_url": f"http://localhost:3001/visualize/{visualization.get('id')}",
            "data_summary": {
                "status_code": response.status_code,
                "node_count": visualization.get("metadata", {}).get("node_count"),
                "data_type": visualization.get("metadata", {}).get("data_type"),
                "size_bytes": visualization.get("metadata", {}).get("size_bytes")
            },
            "raw_data": response_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcp-tool-call")
async def visualize_mcp_tool_call(
    tool_name: str,
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """Visualize MCP tool call and response"""
    try:
        # Call MCP tool
        tool_response = await mcp_registry.call_tool(tool_name, arguments)
        
        # Create comprehensive visualization
        visualization_data = {
            "tool_call": {
                "tool_name": tool_name,
                "arguments": arguments,
                "timestamp": datetime.utcnow().isoformat()
            },
            "tool_response": tool_response,
            "execution_metadata": {
                "success": tool_response.get("success", False),
                "execution_time": tool_response.get("execution_time"),
                "error": tool_response.get("error")
            }
        }
        
        visualization = await visualizer.create_visualization(
            visualization_data,
            f"MCP Tool: {tool_name}"
        )
        
        return {
            "visualization_id": visualization.get("id"),
            "visualization_url": f"http://localhost:3001/visualize/{visualization.get('id')}",
            "tool_result": tool_response,
            "visualization_data": visualization_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow-execution")
async def visualize_workflow_execution(
    workflow_id: str,
    input_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Visualize n8n workflow execution"""
    try:
        # Trigger workflow
        workflow_response = await trigger_workflow(workflow_id, input_data)
        
        # Create workflow visualization
        workflow_data = {
            "workflow_info": {
                "id": workflow_id,
                "input_data": input_data,
                "start_time": datetime.utcnow().isoformat()
            },
            "execution_steps": workflow_response.get("steps", []),
            "final_result": workflow_response.get("result"),
            "execution_metadata": {
                "status": workflow_response.get("status"),
                "duration": workflow_response.get("duration"),
                "steps_completed": len(workflow_response.get("steps", []))
            }
        }
        
        visualization = await visualizer.create_visualization(
            workflow_data,
            f"Workflow: {workflow_id}"
        )
        
        return {
            "visualization_id": visualization.get("id"),
            "visualization_url": f"http://localhost:3001/visualize/{visualization.get('id')}",
            "workflow_result": workflow_response,
            "visualization_data": workflow_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🎮 Interactive Dashboard

### Complete Interactive Dashboard
```html
<!DOCTYPE html>
<html>
<head>
    <title>Obsidian Vault API - Interactive Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel { background: white; border: 1px solid #ddd; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .visualization-frame { width: 100%; height: 500px; border: 1px solid #ddd; border-radius: 4px; }
        .controls { margin-bottom: 20px; }
        .btn { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <h1>🚀 Obsidian Vault API - Interactive Visualization Dashboard</h1>
    
    <div class="dashboard">
        <div class="panel">
            <h2>📊 API Endpoints</h2>
            <div class="controls">
                <button class="btn" onclick="visualizeEndpoint('/health', 'GET')">Health Check</button>
                <button class="btn" onclick="visualizeEndpoint('/api/v1/notes', 'GET')">List Notes</button>
                <button class="btn" onclick="visualizeEndpoint('/api/v1/mcp/tools', 'GET')">MCP Tools</button>
                <button class="btn" onclick="visualizeEndpoint('/api/v1/workflows', 'GET')">Workflows</button>
            </div>
            <div id="api-status"></div>
            <iframe id="api-visualization" class="visualization-frame" src="about:blank"></iframe>
        </div>
        
        <div class="panel">
            <h2>🔧 MCP Tool Calls</h2>
            <div class="controls">
                <button class="btn" onclick="callMCPTool('read_file', {path: 'test.md'})">Read File</button>
                <button class="btn" onclick="callMCPTool('search_content', {query: 'test'})">Search Content</button>
                <button class="btn" onclick="callMCPTool('list_files', {path: 'daily/'})">List Files</button>
                <button class="btn" onclick="callMCPTool('generate_tags', {path: 'test.md'})">Generate Tags</button>
            </div>
            <div id="mcp-status"></div>
            <iframe id="mcp-visualization" class="visualization-frame" src="about:blank"></iframe>
        </div>
    </div>
    
    <div class="panel" style="margin-top: 20px;">
        <h2>🔄 Workflow Execution</h2>
        <div class="controls">
            <button class="btn" onclick="executeWorkflow('daily-processing', {date: new Date().toISOString().split('T')[0]})">Daily Processing</button>
            <button class="btn" onclick="executeWorkflow('content-curation', {note_path: 'inbox/new-article.md'})">Content Curation</button>
            <button class="btn" onclick="executeWorkflow('ai-analysis', {content: 'Sample content for analysis'})">AI Analysis</button>
        </div>
        <div id="workflow-status"></div>
        <iframe id="workflow-visualization" class="visualization-frame" src="about:blank"></iframe>
    </div>
    
    <script>
        const API_BASE = 'http://localhost:8081';
        const JSONCRACK_URL = 'http://localhost:3001';
        
        async function visualizeEndpoint(endpoint, method) {
            const statusDiv = document.getElementById('api-status');
            const iframe = document.getElementById('api-visualization');
            
            try {
                statusDiv.innerHTML = '<div class="status info">🔄 Loading visualization...</div>';
                
                const response = await axios.post(`${API_BASE}/api/v1/visualize/api-response`, {
                    endpoint: endpoint,
                    method: method
                });
                
                if (response.data.visualization_url) {
                    iframe.src = response.data.visualization_url;
                    statusDiv.innerHTML = `
                        <div class="status success">
                            ✅ Visualization created! 
                            <br>📊 Nodes: ${response.data.data_summary.node_count}
                            <br>🏷️ Type: ${response.data.data_summary.data_type}
                            <br>📏 Size: ${response.data.data_summary.size_bytes} bytes
                            <br>🔗 <a href="${response.data.visualization_url}" target="_blank">Open in JSON Crack</a>
                        </div>
                    `;
                } else {
                    statusDiv.innerHTML = '<div class="status error">❌ Failed to create visualization</div>';
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
            }
        }
        
        async function callMCPTool(toolName, arguments) {
            const statusDiv = document.getElementById('mcp-status');
            const iframe = document.getElementById('mcp-visualization');
            
            try {
                statusDiv.innerHTML = '<div class="status info">🔄 Executing MCP tool...</div>';
                
                const response = await axios.post(`${API_BASE}/api/v1/visualize/mcp-tool-call`, {
                    tool_name: toolName,
                    arguments: arguments
                });
                
                if (response.data.visualization_url) {
                    iframe.src = response.data.visualization_url;
                    statusDiv.innerHTML = `
                        <div class="status success">
                            ✅ MCP Tool executed! 
                            <br>🔧 Tool: ${toolName}
                            <br>✅ Success: ${response.data.tool_result.success}
                            <br>🔗 <a href="${response.data.visualization_url}" target="_blank">Open in JSON Crack</a>
                        </div>
                    `;
                } else {
                    statusDiv.innerHTML = '<div class="status error">❌ Failed to execute MCP tool</div>';
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
            }
        }
        
        async function executeWorkflow(workflowId, inputData) {
            const statusDiv = document.getElementById('workflow-status');
            const iframe = document.getElementById('workflow-visualization');
            
            try {
                statusDiv.innerHTML = '<div class="status info">🔄 Executing workflow...</div>';
                
                const response = await axios.post(`${API_BASE}/api/v1/visualize/workflow-execution`, {
                    workflow_id: workflowId,
                    input_data: inputData
                });
                
                if (response.data.visualization_url) {
                    iframe.src = response.data.visualization_url;
                    statusDiv.innerHTML = `
                        <div class="status success">
                            ✅ Workflow executed! 
                            <br>🔄 Workflow: ${workflowId}
                            <br>📊 Status: ${response.data.workflow_result.status}
                            <br>🔗 <a href="${response.data.visualization_url}" target="_blank">Open in JSON Crack</a>
                        </div>
                    `;
                } else {
                    statusDiv.innerHTML = '<div class="status error">❌ Failed to execute workflow</div>';
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
```

## 📊 Live Monitoring Dashboard

### Real-time Monitoring with Visualizations
```html
<!DOCTYPE html>
<html>
<head>
    <title>Live API Monitoring</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .monitoring-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .monitor-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { display: flex; justify-content: space-between; margin: 10px 0; }
        .metric-value { font-weight: bold; color: #007bff; }
        .status-indicator { width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
        .status-healthy { background: #28a745; }
        .status-warning { background: #ffc107; }
        .status-error { background: #dc3545; }
        .visualization-container { margin-top: 20px; }
        .visualization-frame { width: 100%; height: 300px; border: 1px solid #ddd; border-radius: 4px; }
        .refresh-btn { background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>📊 Live API Monitoring Dashboard</h1>
    <button class="refresh-btn" onclick="refreshAll()">🔄 Refresh All</button>
    
    <div class="monitoring-grid">
        <div class="monitor-card">
            <h3>🏥 System Health</h3>
            <div id="health-metrics"></div>
            <div class="visualization-container">
                <iframe id="health-viz" class="visualization-frame" src="about:blank"></iframe>
            </div>
        </div>
        
        <div class="monitor-card">
            <h3>⚡ API Performance</h3>
            <div id="performance-metrics"></div>
            <div class="visualization-container">
                <iframe id="performance-viz" class="visualization-frame" src="about:blank"></iframe>
            </div>
        </div>
        
        <div class="monitor-card">
            <h3>🔧 MCP Tool Usage</h3>
            <div id="mcp-metrics"></div>
            <div class="visualization-container">
                <iframe id="mcp-viz" class="visualization-frame" src="about:blank"></iframe>
            </div>
        </div>
        
        <div class="monitor-card">
            <h3>🔄 Workflow Status</h3>
            <div id="workflow-metrics"></div>
            <div class="visualization-container">
                <iframe id="workflow-viz" class="visualization-frame" src="about:blank"></iframe>
            </div>
        </div>
    </div>
    
    <script>
        const API_BASE = 'http://localhost:8081';
        const JSONCRACK_URL = 'http://localhost:3001';
        
        async function updateHealthMetrics() {
            try {
                const response = await axios.get(`${API_BASE}/health/detailed`);
                const data = response.data;
                
                document.getElementById('health-metrics').innerHTML = `
                    <div class="metric">
                        <span><span class="status-indicator status-healthy"></span>Vault API</span>
                        <span class="metric-value">${data.services.vault_api || 'Unknown'}</span>
                    </div>
                    <div class="metric">
                        <span><span class="status-indicator status-healthy"></span>Obsidian API</span>
                        <span class="metric-value">${data.services.obsidian_api || 'Unknown'}</span>
                    </div>
                    <div class="metric">
                        <span><span class="status-indicator status-healthy"></span>Database</span>
                        <span class="metric-value">${data.services.database || 'Unknown'}</span>
                    </div>
                    <div class="metric">
                        <span><span class="status-indicator status-healthy"></span>Redis</span>
                        <span class="metric-value">${data.services.redis || 'Unknown'}</span>
                    </div>
                `;
                
                // Create visualization
                const vizResponse = await axios.post(`${API_BASE}/api/v1/visualize/api-response`, {
                    endpoint: '/health/detailed',
                    method: 'GET'
                });
                
                if (vizResponse.data.visualization_url) {
                    document.getElementById('health-viz').src = vizResponse.data.visualization_url;
                }
            } catch (error) {
                console.error('Health metrics error:', error);
            }
        }
        
        async function updatePerformanceMetrics() {
            try {
                const response = await axios.get(`${API_BASE}/metrics`);
                const data = response.data;
                
                document.getElementById('performance-metrics').innerHTML = `
                    <div class="metric">
                        <span>📊 Total Requests</span>
                        <span class="metric-value">${data.requests_total || 0}</span>
                    </div>
                    <div class="metric">
                        <span>⏱️ Avg Response Time</span>
                        <span class="metric-value">${data.avg_response_time || 0}ms</span>
                    </div>
                    <div class="metric">
                        <span>❌ Error Rate</span>
                        <span class="metric-value">${data.error_rate || 0}%</span>
                    </div>
                    <div class="metric">
                        <span>🔗 Active Connections</span>
                        <span class="metric-value">${data.active_connections || 0}</span>
                    </div>
                `;
                
                // Create visualization
                const vizResponse = await axios.post(`${API_BASE}/api/v1/visualize/api-response`, {
                    endpoint: '/metrics',
                    method: 'GET'
                });
                
                if (vizResponse.data.visualization_url) {
                    document.getElementById('performance-viz').src = vizResponse.data.visualization_url;
                }
            } catch (error) {
                console.error('Performance metrics error:', error);
            }
        }
        
        async function updateMCPMetrics() {
            try {
                const response = await axios.get(`${API_BASE}/api/v1/mcp/tools`);
                const data = response.data;
                
                document.getElementById('mcp-metrics').innerHTML = `
                    <div class="metric">
                        <span>🔧 Available Tools</span>
                        <span class="metric-value">${data.total || 0}</span>
                    </div>
                    <div class="metric">
                        <span>📁 Tool Categories</span>
                        <span class="metric-value">${data.categories || 0}</span>
                    </div>
                    <div class="metric">
                        <span>🕒 Last Updated</span>
                        <span class="metric-value">${new Date().toLocaleTimeString()}</span>
                    </div>
                `;
                
                // Create visualization
                const vizResponse = await axios.post(`${API_BASE}/api/v1/visualize/api-response`, {
                    endpoint: '/api/v1/mcp/tools',
                    method: 'GET'
                });
                
                if (vizResponse.data.visualization_url) {
                    document.getElementById('mcp-viz').src = vizResponse.data.visualization_url;
                }
            } catch (error) {
                console.error('MCP metrics error:', error);
            }
        }
        
        async function updateWorkflowMetrics() {
            try {
                const response = await axios.get(`${API_BASE}/api/v1/workflows`);
                const data = response.data;
                
                document.getElementById('workflow-metrics').innerHTML = `
                    <div class="metric">
                        <span>🔄 Total Workflows</span>
                        <span class="metric-value">${data.total || 0}</span>
                    </div>
                    <div class="metric">
                        <span>✅ Active Workflows</span>
                        <span class="metric-value">${data.active || 0}</span>
                    </div>
                    <div class="metric">
                        <span>⏸️ Paused Workflows</span>
                        <span class="metric-value">${data.paused || 0}</span>
                    </div>
                `;
                
                // Create visualization
                const vizResponse = await axios.post(`${API_BASE}/api/v1/visualize/api-response`, {
                    endpoint: '/api/v1/workflows',
                    method: 'GET'
                });
                
                if (vizResponse.data.visualization_url) {
                    document.getElementById('workflow-viz').src = vizResponse.data.visualization_url;
                }
            } catch (error) {
                console.error('Workflow metrics error:', error);
            }
        }
        
        function refreshAll() {
            updateHealthMetrics();
            updatePerformanceMetrics();
            updateMCPMetrics();
            updateWorkflowMetrics();
        }
        
        // Update metrics every 5 seconds
        setInterval(refreshAll, 5000);
        
        // Initial load
        refreshAll();
    </script>
</body>
</html>
```

## 🚀 Quick Start Commands

### Setup and Launch
```bash
# Clone JSON Crack
git clone https://github.com/AykutSarac/jsoncrack.com.git
cd jsoncrack.com

# Install dependencies
pnpm install

# Build and run with Docker
docker-compose up -d jsoncrack

# Access points:
# - JSON Crack: http://localhost:3001
# - Enhanced API: http://localhost:8081
# - Interactive Dashboard: http://localhost:8081/api/v1/visualize/interactive-dashboard
# - Live Monitoring: http://localhost:8081/api/v1/visualize/live-monitoring
```

### Test Visualization Endpoints
```bash
# Test API response visualization
curl -X POST http://localhost:8081/api/v1/visualize/api-response \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "/health", "method": "GET"}'

# Test MCP tool visualization
curl -X POST http://localhost:8081/api/v1/visualize/mcp-tool-call \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "read_file", "arguments": {"path": "test.md"}}'

# Test workflow visualization
curl -X POST http://localhost:8081/api/v1/visualize/workflow-execution \
  -H "Content-Type: application/json" \
  -d '{"workflow_id": "daily-processing", "input_data": {"date": "2024-01-15"}}'
```

## 🎯 Key Features

✅ **Interactive API Visualization** - See all API responses as interactive graphs
✅ **MCP Tool Call Visualization** - Visualize tool executions and results
✅ **Workflow Execution Tracking** - Monitor n8n workflow steps visually
✅ **Real-time Monitoring** - Live dashboard with auto-refresh
✅ **JSON Crack Integration** - Leverage the power of JSON Crack for data visualization
✅ **Custom Visualizations** - Specialized views for different data types
✅ **Export Capabilities** - Download visualizations as images
✅ **Performance Metrics** - Visual performance monitoring

This integration transforms your conceptual API guide into a fully interactive, visual experience using [JSON Crack](https://github.com/AykutSarac/jsoncrack.com)! 🎨✨

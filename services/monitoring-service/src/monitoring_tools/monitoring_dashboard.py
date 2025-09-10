"""
Comprehensive Monitoring Dashboard and Debugging Interface
Real-time observability for LangGraph agents with time-travel debugging
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
from dataclasses import dataclass

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
OBSERVABILITY_MCP_URL = "http://127.0.0.1:8002"
LANGGRAPH_SERVER_URL = "http://127.0.0.1:2024"
OBSIDIAN_API_URL = "http://127.0.0.1:27123"

@dataclass
class DashboardMetrics:
    """Dashboard metrics for real-time monitoring"""
    total_agents: int = 0
    active_threads: int = 0
    total_traces: int = 0
    total_checkpoints: int = 0
    error_rate: float = 0.0
    average_response_time: float = 0.0
    vault_health: str = "unknown"
    langgraph_health: str = "unknown"
    last_updated: datetime = None

class ObservabilityClient:
    """Client for interacting with the Observability MCP server"""
    
    def __init__(self, base_url: str = OBSERVABILITY_MCP_URL):
        self.base_url = base_url
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def get_traces(self, thread_id: str = None, agent_id: str = None, limit: int = 100) -> Dict[str, Any]:
        """Get trace events"""
        try:
            payload = {}
            if thread_id:
                payload["thread_id"] = thread_id
            if agent_id:
                payload["agent_id"] = agent_id
            payload["limit"] = limit
            
            response = await self.session.post(
                f"{self.base_url}/tools/get_traces",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get traces: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting traces: {e}")
            return {"error": str(e)}
    
    async def get_checkpoints(self, thread_id: str = None, agent_id: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get checkpoints"""
        try:
            payload = {}
            if thread_id:
                payload["thread_id"] = thread_id
            if agent_id:
                payload["agent_id"] = agent_id
            payload["limit"] = limit
            
            response = await self.session.post(
                f"{self.base_url}/tools/get_checkpoints",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get checkpoints: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting checkpoints: {e}")
            return {"error": str(e)}
    
    async def get_performance_metrics(self, agent_id: str = None, thread_id: str = None) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            payload = {}
            if agent_id:
                payload["agent_id"] = agent_id
            if thread_id:
                payload["thread_id"] = thread_id
            
            response = await self.session.post(
                f"{self.base_url}/tools/get_performance_metrics",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get performance metrics: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    async def get_debug_summary(self, thread_id: str, agent_id: str = None) -> Dict[str, Any]:
        """Get debug summary"""
        try:
            payload = {
                "thread_id": thread_id,
                "agent_id": agent_id,
                "include_traces": True,
                "include_checkpoints": True,
                "include_performance": True
            }
            
            response = await self.session.post(
                f"{self.base_url}/tools/get_debug_summary",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get debug summary: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting debug summary: {e}")
            return {"error": str(e)}
    
    async def time_travel_debug(self, checkpoint_id: str, thread_id: str, restore_state: bool = False) -> Dict[str, Any]:
        """Time-travel to a checkpoint"""
        try:
            payload = {
                "checkpoint_id": checkpoint_id,
                "thread_id": thread_id,
                "restore_state": restore_state
            }
            
            response = await self.session.post(
                f"{self.base_url}/tools/time_travel_debug",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to time-travel: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error time-traveling: {e}")
            return {"error": str(e)}

class MonitoringDashboard:
    """Main monitoring dashboard class"""
    
    def __init__(self):
        self.app = FastAPI(title="LangGraph Observability Dashboard", version="1.0.0")
        self.observability_client = ObservabilityClient()
        self.metrics = DashboardMetrics()
        self.websocket_connections: List[WebSocket] = []
        
        self._setup_routes()
        self._setup_cors()
        self._start_metrics_collection()
    
    def _setup_cors(self):
        """Setup CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def dashboard_home():
            """Main dashboard page"""
            return HTMLResponse(content=self._get_dashboard_html())
        
        @self.app.get("/api/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """Get current metrics"""
            return self.metrics.__dict__
        
        @self.app.get("/api/traces")
        async def get_traces(thread_id: str = None, agent_id: str = None, limit: int = 100):
            """Get trace events"""
            result = await self.observability_client.get_traces(thread_id, agent_id, limit)
            return result
        
        @self.app.get("/api/checkpoints")
        async def get_checkpoints(thread_id: str = None, agent_id: str = None, limit: int = 50):
            """Get checkpoints"""
            result = await self.observability_client.get_checkpoints(thread_id, agent_id, limit)
            return result
        
        @self.app.get("/api/performance")
        async def get_performance(agent_id: str = None, thread_id: str = None):
            """Get performance metrics"""
            result = await self.observability_client.get_performance_metrics(agent_id, thread_id)
            return result
        
        @self.app.get("/api/debug/{thread_id}")
        async def get_debug_summary(thread_id: str, agent_id: str = None):
            """Get debug summary for a thread"""
            result = await self.observability_client.get_debug_summary(thread_id, agent_id)
            return result
        
        @self.app.post("/api/time-travel")
        async def time_travel_debug(checkpoint_id: str, thread_id: str, restore_state: bool = False):
            """Time-travel to a checkpoint"""
            result = await self.observability_client.time_travel_debug(checkpoint_id, thread_id, restore_state)
            return result
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            self.websocket_connections.append(websocket)
            
            try:
                while True:
                    # Send periodic updates
                    await websocket.send_json({
                        "type": "metrics_update",
                        "data": self.metrics.__dict__
                    })
                    await asyncio.sleep(5)  # Update every 5 seconds
                    
            except WebSocketDisconnect:
                self.websocket_connections.remove(websocket)
    
    def _get_dashboard_html(self) -> str:
        """Get the dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGraph Observability Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
        .section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .section h2 {
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .trace-item {
            background: #f8f9fa;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .trace-item.error {
            border-left-color: #dc3545;
        }
        .trace-item.warning {
            border-left-color: #ffc107;
        }
        .checkpoint-item {
            background: #e8f5e8;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }
        .time-travel-btn {
            background: #17a2b8;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            margin-left: 10px;
        }
        .time-travel-btn:hover {
            background: #138496;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-healthy { background-color: #28a745; }
        .status-warning { background-color: #ffc107; }
        .status-error { background-color: #dc3545; }
        .status-unknown { background-color: #6c757d; }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px 0;
        }
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 LangGraph Observability Dashboard</h1>
            <p>Real-time monitoring and debugging for AI agents</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value" id="total-agents">-</div>
                <div class="metric-label">Total Agents</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="active-threads">-</div>
                <div class="metric-label">Active Threads</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="total-traces">-</div>
                <div class="metric-label">Total Traces</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="total-checkpoints">-</div>
                <div class="metric-label">Checkpoints</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="error-rate">-</div>
                <div class="metric-label">Error Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="vault-health">-</div>
                <div class="metric-label">Vault Health</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Recent Trace Events</h2>
            <button class="refresh-btn" onclick="loadTraces()">Refresh Traces</button>
            <div id="traces-container">
                <div class="loading">Loading traces...</div>
            </div>
        </div>
        
        <div class="section">
            <h2>⏰ Checkpoints (Time-Travel Debugging)</h2>
            <button class="refresh-btn" onclick="loadCheckpoints()">Refresh Checkpoints</button>
            <div id="checkpoints-container">
                <div class="loading">Loading checkpoints...</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 Debug Summary</h2>
            <input type="text" id="thread-id-input" placeholder="Enter Thread ID" style="padding: 8px; margin-right: 10px; border: 1px solid #ddd; border-radius: 3px;">
            <button class="refresh-btn" onclick="loadDebugSummary()">Get Debug Summary</button>
            <div id="debug-container">
                <div class="loading">Enter a thread ID to get debug summary</div>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        
        // WebSocket connection for real-time updates
        function connectWebSocket() {
            ws = new WebSocket('ws://localhost:8001/ws');
            
            ws.onopen = function() {
                console.log('WebSocket connected');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'metrics_update') {
                    updateMetrics(data.data);
                }
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected, reconnecting...');
                setTimeout(connectWebSocket, 5000);
            };
        }
        
        // Update metrics display
        function updateMetrics(metrics) {
            document.getElementById('total-agents').textContent = metrics.total_agents || 0;
            document.getElementById('active-threads').textContent = metrics.active_threads || 0;
            document.getElementById('total-traces').textContent = metrics.total_traces || 0;
            document.getElementById('total-checkpoints').textContent = metrics.total_checkpoints || 0;
            document.getElementById('error-rate').textContent = (metrics.error_rate || 0).toFixed(2) + '%';
            
            const vaultHealth = document.getElementById('vault-health');
            const status = metrics.vault_health || 'unknown';
            vaultHealth.innerHTML = `<span class="status-indicator status-${status}"></span>${status}`;
        }
        
        // Load traces
        async function loadTraces() {
            try {
                const response = await fetch('/api/traces?limit=20');
                const data = await response.json();
                
                const container = document.getElementById('traces-container');
                if (data.error) {
                    container.innerHTML = `<div class="trace-item error">Error: ${data.error}</div>`;
                    return;
                }
                
                if (data.content && data.content[0]) {
                    const traces = JSON.parse(data.content[0].text);
                    container.innerHTML = traces.map(trace => `
                        <div class="trace-item ${trace.level}">
                            <strong>${trace.event_type}</strong> - ${trace.message}
                            <br>
                            <small>Thread: ${trace.thread_id} | Agent: ${trace.agent_id} | ${trace.timestamp}</small>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<div class="loading">No traces found</div>';
                }
            } catch (error) {
                document.getElementById('traces-container').innerHTML = `<div class="trace-item error">Error loading traces: ${error.message}</div>`;
            }
        }
        
        // Load checkpoints
        async function loadCheckpoints() {
            try {
                const response = await fetch('/api/checkpoints?limit=10');
                const data = await response.json();
                
                const container = document.getElementById('checkpoints-container');
                if (data.error) {
                    container.innerHTML = `<div class="checkpoint-item error">Error: ${data.error}</div>`;
                    return;
                }
                
                if (data.content && data.content[0]) {
                    const checkpoints = JSON.parse(data.content[0].text);
                    container.innerHTML = checkpoints.map(checkpoint => `
                        <div class="checkpoint-item">
                            <strong>${checkpoint.checkpoint_type}</strong> - ${checkpoint.timestamp}
                            <br>
                            <small>Thread: ${checkpoint.thread_id} | Agent: ${checkpoint.agent_id}</small>
                            <button class="time-travel-btn" onclick="timeTravel('${checkpoint.checkpoint_id}', '${checkpoint.thread_id}')">
                                Time Travel
                            </button>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<div class="loading">No checkpoints found</div>';
                }
            } catch (error) {
                document.getElementById('checkpoints-container').innerHTML = `<div class="checkpoint-item error">Error loading checkpoints: ${error.message}</div>`;
            }
        }
        
        // Load debug summary
        async function loadDebugSummary() {
            const threadId = document.getElementById('thread-id-input').value;
            if (!threadId) {
                alert('Please enter a thread ID');
                return;
            }
            
            try {
                const response = await fetch(`/api/debug/${threadId}`);
                const data = await response.json();
                
                const container = document.getElementById('debug-container');
                if (data.error) {
                    container.innerHTML = `<div class="trace-item error">Error: ${data.error}</div>`;
                    return;
                }
                
                container.innerHTML = `
                    <div class="trace-item">
                        <h3>Debug Summary for Thread: ${threadId}</h3>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </div>
                `;
            } catch (error) {
                document.getElementById('debug-container').innerHTML = `<div class="trace-item error">Error loading debug summary: ${error.message}</div>`;
            }
        }
        
        // Time travel to checkpoint
        async function timeTravel(checkpointId, threadId) {
            try {
                const response = await fetch('/api/time-travel', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        checkpoint_id: checkpointId,
                        thread_id: threadId,
                        restore_state: true
                    })
                });
                
                const data = await response.json();
                if (data.error) {
                    alert(`Time travel failed: ${data.error}`);
                } else {
                    alert(`Time travel successful! Checkpoint: ${checkpointId}`);
                }
            } catch (error) {
                alert(`Time travel error: ${error.message}`);
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            connectWebSocket();
            loadTraces();
            loadCheckpoints();
        });
    </script>
</body>
</html>
        """
    
    def _start_metrics_collection(self):
        """Start background metrics collection"""
        def collect_metrics():
            while True:
                try:
                    # This would be implemented to collect real metrics
                    # For now, we'll use placeholder data
                    self.metrics.total_agents = 3
                    self.metrics.active_threads = 5
                    self.metrics.total_traces = 150
                    self.metrics.total_checkpoints = 25
                    self.metrics.error_rate = 2.5
                    self.metrics.average_response_time = 1.2
                    self.metrics.vault_health = "healthy"
                    self.metrics.langgraph_health = "healthy"
                    self.metrics.last_updated = datetime.now()
                    
                    time.sleep(10)  # Update every 10 seconds
                except Exception as e:
                    logger.error(f"Error collecting metrics: {e}")
                    time.sleep(30)  # Wait longer on error
        
        # Start metrics collection in background thread
        metrics_thread = threading.Thread(target=collect_metrics, daemon=True)
        metrics_thread.start()
    
    def run(self, host: str = "0.0.0.0", port: int = 8001):
        """Run the monitoring dashboard"""
        logger.info(f"Starting monitoring dashboard on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

def main():
    """Main function to run the monitoring dashboard"""
    try:
        dashboard = MonitoringDashboard()
        dashboard.run()
    except Exception as e:
        logger.error(f"Failed to start monitoring dashboard: {e}")
        raise

if __name__ == "__main__":
    main()

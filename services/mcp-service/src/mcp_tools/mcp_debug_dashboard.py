#!/usr/bin/env python3
"""
MCP Debug Dashboard
Advanced debugging and monitoring for MCP servers
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPDebugSession(BaseModel):
    session_id: str
    name: str
    created_at: datetime
    status: str = "active"
    mcp_calls: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    performance_metrics: Dict[str, Any] = {}

class MCPDebugDashboard:
    """Advanced MCP Debug Dashboard"""
    
    def __init__(self, mcp_integration_url: str = "http://127.0.0.1:8003"):
        self.mcp_integration_url = mcp_integration_url
        self.debug_sessions = {}
        self.active_connections = []
        self.real_time_metrics = {}
        self.error_patterns = {}
        self.performance_history = []
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="MCP Debug Dashboard",
            description="Advanced debugging and monitoring for MCP servers",
            version="1.0.0"
        )
        self.setup_routes()
        self.setup_websocket()
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            """Main dashboard page"""
            return self.get_dashboard_html()
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "mcp-debug-dashboard",
                "version": "1.0.0",
                "active_sessions": len(self.debug_sessions),
                "active_connections": len(self.active_connections)
            }
        
        @self.app.get("/api/sessions")
        async def get_debug_sessions():
            """Get all debug sessions"""
            return {
                "sessions": list(self.debug_sessions.values()),
                "total": len(self.debug_sessions)
            }
        
        @self.app.post("/api/sessions")
        async def create_debug_session(session_data: Dict[str, Any]):
            """Create a new debug session"""
            session_id = str(uuid.uuid4())
            session = MCPDebugSession(
                session_id=session_id,
                name=session_data.get("name", f"Debug Session {len(self.debug_sessions) + 1}"),
                created_at=datetime.now()
            )
            self.debug_sessions[session_id] = session
            return {"session_id": session_id, "session": session}
        
        @self.app.get("/api/sessions/{session_id}")
        async def get_debug_session(session_id: str):
            """Get specific debug session"""
            if session_id not in self.debug_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            return self.debug_sessions[session_id]
        
        @self.app.post("/api/sessions/{session_id}/mcp-call")
        async def log_mcp_call(session_id: str, call_data: Dict[str, Any]):
            """Log an MCP call to a debug session"""
            if session_id not in self.debug_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            call_record = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "server": call_data.get("server"),
                "tool": call_data.get("tool"),
                "arguments": call_data.get("arguments", {}),
                "execution_time_ms": call_data.get("execution_time_ms", 0),
                "success": call_data.get("success", False),
                "error": call_data.get("error")
            }
            
            self.debug_sessions[session_id].mcp_calls.append(call_record)
            
            # Update performance metrics
            self.update_performance_metrics(session_id, call_record)
            
            # Check for error patterns
            if not call_record["success"]:
                self.analyze_error_pattern(session_id, call_record)
            
            # Broadcast to WebSocket connections
            await self.broadcast_update(session_id, "mcp_call", call_record)
            
            return {"success": True, "call_id": call_record["id"]}
        
        @self.app.get("/api/sessions/{session_id}/metrics")
        async def get_session_metrics(session_id: str):
            """Get performance metrics for a debug session"""
            if session_id not in self.debug_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            session = self.debug_sessions[session_id]
            calls = session.mcp_calls
            
            if not calls:
                return {"metrics": {}}
            
            # Calculate metrics
            total_calls = len(calls)
            successful_calls = len([c for c in calls if c["success"]])
            failed_calls = total_calls - successful_calls
            success_rate = (successful_calls / total_calls) * 100 if total_calls > 0 else 0
            
            execution_times = [c["execution_time_ms"] for c in calls if c["execution_time_ms"] > 0]
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            max_execution_time = max(execution_times) if execution_times else 0
            min_execution_time = min(execution_times) if execution_times else 0
            
            # Server-specific metrics
            server_metrics = {}
            for call in calls:
                server = call["server"]
                if server not in server_metrics:
                    server_metrics[server] = {"total": 0, "successful": 0, "failed": 0, "avg_time": 0}
                
                server_metrics[server]["total"] += 1
                if call["success"]:
                    server_metrics[server]["successful"] += 1
                else:
                    server_metrics[server]["failed"] += 1
            
            # Calculate server averages
            for server, metrics in server_metrics.items():
                server_calls = [c for c in calls if c["server"] == server and c["execution_time_ms"] > 0]
                if server_calls:
                    metrics["avg_time"] = sum(c["execution_time_ms"] for c in server_calls) / len(server_calls)
            
            metrics = {
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "success_rate": success_rate,
                "avg_execution_time": avg_execution_time,
                "max_execution_time": max_execution_time,
                "min_execution_time": min_execution_time,
                "server_metrics": server_metrics,
                "error_patterns": self.error_patterns.get(session_id, {}),
                "last_updated": datetime.now().isoformat()
            }
            
            return {"metrics": metrics}
        
        @self.app.get("/api/sessions/{session_id}/errors")
        async def get_session_errors(session_id: str):
            """Get error analysis for a debug session"""
            if session_id not in self.debug_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            session = self.debug_sessions[session_id]
            error_calls = [c for c in session.mcp_calls if not c["success"]]
            
            # Analyze error patterns
            error_analysis = {
                "total_errors": len(error_calls),
                "error_types": {},
                "server_errors": {},
                "tool_errors": {},
                "recent_errors": error_calls[-10:] if error_calls else []
            }
            
            for call in error_calls:
                # Error type analysis
                error_msg = call.get("error", "Unknown error")
                error_type = self.categorize_error(error_msg)
                error_analysis["error_types"][error_type] = error_analysis["error_types"].get(error_type, 0) + 1
                
                # Server error analysis
                server = call["server"]
                error_analysis["server_errors"][server] = error_analysis["server_errors"].get(server, 0) + 1
                
                # Tool error analysis
                tool = call["tool"]
                error_analysis["tool_errors"][tool] = error_analysis["tool_errors"].get(tool, 0) + 1
            
            return {"error_analysis": error_analysis}
        
        @self.app.get("/api/real-time-metrics")
        async def get_real_time_metrics():
            """Get real-time metrics across all sessions"""
            return {
                "active_sessions": len(self.debug_sessions),
                "total_mcp_calls": sum(len(s.mcp_calls) for s in self.debug_sessions.values()),
                "active_connections": len(self.active_connections),
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/api/sessions/{session_id}/export")
        async def export_session_data(session_id: str):
            """Export debug session data"""
            if session_id not in self.debug_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            session = self.debug_sessions[session_id]
            export_data = {
                "session": session.dict(),
                "metrics": await self.get_session_metrics(session_id),
                "errors": await self.get_session_errors(session_id),
                "exported_at": datetime.now().isoformat()
            }
            
            # Save to file
            filename = f"mcp_debug_session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return {"filename": filename, "data": export_data}
    
    def setup_websocket(self):
        """Setup WebSocket for real-time updates"""
        
        @self.app.websocket("/ws/{session_id}")
        async def websocket_endpoint(websocket: WebSocket, session_id: str):
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    # Send periodic updates
                    await asyncio.sleep(1)
                    
                    if session_id in self.debug_sessions:
                        session = self.debug_sessions[session_id]
                        update = {
                            "type": "session_update",
                            "session_id": session_id,
                            "total_calls": len(session.mcp_calls),
                            "errors": len([c for c in session.mcp_calls if not c["success"]]),
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send_text(json.dumps(update))
                    
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
    
    async def broadcast_update(self, session_id: str, update_type: str, data: Any):
        """Broadcast update to all WebSocket connections"""
        update = {
            "type": update_type,
            "session_id": session_id,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(update))
            except:
                # Remove dead connections
                self.active_connections.remove(connection)
    
    def update_performance_metrics(self, session_id: str, call_record: Dict[str, Any]):
        """Update performance metrics for a session"""
        if session_id not in self.real_time_metrics:
            self.real_time_metrics[session_id] = {
                "calls_per_minute": [],
                "avg_response_time": [],
                "error_rate": []
            }
        
        metrics = self.real_time_metrics[session_id]
        current_time = datetime.now()
        
        # Add to performance history
        self.performance_history.append({
            "session_id": session_id,
            "timestamp": current_time,
            "execution_time_ms": call_record["execution_time_ms"],
            "success": call_record["success"]
        })
        
        # Keep only last hour of data
        cutoff_time = current_time - timedelta(hours=1)
        self.performance_history = [
            p for p in self.performance_history 
            if p["timestamp"] > cutoff_time
        ]
    
    def analyze_error_pattern(self, session_id: str, call_record: Dict[str, Any]):
        """Analyze error patterns for debugging insights"""
        if session_id not in self.error_patterns:
            self.error_patterns[session_id] = {}
        
        error_msg = call_record.get("error", "")
        server = call_record["server"]
        tool = call_record["tool"]
        
        # Categorize error
        error_type = self.categorize_error(error_msg)
        
        if error_type not in self.error_patterns[session_id]:
            self.error_patterns[session_id][error_type] = {
                "count": 0,
                "servers": set(),
                "tools": set(),
                "first_seen": datetime.now(),
                "last_seen": datetime.now()
            }
        
        pattern = self.error_patterns[session_id][error_type]
        pattern["count"] += 1
        pattern["servers"].add(server)
        pattern["tools"].add(tool)
        pattern["last_seen"] = datetime.now()
    
    def categorize_error(self, error_msg: str) -> str:
        """Categorize error message for pattern analysis"""
        error_msg_lower = error_msg.lower()
        
        if "timeout" in error_msg_lower:
            return "timeout"
        elif "connection" in error_msg_lower:
            return "connection"
        elif "not found" in error_msg_lower or "404" in error_msg:
            return "not_found"
        elif "unauthorized" in error_msg_lower or "401" in error_msg:
            return "unauthorized"
        elif "server error" in error_msg_lower or "500" in error_msg:
            return "server_error"
        elif "invalid" in error_msg_lower or "400" in error_msg:
            return "invalid_request"
        else:
            return "other"
    
    def get_dashboard_html(self) -> str:
        """Generate HTML dashboard"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Debug Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.8;
        }
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }
        .card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #3498db;
        }
        .card h3 {
            margin: 0 0 15px 0;
            color: #2c3e50;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }
        .metric-value {
            font-weight: bold;
            color: #27ae60;
        }
        .error {
            color: #e74c3c;
        }
        .success {
            color: #27ae60;
        }
        .warning {
            color: #f39c12;
        }
        .session-list {
            grid-column: 1 / -1;
        }
        .session-item {
            background: white;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
        }
        .session-name {
            font-weight: bold;
            color: #2c3e50;
        }
        .session-stats {
            display: flex;
            gap: 20px;
            margin-top: 10px;
        }
        .stat {
            font-size: 0.9em;
            color: #7f8c8d;
        }
        .real-time {
            background: #2c3e50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            text-align: center;
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background: #2980b9;
        }
        .btn-danger {
            background: #e74c3c;
        }
        .btn-danger:hover {
            background: #c0392b;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 MCP Debug Dashboard</h1>
            <p>Advanced debugging and monitoring for MCP servers</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>📊 Real-Time Metrics</h3>
                <div class="real-time pulse" id="real-time-status">
                    <div>🟢 Connected</div>
                    <div id="real-time-data">Loading...</div>
                </div>
                <div class="metric">
                    <span>Active Sessions:</span>
                    <span class="metric-value" id="active-sessions">0</span>
                </div>
                <div class="metric">
                    <span>Total MCP Calls:</span>
                    <span class="metric-value" id="total-calls">0</span>
                </div>
                <div class="metric">
                    <span>WebSocket Connections:</span>
                    <span class="metric-value" id="ws-connections">0</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🚀 Quick Actions</h3>
                <button class="btn" onclick="createNewSession()">Create New Session</button>
                <button class="btn" onclick="refreshData()">Refresh Data</button>
                <button class="btn" onclick="exportAllData()">Export All Data</button>
                <button class="btn btn-danger" onclick="clearAllSessions()">Clear All Sessions</button>
            </div>
            
            <div class="card session-list">
                <h3>📋 Debug Sessions</h3>
                <div id="sessions-list">
                    <div class="session-item">
                        <div class="session-name">Loading sessions...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let currentSessionId = null;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadSessions();
            loadRealTimeMetrics();
            startWebSocket();
        });
        
        // Load debug sessions
        async function loadSessions() {
            try {
                const response = await fetch('/api/sessions');
                const data = await response.json();
                displaySessions(data.sessions);
            } catch (error) {
                console.error('Error loading sessions:', error);
            }
        }
        
        // Display sessions
        function displaySessions(sessions) {
            const container = document.getElementById('sessions-list');
            if (sessions.length === 0) {
                container.innerHTML = '<div class="session-item">No debug sessions found</div>';
                return;
            }
            
            container.innerHTML = sessions.map(session => `
                <div class="session-item">
                    <div class="session-name">${session.name}</div>
                    <div class="session-stats">
                        <div class="stat">Created: ${new Date(session.created_at).toLocaleString()}</div>
                        <div class="stat">Status: ${session.status}</div>
                        <div class="stat">MCP Calls: ${session.mcp_calls.length}</div>
                        <div class="stat">Errors: ${session.errors.length}</div>
                    </div>
                    <div>
                        <button class="btn" onclick="viewSession('${session.session_id}')">View Details</button>
                        <button class="btn" onclick="exportSession('${session.session_id}')">Export</button>
                    </div>
                </div>
            `).join('');
        }
        
        // Load real-time metrics
        async function loadRealTimeMetrics() {
            try {
                const response = await fetch('/api/real-time-metrics');
                const data = await response.json();
                
                document.getElementById('active-sessions').textContent = data.active_sessions;
                document.getElementById('total-calls').textContent = data.total_mcp_calls;
                document.getElementById('ws-connections').textContent = data.active_connections;
                
                document.getElementById('real-time-data').textContent = 
                    `Last updated: ${new Date(data.timestamp).toLocaleTimeString()}`;
            } catch (error) {
                console.error('Error loading real-time metrics:', error);
            }
        }
        
        // Start WebSocket connection
        function startWebSocket() {
            // This would connect to a specific session's WebSocket
            // For now, we'll just refresh data periodically
            setInterval(loadRealTimeMetrics, 2000);
        }
        
        // Create new session
        async function createNewSession() {
            const name = prompt('Enter session name:', `Debug Session ${Date.now()}`);
            if (!name) return;
            
            try {
                const response = await fetch('/api/sessions', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name})
                });
                const data = await response.json();
                alert(`Session created: ${data.session_id}`);
                loadSessions();
            } catch (error) {
                console.error('Error creating session:', error);
                alert('Error creating session');
            }
        }
        
        // View session details
        function viewSession(sessionId) {
            window.open(`/session/${sessionId}`, '_blank');
        }
        
        // Export session
        async function exportSession(sessionId) {
            try {
                const response = await fetch(`/api/sessions/${sessionId}/export`);
                const data = await response.json();
                alert(`Session exported to: ${data.filename}`);
            } catch (error) {
                console.error('Error exporting session:', error);
                alert('Error exporting session');
            }
        }
        
        // Refresh data
        function refreshData() {
            loadSessions();
            loadRealTimeMetrics();
        }
        
        // Export all data
        async function exportAllData() {
            try {
                const response = await fetch('/api/sessions');
                const data = await response.json();
                
                const exportData = {
                    timestamp: new Date().toISOString(),
                    sessions: data.sessions,
                    real_time_metrics: await fetch('/api/real-time-metrics').then(r => r.json())
                };
                
                const blob = new Blob([JSON.stringify(exportData, null, 2)], {type: 'application/json'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `mcp_debug_dashboard_${Date.now()}.json`;
                a.click();
                URL.revokeObjectURL(url);
            } catch (error) {
                console.error('Error exporting all data:', error);
                alert('Error exporting data');
            }
        }
        
        // Clear all sessions
        async function clearAllSessions() {
            if (!confirm('Are you sure you want to clear all sessions?')) return;
            
            try {
                // This would need to be implemented in the backend
                alert('Clear all sessions functionality not implemented yet');
            } catch (error) {
                console.error('Error clearing sessions:', error);
                alert('Error clearing sessions');
            }
        }
    </script>
</body>
</html>
        """
    
    def run(self, host: str = "127.0.0.1", port: int = 8004):
        """Run the MCP Debug Dashboard"""
        uvicorn.run(self.app, host=host, port=port)

# Create the FastAPI app instance
app = FastAPI(
    title="MCP Debug Dashboard",
    description="Advanced debugging and monitoring for MCP servers",
    version="1.0.0"
)

# Create the dashboard instance and set up routes
mcp_debug_dashboard = MCPDebugDashboard()
mcp_debug_dashboard.app = app
mcp_debug_dashboard.setup_routes()

if __name__ == "__main__":
    mcp_debug_dashboard.run()

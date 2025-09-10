#!/usr/bin/env python3
"""
LangGraph Studio Server
A simple implementation of LangGraph Studio functionality
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="LangGraph Studio Server",
    description="A simple LangGraph Studio implementation",
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

# Global state
active_connections: List[WebSocket] = []
workflows: Dict[str, Dict] = {}
execution_history: List[Dict] = []

class WorkflowRequest(BaseModel):
    name: str
    description: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, str]]

class ExecutionRequest(BaseModel):
    workflow_id: str
    input_data: Dict[str, Any]

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "service": "LangGraph Studio Server",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(active_connections),
        "workflows": len(workflows),
        "executions": len(execution_history)
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "langgraph-studio-server",
        "version": "1.0.0",
        "active_connections": len(active_connections),
        "workflows": len(workflows),
        "executions": len(execution_history)
    }

@app.get("/workflows")
async def list_workflows():
    """List all workflows"""
    return {
        "workflows": list(workflows.values()),
        "total": len(workflows)
    }

@app.post("/workflows")
async def create_workflow(workflow: WorkflowRequest):
    """Create a new workflow"""
    workflow_id = f"workflow_{len(workflows) + 1}"
    workflow_data = {
        "id": workflow_id,
        "name": workflow.name,
        "description": workflow.description,
        "nodes": workflow.nodes,
        "edges": workflow.edges,
        "created_at": datetime.now().isoformat(),
        "status": "created"
    }
    workflows[workflow_id] = workflow_data
    
    # Notify connected clients
    await broadcast_update({
        "type": "workflow_created",
        "workflow": workflow_data
    })
    
    return workflow_data

@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get a specific workflow"""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflows[workflow_id]

@app.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, execution: ExecutionRequest):
    """Execute a workflow"""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    execution_id = f"exec_{len(execution_history) + 1}"
    execution_data = {
        "id": execution_id,
        "workflow_id": workflow_id,
        "input_data": execution.input_data,
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "output": None,
        "logs": []
    }
    
    execution_history.append(execution_data)
    
    # Simulate workflow execution
    try:
        # Simple mock execution
        result = {
            "message": f"Workflow '{workflow_id}' executed successfully",
            "input": execution.input_data,
            "output": {"result": "mock_output", "status": "completed"},
            "execution_time": "0.1s"
        }
        
        execution_data["status"] = "completed"
        execution_data["output"] = result
        execution_data["completed_at"] = datetime.now().isoformat()
        
        # Notify connected clients
        await broadcast_update({
            "type": "execution_completed",
            "execution": execution_data
        })
        
        return execution_data
        
    except Exception as e:
        execution_data["status"] = "failed"
        execution_data["error"] = str(e)
        execution_data["completed_at"] = datetime.now().isoformat()
        
        await broadcast_update({
            "type": "execution_failed",
            "execution": execution_data
        })
        
        return execution_data

@app.get("/executions")
async def list_executions():
    """List all executions"""
    return {
        "executions": execution_history,
        "total": len(execution_history)
    }

@app.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get a specific execution"""
    for execution in execution_history:
        if execution["id"] == execution_id:
            return execution
    raise HTTPException(status_code=404, detail="Execution not found")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "initial_state",
            "workflows": list(workflows.values()),
            "executions": execution_history[-10:]  # Last 10 executions
        })
        
        while True:
            # Keep connection alive
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Active connections: {len(active_connections)}")

async def broadcast_update(message: Dict[str, Any]):
    """Broadcast update to all connected clients"""
    if active_connections:
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            active_connections.remove(connection)

@app.get("/studio")
async def studio_ui():
    """LangGraph Studio UI"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LangGraph Studio</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .workflow { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .status { padding: 5px 10px; border-radius: 3px; color: white; }
            .status.running { background: #007bff; }
            .status.completed { background: #28a745; }
            .status.failed { background: #dc3545; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
            .button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 LangGraph Studio</h1>
            <p>Workflow Development and Execution Environment</p>
            <p>Status: <span class="status running">Running</span></p>
        </div>
        
        <div>
            <h2>📊 System Status</h2>
            <p>Active Connections: <span id="connections">0</span></p>
            <p>Workflows: <span id="workflows">0</span></p>
            <p>Executions: <span id="executions">0</span></p>
        </div>
        
        <div>
            <h2>🔧 Quick Actions</h2>
            <button class="button" onclick="createSampleWorkflow()">Create Sample Workflow</button>
            <button class="button" onclick="executeSampleWorkflow()">Execute Sample Workflow</button>
            <button class="button" onclick="refreshStatus()">Refresh Status</button>
        </div>
        
        <div>
            <h2>📋 Recent Executions</h2>
            <div id="executions-list">Loading...</div>
        </div>
        
        <script>
            let ws = null;
            
            function connectWebSocket() {
                ws = new WebSocket('ws://localhost:8000/ws');
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateUI(data);
                };
                
                ws.onclose = function() {
                    setTimeout(connectWebSocket, 5000);
                };
            }
            
            function updateUI(data) {
                if (data.type === 'initial_state') {
                    document.getElementById('workflows').textContent = data.workflows.length;
                    document.getElementById('executions').textContent = data.executions.length;
                    updateExecutionsList(data.executions);
                }
            }
            
            function updateExecutionsList(executions) {
                const list = document.getElementById('executions-list');
                list.innerHTML = executions.map(exec => 
                    `<div class="workflow">
                        <strong>${exec.id}</strong> - 
                        <span class="status ${exec.status}">${exec.status}</span>
                        <br>Workflow: ${exec.workflow_id}
                        <br>Started: ${new Date(exec.started_at).toLocaleString()}
                    </div>`
                ).join('');
            }
            
            function createSampleWorkflow() {
                fetch('/workflows', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        name: 'Sample Workflow',
                        description: 'A sample workflow for testing',
                        nodes: [
                            {id: 'start', type: 'start', label: 'Start'},
                            {id: 'process', type: 'process', label: 'Process Data'},
                            {id: 'end', type: 'end', label: 'End'}
                        ],
                        edges: [
                            {from: 'start', to: 'process'},
                            {from: 'process', to: 'end'}
                        ]
                    })
                }).then(response => response.json())
                .then(data => {
                    alert('Sample workflow created!');
                    refreshStatus();
                });
            }
            
            function executeSampleWorkflow() {
                fetch('/workflows/workflow_1/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        workflow_id: 'workflow_1',
                        input_data: {message: 'Hello from LangGraph Studio!'}
                    })
                }).then(response => response.json())
                .then(data => {
                    alert('Workflow executed!');
                    refreshStatus();
                });
            }
            
            function refreshStatus() {
                fetch('/health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('connections').textContent = data.active_connections;
                    document.getElementById('workflows').textContent = data.workflows;
                    document.getElementById('executions').textContent = data.executions;
                });
            }
            
            // Initialize
            connectWebSocket();
            refreshStatus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🚀 Starting LangGraph Studio Server...")
    print("📊 Server will be available at: http://localhost:8000")
    print("🎨 Studio UI will be available at: http://localhost:8000/studio")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

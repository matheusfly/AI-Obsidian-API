#!/usr/bin/env python3
"""
HTTP Observability MCP Server
Provides HTTP API endpoints for the observability MCP server
"""

import asyncio
import json
import logging
import traceback
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
import time
import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import the observability MCP server
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from observability_mcp_server import ObservabilityMCP, TraceEvent, Checkpoint, PerformanceMetrics, TraceLevel, CheckpointType

# Configuration
LANGSMITH_API_KEY = "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"
LANGSMITH_PROJECT = "langgraph-observability"
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s',
    handlers=[
        logging.FileHandler('observability_http.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Observability MCP HTTP Server",
    description="HTTP API for observability MCP server with LangSmith integration",
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

# Global observability instance
observability = None

class TraceEventRequest(BaseModel):
    thread_id: str
    agent_id: str
    workflow_id: str = ""
    event_type: str
    level: str = "info"
    message: str
    data: Dict[str, Any] = {}
    tags: List[str] = []
    parent_event_id: Optional[str] = None

class CheckpointRequest(BaseModel):
    thread_id: str
    agent_id: str
    workflow_id: str
    checkpoint_type: str
    state_snapshot: Dict[str, Any]
    human_input_required: bool = False
    human_input_prompt: str = ""
    metadata: Dict[str, Any] = {}

class DebugSessionRequest(BaseModel):
    session_name: str
    thread_id: str
    agent_id: str
    workflow_id: str
    monitoring_level: str = "detailed"
    auto_checkpoint_interval: int = 0

@app.on_event("startup")
async def startup_event():
    """Initialize the observability MCP server on startup"""
    global observability
    try:
        observability = ObservabilityMCP()
        logger.info("Observability MCP server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize observability MCP server: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "observability_mcp": "running",
            "langsmith_integration": "active" if observability and observability.langsmith_client else "inactive"
        }
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Observability MCP HTTP Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "trace_events": "/mcp/call_tool (create_trace_event)",
            "checkpoints": "/mcp/call_tool (create_checkpoint)",
            "debug_sessions": "/mcp/call_tool (create_debug_session)",
            "performance": "/mcp/call_tool (get_performance_metrics)",
            "error_analysis": "/mcp/call_tool (analyze_error_patterns)"
        }
    }

@app.post("/mcp/call_tool")
async def call_mcp_tool(request: Dict[str, Any]):
    """Call MCP tool endpoint"""
    try:
        if not observability:
            raise HTTPException(status_code=500, detail="Observability MCP server not initialized")
        
        tool_name = request.get("name")
        arguments = request.get("arguments", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name is required")
        
        # Create a mock CallToolRequest
        class MockCallToolRequest:
            def __init__(self, name: str, arguments: Dict[str, Any]):
                self.name = name
                self.arguments = arguments
        
        mock_request = MockCallToolRequest(tool_name, arguments)
        
        # Call the appropriate tool method
        if tool_name == "create_trace_event":
            result = await observability._create_trace_event(arguments)
        elif tool_name == "create_checkpoint":
            result = await observability._create_checkpoint(arguments)
        elif tool_name == "get_traces":
            result = await observability._get_traces(arguments)
        elif tool_name == "get_checkpoints":
            result = await observability._get_checkpoints(arguments)
        elif tool_name == "time_travel_debug":
            result = await observability._time_travel_debug(arguments)
        elif tool_name == "get_performance_metrics":
            result = await observability._get_performance_metrics(arguments)
        elif tool_name == "start_performance_monitoring":
            result = await observability._start_performance_monitoring(arguments)
        elif tool_name == "stop_performance_monitoring":
            result = await observability._stop_performance_monitoring(arguments)
        elif tool_name == "get_debug_summary":
            result = await observability._get_debug_summary(arguments)
        elif tool_name == "export_traces_to_langsmith":
            result = await observability._export_traces_to_langsmith(arguments)
        elif tool_name == "analyze_error_patterns":
            result = await observability._analyze_error_patterns(arguments)
        elif tool_name == "get_agent_communication_log":
            result = await observability._get_agent_communication_log(arguments)
        elif tool_name == "create_debug_session":
            result = await observability._create_debug_session(arguments)
        elif tool_name == "get_debug_session_status":
            result = await observability._get_debug_session_status(arguments)
        elif tool_name == "correlate_errors_with_traces":
            result = await observability._correlate_errors_with_traces(arguments)
        elif tool_name == "generate_debug_report":
            result = await observability._generate_debug_report(arguments)
        elif tool_name == "monitor_langgraph_server_health":
            result = await observability._monitor_langgraph_server_health(arguments)
        elif tool_name == "trace_workflow_execution":
            result = await observability._trace_workflow_execution(arguments)
        elif tool_name == "optimize_agent_performance":
            result = await observability._optimize_agent_performance(arguments)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
        
        # Convert result to JSON response
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text if result.content else ""
            return {
                "success": not result.isError if hasattr(result, 'isError') else True,
                "content": content,
                "tool_name": tool_name
            }
        else:
            return {
                "success": True,
                "content": "Tool executed successfully",
                "tool_name": tool_name
            }
            
    except Exception as e:
        logger.error(f"Tool call failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Tool call failed: {str(e)}")

@app.get("/traces")
async def get_traces(thread_id: Optional[str] = None, limit: int = 100):
    """Get traces endpoint"""
    try:
        if not observability:
            raise HTTPException(status_code=500, detail="Observability MCP server not initialized")
        
        arguments = {"limit": limit}
        if thread_id:
            arguments["thread_id"] = thread_id
        
        result = await observability._get_traces(arguments)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text if result.content else "[]"
            try:
                traces = json.loads(content)
                return {"traces": traces, "count": len(traces)}
            except json.JSONDecodeError:
                return {"traces": [], "count": 0, "raw_content": content}
        else:
            return {"traces": [], "count": 0}
            
    except Exception as e:
        logger.error(f"Failed to get traces: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get traces: {str(e)}")

@app.get("/checkpoints")
async def get_checkpoints(thread_id: Optional[str] = None, limit: int = 50):
    """Get checkpoints endpoint"""
    try:
        if not observability:
            raise HTTPException(status_code=500, detail="Observability MCP server not initialized")
        
        arguments = {"limit": limit}
        if thread_id:
            arguments["thread_id"] = thread_id
        
        result = await observability._get_checkpoints(arguments)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text if result.content else "[]"
            try:
                checkpoints = json.loads(content)
                return {"checkpoints": checkpoints, "count": len(checkpoints)}
            except json.JSONDecodeError:
                return {"checkpoints": [], "count": 0, "raw_content": content}
        else:
            return {"checkpoints": [], "count": 0}
            
    except Exception as e:
        logger.error(f"Failed to get checkpoints: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get checkpoints: {str(e)}")

@app.get("/performance")
async def get_performance(thread_id: Optional[str] = None, agent_id: Optional[str] = None):
    """Get performance metrics endpoint"""
    try:
        if not observability:
            raise HTTPException(status_code=500, detail="Observability MCP server not initialized")
        
        arguments = {}
        if thread_id:
            arguments["thread_id"] = thread_id
        if agent_id:
            arguments["agent_id"] = agent_id
        
        result = await observability._get_performance_metrics(arguments)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text if result.content else "[]"
            try:
                metrics = json.loads(content)
                return {"performance_metrics": metrics, "count": len(metrics)}
            except json.JSONDecodeError:
                return {"performance_metrics": [], "count": 0, "raw_content": content}
        else:
            return {"performance_metrics": [], "count": 0}
            
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@app.get("/debug_sessions")
async def get_debug_sessions():
    """Get debug sessions endpoint"""
    try:
        if not observability:
            raise HTTPException(status_code=500, detail="Observability MCP server not initialized")
        
        if hasattr(observability, 'debug_sessions'):
            return {"debug_sessions": observability.debug_sessions}
        else:
            return {"debug_sessions": {}}
            
    except Exception as e:
        logger.error(f"Failed to get debug sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get debug sessions: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")

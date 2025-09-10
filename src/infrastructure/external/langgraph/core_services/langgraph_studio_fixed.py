#!/usr/bin/env python3
"""
Fixed LangGraph Studio Server - Simple FastAPI implementation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
import asyncio
import json
import uuid
from datetime import datetime

app = FastAPI(title="LangGraph Studio Server", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for assistants and runs
assistants_db: Dict[str, Dict] = {}
runs_db: Dict[str, Dict] = {}

class AssistantCreate(BaseModel):
    name: str
    description: Optional[str] = None
    graph_id: str = "agent"

class RunCreate(BaseModel):
    assistant_id: str
    input_data: Dict[str, Any]
    thread_id: Optional[str] = None

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "langgraph-studio-server",
        "version": "1.0.0",
        "assistants": len(assistants_db),
        "runs": len(runs_db)
    }

@app.get("/assistants")
async def list_assistants():
    """List all assistants"""
    return {
        "assistants": list(assistants_db.values()),
        "total": len(assistants_db)
    }

@app.get("/assistants/{assistant_id}")
async def get_assistant(assistant_id: str):
    """Get specific assistant"""
    if assistant_id not in assistants_db:
        raise HTTPException(status_code=404, detail="Assistant not found")
    return assistants_db[assistant_id]

@app.get("/assistants/{assistant_id}/schemas")
async def get_assistant_schemas(assistant_id: str):
    """Get assistant schemas"""
    if assistant_id not in assistants_db:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    # Return a simple schema for the agent
    return {
        "input_schema": {
            "type": "object",
            "properties": {
                "messages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "type": {"type": "string", "enum": ["human", "ai"]}
                        }
                    }
                }
            },
            "required": ["messages"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "messages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "type": {"type": "string", "enum": ["human", "ai"]}
                        }
                    }
                }
            }
        }
    }

@app.post("/assistants")
async def create_assistant(assistant: AssistantCreate):
    """Create a new assistant"""
    assistant_id = str(uuid.uuid4())
    assistant_data = {
        "id": assistant_id,
        "name": assistant.name,
        "description": assistant.description,
        "graph_id": assistant.graph_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    assistants_db[assistant_id] = assistant_data
    return assistant_data

@app.post("/runs")
async def create_run(run: RunCreate):
    """Create a new run"""
    run_id = str(uuid.uuid4())
    thread_id = run.thread_id or str(uuid.uuid4())
    
    # Simulate running the workflow
    messages = run.input_data.get("messages", [])
    if messages:
        last_message = messages[-1]
        if isinstance(last_message, dict) and last_message.get("type") == "human":
            response_content = f"Echo: {last_message.get('content', '')}"
        else:
            response_content = "Hello from LangGraph Studio!"
    else:
        response_content = "No messages provided"
    
    # Create response
    response_messages = messages + [{
        "content": response_content,
        "type": "ai"
    }]
    
    run_data = {
        "id": run_id,
        "assistant_id": run.assistant_id,
        "thread_id": thread_id,
        "status": "completed",
        "input": run.input_data,
        "output": {"messages": response_messages},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    runs_db[run_id] = run_data
    return run_data

@app.get("/runs")
async def list_runs(assistant_id: Optional[str] = None, limit: int = 10):
    """List runs"""
    runs = list(runs_db.values())
    if assistant_id:
        runs = [r for r in runs if r["assistant_id"] == assistant_id]
    
    runs = runs[:limit]
    return {
        "runs": runs,
        "total": len(runs)
    }

@app.get("/runs/{run_id}")
async def get_run(run_id: str):
    """Get specific run"""
    if run_id not in runs_db:
        raise HTTPException(status_code=404, detail="Run not found")
    return runs_db[run_id]

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LangGraph Studio Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "assistants": "/assistants",
            "runs": "/runs",
            "docs": "/docs"
        }
    }

# Initialize with a default assistant
@app.on_event("startup")
async def startup():
    """Initialize default assistant on startup"""
    default_assistant = {
        "id": "4c28d832-c8fa-5f9c-a13e-359aff3a2c9e",
        "name": "Echo Agent",
        "description": "Simple echo agent for testing",
        "graph_id": "agent",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    assistants_db[default_assistant["id"]] = default_assistant
    print("✅ Default assistant created")

if __name__ == "__main__":
    print("🚀 Starting LangGraph Studio Server...")
    print("🌐 Server will be available at: http://127.0.0.1:8125")
    print("📚 API docs available at: http://127.0.0.1:8125/docs")
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8125,
        log_level="info"
    )

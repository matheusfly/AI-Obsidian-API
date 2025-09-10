#!/usr/bin/env python3
"""
Mock Obsidian Local REST API Server
This simulates the Obsidian API for testing when the real plugin is not available
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os

app = FastAPI(
    title="Mock Obsidian Local REST API",
    description="Mock server for testing LangGraph integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
VAULT_NAME = "Nomade Milionario"
VAULT_PATH = f"D:\\{VAULT_NAME}"

mock_vault_data = {
    "vaults": [
        {
            "name": VAULT_NAME,
            "path": VAULT_PATH,
            "active": True
        }
    ]
}

mock_files = [
    {
        "path": "README.md",
        "name": "README.md",
        "type": "file",
        "size": 1024,
        "modified": "2025-09-06T00:00:00Z"
    },
    {
        "path": "test_note.md", 
        "name": "test_note.md",
        "type": "file",
        "size": 512,
        "modified": "2025-09-06T00:00:00Z"
    },
    {
        "path": "langgraph_integration.md",
        "name": "langgraph_integration.md", 
        "type": "file",
        "size": 2048,
        "modified": "2025-09-06T00:00:00Z"
    }
]

mock_file_contents = {
    "README.md": """# Nomade Milionario

Welcome to the Nomade Milionario vault!

## About
This vault contains notes about digital nomadism, entrepreneurship, and personal development.

## Structure
- Projects
- Ideas
- Resources
- Notes

## LangGraph Integration
This vault is integrated with LangGraph for AI-powered note management and retrieval.
""",
    "test_note.md": """# Test Note

This is a test note created by LangGraph integration.

## Content
- Item 1: Testing LangGraph workflows
- Item 2: Obsidian API integration
- Item 3: MCP server communication

## Status
✅ Integration working
✅ API calls successful
✅ Workflow completed
""",
    "langgraph_integration.md": """# LangGraph Integration

This document describes the LangGraph integration with Obsidian.

## Features
- AI-powered note search
- Automated content generation
- Workflow orchestration
- Real-time collaboration

## API Endpoints
- `/vault` - Get vault information
- `/vault/files` - List files
- `/vault/file` - Read file content
- `/vault/search` - Search notes

## Workflows
1. Content Analysis
2. Note Generation
3. Search and Retrieval
4. Workflow Management
"""
}

class FileContent(BaseModel):
    content: str
    path: str

class SearchQuery(BaseModel):
    query: str
    vault_name: str = VAULT_NAME

@app.get("/")
async def root():
    return {"message": "Mock Obsidian Local REST API", "version": "1.0.0"}

@app.get("/vault")
async def get_vault(authorization: str = Header(None)):
    """Get vault information"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    return mock_vault_data

@app.get("/vault/files")
async def list_files(authorization: str = Header(None)):
    """List files in the vault"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    return {"files": mock_files}

@app.get("/vault/file")
async def read_file(path: str, authorization: str = Header(None)):
    """Read file content"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if path not in mock_file_contents:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileContent(
        content=mock_file_contents[path],
        path=path
    )

@app.post("/vault/file")
async def write_file(
    path: str,
    content: str,
    authorization: str = Header(None)
):
    """Write file content"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    mock_file_contents[path] = content
    
    # Add to mock files if not exists
    if not any(f["path"] == path for f in mock_files):
        mock_files.append({
            "path": path,
            "name": os.path.basename(path),
            "type": "file",
            "size": len(content),
            "modified": "2025-09-06T00:00:00Z"
        })
    
    return {"success": True, "path": path, "message": "File written successfully"}

@app.post("/vault/search")
async def search_notes(query: SearchQuery, authorization: str = Header(None)):
    """Search notes in the vault"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Simple search implementation
    results = []
    search_term = query.query.lower()
    
    for file_info in mock_files:
        if search_term in file_info["name"].lower():
            results.append(file_info)
        elif file_info["path"] in mock_file_contents:
            content = mock_file_contents[file_info["path"]].lower()
            if search_term in content:
                results.append(file_info)
    
    return {
        "query": query.query,
        "results": results,
        "total": len(results)
    }

@app.post("/vault/{vault_name}/search")
async def search_vault_notes(vault_name: str, query: SearchQuery, authorization: str = Header(None)):
    """Search notes in specific vault"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if vault_name != VAULT_NAME:
        raise HTTPException(status_code=404, detail="Vault not found")
    
    # Simple search implementation
    results = []
    search_term = query.query.lower()
    
    for file_info in mock_files:
        if search_term in file_info["name"].lower():
            results.append(file_info)
        elif file_info["path"] in mock_file_contents:
            content = mock_file_contents[file_info["path"]].lower()
            if search_term in content:
                results.append(file_info)
    
    return {
        "query": query.query,
        "vault_name": vault_name,
        "results": results,
        "total": len(results)
    }

@app.put("/vault/{file_path}")
async def put_file(file_path: str, content: str, authorization: str = Header(None)):
    """Write file content to specific path"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    mock_file_contents[file_path] = content
    
    # Add to mock files if not exists
    if not any(f["path"] == file_path for f in mock_files):
        mock_files.append({
            "path": file_path,
            "name": os.path.basename(file_path),
            "type": "file",
            "size": len(content),
            "modified": "2025-09-06T00:00:00Z"
        })
    
    return {"success": True, "path": file_path, "message": "File written successfully"}

@app.get("/vault/stats")
async def get_vault_stats(authorization: str = Header(None)):
    """Get vault statistics"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    total_files = len(mock_files)
    total_size = sum(f.get("size", 0) for f in mock_files)
    
    return {
        "vault_name": VAULT_NAME,
        "total_files": total_files,
        "total_size": total_size,
        "last_modified": "2025-09-06T00:00:00Z"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Mock Obsidian Local REST API",
        "timestamp": "2025-09-06T00:00:00Z"
    }

if __name__ == "__main__":
    print("🚀 Starting Mock Obsidian Local REST API Server...")
    print(f"📍 Vault: {VAULT_NAME}")
    print(f"📁 Path: {VAULT_PATH}")
    print("🌐 Server: http://127.0.0.1:27123")
    print("🔑 API Key: b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=27123,
        log_level="info"
    )

"""
Minimal API Gateway for immediate deployment
Hotfix version with minimal dependencies
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Data Vault Obsidian API Gateway",
    description="Minimal API Gateway for Obsidian integration",
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

# Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8002")
CHROMADB_URL = os.getenv("CHROMADB_URL", "http://localhost:8000")
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "D:/Nomade Milionario")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0",
        "timestamp": "2025-01-01T00:00:00Z"
    }

@app.get("/api/v1/obsidian/vaults")
async def list_vaults():
    """List available Obsidian vaults"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_SERVER_URL}/tools/obsidian_list_vaults",
                json={},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "vaults": data.get("vaults", []),
                    "message": "Vaults retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "vaults": [],
                    "message": f"MCP Server error: {response.status_code}"
                }
    except Exception as e:
        logger.error(f"Error listing vaults: {e}")
        return {
            "success": False,
            "vaults": [],
            "message": f"Error: {str(e)}"
        }

@app.get("/api/v1/obsidian/files")
async def list_files(vault: str = "Nomade Milionario", path: str = "", recursive: bool = True, limit: int = 100):
    """List files in Obsidian vault"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_SERVER_URL}/tools/obsidian_list_files",
                json={
                    "vault_name": vault,
                    "path": path,
                    "recursive": recursive,
                    "limit": limit
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "files": data.get("files", []),
                    "message": "Files retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "files": [],
                    "message": f"MCP Server error: {response.status_code}"
                }
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return {
            "success": False,
            "files": [],
            "message": f"Error: {str(e)}"
        }

@app.get("/api/v1/obsidian/read/{file_path:path}")
async def read_file(file_path: str, vault: str = "Nomade Milionario"):
    """Read a file from Obsidian vault"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_SERVER_URL}/tools/obsidian_read_file",
                json={
                    "vault_name": vault,
                    "file_path": file_path
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "content": data.get("content", ""),
                    "message": "File read successfully"
                }
            else:
                return {
                    "success": False,
                    "content": "",
                    "message": f"MCP Server error: {response.status_code}"
                }
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return {
            "success": False,
            "content": "",
            "message": f"Error: {str(e)}"
        }

@app.get("/api/v1/chromadb/collections")
async def list_collections():
    """List ChromaDB collections"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CHROMADB_URL}/api/v1/collections",
                timeout=10.0
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "collections": response.json(),
                    "message": "Collections retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "collections": [],
                    "message": f"ChromaDB error: {response.status_code}"
                }
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        return {
            "success": False,
            "collections": [],
            "message": f"Error: {str(e)}"
        }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return {
        "http_requests_total": 0,
        "http_request_duration_seconds": 0,
        "service_status": "healthy"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

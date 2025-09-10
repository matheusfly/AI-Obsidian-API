#!/usr/bin/env python3
"""
MCP Integration Server
Connects LangGraph with all configured MCP servers from mcp.json
"""

import asyncio
import json
import logging
import subprocess
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPCallRequest(BaseModel):
    server_name: str
    tool_name: str
    arguments: Dict[str, Any] = {}

class MCPCallResponse(BaseModel):
    success: bool
    result: Any = None
    error: str = None
    execution_time_ms: float = 0.0

class MCPIntegrationServer:
    """MCP Integration Server for LangGraph workflows"""
    
    def __init__(self, mcp_config_path: str = "c:/Users/mathe/.cursor/mcp.json"):
        self.mcp_config_path = mcp_config_path
        self.mcp_servers = {}
        self.server_processes = {}
        self.active_connections = {}
        self.call_history = []
        self.performance_metrics = {}
        
        # Load MCP configuration
        self.load_mcp_config()
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="MCP Integration Server",
            description="Integrates LangGraph with all configured MCP servers",
            version="1.0.0"
        )
        self.setup_routes()
    
    def load_mcp_config(self):
        """Load MCP configuration from mcp.json"""
        try:
            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)
            
            self.mcp_servers = config.get('mcpServers', {})
            logger.info(f"Loaded {len(self.mcp_servers)} MCP servers from configuration")
            
            # Log available servers
            for server_name, server_config in self.mcp_servers.items():
                logger.info(f"  - {server_name}: {server_config.get('command', 'URL')}")
                
        except Exception as e:
            logger.error(f"Failed to load MCP configuration: {e}")
            self.mcp_servers = {}
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "mcp_servers": len(self.mcp_servers),
                "active_connections": len(self.active_connections)
            }
        
        @self.app.get("/mcp/servers")
        async def list_servers():
            """List all available MCP servers"""
            return {
                "servers": list(self.mcp_servers.keys()),
                "total": len(self.mcp_servers)
            }
        
        @self.app.get("/mcp/servers/{server_name}")
        async def get_server_info(server_name: str):
            """Get information about a specific MCP server"""
            if server_name not in self.mcp_servers:
                raise HTTPException(status_code=404, detail="Server not found")
            
            server_config = self.mcp_servers[server_name]
            return {
                "name": server_name,
                "config": server_config,
                "status": "available" if server_name in self.active_connections else "inactive"
            }
        
        @self.app.post("/mcp/call")
        async def call_mcp_tool(request: MCPCallRequest):
            """Call a tool on an MCP server"""
            start_time = time.time()
            
            try:
                result = await self.call_mcp_tool_async(
                    request.server_name,
                    request.tool_name,
                    request.arguments
                )
                
                execution_time = (time.time() - start_time) * 1000
                
                # Log the call
                call_record = {
                    "timestamp": datetime.now().isoformat(),
                    "server": request.server_name,
                    "tool": request.tool_name,
                    "arguments": request.arguments,
                    "execution_time_ms": execution_time,
                    "success": True
                }
                self.call_history.append(call_record)
                
                return MCPCallResponse(
                    success=True,
                    result=result,
                    execution_time_ms=execution_time
                )
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                error_msg = str(e)
                
                # Log the error
                call_record = {
                    "timestamp": datetime.now().isoformat(),
                    "server": request.server_name,
                    "tool": request.tool_name,
                    "arguments": request.arguments,
                    "execution_time_ms": execution_time,
                    "success": False,
                    "error": error_msg
                }
                self.call_history.append(call_record)
                
                return MCPCallResponse(
                    success=False,
                    error=error_msg,
                    execution_time_ms=execution_time
                )
        
        @self.app.get("/mcp/history")
        async def get_call_history(limit: int = 100):
            """Get MCP call history"""
            return {
                "calls": self.call_history[-limit:],
                "total": len(self.call_history)
            }
        
        @self.app.get("/mcp/metrics")
        async def get_performance_metrics():
            """Get performance metrics for MCP calls"""
            return {
                "total_calls": len(self.call_history),
                "successful_calls": len([c for c in self.call_history if c.get("success", False)]),
                "failed_calls": len([c for c in self.call_history if not c.get("success", False)]),
                "average_execution_time": self.calculate_average_execution_time(),
                "server_metrics": self.calculate_server_metrics()
            }
        
        @self.app.post("/mcp/batch")
        async def batch_call_mcp_tools(requests: List[MCPCallRequest]):
            """Execute multiple MCP calls in batch"""
            results = []
            
            for request in requests:
                result = await self.call_mcp_tool_async(
                    request.server_name,
                    request.tool_name,
                    request.arguments
                )
                results.append({
                    "server": request.server_name,
                    "tool": request.tool_name,
                    "result": result
                })
            
            return {"results": results}
        
        @self.app.get("/mcp/debug")
        async def debug_mcp_servers():
            """Debug information about MCP servers"""
            debug_info = {
                "timestamp": datetime.now().isoformat(),
                "total_servers": len(self.mcp_servers),
                "active_connections": len(self.active_connections),
                "servers": {}
            }
            
            for server_name, server_config in self.mcp_servers.items():
                debug_info["servers"][server_name] = {
                    "config": server_config,
                    "status": "active" if server_name in self.active_connections else "inactive",
                    "calls": len([c for c in self.call_history if c.get("server") == server_name])
                }
            
            return debug_info
    
    async def call_mcp_tool_async(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on an MCP server asynchronously"""
        if server_name not in self.mcp_servers:
            raise ValueError(f"MCP server '{server_name}' not found")
        
        server_config = self.mcp_servers[server_name]
        
        # Handle different MCP server types
        if "url" in server_config:
            # HTTP-based MCP server
            return await self.call_http_mcp_server(server_config["url"], tool_name, arguments)
        elif "command" in server_config:
            # Command-based MCP server
            return await self.call_command_mcp_server(server_config, tool_name, arguments)
        else:
            raise ValueError(f"Unsupported MCP server configuration for '{server_name}'")
    
    async def call_http_mcp_server(self, url: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an HTTP-based MCP server"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            payload = {
                "name": tool_name,
                "arguments": arguments
            }
            
            response = await client.post(f"{url}/mcp/call_tool", json=payload)
            response.raise_for_status()
            
            return response.json()
    
    async def call_command_mcp_server(self, server_config: Dict[str, Any], tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a command-based MCP server"""
        # This is a simplified implementation
        # In a real implementation, you would need to establish proper MCP protocol communication
        
        command = server_config.get("command", "npx")
        args = server_config.get("args", [])
        env = server_config.get("env", {})
        working_dir = server_config.get("working_directory")
        
        # Create the command
        full_command = [command] + args
        
        # Prepare environment
        import os
        process_env = os.environ.copy()
        process_env.update(env)
        
        try:
            # Execute the command
            process = await asyncio.create_subprocess_exec(
                *full_command,
                env=process_env,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send the tool call via stdin
            tool_call = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            stdout, stderr = await process.communicate(
                input=json.dumps(tool_call).encode()
            )
            
            if process.returncode != 0:
                raise RuntimeError(f"Command failed: {stderr.decode()}")
            
            # Parse the response
            response = json.loads(stdout.decode())
            
            if "error" in response:
                raise RuntimeError(f"MCP error: {response['error']}")
            
            return response.get("result", {})
            
        except Exception as e:
            logger.error(f"Failed to call MCP server: {e}")
            raise
    
    def calculate_average_execution_time(self) -> float:
        """Calculate average execution time for MCP calls"""
        if not self.call_history:
            return 0.0
        
        total_time = sum(call.get("execution_time_ms", 0) for call in self.call_history)
        return total_time / len(self.call_history)
    
    def calculate_server_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Calculate metrics per MCP server"""
        server_metrics = {}
        
        for call in self.call_history:
            server = call.get("server", "unknown")
            if server not in server_metrics:
                server_metrics[server] = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "total_execution_time": 0.0,
                    "average_execution_time": 0.0
                }
            
            server_metrics[server]["total_calls"] += 1
            if call.get("success", False):
                server_metrics[server]["successful_calls"] += 1
            else:
                server_metrics[server]["failed_calls"] += 1
            
            server_metrics[server]["total_execution_time"] += call.get("execution_time_ms", 0)
        
        # Calculate averages
        for server, metrics in server_metrics.items():
            if metrics["total_calls"] > 0:
                metrics["average_execution_time"] = metrics["total_execution_time"] / metrics["total_calls"]
        
        return server_metrics

# Create the server instance
mcp_integration = MCPIntegrationServer()
app = mcp_integration.app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)

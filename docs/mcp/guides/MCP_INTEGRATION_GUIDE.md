# MCP Integration Guide

## Overview

This guide provides comprehensive instructions for implementing and integrating Model Context Protocol (MCP) servers with the LangGraph + Obsidian Vault Integration System.

## Table of Contents

1. [MCP Server Implementation](#mcp-server-implementation)
2. [Tool Development](#tool-development)
3. [LangGraph Integration](#langgraph-integration)
4. [Testing MCP Tools](#testing-mcp-tools)
5. [Advanced Patterns](#advanced-patterns)

## MCP Server Implementation

### Basic MCP Server Structure

```python
# mcp_tools/obsidian_mcp_server.py
from fastmcp import FastMCP
from mcp_tools.models import *
from mcp_tools.registry import tool_registry

# Create MCP server
mcp = FastMCP("obsidian-mcp-server")

@mcp.tool()
async def obsidian_read_note(input: ReadNoteInput) -> Dict[str, Any]:
    """Read the content of a specific note from an Obsidian vault."""
    try:
        # Implementation here
        return {
            "content": content,
            "metadata": metadata,
            "hash": file_hash
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def obsidian_put_file(input: PutFileInput) -> Dict[str, Any]:
    """Create or update a file in an Obsidian vault."""
    try:
        # Implementation here
        return {
            "success": True,
            "message": "File created/updated successfully",
            "file_path": input.file_path
        }
    except Exception as e:
        return {"error": str(e)}

# Register tools
tool_registry.register_all(mcp)

# Run server
if __name__ == "__main__":
    mcp.run(port=8002)
```

### Tool Input/Output Models

```python
# mcp_tools/models.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ReadNoteInput(BaseModel):
    vault_name: str
    file_path: str
    include_metadata: bool = True

class PutFileInput(BaseModel):
    vault_name: str
    file_path: str
    content: str
    create_dirs: bool = True

class SearchNotesInput(BaseModel):
    vault_name: str
    query: str
    limit: int = 10
    include_content: bool = False

class ListFilesInput(BaseModel):
    vault_name: str
    path: str = ""
    recursive: bool = True
    limit: int = 100
```

## Tool Development

### Core Obsidian Tools

```python
# mcp_tools/obsidian_tools.py
import httpx
from typing import Dict, Any

class ObsidianTools:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"}
        )
    
    async def read_note(self, vault_name: str, file_path: str) -> Dict[str, Any]:
        """Read a note from the vault."""
        response = await self.client.get(
            f"{self.base_url}/vault/{vault_name}/file/{file_path}"
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "content": data.get("content", ""),
                "metadata": data.get("metadata", {}),
                "hash": data.get("hash", ""),
                "success": True
            }
        else:
            return {"error": f"Failed to read note: {response.text}"}
    
    async def put_file(self, vault_name: str, file_path: str, content: str) -> Dict[str, Any]:
        """Create or update a file in the vault."""
        response = await self.client.put(
            f"{self.base_url}/vault/{vault_name}/file/{file_path}",
            json={"content": content}
        )
        if response.status_code in [200, 201]:
            return {
                "success": True,
                "message": "File created/updated successfully",
                "file_path": file_path
            }
        else:
            return {"error": f"Failed to create/update file: {response.text}"}
    
    async def search_notes(self, vault_name: str, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for notes in the vault."""
        response = await self.client.post(
            f"{self.base_url}/vault/{vault_name}/search",
            json={"query": query, "limit": limit}
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "results": data.get("results", []),
                "total": data.get("total", 0),
                "success": True
            }
        else:
            return {"error": f"Failed to search notes: {response.text}"}
```

### Advanced Tools

```python
# mcp_tools/advanced_tools.py
from typing import List, Dict, Any
import asyncio

class AdvancedTools:
    def __init__(self, obsidian_tools: ObsidianTools):
        self.obsidian_tools = obsidian_tools
    
    async def batch_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple operations in batch."""
        results = []
        for operation in operations:
            if operation["type"] == "read":
                result = await self.obsidian_tools.read_note(
                    operation["vault_name"],
                    operation["file_path"]
                )
            elif operation["type"] == "write":
                result = await self.obsidian_tools.put_file(
                    operation["vault_name"],
                    operation["file_path"],
                    operation["content"]
                )
            results.append(result)
        
        return {
            "results": results,
            "total": len(results),
            "success": all(r.get("success", False) for r in results)
        }
    
    async def parallel_search(self, vault_name: str, queries: List[str]) -> Dict[str, Any]:
        """Execute multiple searches in parallel."""
        tasks = [
            self.obsidian_tools.search_notes(vault_name, query)
            for query in queries
        ]
        results = await asyncio.gather(*tasks)
        
        return {
            "results": results,
            "total_queries": len(queries),
            "success": all(r.get("success", False) for r in results)
        }
```

## LangGraph Integration

### Agent Workflow with MCP Tools

```python
# langgraph_workflows/obsidian_agent.py
from langgraph import StateGraph, END
from langgraph_workflows.models import AgentState
from mcp_tools.obsidian_mcp_server import mcp

def create_agent_workflow():
    """Create the agent workflow with MCP tools."""
    
    def research_node(state: AgentState) -> AgentState:
        """Research node that uses MCP tools to gather information."""
        # Use MCP tools to search for relevant information
        search_results = mcp.call_tool("obsidian_search_notes", {
            "vault_name": state.vault_name,
            "query": state.user_input,
            "limit": 5
        })
        
        # Process search results
        state.research_data = search_results.get("results", [])
        state.message = f"Found {len(state.research_data)} relevant notes"
        
        return state
    
    def write_node(state: AgentState) -> AgentState:
        """Write node that uses MCP tools to create content."""
        # Use MCP tools to create or update files
        write_result = mcp.call_tool("obsidian_put_file", {
            "vault_name": state.vault_name,
            "file_path": state.output_path,
            "content": state.generated_content
        })
        
        if write_result.get("success"):
            state.message = "Content written successfully"
            state.success = True
        else:
            state.message = f"Failed to write content: {write_result.get('error')}"
            state.success = False
        
        return state
    
    def human_review_node(state: AgentState) -> AgentState:
        """Human review node for approval workflow."""
        # This would integrate with human-in-the-loop approval
        state.requires_approval = True
        state.message = "Content requires human approval"
        
        return state
    
    # Create workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("write", write_node)
    workflow.add_node("human_review", human_review_node)
    
    # Add edges
    workflow.add_edge("research", "write")
    workflow.add_edge("write", "human_review")
    workflow.add_edge("human_review", END)
    
    # Set entry point
    workflow.set_entry_point("research")
    
    return workflow.compile()
```

### Tool Call Handling

```python
# langgraph_workflows/tool_handler.py
from typing import Dict, Any, List
import asyncio

class MCPToolHandler:
    def __init__(self, mcp_server_url: str):
        self.mcp_server_url = mcp_server_url
        self.client = httpx.AsyncClient()
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        try:
            response = await self.client.post(
                f"{self.mcp_server_url}/tools/{tool_name}",
                json=parameters
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def call_multiple_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Call multiple tools in parallel."""
        tasks = [
            self.call_tool(call["tool_name"], call["parameters"])
            for call in tool_calls
        ]
        return await asyncio.gather(*tasks)
```

## Testing MCP Tools

### Unit Tests

```python
# tests/test_mcp_tools.py
import pytest
from unittest.mock import Mock, patch
from mcp_tools.obsidian_mcp_server import mcp
from mcp_tools.models import ReadNoteInput, PutFileInput

class TestMCPTools:
    @pytest.fixture
    def mock_obsidian_client(self):
        with patch('mcp_tools.obsidian_mcp_server.obsidian_client') as mock:
            yield mock
    
    def test_read_note_tool(self, mock_obsidian_client):
        """Test read note tool."""
        # Mock response
        mock_obsidian_client.read_note.return_value = {
            "content": "# Test Note\n\nContent",
            "metadata": {"size": 100},
            "hash": "abc123"
        }
        
        # Test tool
        input_data = ReadNoteInput(
            vault_name="test_vault",
            file_path="test.md"
        )
        
        result = mcp.call_tool("obsidian_read_note", input_data.dict())
        
        assert result["content"] == "# Test Note\n\nContent"
        assert result["metadata"]["size"] == 100
        assert result["hash"] == "abc123"
    
    def test_put_file_tool(self, mock_obsidian_client):
        """Test put file tool."""
        # Mock response
        mock_obsidian_client.put_file.return_value = {
            "success": True,
            "message": "File created successfully"
        }
        
        # Test tool
        input_data = PutFileInput(
            vault_name="test_vault",
            file_path="test.md",
            content="# Test Note\n\nContent"
        )
        
        result = mcp.call_tool("obsidian_put_file", input_data.dict())
        
        assert result["success"] is True
        assert "created successfully" in result["message"]
```

### Integration Tests

```python
# tests/test_mcp_integration.py
import pytest
from fastapi.testclient import TestClient
from mcp_tools.obsidian_mcp_server import app

class TestMCPIntegration:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_tool_endpoints(self, client):
        """Test MCP tool endpoints."""
        # Test read note endpoint
        response = client.post(
            "/tools/read_note",
            json={
                "vault_name": "test_vault",
                "file_path": "test.md"
            }
        )
        assert response.status_code in [200, 404]
        
        # Test put file endpoint
        response = client.post(
            "/tools/put_file",
            json={
                "vault_name": "test_vault",
                "file_path": "test.md",
                "content": "# Test\n\nContent"
            }
        )
        assert response.status_code in [200, 201]
```

## Advanced Patterns

### Tool Chaining

```python
# mcp_tools/advanced_patterns.py
from typing import List, Dict, Any
import asyncio

class ToolChaining:
    def __init__(self, mcp_handler: MCPToolHandler):
        self.mcp_handler = mcp_handler
    
    async def chain_tools(self, tool_chain: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a chain of tools where output of one feeds into the next."""
        results = []
        current_input = None
        
        for tool_call in tool_chain:
            if current_input:
                tool_call["parameters"].update(current_input)
            
            result = await self.mcp_handler.call_tool(
                tool_call["tool_name"],
                tool_call["parameters"]
            )
            
            results.append(result)
            
            # Extract output for next tool
            if result.get("success"):
                current_input = result.get("output", {})
            else:
                break
        
        return {
            "results": results,
            "success": all(r.get("success", False) for r in results)
        }
```

### Error Handling and Retry

```python
# mcp_tools/error_handling.py
import asyncio
from typing import Dict, Any, Callable
from functools import wraps

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed tool calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    result = await func(*args, **kwargs)
                    if result.get("success", False):
                        return result
                except Exception as e:
                    if attempt == max_retries - 1:
                        return {"error": str(e), "success": False}
                
                await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
            
            return {"error": "Max retries exceeded", "success": False}
        return wrapper
    return decorator

class RobustMCPHandler:
    def __init__(self, mcp_server_url: str):
        self.mcp_server_url = mcp_server_url
        self.client = httpx.AsyncClient()
    
    @retry_on_failure(max_retries=3)
    async def call_tool_with_retry(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with retry logic."""
        response = await self.client.post(
            f"{self.mcp_server_url}/tools/{tool_name}",
            json=parameters
        )
        return response.json()
```

## Conclusion

This MCP integration guide provides comprehensive instructions for implementing and integrating MCP servers with the LangGraph + Obsidian Vault Integration System. The guide covers everything from basic MCP server implementation to advanced patterns like tool chaining and error handling.

The modular approach allows for flexible tool development and easy integration with LangGraph workflows. The comprehensive testing strategy ensures reliable operation and quick issue resolution.

By following this guide, developers can create robust MCP tools that seamlessly integrate with the LangGraph system, providing powerful automation capabilities for Obsidian vault operations.

#!/usr/bin/env python3
"""
MCP Integrated LangGraph Agent
Integrates with all MCP servers from mcp.json configuration
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, TypedDict
from pathlib import Path

import httpx
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPAgentState(TypedDict):
    """State for MCP Integrated Agent"""
    messages: List[Dict[str, Any]]
    current_task: str
    mcp_results: Dict[str, Any]
    vault_data: Dict[str, Any]
    search_results: Dict[str, Any]
    analysis_results: Dict[str, Any]
    final_response: str
    error_log: List[str]
    performance_metrics: Dict[str, float]

class MCPIntegratedAgent:
    """LangGraph Agent integrated with all MCP servers"""
    
    def __init__(self, mcp_integration_url: str = "http://127.0.0.1:8003"):
        self.mcp_integration_url = mcp_integration_url
        self.available_servers = []
        self.performance_metrics = {}
        
    async def initialize(self):
        """Initialize the agent and discover available MCP servers"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.mcp_integration_url}/mcp/servers")
                if response.status_code == 200:
                    data = response.json()
                    self.available_servers = data.get("servers", [])
                    logger.info(f"Discovered {len(self.available_servers)} MCP servers: {self.available_servers}")
                else:
                    logger.error(f"Failed to discover MCP servers: {response.status_code}")
        except Exception as e:
            logger.error(f"Error initializing MCP agent: {e}")
    
    @tool
    async def call_mcp_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool on any MCP server"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "arguments": arguments or {}
                }
                
                response = await client.post(f"{self.mcp_integration_url}/mcp/call", json=payload)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"MCP call successful: {server_name}.{tool_name}")
                return result
                
        except Exception as e:
            error_msg = f"MCP call failed: {server_name}.{tool_name} - {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    @tool
    async def search_web(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search the web using MCP web search tools"""
        try:
            # Try multiple web search providers
            search_providers = ["brave-search", "serper", "web-search"]
            
            for provider in search_providers:
                if provider in self.available_servers:
                    result = await self.call_mcp_tool(
                        provider,
                        "brave_web_search" if provider == "brave-search" else "search",
                        {"query": query, "count": num_results}
                    )
                    if result.get("success", False):
                        return result
            
            return {"success": False, "error": "No web search providers available"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    async def access_obsidian_vault(self, action: str, **kwargs) -> Dict[str, Any]:
        """Access Obsidian vault using MCP obsidian-vault server"""
        try:
            if "obsidian-vault" not in self.available_servers:
                return {"success": False, "error": "Obsidian vault MCP server not available"}
            
            result = await self.call_mcp_tool("obsidian-vault", action, kwargs)
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    async def use_memory_system(self, action: str, **kwargs) -> Dict[str, Any]:
        """Use memory system for persistent storage"""
        try:
            if "memory" not in self.available_servers:
                return {"success": False, "error": "Memory MCP server not available"}
            
            result = await self.call_mcp_tool("memory", action, kwargs)
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    async def access_filesystem(self, action: str, **kwargs) -> Dict[str, Any]:
        """Access filesystem using MCP filesystem server"""
        try:
            if "filesystem" not in self.available_servers:
                return {"success": False, "error": "Filesystem MCP server not available"}
            
            result = await self.call_mcp_tool("filesystem", action, kwargs)
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    async def use_sequential_thinking(self, problem: str, steps: int = 5) -> Dict[str, Any]:
        """Use sequential thinking for complex problem solving"""
        try:
            if "sequential-thinking" not in self.available_servers:
                return {"success": False, "error": "Sequential thinking MCP server not available"}
            
            result = await self.call_mcp_tool(
                "sequential-thinking",
                "sequentialthinking",
                {"thought": problem, "nextThoughtNeeded": True, "thoughtNumber": 1, "totalThoughts": steps}
            )
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    async def get_mcp_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all MCP servers"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.mcp_integration_url}/mcp/metrics")
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"success": False, "error": f"Failed to get metrics: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def create_mcp_integrated_workflow():
    """Create the MCP integrated LangGraph workflow"""
    
    # Initialize the agent
    agent = MCPIntegratedAgent()
    
    # Define workflow nodes
    def start_mcp_agent(state: MCPAgentState) -> MCPAgentState:
        """Start the MCP integrated agent"""
        logger.info("Starting MCP integrated agent")
        
        state["messages"] = state.get("messages", [])
        state["current_task"] = state.get("current_task", "MCP integration task")
        state["mcp_results"] = {}
        state["vault_data"] = {}
        state["search_results"] = {}
        state["analysis_results"] = {}
        state["error_log"] = []
        state["performance_metrics"] = {}
        
        return state
    
    async def discover_mcp_servers(state: MCPAgentState) -> MCPAgentState:
        """Discover available MCP servers"""
        logger.info("Discovering MCP servers")
        
        try:
            await agent.initialize()
            state["mcp_results"]["discovered_servers"] = agent.available_servers
            logger.info(f"Discovered {len(agent.available_servers)} MCP servers")
        except Exception as e:
            error_msg = f"Failed to discover MCP servers: {str(e)}"
            logger.error(error_msg)
            state["error_log"].append(error_msg)
        
        return state
    
    async def access_obsidian_vault(state: MCPAgentState) -> MCPAgentState:
        """Access Obsidian vault data"""
        logger.info("Accessing Obsidian vault")
        
        try:
            # List vault files
            files_result = await agent.access_obsidian_vault("list_files")
            if files_result.get("success", False):
                state["vault_data"]["files"] = files_result.get("result", {})
                logger.info("Successfully accessed Obsidian vault files")
            else:
                state["error_log"].append(f"Failed to access vault files: {files_result.get('error', 'Unknown error')}")
            
            # Search vault content
            search_result = await agent.access_obsidian_vault("search", query="langgraph")
            if search_result.get("success", False):
                state["vault_data"]["search_results"] = search_result.get("result", {})
                logger.info("Successfully searched Obsidian vault")
            else:
                state["error_log"].append(f"Failed to search vault: {search_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            error_msg = f"Error accessing Obsidian vault: {str(e)}"
            logger.error(error_msg)
            state["error_log"].append(error_msg)
        
        return state
    
    async def perform_web_search(state: MCPAgentState) -> MCPAgentState:
        """Perform web search using MCP tools"""
        logger.info("Performing web search")
        
        try:
            search_result = await agent.search_web("langgraph MCP integration", num_results=3)
            if search_result.get("success", False):
                state["search_results"] = search_result.get("result", {})
                logger.info("Successfully performed web search")
            else:
                state["error_log"].append(f"Web search failed: {search_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            error_msg = f"Error performing web search: {str(e)}"
            logger.error(error_msg)
            state["error_log"].append(error_msg)
        
        return state
    
    async def use_sequential_thinking(state: MCPAgentState) -> MCPAgentState:
        """Use sequential thinking for analysis"""
        logger.info("Using sequential thinking for analysis")
        
        try:
            problem = f"Analyze the integration between LangGraph and MCP servers. " \
                     f"Available servers: {state.get('mcp_results', {}).get('discovered_servers', [])}. " \
                     f"Vault data: {len(state.get('vault_data', {}).get('files', []))} files. " \
                     f"Search results: {len(state.get('search_results', {}))} items."
            
            thinking_result = await agent.use_sequential_thinking(problem, steps=3)
            if thinking_result.get("success", False):
                state["analysis_results"]["sequential_thinking"] = thinking_result.get("result", {})
                logger.info("Successfully used sequential thinking")
            else:
                state["error_log"].append(f"Sequential thinking failed: {thinking_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            error_msg = f"Error using sequential thinking: {str(e)}"
            logger.error(error_msg)
            state["error_log"].append(error_msg)
        
        return state
    
    async def get_performance_metrics(state: MCPAgentState) -> MCPAgentState:
        """Get performance metrics for all MCP calls"""
        logger.info("Getting performance metrics")
        
        try:
            metrics_result = await agent.get_mcp_metrics()
            if metrics_result.get("success", False):
                state["performance_metrics"] = metrics_result.get("result", {})
                logger.info("Successfully retrieved performance metrics")
            else:
                state["error_log"].append(f"Failed to get metrics: {metrics_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            error_msg = f"Error getting performance metrics: {str(e)}"
            logger.error(error_msg)
            state["error_log"].append(error_msg)
        
        return state
    
    def generate_final_response(state: MCPAgentState) -> MCPAgentState:
        """Generate final response based on all MCP interactions"""
        logger.info("Generating final response")
        
        # Compile results
        discovered_servers = state.get("mcp_results", {}).get("discovered_servers", [])
        vault_files = len(state.get("vault_data", {}).get("files", []))
        search_items = len(state.get("search_results", {}))
        errors = len(state.get("error_log", []))
        
        response = f"""
# MCP Integrated Agent Report

## Summary
- **Discovered MCP Servers**: {len(discovered_servers)}
- **Vault Files Accessed**: {vault_files}
- **Web Search Results**: {search_items}
- **Errors Encountered**: {errors}

## Available MCP Servers
{', '.join(discovered_servers) if discovered_servers else 'None discovered'}

## Performance Metrics
{json.dumps(state.get('performance_metrics', {}), indent=2)}

## Errors
{chr(10).join(state.get('error_log', [])) if state.get('error_log') else 'No errors'}

## Timestamp
Generated: {datetime.now().isoformat()}
        """
        
        state["final_response"] = response
        logger.info("Final response generated successfully")
        
        return state
    
    # Create the workflow
    workflow = StateGraph(MCPAgentState)
    
    # Add nodes
    workflow.add_node("start", start_mcp_agent)
    workflow.add_node("discover_servers", discover_mcp_servers)
    workflow.add_node("access_vault", access_obsidian_vault)
    workflow.add_node("web_search", perform_web_search)
    workflow.add_node("sequential_thinking", use_sequential_thinking)
    workflow.add_node("get_metrics", get_performance_metrics)
    workflow.add_node("generate_response", generate_final_response)
    
    # Add edges
    workflow.set_entry_point("start")
    workflow.add_edge("start", "discover_servers")
    workflow.add_edge("discover_servers", "access_vault")
    workflow.add_edge("access_vault", "web_search")
    workflow.add_edge("web_search", "sequential_thinking")
    workflow.add_edge("sequential_thinking", "get_metrics")
    workflow.add_edge("get_metrics", "generate_response")
    workflow.add_edge("generate_response", END)
    
    return workflow.compile()

# Create the workflow instance
mcp_integrated_workflow = create_mcp_integrated_workflow()

# Export for LangGraph
def mcp_integrated_agent(state: MCPAgentState) -> MCPAgentState:
    """Main entry point for the MCP integrated agent"""
    return mcp_integrated_workflow.invoke(state)

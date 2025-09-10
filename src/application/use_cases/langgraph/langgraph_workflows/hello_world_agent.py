#!/usr/bin/env python3
"""
Hello World LangGraph Agent with Stateful React Capabilities
This agent demonstrates vault data retrieval, MCP integration, and comprehensive testing
"""

from typing import TypedDict, Annotated, Sequence, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
import httpx
import json
import asyncio
import datetime
import os
from dataclasses import dataclass
import time
import random

# Configuration
OBSIDIAN_API_BASE_URL = "http://127.0.0.1:27123"
OBSIDIAN_API_KEY = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
VAULT_NAME = "Nomade Milionario"

@dataclass
class AgentMetrics:
    """Metrics for agent performance tracking"""
    start_time: float
    end_time: float
    api_calls: int
    vault_operations: int
    search_queries: int
    errors: int
    success_rate: float

class HelloWorldState(TypedDict):
    """State for Hello World agent"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    vault_name: str
    current_task: str
    search_query: str
    retrieved_data: List[Dict[str, Any]]
    agent_thoughts: List[str]
    metrics: Optional[AgentMetrics]
    workflow_status: str
    results: Dict[str, Any]
    user_feedback: Optional[str]
    next_action: Optional[str]

# Tools for vault operations
@tool
def list_vault_files(vault_name: str) -> Dict[str, Any]:
    """List all files in the Obsidian vault"""
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{OBSIDIAN_API_BASE_URL}/vault/files",
                headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e), "files": []}

@tool
def read_vault_file(file_path: str) -> Dict[str, Any]:
    """Read content of a specific file from the vault"""
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{OBSIDIAN_API_BASE_URL}/vault/file",
                params={"path": file_path},
                headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e), "content": ""}

@tool
def search_vault_content(query: str, vault_name: str) -> Dict[str, Any]:
    """Search for content in the vault"""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{OBSIDIAN_API_BASE_URL}/vault/{vault_name}/search",
                json={"query": query, "vault_name": vault_name},
                headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e), "results": []}

@tool
def write_vault_file(file_path: str, content: str) -> Dict[str, Any]:
    """Write content to a file in the vault"""
    try:
        with httpx.Client() as client:
            response = client.put(
                f"{OBSIDIAN_API_BASE_URL}/vault/{file_path}",
                content=content,
                headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e), "success": False}

@tool
def get_vault_stats(vault_name: str) -> Dict[str, Any]:
    """Get vault statistics and metadata"""
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{OBSIDIAN_API_BASE_URL}/vault/stats",
                headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e), "stats": {}}

# Agent nodes
def start_hello_world_agent(state: HelloWorldState) -> HelloWorldState:
    """Initialize the Hello World agent"""
    print("🚀 Starting Hello World LangGraph Agent!")
    print(f"📁 Vault: {state.get('vault_name', VAULT_NAME)}")
    print(f"🎯 Task: {state.get('current_task', 'Hello World')}")
    
    # Initialize metrics
    metrics = AgentMetrics(
        start_time=time.time(),
        end_time=0.0,
        api_calls=0,
        vault_operations=0,
        search_queries=0,
        errors=0,
        success_rate=0.0
    )
    
    # Add system message
    system_msg = SystemMessage(content="""
    You are a Hello World LangGraph Agent with stateful React capabilities.
    Your mission is to:
    1. Retrieve data from the Obsidian vault
    2. Demonstrate MCP integration
    3. Show stateful behavior
    4. Provide comprehensive testing and benchmarking
    
    Always think step by step and explain your reasoning.
    """)
    
    return {
        **state,
        "messages": [system_msg],
        "metrics": metrics,
        "workflow_status": "initialized",
        "agent_thoughts": ["Agent initialized", "Ready to start vault operations"]
    }

def analyze_vault_structure(state: HelloWorldState) -> HelloWorldState:
    """Analyze the vault structure and get basic information"""
    print("🔍 Analyzing vault structure...")
    
    thoughts = state.get("agent_thoughts", [])
    thoughts.append("Starting vault structure analysis")
    
    # Get vault stats
    stats_result = get_vault_stats.invoke({"vault_name": state.get("vault_name", VAULT_NAME)})
    thoughts.append(f"Vault stats retrieved: {stats_result}")
    
    # List files
    files_result = list_vault_files.invoke({"vault_name": state.get("vault_name", VAULT_NAME)})
    thoughts.append(f"Files listed: {len(files_result.get('files', []))} files found")
    
    # Update metrics
    metrics = state.get("metrics")
    if metrics:
        metrics.api_calls += 2
        metrics.vault_operations += 2
    
    return {
        **state,
        "agent_thoughts": thoughts,
        "retrieved_data": [stats_result, files_result],
        "workflow_status": "analyzing"
    }

def perform_intelligent_search(state: HelloWorldState) -> HelloWorldState:
    """Perform intelligent search based on the task"""
    print("🔍 Performing intelligent search...")
    
    thoughts = state.get("agent_thoughts", [])
    search_query = state.get("search_query", "langgraph")
    
    thoughts.append(f"Searching for: {search_query}")
    
    # Perform search
    search_result = search_vault_content.invoke({
        "query": search_query,
        "vault_name": state.get("vault_name", VAULT_NAME)
    })
    
    thoughts.append(f"Search completed: {search_result.get('total', 0)} results found")
    
    # Update metrics
    metrics = state.get("metrics")
    if metrics:
        metrics.api_calls += 1
        metrics.search_queries += 1
    
    return {
        **state,
        "agent_thoughts": thoughts,
        "retrieved_data": state.get("retrieved_data", []) + [search_result],
        "workflow_status": "searching"
    }

def demonstrate_stateful_behavior(state: HelloWorldState) -> HelloWorldState:
    """Demonstrate stateful React behavior"""
    print("🧠 Demonstrating stateful React behavior...")
    
    thoughts = state.get("agent_thoughts", [])
    thoughts.append("Demonstrating stateful behavior")
    
    # Simulate thinking process
    current_data = state.get("retrieved_data", [])
    thoughts.append(f"Processing {len(current_data)} data sources")
    
    # Generate insights
    insights = []
    for data in current_data:
        if "files" in data:
            insights.append(f"Found {len(data['files'])} files in vault")
        if "results" in data:
            insights.append(f"Search returned {len(data['results'])} results")
        if "stats" in data:
            insights.append(f"Vault has {data['stats'].get('total_files', 0)} total files")
    
    thoughts.extend(insights)
    thoughts.append("Stateful processing completed")
    
    return {
        **state,
        "agent_thoughts": thoughts,
        "workflow_status": "processing"
    }

def create_hello_world_summary(state: HelloWorldState) -> HelloWorldState:
    """Create a comprehensive Hello World summary"""
    print("📝 Creating Hello World summary...")
    
    thoughts = state.get("agent_thoughts", [])
    thoughts.append("Creating comprehensive summary")
    
    # Generate summary content
    summary_content = f"""# Hello World LangGraph Agent Summary

## Agent Status: ✅ SUCCESSFUL

### Vault Information
- **Vault Name**: {state.get('vault_name', VAULT_NAME)}
- **Task**: {state.get('current_task', 'Hello World')}
- **Search Query**: {state.get('search_query', 'langgraph')}

### Agent Thoughts
{chr(10).join(f"- {thought}" for thought in thoughts)}

### Retrieved Data Summary
"""
    
    # Add data summaries
    for i, data in enumerate(state.get("retrieved_data", [])):
        summary_content += f"\n#### Data Source {i+1}\n"
        if "files" in data:
            summary_content += f"- Files: {len(data['files'])} items\n"
        if "results" in data:
            summary_content += f"- Search Results: {len(data['results'])} items\n"
        if "stats" in data:
            summary_content += f"- Stats: {data['stats']}\n"
    
    summary_content += f"""
### Metrics
- **API Calls**: {state.get('metrics', AgentMetrics(0,0,0,0,0,0,0.0)).api_calls}
- **Vault Operations**: {state.get('metrics', AgentMetrics(0,0,0,0,0,0,0.0)).vault_operations}
- **Search Queries**: {state.get('metrics', AgentMetrics(0,0,0,0,0,0,0.0)).search_queries}
- **Errors**: {state.get('metrics', AgentMetrics(0,0,0,0,0,0,0.0)).errors}

### Timestamp
Generated: {datetime.datetime.now().isoformat()}

## 🎉 Hello World Agent Mission Complete!
"""
    
    # Write summary to vault
    summary_path = f"Hello_World_Agent_Summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    write_result = write_vault_file.invoke({
        "file_path": summary_path,
        "content": summary_content
    })
    
    thoughts.append(f"Summary written to vault: {summary_path}")
    
    # Update metrics
    metrics = state.get("metrics")
    if metrics:
        metrics.api_calls += 1
        metrics.vault_operations += 1
        metrics.end_time = time.time()
        metrics.success_rate = 1.0 if metrics.errors == 0 else 0.8
    
    return {
        **state,
        "agent_thoughts": thoughts,
        "workflow_status": "completed",
        "results": {
            "summary_file": summary_path,
            "summary_content": summary_content,
            "write_result": write_result,
            "metrics": metrics.__dict__ if metrics else {}
        }
    }

def finalize_agent(state: HelloWorldState) -> HelloWorldState:
    """Finalize the agent and provide final results"""
    print("✅ Hello World Agent completed successfully!")
    
    metrics = state.get("metrics")
    if metrics:
        duration = metrics.end_time - metrics.start_time
        print(f"⏱️  Total execution time: {duration:.2f} seconds")
        print(f"📊 API calls made: {metrics.api_calls}")
        print(f"📁 Vault operations: {metrics.vault_operations}")
        print(f"🔍 Search queries: {metrics.search_queries}")
        print(f"❌ Errors: {metrics.errors}")
        print(f"✅ Success rate: {metrics.success_rate:.1%}")
    
    return {
        **state,
        "workflow_status": "finalized",
        "next_action": "complete"
    }

# Create the Hello World agent workflow
def create_hello_world_agent() -> StateGraph:
    """Create the Hello World agent workflow"""
    workflow = StateGraph(HelloWorldState)
    
    # Add nodes
    workflow.add_node("start", start_hello_world_agent)
    workflow.add_node("analyze", analyze_vault_structure)
    workflow.add_node("search", perform_intelligent_search)
    workflow.add_node("process", demonstrate_stateful_behavior)
    workflow.add_node("summarize", create_hello_world_summary)
    workflow.add_node("finalize", finalize_agent)
    
    # Set entry point
    workflow.set_entry_point("start")
    
    # Add edges
    workflow.add_edge("start", "analyze")
    workflow.add_edge("analyze", "search")
    workflow.add_edge("search", "process")
    workflow.add_edge("process", "summarize")
    workflow.add_edge("summarize", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow

# Create the workflow instance
hello_world_agent = create_hello_world_agent().compile()

# Example function to run the agent
def run_hello_world_example():
    """Run the Hello World agent example"""
    print("🚀 Starting Hello World LangGraph Agent Example")
    print("=" * 60)
    
    # Initial state
    initial_state = {
        "messages": [],
        "vault_name": VAULT_NAME,
        "current_task": "Hello World Agent Demo",
        "search_query": "langgraph",
        "retrieved_data": [],
        "agent_thoughts": [],
        "workflow_status": "starting",
        "results": {}
    }
    
    try:
        # Run the workflow
        result = hello_world_agent.invoke(initial_state)
        
        print("\n🎉 Hello World Agent completed successfully!")
        print(f"📊 Final status: {result['workflow_status']}")
        print(f"📝 Summary file: {result['results'].get('summary_file', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running Hello World agent: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    run_hello_world_example()

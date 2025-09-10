"""
LangGraph Workflow for Obsidian Integration
Demonstrates complete symbiosis between LangGraph and Obsidian Local REST API
"""

from typing import TypedDict, Annotated, Sequence, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
import httpx
import json
import asyncio
from datetime import datetime
import os

# Configuration
OBSIDIAN_API_BASE_URL = os.getenv("OBSIDIAN_API_URL", "http://127.0.0.1:27123")
OBSIDIAN_API_KEY = os.getenv("OBSIDIAN_API_KEY", "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70")
OBSIDIAN_HEADERS = {
    "Authorization": f"Bearer {OBSIDIAN_API_KEY}",
    "Content-Type": "application/json"
}

# State definition
class ObsidianState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    vault_name: str
    current_file: str
    search_query: str
    workflow_status: str
    results: dict

# Tools for Obsidian integration
@tool
def list_obsidian_files(vault_name: str, path: str = "", recursive: bool = True, limit: int = 100) -> dict:
    """List files in an Obsidian vault"""
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{OBSIDIAN_API_BASE_URL}/vault/{path}",
                headers=OBSIDIAN_HEADERS,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            files = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        files.append({
                            "name": item.get("name", ""),
                            "path": item.get("path", ""),
                            "size": item.get("size", 0),
                            "modified": item.get("modified", ""),
                            "is_folder": item.get("type") == "folder"
                        })
            
            return {
                "success": True,
                "files": files[:limit],
                "count": len(files),
                "vault_name": vault_name,
                "path": path
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
def read_obsidian_file(vault_name: str, file_path: str) -> dict:
    """Read a file from an Obsidian vault"""
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{OBSIDIAN_API_BASE_URL}/vault/{file_path}",
                headers=OBSIDIAN_HEADERS,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "content": data.get("content", ""),
                "file_path": file_path,
                "vault_name": vault_name,
                "metadata": data.get("metadata", {})
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
def write_obsidian_file(vault_name: str, file_path: str, content: str) -> dict:
    """Write content to a file in an Obsidian vault"""
    try:
        with httpx.Client() as client:
            response = client.put(
                f"{OBSIDIAN_API_BASE_URL}/vault/{file_path}",
                headers=OBSIDIAN_HEADERS,
                json={"content": content},
                timeout=10
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "file_path": file_path,
                "vault_name": vault_name,
                "content_length": len(content),
                "message": "File written successfully"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
def search_obsidian_notes(vault_name: str, query: str, limit: int = 10) -> dict:
    """Search for notes in an Obsidian vault"""
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{OBSIDIAN_API_BASE_URL}/vault/{vault_name}/search",
                headers=OBSIDIAN_HEADERS,
                json={"query": query, "limit": limit},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "results": data.get("results", []),
                "query": query,
                "vault_name": vault_name,
                "count": len(data.get("results", []))
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Workflow nodes
def start_workflow(state: ObsidianState) -> ObsidianState:
    """Initialize the workflow"""
    print(f"🚀 Starting Obsidian integration workflow for vault: {state['vault_name']}")
    return {
        **state,
        "workflow_status": "initialized",
        "results": {"start_time": datetime.now().isoformat()}
    }

def list_vault_files(state: ObsidianState) -> ObsidianState:
    """List files in the vault"""
    print(f"📁 Listing files in vault: {state['vault_name']}")
    
    result = list_obsidian_files(
        vault_name=state["vault_name"],
        path=state.get("current_file", ""),
        recursive=True,
        limit=50
    )
    
    return {
        **state,
        "workflow_status": "files_listed",
        "results": {
            **state["results"],
            "files": result.get("files", []),
            "file_count": result.get("count", 0)
        }
    }

def search_notes(state: ObsidianState) -> ObsidianState:
    """Search for notes based on query"""
    if not state.get("search_query"):
        return state
    
    print(f"🔍 Searching for: {state['search_query']}")
    
    result = search_obsidian_notes(
        vault_name=state["vault_name"],
        query=state["search_query"],
        limit=20
    )
    
    return {
        **state,
        "workflow_status": "search_completed",
        "results": {
            **state["results"],
            "search_results": result.get("results", []),
            "search_count": result.get("count", 0)
        }
    }

def read_current_file(state: ObsidianState) -> ObsidianState:
    """Read the current file if specified"""
    if not state.get("current_file"):
        return state
    
    print(f"📖 Reading file: {state['current_file']}")
    
    result = read_obsidian_file(
        vault_name=state["vault_name"],
        file_path=state["current_file"]
    )
    
    return {
        **state,
        "workflow_status": "file_read",
        "results": {
            **state["results"],
            "current_file_content": result.get("content", ""),
            "current_file_metadata": result.get("metadata", {})
        }
    }

def create_summary_note(state: ObsidianState) -> ObsidianState:
    """Create a summary note of the workflow results"""
    print("📝 Creating summary note...")
    
    summary_content = f"""# Obsidian Integration Workflow Summary

**Generated:** {datetime.now().isoformat()}
**Vault:** {state['vault_name']}
**Status:** {state['workflow_status']}

## Files Found
- Total files: {state['results'].get('file_count', 0)}
- Files: {json.dumps(state['results'].get('files', [])[:5], indent=2)}

## Search Results
- Query: {state.get('search_query', 'N/A')}
- Results found: {state['results'].get('search_count', 0)}
- Results: {json.dumps(state['results'].get('search_results', [])[:3], indent=2)}

## Current File
- File: {state.get('current_file', 'N/A')}
- Content length: {len(state['results'].get('current_file_content', ''))}

---
*This note was automatically generated by the LangGraph-Obsidian integration workflow.*
"""
    
    summary_file_path = f"LangGraph_Workflow_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    result = write_obsidian_file(
        vault_name=state["vault_name"],
        file_path=summary_file_path,
        content=summary_content
    )
    
    return {
        **state,
        "workflow_status": "summary_created",
        "results": {
            **state["results"],
            "summary_file": summary_file_path,
            "summary_result": result
        }
    }

def complete_workflow(state: ObsidianState) -> ObsidianState:
    """Complete the workflow"""
    print("✅ Workflow completed successfully!")
    return {
        **state,
        "workflow_status": "completed",
        "results": {
            **state["results"],
            "end_time": datetime.now().isoformat(),
            "status": "success"
        }
    }

# Create the workflow graph
def create_obsidian_workflow():
    """Create the Obsidian integration workflow"""
    
    # Create the state graph
    workflow = StateGraph(ObsidianState)
    
    # Add nodes
    workflow.add_node("start", start_workflow)
    workflow.add_node("list_files", list_vault_files)
    workflow.add_node("search_notes", search_notes)
    workflow.add_node("read_file", read_current_file)
    workflow.add_node("create_summary", create_summary_note)
    workflow.add_node("complete", complete_workflow)
    
    # Add edges
    workflow.add_edge("start", "list_files")
    workflow.add_edge("list_files", "search_notes")
    workflow.add_edge("search_notes", "read_file")
    workflow.add_edge("read_file", "create_summary")
    workflow.add_edge("create_summary", "complete")
    workflow.add_edge("complete", END)
    
    # Compile the workflow
    return workflow.compile()

# Example usage
def run_obsidian_workflow_example():
    """Run an example of the Obsidian workflow"""
    
    # Create the workflow
    obsidian_workflow = create_obsidian_workflow()
    
    # Define the initial state
    initial_state = {
        "messages": [HumanMessage(content="Start Obsidian integration workflow")],
        "vault_name": "Nomade Milionario",
        "current_file": "",
        "search_query": "langgraph integration",
        "workflow_status": "pending",
        "results": {}
    }
    
    # Run the workflow
    print("🚀 Running Obsidian Integration Workflow...")
    print("=" * 50)
    
    try:
        result = obsidian_workflow.invoke(initial_state)
        
        print("\n📊 Workflow Results:")
        print("=" * 30)
        print(f"Status: {result['workflow_status']}")
        print(f"Files found: {result['results'].get('file_count', 0)}")
        print(f"Search results: {result['results'].get('search_count', 0)}")
        print(f"Summary file: {result['results'].get('summary_file', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        return None

if __name__ == "__main__":
    # Run the example
    run_obsidian_workflow_example()

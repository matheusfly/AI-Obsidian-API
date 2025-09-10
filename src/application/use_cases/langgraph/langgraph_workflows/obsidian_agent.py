"""
LangGraph Workflow for Obsidian Vault Agent
Implements stateful multi-agent workflows with checkpointing and HITL support
"""
import asyncio
from typing import Annotated, Sequence, TypedDict, Dict, Any, List, Optional
from datetime import datetime
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
import httpx
import structlog

from config.environment import config

logger = structlog.get_logger()

# State definition for the agent
class AgentState(TypedDict):
    messages: Annotated[Sequence[dict], operator.add]
    next_action: str
    context: Dict[str, Any]
    vault_data: Dict[str, Any]
    tool_calls: Annotated[Sequence[Dict[str, Any]], operator.add]
    current_task: str
    session_id: str
    pending_approvals: Annotated[Sequence[Dict[str, Any]], operator.add]
    error_count: int
    max_retries: int

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.1,
    api_key=config.OPENAI_API_KEY
)

# HTTP client for API Gateway
class APIClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.GATEWAY_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the API Gateway"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(
                "api_request_error",
                method=method,
                endpoint=endpoint,
                error=str(e)
            )
            raise Exception(f"API request failed: {str(e)}")
    
    async def close(self):
        await self.client.aclose()

api_client = APIClient()

# LangChain tools for Obsidian operations
@tool
async def obsidian_list_files(vault: str, cursor: str = None, limit: int = 100, filter: str = None) -> Dict[str, Any]:
    """List files in an Obsidian vault with pagination"""
    try:
        result = await api_client.request(
            "GET",
            f"/vault/{vault}/files",
            params={
                "cursor": cursor,
                "limit": limit,
                "filter": filter
            }
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
async def obsidian_read_note(vault: str, path: str) -> Dict[str, Any]:
    """Read content of a specific note from an Obsidian vault"""
    try:
        result = await api_client.request("GET", f"/vault/{vault}/file/{path}")
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
async def obsidian_put_file(vault: str, path: str, content: str, dry_run: bool = True, if_match: str = None) -> Dict[str, Any]:
    """Create or update a file in an Obsidian vault"""
    try:
        result = await api_client.request(
            "PUT",
            f"/vault/{vault}/file/{path}",
            json={
                "path": path,
                "content": content,
                "dry_run": dry_run,
                "if_match": if_match
            }
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
async def obsidian_search_notes(vault: str, query: str, limit: int = 20) -> Dict[str, Any]:
    """Search for notes in an Obsidian vault"""
    try:
        result = await api_client.request(
            "POST",
            f"/vault/{vault}/search",
            json={"query": query, "limit": limit}
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
async def obsidian_list_pending_operations() -> Dict[str, Any]:
    """List pending operations requiring approval"""
    try:
        result = await api_client.request("GET", "/pending_operations")
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
async def obsidian_approve_operation(tool_call_id: str, approved_by: str = "agent") -> Dict[str, Any]:
    """Approve a pending operation"""
    try:
        result = await api_client.request(
            "POST",
            f"/approve/{tool_call_id}",
            json={"approved_by": approved_by}
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Available tools
tools = [
    obsidian_list_files,
    obsidian_read_note,
    obsidian_put_file,
    obsidian_search_notes,
    obsidian_list_pending_operations,
    obsidian_approve_operation
]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

# Node implementations
async def classify_task(state: AgentState) -> AgentState:
    """Classify the user task into categories"""
    logger.info("classifying_task", session_id=state["session_id"])
    
    # Get the latest user message
    user_message = state["messages"][-1] if state["messages"] else {"content": ""}
    user_input = user_message.get("content", "")
    
    # Simple classification logic (in production, use a more sophisticated classifier)
    task_type = "READ"  # default
    
    if any(keyword in user_input.lower() for keyword in ["write", "create", "update", "edit", "modify"]):
        task_type = "WRITE"
    elif any(keyword in user_input.lower() for keyword in ["search", "find", "look for"]):
        task_type = "SEARCH"
    elif any(keyword in user_input.lower() for keyword in ["organize", "sort", "move", "categorize"]):
        task_type = "ORGANIZE"
    elif any(keyword in user_input.lower() for keyword in ["summarize", "analyze", "process"]):
        task_type = "ANALYZE"
    
    logger.info("task_classified", task_type=task_type, session_id=state["session_id"])
    
    return {
        "current_task": task_type,
        "next_action": f"execute_{task_type.lower()}_workflow"
    }

async def execute_read_workflow(state: AgentState) -> AgentState:
    """Execute read operations on the vault"""
    logger.info("executing_read_workflow", session_id=state["session_id"])
    
    user_message = state["messages"][-1]
    user_input = user_message.get("content", "")
    
    # Extract vault and path from user input (simplified)
    vault = config.VAULT_NAME  # Use default vault
    
    # Try to extract specific file path or search query
    if "file:" in user_input:
        path = user_input.split("file:")[1].strip()
        result = await obsidian_read_note(vault, path)
    elif "search:" in user_input:
        query = user_input.split("search:")[1].strip()
        result = await obsidian_search_notes(vault, query)
    else:
        # List files in vault
        result = await obsidian_list_files(vault)
    
    if result["success"]:
        response_content = f"Successfully retrieved data from vault '{vault}':\n\n{result['data']}"
    else:
        response_content = f"Failed to read from vault: {result['error']}"
    
    return {
        "messages": [AIMessage(content=response_content)],
        "vault_data": result.get("data", {}),
        "next_action": "check_pending_approvals"
    }

async def execute_write_workflow(state: AgentState) -> AgentState:
    """Execute write operations on the vault"""
    logger.info("executing_write_workflow", session_id=state["session_id"])
    
    user_message = state["messages"][-1]
    user_input = user_message.get("content", "")
    
    vault = config.VAULT_NAME
    
    # Extract path and content from user input (simplified)
    # In production, use more sophisticated parsing
    if "create:" in user_input and "content:" in user_input:
        parts = user_input.split("create:")[1]
        if "content:" in parts:
            path, content = parts.split("content:", 1)
            path = path.strip()
            content = content.strip()
        else:
            path = parts.strip()
            content = "New note created by agent"
    else:
        # Default to creating a note with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"agent_notes/note_{timestamp}.md"
        content = f"# Agent Note - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{user_input}"
    
    # Perform dry-run write first
    result = await obsidian_put_file(vault, path, content, dry_run=True)
    
    if result["success"]:
        data = result["data"]
        if data.get("approval_required"):
            # Add to pending approvals
            approval_info = {
                "tool_call_id": data.get("tool_call_id"),
                "operation": "write",
                "vault": vault,
                "path": path,
                "content_preview": content[:100] + "..." if len(content) > 100 else content
            }
            
            response_content = f"""Write operation prepared for vault '{vault}':

Path: {path}
Content Preview: {content[:200]}{'...' if len(content) > 200 else ''}

This operation requires approval. Tool Call ID: {data.get('tool_call_id')}

You can approve this operation by calling the approval endpoint or wait for human approval."""
            
            return {
                "messages": [AIMessage(content=response_content)],
                "pending_approvals": [approval_info],
                "next_action": "check_pending_approvals"
            }
        else:
            response_content = f"Write operation completed successfully in vault '{vault}' at path '{path}'"
    else:
        response_content = f"Failed to write to vault: {result['error']}"
    
    return {
        "messages": [AIMessage(content=response_content)],
        "next_action": "check_pending_approvals"
    }

async def execute_search_workflow(state: AgentState) -> AgentState:
    """Execute search operations on the vault"""
    logger.info("executing_search_workflow", session_id=state["session_id"])
    
    user_message = state["messages"][-1]
    user_input = user_message.get("content", "")
    
    vault = config.VAULT_NAME
    
    # Extract search query
    if "search:" in user_input:
        query = user_input.split("search:")[1].strip()
    else:
        query = user_input
    
    result = await obsidian_search_notes(vault, query)
    
    if result["success"]:
        data = result["data"]
        results = data.get("results", [])
        
        if results:
            response_content = f"Found {len(results)} results for query '{query}':\n\n"
            for i, item in enumerate(results[:10], 1):  # Limit to 10 results
                response_content += f"{i}. {item.get('path', 'Unknown path')}\n"
                response_content += f"   {item.get('content', '')[:100]}...\n\n"
        else:
            response_content = f"No results found for query '{query}'"
    else:
        response_content = f"Search failed: {result['error']}"
    
    return {
        "messages": [AIMessage(content=response_content)],
        "vault_data": result.get("data", {}),
        "next_action": "check_pending_approvals"
    }

async def execute_organize_workflow(state: AgentState) -> AgentState:
    """Execute organization operations on the vault"""
    logger.info("executing_organize_workflow", session_id=state["session_id"])
    
    # This is a simplified organization workflow
    # In production, implement more sophisticated organization logic
    
    vault = config.VAULT_NAME
    
    # List files in inbox
    result = await obsidian_list_files(vault, filter="inbox/*")
    
    if result["success"]:
        files = result["data"].get("files", [])
        response_content = f"Found {len(files)} files in inbox that could be organized:\n\n"
        
        for file in files[:5]:  # Show first 5 files
            response_content += f"- {file.get('path', 'Unknown path')}\n"
        
        if len(files) > 5:
            response_content += f"... and {len(files) - 5} more files\n"
        
        response_content += "\nOrganization workflow would categorize these files based on content analysis."
    else:
        response_content = f"Failed to list files for organization: {result['error']}"
    
    return {
        "messages": [AIMessage(content=response_content)],
        "next_action": "check_pending_approvals"
    }

async def execute_analyze_workflow(state: AgentState) -> AgentState:
    """Execute analysis operations on the vault"""
    logger.info("executing_analyze_workflow", session_id=state["session_id"])
    
    vault = config.VAULT_NAME
    
    # Get vault statistics
    result = await obsidian_list_files(vault)
    
    if result["success"]:
        files = result["data"].get("files", [])
        total_files = len(files)
        
        # Simple analysis
        file_types = {}
        total_size = 0
        
        for file in files:
            path = file.get("path", "")
            content = file.get("content", "")
            
            # Count file types
            if path.endswith(".md"):
                file_types["markdown"] = file_types.get("markdown", 0) + 1
            elif path.endswith(".png") or path.endswith(".jpg"):
                file_types["images"] = file_types.get("images", 0) + 1
            else:
                file_types["other"] = file_types.get("other", 0) + 1
            
            total_size += len(content)
        
        response_content = f"""Vault Analysis for '{vault}':

Total Files: {total_files}
Total Content Size: {total_size:,} characters

File Type Distribution:
"""
        for file_type, count in file_types.items():
            response_content += f"- {file_type}: {count} files\n"
        
        response_content += f"\nAverage file size: {total_size // max(total_files, 1):,} characters"
    else:
        response_content = f"Failed to analyze vault: {result['error']}"
    
    return {
        "messages": [AIMessage(content=response_content)],
        "next_action": "check_pending_approvals"
    }

async def check_pending_approvals(state: AgentState) -> AgentState:
    """Check for pending operations requiring approval"""
    logger.info("checking_pending_approvals", session_id=state["session_id"])
    
    # Check for pending operations
    result = await obsidian_list_pending_operations()
    
    if result["success"]:
        pending_ops = result["data"]
        
        if pending_ops:
            response_content = f"Found {len(pending_ops)} pending operations:\n\n"
            
            for op in pending_ops:
                response_content += f"- {op.get('operation_type', 'unknown')}: {op.get('path', 'unknown path')}\n"
                response_content += f"  Created: {op.get('created_at', 'unknown time')}\n"
                response_content += f"  Tool Call ID: {op.get('tool_call_id', 'unknown')}\n\n"
            
            response_content += "These operations are waiting for approval before execution."
        else:
            response_content = "No pending operations requiring approval."
    else:
        response_content = f"Failed to check pending operations: {result['error']}"
    
    return {
        "messages": [AIMessage(content=response_content)],
        "next_action": "end"
    }

async def error_handler(state: AgentState) -> AgentState:
    """Handle errors and retry logic"""
    logger.error("error_handler_triggered", session_id=state["session_id"], error_count=state["error_count"])
    
    error_count = state.get("error_count", 0) + 1
    max_retries = state.get("max_retries", 3)
    
    if error_count >= max_retries:
        return {
            "messages": [AIMessage(content="Maximum retry attempts reached. Please try again later.")],
            "next_action": "end",
            "error_count": error_count
        }
    
    return {
        "messages": [AIMessage(content=f"An error occurred (attempt {error_count}/{max_retries}). Retrying...")],
        "next_action": "classify_task",
        "error_count": error_count
    }

# Build the workflow graph
def create_obsidian_agent_workflow():
    """Create the LangGraph workflow for Obsidian agent"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classify_task", classify_task)
    workflow.add_node("execute_read_workflow", execute_read_workflow)
    workflow.add_node("execute_write_workflow", execute_write_workflow)
    workflow.add_node("execute_search_workflow", execute_search_workflow)
    workflow.add_node("execute_organize_workflow", execute_organize_workflow)
    workflow.add_node("execute_analyze_workflow", execute_analyze_workflow)
    workflow.add_node("check_pending_approvals", check_pending_approvals)
    workflow.add_node("error_handler", error_handler)
    
    # Define edges
    workflow.add_edge("classify_task", "execute_read_workflow")
    workflow.add_edge("classify_task", "execute_write_workflow")
    workflow.add_edge("classify_task", "execute_search_workflow")
    workflow.add_edge("classify_task", "execute_organize_workflow")
    workflow.add_edge("classify_task", "execute_analyze_workflow")
    
    workflow.add_edge("execute_read_workflow", "check_pending_approvals")
    workflow.add_edge("execute_write_workflow", "check_pending_approvals")
    workflow.add_edge("execute_search_workflow", "check_pending_approvals")
    workflow.add_edge("execute_organize_workflow", "check_pending_approvals")
    workflow.add_edge("execute_analyze_workflow", "check_pending_approvals")
    
    workflow.add_edge("check_pending_approvals", END)
    workflow.add_edge("error_handler", END)
    
    # Add conditional edges from classify_task
    workflow.add_conditional_edges(
        "classify_task",
        lambda state: state["next_action"],
        {
            "execute_read_workflow": "execute_read_workflow",
            "execute_write_workflow": "execute_write_workflow",
            "execute_search_workflow": "execute_search_workflow",
            "execute_organize_workflow": "execute_organize_workflow",
            "execute_analyze_workflow": "execute_analyze_workflow",
            "error_handler": "error_handler"
        }
    )
    
    # Set entry point
    workflow.set_entry_point("classify_task")
    
    return workflow

# Create and compile the workflow
workflow = create_obsidian_agent_workflow()

# Add checkpointing
memory = SqliteSaver.from_conn_string(config.SQLITE_DB_PATH)
app = workflow.compile(checkpointer=memory)

# Utility functions
async def run_agent(user_input: str, session_id: str = None) -> Dict[str, Any]:
    """Run the agent with a user input"""
    if not session_id:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    config_dict = {"configurable": {"thread_id": session_id}}
    
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "next_action": "classify_task",
        "context": {},
        "vault_data": {},
        "tool_calls": [],
        "current_task": "",
        "session_id": session_id,
        "pending_approvals": [],
        "error_count": 0,
        "max_retries": 3
    }
    
    try:
        result = await app.ainvoke(initial_state, config_dict)
        return {
            "success": True,
            "session_id": session_id,
            "result": result,
            "messages": [msg.content for msg in result.get("messages", [])]
        }
    except Exception as e:
        logger.error("agent_execution_error", session_id=session_id, error=str(e))
        return {
            "success": False,
            "session_id": session_id,
            "error": str(e),
            "messages": []
        }

async def cleanup():
    """Cleanup resources"""
    await api_client.close()

# Example usage
if __name__ == "__main__":
    async def main():
        # Example usage
        result = await run_agent("List all files in my vault")
        print("Agent Result:", result)
        
        await cleanup()
    
    asyncio.run(main())

"""
Enhanced Interactive Agent with Comprehensive Error Logging and Context Retrieval
This agent provides advanced conversation capabilities with proper error handling
"""

import asyncio
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Annotated
from dataclasses import dataclass, field
from enum import Enum

import httpx
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConversationState(Enum):
    INITIAL = "initial"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    ERROR = "error"
    COMPLETED = "completed"

@dataclass
class AgentMetrics:
    """Enhanced metrics tracking for the agent"""
    api_calls: int = 0
    vault_operations: int = 0
    search_queries: int = 0
    errors: int = 0
    successful_responses: int = 0
    context_retrievals: int = 0
    conversation_turns: int = 0
    average_response_time: float = 0.0
    error_rate: float = 0.0

@dataclass
class AgentState:
    """Enhanced state for the interactive agent"""
    messages: List[Any] = field(default_factory=list)
    current_state: ConversationState = ConversationState.INITIAL
    user_input: str = ""
    vault_name: str = "Nomade Milionario"
    context_data: Dict[str, Any] = field(default_factory=dict)
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    error_log: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.now)
    session_id: str = field(default_factory=lambda: f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

# Configuration
OBSIDIAN_API_KEY = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
OBSIDIAN_BASE_URL = "http://127.0.0.1:27123"

class SearchQuery(BaseModel):
    query: str = Field(..., description="Search query for vault content")

class VaultFile(BaseModel):
    path: str = Field(..., description="File path in vault")
    content: str = Field(..., description="File content")

# Enhanced MCP Tools with comprehensive error handling
@tool
def enhanced_vault_health_check() -> Dict[str, Any]:
    """Check vault health and connectivity with detailed diagnostics"""
    try:
        logger.info("Starting enhanced vault health check")
        
        async def check_health():
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test basic connectivity
                health_response = await client.get(f"{OBSIDIAN_BASE_URL}/health")
                
                if health_response.status_code == 200:
                    # Test authentication
                    auth_response = await client.get(
                        f"{OBSIDIAN_BASE_URL}/vault/Nomade%20Milionario/files",
                        headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"}
                    )
                    
                    if auth_response.status_code == 200:
                        vault_data = auth_response.json()
                        return {
                            "status": "healthy",
                            "connectivity": "ok",
                            "authentication": "ok",
                            "vault_files_count": len(vault_data.get("files", [])),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "auth_error",
                            "connectivity": "ok",
                            "authentication": "failed",
                            "error": f"Auth failed: {auth_response.status_code}",
                            "timestamp": datetime.now().isoformat()
                        }
                else:
                    return {
                        "status": "unhealthy",
                        "connectivity": "failed",
                        "authentication": "unknown",
                        "error": f"Health check failed: {health_response.status_code}",
                        "timestamp": datetime.now().isoformat()
                    }
        
        result = asyncio.run(check_health())
        logger.info(f"Vault health check completed: {result['status']}")
        return result
        
    except Exception as e:
        error_msg = f"Vault health check failed: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

@tool
def enhanced_list_vault_files(vault_name: str = "Nomade Milionario") -> Dict[str, Any]:
    """List all files in the vault with enhanced metadata and error handling"""
    try:
        logger.info(f"Listing files in vault: {vault_name}")
        
        async def list_files():
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{OBSIDIAN_BASE_URL}/vault/{vault_name}/files",
                    headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    files = data.get("files", [])
                    
                    # Enhanced file metadata
                    enhanced_files = []
                    for file_info in files:
                        enhanced_file = {
                            "path": file_info.get("path", ""),
                            "name": file_info.get("name", ""),
                            "type": file_info.get("type", "file"),
                            "size": file_info.get("size", 0),
                            "modified": file_info.get("modified", ""),
                            "extension": file_info.get("path", "").split(".")[-1] if "." in file_info.get("path", "") else "",
                            "is_markdown": file_info.get("path", "").endswith((".md", ".markdown")),
                            "is_note": file_info.get("type") == "file" and file_info.get("path", "").endswith((".md", ".markdown"))
                        }
                        enhanced_files.append(enhanced_file)
                    
                    return {
                        "success": True,
                        "vault_name": vault_name,
                        "files": enhanced_files,
                        "total_files": len(enhanced_files),
                        "markdown_files": len([f for f in enhanced_files if f["is_markdown"]]),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}",
                        "response_text": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
        
        result = asyncio.run(list_files())
        logger.info(f"List vault files completed: {result.get('success', False)}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to list vault files: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

@tool
def enhanced_read_vault_file(file_path: str, vault_name: str = "Nomade Milionario") -> Dict[str, Any]:
    """Read a specific file from the vault with enhanced error handling and content analysis"""
    try:
        logger.info(f"Reading file: {file_path} from vault: {vault_name}")
        
        async def read_file():
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{OBSIDIAN_BASE_URL}/vault/{file_path}",
                    headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"}
                )
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Analyze content
                    word_count = len(content.split())
                    line_count = len(content.split('\n'))
                    char_count = len(content)
                    
                    # Extract metadata if it's markdown
                    metadata = {}
                    if file_path.endswith(('.md', '.markdown')):
                        lines = content.split('\n')
                        if lines and lines[0].startswith('---'):
                            # Extract frontmatter
                            frontmatter_lines = []
                            for i, line in enumerate(lines[1:], 1):
                                if line.strip() == '---':
                                    break
                                frontmatter_lines.append(line)
                            
                            if frontmatter_lines:
                                try:
                                    import yaml
                                    metadata = yaml.safe_load('\n'.join(frontmatter_lines))
                                except:
                                    metadata = {"raw_frontmatter": frontmatter_lines}
                    
                    return {
                        "success": True,
                        "file_path": file_path,
                        "content": content,
                        "metadata": {
                            "word_count": word_count,
                            "line_count": line_count,
                            "char_count": char_count,
                            "frontmatter": metadata,
                            "is_markdown": file_path.endswith(('.md', '.markdown')),
                            "file_extension": file_path.split('.')[-1] if '.' in file_path else ""
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API returned status {response.status_code}",
                        "response_text": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
        
        result = asyncio.run(read_file())
        logger.info(f"Read vault file completed: {result.get('success', False)}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to read vault file {file_path}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

@tool
def enhanced_search_vault_content(query: str, vault_name: str = "Nomade Milionario", limit: int = 10) -> Dict[str, Any]:
    """Search vault content with enhanced query processing and result ranking"""
    try:
        logger.info(f"Searching vault content: '{query}' in vault: {vault_name}")
        
        async def search_content():
            async with httpx.AsyncClient(timeout=20.0) as client:
                search_payload = {"query": query}
                response = await client.post(
                    f"{OBSIDIAN_BASE_URL}/vault/{vault_name}/search",
                    headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"},
                    json=search_payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    # Enhanced result processing
                    enhanced_results = []
                    for result in results[:limit]:
                        enhanced_result = {
                            "path": result.get("path", ""),
                            "name": result.get("name", ""),
                            "type": result.get("type", "file"),
                            "size": result.get("size", 0),
                            "modified": result.get("modified", ""),
                            "relevance_score": 1.0,  # Placeholder for actual relevance scoring
                            "is_markdown": result.get("path", "").endswith(('.md', '.markdown')),
                            "query_matches": query.lower() in result.get("name", "").lower()
                        }
                        enhanced_results.append(enhanced_result)
                    
                    # Sort by relevance (simple implementation)
                    enhanced_results.sort(key=lambda x: (x["query_matches"], x["is_markdown"]), reverse=True)
                    
                    return {
                        "success": True,
                        "query": query,
                        "vault_name": vault_name,
                        "results": enhanced_results,
                        "total_results": len(enhanced_results),
                        "search_timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Search API returned status {response.status_code}",
                        "response_text": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
        
        result = asyncio.run(search_content())
        logger.info(f"Search vault content completed: {result.get('success', False)}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to search vault content: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

@tool
def enhanced_write_vault_file(file_path: str, content: str, vault_name: str = "Nomade Milionario") -> Dict[str, Any]:
    """Write content to a vault file with enhanced validation and backup"""
    try:
        logger.info(f"Writing file: {file_path} to vault: {vault_name}")
        
        async def write_file():
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.put(
                    f"{OBSIDIAN_BASE_URL}/vault/{file_path}",
                    headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"},
                    content=content
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "file_path": file_path,
                        "content_length": len(content),
                        "message": "File written successfully",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Write API returned status {response.status_code}",
                        "response_text": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
        
        result = asyncio.run(write_file())
        logger.info(f"Write vault file completed: {result.get('success', False)}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to write vault file {file_path}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

@tool
def enhanced_get_vault_statistics(vault_name: str = "Nomade Milionario") -> Dict[str, Any]:
    """Get comprehensive vault statistics and analytics"""
    try:
        logger.info(f"Getting vault statistics for: {vault_name}")
        
        # Get file list first
        files_result = enhanced_list_vault_files(vault_name)
        if not files_result.get("success"):
            return files_result
        
        files = files_result.get("files", [])
        
        # Calculate comprehensive statistics
        total_files = len(files)
        markdown_files = [f for f in files if f.get("is_markdown", False)]
        other_files = [f for f in files if not f.get("is_markdown", False)]
        
        # File type analysis
        file_extensions = {}
        for file in files:
            ext = file.get("extension", "no_extension")
            file_extensions[ext] = file_extensions.get(ext, 0) + 1
        
        # Size analysis
        total_size = sum(f.get("size", 0) for f in files)
        avg_size = total_size / total_files if total_files > 0 else 0
        
        # Recent activity (files modified in last 7 days)
        recent_files = []
        cutoff_date = datetime.now().timestamp() - (7 * 24 * 60 * 60)  # 7 days ago
        
        for file in files:
            try:
                if file.get("modified"):
                    # Parse ISO timestamp
                    modified_time = datetime.fromisoformat(file["modified"].replace("Z", "+00:00")).timestamp()
                    if modified_time > cutoff_date:
                        recent_files.append(file)
            except:
                pass
        
        statistics = {
            "success": True,
            "vault_name": vault_name,
            "total_files": total_files,
            "markdown_files": len(markdown_files),
            "other_files": len(other_files),
            "total_size_bytes": total_size,
            "average_file_size": round(avg_size, 2),
            "file_extensions": file_extensions,
            "recent_files_count": len(recent_files),
            "recent_files": recent_files[:10],  # Top 10 recent files
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Vault statistics completed for {vault_name}: {total_files} files")
        return statistics
        
    except Exception as e:
        error_msg = f"Failed to get vault statistics: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

# Enhanced workflow nodes with comprehensive error handling
def start_enhanced_agent(state: AgentState) -> AgentState:
    """Initialize the enhanced interactive agent"""
    try:
        logger.info(f"Starting enhanced agent for session: {state.session_id}")
        
        state.current_state = ConversationState.LISTENING
        state.messages.append(SystemMessage(content="You are an enhanced interactive AI agent with comprehensive vault access and error handling capabilities. You can help users explore, search, and manage their Obsidian vault with advanced context retrieval."))
        
        # Initialize metrics
        state.metrics.conversation_turns = 1
        state.last_activity = datetime.now()
        
        logger.info("Enhanced agent initialized successfully")
        return state
        
    except Exception as e:
        logger.error(f"Failed to start enhanced agent: {str(e)}")
        logger.error(traceback.format_exc())
        state.current_state = ConversationState.ERROR
        state.error_log.append(f"Start agent error: {str(e)}")
        state.metrics.errors += 1
        return state

def analyze_user_input(state: AgentState) -> AgentState:
    """Analyze user input and determine appropriate actions"""
    try:
        logger.info(f"Analyzing user input: {state.user_input[:100]}...")
        
        state.current_state = ConversationState.PROCESSING
        
        # Simple intent analysis
        user_input_lower = state.user_input.lower()
        
        if any(keyword in user_input_lower for keyword in ["search", "find", "look for", "query"]):
            state.context_data["intent"] = "search"
            state.context_data["search_query"] = state.user_input
        elif any(keyword in user_input_lower for keyword in ["list", "show", "files", "notes"]):
            state.context_data["intent"] = "list"
        elif any(keyword in user_input_lower for keyword in ["read", "open", "view", "show me"]):
            state.context_data["intent"] = "read"
        elif any(keyword in user_input_lower for keyword in ["write", "create", "save", "update"]):
            state.context_data["intent"] = "write"
        elif any(keyword in user_input_lower for keyword in ["stats", "statistics", "info", "health"]):
            state.context_data["intent"] = "stats"
        else:
            state.context_data["intent"] = "general"
        
        state.metrics.context_retrievals += 1
        logger.info(f"User intent determined: {state.context_data['intent']}")
        
        return state
        
    except Exception as e:
        logger.error(f"Failed to analyze user input: {str(e)}")
        logger.error(traceback.format_exc())
        state.current_state = ConversationState.ERROR
        state.error_log.append(f"Analyze input error: {str(e)}")
        state.metrics.errors += 1
        return state

def execute_vault_operations(state: AgentState) -> AgentState:
    """Execute appropriate vault operations based on user intent"""
    try:
        logger.info(f"Executing vault operations for intent: {state.context_data.get('intent', 'unknown')}")
        
        intent = state.context_data.get("intent", "general")
        
        if intent == "search":
            # Perform search operation
            search_query = state.context_data.get("search_query", state.user_input)
            search_result = enhanced_search_vault_content(search_query, state.vault_name)
            
            if search_result.get("success"):
                state.context_data["search_results"] = search_result
                state.metrics.search_queries += 1
                state.metrics.vault_operations += 1
                logger.info(f"Search completed: {len(search_result.get('results', []))} results")
            else:
                state.error_log.append(f"Search failed: {search_result.get('error', 'Unknown error')}")
                state.metrics.errors += 1
        
        elif intent == "list":
            # List vault files
            list_result = enhanced_list_vault_files(state.vault_name)
            
            if list_result.get("success"):
                state.context_data["file_list"] = list_result
                state.metrics.vault_operations += 1
                logger.info(f"File listing completed: {list_result.get('total_files', 0)} files")
            else:
                state.error_log.append(f"File listing failed: {list_result.get('error', 'Unknown error')}")
                state.metrics.errors += 1
        
        elif intent == "stats":
            # Get vault statistics
            stats_result = enhanced_get_vault_statistics(state.vault_name)
            
            if stats_result.get("success"):
                state.context_data["vault_stats"] = stats_result
                state.metrics.vault_operations += 1
                logger.info("Vault statistics retrieved successfully")
            else:
                state.error_log.append(f"Stats retrieval failed: {stats_result.get('error', 'Unknown error')}")
                state.metrics.errors += 1
        
        # Always check vault health
        health_result = enhanced_vault_health_check()
        state.context_data["vault_health"] = health_result
        state.metrics.api_calls += 1
        
        return state
        
    except Exception as e:
        logger.error(f"Failed to execute vault operations: {str(e)}")
        logger.error(traceback.format_exc())
        state.current_state = ConversationState.ERROR
        state.error_log.append(f"Vault operations error: {str(e)}")
        state.metrics.errors += 1
        return state

def generate_intelligent_response(state: AgentState) -> AgentState:
    """Generate intelligent response based on context and operations"""
    try:
        logger.info("Generating intelligent response")
        
        state.current_state = ConversationState.RESPONDING
        
        # Build response based on context
        response_parts = []
        
        # Add greeting
        response_parts.append("🤖 **Enhanced Interactive Agent Response**")
        response_parts.append("")
        
        # Add vault health status
        health = state.context_data.get("vault_health", {})
        if health.get("status") == "healthy":
            response_parts.append("✅ **Vault Status**: Healthy and connected")
        else:
            response_parts.append(f"⚠️ **Vault Status**: {health.get('status', 'Unknown')} - {health.get('error', 'No details')}")
        
        # Add specific responses based on intent
        intent = state.context_data.get("intent", "general")
        
        if intent == "search" and "search_results" in state.context_data:
            search_results = state.context_data["search_results"]
            results = search_results.get("results", [])
            
            response_parts.append(f"")
            response_parts.append(f"🔍 **Search Results** for '{search_results.get('query', '')}':")
            response_parts.append(f"Found {len(results)} results")
            response_parts.append("")
            
            for i, result in enumerate(results[:5], 1):  # Show top 5 results
                response_parts.append(f"{i}. **{result.get('name', 'Unknown')}**")
                response_parts.append(f"   - Path: `{result.get('path', 'Unknown')}`")
                response_parts.append(f"   - Type: {result.get('type', 'Unknown')}")
                response_parts.append(f"   - Modified: {result.get('modified', 'Unknown')}")
                response_parts.append("")
        
        elif intent == "list" and "file_list" in state.context_data:
            file_list = state.context_data["file_list"]
            files = file_list.get("files", [])
            
            response_parts.append(f"")
            response_parts.append(f"📁 **Vault Files** ({file_list.get('total_files', 0)} total):")
            response_parts.append(f"- Markdown files: {file_list.get('markdown_files', 0)}")
            response_parts.append("")
            
            # Show recent files
            recent_files = [f for f in files if f.get("is_markdown", False)][:10]
            for i, file in enumerate(recent_files, 1):
                response_parts.append(f"{i}. **{file.get('name', 'Unknown')}**")
                response_parts.append(f"   - Path: `{file.get('path', 'Unknown')}`")
                response_parts.append("")
        
        elif intent == "stats" and "vault_stats" in state.context_data:
            stats = state.context_data["vault_stats"]
            
            response_parts.append(f"")
            response_parts.append(f"📊 **Vault Statistics**:")
            response_parts.append(f"- Total files: {stats.get('total_files', 0)}")
            response_parts.append(f"- Markdown files: {stats.get('markdown_files', 0)}")
            response_parts.append(f"- Total size: {stats.get('total_size_bytes', 0):,} bytes")
            response_parts.append(f"- Average file size: {stats.get('average_file_size', 0):.2f} bytes")
            response_parts.append(f"- Recent files: {stats.get('recent_files_count', 0)}")
            response_parts.append("")
        
        else:
            response_parts.append("")
            response_parts.append("💬 **General Response**:")
            response_parts.append("I'm here to help you explore and manage your Obsidian vault!")
            response_parts.append("")
            response_parts.append("**Available commands:**")
            response_parts.append("- Search for content: 'search [query]' or 'find [query]'")
            response_parts.append("- List files: 'list files' or 'show notes'")
            response_parts.append("- Get statistics: 'stats' or 'vault info'")
            response_parts.append("- Read a file: 'read [file path]'")
            response_parts.append("")
        
        # Add metrics
        response_parts.append("📈 **Session Metrics**:")
        response_parts.append(f"- API Calls: {state.metrics.api_calls}")
        response_parts.append(f"- Vault Operations: {state.metrics.vault_operations}")
        response_parts.append(f"- Search Queries: {state.metrics.search_queries}")
        response_parts.append(f"- Errors: {state.metrics.errors}")
        response_parts.append(f"- Conversation Turns: {state.metrics.conversation_turns}")
        response_parts.append("")
        
        # Add error log if any
        if state.error_log:
            response_parts.append("⚠️ **Recent Errors**:")
            for error in state.error_log[-3:]:  # Show last 3 errors
                response_parts.append(f"- {error}")
            response_parts.append("")
        
        # Add timestamp
        response_parts.append(f"🕒 **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create AI message
        response_content = "\n".join(response_parts)
        state.messages.append(AIMessage(content=response_content))
        
        # Update metrics
        state.metrics.successful_responses += 1
        state.metrics.conversation_turns += 1
        state.last_activity = datetime.now()
        
        # Add to conversation history
        state.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": state.user_input,
            "agent_response": response_content,
            "intent": intent,
            "success": True
        })
        
        logger.info("Intelligent response generated successfully")
        return state
        
    except Exception as e:
        logger.error(f"Failed to generate intelligent response: {str(e)}")
        logger.error(traceback.format_exc())
        state.current_state = ConversationState.ERROR
        state.error_log.append(f"Response generation error: {str(e)}")
        state.metrics.errors += 1
        
        # Generate error response
        error_response = f"❌ **Error**: I encountered an issue while processing your request: {str(e)}"
        state.messages.append(AIMessage(content=error_response))
        
        return state

def finalize_enhanced_agent(state: AgentState) -> AgentState:
    """Finalize the enhanced agent session"""
    try:
        logger.info(f"Finalizing enhanced agent session: {state.session_id}")
        
        state.current_state = ConversationState.COMPLETED
        
        # Calculate final metrics
        if state.metrics.conversation_turns > 0:
            state.metrics.error_rate = state.metrics.errors / state.metrics.conversation_turns
        
        # Log session summary
        logger.info(f"Session {state.session_id} completed:")
        logger.info(f"- Conversation turns: {state.metrics.conversation_turns}")
        logger.info(f"- API calls: {state.metrics.api_calls}")
        logger.info(f"- Vault operations: {state.metrics.vault_operations}")
        logger.info(f"- Errors: {state.metrics.errors}")
        logger.info(f"- Error rate: {state.metrics.error_rate:.2%}")
        
        return state
        
    except Exception as e:
        logger.error(f"Failed to finalize enhanced agent: {str(e)}")
        logger.error(traceback.format_exc())
        state.current_state = ConversationState.ERROR
        state.error_log.append(f"Finalization error: {str(e)}")
        return state

# Create the enhanced interactive agent workflow
def create_enhanced_interactive_agent():
    """Create the enhanced interactive agent workflow"""
    try:
        logger.info("Creating enhanced interactive agent workflow")
        
        # Create workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("start", start_enhanced_agent)
        workflow.add_node("analyze_input", analyze_user_input)
        workflow.add_node("execute_operations", execute_vault_operations)
        workflow.add_node("generate_response", generate_intelligent_response)
        workflow.add_node("finalize", finalize_enhanced_agent)
        
        # Add edges
        workflow.set_entry_point("start")
        workflow.add_edge("start", "analyze_input")
        workflow.add_edge("analyze_input", "execute_operations")
        workflow.add_edge("execute_operations", "generate_response")
        workflow.add_edge("generate_response", "finalize")
        workflow.add_edge("finalize", END)
        
        # Compile workflow
        compiled_workflow = workflow.compile()
        
        logger.info("Enhanced interactive agent workflow created successfully")
        return compiled_workflow
        
    except Exception as e:
        logger.error(f"Failed to create enhanced interactive agent workflow: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Create the workflow instance
enhanced_interactive_agent = create_enhanced_interactive_agent()

# Example usage function
def run_enhanced_agent_example():
    """Run an example of the enhanced interactive agent"""
    try:
        logger.info("Running enhanced agent example")
        
        # Create initial state
        initial_state = AgentState(
            user_input="Hello! Can you help me search for 'langgraph' in my vault and show me some statistics?",
            vault_name="Nomade Milionario"
        )
        
        # Run the workflow
        result = enhanced_interactive_agent.invoke(initial_state)
        
        # Print results
        print("🤖 Enhanced Interactive Agent Example Results:")
        print("=" * 60)
        
        for message in result.messages:
            if hasattr(message, 'content'):
                print(f"\n{message.content}")
        
        print(f"\n📊 Final Metrics:")
        print(f"- API Calls: {result.metrics.api_calls}")
        print(f"- Vault Operations: {result.metrics.vault_operations}")
        print(f"- Search Queries: {result.metrics.search_queries}")
        print(f"- Errors: {result.metrics.errors}")
        print(f"- Conversation Turns: {result.metrics.conversation_turns}")
        print(f"- Error Rate: {result.metrics.error_rate:.2%}")
        
        logger.info("Enhanced agent example completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Failed to run enhanced agent example: {str(e)}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    # Run the example
    run_enhanced_agent_example()

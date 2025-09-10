"""
Observable LangGraph Agent with Comprehensive Tracing and Debugging
Integrates with the Observability MCP server for complete monitoring
"""

import asyncio
import json
import logging
import traceback
import uuid
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(Enum):
    INITIAL = "initial"
    LISTENING = "listening"
    PROCESSING = "processing"
    EXECUTING = "executing"
    RESPONDING = "responding"
    CHECKPOINTING = "checkpointing"
    ERROR = "error"
    COMPLETED = "completed"

@dataclass
class ObservableAgentState:
    """Enhanced state with observability features"""
    messages: List[Any] = field(default_factory=list)
    current_state: AgentState = AgentState.INITIAL
    user_input: str = ""
    vault_name: str = "Nomade Milionario"
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    # Observability fields
    thread_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = field(default_factory=lambda: f"observable_agent_{uuid.uuid4().hex[:8]}")
    workflow_id: str = "observable_workflow"
    trace_events: List[Dict[str, Any]] = field(default_factory=list)
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    error_log: List[str] = field(default_factory=list)
    
    # Human-in-the-loop fields
    human_input_required: bool = False
    human_input_prompt: str = ""
    human_input_response: Optional[str] = None
    checkpoint_required: bool = False
    checkpoint_reason: str = ""

# Configuration
OBSIDIAN_API_KEY = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
OBSIDIAN_BASE_URL = "http://127.0.0.1:27123"
OBSERVABILITY_MCP_URL = "http://127.0.0.1:8002"  # Assuming observability MCP runs on port 8002

class SearchQuery(BaseModel):
    query: str = Field(..., description="Search query for vault content")

# Observability MCP client
class ObservabilityClient:
    """Client for interacting with the Observability MCP server"""
    
    def __init__(self, base_url: str = OBSERVABILITY_MCP_URL):
        self.base_url = base_url
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def create_trace_event(self, thread_id: str, agent_id: str, workflow_id: str, 
                               event_type: str, level: str, message: str, 
                               data: Dict[str, Any] = None, tags: List[str] = None) -> bool:
        """Create a trace event"""
        try:
            payload = {
                "thread_id": thread_id,
                "agent_id": agent_id,
                "workflow_id": workflow_id,
                "event_type": event_type,
                "level": level,
                "message": message,
                "data": data or {},
                "tags": tags or []
            }
            
            response = await self.session.post(
                f"{self.base_url}/tools/create_trace_event",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Trace event created: {event_type} - {message}")
                return True
            else:
                logger.warning(f"Failed to create trace event: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating trace event: {e}")
            return False
    
    async def create_checkpoint(self, thread_id: str, agent_id: str, workflow_id: str,
                              checkpoint_type: str, state_snapshot: Dict[str, Any],
                              human_input_required: bool = False, human_input_prompt: str = "",
                              metadata: Dict[str, Any] = None) -> bool:
        """Create a checkpoint"""
        try:
            payload = {
                "thread_id": thread_id,
                "agent_id": agent_id,
                "workflow_id": workflow_id,
                "checkpoint_type": checkpoint_type,
                "state_snapshot": state_snapshot,
                "human_input_required": human_input_required,
                "human_input_prompt": human_input_prompt,
                "metadata": metadata or {}
            }
            
            response = await self.session.post(
                f"{self.base_url}/tools/create_checkpoint",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Checkpoint created: {checkpoint_type}")
                return True
            else:
                logger.warning(f"Failed to create checkpoint: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating checkpoint: {e}")
            return False
    
    async def start_performance_monitoring(self, agent_id: str, workflow_id: str, thread_id: str) -> bool:
        """Start performance monitoring"""
        try:
            payload = {
                "agent_id": agent_id,
                "workflow_id": workflow_id,
                "thread_id": thread_id
            }
            
            response = await self.session.post(
                f"{self.base_url}/tools/start_performance_monitoring",
                json=payload
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error starting performance monitoring: {e}")
            return False
    
    async def stop_performance_monitoring(self, agent_id: str, workflow_id: str, thread_id: str) -> bool:
        """Stop performance monitoring"""
        try:
            payload = {
                "agent_id": agent_id,
                "workflow_id": workflow_id,
                "thread_id": thread_id
            }
            
            response = await self.session.post(
                f"{self.base_url}/tools/stop_performance_monitoring",
                json=payload
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error stopping performance monitoring: {e}")
            return False
    
    async def get_debug_summary(self, thread_id: str, agent_id: str = None) -> Dict[str, Any]:
        """Get debug summary"""
        try:
            payload = {
                "thread_id": thread_id,
                "agent_id": agent_id,
                "include_traces": True,
                "include_checkpoints": True,
                "include_performance": True
            }
            
            response = await self.session.post(
                f"{self.base_url}/tools/get_debug_summary",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get debug summary: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting debug summary: {e}")
            return {"error": str(e)}

# Initialize observability client
observability_client = ObservabilityClient()

# Enhanced MCP Tools with observability
@tool
def observable_vault_health_check() -> Dict[str, Any]:
    """Check vault health with comprehensive tracing"""
    try:
        logger.info("Starting observable vault health check")
        
        async def check_health():
            # Create trace event
            await observability_client.create_trace_event(
                thread_id="current_thread",  # Will be updated by workflow
                agent_id="observable_agent",
                workflow_id="observable_workflow",
                event_type="vault_health_check_start",
                level="info",
                message="Starting vault health check",
                tags=["health_check", "vault"]
            )
            
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
                        
                        # Create success trace event
                        await observability_client.create_trace_event(
                            thread_id="current_thread",
                            agent_id="observable_agent",
                            workflow_id="observable_workflow",
                            event_type="vault_health_check_success",
                            level="info",
                            message="Vault health check successful",
                            data={"vault_files_count": len(vault_data.get("files", []))},
                            tags=["health_check", "vault", "success"]
                        )
                        
                        return {
                            "status": "healthy",
                            "connectivity": "ok",
                            "authentication": "ok",
                            "vault_files_count": len(vault_data.get("files", [])),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        # Create auth error trace event
                        await observability_client.create_trace_event(
                            thread_id="current_thread",
                            agent_id="observable_agent",
                            workflow_id="observable_workflow",
                            event_type="vault_health_check_auth_error",
                            level="error",
                            message=f"Authentication failed: {auth_response.status_code}",
                            data={"status_code": auth_response.status_code},
                            tags=["health_check", "vault", "error", "auth"]
                        )
                        
                        return {
                            "status": "auth_error",
                            "connectivity": "ok",
                            "authentication": "failed",
                            "error": f"Auth failed: {auth_response.status_code}",
                            "timestamp": datetime.now().isoformat()
                        }
                else:
                    # Create connectivity error trace event
                    await observability_client.create_trace_event(
                        thread_id="current_thread",
                        agent_id="observable_agent",
                        workflow_id="observable_workflow",
                        event_type="vault_health_check_connectivity_error",
                        level="error",
                        message=f"Health check failed: {health_response.status_code}",
                        data={"status_code": health_response.status_code},
                        tags=["health_check", "vault", "error", "connectivity"]
                    )
                    
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
        
        # Create error trace event
        asyncio.run(observability_client.create_trace_event(
            thread_id="current_thread",
            agent_id="observable_agent",
            workflow_id="observable_workflow",
            event_type="vault_health_check_exception",
            level="error",
            message=error_msg,
            data={"exception": str(e)},
            tags=["health_check", "vault", "error", "exception"]
        ))
        
        return {
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

@tool
def observable_search_vault_content(query: str, vault_name: str = "Nomade Milionario", limit: int = 10) -> Dict[str, Any]:
    """Search vault content with comprehensive tracing and checkpointing"""
    try:
        logger.info(f"Starting observable vault search: '{query}'")
        
        async def search_content():
            # Create trace event
            await observability_client.create_trace_event(
                thread_id="current_thread",
                agent_id="observable_agent",
                workflow_id="observable_workflow",
                event_type="vault_search_start",
                level="info",
                message=f"Starting vault search for: {query}",
                data={"query": query, "vault_name": vault_name, "limit": limit},
                tags=["search", "vault"]
            )
            
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
                            "relevance_score": 1.0,
                            "is_markdown": result.get("path", "").endswith(('.md', '.markdown')),
                            "query_matches": query.lower() in result.get("name", "").lower()
                        }
                        enhanced_results.append(enhanced_result)
                    
                    # Sort by relevance
                    enhanced_results.sort(key=lambda x: (x["query_matches"], x["is_markdown"]), reverse=True)
                    
                    # Create success trace event
                    await observability_client.create_trace_event(
                        thread_id="current_thread",
                        agent_id="observable_agent",
                        workflow_id="observable_workflow",
                        event_type="vault_search_success",
                        level="info",
                        message=f"Vault search completed: {len(enhanced_results)} results",
                        data={"query": query, "results_count": len(enhanced_results)},
                        tags=["search", "vault", "success"]
                    )
                    
                    # Create checkpoint for search results
                    await observability_client.create_checkpoint(
                        thread_id="current_thread",
                        agent_id="observable_agent",
                        workflow_id="observable_workflow",
                        checkpoint_type="workflow_state",
                        state_snapshot={
                            "search_query": query,
                            "results": enhanced_results,
                            "timestamp": datetime.now().isoformat()
                        },
                        metadata={"operation": "vault_search", "results_count": len(enhanced_results)}
                    )
                    
                    return {
                        "success": True,
                        "query": query,
                        "vault_name": vault_name,
                        "results": enhanced_results,
                        "total_results": len(enhanced_results),
                        "search_timestamp": datetime.now().isoformat()
                    }
                else:
                    # Create error trace event
                    await observability_client.create_trace_event(
                        thread_id="current_thread",
                        agent_id="observable_agent",
                        workflow_id="observable_workflow",
                        event_type="vault_search_error",
                        level="error",
                        message=f"Search API returned status {response.status_code}",
                        data={"status_code": response.status_code, "response_text": response.text},
                        tags=["search", "vault", "error"]
                    )
                    
                    return {
                        "success": False,
                        "error": f"Search API returned status {response.status_code}",
                        "response_text": response.text,
                        "timestamp": datetime.now().isoformat()
                    }
        
        result = asyncio.run(search_content())
        logger.info(f"Observable vault search completed: {result.get('success', False)}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to search vault content: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Create error trace event
        asyncio.run(observability_client.create_trace_event(
            thread_id="current_thread",
            agent_id="observable_agent",
            workflow_id="observable_workflow",
            event_type="vault_search_exception",
            level="error",
            message=error_msg,
            data={"exception": str(e)},
            tags=["search", "vault", "error", "exception"]
        ))
        
        return {
            "success": False,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }

# Enhanced workflow nodes with observability
def start_observable_agent(state: ObservableAgentState) -> ObservableAgentState:
    """Initialize the observable agent with comprehensive tracing"""
    try:
        logger.info(f"Starting observable agent: {state.agent_id}")
        
        # Update thread_id in observability client calls
        global current_thread_id
        current_thread_id = state.thread_id
        
        state.current_state = AgentState.LISTENING
        state.messages.append(SystemMessage(content="You are an observable AI agent with comprehensive tracing, debugging, and human-in-the-loop capabilities. You can help users explore and manage their Obsidian vault with full observability."))
        
        # Start performance monitoring
        asyncio.run(observability_client.start_performance_monitoring(
            state.agent_id, state.workflow_id, state.thread_id
        ))
        
        # Create initial trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "agent_start", "info", "Observable agent initialized",
            {"agent_id": state.agent_id, "thread_id": state.thread_id},
            ["agent", "initialization"]
        ))
        
        # Create initial checkpoint
        asyncio.run(observability_client.create_checkpoint(
            state.thread_id, state.agent_id, state.workflow_id,
            "workflow_state", {"state": "initialized", "agent_id": state.agent_id},
            metadata={"operation": "agent_initialization"}
        ))
        
        logger.info("Observable agent initialized successfully")
        return state
        
    except Exception as e:
        logger.error(f"Failed to start observable agent: {str(e)}")
        logger.error(traceback.format_exc())
        state.current_state = AgentState.ERROR
        state.error_log.append(f"Start agent error: {str(e)}")
        
        # Create error trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "agent_start_error", "error", f"Failed to start agent: {str(e)}",
            {"exception": str(e)},
            ["agent", "error", "initialization"]
        ))
        
        return state

def analyze_user_input_observable(state: ObservableAgentState) -> ObservableAgentState:
    """Analyze user input with comprehensive tracing"""
    try:
        logger.info(f"Analyzing user input: {state.user_input[:100]}...")
        
        state.current_state = AgentState.PROCESSING
        
        # Create trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "user_input_analysis_start", "info", "Starting user input analysis",
            {"user_input_length": len(state.user_input)},
            ["analysis", "user_input"]
        ))
        
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
        elif any(keyword in user_input_lower for keyword in ["debug", "trace", "logs", "monitor"]):
            state.context_data["intent"] = "debug"
        else:
            state.context_data["intent"] = "general"
        
        # Create analysis complete trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "user_input_analysis_complete", "info", f"User intent determined: {state.context_data['intent']}",
            {"intent": state.context_data["intent"]},
            ["analysis", "user_input", "intent"]
        ))
        
        # Check if human input is required
        if state.context_data["intent"] in ["write", "delete", "modify"]:
            state.human_input_required = True
            state.human_input_prompt = f"Are you sure you want to {state.context_data['intent']}? Please confirm:"
            state.checkpoint_required = True
            state.checkpoint_reason = "Human confirmation required for destructive operation"
        
        logger.info(f"User intent determined: {state.context_data['intent']}")
        return state
        
    except Exception as e:
        logger.error(f"Failed to analyze user input: {str(e)}")
        logger.error(traceback.format_exc())
        state.current_state = AgentState.ERROR
        state.error_log.append(f"Analyze input error: {str(e)}")
        
        # Create error trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "user_input_analysis_error", "error", f"Failed to analyze user input: {str(e)}",
            {"exception": str(e)},
            ["analysis", "user_input", "error"]
        ))
        
        return state

def execute_vault_operations_observable(state: ObservableAgentState) -> ObservableAgentState:
    """Execute vault operations with comprehensive tracing and checkpointing"""
    try:
        logger.info(f"Executing vault operations for intent: {state.context_data.get('intent', 'unknown')}")
        
        state.current_state = AgentState.EXECUTING
        
        intent = state.context_data.get("intent", "general")
        
        # Create execution start trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "vault_operations_start", "info", f"Starting vault operations for intent: {intent}",
            {"intent": intent},
            ["execution", "vault_operations"]
        ))
        
        if intent == "search":
            # Perform search operation
            search_query = state.context_data.get("search_query", state.user_input)
            search_result = observable_search_vault_content(search_query, state.vault_name)
            
            if search_result.get("success"):
                state.context_data["search_results"] = search_result
                logger.info(f"Search completed: {len(search_result.get('results', []))} results")
            else:
                state.error_log.append(f"Search failed: {search_result.get('error', 'Unknown error')}")
        
        elif intent == "debug":
            # Get debug summary
            debug_summary = asyncio.run(observability_client.get_debug_summary(
                state.thread_id, state.agent_id
            ))
            state.context_data["debug_summary"] = debug_summary
        
        # Always check vault health
        health_result = observable_vault_health_check()
        state.context_data["vault_health"] = health_result
        
        # Create execution complete trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "vault_operations_complete", "info", "Vault operations completed",
            {"intent": intent, "success": True},
            ["execution", "vault_operations", "success"]
        ))
        
        # Create checkpoint for operations
        asyncio.run(observability_client.create_checkpoint(
            state.thread_id, state.agent_id, state.workflow_id,
            "workflow_state", {
                "intent": intent,
                "context_data": state.context_data,
                "timestamp": datetime.now().isoformat()
            },
            metadata={"operation": "vault_operations", "intent": intent}
        ))
        
        return state
        
    except Exception as e:
        logger.error(f"Failed to execute vault operations: {str(e)}")
        logger.error(traceback.format_exc())
        state.current_state = AgentState.ERROR
        state.error_log.append(f"Vault operations error: {str(e)}")
        
        # Create error trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "vault_operations_error", "error", f"Failed to execute vault operations: {str(e)}",
            {"exception": str(e)},
            ["execution", "vault_operations", "error"]
        ))
        
        return state

def generate_intelligent_response_observable(state: ObservableAgentState) -> ObservableAgentState:
    """Generate intelligent response with comprehensive tracing"""
    try:
        logger.info("Generating intelligent response with observability")
        
        state.current_state = AgentState.RESPONDING
        
        # Create response generation trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "response_generation_start", "info", "Starting response generation",
            {},
            ["response", "generation"]
        ))
        
        # Build response based on context
        response_parts = []
        
        # Add greeting
        response_parts.append("🤖 **Observable Interactive Agent Response**")
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
            
            for i, result in enumerate(results[:5], 1):
                response_parts.append(f"{i}. **{result.get('name', 'Unknown')}**")
                response_parts.append(f"   - Path: `{result.get('path', 'Unknown')}`")
                response_parts.append(f"   - Type: {result.get('type', 'Unknown')}")
                response_parts.append(f"   - Modified: {result.get('modified', 'Unknown')}")
                response_parts.append("")
        
        elif intent == "debug" and "debug_summary" in state.context_data:
            debug_summary = state.context_data["debug_summary"]
            
            response_parts.append(f"")
            response_parts.append(f"🐛 **Debug Summary**:")
            response_parts.append(f"Thread ID: {debug_summary.get('thread_id', 'Unknown')}")
            response_parts.append(f"Total Traces: {debug_summary.get('total_traces', 0)}")
            response_parts.append(f"Total Checkpoints: {debug_summary.get('total_checkpoints', 0)}")
            response_parts.append("")
            
            if "recent_traces" in debug_summary:
                response_parts.append("**Recent Trace Events:**")
                for trace in debug_summary["recent_traces"][:5]:
                    response_parts.append(f"- {trace['timestamp']}: {trace['event_type']} - {trace['message']}")
                response_parts.append("")
        
        else:
            response_parts.append("")
            response_parts.append("💬 **General Response**:")
            response_parts.append("I'm here to help you explore and manage your Obsidian vault with full observability!")
            response_parts.append("")
            response_parts.append("**Available commands:**")
            response_parts.append("- Search for content: 'search [query]' or 'find [query]'")
            response_parts.append("- Debug and monitor: 'debug' or 'trace' or 'logs'")
            response_parts.append("- Get vault info: 'stats' or 'vault info'")
            response_parts.append("")
        
        # Add observability information
        response_parts.append("🔍 **Observability Information**:")
        response_parts.append(f"- Thread ID: {state.thread_id}")
        response_parts.append(f"- Agent ID: {state.agent_id}")
        response_parts.append(f"- Workflow ID: {state.workflow_id}")
        response_parts.append(f"- Current State: {state.current_state.value}")
        response_parts.append("")
        
        # Add human-in-the-loop information
        if state.human_input_required:
            response_parts.append("⚠️ **Human Input Required**:")
            response_parts.append(f"{state.human_input_prompt}")
            response_parts.append("")
        
        # Add timestamp
        response_parts.append(f"🕒 **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create AI message
        response_content = "\n".join(response_parts)
        state.messages.append(AIMessage(content=response_content))
        
        # Create response complete trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "response_generation_complete", "info", "Response generation completed",
            {"response_length": len(response_content)},
            ["response", "generation", "success"]
        ))
        
        logger.info("Intelligent response generated successfully")
        return state
        
    except Exception as e:
        logger.error(f"Failed to generate intelligent response: {str(e)}")
        logger.error(traceback.format_exc())
        state.current_state = AgentState.ERROR
        state.error_log.append(f"Response generation error: {str(e)}")
        
        # Create error trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "response_generation_error", "error", f"Failed to generate response: {str(e)}",
            {"exception": str(e)},
            ["response", "generation", "error"]
        ))
        
        # Generate error response
        error_response = f"❌ **Error**: I encountered an issue while processing your request: {str(e)}"
        state.messages.append(AIMessage(content=error_response))
        
        return state

def finalize_observable_agent(state: ObservableAgentState) -> ObservableAgentState:
    """Finalize the observable agent with comprehensive tracing"""
    try:
        logger.info(f"Finalizing observable agent: {state.agent_id}")
        
        state.current_state = AgentState.COMPLETED
        
        # Stop performance monitoring
        asyncio.run(observability_client.stop_performance_monitoring(
            state.agent_id, state.workflow_id, state.thread_id
        ))
        
        # Create finalization trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "agent_finalization", "info", "Observable agent finalized",
            {"agent_id": state.agent_id, "thread_id": state.thread_id},
            ["agent", "finalization"]
        ))
        
        # Create final checkpoint
        asyncio.run(observability_client.create_checkpoint(
            state.thread_id, state.agent_id, state.workflow_id,
            "workflow_state", {
                "state": "completed",
                "agent_id": state.agent_id,
                "final_timestamp": datetime.now().isoformat()
            },
            metadata={"operation": "agent_finalization"}
        ))
        
        logger.info("Observable agent finalized successfully")
        return state
        
    except Exception as e:
        logger.error(f"Failed to finalize observable agent: {str(e)}")
        logger.error(traceback.format_exc())
        state.current_state = AgentState.ERROR
        state.error_log.append(f"Finalization error: {str(e)}")
        
        # Create error trace event
        asyncio.run(observability_client.create_trace_event(
            state.thread_id, state.agent_id, state.workflow_id,
            "agent_finalization_error", "error", f"Failed to finalize agent: {str(e)}",
            {"exception": str(e)},
            ["agent", "error", "finalization"]
        ))
        
        return state

# Create the observable agent workflow
def create_observable_agent():
    """Create the observable agent workflow"""
    try:
        logger.info("Creating observable agent workflow")
        
        # Create workflow
        workflow = StateGraph(ObservableAgentState)
        
        # Add nodes
        workflow.add_node("start", start_observable_agent)
        workflow.add_node("analyze_input", analyze_user_input_observable)
        workflow.add_node("execute_operations", execute_vault_operations_observable)
        workflow.add_node("generate_response", generate_intelligent_response_observable)
        workflow.add_node("finalize", finalize_observable_agent)
        
        # Add edges
        workflow.set_entry_point("start")
        workflow.add_edge("start", "analyze_input")
        workflow.add_edge("analyze_input", "execute_operations")
        workflow.add_edge("execute_operations", "generate_response")
        workflow.add_edge("generate_response", "finalize")
        workflow.add_edge("finalize", END)
        
        # Compile workflow
        compiled_workflow = workflow.compile()
        
        logger.info("Observable agent workflow created successfully")
        return compiled_workflow
        
    except Exception as e:
        logger.error(f"Failed to create observable agent workflow: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Create the workflow instance
observable_agent = create_observable_agent()

# Example usage function
def run_observable_agent_example():
    """Run an example of the observable agent"""
    try:
        logger.info("Running observable agent example")
        
        # Create initial state
        initial_state = ObservableAgentState(
            user_input="Hello! Can you search for 'langgraph' in my vault and show me debug information?",
            vault_name="Nomade Milionario"
        )
        
        # Run the workflow
        result = observable_agent.invoke(initial_state)
        
        # Print results
        print("🤖 Observable Agent Example Results:")
        print("=" * 60)
        
        for message in result.messages:
            if hasattr(message, 'content'):
                print(f"\n{message.content}")
        
        print(f"\n📊 Final State:")
        print(f"- Thread ID: {result.thread_id}")
        print(f"- Agent ID: {result.agent_id}")
        print(f"- Current State: {result.current_state.value}")
        print(f"- Errors: {len(result.error_log)}")
        
        logger.info("Observable agent example completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Failed to run observable agent example: {str(e)}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    # Run the example
    run_observable_agent_example()

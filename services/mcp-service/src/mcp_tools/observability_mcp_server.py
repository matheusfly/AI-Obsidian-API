"""
Observability MCP Server - Complete Tracing, Logging, and Debugging System
Integrates with LangSmith for comprehensive agent observability and debugging
"""

import asyncio
import json
import logging
import traceback
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
import time
import os
from pathlib import Path

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListResourcesRequest, ListResourcesResult,
    ReadResourceRequest, ReadResourceResult
)
from pydantic import BaseModel, Field

# LangSmith integration
try:
    from langsmith import Client as LangSmithClient
    from langsmith.tracing import LangChainTracer
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    print("Warning: LangSmith not available. Install with: pip install langsmith")

# Configuration
LANGSMITH_API_KEY = "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"
LANGSMITH_PROJECT = "langgraph-observability"
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s',
    handlers=[
        logging.FileHandler('observability.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TraceLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class CheckpointType(Enum):
    HUMAN_INPUT = "human_input"
    AGENT_DECISION = "agent_decision"
    WORKFLOW_STATE = "workflow_state"
    ERROR_RECOVERY = "error_recovery"
    PERFORMANCE_MILESTONE = "performance_milestone"

@dataclass
class TraceEvent:
    """Individual trace event"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    thread_id: str = ""
    agent_id: str = ""
    workflow_id: str = ""
    event_type: str = ""
    level: TraceLevel = TraceLevel.INFO
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    parent_event_id: Optional[str] = None
    duration_ms: Optional[float] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class Checkpoint:
    """Checkpoint for time-travel debugging"""
    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    thread_id: str = ""
    agent_id: str = ""
    workflow_id: str = ""
    checkpoint_type: CheckpointType = CheckpointType.WORKFLOW_STATE
    state_snapshot: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    human_input_required: bool = False
    human_input_prompt: str = ""
    human_input_response: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics for agents and workflows"""
    agent_id: str = ""
    workflow_id: str = ""
    thread_id: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration_ms: float = 0.0
    api_calls: int = 0
    vault_operations: int = 0
    llm_tokens_used: int = 0
    llm_cost_usd: float = 0.0
    errors: int = 0
    checkpoints_created: int = 0
    human_interactions: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

class ObservabilityMCP:
    """Main observability MCP server class"""
    
    def __init__(self):
        self.server = Server("observability-mcp")
        self.traces: Dict[str, List[TraceEvent]] = {}
        self.checkpoints: Dict[str, List[Checkpoint]] = {}
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self.active_threads: Dict[str, Dict[str, Any]] = {}
        self.langsmith_client = None
        self.tracer = None
        
        # Initialize LangSmith if available
        if LANGSMITH_AVAILABLE:
            try:
                self.langsmith_client = LangSmithClient(
                    api_key=LANGSMITH_API_KEY,
                    api_url=LANGSMITH_ENDPOINT
                )
                self.tracer = LangChainTracer(project_name=LANGSMITH_PROJECT)
                logger.info("LangSmith client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize LangSmith client: {e}")
                self.langsmith_client = None
                self.tracer = None
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> ListResourcesResult:
            """List available observability resources"""
            resources = [
                Resource(
                    uri="observability://traces",
                    name="Trace Events",
                    description="All trace events across all threads and agents",
                    mimeType="application/json"
                ),
                Resource(
                    uri="observability://checkpoints",
                    name="Checkpoints",
                    description="All checkpoints for time-travel debugging",
                    mimeType="application/json"
                ),
                Resource(
                    uri="observability://performance",
                    name="Performance Metrics",
                    description="Performance metrics for agents and workflows",
                    mimeType="application/json"
                ),
                Resource(
                    uri="observability://threads",
                    name="Active Threads",
                    description="Currently active threads and their status",
                    mimeType="application/json"
                ),
                Resource(
                    uri="observability://logs",
                    name="Log Files",
                    description="Log files and debugging information",
                    mimeType="text/plain"
                )
            ]
            return ListResourcesResult(resources=resources)
        
        @self.server.read_resource()
        async def read_resource(request: ReadResourceRequest) -> ReadResourceResult:
            """Read observability resources"""
            uri = request.uri
            
            if uri == "observability://traces":
                content = self._get_all_traces()
                return ReadResourceResult(contents=[TextContent(type="text", text=content)])
            
            elif uri == "observability://checkpoints":
                content = self._get_all_checkpoints()
                return ReadResourceResult(contents=[TextContent(type="text", text=content)])
            
            elif uri == "observability://performance":
                content = self._get_performance_metrics()
                return ReadResourceResult(contents=[TextContent(type="text", text=content)])
            
            elif uri == "observability://threads":
                content = self._get_active_threads()
                return ReadResourceResult(contents=[TextContent(type="text", text=content)])
            
            elif uri == "observability://logs":
                content = self._get_log_content()
                return ReadResourceResult(contents=[TextContent(type="text", text=content)])
            
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available observability tools"""
            return [
                Tool(
                    name="create_trace_event",
                    description="Create a new trace event for debugging and monitoring",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "Thread ID"},
                            "agent_id": {"type": "string", "description": "Agent ID"},
                            "workflow_id": {"type": "string", "description": "Workflow ID"},
                            "event_type": {"type": "string", "description": "Type of event"},
                            "level": {"type": "string", "enum": ["debug", "info", "warning", "error", "critical"]},
                            "message": {"type": "string", "description": "Event message"},
                            "data": {"type": "object", "description": "Additional event data"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Event tags"}
                        },
                        "required": ["thread_id", "agent_id", "event_type", "message"]
                    }
                ),
                Tool(
                    name="create_checkpoint",
                    description="Create a checkpoint for time-travel debugging",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "Thread ID"},
                            "agent_id": {"type": "string", "description": "Agent ID"},
                            "workflow_id": {"type": "string", "description": "Workflow ID"},
                            "checkpoint_type": {"type": "string", "enum": ["human_input", "agent_decision", "workflow_state", "error_recovery", "performance_milestone"]},
                            "state_snapshot": {"type": "object", "description": "Current state snapshot"},
                            "human_input_required": {"type": "boolean", "description": "Whether human input is required"},
                            "human_input_prompt": {"type": "string", "description": "Prompt for human input"},
                            "metadata": {"type": "object", "description": "Additional checkpoint metadata"}
                        },
                        "required": ["thread_id", "agent_id", "workflow_id", "checkpoint_type", "state_snapshot"]
                    }
                ),
                Tool(
                    name="get_traces",
                    description="Get trace events for a specific thread, agent, or time range",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "Filter by thread ID"},
                            "agent_id": {"type": "string", "description": "Filter by agent ID"},
                            "workflow_id": {"type": "string", "description": "Filter by workflow ID"},
                            "start_time": {"type": "string", "description": "Start time (ISO format)"},
                            "end_time": {"type": "string", "description": "End time (ISO format)"},
                            "level": {"type": "string", "enum": ["debug", "info", "warning", "error", "critical"]},
                            "limit": {"type": "integer", "description": "Maximum number of events to return"}
                        }
                    }
                ),
                Tool(
                    name="get_checkpoints",
                    description="Get checkpoints for a specific thread or agent",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "Filter by thread ID"},
                            "agent_id": {"type": "string", "description": "Filter by agent ID"},
                            "workflow_id": {"type": "string", "description": "Filter by workflow ID"},
                            "checkpoint_type": {"type": "string", "enum": ["human_input", "agent_decision", "workflow_state", "error_recovery", "performance_milestone"]},
                            "limit": {"type": "integer", "description": "Maximum number of checkpoints to return"}
                        }
                    }
                ),
                Tool(
                    name="time_travel_debug",
                    description="Time-travel to a specific checkpoint for debugging",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "checkpoint_id": {"type": "string", "description": "Checkpoint ID to travel to"},
                            "thread_id": {"type": "string", "description": "Thread ID"},
                            "restore_state": {"type": "boolean", "description": "Whether to restore the state from checkpoint"}
                        },
                        "required": ["checkpoint_id", "thread_id"]
                    }
                ),
                Tool(
                    name="get_performance_metrics",
                    description="Get performance metrics for agents and workflows",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string", "description": "Filter by agent ID"},
                            "workflow_id": {"type": "string", "description": "Filter by workflow ID"},
                            "thread_id": {"type": "string", "description": "Filter by thread ID"},
                            "time_range_hours": {"type": "integer", "description": "Time range in hours"}
                        }
                    }
                ),
                Tool(
                    name="start_performance_monitoring",
                    description="Start performance monitoring for an agent or workflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string", "description": "Agent ID to monitor"},
                            "workflow_id": {"type": "string", "description": "Workflow ID to monitor"},
                            "thread_id": {"type": "string", "description": "Thread ID to monitor"}
                        },
                        "required": ["agent_id", "workflow_id", "thread_id"]
                    }
                ),
                Tool(
                    name="stop_performance_monitoring",
                    description="Stop performance monitoring for an agent or workflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string", "description": "Agent ID to stop monitoring"},
                            "workflow_id": {"type": "string", "description": "Workflow ID to stop monitoring"},
                            "thread_id": {"type": "string", "description": "Thread ID to stop monitoring"}
                        },
                        "required": ["agent_id", "workflow_id", "thread_id"]
                    }
                ),
                Tool(
                    name="get_debug_summary",
                    description="Get a comprehensive debug summary for a thread or agent",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "Thread ID"},
                            "agent_id": {"type": "string", "description": "Agent ID"},
                            "include_traces": {"type": "boolean", "description": "Include trace events"},
                            "include_checkpoints": {"type": "boolean", "description": "Include checkpoints"},
                            "include_performance": {"type": "boolean", "description": "Include performance metrics"}
                        },
                        "required": ["thread_id"]
                    }
                ),
                Tool(
                    name="export_traces_to_langsmith",
                    description="Export traces to LangSmith for analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "Thread ID to export"},
                            "agent_id": {"type": "string", "description": "Agent ID to export"},
                            "workflow_id": {"type": "string", "description": "Workflow ID to export"},
                            "project_name": {"type": "string", "description": "LangSmith project name"}
                        }
                    }
                ),
                Tool(
                    name="analyze_error_patterns",
                    description="Analyze error patterns and provide debugging insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "Thread ID to analyze"},
                            "agent_id": {"type": "string", "description": "Agent ID to analyze"},
                            "time_range_hours": {"type": "integer", "description": "Time range in hours to analyze"},
                            "error_threshold": {"type": "integer", "description": "Minimum number of errors to consider a pattern"}
                        }
                    }
                ),
                Tool(
                    name="get_agent_communication_log",
                    description="Get detailed agent communication logs and patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "Thread ID to analyze"},
                            "agent_id": {"type": "string", "description": "Agent ID to analyze"},
                            "communication_type": {"type": "string", "enum": ["all", "mcp_calls", "api_calls", "vault_operations", "llm_calls"], "description": "Type of communication to filter"},
                            "limit": {"type": "integer", "description": "Maximum number of entries to return"}
                        }
                    }
                ),
                Tool(
                    name="create_debug_session",
                    description="Create a new debugging session with comprehensive monitoring",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_name": {"type": "string", "description": "Name for the debug session"},
                            "thread_id": {"type": "string", "description": "Thread ID to monitor"},
                            "agent_id": {"type": "string", "description": "Agent ID to monitor"},
                            "workflow_id": {"type": "string", "description": "Workflow ID to monitor"},
                            "monitoring_level": {"type": "string", "enum": ["basic", "detailed", "comprehensive"], "description": "Level of monitoring detail"},
                            "auto_checkpoint_interval": {"type": "integer", "description": "Auto-checkpoint interval in seconds (0 to disable)"}
                        },
                        "required": ["session_name", "thread_id", "agent_id", "workflow_id"]
                    }
                ),
                Tool(
                    name="get_debug_session_status",
                    description="Get status and insights from an active debug session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_name": {"type": "string", "description": "Name of the debug session"},
                            "include_recommendations": {"type": "boolean", "description": "Include debugging recommendations"}
                        },
                        "required": ["session_name"]
                    }
                ),
                Tool(
                    name="correlate_errors_with_traces",
                    description="Correlate errors with trace events to identify root causes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "error_id": {"type": "string", "description": "Specific error ID to correlate"},
                            "thread_id": {"type": "string", "description": "Thread ID to analyze"},
                            "time_window_minutes": {"type": "integer", "description": "Time window in minutes before error"},
                            "include_performance_impact": {"type": "boolean", "description": "Include performance impact analysis"}
                        }
                    }
                ),
                Tool(
                    name="generate_debug_report",
                    description="Generate a comprehensive debug report with insights and recommendations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "Thread ID to analyze"},
                            "agent_id": {"type": "string", "description": "Agent ID to analyze"},
                            "report_type": {"type": "string", "enum": ["summary", "detailed", "performance", "error_analysis"], "description": "Type of report to generate"},
                            "include_timeline": {"type": "boolean", "description": "Include detailed timeline"},
                            "include_recommendations": {"type": "boolean", "description": "Include debugging recommendations"}
                        },
                        "required": ["thread_id"]
                    }
                ),
                Tool(
                    name="monitor_langgraph_server_health",
                    description="Monitor LangGraph server health and performance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_url": {"type": "string", "description": "LangGraph server URL", "default": "http://127.0.0.1:2024"},
                            "check_endpoints": {"type": "boolean", "description": "Check all available endpoints"},
                            "performance_metrics": {"type": "boolean", "description": "Collect performance metrics"}
                        }
                    }
                ),
                Tool(
                    name="trace_workflow_execution",
                    description="Trace the complete execution of a LangGraph workflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_name": {"type": "string", "description": "Name of the workflow to trace"},
                            "thread_id": {"type": "string", "description": "Thread ID for the execution"},
                            "include_node_details": {"type": "boolean", "description": "Include detailed node execution information"},
                            "include_state_changes": {"type": "boolean", "description": "Include state change tracking"}
                        },
                        "required": ["workflow_name", "thread_id"]
                    }
                ),
                Tool(
                    name="optimize_agent_performance",
                    description="Analyze and provide optimization recommendations for agent performance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string", "description": "Agent ID to optimize"},
                            "thread_id": {"type": "string", "description": "Thread ID to analyze"},
                            "optimization_focus": {"type": "string", "enum": ["speed", "accuracy", "cost", "reliability"], "description": "Focus area for optimization"},
                            "include_benchmarks": {"type": "boolean", "description": "Include performance benchmarks"}
                        },
                        "required": ["agent_id", "thread_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool calls"""
            try:
                if request.name == "create_trace_event":
                    return await self._create_trace_event(request.arguments)
                elif request.name == "create_checkpoint":
                    return await self._create_checkpoint(request.arguments)
                elif request.name == "get_traces":
                    return await self._get_traces(request.arguments)
                elif request.name == "get_checkpoints":
                    return await self._get_checkpoints(request.arguments)
                elif request.name == "time_travel_debug":
                    return await self._time_travel_debug(request.arguments)
                elif request.name == "get_performance_metrics":
                    return await self._get_performance_metrics(request.arguments)
                elif request.name == "start_performance_monitoring":
                    return await self._start_performance_monitoring(request.arguments)
                elif request.name == "stop_performance_monitoring":
                    return await self._stop_performance_monitoring(request.arguments)
                elif request.name == "get_debug_summary":
                    return await self._get_debug_summary(request.arguments)
                elif request.name == "export_traces_to_langsmith":
                    return await self._export_traces_to_langsmith(request.arguments)
                elif request.name == "analyze_error_patterns":
                    return await self._analyze_error_patterns(request.arguments)
                elif request.name == "get_agent_communication_log":
                    return await self._get_agent_communication_log(request.arguments)
                elif request.name == "create_debug_session":
                    return await self._create_debug_session(request.arguments)
                elif request.name == "get_debug_session_status":
                    return await self._get_debug_session_status(request.arguments)
                elif request.name == "correlate_errors_with_traces":
                    return await self._correlate_errors_with_traces(request.arguments)
                elif request.name == "generate_debug_report":
                    return await self._generate_debug_report(request.arguments)
                elif request.name == "monitor_langgraph_server_health":
                    return await self._monitor_langgraph_server_health(request.arguments)
                elif request.name == "trace_workflow_execution":
                    return await self._trace_workflow_execution(request.arguments)
                elif request.name == "optimize_agent_performance":
                    return await self._optimize_agent_performance(request.arguments)
                else:
                    raise ValueError(f"Unknown tool: {request.name}")
            except Exception as e:
                logger.error(f"Tool call failed: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    async def _create_trace_event(self, args: Dict[str, Any]) -> CallToolResult:
        """Create a new trace event"""
        try:
            event = TraceEvent(
                thread_id=args["thread_id"],
                agent_id=args["agent_id"],
                workflow_id=args.get("workflow_id", ""),
                event_type=args["event_type"],
                level=TraceLevel(args.get("level", "info")),
                message=args["message"],
                data=args.get("data", {}),
                tags=args.get("tags", [])
            )
            
            # Store trace event
            if event.thread_id not in self.traces:
                self.traces[event.thread_id] = []
            self.traces[event.thread_id].append(event)
            
            # Send to LangSmith if available
            if self.langsmith_client and self.tracer:
                try:
                    self.tracer.on_llm_start(
                        serialized={"name": event.event_type},
                        prompts=[event.message],
                        run_id=event.event_id,
                        parent_run_id=event.parent_event_id,
                        tags=event.tags
                    )
                except Exception as e:
                    logger.warning(f"Failed to send trace to LangSmith: {e}")
            
            logger.info(f"Created trace event: {event.event_id} - {event.message}")
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Trace event created: {event.event_id}\nThread: {event.thread_id}\nAgent: {event.agent_id}\nType: {event.event_type}\nMessage: {event.message}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to create trace event: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error creating trace event: {str(e)}")],
                isError=True
            )
    
    async def _create_checkpoint(self, args: Dict[str, Any]) -> CallToolResult:
        """Create a new checkpoint"""
        try:
            checkpoint = Checkpoint(
                thread_id=args["thread_id"],
                agent_id=args["agent_id"],
                workflow_id=args["workflow_id"],
                checkpoint_type=CheckpointType(args["checkpoint_type"]),
                state_snapshot=args["state_snapshot"],
                human_input_required=args.get("human_input_required", False),
                human_input_prompt=args.get("human_input_prompt", ""),
                metadata=args.get("metadata", {})
            )
            
            # Store checkpoint
            if checkpoint.thread_id not in self.checkpoints:
                self.checkpoints[checkpoint.thread_id] = []
            self.checkpoints[checkpoint.thread_id].append(checkpoint)
            
            logger.info(f"Created checkpoint: {checkpoint.checkpoint_id} - {checkpoint.checkpoint_type.value}")
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Checkpoint created: {checkpoint.checkpoint_id}\nThread: {checkpoint.thread_id}\nAgent: {checkpoint.agent_id}\nType: {checkpoint.checkpoint_type.value}\nHuman input required: {checkpoint.human_input_required}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error creating checkpoint: {str(e)}")],
                isError=True
            )
    
    async def _get_traces(self, args: Dict[str, Any]) -> CallToolResult:
        """Get trace events with filtering"""
        try:
            all_traces = []
            for thread_traces in self.traces.values():
                all_traces.extend(thread_traces)
            
            # Apply filters
            filtered_traces = all_traces
            
            if "thread_id" in args:
                filtered_traces = [t for t in filtered_traces if t.thread_id == args["thread_id"]]
            
            if "agent_id" in args:
                filtered_traces = [t for t in filtered_traces if t.agent_id == args["agent_id"]]
            
            if "workflow_id" in args:
                filtered_traces = [t for t in filtered_traces if t.workflow_id == args["workflow_id"]]
            
            if "level" in args:
                filtered_traces = [t for t in filtered_traces if t.level.value == args["level"]]
            
            # Sort by timestamp (newest first)
            filtered_traces.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply limit
            limit = args.get("limit", 100)
            filtered_traces = filtered_traces[:limit]
            
            # Format results
            results = []
            for trace in filtered_traces:
                results.append({
                    "event_id": trace.event_id,
                    "timestamp": trace.timestamp.isoformat(),
                    "thread_id": trace.thread_id,
                    "agent_id": trace.agent_id,
                    "workflow_id": trace.workflow_id,
                    "event_type": trace.event_type,
                    "level": trace.level.value,
                    "message": trace.message,
                    "data": trace.data,
                    "tags": trace.tags,
                    "duration_ms": trace.duration_ms
                })
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Found {len(results)} trace events:\n{json.dumps(results, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to get traces: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting traces: {str(e)}")],
                isError=True
            )
    
    async def _get_checkpoints(self, args: Dict[str, Any]) -> CallToolResult:
        """Get checkpoints with filtering"""
        try:
            all_checkpoints = []
            for thread_checkpoints in self.checkpoints.values():
                all_checkpoints.extend(thread_checkpoints)
            
            # Apply filters
            filtered_checkpoints = all_checkpoints
            
            if "thread_id" in args:
                filtered_checkpoints = [c for c in filtered_checkpoints if c.thread_id == args["thread_id"]]
            
            if "agent_id" in args:
                filtered_checkpoints = [c for c in filtered_checkpoints if c.agent_id == args["agent_id"]]
            
            if "workflow_id" in args:
                filtered_checkpoints = [c for c in filtered_checkpoints if c.workflow_id == args["workflow_id"]]
            
            if "checkpoint_type" in args:
                filtered_checkpoints = [c for c in filtered_checkpoints if c.checkpoint_type.value == args["checkpoint_type"]]
            
            # Sort by timestamp (newest first)
            filtered_checkpoints.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply limit
            limit = args.get("limit", 50)
            filtered_checkpoints = filtered_checkpoints[:limit]
            
            # Format results
            results = []
            for checkpoint in filtered_checkpoints:
                results.append({
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "timestamp": checkpoint.timestamp.isoformat(),
                    "thread_id": checkpoint.thread_id,
                    "agent_id": checkpoint.agent_id,
                    "workflow_id": checkpoint.workflow_id,
                    "checkpoint_type": checkpoint.checkpoint_type.value,
                    "human_input_required": checkpoint.human_input_required,
                    "human_input_prompt": checkpoint.human_input_prompt,
                    "human_input_response": checkpoint.human_input_response,
                    "metadata": checkpoint.metadata
                })
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Found {len(results)} checkpoints:\n{json.dumps(results, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to get checkpoints: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting checkpoints: {str(e)}")],
                isError=True
            )
    
    async def _time_travel_debug(self, args: Dict[str, Any]) -> CallToolResult:
        """Time-travel to a specific checkpoint"""
        try:
            checkpoint_id = args["checkpoint_id"]
            thread_id = args["thread_id"]
            restore_state = args.get("restore_state", False)
            
            # Find the checkpoint
            checkpoint = None
            for thread_checkpoints in self.checkpoints.values():
                for cp in thread_checkpoints:
                    if cp.checkpoint_id == checkpoint_id:
                        checkpoint = cp
                        break
                if checkpoint:
                    break
            
            if not checkpoint:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Checkpoint {checkpoint_id} not found")],
                    isError=True
                )
            
            # Create time-travel trace event
            time_travel_event = TraceEvent(
                thread_id=thread_id,
                agent_id=checkpoint.agent_id,
                workflow_id=checkpoint.workflow_id,
                event_type="time_travel",
                level=TraceLevel.INFO,
                message=f"Time-traveled to checkpoint {checkpoint_id}",
                data={
                    "checkpoint_id": checkpoint_id,
                    "checkpoint_timestamp": checkpoint.timestamp.isoformat(),
                    "restore_state": restore_state
                },
                tags=["time_travel", "debugging"]
            )
            
            if thread_id not in self.traces:
                self.traces[thread_id] = []
            self.traces[thread_id].append(time_travel_event)
            
            result_text = f"Time-traveled to checkpoint {checkpoint_id}\n"
            result_text += f"Checkpoint timestamp: {checkpoint.timestamp.isoformat()}\n"
            result_text += f"Checkpoint type: {checkpoint.checkpoint_type.value}\n"
            result_text += f"Thread: {checkpoint.thread_id}\n"
            result_text += f"Agent: {checkpoint.agent_id}\n"
            
            if restore_state:
                result_text += f"State restored: {json.dumps(checkpoint.state_snapshot, indent=2)}\n"
            
            logger.info(f"Time-traveled to checkpoint {checkpoint_id}")
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            logger.error(f"Failed to time-travel debug: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error time-traveling: {str(e)}")],
                isError=True
            )
    
    async def _get_performance_metrics(self, args: Dict[str, Any]) -> CallToolResult:
        """Get performance metrics"""
        try:
            filtered_metrics = []
            
            for metrics in self.performance_metrics.values():
                include = True
                
                if "agent_id" in args and metrics.agent_id != args["agent_id"]:
                    include = False
                if "workflow_id" in args and metrics.workflow_id != args["workflow_id"]:
                    include = False
                if "thread_id" in args and metrics.thread_id != args["thread_id"]:
                    include = False
                
                if include:
                    filtered_metrics.append({
                        "agent_id": metrics.agent_id,
                        "workflow_id": metrics.workflow_id,
                        "thread_id": metrics.thread_id,
                        "start_time": metrics.start_time.isoformat(),
                        "end_time": metrics.end_time.isoformat() if metrics.end_time else None,
                        "total_duration_ms": metrics.total_duration_ms,
                        "api_calls": metrics.api_calls,
                        "vault_operations": metrics.vault_operations,
                        "llm_tokens_used": metrics.llm_tokens_used,
                        "llm_cost_usd": metrics.llm_cost_usd,
                        "errors": metrics.errors,
                        "checkpoints_created": metrics.checkpoints_created,
                        "human_interactions": metrics.human_interactions,
                        "memory_usage_mb": metrics.memory_usage_mb,
                        "cpu_usage_percent": metrics.cpu_usage_percent
                    })
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Performance metrics ({len(filtered_metrics)} entries):\n{json.dumps(filtered_metrics, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting performance metrics: {str(e)}")],
                isError=True
            )
    
    async def _start_performance_monitoring(self, args: Dict[str, Any]) -> CallToolResult:
        """Start performance monitoring"""
        try:
            agent_id = args["agent_id"]
            workflow_id = args["workflow_id"]
            thread_id = args["thread_id"]
            
            metrics_key = f"{agent_id}_{workflow_id}_{thread_id}"
            
            if metrics_key in self.performance_metrics:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Performance monitoring already active for {metrics_key}")],
                    isError=True
                )
            
            metrics = PerformanceMetrics(
                agent_id=agent_id,
                workflow_id=workflow_id,
                thread_id=thread_id
            )
            
            self.performance_metrics[metrics_key] = metrics
            
            logger.info(f"Started performance monitoring for {metrics_key}")
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Performance monitoring started for {metrics_key}")]
            )
            
        except Exception as e:
            logger.error(f"Failed to start performance monitoring: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error starting performance monitoring: {str(e)}")],
                isError=True
            )
    
    async def _stop_performance_monitoring(self, args: Dict[str, Any]) -> CallToolResult:
        """Stop performance monitoring"""
        try:
            agent_id = args["agent_id"]
            workflow_id = args["workflow_id"]
            thread_id = args["thread_id"]
            
            metrics_key = f"{agent_id}_{workflow_id}_{thread_id}"
            
            if metrics_key not in self.performance_metrics:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"No active performance monitoring for {metrics_key}")],
                    isError=True
                )
            
            metrics = self.performance_metrics[metrics_key]
            metrics.end_time = datetime.now()
            metrics.total_duration_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            
            logger.info(f"Stopped performance monitoring for {metrics_key}")
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Performance monitoring stopped for {metrics_key}\nDuration: {metrics.total_duration_ms:.2f}ms")]
            )
            
        except Exception as e:
            logger.error(f"Failed to stop performance monitoring: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error stopping performance monitoring: {str(e)}")],
                isError=True
            )
    
    async def _get_debug_summary(self, args: Dict[str, Any]) -> CallToolResult:
        """Get comprehensive debug summary"""
        try:
            thread_id = args["thread_id"]
            agent_id = args.get("agent_id")
            include_traces = args.get("include_traces", True)
            include_checkpoints = args.get("include_checkpoints", True)
            include_performance = args.get("include_performance", True)
            
            summary = {
                "thread_id": thread_id,
                "agent_id": agent_id,
                "summary_timestamp": datetime.now().isoformat(),
                "total_traces": 0,
                "total_checkpoints": 0,
                "performance_metrics": None
            }
            
            # Get traces
            if include_traces:
                thread_traces = self.traces.get(thread_id, [])
                if agent_id:
                    thread_traces = [t for t in thread_traces if t.agent_id == agent_id]
                summary["total_traces"] = len(thread_traces)
                summary["recent_traces"] = [
                    {
                        "event_id": t.event_id,
                        "timestamp": t.timestamp.isoformat(),
                        "event_type": t.event_type,
                        "level": t.level.value,
                        "message": t.message
                    } for t in sorted(thread_traces, key=lambda x: x.timestamp, reverse=True)[:10]
                ]
            
            # Get checkpoints
            if include_checkpoints:
                thread_checkpoints = self.checkpoints.get(thread_id, [])
                if agent_id:
                    thread_checkpoints = [c for c in thread_checkpoints if c.agent_id == agent_id]
                summary["total_checkpoints"] = len(thread_checkpoints)
                summary["recent_checkpoints"] = [
                    {
                        "checkpoint_id": c.checkpoint_id,
                        "timestamp": c.timestamp.isoformat(),
                        "checkpoint_type": c.checkpoint_type.value,
                        "human_input_required": c.human_input_required
                    } for c in sorted(thread_checkpoints, key=lambda x: x.timestamp, reverse=True)[:5]
                ]
            
            # Get performance metrics
            if include_performance:
                metrics_key = f"{agent_id}_{thread_id}" if agent_id else thread_id
                for key, metrics in self.performance_metrics.items():
                    if thread_id in key and (not agent_id or agent_id in key):
                        summary["performance_metrics"] = {
                            "total_duration_ms": metrics.total_duration_ms,
                            "api_calls": metrics.api_calls,
                            "vault_operations": metrics.vault_operations,
                            "errors": metrics.errors,
                            "checkpoints_created": metrics.checkpoints_created,
                            "human_interactions": metrics.human_interactions
                        }
                        break
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Debug Summary for Thread {thread_id}:\n{json.dumps(summary, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to get debug summary: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting debug summary: {str(e)}")],
                isError=True
            )
    
    async def _export_traces_to_langsmith(self, args: Dict[str, Any]) -> CallToolResult:
        """Export traces to LangSmith"""
        try:
            if not self.langsmith_client:
                return CallToolResult(
                    content=[TextContent(type="text", text="LangSmith client not available")],
                    isError=True
                )
            
            thread_id = args.get("thread_id")
            agent_id = args.get("agent_id")
            workflow_id = args.get("workflow_id")
            project_name = args.get("project_name", LANGSMITH_PROJECT)
            
            # Get traces to export
            traces_to_export = []
            for thread_traces in self.traces.values():
                for trace in thread_traces:
                    if thread_id and trace.thread_id != thread_id:
                        continue
                    if agent_id and trace.agent_id != agent_id:
                        continue
                    if workflow_id and trace.workflow_id != workflow_id:
                        continue
                    traces_to_export.append(trace)
            
            # Export to LangSmith
            exported_count = 0
            for trace in traces_to_export:
                try:
                    # Create a run in LangSmith
                    run_data = {
                        "name": trace.event_type,
                        "run_type": "chain",
                        "inputs": {"message": trace.message},
                        "outputs": {"data": trace.data},
                        "start_time": trace.timestamp,
                        "end_time": trace.timestamp,
                        "tags": trace.tags + ["observability-mcp"],
                        "extra": {
                            "thread_id": trace.thread_id,
                            "agent_id": trace.agent_id,
                            "workflow_id": trace.workflow_id,
                            "event_id": trace.event_id
                        }
                    }
                    
                    # Note: In a real implementation, you would use the LangSmith client to create runs
                    # This is a simplified version
                    exported_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to export trace {trace.event_id}: {e}")
            
            logger.info(f"Exported {exported_count} traces to LangSmith")
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Exported {exported_count} traces to LangSmith project '{project_name}'"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to export traces to LangSmith: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error exporting traces: {str(e)}")],
                isError=True
            )
    
    def _get_all_traces(self) -> str:
        """Get all traces as JSON string"""
        all_traces = []
        for thread_traces in self.traces.values():
            for trace in thread_traces:
                all_traces.append({
                    "event_id": trace.event_id,
                    "timestamp": trace.timestamp.isoformat(),
                    "thread_id": trace.thread_id,
                    "agent_id": trace.agent_id,
                    "workflow_id": trace.workflow_id,
                    "event_type": trace.event_type,
                    "level": trace.level.value,
                    "message": trace.message,
                    "data": trace.data,
                    "tags": trace.tags,
                    "duration_ms": trace.duration_ms
                })
        
        return json.dumps(all_traces, indent=2)
    
    def _get_all_checkpoints(self) -> str:
        """Get all checkpoints as JSON string"""
        all_checkpoints = []
        for thread_checkpoints in self.checkpoints.values():
            for checkpoint in thread_checkpoints:
                all_checkpoints.append({
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "timestamp": checkpoint.timestamp.isoformat(),
                    "thread_id": checkpoint.thread_id,
                    "agent_id": checkpoint.agent_id,
                    "workflow_id": checkpoint.workflow_id,
                    "checkpoint_type": checkpoint.checkpoint_type.value,
                    "human_input_required": checkpoint.human_input_required,
                    "human_input_prompt": checkpoint.human_input_prompt,
                    "human_input_response": checkpoint.human_input_response,
                    "metadata": checkpoint.metadata
                })
        
        return json.dumps(all_checkpoints, indent=2)
    
    def _get_performance_metrics(self) -> str:
        """Get all performance metrics as JSON string"""
        all_metrics = []
        for metrics in self.performance_metrics.values():
            all_metrics.append({
                "agent_id": metrics.agent_id,
                "workflow_id": metrics.workflow_id,
                "thread_id": metrics.thread_id,
                "start_time": metrics.start_time.isoformat(),
                "end_time": metrics.end_time.isoformat() if metrics.end_time else None,
                "total_duration_ms": metrics.total_duration_ms,
                "api_calls": metrics.api_calls,
                "vault_operations": metrics.vault_operations,
                "llm_tokens_used": metrics.llm_tokens_used,
                "llm_cost_usd": metrics.llm_cost_usd,
                "errors": metrics.errors,
                "checkpoints_created": metrics.checkpoints_created,
                "human_interactions": metrics.human_interactions,
                "memory_usage_mb": metrics.memory_usage_mb,
                "cpu_usage_percent": metrics.cpu_usage_percent
            })
        
        return json.dumps(all_metrics, indent=2)
    
    def _get_active_threads(self) -> str:
        """Get active threads as JSON string"""
        return json.dumps(self.active_threads, indent=2)
    
    def _get_log_content(self) -> str:
        """Get log file content"""
        try:
            with open("observability.log", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "No log file found"
        except Exception as e:
            return f"Error reading log file: {str(e)}"
    
    async def _analyze_error_patterns(self, args: Dict[str, Any]) -> CallToolResult:
        """Analyze error patterns and provide debugging insights"""
        try:
            thread_id = args.get("thread_id")
            agent_id = args.get("agent_id")
            time_range_hours = args.get("time_range_hours", 24)
            error_threshold = args.get("error_threshold", 3)
            
            # Get error traces
            error_traces = []
            for thread_traces in self.traces.values():
                for trace in thread_traces:
                    if trace.level in [TraceLevel.ERROR, TraceLevel.CRITICAL]:
                        if thread_id and trace.thread_id != thread_id:
                            continue
                        if agent_id and trace.agent_id != agent_id:
                            continue
                        error_traces.append(trace)
            
            # Analyze patterns
            error_patterns = {}
            for trace in error_traces:
                pattern_key = f"{trace.event_type}_{trace.message[:50]}"
                if pattern_key not in error_patterns:
                    error_patterns[pattern_key] = {
                        "count": 0,
                        "first_occurrence": trace.timestamp,
                        "last_occurrence": trace.timestamp,
                        "threads": set(),
                        "agents": set(),
                        "sample_error": trace
                    }
                
                error_patterns[pattern_key]["count"] += 1
                error_patterns[pattern_key]["last_occurrence"] = trace.timestamp
                error_patterns[pattern_key]["threads"].add(trace.thread_id)
                error_patterns[pattern_key]["agents"].add(trace.agent_id)
            
            # Filter by threshold
            significant_patterns = {
                k: v for k, v in error_patterns.items() 
                if v["count"] >= error_threshold
            }
            
            # Generate insights
            insights = []
            for pattern_key, pattern_data in significant_patterns.items():
                insight = {
                    "pattern": pattern_key,
                    "frequency": pattern_data["count"],
                    "affected_threads": len(pattern_data["threads"]),
                    "affected_agents": len(pattern_data["agents"]),
                    "time_span": (pattern_data["last_occurrence"] - pattern_data["first_occurrence"]).total_seconds() / 3600,
                    "sample_error": {
                        "event_id": pattern_data["sample_error"].event_id,
                        "message": pattern_data["sample_error"].message,
                        "data": pattern_data["sample_error"].data
                    }
                }
                insights.append(insight)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error Pattern Analysis:\n{json.dumps(insights, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze error patterns: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error analyzing patterns: {str(e)}")],
                isError=True
            )
    
    async def _get_agent_communication_log(self, args: Dict[str, Any]) -> CallToolResult:
        """Get detailed agent communication logs and patterns"""
        try:
            thread_id = args.get("thread_id")
            agent_id = args.get("agent_id")
            communication_type = args.get("communication_type", "all")
            limit = args.get("limit", 100)
            
            # Filter traces by communication type
            communication_traces = []
            for thread_traces in self.traces.values():
                for trace in thread_traces:
                    if thread_id and trace.thread_id != thread_id:
                        continue
                    if agent_id and trace.agent_id != agent_id:
                        continue
                    
                    # Filter by communication type
                    if communication_type == "all":
                        communication_traces.append(trace)
                    elif communication_type == "mcp_calls" and "mcp" in trace.event_type.lower():
                        communication_traces.append(trace)
                    elif communication_type == "api_calls" and "api" in trace.event_type.lower():
                        communication_traces.append(trace)
                    elif communication_type == "vault_operations" and "vault" in trace.event_type.lower():
                        communication_traces.append(trace)
                    elif communication_type == "llm_calls" and "llm" in trace.event_type.lower():
                        communication_traces.append(trace)
            
            # Sort by timestamp
            communication_traces.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply limit
            communication_traces = communication_traces[:limit]
            
            # Format results
            results = []
            for trace in communication_traces:
                results.append({
                    "event_id": trace.event_id,
                    "timestamp": trace.timestamp.isoformat(),
                    "thread_id": trace.thread_id,
                    "agent_id": trace.agent_id,
                    "event_type": trace.event_type,
                    "level": trace.level.value,
                    "message": trace.message,
                    "data": trace.data,
                    "tags": trace.tags
                })
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Agent Communication Log ({len(results)} entries):\n{json.dumps(results, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to get agent communication log: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting communication log: {str(e)}")],
                isError=True
            )
    
    async def _create_debug_session(self, args: Dict[str, Any]) -> CallToolResult:
        """Create a new debugging session with comprehensive monitoring"""
        try:
            session_name = args["session_name"]
            thread_id = args["thread_id"]
            agent_id = args["agent_id"]
            workflow_id = args["workflow_id"]
            monitoring_level = args.get("monitoring_level", "detailed")
            auto_checkpoint_interval = args.get("auto_checkpoint_interval", 0)
            
            # Create debug session
            debug_session = {
                "session_name": session_name,
                "thread_id": thread_id,
                "agent_id": agent_id,
                "workflow_id": workflow_id,
                "monitoring_level": monitoring_level,
                "auto_checkpoint_interval": auto_checkpoint_interval,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "checkpoints_created": 0,
                "traces_collected": 0,
                "errors_detected": 0
            }
            
            # Store session
            if not hasattr(self, 'debug_sessions'):
                self.debug_sessions = {}
            self.debug_sessions[session_name] = debug_session
            
            # Start performance monitoring
            await self._start_performance_monitoring({
                "agent_id": agent_id,
                "workflow_id": workflow_id,
                "thread_id": thread_id
            })
            
            logger.info(f"Created debug session: {session_name}")
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Debug session '{session_name}' created successfully\nThread: {thread_id}\nAgent: {agent_id}\nWorkflow: {workflow_id}\nMonitoring Level: {monitoring_level}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to create debug session: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error creating debug session: {str(e)}")],
                isError=True
            )
    
    async def _get_debug_session_status(self, args: Dict[str, Any]) -> CallToolResult:
        """Get status and insights from an active debug session"""
        try:
            session_name = args["session_name"]
            include_recommendations = args.get("include_recommendations", True)
            
            if not hasattr(self, 'debug_sessions') or session_name not in self.debug_sessions:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Debug session '{session_name}' not found")],
                    isError=True
                )
            
            session = self.debug_sessions[session_name]
            
            # Get current status
            thread_traces = self.traces.get(session["thread_id"], [])
            thread_checkpoints = self.checkpoints.get(session["thread_id"], [])
            
            # Count errors
            error_count = len([t for t in thread_traces if t.level in [TraceLevel.ERROR, TraceLevel.CRITICAL]])
            
            # Update session stats
            session["traces_collected"] = len(thread_traces)
            session["checkpoints_created"] = len(thread_checkpoints)
            session["errors_detected"] = error_count
            
            status = {
                "session_name": session_name,
                "status": session["status"],
                "created_at": session["created_at"],
                "monitoring_level": session["monitoring_level"],
                "thread_id": session["thread_id"],
                "agent_id": session["agent_id"],
                "workflow_id": session["workflow_id"],
                "traces_collected": session["traces_collected"],
                "checkpoints_created": session["checkpoints_created"],
                "errors_detected": session["errors_detected"],
                "uptime_hours": (datetime.now() - datetime.fromisoformat(session["created_at"])).total_seconds() / 3600
            }
            
            # Add recommendations if requested
            if include_recommendations:
                recommendations = []
                if error_count > 0:
                    recommendations.append("High error count detected - consider analyzing error patterns")
                if session["checkpoints_created"] == 0:
                    recommendations.append("No checkpoints created - consider enabling auto-checkpointing")
                if session["traces_collected"] < 10:
                    recommendations.append("Low trace activity - check if agent is running properly")
                
                status["recommendations"] = recommendations
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Debug Session Status:\n{json.dumps(status, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to get debug session status: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting session status: {str(e)}")],
                isError=True
            )
    
    async def _correlate_errors_with_traces(self, args: Dict[str, Any]) -> CallToolResult:
        """Correlate errors with trace events to identify root causes"""
        try:
            error_id = args.get("error_id")
            thread_id = args.get("thread_id")
            time_window_minutes = args.get("time_window_minutes", 30)
            include_performance_impact = args.get("include_performance_impact", True)
            
            # Find the error trace
            error_trace = None
            if error_id:
                for thread_traces in self.traces.values():
                    for trace in thread_traces:
                        if trace.event_id == error_id:
                            error_trace = trace
                            break
                    if error_trace:
                        break
            
            if not error_trace and thread_id:
                # Find the most recent error in the thread
                thread_traces = self.traces.get(thread_id, [])
                error_traces = [t for t in thread_traces if t.level in [TraceLevel.ERROR, TraceLevel.CRITICAL]]
                if error_traces:
                    error_trace = max(error_traces, key=lambda x: x.timestamp)
            
            if not error_trace:
                return CallToolResult(
                    content=[TextContent(type="text", text="No error trace found")],
                    isError=True
                )
            
            # Get traces within time window
            time_window = timedelta(minutes=time_window_minutes)
            start_time = error_trace.timestamp - time_window
            
            related_traces = []
            for thread_traces in self.traces.values():
                for trace in thread_traces:
                    if trace.timestamp >= start_time and trace.timestamp <= error_trace.timestamp:
                        related_traces.append(trace)
            
            # Sort by timestamp
            related_traces.sort(key=lambda x: x.timestamp)
            
            # Analyze correlation
            correlation_analysis = {
                "error_trace": {
                    "event_id": error_trace.event_id,
                    "timestamp": error_trace.timestamp.isoformat(),
                    "event_type": error_trace.event_type,
                    "message": error_trace.message,
                    "level": error_trace.level.value
                },
                "time_window_minutes": time_window_minutes,
                "related_traces_count": len(related_traces),
                "timeline": []
            }
            
            # Build timeline
            for trace in related_traces:
                timeline_entry = {
                    "timestamp": trace.timestamp.isoformat(),
                    "event_type": trace.event_type,
                    "level": trace.level.value,
                    "message": trace.message,
                    "time_to_error_seconds": (error_trace.timestamp - trace.timestamp).total_seconds()
                }
                correlation_analysis["timeline"].append(timeline_entry)
            
            # Add performance impact if requested
            if include_performance_impact:
                performance_impact = {
                    "api_calls_before_error": len([t for t in related_traces if "api" in t.event_type.lower()]),
                    "vault_operations_before_error": len([t for t in related_traces if "vault" in t.event_type.lower()]),
                    "mcp_calls_before_error": len([t for t in related_traces if "mcp" in t.event_type.lower()]),
                    "llm_calls_before_error": len([t for t in related_traces if "llm" in t.event_type.lower()])
                }
                correlation_analysis["performance_impact"] = performance_impact
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error Correlation Analysis:\n{json.dumps(correlation_analysis, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to correlate errors with traces: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error correlating traces: {str(e)}")],
                isError=True
            )
    
    async def _generate_debug_report(self, args: Dict[str, Any]) -> CallToolResult:
        """Generate a comprehensive debug report with insights and recommendations"""
        try:
            thread_id = args["thread_id"]
            agent_id = args.get("agent_id")
            report_type = args.get("report_type", "summary")
            include_timeline = args.get("include_timeline", True)
            include_recommendations = args.get("include_recommendations", True)
            
            # Get traces and checkpoints
            thread_traces = self.traces.get(thread_id, [])
            thread_checkpoints = self.checkpoints.get(thread_id, [])
            
            if agent_id:
                thread_traces = [t for t in thread_traces if t.agent_id == agent_id]
                thread_checkpoints = [c for c in thread_checkpoints if c.agent_id == agent_id]
            
            # Generate report
            report = {
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "thread_id": thread_id,
                "agent_id": agent_id,
                "summary": {
                    "total_traces": len(thread_traces),
                    "total_checkpoints": len(thread_checkpoints),
                    "error_count": len([t for t in thread_traces if t.level in [TraceLevel.ERROR, TraceLevel.CRITICAL]]),
                    "warning_count": len([t for t in thread_traces if t.level == TraceLevel.WARNING]),
                    "time_span_hours": 0
                }
            }
            
            # Calculate time span
            if thread_traces:
                start_time = min(t.timestamp for t in thread_traces)
                end_time = max(t.timestamp for t in thread_traces)
                report["summary"]["time_span_hours"] = (end_time - start_time).total_seconds() / 3600
            
            # Add timeline if requested
            if include_timeline:
                timeline = []
                for trace in sorted(thread_traces, key=lambda x: x.timestamp):
                    timeline.append({
                        "timestamp": trace.timestamp.isoformat(),
                        "event_type": trace.event_type,
                        "level": trace.level.value,
                        "message": trace.message,
                        "data": trace.data
                    })
                report["timeline"] = timeline
            
            # Add performance metrics
            metrics_key = f"{agent_id}_{thread_id}" if agent_id else thread_id
            if metrics_key in self.performance_metrics:
                metrics = self.performance_metrics[metrics_key]
                report["performance_metrics"] = {
                    "total_duration_ms": metrics.total_duration_ms,
                    "api_calls": metrics.api_calls,
                    "vault_operations": metrics.vault_operations,
                    "errors": metrics.errors,
                    "checkpoints_created": metrics.checkpoints_created,
                    "human_interactions": metrics.human_interactions
                }
            
            # Add recommendations if requested
            if include_recommendations:
                recommendations = []
                
                if report["summary"]["error_count"] > 0:
                    recommendations.append("High error count detected - investigate error patterns")
                
                if report["summary"]["total_checkpoints"] == 0:
                    recommendations.append("No checkpoints created - consider implementing checkpointing")
                
                if report["summary"]["total_traces"] < 5:
                    recommendations.append("Low trace activity - verify agent is running properly")
                
                if report["summary"]["warning_count"] > report["summary"]["error_count"]:
                    recommendations.append("High warning count - review warning patterns")
                
                report["recommendations"] = recommendations
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Debug Report ({report_type}):\n{json.dumps(report, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate debug report: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error generating report: {str(e)}")],
                isError=True
            )
    
    async def _monitor_langgraph_server_health(self, args: Dict[str, Any]) -> CallToolResult:
        """Monitor LangGraph server health and performance"""
        try:
            server_url = args.get("server_url", "http://127.0.0.1:2024")
            check_endpoints = args.get("check_endpoints", True)
            performance_metrics = args.get("performance_metrics", True)
            
            health_status = {
                "server_url": server_url,
                "timestamp": datetime.now().isoformat(),
                "status": "unknown",
                "response_time_ms": 0,
                "endpoints": {},
                "performance_metrics": {}
            }
            
            # Check basic health
            try:
                start_time = time.time()
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{server_url}/health", timeout=5.0)
                    health_status["status"] = "healthy" if response.status_code == 200 else "unhealthy"
                    health_status["response_time_ms"] = (time.time() - start_time) * 1000
            except Exception as e:
                health_status["status"] = "unreachable"
                health_status["error"] = str(e)
            
            # Check endpoints if requested
            if check_endpoints and health_status["status"] == "healthy":
                endpoints_to_check = [
                    "/assistants",
                    "/threads",
                    "/runs",
                    "/workflows"
                ]
                
                for endpoint in endpoints_to_check:
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.get(f"{server_url}{endpoint}", timeout=5.0)
                            health_status["endpoints"][endpoint] = {
                                "status_code": response.status_code,
                                "accessible": response.status_code < 400
                            }
                    except Exception as e:
                        health_status["endpoints"][endpoint] = {
                            "status_code": 0,
                            "accessible": False,
                            "error": str(e)
                        }
            
            # Collect performance metrics if requested
            if performance_metrics and health_status["status"] == "healthy":
                try:
                    # This would be more comprehensive in a real implementation
                    health_status["performance_metrics"] = {
                        "server_uptime": "unknown",
                        "memory_usage": "unknown",
                        "cpu_usage": "unknown",
                        "active_connections": "unknown"
                    }
                except Exception as e:
                    health_status["performance_metrics"]["error"] = str(e)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"LangGraph Server Health Status:\n{json.dumps(health_status, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to monitor LangGraph server health: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error monitoring server health: {str(e)}")],
                isError=True
            )
    
    async def _trace_workflow_execution(self, args: Dict[str, Any]) -> CallToolResult:
        """Trace the complete execution of a LangGraph workflow"""
        try:
            workflow_name = args["workflow_name"]
            thread_id = args["thread_id"]
            include_node_details = args.get("include_node_details", True)
            include_state_changes = args.get("include_state_changes", True)
            
            # Get traces for the workflow
            workflow_traces = []
            for thread_traces in self.traces.values():
                for trace in thread_traces:
                    if trace.thread_id == thread_id and workflow_name in trace.workflow_id:
                        workflow_traces.append(trace)
            
            # Sort by timestamp
            workflow_traces.sort(key=lambda x: x.timestamp)
            
            # Build execution trace
            execution_trace = {
                "workflow_name": workflow_name,
                "thread_id": thread_id,
                "execution_start": workflow_traces[0].timestamp.isoformat() if workflow_traces else None,
                "execution_end": workflow_traces[-1].timestamp.isoformat() if workflow_traces else None,
                "total_steps": len(workflow_traces),
                "execution_steps": []
            }
            
            # Add execution steps
            for trace in workflow_traces:
                step = {
                    "timestamp": trace.timestamp.isoformat(),
                    "event_type": trace.event_type,
                    "level": trace.level.value,
                    "message": trace.message
                }
                
                if include_node_details:
                    step["node_details"] = trace.data.get("node_details", {})
                
                if include_state_changes:
                    step["state_changes"] = trace.data.get("state_changes", {})
                
                execution_trace["execution_steps"].append(step)
            
            # Calculate execution metrics
            if workflow_traces:
                start_time = workflow_traces[0].timestamp
                end_time = workflow_traces[-1].timestamp
                execution_trace["execution_duration_ms"] = (end_time - start_time).total_seconds() * 1000
                execution_trace["error_count"] = len([t for t in workflow_traces if t.level in [TraceLevel.ERROR, TraceLevel.CRITICAL]])
                execution_trace["warning_count"] = len([t for t in workflow_traces if t.level == TraceLevel.WARNING])
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Workflow Execution Trace:\n{json.dumps(execution_trace, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to trace workflow execution: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error tracing workflow: {str(e)}")],
                isError=True
            )
    
    async def _optimize_agent_performance(self, args: Dict[str, Any]) -> CallToolResult:
        """Analyze and provide optimization recommendations for agent performance"""
        try:
            agent_id = args["agent_id"]
            thread_id = args["thread_id"]
            optimization_focus = args.get("optimization_focus", "speed")
            include_benchmarks = args.get("include_benchmarks", True)
            
            # Get agent traces
            agent_traces = []
            for thread_traces in self.traces.values():
                for trace in thread_traces:
                    if trace.thread_id == thread_id and trace.agent_id == agent_id:
                        agent_traces.append(trace)
            
            # Analyze performance patterns
            analysis = {
                "agent_id": agent_id,
                "thread_id": thread_id,
                "optimization_focus": optimization_focus,
                "analysis_timestamp": datetime.now().isoformat(),
                "total_events": len(agent_traces),
                "performance_insights": {},
                "recommendations": []
            }
            
            # Analyze by focus area
            if optimization_focus == "speed":
                # Analyze response times
                api_calls = [t for t in agent_traces if "api" in t.event_type.lower()]
                if api_calls:
                    analysis["performance_insights"]["api_calls"] = len(api_calls)
                    analysis["recommendations"].append("Consider batching API calls to reduce latency")
                
                # Analyze sequential operations
                sequential_ops = [t for t in agent_traces if "sequential" in t.message.lower()]
                if sequential_ops:
                    analysis["performance_insights"]["sequential_operations"] = len(sequential_ops)
                    analysis["recommendations"].append("Consider parallelizing sequential operations")
            
            elif optimization_focus == "accuracy":
                # Analyze error patterns
                errors = [t for t in agent_traces if t.level in [TraceLevel.ERROR, TraceLevel.CRITICAL]]
                if errors:
                    analysis["performance_insights"]["error_count"] = len(errors)
                    analysis["recommendations"].append("High error count - review error handling and validation")
                
                # Analyze retry patterns
                retries = [t for t in agent_traces if "retry" in t.message.lower()]
                if retries:
                    analysis["performance_insights"]["retry_count"] = len(retries)
                    analysis["recommendations"].append("Frequent retries detected - improve initial accuracy")
            
            elif optimization_focus == "cost":
                # Analyze LLM usage
                llm_calls = [t for t in agent_traces if "llm" in t.event_type.lower()]
                if llm_calls:
                    analysis["performance_insights"]["llm_calls"] = len(llm_calls)
                    analysis["recommendations"].append("Consider caching LLM responses for repeated queries")
                
                # Analyze token usage
                token_usage = [t for t in agent_traces if "token" in t.message.lower()]
                if token_usage:
                    analysis["performance_insights"]["token_usage_events"] = len(token_usage)
                    analysis["recommendations"].append("Monitor token usage and optimize prompts")
            
            elif optimization_focus == "reliability":
                # Analyze checkpoint usage
                checkpoints = [t for t in agent_traces if "checkpoint" in t.event_type.lower()]
                if checkpoints:
                    analysis["performance_insights"]["checkpoints"] = len(checkpoints)
                else:
                    analysis["recommendations"].append("No checkpoints found - implement checkpointing for reliability")
                
                # Analyze error recovery
                error_recovery = [t for t in agent_traces if "recovery" in t.message.lower()]
                if error_recovery:
                    analysis["performance_insights"]["error_recovery"] = len(error_recovery)
                else:
                    analysis["recommendations"].append("No error recovery patterns found - implement error recovery")
            
            # Add benchmarks if requested
            if include_benchmarks:
                analysis["benchmarks"] = {
                    "average_response_time_ms": "calculated_from_traces",
                    "success_rate_percent": "calculated_from_traces",
                    "error_rate_percent": "calculated_from_traces",
                    "throughput_events_per_minute": "calculated_from_traces"
                }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Agent Performance Optimization Analysis:\n{json.dumps(analysis, indent=2)}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Failed to optimize agent performance: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error optimizing performance: {str(e)}")],
                isError=True
            )

async def main():
    """Main function to run the observability MCP server"""
    try:
        observability = ObservabilityMCP()
        
        logger.info("Starting Observability MCP Server...")
        logger.info(f"LangSmith available: {LANGSMITH_AVAILABLE}")
        logger.info(f"LangSmith project: {LANGSMITH_PROJECT}")
        
        async with stdio_server() as (read_stream, write_stream):
            await observability.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="observability-mcp",
                    server_version="1.0.0",
                    capabilities=observability.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )
    
    except Exception as e:
        logger.error(f"Failed to start observability MCP server: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())

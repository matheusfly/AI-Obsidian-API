"""
AI Agent Observability Enhancement System
Comprehensive monitoring and tracking for AI agents and workflows
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import aiohttp
import asyncpg
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, start_http_server
import openai
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"

class InteractionType(Enum):
    USER_QUERY = "user_query"
    SYSTEM_TASK = "system_task"
    AGENT_COLLABORATION = "agent_collaboration"
    TOOL_CALL = "tool_call"
    MODEL_INFERENCE = "model_inference"

@dataclass
class AgentMetrics:
    agent_id: str
    agent_name: str
    status: AgentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    token_usage: Dict[str, int] = None
    model_calls: int = 0
    tool_calls: int = 0
    error_count: int = 0
    success_count: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    interaction_type: InteractionType = InteractionType.USER_QUERY
    context_size: int = 0
    response_quality_score: float = 0.0
    user_satisfaction: Optional[float] = None

@dataclass
class WorkflowMetrics:
    workflow_id: str
    workflow_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_ms: Optional[float] = None
    agent_count: int = 0
    successful_agents: int = 0
    failed_agents: int = 0
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    complexity_score: float = 0.0
    efficiency_score: float = 0.0

class AIAgentObservability:
    """Enhanced AI Agent Observability System"""
    
    def __init__(self, 
                 prometheus_port: int = 8000,
                 database_url: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        self.prometheus_port = prometheus_port
        self.database_url = database_url
        self.openai_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        
        # Prometheus metrics
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
        # In-memory storage for real-time metrics
        self.active_agents: Dict[str, AgentMetrics] = {}
        self.agent_history: List[AgentMetrics] = []
        self.workflow_metrics: Dict[str, WorkflowMetrics] = {}
        
        # Performance tracking
        self.performance_cache = {}
        self.alert_thresholds = {
            'response_time_ms': 5000,
            'error_rate_percent': 5.0,
            'memory_usage_mb': 1000,
            'cpu_usage_percent': 80.0
        }
        
        logger.info("AI Agent Observability System initialized")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for AI agent monitoring"""
        
        # Agent metrics
        self.agent_counter = Counter(
            'ai_agent_total_requests',
            'Total number of AI agent requests',
            ['agent_name', 'status', 'interaction_type'],
            registry=self.registry
        )
        
        self.agent_duration = Histogram(
            'ai_agent_request_duration_seconds',
            'Duration of AI agent requests in seconds',
            ['agent_name', 'interaction_type'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )
        
        self.agent_tokens = Counter(
            'ai_agent_tokens_total',
            'Total tokens used by AI agents',
            ['agent_name', 'token_type'],
            registry=self.registry
        )
        
        self.agent_errors = Counter(
            'ai_agent_errors_total',
            'Total errors from AI agents',
            ['agent_name', 'error_type'],
            registry=self.registry
        )
        
        # System metrics
        self.agent_memory_usage = Gauge(
            'ai_agent_memory_usage_bytes',
            'Memory usage of AI agents in bytes',
            ['agent_name'],
            registry=self.registry
        )
        
        self.agent_cpu_usage = Gauge(
            'ai_agent_cpu_usage_percent',
            'CPU usage of AI agents in percent',
            ['agent_name'],
            registry=self.registry
        )
        
        # Workflow metrics
        self.workflow_duration = Histogram(
            'ai_workflow_duration_seconds',
            'Duration of AI workflows in seconds',
            ['workflow_name'],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0],
            registry=self.registry
        )
        
        self.workflow_agents = Gauge(
            'ai_workflow_agent_count',
            'Number of agents in workflow',
            ['workflow_name'],
            registry=self.registry
        )
        
        # Quality metrics
        self.response_quality = Histogram(
            'ai_agent_response_quality_score',
            'Quality score of AI agent responses',
            ['agent_name'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )
        
        self.user_satisfaction = Histogram(
            'ai_agent_user_satisfaction_score',
            'User satisfaction score for AI agent responses',
            ['agent_name'],
            buckets=[1.0, 2.0, 3.0, 4.0, 5.0],
            registry=self.registry
        )
    
    async def start_agent_session(self, 
                                agent_id: str, 
                                agent_name: str,
                                interaction_type: InteractionType = InteractionType.USER_QUERY,
                                context_size: int = 0) -> AgentMetrics:
        """Start monitoring a new AI agent session"""
        
        agent_metrics = AgentMetrics(
            agent_id=agent_id,
            agent_name=agent_name,
            status=AgentStatus.PROCESSING,
            start_time=datetime.utcnow(),
            interaction_type=interaction_type,
            context_size=context_size,
            token_usage={},
            memory_usage_mb=psutil.Process().memory_info().rss / 1024 / 1024,
            cpu_usage_percent=psutil.Process().cpu_percent()
        )
        
        self.active_agents[agent_id] = agent_metrics
        
        # Update Prometheus metrics
        self.agent_counter.labels(
            agent_name=agent_name,
            status=agent_metrics.status.value,
            interaction_type=interaction_type.value
        ).inc()
        
        logger.info(f"Started monitoring agent session: {agent_id} ({agent_name})")
        return agent_metrics
    
    async def update_agent_metrics(self, 
                                 agent_id: str,
                                 status: Optional[AgentStatus] = None,
                                 token_usage: Optional[Dict[str, int]] = None,
                                 model_calls: Optional[int] = None,
                                 tool_calls: Optional[int] = None,
                                 error_count: Optional[int] = None,
                                 success_count: Optional[int] = None,
                                 response_quality_score: Optional[float] = None,
                                 user_satisfaction: Optional[float] = None):
        """Update metrics for an active agent session"""
        
        if agent_id not in self.active_agents:
            logger.warning(f"Agent {agent_id} not found in active agents")
            return
        
        agent = self.active_agents[agent_id]
        
        if status:
            agent.status = status
            self.agent_counter.labels(
                agent_name=agent.agent_name,
                status=status.value,
                interaction_type=agent.interaction_type.value
            ).inc()
        
        if token_usage:
            agent.token_usage.update(token_usage)
            for token_type, count in token_usage.items():
                self.agent_tokens.labels(
                    agent_name=agent.agent_name,
                    token_type=token_type
                ).inc(count)
        
        if model_calls is not None:
            agent.model_calls += model_calls
        
        if tool_calls is not None:
            agent.tool_calls += tool_calls
        
        if error_count is not None:
            agent.error_count += error_count
            self.agent_errors.labels(
                agent_name=agent.agent_name,
                error_type="general"
            ).inc(error_count)
        
        if success_count is not None:
            agent.success_count += success_count
        
        if response_quality_score is not None:
            agent.response_quality_score = response_quality_score
            self.response_quality.labels(
                agent_name=agent.agent_name
            ).observe(response_quality_score)
        
        if user_satisfaction is not None:
            agent.user_satisfaction = user_satisfaction
            self.user_satisfaction.labels(
                agent_name=agent.agent_name
            ).observe(user_satisfaction)
        
        # Update system metrics
        agent.memory_usage_mb = psutil.Process().memory_info().rss / 1024 / 1024
        agent.cpu_usage_percent = psutil.Process().cpu_percent()
        
        self.agent_memory_usage.labels(agent_name=agent.agent_name).set(agent.memory_usage_mb * 1024 * 1024)
        self.agent_cpu_usage.labels(agent_name=agent.agent_name).set(agent.cpu_usage_percent)
    
    async def end_agent_session(self, agent_id: str, final_status: AgentStatus = AgentStatus.COMPLETED):
        """End monitoring for an AI agent session"""
        
        if agent_id not in self.active_agents:
            logger.warning(f"Agent {agent_id} not found in active agents")
            return
        
        agent = self.active_agents[agent_id]
        agent.status = final_status
        agent.end_time = datetime.utcnow()
        agent.duration_ms = (agent.end_time - agent.start_time).total_seconds() * 1000
        
        # Update Prometheus metrics
        self.agent_duration.labels(
            agent_name=agent.agent_name,
            interaction_type=agent.interaction_type.value
        ).observe(agent.duration_ms / 1000)
        
        # Move to history
        self.agent_history.append(agent)
        del self.active_agents[agent_id]
        
        logger.info(f"Ended monitoring agent session: {agent_id} (Duration: {agent.duration_ms:.2f}ms)")
        return agent
    
    async def start_workflow_session(self, 
                                   workflow_id: str, 
                                   workflow_name: str,
                                   agent_count: int = 0) -> WorkflowMetrics:
        """Start monitoring a new AI workflow session"""
        
        workflow_metrics = WorkflowMetrics(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            start_time=datetime.utcnow(),
            agent_count=agent_count
        )
        
        self.workflow_metrics[workflow_id] = workflow_metrics
        
        logger.info(f"Started monitoring workflow: {workflow_id} ({workflow_name})")
        return workflow_metrics
    
    async def update_workflow_metrics(self, 
                                    workflow_id: str,
                                    successful_agents: Optional[int] = None,
                                    failed_agents: Optional[int] = None,
                                    total_tokens_used: Optional[int] = None,
                                    total_cost_usd: Optional[float] = None,
                                    complexity_score: Optional[float] = None,
                                    efficiency_score: Optional[float] = None):
        """Update metrics for an active workflow session"""
        
        if workflow_id not in self.workflow_metrics:
            logger.warning(f"Workflow {workflow_id} not found in active workflows")
            return
        
        workflow = self.workflow_metrics[workflow_id]
        
        if successful_agents is not None:
            workflow.successful_agents = successful_agents
        
        if failed_agents is not None:
            workflow.failed_agents = failed_agents
        
        if total_tokens_used is not None:
            workflow.total_tokens_used = total_tokens_used
        
        if total_cost_usd is not None:
            workflow.total_cost_usd = total_cost_usd
        
        if complexity_score is not None:
            workflow.complexity_score = complexity_score
        
        if efficiency_score is not None:
            workflow.efficiency_score = efficiency_score
    
    async def end_workflow_session(self, workflow_id: str):
        """End monitoring for an AI workflow session"""
        
        if workflow_id not in self.workflow_metrics:
            logger.warning(f"Workflow {workflow_id} not found in active workflows")
            return
        
        workflow = self.workflow_metrics[workflow_id]
        workflow.end_time = datetime.utcnow()
        workflow.total_duration_ms = (workflow.end_time - workflow.start_time).total_seconds() * 1000
        
        # Update Prometheus metrics
        self.workflow_duration.labels(
            workflow_name=workflow.workflow_name
        ).observe(workflow.total_duration_ms / 1000)
        
        self.workflow_agents.labels(
            workflow_name=workflow.workflow_name
        ).set(workflow.agent_count)
        
        logger.info(f"Ended monitoring workflow: {workflow_id} (Duration: {workflow.total_duration_ms:.2f}ms)")
        return workflow
    
    async def get_agent_performance_summary(self, 
                                          agent_name: Optional[str] = None,
                                          time_window_hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for agents"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Filter agents by time window and optionally by name
        filtered_agents = [
            agent for agent in self.agent_history
            if agent.start_time >= cutoff_time and (agent_name is None or agent.agent_name == agent_name)
        ]
        
        if not filtered_agents:
            return {"message": "No agents found in the specified time window"}
        
        # Calculate summary statistics
        total_agents = len(filtered_agents)
        successful_agents = len([a for a in filtered_agents if a.status == AgentStatus.COMPLETED])
        failed_agents = len([a for a in filtered_agents if a.status == AgentStatus.ERROR])
        
        avg_duration = sum(a.duration_ms or 0 for a in filtered_agents) / total_agents
        avg_tokens = sum(sum(a.token_usage.values()) for a in filtered_agents) / total_agents
        avg_quality = sum(a.response_quality_score for a in filtered_agents if a.response_quality_score > 0) / max(1, len([a for a in filtered_agents if a.response_quality_score > 0]))
        
        return {
            "time_window_hours": time_window_hours,
            "total_agents": total_agents,
            "successful_agents": successful_agents,
            "failed_agents": failed_agents,
            "success_rate": (successful_agents / total_agents) * 100,
            "average_duration_ms": avg_duration,
            "average_tokens_used": avg_tokens,
            "average_quality_score": avg_quality,
            "agents_by_name": self._group_agents_by_name(filtered_agents)
        }
    
    def _group_agents_by_name(self, agents: List[AgentMetrics]) -> Dict[str, Dict[str, Any]]:
        """Group agents by name and calculate statistics"""
        
        grouped = {}
        for agent in agents:
            if agent.agent_name not in grouped:
                grouped[agent.agent_name] = {
                    "total_count": 0,
                    "successful_count": 0,
                    "failed_count": 0,
                    "total_duration_ms": 0,
                    "total_tokens": 0,
                    "quality_scores": []
                }
            
            stats = grouped[agent.agent_name]
            stats["total_count"] += 1
            
            if agent.status == AgentStatus.COMPLETED:
                stats["successful_count"] += 1
            elif agent.status == AgentStatus.ERROR:
                stats["failed_count"] += 1
            
            if agent.duration_ms:
                stats["total_duration_ms"] += agent.duration_ms
            
            stats["total_tokens"] += sum(agent.token_usage.values())
            
            if agent.response_quality_score > 0:
                stats["quality_scores"].append(agent.response_quality_score)
        
        # Calculate averages
        for name, stats in grouped.items():
            if stats["total_count"] > 0:
                stats["success_rate"] = (stats["successful_count"] / stats["total_count"]) * 100
                stats["average_duration_ms"] = stats["total_duration_ms"] / stats["total_count"]
                stats["average_tokens"] = stats["total_tokens"] / stats["total_count"]
                
                if stats["quality_scores"]:
                    stats["average_quality_score"] = sum(stats["quality_scores"]) / len(stats["quality_scores"])
                else:
                    stats["average_quality_score"] = 0
        
        return grouped
    
    async def check_performance_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance alerts and anomalies"""
        
        alerts = []
        current_time = datetime.utcnow()
        
        # Check active agents for performance issues
        for agent_id, agent in self.active_agents.items():
            # Check for long-running agents
            if (current_time - agent.start_time).total_seconds() > 300:  # 5 minutes
                alerts.append({
                    "type": "long_running_agent",
                    "severity": "warning",
                    "agent_id": agent_id,
                    "agent_name": agent.agent_name,
                    "duration_seconds": (current_time - agent.start_time).total_seconds(),
                    "message": f"Agent {agent.agent_name} has been running for {(current_time - agent.start_time).total_seconds():.0f} seconds"
                })
            
            # Check memory usage
            if agent.memory_usage_mb > self.alert_thresholds['memory_usage_mb']:
                alerts.append({
                    "type": "high_memory_usage",
                    "severity": "critical",
                    "agent_id": agent_id,
                    "agent_name": agent.agent_name,
                    "memory_usage_mb": agent.memory_usage_mb,
                    "threshold_mb": self.alert_thresholds['memory_usage_mb'],
                    "message": f"Agent {agent.agent_name} using {agent.memory_usage_mb:.1f}MB memory (threshold: {self.alert_thresholds['memory_usage_mb']}MB)"
                })
            
            # Check CPU usage
            if agent.cpu_usage_percent > self.alert_thresholds['cpu_usage_percent']:
                alerts.append({
                    "type": "high_cpu_usage",
                    "severity": "warning",
                    "agent_id": agent_id,
                    "agent_name": agent.agent_name,
                    "cpu_usage_percent": agent.cpu_usage_percent,
                    "threshold_percent": self.alert_thresholds['cpu_usage_percent'],
                    "message": f"Agent {agent.agent_name} using {agent.cpu_usage_percent:.1f}% CPU (threshold: {self.alert_thresholds['cpu_usage_percent']}%)"
                })
        
        # Check recent agent history for error rates
        recent_agents = [
            agent for agent in self.agent_history
            if (current_time - agent.start_time).total_seconds() < 3600  # Last hour
        ]
        
        if recent_agents:
            error_rate = len([a for a in recent_agents if a.status == AgentStatus.ERROR]) / len(recent_agents) * 100
            
            if error_rate > self.alert_thresholds['error_rate_percent']:
                alerts.append({
                    "type": "high_error_rate",
                    "severity": "critical",
                    "error_rate_percent": error_rate,
                    "threshold_percent": self.alert_thresholds['error_rate_percent'],
                    "total_agents": len(recent_agents),
                    "failed_agents": len([a for a in recent_agents if a.status == AgentStatus.ERROR]),
                    "message": f"High error rate: {error_rate:.1f}% ({len([a for a in recent_agents if a.status == AgentStatus.ERROR])}/{len(recent_agents)} agents failed)"
                })
        
        return alerts
    
    async def export_metrics_to_prometheus(self):
        """Start Prometheus metrics server"""
        
        try:
            start_http_server(self.prometheus_port, registry=self.registry)
            logger.info(f"Prometheus metrics server started on port {self.prometheus_port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus metrics server: {e}")
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for AI agent observability"""
        
        current_time = datetime.utcnow()
        
        # Active agents summary
        active_agents_summary = {
            "total_active": len(self.active_agents),
            "by_status": {},
            "by_interaction_type": {},
            "total_memory_mb": 0,
            "total_cpu_percent": 0
        }
        
        for agent in self.active_agents.values():
            # Count by status
            status = agent.status.value
            active_agents_summary["by_status"][status] = active_agents_summary["by_status"].get(status, 0) + 1
            
            # Count by interaction type
            interaction_type = agent.interaction_type.value
            active_agents_summary["by_interaction_type"][interaction_type] = active_agents_summary["by_interaction_type"].get(interaction_type, 0) + 1
            
            # Sum resource usage
            active_agents_summary["total_memory_mb"] += agent.memory_usage_mb
            active_agents_summary["total_cpu_percent"] += agent.cpu_usage_percent
        
        # Recent performance (last hour)
        recent_agents = [
            agent for agent in self.agent_history
            if (current_time - agent.start_time).total_seconds() < 3600
        ]
        
        recent_performance = {
            "total_requests": len(recent_agents),
            "successful_requests": len([a for a in recent_agents if a.status == AgentStatus.COMPLETED]),
            "failed_requests": len([a for a in recent_agents if a.status == AgentStatus.ERROR]),
            "average_response_time_ms": 0,
            "total_tokens_used": 0,
            "average_quality_score": 0
        }
        
        if recent_agents:
            recent_performance["average_response_time_ms"] = sum(a.duration_ms or 0 for a in recent_agents) / len(recent_agents)
            recent_performance["total_tokens_used"] = sum(sum(a.token_usage.values()) for a in recent_agents)
            
            quality_scores = [a.response_quality_score for a in recent_agents if a.response_quality_score > 0]
            if quality_scores:
                recent_performance["average_quality_score"] = sum(quality_scores) / len(quality_scores)
        
        # Workflow summary
        active_workflows = len(self.workflow_metrics)
        
        return {
            "timestamp": current_time.isoformat(),
            "active_agents": active_agents_summary,
            "recent_performance": recent_performance,
            "active_workflows": active_workflows,
            "alerts": await self.check_performance_alerts()
        }

# Example usage and testing
async def main():
    """Example usage of the AI Agent Observability system"""
    
    # Initialize the observability system
    observability = AIAgentObservability(
        prometheus_port=8001,
        openai_api_key="your-openai-api-key"
    )
    
    # Start Prometheus metrics server
    await observability.export_metrics_to_prometheus()
    
    # Example: Monitor an AI agent session
    agent_id = "agent_001"
    agent_metrics = await observability.start_agent_session(
        agent_id=agent_id,
        agent_name="GPT-4 Assistant",
        interaction_type=InteractionType.USER_QUERY,
        context_size=1500
    )
    
    # Simulate some work
    await asyncio.sleep(2)
    
    # Update metrics during processing
    await observability.update_agent_metrics(
        agent_id=agent_id,
        token_usage={"prompt_tokens": 100, "completion_tokens": 50},
        model_calls=1,
        response_quality_score=0.85
    )
    
    # End the session
    final_metrics = await observability.end_agent_session(agent_id)
    
    # Get performance summary
    summary = await observability.get_agent_performance_summary()
    print("Performance Summary:", json.dumps(summary, indent=2, default=str))
    
    # Get dashboard data
    dashboard_data = await observability.get_dashboard_data()
    print("Dashboard Data:", json.dumps(dashboard_data, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())

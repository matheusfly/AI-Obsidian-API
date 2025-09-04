"""
LangGraph Tracer - Advanced AI Workflow Monitoring with LangSmith Integration
"""

from langgraph import StateGraph
from langsmith import Client
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class TraceStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class CheckpointStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class TraceEvent:
    event_id: str
    trace_id: str
    thread_id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    source: str

@dataclass
class NodeExecution:
    node_id: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    execution_time: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class EdgeTraversal:
    from_node: str
    to_node: str
    condition: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class Checkpoint:
    checkpoint_id: str
    thread_id: str
    trace_id: str
    state: Dict[str, Any]
    description: str
    created_at: datetime
    status: CheckpointStatus
    approver_id: Optional[str]
    approved_at: Optional[datetime]
    expires_at: Optional[datetime]

@dataclass
class Trace:
    trace_id: str
    thread_id: str
    workflow_name: str
    status: TraceStatus
    started_at: datetime
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]
    nodes: List[NodeExecution]
    edges: List[EdgeTraversal]
    checkpoints: List[Checkpoint]

class LangGraphTracer:
    """
    Advanced tracer for LangGraph workflows with LangSmith integration
    """
    
    def __init__(self, langsmith_api_key: str, project_name: str, 
                 elasticsearch_client=None, redis_client=None):
        self.langsmith_client = Client(api_key=langsmith_api_key)
        self.project_name = project_name
        self.elasticsearch = elasticsearch_client
        self.redis = redis_client
        
        # In-memory storage for active traces
        self.active_traces: Dict[str, Trace] = {}
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.trace_events: List[TraceEvent] = []
        
        # Performance metrics
        self.metrics = {
            "traces_created": 0,
            "nodes_executed": 0,
            "edges_traversed": 0,
            "checkpoints_created": 0,
            "average_execution_time": 0.0
        }
    
    async def start_trace(self, thread_id: str, workflow_name: str, 
                         metadata: Dict[str, Any] = None) -> str:
        """
        Start a new trace for a workflow execution
        
        Args:
            thread_id: Unique thread identifier
            workflow_name: Name of the workflow being executed
            metadata: Additional metadata for the trace
            
        Returns:
            trace_id: Unique identifier for the trace
        """
        trace_id = str(uuid.uuid4())
        
        trace = Trace(
            trace_id=trace_id,
            thread_id=thread_id,
            workflow_name=workflow_name,
            status=TraceStatus.ACTIVE,
            started_at=datetime.utcnow(),
            completed_at=None,
            metadata=metadata or {},
            nodes=[],
            edges=[],
            checkpoints=[]
        )
        
        self.active_traces[thread_id] = trace
        self.metrics["traces_created"] += 1
        
        # Log trace creation
        await self._log_event(
            trace_id=trace_id,
            thread_id=thread_id,
            event_type="trace_started",
            data={"workflow_name": workflow_name, "metadata": metadata},
            source="langgraph_tracer"
        )
        
        # Send to LangSmith
        try:
            await self.langsmith_client.create_run(
                name=f"{workflow_name}_trace",
                run_type="chain",
                inputs=metadata or {},
                project_name=self.project_name,
                metadata={"trace_id": trace_id, "thread_id": thread_id}
            )
        except Exception as e:
            logger.error(f"Failed to send trace to LangSmith: {e}")
        
        logger.info(f"Started trace {trace_id} for workflow {workflow_name}")
        return trace_id
    
    async def log_node_execution(self, thread_id: str, node_id: str, 
                                input_data: Dict[str, Any], 
                                output_data: Dict[str, Any],
                                execution_time: float = None,
                                metadata: Dict[str, Any] = None) -> None:
        """
        Log a node execution within a trace
        
        Args:
            thread_id: Thread identifier
            node_id: Node identifier
            input_data: Input data for the node
            output_data: Output data from the node
            execution_time: Time taken to execute the node
            metadata: Additional metadata
        """
        if thread_id not in self.active_traces:
            logger.warning(f"Trace not found for thread {thread_id}")
            return
        
        trace = self.active_traces[thread_id]
        
        node_execution = NodeExecution(
            node_id=node_id,
            input_data=input_data,
            output_data=output_data,
            execution_time=execution_time or 0.0,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        trace.nodes.append(node_execution)
        self.metrics["nodes_executed"] += 1
        
        # Update average execution time
        if execution_time:
            total_time = self.metrics["average_execution_time"] * (self.metrics["nodes_executed"] - 1)
            self.metrics["average_execution_time"] = (total_time + execution_time) / self.metrics["nodes_executed"]
        
        # Log node execution
        await self._log_event(
            trace_id=trace.trace_id,
            thread_id=thread_id,
            event_type="node_executed",
            data={
                "node_id": node_id,
                "execution_time": execution_time,
                "input_size": len(str(input_data)),
                "output_size": len(str(output_data))
            },
            source="langgraph_tracer"
        )
        
        # Send to LangSmith
        try:
            await self.langsmith_client.create_run(
                name=f"{trace.workflow_name}_{node_id}",
                run_type="tool",
                inputs=input_data,
                outputs=output_data,
                project_name=self.project_name,
                metadata={
                    "trace_id": trace.trace_id,
                    "thread_id": thread_id,
                    "node_id": node_id,
                    "execution_time": execution_time
                }
            )
        except Exception as e:
            logger.error(f"Failed to send node execution to LangSmith: {e}")
    
    async def log_edge_traversal(self, thread_id: str, from_node: str, 
                                to_node: str, condition: str = None,
                                metadata: Dict[str, Any] = None) -> None:
        """
        Log an edge traversal within a trace
        
        Args:
            thread_id: Thread identifier
            from_node: Source node
            to_node: Target node
            condition: Condition that triggered the traversal
            metadata: Additional metadata
        """
        if thread_id not in self.active_traces:
            logger.warning(f"Trace not found for thread {thread_id}")
            return
        
        trace = self.active_traces[thread_id]
        
        edge_traversal = EdgeTraversal(
            from_node=from_node,
            to_node=to_node,
            condition=condition,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        trace.edges.append(edge_traversal)
        self.metrics["edges_traversed"] += 1
        
        # Log edge traversal
        await self._log_event(
            trace_id=trace.trace_id,
            thread_id=thread_id,
            event_type="edge_traversed",
            data={
                "from_node": from_node,
                "to_node": to_node,
                "condition": condition
            },
            source="langgraph_tracer"
        )
    
    async def create_checkpoint(self, thread_id: str, state: Dict[str, Any], 
                               description: str = None, 
                               expires_in_minutes: int = 60) -> str:
        """
        Create a checkpoint for human-in-the-loop interactions
        
        Args:
            thread_id: Thread identifier
            state: Current state to checkpoint
            description: Human-readable description
            expires_in_minutes: Checkpoint expiration time
            
        Returns:
            checkpoint_id: Unique identifier for the checkpoint
        """
        if thread_id not in self.active_traces:
            logger.warning(f"Trace not found for thread {thread_id}")
            return None
        
        trace = self.active_traces[thread_id]
        checkpoint_id = str(uuid.uuid4())
        
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            thread_id=thread_id,
            trace_id=trace.trace_id,
            state=state,
            description=description or f"Checkpoint at {datetime.utcnow()}",
            created_at=datetime.utcnow(),
            status=CheckpointStatus.PENDING,
            approver_id=None,
            approved_at=None,
            expires_at=datetime.utcnow().replace(
                minute=datetime.utcnow().minute + expires_in_minutes
            ) if expires_in_minutes else None
        )
        
        trace.checkpoints.append(checkpoint)
        self.checkpoints[checkpoint_id] = checkpoint
        self.metrics["checkpoints_created"] += 1
        
        # Log checkpoint creation
        await self._log_event(
            trace_id=trace.trace_id,
            thread_id=thread_id,
            event_type="checkpoint_created",
            data={
                "checkpoint_id": checkpoint_id,
                "description": description,
                "state_size": len(str(state))
            },
            source="langgraph_tracer"
        )
        
        # Store in Redis for quick access
        if self.redis:
            await self.redis.setex(
                f"checkpoint:{checkpoint_id}",
                expires_in_minutes * 60,
                json.dumps(asdict(checkpoint), default=str)
            )
        
        logger.info(f"Created checkpoint {checkpoint_id} for thread {thread_id}")
        return checkpoint_id
    
    async def restore_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore state from a checkpoint
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            state: Restored state or None if not found
        """
        checkpoint = self.checkpoints.get(checkpoint_id)
        
        if not checkpoint:
            # Try to load from Redis
            if self.redis:
                checkpoint_data = await self.redis.get(f"checkpoint:{checkpoint_id}")
                if checkpoint_data:
                    checkpoint = Checkpoint(**json.loads(checkpoint_data))
                    self.checkpoints[checkpoint_id] = checkpoint
        
        if not checkpoint:
            logger.warning(f"Checkpoint {checkpoint_id} not found")
            return None
        
        if checkpoint.status != CheckpointStatus.APPROVED:
            logger.warning(f"Checkpoint {checkpoint_id} not approved (status: {checkpoint.status})")
            return None
        
        if checkpoint.expires_at and datetime.utcnow() > checkpoint.expires_at:
            logger.warning(f"Checkpoint {checkpoint_id} has expired")
            checkpoint.status = CheckpointStatus.EXPIRED
            return None
        
        # Log checkpoint restoration
        await self._log_event(
            trace_id=checkpoint.trace_id,
            thread_id=checkpoint.thread_id,
            event_type="checkpoint_restored",
            data={"checkpoint_id": checkpoint_id},
            source="langgraph_tracer"
        )
        
        logger.info(f"Restored checkpoint {checkpoint_id}")
        return checkpoint.state
    
    async def approve_checkpoint(self, checkpoint_id: str, approver_id: str) -> bool:
        """
        Approve a checkpoint for restoration
        
        Args:
            checkpoint_id: Checkpoint identifier
            approver_id: ID of the approver
            
        Returns:
            success: Whether the approval was successful
        """
        checkpoint = self.checkpoints.get(checkpoint_id)
        
        if not checkpoint:
            logger.warning(f"Checkpoint {checkpoint_id} not found")
            return False
        
        if checkpoint.status != CheckpointStatus.PENDING:
            logger.warning(f"Checkpoint {checkpoint_id} not pending (status: {checkpoint.status})")
            return False
        
        checkpoint.status = CheckpointStatus.APPROVED
        checkpoint.approver_id = approver_id
        checkpoint.approved_at = datetime.utcnow()
        
        # Log checkpoint approval
        await self._log_event(
            trace_id=checkpoint.trace_id,
            thread_id=checkpoint.thread_id,
            event_type="checkpoint_approved",
            data={
                "checkpoint_id": checkpoint_id,
                "approver_id": approver_id
            },
            source="langgraph_tracer"
        )
        
        logger.info(f"Approved checkpoint {checkpoint_id} by {approver_id}")
        return True
    
    async def reject_checkpoint(self, checkpoint_id: str, approver_id: str, 
                               reason: str = None) -> bool:
        """
        Reject a checkpoint
        
        Args:
            checkpoint_id: Checkpoint identifier
            approver_id: ID of the approver
            reason: Reason for rejection
            
        Returns:
            success: Whether the rejection was successful
        """
        checkpoint = self.checkpoints.get(checkpoint_id)
        
        if not checkpoint:
            logger.warning(f"Checkpoint {checkpoint_id} not found")
            return False
        
        if checkpoint.status != CheckpointStatus.PENDING:
            logger.warning(f"Checkpoint {checkpoint_id} not pending (status: {checkpoint.status})")
            return False
        
        checkpoint.status = CheckpointStatus.REJECTED
        checkpoint.approver_id = approver_id
        checkpoint.approved_at = datetime.utcnow()
        
        # Log checkpoint rejection
        await self._log_event(
            trace_id=checkpoint.trace_id,
            thread_id=checkpoint.thread_id,
            event_type="checkpoint_rejected",
            data={
                "checkpoint_id": checkpoint_id,
                "approver_id": approver_id,
                "reason": reason
            },
            source="langgraph_tracer"
        )
        
        logger.info(f"Rejected checkpoint {checkpoint_id} by {approver_id}: {reason}")
        return True
    
    async def complete_trace(self, thread_id: str, final_state: Dict[str, Any] = None,
                           status: TraceStatus = TraceStatus.COMPLETED) -> None:
        """
        Complete a trace and send to LangSmith
        
        Args:
            thread_id: Thread identifier
            final_state: Final state of the workflow
            status: Final status of the trace
        """
        if thread_id not in self.active_traces:
            logger.warning(f"Trace not found for thread {thread_id}")
            return
        
        trace = self.active_traces[thread_id]
        trace.status = status
        trace.completed_at = datetime.utcnow()
        
        # Log trace completion
        await self._log_event(
            trace_id=trace.trace_id,
            thread_id=thread_id,
            event_type="trace_completed",
            data={
                "status": status.value,
                "final_state": final_state,
                "execution_time": (trace.completed_at - trace.started_at).total_seconds(),
                "nodes_executed": len(trace.nodes),
                "edges_traversed": len(trace.edges),
                "checkpoints_created": len(trace.checkpoints)
            },
            source="langgraph_tracer"
        )
        
        # Send complete trace to LangSmith
        try:
            await self.langsmith_client.create_run(
                name=trace.workflow_name,
                run_type="chain",
                inputs=trace.metadata,
                outputs=final_state,
                project_name=self.project_name,
                metadata={
                    "trace_id": trace.trace_id,
                    "thread_id": thread_id,
                    "status": status.value,
                    "execution_time": (trace.completed_at - trace.started_at).total_seconds()
                }
            )
        except Exception as e:
            logger.error(f"Failed to send complete trace to LangSmith: {e}")
        
        # Store in Elasticsearch
        if self.elasticsearch:
            await self.elasticsearch.index(
                index="langgraph_traces",
                id=trace.trace_id,
                body=asdict(trace)
            )
        
        logger.info(f"Completed trace {trace.trace_id} with status {status.value}")
        
        # Clean up
        del self.active_traces[thread_id]
    
    async def get_trace(self, thread_id: str) -> Optional[Trace]:
        """
        Get a trace by thread ID
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            trace: Trace object or None if not found
        """
        return self.active_traces.get(thread_id)
    
    async def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Get a checkpoint by ID
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            checkpoint: Checkpoint object or None if not found
        """
        return self.checkpoints.get(checkpoint_id)
    
    async def list_pending_checkpoints(self) -> List[Checkpoint]:
        """
        List all pending checkpoints
        
        Returns:
            checkpoints: List of pending checkpoints
        """
        return [
            checkpoint for checkpoint in self.checkpoints.values()
            if checkpoint.status == CheckpointStatus.PENDING
        ]
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get tracer performance metrics
        
        Returns:
            metrics: Performance metrics
        """
        return {
            **self.metrics,
            "active_traces": len(self.active_traces),
            "total_checkpoints": len(self.checkpoints),
            "pending_checkpoints": len(await self.list_pending_checkpoints())
        }
    
    async def _log_event(self, trace_id: str, thread_id: str, event_type: str,
                        data: Dict[str, Any], source: str) -> None:
        """
        Log a trace event
        
        Args:
            trace_id: Trace identifier
            thread_id: Thread identifier
            event_type: Type of event
            data: Event data
            source: Event source
        """
        event = TraceEvent(
            event_id=str(uuid.uuid4()),
            trace_id=trace_id,
            thread_id=thread_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data,
            source=source
        )
        
        self.trace_events.append(event)
        
        # Store in Elasticsearch
        if self.elasticsearch:
            await self.elasticsearch.index(
                index="trace_events",
                body=asdict(event)
            )
        
        # Store in Redis for real-time access
        if self.redis:
            await self.redis.lpush(
                f"trace_events:{thread_id}",
                json.dumps(asdict(event), default=str)
            )
            await self.redis.expire(f"trace_events:{thread_id}", 3600)  # 1 hour TTL

# Example usage
async def main():
    """Example usage of LangGraphTracer"""
    
    # Initialize tracer
    tracer = LangGraphTracer(
        langsmith_api_key="your-api-key",
        project_name="obsidian-vault-ai"
    )
    
    # Start a trace
    thread_id = "user-123-session-456"
    trace_id = await tracer.start_trace(
        thread_id=thread_id,
        workflow_name="document_processing",
        metadata={"user_id": "user-123", "document_type": "markdown"}
    )
    
    # Log node executions
    await tracer.log_node_execution(
        thread_id=thread_id,
        node_id="text_extractor",
        input_data={"file_path": "/documents/example.md"},
        output_data={"text": "Sample document content", "word_count": 150},
        execution_time=0.5,
        metadata={"model": "gpt-4", "tokens_used": 200}
    )
    
    # Log edge traversal
    await tracer.log_edge_traversal(
        thread_id=thread_id,
        from_node="text_extractor",
        to_node="content_analyzer",
        condition="text_length > 100",
        metadata={"condition_met": True}
    )
    
    # Create checkpoint for human review
    checkpoint_id = await tracer.create_checkpoint(
        thread_id=thread_id,
        state={"extracted_text": "Sample content", "analysis_ready": True},
        description="Ready for human review of extracted content",
        expires_in_minutes=30
    )
    
    # Approve checkpoint
    await tracer.approve_checkpoint(checkpoint_id, "human-reviewer-1")
    
    # Restore from checkpoint
    restored_state = await tracer.restore_checkpoint(checkpoint_id)
    print(f"Restored state: {restored_state}")
    
    # Complete trace
    await tracer.complete_trace(
        thread_id=thread_id,
        final_state={"processed": True, "result": "Document processed successfully"}
    )
    
    # Get metrics
    metrics = await tracer.get_metrics()
    print(f"Tracer metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(main())

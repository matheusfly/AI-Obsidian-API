"""
Workflow Monitor - Advanced Workflow Execution Monitoring and Analytics
"""

import uuid
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from langsmith import Client

logger = logging.getLogger(__name__)

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class ExecutionStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    WAITING_FOR_HUMAN = "waiting_for_human"

class CheckpointStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class LogEntry:
    log_id: str
    step_id: str
    execution_id: str
    level: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]
    source: str

@dataclass
class WorkflowStep:
    step_id: str
    step_name: str
    step_type: str
    status: StepStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    error_message: Optional[str]
    logs: List[LogEntry]
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class WorkflowCheckpoint:
    checkpoint_id: str
    execution_id: str
    step_id: str
    timestamp: datetime
    state: Dict[str, Any]
    description: str
    status: CheckpointStatus
    approver_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

@dataclass
class HumanApproval:
    approval_id: str
    execution_id: str
    step_id: str
    approver_id: str
    status: str
    comment: Optional[str]
    requested_at: datetime
    responded_at: Optional[datetime]
    timeout_minutes: int = 60

@dataclass
class WorkflowExecution:
    execution_id: str
    workflow_id: str
    thread_id: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    steps: List[WorkflowStep]
    variables: Dict[str, Any]
    checkpoints: List[WorkflowCheckpoint]
    human_approvals: List[HumanApproval]
    metadata: Dict[str, Any]

@dataclass
class ExecutionMetrics:
    execution_id: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    skipped_steps: int
    total_execution_time: float
    average_step_time: float
    checkpoints_created: int
    human_approvals: int
    error_count: int
    retry_count: int

class WorkflowMonitor:
    """
    Advanced workflow execution monitoring and analytics
    """
    
    def __init__(self, elasticsearch_client=None, langsmith_client=None, 
                 redis_client=None):
        self.elasticsearch = elasticsearch_client
        self.langsmith = langsmith_client
        self.redis = redis_client
        
        # In-memory storage for active executions
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_metrics: Dict[str, ExecutionMetrics] = {}
        
        # Performance metrics
        self.metrics = {
            "active_executions": 0,
            "total_steps_executed": 0,
            "total_checkpoints_created": 0,
            "total_human_approvals": 0,
            "average_execution_time": 0.0,
            "success_rate": 0.0
        }
    
    async def start_execution(self, workflow_id: str, thread_id: str, 
                            initial_variables: Dict[str, Any] = None,
                            metadata: Dict[str, Any] = None) -> str:
        """
        Start a new workflow execution
        
        Args:
            workflow_id: Workflow identifier
            thread_id: Thread identifier
            initial_variables: Initial execution variables
            metadata: Additional metadata
            
        Returns:
            execution_id: Unique identifier for the execution
        """
        execution_id = str(uuid.uuid4())
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            thread_id=thread_id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.utcnow(),
            completed_at=None,
            steps=[],
            variables=initial_variables or {},
            checkpoints=[],
            human_approvals=[],
            metadata=metadata or {}
        )
        
        self.active_executions[execution_id] = execution
        self.metrics["active_executions"] = len(self.active_executions)
        
        # Log execution start
        await self._log_execution_event(
            execution_id=execution_id,
            event_type="execution_started",
            data={"workflow_id": workflow_id, "thread_id": thread_id}
        )
        
        # Store in Elasticsearch
        if self.elasticsearch:
            await self.elasticsearch.index(
                index="workflow_executions",
                id=execution_id,
                body=asdict(execution)
            )
        
        # Store in Redis
        if self.redis:
            await self.redis.setex(
                f"execution:{execution_id}",
                3600,  # 1 hour TTL
                json.dumps(asdict(execution), default=str)
            )
        
        logger.info(f"Started workflow execution {execution_id} for workflow {workflow_id}")
        return execution_id
    
    async def add_step(self, execution_id: str, step_id: str, 
                      step_name: str, step_type: str,
                      max_retries: int = 3) -> WorkflowStep:
        """
        Add a step to the execution
        
        Args:
            execution_id: Execution identifier
            step_id: Step identifier
            step_name: Human-readable step name
            step_type: Type of step
            max_retries: Maximum number of retries
            
        Returns:
            step: Workflow step object
        """
        if execution_id not in self.active_executions:
            raise ValueError(f"Execution {execution_id} not found")
        
        execution = self.active_executions[execution_id]
        
        step = WorkflowStep(
            step_id=step_id,
            step_name=step_name,
            step_type=step_type,
            status=StepStatus.PENDING,
            started_at=None,
            completed_at=None,
            input_data={},
            output_data={},
            error_message=None,
            logs=[],
            retry_count=0,
            max_retries=max_retries
        )
        
        execution.steps.append(step)
        
        # Log step addition
        await self._log_execution_event(
            execution_id=execution_id,
            event_type="step_added",
            data={"step_id": step_id, "step_name": step_name, "step_type": step_type}
        )
        
        logger.info(f"Added step {step_id} to execution {execution_id}")
        return step
    
    async def start_step(self, execution_id: str, step_id: str, 
                        input_data: Dict[str, Any]) -> None:
        """
        Start executing a step
        
        Args:
            execution_id: Execution identifier
            step_id: Step identifier
            input_data: Input data for the step
        """
        execution = self.active_executions[execution_id]
        step = next((s for s in execution.steps if s.step_id == step_id), None)
        
        if not step:
            raise ValueError(f"Step {step_id} not found")
        
        step.status = StepStatus.RUNNING
        step.started_at = datetime.utcnow()
        step.input_data = input_data
        
        # Log step start
        await self._log_step_event(
            execution_id=execution_id,
            step_id=step_id,
            event_type="step_started",
            data={"input_data": input_data}
        )
        
        logger.info(f"Started step {step_id} in execution {execution_id}")
    
    async def complete_step(self, execution_id: str, step_id: str, 
                           output_data: Dict[str, Any]) -> None:
        """
        Complete a step execution
        
        Args:
            execution_id: Execution identifier
            step_id: Step identifier
            output_data: Output data from the step
        """
        execution = self.active_executions[execution_id]
        step = next((s for s in execution.steps if s.step_id == step_id), None)
        
        if not step:
            raise ValueError(f"Step {step_id} not found")
        
        step.status = StepStatus.COMPLETED
        step.completed_at = datetime.utcnow()
        step.output_data = output_data
        
        execution_time = (step.completed_at - step.started_at).total_seconds()
        
        # Log step completion
        await self._log_step_event(
            execution_id=execution_id,
            step_id=step_id,
            event_type="step_completed",
            data={
                "output_data": output_data,
                "execution_time": execution_time
            }
        )
        
        # Update metrics
        self.metrics["total_steps_executed"] += 1
        
        logger.info(f"Completed step {step_id} in execution {execution_id} in {execution_time:.2f}s")
    
    async def fail_step(self, execution_id: str, step_id: str, 
                       error_message: str, retry: bool = True) -> None:
        """
        Mark a step as failed
        
        Args:
            execution_id: Execution identifier
            step_id: Step identifier
            error_message: Error message
            retry: Whether to retry the step
        """
        execution = self.active_executions[execution_id]
        step = next((s for s in execution.steps if s.step_id == step_id), None)
        
        if not step:
            raise ValueError(f"Step {step_id} not found")
        
        step.retry_count += 1
        step.error_message = error_message
        
        if retry and step.retry_count <= step.max_retries:
            # Retry the step
            step.status = StepStatus.PENDING
            step.started_at = None
            step.completed_at = None
            step.error_message = None
            
            # Log retry
            await self._log_step_event(
                execution_id=execution_id,
                step_id=step_id,
                event_type="step_retry",
                data={
                    "retry_count": step.retry_count,
                    "max_retries": step.max_retries,
                    "error_message": error_message
                }
            )
            
            logger.info(f"Retrying step {step_id} (attempt {step.retry_count})")
        else:
            # Mark as failed
            step.status = StepStatus.FAILED
            step.completed_at = datetime.utcnow()
            
            # Log step failure
            await self._log_step_event(
                execution_id=execution_id,
                step_id=step_id,
                event_type="step_failed",
                data={
                    "error_message": error_message,
                    "retry_count": step.retry_count,
                    "max_retries": step.max_retries
                }
            )
            
            # Check if execution should fail
            if not await self._should_continue_execution(execution):
                execution.status = ExecutionStatus.FAILED
                execution.completed_at = datetime.utcnow()
                
                await self._log_execution_event(
                    execution_id=execution_id,
                    event_type="execution_failed",
                    data={"reason": "Step failure", "failed_step": step_id}
                )
            
            logger.error(f"Failed step {step_id} in execution {execution_id}: {error_message}")
    
    async def create_checkpoint(self, execution_id: str, step_id: str, 
                               state: Dict[str, Any], description: str = None,
                               expires_in_minutes: int = 60) -> str:
        """
        Create a checkpoint for human-in-the-loop interactions
        
        Args:
            execution_id: Execution identifier
            step_id: Step identifier
            state: Current state to checkpoint
            description: Human-readable description
            expires_in_minutes: Checkpoint expiration time
            
        Returns:
            checkpoint_id: Unique identifier for the checkpoint
        """
        execution = self.active_executions[execution_id]
        checkpoint_id = str(uuid.uuid4())
        
        checkpoint = WorkflowCheckpoint(
            checkpoint_id=checkpoint_id,
            execution_id=execution_id,
            step_id=step_id,
            timestamp=datetime.utcnow(),
            state=state,
            description=description or f"Checkpoint at step {step_id}",
            status=CheckpointStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes) if expires_in_minutes else None
        )
        
        execution.checkpoints.append(checkpoint)
        self.metrics["total_checkpoints_created"] += 1
        
        # Log checkpoint creation
        await self._log_execution_event(
            execution_id=execution_id,
            event_type="checkpoint_created",
            data={
                "checkpoint_id": checkpoint_id,
                "step_id": step_id,
                "description": description
            }
        )
        
        # Store in Redis
        if self.redis:
            await self.redis.setex(
                f"checkpoint:{checkpoint_id}",
                expires_in_minutes * 60,
                json.dumps(asdict(checkpoint), default=str)
            )
        
        logger.info(f"Created checkpoint {checkpoint_id} for step {step_id}")
        return checkpoint_id
    
    async def approve_checkpoint(self, checkpoint_id: str, approver_id: str) -> bool:
        """
        Approve a checkpoint
        
        Args:
            checkpoint_id: Checkpoint identifier
            approver_id: ID of the approver
            
        Returns:
            success: Whether the approval was successful
        """
        # Find checkpoint
        checkpoint = None
        execution = None
        
        for exec in self.active_executions.values():
            for cp in exec.checkpoints:
                if cp.checkpoint_id == checkpoint_id:
                    checkpoint = cp
                    execution = exec
                    break
            if checkpoint:
                break
        
        if not checkpoint:
            logger.warning(f"Checkpoint {checkpoint_id} not found")
            return False
        
        if checkpoint.status != CheckpointStatus.PENDING:
            logger.warning(f"Checkpoint {checkpoint_id} not pending")
            return False
        
        # Check expiration
        if checkpoint.expires_at and datetime.utcnow() > checkpoint.expires_at:
            checkpoint.status = CheckpointStatus.EXPIRED
            logger.warning(f"Checkpoint {checkpoint_id} has expired")
            return False
        
        checkpoint.status = CheckpointStatus.APPROVED
        checkpoint.approver_id = approver_id
        checkpoint.approved_at = datetime.utcnow()
        
        # Log checkpoint approval
        await self._log_execution_event(
            execution_id=execution.execution_id,
            event_type="checkpoint_approved",
            data={
                "checkpoint_id": checkpoint_id,
                "approver_id": approver_id
            }
        )
        
        logger.info(f"Approved checkpoint {checkpoint_id} by {approver_id}")
        return True
    
    async def create_human_approval(self, execution_id: str, step_id: str, 
                                   approver_id: str, comment: str = None,
                                   timeout_minutes: int = 60) -> str:
        """
        Create a human approval request
        
        Args:
            execution_id: Execution identifier
            step_id: Step identifier
            approver_id: Approver identifier
            comment: Approval comment
            timeout_minutes: Timeout in minutes
            
        Returns:
            approval_id: Unique identifier for the approval
        """
        execution = self.active_executions[execution_id]
        approval_id = str(uuid.uuid4())
        
        approval = HumanApproval(
            approval_id=approval_id,
            execution_id=execution_id,
            step_id=step_id,
            approver_id=approver_id,
            status="pending",
            comment=comment,
            requested_at=datetime.utcnow(),
            timeout_minutes=timeout_minutes
        )
        
        execution.human_approvals.append(approval)
        execution.status = ExecutionStatus.WAITING_FOR_HUMAN
        self.metrics["total_human_approvals"] += 1
        
        # Log approval request
        await self._log_execution_event(
            execution_id=execution_id,
            event_type="human_approval_requested",
            data={
                "approval_id": approval_id,
                "step_id": step_id,
                "approver_id": approver_id,
                "comment": comment
            }
        )
        
        # Store in Redis
        if self.redis:
            await self.redis.setex(
                f"approval:{approval_id}",
                timeout_minutes * 60,
                json.dumps(asdict(approval), default=str)
            )
        
        logger.info(f"Created human approval {approval_id} for step {step_id}")
        return approval_id
    
    async def submit_approval(self, approval_id: str, approved: bool, 
                             comment: str = None) -> bool:
        """
        Submit an approval response
        
        Args:
            approval_id: Approval identifier
            approved: Whether the approval was granted
            comment: Approval comment
            
        Returns:
            success: Whether the submission was successful
        """
        # Find approval
        approval = None
        execution = None
        
        for exec in self.active_executions.values():
            for app in exec.human_approvals:
                if app.approval_id == approval_id:
                    approval = app
                    execution = exec
                    break
            if approval:
                break
        
        if not approval:
            logger.warning(f"Approval {approval_id} not found")
            return False
        
        if approval.status != "pending":
            logger.warning(f"Approval {approval_id} not pending")
            return False
        
        # Check timeout
        timeout_time = approval.requested_at + timedelta(minutes=approval.timeout_minutes)
        if datetime.utcnow() > timeout_time:
            approval.status = "timeout"
            logger.warning(f"Approval {approval_id} timed out")
            return False
        
        approval.status = "approved" if approved else "rejected"
        approval.responded_at = datetime.utcnow()
        if comment:
            approval.comment = comment
        
        # Update execution status
        pending_approvals = [a for a in execution.human_approvals if a.status == "pending"]
        if not pending_approvals:
            execution.status = ExecutionStatus.RUNNING
        
        # Log approval response
        await self._log_execution_event(
            execution_id=execution.execution_id,
            event_type="human_approval_submitted",
            data={
                "approval_id": approval_id,
                "approved": approved,
                "comment": comment
            }
        )
        
        logger.info(f"Submitted approval {approval_id}: {'approved' if approved else 'rejected'}")
        return True
    
    async def add_log_entry(self, execution_id: str, step_id: str, 
                           level: str, message: str, 
                           metadata: Dict[str, Any] = None,
                           source: str = "workflow") -> str:
        """
        Add a log entry to a step
        
        Args:
            execution_id: Execution identifier
            step_id: Step identifier
            level: Log level
            message: Log message
            metadata: Additional metadata
            source: Log source
            
        Returns:
            log_id: Unique identifier for the log entry
        """
        execution = self.active_executions[execution_id]
        step = next((s for s in execution.steps if s.step_id == step_id), None)
        
        if not step:
            raise ValueError(f"Step {step_id} not found")
        
        log_id = str(uuid.uuid4())
        log_entry = LogEntry(
            log_id=log_id,
            step_id=step_id,
            execution_id=execution_id,
            level=level,
            message=message,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            source=source
        )
        
        step.logs.append(log_entry)
        
        # Log to Elasticsearch
        if self.elasticsearch:
            await self.elasticsearch.index(
                index="workflow_logs",
                id=log_id,
                body=asdict(log_entry)
            )
        
        logger.info(f"Added log entry {log_id} to step {step_id}")
        return log_id
    
    async def complete_execution(self, execution_id: str, 
                               final_status: ExecutionStatus = ExecutionStatus.COMPLETED) -> None:
        """
        Complete a workflow execution
        
        Args:
            execution_id: Execution identifier
            final_status: Final execution status
        """
        if execution_id not in self.active_executions:
            raise ValueError(f"Execution {execution_id} not found")
        
        execution = self.active_executions[execution_id]
        execution.status = final_status
        execution.completed_at = datetime.utcnow()
        
        # Calculate execution metrics
        total_time = (execution.completed_at - execution.started_at).total_seconds()
        completed_steps = len([s for s in execution.steps if s.status == StepStatus.COMPLETED])
        failed_steps = len([s for s in execution.steps if s.status == StepStatus.FAILED])
        
        metrics = ExecutionMetrics(
            execution_id=execution_id,
            total_steps=len(execution.steps),
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            skipped_steps=len([s for s in execution.steps if s.status == StepStatus.SKIPPED]),
            total_execution_time=total_time,
            average_step_time=total_time / len(execution.steps) if execution.steps else 0,
            checkpoints_created=len(execution.checkpoints),
            human_approvals=len(execution.human_approvals),
            error_count=sum(len(s.logs) for s in execution.steps if s.status == StepStatus.FAILED),
            retry_count=sum(s.retry_count for s in execution.steps)
        )
        
        self.execution_metrics[execution_id] = metrics
        
        # Update global metrics
        self.metrics["active_executions"] = len(self.active_executions)
        
        # Calculate success rate
        total_executions = len(self.execution_metrics)
        successful_executions = len([m for m in self.execution_metrics.values() if m.failed_steps == 0])
        self.metrics["success_rate"] = successful_executions / total_executions if total_executions > 0 else 0
        
        # Log execution completion
        await self._log_execution_event(
            execution_id=execution_id,
            event_type="execution_completed",
            data={
                "status": final_status.value,
                "total_time": total_time,
                "completed_steps": completed_steps,
                "failed_steps": failed_steps
            }
        )
        
        # Send to LangSmith
        if self.langsmith:
            try:
                await self.langsmith.create_run(
                    name=f"workflow_{execution.workflow_id}",
                    run_type="chain",
                    inputs=execution.variables,
                    outputs={"status": final_status.value, "metrics": asdict(metrics)},
                    project_name="workflow_monitoring",
                    metadata={
                        "execution_id": execution_id,
                        "workflow_id": execution.workflow_id,
                        "thread_id": execution.thread_id,
                        "total_time": total_time
                    }
                )
            except Exception as e:
                logger.error(f"Failed to send execution to LangSmith: {e}")
        
        # Store final execution in Elasticsearch
        if self.elasticsearch:
            await self.elasticsearch.index(
                index="workflow_executions",
                id=execution_id,
                body=asdict(execution)
            )
        
        logger.info(f"Completed execution {execution_id} with status {final_status.value}")
        
        # Clean up
        del self.active_executions[execution_id]
    
    async def get_execution_metrics(self, execution_id: str) -> Optional[ExecutionMetrics]:
        """
        Get metrics for a specific execution
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            metrics: Execution metrics or None if not found
        """
        return self.execution_metrics.get(execution_id)
    
    async def get_global_metrics(self) -> Dict[str, Any]:
        """
        Get global workflow metrics
        
        Returns:
            metrics: Global metrics
        """
        return {
            **self.metrics,
            "total_executions": len(self.execution_metrics),
            "average_execution_time": sum(
                m.total_execution_time for m in self.execution_metrics.values()
            ) / len(self.execution_metrics) if self.execution_metrics else 0
        }
    
    async def _should_continue_execution(self, execution: WorkflowExecution) -> bool:
        """
        Determine if execution should continue after a step failure
        
        Args:
            execution: Workflow execution
            
        Returns:
            should_continue: Whether to continue execution
        """
        # Simple logic: continue if less than 50% of steps have failed
        total_steps = len(execution.steps)
        failed_steps = len([s for s in execution.steps if s.status == StepStatus.FAILED])
        
        return (failed_steps / total_steps) < 0.5 if total_steps > 0 else True
    
    async def _log_execution_event(self, execution_id: str, event_type: str, 
                                  data: Dict[str, Any]) -> None:
        """
        Log an execution event
        
        Args:
            execution_id: Execution identifier
            event_type: Type of event
            data: Event data
        """
        event = {
            "execution_id": execution_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow(),
            "data": data
        }
        
        # Store in Elasticsearch
        if self.elasticsearch:
            await self.elasticsearch.index(
                index="execution_events",
                body=event
            )
        
        # Store in Redis
        if self.redis:
            await self.redis.lpush(
                f"execution_events:{execution_id}",
                json.dumps(event, default=str)
            )
            await self.redis.expire(f"execution_events:{execution_id}", 3600)
    
    async def _log_step_event(self, execution_id: str, step_id: str, 
                             event_type: str, data: Dict[str, Any]) -> None:
        """
        Log a step event
        
        Args:
            execution_id: Execution identifier
            step_id: Step identifier
            event_type: Type of event
            data: Event data
        """
        event = {
            "execution_id": execution_id,
            "step_id": step_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow(),
            "data": data
        }
        
        # Store in Elasticsearch
        if self.elasticsearch:
            await self.elasticsearch.index(
                index="step_events",
                body=event
            )
        
        # Store in Redis
        if self.redis:
            await self.redis.lpush(
                f"step_events:{execution_id}:{step_id}",
                json.dumps(event, default=str)
            )
            await self.redis.expire(f"step_events:{execution_id}:{step_id}", 3600)

# Example usage
async def main():
    """Example usage of WorkflowMonitor"""
    
    # Initialize monitor
    monitor = WorkflowMonitor()
    
    # Start execution
    execution_id = await monitor.start_execution(
        workflow_id="document_processing",
        thread_id="thread-123",
        initial_variables={"file_path": "/documents/example.md"},
        metadata={"user_id": "user-123", "priority": "high"}
    )
    
    # Add steps
    step1 = await monitor.add_step(execution_id, "extract_text", "Extract Text", "text_extraction")
    step2 = await monitor.add_step(execution_id, "analyze_content", "Analyze Content", "content_analysis")
    step3 = await monitor.add_step(execution_id, "generate_summary", "Generate Summary", "summary_generation")
    
    # Execute steps
    await monitor.start_step(execution_id, "extract_text", {"file_path": "/documents/example.md"})
    await monitor.add_log_entry(execution_id, "extract_text", "info", "Starting text extraction")
    await monitor.complete_step(execution_id, "extract_text", {"text": "Sample content", "word_count": 150})
    
    # Create checkpoint
    checkpoint_id = await monitor.create_checkpoint(
        execution_id, "extract_text", 
        {"extracted_text": "Sample content"}, 
        "Review extracted text"
    )
    
    # Approve checkpoint
    await monitor.approve_checkpoint(checkpoint_id, "human-reviewer-1")
    
    # Continue execution
    await monitor.start_step(execution_id, "analyze_content", {"text": "Sample content"})
    await monitor.complete_step(execution_id, "analyze_content", {"analysis": "Positive sentiment"})
    
    # Create human approval
    approval_id = await monitor.create_human_approval(
        execution_id, "generate_summary", "human-reviewer-1", 
        "Please approve summary generation"
    )
    
    # Submit approval
    await monitor.submit_approval(approval_id, True, "Approved for generation")
    
    # Complete execution
    await monitor.complete_execution(execution_id)
    
    # Get metrics
    metrics = await monitor.get_execution_metrics(execution_id)
    print(f"Execution metrics: {metrics}")
    
    global_metrics = await monitor.get_global_metrics()
    print(f"Global metrics: {global_metrics}")

if __name__ == "__main__":
    asyncio.run(main())

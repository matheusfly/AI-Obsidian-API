"""
Chat Monitor - Interactive Chat Thread Monitoring and Analytics
"""

import uuid
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from langsmith import Client

logger = logging.getLogger(__name__)

class MessageType(Enum):
    USER = "user"
    AI = "ai"
    SYSTEM = "system"
    HUMAN_APPROVAL = "human_approval"
    ERROR = "error"

class ThreadStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_FOR_HUMAN = "waiting_for_human"

class InteractionType(Enum):
    APPROVAL = "approval"
    CLARIFICATION = "clarification"
    CONFIRMATION = "confirmation"
    FEEDBACK = "feedback"

@dataclass
class ChatMessage:
    message_id: str
    thread_id: str
    user_id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    metadata: Dict[str, Any]
    parent_message_id: Optional[str] = None
    response_time: Optional[float] = None

@dataclass
class ThreadContext:
    current_state: str
    variables: Dict[str, Any]
    checkpoints: List[str]
    pending_actions: List[str]
    ai_model: Optional[str] = None
    confidence_score: Optional[float] = None
    last_ai_response: Optional[str] = None

@dataclass
class HumanInteraction:
    interaction_id: str
    thread_id: str
    interaction_type: InteractionType
    prompt: str
    response: Optional[str]
    requested_at: datetime
    responded_at: Optional[datetime]
    status: str
    approver_id: Optional[str] = None
    timeout_minutes: int = 30

@dataclass
class ChatThread:
    thread_id: str
    user_id: str
    session_id: str
    created_at: datetime
    last_activity: datetime
    status: ThreadStatus
    messages: List[ChatMessage]
    context: ThreadContext
    human_interactions: List[HumanInteraction]
    metadata: Dict[str, Any]

@dataclass
class ThreadAnalytics:
    thread_id: str
    message_count: int
    duration_minutes: float
    user_messages: int
    ai_messages: int
    human_interactions: int
    average_response_time: float
    sentiment_score: float
    topic_changes: int
    error_count: int
    satisfaction_score: Optional[float] = None

class ChatMonitor:
    """
    Advanced chat thread monitoring and analytics
    """
    
    def __init__(self, elasticsearch_client=None, langsmith_client=None, 
                 redis_client=None, sentiment_analyzer=None):
        self.elasticsearch = elasticsearch_client
        self.langsmith = langsmith_client
        self.redis = redis_client
        self.sentiment_analyzer = sentiment_analyzer
        
        # In-memory storage for active threads
        self.active_threads: Dict[str, ChatThread] = {}
        self.thread_analytics: Dict[str, ThreadAnalytics] = {}
        
        # Performance metrics
        self.metrics = {
            "active_threads": 0,
            "total_messages": 0,
            "average_response_time": 0.0,
            "human_interaction_rate": 0.0,
            "error_rate": 0.0
        }
    
    async def create_thread(self, user_id: str, session_id: str, 
                           initial_context: Dict[str, Any] = None,
                           metadata: Dict[str, Any] = None) -> str:
        """
        Create a new chat thread
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            initial_context: Initial thread context
            metadata: Additional metadata
            
        Returns:
            thread_id: Unique identifier for the thread
        """
        thread_id = str(uuid.uuid4())
        
        thread = ChatThread(
            thread_id=thread_id,
            user_id=user_id,
            session_id=session_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            status=ThreadStatus.ACTIVE,
            messages=[],
            context=ThreadContext(
                current_state="initialized",
                variables=initial_context or {},
                checkpoints=[],
                pending_actions=[]
            ),
            human_interactions=[],
            metadata=metadata or {}
        )
        
        self.active_threads[thread_id] = thread
        self.metrics["active_threads"] = len(self.active_threads)
        
        # Log thread creation
        await self._log_thread_event(
            thread_id=thread_id,
            event_type="thread_created",
            data={"user_id": user_id, "session_id": session_id}
        )
        
        # Store in Elasticsearch
        if self.elasticsearch:
            await self.elasticsearch.index(
                index="chat_threads",
                id=thread_id,
                body=asdict(thread)
            )
        
        # Store in Redis for quick access
        if self.redis:
            await self.redis.setex(
                f"thread:{thread_id}",
                3600,  # 1 hour TTL
                json.dumps(asdict(thread), default=str)
            )
        
        logger.info(f"Created chat thread {thread_id} for user {user_id}")
        return thread_id
    
    async def add_message(self, thread_id: str, user_id: str, content: str, 
                         message_type: MessageType = MessageType.USER,
                         metadata: Dict[str, Any] = None,
                         parent_message_id: str = None) -> str:
        """
        Add a message to a thread
        
        Args:
            thread_id: Thread identifier
            user_id: User identifier
            content: Message content
            message_type: Type of message
            metadata: Additional metadata
            parent_message_id: Parent message ID for threading
            
        Returns:
            message_id: Unique identifier for the message
        """
        if thread_id not in self.active_threads:
            raise ValueError(f"Thread {thread_id} not found")
        
        thread = self.active_threads[thread_id]
        
        # Calculate response time for AI messages
        response_time = None
        if message_type == MessageType.AI and thread.messages:
            last_user_message = None
            for msg in reversed(thread.messages):
                if msg.message_type == MessageType.USER:
                    last_user_message = msg
                    break
            
            if last_user_message:
                response_time = (datetime.utcnow() - last_user_message.timestamp).total_seconds()
        
        message_id = str(uuid.uuid4())
        message = ChatMessage(
            message_id=message_id,
            thread_id=thread_id,
            user_id=user_id,
            content=content,
            message_type=message_type,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            parent_message_id=parent_message_id,
            response_time=response_time
        )
        
        thread.messages.append(message)
        thread.last_activity = datetime.utcnow()
        self.metrics["total_messages"] += 1
        
        # Update average response time
        if response_time:
            current_avg = self.metrics["average_response_time"]
            total_ai_messages = sum(1 for m in thread.messages if m.message_type == MessageType.AI)
            self.metrics["average_response_time"] = (
                (current_avg * (total_ai_messages - 1) + response_time) / total_ai_messages
            )
        
        # Log message
        await self._log_thread_event(
            thread_id=thread_id,
            event_type="message_added",
            data={
                "message_id": message_id,
                "message_type": message_type.value,
                "content_length": len(content),
                "response_time": response_time
            }
        )
        
        # Store in Elasticsearch
        if self.elasticsearch:
            await self.elasticsearch.index(
                index="chat_messages",
                id=message_id,
                body=asdict(message)
            )
        
        # Send to LangSmith for analysis
        if self.langsmith:
            try:
                await self.langsmith.create_run(
                    name="chat_message",
                    run_type="llm",
                    inputs={"content": content, "type": message_type.value},
                    outputs={"message_id": message_id},
                    project_name="chat_monitoring",
                    metadata={
                        "thread_id": thread_id,
                        "user_id": user_id,
                        "response_time": response_time
                    }
                )
            except Exception as e:
                logger.error(f"Failed to send message to LangSmith: {e}")
        
        logger.info(f"Added {message_type.value} message to thread {thread_id}")
        return message_id
    
    async def create_human_interaction(self, thread_id: str, 
                                     interaction_type: InteractionType,
                                     prompt: str, timeout_minutes: int = 30) -> str:
        """
        Create a human-in-the-loop interaction
        
        Args:
            thread_id: Thread identifier
            interaction_type: Type of interaction
            prompt: Prompt for human
            timeout_minutes: Timeout in minutes
            
        Returns:
            interaction_id: Unique identifier for the interaction
        """
        if thread_id not in self.active_threads:
            raise ValueError(f"Thread {thread_id} not found")
        
        thread = self.active_threads[thread_id]
        interaction_id = str(uuid.uuid4())
        
        interaction = HumanInteraction(
            interaction_id=interaction_id,
            thread_id=thread_id,
            interaction_type=interaction_type,
            prompt=prompt,
            response=None,
            requested_at=datetime.utcnow(),
            responded_at=None,
            status="pending",
            timeout_minutes=timeout_minutes
        )
        
        thread.human_interactions.append(interaction)
        thread.status = ThreadStatus.WAITING_FOR_HUMAN
        
        # Log human interaction
        await self._log_thread_event(
            thread_id=thread_id,
            event_type="human_interaction_created",
            data={
                "interaction_id": interaction_id,
                "interaction_type": interaction_type.value,
                "prompt": prompt,
                "timeout_minutes": timeout_minutes
            }
        )
        
        # Store in Redis with timeout
        if self.redis:
            await self.redis.setex(
                f"human_interaction:{interaction_id}",
                timeout_minutes * 60,
                json.dumps(asdict(interaction), default=str)
            )
        
        logger.info(f"Created human interaction {interaction_id} for thread {thread_id}")
        return interaction_id
    
    async def submit_human_response(self, interaction_id: str, response: str, 
                                   approver_id: str = None) -> bool:
        """
        Submit a human response to an interaction
        
        Args:
            interaction_id: Interaction identifier
            response: Human response
            approver_id: ID of the approver
            
        Returns:
            success: Whether the response was submitted successfully
        """
        # Find the interaction
        interaction = None
        thread = None
        
        for t in self.active_threads.values():
            for i in t.human_interactions:
                if i.interaction_id == interaction_id:
                    interaction = i
                    thread = t
                    break
            if interaction:
                break
        
        if not interaction:
            logger.warning(f"Human interaction {interaction_id} not found")
            return False
        
        if interaction.status != "pending":
            logger.warning(f"Human interaction {interaction_id} not pending")
            return False
        
        # Check timeout
        if interaction.timeout_minutes:
            timeout_time = interaction.requested_at + timedelta(minutes=interaction.timeout_minutes)
            if datetime.utcnow() > timeout_time:
                interaction.status = "timeout"
                logger.warning(f"Human interaction {interaction_id} timed out")
                return False
        
        # Update interaction
        interaction.response = response
        interaction.responded_at = datetime.utcnow()
        interaction.status = "completed"
        interaction.approver_id = approver_id
        
        # Update thread status
        if thread:
            pending_interactions = [i for i in thread.human_interactions if i.status == "pending"]
            if not pending_interactions:
                thread.status = ThreadStatus.ACTIVE
        
        # Log human response
        await self._log_thread_event(
            thread_id=interaction.thread_id,
            event_type="human_response_submitted",
            data={
                "interaction_id": interaction_id,
                "response": response,
                "approver_id": approver_id,
                "response_time": (interaction.responded_at - interaction.requested_at).total_seconds()
            }
        )
        
        # Add response as a message
        await self.add_message(
            thread_id=interaction.thread_id,
            user_id=approver_id or "human",
            content=response,
            message_type=MessageType.HUMAN_APPROVAL,
            metadata={"interaction_id": interaction_id}
        )
        
        logger.info(f"Submitted human response for interaction {interaction_id}")
        return True
    
    async def update_thread_context(self, thread_id: str, 
                                   context_updates: Dict[str, Any]) -> None:
        """
        Update thread context
        
        Args:
            thread_id: Thread identifier
            context_updates: Context updates
        """
        if thread_id not in self.active_threads:
            raise ValueError(f"Thread {thread_id} not found")
        
        thread = self.active_threads[thread_id]
        
        # Update context variables
        for key, value in context_updates.items():
            if key == "current_state":
                thread.context.current_state = value
            elif key == "ai_model":
                thread.context.ai_model = value
            elif key == "confidence_score":
                thread.context.confidence_score = value
            elif key == "last_ai_response":
                thread.context.last_ai_response = value
            else:
                thread.context.variables[key] = value
        
        # Log context update
        await self._log_thread_event(
            thread_id=thread_id,
            event_type="context_updated",
            data={"updates": context_updates}
        )
        
        logger.info(f"Updated context for thread {thread_id}")
    
    async def get_thread_analytics(self, thread_id: str) -> ThreadAnalytics:
        """
        Get analytics for a specific thread
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            analytics: Thread analytics
        """
        if thread_id not in self.active_threads:
            raise ValueError(f"Thread {thread_id} not found")
        
        thread = self.active_threads[thread_id]
        
        # Calculate basic metrics
        user_messages = len([m for m in thread.messages if m.message_type == MessageType.USER])
        ai_messages = len([m for m in thread.messages if m.message_type == MessageType.AI])
        human_interactions = len(thread.human_interactions)
        error_messages = len([m for m in thread.messages if m.message_type == MessageType.ERROR])
        
        # Calculate response times
        response_times = [m.response_time for m in thread.messages if m.response_time is not None]
        average_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        # Calculate sentiment score
        sentiment_score = await self._calculate_sentiment(thread)
        
        # Calculate topic changes (simplified)
        topic_changes = await self._calculate_topic_changes(thread)
        
        analytics = ThreadAnalytics(
            thread_id=thread_id,
            message_count=len(thread.messages),
            duration_minutes=(thread.last_activity - thread.created_at).total_seconds() / 60,
            user_messages=user_messages,
            ai_messages=ai_messages,
            human_interactions=human_interactions,
            average_response_time=average_response_time,
            sentiment_score=sentiment_score,
            topic_changes=topic_changes,
            error_count=error_messages
        )
        
        self.thread_analytics[thread_id] = analytics
        return analytics
    
    async def get_pending_interactions(self) -> List[HumanInteraction]:
        """
        Get all pending human interactions
        
        Returns:
            interactions: List of pending interactions
        """
        pending_interactions = []
        
        for thread in self.active_threads.values():
            for interaction in thread.human_interactions:
                if interaction.status == "pending":
                    # Check timeout
                    if interaction.timeout_minutes:
                        timeout_time = interaction.requested_at + timedelta(minutes=interaction.timeout_minutes)
                        if datetime.utcnow() > timeout_time:
                            interaction.status = "timeout"
                            continue
                    
                    pending_interactions.append(interaction)
        
        return pending_interactions
    
    async def get_thread_metrics(self) -> Dict[str, Any]:
        """
        Get overall thread metrics
        
        Returns:
            metrics: Thread metrics
        """
        total_threads = len(self.active_threads)
        total_messages = sum(len(t.messages) for t in self.active_threads.values())
        total_human_interactions = sum(len(t.human_interactions) for t in self.active_threads.values())
        
        # Calculate human interaction rate
        human_interaction_rate = 0.0
        if total_messages > 0:
            human_interaction_rate = total_human_interactions / total_messages
        
        # Calculate error rate
        total_errors = sum(
            len([m for m in t.messages if m.message_type == MessageType.ERROR])
            for t in self.active_threads.values()
        )
        error_rate = total_errors / total_messages if total_messages > 0 else 0.0
        
        return {
            "active_threads": total_threads,
            "total_messages": total_messages,
            "total_human_interactions": total_human_interactions,
            "human_interaction_rate": human_interaction_rate,
            "error_rate": error_rate,
            "average_response_time": self.metrics["average_response_time"]
        }
    
    async def _calculate_sentiment(self, thread: ChatThread) -> float:
        """
        Calculate sentiment score for a thread
        
        Args:
            thread: Chat thread
            
        Returns:
            sentiment_score: Sentiment score between -1 and 1
        """
        if not self.sentiment_analyzer:
            # Simple keyword-based sentiment analysis
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "perfect"]
            negative_words = ["bad", "terrible", "awful", "horrible", "disappointing", "wrong"]
            
            all_text = " ".join([m.content for m in thread.messages])
            text_lower = all_text.lower()
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            total_words = len(text_lower.split())
            if total_words == 0:
                return 0.0
            
            sentiment_score = (positive_count - negative_count) / total_words
            return max(-1.0, min(1.0, sentiment_score))
        
        # Use external sentiment analyzer
        try:
            all_text = " ".join([m.content for m in thread.messages])
            sentiment_score = await self.sentiment_analyzer.analyze(all_text)
            return sentiment_score
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            return 0.0
    
    async def _calculate_topic_changes(self, thread: ChatThread) -> int:
        """
        Calculate number of topic changes in a thread
        
        Args:
            thread: Chat thread
            
        Returns:
            topic_changes: Number of topic changes
        """
        # Simple topic change detection based on message content similarity
        messages = [m.content for m in thread.messages if m.message_type in [MessageType.USER, MessageType.AI]]
        
        if len(messages) < 2:
            return 0
        
        topic_changes = 0
        for i in range(1, len(messages)):
            # Simple similarity check (in practice, use more sophisticated NLP)
            prev_words = set(messages[i-1].lower().split())
            curr_words = set(messages[i].lower().split())
            
            # If less than 30% word overlap, consider it a topic change
            if prev_words and curr_words:
                overlap = len(prev_words.intersection(curr_words))
                similarity = overlap / max(len(prev_words), len(curr_words))
                if similarity < 0.3:
                    topic_changes += 1
        
        return topic_changes
    
    async def _log_thread_event(self, thread_id: str, event_type: str, 
                               data: Dict[str, Any]) -> None:
        """
        Log a thread event
        
        Args:
            thread_id: Thread identifier
            event_type: Type of event
            data: Event data
        """
        event = {
            "thread_id": thread_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow(),
            "data": data
        }
        
        # Store in Elasticsearch
        if self.elasticsearch:
            await self.elasticsearch.index(
                index="thread_events",
                body=event
            )
        
        # Store in Redis for real-time access
        if self.redis:
            await self.redis.lpush(
                f"thread_events:{thread_id}",
                json.dumps(event, default=str)
            )
            await self.redis.expire(f"thread_events:{thread_id}", 3600)  # 1 hour TTL

# Example usage
async def main():
    """Example usage of ChatMonitor"""
    
    # Initialize monitor
    monitor = ChatMonitor()
    
    # Create a thread
    thread_id = await monitor.create_thread(
        user_id="user-123",
        session_id="session-456",
        initial_context={"language": "en", "domain": "technical"},
        metadata={"source": "web", "version": "1.0"}
    )
    
    # Add messages
    await monitor.add_message(
        thread_id=thread_id,
        user_id="user-123",
        content="Hello, I need help with my Obsidian vault",
        message_type=MessageType.USER
    )
    
    await monitor.add_message(
        thread_id=thread_id,
        user_id="ai-assistant",
        content="I'd be happy to help you with your Obsidian vault! What specific issue are you facing?",
        message_type=MessageType.AI,
        metadata={"model": "gpt-4", "confidence": 0.95}
    )
    
    # Create human interaction
    interaction_id = await monitor.create_human_interaction(
        thread_id=thread_id,
        interaction_type=InteractionType.APPROVAL,
        prompt="Please review this AI response for accuracy",
        timeout_minutes=15
    )
    
    # Submit human response
    await monitor.submit_human_response(
        interaction_id=interaction_id,
        response="The response looks good, please proceed",
        approver_id="human-reviewer-1"
    )
    
    # Get analytics
    analytics = await monitor.get_thread_analytics(thread_id)
    print(f"Thread analytics: {analytics}")
    
    # Get metrics
    metrics = await monitor.get_thread_metrics()
    print(f"Thread metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(main())

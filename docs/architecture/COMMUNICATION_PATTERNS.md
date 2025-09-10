# 📡 **COMMUNICATION PATTERNS**

**Version:** 3.0.0  
**Last Updated:** September 6, 2025  
**Status:** ✅ **PRODUCTION READY**

---

## 🎯 **OVERVIEW**

Communication patterns define how services interact and exchange information in the Data Vault Obsidian platform. These patterns ensure reliable, efficient, and maintainable inter-service communication.

### **Key Benefits**
- **Reliability** - Robust communication with error handling and retry mechanisms
- **Performance** - Optimized communication for high-throughput systems
- **Scalability** - Communication patterns that scale with system growth
- **Maintainability** - Clear communication contracts and interfaces
- **Flexibility** - Support for various communication protocols and patterns

---

## 🏗️ **CORE COMMUNICATION PATTERNS**

### **1. Request-Response Pattern**

#### **Pattern Description**
Synchronous communication where a client sends a request and waits for a response from the server.

#### **Implementation**
```python
# request_response_client.py
import httpx
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Request:
    method: str
    url: str
    headers: Dict[str, str]
    data: Dict[str, Any]
    timeout: int = 30

@dataclass
class Response:
    status_code: int
    headers: Dict[str, str]
    data: Dict[str, Any]
    success: bool

class RequestResponseClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def send_request(self, request: Request) -> Response:
        """Send request and wait for response"""
        try:
            response = await self.client.request(
                method=request.method,
                url=f"{self.base_url}{request.url}",
                headers=request.headers,
                json=request.data,
                timeout=request.timeout
            )
            
            return Response(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=response.json() if response.content else {},
                success=200 <= response.status_code < 300
            )
        except Exception as e:
            return Response(
                status_code=500,
                headers={},
                data={"error": str(e)},
                success=False
            )
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()
```

### **2. Publish-Subscribe Pattern**

#### **Pattern Description**
Asynchronous communication where publishers send messages to topics and subscribers receive messages from topics they're interested in.

#### **Implementation**
```python
# pub_sub_client.py
from typing import Dict, Any, Callable, List
from dataclasses import dataclass
import asyncio
import json

@dataclass
class Message:
    topic: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str

class PubSubClient:
    def __init__(self, broker_url: str):
        self.broker_url = broker_url
        self.subscribers = {}
        self.publishers = {}
        self.running = False
    
    async def publish(self, topic: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Publish message to topic"""
        message = Message(
            topic=topic,
            data=data,
            metadata=metadata or {},
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Send to broker
        await self._send_to_broker(message)
    
    async def subscribe(self, topic: str, handler: Callable[[Message], None]):
        """Subscribe to topic with handler"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        
        self.subscribers[topic].append(handler)
        await self._register_subscription(topic)
    
    async def _send_to_broker(self, message: Message):
        """Send message to broker"""
        # Implementation depends on broker (Redis, RabbitMQ, etc.)
        pass
    
    async def _register_subscription(self, topic: str):
        """Register subscription with broker"""
        # Implementation depends on broker
        pass
```

### **3. Message Queue Pattern**

#### **Pattern Description**
Asynchronous communication using message queues for reliable message delivery and processing.

#### **Implementation**
```python
# message_queue_client.py
from typing import Dict, Any, Callable
from dataclasses import dataclass
import asyncio
import json

@dataclass
class QueueMessage:
    id: str
    queue: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3

class MessageQueueClient:
    def __init__(self, queue_backend):
        self.queue_backend = queue_backend
        self.consumers = {}
        self.running = False
    
    async def send_message(self, queue: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Send message to queue"""
        message = QueueMessage(
            id=f"msg_{uuid.uuid4()}",
            queue=queue,
            data=data,
            metadata=metadata or {}
        )
        
        await self.queue_backend.enqueue(queue, message)
    
    async def consume_messages(self, queue: str, handler: Callable[[QueueMessage], None]):
        """Consume messages from queue"""
        self.consumers[queue] = handler
        self.running = True
        
        while self.running:
            try:
                message = await self.queue_backend.dequeue(queue)
                if message:
                    await handler(message)
            except Exception as e:
                print(f"Error consuming message: {e}")
                await asyncio.sleep(1)
    
    async def stop_consuming(self):
        """Stop consuming messages"""
        self.running = False
```

### **4. API Gateway Pattern**

#### **Pattern Description**
Single entry point for all client requests, routing them to appropriate backend services.

#### **Implementation**
```python
# api_gateway.py
from typing import Dict, Any, Optional
from dataclasses import dataclass
import httpx
import asyncio

@dataclass
class Route:
    path: str
    method: str
    service_url: str
    timeout: int = 30
    retry_count: int = 3

class APIGateway:
    def __init__(self):
        self.routes = {}
        self.client = httpx.AsyncClient()
    
    def add_route(self, route: Route):
        """Add route to gateway"""
        key = f"{route.method}:{route.path}"
        self.routes[key] = route
    
    async def handle_request(self, method: str, path: str, headers: Dict[str, str], data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming request"""
        key = f"{method}:{path}"
        
        if key not in self.routes:
            return {"error": "Route not found", "status_code": 404}
        
        route = self.routes[key]
        
        # Route request to service
        try:
            response = await self.client.request(
                method=method,
                url=f"{route.service_url}{path}",
                headers=headers,
                json=data,
                timeout=route.timeout
            )
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.content else {}
            }
        except Exception as e:
            return {"error": str(e), "status_code": 500}
    
    async def close(self):
        """Close gateway"""
        await self.client.aclose()
```

---

## 🔧 **ADVANCED COMMUNICATION PATTERNS**

### **1. Circuit Breaker Pattern**

#### **Implementation**
```python
# circuit_breaker.py
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (datetime.utcnow() - self.last_failure_time).seconds >= self.timeout
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### **2. Retry Pattern**

#### **Implementation**
```python
# retry_pattern.py
import asyncio
import random
from typing import Callable, Any

class RetryHandler:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)
        
        raise last_exception
```

### **3. Load Balancing Pattern**

#### **Implementation**
```python
# load_balancer.py
from typing import List, Dict, Any
import random
import asyncio

class LoadBalancer:
    def __init__(self, servers: List[str], strategy: str = "round_robin"):
        self.servers = servers
        self.strategy = strategy
        self.current_index = 0
    
    def get_server(self) -> str:
        """Get next server based on strategy"""
        if self.strategy == "round_robin":
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            return server
        elif self.strategy == "random":
            return random.choice(self.servers)
        elif self.strategy == "least_connections":
            return self._get_least_loaded_server()
        else:
            return self.servers[0]
    
    def _get_least_loaded_server(self) -> str:
        """Get server with least active connections"""
        # Implementation would track active connections per server
        return self.servers[0]
```

---

## 📊 **MONITORING AND OBSERVABILITY**

### **Communication Metrics**
```python
# communication_metrics.py
from typing import Dict, Any
from datetime import datetime

class CommunicationMetrics:
    def __init__(self):
        self.request_counts = {}
        self.response_times = {}
        self.error_counts = {}
        self.throughput = 0
    
    def record_request(self, service: str, response_time: float, success: bool):
        """Record request metrics"""
        self.request_counts[service] = self.request_counts.get(service, 0) + 1
        self.response_times[service] = self.response_times.get(service, [])
        self.response_times[service].append(response_time)
        
        if not success:
            self.error_counts[service] = self.error_counts.get(service, 0) + 1
        
        self.throughput += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            "request_counts": self.request_counts,
            "average_response_times": {
                service: sum(times) / len(times)
                for service, times in self.response_times.items()
            },
            "error_counts": self.error_counts,
            "throughput": self.throughput
        }
```

---

## 🚀 **IMPLEMENTATION ROADMAP**

### **Phase 1: Basic Communication (Weeks 1-2)**
1. **Request-Response** - Implement basic request-response pattern
2. **API Gateway** - Setup API gateway for routing
3. **Error Handling** - Add basic error handling
4. **Monitoring** - Implement basic metrics collection

### **Phase 2: Advanced Patterns (Weeks 3-4)**
1. **Pub-Sub** - Implement publish-subscribe pattern
2. **Message Queues** - Add message queue support
3. **Circuit Breaker** - Implement circuit breaker pattern
4. **Retry Logic** - Add retry mechanisms

### **Phase 3: Optimization (Weeks 5-6)**
1. **Load Balancing** - Implement load balancing
2. **Performance Tuning** - Optimize communication performance
3. **Advanced Monitoring** - Add comprehensive monitoring
4. **Testing** - Implement comprehensive testing

### **Phase 4: Production (Weeks 7-8)**
1. **Production Deployment** - Deploy to production
2. **Performance Monitoring** - Monitor production performance
3. **Issue Resolution** - Address production issues
4. **Continuous Improvement** - Ongoing optimization

---

## 🔗 **RELATED PATTERNS**

### **Complementary Patterns**
- **[Event-Driven Patterns](EVENT_DRIVEN_PATTERNS.md)** - Event-based communication
- **[Coordination Patterns](COORDINATION_PATTERNS.md)** - Service coordination
- **[Orchestration Patterns](ORCHESTRATION_PATTERNS.md)** - Workflow orchestration
- **[Async Patterns](ASYNC_PATTERNS.md)** - Asynchronous programming

### **Architecture Patterns**
- **[API Design Patterns](API_DESIGN_PATTERNS.md)** - API design and implementation
- **[Database Patterns](DATABASE_PATTERNS.md)** - Data persistence patterns
- **[Caching Patterns](CACHING_PATTERNS.md)** - Caching strategies
- **[Logging Patterns](LOGGING_PATTERNS.md)** - Logging and monitoring

---

**Last Updated:** September 6, 2025  
**Communication Patterns Version:** 3.0.0  
**Status:** ✅ **PRODUCTION READY**

**COMMUNICATION PATTERNS COMPLETE!**

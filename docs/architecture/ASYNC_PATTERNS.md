# ⚡ **ASYNC PATTERNS & TECHNIQUES**

**Version:** 3.0.0  
**Last Updated:** September 6, 2025  
**Status:** ✅ **PRODUCTION-READY ASYNC ARCHITECTURE**

---

## 🎯 **ASYNC ARCHITECTURE PHILOSOPHY**

The Data Vault Obsidian async architecture implements **Event-Driven Programming** with **Coroutine Management**, **Async/Await Patterns**, and **Concurrent Processing** to maximize performance and responsiveness across the microservices ecosystem.

### **Core Async Principles**

- **Non-Blocking I/O** - Asynchronous operations for better performance
- **Event-Driven Architecture** - Reactive programming patterns
- **Coroutine Management** - Efficient task scheduling and execution
- **Concurrent Processing** - Parallel execution of independent tasks
- **Resource Pooling** - Efficient resource utilization
- **Error Handling** - Robust async error management
- **Backpressure Control** - Flow control for high-load scenarios

---

## 🏗️ **ASYNC ARCHITECTURE PATTERNS**

### **1. Async Context Manager Pattern**

#### **Resource Management**
```python
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
import time

class AsyncResourceManager:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.semaphore = asyncio.Semaphore(max_connections)
        self.active_connections = 0
        self.connection_pool = asyncio.Queue(maxsize=max_connections)
        self._initialize_pool()
    
    async def _initialize_pool(self):
        """Initialize connection pool"""
        for _ in range(self.max_connections):
            connection = await self._create_connection()
            await self.connection_pool.put(connection)
    
    async def _create_connection(self) -> Any:
        """Create new connection (placeholder)"""
        await asyncio.sleep(0.01)  # Simulate connection creation
        return f"connection_{id(self)}"
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Any, None]:
        """Get connection from pool with automatic cleanup"""
        async with self.semaphore:
            connection = await self.connection_pool.get()
            self.active_connections += 1
            
            try:
                yield connection
            finally:
                await self.connection_pool.put(connection)
                self.active_connections -= 1
    
    async def close_all(self):
        """Close all connections"""
        while not self.connection_pool.empty():
            connection = await self.connection_pool.get()
            await self._close_connection(connection)
    
    async def _close_connection(self, connection: Any):
        """Close connection (placeholder)"""
        await asyncio.sleep(0.01)  # Simulate connection closure
```

### **2. Async Producer-Consumer Pattern**

#### **Message Queue Processing**
```python
import asyncio
from asyncio import Queue
from typing import Any, Callable, Optional
import logging

class AsyncProducerConsumer:
    def __init__(self, queue_size: int = 1000, max_workers: int = 5):
        self.queue = Queue(maxsize=queue_size)
        self.max_workers = max_workers
        self.workers = []
        self.is_running = False
        self.logger = logging.getLogger(__name__)
    
    async def start(self, consumer_func: Callable[[Any], None]):
        """Start producer-consumer system"""
        self.is_running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}", consumer_func))
            self.workers.append(worker)
        
        self.logger.info(f"Started {self.max_workers} workers")
    
    async def stop(self):
        """Stop producer-consumer system"""
        self.is_running = False
        
        # Wait for queue to empty
        await self.queue.join()
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.logger.info("Stopped all workers")
    
    async def produce(self, item: Any):
        """Produce item to queue"""
        await self.queue.put(item)
    
    async def _worker(self, worker_name: str, consumer_func: Callable[[Any], None]):
        """Worker coroutine"""
        while self.is_running:
            try:
                item = await self.queue.get()
                await consumer_func(item)
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Worker {worker_name} error: {e}")
                self.queue.task_done()

# Example usage
async def process_message(message: str):
    """Process a single message"""
    await asyncio.sleep(0.1)  # Simulate processing
    print(f"Processed: {message}")

async def main():
    pc = AsyncProducerConsumer(queue_size=100, max_workers=3)
    
    # Start the system
    await pc.start(process_message)
    
    # Produce messages
    for i in range(10):
        await pc.produce(f"message-{i}")
    
    # Wait for processing to complete
    await asyncio.sleep(2)
    
    # Stop the system
    await pc.stop()
```

### **3. Async Batch Processing Pattern**

#### **Efficient Batch Operations**
```python
from typing import List, Any, Callable, Optional
import asyncio
from dataclasses import dataclass
import time

@dataclass
class BatchConfig:
    max_batch_size: int = 100
    max_wait_time: float = 1.0  # seconds
    max_concurrent_batches: int = 5

class AsyncBatchProcessor:
    def __init__(self, config: BatchConfig):
        self.config = config
        self.pending_items = []
        self.batch_lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(config.max_concurrent_batches)
        self.is_running = False
        self.batch_task = None
    
    async def start(self):
        """Start batch processing"""
        self.is_running = True
        self.batch_task = asyncio.create_task(self._batch_loop())
    
    async def stop(self):
        """Stop batch processing"""
        self.is_running = False
        if self.batch_task:
            self.batch_task.cancel()
            try:
                await self.batch_task
            except asyncio.CancelledError:
                pass
    
    async def add_item(self, item: Any):
        """Add item to batch queue"""
        async with self.batch_lock:
            self.pending_items.append(item)
    
    async def _batch_loop(self):
        """Main batch processing loop"""
        while self.is_running:
            try:
                # Wait for batch conditions
                await self._wait_for_batch_conditions()
                
                # Process batch if items available
                async with self.batch_lock:
                    if self.pending_items:
                        batch = self.pending_items[:self.config.max_batch_size]
                        self.pending_items = self.pending_items[self.config.max_batch_size:]
                        
                        # Process batch asynchronously
                        asyncio.create_task(self._process_batch(batch))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Batch loop error: {e}")
                await asyncio.sleep(1)
    
    async def _wait_for_batch_conditions(self):
        """Wait for batch to be ready"""
        start_time = time.time()
        
        while self.is_running:
            async with self.batch_lock:
                if (len(self.pending_items) >= self.config.max_batch_size or
                    (self.pending_items and time.time() - start_time >= self.config.max_wait_time)):
                    return
            
            await asyncio.sleep(0.01)
    
    async def _process_batch(self, batch: List[Any]):
        """Process a batch of items"""
        async with self.semaphore:
            try:
                # Simulate batch processing
                await asyncio.sleep(0.1)
                print(f"Processed batch of {len(batch)} items")
            except Exception as e:
                print(f"Batch processing error: {e}")

# Example usage
async def example_batch_processing():
    processor = AsyncBatchProcessor(BatchConfig(max_batch_size=5, max_wait_time=0.5))
    
    await processor.start()
    
    # Add items
    for i in range(20):
        await processor.add_item(f"item-{i}")
        await asyncio.sleep(0.05)
    
    # Wait for processing
    await asyncio.sleep(3)
    
    await processor.stop()
```

### **4. Async Circuit Breaker Pattern**

#### **Fault Tolerance**
```python
import asyncio
from enum import Enum
from typing import Callable, Any, Optional
import time
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 3

class AsyncCircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        async with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    async def _on_success(self):
        """Handle successful operation"""
        async with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
            elif self.state == CircuitState.CLOSED:
                self.failure_count = max(0, self.failure_count - 1)
    
    async def _on_failure(self):
        """Handle failed operation"""
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.state == CircuitState.CLOSED and self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
    
    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time
        }

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

# Example usage
async def unreliable_service_call():
    """Simulate unreliable service call"""
    import random
    if random.random() < 0.7:  # 70% failure rate
        raise Exception("Service unavailable")
    return "Success"

async def example_circuit_breaker():
    config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=5.0)
    breaker = AsyncCircuitBreaker(config)
    
    for i in range(10):
        try:
            result = await breaker.call(unreliable_service_call)
            print(f"Call {i}: {result}")
        except CircuitBreakerOpenError:
            print(f"Call {i}: Circuit breaker open")
        except Exception as e:
            print(f"Call {i}: {e}")
        
        await asyncio.sleep(1)
```

### **5. Async Rate Limiting Pattern**

#### **Request Throttling**
```python
import asyncio
import time
from typing import Dict, Optional
from collections import defaultdict, deque

class AsyncRateLimiter:
    def __init__(self, requests_per_second: float = 10.0, burst_size: int = 20):
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens for request"""
        async with self.lock:
            now = time.time()
            time_passed = now - self.last_update
            
            # Add tokens based on time passed
            self.tokens = min(self.burst_size, self.tokens + time_passed * self.requests_per_second)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    async def wait_for_token(self, tokens: int = 1) -> None:
        """Wait until tokens are available"""
        while not await self.acquire(tokens):
            await asyncio.sleep(0.01)

class AsyncSlidingWindowRateLimiter:
    def __init__(self, window_size: float = 60.0, max_requests: int = 100):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
        self.lock = asyncio.Lock()
    
    async def is_allowed(self) -> bool:
        """Check if request is allowed"""
        async with self.lock:
            now = time.time()
            
            # Remove old requests outside window
            while self.requests and self.requests[0] <= now - self.window_size:
                self.requests.popleft()
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    async def wait_for_allowance(self) -> None:
        """Wait until request is allowed"""
        while not await self.is_allowed():
            await asyncio.sleep(0.01)

# Example usage
async def example_rate_limiting():
    # Token bucket rate limiter
    limiter = AsyncRateLimiter(requests_per_second=5.0, burst_size=10)
    
    async def make_request(request_id: int):
        await limiter.wait_for_token()
        print(f"Request {request_id} processed")
    
    # Make multiple requests
    tasks = [make_request(i) for i in range(20)]
    await asyncio.gather(*tasks)
```

### **6. Async Retry Pattern**

#### **Resilient Operations**
```python
import asyncio
import random
from typing import Callable, Any, Optional, List
from dataclasses import dataclass

@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple = (Exception,)

class AsyncRetry:
    def __init__(self, config: RetryConfig):
        self.config = config
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
            except self.config.retryable_exceptions as e:
                last_exception = e
                
                if attempt == self.config.max_attempts - 1:
                    raise e
                
                delay = self._calculate_delay(attempt)
                await asyncio.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            # Add random jitter to prevent thundering herd
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter
        
        return delay

# Example usage
async def unreliable_operation():
    """Simulate unreliable operation"""
    import random
    if random.random() < 0.8:  # 80% failure rate
        raise Exception("Operation failed")
    return "Success"

async def example_retry():
    config = RetryConfig(max_attempts=5, base_delay=0.5)
    retry = AsyncRetry(config)
    
    try:
        result = await retry.execute(unreliable_operation)
        print(f"Operation succeeded: {result}")
    except Exception as e:
        print(f"Operation failed after retries: {e}")
```

### **7. Async Monitoring Pattern**

#### **Performance Tracking**
```python
import asyncio
import time
from typing import Dict, Any, List
from dataclasses import dataclass
from collections import defaultdict, deque

@dataclass
class AsyncMetrics:
    operation_name: str
    duration: float
    success: bool
    timestamp: float
    error_message: Optional[str] = None

class AsyncMonitor:
    def __init__(self, max_metrics: int = 1000):
        self.max_metrics = max_metrics
        self.metrics = deque(maxlen=max_metrics)
        self.operation_stats = defaultdict(lambda: {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_duration": 0.0,
            "min_duration": float('inf'),
            "max_duration": 0.0
        })
        self.lock = asyncio.Lock()
    
    async def record_operation(self, operation_name: str, duration: float, 
                             success: bool, error_message: Optional[str] = None):
        """Record operation metrics"""
        async with self.lock:
            metric = AsyncMetrics(
                operation_name=operation_name,
                duration=duration,
                success=success,
                timestamp=time.time(),
                error_message=error_message
            )
            
            self.metrics.append(metric)
            
            # Update operation stats
            stats = self.operation_stats[operation_name]
            stats["total_calls"] += 1
            stats["total_duration"] += duration
            stats["min_duration"] = min(stats["min_duration"], duration)
            stats["max_duration"] = max(stats["max_duration"], duration)
            
            if success:
                stats["successful_calls"] += 1
            else:
                stats["failed_calls"] += 1
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get statistics for specific operation"""
        stats = self.operation_stats[operation_name]
        
        if stats["total_calls"] == 0:
            return {"message": "No calls recorded"}
        
        avg_duration = stats["total_duration"] / stats["total_calls"]
        success_rate = stats["successful_calls"] / stats["total_calls"]
        
        return {
            "operation_name": operation_name,
            "total_calls": stats["total_calls"],
            "successful_calls": stats["successful_calls"],
            "failed_calls": stats["failed_calls"],
            "success_rate": f"{success_rate:.2%}",
            "avg_duration": f"{avg_duration:.3f}s",
            "min_duration": f"{stats['min_duration']:.3f}s",
            "max_duration": f"{stats['max_duration']:.3f}s"
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all operations"""
        return {
            operation: self.get_operation_stats(operation)
            for operation in self.operation_stats.keys()
        }

# Decorator for automatic monitoring
def monitor_async(monitor: AsyncMonitor, operation_name: str):
    """Decorator to monitor async operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_message = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                duration = time.time() - start_time
                await monitor.record_operation(operation_name, duration, success, error_message)
        
        return wrapper
    return decorator

# Example usage
async def example_monitoring():
    monitor = AsyncMonitor()
    
    @monitor_async(monitor, "database_query")
    async def database_query():
        await asyncio.sleep(0.1)
        return "Query result"
    
    @monitor_async(monitor, "api_call")
    async def api_call():
        await asyncio.sleep(0.2)
        return "API response"
    
    # Execute operations
    await database_query()
    await api_call()
    
    # Print statistics
    print("Operation Statistics:")
    for operation, stats in monitor.get_all_stats().items():
        print(f"{operation}: {stats}")
```

---

## 🚀 **ASYNC OPTIMIZATION PATTERNS**

### **1. Connection Pooling**
```python
class AsyncConnectionPool:
    def __init__(self, factory: Callable, max_size: int = 10):
        self.factory = factory
        self.max_size = max_size
        self.pool = asyncio.Queue(maxsize=max_size)
        self.created_connections = 0
        self.lock = asyncio.Lock()
    
    async def get_connection(self):
        """Get connection from pool"""
        if not self.pool.empty():
            return await self.pool.get()
        
        async with self.lock:
            if self.created_connections < self.max_size:
                connection = await self.factory()
                self.created_connections += 1
                return connection
        
        return await self.pool.get()
    
    async def return_connection(self, connection):
        """Return connection to pool"""
        await self.pool.put(connection)
```

### **2. Async Caching**
```python
class AsyncCache:
    def __init__(self, ttl: float = 300.0):
        self.cache = {}
        self.ttl = ttl
        self.timestamps = {}
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self.lock:
            if key in self.cache and time.time() - self.timestamps[key] < self.ttl:
                return self.cache[key]
            return None
    
    async def set(self, key: str, value: Any):
        """Set value in cache"""
        async with self.lock:
            self.cache[key] = value
            self.timestamps[key] = time.time()
```

---

**Last Updated:** September 6, 2025  
**Async Patterns Version:** 3.0.0  
**Status:** ✅ **PRODUCTION-READY**

**COMPREHENSIVE ASYNC PATTERNS COMPLETE!**

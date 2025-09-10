# 📝 **LOGGING PATTERNS & TECHNIQUES**

**Version:** 3.0.0  
**Last Updated:** September 6, 2025  
**Status:** ✅ **PRODUCTION-READY LOGGING ARCHITECTURE**

---

## 🎯 **LOGGING ARCHITECTURE PHILOSOPHY**

The Data Vault Obsidian logging architecture implements **Structured Logging** with **Centralized Aggregation**, **Real-time Monitoring**, and **Intelligent Analysis** to provide comprehensive observability across the microservices ecosystem.

### **Core Logging Principles**

- **Structured Logging** - JSON-based log format for machine readability
- **Centralized Aggregation** - Single point for log collection and analysis
- **Real-time Processing** - Immediate log processing and alerting
- **Context Preservation** - Maintain request context across services
- **Performance Optimization** - Minimal impact on application performance
- **Security & Compliance** - Secure log handling and retention policies
- **Intelligent Analysis** - AI-powered log analysis and insights

---

## 🏗️ **LOGGING ARCHITECTURE PATTERNS**

### **1. Structured Logging Pattern**

#### **JSON-Based Logging**
```python
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LogEntry:
    timestamp: str
    level: str
    service: str
    message: str
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None

class StructuredLogger:
    def __init__(self, service_name: str, log_level: LogLevel = LogLevel.INFO):
        self.service_name = service_name
        self.log_level = log_level
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Configure JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def log(self, level: LogLevel, message: str, **kwargs):
        """Log structured message"""
        log_entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level=level.value,
            service=self.service_name,
            message=message,
            **kwargs
        )
        
        # Convert to appropriate log level
        log_level = getattr(logging, level.value)
        self.logger.log(log_level, json.dumps(asdict(log_entry)))
    
    def debug(self, message: str, **kwargs):
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self.log(LogLevel.CRITICAL, message, **kwargs)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return record.getMessage()
```

### **2. Context-Aware Logging Pattern**

#### **Request Context Preservation**
```python
import contextvars
from typing import Optional, Dict, Any
import uuid

# Context variables for request tracking
request_id_var = contextvars.ContextVar('request_id', default=None)
user_id_var = contextvars.ContextVar('user_id', default=None)
correlation_id_var = contextvars.ContextVar('correlation_id', default=None)

class ContextAwareLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = StructuredLogger(service_name)
    
    def log_with_context(self, level: LogLevel, message: str, **kwargs):
        """Log message with current context"""
        context_data = {
            'request_id': request_id_var.get(),
            'user_id': user_id_var.get(),
            'correlation_id': correlation_id_var.get()
        }
        
        # Merge context data with provided kwargs
        context_data.update(kwargs)
        
        self.logger.log(level, message, **context_data)
    
    def set_request_context(self, request_id: str, user_id: str = None, correlation_id: str = None):
        """Set request context for current execution"""
        request_id_var.set(request_id)
        if user_id:
            user_id_var.set(user_id)
        if correlation_id:
            correlation_id_var.set(correlation_id)
    
    def clear_context(self):
        """Clear current request context"""
        request_id_var.set(None)
        user_id_var.set(None)
        correlation_id_var.set(None)

# Context manager for request tracking
class RequestContext:
    def __init__(self, request_id: str = None, user_id: str = None, correlation_id: str = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.logger = ContextAwareLogger("request_context")
    
    def __enter__(self):
        self.logger.set_request_context(
            self.request_id, 
            self.user_id, 
            self.correlation_id
        )
        self.logger.log_with_context(LogLevel.INFO, "Request started")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.log_with_context(
                LogLevel.ERROR, 
                "Request failed", 
                error_type=str(exc_type),
                error_message=str(exc_val)
            )
        else:
            self.logger.log_with_context(LogLevel.INFO, "Request completed")
        
        self.logger.clear_context()
```

### **3. Distributed Logging Pattern**

#### **Centralized Log Aggregation**
```python
import asyncio
import aiohttp
from typing import List, Dict, Any
from dataclasses import asdict
import json

class LogAggregator:
    def __init__(self, log_endpoint: str, batch_size: int = 100, flush_interval: float = 5.0):
        self.log_endpoint = log_endpoint
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.log_buffer = []
        self.buffer_lock = asyncio.Lock()
        self.flush_task = None
        self.is_running = False
    
    async def start(self):
        """Start log aggregation service"""
        self.is_running = True
        self.flush_task = asyncio.create_task(self._flush_loop())
    
    async def stop(self):
        """Stop log aggregation service"""
        self.is_running = False
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining logs
        await self._flush_logs()
    
    async def add_log(self, log_entry: LogEntry):
        """Add log entry to buffer"""
        async with self.buffer_lock:
            self.log_buffer.append(asdict(log_entry))
            
            if len(self.log_buffer) >= self.batch_size:
                await self._flush_logs()
    
    async def _flush_loop(self):
        """Periodic log flushing"""
        while self.is_running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_logs()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Log flush error: {e}")
    
    async def _flush_logs(self):
        """Flush logs to central endpoint"""
        if not self.log_buffer:
            return
        
        async with self.buffer_lock:
            logs_to_send = self.log_buffer.copy()
            self.log_buffer.clear()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.log_endpoint,
                    json={"logs": logs_to_send},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        print(f"Log aggregation failed: {response.status}")
        except Exception as e:
            print(f"Log aggregation error: {e}")

class DistributedLogger:
    def __init__(self, service_name: str, aggregator: LogAggregator):
        self.service_name = service_name
        self.aggregator = aggregator
        self.context_logger = ContextAwareLogger(service_name)
    
    async def log(self, level: LogLevel, message: str, **kwargs):
        """Log message to distributed system"""
        # Log locally
        self.context_logger.log_with_context(level, message, **kwargs)
        
        # Send to aggregator
        log_entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level=level.value,
            service=self.service_name,
            message=message,
            **kwargs
        )
        
        await self.aggregator.add_log(log_entry)
```

### **4. Log Analysis Pattern**

#### **Intelligent Log Processing**
```python
import re
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
import json

class LogAnalyzer:
    def __init__(self):
        self.error_patterns = [
            r"ERROR.*?(\w+Error)",
            r"Exception.*?(\w+Exception)",
            r"Failed.*?(\w+)",
            r"Timeout.*?(\w+)"
        ]
        self.performance_patterns = [
            r"duration.*?(\d+\.?\d*)\s*ms",
            r"response_time.*?(\d+\.?\d*)\s*s",
            r"execution_time.*?(\d+\.?\d*)\s*ms"
        ]
    
    def analyze_logs(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze logs for patterns and insights"""
        analysis = {
            "error_analysis": self._analyze_errors(logs),
            "performance_analysis": self._analyze_performance(logs),
            "frequency_analysis": self._analyze_frequency(logs),
            "correlation_analysis": self._analyze_correlations(logs),
            "trend_analysis": self._analyze_trends(logs)
        }
        
        return analysis
    
    def _analyze_errors(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze error patterns in logs"""
        error_logs = [log for log in logs if log.get("level") in ["ERROR", "CRITICAL"]]
        
        error_types = []
        error_services = defaultdict(int)
        error_messages = []
        
        for log in error_logs:
            message = log.get("message", "")
            service = log.get("service", "unknown")
            
            error_services[service] += 1
            error_messages.append(message)
            
            # Extract error types using patterns
            for pattern in self.error_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    error_types.append(match.group(1))
        
        return {
            "total_errors": len(error_logs),
            "error_types": Counter(error_types).most_common(10),
            "error_by_service": dict(error_services),
            "common_error_messages": Counter(error_messages).most_common(5)
        }
    
    def _analyze_performance(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance patterns in logs"""
        performance_metrics = []
        
        for log in logs:
            message = log.get("message", "")
            metadata = log.get("metadata", {})
            
            # Extract performance metrics
            for pattern in self.performance_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    performance_metrics.append(float(match.group(1)))
            
            # Check metadata for performance data
            if "duration" in metadata:
                performance_metrics.append(metadata["duration"])
            if "response_time" in metadata:
                performance_metrics.append(metadata["response_time"])
        
        if not performance_metrics:
            return {"message": "No performance metrics found"}
        
        return {
            "total_metrics": len(performance_metrics),
            "average_performance": sum(performance_metrics) / len(performance_metrics),
            "min_performance": min(performance_metrics),
            "max_performance": max(performance_metrics),
            "performance_distribution": self._calculate_percentiles(performance_metrics)
        }
    
    def _analyze_frequency(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze log frequency patterns"""
        service_frequency = defaultdict(int)
        level_frequency = defaultdict(int)
        hourly_frequency = defaultdict(int)
        
        for log in logs:
            service = log.get("service", "unknown")
            level = log.get("level", "unknown")
            timestamp = log.get("timestamp", "")
            
            service_frequency[service] += 1
            level_frequency[level] += 1
            
            # Extract hour from timestamp
            if timestamp:
                try:
                    hour = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).hour
                    hourly_frequency[hour] += 1
                except:
                    pass
        
        return {
            "service_frequency": dict(service_frequency),
            "level_frequency": dict(level_frequency),
            "hourly_frequency": dict(hourly_frequency)
        }
    
    def _analyze_correlations(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlations between log events"""
        # Group logs by request_id to find correlations
        request_logs = defaultdict(list)
        
        for log in logs:
            request_id = log.get("request_id")
            if request_id:
                request_logs[request_id].append(log)
        
        # Find common patterns
        error_correlations = defaultdict(int)
        service_correlations = defaultdict(int)
        
        for request_id, request_log_list in request_logs.items():
            if len(request_log_list) > 1:
                services = [log.get("service") for log in request_log_list]
                levels = [log.get("level") for log in request_log_list]
                
                # Track service correlations
                for i in range(len(services)):
                    for j in range(i + 1, len(services)):
                        service_pair = tuple(sorted([services[i], services[j]]))
                        service_correlations[service_pair] += 1
                
                # Track error correlations
                if "ERROR" in levels:
                    error_services = [log.get("service") for log in request_log_list if log.get("level") == "ERROR"]
                    for service in error_services:
                        error_correlations[service] += 1
        
        return {
            "service_correlations": dict(service_correlations),
            "error_correlations": dict(error_correlations),
            "request_traces": len(request_logs)
        }
    
    def _analyze_trends(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends over time"""
        # Group logs by time periods
        daily_logs = defaultdict(list)
        
        for log in logs:
            timestamp = log.get("timestamp", "")
            if timestamp:
                try:
                    date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
                    daily_logs[date].append(log)
                except:
                    pass
        
        # Calculate trends
        daily_counts = {date: len(logs) for date, logs in daily_logs.items()}
        daily_errors = {
            date: len([log for log in logs if log.get("level") in ["ERROR", "CRITICAL"]])
            for date, logs in daily_logs.items()
        }
        
        return {
            "daily_log_counts": daily_counts,
            "daily_error_counts": daily_errors,
            "trend_periods": len(daily_logs)
        }
    
    def _calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        """Calculate percentiles for performance metrics"""
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            "p50": sorted_values[int(n * 0.5)] if n > 0 else 0,
            "p90": sorted_values[int(n * 0.9)] if n > 0 else 0,
            "p95": sorted_values[int(n * 0.95)] if n > 0 else 0,
            "p99": sorted_values[int(n * 0.99)] if n > 0 else 0
        }
```

### **5. Log Monitoring Pattern**

#### **Real-time Log Monitoring**
```python
import asyncio
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
import time

@dataclass
class LogAlert:
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    severity: str
    message: str
    cooldown: float = 300.0  # 5 minutes

class LogMonitor:
    def __init__(self):
        self.alerts = []
        self.alert_history = {}
        self.is_running = False
        self.monitor_task = None
    
    def add_alert(self, alert: LogAlert):
        """Add log alert"""
        self.alerts.append(alert)
    
    async def start_monitoring(self, log_stream: List[Dict[str, Any]]):
        """Start monitoring log stream"""
        self.is_running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(log_stream))
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_loop(self, log_stream: List[Dict[str, Any]]):
        """Main monitoring loop"""
        while self.is_running:
            try:
                for log in log_stream:
                    await self._check_alerts(log)
                await asyncio.sleep(1)  # Check every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _check_alerts(self, log: Dict[str, Any]):
        """Check alerts against log entry"""
        for alert in self.alerts:
            try:
                if alert.condition(log):
                    await self._trigger_alert(alert, log)
            except Exception as e:
                print(f"Alert check error: {e}")
    
    async def _trigger_alert(self, alert: LogAlert, log: Dict[str, Any]):
        """Trigger alert if not in cooldown"""
        current_time = time.time()
        alert_key = f"{alert.name}_{log.get('service', 'unknown')}"
        
        if alert_key in self.alert_history:
            last_triggered = self.alert_history[alert_key]
            if current_time - last_triggered < alert.cooldown:
                return  # Still in cooldown
        
        # Trigger alert
        self.alert_history[alert_key] = current_time
        
        alert_message = f"ALERT: {alert.message}\nLog: {log}"
        print(f"[{alert.severity}] {alert_message}")
        
        # Here you would send to alerting system
        await self._send_alert(alert, log)
    
    async def _send_alert(self, alert: LogAlert, log: Dict[str, Any]):
        """Send alert to external system"""
        # Placeholder for alert sending (Slack, email, etc.)
        pass

# Example alert conditions
def error_rate_high(log: Dict[str, Any]) -> bool:
    """Check if error rate is high"""
    return log.get("level") in ["ERROR", "CRITICAL"]

def performance_degraded(log: Dict[str, Any]) -> bool:
    """Check if performance is degraded"""
    metadata = log.get("metadata", {})
    duration = metadata.get("duration", 0)
    return duration > 1000  # More than 1 second

def service_down(log: Dict[str, Any]) -> bool:
    """Check if service is down"""
    message = log.get("message", "").lower()
    return "service unavailable" in message or "connection refused" in message

# Example usage
async def example_log_monitoring():
    monitor = LogMonitor()
    
    # Add alerts
    monitor.add_alert(LogAlert(
        name="error_rate",
        condition=error_rate_high,
        severity="WARNING",
        message="High error rate detected"
    ))
    
    monitor.add_alert(LogAlert(
        name="performance",
        condition=performance_degraded,
        severity="ERROR",
        message="Performance degradation detected"
    ))
    
    monitor.add_alert(LogAlert(
        name="service_down",
        condition=service_down,
        severity="CRITICAL",
        message="Service appears to be down"
    ))
    
    # Start monitoring
    await monitor.start_monitoring([])
    
    # Stop after some time
    await asyncio.sleep(60)
    await monitor.stop_monitoring()
```

### **6. Log Security Pattern**

#### **Secure Log Handling**
```python
import re
from typing import Dict, Any, List
import hashlib
import base64

class LogSanitizer:
    def __init__(self):
        self.sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            r'api_key["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            r'token["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            r'secret["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            r'credit_card["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
            r'ssn["\']?\s*[:=]\s*["\']?([^"\']+)["\']?'
        ]
        
        self.sensitive_fields = [
            'password', 'api_key', 'token', 'secret', 'credit_card', 'ssn',
            'authorization', 'x-api-key', 'x-auth-token'
        ]
    
    def sanitize_log(self, log: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive information from log"""
        sanitized_log = log.copy()
        
        # Sanitize message
        if 'message' in sanitized_log:
            sanitized_log['message'] = self._sanitize_text(sanitized_log['message'])
        
        # Sanitize metadata
        if 'metadata' in sanitized_log:
            sanitized_log['metadata'] = self._sanitize_metadata(sanitized_log['metadata'])
        
        # Sanitize error details
        if 'error_details' in sanitized_log:
            sanitized_log['error_details'] = self._sanitize_metadata(sanitized_log['error_details'])
        
        return sanitized_log
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize sensitive information in text"""
        sanitized_text = text
        
        for pattern in self.sensitive_patterns:
            sanitized_text = re.sub(pattern, r'\1=***REDACTED***', sanitized_text, flags=re.IGNORECASE)
        
        return sanitized_text
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive information in metadata"""
        sanitized_metadata = {}
        
        for key, value in metadata.items():
            if key.lower() in self.sensitive_fields:
                sanitized_metadata[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized_metadata[key] = self._sanitize_metadata(value)
            elif isinstance(value, str):
                sanitized_metadata[key] = self._sanitize_text(value)
            else:
                sanitized_metadata[key] = value
        
        return sanitized_metadata

class SecureLogger:
    def __init__(self, service_name: str, sanitizer: LogSanitizer = None):
        self.service_name = service_name
        self.sanitizer = sanitizer or LogSanitizer()
        self.logger = StructuredLogger(service_name)
    
    def log(self, level: LogLevel, message: str, **kwargs):
        """Log message with security sanitization"""
        # Create log entry
        log_entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level=level.value,
            service=self.service_name,
            message=message,
            **kwargs
        )
        
        # Sanitize sensitive information
        sanitized_entry = self.sanitizer.sanitize_log(asdict(log_entry))
        
        # Log sanitized entry
        log_level = getattr(logging, level.value)
        self.logger.logger.log(log_level, json.dumps(sanitized_entry))
    
    def log_error(self, message: str, exception: Exception = None, **kwargs):
        """Log error with exception details"""
        error_details = {}
        if exception:
            error_details = {
                "error_type": type(exception).__name__,
                "error_message": str(exception),
                "traceback": self._get_traceback(exception)
            }
        
        self.log(LogLevel.ERROR, message, error_details=error_details, **kwargs)
    
    def _get_traceback(self, exception: Exception) -> str:
        """Get traceback string for exception"""
        import traceback
        return traceback.format_exc()
```

---

## 🚀 **LOGGING OPTIMIZATION PATTERNS**

### **1. Async Logging**
```python
import asyncio
from asyncio import Queue
from typing import Dict, Any

class AsyncLogger:
    def __init__(self, service_name: str, queue_size: int = 1000):
        self.service_name = service_name
        self.log_queue = Queue(maxsize=queue_size)
        self.is_running = False
        self.processor_task = None
    
    async def start(self):
        """Start async logging"""
        self.is_running = True
        self.processor_task = asyncio.create_task(self._process_logs())
    
    async def stop(self):
        """Stop async logging"""
        self.is_running = False
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
    
    async def log(self, level: LogLevel, message: str, **kwargs):
        """Add log to queue"""
        log_entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level=level.value,
            service=self.service_name,
            message=message,
            **kwargs
        )
        
        try:
            await self.log_queue.put(asdict(log_entry))
        except asyncio.QueueFull:
            print("Log queue full, dropping log entry")
    
    async def _process_logs(self):
        """Process logs from queue"""
        while self.is_running:
            try:
                log_entry = await asyncio.wait_for(self.log_queue.get(), timeout=1.0)
                # Process log entry (send to external system, write to file, etc.)
                print(json.dumps(log_entry))
                self.log_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Log processing error: {e}")
```

### **2. Log Compression**
```python
import gzip
import json
from typing import Dict, Any

class LogCompressor:
    def __init__(self, compression_threshold: int = 1024):
        self.compression_threshold = compression_threshold
    
    def compress_log(self, log: Dict[str, Any]) -> Dict[str, Any]:
        """Compress log if it exceeds threshold"""
        log_json = json.dumps(log)
        
        if len(log_json) > self.compression_threshold:
            compressed = gzip.compress(log_json.encode())
            return {
                "compressed": True,
                "data": base64.b64encode(compressed).decode(),
                "original_size": len(log_json)
            }
        
        return {
            "compressed": False,
            "data": log_json
        }
    
    def decompress_log(self, compressed_log: Dict[str, Any]) -> Dict[str, Any]:
        """Decompress log if it was compressed"""
        if compressed_log.get("compressed", False):
            compressed_data = base64.b64decode(compressed_log["data"])
            decompressed = gzip.decompress(compressed_data)
            return json.loads(decompressed.decode())
        
        return json.loads(compressed_log["data"])
```

---

## 🔒 **LOGGING SECURITY PATTERNS**

### **1. Log Encryption**
```python
from cryptography.fernet import Fernet
import json

class LogEncryption:
    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)
    
    def encrypt_log(self, log: Dict[str, Any]) -> str:
        """Encrypt log entry"""
        log_json = json.dumps(log)
        encrypted = self.cipher.encrypt(log_json.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_log(self, encrypted_log: str) -> Dict[str, Any]:
        """Decrypt log entry"""
        encrypted_data = base64.b64decode(encrypted_log)
        decrypted = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted.decode())
```

### **2. Log Access Control**
```python
from typing import List, Dict, Any
from enum import Enum

class LogAccessLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class LogAccessController:
    def __init__(self):
        self.access_rules = {}
        self.user_permissions = {}
    
    def set_log_access_level(self, log_pattern: str, access_level: LogAccessLevel):
        """Set access level for log pattern"""
        self.access_rules[log_pattern] = access_level
    
    def set_user_permissions(self, user_id: str, allowed_levels: List[LogAccessLevel]):
        """Set user permissions"""
        self.user_permissions[user_id] = allowed_levels
    
    def can_access_log(self, user_id: str, log: Dict[str, Any]) -> bool:
        """Check if user can access log"""
        user_levels = self.user_permissions.get(user_id, [])
        
        # Check log access level
        for pattern, access_level in self.access_rules.items():
            if self._matches_pattern(log, pattern):
                return access_level in user_levels
        
        # Default to internal access
        return LogAccessLevel.INTERNAL in user_levels
    
    def _matches_pattern(self, log: Dict[str, Any], pattern: str) -> bool:
        """Check if log matches pattern"""
        import fnmatch
        service = log.get("service", "")
        level = log.get("level", "")
        return fnmatch.fnmatch(f"{service}:{level}", pattern)
```

---

**Last Updated:** September 6, 2025  
**Logging Patterns Version:** 3.0.0  
**Status:** ✅ **PRODUCTION-READY**

**COMPREHENSIVE LOGGING PATTERNS COMPLETE!**

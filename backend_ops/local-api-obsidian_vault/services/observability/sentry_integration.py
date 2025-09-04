"""
Advanced Sentry Integration for Enhanced Error Tracking and Performance Monitoring
Comprehensive error tracking, performance monitoring, and intelligent alerting
"""

import sentry_sdk
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
import traceback
import psutil
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorContext:
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    agent_id: Optional[str] = None
    workflow_id: Optional[str] = None
    custom_tags: Dict[str, str] = None
    performance_metrics: Dict[str, Any] = None

class AdvancedSentryIntegration:
    """Advanced Sentry integration with comprehensive error tracking"""
    
    def __init__(self, 
                 dsn: str,
                 environment: str = "production",
                 release: str = "1.0.0",
                 sample_rate: float = 1.0,
                 traces_sample_rate: float = 0.1,
                 profiles_sample_rate: float = 0.1):
        
        self.dsn = dsn
        self.environment = environment
        self.release = release
        
        # Initialize Sentry
        self._initialize_sentry(sample_rate, traces_sample_rate, profiles_sample_rate)
        
        # Error tracking
        self.error_counts = {}
        self.performance_issues = []
        self.alert_thresholds = {
            'error_rate': 5.0,  # 5% error rate
            'response_time': 5000,  # 5 seconds
            'memory_usage': 90,  # 90% memory usage
            'cpu_usage': 90  # 90% CPU usage
        }
        
        logger.info("Advanced Sentry Integration initialized")
    
    def _initialize_sentry(self, sample_rate: float, traces_sample_rate: float, profiles_sample_rate: float):
        """Initialize Sentry with comprehensive integrations"""
        
        sentry_sdk.init(
            dsn=self.dsn,
            environment=self.environment,
            release=self.release,
            sample_rate=sample_rate,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            integrations=[
                FastApiIntegration(auto_enabling_instrumentations=True),
                HttpxIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
                CeleryIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                )
            ],
            before_send=self._before_send_hook,
            before_send_transaction=self._before_send_transaction_hook
        )
        
        # Set global context
        sentry_sdk.set_context("system", {
            "platform": "python",
            "version": "3.9+",
            "environment": self.environment
        })
    
    def _before_send_hook(self, event, hint):
        """Custom hook to filter and enhance events before sending to Sentry"""
        
        try:
            # Add custom context
            event.setdefault("tags", {}).update({
                "component": "observability",
                "integration": "sentry"
            })
            
            # Add performance context
            if "contexts" not in event:
                event["contexts"] = {}
            
            event["contexts"]["performance"] = {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Filter out low-severity errors in production
            if self.environment == "production":
                if event.get("level") == "info":
                    return None
            
            return event
            
        except Exception as e:
            logger.error(f"Error in before_send_hook: {e}")
            return event
    
    def _before_send_transaction_hook(self, event, hint):
        """Custom hook to filter and enhance transactions before sending to Sentry"""
        
        try:
            # Add custom transaction context
            event.setdefault("tags", {}).update({
                "transaction_type": "api_request",
                "component": "observability"
            })
            
            return event
            
        except Exception as e:
            logger.error(f"Error in before_send_transaction_hook: {e}")
            return event
    
    def capture_error(self, 
                     error: Exception, 
                     context: Optional[ErrorContext] = None,
                     severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                     additional_data: Optional[Dict[str, Any]] = None):
        """Capture error with enhanced context"""
        
        try:
            with sentry_sdk.push_scope() as scope:
                # Set error level
                scope.set_level(severity.value)
                
                # Add context
                if context:
                    if context.user_id:
                        scope.set_user({"id": context.user_id})
                    
                    if context.session_id:
                        scope.set_tag("session_id", context.session_id)
                    
                    if context.request_id:
                        scope.set_tag("request_id", context.request_id)
                    
                    if context.agent_id:
                        scope.set_tag("agent_id", context.agent_id)
                    
                    if context.workflow_id:
                        scope.set_tag("workflow_id", context.workflow_id)
                    
                    if context.custom_tags:
                        for key, value in context.custom_tags.items():
                            scope.set_tag(key, value)
                    
                    if context.performance_metrics:
                        scope.set_context("performance", context.performance_metrics)
                
                # Add additional data
                if additional_data:
                    scope.set_context("additional_data", additional_data)
                
                # Capture the error
                sentry_sdk.capture_exception(error)
                
                # Track error counts
                error_type = type(error).__name__
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
                
                logger.error(f"Error captured: {error_type} - {str(error)}")
                
        except Exception as e:
            logger.error(f"Failed to capture error: {e}")
    
    def capture_message(self, 
                       message: str, 
                       level: str = "info",
                       context: Optional[ErrorContext] = None,
                       additional_data: Optional[Dict[str, Any]] = None):
        """Capture custom message with context"""
        
        try:
            with sentry_sdk.push_scope() as scope:
                scope.set_level(level)
                
                if context:
                    if context.user_id:
                        scope.set_user({"id": context.user_id})
                    
                    if context.custom_tags:
                        for key, value in context.custom_tags.items():
                            scope.set_tag(key, value)
                
                if additional_data:
                    scope.set_context("additional_data", additional_data)
                
                sentry_sdk.capture_message(message)
                
        except Exception as e:
            logger.error(f"Failed to capture message: {e}")
    
    def start_transaction(self, 
                         operation: str,
                         name: Optional[str] = None,
                         context: Optional[ErrorContext] = None) -> sentry_sdk.Transaction:
        """Start a new transaction with context"""
        
        try:
            transaction = sentry_sdk.start_transaction(
                op=operation,
                name=name or operation
            )
            
            if context:
                with transaction:
                    if context.user_id:
                        sentry_sdk.set_user({"id": context.user_id})
                    
                    if context.custom_tags:
                        for key, value in context.custom_tags.items():
                            sentry_sdk.set_tag(key, value)
            
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to start transaction: {e}")
            return None
    
    def add_breadcrumb(self, 
                      message: str,
                      category: str = "custom",
                      level: str = "info",
                      data: Optional[Dict[str, Any]] = None):
        """Add breadcrumb for better error context"""
        
        try:
            breadcrumb = {
                "message": message,
                "category": category,
                "level": level,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if data:
                breadcrumb["data"] = data
            
            sentry_sdk.add_breadcrumb(breadcrumb)
            
        except Exception as e:
            logger.error(f"Failed to add breadcrumb: {e}")
    
    def set_user_context(self, user_id: str, **kwargs):
        """Set user context for error tracking"""
        
        try:
            sentry_sdk.set_user({
                "id": user_id,
                **kwargs
            })
            
        except Exception as e:
            logger.error(f"Failed to set user context: {e}")
    
    def set_tag(self, key: str, value: str):
        """Set custom tag for error tracking"""
        
        try:
            sentry_sdk.set_tag(key, value)
            
        except Exception as e:
            logger.error(f"Failed to set tag: {e}")
    
    def set_context(self, key: str, value: Dict[str, Any]):
        """Set custom context for error tracking"""
        
        try:
            sentry_sdk.set_context(key, value)
            
        except Exception as e:
            logger.error(f"Failed to set context: {e}")
    
    async def monitor_performance_issues(self):
        """Monitor for performance issues and create alerts"""
        
        try:
            # Check system metrics
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            
            # Check for CPU issues
            if cpu_usage > self.alert_thresholds['cpu_usage']:
                self.capture_message(
                    f"High CPU usage detected: {cpu_usage}%",
                    level="warning",
                    additional_data={
                        "cpu_usage": cpu_usage,
                        "threshold": self.alert_thresholds['cpu_usage'],
                        "alert_type": "performance"
                    }
                )
            
            # Check for memory issues
            if memory_usage > self.alert_thresholds['memory_usage']:
                self.capture_message(
                    f"High memory usage detected: {memory_usage}%",
                    level="warning",
                    additional_data={
                        "memory_usage": memory_usage,
                        "threshold": self.alert_thresholds['memory_usage'],
                        "alert_type": "performance"
                    }
                )
            
        except Exception as e:
            logger.error(f"Failed to monitor performance issues: {e}")
    
    async def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        
        try:
            # This would typically query Sentry API or your own error tracking
            # For now, return mock data
            return {
                "time_range_hours": hours,
                "total_errors": sum(self.error_counts.values()),
                "error_types": self.error_counts,
                "error_rate": self._calculate_error_rate(),
                "top_errors": sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "performance_issues": len(self.performance_issues)
            }
            
        except Exception as e:
            logger.error(f"Failed to get error summary: {e}")
            return {}
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        
        try:
            # This would typically be calculated from actual error data
            # For now, return a mock calculation
            total_requests = 1000  # Mock total requests
            total_errors = sum(self.error_counts.values())
            return (total_errors / total_requests) * 100 if total_requests > 0 else 0
            
        except Exception as e:
            logger.error(f"Failed to calculate error rate: {e}")
            return 0.0
    
    async def create_performance_alert(self, 
                                     alert_type: str,
                                     message: str,
                                     severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                                     metrics: Optional[Dict[str, Any]] = None):
        """Create a performance alert"""
        
        try:
            context = ErrorContext(
                custom_tags={
                    "alert_type": alert_type,
                    "severity": severity.value
                },
                performance_metrics=metrics
            )
            
            self.capture_message(
                f"Performance Alert: {message}",
                level=severity.value,
                context=context,
                additional_data={
                    "alert_type": alert_type,
                    "metrics": metrics or {}
                }
            )
            
            # Store performance issue
            self.performance_issues.append({
                "timestamp": datetime.utcnow(),
                "type": alert_type,
                "message": message,
                "severity": severity.value,
                "metrics": metrics
            })
            
        except Exception as e:
            logger.error(f"Failed to create performance alert: {e}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for Sentry integration"""
        
        try:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error_counts": self.error_counts,
                "performance_issues": len(self.performance_issues),
                "error_rate": self._calculate_error_rate(),
                "environment": self.environment,
                "release": self.release,
                "sentry_status": "active"
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}

# Global instance
sentry_integration = AdvancedSentryIntegration(
    dsn="your-sentry-dsn-here",
    environment="production",
    release="1.0.0"
)

# Example usage
async def main():
    """Example usage of Sentry integration"""
    
    # Capture an error
    try:
        raise ValueError("Example error for testing")
    except Exception as e:
        context = ErrorContext(
            user_id="user123",
            session_id="session456",
            agent_id="agent789",
            custom_tags={"component": "test"}
        )
        sentry_integration.capture_error(e, context, ErrorSeverity.MEDIUM)
    
    # Capture a message
    sentry_integration.capture_message(
        "System performance is optimal",
        level="info",
        additional_data={"cpu_usage": 45.2, "memory_usage": 67.8}
    )
    
    # Monitor performance
    await sentry_integration.monitor_performance_issues()
    
    # Get dashboard data
    dashboard_data = sentry_integration.get_dashboard_data()
    print("Dashboard Data:", json.dumps(dashboard_data, indent=2))

if __name__ == "__main__":
    asyncio.run(main())

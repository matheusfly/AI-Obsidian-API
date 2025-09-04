"""
Advanced MCP Tools Integration for Enhanced Observability
Comprehensive integration with MCP tools for robust observability setup
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import httpx
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPToolStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class MCPToolMetrics:
    tool_name: str
    status: MCPToolStatus
    response_time_ms: float
    success_count: int
    error_count: int
    last_used: datetime
    total_calls: int
    average_response_time: float
    error_rate: float

@dataclass
class MCPToolResult:
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    response_time_ms: float = 0.0
    metadata: Dict[str, Any] = None

class AdvancedMCPToolsIntegration:
    """Advanced MCP Tools Integration for comprehensive observability"""
    
    def __init__(self, 
                 mcp_server_url: str = "http://localhost:3000",
                 timeout_seconds: int = 30,
                 max_retries: int = 3,
                 prometheus_port: int = 8003):
        
        self.mcp_server_url = mcp_server_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.prometheus_port = prometheus_port
        
        # MCP Tools registry
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        self.tool_metrics: Dict[str, MCPToolMetrics] = {}
        self.tool_results: List[MCPToolResult] = []
        
        # Prometheus metrics
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
        # Tool execution tracking
        self.active_executions: Dict[str, datetime] = {}
        
        logger.info("Advanced MCP Tools Integration initialized")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for MCP tools monitoring"""
        
        # Tool execution metrics
        self.tool_executions_total = Counter(
            'mcp_tool_executions_total',
            'Total MCP tool executions',
            ['tool_name', 'status'],
            registry=self.registry
        )
        
        self.tool_response_time = Histogram(
            'mcp_tool_response_time_seconds',
            'MCP tool response time in seconds',
            ['tool_name'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        self.tool_errors_total = Counter(
            'mcp_tool_errors_total',
            'Total MCP tool errors',
            ['tool_name', 'error_type'],
            registry=self.registry
        )
        
        self.tool_availability = Gauge(
            'mcp_tool_availability',
            'MCP tool availability (1=available, 0=unavailable)',
            ['tool_name'],
            registry=self.registry
        )
        
        # System metrics
        self.active_tools_gauge = Gauge(
            'mcp_active_tools',
            'Number of active MCP tools',
            registry=self.registry
        )
        
        self.tool_success_rate = Gauge(
            'mcp_tool_success_rate',
            'MCP tool success rate percentage',
            ['tool_name'],
            registry=self.registry
        )
    
    async def discover_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Discover available MCP tools from the server"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(f"{self.mcp_server_url}/tools")
                
                if response.status_code == 200:
                    tools_data = response.json()
                    self.available_tools = tools_data.get("tools", {})
                    
                    # Initialize metrics for new tools
                    for tool_name in self.available_tools.keys():
                        if tool_name not in self.tool_metrics:
                            self.tool_metrics[tool_name] = MCPToolMetrics(
                                tool_name=tool_name,
                                status=MCPToolStatus.AVAILABLE,
                                response_time_ms=0.0,
                                success_count=0,
                                error_count=0,
                                last_used=datetime.utcnow(),
                                total_calls=0,
                                average_response_time=0.0,
                                error_rate=0.0
                            )
                    
                    logger.info(f"Discovered {len(self.available_tools)} MCP tools")
                    return self.available_tools
                
                else:
                    logger.error(f"Failed to discover tools: {response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Failed to discover MCP tools: {e}")
            return {}
    
    async def execute_tool(self, 
                          tool_name: str, 
                          parameters: Dict[str, Any],
                          timeout: Optional[int] = None) -> MCPToolResult:
        """Execute an MCP tool with comprehensive monitoring"""
        
        start_time = time.time()
        execution_id = f"{tool_name}_{int(start_time)}"
        
        try:
            # Track active execution
            self.active_executions[execution_id] = datetime.utcnow()
            
            # Check if tool is available
            if tool_name not in self.available_tools:
                await self.discover_available_tools()
            
            if tool_name not in self.available_tools:
                result = MCPToolResult(
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error="Tool not available",
                    response_time_ms=0.0
                )
                self._update_tool_metrics(tool_name, result)
                return result
            
            # Execute tool with retries
            for attempt in range(self.max_retries):
                try:
                    async with httpx.AsyncClient(timeout=timeout or self.timeout_seconds) as client:
                        response = await client.post(
                            f"{self.mcp_server_url}/tools/{tool_name}/execute",
                            json={"parameters": parameters}
                        )
                        
                        response_time_ms = (time.time() - start_time) * 1000
                        
                        if response.status_code == 200:
                            result_data = response.json()
                            result = MCPToolResult(
                                tool_name=tool_name,
                                success=True,
                                result=result_data.get("result"),
                                response_time_ms=response_time_ms,
                                metadata=result_data.get("metadata", {})
                            )
                        else:
                            result = MCPToolResult(
                                tool_name=tool_name,
                                success=False,
                                result=None,
                                error=f"HTTP {response.status_code}: {response.text}",
                                response_time_ms=response_time_ms
                            )
                        
                        # Update metrics
                        self._update_tool_metrics(tool_name, result)
                        
                        # Store result
                        self.tool_results.append(result)
                        
                        # Update Prometheus metrics
                        self.tool_executions_total.labels(
                            tool_name=tool_name,
                            status="success" if result.success else "error"
                        ).inc()
                        
                        self.tool_response_time.labels(tool_name=tool_name).observe(response_time_ms / 1000)
                        
                        if not result.success:
                            self.tool_errors_total.labels(
                                tool_name=tool_name,
                                error_type="execution_error"
                            ).inc()
                        
                        return result
                
                except asyncio.TimeoutError:
                    if attempt == self.max_retries - 1:
                        result = MCPToolResult(
                            tool_name=tool_name,
                            success=False,
                            result=None,
                            error="Timeout after retries",
                            response_time_ms=(time.time() - start_time) * 1000
                        )
                        self._update_tool_metrics(tool_name, result)
                        return result
                    else:
                        await asyncio.sleep(1)  # Wait before retry
                
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        result = MCPToolResult(
                            tool_name=tool_name,
                            success=False,
                            result=None,
                            error=str(e),
                            response_time_ms=(time.time() - start_time) * 1000
                        )
                        self._update_tool_metrics(tool_name, result)
                        return result
                    else:
                        await asyncio.sleep(1)  # Wait before retry
        
        except Exception as e:
            result = MCPToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000
            )
            self._update_tool_metrics(tool_name, result)
            return result
        
        finally:
            # Clean up active execution
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    def _update_tool_metrics(self, tool_name: str, result: MCPToolResult):
        """Update metrics for a tool execution"""
        
        if tool_name not in self.tool_metrics:
            self.tool_metrics[tool_name] = MCPToolMetrics(
                tool_name=tool_name,
                status=MCPToolStatus.AVAILABLE,
                response_time_ms=0.0,
                success_count=0,
                error_count=0,
                last_used=datetime.utcnow(),
                total_calls=0,
                average_response_time=0.0,
                error_rate=0.0
            )
        
        metrics = self.tool_metrics[tool_name]
        metrics.total_calls += 1
        metrics.last_used = datetime.utcnow()
        
        if result.success:
            metrics.success_count += 1
            metrics.status = MCPToolStatus.AVAILABLE
        else:
            metrics.error_count += 1
            metrics.status = MCPToolStatus.ERROR
        
        # Update response time
        if result.response_time_ms > 0:
            metrics.response_time_ms = result.response_time_ms
            # Calculate running average
            if metrics.average_response_time == 0:
                metrics.average_response_time = result.response_time_ms
            else:
                metrics.average_response_time = (
                    (metrics.average_response_time * (metrics.total_calls - 1) + result.response_time_ms) 
                    / metrics.total_calls
                )
        
        # Calculate error rate
        metrics.error_rate = (metrics.error_count / metrics.total_calls) * 100
        
        # Update Prometheus metrics
        self.tool_availability.labels(tool_name=tool_name).set(
            1 if metrics.status == MCPToolStatus.AVAILABLE else 0
        )
        
        self.tool_success_rate.labels(tool_name=tool_name).set(
            100 - metrics.error_rate
        )
        
        self.active_tools_gauge.set(len(self.active_executions))
    
    async def execute_tool_batch(self, 
                                tool_requests: List[Dict[str, Any]],
                                max_concurrent: int = 5) -> List[MCPToolResult]:
        """Execute multiple MCP tools concurrently"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single(request):
            async with semaphore:
                return await self.execute_tool(
                    request["tool_name"],
                    request["parameters"],
                    request.get("timeout")
                )
        
        tasks = [execute_single(request) for request in tool_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(MCPToolResult(
                    tool_name=tool_requests[i]["tool_name"],
                    success=False,
                    result=None,
                    error=str(result),
                    response_time_ms=0.0
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def health_check_tools(self) -> Dict[str, Any]:
        """Perform health check on all available tools"""
        
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tools": len(self.available_tools),
            "healthy_tools": 0,
            "unhealthy_tools": 0,
            "tool_status": {}
        }
        
        for tool_name in self.available_tools.keys():
            try:
                # Simple health check - execute tool with minimal parameters
                result = await self.execute_tool(tool_name, {})
                
                if result.success:
                    health_status["healthy_tools"] += 1
                    health_status["tool_status"][tool_name] = "healthy"
                else:
                    health_status["unhealthy_tools"] += 1
                    health_status["tool_status"][tool_name] = "unhealthy"
                
            except Exception as e:
                health_status["unhealthy_tools"] += 1
                health_status["tool_status"][tool_name] = f"error: {str(e)}"
        
        return health_status
    
    async def get_tool_performance_summary(self, 
                                         tool_name: Optional[str] = None,
                                         hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for MCP tools"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter results by time and optionally by tool
        filtered_results = [
            result for result in self.tool_results
            if result.tool_name == tool_name or tool_name is None
        ]
        
        if not filtered_results:
            return {"message": "No tool executions found in the specified time window"}
        
        # Calculate summary statistics
        total_executions = len(filtered_results)
        successful_executions = len([r for r in filtered_results if r.success])
        failed_executions = total_executions - successful_executions
        
        response_times = [r.response_time_ms for r in filtered_results if r.response_time_ms > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Group by tool
        tool_summaries = {}
        for result in filtered_results:
            if result.tool_name not in tool_summaries:
                tool_summaries[result.tool_name] = {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "avg_response_time_ms": 0,
                    "success_rate": 0
                }
            
            summary = tool_summaries[result.tool_name]
            summary["total_executions"] += 1
            if result.success:
                summary["successful_executions"] += 1
            else:
                summary["failed_executions"] += 1
        
        # Calculate averages for each tool
        for tool_name, summary in tool_summaries.items():
            tool_results = [r for r in filtered_results if r.tool_name == tool_name]
            tool_response_times = [r.response_time_ms for r in tool_results if r.response_time_ms > 0]
            
            if tool_response_times:
                summary["avg_response_time_ms"] = sum(tool_response_times) / len(tool_response_times)
            
            summary["success_rate"] = (summary["successful_executions"] / summary["total_executions"]) * 100
        
        return {
            "time_window_hours": hours,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "overall_success_rate": (successful_executions / total_executions) * 100,
            "average_response_time_ms": avg_response_time,
            "tool_summaries": tool_summaries
        }
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for MCP tools"""
        
        try:
            # Get current metrics
            current_metrics = {}
            for tool_name, metrics in self.tool_metrics.items():
                current_metrics[tool_name] = {
                    "status": metrics.status.value,
                    "total_calls": metrics.total_calls,
                    "success_count": metrics.success_count,
                    "error_count": metrics.error_count,
                    "error_rate": metrics.error_rate,
                    "avg_response_time_ms": metrics.average_response_time,
                    "last_used": metrics.last_used.isoformat()
                }
            
            # Get health status
            health_status = await self.health_check_tools()
            
            # Get performance summary
            performance_summary = await self.get_tool_performance_summary()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "mcp_server_url": self.mcp_server_url,
                "available_tools": len(self.available_tools),
                "active_executions": len(self.active_executions),
                "tool_metrics": current_metrics,
                "health_status": health_status,
                "performance_summary": performance_summary
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}
    
    async def start_continuous_monitoring(self, interval_seconds: int = 60):
        """Start continuous monitoring of MCP tools"""
        
        logger.info(f"Starting continuous MCP tools monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                # Discover tools
                await self.discover_available_tools()
                
                # Health check
                health_status = await self.health_check_tools()
                
                # Log status
                logger.info(f"MCP Tools Status: {health_status['healthy_tools']}/{health_status['total_tools']} healthy")
                
                # Clean up old results (keep last 24 hours)
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.tool_results = [
                    result for result in self.tool_results
                    if hasattr(result, 'timestamp') and result.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(interval_seconds)

# Example usage
async def main():
    """Example usage of MCP Tools Integration"""
    
    mcp_integration = AdvancedMCPToolsIntegration(
        mcp_server_url="http://localhost:3000",
        timeout_seconds=30
    )
    
    # Discover tools
    await mcp_integration.discover_available_tools()
    
    # Execute a tool
    result = await mcp_integration.execute_tool(
        "echo",
        {"message": "Hello from MCP Tools Integration!"}
    )
    print("Tool Result:", result)
    
    # Get dashboard data
    dashboard_data = await mcp_integration.get_dashboard_data()
    print("Dashboard Data:", json.dumps(dashboard_data, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())

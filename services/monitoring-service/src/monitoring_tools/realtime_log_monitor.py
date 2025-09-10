#!/usr/bin/env python3
"""
Real-time Log Monitor for MCP Observability and LangSmith Tracing
Continuously monitors and captures logs from all services
"""

import asyncio
import json
import logging
import os
import requests
import time
import websockets
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import sys
import threading
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('realtime_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealTimeLogMonitor:
    """Real-time log monitoring system"""
    
    def __init__(self, max_logs=1000):
        self.max_logs = max_logs
        self.log_buffer = deque(maxlen=max_logs)
        self.is_monitoring = False
        
        # Service endpoints
        self.services = {
            "observability": "http://127.0.0.1:8002",
            "mcp_integration": "http://127.0.0.1:8003", 
            "debug_dashboard": "http://127.0.0.1:8004",
            "langgraph_studio": "http://127.0.0.1:8123"
        }
        
        # LangSmith configuration
        self.langsmith_api_key = "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"
        self.langsmith_project = "mcp-obsidian-integration"
        self.langsmith_base_url = "https://api.smith.langchain.com"
        
        # Statistics
        self.stats = {
            "start_time": datetime.now().isoformat(),
            "total_logs_captured": 0,
            "service_health_checks": 0,
            "langsmith_polls": 0,
            "errors_captured": 0
        }
    
    def add_log(self, log_entry: Dict):
        """Add log entry to buffer"""
        log_entry["timestamp"] = datetime.now().isoformat()
        log_entry["log_id"] = f"log_{int(time.time() * 1000)}"
        self.log_buffer.append(log_entry)
        self.stats["total_logs_captured"] += 1
        
        # Log to console
        level = log_entry.get("level", "INFO")
        message = log_entry.get("message", "")
        service = log_entry.get("service", "UNKNOWN")
        
        if level == "ERROR":
            logger.error(f"[{service}] {message}")
        elif level == "WARN":
            logger.warning(f"[{service}] {message}")
        else:
            logger.info(f"[{service}] {message}")
    
    async def monitor_service_health(self, service_name: str, url: str):
        """Monitor health of a specific service"""
        while self.is_monitoring:
            try:
                start_time = time.time()
                response = requests.get(f"{url}/health", timeout=5)
                response_time = time.time() - start_time
                
                health_data = response.json() if response.status_code == 200 else {}
                
                self.add_log({
                    "type": "health_check",
                    "service": service_name,
                    "url": url,
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time * 1000, 2),
                    "health_data": health_data,
                    "level": "INFO" if response.status_code == 200 else "WARN"
                })
                
                self.stats["service_health_checks"] += 1
                
            except Exception as e:
                self.add_log({
                    "type": "health_check_error",
                    "service": service_name,
                    "url": url,
                    "error": str(e),
                    "level": "ERROR"
                })
                self.stats["errors_captured"] += 1
            
            await asyncio.sleep(10)  # Check every 10 seconds
    
    async def monitor_langsmith_traces(self):
        """Monitor LangSmith traces in real-time"""
        while self.is_monitoring:
            try:
                headers = {
                    "Authorization": f"Bearer {self.langsmith_api_key}",
                    "Content-Type": "application/json"
                }
                
                # Get recent runs
                runs_url = f"{self.langsmith_base_url}/runs"
                params = {
                    "project_name": self.langsmith_project,
                    "limit": 10,
                    "order": "desc"
                }
                
                response = requests.get(runs_url, headers=headers, params=params, timeout=30)
                
                if response.status_code == 200:
                    runs_data = response.json()
                    runs = runs_data.get('data', [])
                    
                    self.add_log({
                        "type": "langsmith_traces",
                        "service": "langsmith",
                        "runs_count": len(runs),
                        "runs": runs[:5],  # Store first 5 runs
                        "level": "INFO"
                    })
                    
                    self.stats["langsmith_polls"] += 1
                else:
                    self.add_log({
                        "type": "langsmith_error",
                        "service": "langsmith",
                        "status_code": response.status_code,
                        "error": response.text,
                        "level": "ERROR"
                    })
                    self.stats["errors_captured"] += 1
                
            except Exception as e:
                self.add_log({
                    "type": "langsmith_error",
                    "service": "langsmith",
                    "error": str(e),
                    "level": "ERROR"
                })
                self.stats["errors_captured"] += 1
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def monitor_mcp_observability(self):
        """Monitor MCP observability service"""
        while self.is_monitoring:
            try:
                # Get observability metrics
                metrics_url = f"{self.services['observability']}/metrics"
                response = requests.get(metrics_url, timeout=10)
                
                if response.status_code == 200:
                    metrics = response.json()
                    self.add_log({
                        "type": "observability_metrics",
                        "service": "observability",
                        "metrics": metrics,
                        "level": "INFO"
                    })
                else:
                    self.add_log({
                        "type": "observability_error",
                        "service": "observability",
                        "status_code": response.status_code,
                        "level": "WARN"
                    })
                
            except Exception as e:
                self.add_log({
                    "type": "observability_error",
                    "service": "observability",
                    "error": str(e),
                    "level": "ERROR"
                })
                self.stats["errors_captured"] += 1
            
            await asyncio.sleep(15)  # Check every 15 seconds
    
    async def monitor_mcp_integration(self):
        """Monitor MCP integration service"""
        while self.is_monitoring:
            try:
                # Get MCP integration data
                health_url = f"{self.services['mcp_integration']}/health"
                response = requests.get(health_url, timeout=10)
                
                if response.status_code == 200:
                    health_data = response.json()
                    self.add_log({
                        "type": "mcp_integration_health",
                        "service": "mcp_integration",
                        "health_data": health_data,
                        "level": "INFO"
                    })
                else:
                    self.add_log({
                        "type": "mcp_integration_error",
                        "service": "mcp_integration",
                        "status_code": response.status_code,
                        "level": "WARN"
                    })
                
            except Exception as e:
                self.add_log({
                    "type": "mcp_integration_error",
                    "service": "mcp_integration",
                    "error": str(e),
                    "level": "ERROR"
                })
                self.stats["errors_captured"] += 1
            
            await asyncio.sleep(20)  # Check every 20 seconds
    
    async def monitor_langgraph_studio(self):
        """Monitor LangGraph Studio service"""
        while self.is_monitoring:
            try:
                # Try to get assistants or docs
                docs_url = f"{self.services['langgraph_studio']}/docs"
                response = requests.get(docs_url, timeout=10)
                
                if response.status_code == 200:
                    self.add_log({
                        "type": "langgraph_studio_health",
                        "service": "langgraph_studio",
                        "status_code": response.status_code,
                        "level": "INFO"
                    })
                else:
                    self.add_log({
                        "type": "langgraph_studio_error",
                        "service": "langgraph_studio",
                        "status_code": response.status_code,
                        "level": "WARN"
                    })
                
            except Exception as e:
                self.add_log({
                    "type": "langgraph_studio_error",
                    "service": "langgraph_studio",
                    "error": str(e),
                    "level": "ERROR"
                })
                self.stats["errors_captured"] += 1
            
            await asyncio.sleep(25)  # Check every 25 seconds
    
    async def start_monitoring(self):
        """Start real-time monitoring"""
        logger.info("🚀 Starting real-time log monitoring...")
        self.is_monitoring = True
        
        # Start all monitoring tasks
        tasks = [
            self.monitor_langsmith_traces(),
            self.monitor_mcp_observability(),
            self.monitor_mcp_integration(),
            self.monitor_langgraph_studio()
        ]
        
        # Add health check tasks for all services
        for service_name, url in self.services.items():
            tasks.append(self.monitor_service_health(service_name, url))
        
        # Run all monitoring tasks concurrently
        await asyncio.gather(*tasks)
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        logger.info("🛑 Stopping real-time log monitoring...")
        self.is_monitoring = False
    
    def get_recent_logs(self, count: int = 50) -> List[Dict]:
        """Get recent logs from buffer"""
        return list(self.log_buffer)[-count:]
    
    def get_logs_by_service(self, service: str) -> List[Dict]:
        """Get logs for a specific service"""
        return [log for log in self.log_buffer if log.get("service") == service]
    
    def get_logs_by_type(self, log_type: str) -> List[Dict]:
        """Get logs of a specific type"""
        return [log for log in self.log_buffer if log.get("type") == log_type]
    
    def get_error_logs(self) -> List[Dict]:
        """Get all error logs"""
        return [log for log in self.log_buffer if log.get("level") == "ERROR"]
    
    def save_logs_to_file(self, filename: str = None) -> str:
        """Save current logs to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"realtime_logs_{timestamp}.json"
        
        try:
            logs_data = {
                "metadata": {
                    "capture_start": self.stats["start_time"],
                    "total_logs": self.stats["total_logs_captured"],
                    "health_checks": self.stats["service_health_checks"],
                    "langsmith_polls": self.stats["langsmith_polls"],
                    "errors": self.stats["errors_captured"],
                    "saved_at": datetime.now().isoformat()
                },
                "logs": list(self.log_buffer)
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(logs_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Logs saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving logs: {e}")
            return ""
    
    def print_statistics(self):
        """Print monitoring statistics"""
        print("\n📊 MONITORING STATISTICS:")
        print("=" * 40)
        print(f"Start Time: {self.stats['start_time']}")
        print(f"Total Logs: {self.stats['total_logs_captured']}")
        print(f"Health Checks: {self.stats['service_health_checks']}")
        print(f"LangSmith Polls: {self.stats['langsmith_polls']}")
        print(f"Errors Captured: {self.stats['errors_captured']}")
        print(f"Buffer Size: {len(self.log_buffer)}/{self.max_logs}")
        
        # Service-specific stats
        print("\n🔍 SERVICE LOGS:")
        for service in self.services.keys():
            service_logs = self.get_logs_by_service(service)
            error_logs = [log for log in service_logs if log.get("level") == "ERROR"]
            print(f"  {service}: {len(service_logs)} logs, {len(error_logs)} errors")

async def main():
    """Main execution function"""
    print("🚀 REAL-TIME LOG MONITOR")
    print("=" * 50)
    print("Press Ctrl+C to stop monitoring and save logs")
    print()
    
    # Initialize monitor
    monitor = RealTimeLogMonitor(max_logs=2000)
    
    try:
        # Start monitoring
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
        monitor.stop_monitoring()
        
        # Print statistics
        monitor.print_statistics()
        
        # Save logs
        filename = monitor.save_logs_to_file()
        
        # Print recent error logs
        error_logs = monitor.get_error_logs()
        if error_logs:
            print(f"\n❌ RECENT ERRORS ({len(error_logs)}):")
            for log in error_logs[-10:]:  # Last 10 errors
                print(f"  [{log.get('timestamp', 'N/A')}] {log.get('service', 'UNKNOWN')}: {log.get('message', log.get('error', 'Unknown error'))}")
        
        print(f"\n💾 All logs saved to: {filename}")
        print("✅ Monitoring session completed!")

if __name__ == "__main__":
    asyncio.run(main())

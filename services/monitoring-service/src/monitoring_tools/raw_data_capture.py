#!/usr/bin/env python3
"""
Raw Data Capture System for MCP Observability and LangSmith Tracing
Captures comprehensive logs, metrics, and tracing data from all services
"""

import asyncio
import json
import logging
import os
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('raw_data_capture.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RawDataCapture:
    """Comprehensive raw data capture system"""
    
    def __init__(self):
        self.capture_data = {
            "timestamp": datetime.now().isoformat(),
            "langsmith_traces": [],
            "mcp_observability_logs": [],
            "mcp_integration_logs": [],
            "debug_dashboard_logs": [],
            "langgraph_studio_logs": [],
            "system_metrics": {},
            "network_traces": [],
            "error_logs": []
        }
        
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
        
    async def capture_langsmith_traces(self) -> List[Dict]:
        """Capture raw LangSmith tracing data"""
        logger.info("🔍 Capturing LangSmith traces...")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.langsmith_api_key}",
                "Content-Type": "application/json"
            }
            
            # Get runs from LangSmith
            runs_url = f"{self.langsmith_base_url}/runs"
            params = {
                "project_name": self.langsmith_project,
                "limit": 50,
                "order": "desc"
            }
            
            response = requests.get(runs_url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                runs_data = response.json()
                logger.info(f"✅ Captured {len(runs_data.get('data', []))} LangSmith runs")
                
                # Get detailed trace data for each run
                detailed_traces = []
                for run in runs_data.get('data', [])[:10]:  # Limit to 10 most recent
                    run_id = run.get('id')
                    if run_id:
                        trace_data = await self.get_detailed_trace(run_id, headers)
                        detailed_traces.append(trace_data)
                
                return detailed_traces
            else:
                logger.error(f"❌ LangSmith API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error capturing LangSmith traces: {e}")
            return []
    
    async def get_detailed_trace(self, run_id: str, headers: Dict) -> Dict:
        """Get detailed trace data for a specific run"""
        try:
            # Get run details
            run_url = f"{self.langsmith_base_url}/runs/{run_id}"
            run_response = requests.get(run_url, headers=headers, timeout=30)
            
            # Get run events
            events_url = f"{self.langsmith_base_url}/runs/{run_id}/events"
            events_response = requests.get(events_url, headers=headers, timeout=30)
            
            trace_data = {
                "run_id": run_id,
                "run_details": run_response.json() if run_response.status_code == 200 else {},
                "events": events_response.json() if events_response.status_code == 200 else [],
                "captured_at": datetime.now().isoformat()
            }
            
            return trace_data
            
        except Exception as e:
            logger.error(f"❌ Error getting detailed trace for {run_id}: {e}")
            return {"run_id": run_id, "error": str(e)}
    
    async def capture_mcp_observability_logs(self) -> List[Dict]:
        """Capture raw MCP observability server logs"""
        logger.info("📊 Capturing MCP observability logs...")
        
        try:
            # Get observability metrics
            metrics_url = f"{self.services['observability']}/metrics"
            response = requests.get(metrics_url, timeout=10)
            
            if response.status_code == 200:
                metrics_data = response.json()
                logger.info("✅ Captured MCP observability metrics")
                
                # Get observability logs
                logs_url = f"{self.services['observability']}/logs"
                logs_response = requests.get(logs_url, timeout=10)
                
                logs_data = logs_response.json() if logs_response.status_code == 200 else []
                
                return {
                    "metrics": metrics_data,
                    "logs": logs_data,
                    "captured_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Observability server error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error capturing MCP observability logs: {e}")
            return []
    
    async def capture_mcp_integration_logs(self) -> List[Dict]:
        """Capture raw MCP integration server logs"""
        logger.info("🔗 Capturing MCP integration logs...")
        
        try:
            # Get MCP integration health and logs
            health_url = f"{self.services['mcp_integration']}/health"
            health_response = requests.get(health_url, timeout=10)
            
            # Get MCP servers list
            servers_url = f"{self.services['mcp_integration']}/mcp/servers"
            servers_response = requests.get(servers_url, timeout=10)
            
            # Get MCP tools
            tools_url = f"{self.services['mcp_integration']}/mcp/tools"
            tools_response = requests.get(tools_url, timeout=10)
            
            integration_data = {
                "health": health_response.json() if health_response.status_code == 200 else {},
                "servers": servers_response.json() if servers_response.status_code == 200 else {},
                "tools": tools_response.json() if tools_response.status_code == 200 else {},
                "captured_at": datetime.now().isoformat()
            }
            
            logger.info("✅ Captured MCP integration data")
            return integration_data
            
        except Exception as e:
            logger.error(f"❌ Error capturing MCP integration logs: {e}")
            return []
    
    async def capture_debug_dashboard_logs(self) -> List[Dict]:
        """Capture raw debug dashboard logs"""
        logger.info("🐛 Capturing debug dashboard logs...")
        
        try:
            # Get debug dashboard data
            dashboard_url = f"{self.services['debug_dashboard']}/debug/data"
            response = requests.get(dashboard_url, timeout=10)
            
            if response.status_code == 200:
                dashboard_data = response.json()
                logger.info("✅ Captured debug dashboard data")
                return dashboard_data
            else:
                logger.error(f"❌ Debug dashboard error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error capturing debug dashboard logs: {e}")
            return []
    
    async def capture_langgraph_studio_logs(self) -> List[Dict]:
        """Capture raw LangGraph Studio logs"""
        logger.info("🎨 Capturing LangGraph Studio logs...")
        
        try:
            # Get LangGraph Studio assistants
            assistants_url = f"{self.services['langgraph_studio']}/assistants"
            response = requests.get(assistants_url, timeout=10)
            
            if response.status_code == 200:
                assistants_data = response.json()
                logger.info("✅ Captured LangGraph Studio data")
                return assistants_data
            else:
                # Try docs endpoint as fallback
                docs_url = f"{self.services['langgraph_studio']}/docs"
                docs_response = requests.get(docs_url, timeout=10)
                
                if docs_response.status_code == 200:
                    logger.info("✅ Captured LangGraph Studio docs (fallback)")
                    return {"docs_accessible": True, "status": docs_response.status_code}
                else:
                    logger.error(f"❌ LangGraph Studio error: {response.status_code}")
                    return []
                
        except Exception as e:
            logger.error(f"❌ Error capturing LangGraph Studio logs: {e}")
            return []
    
    async def capture_system_metrics(self) -> Dict:
        """Capture system metrics and network traces"""
        logger.info("💻 Capturing system metrics...")
        
        try:
            import psutil
            
            system_data = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_connections": len(psutil.net_connections()),
                "process_count": len(psutil.pids()),
                "captured_at": datetime.now().isoformat()
            }
            
            # Get network traces for our services
            network_traces = []
            for service_name, url in self.services.items():
                try:
                    start_time = time.time()
                    response = requests.get(f"{url}/health", timeout=5)
                    response_time = time.time() - start_time
                    
                    network_traces.append({
                        "service": service_name,
                        "url": url,
                        "status_code": response.status_code,
                        "response_time_ms": round(response_time * 1000, 2),
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    network_traces.append({
                        "service": service_name,
                        "url": url,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
            
            system_data["network_traces"] = network_traces
            logger.info("✅ Captured system metrics")
            return system_data
            
        except ImportError:
            logger.warning("⚠️ psutil not available, skipping system metrics")
            return {"error": "psutil not available"}
        except Exception as e:
            logger.error(f"❌ Error capturing system metrics: {e}")
            return {"error": str(e)}
    
    async def capture_all_raw_data(self) -> Dict:
        """Capture all raw data from all sources"""
        logger.info("🚀 Starting comprehensive raw data capture...")
        
        start_time = time.time()
        
        # Capture data from all sources concurrently
        tasks = [
            self.capture_langsmith_traces(),
            self.capture_mcp_observability_logs(),
            self.capture_mcp_integration_logs(),
            self.capture_debug_dashboard_logs(),
            self.capture_langgraph_studio_logs(),
            self.capture_system_metrics()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organize results
        self.capture_data.update({
            "langsmith_traces": results[0] if not isinstance(results[0], Exception) else [],
            "mcp_observability_logs": results[1] if not isinstance(results[1], Exception) else [],
            "mcp_integration_logs": results[2] if not isinstance(results[2], Exception) else [],
            "debug_dashboard_logs": results[3] if not isinstance(results[3], Exception) else [],
            "langgraph_studio_logs": results[4] if not isinstance(results[4], Exception) else [],
            "system_metrics": results[5] if not isinstance(results[5], Exception) else {}
        })
        
        # Add capture metadata
        self.capture_data.update({
            "capture_duration_seconds": round(time.time() - start_time, 2),
            "total_data_points": sum([
                len(self.capture_data.get("langsmith_traces", [])),
                len(self.capture_data.get("mcp_observability_logs", [])),
                len(self.capture_data.get("mcp_integration_logs", [])),
                len(self.capture_data.get("debug_dashboard_logs", [])),
                len(self.capture_data.get("langgraph_studio_logs", [])),
                1 if self.capture_data.get("system_metrics") else 0
            ]),
            "capture_completed_at": datetime.now().isoformat()
        })
        
        logger.info(f"✅ Raw data capture completed in {self.capture_data['capture_duration_seconds']}s")
        logger.info(f"📊 Total data points captured: {self.capture_data['total_data_points']}")
        
        return self.capture_data
    
    def save_raw_data(self, filename: str = None) -> str:
        """Save captured raw data to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"raw_data_capture_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.capture_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Raw data saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving raw data: {e}")
            return ""
    
    def generate_analysis_report(self) -> str:
        """Generate analysis report from captured data"""
        logger.info("📋 Generating analysis report...")
        
        report = {
            "summary": {
                "capture_timestamp": self.capture_data.get("timestamp"),
                "capture_duration": self.capture_data.get("capture_duration_seconds"),
                "total_data_points": self.capture_data.get("total_data_points")
            },
            "langsmith_analysis": {
                "total_traces": len(self.capture_data.get("langsmith_traces", [])),
                "trace_ids": [trace.get("run_id") for trace in self.capture_data.get("langsmith_traces", [])]
            },
            "mcp_services_analysis": {
                "observability_status": "✅ Captured" if self.capture_data.get("mcp_observability_logs") else "❌ Failed",
                "integration_status": "✅ Captured" if self.capture_data.get("mcp_integration_logs") else "❌ Failed",
                "debug_dashboard_status": "✅ Captured" if self.capture_data.get("debug_dashboard_logs") else "❌ Failed",
                "langgraph_studio_status": "✅ Captured" if self.capture_data.get("langgraph_studio_logs") else "❌ Failed"
            },
            "system_health": self.capture_data.get("system_metrics", {}),
            "recommendations": self.generate_recommendations()
        }
        
        return json.dumps(report, indent=2)
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on captured data"""
        recommendations = []
        
        # Check LangSmith traces
        if not self.capture_data.get("langsmith_traces"):
            recommendations.append("⚠️ No LangSmith traces captured - check API key and project configuration")
        
        # Check MCP services
        if not self.capture_data.get("mcp_observability_logs"):
            recommendations.append("⚠️ MCP observability service not responding - check if service is running")
        
        if not self.capture_data.get("mcp_integration_logs"):
            recommendations.append("⚠️ MCP integration service not responding - check if service is running")
        
        # Check system metrics
        system_metrics = self.capture_data.get("system_metrics", {})
        if system_metrics.get("cpu_percent", 0) > 80:
            recommendations.append("⚠️ High CPU usage detected - consider optimizing services")
        
        if system_metrics.get("memory_percent", 0) > 80:
            recommendations.append("⚠️ High memory usage detected - consider restarting services")
        
        if not recommendations:
            recommendations.append("✅ All systems appear to be functioning normally")
        
        return recommendations

async def main():
    """Main execution function"""
    print("🚀 RAW DATA CAPTURE SYSTEM")
    print("=" * 50)
    
    # Initialize capture system
    capture = RawDataCapture()
    
    # Capture all raw data
    raw_data = await capture.capture_all_raw_data()
    
    # Save raw data
    filename = capture.save_raw_data()
    
    # Generate analysis report
    analysis_report = capture.generate_analysis_report()
    
    # Print summary
    print("\n📊 CAPTURE SUMMARY:")
    print(f"Duration: {raw_data.get('capture_duration_seconds', 0)}s")
    print(f"Data Points: {raw_data.get('total_data_points', 0)}")
    print(f"File: {filename}")
    
    print("\n📋 ANALYSIS REPORT:")
    print(analysis_report)
    
    # Save analysis report
    analysis_filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(analysis_filename, 'w') as f:
        f.write(analysis_report)
    
    print(f"\n💾 Analysis report saved to: {analysis_filename}")
    print("\n✅ Raw data capture completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Final LangSmith Tracing Report
Comprehensive report on LangSmith integration and tracing
"""

import asyncio
import json
import logging
import requests
import time
import os
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinalLangSmithReport:
    """Generate final comprehensive LangSmith tracing report"""
    
    def __init__(self):
        self.observability_url = "http://127.0.0.1:8002"
        self.mcp_integration_url = "http://127.0.0.1:8003"
        self.langsmith_api_key = "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"
        self.langsmith_project = "mcp-obsidian-integration"
        
        # Set environment variables
        os.environ['LANGSMITH_API_KEY'] = self.langsmith_api_key
        os.environ['LANGSMITH_PROJECT'] = self.langsmith_project
        
    async def get_langsmith_logs(self):
        """Retrieve LangSmith logs and convert to JSON-serializable format"""
        try:
            import langsmith
            from langsmith import Client
            
            client = Client(api_key=self.langsmith_api_key)
            
            # Get recent runs
            runs = client.list_runs(
                project_name=self.langsmith_project,
                limit=50
            )
            
            run_list = list(runs)
            logger.info(f"✅ Retrieved {len(run_list)} runs from LangSmith")
            
            # Convert to JSON-serializable format
            serializable_runs = []
            for run in run_list:
                serializable_run = {
                    "id": str(run.id),
                    "name": run.name,
                    "type": run.run_type,
                    "status": run.status,
                    "start_time": run.start_time.isoformat() if run.start_time else None,
                    "end_time": run.end_time.isoformat() if run.end_time else None,
                    "inputs": run.inputs if hasattr(run, 'inputs') else {},
                    "outputs": run.outputs if hasattr(run, 'outputs') else {}
                }
                serializable_runs.append(serializable_run)
            
            return {
                "total_runs": len(serializable_runs),
                "runs": serializable_runs,
                "project": self.langsmith_project,
                "retrieved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ LangSmith Log Retrieval: {e}")
            return {
                "error": str(e),
                "total_runs": 0,
                "runs": [],
                "project": self.langsmith_project,
                "retrieved_at": datetime.now().isoformat()
            }
    
    async def test_all_services(self):
        """Test all services and return results"""
        logger.info("🔍 Testing all services...")
        
        services = {
            "mcp_integration": {
                "name": "MCP Integration Server",
                "url": "http://127.0.0.1:8003/health",
                "status": "unknown"
            },
            "observability": {
                "name": "Observability Server", 
                "url": "http://127.0.0.1:8002/health",
                "status": "unknown"
            },
            "debug_dashboard": {
                "name": "Debug Dashboard",
                "url": "http://127.0.0.1:8004/health", 
                "status": "unknown"
            },
            "langgraph_studio": {
                "name": "LangGraph Studio",
                "url": "http://127.0.0.1:8000/",
                "status": "unknown"
            }
        }
        
        for service_id, service in services.items():
            try:
                response = requests.get(service["url"], timeout=5)
                if response.status_code == 200:
                    service["status"] = "healthy"
                    service["response_time"] = response.elapsed.total_seconds()
                    service["data"] = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                else:
                    service["status"] = "unhealthy"
                    service["status_code"] = response.status_code
                logger.info(f"✅ {service['name']}: {service['status']}")
            except Exception as e:
                service["status"] = "error"
                service["error"] = str(e)
                logger.error(f"❌ {service['name']}: {e}")
        
        return services
    
    async def test_mcp_tool_calls(self):
        """Test MCP tool calls"""
        logger.info("🔧 Testing MCP tool calls...")
        
        tool_tests = [
            {
                "name": "Sequential Thinking",
                "server": "sequential-thinking",
                "tool": "sequentialthinking",
                "args": {
                    "thought": "Final LangSmith tracing test",
                    "nextThoughtNeeded": False,
                    "thoughtNumber": 1,
                    "totalThoughts": 1
                }
            }
        ]
        
        results = []
        for test in tool_tests:
            try:
                response = requests.post(
                    f"{self.mcp_integration_url}/mcp/call",
                    json={
                        "server_name": test["server"],
                        "tool_name": test["tool"],
                        "arguments": test["args"]
                    },
                    timeout=10
                )
                
                result = {
                    "name": test["name"],
                    "status": "success" if response.status_code == 200 else "failed",
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text
                }
                results.append(result)
                logger.info(f"✅ {test['name']}: {result['status']}")
                
            except Exception as e:
                result = {
                    "name": test["name"],
                    "status": "error",
                    "error": str(e)
                }
                results.append(result)
                logger.error(f"❌ {test['name']}: {e}")
        
        return results
    
    async def generate_final_report(self):
        """Generate final comprehensive report"""
        logger.info("📋 Generating final LangSmith tracing report...")
        
        start_time = time.time()
        
        # Gather all data
        services = await self.test_all_services()
        tool_results = await self.test_mcp_tool_calls()
        langsmith_logs = await self.get_langsmith_logs()
        
        end_time = time.time()
        
        # Create comprehensive report
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_time_seconds": end_time - start_time,
                "langsmith_project": self.langsmith_project,
                "api_key_configured": bool(self.langsmith_api_key)
            },
            "service_status": services,
            "mcp_tool_tests": tool_results,
            "langsmith_logs": langsmith_logs,
            "summary": {
                "total_services": len(services),
                "healthy_services": len([s for s in services.values() if s["status"] == "healthy"]),
                "unhealthy_services": len([s for s in services.values() if s["status"] == "unhealthy"]),
                "error_services": len([s for s in services.values() if s["status"] == "error"]),
                "total_tool_tests": len(tool_results),
                "successful_tool_tests": len([t for t in tool_results if t["status"] == "success"]),
                "langsmith_runs_retrieved": langsmith_logs.get("total_runs", 0)
            }
        }
        
        # Save report
        report_filename = f"final_langsmith_tracing_report_{int(time.time())}.json"
        with open(report_filename, "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🎯 FINAL LANGSMITH TRACING REPORT")
        logger.info("=" * 60)
        logger.info(f"⏱️  Generation Time: {end_time - start_time:.2f} seconds")
        logger.info(f"📊 Services: {report['summary']['healthy_services']}/{report['summary']['total_services']} healthy")
        logger.info(f"🔧 Tool Tests: {report['summary']['successful_tool_tests']}/{report['summary']['total_tool_tests']} successful")
        logger.info(f"📋 LangSmith Runs: {report['summary']['langsmith_runs_retrieved']} retrieved")
        logger.info("=" * 60)
        
        # Print service details
        for service_id, service in services.items():
            status_icon = "✅" if service["status"] == "healthy" else "❌" if service["status"] == "error" else "⚠️"
            logger.info(f"{status_icon} {service['name']}: {service['status']}")
        
        logger.info("=" * 60)
        logger.info(f"📄 Full report saved to: {report_filename}")
        
        return report

async def main():
    """Main execution"""
    reporter = FinalLangSmithReport()
    await reporter.generate_final_report()

if __name__ == "__main__":
    asyncio.run(main())

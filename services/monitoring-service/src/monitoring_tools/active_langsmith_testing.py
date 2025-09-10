#!/usr/bin/env python3
"""
Active LangSmith Testing with MCP Integration
Continuous testing and tracing with LangSmith integration
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

class ActiveLangSmithTesting:
    """Active testing with LangSmith tracing integration"""
    
    def __init__(self):
        self.observability_url = "http://127.0.0.1:8002"
        self.mcp_integration_url = "http://127.0.0.1:8003"
        self.langsmith_api_key = "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"
        self.langsmith_project = "mcp-obsidian-integration"
        self.test_session_id = f"active_test_{int(time.time())}"
        
        # Set environment variables
        os.environ['LANGSMITH_API_KEY'] = self.langsmith_api_key
        os.environ['LANGSMITH_PROJECT'] = self.langsmith_project
        
    async def create_langsmith_trace(self, event_name: str, data: Dict[str, Any]):
        """Create a trace in LangSmith"""
        try:
            import langsmith
            from langsmith import Client
            
            client = Client(api_key=self.langsmith_api_key)
            
            # Create a run
            run = client.create_run(
                name=event_name,
                run_type="tool",
                project_name=self.langsmith_project,
                inputs=data,
                start_time=datetime.now()
            )
            
            logger.info(f"✅ LangSmith Trace Created: {run.id} - {event_name}")
            return run
            
        except Exception as e:
            logger.error(f"❌ LangSmith Trace Creation Failed: {e}")
            return None
    
    async def test_mcp_server_health(self):
        """Test MCP server health and create trace"""
        logger.info("🔍 Testing MCP server health...")
        
        start_time = time.time()
        
        # Test all servers
        servers = [
            ("MCP Integration", "http://127.0.0.1:8003/health"),
            ("Observability", "http://127.0.0.1:8002/health"),
            ("Debug Dashboard", "http://127.0.0.1:8004/health")
        ]
        
        results = {}
        for name, url in servers:
            try:
                response = requests.get(url, timeout=5)
                results[name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
                logger.info(f"✅ {name}: {results[name]['status']} ({results[name]['response_time']:.3f}s)")
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error(f"❌ {name}: {e}")
        
        end_time = time.time()
        
        # Create LangSmith trace
        trace_data = {
            "test_type": "mcp_health_check",
            "session_id": self.test_session_id,
            "results": results,
            "execution_time": end_time - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.create_langsmith_trace("MCP Health Check", trace_data)
        
        return results
    
    async def test_mcp_tool_calls(self):
        """Test MCP tool calls and create trace"""
        logger.info("🔧 Testing MCP tool calls...")
        
        start_time = time.time()
        
        # Test different MCP tool calls
        tool_tests = [
            {
                "name": "Sequential Thinking",
                "server": "sequential-thinking",
                "tool": "sequentialthinking",
                "args": {
                    "thought": "Testing MCP integration with LangSmith tracing",
                    "nextThoughtNeeded": True,
                    "thoughtNumber": 1,
                    "totalThoughts": 3
                }
            },
            {
                "name": "Observability Trace",
                "server": "observability-mcp",
                "tool": "create_trace_event",
                "args": {
                    "thread_id": f"test_{int(time.time())}",
                    "agent_id": "active_test_agent",
                    "workflow_id": "mcp_testing",
                    "event_type": "test_event",
                    "level": "info",
                    "message": "Active testing with LangSmith integration",
                    "data": {"test": "active_testing"},
                    "tags": ["test", "active", "langsmith"]
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
        
        end_time = time.time()
        
        # Create LangSmith trace
        trace_data = {
            "test_type": "mcp_tool_calls",
            "session_id": self.test_session_id,
            "results": results,
            "execution_time": end_time - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.create_langsmith_trace("MCP Tool Calls Test", trace_data)
        
        return results
    
    async def test_langgraph_integration(self):
        """Test LangGraph integration and create trace"""
        logger.info("🔄 Testing LangGraph integration...")
        
        start_time = time.time()
        
        # Test LangGraph Studio
        langgraph_tests = [
            {
                "name": "LangGraph Studio Health",
                "url": "http://127.0.0.1:8000/health",
                "expected_status": 200
            },
            {
                "name": "LangGraph Studio Root",
                "url": "http://127.0.0.1:8000/",
                "expected_status": 200
            }
        ]
        
        results = []
        for test in langgraph_tests:
            try:
                response = requests.get(test["url"], timeout=5)
                result = {
                    "name": test["name"],
                    "status": "success" if response.status_code == test["expected_status"] else "failed",
                    "status_code": response.status_code,
                    "expected_status": test["expected_status"]
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
        
        end_time = time.time()
        
        # Create LangSmith trace
        trace_data = {
            "test_type": "langgraph_integration",
            "session_id": self.test_session_id,
            "results": results,
            "execution_time": end_time - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.create_langsmith_trace("LangGraph Integration Test", trace_data)
        
        return results
    
    async def retrieve_langsmith_logs(self):
        """Retrieve and analyze LangSmith logs"""
        logger.info("📋 Retrieving LangSmith logs...")
        
        try:
            import langsmith
            from langsmith import Client
            
            client = Client(api_key=self.langsmith_api_key)
            
            # Get recent runs
            runs = client.list_runs(
                project_name=self.langsmith_project,
                limit=20
            )
            
            run_list = list(runs)
            logger.info(f"✅ Retrieved {len(run_list)} runs from LangSmith")
            
            # Analyze runs
            run_analysis = {
                "total_runs": len(run_list),
                "run_types": {},
                "status_counts": {},
                "recent_runs": []
            }
            
            for run in run_list:
                # Count run types
                run_type = run.run_type or "unknown"
                run_analysis["run_types"][run_type] = run_analysis["run_types"].get(run_type, 0) + 1
                
                # Count statuses
                status = run.status or "unknown"
                run_analysis["status_counts"][status] = run_analysis["status_counts"].get(status, 0) + 1
                
                # Add to recent runs
                run_analysis["recent_runs"].append({
                    "id": run.id,
                    "name": run.name,
                    "type": run_type,
                    "status": status,
                    "start_time": run.start_time.isoformat() if run.start_time else None,
                    "end_time": run.end_time.isoformat() if run.end_time else None
                })
            
            logger.info(f"   Run Types: {run_analysis['run_types']}")
            logger.info(f"   Status Counts: {run_analysis['status_counts']}")
            
            # Create LangSmith trace
            trace_data = {
                "test_type": "langsmith_log_retrieval",
                "session_id": self.test_session_id,
                "analysis": run_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.create_langsmith_trace("LangSmith Log Retrieval", trace_data)
            
            return run_analysis
            
        except Exception as e:
            logger.error(f"❌ LangSmith Log Retrieval: {e}")
            return None
    
    async def run_active_testing_cycle(self):
        """Run a complete active testing cycle"""
        logger.info("🚀 Starting Active LangSmith Testing Cycle...")
        logger.info("=" * 60)
        
        cycle_start = time.time()
        
        # Run all tests
        health_results = await self.test_mcp_server_health()
        tool_results = await self.test_mcp_tool_calls()
        langgraph_results = await self.test_langgraph_integration()
        logs_analysis = await self.retrieve_langsmith_logs()
        
        cycle_end = time.time()
        cycle_duration = cycle_end - cycle_start
        
        # Generate cycle report
        cycle_report = {
            "cycle_id": self.test_session_id,
            "start_time": datetime.fromtimestamp(cycle_start).isoformat(),
            "end_time": datetime.fromtimestamp(cycle_end).isoformat(),
            "duration_seconds": cycle_duration,
            "health_results": health_results,
            "tool_results": tool_results,
            "langgraph_results": langgraph_results,
            "logs_analysis": logs_analysis
        }
        
        # Save cycle report
        with open(f"active_testing_cycle_{self.test_session_id}.json", "w") as f:
            json.dump(cycle_report, f, indent=2)
        
        logger.info("=" * 60)
        logger.info("🎯 ACTIVE TESTING CYCLE COMPLETE")
        logger.info("=" * 60)
        logger.info(f"⏱️  Cycle Duration: {cycle_duration:.2f} seconds")
        logger.info(f"📊 Health Tests: {len(health_results)} servers tested")
        logger.info(f"🔧 Tool Tests: {len(tool_results)} tools tested")
        logger.info(f"🔄 LangGraph Tests: {len(langgraph_results)} tests completed")
        logger.info(f"📋 LangSmith Logs: {logs_analysis['total_runs'] if logs_analysis else 0} runs analyzed")
        logger.info("=" * 60)
        logger.info(f"📄 Cycle report saved to: active_testing_cycle_{self.test_session_id}.json")
        
        return cycle_report

async def main():
    """Main active testing execution"""
    tester = ActiveLangSmithTesting()
    await tester.run_active_testing_cycle()

if __name__ == "__main__":
    asyncio.run(main())

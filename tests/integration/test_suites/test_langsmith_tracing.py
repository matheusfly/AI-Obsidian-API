#!/usr/bin/env python3
"""
LangSmith Tracing Test
Tests LangSmith integration and retrieves tracing logs
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

class LangSmithTracingTest:
    """Test LangSmith tracing integration and retrieve logs"""
    
    def __init__(self):
        self.observability_url = "http://127.0.0.1:8002"
        self.mcp_integration_url = "http://127.0.0.1:8003"
        self.langsmith_api_key = "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"
        self.langsmith_project = "mcp-obsidian-integration"
        self.test_results = []
        
        # Set environment variables
        os.environ['LANGSMITH_API_KEY'] = self.langsmith_api_key
        os.environ['LANGSMITH_PROJECT'] = self.langsmith_project
        
    async def test_langsmith_connection(self):
        """Test LangSmith connection and configuration"""
        logger.info("🔗 Testing LangSmith connection...")
        
        try:
            # Test if LangSmith is available
            import langsmith
            from langsmith import Client
            
            client = Client(api_key=self.langsmith_api_key)
            
            # Test connection
            runs = client.list_runs(project_name=self.langsmith_project, limit=1)
            run_list = list(runs)
            
            logger.info(f"✅ LangSmith Connection: SUCCESS")
            logger.info(f"   Project: {self.langsmith_project}")
            logger.info(f"   Available runs: {len(run_list)}")
            
            self.test_results.append({
                "test": "langsmith_connection",
                "status": "PASS",
                "details": {
                    "project": self.langsmith_project,
                    "available_runs": len(run_list)
                }
            })
            
            return True
            
        except ImportError:
            logger.error("❌ LangSmith not installed")
            self.test_results.append({
                "test": "langsmith_connection",
                "status": "FAIL",
                "details": "LangSmith not installed"
            })
            return False
        except Exception as e:
            logger.error(f"❌ LangSmith Connection: ERROR - {e}")
            self.test_results.append({
                "test": "langsmith_connection",
                "status": "ERROR",
                "details": str(e)
            })
            return False
    
    async def test_observability_tracing(self):
        """Test observability server tracing functionality"""
        logger.info("📊 Testing observability server tracing...")
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.observability_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Observability Health: {health_data}")
                
                # Check if LangSmith integration is active
                if health_data.get('services', {}).get('langsmith_integration') == 'active':
                    logger.info("✅ LangSmith Integration: ACTIVE")
                    self.test_results.append({
                        "test": "observability_tracing",
                        "status": "PASS",
                        "details": "LangSmith integration is active"
                    })
                else:
                    logger.warning("⚠️ LangSmith Integration: INACTIVE")
                    self.test_results.append({
                        "test": "observability_tracing",
                        "status": "PARTIAL",
                        "details": "LangSmith integration is inactive"
                    })
            else:
                logger.error(f"❌ Observability Health: FAILED ({response.status_code})")
                self.test_results.append({
                    "test": "observability_tracing",
                    "status": "FAIL",
                    "details": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            logger.error(f"❌ Observability Tracing: ERROR - {e}")
            self.test_results.append({
                "test": "observability_tracing",
                "status": "ERROR",
                "details": str(e)
            })
    
    async def create_test_traces(self):
        """Create test traces for LangSmith"""
        logger.info("🔄 Creating test traces...")
        
        try:
            # Create a test trace event
            trace_data = {
                "thread_id": f"test_langsmith_{int(time.time())}",
                "agent_id": "langsmith_test_agent",
                "workflow_id": "test_workflow",
                "event_type": "test_event",
                "level": "info",
                "message": "Testing LangSmith tracing integration",
                "data": {
                    "test": "langsmith_tracing",
                    "timestamp": datetime.now().isoformat(),
                    "api_key": self.langsmith_api_key[:10] + "...",
                    "project": self.langsmith_project
                },
                "tags": ["test", "langsmith", "tracing"]
            }
            
            # Send trace to observability server
            response = requests.post(f"{self.observability_url}/mcp/call_tool", 
                                   json={"tool_name": "create_trace_event", "arguments": trace_data},
                                   timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Test Trace Created: SUCCESS")
                self.test_results.append({
                    "test": "create_test_traces",
                    "status": "PASS",
                    "details": "Test trace created successfully"
                })
            else:
                logger.warning(f"⚠️ Test Trace Created: PARTIAL ({response.status_code})")
                self.test_results.append({
                    "test": "create_test_traces",
                    "status": "PARTIAL",
                    "details": response.text
                })
                
        except Exception as e:
            logger.error(f"❌ Create Test Traces: ERROR - {e}")
            self.test_results.append({
                "test": "create_test_traces",
                "status": "ERROR",
                "details": str(e)
            })
    
    async def retrieve_langsmith_logs(self):
        """Retrieve logs from LangSmith"""
        logger.info("📋 Retrieving LangSmith logs...")
        
        try:
            import langsmith
            from langsmith import Client
            
            client = Client(api_key=self.langsmith_api_key)
            
            # Get recent runs
            runs = client.list_runs(
                project_name=self.langsmith_project,
                limit=10
            )
            
            run_list = list(runs)
            logger.info(f"✅ LangSmith Logs Retrieved: {len(run_list)} runs found")
            
            # Process each run
            for i, run in enumerate(run_list):
                logger.info(f"   Run {i+1}: {run.id} - {run.status} - {run.start_time}")
                
                # Get run details
                run_details = client.read_run(run.id)
                logger.info(f"      Details: {run_details.name} - {run_details.run_type}")
                
                # Get child runs
                child_runs = client.list_runs(parent_run_id=run.id)
                child_list = list(child_runs)
                if child_list:
                    logger.info(f"      Child runs: {len(child_list)}")
            
            self.test_results.append({
                "test": "retrieve_langsmith_logs",
                "status": "PASS",
                "details": {
                    "runs_found": len(run_list),
                    "project": self.langsmith_project
                }
            })
            
            return run_list
            
        except Exception as e:
            logger.error(f"❌ Retrieve LangSmith Logs: ERROR - {e}")
            self.test_results.append({
                "test": "retrieve_langsmith_logs",
                "status": "ERROR",
                "details": str(e)
            })
            return []
    
    async def test_mcp_langsmith_integration(self):
        """Test MCP integration with LangSmith"""
        logger.info("🔧 Testing MCP-LangSmith integration...")
        
        try:
            # Test MCP tool call with tracing
            mcp_data = {
                "server_name": "observability-mcp",
                "tool_name": "create_trace_event",
                "arguments": {
                    "thread_id": f"mcp_langsmith_test_{int(time.time())}",
                    "agent_id": "mcp_langsmith_agent",
                    "workflow_id": "mcp_integration_test",
                    "event_type": "mcp_tool_call",
                    "level": "info",
                    "message": "Testing MCP-LangSmith integration",
                    "data": {
                        "integration": "mcp_langsmith",
                        "timestamp": datetime.now().isoformat()
                    },
                    "tags": ["mcp", "langsmith", "integration"]
                }
            }
            
            response = requests.post(f"{self.mcp_integration_url}/mcp/call", 
                                   json=mcp_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ MCP-LangSmith Integration: SUCCESS")
                self.test_results.append({
                    "test": "mcp_langsmith_integration",
                    "status": "PASS",
                    "details": result
                })
            else:
                logger.warning(f"⚠️ MCP-LangSmith Integration: PARTIAL ({response.status_code})")
                self.test_results.append({
                    "test": "mcp_langsmith_integration",
                    "status": "PARTIAL",
                    "details": response.text
                })
                
        except Exception as e:
            logger.error(f"❌ MCP-LangSmith Integration: ERROR - {e}")
            self.test_results.append({
                "test": "mcp_langsmith_integration",
                "status": "ERROR",
                "details": str(e)
            })
    
    async def run_comprehensive_test(self):
        """Run comprehensive LangSmith tracing test"""
        logger.info("🚀 Starting LangSmith Tracing Test...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        langsmith_available = await self.test_langsmith_connection()
        await self.test_observability_tracing()
        await self.create_test_traces()
        
        if langsmith_available:
            await self.retrieve_langsmith_logs()
        
        await self.test_mcp_langsmith_integration()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Generate report
        self.generate_report(execution_time)
    
    def generate_report(self, execution_time: float):
        """Generate comprehensive test report"""
        logger.info("📋 Generating LangSmith tracing report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
        partial_tests = len([r for r in self.test_results if r["status"] == "PARTIAL"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Create report
        report = {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "execution_time_seconds": round(execution_time, 2),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "partial_tests": partial_tests,
                "success_rate_percent": round(success_rate, 2)
            },
            "langsmith_config": {
                "api_key": self.langsmith_api_key[:10] + "...",
                "project": self.langsmith_project
            },
            "test_results": self.test_results,
            "recommendations": self.generate_recommendations()
        }
        
        # Save report
        with open("langsmith_tracing_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🎯 LANGSMITH TRACING TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"⏱️  Execution Time: {execution_time:.2f} seconds")
        logger.info(f"📊 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"⚠️  Errors: {error_tests}")
        logger.info(f"🔄 Partial: {partial_tests}")
        logger.info(f"🎯 Success Rate: {success_rate:.1f}%")
        logger.info("=" * 60)
        
        # Print detailed results
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️" if result["status"] == "ERROR" else "🔄"
            logger.info(f"{status_icon} {result['test']}: {result['status']}")
            if result["status"] != "PASS":
                logger.info(f"   Details: {result['details']}")
        
        logger.info("=" * 60)
        logger.info("📄 Full report saved to: langsmith_tracing_report.json")
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r["status"] in ["FAIL", "ERROR"]]
        
        if any("langsmith_connection" in r["test"] for r in failed_tests):
            recommendations.append("Install LangSmith: pip install langsmith")
        
        if any("observability_tracing" in r["test"] for r in failed_tests):
            recommendations.append("Fix observability server LangSmith integration")
        
        if any("create_test_traces" in r["test"] for r in failed_tests):
            recommendations.append("Fix trace creation functionality")
        
        if not recommendations:
            recommendations.append("LangSmith tracing is working correctly!")
        
        return recommendations

async def main():
    """Main test execution"""
    test = LangSmithTracingTest()
    await test.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())

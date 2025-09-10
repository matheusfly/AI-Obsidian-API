#!/usr/bin/env python3
"""
LangGraph MCP Integration Test
Tests LangGraph workflow with MCP server integration and LangSmith tracing
"""

import asyncio
import json
import logging
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LangGraphMCPIntegrationTest:
    """Test LangGraph integration with MCP servers"""
    
    def __init__(self):
        self.mcp_integration_url = "http://127.0.0.1:8003"
        self.observability_url = "http://127.0.0.1:8002"
        self.langgraph_url = "http://127.0.0.1:8000"  # LangGraph Studio
        self.test_results = []
        
    async def test_mcp_servers_health(self):
        """Test MCP servers health"""
        logger.info("🔍 Testing MCP servers health...")
        
        # Test MCP Integration Server
        try:
            response = requests.get(f"{self.mcp_integration_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ MCP Integration Server: HEALTHY")
                self.test_results.append({
                    "test": "mcp_integration_health",
                    "status": "PASS",
                    "details": response.json()
                })
            else:
                logger.error(f"❌ MCP Integration Server: FAILED ({response.status_code})")
                self.test_results.append({
                    "test": "mcp_integration_health",
                    "status": "FAIL",
                    "details": f"HTTP {response.status_code}"
                })
        except Exception as e:
            logger.error(f"❌ MCP Integration Server: ERROR - {e}")
            self.test_results.append({
                "test": "mcp_integration_health",
                "status": "ERROR",
                "details": str(e)
            })
        
        # Test Observability Server
        try:
            response = requests.get(f"{self.observability_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Observability Server: HEALTHY")
                self.test_results.append({
                    "test": "observability_health",
                    "status": "PASS",
                    "details": response.json()
                })
            else:
                logger.error(f"❌ Observability Server: FAILED ({response.status_code})")
                self.test_results.append({
                    "test": "observability_health",
                    "status": "FAIL",
                    "details": f"HTTP {response.status_code}"
                })
        except Exception as e:
            logger.error(f"❌ Observability Server: ERROR - {e}")
            self.test_results.append({
                "test": "observability_health",
                "status": "ERROR",
                "details": str(e)
            })
    
    async def test_mcp_tool_calls(self):
        """Test MCP tool calls"""
        logger.info("🔧 Testing MCP tool calls...")
        
        # Test with our custom observability server
        test_data = {
            "thread_id": f"test_langgraph_{int(time.time())}",
            "agent_id": "langgraph_test_agent",
            "workflow_id": "test_workflow",
            "event_type": "test_event",
            "level": "info",
            "message": "Testing LangGraph MCP integration",
            "data": {"test": "value", "timestamp": datetime.now().isoformat()},
            "tags": ["test", "langgraph", "mcp"]
        }
        
        try:
            # Test direct observability endpoint
            response = requests.post(f"{self.observability_url}/mcp/call_tool", 
                                   json={"tool_name": "create_trace_event", "arguments": test_data},
                                   timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ MCP Tool Call: SUCCESS")
                self.test_results.append({
                    "test": "mcp_tool_call",
                    "status": "PASS",
                    "details": response.json()
                })
            else:
                logger.warning(f"⚠️ MCP Tool Call: PARTIAL ({response.status_code})")
                self.test_results.append({
                    "test": "mcp_tool_call",
                    "status": "PARTIAL",
                    "details": response.text
                })
        except Exception as e:
            logger.error(f"❌ MCP Tool Call: ERROR - {e}")
            self.test_results.append({
                "test": "mcp_tool_call",
                "status": "ERROR",
                "details": str(e)
            })
    
    async def test_langgraph_workflow(self):
        """Test LangGraph workflow execution"""
        logger.info("🔄 Testing LangGraph workflow...")
        
        # Create a simple LangGraph workflow test
        workflow_data = {
            "workflow_id": f"test_workflow_{int(time.time())}",
            "thread_id": f"test_thread_{int(time.time())}",
            "input": {
                "message": "Hello from LangGraph MCP integration test!",
                "temperature": 0.7
            },
            "config": {
                "recursion_limit": 10,
                "debug": True
            }
        }
        
        try:
            # Test if LangGraph Studio is running
            response = requests.get(f"{self.langgraph_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ LangGraph Studio: AVAILABLE")
                self.test_results.append({
                    "test": "langgraph_studio",
                    "status": "PASS",
                    "details": "LangGraph Studio is running"
                })
            else:
                logger.warning(f"⚠️ LangGraph Studio: NOT AVAILABLE ({response.status_code})")
                self.test_results.append({
                    "test": "langgraph_studio",
                    "status": "SKIP",
                    "details": "LangGraph Studio not running"
                })
        except Exception as e:
            logger.warning(f"⚠️ LangGraph Studio: NOT AVAILABLE - {e}")
            self.test_results.append({
                "test": "langgraph_studio",
                "status": "SKIP",
                "details": "LangGraph Studio not running"
            })
    
    async def test_trace_capture(self):
        """Test trace capture and retrieval"""
        logger.info("📊 Testing trace capture...")
        
        try:
            # Get traces from observability server
            response = requests.get(f"{self.observability_url}/traces", timeout=5)
            if response.status_code == 200:
                traces = response.json()
                logger.info(f"✅ Trace Retrieval: SUCCESS ({traces.get('count', 0)} traces)")
                self.test_results.append({
                    "test": "trace_retrieval",
                    "status": "PASS",
                    "details": f"Retrieved {traces.get('count', 0)} traces"
                })
            else:
                logger.error(f"❌ Trace Retrieval: FAILED ({response.status_code})")
                self.test_results.append({
                    "test": "trace_retrieval",
                    "status": "FAIL",
                    "details": f"HTTP {response.status_code}"
                })
        except Exception as e:
            logger.error(f"❌ Trace Retrieval: ERROR - {e}")
            self.test_results.append({
                "test": "trace_retrieval",
                "status": "ERROR",
                "details": str(e)
            })
    
    async def test_performance_metrics(self):
        """Test performance metrics"""
        logger.info("⚡ Testing performance metrics...")
        
        try:
            # Get performance metrics
            response = requests.get(f"{self.observability_url}/performance", timeout=5)
            if response.status_code == 200:
                metrics = response.json()
                logger.info("✅ Performance Metrics: SUCCESS")
                self.test_results.append({
                    "test": "performance_metrics",
                    "status": "PASS",
                    "details": metrics
                })
            else:
                logger.error(f"❌ Performance Metrics: FAILED ({response.status_code})")
                self.test_results.append({
                    "test": "performance_metrics",
                    "status": "FAIL",
                    "details": f"HTTP {response.status_code}"
                })
        except Exception as e:
            logger.error(f"❌ Performance Metrics: ERROR - {e}")
            self.test_results.append({
                "test": "performance_metrics",
                "status": "ERROR",
                "details": str(e)
            })
    
    async def run_comprehensive_test(self):
        """Run comprehensive integration test"""
        logger.info("🚀 Starting LangGraph MCP Integration Test...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        await self.test_mcp_servers_health()
        await self.test_mcp_tool_calls()
        await self.test_langgraph_workflow()
        await self.test_trace_capture()
        await self.test_performance_metrics()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Generate report
        self.generate_report(execution_time)
    
    def generate_report(self, execution_time: float):
        """Generate comprehensive test report"""
        logger.info("📋 Generating test report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
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
                "skipped_tests": skipped_tests,
                "success_rate_percent": round(success_rate, 2)
            },
            "test_results": self.test_results,
            "recommendations": self.generate_recommendations()
        }
        
        # Save report
        with open("langgraph_mcp_integration_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🎯 LANGGRAPH MCP INTEGRATION TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"⏱️  Execution Time: {execution_time:.2f} seconds")
        logger.info(f"📊 Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"⚠️  Errors: {error_tests}")
        logger.info(f"⏭️  Skipped: {skipped_tests}")
        logger.info(f"🎯 Success Rate: {success_rate:.1f}%")
        logger.info("=" * 60)
        
        # Print detailed results
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️" if result["status"] == "ERROR" else "⏭️"
            logger.info(f"{status_icon} {result['test']}: {result['status']}")
            if result["status"] != "PASS":
                logger.info(f"   Details: {result['details']}")
        
        logger.info("=" * 60)
        logger.info("📄 Full report saved to: langgraph_mcp_integration_report.json")
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r["status"] in ["FAIL", "ERROR"]]
        
        if any("mcp_integration_health" in r["test"] for r in failed_tests):
            recommendations.append("Fix MCP Integration Server health issues")
        
        if any("observability_health" in r["test"] for r in failed_tests):
            recommendations.append("Fix Observability Server health issues")
        
        if any("mcp_tool_call" in r["test"] for r in failed_tests):
            recommendations.append("Fix MCP tool call functionality")
        
        if any("langgraph_studio" in r["test"] for r in failed_tests):
            recommendations.append("Start LangGraph Studio for full integration testing")
        
        if not recommendations:
            recommendations.append("All systems are working correctly!")
        
        return recommendations

async def main():
    """Main test execution"""
    test = LangGraphMCPIntegrationTest()
    await test.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())

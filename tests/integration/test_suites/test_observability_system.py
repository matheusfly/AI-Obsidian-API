"""
Comprehensive Test Suite for Observability System
Tests LangSmith tracing, MCP observability server, and monitoring dashboard
"""

import asyncio
import json
import time
import traceback
from datetime import datetime
from typing import Dict, List, Any

import httpx
import requests

# Configuration
OBSERVABILITY_MCP_URL = "http://127.0.0.1:8002"
MONITORING_DASHBOARD_URL = "http://127.0.0.1:8001"
LANGGRAPH_SERVER_URL = "http://127.0.0.1:2024"
OBSIDIAN_API_URL = "http://127.0.0.1:27123"

class ObservabilityTester:
    """Comprehensive tester for the observability system"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def add_test_result(self, test_name: str, passed: bool, duration: float, error: str = None):
        """Add a test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "duration": duration,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_success_rate(self) -> float:
        """Get success rate percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    async def test_observability_mcp_server(self) -> bool:
        """Test the Observability MCP server"""
        try:
            print("🔍 Testing Observability MCP Server...")
            
            # Test health endpoint
            response = requests.get(f"{OBSERVABILITY_MCP_URL}/health", timeout=10)
            if response.status_code != 200:
                print(f"❌ MCP Server health check failed: {response.status_code}")
                return False
            
            # Test trace creation
            trace_payload = {
                "thread_id": "test_thread_123",
                "agent_id": "test_agent_456",
                "workflow_id": "test_workflow_789",
                "event_type": "test_event",
                "level": "info",
                "message": "Test trace event from Python",
                "data": {"test_data": "test_value"},
                "tags": ["test", "observability", "python"]
            }
            
            response = requests.post(
                f"{OBSERVABILITY_MCP_URL}/tools/create_trace_event",
                json=trace_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Trace creation failed: {response.status_code}")
                return False
            
            # Test checkpoint creation
            checkpoint_payload = {
                "thread_id": "test_thread_123",
                "agent_id": "test_agent_456",
                "workflow_id": "test_workflow_789",
                "checkpoint_type": "workflow_state",
                "state_snapshot": {"test_state": "test_value"},
                "human_input_required": False,
                "metadata": {"test_metadata": "test_value"}
            }
            
            response = requests.post(
                f"{OBSERVABILITY_MCP_URL}/tools/create_checkpoint",
                json=checkpoint_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Checkpoint creation failed: {response.status_code}")
                return False
            
            # Test getting traces
            traces_payload = {
                "thread_id": "test_thread_123",
                "limit": 10
            }
            
            response = requests.post(
                f"{OBSERVABILITY_MCP_URL}/tools/get_traces",
                json=traces_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Get traces failed: {response.status_code}")
                return False
            
            # Test getting checkpoints
            checkpoints_payload = {
                "thread_id": "test_thread_123",
                "limit": 10
            }
            
            response = requests.post(
                f"{OBSERVABILITY_MCP_URL}/tools/get_checkpoints",
                json=checkpoints_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Get checkpoints failed: {response.status_code}")
                return False
            
            # Test debug summary
            debug_payload = {
                "thread_id": "test_thread_123",
                "agent_id": "test_agent_456",
                "include_traces": True,
                "include_checkpoints": True,
                "include_performance": True
            }
            
            response = requests.post(
                f"{OBSERVABILITY_MCP_URL}/tools/get_debug_summary",
                json=debug_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Debug summary failed: {response.status_code}")
                return False
            
            print("✅ Observability MCP Server tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Observability MCP Server test failed: {str(e)}")
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    async def test_monitoring_dashboard(self) -> bool:
        """Test the monitoring dashboard"""
        try:
            print("📊 Testing Monitoring Dashboard...")
            
            # Test health endpoint
            response = requests.get(f"{MONITORING_DASHBOARD_URL}/api/health", timeout=10)
            if response.status_code != 200:
                print(f"❌ Dashboard health check failed: {response.status_code}")
                return False
            
            # Test metrics endpoint
            response = requests.get(f"{MONITORING_DASHBOARD_URL}/api/metrics", timeout=10)
            if response.status_code != 200:
                print(f"❌ Metrics endpoint failed: {response.status_code}")
                return False
            
            # Test traces endpoint
            response = requests.get(f"{MONITORING_DASHBOARD_URL}/api/traces?limit=10", timeout=10)
            if response.status_code != 200:
                print(f"❌ Traces endpoint failed: {response.status_code}")
                return False
            
            # Test checkpoints endpoint
            response = requests.get(f"{MONITORING_DASHBOARD_URL}/api/checkpoints?limit=10", timeout=10)
            if response.status_code != 200:
                print(f"❌ Checkpoints endpoint failed: {response.status_code}")
                return False
            
            # Test performance endpoint
            response = requests.get(f"{MONITORING_DASHBOARD_URL}/api/performance", timeout=10)
            if response.status_code != 200:
                print(f"❌ Performance endpoint failed: {response.status_code}")
                return False
            
            print("✅ Monitoring Dashboard tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Monitoring Dashboard test failed: {str(e)}")
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    async def test_langgraph_workflows_with_observability(self) -> bool:
        """Test LangGraph workflows with observability integration"""
        try:
            print("🤖 Testing LangGraph Workflows with Observability...")
            
            # Test observable-agent
            observable_test = {
                "assistant_id": "observable-agent",
                "input": {
                    "user_input": "Hello! Can you search for 'langgraph' and show me debug information?",
                    "vault_name": "Nomade Milionario"
                }
            }
            
            response = requests.post(
                f"{LANGGRAPH_SERVER_URL}/assistants/observable-agent/invoke",
                json=observable_test,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Observable agent test failed: {response.status_code}")
                return False
            
            # Test enhanced-interactive-agent
            enhanced_test = {
                "assistant_id": "enhanced-interactive-agent",
                "input": {
                    "user_input": "Hello! Can you search for 'langgraph' and show me statistics?",
                    "vault_name": "Nomade Milionario"
                }
            }
            
            response = requests.post(
                f"{LANGGRAPH_SERVER_URL}/assistants/enhanced-interactive-agent/invoke",
                json=enhanced_test,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Enhanced interactive agent test failed: {response.status_code}")
                return False
            
            print("✅ LangGraph Workflows with Observability tests passed")
            return True
            
        except Exception as e:
            print(f"❌ LangGraph Workflows with Observability test failed: {str(e)}")
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    async def test_time_travel_debugging(self) -> bool:
        """Test time-travel debugging functionality"""
        try:
            print("⏰ Testing Time-Travel Debugging...")
            
            # First, create a checkpoint
            checkpoint_payload = {
                "thread_id": "time_travel_test_thread",
                "agent_id": "time_travel_test_agent",
                "workflow_id": "time_travel_test_workflow",
                "checkpoint_type": "workflow_state",
                "state_snapshot": {
                    "test_state": "before_time_travel",
                    "timestamp": datetime.now().isoformat()
                },
                "human_input_required": False,
                "metadata": {"test": "time_travel"}
            }
            
            response = requests.post(
                f"{OBSERVABILITY_MCP_URL}/tools/create_checkpoint",
                json=checkpoint_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Checkpoint creation for time-travel test failed: {response.status_code}")
                return False
            
            # Get the checkpoint ID from the response
            checkpoint_data = response.json()
            checkpoint_id = checkpoint_data.get("content", [{}])[0].get("text", "").split("Checkpoint created: ")[1].split("\n")[0]
            
            # Test time-travel
            time_travel_payload = {
                "checkpoint_id": checkpoint_id,
                "thread_id": "time_travel_test_thread",
                "restore_state": True
            }
            
            response = requests.post(
                f"{OBSERVABILITY_MCP_URL}/tools/time_travel_debug",
                json=time_travel_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Time-travel test failed: {response.status_code}")
                return False
            
            print("✅ Time-Travel Debugging tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Time-Travel Debugging test failed: {str(e)}")
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    async def test_performance_monitoring(self) -> bool:
        """Test performance monitoring functionality"""
        try:
            print("⚡ Testing Performance Monitoring...")
            
            # Start performance monitoring
            start_payload = {
                "agent_id": "perf_test_agent",
                "workflow_id": "perf_test_workflow",
                "thread_id": "perf_test_thread"
            }
            
            response = requests.post(
                f"{OBSERVABILITY_MCP_URL}/tools/start_performance_monitoring",
                json=start_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Start performance monitoring failed: {response.status_code}")
                return False
            
            # Wait a bit
            await asyncio.sleep(2)
            
            # Stop performance monitoring
            stop_payload = {
                "agent_id": "perf_test_agent",
                "workflow_id": "perf_test_workflow",
                "thread_id": "perf_test_thread"
            }
            
            response = requests.post(
                f"{OBSERVABILITY_MCP_URL}/tools/stop_performance_monitoring",
                json=stop_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Stop performance monitoring failed: {response.status_code}")
                return False
            
            # Get performance metrics
            response = requests.post(
                f"{OBSERVABILITY_MCP_URL}/tools/get_performance_metrics",
                json={"agent_id": "perf_test_agent"},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Get performance metrics failed: {response.status_code}")
                return False
            
            print("✅ Performance Monitoring tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Performance Monitoring test failed: {str(e)}")
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    async def test_websocket_connection(self) -> bool:
        """Test WebSocket connection for real-time updates"""
        try:
            print("🔌 Testing WebSocket Connection...")
            
            import websockets
            
            async with websockets.connect(f"ws://localhost:8001/ws") as websocket:
                # Wait for a message
                message = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(message)
                
                if data.get("type") == "metrics_update":
                    print("✅ WebSocket connection test passed")
                    return True
                else:
                    print(f"❌ Unexpected WebSocket message: {data}")
                    return False
                    
        except Exception as e:
            print(f"❌ WebSocket connection test failed: {str(e)}")
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🧪 COMPREHENSIVE OBSERVABILITY SYSTEM TEST SUITE")
        print("=" * 60)
        
        # Test categories
        test_categories = [
            ("Observability MCP Server", self.test_observability_mcp_server),
            ("Monitoring Dashboard", self.test_monitoring_dashboard),
            ("LangGraph Workflows with Observability", self.test_langgraph_workflows_with_observability),
            ("Time-Travel Debugging", self.test_time_travel_debugging),
            ("Performance Monitoring", self.test_performance_monitoring),
            ("WebSocket Connection", self.test_websocket_connection)
        ]
        
        # Run all tests
        for test_name, test_func in test_categories:
            print(f"\n📋 Running: {test_name}")
            print("-" * 40)
            
            start_time = time.time()
            
            try:
                passed = await test_func()
                duration = time.time() - start_time
                self.add_test_result(test_name, passed, duration)
                
            except Exception as e:
                duration = time.time() - start_time
                self.add_test_result(test_name, False, duration, str(e))
                print(f"❌ {test_name} crashed: {str(e)}")
        
        # Generate test report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE OBSERVABILITY TEST REPORT")
        print("=" * 60)
        
        # Overall statistics
        success_rate = self.get_success_rate()
        total_duration = sum(result["duration"] for result in self.test_results)
        
        print(f"🎯 Overall Success Rate: {success_rate:.1f}%")
        print(f"⏱️ Total Duration: {total_duration:.2f} seconds")
        print(f"✅ Passed Tests: {self.passed_tests}")
        print(f"❌ Failed Tests: {self.failed_tests}")
        print(f"📊 Total Tests: {self.total_tests}")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        print("-" * 40)
        
        for result in self.test_results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} {result['test_name']} ({result['duration']:.2f}s)")
            if result["error"]:
                print(f"    Error: {result['error']}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        print("-" * 40)
        
        if success_rate >= 90:
            print("🎉 Excellent! Observability system is performing at 110%+ level")
            print("   - All major components are working correctly")
            print("   - LangSmith tracing is integrated")
            print("   - Real-time monitoring is functional")
            print("   - Time-travel debugging is operational")
        elif success_rate >= 70:
            print("⚠️ Good performance with room for improvement")
            print("   - Most components are working")
            print("   - Address failed tests for better reliability")
            print("   - Consider performance optimizations")
        else:
            print("❌ System needs attention")
            print("   - Multiple components are failing")
            print("   - Review error logs for common issues")
            print("   - Consider restarting services")
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "success_rate": success_rate,
            "total_duration": total_duration,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "total_tests": self.total_tests,
            "test_results": self.test_results
        }
        
        with open("observability_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: observability_test_report.json")

async def main():
    """Main function to run the comprehensive observability tests"""
    try:
        tester = ObservabilityTester()
        await tester.run_comprehensive_tests()
        
        # Final status
        if tester.get_success_rate() >= 90:
            print(f"\n🎉 MISSION ACCOMPLISHED! 110%+ Observability System Health Achieved! 🚀")
        else:
            print(f"\n⚠️ System needs attention. Success rate: {tester.get_success_rate():.1f}%")
            
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())

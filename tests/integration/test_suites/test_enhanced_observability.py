#!/usr/bin/env python3
"""
Enhanced Observability MCP Server Test Suite
Tests all the new advanced debugging capabilities
"""

import asyncio
import json
import requests
import time
from datetime import datetime

class EnhancedObservabilityTester:
    """Test suite for enhanced observability MCP server"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8002"
        self.test_results = []
        self.thread_id = f"test_thread_{int(time.time())}"
        self.agent_id = "test_agent_enhanced"
        self.workflow_id = "test_workflow_enhanced"
    
    async def test_enhanced_observability_features(self):
        """Test all enhanced observability features"""
        print("🧪 ENHANCED OBSERVABILITY MCP SERVER TEST SUITE")
        print("=" * 60)
        
        # Test 1: Create debug session
        await self.test_create_debug_session()
        
        # Test 2: Create trace events
        await self.test_create_trace_events()
        
        # Test 3: Create checkpoints
        await self.test_create_checkpoints()
        
        # Test 4: Analyze error patterns
        await self.test_analyze_error_patterns()
        
        # Test 5: Get agent communication log
        await self.test_get_agent_communication_log()
        
        # Test 6: Correlate errors with traces
        await self.test_correlate_errors_with_traces()
        
        # Test 7: Generate debug report
        await self.test_generate_debug_report()
        
        # Test 8: Monitor LangGraph server health
        await self.test_monitor_langgraph_server_health()
        
        # Test 9: Trace workflow execution
        await self.test_trace_workflow_execution()
        
        # Test 10: Optimize agent performance
        await self.test_optimize_agent_performance()
        
        # Test 11: Get debug session status
        await self.test_get_debug_session_status()
        
        # Generate final report
        self.generate_final_report()
    
    async def test_create_debug_session(self):
        """Test creating a debug session"""
        print("\n📋 Testing: Create Debug Session")
        try:
            response = requests.post(f"{self.base_url}/mcp/call_tool", json={
                "name": "create_debug_session",
                "arguments": {
                    "session_name": "enhanced_test_session",
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "monitoring_level": "comprehensive",
                    "auto_checkpoint_interval": 30
                }
            })
            
            if response.status_code == 200:
                print("✅ Debug session created successfully")
                self.test_results.append(("create_debug_session", True, "Success"))
            else:
                print(f"❌ Debug session creation failed: {response.status_code}")
                self.test_results.append(("create_debug_session", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Debug session creation error: {e}")
            self.test_results.append(("create_debug_session", False, str(e)))
    
    async def test_create_trace_events(self):
        """Test creating trace events"""
        print("\n📋 Testing: Create Trace Events")
        try:
            # Create various types of trace events
            trace_events = [
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": "api_call",
                    "level": "info",
                    "message": "Making API call to Obsidian vault",
                    "data": {"endpoint": "/vault/files", "method": "GET"},
                    "tags": ["api", "vault", "obsidian"]
                },
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": "mcp_call",
                    "level": "info",
                    "message": "Calling MCP tool for file search",
                    "data": {"tool": "search_notes", "query": "langgraph"},
                    "tags": ["mcp", "search"]
                },
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": "error",
                    "level": "error",
                    "message": "Failed to connect to LangGraph server",
                    "data": {"error_code": 404, "endpoint": "/assistants"},
                    "tags": ["error", "langgraph", "connection"]
                },
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": "llm_call",
                    "level": "info",
                    "message": "Calling LLM for response generation",
                    "data": {"model": "gpt-4", "tokens": 150},
                    "tags": ["llm", "generation"]
                }
            ]
            
            success_count = 0
            for event in trace_events:
                response = requests.post(f"{self.base_url}/mcp/call_tool", json={
                    "name": "create_trace_event",
                    "arguments": event
                })
                
                if response.status_code == 200:
                    success_count += 1
            
            if success_count == len(trace_events):
                print(f"✅ Created {success_count} trace events successfully")
                self.test_results.append(("create_trace_events", True, f"Created {success_count} events"))
            else:
                print(f"⚠️ Created {success_count}/{len(trace_events)} trace events")
                self.test_results.append(("create_trace_events", False, f"Only {success_count}/{len(trace_events)} created"))
                
        except Exception as e:
            print(f"❌ Trace event creation error: {e}")
            self.test_results.append(("create_trace_events", False, str(e)))
    
    async def test_create_checkpoints(self):
        """Test creating checkpoints"""
        print("\n📋 Testing: Create Checkpoints")
        try:
            checkpoints = [
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "checkpoint_type": "workflow_state",
                    "state_snapshot": {"step": "initialization", "status": "running"},
                    "human_input_required": False,
                    "metadata": {"checkpoint_reason": "workflow_start"}
                },
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "checkpoint_type": "human_input",
                    "state_snapshot": {"step": "user_interaction", "status": "waiting"},
                    "human_input_required": True,
                    "human_input_prompt": "Please confirm the next action",
                    "metadata": {"checkpoint_reason": "user_confirmation"}
                },
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "checkpoint_type": "error_recovery",
                    "state_snapshot": {"step": "error_handling", "status": "recovering"},
                    "human_input_required": False,
                    "metadata": {"checkpoint_reason": "error_recovery"}
                }
            ]
            
            success_count = 0
            for checkpoint in checkpoints:
                response = requests.post(f"{self.base_url}/mcp/call_tool", json={
                    "name": "create_checkpoint",
                    "arguments": checkpoint
                })
                
                if response.status_code == 200:
                    success_count += 1
            
            if success_count == len(checkpoints):
                print(f"✅ Created {success_count} checkpoints successfully")
                self.test_results.append(("create_checkpoints", True, f"Created {success_count} checkpoints"))
            else:
                print(f"⚠️ Created {success_count}/{len(checkpoints)} checkpoints")
                self.test_results.append(("create_checkpoints", False, f"Only {success_count}/{len(checkpoints)} created"))
                
        except Exception as e:
            print(f"❌ Checkpoint creation error: {e}")
            self.test_results.append(("create_checkpoints", False, str(e)))
    
    async def test_analyze_error_patterns(self):
        """Test error pattern analysis"""
        print("\n📋 Testing: Analyze Error Patterns")
        try:
            response = requests.post(f"{self.base_url}/mcp/call_tool", json={
                "name": "analyze_error_patterns",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "time_range_hours": 1,
                    "error_threshold": 1
                }
            })
            
            if response.status_code == 200:
                print("✅ Error pattern analysis completed")
                self.test_results.append(("analyze_error_patterns", True, "Success"))
            else:
                print(f"❌ Error pattern analysis failed: {response.status_code}")
                self.test_results.append(("analyze_error_patterns", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Error pattern analysis error: {e}")
            self.test_results.append(("analyze_error_patterns", False, str(e)))
    
    async def test_get_agent_communication_log(self):
        """Test getting agent communication log"""
        print("\n📋 Testing: Get Agent Communication Log")
        try:
            response = requests.post(f"{self.base_url}/mcp/call_tool", json={
                "name": "get_agent_communication_log",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "communication_type": "all",
                    "limit": 50
                }
            })
            
            if response.status_code == 200:
                print("✅ Agent communication log retrieved")
                self.test_results.append(("get_agent_communication_log", True, "Success"))
            else:
                print(f"❌ Agent communication log failed: {response.status_code}")
                self.test_results.append(("get_agent_communication_log", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Agent communication log error: {e}")
            self.test_results.append(("get_agent_communication_log", False, str(e)))
    
    async def test_correlate_errors_with_traces(self):
        """Test error correlation with traces"""
        print("\n📋 Testing: Correlate Errors with Traces")
        try:
            response = requests.post(f"{self.base_url}/mcp/call_tool", json={
                "name": "correlate_errors_with_traces",
                "arguments": {
                    "thread_id": self.thread_id,
                    "time_window_minutes": 30,
                    "include_performance_impact": True
                }
            })
            
            if response.status_code == 200:
                print("✅ Error correlation analysis completed")
                self.test_results.append(("correlate_errors_with_traces", True, "Success"))
            else:
                print(f"❌ Error correlation failed: {response.status_code}")
                self.test_results.append(("correlate_errors_with_traces", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Error correlation error: {e}")
            self.test_results.append(("correlate_errors_with_traces", False, str(e)))
    
    async def test_generate_debug_report(self):
        """Test generating debug report"""
        print("\n📋 Testing: Generate Debug Report")
        try:
            response = requests.post(f"{self.base_url}/mcp/call_tool", json={
                "name": "generate_debug_report",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "report_type": "detailed",
                    "include_timeline": True,
                    "include_recommendations": True
                }
            })
            
            if response.status_code == 200:
                print("✅ Debug report generated")
                self.test_results.append(("generate_debug_report", True, "Success"))
            else:
                print(f"❌ Debug report generation failed: {response.status_code}")
                self.test_results.append(("generate_debug_report", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Debug report generation error: {e}")
            self.test_results.append(("generate_debug_report", False, str(e)))
    
    async def test_monitor_langgraph_server_health(self):
        """Test monitoring LangGraph server health"""
        print("\n📋 Testing: Monitor LangGraph Server Health")
        try:
            response = requests.post(f"{self.base_url}/mcp/call_tool", json={
                "name": "monitor_langgraph_server_health",
                "arguments": {
                    "server_url": "http://127.0.0.1:2024",
                    "check_endpoints": True,
                    "performance_metrics": True
                }
            })
            
            if response.status_code == 200:
                print("✅ LangGraph server health monitored")
                self.test_results.append(("monitor_langgraph_server_health", True, "Success"))
            else:
                print(f"❌ LangGraph server health monitoring failed: {response.status_code}")
                self.test_results.append(("monitor_langgraph_server_health", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ LangGraph server health monitoring error: {e}")
            self.test_results.append(("monitor_langgraph_server_health", False, str(e)))
    
    async def test_trace_workflow_execution(self):
        """Test tracing workflow execution"""
        print("\n📋 Testing: Trace Workflow Execution")
        try:
            response = requests.post(f"{self.base_url}/mcp/call_tool", json={
                "name": "trace_workflow_execution",
                "arguments": {
                    "workflow_name": self.workflow_id,
                    "thread_id": self.thread_id,
                    "include_node_details": True,
                    "include_state_changes": True
                }
            })
            
            if response.status_code == 200:
                print("✅ Workflow execution traced")
                self.test_results.append(("trace_workflow_execution", True, "Success"))
            else:
                print(f"❌ Workflow execution tracing failed: {response.status_code}")
                self.test_results.append(("trace_workflow_execution", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Workflow execution tracing error: {e}")
            self.test_results.append(("trace_workflow_execution", False, str(e)))
    
    async def test_optimize_agent_performance(self):
        """Test optimizing agent performance"""
        print("\n📋 Testing: Optimize Agent Performance")
        try:
            response = requests.post(f"{self.base_url}/mcp/call_tool", json={
                "name": "optimize_agent_performance",
                "arguments": {
                    "agent_id": self.agent_id,
                    "thread_id": self.thread_id,
                    "optimization_focus": "speed",
                    "include_benchmarks": True
                }
            })
            
            if response.status_code == 200:
                print("✅ Agent performance optimization completed")
                self.test_results.append(("optimize_agent_performance", True, "Success"))
            else:
                print(f"❌ Agent performance optimization failed: {response.status_code}")
                self.test_results.append(("optimize_agent_performance", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Agent performance optimization error: {e}")
            self.test_results.append(("optimize_agent_performance", False, str(e)))
    
    async def test_get_debug_session_status(self):
        """Test getting debug session status"""
        print("\n📋 Testing: Get Debug Session Status")
        try:
            response = requests.post(f"{self.base_url}/mcp/call_tool", json={
                "name": "get_debug_session_status",
                "arguments": {
                    "session_name": "enhanced_test_session",
                    "include_recommendations": True
                }
            })
            
            if response.status_code == 200:
                print("✅ Debug session status retrieved")
                self.test_results.append(("get_debug_session_status", True, "Success"))
            else:
                print(f"❌ Debug session status failed: {response.status_code}")
                self.test_results.append(("get_debug_session_status", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Debug session status error: {e}")
            self.test_results.append(("get_debug_session_status", False, str(e)))
    
    def generate_final_report(self):
        """Generate final test report"""
        print("\n" + "=" * 60)
        print("📊 ENHANCED OBSERVABILITY TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r[1]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"🎯 Overall Success Rate: {success_rate:.1f}%")
        print(f"⏱️ Total Duration: {time.time():.2f} seconds")
        print(f"✅ Passed Tests: {passed_tests}")
        print(f"❌ Failed Tests: {failed_tests}")
        print(f"📊 Total Tests: {total_tests}")
        
        print("\n📋 Detailed Results:")
        print("-" * 40)
        for test_name, passed, message in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name} - {message}")
        
        print("\n💡 Recommendations:")
        print("-" * 40)
        if success_rate >= 90:
            print("🎉 Excellent! Enhanced observability system is working perfectly")
        elif success_rate >= 70:
            print("👍 Good! Most features are working, minor issues to address")
        elif success_rate >= 50:
            print("⚠️ Fair! Some features need attention")
        else:
            print("❌ Needs work! Multiple features require fixes")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "test_results": [
                {"test_name": r[0], "passed": r[1], "message": r[2]} 
                for r in self.test_results
            ]
        }
        
        with open("enhanced_observability_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: enhanced_observability_test_report.json")
        
        if success_rate < 100:
            print(f"\n⚠️ System needs attention. Success rate: {success_rate:.1f}%")
        else:
            print(f"\n🎉 Perfect! All enhanced observability features are working! Success rate: {success_rate:.1f}%")

async def main():
    """Main test function"""
    tester = EnhancedObservabilityTester()
    await tester.test_enhanced_observability_features()

if __name__ == "__main__":
    asyncio.run(main())

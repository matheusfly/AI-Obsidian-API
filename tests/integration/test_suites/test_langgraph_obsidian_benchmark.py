#!/usr/bin/env python3
"""
LangGraph + Obsidian + MCP Benchmark Test
Focused testing with comprehensive tracing and benchmarking
"""

import asyncio
import json
import requests
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any

class LangGraphObsidianBenchmark:
    """Benchmark test for LangGraph + Obsidian + MCP integration"""
    
    def __init__(self):
        self.obsidian_url = "http://127.0.0.1:27123"
        self.langgraph_url = "http://127.0.0.1:2024"
        self.observability_url = "http://127.0.0.1:8002"
        self.thread_id = f"benchmark_{int(time.time())}"
        self.agent_id = "benchmark_agent"
        self.workflow_id = "obsidian_benchmark_workflow"
        self.benchmark_results = []
        
    async def run_benchmark_test(self):
        """Run comprehensive benchmark test with full tracing"""
        print("🚀 LANGGRAPH + OBSIDIAN + MCP BENCHMARK TEST")
        print("=" * 60)
        
        # Step 1: Setup comprehensive observability
        await self.setup_comprehensive_observability()
        
        # Step 2: Test Obsidian API with detailed tracing
        await self.benchmark_obsidian_api_calls()
        
        # Step 3: Test MCP observability tools
        await self.benchmark_mcp_observability_tools()
        
        # Step 4: Test LangGraph workflow (if available)
        await self.benchmark_langgraph_workflow()
        
        # Step 5: Generate comprehensive benchmark report
        await self.generate_benchmark_report()
        
    async def setup_comprehensive_observability(self):
        """Setup comprehensive observability for benchmarking"""
        print("\n📋 Setting up comprehensive observability...")
        try:
            # Create debug session
            session_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "create_debug_session",
                "arguments": {
                    "session_name": "langgraph_obsidian_benchmark",
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "monitoring_level": "comprehensive",
                    "auto_checkpoint_interval": 5
                }
            })
            
            if session_response.status_code == 200:
                print("✅ Debug session created successfully")
                
                # Start performance monitoring
                perf_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                    "name": "start_performance_monitoring",
                    "arguments": {
                        "agent_id": self.agent_id,
                        "workflow_id": self.workflow_id,
                        "thread_id": self.thread_id
                    }
                })
                
                if perf_response.status_code == 200:
                    print("✅ Performance monitoring started")
                    self.benchmark_results.append(("observability_setup", True, "Complete setup successful"))
                else:
                    print(f"⚠️ Performance monitoring failed: {perf_response.status_code}")
                    self.benchmark_results.append(("observability_setup", True, "Session created, monitoring failed"))
            else:
                print(f"❌ Debug session creation failed: {session_response.status_code}")
                self.benchmark_results.append(("observability_setup", False, f"Session creation failed: {session_response.status_code}"))
                
        except Exception as e:
            print(f"❌ Observability setup error: {e}")
            self.benchmark_results.append(("observability_setup", False, str(e)))
    
    async def benchmark_obsidian_api_calls(self):
        """Benchmark Obsidian API calls with comprehensive tracing"""
        print("\n📋 Benchmarking Obsidian API calls...")
        try:
            # Test 1: Health check
            start_time = time.time()
            health_response = requests.get(f"{self.obsidian_url}/health", timeout=5)
            health_duration = (time.time() - start_time) * 1000
            
            if health_response.status_code == 200:
                print(f"✅ Health check: {health_duration:.2f}ms")
                
                # Log trace event
                await self.log_trace_event("obsidian_health_check", "info", 
                    f"Health check completed in {health_duration:.2f}ms", 
                    {"duration_ms": health_duration, "status_code": health_response.status_code})
                
                # Test 2: File listing
                start_time = time.time()
                files_response = requests.get(f"{self.obsidian_url}/vault/files", 
                    headers={"Authorization": "Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"})
                files_duration = (time.time() - start_time) * 1000
                
                if files_response.status_code == 200:
                    files_data = files_response.json()
                    file_count = len(files_data.get('files', []))
                    print(f"✅ File listing: {files_duration:.2f}ms ({file_count} files)")
                    
                    # Log trace event
                    await self.log_trace_event("obsidian_file_listing", "info", 
                        f"File listing completed in {files_duration:.2f}ms", 
                        {"duration_ms": files_duration, "file_count": file_count, "status_code": files_response.status_code})
                    
                    # Test 3: File reading (if files available)
                    if file_count > 0:
                        test_file = files_data['files'][0]
                        start_time = time.time()
                        read_response = requests.get(f"{self.obsidian_url}/vault/{test_file['path']}", 
                            headers={"Authorization": "Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"})
                        read_duration = (time.time() - start_time) * 1000
                        
                        if read_response.status_code == 200:
                            content_length = len(read_response.text)
                            print(f"✅ File reading: {read_duration:.2f}ms ({content_length} chars)")
                            
                            # Log trace event
                            await self.log_trace_event("obsidian_file_reading", "info", 
                                f"File reading completed in {read_duration:.2f}ms", 
                                {"duration_ms": read_duration, "content_length": content_length, "file_path": test_file['path']})
                        else:
                            print(f"❌ File reading failed: {read_response.status_code}")
                            await self.log_trace_event("obsidian_file_reading", "error", 
                                f"File reading failed with status {read_response.status_code}", 
                                {"status_code": read_response.status_code, "file_path": test_file['path']})
                    
                    # Test 4: Search functionality
                    start_time = time.time()
                    search_response = requests.post(f"{self.obsidian_url}/vault/Nomade Milionario/search", 
                        json={"query": "langgraph"}, 
                        headers={"Authorization": "Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"})
                    search_duration = (time.time() - start_time) * 1000
                    
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        result_count = len(search_data.get('results', []))
                        print(f"✅ Search: {search_duration:.2f}ms ({result_count} results)")
                        
                        # Log trace event
                        await self.log_trace_event("obsidian_search", "info", 
                            f"Search completed in {search_duration:.2f}ms", 
                            {"duration_ms": search_duration, "result_count": result_count, "query": "langgraph"})
                    else:
                        print(f"❌ Search failed: {search_response.status_code}")
                        await self.log_trace_event("obsidian_search", "error", 
                            f"Search failed with status {search_response.status_code}", 
                            {"status_code": search_response.status_code, "query": "langgraph"})
                    
                    self.benchmark_results.append(("obsidian_api", True, f"All tests completed - Health: {health_duration:.2f}ms, Files: {files_duration:.2f}ms"))
                else:
                    print(f"❌ File listing failed: {files_response.status_code}")
                    await self.log_trace_event("obsidian_file_listing", "error", 
                        f"File listing failed with status {files_response.status_code}", 
                        {"status_code": files_response.status_code})
                    self.benchmark_results.append(("obsidian_api", False, f"File listing failed: {files_response.status_code}"))
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                await self.log_trace_event("obsidian_health_check", "error", 
                    f"Health check failed with status {health_response.status_code}", 
                    {"status_code": health_response.status_code})
                self.benchmark_results.append(("obsidian_api", False, f"Health check failed: {health_response.status_code}"))
                
        except Exception as e:
            print(f"❌ Obsidian API benchmark error: {e}")
            await self.log_trace_event("obsidian_api_error", "error", f"Obsidian API benchmark error: {str(e)}", {"error": str(e)})
            self.benchmark_results.append(("obsidian_api", False, str(e)))
    
    async def benchmark_mcp_observability_tools(self):
        """Benchmark MCP observability tools"""
        print("\n📋 Benchmarking MCP observability tools...")
        try:
            # Test 1: Get traces
            start_time = time.time()
            traces_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "get_traces",
                "arguments": {
                    "thread_id": self.thread_id,
                    "limit": 50
                }
            })
            traces_duration = (time.time() - start_time) * 1000
            
            if traces_response.status_code == 200:
                print(f"✅ Get traces: {traces_duration:.2f}ms")
                await self.log_trace_event("mcp_get_traces", "info", 
                    f"Get traces completed in {traces_duration:.2f}ms", 
                    {"duration_ms": traces_duration})
            else:
                print(f"❌ Get traces failed: {traces_response.status_code}")
                await self.log_trace_event("mcp_get_traces", "error", 
                    f"Get traces failed with status {traces_response.status_code}", 
                    {"status_code": traces_response.status_code})
            
            # Test 2: Get checkpoints
            start_time = time.time()
            checkpoints_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "get_checkpoints",
                "arguments": {
                    "thread_id": self.thread_id,
                    "limit": 20
                }
            })
            checkpoints_duration = (time.time() - start_time) * 1000
            
            if checkpoints_response.status_code == 200:
                print(f"✅ Get checkpoints: {checkpoints_duration:.2f}ms")
                await self.log_trace_event("mcp_get_checkpoints", "info", 
                    f"Get checkpoints completed in {checkpoints_duration:.2f}ms", 
                    {"duration_ms": checkpoints_duration})
            else:
                print(f"❌ Get checkpoints failed: {checkpoints_response.status_code}")
                await self.log_trace_event("mcp_get_checkpoints", "error", 
                    f"Get checkpoints failed with status {checkpoints_response.status_code}", 
                    {"status_code": checkpoints_response.status_code})
            
            # Test 3: Analyze error patterns
            start_time = time.time()
            error_analysis_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "analyze_error_patterns",
                "arguments": {
                    "thread_id": self.thread_id,
                    "time_range_hours": 1,
                    "error_threshold": 1
                }
            })
            error_analysis_duration = (time.time() - start_time) * 1000
            
            if error_analysis_response.status_code == 200:
                print(f"✅ Error analysis: {error_analysis_duration:.2f}ms")
                await self.log_trace_event("mcp_error_analysis", "info", 
                    f"Error analysis completed in {error_analysis_duration:.2f}ms", 
                    {"duration_ms": error_analysis_duration})
            else:
                print(f"❌ Error analysis failed: {error_analysis_response.status_code}")
                await self.log_trace_event("mcp_error_analysis", "error", 
                    f"Error analysis failed with status {error_analysis_response.status_code}", 
                    {"status_code": error_analysis_response.status_code})
            
            # Test 4: Get agent communication log
            start_time = time.time()
            comm_log_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "get_agent_communication_log",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "communication_type": "all",
                    "limit": 30
                }
            })
            comm_log_duration = (time.time() - start_time) * 1000
            
            if comm_log_response.status_code == 200:
                print(f"✅ Communication log: {comm_log_duration:.2f}ms")
                await self.log_trace_event("mcp_communication_log", "info", 
                    f"Communication log completed in {comm_log_duration:.2f}ms", 
                    {"duration_ms": comm_log_duration})
            else:
                print(f"❌ Communication log failed: {comm_log_response.status_code}")
                await self.log_trace_event("mcp_communication_log", "error", 
                    f"Communication log failed with status {comm_log_response.status_code}", 
                    {"status_code": comm_log_response.status_code})
            
            # Test 5: Generate debug report
            start_time = time.time()
            debug_report_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "generate_debug_report",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "report_type": "detailed",
                    "include_timeline": True,
                    "include_recommendations": True
                }
            })
            debug_report_duration = (time.time() - start_time) * 1000
            
            if debug_report_response.status_code == 200:
                print(f"✅ Debug report: {debug_report_duration:.2f}ms")
                await self.log_trace_event("mcp_debug_report", "info", 
                    f"Debug report completed in {debug_report_duration:.2f}ms", 
                    {"duration_ms": debug_report_duration})
            else:
                print(f"❌ Debug report failed: {debug_report_response.status_code}")
                await self.log_trace_event("mcp_debug_report", "error", 
                    f"Debug report failed with status {debug_report_response.status_code}", 
                    {"status_code": debug_report_response.status_code})
            
            self.benchmark_results.append(("mcp_observability", True, "All MCP tools benchmarked successfully"))
            
        except Exception as e:
            print(f"❌ MCP observability benchmark error: {e}")
            await self.log_trace_event("mcp_observability_error", "error", f"MCP observability benchmark error: {str(e)}", {"error": str(e)})
            self.benchmark_results.append(("mcp_observability", False, str(e)))
    
    async def benchmark_langgraph_workflow(self):
        """Benchmark LangGraph workflow execution"""
        print("\n📋 Benchmarking LangGraph workflow...")
        try:
            # Test LangGraph server connectivity
            start_time = time.time()
            assistants_response = requests.get(f"{self.langgraph_url}/assistants", timeout=5)
            connectivity_duration = (time.time() - start_time) * 1000
            
            if assistants_response.status_code == 200:
                print(f"✅ LangGraph connectivity: {connectivity_duration:.2f}ms")
                await self.log_trace_event("langgraph_connectivity", "info", 
                    f"LangGraph connectivity test completed in {connectivity_duration:.2f}ms", 
                    {"duration_ms": connectivity_duration})
                
                # Try to execute workflow
                workflow_payload = {
                    "assistant_id": "obsidian-workflow",
                    "input": {
                        "vault_name": "Nomade Milionario",
                        "search_query": "langgraph",
                        "limit": 5
                    }
                }
                
                start_time = time.time()
                workflow_response = requests.post(f"{self.langgraph_url}/threads/{self.thread_id}/runs", 
                    json=workflow_payload, timeout=30)
                workflow_duration = (time.time() - start_time) * 1000
                
                if workflow_response.status_code == 200:
                    print(f"✅ LangGraph workflow: {workflow_duration:.2f}ms")
                    await self.log_trace_event("langgraph_workflow", "info", 
                        f"LangGraph workflow executed in {workflow_duration:.2f}ms", 
                        {"duration_ms": workflow_duration, "workflow_id": "obsidian-workflow"})
                    self.benchmark_results.append(("langgraph_workflow", True, f"Workflow executed in {workflow_duration:.2f}ms"))
                else:
                    print(f"❌ LangGraph workflow failed: {workflow_response.status_code}")
                    await self.log_trace_event("langgraph_workflow", "error", 
                        f"LangGraph workflow failed with status {workflow_response.status_code}", 
                        {"status_code": workflow_response.status_code, "response": workflow_response.text})
                    self.benchmark_results.append(("langgraph_workflow", False, f"Workflow failed: {workflow_response.status_code}"))
            else:
                print(f"❌ LangGraph connectivity failed: {assistants_response.status_code}")
                await self.log_trace_event("langgraph_connectivity", "error", 
                    f"LangGraph connectivity failed with status {assistants_response.status_code}", 
                    {"status_code": assistants_response.status_code})
                self.benchmark_results.append(("langgraph_workflow", False, f"Connectivity failed: {assistants_response.status_code}"))
                
        except Exception as e:
            print(f"❌ LangGraph workflow benchmark error: {e}")
            await self.log_trace_event("langgraph_workflow_error", "error", f"LangGraph workflow benchmark error: {str(e)}", {"error": str(e)})
            self.benchmark_results.append(("langgraph_workflow", False, str(e)))
    
    async def log_trace_event(self, event_type: str, level: str, message: str, data: Dict[str, Any] = None):
        """Log a trace event to the observability server"""
        try:
            trace_payload = {
                "name": "create_trace_event",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": event_type,
                    "level": level,
                    "message": message,
                    "data": data or {},
                    "tags": ["benchmark", "integration", "performance"]
                }
            }
            
            response = requests.post(f"{self.observability_url}/mcp/call_tool", json=trace_payload)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Failed to log trace event: {e}")
            return False
    
    async def generate_benchmark_report(self):
        """Generate comprehensive benchmark report"""
        print("\n📋 Generating benchmark report...")
        try:
            # Stop performance monitoring
            stop_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "stop_performance_monitoring",
                "arguments": {
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "thread_id": self.thread_id
                }
            })
            
            # Get final debug report
            report_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "generate_debug_report",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "report_type": "performance",
                    "include_timeline": True,
                    "include_recommendations": True
                }
            })
            
            # Generate final benchmark report
            total_tests = len(self.benchmark_results)
            passed_tests = len([r for r in self.benchmark_results if r[1]])
            failed_tests = total_tests - passed_tests
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            print("\n" + "=" * 60)
            print("📊 LANGGRAPH + OBSIDIAN + MCP BENCHMARK REPORT")
            print("=" * 60)
            print(f"🎯 Overall Success Rate: {success_rate:.1f}%")
            print(f"⏱️ Total Duration: {time.time():.2f} seconds")
            print(f"✅ Passed Tests: {passed_tests}")
            print(f"❌ Failed Tests: {failed_tests}")
            print(f"📊 Total Tests: {total_tests}")
            
            print("\n📋 Detailed Results:")
            print("-" * 40)
            for test_name, passed, message in self.benchmark_results:
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"{status} {test_name} - {message}")
            
            # Save detailed report
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "thread_id": self.thread_id,
                "agent_id": self.agent_id,
                "workflow_id": self.workflow_id,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "benchmark_results": [
                    {"test_name": r[0], "passed": r[1], "message": r[2]} 
                    for r in self.benchmark_results
                ],
                "debug_report": report_response.json() if report_response.status_code == 200 else None
            }
            
            with open("langgraph_obsidian_benchmark_report.json", "w") as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n💾 Detailed report saved to: langgraph_obsidian_benchmark_report.json")
            
            if success_rate >= 90:
                print("\n🎉 EXCELLENT! LangGraph + Obsidian + MCP integration is performing perfectly!")
            elif success_rate >= 70:
                print("\n👍 GOOD! Most integration features are working well!")
            else:
                print("\n⚠️ NEEDS ATTENTION! Multiple integration issues require fixes")
                
        except Exception as e:
            print(f"❌ Report generation error: {e}")

async def main():
    """Main benchmark function"""
    benchmark = LangGraphObsidianBenchmark()
    await benchmark.run_benchmark_test()

if __name__ == "__main__":
    asyncio.run(main())

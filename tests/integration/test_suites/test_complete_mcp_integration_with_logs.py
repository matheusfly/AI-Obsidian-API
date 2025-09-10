#!/usr/bin/env python3
"""
Complete MCP Integration Test with Full Logging
Tests all MCP servers with comprehensive logging and reporting
"""

import asyncio
import json
import logging
import requests
import time
import subprocess
import signal
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_integration_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CompleteMCPIntegrationTest:
    """Complete MCP Integration Test with Full Logging"""
    
    def __init__(self):
        self.mcp_integration_url = "http://127.0.0.1:8003"
        self.langgraph_url = "http://127.0.0.1:2024"
        self.observability_url = "http://127.0.0.1:8002"
        self.debug_dashboard_url = "http://127.0.0.1:8004"
        self.mock_obsidian_url = "http://127.0.0.1:8001"
        
        self.processes = {}
        self.test_results = []
        self.detailed_logs = []
        self.performance_metrics = {}
        
    async def run_complete_integration_test(self):
        """Run complete MCP integration test with full logging"""
        logger.info("🚀 STARTING COMPLETE MCP INTEGRATION TEST WITH FULL LOGGING")
        logger.info("=" * 80)
        
        try:
            # Step 1: Start all services
            await self.start_all_services()
            
            # Step 2: Test MCP Integration Server
            await self.test_mcp_integration_server_comprehensive()
            
            # Step 3: Test all MCP servers individually
            await self.test_all_mcp_servers()
            
            # Step 4: Test MCP tool calls with real queries
            await self.test_mcp_tool_calls_with_queries()
            
            # Step 5: Test LangGraph integration
            await self.test_langgraph_integration_comprehensive()
            
            # Step 6: Test observability and debugging
            await self.test_observability_system()
            
            # Step 7: Test complete workflow
            await self.test_complete_workflow()
            
            # Step 8: Generate comprehensive report
            await self.generate_comprehensive_report()
            
        except Exception as e:
            logger.error(f"❌ Test failed with error: {e}", exc_info=True)
        finally:
            await self.cleanup_all_services()
    
    async def start_all_services(self):
        """Start all required services"""
        logger.info("📋 Starting all services...")
        
        services = [
            ("mock_obsidian", ["python", "mock_obsidian_api.py"], 8001),
            ("mcp_integration", ["python", "mcp_tools/mcp_integration_server.py"], 8003),
            ("observability", ["python", "mcp_tools/http_observability_server.py"], 8002),
            ("debug_dashboard", ["python", "mcp_tools/mcp_debug_dashboard.py"], 8004),
            ("langgraph_server", ["python", "langgraph_server/main.py"], 2024)
        ]
        
        for service_name, command, port in services:
            try:
                logger.info(f"  Starting {service_name} on port {port}...")
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.processes[service_name] = process
                
                # Wait for service to start
                await asyncio.sleep(3)
                
                # Test if service is running
                try:
                    response = requests.get(f"http://127.0.0.1:{port}/health", timeout=5)
                    if response.status_code == 200:
                        logger.info(f"  ✅ {service_name} started successfully")
                    else:
                        logger.warning(f"  ⚠️ {service_name} responded with {response.status_code}")
                except:
                    logger.warning(f"  ⚠️ {service_name} health check failed, but continuing...")
                    
            except Exception as e:
                logger.error(f"  ❌ Failed to start {service_name}: {e}")
    
    async def test_mcp_integration_server_comprehensive(self):
        """Test MCP Integration Server with comprehensive logging"""
        logger.info("📋 Testing MCP Integration Server (Comprehensive)...")
        
        try:
            # Test health endpoint
            start_time = time.time()
            health_response = requests.get(f"{self.mcp_integration_url}/health", timeout=10)
            health_duration = (time.time() - start_time) * 1000
            
            logger.info(f"  Health check: {health_duration:.2f}ms - Status: {health_response.status_code}")
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                logger.info(f"  ✅ MCP Integration Server healthy - {health_data.get('mcp_servers', 0)} servers")
                
                # Test list servers
                start_time = time.time()
                servers_response = requests.get(f"{self.mcp_integration_url}/mcp/servers", timeout=10)
                servers_duration = (time.time() - start_time) * 1000
                
                logger.info(f"  List servers: {servers_duration:.2f}ms - Status: {servers_response.status_code}")
                
                if servers_response.status_code == 200:
                    servers_data = servers_response.json()
                    server_count = len(servers_data.get("servers", []))
                    logger.info(f"  ✅ Discovered {server_count} MCP servers")
                    
                    # Log all discovered servers
                    for server in servers_data.get("servers", []):
                        logger.info(f"    - {server}")
                    
                    self.test_results.append(("mcp_integration_server", True, f"Healthy - {server_count} servers discovered"))
                else:
                    logger.error(f"  ❌ List servers failed: {servers_response.status_code}")
                    self.test_results.append(("mcp_integration_server", False, f"List servers failed: {servers_response.status_code}"))
            else:
                logger.error(f"  ❌ Health check failed: {health_response.status_code}")
                self.test_results.append(("mcp_integration_server", False, f"Health check failed: {health_response.status_code}"))
                
        except Exception as e:
            logger.error(f"  ❌ MCP Integration Server test error: {e}", exc_info=True)
            self.test_results.append(("mcp_integration_server", False, str(e)))
    
    async def test_all_mcp_servers(self):
        """Test all MCP servers individually"""
        logger.info("📋 Testing all MCP servers individually...")
        
        try:
            # Get list of servers
            servers_response = requests.get(f"{self.mcp_integration_url}/mcp/servers", timeout=10)
            if servers_response.status_code != 200:
                logger.error("  ❌ Cannot get server list")
                return
            
            servers_data = servers_response.json()
            available_servers = servers_data.get("servers", [])
            
            logger.info(f"  Testing {len(available_servers)} MCP servers...")
            
            tested_servers = 0
            successful_servers = 0
            
            for server_name in available_servers:
                try:
                    logger.info(f"    Testing {server_name}...")
                    
                    # Get server info
                    start_time = time.time()
                    server_info_response = requests.get(f"{self.mcp_integration_url}/mcp/servers/{server_name}", timeout=5)
                    server_info_duration = (time.time() - start_time) * 1000
                    
                    if server_info_response.status_code == 200:
                        server_info = server_info_response.json()
                        status = server_info.get("status", "unknown")
                        logger.info(f"      ✅ {server_name}: {status} ({server_info_duration:.2f}ms)")
                        successful_servers += 1
                    else:
                        logger.warning(f"      ⚠️ {server_name}: Failed to get info ({server_info_response.status_code})")
                    
                    tested_servers += 1
                    
                except Exception as e:
                    logger.error(f"      ❌ {server_name}: Error - {e}")
            
            logger.info(f"  ✅ Tested {tested_servers} servers, {successful_servers} successful")
            self.test_results.append(("mcp_server_testing", True, f"Tested {tested_servers} servers, {successful_servers} successful"))
            
        except Exception as e:
            logger.error(f"  ❌ MCP server testing error: {e}", exc_info=True)
            self.test_results.append(("mcp_server_testing", False, str(e)))
    
    async def test_mcp_tool_calls_with_queries(self):
        """Test MCP tool calls with real queries"""
        logger.info("📋 Testing MCP tool calls with real queries...")
        
        try:
            # Test queries to try
            test_queries = [
                {
                    "server": "brave-search",
                    "tool": "brave_web_search",
                    "arguments": {"query": "langgraph MCP integration", "count": 3}
                },
                {
                    "server": "sequential-thinking",
                    "tool": "sequentialthinking",
                    "arguments": {
                        "thought": "How can we improve MCP integration with LangGraph?",
                        "nextThoughtNeeded": True,
                        "thoughtNumber": 1,
                        "totalThoughts": 3
                    }
                },
                {
                    "server": "obsidian-vault",
                    "tool": "list_files",
                    "arguments": {"vault_path": "D:\\Nomade Milionario"}
                }
            ]
            
            successful_calls = 0
            total_calls = len(test_queries)
            
            for i, query in enumerate(test_queries, 1):
                try:
                    logger.info(f"    Query {i}/{total_calls}: {query['server']}.{query['tool']}")
                    
                    start_time = time.time()
                    call_response = requests.post(f"{self.mcp_integration_url}/mcp/call", 
                        json=query, timeout=30)
                    call_duration = (time.time() - start_time) * 1000
                    
                    if call_response.status_code == 200:
                        call_data = call_response.json()
                        success = call_data.get("success", False)
                        execution_time = call_data.get("execution_time_ms", 0)
                        
                        if success:
                            logger.info(f"      ✅ Success: {execution_time:.2f}ms")
                            successful_calls += 1
                        else:
                            logger.warning(f"      ⚠️ Tool call failed: {call_data.get('error', 'Unknown error')}")
                    else:
                        logger.warning(f"      ⚠️ HTTP {call_response.status_code}: {call_response.text}")
                    
                    logger.info(f"      Duration: {call_duration:.2f}ms")
                    
                except Exception as e:
                    logger.error(f"      ❌ Query {i} error: {e}")
            
            success_rate = (successful_calls / total_calls) * 100
            logger.info(f"  ✅ Tool calls: {successful_calls}/{total_calls} successful ({success_rate:.1f}%)")
            self.test_results.append(("mcp_tool_calls", True, f"{successful_calls}/{total_calls} successful ({success_rate:.1f}%)"))
            
        except Exception as e:
            logger.error(f"  ❌ MCP tool calls test error: {e}", exc_info=True)
            self.test_results.append(("mcp_tool_calls", False, str(e)))
    
    async def test_langgraph_integration_comprehensive(self):
        """Test LangGraph integration comprehensively"""
        logger.info("📋 Testing LangGraph integration (Comprehensive)...")
        
        try:
            # Test LangGraph server
            start_time = time.time()
            langgraph_response = requests.get(f"{self.langgraph_url}/assistants", timeout=10)
            langgraph_duration = (time.time() - start_time) * 1000
            
            logger.info(f"  LangGraph server: {langgraph_duration:.2f}ms - Status: {langgraph_response.status_code}")
            
            if langgraph_response.status_code in [200, 405]:  # 405 is expected for GET on /assistants
                logger.info("  ✅ LangGraph server is accessible")
                
                # Try to create an assistant
                try:
                    assistant_payload = {
                        "graph_id": "mcp-integrated-agent",
                        "config": {
                            "configurable": {
                                "thread_id": f"test_thread_{int(time.time())}"
                            }
                        }
                    }
                    
                    start_time = time.time()
                    assistant_response = requests.post(f"{self.langgraph_url}/assistants", 
                        json=assistant_payload, timeout=15)
                    assistant_duration = (time.time() - start_time) * 1000
                    
                    logger.info(f"  Assistant creation: {assistant_duration:.2f}ms - Status: {assistant_response.status_code}")
                    
                    if assistant_response.status_code == 200:
                        assistant_data = assistant_response.json()
                        assistant_id = assistant_data.get("assistant_id")
                        logger.info(f"  ✅ Assistant created: {assistant_id}")
                        
                        # Create thread
                        thread_payload = {
                            "metadata": {
                                "test": "mcp_langgraph_integration",
                                "timestamp": datetime.now().isoformat()
                            }
                        }
                        
                        start_time = time.time()
                        thread_response = requests.post(f"{self.langgraph_url}/threads", 
                            json=thread_payload, timeout=15)
                        thread_duration = (time.time() - start_time) * 1000
                        
                        logger.info(f"  Thread creation: {thread_duration:.2f}ms - Status: {thread_response.status_code}")
                        
                        if thread_response.status_code == 200:
                            thread_data = thread_response.json()
                            thread_id = thread_data.get("thread_id")
                            logger.info(f"  ✅ Thread created: {thread_id}")
                            
                            self.test_results.append(("langgraph_integration", True, f"Assistant: {assistant_id}, Thread: {thread_id}"))
                        else:
                            logger.warning(f"  ⚠️ Thread creation failed: {thread_response.status_code}")
                            self.test_results.append(("langgraph_integration", False, f"Thread creation failed: {thread_response.status_code}"))
                    else:
                        logger.warning(f"  ⚠️ Assistant creation failed: {assistant_response.status_code}")
                        self.test_results.append(("langgraph_integration", False, f"Assistant creation failed: {assistant_response.status_code}"))
                        
                except Exception as e:
                    logger.error(f"  ❌ LangGraph integration error: {e}")
                    self.test_results.append(("langgraph_integration", False, str(e)))
            else:
                logger.error(f"  ❌ LangGraph server not accessible: {langgraph_response.status_code}")
                self.test_results.append(("langgraph_integration", False, f"Server not accessible: {langgraph_response.status_code}"))
                
        except Exception as e:
            logger.error(f"  ❌ LangGraph integration test error: {e}", exc_info=True)
            self.test_results.append(("langgraph_integration", False, str(e)))
    
    async def test_observability_system(self):
        """Test observability system"""
        logger.info("📋 Testing observability system...")
        
        try:
            # Test observability server
            start_time = time.time()
            obs_response = requests.get(f"{self.observability_url}/health", timeout=10)
            obs_duration = (time.time() - start_time) * 1000
            
            logger.info(f"  Observability server: {obs_duration:.2f}ms - Status: {obs_response.status_code}")
            
            if obs_response.status_code == 200:
                obs_data = obs_response.json()
                logger.info(f"  ✅ Observability server healthy: {obs_data}")
                
                # Test trace creation
                try:
                    trace_payload = {
                        "name": "create_trace_event",
                        "arguments": {
                            "thread_id": f"test_thread_{int(time.time())}",
                            "agent_id": "test_agent",
                            "workflow_id": "test_workflow",
                            "event_type": "test_event",
                            "level": "info",
                            "message": "Test trace event from comprehensive test",
                            "data": {"test": "value"},
                            "tags": ["comprehensive_test", "mcp_integration"]
                        }
                    }
                    
                    start_time = time.time()
                    trace_response = requests.post(f"{self.observability_url}/tool", 
                        json=trace_payload, timeout=15)
                    trace_duration = (time.time() - start_time) * 1000
                    
                    logger.info(f"  Trace creation: {trace_duration:.2f}ms - Status: {trace_response.status_code}")
                    
                    if trace_response.status_code == 200:
                        trace_data = trace_response.json()
                        logger.info(f"  ✅ Trace created successfully: {trace_data}")
                        self.test_results.append(("observability_system", True, "Trace creation successful"))
                    else:
                        logger.warning(f"  ⚠️ Trace creation failed: {trace_response.status_code}")
                        self.test_results.append(("observability_system", False, f"Trace creation failed: {trace_response.status_code}"))
                        
                except Exception as e:
                    logger.error(f"  ❌ Trace creation error: {e}")
                    self.test_results.append(("observability_system", False, str(e)))
            else:
                logger.error(f"  ❌ Observability server not accessible: {obs_response.status_code}")
                self.test_results.append(("observability_system", False, f"Server not accessible: {obs_response.status_code}"))
                
        except Exception as e:
            logger.error(f"  ❌ Observability system test error: {e}", exc_info=True)
            self.test_results.append(("observability_system", False, str(e)))
    
    async def test_complete_workflow(self):
        """Test complete workflow integration"""
        logger.info("📋 Testing complete workflow integration...")
        
        try:
            # Test complete integration
            integration_test = subprocess.Popen(
                ["python", "test_complete_integration.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = integration_test.communicate(timeout=60)
            
            logger.info("  Complete integration test output:")
            logger.info(f"  STDOUT: {stdout}")
            if stderr:
                logger.info(f"  STDERR: {stderr}")
            
            if integration_test.returncode == 0:
                logger.info("  ✅ Complete workflow integration successful")
                self.test_results.append(("complete_workflow", True, "Integration test passed"))
            else:
                logger.warning(f"  ⚠️ Complete workflow integration failed with return code: {integration_test.returncode}")
                self.test_results.append(("complete_workflow", False, f"Integration test failed: {integration_test.returncode}"))
                
        except Exception as e:
            logger.error(f"  ❌ Complete workflow test error: {e}", exc_info=True)
            self.test_results.append(("complete_workflow", False, str(e)))
    
    async def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        logger.info("📊 GENERATING COMPREHENSIVE TEST REPORT")
        logger.info("=" * 80)
        
        try:
            # Calculate success metrics
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r[1]])
            failed_tests = total_tests - passed_tests
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            logger.info(f"🎯 Overall Success Rate: {success_rate:.1f}%")
            logger.info(f"✅ Passed Tests: {passed_tests}")
            logger.info(f"❌ Failed Tests: {failed_tests}")
            logger.info(f"📊 Total Tests: {total_tests}")
            
            logger.info("\n📋 Detailed Results:")
            logger.info("-" * 50)
            for test_name, passed, message in self.test_results:
                status = "✅ PASS" if passed else "❌ FAIL"
                logger.info(f"{status} {test_name} - {message}")
            
            # Get MCP integration metrics
            try:
                metrics_response = requests.get(f"{self.mcp_integration_url}/mcp/metrics", timeout=10)
                if metrics_response.status_code == 200:
                    mcp_metrics = metrics_response.json()
                    logger.info(f"\n📈 MCP Integration Metrics:")
                    logger.info(f"  Total MCP Calls: {mcp_metrics.get('total_calls', 0)}")
                    logger.info(f"  Successful Calls: {mcp_metrics.get('successful_calls', 0)}")
                    logger.info(f"  Failed Calls: {mcp_metrics.get('failed_calls', 0)}")
                    logger.info(f"  Average Execution Time: {mcp_metrics.get('average_execution_time', 0):.2f}ms")
            except Exception as e:
                logger.warning(f"⚠️ Could not retrieve MCP metrics: {e}")
                mcp_metrics = None
            
            # Save comprehensive report
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "test_type": "complete_mcp_integration_with_logs",
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "test_results": [
                    {"test_name": r[0], "passed": r[1], "message": r[2]} 
                    for r in self.test_results
                ],
                "mcp_metrics": mcp_metrics,
                "services_started": list(self.processes.keys()),
                "log_file": "mcp_integration_test.log"
            }
            
            with open("complete_mcp_integration_report.json", "w") as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"\n💾 Complete report saved to: complete_mcp_integration_report.json")
            logger.info(f"📝 Detailed logs saved to: mcp_integration_test.log")
            
            if success_rate >= 90:
                logger.info("\n🎉 EXCELLENT! Complete MCP integration is working perfectly!")
                logger.info("🚀 All systems are operational with comprehensive logging!")
            elif success_rate >= 70:
                logger.info("\n👍 GOOD! Most MCP integration features are working!")
            else:
                logger.info("\n⚠️ NEEDS ATTENTION! Multiple integration issues require fixes")
                
        except Exception as e:
            logger.error(f"❌ Report generation error: {e}", exc_info=True)
    
    async def cleanup_all_services(self):
        """Cleanup all services"""
        logger.info("🧹 Cleaning up all services...")
        
        for service_name, process in self.processes.items():
            try:
                logger.info(f"  Stopping {service_name}...")
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"  ✅ {service_name} stopped")
            except:
                try:
                    process.kill()
                    logger.info(f"  ✅ {service_name} killed")
                except:
                    logger.warning(f"  ⚠️ Could not stop {service_name}")

async def main():
    """Main function"""
    test = CompleteMCPIntegrationTest()
    try:
        await test.run_complete_integration_test()
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
    finally:
        await test.cleanup_all_services()

if __name__ == "__main__":
    asyncio.run(main())

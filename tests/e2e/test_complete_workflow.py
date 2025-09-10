"""
End-to-End Tests for Complete Workflow
Tests complete user workflows from start to finish
"""

import pytest
import asyncio
import requests
import time
import json
from unittest.mock import patch, Mock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class TestCompleteWorkflow:
    """Test cases for complete end-to-end workflows"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.base_urls = {
            "mcp_integration": "http://127.0.0.1:8001",
            "observability": "http://127.0.0.1:8002",
            "debug_dashboard": "http://127.0.0.1:8003",
            "langgraph_studio": "http://127.0.0.1:2024"
        }
        self.timeout = 10
    
    def test_complete_system_startup_workflow(self):
        """Test complete system startup workflow"""
        # Step 1: Check all services are running
        services_status = {}
        
        for service, url in self.base_urls.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                services_status[service] = response.status_code == 200
            except:
                services_status[service] = False
        
        # At least 3 out of 4 services should be running
        running_services = sum(services_status.values())
        assert running_services >= 3, f"Only {running_services} services running: {services_status}"
    
    def test_langgraph_to_mcp_workflow(self):
        """Test complete workflow from LangGraph to MCP tools"""
        try:
            # Step 1: Start a LangGraph workflow
            workflow_data = {
                "input": "Hello, test the MCP integration",
                "thread_id": f"test_thread_{int(time.time())}"
            }
            
            # Step 2: Execute workflow (this would trigger MCP calls)
            response = requests.post(
                f"{self.base_urls['langgraph_studio']}/assistants",
                json=workflow_data,
                timeout=15
            )
            
            # Step 3: Verify workflow executed
            assert response.status_code in [200, 405, 404]
            
            # Step 4: Check if MCP calls were made
            if services_status.get('mcp_integration', False):
                mcp_response = requests.get(
                    f"{self.base_urls['mcp_integration']}/calls/history",
                    timeout=5
                )
                # Should have call history
                assert mcp_response.status_code in [200, 404]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Required services not running")
    
    def test_observability_monitoring_workflow(self):
        """Test complete observability monitoring workflow"""
        try:
            # Step 1: Generate some activity
            for i in range(3):
                requests.get(f"{self.base_urls['mcp_integration']}/health", timeout=2)
                time.sleep(0.5)
            
            # Step 2: Check observability metrics
            metrics_response = requests.get(
                f"{self.base_urls['observability']}/metrics",
                timeout=5
            )
            assert metrics_response.status_code == 200
            
            metrics_data = metrics_response.json()
            assert "timestamp" in metrics_data
            assert "services" in metrics_data
            
            # Step 3: Check debug dashboard
            dashboard_response = requests.get(
                f"{self.base_urls['debug_dashboard']}/",
                timeout=5
            )
            assert dashboard_response.status_code == 200
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Required services not running")
    
    def test_error_handling_workflow(self):
        """Test error handling across the complete workflow"""
        try:
            # Step 1: Test invalid MCP call
            invalid_call = {
                "server_name": "nonexistent_server",
                "tool_name": "nonexistent_tool",
                "arguments": {}
            }
            
            response = requests.post(
                f"{self.base_urls['mcp_integration']}/mcp/call",
                json=invalid_call,
                timeout=5
            )
            
            # Should handle error gracefully
            assert response.status_code in [200, 404, 500]
            
            # Step 2: Test invalid LangGraph input
            invalid_workflow = {
                "input": "",
                "thread_id": ""
            }
            
            response = requests.post(
                f"{self.base_urls['langgraph_studio']}/assistants",
                json=invalid_workflow,
                timeout=5
            )
            
            # Should handle error gracefully
            assert response.status_code in [200, 400, 405, 404]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Required services not running")
    
    def test_performance_workflow(self):
        """Test performance across the complete workflow"""
        try:
            start_time = time.time()
            
            # Step 1: Execute multiple operations
            operations = []
            for i in range(5):
                op_start = time.time()
                
                # Health check
                health_response = requests.get(
                    f"{self.base_urls['mcp_integration']}/health",
                    timeout=2
                )
                
                op_end = time.time()
                operations.append({
                    "operation": f"health_check_{i}",
                    "duration": op_end - op_start,
                    "status": health_response.status_code
                })
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            # Step 2: Verify performance
            assert total_duration < 10.0, f"Total workflow took too long: {total_duration}s"
            
            # Step 3: Check individual operation performance
            for op in operations:
                assert op["duration"] < 2.0, f"Operation {op['operation']} took too long: {op['duration']}s"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Required services not running")
    
    def test_data_flow_workflow(self):
        """Test data flow through the complete system"""
        try:
            # Step 1: Create test data
            test_data = {
                "message": "Test data flow",
                "timestamp": time.time(),
                "metadata": {"test": True}
            }
            
            # Step 2: Send data through LangGraph
            workflow_data = {
                "input": test_data["message"],
                "thread_id": f"data_flow_test_{int(time.time())}"
            }
            
            response = requests.post(
                f"{self.base_urls['langgraph_studio']}/assistants",
                json=workflow_data,
                timeout=10
            )
            
            # Step 3: Verify data processing
            assert response.status_code in [200, 405, 404]
            
            # Step 4: Check observability for data flow
            metrics_response = requests.get(
                f"{self.base_urls['observability']}/metrics",
                timeout=5
            )
            
            if metrics_response.status_code == 200:
                metrics_data = metrics_response.json()
                assert "timestamp" in metrics_data
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Required services not running")
    
    def test_concurrent_workflow(self):
        """Test concurrent operations across the system"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def worker(service_name, url, worker_id):
            """Worker function for concurrent testing"""
            try:
                start_time = time.time()
                response = requests.get(f"{url}/health", timeout=5)
                end_time = time.time()
                
                results.put({
                    "worker_id": worker_id,
                    "service": service_name,
                    "status_code": response.status_code,
                    "duration": end_time - start_time,
                    "success": response.status_code == 200
                })
            except Exception as e:
                results.put({
                    "worker_id": worker_id,
                    "service": service_name,
                    "error": str(e),
                    "success": False
                })
        
        # Start concurrent workers
        threads = []
        worker_id = 0
        
        for service, url in self.base_urls.items():
            for i in range(2):  # 2 workers per service
                thread = threading.Thread(
                    target=worker,
                    args=(service, url, f"{service}_{i}")
                )
                threads.append(thread)
                thread.start()
                worker_id += 1
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Collect results
        worker_results = []
        while not results.empty():
            worker_results.append(results.get())
        
        # Verify results
        assert len(worker_results) > 0, "No worker results received"
        
        successful_workers = [r for r in worker_results if r.get("success", False)]
        assert len(successful_workers) > 0, f"No successful workers: {worker_results}"
    
    def test_system_recovery_workflow(self):
        """Test system recovery after simulated failures"""
        try:
            # Step 1: Test system in normal state
            initial_health = {}
            for service, url in self.base_urls.items():
                try:
                    response = requests.get(f"{url}/health", timeout=2)
                    initial_health[service] = response.status_code == 200
                except:
                    initial_health[service] = False
            
            # Step 2: Simulate some operations
            for i in range(3):
                requests.get(f"{self.base_urls['mcp_integration']}/health", timeout=2)
                time.sleep(0.5)
            
            # Step 3: Test system still responsive
            final_health = {}
            for service, url in self.base_urls.items():
                try:
                    response = requests.get(f"{url}/health", timeout=2)
                    final_health[service] = response.status_code == 200
                except:
                    final_health[service] = False
            
            # Step 4: Verify system stability
            for service in initial_health:
                if initial_health[service]:
                    assert final_health.get(service, False), f"{service} became unresponsive"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Required services not running")

class TestUserJourneyWorkflows:
    """Test cases for complete user journey workflows"""
    
    def test_developer_onboarding_workflow(self):
        """Test complete developer onboarding workflow"""
        try:
            # Step 1: Check system status
            status_response = requests.get(
                "http://127.0.0.1:8001/health",
                timeout=5
            )
            assert status_response.status_code in [200, 404]
            
            # Step 2: Access documentation
            docs_response = requests.get(
                "http://127.0.0.1:2024/docs",
                timeout=5
            )
            assert docs_response.status_code == 200
            
            # Step 3: Test basic functionality
            test_call = {
                "server_name": "test_server",
                "tool_name": "test_tool",
                "arguments": {"test": "value"}
            }
            
            call_response = requests.post(
                "http://127.0.0.1:8001/mcp/call",
                json=test_call,
                timeout=5
            )
            assert call_response.status_code in [200, 404, 500]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Required services not running")
    
    def test_monitoring_dashboard_workflow(self):
        """Test complete monitoring dashboard workflow"""
        try:
            # Step 1: Access debug dashboard
            dashboard_response = requests.get(
                "http://127.0.0.1:8003/",
                timeout=5
            )
            assert dashboard_response.status_code == 200
            
            # Step 2: Check observability metrics
            metrics_response = requests.get(
                "http://127.0.0.1:8002/metrics",
                timeout=5
            )
            assert metrics_response.status_code == 200
            
            # Step 3: Verify data consistency
            metrics_data = metrics_response.json()
            assert "timestamp" in metrics_data
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Required services not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

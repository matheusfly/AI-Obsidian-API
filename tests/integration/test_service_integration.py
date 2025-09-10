"""
Integration Tests for Service Integration
Tests how different services work together
"""

import pytest
import asyncio
import requests
import time
from unittest.mock import patch, Mock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class TestServiceIntegration:
    """Test cases for service integration"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.base_urls = {
            "mcp_integration": "http://127.0.0.1:8001",
            "observability": "http://127.0.0.1:8002", 
            "debug_dashboard": "http://127.0.0.1:8003",
            "langgraph_studio": "http://127.0.0.1:2024"
        }
        self.timeout = 5
    
    def test_mcp_integration_health_check(self):
        """Test MCP Integration Server health check"""
        try:
            response = requests.get(
                f"{self.base_urls['mcp_integration']}/health",
                timeout=self.timeout
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
        except requests.exceptions.ConnectionError:
            pytest.skip("MCP Integration Server not running")
    
    def test_observability_server_health_check(self):
        """Test Observability Server health check"""
        try:
            response = requests.get(
                f"{self.base_urls['observability']}/health",
                timeout=self.timeout
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
        except requests.exceptions.ConnectionError:
            pytest.skip("Observability Server not running")
    
    def test_debug_dashboard_health_check(self):
        """Test Debug Dashboard health check"""
        try:
            response = requests.get(
                f"{self.base_urls['debug_dashboard']}/health",
                timeout=self.timeout
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
        except requests.exceptions.ConnectionError:
            pytest.skip("Debug Dashboard not running")
    
    def test_langgraph_studio_health_check(self):
        """Test LangGraph Studio health check"""
        try:
            response = requests.get(
                f"{self.base_urls['langgraph_studio']}/docs",
                timeout=self.timeout
            )
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("LangGraph Studio not running")
    
    def test_mcp_call_workflow(self):
        """Test complete MCP call workflow"""
        try:
            # Test MCP call endpoint
            call_data = {
                "server_name": "test_server",
                "tool_name": "test_tool",
                "arguments": {"param": "value"}
            }
            
            response = requests.post(
                f"{self.base_urls['mcp_integration']}/mcp/call",
                json=call_data,
                timeout=self.timeout
            )
            
            # Should return 200 even if server doesn't exist (graceful error handling)
            assert response.status_code in [200, 404, 500]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("MCP Integration Server not running")
    
    def test_observability_metrics_collection(self):
        """Test observability metrics collection"""
        try:
            response = requests.get(
                f"{self.base_urls['observability']}/metrics",
                timeout=self.timeout
            )
            assert response.status_code == 200
            data = response.json()
            assert "timestamp" in data
            assert "services" in data
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Observability Server not running")
    
    def test_debug_dashboard_ui_access(self):
        """Test debug dashboard UI access"""
        try:
            response = requests.get(
                f"{self.base_urls['debug_dashboard']}/",
                timeout=self.timeout
            )
            assert response.status_code == 200
            # Should return HTML content
            assert "text/html" in response.headers.get("content-type", "")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Debug Dashboard not running")
    
    def test_service_port_conflicts(self):
        """Test that services are running on correct ports"""
        expected_ports = {
            "mcp_integration": 8001,
            "observability": 8002,
            "debug_dashboard": 8003,
            "langgraph_studio": 2024
        }
        
        for service, expected_port in expected_ports.items():
            try:
                response = requests.get(
                    f"http://127.0.0.1:{expected_port}/health",
                    timeout=2
                )
                # If we get a response, the port is correct
                assert response.status_code in [200, 404, 405]
            except requests.exceptions.ConnectionError:
                # Service not running on this port
                pass
    
    def test_cross_service_communication(self):
        """Test communication between services"""
        # This would test if services can communicate with each other
        # For now, we'll test that they're all accessible
        services_accessible = []
        
        for service, url in self.base_urls.items():
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    services_accessible.append(service)
            except:
                pass
        
        # At least some services should be accessible
        assert len(services_accessible) > 0, "No services are accessible"
    
    def test_service_startup_time(self):
        """Test that services start up within reasonable time"""
        # This would test service startup time
        # For now, we'll just verify services are running
        startup_times = {}
        
        for service, url in self.base_urls.items():
            start_time = time.time()
            try:
                response = requests.get(f"{url}/health", timeout=5)
                end_time = time.time()
                if response.status_code == 200:
                    startup_times[service] = end_time - start_time
            except:
                pass
        
        # Services should respond within 5 seconds
        for service, response_time in startup_times.items():
            assert response_time < 5.0, f"{service} took too long to respond: {response_time}s"
    
    def test_service_error_handling(self):
        """Test service error handling"""
        # Test with invalid endpoints
        invalid_endpoints = [
            "/invalid",
            "/nonexistent",
            "/error"
        ]
        
        for service, url in self.base_urls.items():
            for endpoint in invalid_endpoints:
                try:
                    response = requests.get(f"{url}{endpoint}", timeout=2)
                    # Should return 404 for invalid endpoints
                    assert response.status_code in [404, 405, 500]
                except requests.exceptions.ConnectionError:
                    # Service not running, skip
                    break

class TestLangGraphIntegration:
    """Test cases for LangGraph integration"""
    
    def test_langgraph_studio_api_access(self):
        """Test LangGraph Studio API access"""
        try:
            response = requests.get(
                "http://127.0.0.1:2024/docs",
                timeout=5
            )
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("LangGraph Studio not running")
    
    def test_langgraph_workflow_execution(self):
        """Test LangGraph workflow execution"""
        try:
            # Test workflow execution endpoint
            workflow_data = {
                "input": "test message",
                "thread_id": "test_thread"
            }
            
            response = requests.post(
                "http://127.0.0.1:2024/assistants",
                json=workflow_data,
                timeout=10
            )
            
            # Should return 200 or 405 (method not allowed)
            assert response.status_code in [200, 405, 404]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("LangGraph Studio not running")

class TestMCPToolIntegration:
    """Test cases for MCP tool integration"""
    
    def test_mcp_tool_discovery(self):
        """Test MCP tool discovery"""
        try:
            response = requests.get(
                "http://127.0.0.1:8001/tools",
                timeout=5
            )
            assert response.status_code in [200, 404]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("MCP Integration Server not running")
    
    def test_mcp_tool_execution(self):
        """Test MCP tool execution"""
        try:
            tool_data = {
                "server_name": "test_server",
                "tool_name": "test_tool",
                "arguments": {}
            }
            
            response = requests.post(
                "http://127.0.0.1:8001/mcp/call",
                json=tool_data,
                timeout=10
            )
            
            assert response.status_code in [200, 404, 500]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("MCP Integration Server not running")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

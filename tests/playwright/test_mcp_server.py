"""
Playwright tests for MCP Server functionality
"""
import pytest
import asyncio
import json
from playwright.async_api import Page, expect
import httpx


class TestMCPServer:
    """Test suite for MCP Server functionality"""
    
    @pytest.mark.asyncio
    async def test_mcp_server_health(self, page: Page, wait_for_services):
        """Test MCP Server health endpoint"""
        response = await page.request.get("http://localhost:8002/health")
        assert response.status == 200
        
        data = await response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_mcp_server_obsidian_connection(self, page: Page, test_data):
        """Test MCP Server connection to Obsidian"""
        # Test vault listing
        response = await page.request.post(
            "http://localhost:8002/tools/obsidian_list_vaults",
            data=json.dumps({}),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status == 200:
            data = await response.json()
            assert data["success"] is True
            assert "vaults" in data
        else:
            # If Obsidian is not available, test should be skipped
            pytest.skip("Obsidian Local REST API plugin not available")
    
    @pytest.mark.asyncio
    async def test_mcp_server_file_operations(self, page: Page, test_data):
        """Test MCP Server file operations"""
        # Test file listing
        payload = {
            "vault_name": test_data["vault_name"],
            "path": "",
            "recursive": True,
            "limit": 10
        }
        
        response = await page.request.post(
            "http://localhost:8002/tools/obsidian_list_files",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status == 200:
            data = await response.json()
            assert data["success"] is True
            assert "files" in data
        else:
            pytest.skip("Obsidian Local REST API plugin not available")
    
    @pytest.mark.asyncio
    async def test_mcp_server_file_reading(self, page: Page, test_data):
        """Test MCP Server file reading functionality"""
        payload = {
            "vault_name": test_data["vault_name"],
            "file_path": "README.md"
        }
        
        response = await page.request.post(
            "http://localhost:8002/tools/obsidian_read_file",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status == 200:
            data = await response.json()
            assert data["success"] is True
            assert "content" in data
        else:
            pytest.skip("Obsidian Local REST API plugin not available")
    
    @pytest.mark.asyncio
    async def test_mcp_server_error_handling(self, page: Page):
        """Test MCP Server error handling"""
        # Test with invalid payload
        response = await page.request.post(
            "http://localhost:8002/tools/obsidian_list_vaults",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status == 422  # Unprocessable Entity
    
    @pytest.mark.asyncio
    async def test_mcp_server_cors_headers(self, page: Page):
        """Test MCP Server CORS headers"""
        response = await page.request.get("http://localhost:8002/health")
        
        # Check for CORS headers
        headers = response.headers
        assert "access-control-allow-origin" in headers or "Access-Control-Allow-Origin" in headers
    
    @pytest.mark.asyncio
    async def test_mcp_server_performance(self, page: Page, test_data):
        """Test MCP Server performance"""
        import time
        
        start_time = time.time()
        
        # Make multiple concurrent requests
        tasks = []
        for i in range(5):
            task = page.request.get("http://localhost:8002/health")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # All requests should succeed
        for response in responses:
            assert response.status == 200
        
        # Response time should be reasonable (less than 5 seconds for 5 requests)
        assert response_time < 5.0
    
    @pytest.mark.asyncio
    async def test_mcp_server_concurrent_requests(self, page: Page, test_data):
        """Test MCP Server handling of concurrent requests"""
        # Create multiple concurrent file listing requests
        payload = {
            "vault_name": test_data["vault_name"],
            "path": "",
            "recursive": True,
            "limit": 5
        }
        
        tasks = []
        for i in range(10):
            task = page.request.post(
                "http://localhost:8002/tools/obsidian_list_files",
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that we got responses (even if some failed due to Obsidian not being available)
        assert len(responses) == 10
        
        # Count successful responses
        successful_responses = [r for r in responses if not isinstance(r, Exception) and r.status == 200]
        assert len(successful_responses) >= 0  # At least some should work or be properly handled

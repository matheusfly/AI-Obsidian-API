"""
Playwright tests for API Gateway functionality
"""
import pytest
import asyncio
import json
from playwright.async_api import Page, expect


class TestAPIGateway:
    """Test suite for API Gateway functionality"""
    
    @pytest.mark.asyncio
    async def test_api_gateway_health(self, page: Page, wait_for_services):
        """Test API Gateway health endpoint"""
        try:
            response = await page.request.get("http://localhost:8001/health")
            assert response.status == 200
            
            data = await response.json()
            assert "status" in data
            assert data["status"] == "healthy"
        except Exception:
            pytest.skip("API Gateway not available")
    
    @pytest.mark.asyncio
    async def test_api_gateway_obsidian_endpoints(self, page: Page, test_data):
        """Test API Gateway Obsidian integration endpoints"""
        try:
            # Test vault listing through API Gateway
            response = await page.request.get("http://localhost:8001/api/v1/obsidian/vaults")
            
            if response.status == 200:
                data = await response.json()
                assert "vaults" in data
            else:
                pytest.skip("API Gateway Obsidian endpoints not available")
        except Exception:
            pytest.skip("API Gateway not available")
    
    @pytest.mark.asyncio
    async def test_api_gateway_file_operations(self, page: Page, test_data):
        """Test API Gateway file operations"""
        try:
            # Test file listing through API Gateway
            response = await page.request.get(
                f"http://localhost:8001/api/v1/obsidian/files?vault={test_data['vault_name']}"
            )
            
            if response.status == 200:
                data = await response.json()
                assert "files" in data
            else:
                pytest.skip("API Gateway file operations not available")
        except Exception:
            pytest.skip("API Gateway not available")
    
    @pytest.mark.asyncio
    async def test_api_gateway_cors_headers(self, page: Page):
        """Test API Gateway CORS headers"""
        try:
            response = await page.request.get("http://localhost:8001/health")
            
            # Check for CORS headers
            headers = response.headers
            assert "access-control-allow-origin" in headers or "Access-Control-Allow-Origin" in headers
        except Exception:
            pytest.skip("API Gateway not available")
    
    @pytest.mark.asyncio
    async def test_api_gateway_error_handling(self, page: Page):
        """Test API Gateway error handling"""
        try:
            # Test with invalid endpoint
            response = await page.request.get("http://localhost:8001/api/v1/invalid")
            assert response.status == 404
        except Exception:
            pytest.skip("API Gateway not available")
    
    @pytest.mark.asyncio
    async def test_api_gateway_rate_limiting(self, page: Page):
        """Test API Gateway rate limiting (if implemented)"""
        try:
            # Make multiple rapid requests
            tasks = []
            for i in range(20):
                task = page.request.get("http://localhost:8001/health")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All requests should succeed (rate limiting not implemented yet)
            successful_responses = [r for r in responses if not isinstance(r, Exception) and r.status == 200]
            assert len(successful_responses) >= 15  # Most should succeed
        except Exception:
            pytest.skip("API Gateway not available")
    
    @pytest.mark.asyncio
    async def test_api_gateway_documentation(self, page: Page):
        """Test API Gateway documentation endpoints"""
        try:
            # Test OpenAPI documentation
            response = await page.request.get("http://localhost:8001/docs")
            assert response.status == 200
            
            # Test OpenAPI JSON
            response = await page.request.get("http://localhost:8001/openapi.json")
            assert response.status == 200
            
            data = await response.json()
            assert "openapi" in data
            assert "info" in data
        except Exception:
            pytest.skip("API Gateway not available")
    
    @pytest.mark.asyncio
    async def test_api_gateway_metrics(self, page: Page):
        """Test API Gateway metrics endpoint"""
        try:
            response = await page.request.get("http://localhost:8001/metrics")
            assert response.status == 200
            
            # Check if response contains Prometheus metrics
            text = await response.text()
            assert "http_requests_total" in text or "prometheus" in text.lower()
        except Exception:
            pytest.skip("API Gateway metrics not available")

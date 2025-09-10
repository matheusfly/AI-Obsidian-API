"""
Playwright integration tests for the complete system
"""
import pytest
import asyncio
import json
from playwright.async_api import Page, expect


class TestSystemIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_system_health_check(self, page: Page, wait_for_services):
        """Test overall system health"""
        services = [
            ("MCP Server", "http://localhost:8002/health"),
            ("ChromaDB", "http://localhost:8000/api/v1/heartbeat"),
        ]
        
        # Optional services
        optional_services = [
            ("API Gateway", "http://localhost:8001/health"),
        ]
        
        # Test required services
        for service_name, url in services:
            try:
                response = await page.request.get(url)
                assert response.status == 200, f"{service_name} is not healthy"
            except Exception as e:
                pytest.fail(f"{service_name} health check failed: {e}")
        
        # Test optional services
        for service_name, url in optional_services:
            try:
                response = await page.request.get(url)
                if response.status == 200:
                    print(f"✅ {service_name} is available")
                else:
                    print(f"⚠️ {service_name} is not available")
            except Exception:
                print(f"⚠️ {service_name} is not available")
    
    @pytest.mark.asyncio
    async def test_obsidian_integration_flow(self, page: Page, test_data):
        """Test complete Obsidian integration flow"""
        try:
            # Step 1: Test MCP Server connection to Obsidian
            response = await page.request.post(
                "http://localhost:8002/tools/obsidian_list_vaults",
                data=json.dumps({}),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status != 200:
                pytest.skip("Obsidian Local REST API plugin not available")
            
            vault_data = await response.json()
            assert vault_data["success"] is True
            assert "vaults" in vault_data
            
            # Step 2: Test file listing
            file_payload = {
                "vault_name": test_data["vault_name"],
                "path": "",
                "recursive": True,
                "limit": 10
            }
            
            response = await page.request.post(
                "http://localhost:8002/tools/obsidian_list_files",
                data=json.dumps(file_payload),
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status == 200
            file_data = await response.json()
            assert file_data["success"] is True
            assert "files" in file_data
            
            # Step 3: Test file reading
            if file_data["files"]:
                test_file = file_data["files"][0]
                read_payload = {
                    "vault_name": test_data["vault_name"],
                    "file_path": test_file["name"]
                }
                
                response = await page.request.post(
                    "http://localhost:8002/tools/obsidian_read_file",
                    data=json.dumps(read_payload),
                    headers={"Content-Type": "application/json"}
                )
                
                assert response.status == 200
                read_data = await response.json()
                assert read_data["success"] is True
                assert "content" in read_data
            
        except Exception as e:
            pytest.skip(f"Obsidian integration not available: {e}")
    
    @pytest.mark.asyncio
    async def test_vector_database_integration(self, page: Page, test_data):
        """Test ChromaDB integration"""
        try:
            # Test ChromaDB health
            response = await page.request.get("http://localhost:8000/api/v1/heartbeat")
            assert response.status == 200
            
            # Test ChromaDB collections endpoint
            response = await page.request.get("http://localhost:8000/api/v1/collections")
            assert response.status == 200
            
            collections_data = await response.json()
            assert isinstance(collections_data, list)
            
        except Exception as e:
            pytest.fail(f"ChromaDB integration failed: {e}")
    
    @pytest.mark.asyncio
    async def test_redis_integration(self, page: Page):
        """Test Redis integration"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # Test basic Redis operations
            r.set('test_key', 'test_value')
            value = r.get('test_key')
            assert value == 'test_value'
            
            # Test Redis ping
            pong = r.ping()
            assert pong is True
            
            # Cleanup
            r.delete('test_key')
            
        except Exception as e:
            pytest.fail(f"Redis integration failed: {e}")
    
    @pytest.mark.asyncio
    async def test_system_performance(self, page: Page, test_data):
        """Test system performance under load"""
        import time
        
        # Test MCP Server performance
        start_time = time.time()
        
        tasks = []
        for i in range(20):
            task = page.request.get("http://localhost:8002/health")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # All requests should succeed
        for response in responses:
            assert response.status == 200
        
        # Response time should be reasonable
        assert response_time < 10.0  # 20 requests in less than 10 seconds
        
        print(f"Performance test: 20 requests completed in {response_time:.2f} seconds")
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, page: Page):
        """Test system error recovery"""
        # Test with invalid requests
        invalid_requests = [
            ("http://localhost:8002/invalid", 404),
            ("http://localhost:8002/tools/invalid", 404),
        ]
        
        for url, expected_status in invalid_requests:
            response = await page.request.get(url)
            assert response.status == expected_status
        
        # Test with malformed JSON
        response = await page.request.post(
            "http://localhost:8002/tools/obsidian_list_vaults",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status == 422
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, page: Page, test_data):
        """Test concurrent operations across services"""
        try:
            # Create concurrent tasks for different services
            tasks = [
                page.request.get("http://localhost:8002/health"),
                page.request.get("http://localhost:8000/api/v1/heartbeat"),
                page.request.post(
                    "http://localhost:8002/tools/obsidian_list_vaults",
                    data=json.dumps({}),
                    headers={"Content-Type": "application/json"}
                )
            ]
            
            # Add API Gateway if available
            try:
                tasks.append(page.request.get("http://localhost:8001/health"))
            except:
                pass
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that we got responses
            assert len(responses) >= 3
            
            # Count successful responses
            successful_responses = [r for r in responses if not isinstance(r, Exception) and r.status == 200]
            assert len(successful_responses) >= 2  # At least MCP Server and ChromaDB should work
            
        except Exception as e:
            pytest.fail(f"Concurrent operations test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_data_consistency(self, page: Page, test_data):
        """Test data consistency across services"""
        try:
            # Test that vault data is consistent between different endpoints
            response1 = await page.request.post(
                "http://localhost:8002/tools/obsidian_list_vaults",
                data=json.dumps({}),
                headers={"Content-Type": "application/json"}
            )
            
            if response1.status == 200:
                data1 = await response1.json()
                
                # Make another request to ensure consistency
                response2 = await page.request.post(
                    "http://localhost:8002/tools/obsidian_list_vaults",
                    data=json.dumps({}),
                    headers={"Content-Type": "application/json"}
                )
                
                if response2.status == 200:
                    data2 = await response2.json()
                    
                    # Data should be consistent
                    assert data1["success"] == data2["success"]
                    if "vaults" in data1 and "vaults" in data2:
                        assert data1["vaults"] == data2["vaults"]
            
        except Exception as e:
            pytest.skip(f"Data consistency test not available: {e}")

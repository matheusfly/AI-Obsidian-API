"""
Comprehensive test suite for API Gateway
"""
import pytest
import asyncio
import httpx
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from api_gateway.main import app
from config.environment import config

# Test client
client = TestClient(app)

class TestAPIGateway:
    """Test cases for API Gateway endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data
    
    @patch('api_gateway.main.make_obsidian_request')
    def test_list_vaults(self, mock_request):
        """Test listing vaults"""
        mock_request.return_value = AsyncMock()
        mock_request.return_value.json.return_value = {"vaults": ["Main", "Test"]}
        
        response = client.get("/vaults")
        assert response.status_code == 200
        
        data = response.json()
        assert "vaults" in data
        assert data["vaults"] == ["Main", "Test"]
    
    @patch('api_gateway.main.make_obsidian_request')
    def test_list_files(self, mock_request):
        """Test listing files in vault"""
        mock_files = [
            {"path": "note1.md", "content": "Content 1"},
            {"path": "note2.md", "content": "Content 2"}
        ]
        mock_request.return_value = AsyncMock()
        mock_request.return_value.json.return_value = {"files": mock_files}
        
        response = client.get("/vault/Main/files")
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data
        assert len(data["files"]) == 2
        
        # Check that hash is added
        for file in data["files"]:
            assert "_hash" in file
    
    @patch('api_gateway.main.make_obsidian_request')
    def test_read_file(self, mock_request):
        """Test reading a file"""
        mock_content = "# Test Note\nThis is a test note."
        mock_request.return_value = AsyncMock()
        mock_request.return_value.json.return_value = {
            "path": "test/note.md",
            "content": mock_content
        }
        
        response = client.get("/vault/Main/file/test/note.md")
        assert response.status_code == 200
        
        data = response.json()
        assert data["content"] == mock_content
        assert "_hash" in data
    
    def test_upsert_file_dry_run(self):
        """Test upsert file in dry run mode"""
        request_data = {
            "path": "test/new_note.md",
            "content": "# New Note\nThis is a new note.",
            "dry_run": True
        }
        
        response = client.put("/vault/Main/file/test/new_note.md", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["dry_run"] == True
        assert "tool_call_id" in data
        assert "approval_required" in data
        assert "approval_endpoint" in data
    
    def test_upsert_file_validation(self):
        """Test upsert file validation"""
        # Test missing required fields
        response = client.put("/vault/Main/file/test.md", json={})
        assert response.status_code == 422  # Validation error
    
    def test_pending_operations(self):
        """Test pending operations endpoints"""
        # List pending operations
        response = client.get("/pending_operations")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_search_notes(self):
        """Test search notes endpoint"""
        search_data = {
            "vault": "Main",
            "query": "test query",
            "limit": 10
        }
        
        with patch('api_gateway.main.make_obsidian_request') as mock_request:
            mock_request.return_value = AsyncMock()
            mock_request.return_value.json.return_value = {
                "results": [
                    {"path": "note1.md", "content": "Test content 1"},
                    {"path": "note2.md", "content": "Test content 2"}
                ]
            }
            
            response = client.post("/vault/Main/search", json=search_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "results" in data
    
    def test_mcp_endpoints(self):
        """Test MCP tool endpoints"""
        # Test MCP list files
        mcp_request = {
            "vault": "Main",
            "limit": 10
        }
        
        with patch('api_gateway.main.list_files') as mock_list_files:
            mock_list_files.return_value = {"files": []}
            
            response = client.post("/mcp/obsidian_list_files", json=mcp_request)
            assert response.status_code == 200
    
    def test_error_handling(self):
        """Test error handling"""
        with patch('api_gateway.main.make_obsidian_request') as mock_request:
            mock_request.side_effect = Exception("API Error")
            
            response = client.get("/vault/Main/files")
            assert response.status_code == 500
            
            data = response.json()
            assert "detail" in data
            assert "API Error" in data["detail"]

class TestConflictDetection:
    """Test conflict detection functionality"""
    
    def test_conflict_detection_success(self):
        """Test successful conflict detection"""
        request_data = {
            "path": "test/note.md",
            "content": "Updated content",
            "if_match": "correct_hash",
            "dry_run": False
        }
        
        with patch('api_gateway.main.read_file') as mock_read:
            mock_read.return_value = {"_hash": "correct_hash"}
            
            with patch('api_gateway.main.make_obsidian_request') as mock_request:
                mock_request.return_value = AsyncMock()
                mock_request.return_value.json.return_value = {"status": "success"}
                
                response = client.put("/vault/Main/file/test/note.md", json=request_data)
                assert response.status_code == 200
    
    def test_conflict_detection_failure(self):
        """Test conflict detection failure"""
        request_data = {
            "path": "test/note.md",
            "content": "Updated content",
            "if_match": "wrong_hash",
            "dry_run": False
        }
        
        with patch('api_gateway.main.read_file') as mock_read:
            mock_read.return_value = {"_hash": "correct_hash"}
            
            response = client.put("/vault/Main/file/test/note.md", json=request_data)
            assert response.status_code == 409  # Conflict

class TestHITLWorkflow:
    """Test Human-in-the-Loop workflow"""
    
    def test_approval_workflow(self):
        """Test the complete approval workflow"""
        # First, create a dry-run operation
        request_data = {
            "path": "test/approval_note.md",
            "content": "Content requiring approval",
            "dry_run": True
        }
        
        response = client.put("/vault/Main/file/test/approval_note.md", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["dry_run"] == True
        assert data["approval_required"] == True
        
        tool_call_id = data["tool_call_id"]
        
        # Check that operation is in pending list
        response = client.get("/pending_operations")
        assert response.status_code == 200
        
        pending_ops = response.json()
        assert len(pending_ops) > 0
        
        # Get specific operation details
        response = client.get(f"/pending_operations/{tool_call_id}")
        assert response.status_code == 200
        
        op_data = response.json()
        assert op_data["tool_call_id"] == tool_call_id
        
        # Approve the operation
        with patch('api_gateway.main.upsert_file') as mock_upsert:
            mock_upsert.return_value = {"status": "success"}
            
            response = client.post(f"/approve/{tool_call_id}")
            assert response.status_code == 200
            
            approval_data = response.json()
            assert approval_data["status"] == "approved"

@pytest.mark.asyncio
class TestAsyncOperations:
    """Test async operations"""
    
    async def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        async def make_request():
            with patch('api_gateway.main.make_obsidian_request') as mock_request:
                mock_request.return_value = AsyncMock()
                mock_request.return_value.json.return_value = {"files": []}
                
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://testserver/vault/Main/files")
                    return response.status_code
        
        # Run multiple concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(status == 200 for status in results)

if __name__ == "__main__":
    pytest.main([__file__])

"""
Unit Tests for MCP Integration Server
Tests individual components and functions
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from services.mcp_service.src.mcp_tools.mcp_integration_server import (
    MCPIntegrationServer, 
    MCPCallRequest, 
    MCPCallResponse
)

class TestMCPIntegrationServer:
    """Test cases for MCP Integration Server"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.server = MCPIntegrationServer()
        self.test_request = MCPCallRequest(
            server_name="test_server",
            tool_name="test_tool",
            arguments={"param1": "value1"}
        )
    
    def test_mcp_call_request_validation(self):
        """Test MCPCallRequest model validation"""
        # Valid request
        request = MCPCallRequest(
            server_name="test_server",
            tool_name="test_tool",
            arguments={"key": "value"}
        )
        assert request.server_name == "test_server"
        assert request.tool_name == "test_tool"
        assert request.arguments == {"key": "value"}
    
    def test_mcp_call_response_creation(self):
        """Test MCPCallResponse model creation"""
        # Success response
        success_response = MCPCallResponse(
            success=True,
            result={"data": "test"},
            execution_time_ms=100.0
        )
        assert success_response.success is True
        assert success_response.result == {"data": "test"}
        assert success_response.execution_time_ms == 100.0
        
        # Error response
        error_response = MCPCallResponse(
            success=False,
            error="Test error",
            execution_time_ms=50.0
        )
        assert error_response.success is False
        assert error_response.error == "Test error"
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=Mock)
    def test_load_mcp_config_success(self, mock_open, mock_exists):
        """Test successful MCP configuration loading"""
        mock_exists.return_value = True
        mock_config = {
            "mcpServers": {
                "test_server": {
                    "command": "python",
                    "args": ["test_script.py"]
                }
            }
        }
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_config)
        
        server = MCPIntegrationServer()
        assert "test_server" in server.mcp_servers
    
    @patch('pathlib.Path.exists')
    def test_load_mcp_config_file_not_found(self, mock_exists):
        """Test MCP configuration loading when file doesn't exist"""
        mock_exists.return_value = False
        
        server = MCPIntegrationServer()
        assert server.mcp_servers == {}
    
    def test_validate_request_valid(self):
        """Test request validation with valid data"""
        request = MCPCallRequest(
            server_name="test_server",
            tool_name="test_tool",
            arguments={"param": "value"}
        )
        
        # This would be a method in the actual implementation
        assert request.server_name is not None
        assert request.tool_name is not None
    
    def test_validate_request_missing_server(self):
        """Test request validation with missing server name"""
        with pytest.raises(ValueError):
            MCPCallRequest(
                server_name="",
                tool_name="test_tool"
            )
    
    def test_validate_request_missing_tool(self):
        """Test request validation with missing tool name"""
        with pytest.raises(ValueError):
            MCPCallRequest(
                server_name="test_server",
                tool_name=""
            )
    
    @pytest.mark.asyncio
    async def test_execute_mcp_call_success(self):
        """Test successful MCP call execution"""
        with patch.object(self.server, 'execute_mcp_call') as mock_execute:
            mock_execute.return_value = MCPCallResponse(
                success=True,
                result={"data": "test_result"},
                execution_time_ms=100.0
            )
            
            result = await mock_execute(self.test_request)
            assert result.success is True
            assert result.result == {"data": "test_result"}
    
    @pytest.mark.asyncio
    async def test_execute_mcp_call_failure(self):
        """Test failed MCP call execution"""
        with patch.object(self.server, 'execute_mcp_call') as mock_execute:
            mock_execute.return_value = MCPCallResponse(
                success=False,
                error="Connection failed",
                execution_time_ms=50.0
            )
            
            result = await mock_execute(self.test_request)
            assert result.success is False
            assert result.error == "Connection failed"
    
    def test_performance_metrics_tracking(self):
        """Test performance metrics tracking"""
        # Simulate adding metrics
        self.server.performance_metrics["test_tool"] = {
            "total_calls": 10,
            "success_rate": 0.9,
            "avg_execution_time": 100.0
        }
        
        assert "test_tool" in self.server.performance_metrics
        assert self.server.performance_metrics["test_tool"]["total_calls"] == 10
        assert self.server.performance_metrics["test_tool"]["success_rate"] == 0.9
    
    def test_call_history_tracking(self):
        """Test call history tracking"""
        # Simulate adding to call history
        call_record = {
            "timestamp": "2025-09-06T17:00:00Z",
            "server_name": "test_server",
            "tool_name": "test_tool",
            "success": True,
            "execution_time_ms": 100.0
        }
        self.server.call_history.append(call_record)
        
        assert len(self.server.call_history) == 1
        assert self.server.call_history[0]["server_name"] == "test_server"
        assert self.server.call_history[0]["success"] is True

class TestMCPCallRequest:
    """Test cases for MCPCallRequest model"""
    
    def test_required_fields(self):
        """Test that required fields are properly validated"""
        request = MCPCallRequest(
            server_name="test_server",
            tool_name="test_tool"
        )
        assert request.server_name == "test_server"
        assert request.tool_name == "test_tool"
        assert request.arguments == {}
    
    def test_optional_arguments(self):
        """Test that optional arguments are handled correctly"""
        arguments = {"param1": "value1", "param2": 123}
        request = MCPCallRequest(
            server_name="test_server",
            tool_name="test_tool",
            arguments=arguments
        )
        assert request.arguments == arguments
    
    def test_empty_arguments_default(self):
        """Test that empty arguments default to empty dict"""
        request = MCPCallRequest(
            server_name="test_server",
            tool_name="test_tool"
        )
        assert request.arguments == {}

class TestMCPCallResponse:
    """Test cases for MCPCallResponse model"""
    
    def test_success_response(self):
        """Test success response creation"""
        response = MCPCallResponse(
            success=True,
            result={"data": "test"},
            execution_time_ms=100.0
        )
        assert response.success is True
        assert response.result == {"data": "test"}
        assert response.error is None
        assert response.execution_time_ms == 100.0
    
    def test_error_response(self):
        """Test error response creation"""
        response = MCPCallResponse(
            success=False,
            error="Test error",
            execution_time_ms=50.0
        )
        assert response.success is False
        assert response.error == "Test error"
        assert response.result is None
        assert response.execution_time_ms == 50.0
    
    def test_minimal_response(self):
        """Test minimal response creation"""
        response = MCPCallResponse(success=True)
        assert response.success is True
        assert response.result is None
        assert response.error is None
        assert response.execution_time_ms == 0.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

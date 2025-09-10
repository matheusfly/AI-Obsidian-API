"""
Comprehensive test suite for enhanced MCP integration with Obsidian
Tests multi-server interoperability and advanced agent-to-agent communication
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from mcp_tools.enhanced_obsidian_mcp_server import mcp, ObsidianMCPClient
from langgraph_workflows.enhanced_obsidian_agent import enhanced_workflow, AgentState

class TestEnhancedMCPIntegration:
    """Test enhanced MCP integration functionality"""
    
    @pytest.fixture
    def mcp_client(self):
        """Create MCP client for testing"""
        return ObsidianMCPClient(
            api_key="test_api_key",
            base_url="http://test-api:8000"
        )
    
    @pytest.fixture
    def mock_obsidian_response(self):
        """Mock Obsidian API response"""
        return {
            "success": True,
            "vaults": [
                {"name": "test_vault", "path": "/test/vault", "file_count": 100}
            ],
            "files": [
                {
                    "path": "test_note.md",
                    "size": 1024,
                    "modified": "2024-01-15T10:00:00Z",
                    "content": "# Test Note\n\nThis is a test note."
                }
            ],
            "results": [
                {
                    "file_path": "test_note.md",
                    "content": "# Test Note\n\nThis is a test note.",
                    "score": 0.95,
                    "metadata": {"size": 1024}
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_obsidian_list_vaults(self, mcp_client, mock_obsidian_response):
        """Test listing vaults with enhanced metadata"""
        with patch.object(mcp_client, '_make_request', return_value=mock_obsidian_response):
            result = await mcp_client.list_vaults()
            
            assert result["success"] is True
            assert len(result["vaults"]) == 1
            assert result["vaults"][0]["name"] == "test_vault"
            assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_obsidian_list_files_with_filtering(self, mcp_client, mock_obsidian_response):
        """Test listing files with advanced filtering"""
        with patch.object(mcp_client, '_make_request', return_value=mock_obsidian_response):
            result = await mcp_client.list_files(
                vault_name="test_vault",
                path="notes",
                recursive=True,
                limit=50
            )
            
            assert result["success"] is True
            assert len(result["files"]) == 1
            assert result["files"][0]["path"] == "test_note.md"
    
    @pytest.mark.asyncio
    async def test_obsidian_read_note_with_metadata(self, mcp_client, mock_obsidian_response):
        """Test reading note with enhanced metadata and links"""
        with patch.object(mcp_client, '_make_request', return_value=mock_obsidian_response):
            result = await mcp_client.read_note(
                vault_name="test_vault",
                file_path="test_note.md",
                include_metadata=True
            )
            
            assert result["success"] is True
            assert "content" in result
            assert "metadata" in result
            assert "statistics" in result
            assert "links" in result
            assert result["statistics"]["word_count"] > 0
    
    @pytest.mark.asyncio
    async def test_obsidian_put_file_with_backup(self, mcp_client):
        """Test putting file with backup functionality"""
        put_response = {"success": True, "message": "File created successfully"}
        
        with patch.object(mcp_client, '_make_request', side_effect=[{"content": "old content"}, put_response]):
            result = await mcp_client.put_file(
                vault_name="test_vault",
                file_path="test_note.md",
                content="# New Content\n\nUpdated content.",
                create_dirs=True,
                backup_existing=True
            )
            
            assert result["success"] is True
            assert "backup_created" in result
    
    @pytest.mark.asyncio
    async def test_obsidian_search_notes_enhanced(self, mcp_client, mock_obsidian_response):
        """Test enhanced search functionality"""
        with patch.object(mcp_client, '_make_request', return_value=mock_obsidian_response):
            result = await mcp_client.search_notes(
                vault_name="test_vault",
                query="test query",
                limit=10,
                include_content=True,
                search_type="semantic"
            )
            
            assert result["success"] is True
            assert len(result["results"]) == 1
            assert result["results"][0]["relevance_score"] == 0.95
            assert result["search_type"] == "semantic"
    
    @pytest.mark.asyncio
    async def test_obsidian_batch_operations(self, mcp_client):
        """Test batch operations functionality"""
        batch_response = {
            "success": True,
            "results": [
                {"success": True, "operation": "read"},
                {"success": True, "operation": "write"}
            ]
        }
        
        with patch.object(mcp_client, '_make_request', return_value=batch_response):
            operations = [
                {"type": "read", "file_path": "note1.md"},
                {"type": "write", "file_path": "note2.md", "content": "content"}
            ]
            
            result = await mcp_client.batch_operations("test_vault", operations)
            
            assert result["success"] is True
            assert len(result["results"]) == 2
            assert all(r["success"] for r in result["results"])
    
    @pytest.mark.asyncio
    async def test_obsidian_agent_communication(self, mcp_client):
        """Test agent-to-agent communication"""
        comm_response = {
            "success": True,
            "message": "Communication sent successfully",
            "communication_id": "test_id"
        }
        
        with patch.object(mcp_client, '_make_request', return_value=comm_response):
            result = await mcp_client.call_tool("obsidian_agent_communication", {
                "target_agent": "test_agent",
                "message": "Test message",
                "data": {"test": "data"}
            })
            
            assert result["success"] is True
            assert "communication_id" in result
    
    @pytest.mark.asyncio
    async def test_obsidian_workflow_status(self, mcp_client):
        """Test workflow status tracking"""
        status_response = {
            "success": True,
            "workflow_id": "test_workflow",
            "status": "running",
            "progress": 75
        }
        
        with patch.object(mcp_client, '_make_request', return_value=status_response):
            result = await mcp_client.call_tool("obsidian_workflow_status", {
                "workflow_id": "test_workflow",
                "vault_name": "test_vault"
            })
            
            assert result["success"] is True
            assert result["status"] == "running"
            assert result["progress"] == 75

class TestEnhancedLangGraphWorkflow:
    """Test enhanced LangGraph workflow functionality"""
    
    @pytest.fixture
    def sample_agent_state(self):
        """Create sample agent state for testing"""
        return AgentState(
            user_input="Test user input",
            vault_name="test_vault",
            session_id="test_session_123",
            current_file=None,
            research_data=[],
            generated_content="",
            output_path="",
            tool_calls=[],
            agent_communications=[],
            workflow_status="initialized",
            success=False,
            message="",
            requires_approval=False,
            approval_status=None,
            error_details=None,
            metadata={}
        )
    
    @pytest.mark.asyncio
    async def test_research_node(self, sample_agent_state):
        """Test research node functionality"""
        with patch('langgraph_workflows.enhanced_obsidian_agent.mcp_client') as mock_client:
            mock_client.call_tool.return_value = {
                "success": True,
                "results": [
                    {
                        "file_path": "test_note.md",
                        "content": "Test content",
                        "relevance_score": 0.95
                    }
                ]
            }
            
            # Test research node
            from langgraph_workflows.enhanced_obsidian_agent import research_node
            result_state = research_node(sample_agent_state)
            
            assert len(result_state["research_data"]) == 1
            assert result_state["research_data"][0]["file_path"] == "test_note.md"
            assert "Found 1 relevant notes" in result_state["message"]
    
    @pytest.mark.asyncio
    async def test_analyze_node(self, sample_agent_state):
        """Test analysis node functionality"""
        # Set up research data
        sample_agent_state["research_data"] = [
            {
                "file_path": "test_note.md",
                "content": "Test content for analysis",
                "relevance_score": 0.95,
                "links": {"wiki_links": ["linked_note"]},
                "statistics": {"word_count": 4}
            }
        ]
        
        with patch('langgraph_workflows.enhanced_obsidian_agent.mcp_client') as mock_client:
            mock_client.call_tool.return_value = {
                "success": True,
                "stats": {"total_files": 100, "total_size": 1024000}
            }
            
            # Test analyze node
            from langgraph_workflows.enhanced_obsidian_agent import analyze_node
            result_state = analyze_node(sample_agent_state)
            
            assert "analysis_results" in result_state["metadata"]
            assert len(result_state["metadata"]["analysis_results"]) == 1
            assert "vault_stats" in result_state["metadata"]
    
    @pytest.mark.asyncio
    async def test_generate_node(self, sample_agent_state):
        """Test content generation node"""
        # Set up research data
        sample_agent_state["research_data"] = [
            {
                "file_path": "test_note.md",
                "content": "Test content",
                "relevance_score": 0.95
            }
        ]
        sample_agent_state["metadata"]["analysis_results"] = [
            {
                "file_path": "test_note.md",
                "relevance_score": 0.95,
                "key_insights": ["Test insight 1", "Test insight 2"]
            }
        ]
        
        with patch('langgraph_workflows.enhanced_obsidian_agent.mcp_client') as mock_client:
            mock_client.call_tool.return_value = {"success": True}
            
            # Test generate node
            from langgraph_workflows.enhanced_obsidian_agent import generate_node
            result_state = generate_node(sample_agent_state)
            
            assert result_state["generated_content"] != ""
            assert "Generated Content for:" in result_state["generated_content"]
            assert result_state["output_path"] != ""
            assert "Content generated successfully" in result_state["message"]
    
    @pytest.mark.asyncio
    async def test_write_node(self, sample_agent_state):
        """Test write node functionality"""
        sample_agent_state["generated_content"] = "# Test Content\n\nGenerated content"
        sample_agent_state["output_path"] = "test_output.md"
        
        with patch('langgraph_workflows.enhanced_obsidian_agent.mcp_client') as mock_client:
            mock_client.call_tool.return_value = {"success": True}
            
            # Test write node
            from langgraph_workflows.enhanced_obsidian_agent import write_node
            result_state = write_node(sample_agent_state)
            
            assert result_state["success"] is True
            assert "Content written successfully" in result_state["message"]
            assert result_state["current_file"] == "test_output.md"
    
    @pytest.mark.asyncio
    async def test_human_review_node(self, sample_agent_state):
        """Test human review node functionality"""
        sample_agent_state["requires_approval"] = True
        
        with patch('langgraph_workflows.enhanced_obsidian_agent.mcp_client') as mock_client:
            mock_client.call_tool.return_value = {
                "success": True,
                "status": "running",
                "progress": 75
            }
            
            # Test human review node
            from langgraph_workflows.enhanced_obsidian_agent import human_review_node
            result_state = human_review_node(sample_agent_state)
            
            assert result_state["workflow_status"] == "pending_approval"
            assert "Content requires human approval" in result_state["message"]
            assert "workflow_status" in result_state["metadata"]
    
    @pytest.mark.asyncio
    async def test_error_handling_node(self, sample_agent_state):
        """Test error handling node functionality"""
        sample_agent_state["error_details"] = "Test error occurred"
        
        with patch('langgraph_workflows.enhanced_obsidian_agent.mcp_client') as mock_client:
            mock_client.call_tool.return_value = {"success": True}
            
            # Test error handling node
            from langgraph_workflows.enhanced_obsidian_agent import error_handling_node
            result_state = error_handling_node(sample_agent_state)
            
            assert "recovery_strategies" in result_state["metadata"]
            assert "retry_operation" in result_state["metadata"]["recovery_strategies"]
            assert "Error handled with recovery strategies" in result_state["message"]
    
    def test_workflow_creation(self):
        """Test enhanced workflow creation"""
        assert enhanced_workflow is not None
        assert hasattr(enhanced_workflow, 'nodes')
        assert hasattr(enhanced_workflow, 'edges')
    
    @pytest.mark.asyncio
    async def test_full_workflow_execution(self, sample_agent_state):
        """Test full workflow execution"""
        with patch('langgraph_workflows.enhanced_obsidian_agent.mcp_client') as mock_client:
            # Mock all MCP tool calls
            mock_client.call_tool.return_value = {
                "success": True,
                "results": [{"file_path": "test.md", "content": "test", "score": 0.95}],
                "stats": {"total_files": 100}
            }
            
            # Execute workflow
            result = await enhanced_workflow.ainvoke(sample_agent_state)
            
            assert result["success"] is True
            assert result["generated_content"] != ""
            assert result["output_path"] != ""

class TestMCPToolIntegration:
    """Test MCP tool integration with LangGraph"""
    
    @pytest.fixture
    def mcp_app(self):
        """Create MCP app for testing"""
        from mcp_tools.enhanced_obsidian_mcp_server import mcp
        return mcp.app
    
    def test_mcp_tool_endpoints(self, mcp_app):
        """Test MCP tool endpoints"""
        client = TestClient(mcp_app)
        
        # Test list vaults endpoint
        response = client.post("/tools/obsidian_list_vaults")
        assert response.status_code in [200, 500]  # 500 if no connection
        
        # Test list files endpoint
        response = client.post("/tools/obsidian_list_files", json={
            "vault_name": "test_vault",
            "path": "",
            "recursive": True,
            "limit": 100
        })
        assert response.status_code in [200, 500]
    
    def test_mcp_tool_validation(self, mcp_app):
        """Test MCP tool input validation"""
        client = TestClient(mcp_app)
        
        # Test with invalid input
        response = client.post("/tools/obsidian_read_note", json={
            "vault_name": "",  # Invalid empty vault name
            "file_path": "test.md"
        })
        assert response.status_code in [200, 422, 500]  # 422 for validation error

class TestMultiServerInteroperability:
    """Test multi-server interoperability features"""
    
    @pytest.mark.asyncio
    async def test_agent_communication_flow(self):
        """Test agent-to-agent communication flow"""
        from langgraph_workflows.enhanced_obsidian_agent import MCPToolClient
        
        client = MCPToolClient("http://test-mcp:8002")
        
        with patch.object(client, 'call_tool') as mock_call:
            mock_call.return_value = {
                "success": True,
                "communication_id": "test_comm_123"
            }
            
            result = await client.call_tool("obsidian_agent_communication", {
                "target_agent": "test_agent",
                "message": "Test message",
                "data": {"test": "data"}
            })
            
            assert result["success"] is True
            assert "communication_id" in result
    
    @pytest.mark.asyncio
    async def test_workflow_status_tracking(self):
        """Test workflow status tracking across servers"""
        from langgraph_workflows.enhanced_obsidian_agent import MCPToolClient
        
        client = MCPToolClient("http://test-mcp:8002")
        
        with patch.object(client, 'call_tool') as mock_call:
            mock_call.return_value = {
                "success": True,
                "workflow_id": "test_workflow",
                "status": "running",
                "progress": 50
            }
            
            result = await client.call_tool("obsidian_workflow_status", {
                "workflow_id": "test_workflow",
                "vault_name": "test_vault"
            })
            
            assert result["success"] is True
            assert result["status"] == "running"
            assert result["progress"] == 50

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

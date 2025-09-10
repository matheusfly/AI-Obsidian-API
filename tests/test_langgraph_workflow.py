"""
Test suite for LangGraph workflow
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

from langgraph_workflows.obsidian_agent import (
    create_obsidian_agent_workflow,
    run_agent,
    AgentState
)

class TestLangGraphWorkflow:
    """Test cases for LangGraph workflow"""
    
    def test_workflow_creation(self):
        """Test workflow creation and compilation"""
        workflow = create_obsidian_agent_workflow()
        assert workflow is not None
        
        # Test that workflow has required nodes
        nodes = workflow.nodes
        expected_nodes = [
            "classify_task",
            "execute_read_workflow", 
            "execute_write_workflow",
            "execute_search_workflow",
            "execute_organize_workflow",
            "execute_analyze_workflow",
            "check_pending_approvals",
            "error_handler"
        ]
        
        for node in expected_nodes:
            assert node in nodes
    
    @pytest.mark.asyncio
    async def test_classify_task(self):
        """Test task classification"""
        from langgraph_workflows.obsidian_agent import classify_task
        
        # Test read task
        state = {
            "messages": [{"content": "List all files in my vault"}],
            "session_id": "test_session"
        }
        
        result = await classify_task(state)
        assert result["current_task"] == "READ"
        assert result["next_action"] == "execute_read_workflow"
        
        # Test write task
        state = {
            "messages": [{"content": "Create a new note about AI"}],
            "session_id": "test_session"
        }
        
        result = await classify_task(state)
        assert result["current_task"] == "WRITE"
        assert result["next_action"] == "execute_write_workflow"
    
    @pytest.mark.asyncio
    async def test_execute_read_workflow(self):
        """Test read workflow execution"""
        from langgraph_workflows.obsidian_agent import execute_read_workflow
        
        with patch('langgraph_workflows.obsidian_agent.obsidian_list_files') as mock_list:
            mock_list.return_value = {
                "success": True,
                "data": {"files": [{"path": "note1.md", "content": "Content 1"}]}
            }
            
            state = {
                "messages": [{"content": "List all files"}],
                "session_id": "test_session"
            }
            
            result = await execute_read_workflow(state)
            
            assert "messages" in result
            assert "vault_data" in result
            assert result["next_action"] == "check_pending_approvals"
    
    @pytest.mark.asyncio
    async def test_execute_write_workflow(self):
        """Test write workflow execution"""
        from langgraph_workflows.obsidian_agent import execute_write_workflow
        
        with patch('langgraph_workflows.obsidian_agent.obsidian_put_file') as mock_put:
            mock_put.return_value = {
                "success": True,
                "data": {
                    "approval_required": True,
                    "tool_call_id": "test_id_123"
                }
            }
            
            state = {
                "messages": [{"content": "Create a new note"}],
                "session_id": "test_session"
            }
            
            result = await execute_write_workflow(state)
            
            assert "messages" in result
            assert "pending_approvals" in result
            assert len(result["pending_approvals"]) > 0
            assert result["next_action"] == "check_pending_approvals"
    
    @pytest.mark.asyncio
    async def test_execute_search_workflow(self):
        """Test search workflow execution"""
        from langgraph_workflows.obsidian_agent import execute_search_workflow
        
        with patch('langgraph_workflows.obsidian_agent.obsidian_search_notes') as mock_search:
            mock_search.return_value = {
                "success": True,
                "data": {
                    "results": [
                        {"path": "note1.md", "content": "Search result 1"},
                        {"path": "note2.md", "content": "Search result 2"}
                    ]
                }
            }
            
            state = {
                "messages": [{"content": "search: AI"}],
                "session_id": "test_session"
            }
            
            result = await execute_search_workflow(state)
            
            assert "messages" in result
            assert "vault_data" in result
            assert result["next_action"] == "check_pending_approvals"
    
    @pytest.mark.asyncio
    async def test_check_pending_approvals(self):
        """Test pending approvals check"""
        from langgraph_workflows.obsidian_agent import check_pending_approvals
        
        with patch('langgraph_workflows.obsidian_agent.obsidian_list_pending_operations') as mock_pending:
            mock_pending.return_value = {
                "success": True,
                "data": [
                    {
                        "tool_call_id": "test_id_123",
                        "operation_type": "write",
                        "path": "test/note.md"
                    }
                ]
            }
            
            state = {
                "messages": [],
                "session_id": "test_session"
            }
            
            result = await check_pending_approvals(state)
            
            assert "messages" in result
            assert result["next_action"] == "end"
    
    @pytest.mark.asyncio
    async def test_error_handler(self):
        """Test error handling"""
        from langgraph_workflows.obsidian_agent import error_handler
        
        state = {
            "messages": [],
            "session_id": "test_session",
            "error_count": 2,
            "max_retries": 3
        }
        
        result = await error_handler(state)
        
        assert "messages" in result
        assert result["error_count"] == 3
        assert result["next_action"] == "classify_task"
        
        # Test max retries exceeded
        state["error_count"] = 3
        result = await error_handler(state)
        assert result["next_action"] == "end"
    
    @pytest.mark.asyncio
    async def test_run_agent_integration(self):
        """Test complete agent execution"""
        with patch('langgraph_workflows.obsidian_agent.obsidian_list_files') as mock_list:
            mock_list.return_value = {
                "success": True,
                "data": {"files": [{"path": "note1.md", "content": "Content 1"}]}
            }
            
            result = await run_agent("List all files in my vault", "test_session")
            
            assert result["success"] == True
            assert "session_id" in result
            assert "messages" in result
            assert len(result["messages"]) > 0

class TestWorkflowState:
    """Test workflow state management"""
    
    def test_agent_state_creation(self):
        """Test AgentState creation"""
        state = AgentState(
            messages=[],
            next_action="classify_task",
            context={},
            vault_data={},
            tool_calls=[],
            current_task="",
            session_id="test_session",
            pending_approvals=[],
            error_count=0,
            max_retries=3
        )
        
        assert state["session_id"] == "test_session"
        assert state["next_action"] == "classify_task"
        assert state["error_count"] == 0
    
    def test_state_transitions(self):
        """Test state transitions between nodes"""
        # This would test the actual state transitions in the workflow
        # For now, we'll test the structure
        workflow = create_obsidian_agent_workflow()
        
        # Check that workflow has proper edges
        edges = workflow.edges
        assert len(edges) > 0

@pytest.mark.asyncio
class TestConcurrentExecution:
    """Test concurrent agent execution"""
    
    async def test_multiple_agents(self):
        """Test running multiple agents concurrently"""
        with patch('langgraph_workflows.obsidian_agent.obsidian_list_files') as mock_list:
            mock_list.return_value = {
                "success": True,
                "data": {"files": []}
            }
            
            # Run multiple agents concurrently
            tasks = [
                run_agent("List files", f"session_{i}")
                for i in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All agents should complete successfully
            assert all(result["success"] for result in results)
            assert len(results) == 5

class TestToolIntegration:
    """Test tool integration with LangGraph"""
    
    @pytest.mark.asyncio
    async def test_obsidian_tools(self):
        """Test Obsidian tool functions"""
        from langgraph_workflows.obsidian_agent import obsidian_list_files
        
        with patch('langgraph_workflows.obsidian_agent.api_client.request') as mock_request:
            mock_request.return_value = {"files": []}
            
            result = await obsidian_list_files("Main")
            
            assert result["success"] == True
            assert "data" in result
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test tool error handling"""
        from langgraph_workflows.obsidian_agent import obsidian_read_note
        
        with patch('langgraph_workflows.obsidian_agent.api_client.request') as mock_request:
            mock_request.side_effect = Exception("API Error")
            
            result = await obsidian_read_note("Main", "nonexistent.md")
            
            assert result["success"] == False
            assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__])

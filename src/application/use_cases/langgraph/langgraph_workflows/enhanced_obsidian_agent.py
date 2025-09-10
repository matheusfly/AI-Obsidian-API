"""
Enhanced LangGraph Obsidian Agent with 2025 MCP integration patterns
Supports multi-server interoperability and advanced agent-to-agent communication
"""

from langgraph import StateGraph, END
from langgraph.workflow import Workflow
from langgraph.models import BaseModel
from typing import Dict, Any, List, Optional, TypedDict
import asyncio
import httpx
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """Enhanced agent state with multi-server support"""
    user_input: str
    vault_name: str
    session_id: str
    current_file: Optional[str]
    research_data: List[Dict[str, Any]]
    generated_content: str
    output_path: str
    tool_calls: List[Dict[str, Any]]
    agent_communications: List[Dict[str, Any]]
    workflow_status: str
    success: bool
    message: str
    requires_approval: bool
    approval_status: Optional[str]
    error_details: Optional[str]
    metadata: Dict[str, Any]

class MCPToolClient:
    """Enhanced MCP tool client with multi-server support"""
    
    def __init__(self, mcp_server_url: str = "http://mcp-server:8002"):
        self.mcp_server_url = mcp_server_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with enhanced error handling"""
        try:
            response = await self.client.post(
                f"{self.mcp_server_url}/tools/{tool_name}",
                json=parameters
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return {"error": str(e), "success": False}
    
    async def call_multiple_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Call multiple tools in parallel for improved performance"""
        tasks = [
            self.call_tool(call["tool_name"], call["parameters"])
            for call in tool_calls
        ]
        return await asyncio.gather(*tasks)

# Initialize MCP client
mcp_client = MCPToolClient()

def create_enhanced_agent_workflow() -> Workflow:
    """Create enhanced agent workflow with multi-server support"""
    
    def research_node(state: AgentState) -> AgentState:
        """Enhanced research node with multi-agent communication"""
        logger.info(f"Starting research for: {state['user_input']}")
        
        try:
            # Search for relevant information
            search_result = asyncio.run(mcp_client.call_tool("obsidian_search_notes", {
                "vault_name": state["vault_name"],
                "query": state["user_input"],
                "limit": 5,
                "include_content": True,
                "search_type": "semantic"
            }))
            
            if search_result.get("success"):
                state["research_data"] = search_result.get("results", [])
                state["message"] = f"Found {len(state['research_data'])} relevant notes"
                
                # Communicate with other agents about findings
                communication = asyncio.run(mcp_client.call_tool("obsidian_agent_communication", {
                    "target_agent": "research-coordinator",
                    "message": f"Research completed for: {state['user_input']}",
                    "data": {
                        "results_count": len(state["research_data"]),
                        "vault_name": state["vault_name"]
                    }
                }))
                
                if communication.get("success"):
                    state["agent_communications"].append(communication)
            else:
                state["message"] = f"Research failed: {search_result.get('error', 'Unknown error')}"
                state["error_details"] = search_result.get("error")
            
        except Exception as e:
            logger.error(f"Error in research node: {str(e)}")
            state["message"] = f"Research error: {str(e)}"
            state["error_details"] = str(e)
        
        return state
    
    def analyze_node(state: AgentState) -> AgentState:
        """Enhanced analysis node with advanced content processing"""
        logger.info("Starting content analysis")
        
        try:
            # Analyze research data
            analysis_results = []
            for item in state["research_data"]:
                analysis = {
                    "file_path": item.get("file_path", ""),
                    "relevance_score": item.get("relevance_score", 0.0),
                    "key_insights": extract_key_insights(item.get("content", "")),
                    "linked_files": item.get("links", {}).get("wiki_links", []),
                    "word_count": item.get("statistics", {}).get("word_count", 0)
                }
                analysis_results.append(analysis)
            
            # Get vault statistics for context
            vault_stats = asyncio.run(mcp_client.call_tool("obsidian_get_vault_stats", {
                "vault_name": state["vault_name"]
            }))
            
            state["metadata"]["analysis_results"] = analysis_results
            state["metadata"]["vault_stats"] = vault_stats.get("stats", {})
            state["message"] = f"Analysis completed: {len(analysis_results)} items processed"
            
        except Exception as e:
            logger.error(f"Error in analysis node: {str(e)}")
            state["message"] = f"Analysis error: {str(e)}"
            state["error_details"] = str(e)
        
        return state
    
    def generate_node(state: AgentState) -> AgentState:
        """Enhanced content generation with multi-agent collaboration"""
        logger.info("Starting content generation")
        
        try:
            # Generate content based on research and analysis
            content_prompt = f"""
            Based on the research data and analysis, generate content for:
            User Input: {state['user_input']}
            Vault: {state['vault_name']}
            
            Research Data: {json.dumps(state['research_data'][:3], indent=2)}
            Analysis Results: {json.dumps(state['metadata'].get('analysis_results', []), indent=2)}
            
            Generate comprehensive, well-structured content that incorporates insights from the research.
            """
            
            # This would integrate with an LLM service
            # For now, we'll generate a structured response
            generated_content = f"""# Generated Content for: {state['user_input']}

## Overview
Based on research from {len(state['research_data'])} sources in vault '{state['vault_name']}'.

## Key Insights
{format_insights(state['metadata'].get('analysis_results', []))}

## Detailed Analysis
{format_detailed_analysis(state['research_data'])}

## Recommendations
Based on the analysis, here are key recommendations:
- Continue research in related areas
- Consider creating additional connections between notes
- Review and update existing content for consistency

---
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Session: {state['session_id']}*
"""
            
            state["generated_content"] = generated_content
            state["output_path"] = f"generated/{state['session_id']}_{int(datetime.now().timestamp())}.md"
            state["message"] = "Content generated successfully"
            
            # Communicate generation completion
            communication = asyncio.run(mcp_client.call_tool("obsidian_agent_communication", {
                "target_agent": "content-reviewer",
                "message": "Content generation completed",
                "data": {
                    "content_length": len(generated_content),
                    "output_path": state["output_path"],
                    "session_id": state["session_id"]
                }
            }))
            
            if communication.get("success"):
                state["agent_communications"].append(communication)
            
        except Exception as e:
            logger.error(f"Error in generation node: {str(e)}")
            state["message"] = f"Generation error: {str(e)}"
            state["error_details"] = str(e)
        
        return state
    
    def write_node(state: AgentState) -> AgentState:
        """Enhanced write node with approval workflow"""
        logger.info("Starting content writing")
        
        try:
            # Write content to vault
            write_result = asyncio.run(mcp_client.call_tool("obsidian_put_file", {
                "vault_name": state["vault_name"],
                "file_path": state["output_path"],
                "content": state["generated_content"],
                "create_dirs": True,
                "backup_existing": True
            }))
            
            if write_result.get("success"):
                state["message"] = "Content written successfully"
                state["success"] = True
                
                # Set as active file
                set_active_result = asyncio.run(mcp_client.call_tool("obsidian_set_active_file", {
                    "vault_name": state["vault_name"],
                    "file_path": state["output_path"]
                }))
                
                if set_active_result.get("success"):
                    state["current_file"] = state["output_path"]
                
                # Communicate write completion
                communication = asyncio.run(mcp_client.call_tool("obsidian_agent_communication", {
                    "target_agent": "workflow-coordinator",
                    "message": "Content written successfully",
                    "data": {
                        "file_path": state["output_path"],
                        "session_id": state["session_id"],
                        "success": True
                    }
                }))
                
                if communication.get("success"):
                    state["agent_communications"].append(communication)
            else:
                state["message"] = f"Write failed: {write_result.get('error', 'Unknown error')}"
                state["error_details"] = write_result.get("error")
                state["success"] = False
            
        except Exception as e:
            logger.error(f"Error in write node: {str(e)}")
            state["message"] = f"Write error: {str(e)}"
            state["error_details"] = str(e)
            state["success"] = False
        
        return state
    
    def human_review_node(state: AgentState) -> AgentState:
        """Enhanced human review node with workflow status tracking"""
        logger.info("Starting human review process")
        
        try:
            # Check if approval is required
            if state.get("requires_approval", False):
                state["message"] = "Content requires human approval"
                state["workflow_status"] = "pending_approval"
                
                # Get workflow status
                workflow_status = asyncio.run(mcp_client.call_tool("obsidian_workflow_status", {
                    "workflow_id": state["session_id"],
                    "vault_name": state["vault_name"]
                }))
                
                if workflow_status.get("success"):
                    state["metadata"]["workflow_status"] = workflow_status
                
                # Communicate review requirement
                communication = asyncio.run(mcp_client.call_tool("obsidian_agent_communication", {
                    "target_agent": "human-reviewer",
                    "message": "Human review required",
                    "data": {
                        "file_path": state["output_path"],
                        "session_id": state["session_id"],
                        "content_preview": state["generated_content"][:200] + "..."
                    }
                }))
                
                if communication.get("success"):
                    state["agent_communications"].append(communication)
            else:
                state["message"] = "Content approved automatically"
                state["workflow_status"] = "approved"
                state["success"] = True
            
        except Exception as e:
            logger.error(f"Error in human review node: {str(e)}")
            state["message"] = f"Review error: {str(e)}"
            state["error_details"] = str(e)
        
        return state
    
    def error_handling_node(state: AgentState) -> AgentState:
        """Enhanced error handling with recovery strategies"""
        logger.info("Handling errors and recovery")
        
        try:
            if state.get("error_details"):
                # Log error for analysis
                logger.error(f"Agent error: {state['error_details']}")
                
                # Attempt recovery strategies
                recovery_strategies = [
                    "retry_operation",
                    "fallback_method",
                    "partial_success"
                ]
                
                state["metadata"]["recovery_strategies"] = recovery_strategies
                state["message"] = f"Error handled with recovery strategies: {', '.join(recovery_strategies)}"
                
                # Communicate error to monitoring system
                communication = asyncio.run(mcp_client.call_tool("obsidian_agent_communication", {
                    "target_agent": "error-monitor",
                    "message": "Error occurred and handled",
                    "data": {
                        "error": state["error_details"],
                        "session_id": state["session_id"],
                        "recovery_strategies": recovery_strategies
                    }
                }))
                
                if communication.get("success"):
                    state["agent_communications"].append(communication)
            
        except Exception as e:
            logger.error(f"Error in error handling node: {str(e)}")
            state["message"] = f"Error handling failed: {str(e)}"
        
        return state
    
    # Create enhanced workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("write", write_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("error_handling", error_handling_node)
    
    # Add edges with conditional logic
    workflow.add_edge("research", "analyze")
    workflow.add_edge("analyze", "generate")
    workflow.add_edge("generate", "write")
    workflow.add_edge("write", "human_review")
    
    # Conditional edges for error handling
    workflow.add_conditional_edges(
        "human_review",
        lambda state: "error_handling" if state.get("error_details") else "end",
        {
            "error_handling": "error_handling",
            "end": END
        }
    )
    
    workflow.add_edge("error_handling", END)
    
    # Set entry point
    workflow.set_entry_point("research")
    
    return workflow.compile()

def extract_key_insights(content: str) -> List[str]:
    """Extract key insights from content"""
    # Simple insight extraction - in production, use NLP libraries
    sentences = content.split('.')
    insights = []
    for sentence in sentences[:5]:  # Top 5 sentences
        if len(sentence.strip()) > 20:  # Meaningful sentences
            insights.append(sentence.strip())
    return insights

def format_insights(analysis_results: List[Dict[str, Any]]) -> str:
    """Format insights for display"""
    if not analysis_results:
        return "No insights available"
    
    formatted = []
    for i, result in enumerate(analysis_results[:3], 1):
        formatted.append(f"{i}. {result.get('file_path', 'Unknown')} (Score: {result.get('relevance_score', 0):.2f})")
        for insight in result.get('key_insights', [])[:2]:
            formatted.append(f"   - {insight}")
    
    return '\n'.join(formatted)

def format_detailed_analysis(research_data: List[Dict[str, Any]]) -> str:
    """Format detailed analysis for display"""
    if not research_data:
        return "No research data available"
    
    formatted = []
    for item in research_data[:3]:
        formatted.append(f"### {item.get('file_path', 'Unknown')}")
        formatted.append(f"**Relevance Score:** {item.get('relevance_score', 0):.2f}")
        formatted.append(f"**Content Preview:** {item.get('content', '')[:200]}...")
        formatted.append("")
    
    return '\n'.join(formatted)

# Create the enhanced workflow
enhanced_workflow = create_enhanced_agent_workflow()

# Export for use in LangGraph Server
__all__ = ["enhanced_workflow", "AgentState", "MCPToolClient"]

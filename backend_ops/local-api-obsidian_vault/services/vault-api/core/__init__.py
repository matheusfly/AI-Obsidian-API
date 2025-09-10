"""
Vault API Core Module
Local-first architecture with MCP tool integration
"""

from .local_first import LocalFirstManager, LocalOperation
from .mcp_tools import MCPToolRegistry, MCPTool, MCPResource, get_mcp_registry

__all__ = [
    'LocalFirstManager',
    'LocalOperation', 
    'MCPToolRegistry',
    'MCPTool',
    'MCPResource',
    'get_mcp_registry'
]
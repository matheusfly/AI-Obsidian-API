from mcp_tools.list_files import ObsidianListFilesTool
from mcp_tools.read_note import ObsidianReadNoteTool
from mcp_tools.put_file import ObsidianPutFileTool
from mcp_tools.patch_file import ObsidianPatchFileTool
from typing import Dict, Any, List
from utils.tracing import trace_tool_execution

class MCPToolRegistry:
    """Registry for all MCP tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default MCP tools"""
        self.register_tool(ObsidianListFilesTool())
        self.register_tool(ObsidianReadNoteTool())
        self.register_tool(ObsidianPutFileTool())
        self.register_tool(ObsidianPatchFileTool())
    
    def register_tool(self, tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str):
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools with their schemas"""
        return [tool.get_schema() for tool in self.tools.values()]
    
    async def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name with the given parameters"""
        tool = self.get_tool(name)
        if not tool:
            error_result = {"error": f"Tool '{name}' not found"}
            trace_tool_execution(name, kwargs, error_result)
            return error_result
        
        try:
            result = await tool(**kwargs)
            trace_tool_execution(name, kwargs, result)
            return result
        except Exception as e:
            error_result = {"error": str(e)}
            trace_tool_execution(name, kwargs, error_result)
            return error_result

# Global tool registry instance
tool_registry = MCPToolRegistry()
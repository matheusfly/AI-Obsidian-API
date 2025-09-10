from mcp_tools.base import MCPTool
from api_gateway.obsidian_client import ObsidianAPIClient
from typing import Dict, Any, Optional

class ObsidianListFilesTool(MCPTool):
    """List files in an Obsidian vault"""
    
    def __init__(self):
        super().__init__(
            name="obsidian_list_files",
            description="List files in an Obsidian vault"
        )
        self.client = ObsidianAPIClient()
    
    async def __call__(self, vault: str, cursor: Optional[str] = None, 
                       limit: int = 100, filter: Optional[str] = None) -> Dict[str, Any]:
        try:
            result = self.client.list_files(vault, filter=filter)
            # In a real implementation, we would handle pagination with cursor and limit
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "vault": {
                    "type": "string",
                    "description": "Name of the vault"
                },
                "cursor": {
                    "type": "string",
                    "description": "Pagination cursor"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of files to return",
                    "default": 100
                },
                "filter": {
                    "type": "string",
                    "description": "Filter files by path or pattern"
                }
            },
            "required": ["vault"]
        }
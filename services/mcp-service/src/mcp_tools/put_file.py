from mcp_tools.base import MCPTool
from api_gateway.obsidian_client import ObsidianAPIClient
from typing import Dict, Any, Optional

class ObsidianPutFileTool(MCPTool):
    """Create or update a file in Obsidian vault"""
    
    def __init__(self):
        super().__init__(
            name="obsidian_put_file",
            description="Create or update a file in Obsidian vault"
        )
        self.client = ObsidianAPIClient()
    
    async def __call__(self, vault: str, path: str, content: str, 
                       dry_run: bool = True, if_match: Optional[str] = None, 
                       mode: str = "upsert") -> Dict[str, Any]:
        try:
            result = self.client.upsert_note(vault, path, content, dry_run, if_match, mode)
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
                "path": {
                    "type": "string",
                    "description": "Path to the file"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write"
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Whether to perform a dry run",
                    "default": True
                },
                "if_match": {
                    "type": "string",
                    "description": "Hash for conflict detection"
                },
                "mode": {
                    "type": "string",
                    "description": "Write mode (upsert, create, update)",
                    "default": "upsert"
                }
            },
            "required": ["vault", "path", "content"]
        }
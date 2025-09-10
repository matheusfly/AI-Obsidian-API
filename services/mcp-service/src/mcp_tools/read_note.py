from mcp_tools.base import MCPTool
from api_gateway.obsidian_client import ObsidianAPIClient
from typing import Dict, Any
import hashlib

class ObsidianReadNoteTool(MCPTool):
    """Read content of a note from Obsidian vault"""
    
    def __init__(self):
        super().__init__(
            name="obsidian_read_note",
            description="Read content of a note from Obsidian vault"
        )
        self.client = ObsidianAPIClient()
    
    async def __call__(self, vault: str, path: str) -> Dict[str, Any]:
        try:
            result = self.client.read_note(vault, path)
            # Add hash for conflict detection
            content = result.get("content", "")
            hash_value = hashlib.sha256(content.encode()).hexdigest()
            result["_hash"] = hash_value
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
                    "description": "Path to the note"
                }
            },
            "required": ["vault", "path"]
        }
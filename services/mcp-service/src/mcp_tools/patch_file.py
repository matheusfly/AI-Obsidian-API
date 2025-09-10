from mcp_tools.base import MCPTool
from api_gateway.obsidian_client import ObsidianAPIClient
from typing import Dict, Any, List

class ObsidianPatchFileTool(MCPTool):
    """Patch content in an Obsidian file"""
    
    def __init__(self):
        super().__init__(
            name="obsidian_patch_file",
            description="Patch content in an Obsidian file"
        )
        self.client = ObsidianAPIClient()
    
    async def __call__(self, vault: str, path: str, patch_ops: List[Dict]) -> Dict[str, Any]:
        try:
            result = self.client.patch_note(vault, path, patch_ops)
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
                "patch_ops": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "op": {
                                "type": "string",
                                "enum": ["append", "insert", "replace"]
                            },
                            "content": {
                                "type": "string"
                            },
                            "position": {
                                "type": "string",
                                "description": "Position for insert operations"
                            },
                            "heading": {
                                "type": "string",
                                "description": "Heading for append operations"
                            }
                        }
                    }
                }
            },
            "required": ["vault", "path", "patch_ops"]
        }
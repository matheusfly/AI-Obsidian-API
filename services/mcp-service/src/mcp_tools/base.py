from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class MCPTool(ABC):
    """Base class for all MCP tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def __call__(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with the given parameters"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for this tool"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters_schema()
        }
    
    @abstractmethod
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Return the parameters schema for this tool"""
        pass
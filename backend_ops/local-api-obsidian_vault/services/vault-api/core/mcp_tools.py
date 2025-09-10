"""
Model Context Protocol (MCP) Tools Implementation
Provides standardized tool calling interface for AI agents
"""
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import aiofiles
from pathlib import Path

@dataclass
class MCPTool:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable

@dataclass
class MCPResource:
    uri: str
    name: str
    description: str
    mime_type: str

class MCPToolRegistry:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self._register_core_tools()
    
    def _register_core_tools(self):
        """Register core MCP tools"""
        
        # File operations
        self.register_tool(
            "read_file",
            "Read content from a file in the vault",
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path relative to vault"}
                },
                "required": ["path"]
            },
            self._read_file
        )
        
        self.register_tool(
            "write_file",
            "Write content to a file in the vault",
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path relative to vault"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            },
            self._write_file
        )
        
        self.register_tool(
            "list_files",
            "List files in a directory",
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path", "default": "."},
                    "pattern": {"type": "string", "description": "File pattern filter"}
                }
            },
            self._list_files
        )
        
        # Search operations
        self.register_tool(
            "search_content",
            "Search for content across vault files",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "semantic": {"type": "boolean", "description": "Use semantic search", "default": False},
                    "limit": {"type": "integer", "description": "Max results", "default": 10}
                },
                "required": ["query"]
            },
            self._search_content
        )
        
        # Note operations
        self.register_tool(
            "create_daily_note",
            "Create a daily note with template",
            {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "template": {"type": "string", "description": "Template name"}
                }
            },
            self._create_daily_note
        )
        
        self.register_tool(
            "extract_links",
            "Extract all links from a note",
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Note path"}
                },
                "required": ["path"]
            },
            self._extract_links
        )
        
        # AI operations
        self.register_tool(
            "summarize_note",
            "Generate summary of a note",
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Note path"},
                    "max_length": {"type": "integer", "description": "Max summary length", "default": 200}
                },
                "required": ["path"]
            },
            self._summarize_note
        )
        
        self.register_tool(
            "generate_tags",
            "Generate tags for a note",
            {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Note path"},
                    "max_tags": {"type": "integer", "description": "Max number of tags", "default": 5}
                },
                "required": ["path"]
            },
            self._generate_tags
        )
        
        # Workflow operations
        self.register_tool(
            "trigger_workflow",
            "Trigger an n8n workflow",
            {
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string", "description": "Workflow ID"},
                    "data": {"type": "object", "description": "Input data"}
                },
                "required": ["workflow_id"]
            },
            self._trigger_workflow
        )
    
    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], handler: Callable):
        """Register a new MCP tool"""
        self.tools[name] = MCPTool(name, description, parameters, handler)
    
    def register_resource(self, uri: str, name: str, description: str, mime_type: str):
        """Register a new MCP resource"""
        self.resources[uri] = MCPResource(uri, name, description, mime_type)
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a registered tool"""
        if name not in self.tools:
            return {"error": f"Tool '{name}' not found"}
        
        tool = self.tools[name]
        try:
            result = await tool.handler(arguments)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all available resources"""
        return [asdict(resource) for resource in self.resources.values()]
    
    # Tool implementations
    async def _read_file(self, args: Dict[str, Any]) -> str:
        """Read file content"""
        file_path = self.vault_path / args["path"]
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {args['path']}")
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    async def _write_file(self, args: Dict[str, Any]) -> str:
        """Write file content"""
        file_path = self.vault_path / args["path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(args["content"])
        
        return f"File written: {args['path']}"
    
    async def _list_files(self, args: Dict[str, Any]) -> List[str]:
        """List files in directory"""
        dir_path = self.vault_path / args.get("path", ".")
        pattern = args.get("pattern", "*")
        
        if not dir_path.exists():
            return []
        
        files = []
        for file_path in dir_path.rglob(pattern):
            if file_path.is_file():
                files.append(str(file_path.relative_to(self.vault_path)))
        
        return sorted(files)
    
    async def _search_content(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search content across files"""
        query = args["query"].lower()
        results = []
        
        for file_path in self.vault_path.rglob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                if query in content.lower():
                    # Find context around match
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if query in line.lower():
                            context_start = max(0, i - 2)
                            context_end = min(len(lines), i + 3)
                            context = '\n'.join(lines[context_start:context_end])
                            
                            results.append({
                                "path": str(file_path.relative_to(self.vault_path)),
                                "line": i + 1,
                                "context": context,
                                "match": line.strip()
                            })
                            break
            except Exception:
                continue
        
        return results[:args.get("limit", 10)]
    
    async def _create_daily_note(self, args: Dict[str, Any]) -> str:
        """Create daily note"""
        date = args.get("date", datetime.now().strftime("%Y-%m-%d"))
        template = args.get("template", "daily")
        
        note_path = f"daily/{date}.md"
        file_path = self.vault_path / note_path
        
        if file_path.exists():
            return f"Daily note already exists: {note_path}"
        
        # Basic daily note template
        content = f"""# Daily Note - {date}

## Tasks
- [ ] 

## Notes


## Reflections


---
Created: {datetime.now().isoformat()}
Tags: #daily
"""
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        return f"Daily note created: {note_path}"
    
    async def _extract_links(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract links from note"""
        content = await self._read_file(args)
        links = []
        
        # Extract [[wikilinks]]
        import re
        wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
        for link in wiki_links:
            links.append({"type": "wikilink", "target": link})
        
        # Extract [markdown](links)
        md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for text, url in md_links:
            links.append({"type": "markdown", "text": text, "url": url})
        
        return links
    
    async def _summarize_note(self, args: Dict[str, Any]) -> str:
        """Summarize note content"""
        content = await self._read_file(args)
        max_length = args.get("max_length", 200)
        
        # Simple extractive summary (first paragraph + key points)
        lines = content.split('\n')
        summary_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                summary_lines.append(line)
                if len(' '.join(summary_lines)) > max_length:
                    break
        
        summary = ' '.join(summary_lines)
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    async def _generate_tags(self, args: Dict[str, Any]) -> List[str]:
        """Generate tags for note"""
        content = await self._read_file(args)
        max_tags = args.get("max_tags", 5)
        
        # Simple keyword extraction
        import re
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = {}
        
        # Common stop words to exclude
        stop_words = {'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'about', 'would', 'there', 'could', 'other', 'more', 'very', 'what', 'know', 'just', 'first', 'into', 'over', 'think', 'also', 'your', 'work', 'life', 'only', 'can', 'still', 'should', 'after', 'being', 'now', 'made', 'before', 'here', 'through', 'when', 'where', 'much', 'some', 'these', 'many', 'then', 'them', 'well', 'were'}
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most frequent words as tags
        tags = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [tag[0] for tag in tags[:max_tags]]
    
    async def _trigger_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger n8n workflow"""
        workflow_id = args["workflow_id"]
        data = args.get("data", {})
        
        async with aiohttp.ClientSession() as session:
            url = f"http://localhost:5678/webhook/{workflow_id}"
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"status": "triggered", "result": result}
                else:
                    return {"status": "error", "message": f"HTTP {response.status}"}

# Global MCP registry instance
mcp_registry = None

def get_mcp_registry(vault_path: str = None) -> MCPToolRegistry:
    """Get or create MCP registry instance"""
    global mcp_registry
    if mcp_registry is None and vault_path:
        mcp_registry = MCPToolRegistry(vault_path)
    return mcp_registry
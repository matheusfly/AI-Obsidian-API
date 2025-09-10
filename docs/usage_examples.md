# Usage Examples

This document provides practical examples of how to use the LangGraph + Obsidian integration.

## Basic API Usage

### Listing Vaults
```bash
curl -X GET "http://localhost:8000/vaults"
```

### Listing Files in a Vault
```bash
curl -X GET "http://localhost:8000/vault/default/files"
```

### Reading a Note
```bash
curl -X GET "http://localhost:8000/vault/default/file/Notes/Example.md"
```

### Creating/Updating a Note
```bash
curl -X PUT "http://localhost:8000/vault/default/file/Notes/NewNote.md" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "Notes/NewNote.md",
    "content": "# New Note\n\nThis is a new note created via the API.",
    "dry_run": false
  }'
```

### Searching Notes
```bash
curl -X POST "http://localhost:8000/search/simple" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "project planning"
  }'
```

## MCP Tool Usage

### Listing Available MCP Tools
```bash
curl -X GET "http://localhost:8000/mcp/tools"
```

### Executing an MCP Tool
```bash
curl -X POST "http://localhost:8000/mcp/tools/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "obsidian_list_files",
    "parameters": {
      "vault": "default"
    }
  }'
```

### Reading a Note with MCP Tool
```bash
curl -X POST "http://localhost:8000/mcp/tools/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "obsidian_read_note",
    "parameters": {
      "vault": "default",
      "path": "Notes/Example.md"
    }
  }'
```

## Python Client Example

```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

# List vaults
response = requests.get(f"{BASE_URL}/vaults")
vaults = response.json()
print("Available vaults:", vaults)

# List files in a vault
response = requests.get(f"{BASE_URL}/vault/default/files")
files = response.json()
print("Files in vault:", files)

# Read a note
response = requests.get(f"{BASE_URL}/vault/default/file/Notes/Example.md")
note = response.json()
print("Note content:", note.get("content"))

# Create/update a note
note_data = {
    "path": "Notes/PythonExample.md",
    "content": "# Python Example\n\nThis note was created using Python requests.",
    "dry_run": False
}
response = requests.put(f"{BASE_URL}/vault/default/file/Notes/PythonExample.md", 
                       json=note_data)
result = response.json()
print("Note creation result:", result)

# Execute an MCP tool
mcp_request = {
    "tool_name": "obsidian_read_note",
    "parameters": {
        "vault": "default",
        "path": "Notes/PythonExample.md"
    }
}
response = requests.post(f"{BASE_URL}/mcp/tools/execute", json=mcp_request)
tool_result = response.json()
print("MCP tool result:", tool_result)
```

## LangGraph Agent Example

```python
from langgraph import Agent
from mcp_tools.registry import tool_registry

# Create an agent with access to Obsidian tools
class ObsidianAgent(Agent):
    def __init__(self):
        super().__init__()
        # Register MCP tools with the agent
        for tool_schema in tool_registry.list_tools():
            self.register_tool(tool_schema["name"], self.execute_mcp_tool)
    
    async def execute_mcp_tool(self, tool_name, **kwargs):
        """Execute an MCP tool through the API gateway"""
        return await tool_registry.execute_tool(tool_name, **kwargs)
    
    def plan_research_task(self, topic):
        """Plan a research task for a given topic"""
        plan = [
            {
                "tool": "obsidian_list_files",
                "parameters": {"vault": "default"},
                "description": "List existing files to avoid duplication"
            },
            {
                "tool": "obsidian_put_file",
                "parameters": {
                    "vault": "default",
                    "path": f"Research/{topic}.md",
                    "content": f"# {topic} Research\n\n## Overview\n\n## Key Points\n\n## References\n",
                    "dry_run": False
                },
                "description": "Create initial research note"
            }
        ]
        return plan

# Usage
agent = ObsidianAgent()
research_plan = agent.plan_research_task("AI Ethics")
print("Research plan:", research_plan)
```

## Indexing and Search Example

### Indexing the Vault
```bash
curl -X POST "http://localhost:8000/index/vault"
```

### Hybrid Search
```bash
curl -X POST "http://localhost:8000/search/hybrid" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning applications",
    "k": 5
  }'
```

## Safe Write Operations

### Conflict Detection Example
```bash
# First, read a note to get its hash
curl -X GET "http://localhost:8000/vault/default/file/Notes/Example.md"

# Then, update the note with conflict detection
curl -X PUT "http://localhost:8000/vault/default/file/Notes/Example.md" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "Notes/Example.md",
    "content": "# Updated Example\n\nThis note has been updated.",
    "dry_run": false,
    "if_match": "previous_hash_value"
  }'
```

## Docker Usage Examples

### Building and Running with Docker
```bash
# Navigate to the docker directory
cd docker

# Build the container
docker-compose build

# Run the container
docker-compose up

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs

# Stop the container
docker-compose down
```

### Environment Configuration
Create a `.env` file in the project root:
```env
OBSIDIAN_API_BASE=http://host.docker.internal:27123
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_VAULT_PATH=/vault
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key_here
```

Then run with:
```bash
docker-compose --env-file .env up
```

## Advanced Usage Patterns

### Batch Operations
```python
import asyncio
import aiohttp

async def batch_read_notes(note_paths):
    """Read multiple notes concurrently"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for path in note_paths:
            url = f"http://localhost:8000/vault/default/file/{path}"
            task = asyncio.create_task(session.get(url))
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        results = []
        for response in responses:
            data = await response.json()
            results.append(data)
        return results

# Usage
note_paths = [
    "Notes/Project1.md",
    "Notes/Project2.md",
    "Notes/Project3.md"
]
notes = asyncio.run(batch_read_notes(note_paths))
```

### Workflow Automation
```python
import requests
import time

def daily_note_workflow():
    """Automated workflow for daily note management"""
    # Get today's daily note
    response = requests.get("http://localhost:8000/periodic/daily/default")
    daily_note = response.json()
    
    # Extract key information from the note
    content = daily_note.get("content", "")
    
    # Update related project notes
    if "# Projects" in content:
        # Parse projects from daily note
        projects = parse_projects_from_content(content)
        
        # Update each project note
        for project in projects:
            update_project_note(project)
    
    # Index the vault to capture changes
    requests.post("http://localhost:8000/index/vault")

def parse_projects_from_content(content):
    """Parse project information from note content"""
    # Implementation would parse the markdown content
    # to extract project-related information
    pass

def update_project_note(project):
    """Update a project note with daily information"""
    # Implementation would update the relevant project note
    # with information extracted from the daily note
    pass

# Schedule this workflow to run daily
# This could be done with a cron job or task scheduler
```

These examples demonstrate the core functionality of the LangGraph + Obsidian integration. The system provides flexible APIs for interacting with Obsidian vaults while maintaining safety through conflict detection and dry-run operations.
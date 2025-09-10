# Python SDK

The Obsidian Vault AI System provides a comprehensive Python SDK for easy integration.

## Installation

```bash
pip install obsidian-vault-ai-sdk
```

## Quick Start

```python
from obsidian_vault_ai import VaultClient, MCPClient

# Initialize the client
client = VaultClient(
    base_url="http://localhost:8085",
    api_key="your-api-key"
)

# Connect to MCP tools
mcp = MCPClient(client)

# List vault files
files = await client.list_files()
print(f"Found {len(files)} files in vault")

# Read a file
content = await client.read_file("path/to/file.md")
print(content)
```

## Vault Operations

### File Management

```python
# List all files
files = await client.list_files()

# List files in directory
files = await client.list_files(directory="notes/")

# Read file content
content = await client.read_file("notes/example.md")

# Write file content
await client.write_file("notes/new-file.md", "# New File\n\nContent here")

# Delete file
await client.delete_file("notes/old-file.md")

# Search files
results = await client.search_files(query="python", limit=10)
```

### AI Operations

```python
# Generate content
content = await client.generate_content(
    prompt="Write a summary of machine learning",
    context_files=["notes/ml-basics.md"]
)

# Analyze vault
analysis = await client.analyze_vault()

# Get insights
insights = await client.get_insights(topic="python")
```

## MCP Integration

### Using MCP Tools

```python
# Filesystem operations
files = await mcp.filesystem.list_files("/vault/path")
content = await mcp.filesystem.read_file("/vault/path/file.md")

# GitHub operations
repo = await mcp.github.get_repository("owner", "repo")
issues = await mcp.github.list_issues("owner", "repo")

# Context management
await mcp.context7.store_context("key", {"data": "value"})
context = await mcp.context7.get_context("key")
```

### Custom MCP Tools

```python
# Register custom tool
@mcp.register_tool("custom_analysis")
async def analyze_document(content: str) -> dict:
    """Analyze document content."""
    # Your analysis logic
    return {"sentiment": "positive", "keywords": ["ai", "ml"]}

# Use custom tool
result = await mcp.call_tool("custom_analysis", {"content": "AI is amazing!"})
```

## WebSocket Support

```python
import asyncio

async def handle_websocket():
    async with client.websocket() as ws:
        async for message in ws:
            if message.type == "vault_update":
                print(f"File updated: {message.data['file_path']}")
            elif message.type == "ai_status":
                print(f"AI task status: {message.data['status']}")

# Run WebSocket listener
asyncio.run(handle_websocket())
```

## Error Handling

```python
from obsidian_vault_ai.exceptions import VaultError, MCPError

try:
    content = await client.read_file("nonexistent.md")
except VaultError as e:
    print(f"Vault error: {e.message}")
except MCPError as e:
    print(f"MCP error: {e.message}")
```

## Configuration

```python
from obsidian_vault_ai import VaultClient

client = VaultClient(
    base_url="http://localhost:8085",
    api_key="your-api-key",
    timeout=30,
    retry_attempts=3,
    retry_delay=1.0
)
```

## Advanced Usage

### Batch Operations

```python
# Batch file operations
files = ["file1.md", "file2.md", "file3.md"]
contents = await client.batch_read_files(files)

# Batch write operations
data = [
    {"path": "file1.md", "content": "Content 1"},
    {"path": "file2.md", "content": "Content 2"}
]
await client.batch_write_files(data)
```

### Caching

```python
from obsidian_vault_ai.cache import MemoryCache

# Enable caching
client = VaultClient(
    base_url="http://localhost:8085",
    cache=MemoryCache(ttl=300)  # 5 minutes
)
```

### Logging

```python
import logging
from obsidian_vault_ai.logging import setup_logging

# Setup logging
setup_logging(level=logging.INFO)

# Use client with logging
client = VaultClient(base_url="http://localhost:8085")
```

## Examples

### Complete Workflow

```python
import asyncio
from obsidian_vault_ai import VaultClient, MCPClient

async def main():
    # Initialize clients
    client = VaultClient(base_url="http://localhost:8085")
    mcp = MCPClient(client)
    
    # List all files
    files = await client.list_files()
    print(f"Found {len(files)} files")
    
    # Analyze each file
    for file_path in files[:5]:  # Process first 5 files
        content = await client.read_file(file_path)
        analysis = await mcp.call_tool("analyze_text", {"text": content})
        print(f"Analysis for {file_path}: {analysis}")
    
    # Generate summary
    summary = await client.generate_content(
        prompt="Summarize the vault content",
        context_files=files
    )
    print(f"Vault summary: {summary}")

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

For complete API reference, see the [OpenAPI documentation](/docs/api/openapi/specification).

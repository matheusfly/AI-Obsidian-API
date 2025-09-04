# MCP (Model Context Protocol) Overview

The Obsidian Vault AI System integrates with multiple MCP tools to enhance AI capabilities and provide rich context for operations.

## Available MCP Tools

### Core MCP Tools

| Tool | Description | Status |
|------|-------------|--------|
| **filesystem** | File system operations | ✅ Active |
| **github** | GitHub repository management | ✅ Active |
| **sequential-thinking** | Advanced reasoning | ✅ Active |
| **playwright** | Web automation | ✅ Active |
| **context7** | Context management | ✅ Active |
| **byterover-mcp** | Memory and knowledge | ✅ Active |
| **fetch** | HTTP requests | ✅ Active |
| **brave-search** | Web search | ✅ Active |

## MCP Configuration

MCP tools are configured in the `mcp-servers.json` file:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/path/to/vault"]
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"
      }
    }
  }
}
```

## Using MCP Tools

### Filesystem Operations

```python
# List files in vault
result = await mcp_client.call_tool("filesystem", "list_files", {
    "path": "/vault/path"
})

# Read file content
content = await mcp_client.call_tool("filesystem", "read_file", {
    "path": "/vault/path/file.md"
})
```

### GitHub Integration

```python
# Get repository information
repo_info = await mcp_client.call_tool("github", "get_repository", {
    "owner": "username",
    "repo": "repository-name"
})

# Create issue
issue = await mcp_client.call_tool("github", "create_issue", {
    "owner": "username",
    "repo": "repository-name",
    "title": "Issue Title",
    "body": "Issue description"
})
```

### Context Management

```python
# Store context
await mcp_client.call_tool("context7", "store_context", {
    "key": "user_preference",
    "value": {"theme": "dark", "language": "en"}
})

# Retrieve context
context = await mcp_client.call_tool("context7", "get_context", {
    "key": "user_preference"
})
```

## MCP Tool Development

### Creating Custom MCP Tools

1. **Define the tool interface**:
```python
@mcp_tool
async def custom_tool(param1: str, param2: int) -> dict:
    """Custom MCP tool description."""
    # Tool implementation
    return {"result": "success"}
```

2. **Register the tool**:
```python
mcp_server.register_tool("custom_tool", custom_tool)
```

3. **Test the tool**:
```python
result = await mcp_client.call_tool("custom_tool", {
    "param1": "value",
    "param2": 42
})
```

## Error Handling

MCP tools return structured error responses:

```json
{
  "error": {
    "code": "TOOL_ERROR",
    "message": "Tool execution failed",
    "details": {
      "tool": "filesystem",
      "operation": "read_file",
      "path": "/invalid/path"
    }
  }
}
```

## Best Practices

1. **Always handle errors** when calling MCP tools
2. **Validate parameters** before tool execution
3. **Use appropriate timeouts** for long-running operations
4. **Log tool usage** for debugging and monitoring
5. **Implement retry logic** for transient failures

## Monitoring

MCP tool usage is monitored through:

- **Prometheus metrics** for tool call counts and durations
- **Grafana dashboards** for visualization
- **Structured logging** for debugging
- **Health checks** for tool availability

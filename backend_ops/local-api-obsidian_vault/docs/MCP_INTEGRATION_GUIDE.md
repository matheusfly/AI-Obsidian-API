# 🔌 MCP Integration Guide - Model Context Protocol

## Overview

Model Context Protocol (MCP) enables AI assistants to interact with your Obsidian vault through standardized tools and resources. This guide shows how to set up and use MCP with your vault system.

## 🚀 Quick MCP Setup

### 1. Install MCP Server
```bash
# Install MCP server for Obsidian
npm install -g @modelcontextprotocol/server-obsidian

# Or use our custom implementation
cd mcp-server
npm install
```

### 2. Configure MCP Server
```json
{
  "name": "obsidian-vault-mcp",
  "version": "1.0.0",
  "capabilities": {
    "tools": true,
    "resources": true,
    "prompts": true
  },
  "vault_path": "/mnt/d/Nomade Milionario",
  "api_endpoint": "http://localhost:27123",
  "api_key": "your_api_key_here"
}
```

### 3. Start MCP Server
```bash
# Start MCP server
node mcp-server/server.js

# Or use Docker
docker-compose up -d mcp-server
```

## 🛠️ Available MCP Tools

### Core Vault Operations

#### `obsidian_read_note`
Read content from a specific note.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "path": {
      "type": "string",
      "description": "Path to the note (e.g., 'daily/2024-01-15.md')"
    }
  },
  "required": ["path"]
}
```

**Example Usage:**
```bash
# Via MCP client
{
  "tool": "obsidian_read_note",
  "arguments": {
    "path": "projects/my-project.md"
  }
}
```

#### `obsidian_create_note`
Create a new note with content.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "path": {
      "type": "string",
      "description": "Path for the new note"
    },
    "content": {
      "type": "string",
      "description": "Markdown content for the note"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Optional tags for the note"
    }
  },
  "required": ["path", "content"]
}
```

#### `obsidian_update_note`
Update existing note content.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "path": {"type": "string"},
    "content": {"type": "string"},
    "append": {
      "type": "boolean",
      "description": "Whether to append or replace content"
    }
  },
  "required": ["path", "content"]
}
```

#### `obsidian_search_notes`
Search across all notes in the vault.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query"
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results",
      "default": 10
    },
    "folders": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Specific folders to search in"
    }
  },
  "required": ["query"]
}
```

#### `obsidian_list_notes`
List notes in the vault or specific folder.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "folder": {
      "type": "string",
      "description": "Specific folder to list (optional)"
    },
    "limit": {
      "type": "integer",
      "default": 50
    }
  }
}
```

### Advanced Tools

#### `obsidian_analyze_note`
Analyze note content with AI.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "path": {"type": "string"},
    "analysis_type": {
      "type": "string",
      "enum": ["summary", "tags", "links", "structure"],
      "description": "Type of analysis to perform"
    }
  },
  "required": ["path", "analysis_type"]
}
```

#### `obsidian_create_daily_note`
Create or get today's daily note.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "date": {
      "type": "string",
      "description": "Date in YYYY-MM-DD format (optional, defaults to today)"
    },
    "template": {
      "type": "string",
      "description": "Template to use for daily note"
    }
  }
}
```

#### `obsidian_link_notes`
Create links between notes.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "source_path": {"type": "string"},
    "target_path": {"type": "string"},
    "link_text": {
      "type": "string",
      "description": "Custom text for the link"
    }
  },
  "required": ["source_path", "target_path"]
}
```

## 📚 MCP Resources

### Available Resources

#### `vault://notes`
Access to all notes in the vault.

```json
{
  "uri": "vault://notes",
  "name": "All Vault Notes",
  "description": "Complete collection of notes in the Obsidian vault",
  "mimeType": "application/json"
}
```

#### `vault://folders`
Folder structure of the vault.

```json
{
  "uri": "vault://folders",
  "name": "Vault Folder Structure",
  "description": "Hierarchical folder structure of the vault",
  "mimeType": "application/json"
}
```

#### `vault://tags`
All tags used in the vault.

```json
{
  "uri": "vault://tags",
  "name": "Vault Tags",
  "description": "All tags used across notes in the vault",
  "mimeType": "application/json"
}
```

#### `vault://recent`
Recently modified notes.

```json
{
  "uri": "vault://recent",
  "name": "Recent Notes",
  "description": "Notes modified in the last 7 days",
  "mimeType": "application/json"
}
```

## 🎯 MCP Prompts

### Pre-configured Prompts

#### `daily_review`
Generate a daily review based on today's notes.

**Arguments:**
- `date` (optional): Date to review
- `include_tasks` (boolean): Include task analysis

#### `note_summary`
Create a summary of a specific note.

**Arguments:**
- `path` (required): Path to the note
- `length` (optional): Summary length (short/medium/long)

#### `vault_insights`
Generate insights about the entire vault.

**Arguments:**
- `timeframe` (optional): Time period to analyze
- `focus` (optional): Specific area to focus on

## 🔧 Custom MCP Server Implementation

### Server Code Structure
```javascript
// mcp-server/server.js
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { 
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema
} from '@modelcontextprotocol/sdk/types.js';

const server = new Server(
  {
    name: "obsidian-vault-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
      prompts: {},
    },
  }
);

// Tool handlers
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "obsidian_read_note",
      description: "Read content from an Obsidian note",
      inputSchema: {
        type: "object",
        properties: {
          path: { type: "string", description: "Path to the note" }
        },
        required: ["path"]
      }
    },
    // ... more tools
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  switch (name) {
    case "obsidian_read_note":
      return await handleReadNote(args.path);
    case "obsidian_create_note":
      return await handleCreateNote(args.path, args.content, args.tags);
    // ... more handlers
  }
});
```

### Tool Implementation Examples

```javascript
// Tool implementations
async function handleReadNote(path) {
  try {
    const response = await fetch(`${API_ENDPOINT}/vault/default/file/${path}`, {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to read note: ${response.statusText}`);
    }
    
    const content = await response.text();
    
    return {
      content: [{
        type: "text",
        text: content
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error reading note: ${error.message}`
      }],
      isError: true
    };
  }
}

async function handleCreateNote(path, content, tags = []) {
  try {
    // Add tags to content if provided
    let noteContent = content;
    if (tags.length > 0) {
      const tagString = tags.map(tag => `#${tag}`).join(' ');
      noteContent = `---\ntags: [${tags.map(t => `"${t}"`).join(', ')}]\n---\n\n${content}`;
    }
    
    const response = await fetch(`${API_ENDPOINT}/vault/default/file/${path}`, {
      method: 'PUT',
      headers: { 
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'text/plain'
      },
      body: noteContent
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create note: ${response.statusText}`);
    }
    
    return {
      content: [{
        type: "text",
        text: `Note created successfully at ${path}`
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error creating note: ${error.message}`
      }],
      isError: true
    };
  }
}
```

## 🤖 AI Assistant Integration

### Claude Desktop Configuration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "obsidian-vault": {
      "command": "node",
      "args": ["path/to/mcp-server/server.js"],
      "env": {
        "VAULT_PATH": "/mnt/d/Nomade Milionario",
        "API_ENDPOINT": "http://localhost:27123",
        "API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Example AI Conversations

**Creating a Daily Note:**
```
User: Create today's daily note with a standard template

AI: I'll create today's daily note for you.

[Uses obsidian_create_daily_note tool]

I've created your daily note for January 15, 2024 with sections for goals, tasks, notes, and reflections.
```

**Searching and Summarizing:**
```
User: Find notes about "machine learning" and summarize the key points

AI: Let me search for notes about machine learning and provide a summary.

[Uses obsidian_search_notes tool, then obsidian_read_note for relevant results]

I found 5 notes about machine learning. Here are the key points:
- [Summary of findings]
```

## 🔄 Workflow Integration

### n8n + MCP Integration

Create n8n workflows that use MCP tools:

```json
{
  "name": "MCP Note Processing",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "name": "MCP Tool Call",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:3001/mcp/call-tool",
        "method": "POST",
        "body": {
          "tool": "obsidian_analyze_note",
          "arguments": {
            "path": "{{$json.note_path}}",
            "analysis_type": "summary"
          }
        }
      }
    }
  ]
}
```

## 📊 Testing MCP Integration

### Test Script
```bash
#!/bin/bash

# Test MCP server connectivity
echo "Testing MCP server..."

# Test tool listing
curl -X POST http://localhost:3001/mcp/list-tools

# Test note reading
curl -X POST http://localhost:3001/mcp/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "obsidian_read_note",
    "arguments": {"path": "test.md"}
  }'

# Test note creation
curl -X POST http://localhost:3001/mcp/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "obsidian_create_note",
    "arguments": {
      "path": "mcp-test.md",
      "content": "# MCP Test\n\nThis note was created via MCP!",
      "tags": ["mcp", "test"]
    }
  }'
```

## 🚀 Advanced MCP Features

### Custom Tool Development

```javascript
// Add custom tools to your MCP server
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    // ... existing tools
    {
      name: "obsidian_generate_moc",
      description: "Generate a Map of Content for a topic",
      inputSchema: {
        type: "object",
        properties: {
          topic: { type: "string", description: "Topic for the MOC" },
          folder: { type: "string", description: "Folder to search in" }
        },
        required: ["topic"]
      }
    }
  ]
}));
```

### Resource Streaming

```javascript
// Stream large resources efficiently
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;
  
  if (uri === "vault://all-notes") {
    // Stream all notes efficiently
    const notes = await getAllNotesStream();
    return {
      contents: [{
        uri,
        mimeType: "application/json",
        text: JSON.stringify(notes)
      }]
    };
  }
});
```

This MCP integration enables powerful AI interactions with your Obsidian vault while maintaining security and performance!
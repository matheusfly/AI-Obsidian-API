# 🔧 API Reference

<div align="center">

![API Reference](https://img.shields.io/badge/API-Reference-blue?style=for-the-badge&logo=api)
![REST API](https://img.shields.io/badge/REST-API-green?style=for-the-badge&logo=rest)
![Real Data](https://img.shields.io/badge/Real-Data-orange?style=for-the-badge&logo=database)

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🌐 Base Endpoints](#-base-endpoints)
- [🛠️ Tool Execution API](#️-tool-execution-api)
- [📊 Response Formats](#-response-formats)
- [🔍 Tool Reference](#-tool-reference)
- [❌ Error Handling](#-error-handling)
- [📝 Examples](#-examples)
- [🚀 Quick Start](#-quick-start)

---

## 🎯 Overview

The MCP Server provides a comprehensive RESTful API for interacting with Obsidian vaults through the Model Context Protocol. All endpoints return real data from your vault.

### 🌐 Base URL

```
http://localhost:3010
```

### 📡 API Features

| Feature | Description | Status |
|---------|-------------|--------|
| **RESTful Design** | Standard HTTP methods and status codes | ✅ Implemented |
| **JSON Payloads** | All requests and responses in JSON | ✅ Implemented |
| **Real Data Integration** | Direct integration with Obsidian vault | ✅ Working |
| **Error Handling** | Comprehensive error responses | ✅ Implemented |
| **Caching** | Built-in response caching | ✅ Optimized |

---

## 🌐 Base Endpoints

### 🏥 Health Check

Check the server health and status.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "MCP Server with real data integration is operational",
  "mode": "real-data",
  "timestamp": "2025-09-17T05:40:56-03:00"
}
```

**Status Codes:**
- `200 OK` - Server is healthy
- `500 Internal Server Error` - Server has issues

<details>
<summary>🔧 <strong>Example Usage</strong></summary>

```bash
# cURL
curl http://localhost:3010/health

# PowerShell
Invoke-RestMethod -Uri "http://localhost:3010/health" -Method Get

# Response
{
  "status": "healthy",
  "message": "MCP Server with real data integration is operational",
  "mode": "real-data",
  "timestamp": "2025-09-17T05:40:56-03:00"
}
```

</details>

### 🛠️ List Tools

Get a list of all available MCP tools.

```http
GET /tools/list
```

**Response:**
```json
[
  {
    "name": "list_files_in_vault",
    "description": "Lists all files in the Obsidian vault",
    "inputSchema": {
      "type": "object",
      "properties": {
        "path": {
          "type": "string",
          "description": "Path to list files from (optional)"
        }
      }
    }
  },
  {
    "name": "read_note",
    "description": "Reads the content of a specific note",
    "inputSchema": {
      "type": "object",
      "properties": {
        "filename": {
          "type": "string",
          "description": "Name of the file to read"
        }
      },
      "required": ["filename"]
    }
  }
]
```

<details>
<summary>🔧 <strong>Example Usage</strong></summary>

```bash
# cURL
curl http://localhost:3010/tools/list

# PowerShell
Invoke-RestMethod -Uri "http://localhost:3010/tools/list" -Method Get

# Response (truncated)
[
  {
    "name": "list_files_in_vault",
    "description": "Lists all files in the Obsidian vault",
    "inputSchema": { ... }
  }
]
```

</details>

---

## 🛠️ Tool Execution API

### ⚡ Execute Tool

Execute any available MCP tool with parameters.

```http
POST /tools/execute
Content-Type: application/json

{
  "tool_name": "string",
  "parameters": {}
}
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool_name` | string | ✅ | Name of the tool to execute |
| `parameters` | object | ✅ | Tool-specific parameters |

**Response:**
```json
{
  "success": true,
  "result": {},
  "message": "string"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the tool execution was successful |
| `result` | object | Tool execution result data |
| `message` | string | Human-readable status message |

---

## 🔍 Tool Reference

### 📁 List Files in Vault

Lists all files and folders in the Obsidian vault.

**Tool Name:** `list_files_in_vault`

**Parameters:**
```json
{
  "path": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "result": [
    {
      "name": "AGENTS.md",
      "path": "AGENTS.md",
      "type": "file"
    },
    {
      "name": "--METAS",
      "path": "--METAS",
      "type": "folder"
    }
  ],
  "message": "Found 69 files"
}
```

<details>
<summary>🔧 <strong>Example Usage</strong></summary>

```bash
# cURL
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"list_files_in_vault","parameters":{}}'

# PowerShell
$body = '{"tool_name":"list_files_in_vault","parameters":{}}'
Invoke-RestMethod -Uri "http://localhost:3010/tools/execute" -Method Post -Body $body -ContentType "application/json"
```

</details>

### 📖 Read Note

Reads the content of a specific note from the vault.

**Tool Name:** `read_note`

**Parameters:**
```json
{
  "filename": "string (required)"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "filename": "AGENTS.md",
    "content": "# AGENTS.md content...",
    "size": 217,
    "lastModified": "2025-09-17T05:40:56-03:00"
  },
  "message": "Note read successfully"
}
```

<details>
<summary>🔧 <strong>Example Usage</strong></summary>

```bash
# cURL
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"read_note","parameters":{"filename":"AGENTS.md"}}'

# PowerShell
$body = '{"tool_name":"read_note","parameters":{"filename":"AGENTS.md"}}'
Invoke-RestMethod -Uri "http://localhost:3010/tools/execute" -Method Post -Body $body -ContentType "application/json"
```

</details>

### 🔍 Search Vault

Searches for content within the vault.

**Tool Name:** `search_vault`

**Parameters:**
```json
{
  "query": "string (required)"
}
```

**Response:**
```json
{
  "success": true,
  "result": [
    {
      "filename": "AGENTS.md",
      "content": "Found content matching query",
      "score": 0.95
    }
  ],
  "message": "Found 1 results for 'query'"
}
```

<details>
<summary>🔧 <strong>Example Usage</strong></summary>

```bash
# cURL
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"search_vault","parameters":{"query":"test"}}'

# PowerShell
$body = '{"tool_name":"search_vault","parameters":{"query":"test"}}'
Invoke-RestMethod -Uri "http://localhost:3010/tools/execute" -Method Post -Body $body -ContentType "application/json"
```

</details>

### 🤖 Semantic Search

Performs AI-powered semantic search using Ollama.

**Tool Name:** `semantic_search`

**Parameters:**
```json
{
  "query": "string (required)",
  "limit": "number (optional, default: 10)"
}
```

**Response:**
```json
{
  "success": true,
  "result": [
    {
      "filename": "AGENTS.md",
      "content": "Semantically relevant content",
      "similarity": 0.87,
      "embedding": [0.1, 0.2, ...]
    }
  ],
  "message": "Found 1 semantically similar results"
}
```

<details>
<summary>🔧 <strong>Example Usage</strong></summary>

```bash
# cURL
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"semantic_search","parameters":{"query":"artificial intelligence","limit":5}}'

# PowerShell
$body = '{"tool_name":"semantic_search","parameters":{"query":"artificial intelligence","limit":5}}'
Invoke-RestMethod -Uri "http://localhost:3010/tools/execute" -Method Post -Body $body -ContentType "application/json"
```

</details>

### ✏️ Create Note

Creates a new note in the vault.

**Tool Name:** `create_note`

**Parameters:**
```json
{
  "filename": "string (required)",
  "content": "string (required)",
  "tags": "array (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "filename": "new-note.md",
    "path": "new-note.md",
    "size": 150,
    "created": "2025-09-17T05:40:56-03:00"
  },
  "message": "Note created successfully"
}
```

<details>
<summary>🔧 <strong>Example Usage</strong></summary>

```bash
# cURL
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"create_note","parameters":{"filename":"test-note.md","content":"# Test Note\nThis is a test note.","tags":["test","example"]}}'

# PowerShell
$body = '{"tool_name":"create_note","parameters":{"filename":"test-note.md","content":"# Test Note\nThis is a test note.","tags":["test","example"]}}'
Invoke-RestMethod -Uri "http://localhost:3010/tools/execute" -Method Post -Body $body -ContentType "application/json"
```

</details>

### 🏷️ Bulk Tag

Applies tags to multiple notes.

**Tool Name:** `bulk_tag`

**Parameters:**
```json
{
  "filenames": "array (required)",
  "tags": "array (required)",
  "action": "string (optional, add|remove|replace)"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "processed": 3,
    "successful": 3,
    "failed": 0,
    "details": [
      {
        "filename": "note1.md",
        "status": "success",
        "tags": ["tag1", "tag2"]
      }
    ]
  },
  "message": "Successfully processed 3 files"
}
```

<details>
<summary>🔧 <strong>Example Usage</strong></summary>

```bash
# cURL
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"bulk_tag","parameters":{"filenames":["note1.md","note2.md"],"tags":["important","project"],"action":"add"}}'

# PowerShell
$body = '{"tool_name":"bulk_tag","parameters":{"filenames":["note1.md","note2.md"],"tags":["important","project"],"action":"add"}}'
Invoke-RestMethod -Uri "http://localhost:3010/tools/execute" -Method Post -Body $body -ContentType "application/json"
```

</details>

### 🔗 Analyze Links

Analyzes relationships and links between notes.

**Tool Name:** `analyze_links`

**Parameters:**
```json
{
  "filename": "string (optional)",
  "depth": "number (optional, default: 2)"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "filename": "AGENTS.md",
    "links": [
      {
        "target": "other-note.md",
        "type": "internal",
        "context": "Link context text"
      }
    ],
    "backlinks": [
      {
        "source": "referring-note.md",
        "context": "Reference context"
      }
    ],
    "graph": {
      "nodes": [...],
      "edges": [...]
    }
  },
  "message": "Link analysis completed"
}
```

<details>
<summary>🔧 <strong>Example Usage</strong></summary>

```bash
# cURL
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"analyze_links","parameters":{"filename":"AGENTS.md","depth":3}}'

# PowerShell
$body = '{"tool_name":"analyze_links","parameters":{"filename":"AGENTS.md","depth":3}}'
Invoke-RestMethod -Uri "http://localhost:3010/tools/execute" -Method Post -Body $body -ContentType "application/json"
```

</details>

---

## 📊 Response Formats

### ✅ Success Response

```json
{
  "success": true,
  "result": {
    // Tool-specific data
  },
  "message": "Operation completed successfully"
}
```

### ❌ Error Response

```json
{
  "success": false,
  "error": {
    "code": "TOOL_NOT_FOUND",
    "message": "Tool 'invalid_tool' not found",
    "details": "Available tools: list_files_in_vault, read_note, search_vault, semantic_search, create_note, bulk_tag, analyze_links"
  }
}
```

---

## ❌ Error Handling

### 🚨 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `TOOL_NOT_FOUND` | 400 | Tool name not recognized |
| `INVALID_PARAMETERS` | 400 | Missing or invalid parameters |
| `VAULT_CONNECTION_ERROR` | 500 | Cannot connect to Obsidian vault |
| `FILE_NOT_FOUND` | 404 | Requested file does not exist |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `INTERNAL_ERROR` | 500 | Internal server error |

### 🔧 Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional error details (optional)"
  }
}
```

---

## 📝 Examples

### 🔄 Complete Workflow Example

<details>
<summary>📋 <strong>Complete Workflow</strong></summary>

```bash
# 1. Check server health
curl http://localhost:3010/health

# 2. List available tools
curl http://localhost:3010/tools/list

# 3. List files in vault
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"list_files_in_vault","parameters":{}}'

# 4. Read a specific note
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"read_note","parameters":{"filename":"AGENTS.md"}}'

# 5. Search for content
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"search_vault","parameters":{"query":"test"}}'

# 6. Create a new note
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"create_note","parameters":{"filename":"api-test.md","content":"# API Test\nThis note was created via API.","tags":["api","test"]}}'
```

</details>

### 🐍 Python Example

<details>
<summary>🐍 <strong>Python Client</strong></summary>

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:3010"

# Health check
def check_health():
    response = requests.get(f"{BASE_URL}/health")
    return response.json()

# List tools
def list_tools():
    response = requests.get(f"{BASE_URL}/tools/list")
    return response.json()

# Execute tool
def execute_tool(tool_name, parameters):
    payload = {
        "tool_name": tool_name,
        "parameters": parameters
    }
    response = requests.post(
        f"{BASE_URL}/tools/execute",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    return response.json()

# Example usage
if __name__ == "__main__":
    # Check health
    health = check_health()
    print("Health:", health)
    
    # List files
    files = execute_tool("list_files_in_vault", {})
    print("Files:", files)
    
    # Read note
    note = execute_tool("read_note", {"filename": "AGENTS.md"})
    print("Note:", note)
```

</details>

### 🔧 PowerShell Example

<details>
<summary>🔧 <strong>PowerShell Client</strong></summary>

```powershell
# Base URL
$BaseUrl = "http://localhost:3010"

# Health check
function Get-Health {
    return Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get
}

# List tools
function Get-Tools {
    return Invoke-RestMethod -Uri "$BaseUrl/tools/list" -Method Get
}

# Execute tool
function Invoke-Tool {
    param(
        [string]$ToolName,
        [hashtable]$Parameters
    )
    
    $body = @{
        tool_name = $ToolName
        parameters = $Parameters
    } | ConvertTo-Json
    
    return Invoke-RestMethod -Uri "$BaseUrl/tools/execute" -Method Post -Body $body -ContentType "application/json"
}

# Example usage
Write-Host "Health: $(Get-Health)"
Write-Host "Files: $(Invoke-Tool -ToolName 'list_files_in_vault' -Parameters @{})"
Write-Host "Note: $(Invoke-Tool -ToolName 'read_note' -Parameters @{filename='AGENTS.md'})"
```

</details>

---

## 🚀 Quick Start

### ⚡ Test API Endpoints

```bash
# 1. Start the server
go run cmd/server/main.go

# 2. Test health endpoint
curl http://localhost:3010/health

# 3. Test tools list
curl http://localhost:3010/tools/list

# 4. Test tool execution
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"list_files_in_vault","parameters":{}}'
```

### 🔧 Interactive Testing

Use the provided scripts for interactive testing:

```bash
# Test all endpoints
.\TEST_ALL.bat

# Interactive CLI
.\INTERACTIVE_CLI.bat

# Verify real data integration
.\VERIFY_REAL_DATA.bat
```

---

<div align="center">

**🔧 API Reference Documentation Complete! 🔧**

[![API](https://img.shields.io/badge/API-✅%20Documented-blue?style=for-the-badge)](#)
[![Examples](https://img.shields.io/badge/Examples-✅%20Complete-green?style=for-the-badge)](#)
[![Real Data](https://img.shields.io/badge/Real%20Data-✅%20Working-orange?style=for-the-badge)](#)

**CENTRALIZED REPORTS & CHANGELOG SYSTEM COMPLETE!**

</div>

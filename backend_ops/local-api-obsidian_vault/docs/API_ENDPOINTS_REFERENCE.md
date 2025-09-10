# 🚀 Complete API Endpoints & MCP Tools Reference

## 📋 Quick Access Guide

### 🌐 Service URLs
- **Vault API**: `http://localhost:8080` - Main API server
- **Obsidian API**: `http://localhost:27123` - Direct Obsidian interface  
- **n8n Workflows**: `http://localhost:5678` - Automation engine
- **API Documentation**: `http://localhost:8080/docs` - Interactive docs
- **Grafana Monitoring**: `http://localhost:3000` - System dashboards

### 🔑 Authentication
All protected endpoints require JWT Bearer token:
```bash
Authorization: Bearer <your_jwt_token>
```

---

## 🎯 Core Vault API Endpoints

### 📊 System Health & Status

#### Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "services": {
    "obsidian_api": "healthy",
    "vault_path": "/vault",
    "api_version": "2.0.0"
  },
  "local_first": {
    "operations": {"pending": 0, "completed": 156, "failed": 2},
    "files": {"total": 1247, "synced": 1245, "unsynced": 2}
  },
  "mcp_tools": {
    "available": 15,
    "tools": ["read_file", "write_file", "search_content", ...]
  }
}
```

#### Sync Status
```http
GET /api/v1/sync/status
Authorization: Bearer <token>
```

---

### 📝 Note Management

#### List Notes
```http
GET /api/v1/notes?folder=projects&limit=50
Authorization: Bearer <token>
```

#### Create Note
```http
POST /api/v1/notes
Authorization: Bearer <token>
Content-Type: application/json

{
  "path": "projects/new-project.md",
  "content": "# New Project\n\nProject description...",
  "tags": ["project", "planning"],
  "metadata": {"priority": "high"}
}
```

#### Read Note
```http
GET /api/v1/notes/projects/project-name.md
Authorization: Bearer <token>
```

#### Update Note
```http
PUT /api/v1/notes/projects/project-name.md
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "# Updated Project\n\nNew content...",
  "tags": ["project", "active"]
}
```

#### Delete Note
```http
DELETE /api/v1/notes/projects/project-name.md
Authorization: Bearer <token>
```

---

### 🔍 Search Operations

#### Text Search
```http
POST /api/v1/search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "machine learning concepts",
  "limit": 10,
  "semantic": false
}
```

#### Semantic Search
```http
POST /api/v1/search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "artificial intelligence applications",
  "limit": 5,
  "semantic": true
}
```

**Response:**
```json
{
  "results": [
    {
      "path": "research/ai-applications.md",
      "score": 0.89,
      "snippet": "Machine learning algorithms...",
      "metadata": {"tags": ["ai", "research"]}
    }
  ],
  "query_time": 0.045,
  "total_results": 12
}
```

---

### 🤖 AI Operations

#### Process Content with AI
```http
POST /api/v1/ai/process
Authorization: Bearer <token>
Content-Type: application/json

{
  "operation": "summarize",
  "content": "Long article content...",
  "parameters": {"max_length": 200}
}
```

**Available Operations:**
- `summarize` - Generate content summary
- `tag` - Generate relevant tags
- `link` - Suggest internal links
- `generate` - Generate new content

---

### 🔄 Workflow Management

#### List Workflows
```http
GET /api/v1/workflows
Authorization: Bearer <token>
```

#### Trigger Workflow
```http
POST /api/v1/workflows/trigger
Authorization: Bearer <token>
Content-Type: application/json

{
  "workflow_id": "daily-processing",
  "data": {"date": "2024-01-15"},
  "async": true
}
```

---

### 🛠️ MCP Tool Interface

#### List Available Tools
```http
GET /api/v1/mcp/tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "read_file",
      "description": "Read content from a file in the vault",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {"type": "string", "description": "File path"}
        },
        "required": ["path"]
      }
    }
  ],
  "total": 15
}
```

#### Call MCP Tool
```http
POST /api/v1/mcp/tools/call
Authorization: Bearer <token>
Content-Type: application/json

{
  "tool": "read_file",
  "arguments": {
    "path": "projects/current-project.md"
  }
}
```

#### List MCP Resources
```http
GET /api/v1/mcp/resources
```

---

### 📦 Batch Operations

#### Execute Multiple Operations
```http
POST /api/v1/batch
Authorization: Bearer <token>
Content-Type: application/json

{
  "operations": [
    {
      "type": "create_note",
      "data": {"path": "batch/note1.md", "content": "Content 1"}
    },
    {
      "type": "mcp_tool",
      "tool": "generate_tags",
      "arguments": {"path": "existing/note.md"}
    }
  ],
  "atomic": true
}
```

---

## 🔧 Available MCP Tools

### 📁 File Operations

#### read_file
```json
{
  "tool": "read_file",
  "arguments": {"path": "notes/example.md"}
}
```

#### write_file
```json
{
  "tool": "write_file",
  "arguments": {
    "path": "notes/new-note.md",
    "content": "# New Note\n\nContent here..."
  }
}
```

#### list_files
```json
{
  "tool": "list_files",
  "arguments": {
    "path": "research/",
    "pattern": "*.md"
  }
}
```

### 🔍 Search Operations

#### search_content
```json
{
  "tool": "search_content",
  "arguments": {
    "query": "machine learning",
    "semantic": true,
    "limit": 5
  }
}
```

### 📝 Note Operations

#### create_daily_note
```json
{
  "tool": "create_daily_note",
  "arguments": {
    "date": "2024-01-15",
    "template": "daily"
  }
}
```

#### extract_links
```json
{
  "tool": "extract_links",
  "arguments": {"path": "research/paper.md"}
}
```

### 🤖 AI Operations

#### summarize_note
```json
{
  "tool": "summarize_note",
  "arguments": {
    "path": "meetings/long-meeting.md",
    "max_length": 150
  }
}
```

#### generate_tags
```json
{
  "tool": "generate_tags",
  "arguments": {
    "path": "articles/tech-article.md",
    "max_tags": 5
  }
}
```

### 🔄 Workflow Operations

#### trigger_workflow
```json
{
  "tool": "trigger_workflow",
  "arguments": {
    "workflow_id": "content-curation",
    "data": {"note_path": "inbox/new-article.md"}
  }
}
```

---

## 📝 Obsidian Direct API

### 🗂️ File Operations
```http
# List files
GET /files?path=daily

# Read file
GET /files/daily/2024-01-15.md

# Create file
POST /files
{
  "path": "new-note.md",
  "content": "# New Note"
}

# Update file
PUT /files/existing-note.md
{
  "content": "Updated content"
}

# Delete file
DELETE /files/note-to-delete.md
```

### 🏛️ Vault Operations
```http
# Get vault info
GET /vault/info

# Search vault
POST /vault/search
{
  "query": "search term",
  "case_sensitive": false
}

# Execute command
POST /vault/command
{
  "command": "app:open-vault"
}
```

---

## 🌐 WebSocket Real-time Updates

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Vault update:', update);
};
```

### Message Types
- `sync_status` - Synchronization status updates
- `note_created` - New note created
- `note_updated` - Note content changed
- `workflow_completed` - Workflow execution finished

---

## 🚨 Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid file path provided",
    "details": {
      "field": "path",
      "reason": "Path contains invalid characters"
    },
    "timestamp": "2024-01-15T12:00:00Z",
    "request_id": "req_123456"
  }
}
```

### Common Error Codes
- `AUTHENTICATION_FAILED` - Invalid/expired token
- `AUTHORIZATION_DENIED` - Insufficient permissions
- `VALIDATION_ERROR` - Invalid request parameters
- `FILE_NOT_FOUND` - Requested file doesn't exist
- `VAULT_UNAVAILABLE` - Vault path not accessible
- `SERVICE_UNAVAILABLE` - Required service is down
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server-side error

---

## 📊 Rate Limits

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Standard endpoints | 100 requests | 1 minute |
| AI operations | 20 requests | 1 minute |
| Search operations | 50 requests | 1 minute |
| Batch operations | 10 requests | 1 minute |
| MCP tool calls | 30 requests | 1 minute |

---

## 🧪 Testing Examples

### PowerShell Examples
```powershell
# Test health
Invoke-RestMethod -Uri "http://localhost:8080/health"

# List MCP tools
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools"

# Search notes
$body = @{query="machine learning"; limit=5} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/search" -Method POST -Body $body -ContentType "application/json"

# Call MCP tool
$body = @{tool="read_file"; arguments=@{path="notes/example.md"}} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools/call" -Method POST -Body $body -ContentType "application/json"
```

### cURL Examples
```bash
# Health check
curl http://localhost:8080/health

# List notes
curl -H "Authorization: Bearer <token>" http://localhost:8080/api/v1/notes

# Create note
curl -X POST http://localhost:8080/api/v1/notes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"path":"test.md","content":"# Test Note"}'

# Call MCP tool
curl -X POST http://localhost:8080/api/v1/mcp/tools/call \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"tool":"read_file","arguments":{"path":"notes/example.md"}}'
```

---

## 🎮 CLI Usage Examples

### Launch System
```powershell
# Start all services
.\scripts\launch.ps1 -Action start

# Interactive mode
.\scripts\launch.ps1 -Interactive

# Check status
.\scripts\launch.ps1 -Action status
```

### Vault CLI Operations
```powershell
# Interactive CLI
.\scripts\vault-cli.ps1 -Interactive

# Direct commands
.\scripts\vault-cli.ps1 -Command health
.\scripts\vault-cli.ps1 -Command tools
.\scripts\vault-cli.ps1 -Command search -Query "machine learning"
.\scripts\vault-cli.ps1 -Command call -Tool read_file -Arguments @{path="notes/example.md"}
```

---

## 📚 Integration Patterns

### 1. **Local-First Operations**
All write operations are queued locally first, then synchronized with remote services.

### 2. **Batch Processing**
Multiple operations can be batched together for efficiency and atomicity.

### 3. **Event-Driven Architecture**
WebSocket connections provide real-time updates for vault changes.

### 4. **AI-Enhanced Workflows**
MCP tools enable AI agents to interact directly with vault content.

### 5. **Monitoring Integration**
All operations are logged and metrics are exposed for monitoring.

---

This comprehensive reference provides everything needed to interact with the Obsidian Vault AI system through its various APIs and interfaces. Use the PowerShell scripts for easy system management and the MCP tools for advanced AI-driven operations.
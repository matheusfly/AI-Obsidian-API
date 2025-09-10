# Complete API Reference Guide

## Overview
This guide provides comprehensive documentation for all API endpoints in the Obsidian Vault AI automation system, including REST APIs, MCP tool calling, and integration patterns.

## Base URLs
- **Vault API**: `http://localhost:8080`
- **Obsidian API**: `http://localhost:27123`
- **n8n Workflows**: `http://localhost:5678`
- **Monitoring**: `http://localhost:3000` (Grafana)

## Authentication
All API endpoints require JWT authentication:
```bash
Authorization: Bearer <your_jwt_token>
```

## Core Vault API Endpoints

### 1. Note Management

#### Create Note
```http
POST /api/v1/notes
Content-Type: application/json
Authorization: Bearer <token>

{
  "path": "projects/new-project.md",
  "content": "# New Project\n\nProject description here...",
  "tags": ["project", "planning"],
  "metadata": {
    "author": "user",
    "priority": "high"
  }
}
```

**Response:**
```json
{
  "success": true,
  "path": "projects/new-project.md",
  "operation_id": "op_123456",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Read Note
```http
GET /api/v1/notes/projects/new-project.md
Authorization: Bearer <token>
```

**Response:**
```json
{
  "path": "projects/new-project.md",
  "content": "# New Project\n\nProject description...",
  "metadata": {
    "size": 1024,
    "created": "2024-01-15T10:30:00Z",
    "modified": "2024-01-15T11:45:00Z",
    "tags": ["project", "planning"]
  },
  "links": {
    "outgoing": ["[[related-note]]"],
    "incoming": ["[[parent-project]]"]
  }
}
```

#### Update Note
```http
PUT /api/v1/notes/projects/new-project.md
Content-Type: application/json
Authorization: Bearer <token>

{
  "content": "# Updated Project\n\nUpdated content...",
  "tags": ["project", "planning", "active"],
  "merge_strategy": "replace"
}
```

#### Delete Note
```http
DELETE /api/v1/notes/projects/new-project.md
Authorization: Bearer <token>
```

#### List Notes
```http
GET /api/v1/notes?path=projects&recursive=true&limit=50&offset=0
Authorization: Bearer <token>
```

**Response:**
```json
{
  "notes": [
    {
      "path": "projects/project-1.md",
      "title": "Project 1",
      "size": 2048,
      "modified": "2024-01-15T10:30:00Z",
      "tags": ["project", "active"]
    }
  ],
  "total": 25,
  "page": 1,
  "has_more": false
}
```

### 2. Search Operations

#### Text Search
```http
POST /api/v1/search
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "machine learning concepts",
  "type": "text",
  "path": "research/",
  "limit": 10,
  "include_content": true
}
```

#### Semantic Search
```http
POST /api/v1/search
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "artificial intelligence applications",
  "type": "semantic",
  "limit": 5,
  "similarity_threshold": 0.7
}
```

**Response:**
```json
{
  "results": [
    {
      "path": "research/ai-applications.md",
      "title": "AI Applications in Healthcare",
      "score": 0.89,
      "snippet": "Machine learning algorithms are revolutionizing...",
      "metadata": {
        "tags": ["ai", "healthcare", "research"],
        "modified": "2024-01-15T09:15:00Z"
      }
    }
  ],
  "query_time": 0.045,
  "total_results": 12
}
```

### 3. AI Operations

#### Summarize Content
```http
POST /api/v1/ai/summarize
Content-Type: application/json
Authorization: Bearer <token>

{
  "path": "research/long-article.md",
  "max_length": 200,
  "style": "bullet_points"
}
```

#### Generate Tags
```http
POST /api/v1/ai/tag
Content-Type: application/json
Authorization: Bearer <token>

{
  "path": "notes/meeting-notes.md",
  "max_tags": 5,
  "existing_tags": ["meeting", "project-x"]
}
```

#### Suggest Links
```http
POST /api/v1/ai/link
Content-Type: application/json
Authorization: Bearer <token>

{
  "path": "concepts/machine-learning.md",
  "max_suggestions": 10,
  "confidence_threshold": 0.6
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "target": "algorithms/neural-networks.md",
      "confidence": 0.85,
      "reason": "Related concept: neural networks are a subset of ML",
      "anchor_text": "neural networks"
    }
  ]
}
```

#### Generate Content
```http
POST /api/v1/ai/generate
Content-Type: application/json
Authorization: Bearer <token>

{
  "prompt": "Create a daily review template",
  "type": "template",
  "parameters": {
    "sections": ["accomplishments", "challenges", "tomorrow"],
    "format": "markdown"
  }
}
```

### 4. Workflow Management

#### Trigger Workflow
```http
POST /api/v1/workflows/trigger
Content-Type: application/json
Authorization: Bearer <token>

{
  "workflow_id": "daily-processing",
  "data": {
    "date": "2024-01-15",
    "notes_path": "daily/"
  },
  "async": true
}
```

#### List Workflows
```http
GET /api/v1/workflows
Authorization: Bearer <token>
```

#### Get Workflow Status
```http
GET /api/v1/workflows/daily-processing/status
Authorization: Bearer <token>
```

### 5. System Operations

#### Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "vault_api": "up",
    "obsidian_api": "up",
    "n8n": "up",
    "database": "up",
    "vector_db": "up"
  },
  "vault": {
    "path": "/mnt/d/Nomade Milionario",
    "accessible": true,
    "note_count": 1247
  },
  "timestamp": "2024-01-15T12:00:00Z"
}
```

#### Sync Status
```http
GET /api/v1/sync/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "local_first": {
    "operations": {
      "pending": 0,
      "completed": 156,
      "failed": 2
    },
    "files": {
      "total": 1247,
      "synced": 1245,
      "unsynced": 2
    }
  },
  "last_sync": "2024-01-15T11:45:00Z"
}
```

## Obsidian Direct API Endpoints

### File Operations
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

### Vault Operations
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

## MCP Tool Calling Interface

### Available Tools

#### File Operations
```json
{
  "tool": "read_file",
  "arguments": {
    "path": "projects/current-project.md"
  }
}
```

```json
{
  "tool": "write_file",
  "arguments": {
    "path": "notes/new-note.md",
    "content": "# New Note\n\nContent here..."
  }
}
```

```json
{
  "tool": "list_files",
  "arguments": {
    "path": "research/",
    "pattern": "*.md"
  }
}
```

#### Search Operations
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

#### Note Operations
```json
{
  "tool": "create_daily_note",
  "arguments": {
    "date": "2024-01-15",
    "template": "daily"
  }
}
```

```json
{
  "tool": "extract_links",
  "arguments": {
    "path": "research/ai-paper.md"
  }
}
```

#### AI Operations
```json
{
  "tool": "summarize_note",
  "arguments": {
    "path": "meetings/long-meeting.md",
    "max_length": 150
  }
}
```

```json
{
  "tool": "generate_tags",
  "arguments": {
    "path": "articles/tech-article.md",
    "max_tags": 5
  }
}
```

#### Workflow Operations
```json
{
  "tool": "trigger_workflow",
  "arguments": {
    "workflow_id": "content-curation",
    "data": {
      "note_path": "inbox/new-article.md"
    }
  }
}
```

### MCP Tool Response Format
```json
{
  "success": true,
  "result": {
    "content": "File content here...",
    "metadata": {
      "size": 1024,
      "modified": "2024-01-15T10:30:00Z"
    }
  }
}
```

## Integration Patterns

### 1. Batch Operations
```http
POST /api/v1/batch
Content-Type: application/json
Authorization: Bearer <token>

{
  "operations": [
    {
      "type": "create_note",
      "data": {
        "path": "batch/note1.md",
        "content": "Content 1"
      }
    },
    {
      "type": "update_note",
      "data": {
        "path": "existing/note.md",
        "content": "Updated content"
      }
    }
  ],
  "atomic": true
}
```

### 2. Webhook Integration
```http
POST /api/v1/webhooks/register
Content-Type: application/json
Authorization: Bearer <token>

{
  "url": "https://your-service.com/webhook",
  "events": ["note_created", "note_updated", "workflow_completed"],
  "secret": "webhook_secret_key"
}
```

### 3. Real-time Updates (WebSocket)
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Vault update:', update);
};
```

## Error Handling

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
- `AUTHENTICATION_FAILED`: Invalid or expired token
- `AUTHORIZATION_DENIED`: Insufficient permissions
- `VALIDATION_ERROR`: Invalid request parameters
- `FILE_NOT_FOUND`: Requested file doesn't exist
- `VAULT_UNAVAILABLE`: Vault path not accessible
- `SERVICE_UNAVAILABLE`: Required service is down
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server-side error

## Rate Limiting
- **Standard endpoints**: 100 requests/minute
- **AI operations**: 20 requests/minute
- **Search operations**: 50 requests/minute
- **Batch operations**: 10 requests/minute

## SDK Examples

### Python SDK
```python
from obsidian_vault_api import VaultClient

client = VaultClient(
    base_url="http://localhost:8080",
    api_key="your_api_key"
)

# Create note
note = client.notes.create(
    path="projects/new-project.md",
    content="# New Project\n\nDescription...",
    tags=["project", "planning"]
)

# Search notes
results = client.search.semantic(
    query="machine learning concepts",
    limit=5
)

# AI operations
summary = client.ai.summarize(
    path="research/long-article.md",
    max_length=200
)
```

### JavaScript SDK
```javascript
import { VaultClient } from 'obsidian-vault-api';

const client = new VaultClient({
  baseUrl: 'http://localhost:8080',
  apiKey: 'your_api_key'
});

// Create note
const note = await client.notes.create({
  path: 'projects/new-project.md',
  content: '# New Project\n\nDescription...',
  tags: ['project', 'planning']
});

// Search notes
const results = await client.search.semantic({
  query: 'machine learning concepts',
  limit: 5
});
```

## Performance Optimization

### Caching Headers
```http
Cache-Control: max-age=300, private
ETag: "abc123def456"
Last-Modified: Mon, 15 Jan 2024 10:30:00 GMT
```

### Compression
All responses support gzip compression:
```http
Accept-Encoding: gzip, deflate
```

### Pagination
Large result sets use cursor-based pagination:
```http
GET /api/v1/notes?cursor=eyJpZCI6MTIzfQ&limit=50
```

## Monitoring and Metrics

### Health Endpoints
- `/health` - Basic health check
- `/health/detailed` - Detailed service status
- `/metrics` - Prometheus metrics
- `/debug/pprof` - Performance profiling (dev only)

### Key Metrics
- `vault_operations_total` - Total operations count
- `vault_operation_duration_seconds` - Operation latency
- `vault_notes_total` - Total notes in vault
- `api_requests_total` - API request count
- `active_connections` - Active WebSocket connections

This comprehensive API reference provides all the information needed to integrate with and extend the Obsidian Vault AI automation system.
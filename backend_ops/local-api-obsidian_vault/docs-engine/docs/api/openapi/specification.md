# OpenAPI Specification

The Obsidian Vault AI System provides a comprehensive OpenAPI 3.0 specification for all REST endpoints.

## Interactive Documentation

- **Swagger UI**: [http://localhost:8085/api/swagger](http://localhost:8085/api/swagger)
- **ReDoc**: [http://localhost:8085/api/redoc](http://localhost:8085/api/redoc)

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login user |
| POST | `/auth/refresh` | Refresh JWT token |
| POST | `/auth/logout` | Logout user |

### Vault Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/vault/files` | List vault files |
| GET | `/vault/files/{path}` | Get file content |
| POST | `/vault/files` | Create new file |
| PUT | `/vault/files/{path}` | Update file content |
| DELETE | `/vault/files/{path}` | Delete file |
| GET | `/vault/search` | Search files |

### AI Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/generate` | Generate content |
| POST | `/ai/analyze` | Analyze content |
| POST | `/ai/insights` | Get insights |
| POST | `/ai/rag` | RAG query |

### MCP Tools

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mcp/tools` | List available tools |
| POST | `/mcp/call` | Call MCP tool |
| GET | `/mcp/status` | Get MCP status |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| GET | `/status` | System status |

## Request/Response Examples

### Authentication

**Register User**
```http
POST /auth/register
Content-Type: application/json

{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Login**
```http
POST /auth/login
Content-Type: application/json

{
  "username": "user123",
  "password": "securepassword"
}
```

**Response**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Vault Operations

**List Files**
```http
GET /vault/files?directory=notes&limit=10
Authorization: Bearer <token>
```

**Response**
```json
{
  "files": [
    {
      "path": "notes/example.md",
      "size": 1024,
      "modified": "2024-01-01T00:00:00Z",
      "type": "file"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

**Read File**
```http
GET /vault/files/notes/example.md
Authorization: Bearer <token>
```

**Response**
```json
{
  "path": "notes/example.md",
  "content": "# Example\n\nThis is an example file.",
  "metadata": {
    "size": 1024,
    "modified": "2024-01-01T00:00:00Z",
    "created": "2024-01-01T00:00:00Z"
  }
}
```

**Create File**
```http
POST /vault/files
Authorization: Bearer <token>
Content-Type: application/json

{
  "path": "notes/new-file.md",
  "content": "# New File\n\nThis is a new file."
}
```

### AI Operations

**Generate Content**
```http
POST /ai/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt": "Write a summary of machine learning",
  "context_files": ["notes/ml-basics.md"],
  "max_tokens": 500
}
```

**Response**
```json
{
  "content": "Machine learning is a subset of artificial intelligence...",
  "tokens_used": 150,
  "model": "gpt-4",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**RAG Query**
```http
POST /ai/rag
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What is the difference between supervised and unsupervised learning?",
  "context_files": ["notes/ml-basics.md"],
  "top_k": 5
}
```

**Response**
```json
{
  "answer": "Supervised learning uses labeled data...",
  "sources": [
    {
      "file": "notes/ml-basics.md",
      "content": "Supervised learning...",
      "score": 0.95
    }
  ],
  "confidence": 0.92
}
```

### MCP Tools

**List Tools**
```http
GET /mcp/tools
Authorization: Bearer <token>
```

**Response**
```json
{
  "tools": [
    {
      "name": "filesystem",
      "description": "File system operations",
      "status": "active",
      "version": "1.0.0"
    },
    {
      "name": "github",
      "description": "GitHub repository management",
      "status": "active",
      "version": "1.0.0"
    }
  ]
}
```

**Call Tool**
```http
POST /mcp/call
Authorization: Bearer <token>
Content-Type: application/json

{
  "tool": "filesystem",
  "operation": "list_files",
  "parameters": {
    "path": "/vault/notes"
  }
}
```

**Response**
```json
{
  "result": {
    "files": ["file1.md", "file2.md"]
  },
  "tool": "filesystem",
  "operation": "list_files",
  "duration": 0.123
}
```

## Error Responses

All endpoints return structured error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "password",
      "issue": "Password must be at least 8 characters"
    },
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTHENTICATION_FAILED` | Invalid credentials |
| `AUTHORIZATION_FAILED` | Insufficient permissions |
| `FILE_NOT_FOUND` | File does not exist |
| `TOOL_ERROR` | MCP tool execution failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

## Rate Limiting

API requests are rate limited:

- **Authentication**: 5 requests per minute
- **Vault Operations**: 100 requests per minute
- **AI Operations**: 20 requests per minute
- **MCP Tools**: 50 requests per minute

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## WebSocket API

The system also provides WebSocket endpoints for real-time communication:

- **Connection**: `ws://localhost:8085/ws`
- **Authentication**: Include JWT token in query parameter
- **Message Format**: JSON

See [WebSocket documentation](/docs/api/websocket/real-time) for details.

## SDKs

Official SDKs are available for:

- **Python**: [Installation guide](/docs/api/sdks/python)
- **JavaScript/Node.js**: Coming soon
- **Go**: Coming soon
- **Rust**: Coming soon

## OpenAPI Schema

The complete OpenAPI 3.0 schema is available at:

- **JSON**: [http://localhost:8085/openapi.json](http://localhost:8085/openapi.json)
- **YAML**: [http://localhost:8085/openapi.yaml](http://localhost:8085/openapi.yaml)

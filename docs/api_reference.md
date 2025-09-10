# API Reference

This document provides detailed information about all available API endpoints.

## Base URL
```
http://localhost:8000
```

## Obsidian API Endpoints

### List Vaults
```
GET /vaults
```

**Description**: List all available Obsidian vaults.

**Response**:
```json
{
  "vaults": ["vault1", "vault2", "default"]
}
```

### List Files in Vault
```
GET /vault/{vault_name}/files
```

**Description**: List all files in a specific Obsidian vault.

**Parameters**:
- `vault_name` (path): Name of the vault
- `recursive` (query, boolean, optional): List files recursively
- `filter` (query, string, optional): Filter files by pattern

**Response**:
```json
{
  "files": ["Notes/Example.md", "Research/Topic.md"],
  "cursor": "optional_pagination_cursor"
}
```

### Read Note
```
GET /vault/{vault_name}/file/{path}
```

**Description**: Read the content of a specific note.

**Parameters**:
- `vault_name` (path): Name of the vault
- `path` (path): Path to the note

**Response**:
```json
{
  "path": "Notes/Example.md",
  "content": "# Example Note\n\nThis is an example note.",
  "_hash": "sha256_hash_of_content"
}
```

### Create/Update Note
```
PUT /vault/{vault_name}/file/{path}
```

**Description**: Create or update a note in the vault.

**Parameters**:
- `vault_name` (path): Name of the vault
- `path` (path): Path to the note

**Request Body**:
```json
{
  "path": "Notes/Example.md",
  "content": "# Example Note\n\nThis is an example note.",
  "dry_run": true,
  "if_match": "optional_hash_for_conflict_detection",
  "mode": "upsert"
}
```

**Response**:
```json
{
  "status": "success",
  "dry_run": true,
  "hash": "sha256_hash_of_content"
}
```

### Patch Note
```
PATCH /vault/{vault_name}/file/{path}
```

**Description**: Patch content in a note.

**Parameters**:
- `vault_name` (path): Name of the vault
- `path` (path): Path to the note

**Request Body**:
```json
{
  "patch_ops": [
    {
      "op": "append",
      "content": "\n## New Section\n\nAdditional content",
      "heading": "New Section"
    }
  ]
}
```

**Response**:
```json
{
  "status": "success"
}
```

### Delete Note
```
DELETE /vault/{vault_name}/file/{path}
```

**Description**: Delete a note from the vault.

**Parameters**:
- `vault_name` (path): Name of the vault
- `path` (path): Path to the note

**Response**:
```json
{
  "status": "success"
}
```

### Get Daily Note
```
GET /periodic/daily/{vault_name}
```

**Description**: Get or create a daily note.

**Parameters**:
- `vault_name` (path): Name of the vault
- `date` (query, string, optional): Date in YYYY-MM-DD format

**Response**:
```json
{
  "path": "Daily/2023-10-15.md",
  "content": "# October 15, 2023\n\n## Today's Tasks\n",
  "_hash": "sha256_hash_of_content"
}
```

### Simple Search
```
POST /search/simple
```

**Description**: Perform a simple search across notes.

**Request Body**:
```json
{
  "query": "search terms"
}
```

**Response**:
```json
{
  "results": [
    {
      "path": "Notes/Example.md",
      "content": "# Example Note\n\nThis note contains search terms.",
      "score": 0.95
    }
  ]
}
```

## MCP Tools Endpoints

### List MCP Tools
```
GET /mcp/tools
```

**Description**: List all available MCP tools.

**Response**:
```json
{
  "tools": [
    {
      "name": "obsidian_list_files",
      "description": "List files in an Obsidian vault",
      "parameters": {
        "type": "object",
        "properties": {
          "vault": {
            "type": "string",
            "description": "Name of the vault"
          }
        },
        "required": ["vault"]
      }
    }
  ]
}
```

### Execute MCP Tool
```
POST /mcp/tools/execute
```

**Description**: Execute an MCP tool.

**Request Body**:
```json
{
  "tool_name": "obsidian_read_note",
  "parameters": {
    "vault": "default",
    "path": "Notes/Example.md"
  }
}
```

**Response**:
```json
{
  "result": {
    "path": "Notes/Example.md",
    "content": "# Example Note\n\nThis is an example note.",
    "_hash": "sha256_hash_of_content"
  }
}
```

## Indexing Endpoints

### Index Vault
```
POST /index/vault
```

**Description**: Index all markdown files in the vault for search.

**Response**:
```json
{
  "indexed_documents": 42
}
```

## Search Endpoints

### Hybrid Search
```
POST /search/hybrid
```

**Description**: Perform hybrid search combining vector and graph-based retrieval.

**Request Body**:
```json
{
  "query": "search terms",
  "k": 10,
  "filters": {
    "path": "Notes/*"
  }
}
```

**Response**:
```json
{
  "results": {
    "ids": [["Notes/Example.md::Introduction"]],
    "distances": [[0.25]],
    "metadatas": [[{"path": "Notes/Example.md", "heading": "Introduction"}]],
    "documents": [["# Introduction\n\nThis note introduces..."]]
  }
}
```

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request**:
```json
{
  "error": "Invalid request parameters"
}
```

**404 Not Found**:
```json
{
  "error": "Resource not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal server error"
}
```

## Authentication

Currently, the API does not implement authentication. In a production environment, you should:

1. Add authentication middleware to the FastAPI application
2. Implement API key or OAuth2 authentication
3. Secure the endpoints appropriately

## Rate Limiting

Currently, the API does not implement rate limiting. In a production environment, you should:

1. Add rate limiting middleware
2. Configure appropriate limits for different endpoints
3. Implement retry logic in clients

## CORS

The API includes basic CORS configuration. For production use, you should:

1. Configure specific origins that are allowed to access the API
2. Set appropriate CORS headers
3. Implement CSRF protection if needed
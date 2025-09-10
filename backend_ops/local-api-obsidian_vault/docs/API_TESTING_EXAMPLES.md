# 🧪 API Testing Examples - Complete Reference

## 🚀 Getting Started

### 1. Set Your API Key
```bash
# Set your API key as environment variable
export API_KEY="your_obsidian_api_key_here"

# Or replace in each command
API_KEY="your_obsidian_api_key_here"
```

### 2. Base URLs
```bash
VAULT_API="http://localhost:8080"
OBSIDIAN_API="http://localhost:27123"
N8N_API="http://localhost:5678"
```

## 📋 Core API Testing

### Health Checks
```bash
# Vault API health
curl $VAULT_API/health

# Obsidian API health
curl $OBSIDIAN_API/health

# n8n health (if accessible)
curl $N8N_API/health
```

### API Status and Info
```bash
# Get API information
curl $VAULT_API/

# Expected response:
{
  "message": "Obsidian Vault AI API",
  "version": "1.0.0",
  "status": "operational",
  "endpoints": {
    "notes": "/api/v1/notes",
    "search": "/api/v1/search",
    "ai": "/api/v1/ai",
    "health": "/health",
    "docs": "/docs"
  }
}
```

## 📝 Note Management

### List Notes
```bash
# List all notes
curl -H "Authorization: Bearer $API_KEY" \
     "$VAULT_API/api/v1/notes"

# List notes with limit
curl -H "Authorization: Bearer $API_KEY" \
     "$VAULT_API/api/v1/notes?limit=10"

# List notes in specific folder
curl -H "Authorization: Bearer $API_KEY" \
     "$VAULT_API/api/v1/notes?folder=daily"
```

### Create Notes
```bash
# Create a simple note
curl -X POST "$VAULT_API/api/v1/notes" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "test/api-created-note.md",
    "content": "# API Created Note\n\nThis note was created via the API!\n\n## Features\n- API integration\n- Automated creation\n- Markdown support",
    "tags": ["api", "test", "automation"]
  }'

# Create daily note
TODAY=$(date +%Y-%m-%d)
curl -X POST "$VAULT_API/api/v1/notes" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"path\": \"daily/${TODAY}.md\",
    \"content\": \"# Daily Note - ${TODAY}\n\n## Goals\n- [ ] Complete API testing\n- [ ] Review system status\n\n## Notes\n\n## Reflections\n\",
    \"tags\": [\"daily\", \"$(date +%Y)\", \"$(date +%B)\"]
  }"

# Create meeting note
TIMESTAMP=$(date +%Y%m%d-%H%M)
curl -X POST "$VAULT_API/api/v1/notes" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"path\": \"meetings/meeting-${TIMESTAMP}.md\",
    \"content\": \"# Meeting - $(date +%Y-%m-%d)\n\n## Attendees\n- \n\n## Agenda\n1. \n\n## Notes\n\n## Action Items\n- [ ] \n\n## Next Steps\n\",
    \"tags\": [\"meeting\", \"work\"]
  }"

# Create project note
curl -X POST "$VAULT_API/api/v1/notes" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "projects/obsidian-automation.md",
    "content": "# Obsidian Automation Project\n\n## Overview\nBuilding a complete AI-powered automation system for Obsidian.\n\n## Components\n- FastAPI backend\n- n8n workflows\n- AI agents\n- Vector database\n\n## Status\n- [x] API development\n- [ ] AI integration\n- [ ] Testing\n\n## Resources\n- [Documentation](./docs/)\n- [GitHub Repo](https://github.com/)\n",
    "tags": ["project", "obsidian", "automation", "ai"]
  }'
```

### Read Notes
```bash
# Read a specific note
curl -H "Authorization: Bearer $API_KEY" \
     "$VAULT_API/api/v1/notes/test/api-created-note.md"

# Read daily note
TODAY=$(date +%Y-%m-%d)
curl -H "Authorization: Bearer $API_KEY" \
     "$VAULT_API/api/v1/notes/daily/${TODAY}.md"

# Read with error handling
curl -H "Authorization: Bearer $API_KEY" \
     "$VAULT_API/api/v1/notes/nonexistent.md" \
     -w "HTTP Status: %{http_code}\n"
```

## 🔍 Search Operations

### Basic Search
```bash
# Simple text search
curl -X POST "$VAULT_API/api/v1/search" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "API",
    "limit": 5
  }'

# Search with semantic flag
curl -X POST "$VAULT_API/api/v1/search" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "automation",
    "limit": 10,
    "semantic": true
  }'

# Search for daily notes
curl -X POST "$VAULT_API/api/v1/search" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "daily",
    "limit": 7
  }'
```

### Advanced Search Examples
```bash
# Search for meeting notes
curl -X POST "$VAULT_API/api/v1/search" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "meeting",
    "limit": 10
  }'

# Search for project-related content
curl -X POST "$VAULT_API/api/v1/search" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "project",
    "limit": 15
  }'
```

## 🤖 AI Processing

### AI Operations
```bash
# Summarize content
curl -X POST "$VAULT_API/api/v1/ai/process" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "summarize",
    "content": "This is a long document about artificial intelligence and machine learning. It covers various topics including neural networks, deep learning, natural language processing, and computer vision. The document explains how these technologies are being used in various industries and their potential future applications.",
    "parameters": {
      "max_length": 100
    }
  }'

# Generate tags
curl -X POST "$VAULT_API/api/v1/ai/process" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "tag",
    "content": "Today I learned about Docker containers and how they can be used to deploy applications. I also explored Kubernetes for orchestration and discovered how microservices architecture can improve scalability.",
    "parameters": {
      "max_tags": 5
    }
  }'

# Generate links/connections
curl -X POST "$VAULT_API/api/v1/ai/process" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "link",
    "content": "Machine learning algorithms require large datasets for training. Neural networks are particularly effective for image recognition tasks.",
    "parameters": {
      "context": "technology"
    }
  }'

# Generate content
curl -X POST "$VAULT_API/api/v1/ai/process" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "generate",
    "content": "Write a brief introduction to API development",
    "parameters": {
      "length": "medium",
      "style": "technical"
    }
  }'
```

## 🔄 Workflow Management

### n8n Workflows
```bash
# List available workflows
curl "$VAULT_API/api/v1/workflows"

# Expected response:
{
  "workflows": [
    {
      "id": "1",
      "name": "Daily Note Processing",
      "active": true
    },
    {
      "id": "2", 
      "name": "AI Content Analysis",
      "active": false
    }
  ]
}
```

## 🧪 Advanced Testing Scenarios

### Batch Operations
```bash
# Create multiple notes in sequence
for i in {1..5}; do
  curl -X POST "$VAULT_API/api/v1/notes" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"path\": \"test/batch-note-${i}.md\",
      \"content\": \"# Batch Note ${i}\n\nThis is batch note number ${i} created for testing.\n\n## Content\n- Item 1\n- Item 2\n- Item 3\",
      \"tags\": [\"batch\", \"test\", \"note${i}\"]
    }"
  
  echo "Created batch note $i"
  sleep 1
done
```

### Error Testing
```bash
# Test invalid API key
curl -H "Authorization: Bearer invalid_key" \
     "$VAULT_API/api/v1/notes" \
     -w "HTTP Status: %{http_code}\n"

# Test missing authorization
curl "$VAULT_API/api/v1/notes" \
     -w "HTTP Status: %{http_code}\n"

# Test invalid note path
curl -H "Authorization: Bearer $API_KEY" \
     "$VAULT_API/api/v1/notes/invalid/path/that/does/not/exist.md" \
     -w "HTTP Status: %{http_code}\n"

# Test malformed JSON
curl -X POST "$VAULT_API/api/v1/notes" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"invalid": json}' \
  -w "HTTP Status: %{http_code}\n"
```

### Performance Testing
```bash
# Measure response time
time curl -H "Authorization: Bearer $API_KEY" \
          "$VAULT_API/api/v1/notes"

# Test concurrent requests
for i in {1..10}; do
  curl -H "Authorization: Bearer $API_KEY" \
       "$VAULT_API/health" &
done
wait
```

## 📊 Direct Obsidian API Testing

### Obsidian API Endpoints
```bash
# List vaults
curl -H "Authorization: Bearer $API_KEY" \
     "$OBSIDIAN_API/vault"

# List files in vault
curl -H "Authorization: Bearer $API_KEY" \
     "$OBSIDIAN_API/vault/default/files"

# Read file directly
curl -H "Authorization: Bearer $API_KEY" \
     "$OBSIDIAN_API/vault/default/file/test/api-created-note.md"

# Create file directly
curl -X PUT "$OBSIDIAN_API/vault/default/file/direct-test.md" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: text/plain" \
  -d "# Direct API Test

This note was created directly via the Obsidian API.

## Features
- Direct file creation
- No intermediate processing
- Raw markdown content"

# Search files
curl -X POST "$OBSIDIAN_API/vault/default/search" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test",
    "limit": 5
  }'

# Get daily note
curl -H "Authorization: Bearer $API_KEY" \
     "$OBSIDIAN_API/periodic/daily/default"

# List available commands
curl -H "Authorization: Bearer $API_KEY" \
     "$OBSIDIAN_API/commands"

# Execute command
curl -X POST "$OBSIDIAN_API/command/create-daily-note" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"vault": "default"}'
```

## 🔧 Testing Scripts

### Complete Test Suite
```bash
#!/bin/bash
# complete-api-test.sh

API_KEY="your_api_key_here"
VAULT_API="http://localhost:8080"

echo "🧪 Running Complete API Test Suite..."

# Test 1: Health Check
echo "1. Testing health endpoint..."
curl -s $VAULT_API/health | jq .

# Test 2: List Notes
echo "2. Testing note listing..."
curl -s -H "Authorization: Bearer $API_KEY" \
     "$VAULT_API/api/v1/notes?limit=5" | jq .

# Test 3: Create Note
echo "3. Testing note creation..."
curl -s -X POST "$VAULT_API/api/v1/notes" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "test/automated-test.md",
    "content": "# Automated Test\n\nCreated by test suite at '$(date)'",
    "tags": ["test", "automated"]
  }' | jq .

# Test 4: Read Note
echo "4. Testing note reading..."
curl -s -H "Authorization: Bearer $API_KEY" \
     "$VAULT_API/api/v1/notes/test/automated-test.md" | jq .

# Test 5: Search
echo "5. Testing search..."
curl -s -X POST "$VAULT_API/api/v1/search" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 3}' | jq .

# Test 6: AI Processing
echo "6. Testing AI processing..."
curl -s -X POST "$VAULT_API/api/v1/ai/process" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "summarize",
    "content": "This is a test document for API testing purposes.",
    "parameters": {"max_length": 50}
  }' | jq .

echo "✅ Test suite completed!"
```

### Performance Benchmark
```bash
#!/bin/bash
# performance-test.sh

API_KEY="your_api_key_here"
VAULT_API="http://localhost:8080"

echo "📊 Running Performance Benchmark..."

# Benchmark health endpoint
echo "Testing health endpoint performance..."
time for i in {1..100}; do
  curl -s $VAULT_API/health > /dev/null
done

# Benchmark note listing
echo "Testing note listing performance..."
time for i in {1..50}; do
  curl -s -H "Authorization: Bearer $API_KEY" \
       "$VAULT_API/api/v1/notes?limit=10" > /dev/null
done

# Benchmark search
echo "Testing search performance..."
time for i in {1..20}; do
  curl -s -X POST "$VAULT_API/api/v1/search" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"query": "test", "limit": 5}' > /dev/null
done

echo "📈 Benchmark completed!"
```

## 📱 Mobile API Testing

### Mobile Endpoints (if implemented)
```bash
# Mobile health check
curl "$VAULT_API/mobile/v1/health"

# Mobile note sync
curl -X POST "$VAULT_API/mobile/v1/sync" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-device",
    "last_sync": "2024-01-01T00:00:00Z",
    "changes": []
  }'
```

## 🎯 Expected Responses

### Successful Note Creation
```json
{
  "status": "created",
  "path": "test/api-created-note.md",
  "message": "Note created successfully, AI processing started"
}
```

### Search Results
```json
{
  "query": "API",
  "results": [
    {
      "path": "test/api-created-note.md",
      "score": 0.8,
      "type": "filename_match"
    }
  ],
  "total": 1,
  "semantic": true
}
```

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "obsidian_api": "healthy",
    "vault_path": "/vault",
    "api_version": "1.0.0"
  }
}
```

This comprehensive testing guide covers all API endpoints and provides practical examples for daily operations!
---
sidebar_position: 1
---

# API Overview

The Obsidian Vault AI Automation System provides a comprehensive REST API and WebSocket interface for interacting with your vault, AI agents, and automation workflows.

## 🌐 API Endpoints

### Base URL
```
http://localhost:8080/api/v1
```

### Authentication
All API endpoints require authentication using JWT tokens or API keys.

```http
Authorization: Bearer <your-jwt-token>
# or
X-API-Key: <your-api-key>
```

## 📊 API Statistics

<div className="api-stats">
  <div className="stat-card">
    <h3>25+</h3>
    <p>REST Endpoints</p>
  </div>
  <div className="stat-card">
    <h3>15+</h3>
    <p>MCP Tools</p>
  </div>
  <div className="stat-card">
    <h3>5+</h3>
    <p>WebSocket Events</p>
  </div>
  <div className="stat-card">
    <h3>4</h3>
    <p>SDK Languages</p>
  </div>
</div>

## 🔗 Interactive API Documentation

### OpenAPI Specification
Our API is fully documented using OpenAPI 3.0 specification:

<div className="api-docs-embed">
  <iframe 
    src="http://localhost:8080/docs" 
    width="100%" 
    height="600"
    title="Interactive API Documentation"
    className="api-iframe">
  </iframe>
</div>

### Swagger UI
Access the interactive Swagger UI for testing endpoints:
- **Swagger UI**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **ReDoc**: [http://localhost:8080/redoc](http://localhost:8080/redoc)
- **OpenAPI JSON**: [http://localhost:8080/openapi.json](http://localhost:8080/openapi.json)

## 🚀 Quick API Examples

### Health Check
```bash
curl -X GET "http://localhost:8080/health" \
  -H "Authorization: Bearer your-token"
```

### Create a Note
```bash
curl -X POST "http://localhost:8080/api/v1/notes" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My New Note",
    "content": "This is the content of my note",
    "path": "notes/my-new-note.md"
  }'
```

### Search Notes
```bash
curl -X POST "http://localhost:8080/api/v1/search" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence",
    "limit": 10,
    "filters": {
      "tags": ["ai", "technology"]
    }
  }'
```

### AI Content Analysis
```bash
curl -X POST "http://localhost:8080/api/v1/ai/analyze" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your content to analyze",
    "analysis_type": "sentiment",
    "model": "gpt-4"
  }'
```

## 📋 API Categories

### 🗂️ Vault Operations
Manage your Obsidian vault files and content:

- **Notes Management**: Create, read, update, delete notes
- **File Operations**: Upload, download, organize files
- **Search & Discovery**: Semantic and keyword search
- **Metadata Management**: Tags, links, and properties

### 🤖 AI Operations
Leverage AI capabilities for content processing:

- **Content Analysis**: Sentiment, topics, entities extraction
- **Content Generation**: AI-assisted writing and editing
- **Knowledge Synthesis**: Extract insights from content
- **Automated Tagging**: Intelligent content categorization

### 🔄 Workflow Operations
Control automation workflows and agents:

- **Workflow Management**: Create, start, stop workflows
- **Agent Control**: Configure and monitor AI agents
- **Task Scheduling**: Schedule automated tasks
- **Event Handling**: Webhook and event processing

### 📊 Monitoring Operations
Monitor system health and performance:

- **System Health**: Health checks and status monitoring
- **Performance Metrics**: API performance and usage stats
- **Log Management**: Access and search system logs
- **Alert Management**: Configure and manage alerts

## 🔌 WebSocket API

Real-time communication for live updates:

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');
ws.onopen = () => {
  console.log('Connected to WebSocket');
};
```

### Events
- **File Changes**: Real-time file modification notifications
- **AI Processing**: Live AI agent processing updates
- **Workflow Status**: Workflow execution status changes
- **System Alerts**: Real-time system alerts and notifications

## 🛠️ MCP (Model Context Protocol) Tools

Access powerful tools through the MCP interface:

### Core Tools
- **Filesystem Operations**: File and directory management
- **Web Scraping**: Extract data from websites
- **Database Queries**: Direct database access
- **API Requests**: Make HTTP requests to external APIs

### AI Tools
- **Text Generation**: Generate content using AI models
- **Summarization**: Create summaries of content
- **Translation**: Translate text between languages
- **Sentiment Analysis**: Analyze text sentiment

### Specialized Tools
- **Obsidian Operations**: Direct Obsidian vault manipulation
- **Vector Search**: Semantic search capabilities
- **Workflow Automation**: Trigger and control workflows
- **Monitoring Alerts**: System monitoring and alerting

## 📱 SDKs

Official SDKs for multiple programming languages:

### Python SDK
```python
from obsidian_vault_ai import VaultClient

client = VaultClient(api_key="your-api-key")
note = client.notes.create(
    title="My Note",
    content="Note content",
    path="notes/my-note.md"
)
```

### JavaScript/TypeScript SDK
```typescript
import { VaultClient } from '@obsidian-vault-ai/client';

const client = new VaultClient({ apiKey: 'your-api-key' });
const note = await client.notes.create({
  title: 'My Note',
  content: 'Note content',
  path: 'notes/my-note.md'
});
```

### PowerShell SDK
```powershell
Import-Module ObsidianVaultAI

$client = New-VaultClient -ApiKey "your-api-key"
$note = New-Note -Title "My Note" -Content "Note content" -Path "notes/my-note.md"
```

## 🔒 Authentication & Security

### Authentication Methods
1. **JWT Tokens**: Stateless authentication with configurable expiration
2. **API Keys**: Long-lived keys for service-to-service communication
3. **OAuth 2.0**: Integration with external identity providers

### Security Features
- **Rate Limiting**: Prevent API abuse with configurable limits
- **CORS Support**: Cross-origin resource sharing configuration
- **Input Validation**: Comprehensive request validation
- **Audit Logging**: Complete audit trail of API usage

### Rate Limits
- **Standard**: 100 requests per minute
- **Burst**: 20 requests per 10 seconds
- **AI Operations**: 10 requests per minute
- **File Operations**: 50 requests per minute

## 📈 Performance & Monitoring

### Response Times
- **Health Check**: < 50ms
- **Note Operations**: < 200ms
- **Search Operations**: < 500ms
- **AI Operations**: < 2000ms

### Monitoring Endpoints
- **Health**: `/health` - System health status
- **Metrics**: `/metrics` - Prometheus metrics
- **Status**: `/status` - Detailed system status
- **Logs**: `/logs` - System logs access

## 🧪 Testing

### Test Environment
- **Base URL**: `http://localhost:8080`
- **Test Data**: Sandbox environment with sample data
- **Rate Limits**: Higher limits for testing

### Testing Tools
- **Postman Collection**: Pre-configured API tests
- **Curl Examples**: Command-line testing examples
- **SDK Tests**: Unit and integration tests for SDKs
- **Load Testing**: Performance and stress testing tools

## 📚 Additional Resources

- **[REST API Reference](/docs/api/rest/authentication)**: Complete REST API documentation
- **[WebSocket API](/docs/api/websocket/real-time)**: Real-time API documentation
- **[MCP Tools](/docs/api/mcp/overview)**: Model Context Protocol tools
- **[SDKs](/docs/api/sdks/python)**: Software development kits
- **[OpenAPI Spec](/docs/api/openapi/specification)**: OpenAPI specification details

## 🆘 Support

- **API Issues**: [GitHub Issues](https://github.com/your-org/obsidian-vault-ai-system/issues)
- **Documentation**: [API Docs](https://docs.your-domain.com/api)
- **Community**: [Discord](https://discord.gg/your-discord)
- **Email**: [api-support@your-domain.com](mailto:api-support@your-domain.com)

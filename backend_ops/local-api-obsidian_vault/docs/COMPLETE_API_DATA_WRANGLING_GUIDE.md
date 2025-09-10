# 🚀 Complete API Data Wrangling & Testing Guide

## 📋 Table of Contents
1. [API Design Concepts](#api-design-concepts)
2. [Automated Testing Interfaces](#automated-testing-interfaces)
3. [Postman UI Integration](#postman-ui-integration)
4. [Swagger/OpenAPI Documentation](#swaggeropenapi-documentation)
5. [Python Backend Testing Tools](#python-backend-testing-tools)
6. [Custom AI Agent Interactions](#custom-ai-agent-interactions)
7. [Advanced API Patterns](#advanced-api-patterns)

---

## 🎯 API Design Concepts

### RESTful API Principles
```python
# FastAPI Best Practices
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="Obsidian Vault AI API",
    description="Complete backend engineering solution for AI-powered Obsidian automation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Endpoint Design Patterns
```python
# Resource-based URL design
@app.get("/api/v1/notes")
async def list_notes(
    folder: Optional[str] = None,
    limit: int = Field(50, ge=1, le=100),
    offset: int = Field(0, ge=0)
):
    """List notes with pagination and filtering"""
    pass

@app.post("/api/v1/notes")
async def create_note(note: NoteCreate):
    """Create a new note"""
    pass

@app.get("/api/v1/notes/{note_path:path}")
async def get_note(note_path: str):
    """Get specific note by path"""
    pass

@app.put("/api/v1/notes/{note_path:path}")
async def update_note(note_path: str, note: NoteUpdate):
    """Update existing note"""
    pass

@app.delete("/api/v1/notes/{note_path:path}")
async def delete_note(note_path: str):
    """Delete note"""
    pass
```

---

## 🧪 Automated Testing Interfaces

### 1. Postman UI Integration

#### Postman Collection Setup
```json
{
  "info": {
    "name": "Obsidian Vault AI API",
    "description": "Complete API testing collection",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{api_token}}",
        "type": "string"
      }
    ]
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8080",
      "type": "string"
    },
    {
      "key": "api_token",
      "value": "your_jwt_token_here",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      },
      "response": []
    }
  ]
}
```

#### Postman Test Scripts
```javascript
// Health Check Test
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
    pm.expect(jsonData).to.have.property('services');
});

// Note Creation Test
pm.test("Note created successfully", function () {
    pm.response.to.have.status(201);
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('path');
    pm.expect(jsonData).to.have.property('operation_id');
});

// Performance Test
pm.test("Response time is less than 200ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(200);
});
```

### 2. Swagger/OpenAPI Documentation

#### Enhanced OpenAPI Configuration
```python
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Obsidian Vault AI API",
        version="2.0.0",
        description="""
        ## 🚀 Complete Backend Engineering Solution
        
        This API provides comprehensive integration between AI agents and your Obsidian vault.
        
        ### Key Features:
        - **Note Management**: Full CRUD operations
        - **AI Processing**: Summarize, tag, link generation
        - **Search**: Text and semantic search
        - **Workflows**: n8n automation integration
        - **MCP Tools**: 15+ Model Context Protocol tools
        
        ### Authentication:
        All endpoints require JWT Bearer token authentication.
        
        ### Rate Limits:
        - Standard endpoints: 100 requests/minute
        - AI operations: 20 requests/minute
        - Search operations: 50 requests/minute
        """,
        routes=app.routes,
    )
    
    # Add custom extensions
    openapi_schema["info"]["x-logo"] = {
        "url": "https://obsidian.md/images/logo.png"
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8080",
            "description": "Local Development Server"
        },
        {
            "url": "https://your-domain.com",
            "description": "Production Server"
        }
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

#### Interactive API Documentation
```python
# Custom documentation endpoints
@app.get("/docs", include_in_schema=False)
async def get_docs():
    """Redirect to interactive API documentation"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

@app.get("/redoc", include_in_schema=False)
async def get_redoc():
    """Redirect to ReDoc documentation"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/redoc")

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_spec():
    """Get OpenAPI specification"""
    return app.openapi()
```

---

## 🐍 Python Backend Testing Tools

### 1. Pytest Integration
```python
# conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers():
    """Authentication headers for testing"""
    return {"Authorization": "Bearer test_token"}
```

### 2. Comprehensive Test Suite
```python
# test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestHealthEndpoint:
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data

class TestNoteManagement:
    def test_list_notes(self, auth_headers):
        """Test note listing"""
        response = client.get("/api/v1/notes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "notes" in data

    def test_create_note(self, auth_headers):
        """Test note creation"""
        note_data = {
            "path": "test/note.md",
            "content": "# Test Note\n\nThis is a test note.",
            "tags": ["test"]
        }
        response = client.post("/api/v1/notes", json=note_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["path"] == "test/note.md"

    def test_get_note(self, auth_headers):
        """Test note retrieval"""
        response = client.get("/api/v1/notes/test/note.md", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "content" in data

class TestSearchOperations:
    def test_text_search(self, auth_headers):
        """Test text search"""
        search_data = {
            "query": "test",
            "limit": 10
        }
        response = client.post("/api/v1/search", json=search_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_semantic_search(self, auth_headers):
        """Test semantic search"""
        search_data = {
            "query": "artificial intelligence",
            "semantic": True,
            "limit": 5
        }
        response = client.post("/api/v1/search", json=search_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

class TestAIProcessing:
    def test_summarize_content(self, auth_headers):
        """Test content summarization"""
        ai_data = {
            "operation": "summarize",
            "content": "This is a long document about machine learning...",
            "parameters": {"max_length": 100}
        }
        response = client.post("/api/v1/ai/process", json=ai_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data

    def test_generate_tags(self, auth_headers):
        """Test tag generation"""
        ai_data = {
            "operation": "tag",
            "content": "Document about Python programming and web development",
            "parameters": {"max_tags": 5}
        }
        response = client.post("/api/v1/ai/process", json=ai_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data

class TestMCPTools:
    def test_list_mcp_tools(self, auth_headers):
        """Test MCP tools listing"""
        response = client.get("/api/v1/mcp/tools", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data

    def test_call_mcp_tool(self, auth_headers):
        """Test MCP tool calling"""
        tool_data = {
            "tool": "read_file",
            "arguments": {"path": "test/note.md"}
        }
        response = client.post("/api/v1/mcp/tools/call", json=tool_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "result" in data

class TestErrorHandling:
    def test_invalid_auth(self):
        """Test invalid authentication"""
        response = client.get("/api/v1/notes")
        assert response.status_code == 401

    def test_not_found(self, auth_headers):
        """Test not found error"""
        response = client.get("/api/v1/notes/nonexistent.md", headers=auth_headers)
        assert response.status_code == 404

    def test_validation_error(self, auth_headers):
        """Test validation error"""
        invalid_data = {"invalid": "data"}
        response = client.post("/api/v1/notes", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422
```

### 3. Performance Testing
```python
# test_performance.py
import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestPerformance:
    def test_response_time(self, auth_headers):
        """Test API response times"""
        start_time = time.time()
        response = client.get("/health")
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 0.2  # Less than 200ms

    def test_concurrent_requests(self, auth_headers):
        """Test concurrent request handling"""
        def make_request():
            return client.get("/health")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        for response in responses:
            assert response.status_code == 200

    def test_rate_limiting(self, auth_headers):
        """Test rate limiting"""
        responses = []
        for _ in range(105):  # Exceed rate limit
            response = client.get("/api/v1/notes", headers=auth_headers)
            responses.append(response)
        
        # Check if rate limiting is applied
        rate_limited = any(r.status_code == 429 for r in responses)
        assert rate_limited
```

---

## 🤖 Custom AI Agent Interactions

### 1. MCP Tool Integration
```python
# mcp_tools.py
from typing import Dict, Any, List
import asyncio
import json

class MCPToolRegistry:
    def __init__(self):
        self.tools = {}
        self.register_default_tools()
    
    def register_default_tools(self):
        """Register default MCP tools"""
        self.tools.update({
            "read_file": {
                "description": "Read content from a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"}
                    },
                    "required": ["path"]
                },
                "handler": self._read_file
            },
            "write_file": {
                "description": "Write content to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["path", "content"]
                },
                "handler": self._write_file
            },
            "search_content": {
                "description": "Search content in vault",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "semantic": {"type": "boolean", "default": True},
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                },
                "handler": self._search_content
            }
        })
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool"""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}
        
        tool = self.tools[tool_name]
        try:
            result = await tool["handler"](**arguments)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _read_file(self, path: str) -> str:
        """Read file content"""
        # Implementation for reading file
        pass
    
    async def _write_file(self, path: str, content: str) -> str:
        """Write file content"""
        # Implementation for writing file
        pass
    
    async def _search_content(self, query: str, semantic: bool = True, limit: int = 10) -> List[Dict]:
        """Search content"""
        # Implementation for searching
        pass

# Global MCP registry
mcp_registry = MCPToolRegistry()
```

### 2. AI Agent Communication Protocol
```python
# ai_agent_protocol.py
from typing import Dict, Any, List
from pydantic import BaseModel
import json

class AgentMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str
    metadata: Dict[str, Any] = {}

class AgentRequest(BaseModel):
    message: AgentMessage
    context: Dict[str, Any] = {}
    tools: List[str] = []
    max_tokens: int = 1000

class AgentResponse(BaseModel):
    message: AgentMessage
    tool_calls: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}

class AIAgent:
    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities
        self.conversation_history = []
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """Process agent request"""
        # Add to conversation history
        self.conversation_history.append(request.message)
        
        # Process with AI model
        response_content = await self._generate_response(request)
        
        # Check for tool calls
        tool_calls = await self._extract_tool_calls(response_content)
        
        # Create response
        response_message = AgentMessage(
            role="assistant",
            content=response_content,
            timestamp=datetime.utcnow().isoformat(),
            metadata={"agent": self.name}
        )
        
        return AgentResponse(
            message=response_message,
            tool_calls=tool_calls,
            metadata={"capabilities": self.capabilities}
        )
    
    async def _generate_response(self, request: AgentRequest) -> str:
        """Generate AI response"""
        # Implementation for AI response generation
        pass
    
    async def _extract_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract tool calls from response"""
        # Implementation for tool call extraction
        pass
```

### 3. Custom Agent Endpoints
```python
# agent_endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from ai_agent_protocol import AgentRequest, AgentResponse, AIAgent

router = APIRouter(prefix="/api/v1/agents", tags=["AI Agents"])

# Available agents
agents = {
    "note_processor": AIAgent("Note Processor", ["summarize", "tag", "link"]),
    "content_curator": AIAgent("Content Curator", ["organize", "categorize", "recommend"]),
    "research_assistant": AIAgent("Research Assistant", ["search", "analyze", "synthesize"])
}

@router.post("/{agent_name}/chat")
async def chat_with_agent(
    agent_name: str,
    request: AgentRequest
) -> AgentResponse:
    """Chat with a specific AI agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents[agent_name]
    response = await agent.process_request(request)
    
    return response

@router.post("/{agent_name}/tools/call")
async def call_agent_tool(
    agent_name: str,
    tool_name: str,
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """Call a tool through an agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Use MCP registry to call tool
    result = await mcp_registry.call_tool(tool_name, arguments)
    return result

@router.get("/{agent_name}/capabilities")
async def get_agent_capabilities(agent_name: str) -> Dict[str, Any]:
    """Get agent capabilities"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents[agent_name]
    return {
        "name": agent.name,
        "capabilities": agent.capabilities,
        "available_tools": list(mcp_registry.tools.keys())
    }

@router.get("/")
async def list_agents() -> Dict[str, Any]:
    """List all available agents"""
    return {
        "agents": [
            {
                "name": name,
                "capabilities": agent.capabilities
            }
            for name, agent in agents.items()
        ]
    }
```

---

## 🔧 Advanced API Patterns

### 1. WebSocket Real-time Communication
```python
# websocket_endpoints.py
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process message and broadcast response
            response = await process_websocket_message(message)
            await manager.broadcast(json.dumps(response))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### 2. Background Task Processing
```python
# background_tasks.py
from fastapi import BackgroundTasks
import asyncio
from typing import Dict, Any

async def process_note_ai(note_path: str, operations: List[str]):
    """Background AI processing for notes"""
    for operation in operations:
        if operation == "summarize":
            await summarize_note(note_path)
        elif operation == "tag":
            await generate_tags(note_path)
        elif operation == "link":
            await suggest_links(note_path)

@app.post("/api/v1/notes")
async def create_note(
    note: NoteCreate,
    background_tasks: BackgroundTasks
):
    """Create note with background AI processing"""
    # Create note immediately
    note_path = await create_note_file(note)
    
    # Schedule background AI processing
    background_tasks.add_task(
        process_note_ai,
        note_path,
        ["summarize", "tag", "link"]
    )
    
    return {"path": note_path, "status": "created", "ai_processing": "scheduled"}
```

### 3. Caching and Performance
```python
# caching.py
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import redis.asyncio as redis

@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis_client), prefix="obsidian-api")

@app.get("/api/v1/notes")
@cache(expire=300)  # Cache for 5 minutes
async def list_notes_cached(folder: Optional[str] = None):
    """List notes with caching"""
    return await get_notes_from_vault(folder)

@app.get("/api/v1/search")
@cache(expire=60)  # Cache for 1 minute
async def search_cached(query: str, semantic: bool = True):
    """Search with caching"""
    return await perform_search(query, semantic)
```

---

## 🎨 Advanced Testing Interfaces

### 1. Insomnia REST Client
```json
{
  "_type": "export",
  "__export_format": 4,
  "__export_date": "2024-01-15T10:30:00.000Z",
  "__export_source": "insomnia.desktop.app:v2023.5.8",
  "resources": [
    {
      "_id": "req_obsidian_health",
      "parentId": "fld_obsidian_api",
      "modified": 1705312200000,
      "created": 1705312200000,
      "url": "{{ _.base_url }}/health",
      "name": "Health Check",
      "description": "Check API health status",
      "method": "GET",
      "body": {},
      "parameters": [],
      "headers": [],
      "authentication": {},
      "metaSortKey": -1705312200000,
      "isPrivate": false,
      "settingStoreCookies": true,
      "settingSendCookies": true,
      "settingDisableRenderRequestBody": false,
      "settingEncodeUrl": true,
      "settingRebuildPath": true,
      "settingFollowRedirects": "global",
      "_type": "request"
    },
    {
      "_id": "req_obsidian_create_note",
      "parentId": "fld_obsidian_api",
      "modified": 1705312200000,
      "created": 1705312200000,
      "url": "{{ _.base_url }}/api/v1/notes",
      "name": "Create Note",
      "description": "Create a new note in the vault",
      "method": "POST",
      "body": {
        "mimeType": "application/json",
        "text": "{\n  \"path\": \"test/insomnia-note.md\",\n  \"content\": \"# Insomnia Test Note\\n\\nCreated via Insomnia REST client.\\n\\n## Features\\n- API testing\\n- Automated requests\\n- Environment variables\",\n  \"tags\": [\"test\", \"insomnia\", \"api\"]\n}"
      },
      "parameters": [],
      "headers": [
        {
          "name": "Authorization",
          "value": "Bearer {{ _.api_token }}",
          "description": "JWT Bearer token"
        },
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ],
      "authentication": {},
      "metaSortKey": -1705312200000,
      "isPrivate": false,
      "settingStoreCookies": true,
      "settingSendCookies": true,
      "settingDisableRenderRequestBody": false,
      "settingEncodeUrl": true,
      "settingRebuildPath": true,
      "settingFollowRedirects": "global",
      "_type": "request"
    }
  ]
}
```

### 2. HTTPie Command Line Testing
```bash
# Install HTTPie
pip install httpie

# Basic health check
http GET localhost:8080/health

# Create note with authentication
http POST localhost:8080/api/v1/notes \
  Authorization:"Bearer your_jwt_token" \
  path="test/httpie-note.md" \
  content="# HTTPie Test Note

Created via HTTPie command line client.

## Features
- Command line testing
- JSON support
- Authentication headers" \
  tags:='["test", "httpie", "cli"]'

# Search with semantic flag
http POST localhost:8080/api/v1/search \
  Authorization:"Bearer your_jwt_token" \
  query="machine learning" \
  semantic:=true \
  limit:=5

# AI processing
http POST localhost:8080/api/v1/ai/process \
  Authorization:"Bearer your_jwt_token" \
  operation="summarize" \
  content="This is a long document about artificial intelligence and machine learning applications in various industries." \
  parameters:='{"max_length": 100}'
```

### 3. Newman (Postman CLI) Integration
```bash
# Install Newman
npm install -g newman

# Run Postman collection
newman run obsidian-api-collection.json \
  --environment obsidian-local.json \
  --reporters cli,html \
  --reporter-html-export report.html

# Run with custom data
newman run obsidian-api-collection.json \
  --environment obsidian-local.json \
  --data test-data.json \
  --iteration-count 10 \
  --delay-request 1000
```

### 4. Locust Load Testing
```python
# locustfile.py
from locust import HttpUser, task, between
import json
import random

class ObsidianAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get authentication token"""
        self.token = "your_jwt_token_here"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    @task(3)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health")
    
    @task(2)
    def list_notes(self):
        """List notes endpoint"""
        self.client.get("/api/v1/notes", headers=self.headers)
    
    @task(1)
    def create_note(self):
        """Create note endpoint"""
        note_data = {
            "path": f"test/locust-note-{random.randint(1, 1000)}.md",
            "content": f"# Locust Test Note {random.randint(1, 1000)}\n\nGenerated by Locust load testing.",
            "tags": ["test", "locust", "load-testing"]
        }
        self.client.post("/api/v1/notes", json=note_data, headers=self.headers)
    
    @task(1)
    def search_notes(self):
        """Search notes endpoint"""
        search_data = {
            "query": random.choice(["test", "api", "automation", "ai"]),
            "limit": 10
        }
        self.client.post("/api/v1/search", json=search_data, headers=self.headers)
    
    @task(1)
    def ai_processing(self):
        """AI processing endpoint"""
        ai_data = {
            "operation": "summarize",
            "content": "This is a test document for AI processing during load testing.",
            "parameters": {"max_length": 50}
        }
        self.client.post("/api/v1/ai/process", json=ai_data, headers=self.headers)

# Run with: locust -f locustfile.py --host=http://localhost:8080
```

---

## 🧠 Advanced AI Agent Patterns

### 1. Multi-Agent Collaboration
```python
# multi_agent_system.py
from typing import Dict, List, Any
import asyncio
from dataclasses import dataclass
from enum import Enum

class AgentRole(Enum):
    RESEARCHER = "researcher"
    WRITER = "writer"
    EDITOR = "editor"
    CURATOR = "curator"

@dataclass
class AgentTask:
    id: str
    role: AgentRole
    description: str
    input_data: Dict[str, Any]
    dependencies: List[str] = None
    priority: int = 1

class MultiAgentOrchestrator:
    def __init__(self):
        self.agents = {}
        self.task_queue = []
        self.completed_tasks = {}
        self.register_agents()
    
    def register_agents(self):
        """Register available agents"""
        self.agents = {
            AgentRole.RESEARCHER: AIAgent("Researcher", ["search", "analyze", "synthesize"]),
            AgentRole.WRITER: AIAgent("Writer", ["write", "structure", "format"]),
            AgentRole.EDITOR: AIAgent("Editor", ["review", "edit", "improve"]),
            AgentRole.CURATOR: AIAgent("Curator", ["organize", "categorize", "recommend"])
        }
    
    async def process_complex_request(self, request: str) -> Dict[str, Any]:
        """Process complex request using multiple agents"""
        # Break down request into tasks
        tasks = await self.decompose_request(request)
        
        # Execute tasks in dependency order
        results = await self.execute_task_pipeline(tasks)
        
        # Synthesize final result
        final_result = await self.synthesize_results(results)
        
        return final_result
    
    async def decompose_request(self, request: str) -> List[AgentTask]:
        """Decompose request into agent tasks"""
        # AI-powered task decomposition
        decomposition_prompt = f"""
        Break down this request into specific agent tasks:
        Request: {request}
        
        Available agents:
        - Researcher: Search, analyze, synthesize information
        - Writer: Write, structure, format content
        - Editor: Review, edit, improve content
        - Curator: Organize, categorize, recommend content
        
        Return tasks with dependencies and priorities.
        """
        
        # Use AI to generate task breakdown
        tasks = await self.generate_task_breakdown(decomposition_prompt)
        return tasks
    
    async def execute_task_pipeline(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """Execute tasks in dependency order"""
        results = {}
        completed = set()
        
        while len(completed) < len(tasks):
            # Find tasks ready to execute
            ready_tasks = [
                task for task in tasks
                if task.id not in completed and
                all(dep in completed for dep in (task.dependencies or []))
            ]
            
            if not ready_tasks:
                raise Exception("Circular dependency detected")
            
            # Execute ready tasks in parallel
            task_results = await asyncio.gather(*[
                self.execute_single_task(task) for task in ready_tasks
            ])
            
            # Update results and completed set
            for task, result in zip(ready_tasks, task_results):
                results[task.id] = result
                completed.add(task.id)
        
        return results
    
    async def execute_single_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a single agent task"""
        agent = self.agents[task.role]
        
        # Prepare agent request
        agent_request = AgentRequest(
            message=AgentMessage(
                role="user",
                content=task.description,
                timestamp=datetime.utcnow().isoformat()
            ),
            context=task.input_data,
            tools=agent.capabilities
        )
        
        # Process with agent
        response = await agent.process_request(agent_request)
        
        return {
            "task_id": task.id,
            "agent": task.role.value,
            "result": response.message.content,
            "tool_calls": response.tool_calls,
            "metadata": response.metadata
        }
    
    async def synthesize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from multiple agents"""
        synthesis_prompt = f"""
        Synthesize the following agent results into a coherent final response:
        
        Results: {json.dumps(results, indent=2)}
        
        Create a comprehensive, well-structured response that combines all insights.
        """
        
        # Use AI to synthesize results
        final_result = await self.generate_synthesis(synthesis_prompt)
        
        return {
            "final_result": final_result,
            "agent_results": results,
            "synthesis_metadata": {
                "total_agents": len(results),
                "synthesis_timestamp": datetime.utcnow().isoformat()
            }
        }
```

### 2. Agent Memory and Learning
```python
# agent_memory.py
from typing import Dict, List, Any
import json
from datetime import datetime, timedelta
from collections import defaultdict

class AgentMemory:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.short_term_memory = []
        self.long_term_memory = {}
        self.episodic_memory = []
        self.semantic_memory = {}
        self.procedural_memory = {}
    
    async def store_interaction(self, interaction: Dict[str, Any]):
        """Store interaction in memory"""
        # Add to short-term memory
        self.short_term_memory.append({
            "timestamp": datetime.utcnow().isoformat(),
            "interaction": interaction
        })
        
        # Process for long-term storage
        await self.process_for_long_term(interaction)
        
        # Clean up old short-term memories
        await self.cleanup_short_term()
    
    async def process_for_long_term(self, interaction: Dict[str, Any]):
        """Process interaction for long-term storage"""
        # Extract key information
        key_info = await self.extract_key_information(interaction)
        
        # Store in appropriate memory type
        if key_info["type"] == "episodic":
            self.episodic_memory.append(key_info)
        elif key_info["type"] == "semantic":
            self.update_semantic_memory(key_info)
        elif key_info["type"] == "procedural":
            self.update_procedural_memory(key_info)
    
    async def retrieve_relevant_memories(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant memories for current context"""
        relevant_memories = []
        
        # Search episodic memories
        episodic_matches = await self.search_episodic_memories(query)
        relevant_memories.extend(episodic_matches)
        
        # Search semantic memories
        semantic_matches = await self.search_semantic_memories(query)
        relevant_memories.extend(semantic_matches)
        
        # Search procedural memories
        procedural_matches = await self.search_procedural_memories(query)
        relevant_memories.extend(procedural_matches)
        
        # Rank by relevance
        ranked_memories = await self.rank_memories_by_relevance(relevant_memories, query, context)
        
        return ranked_memories[:10]  # Return top 10 most relevant
    
    async def learn_from_feedback(self, feedback: Dict[str, Any]):
        """Learn from user feedback"""
        if feedback["type"] == "positive":
            # Strengthen successful patterns
            await self.strengthen_pattern(feedback["pattern"])
        elif feedback["type"] == "negative":
            # Weaken unsuccessful patterns
            await self.weaken_pattern(feedback["pattern"])
        
        # Update procedural memory with new insights
        await self.update_procedural_memory(feedback)
```

### 3. Custom Agent Endpoints with Memory
```python
# enhanced_agent_endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from multi_agent_system import MultiAgentOrchestrator
from agent_memory import AgentMemory

router = APIRouter(prefix="/api/v1/agents", tags=["Enhanced AI Agents"])

# Global orchestrator and memory systems
orchestrator = MultiAgentOrchestrator()
agent_memories = {}

@router.post("/orchestrate")
async def orchestrate_agents(request: Dict[str, Any]) -> Dict[str, Any]:
    """Orchestrate multiple agents for complex tasks"""
    try:
        result = await orchestrator.process_complex_request(request["description"])
        return {
            "success": True,
            "result": result,
            "orchestration_id": f"orch_{datetime.utcnow().timestamp()}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_name}/chat-with-memory")
async def chat_with_memory(
    agent_name: str,
    request: Dict[str, Any]
) -> Dict[str, Any]:
    """Chat with agent using memory system"""
    if agent_name not in agent_memories:
        agent_memories[agent_name] = AgentMemory(agent_name)
    
    memory = agent_memories[agent_name]
    
    # Retrieve relevant memories
    relevant_memories = await memory.retrieve_relevant_memories(
        request["message"],
        request.get("context", {})
    )
    
    # Enhance request with memory context
    enhanced_request = {
        **request,
        "memory_context": relevant_memories
    }
    
    # Process with agent
    response = await agents[agent_name].process_request(
        AgentRequest(
            message=AgentMessage(
                role="user",
                content=request["message"],
                timestamp=datetime.utcnow().isoformat()
            ),
            context=enhanced_request
        )
    )
    
    # Store interaction in memory
    await memory.store_interaction({
        "request": request,
        "response": response.dict(),
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {
        "response": response.dict(),
        "memory_used": len(relevant_memories),
        "agent": agent_name
    }

@router.post("/{agent_name}/feedback")
async def provide_feedback(
    agent_name: str,
    feedback: Dict[str, Any]
) -> Dict[str, Any]:
    """Provide feedback to agent for learning"""
    if agent_name not in agent_memories:
        agent_memories[agent_name] = AgentMemory(agent_name)
    
    memory = agent_memories[agent_name]
    await memory.learn_from_feedback(feedback)
    
    return {
        "success": True,
        "message": "Feedback processed and learned",
        "agent": agent_name
    }

@router.get("/{agent_name}/memory")
async def get_agent_memory(agent_name: str) -> Dict[str, Any]:
    """Get agent memory statistics"""
    if agent_name not in agent_memories:
        return {"error": "Agent memory not found"}
    
    memory = agent_memories[agent_name]
    return {
        "agent_id": memory.agent_id,
        "short_term_count": len(memory.short_term_memory),
        "episodic_count": len(memory.episodic_memory),
        "semantic_count": len(memory.semantic_memory),
        "procedural_count": len(memory.procedural_memory)
    }
```

---

## 🔄 Continuous Integration & Testing

### 1. GitHub Actions Workflow
```yaml
# .github/workflows/api-testing.yml
name: API Testing & Validation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio httpx
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app --cov-report=xml
    
    - name: Run Postman tests
      run: |
        npm install -g newman
        newman run tests/postman/obsidian-api-collection.json \
          --environment tests/postman/test-environment.json \
          --reporters cli,junit \
          --reporter-junit-export test-results.xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 2. Docker Testing Environment
```dockerfile
# Dockerfile.test
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Install testing tools
RUN pip install pytest pytest-asyncio httpx newman

# Copy test files
COPY tests/ tests/
COPY postman/ postman/

# Run tests
CMD ["pytest", "tests/", "-v"]
```

### 3. API Contract Testing
```python
# test_contracts.py
import pytest
from pact import Consumer, Provider
import requests

@pytest.fixture
def pact():
    """Pact contract testing fixture"""
    return Consumer('ObsidianVaultClient').has_pact_with(Provider('ObsidianVaultAPI'))

def test_health_endpoint_contract(pact):
    """Test health endpoint contract"""
    expected = {
        'status': 'healthy',
        'services': {
            'obsidian_api': 'healthy',
            'vault_path': '/vault',
            'api_version': '2.0.0'
        }
    }
    
    (pact
     .given('API is healthy')
     .upon_receiving('a health check request')
     .with_request('GET', '/health')
     .will_respond_with(200, body=expected))
    
    with pact:
        response = requests.get(f"{pact.uri}/health")
        assert response.status_code == 200
        assert response.json() == expected

def test_note_creation_contract(pact):
    """Test note creation contract"""
    expected_request = {
        'path': 'test/contract-note.md',
        'content': '# Contract Test Note',
        'tags': ['test', 'contract']
    }
    
    expected_response = {
        'status': 'created',
        'path': 'test/contract-note.md',
        'operation_id': 'op_123456'
    }
    
    (pact
     .given('valid authentication')
     .upon_receiving('a note creation request')
     .with_request('POST', '/api/v1/notes', body=expected_request)
     .will_respond_with(201, body=expected_response))
    
    with pact:
        response = requests.post(
            f"{pact.uri}/api/v1/notes",
            json=expected_request,
            headers={'Authorization': 'Bearer test_token'}
        )
        assert response.status_code == 201
        assert response.json() == expected_response
```

This comprehensive guide provides everything needed for API data wrangling, automated testing, and custom AI agent interactions with your Obsidian vault system!

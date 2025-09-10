# 🌐 **API DESIGN PATTERNS & TECHNIQUES**

**Version:** 3.0.0  
**Last Updated:** September 6, 2025  
**Status:** ✅ **PRODUCTION-READY API DESIGN**

---

## 🎯 **API DESIGN PHILOSOPHY**

The Data Vault Obsidian API follows **RESTful principles** with **GraphQL capabilities**, **OpenAPI standards**, and **microservices architecture** patterns for scalable, maintainable, and developer-friendly APIs.

### **Core API Design Principles**

- **RESTful Design** - Resource-based URLs with HTTP methods
- **OpenAPI Specification** - Comprehensive API documentation
- **Versioning Strategy** - Backward compatibility and evolution
- **Error Handling** - Consistent error responses and status codes
- **Rate Limiting** - Protection against abuse and overload
- **Authentication** - Secure access control and authorization
- **Documentation** - Self-documenting and interactive APIs

---

## 🏗️ **API ARCHITECTURE PATTERNS**

### **1. RESTful API Pattern**

#### **Resource-Based URL Design**
```python
# Good RESTful design
GET    /api/v1/notes                    # List all notes
GET    /api/v1/notes/{id}               # Get specific note
POST   /api/v1/notes                    # Create new note
PUT    /api/v1/notes/{id}               # Update entire note
PATCH  /api/v1/notes/{id}               # Partial update
DELETE /api/v1/notes/{id}               # Delete note

# Nested resources
GET    /api/v1/notes/{id}/tags          # Get note tags
POST   /api/v1/notes/{id}/tags          # Add tag to note
DELETE /api/v1/notes/{id}/tags/{tag_id} # Remove tag from note
```

#### **HTTP Status Code Strategy**
```python
class APIResponse:
    @staticmethod
    def success(data: Any, status_code: int = 200) -> dict:
        return {
            "success": True,
            "data": data,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def error(message: str, status_code: int = 400, details: dict = None) -> dict:
        return {
            "success": False,
            "error": {
                "message": message,
                "code": status_code,
                "details": details or {}
            },
            "timestamp": datetime.utcnow().isoformat()
        }
```

---

### **2. API Gateway Pattern**

#### **Centralized API Gateway Implementation**
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import httpx

class APIGateway:
    def __init__(self):
        self.app = FastAPI(
            title="Data Vault Obsidian API Gateway",
            version="3.0.0",
            description="Centralized API Gateway for Data Vault Obsidian"
        )
        self.service_registry = ServiceRegistry()
        self.rate_limiter = RateLimiter()
        self.auth_service = AuthService()
        self._setup_middleware()
    
    def _setup_middleware(self):
        """Setup API Gateway middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]
        )
        
        # Rate limiting middleware
        self.app.middleware("http")(self.rate_limiter.middleware)
        
        # Authentication middleware
        self.app.middleware("http")(self.auth_service.middleware)
    
    async def route_request(self, service_name: str, path: str, method: str, 
                          headers: dict, body: bytes) -> dict:
        """Route request to appropriate microservice"""
        try:
            # Get service endpoint
            service_url = await self.service_registry.get_service_url(service_name)
            if not service_url:
                raise HTTPException(status_code=503, detail="Service unavailable")
            
            # Forward request
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=f"{service_url}{path}",
                    headers=headers,
                    content=body,
                    timeout=30.0
                )
                
                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.content
                }
                
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Gateway timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
```

---

### **3. API Versioning Pattern**

#### **URL Path Versioning**
```python
from fastapi import APIRouter, Depends
from enum import Enum

class APIVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"

class VersionedAPIRouter(APIRouter):
    def __init__(self, version: APIVersion, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = version
        self.prefix = f"/api/{version.value}"
    
    def add_versioned_endpoint(self, path: str, methods: list, handler, **kwargs):
        """Add versioned endpoint with backward compatibility"""
        for method in methods:
            self.add_api_route(
                path=path,
                endpoint=handler,
                methods=[method],
                **kwargs
            )

# Usage example
v1_router = VersionedAPIRouter(APIVersion.V1)
v2_router = VersionedAPIRouter(APIVersion.V2)

@v1_router.get("/notes")
async def get_notes_v1():
    """V1 notes endpoint - basic functionality"""
    return {"version": "v1", "notes": []}

@v2_router.get("/notes")
async def get_notes_v2():
    """V2 notes endpoint - enhanced functionality"""
    return {
        "version": "v2", 
        "notes": [],
        "pagination": {"page": 1, "limit": 10},
        "metadata": {"total": 0}
    }
```

#### **Header-Based Versioning**
```python
from fastapi import Header, HTTPException

class VersionHeader:
    def __init__(self, version: str = Header(..., alias="API-Version")):
        self.version = version
        if version not in ["v1", "v2", "v3"]:
            raise HTTPException(status_code=400, detail="Invalid API version")

@app.get("/notes")
async def get_notes(version: VersionHeader = Depends()):
    """Version-aware notes endpoint"""
    if version.version == "v1":
        return get_notes_v1()
    elif version.version == "v2":
        return get_notes_v2()
    else:
        return get_notes_v3()
```

---

### **4. API Documentation Pattern**

#### **OpenAPI Specification**
```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def create_openapi_schema(app: FastAPI) -> dict:
    """Create comprehensive OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Data Vault Obsidian API",
        version="3.0.0",
        description="""
        ## Data Vault Obsidian API
        
        A comprehensive API for managing Obsidian vaults, AI workflows, and MCP integrations.
        
        ### Features
        - **Note Management**: Create, read, update, and delete Obsidian notes
        - **AI Workflows**: Execute LangGraph workflows and AI agents
        - **MCP Integration**: Connect to Model Context Protocol servers
        - **Monitoring**: Real-time observability and metrics
        
        ### Authentication
        All endpoints require authentication via JWT tokens.
        
        ### Rate Limiting
        API calls are rate limited to prevent abuse.
        """,
        routes=app.routes,
        servers=[
            {"url": "https://api.datavaultobsidian.com", "description": "Production server"},
            {"url": "https://staging-api.datavaultobsidian.com", "description": "Staging server"},
            {"url": "http://localhost:8000", "description": "Development server"}
        ]
    )
    
    # Add custom schema components
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Add examples
    openapi_schema["components"]["examples"] = {
        "NoteExample": {
            "summary": "Example Note",
            "value": {
                "id": "note-123",
                "title": "My First Note",
                "content": "# My First Note\n\nThis is the content of my note.",
                "tags": ["example", "first"],
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
```

---

### **5. API Error Handling Pattern**

#### **Centralized Error Handling**
```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

class APIErrorHandler:
    def __init__(self, app: FastAPI):
        self.app = app
        self.logger = logging.getLogger(__name__)
        self._setup_error_handlers()
    
    def _setup_error_handlers(self):
        """Setup centralized error handlers"""
        
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": {
                        "type": "HTTPException",
                        "message": exc.detail,
                        "status_code": exc.status_code
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url)
                }
            )
        
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": {
                        "type": "ValidationError",
                        "message": "Request validation failed",
                        "details": exc.errors()
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url)
                }
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            self.logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "type": "InternalServerError",
                        "message": "An internal server error occurred"
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url)
                }
            )
```

---

### **6. API Rate Limiting Pattern**

#### **Token Bucket Rate Limiting**
```python
import time
from collections import defaultdict
from typing import Dict, Optional

class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, Dict] = defaultdict(lambda: {
            "tokens": capacity,
            "last_refill": time.time()
        })
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed based on rate limit"""
        bucket = self.buckets[key]
        now = time.time()
        
        # Refill tokens based on time elapsed
        time_passed = now - bucket["last_refill"]
        tokens_to_add = time_passed * self.refill_rate
        bucket["tokens"] = min(self.capacity, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now
        
        # Check if tokens available
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        return False
    
    def get_retry_after(self, key: str) -> float:
        """Get time until next token is available"""
        bucket = self.buckets[key]
        if bucket["tokens"] >= 1:
            return 0.0
        
        tokens_needed = 1 - bucket["tokens"]
        return tokens_needed / self.refill_rate

class RateLimiter:
    def __init__(self):
        self.limiter = TokenBucketRateLimiter(capacity=100, refill_rate=10)  # 100 requests, 10 per second
    
    async def middleware(self, request: Request, call_next):
        """Rate limiting middleware"""
        client_ip = request.client.host
        user_id = getattr(request.state, "user_id", None)
        key = f"{client_ip}:{user_id}" if user_id else client_ip
        
        if not self.limiter.is_allowed(key):
            retry_after = self.limiter.get_retry_after(key)
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "type": "RateLimitExceeded",
                        "message": "Rate limit exceeded",
                        "retry_after": retry_after
                    }
                },
                headers={"Retry-After": str(int(retry_after))}
            )
        
        response = await call_next(request)
        return response
```

---

### **7. API Authentication Pattern**

#### **JWT Authentication**
```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

class JWTAuthService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

class AuthMiddleware:
    def __init__(self, auth_service: JWTAuthService):
        self.auth_service = auth_service
    
    async def middleware(self, request: Request, call_next):
        """Authentication middleware"""
        # Skip auth for public endpoints
        if request.url.path in ["/docs", "/openapi.json", "/health"]:
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": {"message": "Missing or invalid authorization header"}}
            )
        
        token = auth_header.split(" ")[1]
        payload = self.auth_service.verify_token(token)
        
        if not payload:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": {"message": "Invalid or expired token"}}
            )
        
        # Add user info to request state
        request.state.user_id = payload.get("user_id")
        request.state.user_roles = payload.get("roles", [])
        
        return await call_next(request)
```

---

### **8. API Caching Pattern**

#### **Redis-Based API Caching**
```python
import redis
import json
from typing import Any, Optional
from datetime import timedelta

class APICache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 300  # 5 minutes
    
    def _generate_cache_key(self, endpoint: str, params: dict) -> str:
        """Generate cache key from endpoint and parameters"""
        import hashlib
        key_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return f"api_cache:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    async def get(self, endpoint: str, params: dict) -> Optional[Any]:
        """Get cached response"""
        cache_key = self._generate_cache_key(endpoint, params)
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def set(self, endpoint: str, params: dict, data: Any, ttl: int = None) -> None:
        """Cache response data"""
        cache_key = self._generate_cache_key(endpoint, params)
        ttl = ttl or self.default_ttl
        
        self.redis_client.setex(
            cache_key,
            ttl,
            json.dumps(data, default=str)
        )
    
    async def invalidate(self, pattern: str) -> None:
        """Invalidate cache entries matching pattern"""
        keys = self.redis_client.keys(f"api_cache:{pattern}")
        if keys:
            self.redis_client.delete(*keys)

class CachingMiddleware:
    def __init__(self, cache: APICache):
        self.cache = cache
    
    async def middleware(self, request: Request, call_next):
        """Caching middleware"""
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Generate cache key
        params = dict(request.query_params)
        cache_key = f"{request.url.path}:{json.dumps(params, sort_keys=True)}"
        
        # Try to get from cache
        cached_response = await self.cache.get(request.url.path, params)
        if cached_response:
            return JSONResponse(content=cached_response)
        
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200:
            response_body = response.body.decode() if hasattr(response, 'body') else None
            if response_body:
                try:
                    data = json.loads(response_body)
                    await self.cache.set(request.url.path, params, data)
                except json.JSONDecodeError:
                    pass
        
        return response
```

---

### **9. API Monitoring Pattern**

#### **Request/Response Monitoring**
```python
import time
from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Any

class APIMetrics:
    def __init__(self):
        self.request_count = Counter(
            'api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.request_duration = Histogram(
            'api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint']
        )
        
        self.active_requests = Gauge(
            'api_active_requests',
            'Currently active requests'
        )
        
        self.error_count = Counter(
            'api_errors_total',
            'Total API errors',
            ['error_type', 'endpoint']
        )
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record request metrics"""
        self.request_count.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_error(self, error_type: str, endpoint: str):
        """Record error metrics"""
        self.error_count.labels(error_type=error_type, endpoint=endpoint).inc()

class MonitoringMiddleware:
    def __init__(self, metrics: APIMetrics):
        self.metrics = metrics
    
    async def middleware(self, request: Request, call_next):
        """Monitoring middleware"""
        start_time = time.time()
        self.metrics.active_requests.inc()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            self.metrics.record_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
            
        except Exception as e:
            # Record error metrics
            self.metrics.record_error(
                error_type=type(e).__name__,
                endpoint=request.url.path
            )
            raise
        
        finally:
            self.metrics.active_requests.dec()
```

---

### **10. API Testing Pattern**

#### **Comprehensive API Testing**
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

class APITestSuite:
    def __init__(self, app: FastAPI):
        self.client = TestClient(app)
        self.test_data = self._create_test_data()
    
    def _create_test_data(self) -> dict:
        """Create test data for API testing"""
        return {
            "valid_note": {
                "title": "Test Note",
                "content": "# Test Note\n\nThis is a test note.",
                "tags": ["test", "example"]
            },
            "invalid_note": {
                "title": "",  # Invalid: empty title
                "content": "Test content"
            },
            "user_credentials": {
                "username": "testuser",
                "password": "testpassword"
            }
        }
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_authentication_required(self):
        """Test that protected endpoints require authentication"""
        response = self.client.get("/api/v1/notes")
        assert response.status_code == 401
    
    def test_valid_authentication(self):
        """Test valid authentication flow"""
        # Login
        login_response = self.client.post(
            "/api/v1/auth/login",
            json=self.test_data["user_credentials"]
        )
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Access protected endpoint
        response = self.client.get("/api/v1/notes", headers=headers)
        assert response.status_code == 200
    
    def test_create_note_success(self):
        """Test successful note creation"""
        # Get auth token
        token = self._get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create note
        response = self.client.post(
            "/api/v1/notes",
            json=self.test_data["valid_note"],
            headers=headers
        )
        assert response.status_code == 201
        assert response.json()["success"] is True
        assert "id" in response.json()["data"]
    
    def test_create_note_validation_error(self):
        """Test note creation with validation errors"""
        token = self._get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = self.client.post(
            "/api/v1/notes",
            json=self.test_data["invalid_note"],
            headers=headers
        )
        assert response.status_code == 422
        assert response.json()["success"] is False
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        token = self._get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make multiple requests quickly
        for _ in range(105):  # Exceed rate limit
            response = self.client.get("/api/v1/notes", headers=headers)
            if response.status_code == 429:
                break
        
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["error"]["message"]
    
    def _get_auth_token(self) -> str:
        """Helper method to get authentication token"""
        login_response = self.client.post(
            "/api/v1/auth/login",
            json=self.test_data["user_credentials"]
        )
        return login_response.json()["access_token"]

# Pytest fixtures
@pytest.fixture
def api_test_suite(app: FastAPI):
    return APITestSuite(app)

@pytest.fixture
def authenticated_client(app: FastAPI):
    client = TestClient(app)
    # Setup authentication
    return client
```

---

## 🚀 **API PERFORMANCE OPTIMIZATION**

### **1. Response Compression**
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### **2. Connection Pooling**
```python
import httpx

class HTTPClientPool:
    def __init__(self, pool_size: int = 10):
        self.pool_size = pool_size
        self._client = None
    
    async def get_client(self) -> httpx.AsyncClient:
        if not self._client:
            self._client = httpx.AsyncClient(
                limits=httpx.Limits(max_keepalive_connections=self.pool_size)
            )
        return self._client
```

### **3. Database Query Optimization**
```python
from sqlalchemy.orm import selectinload, joinedload

class OptimizedNoteRepository:
    def get_notes_with_tags(self, limit: int = 10):
        """Optimized query with eager loading"""
        return self.session.query(Note)\
            .options(joinedload(Note.tags))\
            .limit(limit)\
            .all()
```

---

## 🔒 **API SECURITY PATTERNS**

### **1. Input Validation**
```python
from pydantic import BaseModel, validator
from typing import List, Optional

class NoteCreateRequest(BaseModel):
    title: str
    content: str
    tags: List[str] = []
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title too long')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Too many tags')
        return [tag.strip().lower() for tag in v if tag.strip()]
```

### **2. SQL Injection Prevention**
```python
from sqlalchemy import text

class SecureNoteRepository:
    def search_notes(self, query: str):
        """Safe parameterized query"""
        return self.session.execute(
            text("SELECT * FROM notes WHERE content ILIKE :query"),
            {"query": f"%{query}%"}
        ).fetchall()
```

---

**Last Updated:** September 6, 2025  
**API Design Version:** 3.0.0  
**Status:** ✅ **PRODUCTION-READY**

**COMPREHENSIVE API DESIGN PATTERNS COMPLETE!**

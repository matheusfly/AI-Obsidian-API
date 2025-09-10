# Advanced LangGraph Server Management Guide
## Complete Symbiosis with Obsidian Vaults

### 🚀 Executive Summary
This guide provides advanced techniques for managing LangGraph servers, debugging workflows, and achieving complete symbiosis with Obsidian vaults through MCP integration.

### 📋 Table of Contents
1. [Advanced LangGraph CLI Commands](#advanced-langgraph-cli-commands)
2. [Server Debugging Techniques](#server-debugging-techniques)
3. [MCP Integration with Obsidian](#mcp-integration-with-obsidian)
4. [Performance Optimization](#performance-optimization)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Production Deployment](#production-deployment)

---

## Advanced LangGraph CLI Commands

### Core Server Management
```bash
# Start development server with advanced options
langgraph dev --host 0.0.0.0 --port 2024 --no-browser --debug

# Start with custom configuration
langgraph dev --config custom-config.json --watch

# Start with specific environment
langgraph dev --env production.env

# Start with debug logging
langgraph dev --log-level debug --verbose

# Start with custom checkpoint store
langgraph dev --checkpoint-store memory --checkpoint-store-config '{"memory": true}'
```

### Production Server Commands
```bash
# Build production image
langgraph build --tag my-langgraph-app:latest --platform linux/amd64

# Deploy with Docker Compose
langgraph up --docker-compose docker-compose.prod.yml

# Deploy with Kubernetes
langgraph deploy --k8s --namespace production

# Scale horizontally
langgraph scale --replicas 5 --auto-scale
```

### Workflow Management
```bash
# List all workflows
langgraph workflows list

# Validate workflow configuration
langgraph workflows validate obsidian-workflow

# Test workflow execution
langgraph workflows test obsidian-workflow --input test-input.json

# Deploy specific workflow
langgraph workflows deploy obsidian-workflow --version 1.0.0

# Monitor workflow execution
langgraph workflows monitor obsidian-workflow --follow
```

### Debugging Commands
```bash
# Start with debugger attached
langgraph dev --debug-port 5678 --debug-host 0.0.0.0

# Profile workflow performance
langgraph profile obsidian-workflow --duration 60s

# Trace workflow execution
langgraph trace obsidian-workflow --trace-id abc123

# Analyze workflow bottlenecks
langgraph analyze obsidian-workflow --output report.html
```

---

## Server Debugging Techniques

### 1. Configuration Validation
```bash
# Validate langgraph.json configuration
langgraph config validate

# Check workflow syntax
langgraph workflows validate --all

# Verify dependencies
langgraph deps check
```

### 2. Runtime Debugging
```bash
# Enable verbose logging
export LANGGRAPH_LOG_LEVEL=DEBUG
langgraph dev --verbose

# Enable request tracing
export LANGGRAPH_TRACE=true
langgraph dev --trace

# Enable performance profiling
export LANGGRAPH_PROFILE=true
langgraph dev --profile
```

### 3. Health Monitoring
```bash
# Check server health
curl http://localhost:2024/health

# Check workflow status
curl http://localhost:2024/workflows/obsidian-workflow/status

# Check MCP endpoint
curl http://localhost:2024/mcp/health
```

### 4. Error Analysis
```bash
# View server logs
langgraph logs --follow --tail 100

# Filter error logs
langgraph logs --level error --since 1h

# Export logs for analysis
langgraph logs --export logs.json --format json
```

---

## MCP Integration with Obsidian

### 1. Enable MCP Support
```bash
# Upgrade to MCP-compatible versions
pip install "langgraph-api>=0.2.3" "langgraph-sdk>=0.1.61"

# Install MCP adapters
pip install langchain-mcp-adapters

# Start server with MCP enabled
langgraph dev --mcp-enabled
```

### 2. Configure Obsidian MCP Server
```python
# mcp_obsidian_server.py
from langchain_mcp_adapters.client import MultiServerMCPClient

# Configure MCP client for Obsidian
obsidian_client = MultiServerMCPClient({
    "obsidian": {
        "url": "http://127.0.0.1:27123",
        "transport": "streamable_http",
        "headers": {
            "Authorization": "Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
        }
    }
})

# Expose Obsidian tools to LangGraph
@tool
async def search_obsidian_notes(query: str) -> dict:
    """Search notes in Obsidian vault"""
    result = await obsidian_client.call_tool("obsidian", "search_notes", {"query": query})
    return result
```

### 3. Advanced Obsidian Integration
```python
# Advanced Obsidian workflow with MCP
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
import asyncio

class ObsidianMCPState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    vault_name: str
    search_results: list
    current_file: str
    workflow_status: str

@tool
async def mcp_obsidian_search(query: str, vault_name: str) -> dict:
    """Advanced Obsidian search using MCP"""
    try:
        # Use MCP client for advanced search
        result = await obsidian_client.call_tool(
            "obsidian", 
            "advanced_search", 
            {
                "query": query,
                "vault_name": vault_name,
                "include_content": True,
                "limit": 50
            }
        )
        return result
    except Exception as e:
        return {"error": str(e), "success": False}

@tool
async def mcp_obsidian_create_note(title: str, content: str, vault_name: str) -> dict:
    """Create note in Obsidian using MCP"""
    try:
        result = await obsidian_client.call_tool(
            "obsidian",
            "create_note",
            {
                "title": title,
                "content": content,
                "vault_name": vault_name,
                "template": "default"
            }
        )
        return result
    except Exception as e:
        return {"error": str(e), "success": False}
```

---

## Performance Optimization

### 1. Workflow Optimization
```python
# Optimized workflow with caching
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

# Enable caching for expensive operations
checkpointer = MemorySaver()

# Create optimized workflow
workflow = StateGraph(ObsidianMCPState)
workflow.add_node("search", mcp_obsidian_search)
workflow.add_node("create", mcp_obsidian_create_note)

# Add caching layer
workflow.add_node("cached_search", 
    lambda state: cache.get(state["query"]) or mcp_obsidian_search(state["query"], state["vault_name"])
)

# Compile with checkpointer
app = workflow.compile(checkpointer=checkpointer)
```

### 2. Memory Management
```python
# Optimize memory usage
import gc
from typing import Optional

class OptimizedObsidianState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    vault_name: str
    search_results: Optional[list] = None  # Lazy loading
    current_file: Optional[str] = None
    workflow_status: str

def cleanup_state(state: OptimizedObsidianState) -> OptimizedObsidianState:
    """Clean up state to reduce memory usage"""
    # Keep only recent messages
    if len(state["messages"]) > 10:
        state["messages"] = state["messages"][-10:]
    
    # Clear large search results if not needed
    if state.get("search_results") and len(state["search_results"]) > 100:
        state["search_results"] = state["search_results"][:50]
    
    # Force garbage collection
    gc.collect()
    
    return state
```

### 3. Async Optimization
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Use thread pool for I/O operations
executor = ThreadPoolExecutor(max_workers=4)

async def parallel_obsidian_operations(state: ObsidianMCPState) -> ObsidianMCPState:
    """Execute multiple Obsidian operations in parallel"""
    
    # Create tasks for parallel execution
    tasks = []
    
    if state.get("search_query"):
        tasks.append(mcp_obsidian_search(state["search_query"], state["vault_name"]))
    
    if state.get("create_note"):
        tasks.append(mcp_obsidian_create_note(
            state["note_title"], 
            state["note_content"], 
            state["vault_name"]
        ))
    
    # Execute all tasks in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for i, result in enumerate(results):
        if not isinstance(result, Exception):
            if i == 0:  # Search result
                state["search_results"] = result.get("results", [])
            elif i == 1:  # Create result
                state["created_note"] = result.get("file_path")
    
    return state
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. LangGraph Server Won't Start
```bash
# Check configuration
langgraph config validate

# Check for port conflicts
netstat -an | findstr :2024

# Clear cache and restart
rm -rf .langgraph_api/
langgraph dev --clean
```

#### 2. Workflow Compilation Errors
```bash
# Validate workflow syntax
langgraph workflows validate obsidian-workflow

# Check Python syntax
python -m py_compile langgraph_workflows/obsidian_workflow.py

# Test workflow import
python -c "from langgraph_workflows.obsidian_workflow import workflow; print('OK')"
```

#### 3. MCP Connection Issues
```bash
# Test MCP endpoint
curl -X POST http://localhost:2024/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list", "params": {}}'

# Check MCP server logs
langgraph logs --filter mcp
```

#### 4. Obsidian API Connectivity
```bash
# Test Obsidian API directly
curl -X GET "http://127.0.0.1:27123/health" \
  -H "Authorization: Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

# Check Obsidian plugin status
# In Obsidian: Settings > Community plugins > Local REST API
```

### Debugging Workflows

#### 1. Enable Debug Mode
```python
# Add debug logging to workflow
import logging
logging.basicConfig(level=logging.DEBUG)

def debug_workflow_node(state: ObsidianMCPState) -> ObsidianMCPState:
    """Debug workflow node with detailed logging"""
    logger = logging.getLogger(__name__)
    logger.debug(f"Processing state: {state}")
    
    try:
        # Your workflow logic here
        result = process_state(state)
        logger.debug(f"Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in workflow node: {e}")
        raise
```

#### 2. Workflow Tracing
```python
# Add tracing to workflow
from langsmith import trace

@trace
def traced_obsidian_search(query: str, vault_name: str) -> dict:
    """Traced Obsidian search for debugging"""
    with trace(name="obsidian_search", inputs={"query": query, "vault_name": vault_name}):
        result = mcp_obsidian_search(query, vault_name)
        trace.outputs = {"result": result}
        return result
```

---

## Production Deployment

### 1. Docker Deployment
```dockerfile
# Dockerfile for production
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 2024

# Start LangGraph server
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "2024"]
```

### 2. Kubernetes Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langgraph-obsidian
spec:
  replicas: 3
  selector:
    matchLabels:
      app: langgraph-obsidian
  template:
    metadata:
      labels:
        app: langgraph-obsidian
    spec:
      containers:
      - name: langgraph
        image: langgraph-obsidian:latest
        ports:
        - containerPort: 2024
        env:
        - name: OBSIDIAN_API_URL
          value: "http://obsidian-api:27123"
        - name: OBSIDIAN_API_KEY
          valueFrom:
            secretKeyRef:
              name: obsidian-secrets
              key: api-key
```

### 3. Monitoring and Observability
```python
# Add monitoring to workflow
from prometheus_client import Counter, Histogram, start_http_server
import time

# Metrics
workflow_counter = Counter('workflow_executions_total', 'Total workflow executions', ['workflow_name', 'status'])
workflow_duration = Histogram('workflow_duration_seconds', 'Workflow execution duration', ['workflow_name'])

def monitored_workflow(state: ObsidianMCPState) -> ObsidianMCPState:
    """Workflow with monitoring"""
    start_time = time.time()
    
    try:
        result = process_workflow(state)
        workflow_counter.labels(workflow_name='obsidian', status='success').inc()
        return result
    except Exception as e:
        workflow_counter.labels(workflow_name='obsidian', status='error').inc()
        raise
    finally:
        duration = time.time() - start_time
        workflow_duration.labels(workflow_name='obsidian').observe(duration)
```

---

## Quick Reference Commands

### Essential LangGraph CLI Commands
```bash
# Development
langgraph dev --host 0.0.0.0 --port 2024 --no-browser
langgraph dev --debug --verbose --watch

# Production
langgraph build --tag my-app:latest
langgraph up --docker-compose prod.yml

# Workflow Management
langgraph workflows list
langgraph workflows validate obsidian-workflow
langgraph workflows test obsidian-workflow --input test.json

# Debugging
langgraph logs --follow --level debug
langgraph trace obsidian-workflow --trace-id abc123
langgraph profile obsidian-workflow --duration 60s

# MCP Integration
langgraph dev --mcp-enabled
curl http://localhost:2024/mcp/health
```

### Obsidian Integration Commands
```bash
# Test Obsidian API
curl -X GET "http://127.0.0.1:27123/health" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Test file operations
curl -X GET "http://127.0.0.1:27123/vault/files" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Test search
curl -X POST "http://127.0.0.1:27123/vault/search" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "langgraph", "vault_name": "Nomade Milionario"}'
```

---

## Conclusion

This guide provides comprehensive techniques for managing LangGraph servers and achieving complete symbiosis with Obsidian vaults. By following these advanced practices, you can:

1. **Optimize Performance**: Implement caching, parallel processing, and memory management
2. **Debug Effectively**: Use advanced debugging techniques and monitoring
3. **Integrate Seamlessly**: Leverage MCP for robust Obsidian integration
4. **Deploy Production-Ready**: Use Docker and Kubernetes for scalable deployment
5. **Monitor Continuously**: Implement comprehensive observability

The key to success is understanding the relationship between LangGraph workflows, MCP servers, and Obsidian vaults, and using the right tools and techniques for each component.

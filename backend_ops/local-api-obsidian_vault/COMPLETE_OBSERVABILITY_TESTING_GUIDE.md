# 🧪 COMPLETE OBSERVABILITY TESTING GUIDE

## 📊 Comprehensive Testing and Validation for Enhanced Observability System

This guide provides complete testing procedures for the enhanced observability system with full coverage of backend API, local servers, and AI agents.

## 🚀 Quick Start Testing

### 1. **One-Command Launch and Test**
```powershell
# Launch complete system with interactive monitoring
.\launchers\ENHANCED_OBSERVABILITY_LAUNCHER.ps1 -Mode full -Interactive -Monitor

# Launch with UV optimization only
.\launchers\ENHANCED_OBSERVABILITY_LAUNCHER.ps1 -Mode full -SkipDocker -Verbose

# Launch observability stack only
.\launchers\ENHANCED_OBSERVABILITY_LAUNCHER.ps1 -Mode observability-only -Interactive
```

### 2. **Docker Compose Testing**
```powershell
# Start enhanced observability stack
docker-compose -f docker-compose.enhanced-observability.yml up -d

# View logs
docker-compose -f docker-compose.enhanced-observability.yml logs -f

# Test all services
docker-compose -f docker-compose.enhanced-observability.yml ps
```

## 🔍 Service Health Testing

### **Backend API Testing**

#### 1. **Vault API Enhanced Health Check**
```bash
# Basic health check
curl -X GET "http://localhost:8080/health" | jq

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "services": {
    "obsidian_api": {
      "status": "healthy",
      "response_time": 0.123,
      "url": "http://obsidian-api:27123"
    },
    "vault_path": {
      "path": "/vault",
      "accessible": true
    }
  },
  "metrics": { ... },
  "uptime": 123.456
}
```

#### 2. **Prometheus Metrics Endpoint**
```bash
# Get Prometheus metrics
curl -X GET "http://localhost:8080/metrics"

# Expected metrics:
# vault_api_requests_total{service="vault-api",method="GET",status="200"} 42
# vault_api_response_time_seconds{service="vault-api",method="GET"} 0.123
# system_cpu_usage_percent 15.5
# system_memory_usage_bytes 1073741824
```

#### 3. **AI Agent Metrics Testing**
```bash
# Test AI agent analytics
curl -X GET "http://localhost:8080/api/v1/ai/agents/context-master/analytics?days=7"

# Expected response:
{
  "agent_id": "context-master",
  "analytics": {
    "agent_type": "rag_agent",
    "total_requests": 150,
    "successful_requests": 145,
    "failed_requests": 5,
    "success_rate": 96.67,
    "average_response_time": 1.23
  }
}
```

### **Observability Stack Testing**

#### 1. **Grafana Dashboard Access**
```bash
# Access Grafana
open http://localhost:3000
# Username: admin
# Password: admin123

# Verify dashboards:
# - System Overview
# - AI Agent Performance
# - Backend API Metrics
# - Distributed Tracing
```

#### 2. **Prometheus Query Testing**
```bash
# Access Prometheus
open http://localhost:9090

# Test queries:
# - up{job="vault-api-enhanced"}
# - rate(vault_api_requests_total[5m])
# - histogram_quantile(0.95, vault_api_response_time_seconds_bucket)
# - ai_agent_requests_total
```

#### 3. **Jaeger Tracing Testing**
```bash
# Access Jaeger
open http://localhost:16686

# Search for traces:
# - Service: vault-api-enhanced
# - Operation: GET /health
# - Tags: service.name=vault-api-enhanced
```

## 🤖 AI Agent Testing

### **1. Enhanced RAG Testing**
```bash
# Test enhanced RAG query
curl -X POST "http://localhost:8080/api/v1/rag/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic of my notes?",
    "agent_id": "context-master",
    "use_hierarchical": true,
    "max_depth": 3,
    "temperature": 0.7
  }'

# Expected response:
{
  "success": true,
  "result": {
    "answer": "Based on your notes...",
    "sources": [...],
    "confidence": 0.85
  },
  "agent_id": "context-master",
  "response_time": 1.23,
  "hierarchical": true
}
```

### **2. AI Retrieval Testing**
```bash
# Test AI retrieval
curl -X POST "http://localhost:8080/api/v1/ai/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find information about machine learning",
    "agent_id": "context-master",
    "context": {"domain": "technology"},
    "use_cache": true
  }'
```

### **3. MCP Tool Testing**
```bash
# Test MCP tool call
curl -X POST "http://localhost:8080/api/v1/mcp/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "search_content",
    "arguments": {
      "query": "observability",
      "limit": 10
    },
    "timeout": 30
  }'
```

## 📊 Performance Testing

### **1. Load Testing with Artillery**
```bash
# Install Artillery
npm install -g artillery

# Create load test config
cat > load-test.yml << EOF
config:
  target: 'http://localhost:8080'
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - name: "Health Check Load Test"
    flow:
      - get:
          url: "/health"
      - get:
          url: "/metrics"
      - post:
          url: "/api/v1/search"
          json:
            query: "test query"
            limit: 10
EOF

# Run load test
artillery run load-test.yml
```

### **2. Memory and CPU Testing**
```bash
# Monitor system resources
docker stats

# Check specific container resources
docker stats vault-api-enhanced obsidian-api grafana prometheus

# Monitor with htop
htop
```

### **3. Database Performance Testing**
```bash
# Test PostgreSQL performance
docker exec -it postgres psql -U admin -d n8n -c "
SELECT 
  schemaname,
  tablename,
  attname,
  n_distinct,
  correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
"

# Test Redis performance
docker exec -it redis redis-cli --latency-history -i 1
```

## 🔧 Integration Testing

### **1. End-to-End Workflow Testing**
```bash
# Complete workflow test
curl -X POST "http://localhost:8080/api/v1/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "test-observability.md",
    "content": "# Observability Test\n\nThis is a test note for observability.",
    "tags": ["test", "observability"],
    "metadata": {"test": true}
  }'

# Search for the note
curl -X POST "http://localhost:8080/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "observability test",
    "limit": 10,
    "semantic": true
  }'

# Use AI retrieval
curl -X POST "http://localhost:8080/api/v1/ai/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is in the test note?",
    "agent_id": "context-master"
  }'
```

### **2. Cross-Service Communication Testing**
```bash
# Test Obsidian API integration
curl -X GET "http://localhost:27123/health"

# Test n8n integration
curl -X GET "http://localhost:5678/healthz"

# Test ChromaDB integration
curl -X GET "http://localhost:8000/api/v1/heartbeat"

# Test Qdrant integration
curl -X GET "http://localhost:6333/health"
```

## 📈 Monitoring and Alerting Testing

### **1. Alert Rule Testing**
```bash
# Trigger high CPU alert
# (Simulate high CPU usage)
stress --cpu 4 --timeout 30s

# Check Prometheus alerts
curl -X GET "http://localhost:9090/api/v1/alerts"

# Check AlertManager
curl -X GET "http://localhost:9093/api/v1/alerts"
```

### **2. Dashboard Testing**
```bash
# Test Grafana dashboards
# 1. Open http://localhost:3000
# 2. Navigate to each dashboard
# 3. Verify data is loading
# 4. Test time range changes
# 5. Test refresh functionality

# Test custom dashboards:
# - AI Agent Performance
# - Backend API Metrics
# - System Resources
# - Distributed Tracing
```

## 🐛 Troubleshooting Testing

### **1. Error Simulation Testing**
```bash
# Simulate service failures
docker stop obsidian-api
# Check health endpoint
curl -X GET "http://localhost:8080/health"

# Restart service
docker start obsidian-api
# Verify recovery
curl -X GET "http://localhost:8080/health"
```

### **2. Network Partition Testing**
```bash
# Simulate network issues
docker network disconnect obsidian-net vault-api-enhanced
# Check service behavior
curl -X GET "http://localhost:8080/health"

# Restore network
docker network connect obsidian-net vault-api-enhanced
```

### **3. Resource Exhaustion Testing**
```bash
# Simulate memory pressure
docker run --rm -it --memory=100m stress --vm 1 --vm-bytes 50M --timeout 30s

# Check system behavior
curl -X GET "http://localhost:8080/api/v1/system/metrics"
```

## 📋 Automated Testing Scripts

### **1. Complete Test Suite**
```powershell
# Run complete test suite
.\tests\TEST-COMPLETE-OBSERVABILITY.ps1

# Run specific test categories
.\tests\TEST-BACKEND-API.ps1
.\tests\TEST-AI-AGENTS.ps1
.\tests\TEST-OBSERVABILITY-STACK.ps1
```

### **2. Performance Benchmarking**
```powershell
# Run performance benchmarks
.\tests\BENCHMARK-PERFORMANCE.ps1

# Run load tests
.\tests\LOAD-TEST-SYSTEM.ps1
```

### **3. Integration Testing**
```powershell
# Run integration tests
.\tests\TEST-INTEGRATION.ps1

# Run end-to-end tests
.\tests\TEST-E2E-WORKFLOWS.ps1
```

## 🎯 Success Criteria

### **Performance Targets**
- ✅ API response time < 200ms (95th percentile)
- ✅ AI agent response time < 2s (95th percentile)
- ✅ System CPU usage < 80%
- ✅ Memory usage < 2GB per service
- ✅ Docker build time < 5 minutes with UV

### **Reliability Targets**
- ✅ Service uptime > 99.9%
- ✅ Error rate < 1%
- ✅ Recovery time < 30 seconds
- ✅ Data consistency 100%

### **Observability Targets**
- ✅ All services monitored
- ✅ All AI agents tracked
- ✅ Complete trace coverage
- ✅ Real-time alerting
- ✅ Dashboard responsiveness < 1s

## 🚀 Quick Commands Reference

```powershell
# Launch everything
.\launchers\ENHANCED_OBSERVABILITY_LAUNCHER.ps1 -Mode full -Interactive

# Test specific components
curl -X GET "http://localhost:8080/health"
curl -X GET "http://localhost:8080/metrics"
curl -X GET "http://localhost:3000"  # Grafana
curl -X GET "http://localhost:9090"  # Prometheus
curl -X GET "http://localhost:16686" # Jaeger

# Monitor logs
docker-compose -f docker-compose.enhanced-observability.yml logs -f

# Check service status
docker-compose -f docker-compose.enhanced-observability.yml ps

# Stop everything
docker-compose -f docker-compose.enhanced-observability.yml down
```

## 📚 Additional Resources

- **Grafana Dashboards**: http://localhost:3000
- **Prometheus Queries**: http://localhost:9090
- **Jaeger Tracing**: http://localhost:16686
- **API Documentation**: http://localhost:8080/docs
- **Metrics Endpoint**: http://localhost:8080/metrics

---

*This testing guide ensures complete coverage and validation of the enhanced observability system with UV optimization and comprehensive monitoring.*

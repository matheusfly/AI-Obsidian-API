# 🔧 Integration Fix Guide - Complete System Setup

## 🚨 **Current Issues Identified:**

1. **Docker Desktop Connection Issue** - Engine not accessible
2. **Vault API Container Missing** - Not building properly
3. **OpenAPI Endpoints Not Available** - Plugin can't connect
4. **PowerShell Color Parameter Issues** - Script errors

## 🎯 **Step-by-Step Fix Process**

### **Step 1: Fix Docker Desktop**

```powershell
# 1. Restart Docker Desktop
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# 2. Wait for Docker to be ready (2-3 minutes)
Write-Host "Waiting for Docker Desktop to start..."
do {
    Start-Sleep -Seconds 10
    try {
        docker info | Out-Null
        Write-Host "✅ Docker is ready!"
        break
    } catch {
        Write-Host "⏳ Still waiting for Docker..."
    }
} while ($true)
```

### **Step 2: Manual System Launch**

```powershell
# Navigate to project directory
cd "D:\codex\master_code\backend_ops\local-api-obsidian_vault"

# Clean up any existing containers
docker-compose down --remove-orphans

# Start services one by one for debugging
docker-compose up -d postgres redis
Start-Sleep -Seconds 10

docker-compose up -d obsidian-api
Start-Sleep -Seconds 10

docker-compose up -d vault-api
Start-Sleep -Seconds 10

# Check status
docker-compose ps
```

### **Step 3: Test Each Service Individually**

```powershell
# Test Obsidian API
Invoke-RestMethod "http://localhost:27123/health"

# Test Vault API (if running)
Invoke-RestMethod "http://localhost:8080/health"

# Check vault access
Invoke-RestMethod "http://localhost:27123/vault/info"
```

### **Step 4: Fix OpenAPI Integration**

```powershell
# Test OpenAPI endpoints
Invoke-RestMethod "http://localhost:8080/openapi.json"
Invoke-RestMethod "http://localhost:8080/docs"

# Update plugin config manually
$configPath = "D:\Nomade Milionario\.obsidian\plugins\openapi-renderer\config.json"
$config = Get-Content $configPath | ConvertFrom-Json
$config.apiEndpoints[0].url = "http://localhost:8080/openapi.json"
$config | ConvertTo-Json -Depth 10 | Set-Content $configPath
```

## 🚀 **Quick Commands for Immediate Testing**

### **Test Vault Access:**
```powershell
# Get vault information
Invoke-RestMethod "http://localhost:27123/vault/info"

# List files in brain_dump
Invoke-RestMethod "http://localhost:27123/files?path=brain_dump"

# Read AGENTS.md file
Invoke-RestMethod "http://localhost:27123/files/AGENTS.md"
```

### **Test MCP Tools:**
```powershell
# List available tools
Invoke-RestMethod "http://localhost:8080/api/v1/mcp/tools"

# Call list_files tool
$body = @{
    tool = "list_files"
    arguments = @{path = "brain_dump"}
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools/call" -Method POST -Body $body -ContentType "application/json"
```

### **Test Search:**
```powershell
# Search vault content
$searchBody = @{
    query = "AI"
    limit = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/v1/search" -Method POST -Body $searchBody -ContentType "application/json"
```

## 🔌 **Plugin Integration Steps**

### **1. Verify Plugin Installation:**
```powershell
# Check if plugin exists
Test-Path "D:\Nomade Milionario\.obsidian\plugins\openapi-renderer"

# Check plugin files
Get-ChildItem "D:\Nomade Milionario\.obsidian\plugins\openapi-renderer"
```

### **2. Update Plugin Configuration:**
```json
{
  "apiEndpoints": [
    {
      "name": "Obsidian Vault AI API",
      "url": "http://localhost:8080/openapi.json",
      "description": "Main API for vault operations",
      "enabled": true,
      "auth": {
        "type": "bearer",
        "token": "obsidian_secure_key_2024"
      }
    },
    {
      "name": "Obsidian Direct API", 
      "url": "http://localhost:27123/openapi.json",
      "description": "Direct vault file operations",
      "enabled": true
    }
  ],
  "settings": {
    "autoRefresh": true,
    "performanceMonitoring": true,
    "showHealthStatus": true
  }
}
```

### **3. Test Plugin Integration:**
1. **Restart Obsidian** to reload the plugin
2. **Open Command Palette** (Ctrl+P)
3. **Search for "OpenAPI"** commands
4. **Test API connections** from within Obsidian

## 📊 **Performance Optimization**

### **Container Resource Limits:**
```yaml
# Add to docker-compose.yml services
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

### **API Response Caching:**
```python
# Add to FastAPI app
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://redis:6379")
    FastAPICache.init(RedisBackend(redis), prefix="vault-api")
```

## 🔍 **Troubleshooting Common Issues**

### **Issue 1: Docker Desktop Not Starting**
```powershell
# Solution: Reset Docker Desktop
& "C:\Program Files\Docker\Docker\Docker Desktop.exe" --reset-to-factory-defaults
```

### **Issue 2: Port Conflicts**
```powershell
# Check what's using ports
netstat -ano | findstr ":8080"
netstat -ano | findstr ":27123"

# Kill processes if needed
taskkill /PID <process_id> /F
```

### **Issue 3: Vault Path Issues**
```powershell
# Check WSL mount
wsl ls -la "/mnt/d/Nomade Milionario"

# Fix permissions
wsl sudo chown -R $USER:$USER "/mnt/d/Nomade Milionario"
```

### **Issue 4: API Not Responding**
```powershell
# Check container logs
docker-compose logs vault-api
docker-compose logs obsidian-api

# Restart specific service
docker-compose restart vault-api
```

## 🎯 **Success Verification Checklist**

- [ ] Docker Desktop running and accessible
- [ ] All containers started successfully
- [ ] Obsidian API responding on port 27123
- [ ] Vault API responding on port 8080
- [ ] OpenAPI spec available at /openapi.json
- [ ] MCP tools accessible and functional
- [ ] Vault files readable through API
- [ ] Plugin configuration updated
- [ ] Obsidian plugin recognizing APIs

## 🚀 **Final Integration Test**

```powershell
# Complete integration test
Write-Host "🧪 Running integration test..."

# 1. Test basic connectivity
$health = Invoke-RestMethod "http://localhost:8080/health"
Write-Host "✅ Vault API: $($health.status)"

# 2. Test vault access
$vault = Invoke-RestMethod "http://localhost:27123/vault/info"
Write-Host "✅ Vault: $($vault.markdownFiles) files"

# 3. Test MCP tools
$tools = Invoke-RestMethod "http://localhost:8080/api/v1/mcp/tools"
Write-Host "✅ MCP Tools: $($tools.total) available"

# 4. Test file operations
$files = Invoke-RestMethod "http://localhost:27123/files?path=brain_dump"
Write-Host "✅ Brain dump: $($files.files.Count) files"

# 5. Test OpenAPI spec
$spec = Invoke-RestMethod "http://localhost:8080/openapi.json"
Write-Host "✅ OpenAPI: $($spec.info.title)"

Write-Host "🎉 Integration test complete!"
```

## 📱 **Next Steps After Integration**

1. **Test from Obsidian Plugin Interface**
2. **Create Custom API Workflows**
3. **Set Up Automated Monitoring**
4. **Configure AI Agent Workflows**
5. **Implement Custom MCP Tools**

Your system will be fully integrated and ready for advanced AI-powered vault operations!
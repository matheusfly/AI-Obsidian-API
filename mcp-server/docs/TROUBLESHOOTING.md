# 🚨 Troubleshooting & FAQ

<div align="center">

![Troubleshooting](https://img.shields.io/badge/Troubleshooting-Guide-red?style=for-the-badge&logo=bug)
![FAQ](https://img.shields.io/badge/FAQ-Complete-blue?style=for-the-badge&logo=question)
![Solutions](https://img.shields.io/badge/Solutions-Available-green?style=for-the-badge&logo=check)

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [❌ Common Issues](#-common-issues)
- [🔧 Server Issues](#-server-issues)
- [🌐 API Issues](#-api-issues)
- [🤖 CLI Issues](#-cli-issues)
- [📊 Performance Issues](#-performance-issues)
- [🔒 Security Issues](#-security-issues)
- [❓ FAQ](#-faq)

---

## 🎯 Overview

This troubleshooting guide covers common issues, solutions, and frequently asked questions for the MCP Server implementation.

### 🎯 Issue Categories

| Category | Common Issues | Solutions Available |
|----------|---------------|-------------------|
| **Server Issues** | Port conflicts, startup failures | ✅ Complete |
| **API Issues** | Connection errors, authentication | ✅ Complete |
| **CLI Issues** | Command recognition, parameter errors | ✅ Complete |
| **Performance Issues** | Slow responses, high memory usage | ✅ Complete |
| **Security Issues** | SSL errors, authentication failures | ✅ Complete |

---

## ❌ Common Issues

### 🔧 Port Already in Use

**Error:** `listen tcp :3010: bind: Only one usage of each socket address`

**Symptoms:**
- Server fails to start
- Port 3010 already in use
- Multiple server instances running

**Solutions:**
```bash
# Kill existing processes
taskkill /f /im server-real.exe
taskkill /f /im go.exe

# Check for processes using port 3010
netstat -ano | findstr :3010

# Kill specific process by PID
taskkill /f /pid [PID]

# Restart server
go run cmd/server/main.go
```

### 🔧 Nil Logger Panics

**Error:** `runtime error: invalid memory address or nil pointer dereference`

**Symptoms:**
- Server crashes on startup
- Panic in logger calls
- Nil pointer dereference errors

**Solutions:**
```bash
# Rebuild server with nil logger fixes
go build -o server-real.exe cmd/server/main.go

# Verify nil checks are implemented
grep -r "if.*logger.*nil" internal/

# Start server
.\server-real.exe
```

### 🔧 API Connection Issues

**Error:** Connection refused to Obsidian API

**Symptoms:**
- Cannot connect to Obsidian API
- 500 Internal Server Error
- Connection timeout

**Solutions:**
1. Ensure Obsidian is running
2. Check API plugin is enabled
3. Verify port 27124 is accessible
4. Check API token configuration
5. Verify firewall settings

---

## 🔧 Server Issues

### 🚀 Server Startup Issues

<details>
<summary>🔧 <strong>Server Won't Start</strong></summary>

**Problem:** Server fails to start
**Solutions:**
1. Check port availability: `netstat -ano | findstr :3010`
2. Kill existing processes: `taskkill /f /im go.exe`
3. Verify configuration: Check `config.yaml`
4. Check dependencies: `go mod tidy`
5. Rebuild server: `go build -o server-real.exe cmd/server/main.go`

</details>

<details>
<summary>🔧 <strong>Configuration Issues</strong></summary>

**Problem:** Configuration errors
**Solutions:**
1. Verify `config.yaml` format
2. Check API token validity
3. Verify Obsidian API URL
4. Check file permissions
5. Validate YAML syntax

</details>

### 🔧 Server Performance Issues

<details>
<summary>🔧 <strong>High Memory Usage</strong></summary>

**Problem:** Server using too much memory
**Solutions:**
1. Check cache size limits
2. Monitor memory usage: `tasklist /fi "imagename eq server-real.exe"`
3. Reduce cache TTL
4. Restart server periodically
5. Check for memory leaks

</details>

<details>
<summary>🔧 <strong>Slow Response Times</strong></summary>

**Problem:** Slow API responses
**Solutions:**
1. Check cache hit rate
2. Optimize cache TTL settings
3. Increase connection pool size
4. Enable request compression
5. Check network latency

</details>

---

## 🌐 API Issues

### 🔗 Connection Issues

<details>
<summary>🔧 <strong>Obsidian API Connection</strong></summary>

**Problem:** Cannot connect to Obsidian API
**Solutions:**
1. Verify Obsidian is running
2. Check API plugin status
3. Test API endpoint: `curl https://localhost:27124/health`
4. Check API token
5. Verify SSL certificate

</details>

<details>
<summary>🔧 <strong>Authentication Issues</strong></summary>

**Problem:** Authentication failures
**Solutions:**
1. Verify API token format
2. Check token permissions
3. Ensure token is not expired
4. Verify Bearer token format
5. Check token in configuration

</details>

### 🔧 API Response Issues

<details>
<summary>🔧 <strong>Empty Responses</strong></summary>

**Problem:** API returns empty results
**Solutions:**
1. Check vault has files
2. Verify file permissions
3. Check search parameters
4. Verify API endpoint
5. Check vault path configuration

</details>

<details>
<summary>🔧 <strong>Malformed Responses</strong></summary>

**Problem:** Invalid JSON responses
**Solutions:**
1. Check API response format
2. Verify tool execution
3. Check for server errors
4. Validate response schema
5. Check logging for errors

</details>

---

## 🤖 CLI Issues

### 💬 Command Recognition Issues

<details>
<summary>🔧 <strong>Unknown Commands</strong></summary>

**Problem:** Commands not recognized
**Solutions:**
1. Use exact command patterns: "list files"
2. Check available commands: `/tools`
3. Use help: `/help`
4. Try alternative variations
5. Check command syntax

</details>

<details>
<summary>🔧 <strong>Parameter Errors</strong></summary>

**Problem:** Missing or invalid parameters
**Solutions:**
1. Provide required parameters
2. Use correct parameter format
3. Check parameter examples
4. Use quoted strings for complex parameters
5. Verify parameter names

</details>

### 🔧 CLI Connection Issues

<details>
<summary>🔧 <strong>Cannot Connect to Server</strong></summary>

**Problem:** CLI cannot connect to server
**Solutions:**
1. Ensure server is running
2. Check server port (3010)
3. Verify server health
4. Check firewall settings
5. Restart both server and CLI

</details>

<details>
<summary>🔧 <strong>Response Formatting Issues</strong></summary>

**Problem:** Malformed CLI responses
**Solutions:**
1. Check server response format
2. Verify tool execution
3. Check for server errors
4. Restart CLI if persistent
5. Check CLI version compatibility

</details>

---

## 📊 Performance Issues

### ⚡ Response Time Issues

<details>
<summary>🔧 <strong>Slow Tool Execution</strong></summary>

**Problem:** Tools execute slowly
**Solutions:**
1. Check cache hit rate
2. Optimize cache TTL
3. Increase connection pool
4. Enable compression
5. Check network latency

</details>

<details>
<summary>🔧 <strong>High CPU Usage</strong></summary>

**Problem:** Server using too much CPU
**Solutions:**
1. Check for infinite loops
2. Monitor CPU usage
3. Optimize algorithms
4. Reduce concurrent requests
5. Check for resource leaks

</details>

### 💾 Memory Issues

<details>
<summary>🔧 <strong>Memory Leaks</strong></summary>

**Problem:** Memory usage increases over time
**Solutions:**
1. Check cache size limits
2. Monitor memory usage
3. Restart server periodically
4. Check for goroutine leaks
5. Optimize data structures

</details>

<details>
<summary>🔧 <strong>Cache Issues</strong></summary>

**Problem:** Cache not working properly
**Solutions:**
1. Check cache configuration
2. Verify cache TTL settings
3. Monitor cache hit rate
4. Check cache size limits
5. Clear cache if needed

</details>

---

## 🔒 Security Issues

### 🔐 Authentication Issues

<details>
<summary>🔧 <strong>Token Validation</strong></summary>

**Problem:** API token validation failures
**Solutions:**
1. Verify token format
2. Check token permissions
3. Ensure token is not expired
4. Verify token in configuration
5. Check token encoding

</details>

<details>
<summary>🔧 <strong>SSL/TLS Issues</strong></summary>

**Problem:** SSL certificate errors
**Solutions:**
1. Enable `skip_verify: true` in config
2. Add certificate to trust store
3. Use HTTP instead of HTTPS
4. Update certificate
5. Check certificate validity

</details>

### 🛡️ Security Configuration

<details>
<summary>🔧 <strong>CORS Issues</strong></summary>

**Problem:** Cross-origin request errors
**Solutions:**
1. Configure CORS policy
2. Allow specific origins
3. Check CORS headers
4. Verify request methods
5. Update CORS configuration

</details>

<details>
<summary>🔧 <strong>Rate Limiting</strong></summary>

**Problem:** Too many requests errors
**Solutions:**
1. Implement rate limiting
2. Increase rate limits
3. Check request frequency
4. Optimize request patterns
5. Add request queuing

</details>

---

## ❓ FAQ

### 🎯 General Questions

<details>
<summary>❓ <strong>How do I start the MCP server?</strong></summary>

**Answer:**
```bash
# Option 1: Use automation script
.\START_EVERYTHING.bat

# Option 2: Manual start
go run cmd/server/main.go

# Option 3: Build and run
go build -o server-real.exe cmd/server/main.go
.\server-real.exe
```

</details>

<details>
<summary>❓ <strong>How do I test the server?</strong></summary>

**Answer:**
```bash
# Test all endpoints
.\TEST_ALL.bat

# Test health only
curl http://localhost:3010/health

# Test tool execution
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"list_files_in_vault","parameters":{}}'
```

</details>

<details>
<summary>❓ <strong>How do I use the Interactive CLI?</strong></summary>

**Answer:**
```bash
# Start CLI
.\INTERACTIVE_CLI.bat

# Available commands:
# - "list files" - List all files
# - "search for [query]" - Search content
# - "read note [filename]" - Read note
# - "/help" - Show help
```

</details>

### 🔧 Technical Questions

<details>
<summary>❓ <strong>How do I configure the Obsidian API?</strong></summary>

**Answer:**
1. Enable Obsidian API plugin
2. Set API token in plugin settings
3. Configure port (default: 27124)
4. Update `config.yaml` with token and URL
5. Restart MCP server

</details>

<details>
<summary>❓ <strong>How do I add new tools?</strong></summary>

**Answer:**
1. Define tool schema in `advanced_tools.go`
2. Implement handler function
3. Register tool in `RegisterDefaultTools()`
4. Test tool with real data
5. Update documentation

</details>

<details>
<summary>❓ <strong>How do I debug issues?</strong></summary>

**Answer:**
1. Check server logs
2. Use `/status` command in CLI
3. Test individual endpoints
4. Check configuration
5. Verify external services

</details>

### 🚀 Performance Questions

<details>
<summary>❓ <strong>How do I optimize performance?</strong></summary>

**Answer:**
1. Enable caching
2. Optimize cache TTL
3. Use connection pooling
4. Enable compression
5. Monitor metrics

</details>

<details>
<summary>❓ <strong>How do I monitor the server?</strong></summary>

**Answer:**
1. Use health check endpoint
2. Monitor response times
3. Check cache hit rates
4. Monitor memory usage
5. Check error rates

</details>

---

## 🎯 Quick Solutions

### ⚡ Common Fixes

| Issue | Quick Fix |
|-------|-----------|
| **Port in use** | `taskkill /f /im go.exe` |
| **Server won't start** | `go build -o server-real.exe cmd/server/main.go` |
| **API connection failed** | Check Obsidian is running |
| **CLI won't connect** | Check server is running on port 3010 |
| **Slow responses** | Check cache hit rate |

### 🔧 Debug Commands

```bash
# Check server health
curl http://localhost:3010/health

# List available tools
curl http://localhost:3010/tools/list

# Test tool execution
curl -X POST http://localhost:3010/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"list_files_in_vault","parameters":{}}'

# Check processes
tasklist /fi "imagename eq go.exe"
netstat -ano | findstr :3010
```

---

<div align="center">

**🚨 Troubleshooting & FAQ Documentation Complete! 🚨**

[![Troubleshooting](https://img.shields.io/badge/Troubleshooting-✅%20Complete-red?style=for-the-badge)](#)
[![FAQ](https://img.shields.io/badge/FAQ-✅%20Complete-blue?style=for-the-badge)](#)
[![Solutions](https://img.shields.io/badge/Solutions-✅%20Available-green?style=for-the-badge)](#)

**CENTRALIZED REPORTS & CHANGELOG SYSTEM COMPLETE!**

</div>

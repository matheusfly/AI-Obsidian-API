# 🚀 Launch Guide - Obsidian Vault AI System

## 📋 Quick Start

### 1. **Prerequisites Check**
```powershell
# Ensure you're in the project directory
cd "d:\codex\master_code\backend_ops\local-api-obsidian_vault"

# Check PowerShell execution policy
Get-ExecutionPolicy
# If restricted, run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. **Environment Setup**
```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env file with your settings
notepad .env
```

### 3. **Launch System**
```powershell
# Interactive launch (recommended for first time)
.\scripts\launch.ps1 -Interactive

# Or direct start
.\scripts\launch.ps1 -Action start
```

---

## 🎮 Available Launch Commands

### **Main Launch Script** (`.\scripts\launch.ps1`)

#### **Interactive Mode** (Recommended)
```powershell
.\scripts\launch.ps1 -Interactive
```
**Features:**
- ✅ Full interactive CLI with help system
- ✅ Real-time service monitoring
- ✅ Built-in troubleshooting
- ✅ Easy command discovery

#### **Direct Actions**
```powershell
# Start all services
.\scripts\launch.ps1 -Action start

# Stop all services
.\scripts\launch.ps1 -Action stop

# Restart services
.\scripts\launch.ps1 -Action restart

# Check service status
.\scripts\launch.ps1 -Action status

# Test service health
.\scripts\launch.ps1 -Action health

# Test API endpoints
.\scripts\launch.ps1 -Action test

# Show MCP tools
.\scripts\launch.ps1 -Action tools

# View logs
.\scripts\launch.ps1 -Action logs

# Verbose output
.\scripts\launch.ps1 -Action start -Verbose

# Skip health checks (faster startup)
.\scripts\launch.ps1 -Action start -SkipHealthCheck
```

---

## 🔧 Vault CLI Tool (`.\scripts\vault-cli.ps1`)

### **Interactive Mode** (Best for exploration)
```powershell
.\scripts\vault-cli.ps1 -Interactive
```

**Available Commands in Interactive Mode:**
```
health                     - Check vault health
tools                      - List MCP tools
notes [folder] [limit]     - List notes
search <query> [semantic]  - Search notes
create <path> <content>    - Create note
read <path>                - Read note
call <tool> [args...]      - Call MCP tool
workflows                  - List workflows
config [key] [value]       - Configuration
verbose                    - Toggle verbose mode
```

### **Direct Commands**
```powershell
# Check system health
.\scripts\vault-cli.ps1 -Command health

# List available MCP tools
.\scripts\vault-cli.ps1 -Command tools

# List notes
.\scripts\vault-cli.ps1 -Command notes

# Search notes
.\scripts\vault-cli.ps1 -Command search -Query "machine learning"

# Create a note
.\scripts\vault-cli.ps1 -Command create -Path "test/new-note.md" -Content "# Test Note"

# Call MCP tool
.\scripts\vault-cli.ps1 -Command call -Tool read_file -Arguments @{path="notes/example.md"}

# With API key
.\scripts\vault-cli.ps1 -Command health -ApiKey "your_api_key"

# Different base URL
.\scripts\vault-cli.ps1 -Command health -BaseUrl "http://localhost:8080"
```

---

## 🎯 Common Usage Scenarios

### **Scenario 1: First Time Setup**
```powershell
# 1. Check prerequisites and start system
.\scripts\launch.ps1 -Interactive

# In interactive mode, type:
start      # Start all services
health     # Check service health
access     # Show access points
test       # Test API endpoints
```

### **Scenario 2: Daily Operations**
```powershell
# Quick start
.\scripts\launch.ps1 -Action start

# Check what's running
.\scripts\launch.ps1 -Action status

# Use vault CLI for operations
.\scripts\vault-cli.ps1 -Interactive
```

### **Scenario 3: Development & Testing**
```powershell
# Start with verbose logging
.\scripts\launch.ps1 -Action start -Verbose

# Test specific functionality
.\scripts\vault-cli.ps1 -Command tools -Verbose
.\scripts\vault-cli.ps1 -Command search -Query "test" -Verbose

# Monitor logs
.\scripts\launch.ps1 -Action logs
```

### **Scenario 4: Troubleshooting**
```powershell
# Check system health
.\scripts\launch.ps1 -Action health

# View service status
.\scripts\launch.ps1 -Action status

# Check specific service logs
# In interactive mode: logs vault-api
.\scripts\launch.ps1 -Interactive
```

---

## 🔍 System Access Points

After successful launch, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Vault API** | http://localhost:8080 | Main API server |
| **API Docs** | http://localhost:8080/docs | Interactive API documentation |
| **n8n Workflows** | http://localhost:5678 | Workflow automation |
| **Obsidian API** | http://localhost:27123 | Direct Obsidian interface |
| **Grafana** | http://localhost:3000 | Monitoring dashboards |
| **Prometheus** | http://localhost:9090 | Metrics collection |

---

## 🧪 Quick API Tests

### **PowerShell Tests**
```powershell
# Test basic connectivity
Invoke-RestMethod -Uri "http://localhost:8080/health"

# List MCP tools
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools"

# Search notes (requires auth)
$headers = @{Authorization = "Bearer your_token"}
$body = @{query="test"; limit=5} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/search" -Method POST -Body $body -ContentType "application/json" -Headers $headers
```

### **cURL Tests**
```bash
# Health check
curl http://localhost:8080/health

# MCP tools
curl http://localhost:8080/api/v1/mcp/tools

# Call MCP tool
curl -X POST http://localhost:8080/api/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"tool":"list_files","arguments":{"path":"daily","pattern":"*.md"}}'
```

---

## 🛠️ MCP Tools Quick Reference

### **File Operations**
```powershell
# Read file
.\scripts\vault-cli.ps1 -Command call -Tool read_file -Arguments @{path="notes/example.md"}

# Write file
.\scripts\vault-cli.ps1 -Command call -Tool write_file -Arguments @{path="test.md"; content="# Test"}

# List files
.\scripts\vault-cli.ps1 -Command call -Tool list_files -Arguments @{path="daily"; pattern="*.md"}
```

### **Search Operations**
```powershell
# Content search
.\scripts\vault-cli.ps1 -Command call -Tool search_content -Arguments @{query="machine learning"; limit=5}
```

### **Note Operations**
```powershell
# Create daily note
.\scripts\vault-cli.ps1 -Command call -Tool create_daily_note -Arguments @{date="2024-01-15"}

# Extract links
.\scripts\vault-cli.ps1 -Command call -Tool extract_links -Arguments @{path="research/paper.md"}
```

### **AI Operations**
```powershell
# Summarize note
.\scripts\vault-cli.ps1 -Command call -Tool summarize_note -Arguments @{path="meetings/long-meeting.md"; max_length=150}

# Generate tags
.\scripts\vault-cli.ps1 -Command call -Tool generate_tags -Arguments @{path="articles/article.md"; max_tags=5}
```

---

## 🔧 Configuration

### **Environment Variables** (`.env` file)
```bash
# Required
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_VAULT_PATH=/mnt/d/Nomade Milionario

# Optional but recommended
N8N_USER=admin
N8N_PASSWORD=secure_password
POSTGRES_PASSWORD=secure_db_password
REDIS_PASSWORD=secure_redis_password

# AI Services (optional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### **PowerShell Execution Policy**
If you get execution policy errors:
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or for current process only
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Docker Not Running**
```powershell
# Check Docker status
docker --version
docker info

# Start Docker Desktop if needed
```

#### **2. Port Conflicts**
```powershell
# Check what's using ports
netstat -an | findstr ":8080"
netstat -an | findstr ":5678"

# Kill processes if needed
# Use Task Manager or: taskkill /PID <process_id> /F
```

#### **3. Vault Path Issues**
```powershell
# Check if vault path exists
Test-Path "D:\Nomade Milionario"

# Check WSL mount (if using WSL)
wsl ls -la "/mnt/d/Nomade Milionario"
```

#### **4. Service Health Issues**
```powershell
# Check service logs
.\scripts\launch.ps1 -Action logs

# Or in interactive mode
.\scripts\launch.ps1 -Interactive
# Then type: logs [service-name]
```

### **Debug Mode**
```powershell
# Start with verbose output
.\scripts\launch.ps1 -Action start -Verbose

# Use vault CLI with verbose
.\scripts\vault-cli.ps1 -Command health -Verbose
```

---

## 📚 Next Steps

1. **Explore Interactive Mode**: Start with `.\scripts\launch.ps1 -Interactive`
2. **Test MCP Tools**: Use `.\scripts\vault-cli.ps1 -Interactive` and type `tools`
3. **Check API Docs**: Visit http://localhost:8080/docs
4. **Set Up Workflows**: Access n8n at http://localhost:5678
5. **Monitor System**: Check Grafana at http://localhost:3000

---

## 🎯 Pro Tips

- **Use Interactive Mode** for learning and exploration
- **Set up aliases** for frequently used commands
- **Monitor logs** during development with `logs` command
- **Use verbose mode** when troubleshooting
- **Check health regularly** with `health` command
- **Explore MCP tools** - they're the key to AI automation

---

**🎉 You're ready to launch your Obsidian Vault AI system!**

Start with: `.\scripts\launch.ps1 -Interactive`
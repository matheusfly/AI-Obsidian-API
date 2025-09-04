# Quick Start Guide

Get up and running with the Obsidian Vault AI System in under 5 minutes.

## Prerequisites

- Docker Desktop installed and running
- PowerShell 7+ (Windows) or Bash (Linux/Mac)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/obsidian-vault-ai-system.git
cd obsidian-vault-ai-system
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
notepad .env  # Windows
# or
nano .env     # Linux/Mac
```

### 3. Configure Your Vault Path

Edit the `.env` file and set your Obsidian vault path:

```env
OBSIDIAN_VAULT_PATH=D:\Your\Obsidian\Vault
```

## Quick Launch

### Option 1: Ultra-Fast Launch (Recommended)

```powershell
# Windows PowerShell
.\launchers\UV_ULTRA_LAUNCHER.ps1

# Or use the production launcher
.\launchers\PRODUCTION_CLI.ps1
```

### Option 2: Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 3: Native Services

```powershell
# Start native services (faster development)
.\scripts\start-native-servers.ps1 -VaultPath "D:\Your\Obsidian\Vault"
```

## Verify Installation

### 1. Check Service Health

```bash
# Check all services
curl http://localhost:8085/health  # Vault API
curl http://localhost:27123/health # Obsidian API
curl http://localhost:5678/        # n8n
```

### 2. Test API Endpoints

```bash
# List vault files
curl -H "Authorization: Bearer your-token" http://localhost:8085/vault/files

# Generate content
curl -X POST http://localhost:8085/ai/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"prompt": "Hello, AI!"}'
```

### 3. Access Web Interfaces

- **Vault API**: [http://localhost:8085](http://localhost:8085)
- **Obsidian API**: [http://localhost:27123](http://localhost:27123)
- **n8n Workflows**: [http://localhost:5678](http://localhost:5678)
- **Grafana Monitoring**: [http://localhost:3004](http://localhost:3004)

## First Steps

### 1. Explore Your Vault

```python
# Python example
import requests

# Get vault files
response = requests.get(
    "http://localhost:8085/vault/files",
    headers={"Authorization": "Bearer your-token"}
)
files = response.json()
print(f"Found {len(files['files'])} files in your vault")
```

### 2. Generate AI Content

```python
# Generate content based on your vault
response = requests.post(
    "http://localhost:8085/ai/generate",
    headers={
        "Authorization": "Bearer your-token",
        "Content-Type": "application/json"
    },
    json={
        "prompt": "Summarize my notes about machine learning",
        "context_files": ["notes/ml-basics.md"]
    }
)
content = response.json()
print(content["content"])
```

### 3. Set Up MCP Tools

```python
# List available MCP tools
response = requests.get(
    "http://localhost:8085/mcp/tools",
    headers={"Authorization": "Bearer your-token"}
)
tools = response.json()
print("Available MCP tools:", [tool["name"] for tool in tools["tools"]])
```

## Common Issues

### Port Conflicts

If you get port conflicts, check what's using the ports:

```powershell
# Windows
Get-NetTCPConnection -LocalPort 8085 -State Listen

# Kill process if needed
Stop-Process -Id <PID> -Force
```

### Docker Issues

```bash
# Reset Docker containers
docker-compose down -v
docker system prune -f
docker-compose up -d
```

### Permission Issues

```bash
# Fix file permissions (Linux/Mac)
sudo chown -R $USER:$USER .
chmod -R 755 .
```

## Next Steps

1. **Read the [Configuration Guide](configuration)** to customize your setup
2. **Explore [API Documentation](../api/overview)** for detailed endpoint information
3. **Check out [Architecture Overview](../architecture/overview)** to understand the system
4. **Set up [Monitoring](../deployment/monitoring)** for production use

## Getting Help

- **Documentation**: [Full docs](../intro)
- **GitHub Issues**: [Report bugs](https://github.com/your-org/obsidian-vault-ai-system/issues)
- **Discord**: [Join community](https://discord.gg/your-discord)
- **Stack Overflow**: [Ask questions](https://stackoverflow.com/questions/tagged/obsidian-vault-ai)

## What's Next?

Now that you have the system running, you can:

- **Create workflows** in n8n for automation
- **Set up monitoring** with Grafana dashboards
- **Integrate MCP tools** for enhanced AI capabilities
- **Deploy to production** using the deployment guides

Happy automating! 🚀

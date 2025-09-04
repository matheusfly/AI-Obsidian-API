# 🚀 Quick Start Guide - Get Running in 5 Minutes!

## Prerequisites Check ✅

```bash
# Check Docker
docker --version

# Check Docker Compose
docker-compose --version

# Check WSL2 (Windows)
wsl --list --verbose
```

## 1. Environment Setup (2 minutes)

```bash
# Clone and navigate
cd d:\codex\master_code\backend_ops\local-api-obsidian_vault

# Copy environment template
copy .env.example .env

# Edit .env file - REQUIRED!
notepad .env
```

**Essential .env Configuration:**
```bash
# MUST CHANGE THESE
OBSIDIAN_API_KEY=your_secure_api_key_here
OBSIDIAN_VAULT_PATH=/mnt/d/Nomade Milionario

# Generated automatically by setup.sh
N8N_PASSWORD=auto_generated
POSTGRES_PASSWORD=auto_generated
```

## 2. Quick Launch (1 minute)

```bash
# Make setup executable
chmod +x setup.sh

# Run setup (creates directories, generates passwords)
./setup.sh

# Start the system
docker-compose up -d
```

## 3. Verify System (1 minute)

```bash
# Check all services
docker-compose ps

# Test API endpoints
curl http://localhost:8080/health
curl http://localhost:27123/health
```

## 4. Access Points (1 minute)

| Service | URL | Purpose |
|---------|-----|---------|
| **Vault API** | http://localhost:8080 | Main API endpoints |
| **n8n** | http://localhost:5678 | Workflow automation |
| **Obsidian API** | http://localhost:27123 | Direct vault access |
| **API Docs** | http://localhost:8080/docs | Interactive API documentation |

## 🎯 First API Test

```bash
# Get API status
curl http://localhost:8080/

# List notes (requires API key)
curl -H "Authorization: Bearer your_api_key" http://localhost:8080/api/v1/notes

# Create a test note
curl -X POST http://localhost:8080/api/v1/notes \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "test/api-test.md",
    "content": "# API Test\n\nThis note was created via API!",
    "tags": ["test", "api"]
  }'
```

## 🔧 Daily Operations

### Start System
```bash
./scripts/start.sh
```

### Stop System
```bash
./scripts/stop.sh
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f vault-api
```

### Restart Service
```bash
docker-compose restart vault-api
```

## 📊 API Endpoints Reference

### Core Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/` | API status | `curl localhost:8080/` |
| GET | `/health` | Health check | `curl localhost:8080/health` |
| GET | `/api/v1/notes` | List notes | `curl -H "Auth: Bearer key" localhost:8080/api/v1/notes` |
| POST | `/api/v1/notes` | Create note | See example above |
| GET | `/api/v1/notes/{path}` | Get note | `curl -H "Auth: Bearer key" localhost:8080/api/v1/notes/test.md` |
| POST | `/api/v1/search` | Search notes | `curl -X POST -H "Auth: Bearer key" -d '{"query":"test"}' localhost:8080/api/v1/search` |

### AI Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/process` | Process with AI |
| GET | `/api/v1/workflows` | List n8n workflows |

## 🐛 Troubleshooting

### Port Conflicts
```bash
# Check what's using port
netstat -ano | findstr :8080

# Kill process
taskkill /PID <PID> /F
```

### Volume Mount Issues
```bash
# Check WSL mount
ls -la /mnt/d/

# Fix permissions
sudo chown -R $USER:$USER "/mnt/d/Nomade Milionario"
```

### Service Not Starting
```bash
# Check logs
docker-compose logs service-name

# Restart specific service
docker-compose restart service-name

# Rebuild if needed
docker-compose build service-name
```

### API Key Issues
```bash
# Check environment variables
docker-compose exec vault-api env | grep API_KEY

# Update API key
# Edit .env file and restart
docker-compose restart vault-api
```

## 🔄 Next Steps

1. **Test API Endpoints** - Use the examples above
2. **Create n8n Workflows** - Visit http://localhost:5678
3. **Set up Obsidian Plugin** - Install Local REST API plugin
4. **Configure AI Models** - Add OpenAI/Anthropic keys to .env
5. **Create Daily Workflows** - Set up automated note processing

## 📱 Mobile Testing

```bash
# Test from mobile device (replace IP)
curl http://192.168.1.100:8080/health

# Enable mobile access in .env
MOBILE_API_ENABLED=true
```

## 🔐 Security Notes

- **Change default API keys** in .env
- **Use HTTPS** in production
- **Restrict network access** if needed
- **Monitor logs** for suspicious activity

## 📚 Documentation Links

- **Full API Docs**: http://localhost:8080/docs
- **n8n Documentation**: http://localhost:5678 (after login)
- **System Architecture**: See COMPLETE_BACKEND_ENGINEERING_ROADMAP.md
- **Advanced Features**: See ADVANCED_AI_AGENTS_IMPLEMENTATION.md

---

**🎉 You're now running a complete AI-powered Obsidian automation system!**

**Need help?** Check the logs with `docker-compose logs -f` or refer to the troubleshooting section above.
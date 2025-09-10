---
sidebar_position: 1
---

# Installation Guide

Get the Obsidian Vault AI Automation System up and running on your machine in minutes.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: 10GB free space
- **Network**: Internet connection for AI services

### Required Software
- **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/)
- **Git**: [Download here](https://git-scm.com/downloads)
- **Node.js 18+**: [Download here](https://nodejs.org/)
- **Python 3.11+**: [Download here](https://www.python.org/downloads/)

### Optional Software
- **Obsidian**: [Download here](https://obsidian.md/)
- **VS Code**: [Download here](https://code.visualstudio.com/)
- **Postman**: [Download here](https://www.postman.com/)

## 🚀 Quick Installation

### Method 1: Automated Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/obsidian-vault-ai-system.git
   cd obsidian-vault-ai-system
   ```

2. **Run the automated installer**
   ```bash
   # Windows
   .\scripts\quick-start.ps1
   
   # macOS/Linux
   ./scripts/quick-start.sh
   ```

3. **Access the system**
   - API: http://localhost:8080
   - Web Interface: http://localhost:3000
   - n8n Workflows: http://localhost:5678

### Method 2: Manual Setup

1. **Clone and navigate to the repository**
   ```bash
   git clone https://github.com/your-org/obsidian-vault-ai-system.git
   cd obsidian-vault-ai-system
   ```

2. **Install dependencies**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Node.js dependencies
   npm install
   ```

3. **Configure environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit configuration
   nano .env  # or use your preferred editor
   ```

4. **Start services**
   ```bash
   # Start with Docker Compose
   docker-compose up -d
   
   # Or start individual services
   python vault-api/main.py &
   node services/obsidian-api/server.js &
   npx n8n start &
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Obsidian Configuration
OBSIDIAN_API_KEY=your_obsidian_api_key
OBSIDIAN_VAULT_PATH=/path/to/your/vault

# n8n Configuration
N8N_USER=admin
N8N_PASSWORD=your_secure_password
N8N_ENCRYPTION_KEY=your_32_character_encryption_key

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=obsidian_vault_ai

# Redis Configuration
REDIS_PASSWORD=your_redis_password

# AI API Keys
OPENAI_API_KEY=sk-your_openai_api_key
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key

# Monitoring
GRAFANA_USER=admin
GRAFANA_PASSWORD=your_grafana_password
```

### Obsidian Vault Setup

1. **Create or select your Obsidian vault**
   ```bash
   # Create a new vault
   mkdir ~/MyObsidianVault
   
   # Or use an existing vault
   # Update OBSIDIAN_VAULT_PATH in .env
   ```

2. **Install required Obsidian plugins**
   - **Obsidian API Plugin**: For API integration
   - **OpenAPI Renderer Plugin**: For interactive API docs
   - **Templater Plugin**: For advanced templating

3. **Configure Obsidian API Plugin**
   ```json
   {
     "apiKey": "your_obsidian_api_key",
     "enabled": true,
     "port": 27123,
     "cors": true
   }
   ```

## 🔧 Service Configuration

### Vault API Service
```yaml
# vault-api/config.yaml
server:
  host: "0.0.0.0"
  port: 8080
  workers: 4

database:
  url: "postgresql://user:password@localhost:5432/obsidian_vault_ai"
  pool_size: 10

ai:
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-sonnet"
```

### n8n Workflow Engine
```json
{
  "database": {
    "type": "postgresdb",
    "host": "localhost",
    "port": 5432,
    "username": "postgres",
    "password": "your_password",
    "database": "n8n"
  },
  "credentials": {
    "overwrite": {
      "data": {
        "encryptionKey": "your_encryption_key"
      }
    }
  }
}
```

### Monitoring Stack
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'vault-api'
    static_configs:
      - targets: ['localhost:8080']
  
  - job_name: 'n8n'
    static_configs:
      - targets: ['localhost:5678']
```

## 🐳 Docker Setup

### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  vault-api:
    build: ./vault-api
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/obsidian_vault_ai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=obsidian_vault_ai
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    command: redis-server --requirepass password
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Build and Run
```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 🧪 Verification

### Health Checks
```bash
# Check API health
curl http://localhost:8080/health

# Check n8n status
curl http://localhost:5678/healthz

# Check database connection
docker-compose exec postgres psql -U postgres -d obsidian_vault_ai -c "SELECT 1;"
```

### Test API Endpoints
```bash
# Test note creation
curl -X POST "http://localhost:8080/api/v1/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Note",
    "content": "This is a test note",
    "path": "test/test-note.md"
  }'

# Test search functionality
curl -X POST "http://localhost:8080/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test",
    "limit": 10
  }'
```

### Verify AI Integration
```bash
# Test AI content analysis
curl -X POST "http://localhost:8080/api/v1/ai/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a test document for AI analysis",
    "analysis_type": "sentiment"
  }'
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
netstat -ano | findstr :8080

# Kill process (Windows)
taskkill /PID <process_id> /F

# Kill process (macOS/Linux)
kill -9 <process_id>
```

#### 2. Docker Issues
```bash
# Reset Docker
docker system prune -a

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 3. Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready

# Reset database
docker-compose down -v
docker-compose up -d
```

#### 4. AI API Key Issues
```bash
# Test API keys
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

### Logs and Debugging

#### View Service Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f vault-api

# Last 100 lines
docker-compose logs --tail=100 vault-api
```

#### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=true

# Restart services
docker-compose restart
```

## 📚 Next Steps

After successful installation:

1. **[Quick Start Guide](/docs/getting-started/quick-start)**: Learn the basics
2. **[Configuration Guide](/docs/getting-started/configuration)**: Customize your setup
3. **[First Workflow](/docs/getting-started/first-workflow)**: Create your first automation
4. **[API Reference](/docs/api/overview)**: Explore the API
5. **[Architecture Guide](/docs/architecture/overview)**: Understand the system

## 🆘 Getting Help

- **Documentation**: Browse our comprehensive guides
- **GitHub Issues**: [Report bugs and request features](https://github.com/your-org/obsidian-vault-ai-system/issues)
- **Discord Community**: [Join our Discord](https://discord.gg/your-discord)
- **Email Support**: [Contact us](mailto:support@your-domain.com)

---

**🎉 Congratulations!** You've successfully installed the Obsidian Vault AI Automation System. Now let's explore what you can do with it!

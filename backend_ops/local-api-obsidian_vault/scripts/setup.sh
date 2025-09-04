#!/bin/bash

# Obsidian Vault AI System Setup Script
# This script sets up the complete backend engineering environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running on WSL
check_wsl() {
    if grep -q Microsoft /proc/version; then
        log "Running on WSL - Good!"
        return 0
    else
        warn "Not running on WSL. Some features may not work as expected."
        return 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker Desktop for Windows."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose."
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        error "Docker is not running. Please start Docker Desktop."
    fi
    
    log "All prerequisites met!"
}

# Create directory structure
create_directories() {
    log "Creating directory structure..."
    
    directories=(
        "obsidian-api"
        "vault-api"
        "file-watcher"
        "n8n/workflows"
        "n8n/credentials"
        "config/obsidian"
        "nginx"
        "nginx/ssl"
        "nginx/logs"
        "monitoring"
        "monitoring/grafana/provisioning/dashboards"
        "monitoring/grafana/provisioning/datasources"
        "postgres/init"
        "logs"
        "backups"
        "scripts"
        "tests"
        "docs"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log "Created directory: $dir"
    done
}

# Generate secure passwords and keys
generate_secrets() {
    log "Generating secure passwords and keys..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        
        # Generate random passwords
        POSTGRES_PASSWORD=$(openssl rand -base64 32)
        REDIS_PASSWORD=$(openssl rand -base64 32)
        N8N_PASSWORD=$(openssl rand -base64 16)
        GRAFANA_PASSWORD=$(openssl rand -base64 16)
        N8N_ENCRYPTION_KEY=$(openssl rand -base64 32)
        JWT_SECRET_KEY=$(openssl rand -base64 64)
        API_SECRET_KEY=$(openssl rand -base64 64)
        
        # Update .env file
        sed -i "s/your_postgres_password_here/$POSTGRES_PASSWORD/g" .env
        sed -i "s/your_redis_password_here/$REDIS_PASSWORD/g" .env
        sed -i "s/your_secure_password_here/$N8N_PASSWORD/g" .env
        sed -i "s/your_grafana_password_here/$GRAFANA_PASSWORD/g" .env
        sed -i "s/your_32_character_encryption_key_here/$N8N_ENCRYPTION_KEY/g" .env
        sed -i "s/your_jwt_secret_key_here/$JWT_SECRET_KEY/g" .env
        sed -i "s/your_api_secret_key_here/$API_SECRET_KEY/g" .env
        
        log "Generated .env file with secure passwords"
        warn "Please update the .env file with your actual API keys and configuration"
    else
        log ".env file already exists, skipping generation"
    fi
}

# Create Obsidian API Dockerfile
create_obsidian_api_dockerfile() {
    log "Creating Obsidian API Dockerfile..."
    
    cat > obsidian-api/Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache curl

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S obsidian -u 1001

# Change ownership of app directory
RUN chown -R obsidian:nodejs /app

USER obsidian

EXPOSE 27123 27124

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:27123/health || exit 1

CMD ["node", "server.js"]
EOF
}

# Create Vault API Dockerfile
create_vault_api_dockerfile() {
    log "Creating Vault API Dockerfile..."
    
    cat > vault-api/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

USER app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF
}

# Create File Watcher Dockerfile
create_file_watcher_dockerfile() {
    log "Creating File Watcher Dockerfile..."
    
    cat > file-watcher/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    inotify-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash watcher && \
    chown -R watcher:watcher /app

USER watcher

CMD ["python", "watcher.py"]
EOF
}

# Create Nginx configuration
create_nginx_config() {
    log "Creating Nginx configuration..."
    
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream vault_api {
        server vault-api:8080;
    }
    
    upstream n8n {
        server n8n:5678;
    }
    
    upstream grafana {
        server grafana:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Vault API
        location /api/ {
            proxy_pass http://vault_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # n8n
        location /n8n/ {
            proxy_pass http://n8n/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "upgrade";
            proxy_set_header Upgrade $http_upgrade;
        }
        
        # Grafana
        location /grafana/ {
            proxy_pass http://grafana/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF
}

# Create Prometheus configuration
create_prometheus_config() {
    log "Creating Prometheus configuration..."
    
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'vault-api'
    static_configs:
      - targets: ['vault-api:8080']
    metrics_path: '/metrics'

  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
}

# Create Grafana datasource configuration
create_grafana_config() {
    log "Creating Grafana configuration..."
    
    mkdir -p monitoring/grafana/provisioning/datasources
    cat > monitoring/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
}

# Create startup script
create_startup_script() {
    log "Creating startup script..."
    
    cat > scripts/start.sh << 'EOF'
#!/bin/bash

# Start the Obsidian Vault AI System

set -e

log() {
    echo -e "\033[0;32m[$(date +'%Y-%m-%d %H:%M:%S')] $1\033[0m"
}

log "Starting Obsidian Vault AI System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please run setup.sh first."
    exit 1
fi

# Pull latest images
log "Pulling latest Docker images..."
docker-compose pull

# Start services
log "Starting services..."
docker-compose up -d

# Wait for services to be ready
log "Waiting for services to be ready..."
sleep 30

# Check service health
log "Checking service health..."
docker-compose ps

log "System started successfully!"
log "Access points:"
log "  - n8n: http://localhost:5678"
log "  - Vault API: http://localhost:8080"
log "  - Grafana: http://localhost:3000"
log "  - Prometheus: http://localhost:9090"
EOF

    chmod +x scripts/start.sh
}

# Create stop script
create_stop_script() {
    log "Creating stop script..."
    
    cat > scripts/stop.sh << 'EOF'
#!/bin/bash

# Stop the Obsidian Vault AI System

set -e

log() {
    echo -e "\033[0;32m[$(date +'%Y-%m-%d %H:%M:%S')] $1\033[0m"
}

log "Stopping Obsidian Vault AI System..."

# Stop services
docker-compose down

log "System stopped successfully!"
EOF

    chmod +x scripts/stop.sh
}

# Create backup script
create_backup_script() {
    log "Creating backup script..."
    
    cat > scripts/backup.sh << 'EOF'
#!/bin/bash

# Backup Obsidian Vault AI System

set -e

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

log() {
    echo -e "\033[0;32m[$(date +'%Y-%m-%d %H:%M:%S')] $1\033[0m"
}

log "Creating backup in $BACKUP_DIR..."

# Backup Docker volumes
docker run --rm -v obsidian_n8n_data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/n8n_data.tar.gz -C /data .
docker run --rm -v obsidian_postgres_data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
docker run --rm -v obsidian_chroma_data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/chroma_data.tar.gz -C /data .

# Backup configuration
cp -r config "$BACKUP_DIR/"
cp .env "$BACKUP_DIR/"
cp docker-compose.yml "$BACKUP_DIR/"

log "Backup completed: $BACKUP_DIR"
EOF

    chmod +x scripts/backup.sh
}

# Create requirements files
create_requirements_files() {
    log "Creating requirements files..."
    
    # Vault API requirements
    cat > vault-api/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
httpx==0.25.2
aiofiles==23.2.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
sqlalchemy==2.0.23
alembic==1.13.0
asyncpg==0.29.0
redis==5.0.1
sentence-transformers==2.2.2
chromadb==0.4.18
openai==1.3.7
anthropic==0.7.7
google-generativeai==0.3.2
watchdog==3.0.0
prometheus-client==0.19.0
structlog==23.2.0
tenacity==8.2.3
PyYAML==6.0.1
markdown==3.5.1
python-dotenv==1.0.0
EOF

    # File Watcher requirements
    cat > file-watcher/requirements.txt << 'EOF'
watchdog==3.0.0
aiohttp==3.9.1
asyncio==3.4.3
python-dotenv==1.0.0
structlog==23.2.0
EOF

    # Obsidian API package.json
    cat > obsidian-api/package.json << 'EOF'
{
  "name": "obsidian-api-server",
  "version": "1.0.0",
  "description": "Obsidian Local REST API Server",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "morgan": "^1.10.0",
    "dotenv": "^16.3.1",
    "fs-extra": "^11.1.1",
    "chokidar": "^3.5.3",
    "markdown-it": "^13.0.2",
    "gray-matter": "^4.0.3",
    "uuid": "^9.0.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
EOF
}

# Main setup function
main() {
    log "Starting Obsidian Vault AI System Setup..."
    
    check_wsl
    check_prerequisites
    create_directories
    generate_secrets
    create_obsidian_api_dockerfile
    create_vault_api_dockerfile
    create_file_watcher_dockerfile
    create_nginx_config
    create_prometheus_config
    create_grafana_config
    create_startup_script
    create_stop_script
    create_backup_script
    create_requirements_files
    
    log "Setup completed successfully!"
    log ""
    log "Next steps:"
    log "1. Update the .env file with your API keys and configuration"
    log "2. Ensure your Obsidian vault path is correct in docker-compose.yml"
    log "3. Run './scripts/start.sh' to start the system"
    log ""
    log "Access points after startup:"
    log "  - n8n: http://localhost:5678"
    log "  - Vault API: http://localhost:8080"
    log "  - Grafana: http://localhost:3000"
    log "  - Prometheus: http://localhost:9090"
}

# Run main function
main "$@"
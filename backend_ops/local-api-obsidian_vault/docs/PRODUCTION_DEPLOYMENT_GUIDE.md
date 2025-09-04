# Production Deployment Guide

## Overview
Complete guide for deploying the Obsidian Vault AI automation system in production environments with high availability, security, and monitoring.

## Pre-Deployment Checklist

### System Requirements
- **OS**: Windows 11 with WSL2 or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: SSD with 100GB+ free space
- **CPU**: 4+ cores recommended
- **Network**: Stable internet connection for initial setup

### Software Dependencies
- [x] Docker Desktop (Windows) or Docker Engine (Linux)
- [x] Docker Compose v2.0+
- [x] Git 2.30+
- [x] Node.js 18+ (for development)
- [x] Python 3.9+ (for development)

### Security Prerequisites
- [x] SSL certificates for HTTPS
- [x] Firewall configuration
- [x] Backup storage location
- [x] Monitoring infrastructure
- [x] Log aggregation system

## Production Configuration

### Environment Variables (.env.prod)
```bash
# Production Environment
NODE_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Vault Configuration
OBSIDIAN_VAULT_PATH=/mnt/d/Nomade Milionario
VAULT_BACKUP_PATH=/backups/vault
VAULT_ENCRYPTION_KEY=your_32_character_encryption_key

# API Configuration
OBSIDIAN_API_KEY=prod_api_key_here
VAULT_API_JWT_SECRET=your_jwt_secret_256_bits
API_RATE_LIMIT=1000
API_TIMEOUT=30

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=obsidian_vault_prod
POSTGRES_USER=vault_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_SSL_MODE=require

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_secure_password
REDIS_SSL=true

# n8n Configuration
N8N_HOST=n8n
N8N_PORT=5678
N8N_USER=admin
N8N_PASSWORD=secure_n8n_password
N8N_ENCRYPTION_KEY=32_character_n8n_encryption_key
N8N_WEBHOOK_URL=https://your-domain.com/webhook

# AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OLLAMA_HOST=ollama
OLLAMA_PORT=11434

# Vector Database
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000
CHROMADB_PERSIST_DIRECTORY=/data/chromadb

# Monitoring
PROMETHEUS_HOST=prometheus
PROMETHEUS_PORT=9090
GRAFANA_HOST=grafana
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=secure_grafana_password

# SSL/TLS
SSL_CERT_PATH=/certs/fullchain.pem
SSL_KEY_PATH=/certs/privkey.pem
SSL_ENABLED=true

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
BACKUP_ENCRYPTION=true
BACKUP_S3_BUCKET=your-backup-bucket
BACKUP_S3_REGION=us-east-1

# Security
CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com
TRUSTED_PROXIES=10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
SECURITY_HEADERS=true
RATE_LIMITING=true

# Performance
WORKER_PROCESSES=4
MAX_CONNECTIONS=1000
CACHE_TTL=3600
COMPRESSION_ENABLED=true
```

### Docker Compose Production (docker-compose.prod.yml)
```yaml
version: '3.8'

services:
  # Reverse Proxy & Load Balancer
  nginx:
    image: nginx:alpine
    container_name: obsidian-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certs:/etc/nginx/certs:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - vault-api
      - obsidian-api
      - n8n
      - grafana
    restart: unless-stopped
    networks:
      - obsidian-network

  # Vault API (Multiple instances for HA)
  vault-api-1:
    build:
      context: ./vault-api
      dockerfile: Dockerfile.prod
    container_name: obsidian-vault-api-1
    env_file: .env.prod
    volumes:
      - "${OBSIDIAN_VAULT_PATH}:/vault:rw"
      - "./logs/vault-api:/app/logs"
      - "./cache:/app/cache"
    depends_on:
      - postgres
      - redis
      - chromadb
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - obsidian-network

  vault-api-2:
    build:
      context: ./vault-api
      dockerfile: Dockerfile.prod
    container_name: obsidian-vault-api-2
    env_file: .env.prod
    volumes:
      - "${OBSIDIAN_VAULT_PATH}:/vault:rw"
      - "./logs/vault-api:/app/logs"
      - "./cache:/app/cache"
    depends_on:
      - postgres
      - redis
      - chromadb
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - obsidian-network

  # Obsidian API
  obsidian-api:
    build:
      context: ./obsidian-api
      dockerfile: Dockerfile.prod
    container_name: obsidian-api
    env_file: .env.prod
    volumes:
      - "${OBSIDIAN_VAULT_PATH}:/vault:rw"
      - "./logs/obsidian-api:/app/logs"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:27123/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - obsidian-network

  # n8n Workflow Engine
  n8n:
    image: n8nio/n8n:latest
    container_name: obsidian-n8n
    env_file: .env.prod
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=${N8N_PORT}
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=${N8N_WEBHOOK_URL}
      - GENERIC_TIMEZONE=UTC
      - N8N_LOG_LEVEL=info
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    volumes:
      - n8n_data:/home/node/.n8n
      - "${OBSIDIAN_VAULT_PATH}:/vault:rw"
      - "./n8n/workflows:/home/node/.n8n/workflows"
      - "./logs/n8n:/home/node/.n8n/logs"
    depends_on:
      - postgres
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - obsidian-network

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: obsidian-postgres
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init:/docker-entrypoint-initdb.d
      - ./logs/postgres:/var/log/postgresql
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - obsidian-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: obsidian-redis
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
      - ./logs/redis:/var/log/redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - obsidian-network

  # ChromaDB Vector Database
  chromadb:
    image: chromadb/chroma:latest
    container_name: obsidian-chromadb
    environment:
      - CHROMA_SERVER_HOST=0.0.0.0
      - CHROMA_SERVER_HTTP_PORT=8000
      - PERSIST_DIRECTORY=/data
    volumes:
      - chromadb_data:/data
      - ./logs/chromadb:/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - obsidian-network

  # Ollama Local AI
  ollama:
    image: ollama/ollama:latest
    container_name: obsidian-ollama
    volumes:
      - ollama_data:/root/.ollama
      - ./logs/ollama:/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 60s
      timeout: 30s
      retries: 3
    networks:
      - obsidian-network

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: obsidian-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
      - ./logs/prometheus:/logs
    restart: unless-stopped
    networks:
      - obsidian-network

  # Grafana Dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: obsidian-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_DOMAIN=your-domain.com
      - GF_SERVER_ROOT_URL=https://your-domain.com/grafana/
      - GF_SERVER_SERVE_FROM_SUB_PATH=true
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
      - ./logs/grafana:/var/log/grafana
    depends_on:
      - prometheus
    restart: unless-stopped
    networks:
      - obsidian-network

  # Backup Service
  backup:
    build:
      context: ./backup
      dockerfile: Dockerfile
    container_name: obsidian-backup
    env_file: .env.prod
    volumes:
      - "${OBSIDIAN_VAULT_PATH}:/vault:ro"
      - "${VAULT_BACKUP_PATH}:/backups:rw"
      - postgres_data:/postgres_data:ro
      - n8n_data:/n8n_data:ro
      - ./logs/backup:/app/logs
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - obsidian-network

volumes:
  postgres_data:
  redis_data:
  chromadb_data:
  ollama_data:
  n8n_data:
  prometheus_data:
  grafana_data:

networks:
  obsidian-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Nginx Configuration (nginx/nginx.conf)
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss 
               application/json application/xml;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=1r/s;

    # Upstream Servers
    upstream vault_api {
        least_conn;
        server vault-api-1:8080 max_fails=3 fail_timeout=30s;
        server vault-api-2:8080 max_fails=3 fail_timeout=30s;
    }

    upstream obsidian_api {
        server obsidian-api:27123 max_fails=3 fail_timeout=30s;
    }

    upstream n8n {
        server n8n:5678 max_fails=3 fail_timeout=30s;
    }

    upstream grafana {
        server grafana:3000 max_fails=3 fail_timeout=30s;
    }

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Main Server Block
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;

        # Vault API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://vault_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # WebSocket Support
        location /ws {
            proxy_pass http://vault_api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Obsidian API
        location /obsidian/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://obsidian_api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # n8n Workflows
        location /n8n/ {
            limit_req zone=auth burst=5 nodelay;
            proxy_pass http://n8n/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Grafana Monitoring
        location /grafana/ {
            proxy_pass http://grafana/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health Check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Static Files (if any)
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## Deployment Steps

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /opt/obsidian-vault
sudo chown $USER:$USER /opt/obsidian-vault
cd /opt/obsidian-vault
```

### 2. SSL Certificate Setup
```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo mkdir -p /opt/obsidian-vault/certs
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/obsidian-vault/certs/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/obsidian-vault/certs/
sudo chown -R $USER:$USER /opt/obsidian-vault/certs
```

### 3. Application Deployment
```bash
# Clone repository
git clone <repository-url> .

# Copy production configuration
cp .env.example .env.prod
# Edit .env.prod with production values

# Create required directories
mkdir -p logs/{nginx,vault-api,obsidian-api,n8n,postgres,redis,chromadb,ollama,prometheus,grafana,backup}
mkdir -p backups cache

# Build and start services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

### 4. Initial Configuration
```bash
# Initialize database
docker-compose -f docker-compose.prod.yml exec postgres psql -U vault_user -d obsidian_vault_prod -c "SELECT version();"

# Load n8n workflows
docker-compose -f docker-compose.prod.yml exec n8n n8n import:workflow --input=/home/node/.n8n/workflows/

# Configure Grafana dashboards
curl -X POST http://admin:${GRAFANA_ADMIN_PASSWORD}@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana/dashboards/vault-dashboard.json
```

## Monitoring and Alerting

### Prometheus Alerts (prometheus/alerts.yml)
```yaml
groups:
  - name: obsidian-vault-alerts
    rules:
      - alert: VaultAPIDown
        expr: up{job="vault-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Vault API is down"
          description: "Vault API has been down for more than 1 minute"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is above 90% for more than 5 minutes"

      - alert: DiskSpaceLow
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Disk usage is above 80% for more than 5 minutes"

      - alert: DatabaseConnectionFailed
        expr: up{job="postgres"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failed"
          description: "PostgreSQL database is unreachable"
```

### Health Check Script (scripts/health-check.sh)
```bash
#!/bin/bash

# Production health check script
set -e

DOMAIN="your-domain.com"
TIMEOUT=10

echo "=== Obsidian Vault System Health Check ==="
echo "Timestamp: $(date)"
echo

# Check main API endpoint
echo "Checking Vault API..."
if curl -f -s --max-time $TIMEOUT "https://$DOMAIN/api/v1/health" > /dev/null; then
    echo "✅ Vault API: Healthy"
else
    echo "❌ Vault API: Failed"
    exit 1
fi

# Check Obsidian API
echo "Checking Obsidian API..."
if curl -f -s --max-time $TIMEOUT "https://$DOMAIN/obsidian/health" > /dev/null; then
    echo "✅ Obsidian API: Healthy"
else
    echo "❌ Obsidian API: Failed"
    exit 1
fi

# Check n8n
echo "Checking n8n..."
if curl -f -s --max-time $TIMEOUT "https://$DOMAIN/n8n/healthz" > /dev/null; then
    echo "✅ n8n: Healthy"
else
    echo "❌ n8n: Failed"
    exit 1
fi

# Check Grafana
echo "Checking Grafana..."
if curl -f -s --max-time $TIMEOUT "https://$DOMAIN/grafana/api/health" > /dev/null; then
    echo "✅ Grafana: Healthy"
else
    echo "❌ Grafana: Failed"
    exit 1
fi

# Check Docker containers
echo "Checking Docker containers..."
FAILED_CONTAINERS=$(docker-compose -f docker-compose.prod.yml ps --services --filter "status=exited")
if [ -z "$FAILED_CONTAINERS" ]; then
    echo "✅ All containers: Running"
else
    echo "❌ Failed containers: $FAILED_CONTAINERS"
    exit 1
fi

echo
echo "=== All systems operational ==="
```

## Backup and Recovery

### Automated Backup Script (backup/backup.sh)
```bash
#!/bin/bash

# Production backup script
set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo "Starting backup at $(date)"

# Create backup directory
mkdir -p "$BACKUP_DIR/$TIMESTAMP"

# Backup vault files
echo "Backing up vault files..."
tar -czf "$BACKUP_DIR/$TIMESTAMP/vault_$TIMESTAMP.tar.gz" -C "/vault" .

# Backup PostgreSQL
echo "Backing up PostgreSQL..."
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U vault_user obsidian_vault_prod | gzip > "$BACKUP_DIR/$TIMESTAMP/postgres_$TIMESTAMP.sql.gz"

# Backup n8n workflows
echo "Backing up n8n workflows..."
docker-compose -f docker-compose.prod.yml exec -T n8n n8n export:workflow --all --output=/tmp/workflows.json
docker cp obsidian-n8n:/tmp/workflows.json "$BACKUP_DIR/$TIMESTAMP/n8n_workflows_$TIMESTAMP.json"

# Backup configuration
echo "Backing up configuration..."
tar -czf "$BACKUP_DIR/$TIMESTAMP/config_$TIMESTAMP.tar.gz" .env.prod nginx/ grafana/ prometheus/

# Encrypt backup (optional)
if [ "$BACKUP_ENCRYPTION" = "true" ]; then
    echo "Encrypting backup..."
    tar -czf - "$BACKUP_DIR/$TIMESTAMP" | gpg --symmetric --cipher-algo AES256 --output "$BACKUP_DIR/encrypted_backup_$TIMESTAMP.tar.gz.gpg"
    rm -rf "$BACKUP_DIR/$TIMESTAMP"
fi

# Upload to S3 (optional)
if [ -n "$BACKUP_S3_BUCKET" ]; then
    echo "Uploading to S3..."
    aws s3 cp "$BACKUP_DIR/" "s3://$BACKUP_S3_BUCKET/backups/" --recursive --exclude "*" --include "*$TIMESTAMP*"
fi

# Cleanup old backups
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete

echo "Backup completed at $(date)"
```

## Maintenance Procedures

### Rolling Updates
```bash
#!/bin/bash

# Rolling update script
set -e

echo "Starting rolling update..."

# Update vault-api instances one by one
echo "Updating vault-api-1..."
docker-compose -f docker-compose.prod.yml stop vault-api-1
docker-compose -f docker-compose.prod.yml build vault-api-1
docker-compose -f docker-compose.prod.yml up -d vault-api-1

# Wait for health check
sleep 30
curl -f "https://your-domain.com/api/v1/health" || exit 1

echo "Updating vault-api-2..."
docker-compose -f docker-compose.prod.yml stop vault-api-2
docker-compose -f docker-compose.prod.yml build vault-api-2
docker-compose -f docker-compose.prod.yml up -d vault-api-2

# Wait for health check
sleep 30
curl -f "https://your-domain.com/api/v1/health" || exit 1

echo "Rolling update completed successfully"
```

### Log Rotation
```bash
# /etc/logrotate.d/obsidian-vault
/opt/obsidian-vault/logs/*/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/obsidian-vault/docker-compose.prod.yml restart nginx
    endscript
}
```

## Security Hardening

### Firewall Configuration
```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Docker Security
```bash
# Docker daemon configuration (/etc/docker/daemon.json)
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true
}
```

This production deployment guide ensures a robust, secure, and scalable deployment of the Obsidian Vault AI automation system.
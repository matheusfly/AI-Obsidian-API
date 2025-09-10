# Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the LangGraph + Obsidian Vault Integration System in various environments, from local development to production cloud deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Cloud Migration](#cloud-migration)
6. [Monitoring and Observability](#monitoring-and-observability)
7. [Security Configuration](#security-configuration)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance and Updates](#maintenance-and-updates)

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 4 cores, 2.4 GHz
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+ with WSL2

#### Recommended Requirements
- **CPU**: 8 cores, 3.0 GHz
- **RAM**: 16 GB
- **Storage**: 100 GB NVMe SSD
- **OS**: Linux (Ubuntu 22.04+), macOS (12+), or Windows 11 with WSL2

### Software Dependencies

#### Required Software
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.11+
- **UV**: 0.1+ (recommended)
- **Git**: 2.30+

#### Optional Software
- **Kubernetes**: 1.24+ (for cloud deployment)
- **Helm**: 3.8+ (for Kubernetes deployment)
- **Terraform**: 1.0+ (for infrastructure as code)

### API Keys and Configuration

#### Required API Keys
- **Obsidian Local REST API**: Plugin API key
- **OpenAI**: API key for LLM operations
- **LangSmith**: API key for tracing and monitoring

#### Optional API Keys
- **Gemini**: API key for alternative LLM provider
- **Pinecone**: API key for cloud vector database
- **Neo4j AuraDB**: API key for cloud graph database

## Local Development Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/langgraph-obsidian-integration.git
cd langgraph-obsidian-integration

# Create development branch
git checkout -b feature/your-feature
```

### 2. Environment Configuration

```bash
# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

#### Environment Variables

```bash
# Obsidian Configuration
OBSIDIAN_API_KEY=your_obsidian_api_key
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27123
OBSIDIAN_VAULT_PATH=/path/to/your/vault
VAULT_NAME=Main

# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=obsidian-agents

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key

# Optional: Gemini Configuration
GEMINI_API_KEY=your_gemini_key

# Optional: Cloud Database Configuration
PINECONE_API_KEY=your_pinecone_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password

# Development Configuration
DEBUG=true
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

### 3. Install Dependencies

#### Using UV (Recommended)

```bash
# Install UV
pip install uv

# Install dependencies
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
```

#### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Start Development Services

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Or start individual services
docker-compose up api-gateway langgraph-server langgraph-studio
```

### 5. Verify Installation

```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:2024/health
curl http://localhost:8002/health

# Check LangGraph Studio
open http://localhost:2025

# Check API documentation
open http://localhost:8000/docs
```

## Docker Deployment

### 1. Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api-gateway:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - /path/to/obsidian/vault:/vault:ro
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  langgraph-server:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "2024:2024"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  langgraph-studio:
    image: langchain/langgraph-studio:latest
    ports:
      - "2025:2025"
    environment:
      - LANGGRAPH_SERVER_URL=http://langgraph-server:2024
    depends_on:
      - langgraph-server
    restart: unless-stopped

  mcp-server:
    build:
      context: .
      dockerfile: docker/Dockerfile.mcp
    ports:
      - "8002:8002"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - /path/to/obsidian/vault:/vault:ro
    depends_on:
      - api-gateway
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=langgraph
      - POSTGRES_USER=langgraph
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  redis:
    image: redis:7
    volumes:
      - redis_data:/data
    restart: unless-stopped

  vector-db:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - vector_data:/chroma/chroma
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  vector_data:
  prometheus_data:
  grafana_data:
```

### 2. Build and Deploy

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Health Checks

```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash

# Check API Gateway
curl -f http://localhost:8000/health || exit 1

# Check LangGraph Server
curl -f http://localhost:2024/health || exit 1

# Check MCP Server
curl -f http://localhost:8002/health || exit 1

# Check LangGraph Studio
curl -f http://localhost:2025 || exit 1

echo "All services are healthy"
EOF

chmod +x health_check.sh
./health_check.sh
```

## Production Deployment

### 1. Infrastructure Setup

#### AWS Deployment

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure

# Create ECS cluster
aws ecs create-cluster --cluster-name langgraph-obsidian

# Create ECR repository
aws ecr create-repository --repository-name langgraph-obsidian
```

#### Azure Deployment

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Create resource group
az group create --name langgraph-obsidian --location eastus

# Create container registry
az acr create --resource-group langgraph-obsidian --name langgraphobsidian --sku Basic
```

### 2. Kubernetes Deployment

#### Create Kubernetes Manifests

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: langgraph-obsidian
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: langgraph-config
  namespace: langgraph-obsidian
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  OBSIDIAN_HOST: "obsidian-service"
  OBSIDIAN_PORT: "27123"
---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: langgraph-secrets
  namespace: langgraph-obsidian
type: Opaque
data:
  OBSIDIAN_API_KEY: <base64-encoded-key>
  OPENAI_API_KEY: <base64-encoded-key>
  LANGCHAIN_API_KEY: <base64-encoded-key>
---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: langgraph-obsidian
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: langgraph-obsidian/api-gateway:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: langgraph-config
              key: ENVIRONMENT
        - name: OBSIDIAN_API_KEY
          valueFrom:
            secretKeyRef:
              name: langgraph-secrets
              key: OBSIDIAN_API_KEY
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-gateway-service
  namespace: langgraph-obsidian
spec:
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n langgraph-obsidian

# Check services
kubectl get services -n langgraph-obsidian

# Check logs
kubectl logs -f deployment/api-gateway -n langgraph-obsidian
```

### 3. Helm Chart Deployment

#### Create Helm Chart

```bash
# Create Helm chart
helm create langgraph-obsidian

# Edit values.yaml
cat > langgraph-obsidian/values.yaml << 'EOF'
replicaCount: 3

image:
  repository: langgraph-obsidian/api-gateway
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80
  targetPort: 8000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: langgraph-obsidian.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: langgraph-obsidian-tls
      hosts:
        - langgraph-obsidian.example.com

resources:
  limits:
    cpu: 500m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}
EOF

# Deploy with Helm
helm install langgraph-obsidian ./langgraph-obsidian

# Check deployment
helm status langgraph-obsidian
```

## Cloud Migration

### 1. Migration Strategy

#### Phase 1: Containerization
- Optimize Docker images
- Implement multi-stage builds
- Configure resource limits
- Set up health checks

#### Phase 2: Cloud Infrastructure
- Deploy to Kubernetes
- Configure load balancing
- Set up auto-scaling
- Implement service mesh

#### Phase 3: Database Migration
- Migrate to cloud databases
- Implement data replication
- Set up backup strategies
- Configure monitoring

#### Phase 4: Advanced Features
- Implement CI/CD pipelines
- Set up monitoring and alerting
- Configure security policies
- Implement disaster recovery

### 2. Database Migration

#### PostgreSQL Migration

```bash
# Create database dump
pg_dump -h localhost -U langgraph -d langgraph > langgraph_backup.sql

# Restore to cloud database
psql -h cloud-db-host -U cloud-user -d langgraph < langgraph_backup.sql

# Verify migration
psql -h cloud-db-host -U cloud-user -d langgraph -c "SELECT COUNT(*) FROM agent_sessions;"
```

#### Vector Database Migration

```python
# migrate_vector_db.py
import chromadb
from chromadb.config import Settings

# Connect to local database
local_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db"
))

# Connect to cloud database
cloud_client = chromadb.Client(Settings(
    chroma_api_impl="rest",
    chroma_server_host="cloud-chroma-host",
    chroma_server_http_port="8000"
))

# Migrate collections
collections = local_client.list_collections()
for collection in collections:
    # Get collection data
    data = local_client.get_collection(collection.name).get()
    
    # Create collection in cloud
    cloud_collection = cloud_client.create_collection(collection.name)
    
    # Add data to cloud collection
    cloud_collection.add(
        documents=data['documents'],
        metadatas=data['metadatas'],
        ids=data['ids']
    )
```

### 3. Service Migration

#### API Gateway Migration

```yaml
# k8s/api-gateway-migration.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-gateway-config
data:
  OBSIDIAN_HOST: "obsidian-cloud-service"
  OBSIDIAN_PORT: "27123"
  VECTOR_DB_URL: "https://cloud-chroma-host:8000"
  GRAPH_DB_URL: "neo4j+s://cloud-neo4j-host:7687"
  POSTGRES_URL: "postgresql://cloud-user:password@cloud-postgres:5432/langgraph"
  REDIS_URL: "redis://cloud-redis:6379"
```

#### LangGraph Server Migration

```yaml
# k8s/langgraph-server-migration.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langgraph-server
spec:
  template:
    spec:
      containers:
      - name: langgraph-server
        env:
        - name: LANGGRAPH_SERVER_URL
          value: "https://cloud-langgraph-host:2024"
        - name: LANGGRAPH_SERVER_API_KEY
          valueFrom:
            secretKeyRef:
              name: langgraph-secrets
              key: LANGGRAPH_SERVER_API_KEY
```

## Monitoring and Observability

### 1. Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'langgraph-server'
    static_configs:
      - targets: ['langgraph-server:2024']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'mcp-server'
    static_configs:
      - targets: ['mcp-server:8002']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 2. Grafana Dashboards

#### System Overview Dashboard

```json
{
  "dashboard": {
    "title": "LangGraph Obsidian Integration - System Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      }
    ]
  }
}
```

### 3. LangSmith Integration

```python
# monitoring/langsmith_config.py
import os
from langchain.callbacks import LangChainTracer

# Configure LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_langsmith_key"
os.environ["LANGCHAIN_PROJECT"] = "obsidian-agents"

# Create tracer
tracer = LangChainTracer()

# Use in workflows
from langgraph_workflows.obsidian_agent import create_agent_workflow

workflow = create_agent_workflow()
workflow = workflow.with_config({"callbacks": [tracer]})
```

## Security Configuration

### 1. Network Security

#### Firewall Configuration

```bash
# UFW configuration
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 2024/tcp
sudo ufw allow 2025/tcp
sudo ufw deny 8001/tcp
sudo ufw deny 8002/tcp
```

#### SSL/TLS Configuration

```yaml
# nginx/ssl.conf
server {
    listen 443 ssl;
    server_name langgraph-obsidian.example.com;
    
    ssl_certificate /etc/ssl/certs/langgraph-obsidian.crt;
    ssl_certificate_key /etc/ssl/private/langgraph-obsidian.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://api-gateway:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Application Security

#### API Key Management

```python
# security/api_key_manager.py
import os
import secrets
from cryptography.fernet import Fernet

class APIKeyManager:
    def __init__(self):
        self.encryption_key = os.environ.get("ENCRYPTION_KEY", Fernet.generate_key())
        self.cipher = Fernet(self.encryption_key)
    
    def generate_api_key(self) -> str:
        """Generate a new API key."""
        return secrets.token_urlsafe(32)
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt an API key."""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt an API key."""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

#### Input Validation

```python
# security/input_validator.py
import re
from typing import Any, Dict
from pydantic import BaseModel, validator

class SecureInput(BaseModel):
    content: str
    file_path: str
    vault_name: str
    
    @validator('content')
    def validate_content(cls, v):
        if len(v) > 1000000:  # 1MB limit
            raise ValueError('Content too large')
        return v
    
    @validator('file_path')
    def validate_file_path(cls, v):
        if not re.match(r'^[a-zA-Z0-9_/.-]+$', v):
            raise ValueError('Invalid file path')
        if '..' in v or v.startswith('/'):
            raise ValueError('Path traversal not allowed')
        return v
    
    @validator('vault_name')
    def validate_vault_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid vault name')
        return v
```

## Troubleshooting

### 1. Common Issues

#### Service Not Starting

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs api-gateway
docker-compose logs langgraph-server

# Check resource usage
docker stats

# Restart services
docker-compose restart api-gateway
```

#### Database Connection Issues

```bash
# Check database connectivity
docker-compose exec postgres psql -U langgraph -d langgraph -c "SELECT 1;"

# Check Redis connectivity
docker-compose exec redis redis-cli ping

# Check vector database
curl http://localhost:8001/api/v1/heartbeat
```

#### API Gateway Issues

```bash
# Check API Gateway health
curl http://localhost:8000/health

# Check API Gateway logs
docker-compose logs -f api-gateway

# Test API endpoints
curl -X GET "http://localhost:8000/vaults" \
  -H "Authorization: Bearer your_api_key"
```

### 2. Performance Issues

#### High Memory Usage

```bash
# Check memory usage
docker stats

# Check specific container
docker exec api-gateway ps aux

# Restart with memory limits
docker-compose up -d --scale api-gateway=2
```

#### Slow Response Times

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/vaults"

# Check database performance
docker-compose exec postgres psql -U langgraph -d langgraph -c "EXPLAIN ANALYZE SELECT * FROM agent_sessions;"

# Check Redis performance
docker-compose exec redis redis-cli --latency
```

### 3. Debug Mode

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with debug output
docker-compose up --build

# Check debug logs
docker-compose logs -f | grep DEBUG
```

## Maintenance and Updates

### 1. Regular Maintenance

#### Daily Tasks

```bash
# Check service health
./health_check.sh

# Check disk usage
df -h

# Check log sizes
du -sh logs/*

# Clean old logs
find logs/ -name "*.log" -mtime +7 -delete
```

#### Weekly Tasks

```bash
# Update dependencies
pip list --outdated
pip install --upgrade -r requirements.txt

# Update Docker images
docker-compose pull
docker-compose up -d

# Check security updates
apt list --upgradable
```

#### Monthly Tasks

```bash
# Backup database
docker-compose exec postgres pg_dump -U langgraph langgraph > backup_$(date +%Y%m%d).sql

# Update system packages
apt update && apt upgrade -y

# Review and rotate logs
logrotate /etc/logrotate.d/langgraph-obsidian
```

### 2. Update Procedures

#### Application Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Rebuild and restart
docker-compose build
docker-compose up -d

# Verify update
./health_check.sh
```

#### Database Updates

```bash
# Create migration script
cat > migrations/001_add_new_table.sql << 'EOF'
CREATE TABLE IF NOT EXISTS new_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF

# Apply migration
docker-compose exec postgres psql -U langgraph -d langgraph -f /migrations/001_add_new_table.sql
```

### 3. Backup and Recovery

#### Backup Strategy

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec postgres pg_dump -U langgraph langgraph > $BACKUP_DIR/database.sql

# Backup vector database
cp -r ./chroma_db $BACKUP_DIR/

# Backup configuration
cp -r ./config $BACKUP_DIR/

# Compress backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR
EOF

chmod +x backup.sh
```

#### Recovery Procedures

```bash
# Restore from backup
tar -xzf backup_20240115.tar.gz
docker-compose exec postgres psql -U langgraph -d langgraph < backup_20240115/database.sql
cp -r backup_20240115/chroma_db ./
cp -r backup_20240115/config ./
```

## Conclusion

This deployment guide provides comprehensive instructions for deploying the LangGraph + Obsidian Vault Integration System in various environments. The guide covers everything from local development setup to production cloud deployment, including monitoring, security, and maintenance procedures.

The modular approach allows for flexible deployment strategies, from simple Docker Compose setups to complex Kubernetes deployments. The comprehensive monitoring and observability setup ensures reliable operation and quick issue resolution.

Regular maintenance and updates are essential for keeping the system secure and performant. The backup and recovery procedures ensure data safety and business continuity.

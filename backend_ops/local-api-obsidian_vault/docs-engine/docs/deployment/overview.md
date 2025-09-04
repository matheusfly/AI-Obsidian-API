# Deployment Overview

Comprehensive deployment strategies for the Obsidian Vault AI System.

## Deployment Architecture

The system supports multiple deployment strategies from local development to production scale:

```mermaid
graph TB
    subgraph "Local Development"
        A[Docker Compose]
        B[Native Services]
        C[Development Tools]
    end
    
    subgraph "Staging Environment"
        D[Kubernetes]
        E[Load Balancer]
        F[Monitoring]
    end
    
    subgraph "Production Environment"
        G[Multi-Region]
        H[Auto-Scaling]
        I[High Availability]
        J[Disaster Recovery]
    end
    
    subgraph "Cloud Providers"
        K[AWS]
        L[Azure]
        M[GCP]
        N[DigitalOcean]
    end
    
    A --> D
    B --> D
    C --> D
    D --> G
    E --> G
    F --> G
    G --> K
    G --> L
    G --> M
    G --> N
```

## Deployment Strategies

### 1. Local Development

**Docker Compose (Recommended)**
```bash
# Quick start
docker-compose up -d

# With custom configuration
docker-compose -f docker-compose.override.yml up -d
```

**Native Services**
```bash
# Start individual services
./scripts/start-native-servers.ps1 -VaultPath "D:\Your\Vault"
```

### 2. Staging Environment

**Kubernetes Deployment**
```yaml
# k8s/staging.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vault-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vault-api
  template:
    metadata:
      labels:
        app: vault-api
    spec:
      containers:
      - name: vault-api
        image: obsidian-vault-ai/vault-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

### 3. Production Environment

**Multi-Region Deployment**
```yaml
# k8s/production.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vault-api-config
data:
  replicas: "5"
  resources.limits.cpu: "2"
  resources.limits.memory: "4Gi"
  resources.requests.cpu: "1"
  resources.requests.memory: "2Gi"
```

## Environment Configurations

### Development

```env
# .env.development
NODE_ENV=development
DEBUG=true
LOG_LEVEL=debug
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/obsidian_vault_dev
REDIS_URL=redis://localhost:6379/0
VAULT_PATH=/vault
```

### Staging

```env
# .env.staging
NODE_ENV=staging
DEBUG=false
LOG_LEVEL=info
DATABASE_URL=postgresql://user:pass@staging-db:5432/obsidian_vault_staging
REDIS_URL=redis://staging-redis:6379/0
VAULT_PATH=/vault
```

### Production

```env
# .env.production
NODE_ENV=production
DEBUG=false
LOG_LEVEL=warning
DATABASE_URL=postgresql://user:pass@prod-db:5432/obsidian_vault_prod
REDIS_URL=redis://prod-redis:6379/0
VAULT_PATH=/vault
```

## Container Orchestration

### Docker Compose

**Basic Configuration**
```yaml
# docker-compose.yml
version: '3.8'

services:
  vault-api:
    build: ./services/vault-api
    ports:
      - "8085:8080"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/obsidian_vault
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=obsidian_vault
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

**Production Configuration**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  vault-api:
    build: ./services/vault-api
    ports:
      - "8085:8080"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/obsidian_vault
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=obsidian_vault
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    restart: unless-stopped

  redis:
    image: redis:7
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes

**Namespace Configuration**
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: obsidian-vault-ai
  labels:
    name: obsidian-vault-ai
```

**ConfigMap**
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vault-api-config
  namespace: obsidian-vault-ai
data:
  DATABASE_URL: "postgresql://postgres:postgres@postgres:5432/obsidian_vault"
  REDIS_URL: "redis://redis:6379/0"
  LOG_LEVEL: "info"
  DEBUG: "false"
```

**Secrets**
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: vault-api-secrets
  namespace: obsidian-vault-ai
type: Opaque
data:
  openai-api-key: <base64-encoded-key>
  supabase-key: <base64-encoded-key>
  jwt-secret: <base64-encoded-secret>
```

**Deployment**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vault-api
  namespace: obsidian-vault-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vault-api
  template:
    metadata:
      labels:
        app: vault-api
    spec:
      containers:
      - name: vault-api
        image: obsidian-vault-ai/vault-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: vault-api-config
              key: DATABASE_URL
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: vault-api-secrets
              key: openai-api-key
        resources:
          limits:
            cpu: 2
            memory: 4Gi
          requests:
            cpu: 1
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Service**
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: vault-api-service
  namespace: obsidian-vault-ai
spec:
  selector:
    app: vault-api
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

**Ingress**
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vault-api-ingress
  namespace: obsidian-vault-ai
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.your-domain.com
    secretName: vault-api-tls
  rules:
  - host: api.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vault-api-service
            port:
              number: 80
```

## Cloud Provider Deployments

### AWS

**ECS Task Definition**
```json
{
  "family": "vault-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "vault-api",
      "image": "obsidian-vault-ai/vault-api:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/obsidian_vault"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/vault-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**CloudFormation Template**
```yaml
# cloudformation/vault-api.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Obsidian Vault AI System'

Parameters:
  VaultPath:
    Type: String
    Default: /vault
    Description: Path to Obsidian vault
  
  DatabasePassword:
    Type: String
    NoEcho: true
    Description: Database password

Resources:
  VaultAPIService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: vault-api
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref VaultAPITaskDefinition
      DesiredCount: 3
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          SecurityGroups:
            - !Ref SecurityGroup
          Subnets:
            - !Ref Subnet1
            - !Ref Subnet2
          AssignPublicIp: ENABLED

  VaultAPITaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: vault-api
      Cpu: 1024
      Memory: 2048
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !Ref TaskExecutionRole
      ContainerDefinitions:
        - Name: vault-api
          Image: obsidian-vault-ai/vault-api:latest
          PortMappings:
            - ContainerPort: 8080
              Protocol: tcp
          Environment:
            - Name: DATABASE_URL
              Value: !Sub 'postgresql://postgres:${DatabasePassword}@${DatabaseEndpoint}:5432/obsidian_vault'
            - Name: VAULT_PATH
              Value: !Ref VaultPath
          Secrets:
            - Name: OPENAI_API_KEY
              ValueFrom: !Sub '${OpenAIKeySecret}:openai-api-key::'
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs
```

### Azure

**ARM Template**
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "vaultPath": {
      "type": "string",
      "defaultValue": "/vault",
      "metadata": {
        "description": "Path to Obsidian vault"
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.ContainerInstance/containerGroups",
      "apiVersion": "2021-03-01",
      "name": "vault-api",
      "location": "[resourceGroup().location]",
      "properties": {
        "containers": [
          {
            "name": "vault-api",
            "properties": {
              "image": "obsidian-vault-ai/vault-api:latest",
              "ports": [
                {
                  "port": 8080
                }
              ],
              "environmentVariables": [
                {
                  "name": "VAULT_PATH",
                  "value": "[parameters('vaultPath')]"
                }
              ],
              "resources": {
                "requests": {
                  "cpu": 1,
                  "memoryInGb": 2
                }
              }
            }
          }
        ],
        "osType": "Linux",
        "ipAddress": {
          "type": "Public",
          "ports": [
            {
              "port": 8080,
              "protocol": "TCP"
            }
          ]
        }
      }
    }
  ]
}
```

### Google Cloud Platform

**Deployment Manager**
```yaml
# gcp/deployment.yaml
resources:
- name: vault-api
  type: compute.v1.instance
  properties:
    zone: us-central1-a
    machineType: zones/us-central1-a/machineTypes/e2-standard-2
    disks:
    - deviceName: boot
      type: PERSISTENT
      boot: true
      autoDelete: true
      initializeParams:
        sourceImage: projects/cos-cloud/global/images/family/cos-stable
    networkInterfaces:
    - network: global/networks/default
      accessConfigs:
      - name: External NAT
        type: ONE_TO_ONE_NAT
    metadata:
      items:
      - key: startup-script
        value: |
          #!/bin/bash
          docker run -d -p 8080:8080 \
            -e DATABASE_URL="postgresql://user:pass@db-ip:5432/obsidian_vault" \
            -e VAULT_PATH="/vault" \
            obsidian-vault-ai/vault-api:latest
```

## CI/CD Pipeline

### GitHub Actions

**Workflow Configuration**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run tests
      run: |
        docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
        docker-compose -f docker-compose.test.yml down

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker images
      run: |
        docker build -t obsidian-vault-ai/vault-api:latest ./services/vault-api
        docker build -t obsidian-vault-ai/obsidian-api:latest ./services/obsidian-api

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/
        kubectl rollout status deployment/vault-api
```

### GitLab CI

**Pipeline Configuration**
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

test:
  stage: test
  script:
    - docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
    - docker-compose -f docker-compose.test.yml down

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE/vault-api:$CI_COMMIT_SHA ./services/vault-api
    - docker push $CI_REGISTRY_IMAGE/vault-api:$CI_COMMIT_SHA
  only:
    - main

deploy:
  stage: deploy
  script:
    - kubectl apply -f k8s/
    - kubectl rollout status deployment/vault-api
  only:
    - main
```

## Monitoring and Observability

### Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "ai-observability-rules.yml"

scrape_configs:
  - job_name: 'vault-api'
    static_configs:
      - targets: ['vault-api:8080']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'obsidian-api'
    static_configs:
      - targets: ['obsidian-api:27123']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Obsidian Vault AI System",
    "panels": [
      {
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
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

## Security Considerations

### 1. Network Security

- **Firewall Rules**: Restrict access to necessary ports
- **VPN Access**: Use VPN for secure access
- **TLS/SSL**: Encrypt all communications
- **Network Segmentation**: Isolate services

### 2. Data Security

- **Encryption at Rest**: Encrypt stored data
- **Encryption in Transit**: Use TLS for all communications
- **Key Management**: Secure key storage and rotation
- **Data Backup**: Regular encrypted backups

### 3. Access Control

- **Authentication**: Strong authentication mechanisms
- **Authorization**: Role-based access control
- **Audit Logging**: Comprehensive audit trails
- **Multi-factor Authentication**: Additional security layer

## Disaster Recovery

### 1. Backup Strategy

```bash
#!/bin/bash
# backup.sh

# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Vault backup
tar -czf vault_backup_$(date +%Y%m%d_%H%M%S).tar.gz $VAULT_PATH

# Upload to cloud storage
aws s3 cp backup_*.sql s3://backup-bucket/database/
aws s3 cp vault_backup_*.tar.gz s3://backup-bucket/vault/
```

### 2. Recovery Procedures

```bash
#!/bin/bash
# restore.sh

# Restore database
psql $DATABASE_URL < backup_20240101_120000.sql

# Restore vault
tar -xzf vault_backup_20240101_120000.tar.gz -C /

# Restart services
kubectl rollout restart deployment/vault-api
```

## Performance Optimization

### 1. Caching Strategy

```yaml
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 2. Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_files_path ON files(path);
CREATE INDEX idx_files_modified ON files(modified_at);
CREATE INDEX idx_metadata_key ON metadata(key);

-- Analyze tables for query optimization
ANALYZE files;
ANALYZE metadata;
```

### 3. Load Balancing

```yaml
# nginx.conf
upstream vault_api {
    server vault-api-1:8080;
    server vault-api-2:8080;
    server vault-api-3:8080;
}

server {
    listen 80;
    server_name api.your-domain.com;
    
    location / {
        proxy_pass http://vault_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### 1. Common Issues

**Service Not Starting**
```bash
# Check logs
docker-compose logs vault-api

# Check health
curl http://localhost:8085/health

# Check resources
docker stats
```

**Database Connection Issues**
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1"

# Check database logs
docker-compose logs postgres
```

**Memory Issues**
```bash
# Check memory usage
free -h
docker stats

# Increase memory limits
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Debugging Tools

**Container Debugging**
```bash
# Enter container
docker exec -it vault-api bash

# Check processes
ps aux

# Check logs
tail -f /var/log/app.log
```

**Kubernetes Debugging**
```bash
# Check pods
kubectl get pods

# Check logs
kubectl logs vault-api-xxx

# Describe pod
kubectl describe pod vault-api-xxx
```

## Best Practices

1. **Start Small**: Begin with local development and scale gradually
2. **Monitor Everything**: Implement comprehensive monitoring
3. **Automate Deployments**: Use CI/CD pipelines
4. **Test Thoroughly**: Comprehensive testing at all levels
5. **Document Everything**: Keep documentation up to date
6. **Security First**: Implement security from the beginning
7. **Backup Regularly**: Implement robust backup strategies
8. **Plan for Scale**: Design for horizontal scaling

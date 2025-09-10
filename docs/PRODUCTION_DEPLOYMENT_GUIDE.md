# 🚀 Production Deployment Guide

## Overview

This guide covers deploying the Data Vault Obsidian observability stack to production with enterprise-grade security, monitoring, and operational features.

## Prerequisites

- Docker and Docker Compose installed
- Administrator privileges
- SSL certificates (for HTTPS)
- Environment variables configured
- Backup storage configured

## Quick Start

### 1. Configure Environment

```bash
# Copy production environment template
cp config/production.env .env

# Edit with your actual values
notepad .env
```

Required environment variables:
- `GRAFANA_ADMIN_PASSWORD` - Strong password for Grafana admin
- `GRAFANA_SECRET_KEY` - Secret key for Grafana sessions
- `REDIS_PASSWORD` - Strong password for Redis
- `PROMETHEUS_PASSWORD` - Password for Prometheus basic auth
- `LANGSMITH_API_KEY` - Your LangSmith API key

### 2. Deploy Production Stack

```powershell
# Run production deployment script
.\scripts\deploy-production.ps1

# Or manually with Docker Compose
docker-compose -f docker-compose.production.yml up -d
```

### 3. Verify Deployment

```powershell
# Run health check
.\scripts\health-check-production.ps1 -Detailed

# Check service status
docker-compose -f docker-compose.production.yml ps
```

## Architecture

### Services

- **ChromaDB**: Vector database with authentication
- **Redis**: Caching layer with password protection
- **Data Pipeline**: FastAPI service with metrics and tracing
- **OpenTelemetry Collector**: Traces and metrics collection
- **Prometheus**: Metrics storage and alerting
- **Grafana**: Dashboards and visualization
- **Nginx**: Reverse proxy with security headers

### Security Features

- Authentication on all services
- HTTPS/TLS support (configurable)
- Security headers via Nginx
- Rate limiting
- Resource limits and constraints
- Network isolation

### Monitoring Features

- Comprehensive health checks
- Auto-restart policies
- Resource monitoring
- Alert rules for critical issues
- Centralized logging
- Distributed tracing

## Configuration

### Grafana

- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: Set in `GRAFANA_ADMIN_PASSWORD`

### Prometheus

- **URL**: http://localhost:9090
- **Username**: admin
- **Password**: Set in `PROMETHEUS_PASSWORD`

### Data Pipeline API

- **URL**: http://localhost:8003
- **Health**: http://localhost:8003/health
- **Metrics**: http://localhost:8003/metrics

## Monitoring

### Dashboards

1. **Production Operations Dashboard** - Overall system health
2. **Vector Database Monitoring** - ChromaDB metrics
3. **Data Pipeline Overview** - API and processing metrics
4. **LangSmith Trace Integration** - Distributed tracing

### Alerting

Critical alerts are configured for:
- Service downtime
- High error rates
- High response times
- Memory usage
- Disk space
- Vector database issues

### Health Checks

```powershell
# Basic health check
.\scripts\health-check-production.ps1

# Detailed health check
.\scripts\health-check-production.ps1 -Detailed

# JSON output for monitoring systems
.\scripts\health-check-production.ps1 -Json -OutputFile health.json
```

## Operations

### Starting Services

```powershell
# Start all services
docker-compose -f docker-compose.production.yml up -d

# Start specific service
docker-compose -f docker-compose.production.yml up -d grafana
```

### Stopping Services

```powershell
# Stop all services
docker-compose -f docker-compose.production.yml down

# Stop and remove volumes
docker-compose -f docker-compose.production.yml down -v
```

### Viewing Logs

```powershell
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f data-pipeline

# Last 100 lines
docker-compose -f docker-compose.production.yml logs --tail=100 grafana
```

### Restarting Services

```powershell
# Restart all services
docker-compose -f docker-compose.production.yml restart

# Restart specific service
docker-compose -f docker-compose.production.yml restart data-pipeline
```

## Backup and Recovery

### Automated Backups

The deployment script creates automatic backups before deployment:

```powershell
# Backup location
backups/YYYY-MM-DD_HH-mm-ss/
├── chroma_data.tar.gz
├── redis_data.tar.gz
├── prometheus_data.tar.gz
└── grafana_data.tar.gz
```

### Manual Backup

```powershell
# Create backup directory
$backupDir = "backups/$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
New-Item -ItemType Directory -Path $backupDir

# Backup ChromaDB
docker run --rm -v obsidian-chroma-prod_chroma_data:/data -v "${PWD}/${backupDir}:/backup" alpine tar czf /backup/chroma_data.tar.gz -C /data .

# Backup Redis
docker run --rm -v obsidian-redis-prod_redis_data:/data -v "${PWD}/${backupDir}:/backup" alpine tar czf /backup/redis_data.tar.gz -C /data .

# Backup Prometheus
docker run --rm -v obsidian-prometheus-prod_prometheus_data:/data -v "${PWD}/${backupDir}:/backup" alpine tar czf /backup/prometheus_data.tar.gz -C /data .

# Backup Grafana
docker run --rm -v obsidian-grafana-prod_grafana_data:/data -v "${PWD}/${backupDir}:/backup" alpine tar czf /backup/grafana_data.tar.gz -C /data .
```

### Restore from Backup

```powershell
# Stop services
docker-compose -f docker-compose.production.yml down

# Restore ChromaDB
docker run --rm -v obsidian-chroma-prod_chroma_data:/data -v "${PWD}/backups/YYYY-MM-DD_HH-mm-ss:/backup" alpine tar xzf /backup/chroma_data.tar.gz -C /data

# Restore other services similarly...

# Start services
docker-compose -f docker-compose.production.yml up -d
```

## Security

### SSL/TLS Configuration

1. Place SSL certificates in `config/nginx/ssl/`:
   - `cert.pem` - SSL certificate
   - `key.pem` - Private key

2. Uncomment HTTPS section in `config/nginx/nginx.conf`

3. Update `docker-compose.production.yml` to use port 443

### Authentication

All services are configured with authentication:
- Grafana: Admin user with strong password
- Prometheus: Basic auth with admin user
- ChromaDB: Htpasswd authentication
- Redis: Password protection

### Network Security

- Services run in isolated Docker network
- Nginx provides security headers
- Rate limiting on API endpoints
- No direct external access to internal services

## Troubleshooting

### Common Issues

1. **Services not starting**
   ```powershell
   # Check logs
   docker-compose -f docker-compose.production.yml logs
   
   # Check resource usage
   docker stats
   ```

2. **Authentication issues**
   ```powershell
   # Verify environment variables
   Get-Content .env
   
   # Check service logs
   docker-compose -f docker-compose.production.yml logs grafana
   ```

3. **Performance issues**
   ```powershell
   # Check resource limits
   docker stats
   
   # Check Prometheus metrics
   curl http://localhost:9090/api/v1/query?query=up
   ```

### Health Check Failures

```powershell
# Run detailed health check
.\scripts\health-check-production.ps1 -Detailed -Json -OutputFile health.json

# Check specific service
docker inspect obsidian-data-pipeline-prod --format='{{.State.Health}}'
```

### Log Analysis

```powershell
# Search for errors
docker-compose -f docker-compose.production.yml logs | Select-String "ERROR"

# Monitor real-time logs
docker-compose -f docker-compose.production.yml logs -f --tail=50
```

## Maintenance

### Regular Tasks

1. **Monitor disk space**
   ```powershell
   # Check Prometheus data retention
   docker exec obsidian-prometheus-prod du -sh /prometheus
   ```

2. **Update images**
   ```powershell
   # Pull latest images
   docker-compose -f docker-compose.production.yml pull
   
   # Rebuild and restart
   docker-compose -f docker-compose.production.yml up -d --build
   ```

3. **Clean up old backups**
   ```powershell
   # Remove backups older than 30 days
   Get-ChildItem backups | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Recurse
   ```

### Performance Tuning

1. **Adjust resource limits** in `docker-compose.production.yml`
2. **Configure Prometheus retention** in `config/prometheus/prometheus.yml`
3. **Optimize Grafana dashboards** for better performance
4. **Tune Redis memory settings** based on usage

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review service logs
3. Run health checks
4. Check the monitoring dashboards

## Changelog

- **v1.0.0** - Initial production deployment
- **v1.1.0** - Added comprehensive monitoring
- **v1.2.0** - Enhanced security features
- **v1.3.0** - Added backup and recovery


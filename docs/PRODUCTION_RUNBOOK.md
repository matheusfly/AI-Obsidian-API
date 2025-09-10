# 🚨 Production Runbook

## Emergency Contacts

- **On-Call Engineer**: [Your Name] - [Phone] - [Email]
- **Backup Engineer**: [Backup Name] - [Phone] - [Email]
- **Manager**: [Manager Name] - [Phone] - [Email]

## Quick Reference

### Service URLs
- **Grafana**: http://localhost:3000 (admin/[PASSWORD])
- **Prometheus**: http://localhost:9090 (admin/[PASSWORD])
- **Data Pipeline**: http://localhost:8003
- **Health Check**: http://localhost/health

### Quick Commands
```powershell
# Check all services
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Restart all services
docker-compose -f docker-compose.production.yml restart

# Health check
.\scripts\health-check-production.ps1 -Detailed
```

## Incident Response

### 1. Service Down

**Symptoms**: Service not responding, health checks failing

**Immediate Actions**:
1. Check service status: `docker-compose -f docker-compose.production.yml ps`
2. Check logs: `docker-compose -f docker-compose.production.yml logs [service-name]`
3. Restart service: `docker-compose -f docker-compose.production.yml restart [service-name]`
4. Wait 2 minutes and verify: `.\scripts\health-check-production.ps1`

**If restart fails**:
1. Check resource usage: `docker stats`
2. Check disk space: `docker system df`
3. Check for port conflicts: `netstat -an | findstr :8003`
4. Check Docker daemon: `docker version`

**Escalation**: If service doesn't start after 10 minutes, escalate to backup engineer.

### 2. High Error Rate

**Symptoms**: 5xx errors, alert firing

**Immediate Actions**:
1. Check error logs: `docker-compose -f docker-compose.production.yml logs data-pipeline | Select-String "ERROR"`
2. Check metrics: `curl http://localhost:8003/metrics`
3. Check resource usage: `docker stats`
4. Check dependencies: `curl http://localhost:8000/api/v1/heartbeat`

**Common Causes**:
- ChromaDB connection issues
- Redis connection issues
- High memory usage
- Network connectivity problems

**Resolution**:
1. Restart data-pipeline: `docker-compose -f docker-compose.production.yml restart data-pipeline`
2. If ChromaDB issues: `docker-compose -f docker-compose.production.yml restart chroma`
3. If Redis issues: `docker-compose -f docker-compose.production.yml restart redis`

### 3. High Response Time

**Symptoms**: Slow API responses, alert firing

**Immediate Actions**:
1. Check current load: `docker stats`
2. Check Prometheus metrics: `curl http://localhost:9090/api/v1/query?query=rate(http_request_duration_seconds_sum[5m])`
3. Check ChromaDB performance: `curl http://localhost:8000/api/v1/heartbeat`
4. Check Redis performance: `docker exec obsidian-redis-prod redis-cli info stats`

**Resolution**:
1. Scale up resources in `docker-compose.production.yml`
2. Restart services to clear memory leaks
3. Check for long-running queries in ChromaDB
4. Clear Redis cache if needed

### 4. Memory Issues

**Symptoms**: Out of memory errors, containers being killed

**Immediate Actions**:
1. Check memory usage: `docker stats`
2. Check system memory: `Get-ComputerInfo | Select-Object TotalPhysicalMemory, AvailablePhysicalMemory`
3. Check for memory leaks in logs
4. Restart services to free memory

**Resolution**:
1. Increase memory limits in `docker-compose.production.yml`
2. Restart services: `docker-compose -f docker-compose.production.yml restart`
3. If persistent, check for memory leaks in application code

### 5. Disk Space Issues

**Symptoms**: Write failures, containers stopping

**Immediate Actions**:
1. Check disk space: `Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name="FreeSpace(GB)";Expression={[math]::Round($_.FreeSpace/1GB,2)}}`
2. Check Docker disk usage: `docker system df`
3. Check Prometheus data size: `docker exec obsidian-prometheus-prod du -sh /prometheus`

**Resolution**:
1. Clean up old Docker images: `docker system prune -a`
2. Clean up old Prometheus data
3. Clean up old backups
4. Increase disk space if needed

## Recovery Procedures

### 1. Complete System Recovery

**When**: All services down, data corruption suspected

**Steps**:
1. Stop all services: `docker-compose -f docker-compose.production.yml down`
2. Check for data corruption in volumes
3. Restore from latest backup
4. Start services: `docker-compose -f docker-compose.production.yml up -d`
5. Verify all services: `.\scripts\health-check-production.ps1 -Detailed`

### 2. Data Recovery

**When**: Data loss or corruption detected

**Steps**:
1. Stop affected services
2. Restore from backup:
   ```powershell
   # Restore ChromaDB
   docker run --rm -v obsidian-chroma-prod_chroma_data:/data -v "${PWD}/backups/[BACKUP_DIR]:/backup" alpine tar xzf /backup/chroma_data.tar.gz -C /data
   
   # Restore Redis
   docker run --rm -v obsidian-redis-prod_redis_data:/data -v "${PWD}/backups/[BACKUP_DIR]:/backup" alpine tar xzf /backup/redis_data.tar.gz -C /data
   ```
3. Start services
4. Verify data integrity

### 3. Configuration Recovery

**When**: Configuration changes cause issues

**Steps**:
1. Stop services
2. Restore configuration from Git: `git checkout HEAD -- config/`
3. Restart services
4. Verify functionality

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Service Health**: `up` metric
2. **Response Time**: `http_request_duration_seconds`
3. **Error Rate**: `rate(http_requests_total{status=~"5.."}[5m])`
4. **Memory Usage**: `node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes`
5. **Disk Space**: `node_filesystem_avail_bytes / node_filesystem_size_bytes`

### Alert Thresholds

- **Service Down**: `up == 0` for 1 minute
- **High Error Rate**: >10% for 2 minutes
- **High Response Time**: >2 seconds for 3 minutes
- **High Memory Usage**: >90% for 5 minutes
- **Low Disk Space**: <10% for 5 minutes

### Dashboard Monitoring

1. **Production Operations Dashboard** - Overall health
2. **Vector Database Monitoring** - ChromaDB metrics
3. **Data Pipeline Overview** - API metrics
4. **LangSmith Trace Integration** - Tracing

## Maintenance Windows

### Weekly Maintenance

**When**: Sunday 2:00 AM - 4:00 AM

**Tasks**:
1. Update Docker images
2. Clean up old logs
3. Verify backups
4. Check disk space
5. Review alert history

### Monthly Maintenance

**When**: First Sunday of month

**Tasks**:
1. Security updates
2. Configuration review
3. Performance analysis
4. Backup testing
5. Documentation updates

## Post-Incident

### 1. Immediate Actions

1. Verify all services are healthy
2. Check monitoring dashboards
3. Review logs for root cause
4. Document incident details

### 2. Within 24 Hours

1. Write incident report
2. Update runbook if needed
3. Schedule post-mortem meeting
4. Implement preventive measures

### 3. Post-Mortem

1. Root cause analysis
2. Timeline reconstruction
3. Action items identification
4. Process improvements
5. Documentation updates

## Escalation Matrix

| Severity | Response Time | Escalation |
|----------|---------------|------------|
| Critical | 15 minutes | On-call → Manager → Director |
| High | 1 hour | On-call → Manager |
| Medium | 4 hours | On-call |
| Low | 24 hours | Next business day |

## Contact Information

### Internal Contacts
- **DevOps Team**: devops@company.com
- **Security Team**: security@company.com
- **Database Team**: dba@company.com

### External Contacts
- **Docker Support**: [Support Portal]
- **Prometheus Community**: [Community Forum]
- **Grafana Support**: [Support Portal]

## Appendix

### A. Service Dependencies

```
Nginx → Grafana
Nginx → Prometheus  
Nginx → Data Pipeline
Data Pipeline → ChromaDB
Data Pipeline → Redis
Data Pipeline → OTel Collector
OTel Collector → LangSmith
Prometheus → All Services
```

### B. Port Reference

| Service | Port | Protocol |
|---------|------|----------|
| Nginx | 80, 443 | HTTP/HTTPS |
| Grafana | 3000 | HTTP |
| Prometheus | 9090 | HTTP |
| Data Pipeline | 8003 | HTTP |
| ChromaDB | 8000 | HTTP |
| Redis | 6379 | TCP |
| OTel Collector | 4317, 4318 | gRPC/HTTP |

### C. Log Locations

| Service | Log Location |
|---------|--------------|
| All Services | `docker-compose -f docker-compose.production.yml logs` |
| Data Pipeline | `/app/logs/` (inside container) |
| Nginx | `/var/log/nginx/` (inside container) |
| Prometheus | Console output |
| Grafana | Console output |


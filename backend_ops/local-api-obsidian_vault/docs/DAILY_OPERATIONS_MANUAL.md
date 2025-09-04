# 📋 Daily Operations Manual

## 🌅 Morning Startup Routine

### 1. System Health Check (2 minutes)
```bash
# Navigate to project directory
cd d:\codex\master_code\backend_ops\local-api-obsidian_vault

# Check if system is running
docker-compose ps

# If not running, start system
./scripts/start.sh

# Verify all services are healthy
curl http://localhost:8080/health
curl http://localhost:27123/health
curl http://localhost:5678/health
```

### 2. Daily System Status
```bash
# Check service status
docker-compose ps

# Expected output:
# vault-api     Up      0.0.0.0:8080->8080/tcp
# obsidian-api  Up      0.0.0.0:27123->27123/tcp
# n8n           Up      0.0.0.0:5678->5678/tcp
# postgres      Up      5432/tcp
# redis         Up      6379/tcp
```

## 🔄 Daily Workflow Operations

### API Testing & Monitoring

#### Test Core Endpoints
```bash
# 1. API Status Check
curl http://localhost:8080/

# 2. List recent notes
curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8080/api/v1/notes?limit=10"

# 3. Search functionality
curl -X POST http://localhost:8080/api/v1/search \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"query": "daily", "limit": 5}'

# 4. Check n8n workflows
curl http://localhost:8080/api/v1/workflows
```

#### Create Daily Note via API
```bash
# Create today's daily note
TODAY=$(date +%Y-%m-%d)
curl -X POST http://localhost:8080/api/v1/notes \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d "{
    \"path\": \"daily/${TODAY}.md\",
    \"content\": \"# Daily Note - ${TODAY}\n\n## Goals\n- [ ] \n\n## Notes\n\n## Reflections\n\",
    \"tags\": [\"daily\", \"$(date +%Y)\", \"$(date +%B)\"]
  }"
```

### n8n Workflow Management

#### Access n8n Dashboard
1. Open browser: http://localhost:5678
2. Login with credentials from .env file
3. Check active workflows

#### Common Workflow Operations
```bash
# Check workflow status via API
curl -X GET http://localhost:5678/rest/workflows \
  -H "Content-Type: application/json"

# Trigger manual workflow
curl -X POST http://localhost:5678/webhook/daily-processing \
  -H "Content-Type: application/json" \
  -d '{"trigger": "manual", "timestamp": "'$(date -Iseconds)'"}'
```

## 📊 Monitoring & Maintenance

### Log Analysis
```bash
# View all service logs
docker-compose logs --tail=50

# Monitor specific service
docker-compose logs -f vault-api

# Check for errors
docker-compose logs | grep -i error

# Check API access logs
docker-compose logs vault-api | grep -E "(POST|GET|PUT|DELETE)"
```

### Performance Monitoring
```bash
# Check container resource usage
docker stats

# Check disk usage
df -h

# Check vault directory size
du -sh "/mnt/d/Nomade Milionario"

# Monitor API response times
time curl http://localhost:8080/health
```

### Database Maintenance
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U n8n_user

# View database size
docker-compose exec postgres psql -U n8n_user -d n8n -c "
SELECT pg_size_pretty(pg_database_size('n8n')) as database_size;"

# Check Redis status
docker-compose exec redis redis-cli ping
```

## 🔧 Common Daily Tasks

### 1. Backup Operations
```bash
# Run daily backup
./scripts/backup.sh

# Verify backup created
ls -la ./backups/

# Test backup integrity
tar -tzf ./backups/$(date +%Y%m%d)_*.tar.gz | head -10
```

### 2. Update API Keys
```bash
# Edit environment file
nano .env

# Restart affected services
docker-compose restart vault-api n8n
```

### 3. Add New Notes via API
```bash
# Meeting notes template
curl -X POST http://localhost:8080/api/v1/notes \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "meetings/meeting-'$(date +%Y%m%d-%H%M)'.md",
    "content": "# Meeting - '$(date +%Y-%m-%d)'\n\n## Attendees\n- \n\n## Agenda\n- \n\n## Notes\n\n## Action Items\n- [ ] \n",
    "tags": ["meeting", "work"]
  }'

# Research note template
curl -X POST http://localhost:8080/api/v1/notes \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "research/topic-'$(date +%Y%m%d)'.md",
    "content": "# Research: Topic\n\n## Overview\n\n## Key Points\n- \n\n## Sources\n- \n\n## Next Steps\n- [ ] \n",
    "tags": ["research", "learning"]
  }'
```

### 4. AI Processing Tasks
```bash
# Trigger AI analysis on recent notes
curl -X POST http://localhost:8080/api/v1/ai/process \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "summarize",
    "content": "Your note content here...",
    "parameters": {"max_length": 200}
  }'

# Generate tags for content
curl -X POST http://localhost:8080/api/v1/ai/process \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "tag",
    "content": "Your note content here...",
    "parameters": {"max_tags": 5}
  }'
```

## 🚨 Troubleshooting Daily Issues

### Service Won't Start
```bash
# Check what's using ports
netstat -ano | findstr :8080
netstat -ano | findstr :5678
netstat -ano | findstr :27123

# Kill conflicting processes
taskkill /PID <PID> /F

# Restart services
docker-compose down
docker-compose up -d
```

### API Errors
```bash
# Check API logs
docker-compose logs vault-api | tail -20

# Test API connectivity
curl -v http://localhost:8080/health

# Verify API key
echo $OBSIDIAN_API_KEY
```

### Volume Mount Issues
```bash
# Check WSL mount
ls -la "/mnt/d/Nomade Milionario"

# Fix permissions
sudo chown -R $USER:$USER "/mnt/d/Nomade Milionario"

# Restart with fresh mount
docker-compose down
docker-compose up -d
```

### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Reset database connection
docker-compose restart postgres
docker-compose restart n8n
```

## 📈 Weekly Maintenance Tasks

### Monday: System Health Review
- Check all service logs for errors
- Review API usage patterns
- Update any outdated dependencies

### Wednesday: Performance Optimization
- Analyze response times
- Clean up old logs
- Optimize database queries

### Friday: Backup & Security Review
- Verify backup integrity
- Review access logs
- Update security configurations

## 🔄 Monthly Tasks

### System Updates
```bash
# Update Docker images
docker-compose pull

# Rebuild services
docker-compose build --no-cache

# Restart with new images
docker-compose down
docker-compose up -d
```

### Vault Maintenance
```bash
# Analyze vault growth
du -sh "/mnt/d/Nomade Milionario"

# Check for orphaned files
find "/mnt/d/Nomade Milionario" -name "*.md" -mtime +30

# Optimize vault structure
# (Manual review recommended)
```

## 📱 Mobile Operations

### Daily Mobile Sync Check
```bash
# Test mobile endpoints
curl http://localhost:8080/mobile/v1/health

# Check sync status
curl -H "Authorization: Bearer your_api_key" \
     http://localhost:8080/mobile/v1/sync/status
```

## 🎯 Success Metrics

### Daily KPIs to Monitor
- **API Response Time**: < 200ms average
- **Service Uptime**: > 99%
- **Error Rate**: < 1%
- **Notes Created**: Track daily count
- **AI Processing**: Success rate > 95%

### Weekly Reports
```bash
# Generate usage report
curl -H "Authorization: Bearer your_api_key" \
     http://localhost:8080/api/v1/reports/weekly

# Export metrics
docker-compose logs vault-api | grep "$(date +%Y-%m-%d)" > daily-metrics.log
```

---

## 🎉 Daily Checklist

**Morning (5 minutes):**
- [ ] Check system status: `docker-compose ps`
- [ ] Verify API health: `curl localhost:8080/health`
- [ ] Review overnight logs: `docker-compose logs --since=8h`

**Midday (2 minutes):**
- [ ] Test API endpoints
- [ ] Check n8n workflows
- [ ] Monitor resource usage

**Evening (3 minutes):**
- [ ] Run backup: `./scripts/backup.sh`
- [ ] Review daily metrics
- [ ] Plan tomorrow's tasks

**This manual ensures smooth daily operations of your Obsidian AI automation system!**
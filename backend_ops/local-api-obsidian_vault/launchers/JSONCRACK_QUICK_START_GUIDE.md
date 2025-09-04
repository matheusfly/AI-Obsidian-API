# 🚀 JSON Crack Integration - Quick Start Guide

## Complete Interactive Visualization Setup

This guide will get you up and running with JSON Crack visualization for your Obsidian Vault API in minutes!

## 🎯 What You'll Get

- **Interactive JSON visualization** of all API endpoints
- **Real-time data structure exploration** 
- **MCP tools visualization**
- **Workflow configuration mapping**
- **Vault structure visualization**
- **Custom data visualization capabilities**

## ⚡ Quick Launch (2 Commands)

### Windows (PowerShell)
```powershell
# 1. Start all services
.\launch-jsoncrack.ps1 start

# 2. Open visualization dashboard
.\launch-jsoncrack.ps1 test
```

### Linux/macOS (Bash)
```bash
# 1. Start all services
./launch-jsoncrack.sh start

# 2. Open visualization dashboard  
./launch-jsoncrack.sh test
```

## 🌐 Access Points

Once running, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Main Dashboard** | http://localhost:8081/visualize | Interactive visualization hub |
| **JSON Crack** | http://localhost:3001 | Direct JSON Crack interface |
| **API Docs** | http://localhost:8081/docs | Swagger documentation |
| **n8n Workflows** | http://localhost:5678 | Workflow management |

## 📊 Available Visualizations

### 1. API Endpoints Structure
```
http://localhost:8081/visualize/api-endpoints
```
- Complete REST API structure
- Request/response schemas
- Authentication flows
- Error handling patterns

### 2. MCP Tools Configuration
```
http://localhost:8081/visualize/mcp-tools
```
- Model Context Protocol tools
- Tool arguments and responses
- Integration patterns
- Custom tool definitions

### 3. n8n Workflows
```
http://localhost:8081/visualize/workflows
```
- Workflow node configurations
- Connection mappings
- Execution flows
- Data transformations

### 4. Vault File Structure
```
http://localhost:8081/visualize/vault-structure
```
- Obsidian vault organization
- File relationships
- Metadata structures
- Plugin configurations

## 🛠 Management Commands

### Check Status
```bash
# Windows
.\launch-jsoncrack.ps1 status

# Linux/macOS
./launch-jsoncrack.sh status
```

### View Logs
```bash
# All services
.\launch-jsoncrack.ps1 logs

# Specific service
.\launch-jsoncrack.ps1 logs jsoncrack
```

### Restart Services
```bash
.\launch-jsoncrack.ps1 restart
```

### Clean Everything
```bash
# Windows (with confirmation)
.\launch-jsoncrack.ps1 clean -Clean

# Linux/macOS
./launch-jsoncrack.sh clean true
```

## 🎨 Custom Visualizations

### Create Custom Visualization
```bash
curl -X POST http://localhost:8081/visualize/custom \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"your": "data", "structure": "here"},
    "title": "My Custom Visualization",
    "layout": "hierarchical",
    "theme": "dark"
  }'
```

### Embed in Your App
```html
<iframe 
  src="http://localhost:8081/visualize/embed" 
  width="100%" 
  height="600px" 
  frameborder="0">
</iframe>
```

## 🔧 Configuration

### Environment Variables
```bash
# JSON Crack URL
JSONCRACK_URL=http://localhost:3001

# Enable visualization
ENABLE_VISUALIZATION=true

# Database connection
DATABASE_URL=postgresql://postgres:password@postgres:5432/obsidian_vault

# Redis cache
REDIS_URL=redis://redis:6379
```

### Docker Compose Services
- **jsoncrack**: JSON visualization service
- **vault-api-visual**: Enhanced API with visualization
- **postgres**: Database
- **redis**: Cache
- **n8n**: Workflow automation

## 🚨 Troubleshooting

### Services Not Starting
```bash
# Check Docker is running
docker version

# Check logs
.\launch-jsoncrack.ps1 logs

# Restart everything
.\launch-jsoncrack.ps1 restart
```

### JSON Crack Not Loading
```bash
# Check JSON Crack health
curl http://localhost:3001/api/health

# Check API visualization status
curl http://localhost:8081/visualize/status
```

### Port Conflicts
If ports are in use, modify `docker-compose.jsoncrack.yml`:
```yaml
ports:
  - "3002:3000"  # Change 3001 to 3002
```

## 📈 Performance Tips

1. **Large Data Sets**: Use pagination for large JSON structures
2. **Caching**: Enable Redis caching for frequently accessed data
3. **Node Limits**: Adjust `NEXT_PUBLIC_NODE_LIMIT` for complex visualizations
4. **Memory**: Allocate sufficient memory to Docker containers

## 🔄 Future Custom Features

### Adding New Visualizations

1. **Create new endpoint** in `visualization_endpoints.py`:
```python
@router.get("/my-custom-viz")
async def my_custom_visualization():
    data = {"custom": "data"}
    return await send_to_jsoncrack(data, "My Custom Viz")
```

2. **Add to dashboard** in `main_visual.py`:
```html
<div class="card">
    <h3>My Custom Feature</h3>
    <a href="/visualize/my-custom-viz" class="btn">View</a>
</div>
```

3. **Update launch scripts** to include new service if needed

### Custom Data Sources

```python
# Example: Database query visualization
@router.get("/visualize/database-schema")
async def visualize_database():
    # Query database schema
    schema = await get_database_schema()
    return await send_to_jsoncrack(schema, "Database Schema")
```

### Integration with External APIs

```python
# Example: External API data visualization
@router.get("/visualize/external-api")
async def visualize_external_api():
    # Fetch external data
    external_data = await fetch_external_data()
    return await send_to_jsoncrack(external_data, "External API Data")
```

## 🎉 You're Ready!

Your JSON Crack integration is now fully operational! 

- **Explore** your API structure visually
- **Debug** data flows interactively  
- **Share** visualizations with your team
- **Extend** with custom features

Happy visualizing! 🚀

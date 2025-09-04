# Professional Repository Structure Reference

## Directory Organization

### 📁 launchers/
All main launcher scripts for starting services and systems
- LAUNCH_ALL.ps1
- QUICK_ULTRA_LAUNCHER.ps1
- SMART_ULTRA_LAUNCHER.ps1
- MEGA_VISUAL_LAUNCHER.ps1
- And many more...

### 📚 docs/
All documentation, guides, and references
- README.md
- API documentation
- Setup guides
- Architecture documents

### ⚙️ config/
Configuration files and schemas
- JSON configurations
- Docker compose files
- Environment templates
- Database schemas

### 🔧 scripts/
Utility and setup scripts
- Setup scripts
- Fix scripts
- Installation scripts
- Debug utilities

### 🚀 services/
All service implementations
- aci-server/
- obsidian-api/
- vault-api/
- web-interface/
- And more...

### 🧪 tests/
Test files and reports
- Unit tests
- Integration tests
- Test reports
- Test utilities

### 📝 logs/
Log files and outputs
- Service logs
- Error logs
- Debug outputs

### 💾 data/
Data storage directories
- Application data
- Memory storage
- Cache files

### 📊 monitoring/
Status and monitoring files
- System status
- Dashboards
- Health checks

### 🔗 integrations/
Integration tools and configurations
- MCP configurations
- External tool integrations
- API integrations

### 🛠️ tools/
External tools and utilities
- Third-party tools
- Development utilities
- Helper scripts

## Quick Launch Commands

```powershell
# Launch any script using the master launcher
.\launch.ps1 -Script LAUNCH_ALL.ps1
.\launch.ps1 -Script setup-mcp-tools.ps1 -Category scripts
.\launch.ps1 -Script test-all-services.ps1 -Category tests

# Or run scripts directly from their new locations
.\launchers\LAUNCH_ALL.ps1
.\scripts\setup-mcp-tools.ps1
.\tests\test-all-services.ps1
```

## Benefits of New Structure

1. **Clear Separation**: Each file type has its dedicated directory
2. **Easy Navigation**: Logical grouping makes finding files intuitive
3. **Professional Appearance**: Clean, organized structure
4. **Maintainable**: Easy to add new files in appropriate categories
5. **Scalable**: Structure can grow with the project
6. **Preserved Functionality**: All launchers work with updated paths

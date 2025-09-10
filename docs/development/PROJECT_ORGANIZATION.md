# 📁 **DATA VAULT OBSIDIAN - PROJECT ORGANIZATION GUIDE**

**Version:** 2.0.0  
**Last Updated:** September 6, 2025

---

## 📋 **ORGANIZATION OVERVIEW**

This document outlines the complete project organization structure for the Data Vault Obsidian system. The project has been reorganized to maintain a clean, professional structure with clear separation of concerns.

---

## 🏗️ **FOLDER STRUCTURE**

### **Root Directory**
```
data-vault-obsidian/
├── README.md                          # Main project documentation
├── PROJECT_ORGANIZATION.md            # This file
├── langgraph.json                     # LangGraph configuration
├── docker-compose*.yml                # Docker configurations
└── [Core Directories Below]
```

### **Core Directories**

#### **🔧 Core Services** (`core_services/`)
Contains the main service implementations:
- `langgraph_studio_fixed.py` - Fixed LangGraph Studio server
- `langgraph_studio_server.py` - Custom LangGraph Studio server
- `run_langgraph_dev.py` - LangGraph development runner
- `start_langgraph_dev.py` - LangGraph startup script

#### **📊 Monitoring Tools** (`monitoring_tools/`)
Contains all monitoring and observability tools:
- `raw_data_capture.py` - Raw data capture from services
- `realtime_log_monitor.py` - Real-time log monitoring
- `tracing_analysis.py` - Trace analysis and reporting
- `comprehensive_logging_suite.py` - Complete logging orchestration
- `monitoring_dashboard.py` - Web-based monitoring dashboard
- `active_langsmith_testing.py` - LangSmith testing tools
- `simple_test.py` - Basic testing utilities

#### **🧪 Test Suites** (`test_suites/`)
Contains all testing scripts and utilities:
- `test_*.py` - Individual test scripts
- `test_*.ps1` - PowerShell test scripts
- `comprehensive_test_final.py` - Final comprehensive tests
- `final_langsmith_tracing_report.py` - LangSmith tracing tests

#### **🚀 Deployment** (`deployment/`)
Contains deployment and automation scripts:
- `main_script*.ps1` - Main PowerShell automation scripts
- `uv_build_*.py` - UV build automation
- `uv_build_*.ps1` - UV build PowerShell scripts

#### **📚 Documentation** (`documentation/`)
Contains all project documentation:
- `README.md` - Main project readme
- `backend-infrastructure-analysis-report.md` - Infrastructure analysis
- `OBSIDIAN_LANGGRAPH_CONNECTION_SUCCESS.md` - Success reports

#### **📖 Docs** (`docs/`)
Contains technical documentation:
- `ARCHITECTURE.md` - System architecture
- `SYSTEM_DESIGN.md` - System design patterns
- `MCP_INTEGRATION_GUIDE.md` - MCP integration guide
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `TESTING_STRATEGY.md` - Testing strategies
- `api_reference.md` - API documentation
- `usage_examples.md` - Usage examples

#### **💡 Examples** (`examples/`)
Contains example implementations:
- `mock_obsidian_api.py` - Mock Obsidian API
- `shadcn_dashboard.html` - Dashboard example

#### **📦 Requirements** (`requirements/`)
Contains all requirements files:
- `requirements.txt` - Main requirements
- `requirements-mcp.txt` - MCP-specific requirements
- `requirements-langgraph.txt` - LangGraph requirements
- `requirements-minimal.txt` - Minimal requirements
- `requirements-minimal-api.txt` - Minimal API requirements

#### **🗂️ Temporary Files** (`temp_files/`)
Contains temporary and generated files:
- `logs/` - All log files
- `reports/` - Generated reports
- `test_results/` - Test result files
- `json_data/` - JSON data files
- `scripts/` - Temporary scripts
- `backup/` - Backup files

---

## 🧹 **CLEANUP RULES**

### **Files Moved to temp_files/**
- **Logs**: All `.log` files → `temp_files/logs/`
- **Reports**: All `*_REPORT*.md` files → `temp_files/reports/`
- **JSON Data**: All `.json` files → `temp_files/json_data/`
- **Test Results**: Test output files → `temp_files/test_results/`

### **Files Organized by Type**
- **Test Scripts**: All `test_*.py` and `test_*.ps1` → `test_suites/`
- **Monitoring Tools**: Monitoring and observability scripts → `monitoring_tools/`
- **Core Services**: Main service implementations → `core_services/`
- **Deployment**: Automation and deployment scripts → `deployment/`
- **Documentation**: All `.md` files → `documentation/` or `docs/`
- **Examples**: Example implementations → `examples/`
- **Requirements**: All `requirements*.txt` → `requirements/`

## 🔧 **MCP INTEGRATION RULES**

### **MCP Server Tooling Priority**
- **ALWAYS** prioritize MCP server tooling calls over standard tools
- **MANDATORY** MCP tool availability check before any operation
- **REQUIRED** MCP tool integration in all active writing loops
- **ENFORCED** MCP tool usage patterns and workflows

### **MCP Tool Categories**
1. **Byterover MCP Tools** (Highest Priority)
   - Knowledge management and context operations
   - Handbook and module management
   - Implementation planning and progress tracking
   - Reflection and context assessment

2. **Obsidian MCP Tools** (High Priority)
   - Vault file operations and management
   - Note creation, reading, and updating
   - Search and metadata operations
   - Content organization and structure

3. **Context MCP Tools** (Medium Priority)
   - Context storage and retrieval
   - Context validation and search
   - Knowledge base operations
   - Information management

4. **Standard Development Tools** (Lowest Priority)
   - Only used when MCP tools are unavailable
   - Fallback for basic operations
   - Emergency tooling when MCP servers are down

### **MCP Integration Workflows**
- **Session Initialization**: Check MCP health → Initialize Byterover → Sync handbook
- **Task Execution**: Retrieve knowledge → Assess context → Execute with MCP tools
- **Content Management**: Use Obsidian MCP tools → Store context → Validate results
- **Knowledge Operations**: Store insights → Update modules → Track progress

---

## 🔄 **MAINTENANCE WORKFLOW**

### **Daily Cleanup**
1. Move new log files to `temp_files/logs/`
2. Move new test results to `temp_files/test_results/`
3. Move new reports to `temp_files/reports/`
4. Move new JSON data to `temp_files/json_data/`

### **Weekly Cleanup**
1. Review and archive old files in `temp_files/`
2. Clean up backup files in `temp_files/backup/`
3. Update documentation in `docs/` and `documentation/`

### **Monthly Cleanup**
1. Archive old logs and reports
2. Clean up temporary scripts
3. Update project organization documentation

---

## 📁 **FILE NAMING CONVENTIONS**

### **Scripts**
- `test_*.py` - Python test scripts
- `test_*.ps1` - PowerShell test scripts
- `main_script*.ps1` - Main automation scripts
- `uv_build_*.py` - UV build scripts

### **Reports**
- `*_REPORT_*.md` - Generated reports
- `*_SUCCESS_*.md` - Success reports
- `*_ANALYSIS_*.md` - Analysis reports

### **Logs**
- `*.log` - Log files
- `*_YYYYMMDD_HHMMSS.log` - Timestamped logs

### **Data Files**
- `*.json` - JSON data files
- `*_capture_*.json` - Data capture files
- `*_analysis_*.json` - Analysis result files

---

## 🚀 **QUICK ACCESS**

### **Most Used Directories**
- **`deployment/`** - Main automation scripts
- **`monitoring_tools/`** - Monitoring and observability
- **`test_suites/`** - Testing scripts
- **`docs/`** - Technical documentation

### **Development Workflow**
1. **Start Services**: Use scripts in `deployment/`
2. **Monitor System**: Use tools in `monitoring_tools/`
3. **Run Tests**: Use scripts in `test_suites/`
4. **Check Logs**: Look in `temp_files/logs/`
5. **View Reports**: Check `temp_files/reports/`

---

## 🔧 **AUTOMATION SCRIPTS**

### **PowerShell Cleanup Script**
```powershell
# Clean up temporary files
Get-ChildItem -Path "temp_files\logs" -Name "*.log" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item
Get-ChildItem -Path "temp_files\reports" -Name "*.md" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item
```

### **Python Organization Script**
```python
# Organize new files automatically
import os
import shutil
from datetime import datetime

def organize_new_files():
    # Move new log files
    for file in os.listdir('.'):
        if file.endswith('.log'):
            shutil.move(file, f'temp_files/logs/{file}')
    
    # Move new JSON files
    for file in os.listdir('.'):
        if file.endswith('.json'):
            shutil.move(file, f'temp_files/json_data/{file}')
```

---

## 📊 **ORGANIZATION BENEFITS**

### **Clean Root Directory**
- Easy to navigate
- Clear project structure
- Professional appearance

### **Logical Grouping**
- Related files grouped together
- Easy to find specific functionality
- Clear separation of concerns

### **Maintainability**
- Easy to clean up temporary files
- Clear organization rules
- Automated cleanup possible

### **Scalability**
- Easy to add new file types
- Clear organization patterns
- Consistent structure

---

**Last Updated:** September 6, 2025  
**Organization Version:** 2.0.0

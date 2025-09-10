# 🏗️ **CODE STRUCTURE DEEP DIVE**

**Version:** 3.0.0  
**Last Updated:** September 6, 2025  
**Status:** ✅ **PRODUCTION-READY CODE ARCHITECTURE**

---

## 🎯 **CODE ORGANIZATION PHILOSOPHY**

The Data Vault Obsidian codebase follows **Clean Architecture** principles with **Domain-Driven Design (DDD)** patterns, ensuring **maintainability**, **testability**, and **scalability**.

### **Core Organization Principles**

- **Separation of Concerns** - Each layer has distinct responsibilities
- **Dependency Inversion** - High-level modules don't depend on low-level modules
- **Single Responsibility** - Each class/function has one clear purpose
- **Open/Closed Principle** - Open for extension, closed for modification
- **Interface Segregation** - Clients depend only on interfaces they use

---

## 📁 **DETAILED DIRECTORY STRUCTURE**

> **📖 Detailed Architecture Documentation:** See [docs/architecture/](docs/architecture/) for comprehensive technical documentation including design patterns, code structure, and architectural decisions.

### **🗂️ Complete Directory Walkthrough**

#### **📁 Source Code (`src/`) - Clean Architecture Implementation**
```
src/
├── 📁 presentation/           # 🎨 User Interface Layer
│   ├── 📁 api/               # 🌐 REST API Endpoints
│   │   ├── 📁 v1/            # 📋 API Version 1
│   │   │   ├── 📁 obsidian/  # 📝 Obsidian API (Notes, Search, Files)
│   │   │   ├── 📁 langgraph/ # 🔄 LangGraph API (Workflows, Agents)
│   │   │   ├── 📁 mcp/       # 🔌 MCP API (Tools, Servers)
│   │   │   └── 📁 monitoring/# 📊 Monitoring API (Metrics, Health)
│   │   ├── 📁 middleware/    # ⚙️ API Middleware (Auth, Logging, Tracing)
│   │   └── 📁 schemas/       # 📋 API Data Schemas
│   ├── 📁 web/               # 🌐 Web Interfaces
│   │   ├── 📁 dashboard/     # 📊 Monitoring Dashboard
│   │   ├── 📁 studio/        # 🎨 LangGraph Studio Interface
│   │   └── 📁 admin/         # 👨‍💼 Admin Interface
│   └── 📁 cli/               # 💻 Command Line Interface
│       ├── 📁 commands/      # 📝 CLI Commands
│       └── 📁 interfaces/    # 🖥️ CLI Interfaces
├── 📁 application/           # 🏢 Business Logic Layer
│   ├── 📁 use_cases/         # 🎯 Business Use Cases
│   │   ├── 📁 obsidian/      # 📝 Obsidian Use Cases
│   │   ├── 📁 langgraph/     # 🔄 LangGraph Use Cases
│   │   ├── 📁 mcp/           # 🔌 MCP Use Cases
│   │   └── 📁 monitoring/    # 📊 Monitoring Use Cases
│   ├── 📁 services/          # 🔧 Application Services
│   │   ├── 📁 obsidian/      # 📝 Obsidian Services
│   │   ├── 📁 langgraph/     # 🔄 LangGraph Services
│   │   ├── 📁 mcp/           # 🔌 MCP Services
│   │   └── 📁 monitoring/    # 📊 Monitoring Services
│   ├── 📁 dto/               # 📦 Data Transfer Objects
│   │   ├── 📁 requests/      # 📥 Request DTOs
│   │   ├── 📁 responses/     # 📤 Response DTOs
│   │   └── 📁 internal/      # 🔒 Internal DTOs
│   └── 📁 interfaces/        # 🔌 Service Interfaces
│       ├── 📁 repositories/  # 🗄️ Repository Interfaces
│       ├── 📁 services/      # 🔧 Service Interfaces
│       └── 📁 external/      # 🌐 External Service Interfaces
├── 📁 domain/                # 🏛️ Business Domain Layer
│   ├── 📁 entities/          # 🏗️ Domain Entities
│   │   ├── 📁 obsidian/      # 📝 Obsidian Entities (Note, File, Metadata)
│   │   ├── 📁 langgraph/     # 🔄 LangGraph Entities (Workflow, Agent, State)
│   │   ├── 📁 mcp/           # 🔌 MCP Entities (Tool, Server, Parameter)
│   │   └── 📁 monitoring/    # 📊 Monitoring Entities (Metric, Alert, Trace)
│   ├── 📁 value_objects/     # 💎 Value Objects
│   │   ├── 📁 common/        # 🔄 Common Value Objects (ID, Timestamp, Status)
│   │   └── 📁 specific/      # 🎯 Specific Value Objects (Title, Content, Path)
│   ├── 📁 repositories/      # 🗄️ Repository Interfaces
│   │   ├── 📁 obsidian/      # 📝 Obsidian Repository Interfaces
│   │   ├── 📁 langgraph/     # 🔄 LangGraph Repository Interfaces
│   │   ├── 📁 mcp/           # 🔌 MCP Repository Interfaces
│   │   └── 📁 monitoring/    # 📊 Monitoring Repository Interfaces
│   ├── 📁 services/          # 🔧 Domain Services
│   │   ├── 📁 obsidian/      # 📝 Obsidian Domain Services
│   │   ├── 📁 langgraph/     # 🔄 LangGraph Domain Services
│   │   ├── 📁 mcp/           # 🔌 MCP Domain Services
│   │   └── 📁 monitoring/    # 📊 Monitoring Domain Services
│   └── 📁 events/            # 📢 Domain Events
│       ├── 📁 obsidian/      # 📝 Obsidian Events (Note Created, Updated, Deleted)
│       ├── 📁 langgraph/     # 🔄 LangGraph Events (Workflow Started, Completed)
│       ├── 📁 mcp/           # 🔌 MCP Events (Tool Discovered, Executed)
│       └── 📁 monitoring/    # 📊 Monitoring Events (Metric Collected, Alert Triggered)
└── 📁 infrastructure/        # 🏗️ Infrastructure Layer
    ├── 📁 persistence/       # 🗄️ Data Persistence
    │   ├── 📁 repositories/  # 🗄️ Repository Implementations
    │   │   ├── 📁 obsidian/  # 📝 Obsidian Repository Implementations
    │   │   ├── 📁 langgraph/ # 🔄 LangGraph Repository Implementations
    │   │   ├── 📁 mcp/       # 🔌 MCP Repository Implementations
    │   │   └── 📁 monitoring/# 📊 Monitoring Repository Implementations
    │   ├── 📁 models/        # 📋 Data Models
    │   │   ├── 📁 obsidian/  # 📝 Obsidian Data Models
    │   │   ├── 📁 langgraph/ # 🔄 LangGraph Data Models
    │   │   ├── 📁 mcp/       # 🔌 MCP Data Models
    │   │   └── 📁 monitoring/# 📊 Monitoring Data Models
    │   └── 📁 migrations/    # 🔄 Database Migrations
    │       ├── 📁 alembic/   # 🔄 Alembic Migrations
    │       └── 📁 scripts/   # 📝 Migration Scripts
    ├── 📁 external/          # 🌐 External Services
    │   ├── 📁 obsidian/      # 📝 Obsidian External Services
    │   ├── 📁 langgraph/     # 🔄 LangGraph External Services
    │   ├── 📁 mcp/           # 🔌 MCP External Services
    │   └── 📁 monitoring/    # 📊 Monitoring External Services
    ├── 📁 messaging/         # 📨 Message Queues and Events
    │   ├── 📁 queues/        # 📨 Message Queues
    │   ├── 📁 handlers/      # 📨 Event Handlers
    │   └── 📁 publishers/    # 📨 Event Publishers
    ├── 📁 monitoring/        # 📊 Monitoring and Observability
    │   ├── 📁 metrics/       # 📊 Metrics Collection
    │   ├── 📁 logging/       # 📝 Logging Infrastructure
    │   └── 📁 tracing/       # 🔍 Distributed Tracing
    └── 📁 config/            # ⚙️ Configuration Management
        ├── 📁 environments/  # 🌍 Environment Configurations
        ├── 📁 secrets/       # 🔐 Secret Management
        └── 📁 validation/    # ✅ Configuration Validation
```

#### **🔧 Services (`services/`) - Microservices Architecture**
```
services/
├── 📁 obsidian-service/      # 📝 Obsidian Microservice
│   ├── 📁 src/              # 🏗️ Service Source Code
│   ├── 📁 tests/            # 🧪 Service Tests
│   ├── 📁 docs/             # 📚 Service Documentation
│   └── 📁 config/           # ⚙️ Service Configuration
├── 📁 langgraph-service/     # 🔄 LangGraph Microservice
│   ├── 📁 src/              # 🏗️ Service Source Code
│   ├── 📁 tests/            # 🧪 Service Tests
│   ├── 📁 docs/             # 📚 Service Documentation
│   └── 📁 config/           # ⚙️ Service Configuration
├── 📁 mcp-service/           # 🔌 MCP Microservice
│   ├── 📁 src/              # 🏗️ Service Source Code
│   ├── 📁 tests/            # 🧪 Service Tests
│   ├── 📁 docs/             # 📚 Service Documentation
│   └── 📁 config/           # ⚙️ Service Configuration
├── 📁 monitoring-service/    # 📊 Monitoring Microservice
│   ├── 📁 src/              # 🏗️ Service Source Code
│   ├── 📁 tests/            # 🧪 Service Tests
│   ├── 📁 docs/             # 📚 Service Documentation
│   └── 📁 config/           # ⚙️ Service Configuration
└── 📁 api-gateway/           # 🌐 API Gateway Service
    ├── 📁 src/              # 🏗️ Gateway Source Code
    ├── 📁 tests/            # 🧪 Gateway Tests
    ├── 📁 docs/             # 📚 Gateway Documentation
    └── 📁 config/           # ⚙️ Gateway Configuration
```

#### **📱 Applications (`apps/`) - User Applications**
```
apps/
├── 📁 web-app/               # 🌐 Web Application
│   ├── 📁 frontend/          # 🎨 Frontend (React/Vue/Angular)
│   ├── 📁 backend/           # 🏗️ Backend API
│   ├── 📁 shared/            # 🔄 Shared Components
│   └── 📁 docs/              # 📚 App Documentation
├── 📁 studio-app/            # 🎨 LangGraph Studio App
│   ├── 📁 src/               # 🏗️ Studio Source Code
│   ├── 📁 config/            # ⚙️ Studio Configuration
│   ├── 📁 workflows/         # 🔄 Workflow Definitions
│   └── 📁 docs/              # 📚 Studio Documentation
├── 📁 dashboard-app/         # 📊 Monitoring Dashboard App
│   ├── 📁 src/               # 🏗️ Dashboard Source Code
│   ├── 📁 components/        # 🧩 Dashboard Components
│   ├── 📁 charts/            # 📈 Chart Components
│   └── 📁 docs/              # 📚 Dashboard Documentation
└── 📁 cli-app/               # 💻 CLI Application
    ├── 📁 src/               # 🏗️ CLI Source Code
    ├── 📁 commands/          # 📝 CLI Commands
    ├── 📁 interfaces/        # 🖥️ CLI Interfaces
    └── 📁 docs/              # 📚 CLI Documentation
```

#### **🏗️ Infrastructure (`infrastructure/`) - Infrastructure as Code**
```
infrastructure/
├── 📁 docker/                # 🐳 Docker Configurations
│   ├── 📁 services/          # 🐳 Service Dockerfiles
│   ├── 📁 compose/           # 🐳 Docker Compose Files
│   ├── 📁 scripts/           # 📝 Docker Scripts
│   └── 📁 docs/              # 📚 Docker Documentation
├── 📁 kubernetes/            # ☸️ Kubernetes Manifests
│   ├── 📁 namespaces/        # 📁 K8s Namespaces
│   ├── 📁 deployments/       # 🚀 K8s Deployments
│   ├── 📁 services/          # 🌐 K8s Services
│   ├── 📁 configmaps/        # ⚙️ K8s ConfigMaps
│   ├── 📁 secrets/           # 🔐 K8s Secrets
│   └── 📁 docs/              # 📚 K8s Documentation
├── 📁 terraform/             # 🏗️ Terraform Configurations
│   ├── 📁 modules/           # 🧩 Terraform Modules
│   ├── 📁 environments/      # 🌍 Environment Configs
│   ├── 📁 scripts/           # 📝 Terraform Scripts
│   └── 📁 docs/              # 📚 Terraform Documentation
└── 📁 monitoring/            # 📊 Monitoring Configurations
    ├── 📁 prometheus/        # 📊 Prometheus Configs
    ├── 📁 grafana/           # 📈 Grafana Dashboards
    ├── 📁 alertmanager/      # 🚨 Alert Manager Configs
    └── 📁 docs/              # 📚 Monitoring Documentation
```

#### **🧪 Testing (`tests/`) - Comprehensive Testing Suite**
```
tests/
├── 📁 unit/                  # 🧪 Unit Tests
│   ├── 📁 domain/            # 🏛️ Domain Layer Tests
│   ├── 📁 application/       # 🏢 Application Layer Tests
│   ├── 📁 infrastructure/    # 🏗️ Infrastructure Layer Tests
│   └── 📁 presentation/      # 🎨 Presentation Layer Tests
├── 📁 integration/           # 🔗 Integration Tests
│   ├── 📁 api/               # 🌐 API Integration Tests
│   ├── 📁 services/          # 🔧 Service Integration Tests
│   ├── 📁 database/          # 🗄️ Database Integration Tests
│   └── 📁 external/          # 🌐 External Service Tests
├── 📁 e2e/                   # 🎯 End-to-End Tests
│   ├── 📁 workflows/         # 🔄 Workflow E2E Tests
│   ├── 📁 scenarios/         # 📋 Scenario E2E Tests
│   └── 📁 user-journeys/     # 👤 User Journey Tests
├── 📁 performance/           # ⚡ Performance Tests
│   ├── 📁 load/              # 📊 Load Tests
│   ├── 📁 stress/            # 💪 Stress Tests
│   └── 📁 benchmark/         # 📈 Benchmark Tests
└── 📁 fixtures/              # 🧩 Test Fixtures
    ├── 📁 data/              # 📊 Test Data
    ├── 📁 mocks/             # 🎭 Mock Objects
    └── 📁 helpers/           # 🛠️ Test Helpers
```

#### **📚 Documentation (`docs/`) - Complete Documentation Suite**
```
docs/
├── 📁 architecture/          # 🏗️ Architecture Documentation
│   ├── 📄 README.md          # 📋 Architecture Overview
│   ├── 📄 DESIGN_PATTERNS.md # 🎨 Design Patterns
│   ├── 📄 CODE_STRUCTURE_DEEP_DIVE.md # 🏗️ Code Structure
│   ├── 📄 MCP_INTEGRATION_PATTERNS.md # 🔌 MCP Integration
│   ├── 📄 LANGGRAPH_WORKFLOW_ARCHITECTURE.md # 🔄 LangGraph Workflows
│   └── 📄 OBSERVABILITY_MONITORING_PATTERNS.md # 📊 Observability
├── 📁 api/                   # 🌐 API Documentation
│   ├── 📁 openapi/           # 📋 OpenAPI Specifications
│   ├── 📁 integrations/      # 🔗 Integration Guides
│   ├── 📁 authentication/    # 🔐 Authentication Guides
│   └── 📁 examples/          # 📝 API Examples
├── 📁 deployment/            # 🚀 Deployment Documentation
│   ├── 📁 docker/            # 🐳 Docker Deployment
│   ├── 📁 kubernetes/        # ☸️ Kubernetes Deployment
│   ├── 📁 terraform/         # 🏗️ Terraform Deployment
│   └── 📁 monitoring/        # 📊 Monitoring Setup
├── 📁 development/           # 🛠️ Development Documentation
│   ├── 📁 guides/            # 📖 Development Guides
│   ├── 📁 reports/           # 📊 Development Reports
│   │   ├── 📁 success_reports/ # ✅ Success Reports
│   │   ├── 📁 analysis/      # 📈 Analysis Reports
│   │   ├── 📁 testing/       # 🧪 Testing Reports
│   │   └── 📁 deployment/    # 🚀 Deployment Reports
│   ├── 📄 PROJECT_ORGANIZATION.md # 📁 Project Organization
│   ├── 📄 TEMP_FILES_SUBFOLDER_LOGIC.md # 📁 Temp Files Logic
│   └── 📄 CHANGELOG_INDEX.md # 📅 Changelog Index
└── 📁 user/                  # 👥 User Documentation
    ├── 📁 getting-started/   # 🚀 Getting Started
    ├── 📁 features/          # ✨ Feature Guides
    ├── 📁 troubleshooting/   # 🔧 Troubleshooting
    └── 📁 examples/          # 📝 Usage Examples
```

#### **🛠️ Scripts (`scripts/`) - Automation and Maintenance**
```
scripts/
├── 📁 maintenance/           # 🔧 Maintenance Scripts
│   ├── 📄 final_root_cleanup.ps1 # 🧹 Final Root Cleanup
│   ├── 📄 restructure_to_production.ps1 # 🏗️ Production Restructuring
│   ├── 📄 organize_remaining_files.ps1 # 📁 File Organization
│   └── 📄 persistent_file_organization.ps1 # 📁 Persistent Organization
├── 📁 build/                 # 🏗️ Build Scripts
│   ├── 📄 build_all.ps1      # 🏗️ Build All Services
│   ├── 📄 build_docker.ps1   # 🐳 Build Docker Images
│   └── 📄 build_k8s.ps1      # ☸️ Build K8s Manifests
├── 📁 deploy/                # 🚀 Deployment Scripts
│   ├── 📄 deploy_local.ps1   # 🏠 Local Deployment
│   ├── 📄 deploy_staging.ps1 # 🧪 Staging Deployment
│   └── 📄 deploy_production.ps1 # 🚀 Production Deployment
├── 📁 test/                  # 🧪 Test Scripts
│   ├── 📄 run_unit_tests.ps1 # 🧪 Run Unit Tests
│   ├── 📄 run_integration_tests.ps1 # 🔗 Run Integration Tests
│   └── 📄 run_e2e_tests.ps1  # 🎯 Run E2E Tests
└── 📁 dev/                   # 🛠️ Development Scripts
    ├── 📄 setup_dev_env.ps1  # 🛠️ Setup Dev Environment
    ├── 📄 start_services.ps1 # 🚀 Start Services
    └── 📄 stop_services.ps1  # 🛑 Stop Services
```

#### **🔧 Tools (`tools/`) - Development Tools**
```
tools/
├── 📁 linting/               # 🔍 Code Linting Tools
│   ├── 📄 eslint.config.js   # 🔍 ESLint Configuration
│   ├── 📄 pylint.rc          # 🐍 Pylint Configuration
│   └── 📄 run_linting.ps1    # 🔍 Run Linting Script
├── 📁 formatting/            # 🎨 Code Formatting Tools
│   ├── 📄 prettier.config.js # 🎨 Prettier Configuration
│   ├── 📄 black.toml         # 🐍 Black Configuration
│   └── 📄 run_formatting.ps1 # 🎨 Run Formatting Script
├── 📁 testing/               # 🧪 Testing Tools
│   ├── 📄 jest.config.js     # 🧪 Jest Configuration
│   ├── 📄 pytest.ini        # 🐍 Pytest Configuration
│   └── 📄 run_testing.ps1    # 🧪 Run Testing Script
└── 📁 monitoring/            # 📊 Monitoring Tools
    ├── 📄 prometheus.yml      # 📊 Prometheus Configuration
    ├── 📄 grafana/           # 📈 Grafana Dashboards
    └── 📄 run_monitoring.ps1 # 📊 Run Monitoring Script
```

#### **📊 Data (`data/`) - Data Storage and Management**
```
data/
├── 📁 raw/                   # 📊 Raw Data
│   ├── 📁 obsidian/          # 📝 Obsidian Raw Data
│   ├── 📁 langgraph/         # 🔄 LangGraph Raw Data
│   └── 📁 mcp/               # 🔌 MCP Raw Data
├── 📁 processed/             # 🔄 Processed Data
│   ├── 📁 indexed/           # 📇 Indexed Data
│   ├── 📁 transformed/       # 🔄 Transformed Data
│   └── 📁 aggregated/        # 📊 Aggregated Data
├── 📁 cache/                 # 💾 Cache Data
│   ├── 📁 redis/             # 🔴 Redis Cache
│   ├── 📁 memory/            # 🧠 Memory Cache
│   └── 📁 file/              # 📁 File Cache
└── 📁 backups/               # 💾 Backup Data
    ├── 📁 daily/             # 📅 Daily Backups
    ├── 📁 weekly/            # 📅 Weekly Backups
    └── 📁 monthly/           # 📅 Monthly Backups
```

#### **📝 Logs (`logs/`) - Log Management**
```
logs/
├── 📁 application/           # 📱 Application Logs
│   ├── 📁 obsidian/          # 📝 Obsidian Service Logs
│   ├── 📁 langgraph/         # 🔄 LangGraph Service Logs
│   ├── 📁 mcp/               # 🔌 MCP Service Logs
│   └── 📁 monitoring/        # 📊 Monitoring Service Logs
├── 📁 system/                # 🖥️ System Logs
│   ├── 📁 docker/            # 🐳 Docker Logs
│   ├── 📁 kubernetes/        # ☸️ Kubernetes Logs
│   └── 📁 infrastructure/    # 🏗️ Infrastructure Logs
└── 📁 audit/                 # 🔍 Audit Logs
    ├── 📁 security/          # 🔐 Security Audit Logs
    ├── 📁 access/            # 🚪 Access Audit Logs
    └── 📁 compliance/        # ✅ Compliance Audit Logs
```

#### **📁 Temp (`temp/`) - Temporary Files Management**
```
temp/
├── 📁 development/           # 🛠️ Development Temp Files
│   ├── 📁 active_tests/      # 🧪 Active Testing Files
│   ├── 📁 feature_development/ # ✨ Feature Development Files
│   ├── 📁 experimental/      # 🧪 Experimental Files
│   └── 📁 backup/            # 💾 Backup Files
├── 📁 testing/               # 🧪 Testing Temp Files
│   ├── 📁 test_results/      # 📊 Test Result Files
│   ├── 📁 test_data/         # 📊 Test Data Files
│   ├── 📁 test_logs/         # 📝 Test Log Files
│   └── 📁 test_reports/      # 📊 Test Report Files
└── 📁 build/                 # 🏗️ Build Temp Files
    ├── 📁 build_artifacts/   # 🏗️ Build Artifact Files
    ├── 📁 build_logs/        # 📝 Build Log Files
    ├── 📁 build_cache/       # 💾 Build Cache Files
    └── 📁 build_reports/     # 📊 Build Report Files
```

### **🧹 Production Organization**

- **Clean Architecture** - Layered structure with clear boundaries
- **Microservices** - Independent, scalable services
- **Professional Structure** - Industry-standard organization
- **Automated Maintenance** - Use `scripts\maintenance\` for cleanup

---

## 🔧 **CODE PATTERNS & CONVENTIONS**

### **1. Naming Conventions**

#### **File Naming**
```python
# Use snake_case for file names
note_service.py
workflow_executor.py
mcp_integration_server.py

# Use descriptive names that indicate purpose
create_note_use_case.py
obsidian_api_client.py
langsmith_tracing_service.py
```

#### **Class Naming**
```python
# Use PascalCase for class names
class NoteService:
    pass

class WorkflowExecutor:
    pass

class MCPIntegrationServer:
    pass

# Use descriptive names with purpose
class CreateNoteUseCase:
    pass

class ObsidianAPIClient:
    pass

class LangSmithTracingService:
    pass
```

#### **Function and Variable Naming**
```python
# Use snake_case for functions and variables
def create_note(title: str, content: str) -> Note:
    pass

def execute_workflow(workflow_id: str) -> WorkflowResult:
    pass

# Use descriptive names
def process_obsidian_note(note_data: dict) -> ProcessedNote:
    pass

def validate_mcp_tool_parameters(parameters: dict) -> bool:
    pass
```

### **2. Import Organization**

#### **Import Structure**
```python
# Standard library imports
import asyncio
import json
import time
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

# Third-party imports
import fastapi
import pydantic
import sqlalchemy
from langchain import LangChain
from langgraph import StateGraph

# Local imports
from src.domain.entities.obsidian.note import Note
from src.domain.value_objects.common.id import ID
from src.application.services.obsidian.note_service import NoteService
from src.infrastructure.persistence.repositories.obsidian.sql_note_repository import SQLNoteRepository
```

### **3. Error Handling Patterns**

#### **Custom Exception Hierarchy**
```python
# Base exceptions
class DataVaultObsidianError(Exception):
    """Base exception for Data Vault Obsidian"""
    pass

class DomainError(DataVaultObsidianError):
    """Domain layer error"""
    pass

class ApplicationError(DataVaultObsidianError):
    """Application layer error"""
    pass

class InfrastructureError(DataVaultObsidianError):
    """Infrastructure layer error"""
    pass

# Specific exceptions
class NoteNotFoundError(DomainError):
    """Note not found error"""
    pass

class InvalidNoteContentError(DomainError):
    """Invalid note content error"""
    pass

class MCPToolExecutionError(ApplicationError):
    """MCP tool execution error"""
    pass

class DatabaseConnectionError(InfrastructureError):
    """Database connection error"""
    pass
```

#### **Error Handling in Services**
```python
class NoteService:
    def __init__(self, note_repository: NoteRepository):
        self.note_repository = note_repository
    
    async def get_note(self, note_id: str) -> Note:
        """Get note by ID with proper error handling"""
        try:
            note = await self.note_repository.find_by_id(note_id)
            if not note:
                raise NoteNotFoundError(f"Note with ID {note_id} not found")
            return note
        except DatabaseConnectionError as e:
            logger.error(f"Database connection error: {e}")
            raise InfrastructureError("Unable to connect to database") from e
        except Exception as e:
            logger.error(f"Unexpected error getting note {note_id}: {e}")
            raise ApplicationError("Failed to get note") from e
```

### **4. Dependency Injection Patterns**

#### **Service Container**
```python
class ServiceContainer:
    def __init__(self):
        self._services = {}
        self._singletons = {}
    
    def register_singleton(self, interface: type, implementation: type):
        """Register singleton service"""
        self._services[interface] = implementation
    
    def register_transient(self, interface: type, implementation: type):
        """Register transient service"""
        self._services[interface] = implementation
    
    def get_service(self, interface: type):
        """Get service instance"""
        if interface in self._singletons:
            return self._singletons[interface]
        
        if interface not in self._services:
            raise ServiceNotFoundError(f"Service {interface} not registered")
        
        implementation = self._services[interface]
        instance = implementation()
        
        # Check if it should be singleton
        if hasattr(implementation, '_singleton') and implementation._singleton:
            self._singletons[interface] = instance
        
        return instance

# Usage
container = ServiceContainer()
container.register_singleton(NoteRepository, SQLNoteRepository)
container.register_transient(NoteService, NoteService)

note_service = container.get_service(NoteService)
```

### **5. Configuration Patterns**

#### **Configuration Classes**
```python
from pydantic import BaseSettings, Field
from typing import Optional

class DatabaseConfig(BaseSettings):
    host: str = Field(..., env='DB_HOST')
    port: int = Field(5432, env='DB_PORT')
    username: str = Field(..., env='DB_USERNAME')
    password: str = Field(..., env='DB_PASSWORD')
    database: str = Field(..., env='DB_NAME')
    
    class Config:
        env_file = '.env'

class ObsidianConfig(BaseSettings):
    vault_path: str = Field(..., env='OBSIDIAN_VAULT_PATH')
    api_port: int = Field(27123, env='OBSIDIAN_API_PORT')
    api_token: Optional[str] = Field(None, env='OBSIDIAN_API_TOKEN')
    
    class Config:
        env_file = '.env'

class LangSmithConfig(BaseSettings):
    api_key: str = Field(..., env='LANGSMITH_API_KEY')
    project: str = Field(..., env='LANGSMITH_PROJECT')
    endpoint: str = Field('https://api.smith.langchain.com', env='LANGSMITH_ENDPOINT')
    
    class Config:
        env_file = '.env'

class AppConfig(BaseSettings):
    database: DatabaseConfig = DatabaseConfig()
    obsidian: ObsidianConfig = ObsidianConfig()
    langsmith: LangSmithConfig = LangSmithConfig()
    debug: bool = Field(False, env='DEBUG')
    log_level: str = Field('INFO', env='LOG_LEVEL')
    
    class Config:
        env_file = '.env'
```

---

## 🧪 **TESTING STRUCTURE**

### **Test Organization**
```
tests/
├── unit/                           # Unit Tests
│   ├── domain/                     # Domain layer tests
│   │   ├── entities/               # Entity tests
│   │   ├── value_objects/          # Value object tests
│   │   ├── services/               # Domain service tests
│   │   └── events/                 # Event tests
│   ├── application/                # Application layer tests
│   │   ├── use_cases/              # Use case tests
│   │   ├── services/               # Application service tests
│   │   └── dto/                    # DTO tests
│   └── infrastructure/             # Infrastructure layer tests
│       ├── persistence/            # Persistence tests
│       ├── external/               # External service tests
│       └── messaging/              # Messaging tests
├── integration/                    # Integration Tests
│   ├── api/                        # API integration tests
│   ├── services/                   # Service integration tests
│   └── database/                   # Database integration tests
├── e2e/                           # End-to-End Tests
│   ├── workflows/                  # Workflow tests
│   └── scenarios/                  # Scenario tests
└── fixtures/                       # Test Fixtures
    ├── data/                       # Test data
    ├── mocks/                      # Mock objects
    └── helpers/                    # Test helpers
```

### **Test Patterns**

#### **Unit Test Pattern**
```python
import pytest
from unittest.mock import Mock, AsyncMock
from src.domain.entities.obsidian.note import Note
from src.application.use_cases.obsidian.create_note import CreateNoteUseCase

class TestCreateNoteUseCase:
    def setup_method(self):
        """Setup test method"""
        self.mock_repository = Mock()
        self.mock_event_publisher = Mock()
        self.use_case = CreateNoteUseCase(
            note_repository=self.mock_repository,
            event_publisher=self.mock_event_publisher
        )
    
    async def test_execute_success(self):
        """Test successful note creation"""
        # Arrange
        request = CreateNoteRequest(
            title="Test Note",
            content="Test Content",
            metadata={"tags": ["test"]}
        )
        
        expected_note = Note(
            id="test-id",
            title="Test Note",
            content="Test Content",
            metadata={"tags": ["test"]}
        )
        
        self.mock_repository.save = AsyncMock(return_value=expected_note)
        self.mock_event_publisher.publish = AsyncMock()
        
        # Act
        result = await self.use_case.execute(request)
        
        # Assert
        assert result.note_id == "test-id"
        assert result.title == "Test Note"
        self.mock_repository.save.assert_called_once()
        self.mock_event_publisher.publish.assert_called_once()
    
    async def test_execute_invalid_title_raises_error(self):
        """Test error handling for invalid title"""
        # Arrange
        request = CreateNoteRequest(
            title="",  # Invalid empty title
            content="Test Content",
            metadata={}
        )
        
        # Act & Assert
        with pytest.raises(InvalidNoteContentError):
            await self.use_case.execute(request)
```

#### **Integration Test Pattern**
```python
import pytest
from httpx import AsyncClient
from src.main import app

class TestObsidianAPI:
    @pytest.fixture
    async def client(self):
        """Create test client"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    async def test_create_note_endpoint(self, client):
        """Test create note API endpoint"""
        # Arrange
        note_data = {
            "title": "Test Note",
            "content": "Test Content",
            "metadata": {"tags": ["test"]}
        }
        
        # Act
        response = await client.post("/api/v1/obsidian/notes", json=note_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Note"
        assert data["content"] == "Test Content"
        assert "id" in data
```

---

**Last Updated:** September 6, 2025  
**Code Structure Version:** 3.0.0  
**Status:** ✅ **PRODUCTION-READY**

**CENTRALIZED REPORTS & CHANGELOG SYSTEM COMPLETE!**

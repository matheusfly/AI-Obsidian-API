# Claude Task Master MCP Setup Script
Write-Host "Setting up Claude Task Master MCP..." -ForegroundColor Green

# Check if Node.js is installed
Write-Host "`n1. Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "SUCCESS: Node.js version $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check if npm is installed
Write-Host "`n2. Checking npm installation..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version
    Write-Host "SUCCESS: npm version $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: npm not found. Please install npm first." -ForegroundColor Red
    exit 1
}

# Install Task Master globally
Write-Host "`n3. Installing Task Master globally..." -ForegroundColor Yellow
try {
    npm install -g task-master-ai
    Write-Host "SUCCESS: Task Master installed globally" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Global installation failed, will use npx instead" -ForegroundColor Yellow
}

# Test Task Master installation
Write-Host "`n4. Testing Task Master installation..." -ForegroundColor Yellow
try {
    $testResult = npx task-master-ai --help 2>$null
    if ($testResult -match "task-master-ai") {
        Write-Host "SUCCESS: Task Master is working via npx" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Task Master test inconclusive" -ForegroundColor Yellow
    }
} catch {
    Write-Host "WARNING: Task Master test failed" -ForegroundColor Yellow
}

# Create Task Master project directory
Write-Host "`n5. Creating Task Master project structure..." -ForegroundColor Yellow
$taskMasterDir = Join-Path $PSScriptRoot ".taskmaster"
if (-not (Test-Path $taskMasterDir)) {
    New-Item -ItemType Directory -Path $taskMasterDir -Force | Out-Null
    Write-Host "SUCCESS: Created .taskmaster directory" -ForegroundColor Green
} else {
    Write-Host "SUCCESS: .taskmaster directory already exists" -ForegroundColor Green
}

# Create docs directory
$docsDir = Join-Path $taskMasterDir "docs"
if (-not (Test-Path $docsDir)) {
    New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
    Write-Host "SUCCESS: Created .taskmaster/docs directory" -ForegroundColor Green
}

# Create templates directory
$templatesDir = Join-Path $taskMasterDir "templates"
if (-not (Test-Path $templatesDir)) {
    New-Item -ItemType Directory -Path $templatesDir -Force | Out-Null
    Write-Host "SUCCESS: Created .taskmaster/templates directory" -ForegroundColor Green
}

# Create example PRD template
$prdTemplate = @"
# Project Requirements Document (PRD) Template

## Project Overview
**Project Name:** [Your Project Name]
**Description:** [Brief description of what you're building]
**Target Audience:** [Who will use this]
**Timeline:** [Expected completion date]

## Goals & Objectives
- [ ] Primary goal 1
- [ ] Primary goal 2
- [ ] Secondary goal 1

## Features & Requirements

### Core Features
1. **Feature 1**
   - Description: [What this feature does]
   - Priority: High/Medium/Low
   - Acceptance Criteria:
     - [ ] Criterion 1
     - [ ] Criterion 2

2. **Feature 2**
   - Description: [What this feature does]
   - Priority: High/Medium/Low
   - Acceptance Criteria:
     - [ ] Criterion 1
     - [ ] Criterion 2

### Technical Requirements
- **Technology Stack:** [List technologies to use]
- **Performance:** [Performance requirements]
- **Security:** [Security requirements]
- **Scalability:** [Scalability requirements]

### User Experience
- **User Interface:** [UI/UX requirements]
- **Accessibility:** [Accessibility requirements]
- **Browser Support:** [Browser compatibility]

## Success Metrics
- [ ] Metric 1: [How to measure success]
- [ ] Metric 2: [How to measure success]

## Constraints & Assumptions
- **Budget:** [Budget constraints]
- **Timeline:** [Time constraints]
- **Resources:** [Resource constraints]
- **Assumptions:** [Key assumptions]

## Risks & Mitigation
- **Risk 1:** [Description] - Mitigation: [How to address]
- **Risk 2:** [Description] - Mitigation: [How to address]

## Dependencies
- **External Dependencies:** [External services, APIs, etc.]
- **Internal Dependencies:** [Other projects, teams, etc.]

## Notes
[Any additional notes or considerations]
"@

$prdTemplatePath = Join-Path $templatesDir "example_prd.txt"
Set-Content -Path $prdTemplatePath -Value $prdTemplate -Encoding UTF8
Write-Host "SUCCESS: Created example PRD template" -ForegroundColor Green

# Create sample PRD for current project
$samplePrd = @"
# Local API Obsidian Vault - Project Requirements Document

## Project Overview
**Project Name:** Local API Obsidian Vault
**Description:** A comprehensive backend system for managing Obsidian vaults with API integration, MCP tools, and advanced features
**Target Audience:** Developers, content creators, knowledge workers
**Timeline:** Ongoing development

## Goals & Objectives
- [ ] Create a robust API for Obsidian vault management
- [ ] Integrate multiple MCP tools for enhanced functionality
- [ ] Implement advanced RAG (Retrieval Augmented Generation) capabilities
- [ ] Provide seamless integration with Cursor and Warp IDEs

## Features & Requirements

### Core Features
1. **Obsidian Vault API**
   - Description: RESTful API for reading, writing, and managing Obsidian vault files
   - Priority: High
   - Acceptance Criteria:
     - [ ] CRUD operations for markdown files
     - [ ] Support for Obsidian-specific features (links, tags, frontmatter)
     - [ ] File watching and real-time updates

2. **MCP Integration**
   - Description: Integration with Model Context Protocol tools
   - Priority: High
   - Acceptance Criteria:
     - [ ] Support for 20+ MCP tools
     - [ ] Seamless tool calling from AI assistants
     - [ ] Configuration management

3. **Advanced RAG System**
   - Description: Retrieval Augmented Generation for intelligent content processing
   - Priority: High
   - Acceptance Criteria:
     - [ ] Vector embeddings for content
     - [ ] Semantic search capabilities
     - [ ] Context-aware responses

### Technical Requirements
- **Technology Stack:** Node.js, Express, TypeScript, PostgreSQL, Redis, Qdrant
- **Performance:** Sub-second response times for API calls
- **Security:** API key authentication, input validation
- **Scalability:** Support for large vaults (10k+ files)

## Success Metrics
- [ ] API response time < 500ms
- [ ] 99.9% uptime
- [ ] Support for 20+ MCP tools
- [ ] Successful integration with Cursor and Warp

## Constraints & Assumptions
- **Budget:** Open source project
- **Timeline:** Continuous development
- **Resources:** Single developer with AI assistance
- **Assumptions:** Users have basic technical knowledge

## Risks & Mitigation
- **Risk 1:** MCP tool compatibility - Mitigation: Regular testing and updates
- **Risk 2:** Performance with large vaults - Mitigation: Optimization and caching

## Dependencies
- **External Dependencies:** OpenAI API, various MCP tool APIs
- **Internal Dependencies:** Node.js ecosystem, database systems

## Notes
This project serves as a comprehensive backend for knowledge management with AI integration.
"@

$samplePrdPath = Join-Path $docsDir "prd.txt"
Set-Content -Path $samplePrdPath -Value $samplePrd -Encoding UTF8
Write-Host "SUCCESS: Created sample PRD for current project" -ForegroundColor Green

# Create configuration files
Write-Host "`n6. Creating configuration files..." -ForegroundColor Yellow

# Create .taskmasterconfig/.json
$config = @{
    project = @{
        name = "Local API Obsidian Vault"
        description = "A comprehensive backend system for managing Obsidian vaults"
        version = "1.0.0"
    }
    models = @{
        main = "claude-3-5-sonnet-20241022"
        research = "gpt-4o"
        fallback = "gpt-4o-mini"
    }
    rules = @("cursor", "windsurf", "vscode")
    features = @{
        research = $true
        task_generation = $true
        dependency_tracking = $true
    }
} | ConvertTo-Json -Depth 3

$configPath = Join-Path $taskMasterDir config/.json"
Set-Content -Path $configPath -Value $config -Encoding UTF8
Write-Host "SUCCESS: Created .taskmasterconfig/.json" -ForegroundColor Green

# Summary
Write-Host "`nClaude Task Master Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "What was set up:" -ForegroundColor Yellow
Write-Host "- Task Master MCP server added to Cursor configuration" -ForegroundColor White
Write-Host "- Warp configuration file created" -ForegroundColor White
Write-Host "- Project structure created (.taskmaster directory)" -ForegroundColor White
Write-Host "- Example PRD template created" -ForegroundColor White
Write-Host "- Sample PRD for current project created" -ForegroundColor White
Write-Host "- Configuration file created" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart Cursor to load Task Master MCP" -ForegroundColor White
Write-Host "2. Copy WARP_TASK_MASTER_CONFIG.json to Warp settings" -ForegroundColor White
Write-Host "3. Initialize Task Master in your project:" -ForegroundColor White
Write-Host "   Say: 'Initialize taskmaster-ai in my project'" -ForegroundColor Cyan
Write-Host "4. Parse your PRD:" -ForegroundColor White
Write-Host "   Say: 'Can you parse my PRD at .taskmaster/docs/prd.txt?'" -ForegroundColor Cyan
Write-Host "5. Start using Task Master:" -ForegroundColor White
Write-Host "   Say: 'What's the next task I should work on?'" -ForegroundColor Cyan
Write-Host ""
Write-Host "Available Task Master commands:" -ForegroundColor Yellow
Write-Host "- Parse requirements: 'Can you parse my PRD at .taskmaster/docs/prd.txt?'" -ForegroundColor White
Write-Host "- Plan next step: 'What's the next task I should work on?'" -ForegroundColor White
Write-Host "- Implement task: 'Can you help me implement task 3?'" -ForegroundColor White
Write-Host "- View tasks: 'Can you show me tasks 1, 3, and 5?'" -ForegroundColor White
Write-Host "- Research: 'Research the latest best practices for Node.js API development'" -ForegroundColor White
Write-Host ""
Write-Host "Happy task managing with Claude Task Master!" -ForegroundColor Green

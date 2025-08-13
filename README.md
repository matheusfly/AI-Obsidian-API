# Development Environment Setup 🚀

Complete development environment with Python, Node.js, and organized project structure.

## 📁 Directory Structure

```
master_code/
├── data-projects/       # Data science projects
├── web-projects/        # Web development projects  
├── ai-projects/         # AI/ML projects
├── scripts/            # Utility scripts
├── templates/          # Project templates
├── README.md           # This file
└── codex.code-workspace # VS Code workspace
```

## 🚀 Quick Navigation Commands

After reloading your PowerShell profile (`. $PROFILE`), use these commands:

### Directory Navigation
- `codex` - Navigate to D:\codex
- `master` - Navigate to D:\codex\master_code
- `data` - Navigate to D:\codex\datamaster

### Environment Management
- `activate-data` - Activate data-science conda environment
- `activate-web` - Activate web-dev conda environment
- `activate-ai` - Activate ai-ml conda environment
- `activate-base` - Activate base conda environment
- `envs` - List all conda environments

### Git Aliases
- `gst` - git status
- `gco` - git checkout
- `gpl` - git pull
- `gps` - git push
- `gcm` - git commit -m

### File Operations
- `ll` - List all files (including hidden)
- `la` - List file names only

## 🐍 Conda Environments

| Environment | Purpose | Key Packages |
|-------------|---------|-------------|
| `data-science` | Data analysis & visualization | pandas, numpy, matplotlib, seaborn, jupyter |
| `web-dev` | Web development | fastapi, flask, django, requests |
| `ai-ml` | AI/ML development | torch, transformers, langchain, openai |

## 🛠️ Development Tools

- **Python**: 3.13.5
- **Node.js**: v22.17.1
- **npm**: 10.9.2
- **Conda**: 25.5.1
- **Git**: Configured with VS Code as editor
- **VS Code**: Workspace configuration included

## 📝 Quick Start Guide

### 1. Create a New Project

```powershell
# Navigate to master directory
master

# Create project structure (data/web/ai)
python scripts/setup_env.py create my-project data

# Or manually create directories
New-Item -ItemType Directory "data-projects/my-new-project"
```

### 2. Start Working with Data Science

```powershell
# Activate data science environment
activate-data

# Navigate to project
cd data-projects/my-project

# Start Jupyter
jupyter lab
```

### 3. Start Web Development

```powershell
# Activate web development environment
activate-web

# Copy FastAPI template
cp ../templates/fastapi_template.py ./app.py

# Run the API
uvicorn app:app --reload
```

### 4. Work with AI/ML

```powershell
# Activate AI/ML environment
activate-ai

# Use the data analysis template
cp ../templates/data_analysis_template.py ./analysis.py

# Run analysis
python analysis.py
```

## 🔧 Utility Scripts

- `scripts/setup_env.py check` - Check current environment and packages
- `scripts/setup_env.py create <name> [type]` - Create new project structure

## 📋 Templates Available

- `templates/fastapi_template.py` - FastAPI web application
- `templates/data_analysis_template.py` - Data analysis with pandas/matplotlib
- `templates/.env.template` - Environment variables template

## 🔐 Environment Variables

1. Copy the template: `cp templates/.env.template .env`
2. Fill in your API keys and secrets
3. Never commit `.env` files to version control!

## 🎯 VS Code Integration

- Open `codex.code-workspace` in VS Code for full project access
- Python environments auto-configured
- Recommended extensions included
- Git integration enabled

## 🔄 Maintenance

### Update Packages
```powershell
# Update conda
conda update conda

# Update environment packages
conda activate data-science
pip list --outdated
pip install --upgrade package-name
```

### Backup Configuration
```powershell
# Your PowerShell profile is at:
# $PROFILE
# Backup this file regularly!
```

---

**Ready to code!** 🎉 Your development environment is fully configured and ready for data science, web development, and AI/ML projects.

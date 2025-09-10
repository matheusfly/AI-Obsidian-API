#!/usr/bin/env python3
"""
Environment setup and testing script
"""
import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check current Python environment and installed packages"""
    print("=== Current Environment Info ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if we're in a conda environment
    if 'CONDA_DEFAULT_ENV' in os.environ:
        print(f"Conda environment: {os.environ['CONDA_DEFAULT_ENV']}")
    else:
        print("Not in a conda environment")
    
    print("\n=== Checking Common Packages ===")
    packages_to_check = [
        'numpy', 'pandas', 'matplotlib', 'seaborn', 'requests',
        'jupyter', 'sklearn', 'torch', 'transformers', 'fastapi'
    ]
    
    for package in packages_to_check:
        try:
            __import__(package)
            print(f"✓ {package} is available")
        except ImportError:
            print(f"✗ {package} is not available")

def create_project_structure(project_name, project_type="general"):
    """Create a standard project structure"""
    project_path = Path(f"../{project_type}-projects/{project_name}")
    
    # Create directories
    directories = [
        "src",
        "tests", 
        "data",
        "docs",
        "notebooks",
        "scripts",
        "config"
    ]
    
    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)
    
    # Create basic files
    (project_path / "README.md").write_text(f"""# {project_name}

## Description
Brief description of the project.

## Setup
1. Activate the appropriate conda environment
2. Install dependencies: `pip install -r requirements.txt`
3. Run the project

## Structure
- `src/` - Source code
- `tests/` - Unit tests
- `data/` - Data files
- `docs/` - Documentation
- `notebooks/` - Jupyter notebooks
- `scripts/` - Utility scripts
- `config/` - Configuration files
""")
    
    (project_path / "requirements.txt").write_text("""# Add your dependencies here
numpy
pandas
requests
""")
    
    (project_path / "src" / "__init__.py").write_text("")
    (project_path / "tests" / "__init__.py").write_text("")
    
    print(f"✓ Created project structure for '{project_name}' in {project_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "check":
            check_environment()
        elif command == "create" and len(sys.argv) > 2:
            project_name = sys.argv[2]
            project_type = sys.argv[3] if len(sys.argv) > 3 else "general"
            create_project_structure(project_name, project_type)
        else:
            print("Usage:")
            print("  python setup_env.py check")
            print("  python setup_env.py create <project_name> [project_type]")
    else:
        check_environment()

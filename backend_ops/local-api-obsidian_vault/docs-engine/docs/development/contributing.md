# Contributing Guide

Welcome to the Obsidian Vault AI System project! We appreciate your interest in contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Release Process](#release-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](../CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## Getting Started

### Prerequisites

- Docker Desktop
- Node.js 18+ and npm
- Python 3.9+ and pip
- Git
- PowerShell 7+ (Windows) or Bash (Linux/Mac)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/obsidian-vault-ai-system.git
   cd obsidian-vault-ai-system
   ```

3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/original-org/obsidian-vault-ai-system.git
   ```

## Development Setup

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
notepad .env  # Windows
# or
nano .env     # Linux/Mac
```

### 2. Start Development Services

```bash
# Start all services
docker-compose up -d

# Or start native services for faster development
./scripts/start-native-servers.ps1 -VaultPath "D:\Your\Vault"
```

### 3. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
cd services/obsidian-api
npm install

# Documentation dependencies
cd docs-engine
npm install
```

### 4. Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_vault_access.py

# Run with coverage
pytest --cov=services/vault-api tests/
```

## Contributing Process

### 1. Create a Branch

```bash
# Create and switch to new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number
```

### 2. Make Changes

- Write clean, readable code
- Follow the coding standards
- Add tests for new functionality
- Update documentation as needed

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new AI analysis endpoint

- Add /ai/analyze endpoint for content analysis
- Support multiple analysis types (sentiment, entities, topics)
- Add comprehensive test coverage
- Update API documentation"
```

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Coding Standards

### Python

**Style Guide**: Follow PEP 8 with some modifications:

```python
# Good example
def analyze_content(
    content: str,
    analysis_type: str = "sentiment",
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze content using specified analysis type.
    
    Args:
        content: Text content to analyze
        analysis_type: Type of analysis to perform
        options: Optional configuration parameters
        
    Returns:
        Analysis results dictionary
        
    Raises:
        ValueError: If analysis_type is not supported
        AnalysisError: If analysis fails
    """
    if not content:
        raise ValueError("Content cannot be empty")
    
    if analysis_type not in SUPPORTED_ANALYSIS_TYPES:
        raise ValueError(f"Unsupported analysis type: {analysis_type}")
    
    try:
        result = perform_analysis(content, analysis_type, options)
        return {
            "analysis_type": analysis_type,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise AnalysisError(f"Analysis failed: {str(e)}") from e
```

**Type Hints**: Always use type hints:

```python
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    """Result of content analysis."""
    analysis_type: str
    confidence: float
    entities: List[str]
    metadata: Dict[str, Any]

def process_files(
    file_paths: List[str],
    batch_size: int = 10
) -> List[AnalysisResult]:
    """Process multiple files in batches."""
    results = []
    
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i + batch_size]
        batch_results = process_batch(batch)
        results.extend(batch_results)
    
    return results
```

**Error Handling**: Use specific exceptions:

```python
class VaultError(Exception):
    """Base exception for vault operations."""
    pass

class FileNotFoundError(VaultError):
    """File not found in vault."""
    pass

class PermissionError(VaultError):
    """Insufficient permissions for operation."""
    pass

def read_file(file_path: str) -> str:
    """Read file from vault."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"No read permission: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise VaultError(f"Failed to read file: {str(e)}") from e
```

### JavaScript/TypeScript

**Style Guide**: Follow Airbnb JavaScript Style Guide:

```typescript
// Good example
interface VaultFile {
  path: string;
  content: string;
  metadata: FileMetadata;
  lastModified: Date;
}

class VaultManager {
  private readonly apiClient: ApiClient;
  private readonly cache: Map<string, VaultFile> = new Map();

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  async getFile(path: string): Promise<VaultFile> {
    if (this.cache.has(path)) {
      return this.cache.get(path)!;
    }

    try {
      const file = await this.apiClient.getFile(path);
      this.cache.set(path, file);
      return file;
    } catch (error) {
      throw new VaultError(`Failed to get file: ${path}`, error);
    }
  }

  async updateFile(path: string, content: string): Promise<void> {
    try {
      await this.apiClient.updateFile(path, content);
      this.cache.delete(path); // Invalidate cache
    } catch (error) {
      throw new VaultError(`Failed to update file: ${path}`, error);
    }
  }
}
```

### PowerShell

**Style Guide**: Follow PowerShell Best Practices:

```powershell
# Good example
function Start-VaultAPI {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$VaultPath,
        
        [Parameter(Mandatory = $false)]
        [int]$Port = 8085,
        
        [Parameter(Mandatory = $false)]
        [switch]$Debug
    )
    
    try {
        Write-Verbose "Starting Vault API on port $Port"
        
        # Validate vault path
        if (-not (Test-Path $VaultPath -PathType Container)) {
            throw "Vault path does not exist or is not a directory: $VaultPath"
        }
        
        # Start the service
        $process = Start-Process -FilePath "python" -ArgumentList @(
            "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", $Port
        ) -PassThru -NoNewWindow
        
        if ($Debug) {
            Write-Host "Vault API started with PID: $($process.Id)" -ForegroundColor Green
        }
        
        return $process
    }
    catch {
        Write-Error "Failed to start Vault API: $($_.Exception.Message)"
        throw
    }
}
```

## Testing

### Unit Tests

**Python Tests**:
```python
# tests/test_vault_operations.py
import pytest
from unittest.mock import Mock, patch
from services.vault_api.vault_operations import VaultManager

class TestVaultManager:
    def setup_method(self):
        self.vault_manager = VaultManager("/test/vault")
    
    def test_read_file_success(self):
        """Test successful file reading."""
        with patch("builtins.open", mock_open(read_data="test content")):
            content = self.vault_manager.read_file("test.md")
            assert content == "test content"
    
    def test_read_file_not_found(self):
        """Test file not found error."""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                self.vault_manager.read_file("nonexistent.md")
    
    def test_write_file_success(self):
        """Test successful file writing."""
        with patch("builtins.open", mock_open()) as mock_file:
            self.vault_manager.write_file("test.md", "new content")
            mock_file.assert_called_once_with("test.md", "w", encoding="utf-8")
    
    @pytest.mark.parametrize("content,expected", [
        ("", False),
        ("   ", False),
        ("valid content", True),
        ("content with\nnewlines", True)
    ])
    def test_validate_content(self, content, expected):
        """Test content validation."""
        result = self.vault_manager.validate_content(content)
        assert result == expected
```

**JavaScript Tests**:
```typescript
// tests/vault-manager.test.ts
import { VaultManager } from '../src/vault-manager';
import { ApiClient } from '../src/api-client';

describe('VaultManager', () => {
  let vaultManager: VaultManager;
  let mockApiClient: jest.Mocked<ApiClient>;

  beforeEach(() => {
    mockApiClient = {
      getFile: jest.fn(),
      updateFile: jest.fn(),
    } as jest.Mocked<ApiClient>;
    
    vaultManager = new VaultManager(mockApiClient);
  });

  describe('getFile', () => {
    it('should return file from cache if available', async () => {
      const cachedFile = {
        path: 'test.md',
        content: 'cached content',
        metadata: {},
        lastModified: new Date()
      };
      
      vaultManager['cache'].set('test.md', cachedFile);
      
      const result = await vaultManager.getFile('test.md');
      
      expect(result).toBe(cachedFile);
      expect(mockApiClient.getFile).not.toHaveBeenCalled();
    });

    it('should fetch file from API if not cached', async () => {
      const file = {
        path: 'test.md',
        content: 'file content',
        metadata: {},
        lastModified: new Date()
      };
      
      mockApiClient.getFile.mockResolvedValue(file);
      
      const result = await vaultManager.getFile('test.md');
      
      expect(result).toBe(file);
      expect(mockApiClient.getFile).toHaveBeenCalledWith('test.md');
    });

    it('should throw VaultError on API failure', async () => {
      const error = new Error('API Error');
      mockApiClient.getFile.mockRejectedValue(error);
      
      await expect(vaultManager.getFile('test.md')).rejects.toThrow('Failed to get file: test.md');
    });
  });
});
```

### Integration Tests

```python
# tests/integration/test_api_endpoints.py
import pytest
import requests
from fastapi.testclient import TestClient
from services.vault_api.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_files_endpoint(client, auth_headers):
    """Test list files endpoint."""
    response = client.get("/vault/files", headers=auth_headers)
    assert response.status_code == 200
    assert "files" in response.json()

def test_create_file_endpoint(client, auth_headers):
    """Test create file endpoint."""
    file_data = {
        "path": "test-file.md",
        "content": "# Test File\n\nThis is a test file."
    }
    
    response = client.post(
        "/vault/files",
        json=file_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json()["path"] == "test-file.md"

def test_ai_generate_endpoint(client, auth_headers):
    """Test AI generate endpoint."""
    request_data = {
        "prompt": "Write a short summary of machine learning",
        "max_tokens": 100
    }
    
    response = client.post(
        "/ai/generate",
        json=request_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "content" in response.json()
```

### End-to-End Tests

```python
# tests/e2e/test_complete_workflow.py
import pytest
import asyncio
from services.vault_api.vault_manager import VaultManager
from services.vault_api.ai_service import AIService
from services.vault_api.mcp_manager import MCPManager

@pytest.mark.asyncio
async def test_complete_ai_workflow():
    """Test complete AI workflow from file creation to analysis."""
    vault_manager = VaultManager("/test/vault")
    ai_service = AIService()
    mcp_manager = MCPManager()
    
    # Create test file
    test_content = "# Machine Learning Notes\n\nAI is fascinating!"
    await vault_manager.write_file("ml-notes.md", test_content)
    
    # Generate AI content
    ai_response = await ai_service.generate_content(
        prompt="Summarize this content",
        context_files=["ml-notes.md"]
    )
    
    assert ai_response["content"]
    assert len(ai_response["content"]) > 0
    
    # Analyze content
    analysis = await ai_service.analyze_content(
        content=test_content,
        analysis_type="sentiment"
    )
    
    assert analysis["analysis_type"] == "sentiment"
    assert "result" in analysis
    
    # Use MCP tools
    files = await mcp_manager.call_tool(
        "filesystem",
        "list_files",
        {"path": "/test/vault"}
    )
    
    assert "ml-notes.md" in files["result"]
```

## Documentation

### Code Documentation

**Python Docstrings**:
```python
def process_vault_files(
    vault_path: str,
    file_pattern: str = "*.md",
    recursive: bool = True,
    max_files: Optional[int] = None
) -> List[ProcessedFile]:
    """
    Process all files in the vault matching the given pattern.
    
    This function scans the vault directory for files matching the specified
    pattern and processes them according to the configured rules. It supports
    recursive scanning and can limit the number of files processed.
    
    Args:
        vault_path: Path to the Obsidian vault directory
        file_pattern: Glob pattern to match files (default: "*.md")
        recursive: Whether to scan subdirectories recursively
        max_files: Maximum number of files to process (None for unlimited)
        
    Returns:
        List of ProcessedFile objects containing file metadata and content
        
    Raises:
        VaultError: If vault_path is invalid or inaccessible
        ProcessingError: If file processing fails
        
    Example:
        >>> files = process_vault_files("/path/to/vault", "*.md", recursive=True)
        >>> print(f"Processed {len(files)} files")
        Processed 42 files
        
    Note:
        Large vaults may take significant time to process. Consider using
        max_files parameter for initial testing.
    """
    # Implementation here
    pass
```

**TypeScript JSDoc**:
```typescript
/**
 * Manages vault operations including file CRUD and metadata handling.
 * 
 * @example
 * ```typescript
 * const vaultManager = new VaultManager(apiClient);
 * const file = await vaultManager.getFile('notes/example.md');
 * console.log(file.content);
 * ```
 */
export class VaultManager {
  private readonly apiClient: ApiClient;
  private readonly cache: Map<string, VaultFile> = new Map();

  /**
   * Creates a new VaultManager instance.
   * 
   * @param apiClient - API client for vault operations
   */
  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  /**
   * Retrieves a file from the vault.
   * 
   * @param path - Path to the file in the vault
   * @returns Promise resolving to the file data
   * @throws {VaultError} When file cannot be retrieved
   * 
   * @example
   * ```typescript
   * const file = await vaultManager.getFile('notes/example.md');
   * console.log(file.content);
   * ```
   */
  async getFile(path: string): Promise<VaultFile> {
    // Implementation here
  }
}
```

### API Documentation

**OpenAPI Annotations**:
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(prefix="/vault", tags=["vault"])

class FileCreateRequest(BaseModel):
    """Request model for creating a new file."""
    path: str = Field(..., description="Path to the file in the vault")
    content: str = Field(..., description="Content of the file")
    metadata: Optional[dict] = Field(None, description="Optional file metadata")

class FileResponse(BaseModel):
    """Response model for file operations."""
    path: str = Field(..., description="Path to the file")
    content: str = Field(..., description="File content")
    metadata: dict = Field(..., description="File metadata")
    created_at: str = Field(..., description="Creation timestamp")
    modified_at: str = Field(..., description="Last modification timestamp")

@router.post(
    "/files",
    response_model=FileResponse,
    summary="Create a new file",
    description="Create a new file in the vault with the specified content and metadata.",
    responses={
        201: {"description": "File created successfully"},
        400: {"description": "Invalid request data"},
        409: {"description": "File already exists"},
        500: {"description": "Internal server error"}
    }
)
async def create_file(
    request: FileCreateRequest,
    current_user: User = Depends(get_current_user)
) -> FileResponse:
    """
    Create a new file in the vault.
    
    This endpoint creates a new file with the specified path and content.
    If the file already exists, a 409 Conflict error is returned.
    
    Args:
        request: File creation request containing path, content, and metadata
        current_user: Authenticated user making the request
        
    Returns:
        FileResponse containing the created file data
        
    Raises:
        HTTPException: 400 if request data is invalid
        HTTPException: 409 if file already exists
        HTTPException: 500 if file creation fails
    """
    # Implementation here
    pass
```

## Release Process

### 1. Version Bumping

```bash
# Update version in pyproject.toml
version = "1.2.0"

# Update version in package.json
"version": "1.2.0"

# Update version in Docker files
LABEL version="1.2.0"
```

### 2. Changelog

Update `CHANGELOG.md`:

```markdown
## [1.2.0] - 2024-01-15

### Added
- New AI analysis endpoint with support for sentiment analysis
- MCP tool integration for enhanced functionality
- Comprehensive test coverage for all endpoints

### Changed
- Improved error handling and user feedback
- Updated API documentation with examples
- Enhanced performance for large vault operations

### Fixed
- Fixed memory leak in file processing
- Resolved race condition in concurrent file operations
- Fixed authentication token expiration handling

### Security
- Added input validation for all API endpoints
- Implemented rate limiting for AI operations
- Enhanced security headers and CORS configuration
```

### 3. Release Notes

Create release notes for GitHub:

```markdown
# Release 1.2.0 - Enhanced AI Capabilities

## 🚀 New Features

- **AI Analysis Endpoint**: Analyze content with sentiment, entity extraction, and topic modeling
- **MCP Tool Integration**: Connect with external tools for enhanced functionality
- **Advanced Caching**: Improved performance with intelligent caching

## 🔧 Improvements

- Better error handling and user feedback
- Enhanced API documentation with interactive examples
- Improved performance for large vault operations

## 🐛 Bug Fixes

- Fixed memory leak in file processing
- Resolved race condition in concurrent operations
- Fixed authentication token expiration handling

## 📚 Documentation

- Updated API documentation with comprehensive examples
- Added contributing guide for developers
- Enhanced deployment documentation

## 🔒 Security

- Added input validation for all endpoints
- Implemented rate limiting for AI operations
- Enhanced security headers and CORS configuration
```

### 4. Tagging

```bash
# Create and push tag
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0

# Push to upstream
git push upstream v1.2.0
```

### 5. Docker Images

```bash
# Build and push Docker images
docker build -t obsidian-vault-ai/vault-api:v1.2.0 ./services/vault-api
docker build -t obsidian-vault-ai/obsidian-api:v1.2.0 ./services/obsidian-api

docker push obsidian-vault-ai/vault-api:v1.2.0
docker push obsidian-vault-ai/obsidian-api:v1.2.0

# Update latest tags
docker tag obsidian-vault-ai/vault-api:v1.2.0 obsidian-vault-ai/vault-api:latest
docker push obsidian-vault-ai/vault-api:latest
```

## Getting Help

- **Documentation**: [Full documentation](../intro)
- **GitHub Issues**: [Report bugs or request features](https://github.com/your-org/obsidian-vault-ai-system/issues)
- **Discord**: [Join our community](https://discord.gg/your-discord)
- **Stack Overflow**: [Ask questions](https://stackoverflow.com/questions/tagged/obsidian-vault-ai)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation
- Community acknowledgments

Thank you for contributing to the Obsidian Vault AI System! 🚀

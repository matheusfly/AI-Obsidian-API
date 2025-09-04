# Configuration Guide

Configure the Obsidian Vault AI System for your specific needs and environment.

## Environment Variables

### Core Configuration

```env
# Vault Configuration
OBSIDIAN_VAULT_PATH=D:\Your\Obsidian\Vault
OBSIDIAN_API_KEY=your-obsidian-api-key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8085
OBSIDIAN_API_PORT=27123

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=obsidian_vault

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
```

### AI Configuration

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000

# Supabase Configuration
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# ChromaDB Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
```

### MCP Tools Configuration

```env
# GitHub MCP
GITHUB_PERSONAL_ACCESS_TOKEN=your-github-token

# Context7 MCP
CONTEXT7_API_KEY=your-context7-key

# ByteRover MCP
BYTEROVER_API_KEY=your-byterover-key

# Playwright MCP
PLAYWRIGHT_BROWSER_PATH=/usr/bin/chromium
```

## Docker Configuration

### Docker Compose Overrides

Create `docker-compose.override.yml` for local development:

```yaml
version: '3.8'

services:
  vault-api:
    build:
      context: .
      dockerfile: services/vault-api/Dockerfile
    volumes:
      - ./services/vault-api:/app
      - ${OBSIDIAN_VAULT_PATH}:/vault
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
    ports:
      - "8085:8080"
      - "8086:8081"  # Debug port

  obsidian-api:
    volumes:
      - ${OBSIDIAN_VAULT_PATH}:/vault
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
```

### Resource Limits

```yaml
services:
  vault-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  postgres:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

## API Configuration

### Rate Limiting

```python
# config/rate_limits.py
RATE_LIMITS = {
    "auth": {"requests": 5, "window": 60},      # 5 requests per minute
    "vault": {"requests": 100, "window": 60},   # 100 requests per minute
    "ai": {"requests": 20, "window": 60},       # 20 requests per minute
    "mcp": {"requests": 50, "window": 60},      # 50 requests per minute
}
```

### CORS Configuration

```python
# config/cors.py
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://your-domain.com"
]

CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS = ["Authorization", "Content-Type", "X-API-Key"]
```

### Authentication

```python
# config/auth.py
JWT_SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SPECIAL = True
```

## MCP Tools Configuration

### MCP Servers Configuration

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/vault"],
      "env": {
        "NODE_ENV": "production"
      }
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-context7"],
      "env": {
        "CONTEXT7_API_KEY": "your-key"
      }
    }
  }
}
```

### Tool Permissions

```json
{
  "permissions": {
    "filesystem": {
      "read": true,
      "write": true,
      "delete": false,
      "paths": ["/vault/notes", "/vault/daily"]
    },
    "github": {
      "read": true,
      "write": false,
      "repos": ["owner/repo1", "owner/repo2"]
    }
  }
}
```

## Monitoring Configuration

### Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "ai-observability-rules.yml"

scrape_configs:
  - job_name: 'vault-api'
    static_configs:
      - targets: ['vault-api:8080']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'obsidian-api'
    static_configs:
      - targets: ['obsidian-api:27123']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Configuration

```yaml
# monitoring/grafana/grafana.ini
[server]
http_port = 3004
root_url = http://localhost:3004/

[security]
admin_user = admin
admin_password = your-password

[auth.anonymous]
enabled = true
org_name = Obsidian Vault AI
```

## Logging Configuration

### Log Levels

```python
# config/logging.py
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "level": "DEBUG",
            "formatter": "detailed"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}
```

### Structured Logging

```python
# config/structured_logging.py
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## Security Configuration

### SSL/TLS Configuration

```python
# config/ssl.py
SSL_CERT_PATH = "/path/to/cert.pem"
SSL_KEY_PATH = "/path/to/key.pem"
SSL_CA_PATH = "/path/to/ca.pem"

# Cipher suites
SSL_CIPHERS = [
    "ECDHE-RSA-AES256-GCM-SHA384",
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-RSA-AES256-SHA384",
    "ECDHE-RSA-AES128-SHA256"
]
```

### Security Headers

```python
# config/security.py
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'"
}
```

## Performance Configuration

### Caching Configuration

```python
# config/cache.py
CACHE_CONFIG = {
    "default": {
        "backend": "redis",
        "location": "redis://localhost:6379/0",
        "timeout": 300
    },
    "vault": {
        "backend": "redis",
        "location": "redis://localhost:6379/1",
        "timeout": 3600
    },
    "ai": {
        "backend": "redis",
        "location": "redis://localhost:6379/2",
        "timeout": 1800
    }
}
```

### Database Configuration

```python
# config/database.py
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True
}
```

## Environment-Specific Configuration

### Development

```env
# .env.development
DEBUG=true
LOG_LEVEL=debug
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/obsidian_vault_dev
```

### Staging

```env
# .env.staging
DEBUG=false
LOG_LEVEL=info
CORS_ORIGINS=https://staging.your-domain.com
DATABASE_URL=postgresql://user:pass@staging-db:5432/obsidian_vault_staging
```

### Production

```env
# .env.production
DEBUG=false
LOG_LEVEL=warning
CORS_ORIGINS=https://your-domain.com
DATABASE_URL=postgresql://user:pass@prod-db:5432/obsidian_vault_prod
```

## Configuration Validation

### Environment Validation

```python
# config/validation.py
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    obsidian_vault_path: str
    openai_api_key: str
    postgres_password: str
    
    @validator('obsidian_vault_path')
    def validate_vault_path(cls, v):
        if not os.path.exists(v):
            raise ValueError('Vault path does not exist')
        return v
    
    @validator('openai_api_key')
    def validate_openai_key(cls, v):
        if not v.startswith('sk-'):
            raise ValueError('Invalid OpenAI API key format')
        return v

settings = Settings()
```

## Configuration Management

### Configuration Loading

```python
# config/loader.py
import os
from pathlib import Path

def load_config():
    """Load configuration from environment and files."""
    config = {}
    
    # Load from .env file
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    
    # Override with environment variables
    config.update(os.environ)
    
    return config
```

### Configuration Hot Reload

```python
# config/hot_reload.py
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.env'):
            asyncio.create_task(reload_config())

def start_config_watcher():
    """Start watching for configuration changes."""
    event_handler = ConfigReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=False)
    observer.start()
    return observer
```

## Best Practices

1. **Never commit secrets** to version control
2. **Use environment-specific** configuration files
3. **Validate configuration** at startup
4. **Use secure defaults** for production
5. **Document all configuration** options
6. **Test configuration** changes in staging
7. **Monitor configuration** changes
8. **Use configuration management** tools for production

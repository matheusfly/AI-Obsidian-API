# Warp Notebook: Obsidian Vault AI System — Launch & Customization (Windows + PowerShell)

This notebook collects the most useful commands for launching, customizing, and troubleshooting the full stack locally. All commands are designed for PowerShell (pwsh) on Windows.

Important ports (current mappings):
- Vault API: http://localhost:8085
- Obsidian API: http://localhost:27123
- n8n: http://localhost:5678
- Grafana: http://localhost:3004
- Nginx: http://localhost:8088
- Chromadb: http://localhost:8000
- Ollama: http://localhost:11434
- Flyde Integration: http://localhost:3012

Prerequisites
- Docker Desktop for Windows (WSL2 backend recommended)
- Git
- Obsidian vault mounted at D:\Nomade Milionario
- .env configured (see README.md) — do not commit secrets

Quick Launch
1) Light Speed (fastest core startup)
- Builds only core local images and brings up the minimal stack.
```pwsh
# From repo root
./scripts/quick-lightspeed.ps1
# or with Docker already running
./scripts/quick-lightspeed.ps1 -SkipDocker
```

2) Full Stack (standard path)
```pwsh
./scripts/quick-start.ps1
# View logs interactively
./scripts/quick-start.ps1 -ShowLogs
# View logs for a specific service
./scripts/quick-start.ps1 -ShowLogs -Service vault-api
```

Docker Compose: Build and Start Variants
- Enable faster builds
```pwsh
$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_DOCKER_CLI_BUILD = "1"
```

- Build everything
```pwsh
docker-compose build
```

- Build only local images that you edit frequently
```pwsh
docker-compose build --parallel vault-api obsidian-api
```

- Start full stack (detached)
```pwsh
docker-compose up -d
```

- Start only core stack (minimal)
```pwsh
docker-compose up -d obsidian-api vault-api postgres redis n8n chromadb ollama
```

- Stop and remove containers (keep volumes)
```pwsh
docker-compose down
```

- Stop and remove containers plus named volumes (DANGEROUS — data loss)
```pwsh
docker-compose down -v
```

- Remove orphan containers left by previous compose files
```pwsh
docker-compose up -d --remove-orphans
```

Service Health Checks
- Vault API
```pwsh
Invoke-WebRequest -Uri http://localhost:8085/health -UseBasicParsing
```

- Obsidian API
```pwsh
Invoke-WebRequest -Uri http://localhost:27123/health -UseBasicParsing
```

- n8n
```pwsh
# Some versions expose /health; home page 200 also indicates up
Invoke-WebRequest -Uri http://localhost:5678/ -UseBasicParsing
```

- Grafana
```pwsh
Invoke-WebRequest -Uri http://localhost:3004/api/health -UseBasicParsing
```

- Nginx
```pwsh
Invoke-WebRequest -Uri http://localhost:8088/ -UseBasicParsing
```

One-shot “Fast Check”
```pwsh
$urls = @(
  'http://localhost:8085/health',
  'http://localhost:27123/health',
  'http://localhost:5678/',
  'http://localhost:3004/api/health',
  'http://localhost:8088/'
)
foreach ($u in $urls) {
  try { "$u -> " + (Invoke-WebRequest -Uri $u -TimeoutSec 5 -UseBasicParsing).StatusCode }
  catch { "$u -> ERR" }
}
```

Logs
- All service logs (follow)
```pwsh
docker-compose logs -f
```

- Specific service logs (follow)
```pwsh
docker-compose logs -f vault-api
```

- Last 100 lines of a container by name
```pwsh
docker logs --tail 100 vault-api
```

Port Conflicts and Diagnostics
- Find what’s using a given port
```pwsh
Get-NetTCPConnection -LocalPort 8085 -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess
Get-Process -Id <OwningProcessId>
```

- If you need to free the port (may require admin)
```pwsh
Stop-Process -Id <PID> -Force
```

- Change host port mapping (example: Vault API from 8085 to 8080)
  - Edit docker-compose.yml:
    - Under services.vault-api.ports, change "8085:8080" to "8080:8080"
  - Then:
```pwsh
docker-compose up -d vault-api
```

n8n Troubleshooting
- Encryption key mismatch or reset n8n state (DANGEROUS: erases n8n data)
```pwsh
# Stop and remove n8n container
docker stop n8n; docker rm n8n

# Remove n8n data volume
docker volume rm local-api-obsidian_vault_n8n_data

# Start again (will regenerate data with current env)
docker-compose up -d n8n
```

Postgres Credential Mismatches
- Reset Postgres data if credentials in .env changed (DANGEROUS: erases DB data)
```pwsh
# Stop and remove postgres container
docker stop postgres; docker rm postgres

# Remove DB volume
docker volume rm local-api-obsidian_vault_postgres_data

# Start again (init scripts in ./postgres/init will re-run)
docker-compose up -d postgres n8n
```

Nginx Proxy Tests
- Verify Nginx is up
```pwsh
Invoke-WebRequest -Uri http://localhost:8088/ -UseBasicParsing
```

- Example proxied call to Vault API via Nginx
```pwsh
# If Nginx routes /api/ to vault-api
Invoke-WebRequest -Uri http://localhost:8088/api/health -UseBasicParsing
```

UV-powered Vault API (inside container)
- Rebuild vault-api with uv-based Dockerfile
```pwsh
docker-compose build vault-api
```

- Restart vault-api
```pwsh
docker-compose up -d vault-api
```

- Exec into the container (for quick inspection)
```pwsh
docker exec -it vault-api bash
# Inside:
uv pip list
python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

Selective Service Operations
- Start only Vault API and Obsidian API
```pwsh
docker-compose up -d vault-api obsidian-api
```

- Start monitoring layer
```pwsh
docker-compose up -d prometheus grafana nginx
```

- Start RAG extras
```pwsh
docker-compose up -d chromadb qdrant embedding-service advanced-indexer
```

Cleaning and Pruning
- Remove unused containers, networks (keep images and volumes)
```pwsh
docker system prune -f
```

- Remove dangling images (free disk space)
```pwsh
docker image prune -f
```

- Remove all stopped containers
```pwsh
docker container prune -f
```

- Remove all unused volumes (DANGEROUS)
```pwsh
docker volume prune -f
```

Service Status Snapshot
```pwsh
docker-compose ps
```

Quick Functions (paste into your pwsh session)
```pwsh
function Test-Stack {
  param([int]$Timeout=5)
  $targets = @(
    'http://localhost:8085/health',
    'http://localhost:27123/health',
    'http://localhost:5678/',
    'http://localhost:3004/api/health',
    'http://localhost:8088/'
  )
  foreach ($t in $targets) {
    try { "$t -> " + (Invoke-WebRequest -Uri $t -TimeoutSec $Timeout -UseBasicParsing).StatusCode }
    catch { "$t -> ERR" }
  }
}

function Start-CoreFast { ./scripts/quick-lightspeed.ps1 }
function Start-Full { ./scripts/quick-start.ps1 }
function Show-Logs { param([string]$Service) if ($Service) { docker-compose logs -f $Service } else { docker-compose logs -f } }
```

Environment Customization (edit .env)
- Examples (placeholders — do not commit secrets):
```
N8N_USER=admin
N8N_PASSWORD=change_me
N8N_ENCRYPTION_KEY=32_character_key_here
OBSIDIAN_API_KEY=your_obsidian_api_key
OPENAI_API_KEY=your_openai_key
REDIS_PASSWORD=choose_a_strong_password
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```
- After editing .env, restart impacted services, e.g.:
```pwsh
docker-compose up -d n8n vault-api
```

Performance Tips
- Use BuildKit and parallel builds for local images you edit often
```pwsh
$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_DOCKER_CLI_BUILD = "1"
docker-compose build --parallel vault-api obsidian-api
```

- Keep large layers cached (avoid unnecessary COPY before dependency install in Dockerfile)
- For Python, uv (already integrated for vault-api) offers faster dependency resolution and installation

WSL/Unix-style alternatives (optional)
- curl tests (if curl is available in PATH)
```pwsh
curl http://localhost:8085/health
curl http://localhost:27123/health
```

Where to change ports
- docker-compose.yml services:
  - vault-api.ports -> host:container (e.g., 8085:8080)
  - grafana.ports -> 3004:3000
  - nginx.ports -> 8088:80 and 8443:443
  - flyde-integration.ports -> 3012:3002

Have a common set of quick references? Add your own shortcuts here.


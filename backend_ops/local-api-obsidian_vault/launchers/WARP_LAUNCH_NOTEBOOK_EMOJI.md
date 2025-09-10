# 🚀 Obsidian Vault AI — Warp Notebook (Emoji Edition)

A curated, emoji-rich command notebook for launching, customizing, and troubleshooting your local stack with PowerShell on Windows.

Current service endpoints (host ports):
- 🔐 Vault API: http://localhost:8085
- 📝 Obsidian API: http://localhost:27123
- 🤖 n8n: http://localhost:5678
- 📊 Grafana: http://localhost:3004
- 🌐 Nginx: http://localhost:8088
- 🧠 ChromaDB: http://localhost:8000
- 🐙 Ollama: http://localhost:11434
- 🧩 Flyde Integration: http://localhost:3012

—

## 🧭 Quick Index
- ⚡ Light Speed Launch
- 🚢 Full Stack Launch
- 🧪 Health Checks
- 📜 Logs & Status
- 🧰 Docker Compose: Build/Up/Down
- 🧷 Ports & Conflicts
- 🔑 n8n / 🐘 Postgres Fixes
- 🧹 Cleanup & Prune
- 🐍 UV-powered Vault API
- 🎯 Selective Service Operations
- 🧩 Monitoring & RAG Extras
- ⚙️ Environment & Secrets
- 🧩 Handy PowerShell Functions

—

## ⚡ Light Speed Launch (fastest core path)
Build only core images locally and start the minimal stack.

```pwsh
# From repo root
./scripts/quick-lightspeed.ps1
# or, if Docker is already running
./scripts/quick-lightspeed.ps1 -SkipDocker
```

—

## 🚢 Full Stack Launch
Standard, all-services path with interactive logs.

```pwsh
./scripts/quick-start.ps1
# View logs interactively
./scripts/quick-start.ps1 -ShowLogs
# Logs for a specific service
./scripts/quick-start.ps1 -ShowLogs -Service vault-api
```

—

## 🧪 Health Checks (one-liners)
```pwsh
Invoke-WebRequest http://localhost:8085/health -UseBasicParsing       # Vault API
Invoke-WebRequest http://localhost:27123/health -UseBasicParsing       # Obsidian API
Invoke-WebRequest http://localhost:5678/ -UseBasicParsing              # n8n (homepage 200 OK)
Invoke-WebRequest http://localhost:3004/api/health -UseBasicParsing    # Grafana
Invoke-WebRequest http://localhost:8088/ -UseBasicParsing              # Nginx welcome
```

Quick sweep:
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

—

## 📜 Logs & Status
```pwsh
docker-compose logs -f                     # All logs (follow)
docker-compose logs -f vault-api           # Specific service

docker logs --tail 100 vault-api           # Last 100 lines (container)

docker-compose ps                          # Compose status snapshot
```

—

## 🧰 Docker Compose: Build / Up / Down
Speed up builds:
```pwsh
$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_DOCKER_CLI_BUILD = "1"
```

Build everything:
```pwsh
docker-compose build
```

Build only local images you edit often:
```pwsh
docker-compose build --parallel vault-api obsidian-api
```

Start full stack (detached):
```pwsh
docker-compose up -d
```

Start only core stack:
```pwsh
docker-compose up -d obsidian-api vault-api postgres redis n8n chromadb ollama
```

Stop/remove containers (keep volumes):
```pwsh
docker-compose down
```

Remove orphans left by old compose files:
```pwsh
docker-compose up -d --remove-orphans
```

—

## 🧷 Ports & Conflicts
Find the process that owns a port and inspect it:
```pwsh
Get-NetTCPConnection -LocalPort 8085 -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess
Get-Process -Id <OwningProcessId>
```

Free the port (admin may be required):
```pwsh
Stop-Process -Id <PID> -Force
```

Change a service’s host port (example: Vault API 8085 -> 8080):
1) Edit docker-compose.yml, change `services.vault-api.ports` from `8085:8080` to `8080:8080`
2) Restart just that service:
```pwsh
docker-compose up -d vault-api
```

—

## 🔑 n8n Fixes (encryption key / config)
Reset n8n state to match your .env (ERASES n8n DATA):
```pwsh
docker stop n8n; docker rm n8n
# Remove n8n data volume (danger: data loss)
docker volume rm local-api-obsidian_vault_n8n_data
# Start fresh
docker-compose up -d n8n
```

—

## 🐘 Postgres Fix (credential mismatch)
Reset DB if credentials in .env changed (ERASES DB DATA):
```pwsh
docker stop postgres; docker rm postgres
# Remove DB volume (danger: data loss)
docker volume rm local-api-obsidian_vault_postgres_data
# Recreate DB/initialization
docker-compose up -d postgres n8n
```

—

## 🧹 Disk Cleanup & Prune
```pwsh
docker system prune -f        # Remove unused containers/networks

docker image prune -f         # Remove dangling images

docker container prune -f     # Remove all stopped containers

docker volume prune -f        # Remove all unused volumes (danger)
```

—

## 🐍 UV-powered Vault API (inside container)
Rebuild vault-api (uses uv in Dockerfile):
```pwsh
docker-compose build vault-api
```
Restart vault-api:
```pwsh
docker-compose up -d vault-api
```
Exec into the container:
```pwsh
docker exec -it vault-api bash
# Inside the container:
uv pip list
python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

—

## 🎯 Selective Service Operations
```pwsh
# APIs only
docker-compose up -d vault-api obsidian-api

# Monitoring slice
docker-compose up -d prometheus grafana nginx

# RAG extras
docker-compose up -d chromadb qdrant embedding-service advanced-indexer
```

—

## 🧩 Monitoring & RAG Extras
- 📊 Grafana dashboards: http://localhost:3004
- 📈 Prometheus: http://localhost:9090
- 🧠 ChromaDB: http://localhost:8000
- 🧲 Qdrant: http://localhost:6333 (if mapped)

—

## ⚙️ Environment & Secrets (.env)
Examples (DO NOT COMMIT SECRETS):
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
After edits, restart impacted services:
```pwsh
docker-compose up -d n8n vault-api
```

—

## 🧩 Handy PowerShell Functions
Paste these into your pwsh session for quick reuse.
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

—

## ✅ Tips
- 🧱 BuildKit + parallel builds = faster local iterations on vault-api and obsidian-api
- 🐍 uv already integrated in vault-api Dockerfile for faster dependency work
- 🌊 Keep orphan containers tidy with `--remove-orphans` when compose file changes
- ⚠️ Use `down -v`, volume prune, and DB/n8n resets with care — they delete data


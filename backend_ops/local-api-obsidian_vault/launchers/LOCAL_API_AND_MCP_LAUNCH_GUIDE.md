# Local API + Docs + MCP: Complete Launch Guide (Windows / PowerShell)

This guide shows how to launch your local API servers, access the auto-generated docs, verify key endpoints, and activate MCP servers in Warp.

What you’ll run:
- Obsidian API (Node/Express) on http://localhost:27123
  - Endpoints: /health, /files, /files/{path}, /vault/search
- Vault API (FastAPI/Uvicorn) on http://localhost:8080 (native) or http://localhost:8085 (if via Docker Compose)
  - Docs: /docs (Swagger UI), /openapi.json, Redoc at /redoc
  - Endpoints: /health, /api/v1/notes, /api/v1/search, /api/v1/mcp/tools, /api/v1/mcp/tools/call, etc.
- Optional: full stack via Docker Compose (n8n, Postgres, Redis, Chromadb, Ollama, Grafana, Prometheus, Nginx)
- MCP servers (filesystem, obsidian-vault, etc.) for Warp


## Prerequisites
- Windows with PowerShell 7+
- Node.js 18+ and npm
- Python 3.11+ (for FastAPI service)
- Docker Desktop (optional, required for the full docker-compose stack)
- Access to your Obsidian vault folder (default path used in repo: `D:\Nomade Milionario`)

Environment variables (use placeholders — do not paste secrets directly into files):
- VAULT_PATH (e.g., `D:\Nomade Milionario`)
- Optional API keys for MCP: `OPENAI_API_KEY`, `BRAVE_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`, `CONTEXT7_API_KEY`, `BYTEROVER_API_KEY`, `SERP_API_KEY`

Example (PowerShell, non-persistent):
- `$env:VAULT_PATH = 'D:\Nomade Milionario'`
- `$env:OPENAI_API_KEY = '{{OPENAI_API_KEY}}'`


## Option A — Quick Native Launch (no Docker)
This spins up Node (Obsidian API) and FastAPI (Vault API) locally.

1) Start the Obsidian API (Node/Express)
- Open a PowerShell in repo root: `D:\codex\master_code\backend_ops\local-api-obsidian_vault`
- Commands:
  - `cd .\obsidian-api`
  - `npm install`
  - `$env:VAULT_PATH = 'D:\Nomade Milionario'` (adjust as needed)
  - `npm start`

This starts http://localhost:27123
- Health: http://localhost:27123/health

2) Start the Vault API (FastAPI/Uvicorn)
- In a new PowerShell in repo root:
  - `pwsh -File .\run_vault_api.ps1 -VaultPath 'D:\Nomade Milionario' -ObsidianApiUrl 'http://localhost:27123' -Port 8080 -Host '0.0.0.0'`

This starts http://localhost:8080
- Docs: http://localhost:8080/docs
- OpenAPI: http://localhost:8080/openapi.json
- Health: http://localhost:8080/health

3) Verify endpoints (PowerShell)
- `Invoke-WebRequest http://localhost:27123/health -UseBasicParsing`
- `Invoke-WebRequest http://localhost:8080/health -UseBasicParsing`
- `Invoke-WebRequest http://localhost:8080/docs -UseBasicParsing`


## Option B — Full Stack via Docker Compose
This launches the broader stack defined in `docker-compose.yml` (n8n, Postgres, Redis, Chromadb, Ollama, Grafana, Prometheus, Nginx, etc.).

- From repo root:
  - `pwsh -File .\scripts\launch.ps1 -Action start`

Ports to know (from docker-compose.yml):
- Obsidian API: http://localhost:27123
- Vault API: http://localhost:8085  (container’s port 8080 mapped to host 8085)
- n8n: http://localhost:5678
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3004
- Qdrant: http://localhost:6333
- Nginx: http://localhost:8088

Note: The `scripts\launch.ps1` output banner references 8080 for Vault API; when running via Docker Compose, use 8085 to reach the containerized FastAPI.


## Core API Endpoints (Quick Reference)
Vault API (FastAPI)
- GET /health — service health + connected services information
- GET /docs — interactive API docs (Swagger)
- GET /openapi.json — OpenAPI schema
- GET /api/v1/notes — list markdown notes from the Obsidian API
- POST /api/v1/notes — create a new note via the Obsidian API
- GET /api/v1/notes/{path} — read note content
- POST /api/v1/search — search vault notes
- GET /api/v1/mcp/tools — list available MCP tools (local HTTP implementation)
- POST /api/v1/mcp/tools/call — call a tool (e.g., `read_file`, `list_files`, `search_content`)

Obsidian API (Node/Express)
- GET /health — health check
- GET /files — list files in `VAULT_PATH` (filter via `?path=subfolder`)
- GET /files/* — read file content & metadata
- POST /files — create/update file `{ path, content }`
- POST /vault/search — simple content search across `.md` files


## MCP Activation in Warp (Recommended Minimal Setup)
You have scripts to generate config, but the simplest is to add a minimal Warp MCP configuration and use environment variables for secrets.

1) Open Warp → Settings (Ctrl/Cmd + ,) → AI → Manage MCP servers → Add server.

2) Add a minimal set:
- Filesystem (browse this project) — example:
  - Command: `npx`
  - Args: `-y`, `@modelcontextprotocol/server-filesystem`, `D:\codex\master_code\backend_ops\local-api-obsidian_vault`
  - Env: `{ "NODE_ENV": "development" }`
  - Start on launch: true

- Obsidian vault (custom MCP) — example:
  - Command: `node`
  - Args: `D:\codex\master_code\backend_ops\local-api-obsidian_vault\obsidian-mcp-server\index.js`
  - Env (replace with your own):
    - `VAULT_PATH = D:\Nomade Milionario`
    - `OPENAI_API_KEY = {{OPENAI_API_KEY}}`
  - Start on launch: true

Optional servers (add if you use them):
- Sequential Thinking: `uvx mcp-server-sequential-thinking`
- Web Search: `uvx mcp-server-web-search` (requires `SERP_API_KEY = {{SERP_API_KEY}}`)
- Brave Search: `uvx mcp-server-brave-search` (requires `BRAVE_API_KEY = {{BRAVE_API_KEY}}`)
- GitHub: `npx -y @modelcontextprotocol/server-github` (requires `GITHUB_PERSONAL_ACCESS_TOKEN = {{GITHUB_TOKEN}}`)

3) Start each MCP server in Warp → ensure it shows “running” and lists tools.

Notes:
- You can also run `.\u200bsetup-mcp-tools.ps1` to generate `warp-mcp-config.json`/`cursor-mcp-config.json`. If you do, replace any placeholder secrets with your environment variables and avoid committing secrets.
- Test prerequisites quickly: `pwsh -File .\scripts\test_mcp_servers.ps1`


## Testing MCP (examples)
Once the `obsidian-vault` MCP server is running in Warp, try tool calls like:
- Read a note: `read_note` with `{ "note_path": "notes/example.md" }`
- Search notes: `search_notes` with `{ "query": "machine learning", "include_content": true }`

From the HTTP side (Vault API’s lightweight MCP endpoints):
- List tools: `GET http://localhost:8080/api/v1/mcp/tools`
- Call a tool: `POST http://localhost:8080/api/v1/mcp/tools/call` with body:
  ```json
  {
    "tool": "read_file",
    "arguments": { "path": "README.md" }
  }
  ```


## Troubleshooting
- Port in use
  - Change ports or stop the conflicting process. For Docker Compose Vault API use 8085.
- VAULT_PATH incorrect or inaccessible
  - Verify path exists and that Node/Python processes have read/write permissions.
- Docker Desktop not running
  - Start Docker Desktop before running `scripts\launch.ps1`.
- Secrets in config
  - Do not hardcode secrets in tracked files. Use environment variables and placeholders.
- Health checks
  - Obsidian API: `Invoke-WebRequest http://localhost:27123/health -UseBasicParsing`
  - Vault API: `Invoke-WebRequest http://localhost:8080/health -UseBasicParsing` (or `:8085` if Docker)


## Stop / Restart
- Native:
  - Stop: close the Node/Python processes (Task Manager or Ctrl+C in their shells).
  - Restart: rerun the steps above.
- Docker Compose:
  - Stop: `docker-compose down`
  - Restart: `pwsh -File .\scripts\launch.ps1 -Action restart`


## One‑liners (PowerShell)
- Native quick start (separate terminals recommended):
  - Obsidian API: `cd .\obsidian-api; $env:VAULT_PATH='D:\Nomade Milionario'; npm install; npm start`
  - Vault API: `pwsh -File .\run_vault_api.ps1 -VaultPath 'D:\Nomade Milionario' -ObsidianApiUrl 'http://localhost:27123' -Port 8080`
- Full stack: `pwsh -File .\scripts\launch.ps1 -Action start`

You’re set. If you want, I can try to launch the services for you now (native or docker).


---

## 🚀 One‑Command Native Start (Convenience)

Use the helper script to start both servers (Obsidian API + Vault API) as background jobs and wait for health.

```powershell
# From repo root: D:\codex\master_code\backend_ops\local-api-obsidian_vault
pwsh -File .\scripts\start-native-servers.ps1 -VaultPath 'D:\Nomade Milionario'
```

What it does:
- 🧩 Installs obsidian-api deps if missing (npm install)
- ⚙️ Starts obsidian-api on http://localhost:27123
- 🐍 Calls run_vault_api.ps1 to start Vault API on http://localhost:8080
- ⏳ Waits for /health, prints quick URLs, and shows handy Job commands

Handy commands:
```powershell
Get-Job
Receive-Job -Name obsidian-api -Keep | Select-Object -Last 100
Receive-Job -Name vault-api    -Keep | Select-Object -Last 100
Stop-Job obsidian-api, vault-api
```

If you instead use Docker Compose, remember: Vault API docs are on http://localhost:8085/docs (not 8080).


---

## 🧪 MCP Test Suite (Logs for Debugging)

Run the comprehensive test harness to exercise HTTP MCP endpoints and custom MCP servers, with outputs saved under logs/mcp-tests/{timestamp}.

- Native (8080):
```powershell
pwsh -File .\scripts\run-mcp-test-suite.ps1 -VaultApiBase "http://localhost:8080"
```

- Docker (8085):
```powershell
pwsh -File .\scripts\run-mcp-test-suite.ps1 -VaultApiBase "http://localhost:8085"
```

Optional flags (only if env keys are set):
- 🔐 -IncludeGitHub (GITHUB_PERSONAL_ACCESS_TOKEN)
- 🦁 -IncludeBrave (BRAVE_API_KEY)
- 📚 -IncludeContext7 (CONTEXT7_API_KEY)
- 🧠 -IncludeByterover (BYTEROVER_API_KEY)
- 🎭 -IncludePlaywright

Artifacts include:
- prerequisites.json, SUMMARY.json
- vault-api.health.json, vault-api.tools.json
- vault-api.call.read_file.json, vault-api.call.list_files.json, vault-api.call.search_content.json
- custom-graphiti.log, custom-aci.log, custom-obsidian-vault.log, plus any *.error.log

Troubleshooting quickies:
- ❌ ERR_EMPTY_RESPONSE on 8080? Ensure you’re running native (or switch to 8085 for Docker).
- 🔒 Port in use? `Get-NetTCPConnection -LocalPort 8080` then stop the owning process or change the port.
- 📁 VAULT_PATH wrong? Update the script arg or set `$env:VAULT_PATH`.

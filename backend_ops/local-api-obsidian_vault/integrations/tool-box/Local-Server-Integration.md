# Local Server Integration (API backend setup)

This guide details step-by-step integration into a local API backend.

## Assumptions
- Windows host, PowerShell available.
- Local services (example from your stack):
  - Vault API: http://localhost:8085
  - Obsidian API: http://localhost:27123
  - n8n: http://localhost:5678
  - Grafana: http://localhost:3004
  - Nginx: http://localhost:8088
  - ChromaDB: http://localhost:8000
  - Flyde Integration: http://localhost:3012

## 1) Prepare flows and nodes
- Create `flows/` in your app.
- Author flows via VS Code extension ("Flyde: New visual flow").
- Add code nodes (`.flyde.ts`) for external calls (LLM/HTTP/DB), no secrets inside nodes.

## 2) Wire a REST endpoint to a flow
Example (pseudo TypeScript):
```ts
import { runFlow, loadFlow } from "@flyde/loader";
import path from "path";

export async function getForecast(req, res) {
  const city = String(req.query.city ?? "");
  if (!city) return res.status(400).json({ ok: false, error: "city required" });

  const correlationId = req.headers["x-correlation-id"] ?? crypto.randomUUID();
  try {
    const flowPath = path.join(__dirname, "../flows/city-forecast.flyde");
    const result = await runFlow(flowPath, { city, correlationId });
    res.json({ ok: true, correlationId, ...result });
  } catch (e) {
    res.status(500).json({ ok: false, correlationId, error: String(e) });
  }
}
```

## 3) Streaming (SSE) endpoint for long flows
```ts
export async function streamLLM(req, res) {
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
  });

  const execute = await loadFlow(path.join(__dirname, "../flows/ai-long-run.flyde"));
  const { result } = execute({ prompt: String(req.query.prompt ?? "") }, {
    onOutputs: (key, value) => {
      res.write(`event: ${key}\n`);
      res.write(`data: ${JSON.stringify(value)}\n\n`);
    },
  });

  result.finally(() => res.end());
}
```

## 4) Reverse proxy (Nginx) for SSE and APIs
- Add upstream for your API backend service.
- Use SSE config from [[Deployment-Playbooks]].
- Example route: `/api/forecast` -> backend service; `/sse/ai` -> SSE endpoint.

## 5) Health checks
- Add `/health` endpoint on APIs, returning 200 OK.
- Optional: `runFlow("./flows/health.flyde")` to verify dependencies.

## 6) Windows ops
- Check port conflicts:
```pwsh
Get-NetTCPConnection -LocalPort 8085 -State Listen | Select LocalAddress,LocalPort,OwningProcess
Get-Process -Id <PID>
```
- Free a port (admin): `Stop-Process -Id <PID> -Force`.

## 7) Compose integration
- Ensure your container includes `.flyde` files.
- Map service ports consistently with your stack.
- Use `.env` for secrets; restart services after changes: `docker-compose up -d <service>`.

## 8) Observability
- Carry `correlationId` across all calls.
- Structured logs to stdout (JSON lines) for log aggregators.
- For Flyde runtime logs: `DEBUG=flyde:*` during debugging.

See also: [[Flow-Starter-Examples]], [[Integration-Patterns]], [[State-Observability]]


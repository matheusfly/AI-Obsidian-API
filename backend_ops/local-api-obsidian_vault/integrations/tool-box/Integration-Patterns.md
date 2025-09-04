# Integration Patterns

## 1) API endpoint → Flow (validation + observability)
- Validate inputs, run a `.flyde` flow, and return structured JSON with correlation IDs.
```ts
import { runFlow } from "@flyde/loader";
import path from "path";

export async function getForecastHandler(req, res) {
  const city = String(req.query.city ?? "");
  if (!city) return res.status(400).json({ ok: false, error: "city required" });

  const correlationId = req.headers["x-correlation-id"] ?? crypto.randomUUID();

  try {
    const flowPath = path.join(__dirname, "../flows/city-forecast.flyde");
    const result = await runFlow(flowPath, { city, correlationId });
    res.json({ ok: true, correlationId, ...result });
  } catch (err) {
    console.error("[getForecastHandler]", { correlationId, error: err.message });
    res.status(500).json({ ok: false, correlationId, error: err.message });
  }
}
```

## 2) Background job → Flow with retries/backoff
- Wrap `runFlow` with exponential backoff for resilience.
```ts
import { runFlow } from "@flyde/loader";
import path from "path";

async function runJobOnce(payload, attempt) {
  const flowPath = path.join(__dirname, "../flows/daily-reconcile.flyde");
  return runFlow(flowPath, { payload, attempt, scheduledAt: new Date().toISOString() });
}

export async function dailyReconcileJob(payload) {
  const maxAttempts = 3;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await runJobOnce(payload, attempt);
    } catch (e) {
      const delayMs = 1000 * Math.pow(2, attempt - 1);
      if (attempt === maxAttempts) throw e;
      await new Promise((r) => setTimeout(r, delayMs));
    }
  }
}
```

## 3) Event-driven orchestration
- On `order.created`, enrich data with a flow; use correlation IDs.
```ts
eventBus.on("order.created", async (evt) => {
  const correlationId = evt.correlationId ?? crypto.randomUUID();
  try {
    await runFlow("./flows/order-enrichment.flyde", { orderId: evt.id, correlationId });
  } catch (err) {
    console.error("[order.created]", { correlationId, error: err });
  }
});
```

## 4) Streaming outputs (SSE/WebSocket) via `loadFlow`
```ts
import { loadFlow } from "@flyde/loader";

export async function sseFlowHandler(req, res) {
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
  });

  const execute = await loadFlow("./flows/ai-long-run.flyde");

  const { result } = execute(
    { prompt: String(req.query.prompt ?? "") },
    {
      onOutputs: (key, value) => {
        res.write(`event: ${key}\n`);
        res.write(`data: ${JSON.stringify(value)}\n\n`);
      },
    }
  );

  result.finally(() => res.end());
}
```

## 5) Dependency injection & testability
- Wrap side effects (HTTP/DB/LLM) in code nodes; pass config/keys via inputs.
- Keep nodes small; make non-IO logic pure for deterministic tests.

## 6) Security
- Never hardcode secrets in flows/nodes.
- Retrieve secrets at the Motia layer (env/secret manager) and inject as inputs when calling `runFlow`/`loadFlow`.

## 7) Performance & concurrency
- Use `runFlow` for single-shot; `loadFlow` for streaming/progress.
- Prefer several composable nodes over one monolith for visibility and reusability.

See also: [[Testing-Deployment-Troubleshooting]], [[Commands]]


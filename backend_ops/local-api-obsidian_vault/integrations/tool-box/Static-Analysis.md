# Static Integration Analysis

This document enumerates likely integration issues on a Windows + Docker Compose stack with Motia + Flyde, and provides remediation steps and performance improvements for advanced custom flows.

## 1) Integration Issues (Symptoms → Causes → Fixes)

### A) Flow files not found at runtime
- Symptom: `ENOENT` or 404-like errors when calling `runFlow("./flows/...")`.
- Likely causes: wrong relative path; `.flyde` files not copied into image or deployment artifact; bundler excluded non-code assets.
- Fixes:
  - Resolve using `path.join(__dirname, "./flows/your-flow.flyde")`.
  - Ensure `.flyde` files are part of final build artifact or Docker image.
  - For bundlers, add asset copy steps or exclude `.flyde` from tree-shaking.

### B) SSE/streaming broken behind reverse proxy
- Symptom: Clients never receive incremental events; connection closes or buffers until end.
- Causes: Proxy buffering; missing HTTP/1.1; read timeouts.
- Fixes:
  - Nginx: `proxy_buffering off; proxy_read_timeout 1h; proxy_http_version 1.1;` (see [[Deployment-Playbooks]]).
  - Use `loadFlow` with `onOutputs` and SSE-friendly headers.

### C) Port conflicts (Windows)
- Symptom: Service fails to bind (EADDRINUSE).
- Causes: Another process uses the port; stale process.
- Fixes:
  - `Get-NetTCPConnection -LocalPort <port> -State Listen | Select LocalAddress,LocalPort,OwningProcess`
  - `Get-Process -Id <PID>` then `Stop-Process -Id <PID> -Force` (admin).

### D) Secrets leakage in logs
- Symptom: API keys visible in log lines.
- Causes: Logging raw inputs; insufficient redaction.
- Fixes:
  - Inject secrets at Motia layer via env; do not log them; pass only as inputs to nodes that need them.
  - Redact fields in JSON logging middleware.

### E) High LLM cost / latency
- Symptom: Slow responses; high monthly usage.
- Causes: Large prompts; retries due to invalid structure; calling wrong model for simple tasks.
- Fixes:
  - Use smaller models for classification/utility tasks.
  - Enforce structured outputs via schema & retries with temperature=0.
  - Cache intermediate results where possible.

### F) Unreliable external integrations
- Symptom: transient 5xx/429 errors; frequent timeouts.
- Causes: Provider instability or throttling.
- Fixes:
  - Backoff + jitter; circuit-breakers per provider.
  - Queue work in background jobs rather than synchronous endpoints.

### G) Flow-level state confusion
- Symptom: "State reset" or unexpected carry-over across runs.
- Causes: Misconception about node `state` lifecycle.
- Fixes:
  - Remember node `state` is per-flow-execution; store durable state externally (DB/Cache) if needed.

### H) CORS / mixed-origin issues
- Symptom: Browser blocks API/SSE calls.
- Fixes:
  - Configure CORS at API/proxy; for SSE ensure correct headers and same-origin paths via proxy.

## 2) Performance Improvements (Advanced Custom Flows)

### Pattern 1: Batch & parallelize
- Batch small requests (e.g., 10 items per call) to reduce overhead.
- Use parallel nodes with a join/merge node; cap concurrency (e.g., 4–8) to avoid provider throttling.

### Pattern 2: Reactive inputs for dynamic config
- Mark inputs as "reactive" for nodes that must re-run on input change (e.g., debounce); avoid busy-loop reruns.

### Pattern 3: Flow segmentation
- Split long flows into phases; checkpoint outputs; resume at next step. Improves observability and restartability.

### Pattern 4: Memoization & cache
- Cache pure computations and stable external results (e.g., static embeddings) by (input → output) key.

### Pattern 5: Guarded retries
- Retry only on transient errors (5xx/429/ETIMEDOUT); abort on 4xx that indicate permanent issues.

### Pattern 6: Structured outputs everywhere
- Ensures downstream nodes do minimal parsing; reduces re-tries from malformed outputs.

## 3) Static Checklist
- [ ] `.flyde` included in artifacts/images
- [ ] `__dirname` + `path.join` used for flows
- [ ] SSE proxy configured (no buffering + long read timeout)
- [ ] CORS rules defined for SPA/clients
- [ ] Secrets injected via env; redaction enabled
- [ ] CorrelationId generated; idempotency keys on writes
- [ ] Unit tests for flows; integration tests for endpoints
- [ ] Retry/backoff & rate limits per provider
- [ ] Metrics dashboard for flow throughput/latency

See also: [[Local-Server-Integration]], [[Deployment-Playbooks]], [[AI-Nodes]]


# Roadmap

A pragmatic roadmap for completing integration and scaling over time.

## Phase 0: Foundation (Week 1)
- ✅ Notebook scaffolding (Motia + Flyde docs, patterns, examples)
- ✅ Flow starter examples defined
- Decide repo locations for `flows/` and code nodes
- Enable Workbench locally (`npx motia dev`) and VS Code Flyde extension

## Phase 1: MVP Integration (Weeks 2–3)
- Implement `celsius-to-fahrenheit.flyde` and `convert` endpoint
- Implement `health.flyde` and wire `/health`
- Implement `order-enrichment.flyde` with code nodes (FetchOrder/FetchCustomer)
- Add structured logging with correlationId
- Basic CI pipeline: test → build → package

## Phase 2: AI Features (Weeks 3–4)
- Implement `CallLLM` node with provider inputs
- Implement streaming SSE endpoint (`ai-long-run.flyde`)
- Add ParseJSON validator node + retry on invalid structure
- Add rate limit/backoff and provider fallback

## Phase 3: Observability & Ops (Weeks 4–5)
- Grafana/Prometheus metrics for flow throughput/latency
- Tracing conventions and sampling policy
- Idempotency for write flows
- Hardening reverse proxy for SSE and CORS

## Phase 4: Productionization (Weeks 5–6)
- Containerize and include `.flyde` in image
- Secrets via env/manager and regular rotation
- Pre-deploy smoke tests and post-deploy verifications
- SLOs & error budgets; incident playbook

## Metrics & Success Criteria
- P50/P95 latency per endpoint and flow
- Error rate < 1% sustained
- Mean time to detect (MTTD) < 2 minutes via alerts
- Mean time to recovery (MTTR) < 30 minutes

## Risks & Mitigations
- Bundler excludes `.flyde` → include flows explicitly in build config
- SSE broken by proxy buffering → apply no-buffering config
- Model cost/control → rate-limit + batch + structured outputs to minimize retries
- Flaky integrations → backoff + circuit-breakers per provider

Ownership
- Tech lead: Integration architecture
- Platform: CI/CD, secrets, infra
- Backend: endpoints/jobs and code nodes
- QA: test plans for flows and streaming paths


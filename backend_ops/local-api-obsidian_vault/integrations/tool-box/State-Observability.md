# State & Observability

Best practices for traceability, reliability, and visibility across Motia and Flyde.

## Correlation & Idempotency
- **correlationId**: Generate once at request ingress; inject into every flow input. Log it in all nodes/handlers.
- **idempotencyKey**: For write operations, pass an idempotency key to prevent duplicate effects on retries.

## Structured Logging
- Use JSON lines with common fields: `{ ts, level, service, correlationId, idempotencyKey?, event, data }`.
- Avoid logging secrets (API keys, tokens).

## Tracing in Motia Workbench
- Run `npx motia dev` and open http://localhost:3000.
- Explore flows/runs, inspect logs and state per step.
- Use consistent step names and include `correlationId` in inputs for quick lookup.

## Flyde Visual Debugger
- In VS Code extension, use "test flow" to see per-node inputs/outputs live.
- For runtime logs, enable `DEBUG=flyde:*`.

## Metrics
- Capture counts/latency per flow/node (requests, failures, retries).
- If using Prometheus/Grafana, export counters/histograms (e.g., per provider/model for AI nodes).

## Sampling & Redaction
- Sample verbose logs (e.g., body payloads) at low rates to control volume.
- Redact PII/secrets before logging/storing.

## Conventions
- Inputs: `correlationId`, `requestedBy`, `source`, `idempotencyKey?`.
- Outputs: include `durationMs`, `status`, `warnings?`.

See also: [[Testing-Deployment-Troubleshooting]], [[Integration-Patterns]]


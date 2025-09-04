# Motia

Motia is a unified backend framework for REST APIs, background jobs, scheduled tasks, event-driven workflows, streams, and built-in observability.

## Quick Start
- Create a new project (interactive):
  - `npx motia@latest create -i`
- Start the dev server + Workbench (http://localhost:3000):
  - `npx motia dev`
- Note: If you selected pnpm/yarn/bun during setup, use `pnpm dev`, `yarn dev`, or `bun dev` respectively.

## Workbench (Visual Debugger)
- Accessible at http://localhost:3000 when running `npx motia dev`.
- Explore the starter flow (often named `default`), run steps, and inspect traces/logs/state.
- Useful for developing and debugging your orchestration.

## Core Capabilities
- REST API endpoints with validation and error handling.
- Background jobs & scheduled tasks with clean orchestration.
- Event-driven flows (publish/subscribe patterns).
- Real-time streams to clients (e.g., WebSockets/SSE).
- Logging, tracing, and state management built in.

## Suggested Structure
- `flows/` — Flyde `.flyde` files and `.flyde.ts` code nodes.
- `src/api/`, `src/jobs/` — Motia handlers calling flows.
- `src/shared/` — shared utilities, domain logic.
- `config/` — env, secrets plumbing.

## Secrets & Config
- Keep secrets in environment variables/secret manager.
- Inject them into flows via inputs (never hardcode keys in flows/nodes).

See also: [[Integration-Patterns]], [[Commands]], [[References]]


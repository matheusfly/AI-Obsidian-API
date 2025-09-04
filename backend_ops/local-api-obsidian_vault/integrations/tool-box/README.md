# Motia + Flyde Knowledge Base

Updated: 2025-09-04

Purpose: Consolidated in-codebase guide for using Motia (unified backend runtime) with Flyde (visual flows) to build APIs, jobs, workflows, and AI logic, with live visualization/debugging.

Quick links (Obsidian):
- [[Motia]]
- [[Flyde]]
- [[Integration-Patterns]]
- [[Flow-Starter-Examples]]
- [[AI-Nodes]]
- [[State-Observability]]
- [[Deployment-Playbooks]]
- [[Local-Server-Integration]]
- [[Testing-Deployment-Troubleshooting]]
- [[Commands]]
- [[Static-Analysis]]
- [[Roadmap]]
- [[References]]

Scope
- Keep logic in your codebase; use Flyde for visual orchestration, nodes, and flows.
- Use Motia to unify APIs, background jobs, event-driven workflows, streams, observability and state.
- Provide patterns for live/interactive UIs (SSE/WebSocket), testing, deployment, and reliability.

Highlights
- Motia Workbench (http://localhost:3000) for live traces, logs, and state when running `npx motia dev`.
- Flyde runs inside the codebase—create `.flyde` flows and custom `.flyde.ts` nodes; execute via `@flyde/loader`.
- Combine both: call flows from endpoints/jobs, stream intermediate outputs, track correlation IDs.

Changelog
- v0.2 (2025-09-04): Added AI-Nodes, State-Observability, Deployment-Playbooks, Local-Server-Integration, Flow-Starter-Examples, Static-Analysis, Roadmap.
- v0.1 (2025-09-04): Initial structure and content.

See also: [[References]]


# AI Nodes (OpenAI, Anthropic, others)

This note provides provider-specific patterns for building robust AI nodes in Flyde, called from Motia endpoints/jobs.

## Goals
- Structured outputs (strict JSON)
- Tool-calling / function-calling workflows
- Safety guardrails (prompt-injection, output validation)
- Streaming tokens / incremental outputs
- Resilience (timeouts, retries, fallbacks)

## Structured outputs (JSON)
Pattern: Ask model to return JSON matching a schema, validate at runtime.
```ts
// Code node pseudo-logic
export const ParseJSON: InternalCodeNode = {
  id: "ParseJSON",
  description: "Validates LLM JSON output against schema",
  inputs: { text: { description: "raw model output" } },
  outputs: { json: { description: "validated object" }, error: { description: "validation errors" } },
  run: ({ text }, { json, error }) => {
    try {
      const obj = JSON.parse(text);
      // Optional: custom schema validation here
      json.next(obj);
    } catch (e) {
      error.next({ message: "Invalid JSON", details: String(e) });
    }
  },
};
```
Guidelines:
- Provide schema examples to the model in the system prompt.
- Reject non-JSON outputs in a validator node and re-try with a clarifying prompt.

## Tool-calling / Function-calling
- Represent tools as inputs to the node (an array of available tools + auth tokens).
- Node chooses the tool by name and calls it (HTTP or internal function).
- Emit intermediate outputs per call so `onOutputs` can stream to clients.

## Guardrails & Safety
- Input sanitization: trim, length-limit, allowlist of domains.
- Output validation: JSON schema check before downstream processing.
- Non-deterministic retry with temperature=0 when structure fails.
- Log correlationId but never secrets.

## Providers: OpenAI & Anthropic
- Inputs: { apiKey, model, system, user, temperature, tools? }
- Control timeouts: fetch timeout + retry on 429/5xx with backoff.
- Fallback model list: e.g., try `gpt-4o-mini` -> fallback `gpt-4o` or Anthropic counterpart if failure.

## Streaming patterns
- Use `loadFlow` and emit partial tokens on a dedicated output (e.g., `delta`).
- SSE endpoint forwards `delta` events to the browser.

## Example: CallLLM node (simplified)
```ts
import { InternalCodeNode } from "@flyde/core";

export const CallLLM: InternalCodeNode = {
  id: "CallLLM",
  description: "Calls an LLM provider and emits text",
  inputs: {
    apiKey: { description: "Provider API key" },
    provider: { description: "'openai'|'anthropic'" },
    model: { description: "Model ID" },
    system: { description: "System prompt" },
    user: { description: "User prompt" },
  },
  outputs: { text: { description: "Model response text" }, error: { description: "Error" } },
  async run({ apiKey, provider, model, system, user }, { text, error }) {
    try {
      const url = provider === "openai" ? "https://api.example/openai" : "https://api.example/anthropic";
      const resp = await fetch(url, {
        method: "POST",
        headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({ model, system, user })
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      text.next(data.output);
    } catch (e) {
      error.next({ message: String(e) });
    }
  },
};
```

## Resilience checklist
- Timeouts (e.g., 20s) + retries with backoff on transient errors.
- Circuit-breaker per provider if repeated failures.
- Observability fields: { correlationId, latencyMs, provider, model, tokens }.

See also: [[Integration-Patterns]], [[State-Observability]], [[References]]


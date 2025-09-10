# Flow Starter Examples

Use these as starting points. Create flows via the VS Code extension ("Flyde: New visual flow"), then connect nodes to match the patterns below and name the files accordingly in your `flows/` folder.

## 1) celsius-to-fahrenheit.flyde
- Inputs: `celsius: number`
- Logic: `fahrenheit = celsius * 9 / 5 + 32`
- Outputs: `fahrenheit: number`
- Endpoint wiring example:
```ts
import { runFlow } from "@flyde/loader";
import path from "path";
export async function convert(req, res) {
  const celsius = Number(req.query.c ?? 0);
  const result = await runFlow(path.join(__dirname, "../flows/celsius-to-fahrenheit.flyde"), { celsius });
  res.json(result);
}
```

## 2) order-enrichment.flyde
- Inputs: `orderId: string`, `correlationId: string`
- Nodes:
  - `FetchOrder` (code node) -> calls DB/HTTP to load order
  - `FetchCustomer` (code node)
  - `Merge` -> combine data
- Outputs: `enrichedOrder: object`
- Event wiring example:
```ts
eventBus.on("order.created", async (evt) => {
  await runFlow("./flows/order-enrichment.flyde", { orderId: evt.id, correlationId: evt.correlationId });
});
```

## 3) ai-long-run.flyde
- Inputs: `prompt: string`
- Nodes:
  - `CallLLM` (code node; see [[AI-Nodes]]) with streaming or chunked outputs
  - Optional `ParseJSON` to enforce JSON structure
- Outputs: `final: object` or `text: string`, plus streamed `delta` events via `loadFlow` onOutputs.
- SSE endpoint example:
```ts
import { loadFlow } from "@flyde/loader";
export async function sseLLM(req, res) {
  res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", Connection: "keep-alive" });
  const execute = await loadFlow("./flows/ai-long-run.flyde");
  const { result } = execute({ prompt: String(req.query.prompt ?? "") }, {
    onOutputs: (key, value) => {
      res.write(`event: ${key}\n`);
      res.write(`data: ${JSON.stringify(value)}\n\n`);
    },
  });
  result.finally(() => res.end());
}
```

## 4) health.flyde
- Simple node that returns `{ ok: true }` to validate the runtime.
- Use in `/health` if you need flow-level validation.

## Code node stubs (place under `flows/` as `.flyde.ts`)
```ts
import { InternalCodeNode } from "@flyde/core";

export const FetchOrder: InternalCodeNode = {
  id: "FetchOrder",
  description: "Loads order by ID",
  inputs: { orderId: { description: "Order ID" } },
  outputs: { order: { description: "Order object" }, error: { description: "Error info" } },
  async run({ orderId }, { order, error }) {
    try {
      const resp = await fetch(`http://orders.internal/api/orders/${orderId}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      order.next(await resp.json());
    } catch (e) { error.next(String(e)); }
  },
};

export const FetchCustomer: InternalCodeNode = {
  id: "FetchCustomer",
  description: "Loads customer by ID",
  inputs: { customerId: { description: "Customer ID" } },
  outputs: { customer: { description: "Customer object" }, error: { description: "Error info" } },
  async run({ customerId }, { customer, error }) {
    try {
      const resp = await fetch(`http://customers.internal/api/customers/${customerId}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      customer.next(await resp.json());
    } catch (e) { error.next(String(e)); }
  },
};
```

Notes
- Replace internal endpoints with your actual services.
- Keep secrets in env at the Motia layer and inject into flows as inputs.

See also: [[Local-Server-Integration]], [[AI-Nodes]], [[Integration-Patterns]]


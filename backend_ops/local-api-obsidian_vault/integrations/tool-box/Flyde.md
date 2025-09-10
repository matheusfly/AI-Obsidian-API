# Flyde

Flyde is a visual, flow-based programming toolkit that integrates with your existing code. It runs inside your codebase and can be authored via a VS Code extension.

## Core Concepts
- **Flows** (`.flyde` files): Nodes connected by wires; flows can have inputs and outputs.
- **Nodes**: Building blocks of logic with inputs/outputs. Types:
  - Code nodes (TypeScript/JavaScript via `.flyde.ts`) — simplest & most flexible.
  - Visual nodes (a flow used as a node).
  - Macro nodes (visual config at edit-time).
- **Connections**: Wires transferring values between nodes.

## Built-in Nodes
- Available via `@flyde/nodes` (installed via `@flyde/loader`).
- Includes control flow utilities (Conditional, Switch, Loop) and simple value nodes.

## Running Flows in Code
- Simple execution (returns final outputs):
```ts
import { runFlow } from "@flyde/loader";
import path from "path";

const result = await runFlow(path.join(__dirname, "./flows/celsius-to-fahrenheit.flyde"), {
  celsius: 0,
});
// e.g. result: { fahrenheit: 32 }
```
- Advanced execution with events (streaming outputs):
```ts
import { loadFlow } from "@flyde/loader";

const execute = await loadFlow("./flows/celsius-to-fahrenheit.flyde");
const { result } = execute({ celsius: 10 }, {
  onOutputs: (key, value) => {
    console.log("output", key, value);
  },
});
```

## Creating Custom Code Nodes
- Write `.flyde.ts` files that export an `InternalCodeNode`.
- Example: Add two numbers
```ts
import { InternalCodeNode } from "@flyde/core";

export const Add: InternalCodeNode = {
  id: "Add",
  description: "Emits the sum of two numbers",
  inputs: { n1: { description: "First number" }, n2: { description: "Second number" } },
  outputs: { sum: { description: "The sum of n1 and n2" } },
  run: ({ n1, n2 }, { sum }) => sum.next(n1 + n2),
};
```
- Example: Average over time (uses per-flow state)
```ts
import { InternalCodeNode } from "@flyde/core";

export const Average: InternalCodeNode = {
  id: "Average",
  description: "Emits the average of all numbers received",
  inputs: { n: { description: "Number" } },
  outputs: { average: { description: "Average so far" } },
  run: ({ n }, { average }, { state }) => {
    const numbers = state.get("numbers") ?? [];
    numbers.push(n);
    state.set("numbers", numbers);
    average.next(numbers.reduce((a, b) => a + b, 0) / numbers.length);
  },
};
```

## Debugging
- Use the VS Code extension’s visual debugger/test feature to see inputs/outputs live.
- Enable verbose runtime logs with `DEBUG=flyde:*` when executing flows in Node.

See also: [[Integration-Patterns]], [[Testing-Deployment-Troubleshooting]], [[References]]


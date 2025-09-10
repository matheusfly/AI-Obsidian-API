# Testing, Deployment, Troubleshooting

## Unit testing flows
```ts
import { runFlow } from "@flyde/loader";
import path from "path";

test("celsius-to-fahrenheit: 0°C -> 32°F", async () => {
  const result = await runFlow(path.join(__dirname, "../flows/celsius-to-fahrenheit.flyde"), { celsius: 0 });
  expect(result.fahrenheit).toBe(32);
});
```

## Integration testing endpoints/jobs
- Stub external calls in code nodes (e.g., mock `fetch`).
- Assert on JSON responses and onOutputs streams.

## Packaging & Deployment
- Ship `.flyde` files with your app (don’t exclude in bundler).
- Resolve flow paths at runtime with `path.join(__dirname, "./flows/...")`.
- Keep secrets in env; inject to flows as inputs in production.
- Motia supports cloud and self-hosted deployments—follow the Motia deployment docs.

## Troubleshooting
- **VS Code extension**: Use "Developer: Toggle Developer Tools" to inspect errors.
- **Verbose runtime logs** for Flyde: `DEBUG=flyde:* node your-entry.js`.
- **Correlation IDs**: Pass a `correlationId` input into flows and add it to logs for seamless traceability.
- **Common pitfalls**:
  - Wrong relative paths to `.flyde` files → prefer `__dirname` + `path.join`.
  - Secrets leaked via logs → never log injected keys; keep them as inputs only.
  - Long-running operations blocking → split into multiple nodes; consider streaming via `loadFlow`.

See also: [[Integration-Patterns]], [[References]]


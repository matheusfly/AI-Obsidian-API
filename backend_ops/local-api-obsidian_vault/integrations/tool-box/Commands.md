# Commands

## Motia
- Bootstrap a new project (interactive):
  - `npx motia@latest create -i`
- Start dev server + Workbench (http://localhost:3000):
  - `npx motia dev`
- Note: If you chose a different package manager during setup, use `pnpm dev`, `yarn dev`, or `bun dev` instead.

## Flyde (runtime usage)
- No separate CLI required to run flows in your app.
- Use `@flyde/loader` from code:
  - Simple: `runFlow(flowPath, inputs)`
  - Advanced: `loadFlow(flowPath)` + `onOutputs` for streaming/progress

## Debugging
- Enable detailed runtime logs for flows:
  - Unix: `DEBUG=flyde:* node your-entry.js`
  - Windows (Powershell): `$env:DEBUG = "flyde:*"; node your-entry.js`

See also: [[Testing-Deployment-Troubleshooting]]


import * as pty from 'node-pty';

// Launch a Textual app in a PTY (interactive)
export function runTextualApp(entry: string, cwd?: string) {
  const shell = process.platform === 'win32' ? 'pwsh.exe' : 'bash';
  const term = pty.spawn(shell, [], {
    name: 'xterm-color',
    cols: 120,
    rows: 30,
    cwd: cwd || process.cwd(),
    env: process.env as any,
  });
  const cmd = `${process.platform === 'win32' ? '' : ''}python ${entry}`; // placeholder
  term.write(cmd + (process.platform === 'win32' ? "\r" : "\n"));
  return term; // caller should hook term.onData
}


import {execa, ExecaReturnValue} from 'execa';
import * as pty from 'node-pty';

export interface RunOptions {
  cmd: string | string[];
  cwd?: string;
  env?: Record<string, string>;
  interactive?: boolean; // if true -> use PTY
  timeoutMs?: number;
  teeToFile?: string;
  redact?: string[];
}

export interface RunResult {
  code: number;
  stdout: string;
  stderr: string;
  timedOut: boolean;
  startedAt: string;
  endedAt: string;
}

export class CommandPool {
  private shells = new Map<string, pty.IPty>();

  async run(name: string, opts: RunOptions): Promise<RunResult> {
    const startedAt = new Date().toISOString();
    if (opts.interactive) {
      // PTY run (simple placeholder that just launches and exits)
      return await new Promise<RunResult>((resolve) => {
        const shell = process.platform === 'win32' ? 'pwsh.exe' : 'bash';
        const term = pty.spawn(shell, [], {
          name: 'xterm-color',
          cols: 120,
          rows: 30,
          cwd: opts.cwd || process.cwd(),
          env: {...process.env, ...(opts.env || {})},
        });
        let stdout = '';
        term.onData((d) => (stdout += d));
        const cmd = Array.isArray(opts.cmd) ? opts.cmd.join(' ') : opts.cmd;
        term.write(cmd + (process.platform === 'win32' ? "\r" : "\n"));
        // naive finish after a short delay (skeleton only)
        setTimeout(() => {
          term.kill();
          const endedAt = new Date().toISOString();
          resolve({code: 0, stdout, stderr: '', timedOut: false, startedAt, endedAt});
        }, 500);
      });
    }

    const args = Array.isArray(opts.cmd) ? (opts.cmd as string[]) : (opts.cmd as string).split(' ');
    const bin = args.shift() as string;
    let result: ExecaReturnValue<string>;
    try {
      result = await execa(bin, args, {
        cwd: opts.cwd,
        env: {...process.env, ...(opts.env || {})},
        timeout: opts.timeoutMs,
        all: false,
      });
      const endedAt = new Date().toISOString();
      return {
        code: result.exitCode ?? 0,
        stdout: result.stdout,
        stderr: result.stderr,
        timedOut: false,
        startedAt,
        endedAt,
      };
    } catch (err: any) {
      const endedAt = new Date().toISOString();
      return {
        code: err.exitCode ?? 1,
        stdout: err.stdout ?? '',
        stderr: err.stderr ?? String(err),
        timedOut: Boolean(err.timedOut),
        startedAt,
        endedAt,
      };
    }
  }

  async startPersistentShell(name: string, shell?: string, cwd?: string) {
    const sh = shell || (process.platform === 'win32' ? 'pwsh.exe' : 'bash');
    const term = pty.spawn(sh, [], {
      name: 'xterm-color',
      cols: 120,
      rows: 30,
      cwd: cwd || process.cwd(),
      env: process.env as any,
    });
    this.shells.set(name, term);
  }

  writeToShell(name: string, data: string) {
    this.shells.get(name)?.write(data);
  }

  stop(name: string) {
    this.shells.get(name)?.kill();
    this.shells.delete(name);
  }

  list() {
    return Array.from(this.shells.keys()).map((k) => ({name: k, running: true}));
  }
}


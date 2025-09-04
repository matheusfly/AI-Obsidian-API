import {execa} from 'execa';
import {detectPython} from './python-env';

export async function runTyper(moduleOrPath: string, args: string[] = [], opts?: {cwd?: string; json?: boolean}) {
  const py = await detectPython();
  const fullArgs = [...py.args];
  // Prefer: python -m module if no .py extension given
  if (!moduleOrPath.endsWith('.py')) {
    fullArgs.push('-m', moduleOrPath);
  } else {
    fullArgs.push(moduleOrPath);
  }
  if (opts?.json) fullArgs.push('--json');
  fullArgs.push(...args);
  const {stdout} = await execa(py.cmd, fullArgs, {cwd: opts?.cwd});
  return stdout;
}


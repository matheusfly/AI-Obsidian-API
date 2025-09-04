import {execa} from 'execa';
import {detectPython} from './python-env';

// Wrapper to run a Python script that prints Rich-formatted output.
export async function runRichScript(scriptPath: string, args: string[] = [], opts?: {cwd?: string}) {
  const py = await detectPython();
  const fullArgs = [...py.args, scriptPath, ...args];
  // We return stdout raw; UI can decide how to display
  const {stdout} = await execa(py.cmd, fullArgs, {cwd: opts?.cwd});
  return stdout;
}


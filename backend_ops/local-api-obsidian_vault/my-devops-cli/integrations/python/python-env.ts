// Detects a Python runner: uv -> python -> py -3
export async function detectPython(): Promise<{cmd: string; args: string[]}> {
  const {execa} = await import('execa');
  const tryCmd = async (cmd: string, args: string[] = ['--version']) => {
    try { await execa(cmd, args); return true; } catch { return false; }
  };
  if (await tryCmd('uv', ['--version'])) return {cmd: 'uv', args: []};
  if (await tryCmd('python', ['--version'])) return {cmd: 'python', args: []};
  if (process.platform === 'win32' && await tryCmd('py', ['-3', '--version'])) return {cmd: 'py', args: ['-3']};
  // Fallback to python even if not verified
  return {cmd: 'python', args: []};
}


import {execa} from 'execa';

export async function up(services?: string[], cwd?: string) {
  const hasDockerCompose = false; // future: detect docker-compose binary if needed
  const bin = 'docker';
  const args = ['compose', 'up', '-d', ...(services ?? [])];
  return execa(bin, args, {cwd, stdio: 'inherit'});
}

export async function down(cwd?: string) {
  return execa('docker', ['compose', 'down'], {cwd, stdio: 'inherit'});
}

export async function logsFollow(service?: string, cwd?: string) {
  const args = ['compose', 'logs', '-f'];
  if (service) args.push(service);
  return execa('docker', args, {cwd, stdio: 'inherit'});
}

export async function ps(cwd?: string) {
  return execa('docker', ['compose', 'ps'], {cwd, stdio: 'inherit'});
}


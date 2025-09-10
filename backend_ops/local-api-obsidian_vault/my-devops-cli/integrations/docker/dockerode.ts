import Docker from 'dockerode';

export function makeDocker(opts?: Docker.DockerOptions) {
  return new Docker(opts);
}

export async function listContainers(docker = makeDocker()) {
  return docker.listContainers({all: true});
}


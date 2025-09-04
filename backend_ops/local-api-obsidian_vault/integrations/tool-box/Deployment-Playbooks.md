# Deployment Playbooks

This note covers Cloud vs self-hosted choices, Docker Compose integration, CI/CD, secrets, and health checks.

## Options
- **Motia Cloud**: Zero-config deployment managed by Motia. Good for speed.
- **Self-hosted**: Deploy Motia app + `.flyde` files as part of your service stack.

## Docker Compose (local)
- Ensure `.flyde` files are copied into the image or mounted in volumes.
- Resolve flows by `path.join(__dirname, "./flows/...")`.
- Environment variables from `.env` for secrets; never bake secrets into images.

## Nginx / Reverse Proxy
- SSE passthrough for streaming endpoints:
```
location /sse/ {
  proxy_http_version 1.1;
  proxy_set_header Connection "";
  proxy_set_header Host $host;
  proxy_buffering off;
  proxy_read_timeout 1h;
  chunked_transfer_encoding on;
  proxy_pass http://backend:PORT;
}
```

## CI/CD Outline
1) **Lint & test**: `npm test` with unit tests for flows (`runFlow`) and integration tests for endpoints.
2) **Build**: compile code; include `.flyde` files in artifact.
3) **Scan**: secrets scanning, dependency vulnerabilities.
4) **Package**: Docker image; tag with commit SHA.
5) **Deploy**: Compose or K8s manifests.
6) **Post-deploy checks**: health endpoints + smoke tests.

## K8s (alternative)
- Mount flows via ConfigMap or include in image.
- Pod readiness: health checks against API endpoints.
- Horizontal autoscaling on CPU/RAM or custom metrics (requests/sec).

## Secrets Management
- Provide secrets via env or secret manager; inject into flows via inputs.
- Rotate keys regularly; avoid logging secrets.

## Health Checks
- Implement `/health` routes for every API
- For Motia endpoints calling flows, add an internal `runFlow("./flows/health.flyde")` if necessary to validate dependencies.

See also: [[Local-Server-Integration]], [[Testing-Deployment-Troubleshooting]], [[References]]


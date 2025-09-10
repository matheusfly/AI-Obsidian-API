export type HealthCheck = {
  id: string;
  url: string;
  expect: number | number[];
};

export type HealthStatus = {
  id: string;
  ok: boolean;
  status: number | 'ERR';
  latencyMs?: number;
};

const toArray = (n: number | number[]) => (Array.isArray(n) ? n : [n]);

export async function ping(url: string, timeoutMs = 4000): Promise<{status: number | 'ERR'; latencyMs?: number}> {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  const start = Date.now();
  try {
    const res = await fetch(url, {signal: controller.signal});
    const latencyMs = Date.now() - start;
    clearTimeout(t);
    return {status: res.status, latencyMs};
  } catch {
    clearTimeout(t);
    return {status: 'ERR'};
  }
}

export async function checkAll(checks: HealthCheck[], timeoutMs = 4000): Promise<HealthStatus[]> {
  const results = await Promise.all(
    checks.map(async (c) => {
      const r = await ping(c.url, timeoutMs);
      const ok = r.status !== 'ERR' && toArray(c.expect).includes(r.status as number);
      return {id: c.id, ok, status: r.status, latencyMs: r.latencyMs} as HealthStatus;
    })
  );
  return results;
}


import {cosmiconfig} from 'cosmiconfig';

export type AppConfig = {
  health: {id: string; url: string; expect: number | number[]}[];
};

const defaultConfig: AppConfig = {
  health: [
    {id: 'vault-api', url: 'http://localhost:8085/health', expect: [200]},
    {id: 'obsidian-api', url: 'http://localhost:27123/health', expect: [200]},
    {id: 'n8n', url: 'http://localhost:5678/', expect: [200]},
    {id: 'grafana', url: 'http://localhost:3004/api/health', expect: [200]},
    {id: 'nginx', url: 'http://localhost:8088/', expect: [200]}
  ]
};

export async function loadConfig(): Promise<AppConfig> {
  const explorer = cosmiconfig('mydevops');
  try {
    const result = await explorer.search();
    if (result && result.config) {
      const cfg = result.config as Partial<AppConfig>;
      return {
        ...defaultConfig,
        ...cfg,
        health: cfg.health ?? defaultConfig.health,
      } satisfies AppConfig;
    }
  } catch {}
  return defaultConfig;
}


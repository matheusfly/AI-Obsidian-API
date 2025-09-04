import React, {useEffect, useState} from 'react';
import {Box, Text, Newline} from 'ink';
import type {HealthCheck, HealthStatus} from '../services/health';
import {checkAll} from '../services/health';

export default function Dashboard({health}: {health: HealthCheck[]}) {
  const [statuses, setStatuses] = useState<HealthStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      setLoading(true);
      const data = await checkAll(health, 4000);
      if (mounted) {
        setStatuses(data);
        setLoading(false);
      }
    })();
    const t = setInterval(async () => {
      const data = await checkAll(health, 4000);
      if (mounted) setStatuses(data);
    }, 8000);
    return () => {
      mounted = false;
      clearInterval(t);
    };
  }, [health]);

  return (
    <Box flexDirection="column">
      <Text>my-devops-cli • Dashboard</Text>
      <Text>
        {loading ? 'Checking services...' : 'Status refreshed'}
      </Text>
      <Newline />
      {statuses.map((s) => (
        <Box key={s.id}>
          <Text>
            {s.ok ? '✅' : '❌'} {s.id.padEnd(12)} → {String(s.status).padEnd(4)}{' '}
            {typeof s.latencyMs === 'number' ? `${s.latencyMs} ms` : ''}
          </Text>
        </Box>
      ))}
      <Newline />
      <Text dimColor>
        q to quit • future: logs, compose controls, workflows, AI/MCP
      </Text>
    </Box>
  );
}


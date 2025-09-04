import React from 'react';
import {render} from 'ink';
import Dashboard from './ui/dashboard';
import {loadConfig} from './services/config';

async function main() {
  const cfg = await loadConfig();
  render(<Dashboard health={cfg.health} />);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});


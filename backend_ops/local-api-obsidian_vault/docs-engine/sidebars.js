/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // Main documentation sidebar
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
        'getting-started/first-workflow',
        'getting-started/configuration',
      ],
    },
    {
      type: 'category',
      label: 'Core Concepts',
      items: [
        'concepts/overview',
        'concepts/ai-agents',
        'concepts/workflows',
        'concepts/data-flow',
        'concepts/security',
      ],
    },
    {
      type: 'category',
      label: 'User Guide',
      items: [
        'user-guide/obsidian-integration',
        'user-guide/ai-features',
        'user-guide/automation',
        'user-guide/monitoring',
        'user-guide/troubleshooting',
      ],
    },
    {
      type: 'category',
      label: 'Development',
      items: [
        'development/setup',
        'development/contributing',
        'development/coding-standards',
        'development/testing',
        'development/debugging',
      ],
    },
    {
      type: 'category',
      label: 'Advanced Topics',
      items: [
        'advanced/custom-agents',
        'advanced/plugin-development',
        'advanced/performance-optimization',
        'advanced/scaling',
        'advanced/monitoring',
      ],
    },
  ],

  // API Reference sidebar
  apiSidebar: [
    'api/overview',
    {
      type: 'category',
      label: 'REST API',
      items: [
        'api/rest/authentication',
        'api/rest/vault-operations',
        'api/rest/ai-operations',
        'api/rest/workflow-operations',
        'api/rest/monitoring',
        'api/rest/errors',
      ],
    },
    {
      type: 'category',
      label: 'WebSocket API',
      items: [
        'api/websocket/real-time',
        'api/websocket/events',
        'api/websocket/authentication',
      ],
    },
    {
      type: 'category',
      label: 'MCP Tools',
      items: [
        'api/mcp/overview',
        'api/mcp/filesystem',
        'api/mcp/web-scraping',
        'api/mcp/database',
        'api/mcp/ai-tools',
        'api/mcp/custom-tools',
      ],
    },
    {
      type: 'category',
      label: 'SDKs',
      items: [
        'api/sdks/python',
        'api/sdks/javascript',
        'api/sdks/typescript',
        'api/sdks/powershell',
      ],
    },
    {
      type: 'category',
      label: 'OpenAPI',
      items: [
        'api/openapi/specification',
        'api/openapi/interactive-docs',
        'api/openapi/testing',
      ],
    },
  ],

  // Architecture sidebar
  architectureSidebar: [
    'architecture/overview',
    {
      type: 'category',
      label: 'System Design',
      items: [
        'architecture/system-design',
        'architecture/data-architecture',
        'architecture/security-architecture',
        'architecture/performance-architecture',
      ],
    },
    {
      type: 'category',
      label: 'Components',
      items: [
        'architecture/components/api-gateway',
        'architecture/components/ai-orchestrator',
        'architecture/components/workflow-engine',
        'architecture/components/vector-database',
        'architecture/components/monitoring',
      ],
    },
    {
      type: 'category',
      label: 'Design Patterns',
      items: [
        'architecture/patterns/clean-architecture',
        'architecture/patterns/microservices',
        'architecture/patterns/event-driven',
        'architecture/patterns/plugin-architecture',
      ],
    },
    {
      type: 'category',
      label: 'Data Flow',
      items: [
        'architecture/data-flow/overview',
        'architecture/data-flow/ingestion',
        'architecture/data-flow/processing',
        'architecture/data-flow/storage',
        'architecture/data-flow/retrieval',
      ],
    },
    {
      type: 'category',
      label: 'Integration Patterns',
      items: [
        'architecture/integrations/obsidian',
        'architecture/integrations/ai-services',
        'architecture/integrations/databases',
        'architecture/integrations/monitoring',
      ],
    },
  ],

  // Deployment sidebar
  deploymentSidebar: [
    'deployment/overview',
    {
      type: 'category',
      label: 'Local Development',
      items: [
        'deployment/local/docker',
        'deployment/local/manual',
        'deployment/local/development-setup',
        'deployment/local/debugging',
      ],
    },
    {
      type: 'category',
      label: 'Production Deployment',
      items: [
        'deployment/production/docker-compose',
        'deployment/production/kubernetes',
        'deployment/production/cloud-providers',
        'deployment/production/security',
      ],
    },
    {
      type: 'category',
      label: 'CI/CD',
      items: [
        'deployment/cicd/github-actions',
        'deployment/cicd/gitlab-ci',
        'deployment/cicd/jenkins',
        'deployment/cicd/automated-testing',
      ],
    },
    {
      type: 'category',
      label: 'Monitoring & Observability',
      items: [
        'deployment/monitoring/prometheus',
        'deployment/monitoring/grafana',
        'deployment/monitoring/logging',
        'deployment/monitoring/alerting',
      ],
    },
    {
      type: 'category',
      label: 'Scaling',
      items: [
        'deployment/scaling/horizontal',
        'deployment/scaling/vertical',
        'deployment/scaling/load-balancing',
        'deployment/scaling/caching',
      ],
    },
  ],

  // Additional sidebars for specific sections
  guidesSidebar: [
    'guides/overview',
    {
      type: 'category',
      label: 'Setup Guides',
      items: [
        'guides/setup/windows',
        'guides/setup/macos',
        'guides/setup/linux',
        'guides/setup/docker',
      ],
    },
    {
      type: 'category',
      label: 'Feature Guides',
      items: [
        'guides/features/ai-agents',
        'guides/features/workflows',
        'guides/features/automation',
        'guides/features/monitoring',
      ],
    },
    {
      type: 'category',
      label: 'Integration Guides',
      items: [
        'guides/integrations/obsidian',
        'guides/integrations/notion',
        'guides/integrations/github',
        'guides/integrations/slack',
      ],
    },
  ],

  // Troubleshooting sidebar
  troubleshootingSidebar: [
    'troubleshooting/overview',
    {
      type: 'category',
      label: 'Common Issues',
      items: [
        'troubleshooting/installation-issues',
        'troubleshooting/api-issues',
        'troubleshooting/ai-issues',
        'troubleshooting/performance-issues',
      ],
    },
    {
      type: 'category',
      label: 'Error Codes',
      items: [
        'troubleshooting/error-codes/api-errors',
        'troubleshooting/error-codes/ai-errors',
        'troubleshooting/error-codes/workflow-errors',
        'troubleshooting/error-codes/system-errors',
      ],
    },
    {
      type: 'category',
      label: 'Debugging',
      items: [
        'troubleshooting/debugging/logs',
        'troubleshooting/debugging/monitoring',
        'troubleshooting/debugging/performance',
        'troubleshooting/debugging/network',
      ],
    },
  ],
};

module.exports = sidebars;

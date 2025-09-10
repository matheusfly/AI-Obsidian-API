import React from 'react';
import clsx from 'clsx';
import styles from '../pages/styles/index.module.css';

const FeatureList = [
  {
    title: '🚀 Ultra-Fast Performance',
    icon: '⚡',
    description: (
      <>
        UV-optimized Python environment with Docker BuildKit for lightning-fast startup times.
        Production-ready with resource limits and health monitoring.
      </>
    ),
  },
  {
    title: '🤖 Advanced AI Integration',
    icon: '🧠',
    description: (
      <>
        Enhanced RAG system with hierarchical queries, batch processing, and intelligent caching.
        MCP tools integration for context-aware AI operations.
      </>
    ),
  },
  {
    title: '📊 Comprehensive Observability',
    icon: '📈',
    description: (
      <>
        Real-time monitoring with Prometheus, Grafana dashboards, and LangSmith tracing.
        Interactive chat monitoring with thread IDs and human-in-the-loop checkpoints.
      </>
    ),
  },
  {
    title: '🔧 Production-Ready Infrastructure',
    icon: '🛠️',
    description: (
      <>
        Docker Compose orchestration with 15+ microservices, CI/CD pipeline, and automated testing.
        Security hardening with JWT authentication and rate limiting.
      </>
    ),
  },
  {
    title: '📚 Complete Documentation',
    icon: '📖',
    description: (
      <>
        Centralized Docusaurus documentation with OpenAPI integration, Mermaid diagrams,
        and beautiful dark theme with high contrast rendering.
      </>
    ),
  },
  {
    title: '🔗 MCP Tools Ecosystem',
    icon: '🧩',
    description: (
      <>
        Model Context Protocol integration with filesystem, GitHub, Playwright, Context7,
        ByteRover, and other advanced tools for enhanced AI capabilities.
      </>
    ),
  },
];

function Feature({title, icon, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className={styles.featureCard}>
        <div className={styles.featureCard__icon}>{icon}</div>
        <h3 className={styles.featureCard__title}>{title}</h3>
        <p className={styles.featureCard__description}>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <div className="text--center">
              <h2>Key Features</h2>
              <p>Everything you need for a production-ready AI automation system</p>
            </div>
          </div>
        </div>
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

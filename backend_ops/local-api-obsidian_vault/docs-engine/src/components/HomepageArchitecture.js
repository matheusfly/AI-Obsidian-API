import React from 'react';
import styles from '../pages/styles/index.module.css';

const HomepageArchitecture = () => {
  const architectureComponents = [
    {
      icon: '🔧',
      title: 'Core Services',
      description: 'FastAPI backend, Obsidian API, and n8n workflow automation',
      technologies: ['FastAPI', 'Node.js', 'n8n', 'Docker']
    },
    {
      icon: '🤖',
      title: 'AI & ML Ops',
      description: 'Enhanced RAG, AI agents, and Supabase integration',
      technologies: ['OpenAI', 'Supabase', 'ChromaDB', 'Ollama']
    },
    {
      icon: '📊',
      title: 'Observability',
      description: 'Advanced monitoring with Prometheus, Grafana, and tracing',
      technologies: ['Prometheus', 'Grafana', 'LangSmith', 'Sentry']
    },
    {
      icon: '🔗',
      title: 'MCP Integration',
      description: 'Model Context Protocol tools for enhanced AI capabilities',
      technologies: ['MCP', 'Context7', 'ByteRover', 'Playwright']
    },
    {
      icon: '🚀',
      title: 'CI/CD Pipeline',
      description: 'Automated testing, deployment, and quality assurance',
      technologies: ['GitHub Actions', 'Docker', 'UV', 'Pytest']
    },
    {
      icon: '🛡️',
      title: 'Security',
      description: 'Production-ready security with authentication and encryption',
      technologies: ['JWT', 'OAuth2', 'HTTPS', 'Rate Limiting']
    }
  ];

  return (
    <section className={styles.architectureSection}>
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <div className="text--center">
              <h2>System Architecture</h2>
              <p>Comprehensive backend engineering solution with modern technologies</p>
            </div>
          </div>
        </div>
        <div className={styles.architectureGrid}>
          {architectureComponents.map((component, idx) => (
            <div key={idx} className={styles.architectureCard}>
              <h3 className={styles.architectureCard__title}>
                <span className={styles.architectureCard__icon}>{component.icon}</span>
                {component.title}
              </h3>
              <p className={styles.architectureCard__description}>
                {component.description}
              </p>
              <div className={styles.architectureCard__tech}>
                {component.technologies.map((tech, techIdx) => (
                  <span key={techIdx} className={styles.techTag}>
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HomepageArchitecture;

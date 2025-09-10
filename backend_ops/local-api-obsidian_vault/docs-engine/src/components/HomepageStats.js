import React from 'react';
import styles from '../pages/styles/index.module.css';

const HomepageStats = () => {
  const stats = [
    {
      number: '15+',
      label: 'Microservices',
      description: 'Containerized services for scalability'
    },
    {
      number: '50+',
      label: 'API Endpoints',
      description: 'RESTful APIs with OpenAPI documentation'
    },
    {
      number: '10+',
      label: 'MCP Tools',
      description: 'Model Context Protocol integrations'
    },
    {
      number: '99.9%',
      label: 'Uptime',
      description: 'Production-ready reliability'
    },
    {
      number: '24/7',
      label: 'Monitoring',
      description: 'Advanced observability and alerting'
    },
    {
      number: '100%',
      label: 'Open Source',
      description: 'MIT licensed and community driven'
    }
  ];

  return (
    <section className={styles.statsSection}>
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <div className="text--center">
              <h2>System Statistics</h2>
              <p>Production-ready metrics and performance indicators</p>
            </div>
          </div>
        </div>
        <div className={styles.statsGrid}>
          {stats.map((stat, idx) => (
            <div key={idx} className={styles.statCard}>
              <span className={styles.statNumber}>{stat.number}</span>
              <div className={styles.statLabel}>{stat.label}</div>
              <p style={{ fontSize: '0.9rem', color: 'var(--ifm-font-color-secondary)', marginTop: '0.5rem' }}>
                {stat.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HomepageStats;

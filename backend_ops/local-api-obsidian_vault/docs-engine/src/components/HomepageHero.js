import React from 'react';
import clsx from 'clsx';
import styles from '../pages/styles/index.module.css';

const HomepageHero = () => {
  return (
    <section className={styles.heroBanner}>
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <div className="text--center">
              <h1 className="hero__title">
                🚀 Obsidian Vault AI Automation System
              </h1>
              <p className="hero__subtitle">
                Complete Backend Engineering Solution for AI-Powered Obsidian Vault Automation
                with FastAPI, Docker, MCP Tools, and Advanced Observability
              </p>
              <div className={styles.buttons}>
                <a
                  className="button button--secondary button--lg"
                  href="/docs/getting-started/installation">
                  🚀 Get Started - 5min ⏱️
                </a>
                <a
                  className="button button--outline button--lg"
                  href="/docs/api/overview">
                  📚 API Reference
                </a>
                <a
                  className="button button--outline button--lg"
                  href="https://github.com/your-org/obsidian-vault-ai-system">
                  ⭐ Star on GitHub
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HomepageHero;

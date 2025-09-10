import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import HomepageHero from '@site/src/components/HomepageHero';
import HomepageStats from '@site/src/components/HomepageStats';
import HomepageArchitecture from '@site/src/components/HomepageArchitecture';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">
          {siteConfig.title}
        </h1>
        <p className="hero__subtitle">
          {siteConfig.tagline}
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg visual-button"
            to="/docs/getting-started/installation">
            Get Started - 5min ⏱️
          </Link>
          <Link
            className="button button--outline button--lg visual-button"
            to="/docs/api/overview">
            API Reference 📚
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title} - Complete Backend Engineering Solution`}
      description="AI-Powered Obsidian Vault Automation System with FastAPI, Docker, MCP Tools, and Advanced Observability">
      <HomepageHeader />
      <main>
        <HomepageHero />
        <HomepageStats />
        <HomepageArchitecture />
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
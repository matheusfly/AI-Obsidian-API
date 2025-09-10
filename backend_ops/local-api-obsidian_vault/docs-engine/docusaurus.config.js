// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Obsidian Vault AI Automation System',
  tagline: 'Complete Backend Engineering Solution for AI-Powered Obsidian Vault Automation',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://your-docs-site.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/',

  // GitHub pages deployment config
  organizationName: 'your-org',
  projectName: 'obsidian-vault-ai-system',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'pt'],
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
        htmlLang: 'en-US',
        calendar: 'gregory',
      },
      pt: {
        label: 'Português',
        direction: 'ltr',
        htmlLang: 'pt-BR',
        calendar: 'gregory',
      },
    },
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/your-org/obsidian-vault-ai-system/tree/main/docs-engine/',
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
          remarkPlugins: [
            [require('@docusaurus/remark-plugin-npm2yarn'), {sync: true}],
          ],
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/your-org/obsidian-vault-ai-system/tree/main/docs-engine/blog/',
          blogSidebarCount: 10,
          blogSidebarTitle: 'Recent Posts',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
        sitemap: {
          changefreq: 'weekly',
          priority: 0.5,
          ignorePatterns: ['/tags/**'],
        },
        googleAnalytics: {
          trackingID: 'G-XXXXXXXXXX',
          anonymizeIP: true,
        },
        gtag: {
          trackingID: 'G-XXXXXXXXXX',
          anonymizeIP: true,
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/social-card.jpg',
      navbar: {
        title: 'Obsidian Vault AI System',
        logo: {
          alt: 'Obsidian Vault AI System Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            type: 'docSidebar',
            sidebarId: 'apiSidebar',
            position: 'left',
            label: 'API Reference',
          },
          {
            type: 'docSidebar',
            sidebarId: 'architectureSidebar',
            position: 'left',
            label: 'Architecture',
          },
          {
            type: 'docSidebar',
            sidebarId: 'deploymentSidebar',
            position: 'left',
            label: 'Deployment',
          },
          {
            to: '/blog',
            label: 'Blog',
            position: 'left'
          },
          {
            type: 'search',
            position: 'right',
          },
          {
            type: 'localeDropdown',
            position: 'right',
          },
          {
            href: 'https://github.com/your-org/obsidian-vault-ai-system',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Getting Started',
                to: '/docs/getting-started',
              },
              {
                label: 'API Reference',
                to: '/docs/api/overview',
              },
              {
                label: 'Architecture',
                to: '/docs/architecture/overview',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Discord',
                href: 'https://discord.gg/your-discord',
              },
              {
                label: 'GitHub Discussions',
                href: 'https://github.com/your-org/obsidian-vault-ai-system/discussions',
              },
              {
                label: 'Stack Overflow',
                href: 'https://stackoverflow.com/questions/tagged/obsidian-vault-ai',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
              {
                label: 'Changelog',
                to: '/docs/changelog',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/your-org/obsidian-vault-ai-system',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Obsidian Vault AI System. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['powershell', 'yaml', 'json', 'bash'],
      },
      algolia: {
        appId: 'YOUR_APP_ID',
        apiKey: 'YOUR_SEARCH_API_KEY',
        indexName: 'obsidian-vault-ai',
        contextualSearch: true,
        searchParameters: {},
        searchPagePath: 'search',
      },
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      announcementBar: {
        id: 'support_us',
        content:
          '⭐️ If you like this project, give it a star on <a target="_blank" rel="noopener noreferrer" href="https://github.com/your-org/obsidian-vault-ai-system">GitHub</a> and follow us on Twitter!',
        backgroundColor: '#fafbfc',
        textColor: '#091E42',
        isCloseable: true,
      },
      tableOfContents: {
        minHeadingLevel: 2,
        maxHeadingLevel: 5,
      },
      mermaid: {
        theme: 'dark',
        themeVariables: {
          primaryColor: '#25c2a0',
          primaryTextColor: '#ffffff',
          primaryBorderColor: '#29d5b0',
          lineColor: '#25c2a0',
          secondaryColor: '#1a1a1a',
          tertiaryColor: '#2a2a2a',
          background: '#0a0a0a',
          mainBkg: '#1a1a1a',
          secondBkg: '#2a2a2a',
          tertiaryBkg: '#0a0a0a',
          nodeTextColor: '#ffffff',
          clusterBkg: '#1a1a1a',
          clusterBorder: '#25c2a0',
          defaultLinkColor: '#25c2a0',
          titleColor: '#ffffff',
          edgeLabelBackground: '#1a1a1a',
          actorBkg: '#1a1a1a',
          actorBorder: '#25c2a0',
          actorTextColor: '#ffffff',
          actorLineColor: '#25c2a0',
          signalColor: '#25c2a0',
          signalTextColor: '#ffffff',
          labelBoxBkgColor: '#1a1a1a',
          labelBoxBorderColor: '#25c2a0',
          labelTextColor: '#ffffff',
          loopTextColor: '#ffffff',
          activationBkgColor: '#25c2a0',
          activationBorderColor: '#29d5b0',
          sequenceNumberColor: '#ffffff',
          section0: '#1a1a1a',
          section1: '#2a2a2a',
          section2: '#1a1a1a',
          section3: '#2a2a2a',
          altSection: '#1a1a1a',
          gridColor: '#404040',
          todayLineColor: '#25c2a0',
          taskBkgColor: '#25c2a0',
          taskTextColor: '#ffffff',
          taskTextLightColor: '#ffffff',
          taskTextOutsideColor: '#ffffff',
          taskTextClickableColor: '#29d5b0',
          activeTaskBkgColor: '#29d5b0',
          activeTaskBorderColor: '#4fddbf'
        }
      },
    }),

  plugins: [
    [
      '@docusaurus/plugin-ideal-image',
      {
        quality: 70,
        max: 1030,
        min: 640,
        steps: 2,
        disableInDev: false,
      },
    ],
    [
      '@docusaurus/plugin-pwa',
      {
        debug: true,
        offlineModeActivationStrategies: [
          'appInstalled',
          'standalone',
          'queryString',
        ],
        pwaHead: [
          {
            tagName: 'link',
            rel: 'icon',
            href: '/img/logo.svg',
          },
          {
            tagName: 'link',
            rel: 'manifest',
            href: '/manifest.json',
          },
          {
            tagName: 'meta',
            name: 'theme-color',
            content: 'rgb(37, 194, 160)',
          },
        ],
      },
    ],
    '@docusaurus/theme-live-codeblock',
    '@docusaurus/plugin-sitemap',
    '@docusaurus/plugin-client-redirects',
    '@docusaurus/plugin-debug',
  ],

  themes: ['@docusaurus/theme-mermaid'],

  markdown: {
    mermaid: true,
  },

};

module.exports = config;

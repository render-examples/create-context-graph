import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Create Context Graph',
  tagline: 'AI agents with graph memory, scaffolded in seconds',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://create-context-graph.vercel.app',
  baseUrl: '/',

  organizationName: 'neo4j-labs',
  projectName: 'create-context-graph',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/neo4j-labs/create-context-graph/tree/main/docs/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Create Context Graph',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://github.com/neo4j-labs/create-context-graph',
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
            {label: 'Getting Started', to: '/docs/intro'},
            {label: 'CLI Reference', to: '/docs/reference/cli-options'},
            {label: 'YAML Schema', to: '/docs/reference/ontology-yaml-schema'},
          ],
        },
        {
          title: 'Community',
          items: [
            {label: 'Neo4j Community Forum', href: 'https://community.neo4j.com/'},
            {label: 'GitHub Issues', href: 'https://github.com/neo4j-labs/create-context-graph/issues'},
          ],
        },
        {
          title: 'More',
          items: [
            {label: 'Neo4j Labs', href: 'https://neo4j.com/labs/'},
            {label: 'neo4j-agent-memory', href: 'https://github.com/neo4j-labs/agent-memory'},
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} Neo4j Labs. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'yaml', 'toml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;

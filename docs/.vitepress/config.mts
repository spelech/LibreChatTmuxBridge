import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(
  defineConfig({
    title: 'LibreChatTmuxBridge',
    description: 'Universal Bidirectional Bridge between LibreChat and Host tmux Multiplexers',
    base: process.env.VITEPRESS_BASE || '/LibreChatTmuxBridge/',
    ignoreDeadLinks: true,
    themeConfig: {
      nav: [
        { text: 'Overview', link: '/' },
        { text: 'Guide', link: '/guide/getting-started' },
        { text: 'Architecture', link: '/architecture/overview' },
        { text: 'Reference', link: '/reference/openai-api' },
        { text: 'GitHub', link: 'https://github.com/spelech/LibreChatTmuxBridge' }
      ],
      sidebar: {
        '/guide/': [
          {
            text: 'User & Setup Guide',
            items: [
              { text: 'Getting Started', link: '/guide/getting-started' },
              { text: 'LibreChat Integration', link: '/guide/librechat-setup' },
              { text: 'Slash Commands & Prompts', link: '/guide/slash-commands' },
              { text: 'Mobile TUI Experience', link: '/guide/mobile-experience' },
              { text: 'Desktop SSH Parity', link: '/guide/desktop-ssh' }
            ]
          }
        ],
        '/architecture/': [
          {
            text: 'System Architecture',
            items: [
              { text: 'Architectural Overview', link: '/architecture/overview' },
              { text: 'TUI Translation Pipeline', link: '/architecture/translation-pipeline' },
              { text: 'Agentic MCP Copilot', link: '/architecture/mcp-copilot' }
            ]
          }
        ],
        '/reference/': [
          {
            text: 'Technical Reference',
            items: [
              { text: 'OpenAI Compatibility API', link: '/reference/openai-api' },
              { text: 'FastMCP Tools Schema', link: '/reference/mcp-tools' },
              { text: 'Configuration & CLI', link: '/reference/configuration' },
              { text: 'Troubleshooting & FAQ', link: '/reference/troubleshooting' }
            ]
          }
        ]
      },
      socialLinks: [
        { icon: 'github', link: 'https://github.com/spelech/LibreChatTmuxBridge' }
      ],
      footer: {
        message: 'Released under the MIT License.',
        copyright: 'Copyright © 2026 Steven T. Pelech'
      }
    }
  })
)

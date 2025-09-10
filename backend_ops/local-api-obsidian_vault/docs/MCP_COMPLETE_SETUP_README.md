# 🚀 Complete MCP Tools Setup for Cursor & Warp

This repository contains a comprehensive setup for Model Context Protocol (MCP) tools that can be used with both Cursor IDE and Warp terminal.

## 📋 What's Included

### Core MCP Tools
- **Filesystem**: File operations (read, write, list, search)
- **GitHub**: Repository management and code access
- **SQLite**: Database operations
- **PostgreSQL**: Advanced database operations
- **Brave Search**: Web search capabilities
- **Playwright**: Browser automation and testing
- **Context7**: Documentation and context management
- **Shadcn UI**: UI component management
- **Byterover**: Advanced context engineering
- **Sequential Thinking**: Structured reasoning
- **Web Search**: General web search capabilities
- **Memory**: Persistent memory storage

### Custom MCP Servers
- **Graphiti**: Real-time knowledge graphs for AI agents
- **Aipotheosis ACI**: AI agent management and workflow automation
- **Obsidian Vault**: Complete Obsidian vault operations

## 🛠️ Quick Setup

### 1. Run the Setup Script
```powershell
.\setup-mcp-tools.ps1
```

This will:
- Install all required Node.js packages
- Create necessary directories
- Generate configuration files
- Set up custom MCP servers

### 2. Configure API Keys
Update the following in `mcp-env-template.txt`:
- GitHub Personal Access Token
- Brave Search API Key
- Context7 API Key
- Byterover API Key
- SERP API Key

### 3. Setup Cursor IDE
1. Open Cursor Settings
2. Go to Tools & Integrations
3. Add Custom MCP
4. Copy contents from `cursor-mcp-config.json`

### 4. Setup Warp Terminal
1. Open Warp Settings (Cmd+,)
2. Go to AI > Manage MCP Servers
3. Import configuration from `WARP_MCP_CONFIG_PASTE_READY.json`

## 🎯 Warp Configuration (Copy & Paste Ready)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "D:\\codex\\master_code\\backend_ops\\local-api-obsidian_vault"],
      "env": {
        "NODE_ENV": "development"
      },
      "start_on_launch": true
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_TOKEN_HERE"
      },
      "start_on_launch": true
    },
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "D:\\codex\\master_code\\backend_ops\\local-api-obsidian_vault\\data\\vault.db"],
      "start_on_launch": true
    },
    "postgres": {
      "command": "uvx",
      "args": ["mcp-server-postgres", "--connection-string", "postgresql://localhost:5432/vault_db"],
      "start_on_launch": true
    },
    "brave-search": {
      "command": "uvx",
      "args": ["mcp-server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "YOUR_BRAVE_API_KEY_HERE"
      },
      "start_on_launch": true
    },
    "playwright": {
      "command": "uvx",
      "args": ["mcp-server-playwright"],
      "start_on_launch": true
    },
    "context7": {
      "command": "uvx",
      "args": ["mcp-server-context7"],
      "env": {
        "CONTEXT7_API_KEY": "YOUR_CONTEXT7_API_KEY_HERE"
      },
      "start_on_launch": true
    },
    "shadcn-ui": {
      "command": "uvx",
      "args": ["mcp-server-shadcn-ui"],
      "start_on_launch": true
    },
    "byterover": {
      "command": "uvx",
      "args": ["mcp-server-byterover"],
      "env": {
        "BYTEROVER_API_KEY": "YOUR_BYTEROVER_API_KEY_HERE"
      },
      "start_on_launch": true
    },
    "sequential-thinking": {
      "command": "uvx",
      "args": ["mcp-server-sequential-thinking"],
      "start_on_launch": true
    },
    "graphiti": {
      "command": "node",
      "args": ["D:\\codex\\master_code\\backend_ops\\local-api-obsidian_vault\\graphiti-server\\index.js"],
      "env": {
        "OPENAI_API_KEY": "$env:OPENAI_API_KEY",
        "ACI_KEY": "$env:ACI_KEY"
      },
      "start_on_launch": true
    },
    "aipotheosis-aci": {
      "command": "node",
      "args": ["D:\\codex\\master_code\\backend_ops\\local-api-obsidian_vault\\aci-server\\index.js"],
      "env": {
        "OPENAI_API_KEY": "$env:OPENAI_API_KEY",
        "ACI_KEY": "$env:ACI_KEY"
      },
      "start_on_launch": true
    },
    "obsidian-vault": {
      "command": "node",
      "args": ["D:\\codex\\master_code\\backend_ops\\local-api-obsidian_vault\\obsidian-mcp-server\\index.js"],
      "env": {
        "VAULT_PATH": "D:\\Nomade Milionario",
        "OPENAI_API_KEY": "$env:OPENAI_API_KEY"
      },
      "start_on_launch": true
    },
    "web-search": {
      "command": "uvx",
      "args": ["mcp-server-web-search"],
      "env": {
        "SERP_API_KEY": "YOUR_SERP_API_KEY_HERE"
      },
      "start_on_launch": true
    },
    "memory": {
      "command": "uvx",
      "args": ["mcp-server-memory"],
      "env": {
        "MEMORY_DB_PATH": "D:\\codex\\master_code\\backend_ops\\local-api-obsidian_vault\\memory.db"
      },
      "start_on_launch": true
    }
  }
}
```

## 🧪 Testing Your Setup

Run the test script to verify everything is working:
```powershell
.\test-mcp-tools.ps1
```

## 📖 Usage Examples

### Graphiti - Knowledge Graphs
```javascript
// Create a knowledge graph
await mcp.callTool('create_knowledge_graph', {
  content: 'AI and machine learning are transforming software development',
  graph_name: 'ai-concepts',
  options: {
    real_time: true,
    persist: true
  }
});

// Query the knowledge graph
await mcp.callTool('query_knowledge_graph', {
  graph_name: 'ai-concepts',
  query: 'machine learning applications',
  limit: 5
});
```

### ACI - AI Agent Management
```javascript
// Create an AI agent
await mcp.callTool('create_agent', {
  name: 'Code Assistant',
  description: 'Helps with code generation and review',
  capabilities: ['code_generation', 'text_generation'],
  model: 'gpt-4',
  temperature: 0.7
});

// Execute a task with the agent
await mcp.callTool('execute_agent_task', {
  agent_id: 'agent_123',
  task: 'Generate a React component for user authentication',
  context: {
    framework: 'React',
    styling: 'Tailwind CSS'
  }
});
```

### Obsidian Vault Operations
```javascript
// Read a note
await mcp.callTool('read_note', {
  note_path: 'notes/my-note.md'
});

// Search notes
await mcp.callTool('search_notes', {
  query: 'machine learning',
  include_content: true,
  case_sensitive: false
});

// Create a new note
await mcp.callTool('create_note', {
  note_path: 'notes/new-note.md',
  title: 'My New Note',
  content: 'This is the content of my new note.',
  tags: ['ai', 'machine-learning'],
  frontmatter: {
    author: 'Your Name',
    date: '2024-01-01'
  }
});
```

## 🔧 Custom MCP Servers

### Graphiti Server
- **Purpose**: Real-time knowledge graphs for AI agents
- **Location**: `graphiti-server/`
- **Features**: Create, query, update, and manage knowledge graphs

### ACI Server
- **Purpose**: AI agent management and workflow automation
- **Location**: `aci-server/`
- **Features**: Create agents, execute tasks, manage workflows

### Obsidian Vault Server
- **Purpose**: Complete Obsidian vault operations
- **Location**: `obsidian-mcp-server/`
- **Features**: Read, write, search, analyze notes

## 🔑 Required API Keys

| Service | Key | Where to Get |
|---------|-----|--------------|
| OpenAI | Already configured | https://openai.com/api/ |
| GitHub | Personal Access Token | https://github.com/settings/tokens |
| Brave Search | API Key | https://brave.com/search/api/ |
| Context7 | API Key | https://context7.ai/ |
| Byterover | API Key | https://byterover.com/ |
| SERP | API Key | https://serpapi.com/ |

## 🆘 Troubleshooting

### Common Issues

1. **Node.js not found**
   - Install Node.js from https://nodejs.org/
   - Ensure it's added to your PATH

2. **Permission errors**
   - Run PowerShell as Administrator
   - Check file permissions

3. **MCP server not starting**
   - Check the logs in Warp's MCP servers page
   - Verify the server paths are correct

4. **API key errors**
   - Verify your API keys are correct
   - Check that keys have proper permissions

### Debug Commands

```powershell
# Test individual servers
node graphiti-server/index.js --test
node aci-server/index.js --test
node obsidian-mcp-server/index.js --test

# Check Node.js version
node --version

# Check npm version
npm --version
```

## 📚 Additional Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Graphiti Repository](https://github.com/getzep/graphiti)
- [Aipotheosis Labs ACI](https://github.com/aipotheosis-labs/aci)
- [Warp MCP Documentation](https://docs.warp.dev/knowledge-and-collaboration/mcp)
- [Cursor MCP Integration](https://cursor.sh/docs)

## 🎉 You're All Set!

Once you've completed the setup, you'll have access to a comprehensive suite of MCP tools that can:

- Manage files and databases
- Search the web and documentation
- Create and manage AI agents
- Build knowledge graphs
- Operate on your Obsidian vault
- And much more!

Happy coding with MCP tools! 🚀

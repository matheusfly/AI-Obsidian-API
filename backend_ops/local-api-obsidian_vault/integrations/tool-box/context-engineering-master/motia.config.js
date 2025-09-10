/** @type {import('motia').Config} */
export default {
  // Project configuration
  name: "context-engineering-master",
  version: "1.0.0",
  
  // Language support
  languages: ["typescript", "python", "javascript"],
  
  // Steps configuration
  steps: {
    // API Steps
    api: {
      port: 3000,
      cors: {
        origin: ["http://localhost:3000", "http://localhost:5173"],
        credentials: true
      },
      rateLimit: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        max: 1000 // limit each IP to 1000 requests per windowMs
      }
    },
    
    // Event Steps
    event: {
      redis: {
        host: process.env.REDIS_HOST || "localhost",
        port: process.env.REDIS_PORT || 6379,
        password: process.env.REDIS_PASSWORD
      },
      topics: [
        "context-updates",
        "tool-executions", 
        "ai-agent-communications",
        "knowledge-extractions"
      ]
    },
    
    // Cron Steps
    cron: {
      timezone: "UTC",
      jobs: [
        {
          name: "knowledge-sync",
          schedule: "0 */6 * * *", // Every 6 hours
          step: "sync-knowledge"
        },
        {
          name: "performance-cleanup",
          schedule: "0 2 * * *", // Daily at 2 AM
          step: "cleanup-performance-data"
        }
      ]
    }
  },
  
  // AI Agent configuration
  ai: {
    providers: {
      openai: {
        apiKey: process.env.OPENAI_API_KEY,
        model: "gpt-4-turbo-preview"
      },
      anthropic: {
        apiKey: process.env.ANTHROPIC_API_KEY,
        model: "claude-3-sonnet-20240229"
      },
      gemini: {
        apiKey: process.env.GEMINI_API_KEY,
        model: "gemini-pro"
      }
    },
    mcp: {
      servers: [
        {
          name: "context7-mcp",
          port: 8004,
          functions: [
            "store_context",
            "retrieve_context", 
            "search_context",
            "update_context"
          ]
        },
        {
          name: "chartdb-mcp",
          port: 8003,
          functions: [
            "scrape_chartdb",
            "extract_database_diagrams",
            "extract_templates",
            "analyze_database_schema"
          ]
        },
        {
          name: "motia-docs-mcp",
          port: 8005,
          functions: [
            "scrape_motia_docs",
            "extract_api_examples",
            "analyze_workflow_patterns"
          ]
        }
      ]
    }
  },
  
  // Database configuration
  database: {
    primary: {
      type: "postgresql",
      url: process.env.DATABASE_URL || "postgresql://localhost:5432/context_engineering"
    },
    cache: {
      type: "redis",
      url: process.env.REDIS_URL || "redis://localhost:6379"
    }
  },
  
  // Monitoring and observability
  monitoring: {
    enabled: true,
    metrics: {
      prometheus: {
        enabled: true,
        port: 9090
      }
    },
    logging: {
      level: "info",
      format: "json"
    },
    tracing: {
      enabled: true,
      jaeger: {
        endpoint: process.env.JAEGER_ENDPOINT || "http://localhost:14268/api/traces"
      }
    }
  },
  
  // Development configuration
  development: {
    hotReload: true,
    debugMode: true,
    workbench: {
      enabled: true,
      port: 3001
    }
  },
  
  // Production configuration
  production: {
    minify: true,
    compression: true,
    security: {
      helmet: true,
      rateLimit: true
    }
  }
};

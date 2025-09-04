import { Step } from "motia";
import { z } from "zod";

// Input validation schema
const HelloWorldInput = z.object({
  name: z.string().min(1).max(100),
  language: z.enum(["typescript", "python", "javascript"]).optional(),
  context: z.string().optional()
});

// Output validation schema
const HelloWorldOutput = z.object({
  message: z.string(),
  timestamp: z.string(),
  context: z.object({
    compressedKnowledge: z.array(z.string()),
    toolIntegrations: z.array(z.string()),
    aiCapabilities: z.array(z.string())
  }),
  metadata: z.object({
    stepId: z.string(),
    executionTime: z.number(),
    version: z.string()
  })
});

export const helloWorldAPI = new Step({
  id: "hello-world-api",
  type: "api",
  method: "POST",
  path: "/hello-world",
  description: "Interactive Hello World API with Context Engineering",
  
  input: HelloWorldInput,
  output: HelloWorldOutput,
  
  async execute({ input, context, metadata }) {
    const startTime = Date.now();
    
    // Compressed knowledge from tool-box
    const compressedKnowledge = [
      "Motia: Unified backend framework for APIs, events, and AI agents",
      "Flyde: Visual programming for complex workflows", 
      "MCP: Model Context Protocol for AI agent communication",
      "ChartDB: Database diagram and schema visualization",
      "Context7: Persistent knowledge storage and retrieval",
      "Documentation Scrapers: Advanced web scraping with MCP integration",
      "Visual Tools: Interactive web UI for tool orchestration"
    ];
    
    // Tool integrations available
    const toolIntegrations = [
      "Motia Docs Scraper",
      "ChartDB Documentation Scraper", 
      "Context7 Memory System",
      "Flyde Visual Flows",
      "MCP Server Network",
      "Interactive Web UI",
      "Performance Monitoring"
    ];
    
    // AI capabilities
    const aiCapabilities = [
      "Context-aware responses",
      "Knowledge compression and extraction",
      "Multi-agent coordination",
      "Real-time learning and adaptation",
      "Semantic search and retrieval",
      "Automated workflow generation"
    ];
    
    // Generate personalized message
    const personalizedMessage = `Hello ${input.name}! Welcome to the Context Engineering Master system powered by Motia. 
    
    You're now connected to a unified backend framework that compresses all our tool-box knowledge into a single, 
    coherent system. This system integrates APIs, background jobs, workflows, and AI agents with built-in 
    observability and state management.
    
    Language: ${input.language || 'typescript'}
    Context: ${input.context || 'Interactive Hello World Demo'}
    
    The system is ready to help you build, deploy, and manage complex applications with the power of 
    context engineering and visual programming.`;
    
    const executionTime = Date.now() - startTime;
    
    return {
      message: personalizedMessage,
      timestamp: new Date().toISOString(),
      context: {
        compressedKnowledge,
        toolIntegrations,
        aiCapabilities
      },
      metadata: {
        stepId: metadata.stepId,
        executionTime,
        version: "1.0.0"
      }
    };
  }
});

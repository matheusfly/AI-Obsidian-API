#!/usr/bin/env node

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');

class ACIMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'aipotheosis-aci-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.apiKey = process.env.ACI_KEY;
    this.openaiApiKey = process.env.OPENAI_API_KEY;
    this.baseUrl = 'https://api.aipotheosis-labs.com';

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'create_agent',
            description: 'Create a new AI agent with specific capabilities',
            inputSchema: {
              type: 'object',
              properties: {
                name: {
                  type: 'string',
                  description: 'Name of the agent',
                },
                description: {
                  type: 'string',
                  description: 'Description of the agent\'s purpose',
                },
                capabilities: {
                  type: 'array',
                  items: {
                    type: 'string',
                    enum: ['text_generation', 'code_generation', 'data_analysis', 'web_search', 'file_processing', 'api_integration'],
                  },
                  description: 'List of agent capabilities',
                },
                model: {
                  type: 'string',
                  description: 'AI model to use',
                  default: 'gpt-4',
                },
                temperature: {
                  type: 'number',
                  description: 'Temperature for response generation',
                  default: 0.7,
                },
              },
              required: ['name', 'description', 'capabilities'],
            },
          },
          {
            name: 'execute_agent_task',
            description: 'Execute a task using a specific agent',
            inputSchema: {
              type: 'object',
              properties: {
                agent_id: {
                  type: 'string',
                  description: 'ID of the agent to use',
                },
                task: {
                  type: 'string',
                  description: 'Task description',
                },
                context: {
                  type: 'object',
                  description: 'Additional context for the task',
                },
                max_tokens: {
                  type: 'number',
                  description: 'Maximum tokens for response',
                  default: 2000,
                },
              },
              required: ['agent_id', 'task'],
            },
          },
          {
            name: 'list_agents',
            description: 'List all available agents',
            inputSchema: {
              type: 'object',
              properties: {
                include_status: {
                  type: 'boolean',
                  description: 'Include agent status information',
                  default: true,
                },
              },
            },
          },
          {
            name: 'update_agent',
            description: 'Update an existing agent configuration',
            inputSchema: {
              type: 'object',
              properties: {
                agent_id: {
                  type: 'string',
                  description: 'ID of the agent to update',
                },
                updates: {
                  type: 'object',
                  properties: {
                    name: { type: 'string' },
                    description: { type: 'string' },
                    capabilities: { type: 'array', items: { type: 'string' } },
                    model: { type: 'string' },
                    temperature: { type: 'number' },
                  },
                  description: 'Fields to update',
                },
              },
              required: ['agent_id', 'updates'],
            },
          },
          {
            name: 'delete_agent',
            description: 'Delete an agent',
            inputSchema: {
              type: 'object',
              properties: {
                agent_id: {
                  type: 'string',
                  description: 'ID of the agent to delete',
                },
                confirm: {
                  type: 'boolean',
                  description: 'Confirmation flag',
                  default: false,
                },
              },
              required: ['agent_id'],
            },
          },
          {
            name: 'get_agent_status',
            description: 'Get the status and performance metrics of an agent',
            inputSchema: {
              type: 'object',
              properties: {
                agent_id: {
                  type: 'string',
                  description: 'ID of the agent',
                },
              },
              required: ['agent_id'],
            },
          },
          {
            name: 'create_workflow',
            description: 'Create a multi-agent workflow',
            inputSchema: {
              type: 'object',
              properties: {
                name: {
                  type: 'string',
                  description: 'Name of the workflow',
                },
                description: {
                  type: 'string',
                  description: 'Description of the workflow',
                },
                steps: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      agent_id: { type: 'string' },
                      task: { type: 'string' },
                      dependencies: { type: 'array', items: { type: 'string' } },
                    },
                    required: ['agent_id', 'task'],
                  },
                  description: 'Workflow steps',
                },
              },
              required: ['name', 'description', 'steps'],
            },
          },
          {
            name: 'execute_workflow',
            description: 'Execute a multi-agent workflow',
            inputSchema: {
              type: 'object',
              properties: {
                workflow_id: {
                  type: 'string',
                  description: 'ID of the workflow to execute',
                },
                input_data: {
                  type: 'object',
                  description: 'Input data for the workflow',
                },
              },
              required: ['workflow_id'],
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'create_agent':
            return await this.createAgent(args);
          case 'execute_agent_task':
            return await this.executeAgentTask(args);
          case 'list_agents':
            return await this.listAgents(args);
          case 'update_agent':
            return await this.updateAgent(args);
          case 'delete_agent':
            return await this.deleteAgent(args);
          case 'get_agent_status':
            return await this.getAgentStatus(args);
          case 'create_workflow':
            return await this.createWorkflow(args);
          case 'execute_workflow':
            return await this.executeWorkflow(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async createAgent(args) {
    const { name, description, capabilities, model = 'gpt-4', temperature = 0.7 } = args;
    
    // Simulate agent creation
    const agentId = `agent_${Date.now()}`;
    const agent = {
      id: agentId,
      name,
      description,
      capabilities,
      model,
      temperature,
      created_at: new Date().toISOString(),
      status: 'active',
      tasks_completed: 0,
      last_used: null,
    };

    // Store in memory (in production, use proper storage)
    if (!this.agents) this.agents = new Map();
    this.agents.set(agentId, agent);

    return {
      content: [
        {
          type: 'text',
          text: `Agent "${name}" created successfully!\n\n` +
                `Agent ID: ${agentId}\n` +
                `Description: ${description}\n` +
                `Capabilities: ${capabilities.join(', ')}\n` +
                `Model: ${model}\n` +
                `Temperature: ${temperature}\n` +
                `Status: ${agent.status}`,
        },
      ],
    };
  }

  async executeAgentTask(args) {
    const { agent_id, task, context = {}, max_tokens = 2000 } = args;
    
    if (!this.agents || !this.agents.has(agent_id)) {
      throw new Error(`Agent with ID "${agent_id}" not found`);
    }

    const agent = this.agents.get(agent_id);
    
    // Simulate task execution
    const taskId = `task_${Date.now()}`;
    const startTime = Date.now();
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
    
    const endTime = Date.now();
    const processingTime = endTime - startTime;
    
    // Generate simulated response based on agent capabilities
    let response = this.generateAgentResponse(agent, task, context);
    
    // Update agent statistics
    agent.tasks_completed++;
    agent.last_used = new Date().toISOString();
    this.agents.set(agent_id, agent);

    return {
      content: [
        {
          type: 'text',
          text: `Task executed successfully!\n\n` +
                `Agent: ${agent.name} (${agent_id})\n` +
                `Task: ${task}\n` +
                `Processing Time: ${processingTime}ms\n` +
                `Response:\n\n${response}\n\n` +
                `Agent Statistics:\n` +
                `- Total Tasks Completed: ${agent.tasks_completed}\n` +
                `- Last Used: ${agent.last_used}`,
        },
      ],
    };
  }

  async listAgents(args) {
    const { include_status = true } = args;
    
    if (!this.agents || this.agents.size === 0) {
      return {
        content: [
          {
            type: 'text',
            text: 'No agents found.',
          },
        ],
      };
    }

    const agents = Array.from(this.agents.values()).map(agent => {
      let info = `- ${agent.name} (ID: ${agent.id})\n  Description: ${agent.description}\n  Capabilities: ${agent.capabilities.join(', ')}`;
      
      if (include_status) {
        info += `\n  Status: ${agent.status}\n  Tasks Completed: ${agent.tasks_completed}`;
        if (agent.last_used) {
          info += `\n  Last Used: ${agent.last_used}`;
        }
      }
      
      return info;
    }).join('\n\n');

    return {
      content: [
        {
          type: 'text',
          text: `Available Agents:\n\n${agents}`,
        },
      ],
    };
  }

  async updateAgent(args) {
    const { agent_id, updates } = args;
    
    if (!this.agents || !this.agents.has(agent_id)) {
      throw new Error(`Agent with ID "${agent_id}" not found`);
    }

    const agent = this.agents.get(agent_id);
    
    // Apply updates
    Object.keys(updates).forEach(key => {
      if (updates[key] !== undefined) {
        agent[key] = updates[key];
      }
    });
    
    agent.updated_at = new Date().toISOString();
    this.agents.set(agent_id, agent);

    return {
      content: [
        {
          type: 'text',
          text: `Agent "${agent.name}" updated successfully!\n\n` +
                `Updated fields: ${Object.keys(updates).join(', ')}\n` +
                `Updated at: ${agent.updated_at}`,
        },
      ],
    };
  }

  async deleteAgent(args) {
    const { agent_id, confirm = false } = args;
    
    if (!confirm) {
      return {
        content: [
          {
            type: 'text',
            text: `To delete agent "${agent_id}", set confirm: true in the request.`,
          },
        ],
      };
    }

    if (!this.agents || !this.agents.has(agent_id)) {
      throw new Error(`Agent with ID "${agent_id}" not found`);
    }

    const agent = this.agents.get(agent_id);
    this.agents.delete(agent_id);

    return {
      content: [
        {
          type: 'text',
          text: `Agent "${agent.name}" (${agent_id}) deleted successfully.`,
        },
      ],
    };
  }

  async getAgentStatus(args) {
    const { agent_id } = args;
    
    if (!this.agents || !this.agents.has(agent_id)) {
      throw new Error(`Agent with ID "${agent_id}" not found`);
    }

    const agent = this.agents.get(agent_id);
    
    // Simulate performance metrics
    const uptime = Date.now() - new Date(agent.created_at).getTime();
    const avgResponseTime = 1500 + Math.random() * 1000; // Simulated
    const successRate = 0.85 + Math.random() * 0.1; // Simulated

    return {
      content: [
        {
          type: 'text',
          text: `Agent Status Report: ${agent.name}\n\n` +
                `Agent ID: ${agent_id}\n` +
                `Status: ${agent.status}\n` +
                `Created: ${agent.created_at}\n` +
                `Last Used: ${agent.last_used || 'Never'}\n\n` +
                `Performance Metrics:\n` +
                `- Uptime: ${Math.floor(uptime / (1000 * 60 * 60))} hours\n` +
                `- Tasks Completed: ${agent.tasks_completed}\n` +
                `- Average Response Time: ${Math.floor(avgResponseTime)}ms\n` +
                `- Success Rate: ${(successRate * 100).toFixed(1)}%\n\n` +
                `Configuration:\n` +
                `- Model: ${agent.model}\n` +
                `- Temperature: ${agent.temperature}\n` +
                `- Capabilities: ${agent.capabilities.join(', ')}`,
        },
      ],
    };
  }

  async createWorkflow(args) {
    const { name, description, steps } = args;
    
    const workflowId = `workflow_${Date.now()}`;
    const workflow = {
      id: workflowId,
      name,
      description,
      steps,
      created_at: new Date().toISOString(),
      executions: 0,
      last_executed: null,
    };

    // Store in memory (in production, use proper storage)
    if (!this.workflows) this.workflows = new Map();
    this.workflows.set(workflowId, workflow);

    return {
      content: [
        {
          type: 'text',
          text: `Workflow "${name}" created successfully!\n\n` +
                `Workflow ID: ${workflowId}\n` +
                `Description: ${description}\n` +
                `Steps: ${steps.length}\n` +
                `Created: ${workflow.created_at}`,
        },
      ],
    };
  }

  async executeWorkflow(args) {
    const { workflow_id, input_data = {} } = args;
    
    if (!this.workflows || !this.workflows.has(workflow_id)) {
      throw new Error(`Workflow with ID "${workflow_id}" not found`);
    }

    const workflow = this.workflows.get(workflow_id);
    const executionId = `exec_${Date.now()}`;
    const startTime = Date.now();
    
    // Simulate workflow execution
    const results = [];
    for (let i = 0; i < workflow.steps.length; i++) {
      const step = workflow.steps[i];
      const stepStartTime = Date.now();
      
      // Simulate step execution
      await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 1000));
      
      const stepEndTime = Date.now();
      const stepDuration = stepEndTime - stepStartTime;
      
      results.push({
        step: i + 1,
        agent_id: step.agent_id,
        task: step.task,
        duration: stepDuration,
        status: 'completed',
        result: `Step ${i + 1} completed successfully`,
      });
    }
    
    const endTime = Date.now();
    const totalDuration = endTime - startTime;
    
    // Update workflow statistics
    workflow.executions++;
    workflow.last_executed = new Date().toISOString();
    this.workflows.set(workflow_id, workflow);

    return {
      content: [
        {
          type: 'text',
          text: `Workflow "${workflow.name}" executed successfully!\n\n` +
                `Execution ID: ${executionId}\n` +
                `Total Duration: ${totalDuration}ms\n` +
                `Steps Completed: ${results.length}\n\n` +
                `Step Results:\n` +
                results.map((result, index) => 
                  `${index + 1}. Agent ${result.agent_id}: ${result.task}\n   Duration: ${result.duration}ms\n   Status: ${result.status}`
                ).join('\n\n') +
                `\n\nWorkflow Statistics:\n` +
                `- Total Executions: ${workflow.executions}\n` +
                `- Last Executed: ${workflow.last_executed}`,
        },
      ],
    };
  }

  generateAgentResponse(agent, task, context) {
    // Simulate response generation based on agent capabilities
    const responses = {
      text_generation: `I'll help you with text generation. For the task "${task}", I can create engaging and informative content.`,
      code_generation: `I'll assist with code generation. For the task "${task}", I can write clean, efficient code with proper documentation.`,
      data_analysis: `I'll perform data analysis. For the task "${task}", I can analyze patterns, create visualizations, and provide insights.`,
      web_search: `I'll conduct web research. For the task "${task}", I can search for relevant information and compile comprehensive results.`,
      file_processing: `I'll handle file processing. For the task "${task}", I can read, parse, and manipulate various file formats.`,
      api_integration: `I'll manage API integration. For the task "${task}", I can connect to external services and handle data exchange.`,
    };

    const primaryCapability = agent.capabilities[0];
    let response = responses[primaryCapability] || `I'll help you with the task "${task}".`;
    
    if (context && Object.keys(context).length > 0) {
      response += `\n\nContext provided: ${JSON.stringify(context, null, 2)}`;
    }
    
    return response;
  }

  setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error('[MCP Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('ACI MCP server running on stdio');
  }
}

const server = new ACIMCPServer();
server.run().catch(console.error);

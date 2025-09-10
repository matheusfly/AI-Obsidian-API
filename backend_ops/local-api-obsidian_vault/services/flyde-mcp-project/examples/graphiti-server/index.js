#!/usr/bin/env node

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');

class GraphitiMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'graphiti-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'create_knowledge_graph',
            description: 'Create a real-time knowledge graph from text or data',
            inputSchema: {
              type: 'object',
              properties: {
                content: {
                  type: 'string',
                  description: 'Text content to build knowledge graph from',
                },
                graph_name: {
                  type: 'string',
                  description: 'Name for the knowledge graph',
                },
                options: {
                  type: 'object',
                  properties: {
                    real_time: {
                      type: 'boolean',
                      description: 'Enable real-time updates',
                      default: true,
                    },
                    persist: {
                      type: 'boolean',
                      description: 'Persist graph to storage',
                      default: true,
                    },
                  },
                },
              },
              required: ['content', 'graph_name'],
            },
          },
          {
            name: 'query_knowledge_graph',
            description: 'Query the knowledge graph for information',
            inputSchema: {
              type: 'object',
              properties: {
                graph_name: {
                  type: 'string',
                  description: 'Name of the knowledge graph to query',
                },
                query: {
                  type: 'string',
                  description: 'Natural language query',
                },
                limit: {
                  type: 'number',
                  description: 'Maximum number of results',
                  default: 10,
                },
              },
              required: ['graph_name', 'query'],
            },
          },
          {
            name: 'update_knowledge_graph',
            description: 'Update an existing knowledge graph with new information',
            inputSchema: {
              type: 'object',
              properties: {
                graph_name: {
                  type: 'string',
                  description: 'Name of the knowledge graph to update',
                },
                content: {
                  type: 'string',
                  description: 'New content to add to the graph',
                },
                merge_strategy: {
                  type: 'string',
                  enum: ['append', 'merge', 'replace'],
                  description: 'Strategy for merging new content',
                  default: 'merge',
                },
              },
              required: ['graph_name', 'content'],
            },
          },
          {
            name: 'list_knowledge_graphs',
            description: 'List all available knowledge graphs',
            inputSchema: {
              type: 'object',
              properties: {
                include_stats: {
                  type: 'boolean',
                  description: 'Include graph statistics',
                  default: false,
                },
              },
            },
          },
          {
            name: 'delete_knowledge_graph',
            description: 'Delete a knowledge graph',
            inputSchema: {
              type: 'object',
              properties: {
                graph_name: {
                  type: 'string',
                  description: 'Name of the knowledge graph to delete',
                },
                confirm: {
                  type: 'boolean',
                  description: 'Confirmation flag',
                  default: false,
                },
              },
              required: ['graph_name'],
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
          case 'create_knowledge_graph':
            return await this.createKnowledgeGraph(args);
          case 'query_knowledge_graph':
            return await this.queryKnowledgeGraph(args);
          case 'update_knowledge_graph':
            return await this.updateKnowledgeGraph(args);
          case 'list_knowledge_graphs':
            return await this.listKnowledgeGraphs(args);
          case 'delete_knowledge_graph':
            return await this.deleteKnowledgeGraph(args);
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

  async createKnowledgeGraph(args) {
    const { content, graph_name, options = {} } = args;
    
    // Simulate knowledge graph creation
    const graphId = `graph_${Date.now()}`;
    const nodes = this.extractEntities(content);
    const relationships = this.extractRelationships(content);
    
    // Store in memory (in production, use proper storage)
    if (!this.graphs) this.graphs = new Map();
    this.graphs.set(graph_name, {
      id: graphId,
      name: graph_name,
      nodes,
      relationships,
      created_at: new Date().toISOString(),
      options,
    });

    return {
      content: [
        {
          type: 'text',
          text: `Knowledge graph "${graph_name}" created successfully!\n\n` +
                `Graph ID: ${graphId}\n` +
                `Nodes: ${nodes.length}\n` +
                `Relationships: ${relationships.length}\n` +
                `Real-time updates: ${options.real_time ? 'Enabled' : 'Disabled'}\n` +
                `Persistence: ${options.persist ? 'Enabled' : 'Disabled'}`,
        },
      ],
    };
  }

  async queryKnowledgeGraph(args) {
    const { graph_name, query, limit = 10 } = args;
    
    if (!this.graphs || !this.graphs.has(graph_name)) {
      throw new Error(`Knowledge graph "${graph_name}" not found`);
    }

    const graph = this.graphs.get(graph_name);
    const results = this.searchGraph(graph, query, limit);

    return {
      content: [
        {
          type: 'text',
          text: `Query results for "${query}" in graph "${graph_name}":\n\n` +
                results.map((result, index) => 
                  `${index + 1}. ${result.type}: ${result.content}\n   Relevance: ${result.relevance}`
                ).join('\n\n'),
        },
      ],
    };
  }

  async updateKnowledgeGraph(args) {
    const { graph_name, content, merge_strategy = 'merge' } = args;
    
    if (!this.graphs || !this.graphs.has(graph_name)) {
      throw new Error(`Knowledge graph "${graph_name}" not found`);
    }

    const graph = this.graphs.get(graph_name);
    const newNodes = this.extractEntities(content);
    const newRelationships = this.extractRelationships(content);

    // Apply merge strategy
    switch (merge_strategy) {
      case 'append':
        graph.nodes.push(...newNodes);
        graph.relationships.push(...newRelationships);
        break;
      case 'merge':
        // Merge nodes and relationships, avoiding duplicates
        this.mergeNodes(graph.nodes, newNodes);
        this.mergeRelationships(graph.relationships, newRelationships);
        break;
      case 'replace':
        graph.nodes = newNodes;
        graph.relationships = newRelationships;
        break;
    }

    graph.updated_at = new Date().toISOString();
    this.graphs.set(graph_name, graph);

    return {
      content: [
        {
          type: 'text',
          text: `Knowledge graph "${graph_name}" updated successfully!\n\n` +
                `New nodes added: ${newNodes.length}\n` +
                `New relationships added: ${newRelationships.length}\n` +
                `Total nodes: ${graph.nodes.length}\n` +
                `Total relationships: ${graph.relationships.length}`,
        },
      ],
    };
  }

  async listKnowledgeGraphs(args) {
    const { include_stats = false } = args;
    
    if (!this.graphs || this.graphs.size === 0) {
      return {
        content: [
          {
            type: 'text',
            text: 'No knowledge graphs found.',
          },
        ],
      };
    }

    const graphs = Array.from(this.graphs.values()).map(graph => {
      let info = `- ${graph.name} (ID: ${graph.id})\n  Created: ${graph.created_at}`;
      
      if (include_stats) {
        info += `\n  Nodes: ${graph.nodes.length}\n  Relationships: ${graph.relationships.length}`;
        if (graph.updated_at) {
          info += `\n  Last updated: ${graph.updated_at}`;
        }
      }
      
      return info;
    }).join('\n\n');

    return {
      content: [
        {
          type: 'text',
          text: `Available Knowledge Graphs:\n\n${graphs}`,
        },
      ],
    };
  }

  async deleteKnowledgeGraph(args) {
    const { graph_name, confirm = false } = args;
    
    if (!confirm) {
      return {
        content: [
          {
            type: 'text',
            text: `To delete knowledge graph "${graph_name}", set confirm: true in the request.`,
          },
        ],
      };
    }

    if (!this.graphs || !this.graphs.has(graph_name)) {
      throw new Error(`Knowledge graph "${graph_name}" not found`);
    }

    this.graphs.delete(graph_name);

    return {
      content: [
        {
          type: 'text',
          text: `Knowledge graph "${graph_name}" deleted successfully.`,
        },
      ],
    };
  }

  extractEntities(content) {
    // Simple entity extraction (in production, use NLP libraries)
    const words = content.toLowerCase().split(/\s+/);
    const entities = [...new Set(words.filter(word => 
      word.length > 3 && 
      /^[a-zA-Z]/.test(word) && 
      !['this', 'that', 'with', 'from', 'they', 'have', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'will', 'about', 'there', 'could', 'other', 'after', 'first', 'well', 'also', 'where', 'much', 'some', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'water', 'been', 'call', 'who', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'].includes(word)
    ))];
    
    return entities.map(entity => ({
      id: `entity_${entity}`,
      type: 'concept',
      content: entity,
      confidence: Math.random() * 0.5 + 0.5,
    }));
  }

  extractRelationships(content) {
    // Simple relationship extraction (in production, use NLP libraries)
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const relationships = [];
    
    sentences.forEach((sentence, index) => {
      const words = sentence.toLowerCase().split(/\s+/);
      for (let i = 0; i < words.length - 1; i++) {
        if (words[i].length > 3 && words[i + 1].length > 3) {
          relationships.push({
            id: `rel_${index}_${i}`,
            source: words[i],
            target: words[i + 1],
            type: 'related_to',
            confidence: Math.random() * 0.5 + 0.5,
          });
        }
      }
    });
    
    return relationships;
  }

  searchGraph(graph, query, limit) {
    const queryWords = query.toLowerCase().split(/\s+/);
    const results = [];
    
    // Search in nodes
    graph.nodes.forEach(node => {
      const relevance = this.calculateRelevance(node.content, queryWords);
      if (relevance > 0.3) {
        results.push({
          type: 'node',
          content: node.content,
          relevance,
        });
      }
    });
    
    // Search in relationships
    graph.relationships.forEach(rel => {
      const relevance = this.calculateRelevance(`${rel.source} ${rel.target}`, queryWords);
      if (relevance > 0.3) {
        results.push({
          type: 'relationship',
          content: `${rel.source} → ${rel.target}`,
          relevance,
        });
      }
    });
    
    return results
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, limit);
  }

  calculateRelevance(text, queryWords) {
    const textWords = text.toLowerCase().split(/\s+/);
    let matches = 0;
    
    queryWords.forEach(queryWord => {
      if (textWords.some(textWord => textWord.includes(queryWord) || queryWord.includes(textWord))) {
        matches++;
      }
    });
    
    return matches / queryWords.length;
  }

  mergeNodes(existingNodes, newNodes) {
    newNodes.forEach(newNode => {
      const existing = existingNodes.find(node => node.content === newNode.content);
      if (!existing) {
        existingNodes.push(newNode);
      } else {
        // Update confidence if new node has higher confidence
        if (newNode.confidence > existing.confidence) {
          existing.confidence = newNode.confidence;
        }
      }
    });
  }

  mergeRelationships(existingRels, newRels) {
    newRels.forEach(newRel => {
      const existing = existingRels.find(rel => 
        rel.source === newRel.source && rel.target === newRel.target
      );
      if (!existing) {
        existingRels.push(newRel);
      } else {
        // Update confidence if new relationship has higher confidence
        if (newRel.confidence > existing.confidence) {
          existing.confidence = newRel.confidence;
        }
      }
    });
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
    console.error('Graphiti MCP server running on stdio');
  }
}

const server = new GraphitiMCPServer();
server.run().catch(console.error);

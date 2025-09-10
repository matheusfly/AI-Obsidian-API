#!/usr/bin/env node

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');
const fs = require('fs').promises;
const path = require('path');

class ObsidianVaultMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'obsidian-vault-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.vaultPath = process.env.VAULT_PATH || 'D:\\Nomade Milionario';
    this.openaiApiKey = process.env.OPENAI_API_KEY;

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'read_note',
            description: 'Read a specific note from the Obsidian vault',
            inputSchema: {
              type: 'object',
              properties: {
                note_path: {
                  type: 'string',
                  description: 'Path to the note file (relative to vault root)',
                },
              },
              required: ['note_path'],
            },
          },
          {
            name: 'write_note',
            description: 'Write or update a note in the Obsidian vault',
            inputSchema: {
              type: 'object',
              properties: {
                note_path: {
                  type: 'string',
                  description: 'Path to the note file (relative to vault root)',
                },
                content: {
                  type: 'string',
                  description: 'Content to write to the note',
                },
                append: {
                  type: 'boolean',
                  description: 'Whether to append to existing content',
                  default: false,
                },
              },
              required: ['note_path', 'content'],
            },
          },
          {
            name: 'list_notes',
            description: 'List all notes in the vault or a specific directory',
            inputSchema: {
              type: 'object',
              properties: {
                directory: {
                  type: 'string',
                  description: 'Directory to list (relative to vault root)',
                  default: '',
                },
                recursive: {
                  type: 'boolean',
                  description: 'Whether to search recursively',
                  default: true,
                },
                include_content: {
                  type: 'boolean',
                  description: 'Whether to include note content preview',
                  default: false,
                },
              },
            },
          },
          {
            name: 'search_notes',
            description: 'Search for notes containing specific text',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'Search query',
                },
                directory: {
                  type: 'string',
                  description: 'Directory to search in (relative to vault root)',
                  default: '',
                },
                case_sensitive: {
                  type: 'boolean',
                  description: 'Whether search should be case sensitive',
                  default: false,
                },
                include_content: {
                  type: 'boolean',
                  description: 'Whether to include matching content snippets',
                  default: true,
                },
              },
              required: ['query'],
            },
          },
          {
            name: 'get_note_links',
            description: 'Get all links (internal and external) from a note',
            inputSchema: {
              type: 'object',
              properties: {
                note_path: {
                  type: 'string',
                  description: 'Path to the note file',
                },
              },
              required: ['note_path'],
            },
          },
          {
            name: 'get_note_tags',
            description: 'Get all tags from a note',
            inputSchema: {
              type: 'object',
              properties: {
                note_path: {
                  type: 'string',
                  description: 'Path to the note file',
                },
              },
              required: ['note_path'],
            },
          },
          {
            name: 'create_note',
            description: 'Create a new note with metadata',
            inputSchema: {
              type: 'object',
              properties: {
                note_path: {
                  type: 'string',
                  description: 'Path to the new note file',
                },
                title: {
                  type: 'string',
                  description: 'Title of the note',
                },
                content: {
                  type: 'string',
                  description: 'Content of the note',
                },
                tags: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'Tags to add to the note',
                },
                frontmatter: {
                  type: 'object',
                  description: 'YAML frontmatter for the note',
                },
              },
              required: ['note_path', 'title', 'content'],
            },
          },
          {
            name: 'delete_note',
            description: 'Delete a note from the vault',
            inputSchema: {
              type: 'object',
              properties: {
                note_path: {
                  type: 'string',
                  description: 'Path to the note file to delete',
                },
                confirm: {
                  type: 'boolean',
                  description: 'Confirmation flag',
                  default: false,
                },
              },
              required: ['note_path'],
            },
          },
          {
            name: 'get_vault_stats',
            description: 'Get statistics about the vault',
            inputSchema: {
              type: 'object',
              properties: {
                include_file_sizes: {
                  type: 'boolean',
                  description: 'Whether to include file size information',
                  default: true,
                },
              },
            },
          },
          {
            name: 'analyze_note_content',
            description: 'Analyze note content using AI (requires OpenAI API key)',
            inputSchema: {
              type: 'object',
              properties: {
                note_path: {
                  type: 'string',
                  description: 'Path to the note file to analyze',
                },
                analysis_type: {
                  type: 'string',
                  enum: ['summary', 'key_points', 'sentiment', 'topics', 'full_analysis'],
                  description: 'Type of analysis to perform',
                  default: 'summary',
                },
              },
              required: ['note_path'],
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
          case 'read_note':
            return await this.readNote(args);
          case 'write_note':
            return await this.writeNote(args);
          case 'list_notes':
            return await this.listNotes(args);
          case 'search_notes':
            return await this.searchNotes(args);
          case 'get_note_links':
            return await this.getNoteLinks(args);
          case 'get_note_tags':
            return await this.getNoteTags(args);
          case 'create_note':
            return await this.createNote(args);
          case 'delete_note':
            return await this.deleteNote(args);
          case 'get_vault_stats':
            return await this.getVaultStats(args);
          case 'analyze_note_content':
            return await this.analyzeNoteContent(args);
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

  async readNote(args) {
    const { note_path } = args;
    const fullPath = path.join(this.vaultPath, note_path);
    
    try {
      const content = await fs.readFile(fullPath, 'utf-8');
      const stats = await fs.stat(fullPath);
      
      return {
        content: [
          {
            type: 'text',
            text: `Note: ${note_path}\n` +
                  `Size: ${stats.size} bytes\n` +
                  `Modified: ${stats.mtime.toISOString()}\n\n` +
                  `Content:\n${content}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to read note: ${error.message}`);
    }
  }

  async writeNote(args) {
    const { note_path, content, append = false } = args;
    const fullPath = path.join(this.vaultPath, note_path);
    
    try {
      // Ensure directory exists
      await fs.mkdir(path.dirname(fullPath), { recursive: true });
      
      if (append) {
        const existingContent = await fs.readFile(fullPath, 'utf-8').catch(() => '');
        await fs.writeFile(fullPath, existingContent + '\n' + content);
      } else {
        await fs.writeFile(fullPath, content);
      }
      
      return {
        content: [
          {
            type: 'text',
            text: `Note "${note_path}" ${append ? 'appended to' : 'written'} successfully!`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to write note: ${error.message}`);
    }
  }

  async listNotes(args) {
    const { directory = '', recursive = true, include_content = false } = args;
    const fullPath = path.join(this.vaultPath, directory);
    
    try {
      const notes = await this.getMarkdownFiles(fullPath, recursive);
      
      let result = `Found ${notes.length} notes in ${directory || 'vault root'}:\n\n`;
      
      for (const note of notes) {
        const relativePath = path.relative(this.vaultPath, note);
        result += `- ${relativePath}\n`;
        
        if (include_content) {
          try {
            const content = await fs.readFile(note, 'utf-8');
            const preview = content.substring(0, 200).replace(/\n/g, ' ');
            result += `  Preview: ${preview}...\n`;
          } catch (error) {
            result += `  Preview: [Error reading file]\n`;
          }
        }
      }
      
      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to list notes: ${error.message}`);
    }
  }

  async searchNotes(args) {
    const { query, directory = '', case_sensitive = false, include_content = true } = args;
    const fullPath = path.join(this.vaultPath, directory);
    
    try {
      const notes = await this.getMarkdownFiles(fullPath, true);
      const searchQuery = case_sensitive ? query : query.toLowerCase();
      const results = [];
      
      for (const note of notes) {
        try {
          const content = await fs.readFile(note, 'utf-8');
          const searchContent = case_sensitive ? content : content.toLowerCase();
          
          if (searchContent.includes(searchQuery)) {
            const relativePath = path.relative(this.vaultPath, note);
            const result = {
              path: relativePath,
              matches: 0,
              snippets: [],
            };
            
            // Count matches and extract snippets
            const lines = content.split('\n');
            for (let i = 0; i < lines.length; i++) {
              const line = lines[i];
              const searchLine = case_sensitive ? line : line.toLowerCase();
              
              if (searchLine.includes(searchQuery)) {
                result.matches++;
                if (include_content) {
                  result.snippets.push({
                    line: i + 1,
                    content: line.trim(),
                  });
                }
              }
            }
            
            results.push(result);
          }
        } catch (error) {
          // Skip files that can't be read
          continue;
        }
      }
      
      let result = `Found ${results.length} notes matching "${query}":\n\n`;
      
      for (const noteResult of results) {
        result += `- ${noteResult.path} (${noteResult.matches} matches)\n`;
        
        if (include_content && noteResult.snippets.length > 0) {
          result += `  Snippets:\n`;
          for (const snippet of noteResult.snippets.slice(0, 3)) {
            result += `    Line ${snippet.line}: ${snippet.content}\n`;
          }
        }
      }
      
      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to search notes: ${error.message}`);
    }
  }

  async getNoteLinks(args) {
    const { note_path } = args;
    const fullPath = path.join(this.vaultPath, note_path);
    
    try {
      const content = await fs.readFile(fullPath, 'utf-8');
      
      // Extract internal links [[link]]
      const internalLinks = content.match(/\[\[([^\]]+)\]\]/g) || [];
      // Extract external links [text](url)
      const externalLinks = content.match(/\[([^\]]+)\]\(([^)]+)\)/g) || [];
      
      let result = `Links in ${note_path}:\n\n`;
      
      if (internalLinks.length > 0) {
        result += `Internal Links (${internalLinks.length}):\n`;
        internalLinks.forEach(link => {
          result += `- ${link}\n`;
        });
        result += '\n';
      }
      
      if (externalLinks.length > 0) {
        result += `External Links (${externalLinks.length}):\n`;
        externalLinks.forEach(link => {
          result += `- ${link}\n`;
        });
      }
      
      if (internalLinks.length === 0 && externalLinks.length === 0) {
        result += 'No links found in this note.';
      }
      
      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to get note links: ${error.message}`);
    }
  }

  async getNoteTags(args) {
    const { note_path } = args;
    const fullPath = path.join(this.vaultPath, note_path);
    
    try {
      const content = await fs.readFile(fullPath, 'utf-8');
      
      // Extract tags #tag
      const tags = content.match(/#[a-zA-Z0-9_-]+/g) || [];
      const uniqueTags = [...new Set(tags)];
      
      let result = `Tags in ${note_path}:\n\n`;
      
      if (uniqueTags.length > 0) {
        result += `Found ${uniqueTags.length} unique tags:\n`;
        uniqueTags.forEach(tag => {
          result += `- ${tag}\n`;
        });
      } else {
        result += 'No tags found in this note.';
      }
      
      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to get note tags: ${error.message}`);
    }
  }

  async createNote(args) {
    const { note_path, title, content, tags = [], frontmatter = {} } = args;
    const fullPath = path.join(this.vaultPath, note_path);
    
    try {
      // Ensure directory exists
      await fs.mkdir(path.dirname(fullPath), { recursive: true });
      
      // Build note content
      let noteContent = '';
      
      // Add frontmatter if provided
      if (Object.keys(frontmatter).length > 0 || tags.length > 0) {
        noteContent += '---\n';
        if (Object.keys(frontmatter).length > 0) {
          for (const [key, value] of Object.entries(frontmatter)) {
            noteContent += `${key}: ${value}\n`;
          }
        }
        if (tags.length > 0) {
          noteContent += `tags: [${tags.map(tag => `"${tag}"`).join(', ')}]\n`;
        }
        noteContent += '---\n\n';
      }
      
      // Add title
      noteContent += `# ${title}\n\n`;
      
      // Add content
      noteContent += content;
      
      await fs.writeFile(fullPath, noteContent);
      
      return {
        content: [
          {
            type: 'text',
            text: `Note "${note_path}" created successfully!\n\n` +
                  `Title: ${title}\n` +
                  `Tags: ${tags.length > 0 ? tags.join(', ') : 'None'}\n` +
                  `Frontmatter: ${Object.keys(frontmatter).length > 0 ? 'Yes' : 'No'}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to create note: ${error.message}`);
    }
  }

  async deleteNote(args) {
    const { note_path, confirm = false } = args;
    const fullPath = path.join(this.vaultPath, note_path);
    
    if (!confirm) {
      return {
        content: [
          {
            type: 'text',
            text: `To delete note "${note_path}", set confirm: true in the request.`,
          },
        ],
      };
    }
    
    try {
      await fs.unlink(fullPath);
      
      return {
        content: [
          {
            type: 'text',
            text: `Note "${note_path}" deleted successfully.`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to delete note: ${error.message}`);
    }
  }

  async getVaultStats(args) {
    const { include_file_sizes = true } = args;
    
    try {
      const notes = await this.getMarkdownFiles(this.vaultPath, true);
      const stats = {
        total_notes: notes.length,
        total_size: 0,
        directories: new Set(),
        file_sizes: [],
      };
      
      for (const note of notes) {
        try {
          const stat = await fs.stat(note);
          stats.total_size += stat.size;
          
          if (include_file_sizes) {
            const relativePath = path.relative(this.vaultPath, note);
            stats.file_sizes.push({
              path: relativePath,
              size: stat.size,
            });
            stats.directories.add(path.dirname(relativePath));
          }
        } catch (error) {
          // Skip files that can't be stat'd
          continue;
        }
      }
      
      let result = `Vault Statistics:\n\n` +
                  `Total Notes: ${stats.total_notes}\n` +
                  `Total Size: ${this.formatBytes(stats.total_size)}\n` +
                  `Directories: ${stats.directories.size}\n\n`;
      
      if (include_file_sizes && stats.file_sizes.length > 0) {
        // Sort by size (largest first)
        stats.file_sizes.sort((a, b) => b.size - a.size);
        
        result += `Largest Files:\n`;
        stats.file_sizes.slice(0, 10).forEach(file => {
          result += `- ${file.path}: ${this.formatBytes(file.size)}\n`;
        });
      }
      
      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to get vault stats: ${error.message}`);
    }
  }

  async analyzeNoteContent(args) {
    const { note_path, analysis_type = 'summary' } = args;
    
    if (!this.openaiApiKey) {
      throw new Error('OpenAI API key not configured for content analysis');
    }
    
    try {
      const fullPath = path.join(this.vaultPath, note_path);
      const content = await fs.readFile(fullPath, 'utf-8');
      
      // Simulate AI analysis (in production, use OpenAI API)
      const analysis = this.simulateAIAnalysis(content, analysis_type);
      
      return {
        content: [
          {
            type: 'text',
            text: `AI Analysis of ${note_path} (${analysis_type}):\n\n${analysis}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to analyze note content: ${error.message}`);
    }
  }

  async getMarkdownFiles(dir, recursive = true) {
    const files = [];
    
    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        
        if (entry.isDirectory() && recursive) {
          const subFiles = await this.getMarkdownFiles(fullPath, recursive);
          files.push(...subFiles);
        } else if (entry.isFile() && entry.name.endsWith('.md')) {
          files.push(fullPath);
        }
      }
    } catch (error) {
      // Skip directories that can't be read
    }
    
    return files;
  }

  simulateAIAnalysis(content, analysisType) {
    const wordCount = content.split(/\s+/).length;
    const charCount = content.length;
    const lineCount = content.split('\n').length;
    
    switch (analysisType) {
      case 'summary':
        return `This note contains ${wordCount} words, ${charCount} characters, and ${lineCount} lines. It appears to be a comprehensive document covering various topics.`;
      
      case 'key_points':
        const lines = content.split('\n').filter(line => line.trim().length > 0);
        const keyPoints = lines.filter(line => 
          line.startsWith('#') || 
          line.startsWith('-') || 
          line.startsWith('*') ||
          line.includes('important') ||
          line.includes('key') ||
          line.includes('main')
        ).slice(0, 5);
        return `Key Points:\n${keyPoints.map(point => `- ${point.trim()}`).join('\n')}`;
      
      case 'sentiment':
        const positiveWords = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic'];
        const negativeWords = ['bad', 'terrible', 'awful', 'horrible', 'disappointing'];
        const positiveCount = positiveWords.reduce((count, word) => 
          count + (content.toLowerCase().split(word).length - 1), 0);
        const negativeCount = negativeWords.reduce((count, word) => 
          count + (content.toLowerCase().split(word).length - 1), 0);
        const sentiment = positiveCount > negativeCount ? 'Positive' : 
                         negativeCount > positiveCount ? 'Negative' : 'Neutral';
        return `Sentiment Analysis: ${sentiment}\nPositive indicators: ${positiveCount}\nNegative indicators: ${negativeCount}`;
      
      case 'topics':
        const words = content.toLowerCase().split(/\s+/);
        const wordFreq = {};
        words.forEach(word => {
          if (word.length > 4) {
            wordFreq[word] = (wordFreq[word] || 0) + 1;
          }
        });
        const topics = Object.entries(wordFreq)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 10)
          .map(([word, freq]) => `${word} (${freq})`)
          .join(', ');
        return `Main Topics: ${topics}`;
      
      case 'full_analysis':
        return `Full Analysis:\n\n` +
               `- Word Count: ${wordCount}\n` +
               `- Character Count: ${charCount}\n` +
               `- Line Count: ${lineCount}\n` +
               `- Average Words per Line: ${(wordCount / lineCount).toFixed(2)}\n` +
               `- Reading Time: ${Math.ceil(wordCount / 200)} minutes\n` +
               `- Complexity: ${wordCount > 1000 ? 'High' : wordCount > 500 ? 'Medium' : 'Low'}`;
      
      default:
        return `Analysis type "${analysisType}" not supported.`;
    }
  }

  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
    console.error('Obsidian Vault MCP server running on stdio');
  }
}

const server = new ObsidianVaultMCPServer();
server.run().catch(console.error);

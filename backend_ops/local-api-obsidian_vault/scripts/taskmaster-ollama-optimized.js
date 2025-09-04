#!/usr/bin/env node
// Task Master Ollama Integration - Optimized for Your Models

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class TaskMasterOllamaOptimized {
    constructor() {
        this.ollamaHost = process.env.OLLAMA_HOST || 'http://localhost:11434';
        this.timeout = parseInt(process.env.OLLAMA_TIMEOUT) || 300000;
        
        // Your specific models
        this.models = {
            main: process.env.OLLAMA_MAIN_MODEL || 'deepseek-r1:8b',
            coding: process.env.OLLAMA_CODING_MODEL || 'kirito1/qwen3-coder:latest',
            research: process.env.OLLAMA_RESEARCH_MODEL || 'qwen3:latest',
            fallback: process.env.OLLAMA_FALLBACK_MODEL || 'gemma3:latest'
        };
        
        // Model-specific configurations
        this.modelConfigs = {
            'deepseek-r1:8b': {
                temperature: 0.7,
                top_p: 0.9,
                max_tokens: 4096,
                context_length: 32768,
                description: 'Main reasoning and analysis model'
            },
            'kirito1/qwen3-coder:latest': {
                temperature: 0.3,
                top_p: 0.8,
                max_tokens: 8192,
                context_length: 32768,
                description: 'Specialized coding model'
            },
            'qwen3:latest': {
                temperature: 0.6,
                top_p: 0.9,
                max_tokens: 4096,
                context_length: 32768,
                description: 'Research and general purpose model'
            },
            'gemma3:latest': {
                temperature: 0.5,
                top_p: 0.85,
                max_tokens: 2048,
                context_length: 8192,
                description: 'Fast fallback model'
            }
        };
    }

    async listModels() {
        try {
            const response = await fetch(`${this.ollamaHost}/api/tags`);
            const data = await response.json();
            return data.models || [];
        } catch (error) {
            console.error('Error listing models:', error);
            return [];
        }
    }

    async generateResponse(prompt, model = 'main', options = {}) {
        const modelName = this.models[model] || this.models.main;
        const modelConfig = this.modelConfigs[modelName] || this.modelConfigs['deepseek-r1:8b'];
        
        const requestBody = {
            model: modelName,
            prompt: prompt,
            stream: false,
            options: {
                temperature: options.temperature || modelConfig.temperature,
                top_p: options.top_p || modelConfig.top_p,
                num_predict: options.max_tokens || modelConfig.max_tokens,
                ...options
            }
        };

        try {
            const response = await fetch(`${this.ollamaHost}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                response: data.response,
                model: modelName,
                config: modelConfig
            };
        } catch (error) {
            console.error('Error generating response:', error);
            throw error;
        }
    }

    async chat(messages, model = 'main', options = {}) {
        const modelName = this.models[model] || this.models.main;
        const modelConfig = this.modelConfigs[modelName] || this.modelConfigs['deepseek-r1:8b'];
        
        const requestBody = {
            model: modelName,
            messages: messages,
            stream: false,
            options: {
                temperature: options.temperature || modelConfig.temperature,
                top_p: options.top_p || modelConfig.top_p,
                num_predict: options.max_tokens || modelConfig.max_tokens,
                ...options
            }
        };

        try {
            const response = await fetch(`${this.ollamaHost}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                content: data.message.content,
                model: modelName,
                config: modelConfig
            };
        } catch (error) {
            console.error('Error in chat:', error);
            throw error;
        }
    }

    async getModelInfo(modelName) {
        const modelConfig = this.modelConfigs[modelName];
        if (modelConfig) {
            return {
                name: modelName,
                ...modelConfig
            };
        }
        return null;
    }

    async isHealthy() {
        try {
            const response = await fetch(`${this.ollamaHost}/api/tags`);
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    async getModelStats() {
        try {
            const models = await this.listModels();
            const stats = {};
            
            for (const model of models) {
                const modelName = model.name;
                const modelInfo = await this.getModelInfo(modelName);
                if (modelInfo) {
                    stats[modelName] = {
                        ...modelInfo,
                        size: model.size,
                        modified: model.modified_at
                    };
                }
            }
            
            return stats;
        } catch (error) {
            console.error('Error getting model stats:', error);
            return {};
        }
    }

    // Task Master specific methods
    async analyzeTask(task, context = '') {
        const prompt = `Analyze this task and provide a structured breakdown:

Task: ${task}
Context: ${context}

Please provide:
1. Task complexity (1-10)
2. Required skills/capabilities
3. Estimated effort
4. Recommended model for this task
5. Potential challenges
6. Step-by-step approach`;

        return await this.generateResponse(prompt, 'main');
    }

    async generateCode(task, language = 'javascript', context = '') {
        const prompt = `Generate code for this task:

Task: ${task}
Language: ${language}
Context: ${context}

Please provide:
1. Complete, working code
2. Comments explaining key parts
3. Usage examples
4. Error handling
5. Testing suggestions`;

        return await this.generateResponse(prompt, 'coding');
    }

    async researchTopic(topic, depth = 'medium') {
        const prompt = `Research this topic in ${depth} detail:

Topic: ${topic}

Please provide:
1. Key concepts and definitions
2. Current state of the field
3. Important developments
4. Key players/contributors
5. Future trends
6. Practical applications`;

        return await this.generateResponse(prompt, 'research');
    }

    async quickResponse(query) {
        return await this.generateResponse(query, 'fallback');
    }
}

// Export for use in Task Master
module.exports = TaskMasterOllamaOptimized;

// CLI usage
if (require.main === module) {
    const ollama = new TaskMasterOllamaOptimized();
    
    const command = process.argv[2];
    const model = process.argv[3] || 'main';
    const prompt = process.argv[4];

    switch (command) {
        case 'list':
            ollama.listModels().then(models => {
                console.log('Available models:');
                models.forEach(model => console.log(`- ${model.name} (${model.size})`));
            });
            break;
        case 'stats':
            ollama.getModelStats().then(stats => {
                console.log('Model Statistics:');
                Object.entries(stats).forEach(([name, info]) => {
                    console.log(`\n${name}:`);
                    console.log(`  Description: ${info.description}`);
                    console.log(`  Size: ${info.size}`);
                    console.log(`  Temperature: ${info.temperature}`);
                    console.log(`  Max Tokens: ${info.max_tokens}`);
                });
            });
            break;
        case 'generate':
            if (prompt) {
                ollama.generateResponse(prompt, model).then(result => {
                    console.log(`\nModel: ${result.model}`);
                    console.log(`Response: ${result.response}`);
                });
            } else {
                console.log('Usage: node taskmaster-ollama-optimized.js generate [model] "prompt"');
            }
            break;
        case 'analyze':
            if (prompt) {
                ollama.analyzeTask(prompt).then(result => {
                    console.log(`\nTask Analysis:\n${result.response}`);
                });
            } else {
                console.log('Usage: node taskmaster-ollama-optimized.js analyze "task description"');
            }
            break;
        case 'code':
            if (prompt) {
                ollama.generateCode(prompt).then(result => {
                    console.log(`\nGenerated Code:\n${result.response}`);
                });
            } else {
                console.log('Usage: node taskmaster-ollama-optimized.js code "coding task"');
            }
            break;
        case 'research':
            if (prompt) {
                ollama.researchTopic(prompt).then(result => {
                    console.log(`\nResearch Results:\n${result.response}`);
                });
            } else {
                console.log('Usage: node taskmaster-ollama-optimized.js research "topic"');
            }
            break;
        case 'health':
            ollama.isHealthy().then(healthy => {
                console.log(healthy ? 'Ollama is healthy' : 'Ollama is not responding');
            });
            break;
        default:
            console.log('Task Master Ollama Optimized - Usage:');
            console.log('  node taskmaster-ollama-optimized.js list');
            console.log('  node taskmaster-ollama-optimized.js stats');
            console.log('  node taskmaster-ollama-optimized.js generate [model] "prompt"');
            console.log('  node taskmaster-ollama-optimized.js analyze "task description"');
            console.log('  node taskmaster-ollama-optimized.js code "coding task"');
            console.log('  node taskmaster-ollama-optimized.js research "topic"');
            console.log('  node taskmaster-ollama-optimized.js health');
            console.log('\nAvailable models: main, coding, research, fallback');
    }
}

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Send, 
  Sparkles, 
  Code2, 
  Database, 
  Workflow,
  Brain,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react';

interface HelloWorldResponse {
  message: string;
  timestamp: string;
  context: {
    compressedKnowledge: string[];
    toolIntegrations: string[];
    aiCapabilities: string[];
  };
  metadata: {
    stepId: string;
    executionTime: number;
    version: string;
  };
}

const HelloWorldPanel: React.FC = () => {
  const [name, setName] = useState('');
  const [language, setLanguage] = useState('typescript');
  const [context, setContext] = useState('');
  const [response, setResponse] = useState<HelloWorldResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [executionHistory, setExecutionHistory] = useState<HelloWorldResponse[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsLoading(true);
    
    try {
      // Simulate API call to Motia step
      const mockResponse: HelloWorldResponse = {
        message: `Hello ${name}! Welcome to the Context Engineering Master system powered by Motia. 

You're now connected to a unified backend framework that compresses all our tool-box knowledge into a single, coherent system. This system integrates APIs, background jobs, workflows, and AI agents with built-in observability and state management.

Language: ${language}
Context: ${context || 'Interactive Hello World Demo'}

The system is ready to help you build, deploy, and manage complex applications with the power of context engineering and visual programming.`,
        timestamp: new Date().toISOString(),
        context: {
          compressedKnowledge: [
            "Motia: Unified backend framework for APIs, events, and AI agents",
            "Flyde: Visual programming for complex workflows", 
            "MCP: Model Context Protocol for AI agent communication",
            "ChartDB: Database diagram and schema visualization",
            "Context7: Persistent knowledge storage and retrieval",
            "Documentation Scrapers: Advanced web scraping with MCP integration",
            "Visual Tools: Interactive web UI for tool orchestration"
          ],
          toolIntegrations: [
            "Motia Docs Scraper",
            "ChartDB Documentation Scraper", 
            "Context7 Memory System",
            "Flyde Visual Flows",
            "MCP Server Network",
            "Interactive Web UI",
            "Performance Monitoring"
          ],
          aiCapabilities: [
            "Context-aware responses",
            "Knowledge compression and extraction",
            "Multi-agent coordination",
            "Real-time learning and adaptation",
            "Semantic search and retrieval",
            "Automated workflow generation"
          ]
        },
        metadata: {
          stepId: `step_${Date.now()}`,
          executionTime: Math.random() * 100 + 50,
          version: "1.0.0"
        }
      };

      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
      
      setResponse(mockResponse);
      setExecutionHistory(prev => [mockResponse, ...prev.slice(0, 4)]);
    } catch (error) {
      console.error('Error calling hello world API:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-center space-x-2 mb-2"
        >
          <Sparkles className="w-6 h-6 text-blue-400" />
          <h2 className="text-2xl font-bold text-white">Interactive Hello World</h2>
          <Sparkles className="w-6 h-6 text-blue-400" />
        </motion.div>
        <p className="text-slate-400">
          Experience the power of Motia's unified backend framework with context engineering
        </p>
      </div>

      {/* Form */}
      <motion.form
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        onSubmit={handleSubmit}
        className="bg-slate-700/50 rounded-lg p-6 space-y-4"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Your Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your name"
              className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Language
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="typescript">TypeScript</option>
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
            </select>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Context (Optional)
          </label>
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Describe your context or requirements..."
            rows={3}
            className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <motion.button
          type="submit"
          disabled={isLoading || !name.trim()}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 px-6 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {isLoading ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
              />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>Send Hello World</span>
            </>
          )}
        </motion.button>
      </motion.form>

      {/* Response */}
      {response && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="bg-slate-700/50 rounded-lg p-6">
            <div className="flex items-center space-x-2 mb-4">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <h3 className="text-lg font-semibold text-white">Response</h3>
              <div className="flex items-center space-x-1 text-sm text-slate-400">
                <Clock className="w-4 h-4" />
                <span>{response.metadata.executionTime.toFixed(0)}ms</span>
              </div>
            </div>
            
            <div className="bg-slate-800 rounded-lg p-4 mb-4">
              <p className="text-slate-300 whitespace-pre-line">
                {response.message}
              </p>
            </div>
            
            {/* Context Information */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Brain className="w-4 h-4 text-purple-400" />
                  <h4 className="font-medium text-white">Compressed Knowledge</h4>
                </div>
                <ul className="space-y-1 text-sm text-slate-300">
                  {response.context.compressedKnowledge.slice(0, 3).map((item, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="text-purple-400">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Workflow className="w-4 h-4 text-green-400" />
                  <h4 className="font-medium text-white">Tool Integrations</h4>
                </div>
                <ul className="space-y-1 text-sm text-slate-300">
                  {response.context.toolIntegrations.slice(0, 3).map((item, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="text-green-400">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Zap className="w-4 h-4 text-yellow-400" />
                  <h4 className="font-medium text-white">AI Capabilities</h4>
                </div>
                <ul className="space-y-1 text-sm text-slate-300">
                  {response.context.aiCapabilities.slice(0, 3).map((item, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="text-yellow-400">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Execution History */}
      {executionHistory.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-700/50 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <Clock className="w-5 h-5" />
            <span>Execution History</span>
          </h3>
          
          <div className="space-y-3">
            {executionHistory.map((item, index) => (
              <div key={item.metadata.stepId} className="bg-slate-800/50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-slate-300">
                    Step {executionHistory.length - index}
                  </span>
                  <div className="flex items-center space-x-2 text-xs text-slate-400">
                    <span>{item.metadata.executionTime.toFixed(0)}ms</span>
                    <span>•</span>
                    <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
                <p className="text-sm text-slate-400 truncate">
                  {item.message.split('\n')[0]}
                </p>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default HelloWorldPanel;

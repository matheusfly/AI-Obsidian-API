import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Settings, 
  Play, 
  Pause, 
  RotateCcw, 
  CheckCircle, 
  XCircle,
  Clock,
  Zap,
  Database,
  Workflow,
  Brain,
  Network,
  Monitor,
  Code2
} from 'lucide-react';

interface Tool {
  id: string;
  name: string;
  type: 'scraper' | 'visualizer' | 'memory' | 'ai' | 'monitor';
  status: 'running' | 'stopped' | 'error' | 'starting';
  lastActivity: string;
  performance: {
    cpu: number;
    memory: number;
    requests: number;
    successRate: number;
  };
  description: string;
  endpoints: string[];
}

const ToolOrchestrator: React.FC = () => {
  const [tools, setTools] = useState<Tool[]>([
    {
      id: '1',
      name: 'Motia Docs Scraper',
      type: 'scraper',
      status: 'running',
      lastActivity: '2 minutes ago',
      performance: { cpu: 25, memory: 40, requests: 150, successRate: 95 },
      description: 'Advanced web scraping with MCP integration for Motia documentation',
      endpoints: ['/api/scrape', '/api/docs', '/api/status']
    },
    {
      id: '2',
      name: 'ChartDB Visualizer',
      type: 'visualizer',
      status: 'running',
      lastActivity: '1 minute ago',
      performance: { cpu: 35, memory: 55, requests: 80, successRate: 92 },
      description: 'Database diagram and schema visualization with interactive features',
      endpoints: ['/api/diagrams', '/api/schemas', '/api/templates']
    },
    {
      id: '3',
      name: 'Context7 Memory',
      type: 'memory',
      status: 'running',
      lastActivity: '30 seconds ago',
      performance: { cpu: 20, memory: 30, requests: 200, successRate: 98 },
      description: 'Persistent knowledge storage and retrieval system',
      endpoints: ['/api/store', '/api/retrieve', '/api/search']
    },
    {
      id: '4',
      name: 'AI Agent Coordinator',
      type: 'ai',
      status: 'running',
      lastActivity: '45 seconds ago',
      performance: { cpu: 45, memory: 60, requests: 120, successRate: 90 },
      description: 'Multi-agent coordination and communication system',
      endpoints: ['/api/agents', '/api/coordinate', '/api/tasks']
    },
    {
      id: '5',
      name: 'Performance Monitor',
      type: 'monitor',
      status: 'running',
      lastActivity: '15 seconds ago',
      performance: { cpu: 15, memory: 25, requests: 300, successRate: 99 },
      description: 'Real-time system monitoring and analytics',
      endpoints: ['/api/metrics', '/api/alerts', '/api/health']
    },
    {
      id: '6',
      name: 'Flyde Visual Flows',
      type: 'visualizer',
      status: 'stopped',
      lastActivity: '5 minutes ago',
      performance: { cpu: 0, memory: 0, requests: 0, successRate: 0 },
      description: 'Visual programming interface for workflow creation',
      endpoints: ['/api/flows', '/api/execute', '/api/debug']
    }
  ]);

  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [isAutoMode, setIsAutoMode] = useState(false);

  // Simulate tool activity
  useEffect(() => {
    const interval = setInterval(() => {
      setTools(prev => prev.map(tool => ({
        ...tool,
        lastActivity: `${Math.floor(Math.random() * 5) + 1} minutes ago`,
        performance: {
          ...tool.performance,
          cpu: tool.status === 'running' ? Math.max(0, Math.min(100, tool.performance.cpu + (Math.random() - 0.5) * 10)) : 0,
          memory: tool.status === 'running' ? Math.max(0, Math.min(100, tool.performance.memory + (Math.random() - 0.5) * 5)) : 0,
          requests: tool.status === 'running' ? tool.performance.requests + Math.floor(Math.random() * 5) : tool.performance.requests,
          successRate: tool.status === 'running' ? Math.min(100, tool.performance.successRate + (Math.random() - 0.5) * 2) : tool.performance.successRate
        }
      })));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleToolAction = (toolId: string, action: 'start' | 'stop' | 'restart') => {
    setTools(prev => prev.map(tool => {
      if (tool.id === toolId) {
        switch (action) {
          case 'start':
            return { ...tool, status: 'starting' as const };
          case 'stop':
            return { ...tool, status: 'stopped' as const };
          case 'restart':
            return { ...tool, status: 'starting' as const };
          default:
            return tool;
        }
      }
      return tool;
    }));

    // Simulate action completion
    setTimeout(() => {
      setTools(prev => prev.map(tool => {
        if (tool.id === toolId) {
          if (action === 'start' || action === 'restart') {
            return { ...tool, status: 'running' as const };
          }
        }
        return tool;
      }));
    }, 2000);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'stopped': return <XCircle className="w-4 h-4 text-red-400" />;
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />;
      case 'starting': return <Clock className="w-4 h-4 text-yellow-400 animate-pulse" />;
      default: return <XCircle className="w-4 h-4 text-slate-400" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'scraper': return <Code2 className="w-5 h-5 text-blue-400" />;
      case 'visualizer': return <Workflow className="w-5 h-5 text-green-400" />;
      case 'memory': return <Database className="w-5 h-5 text-purple-400" />;
      case 'ai': return <Brain className="w-5 h-5 text-yellow-400" />;
      case 'monitor': return <Monitor className="w-5 h-5 text-orange-400" />;
      default: return <Settings className="w-5 h-5 text-slate-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-500';
      case 'stopped': return 'bg-red-500';
      case 'error': return 'bg-red-500';
      case 'starting': return 'bg-yellow-500';
      default: return 'bg-slate-500';
    }
  };

  const runningTools = tools.filter(tool => tool.status === 'running').length;
  const totalTools = tools.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-center space-x-2 mb-2"
        >
          <Settings className="w-6 h-6 text-red-400" />
          <h2 className="text-2xl font-bold text-white">Tool Orchestrator</h2>
          <Settings className="w-6 h-6 text-red-400" />
        </motion.div>
        <p className="text-slate-400">
          Unified control panel for all tool-box components
        </p>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">Total Tools</h3>
            <Settings className="w-5 h-5 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-blue-400">{totalTools}</div>
          <div className="text-sm text-slate-400">Registered tools</div>
        </div>

        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">Running</h3>
            <CheckCircle className="w-5 h-5 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-green-400">{runningTools}</div>
          <div className="text-sm text-slate-400">Active tools</div>
        </div>

        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">Stopped</h3>
            <XCircle className="w-5 h-5 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-red-400">{totalTools - runningTools}</div>
          <div className="text-sm text-slate-400">Inactive tools</div>
        </div>

        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">Health</h3>
            <Zap className="w-5 h-5 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-purple-400">
            {Math.round((runningTools / totalTools) * 100)}%
          </div>
          <div className="text-sm text-slate-400">System health</div>
        </div>
      </div>

      {/* Tools Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tools.map((tool) => (
          <motion.div
            key={tool.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`bg-slate-700/50 rounded-lg p-4 cursor-pointer transition-all duration-200 ${
              selectedTool === tool.id ? 'ring-2 ring-blue-500' : 'hover:bg-slate-600/50'
            }`}
            onClick={() => setSelectedTool(selectedTool === tool.id ? null : tool.id)}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                {getTypeIcon(tool.type)}
                <h3 className="font-medium text-white">{tool.name}</h3>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(tool.status)}
                <div className={`w-3 h-3 rounded-full ${getStatusColor(tool.status)}`} />
              </div>
            </div>

            <p className="text-sm text-slate-400 mb-3">{tool.description}</p>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-300">CPU:</span>
                <span className="text-slate-300">{tool.performance.cpu.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Memory:</span>
                <span className="text-slate-300">{tool.performance.memory.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Requests:</span>
                <span className="text-slate-300">{tool.performance.requests}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Success Rate:</span>
                <span className="text-slate-300">{tool.performance.successRate.toFixed(1)}%</span>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-slate-600">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Last Activity:</span>
                <span className="text-xs text-slate-400">{tool.lastActivity}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Tool Details */}
      <AnimatePresence>
        {selectedTool && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-slate-700/50 rounded-lg p-6"
          >
            {(() => {
              const tool = tools.find(t => t.id === selectedTool);
              if (!tool) return null;

              return (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-white">
                      {tool.name} Details
                    </h3>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleToolAction(tool.id, 'start')}
                        disabled={tool.status === 'running' || tool.status === 'starting'}
                        className="bg-green-500 text-white py-1 px-3 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
                      >
                        <Play className="w-3 h-3" />
                        <span>Start</span>
                      </button>
                      <button
                        onClick={() => handleToolAction(tool.id, 'stop')}
                        disabled={tool.status === 'stopped'}
                        className="bg-red-500 text-white py-1 px-3 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
                      >
                        <Pause className="w-3 h-3" />
                        <span>Stop</span>
                      </button>
                      <button
                        onClick={() => handleToolAction(tool.id, 'restart')}
                        className="bg-yellow-500 text-white py-1 px-3 rounded text-sm flex items-center space-x-1"
                      >
                        <RotateCcw className="w-3 h-3" />
                        <span>Restart</span>
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium text-white mb-2">Endpoints</h4>
                      <ul className="space-y-1">
                        {tool.endpoints.map((endpoint, index) => (
                          <li key={index} className="text-sm text-slate-300 font-mono">
                            {endpoint}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h4 className="font-medium text-white mb-2">Performance Metrics</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-slate-300">CPU Usage:</span>
                          <span className="text-sm text-slate-300">{tool.performance.cpu.toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-slate-300">Memory Usage:</span>
                          <span className="text-sm text-slate-300">{tool.performance.memory.toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-slate-300">Total Requests:</span>
                          <span className="text-sm text-slate-300">{tool.performance.requests}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-slate-300">Success Rate:</span>
                          <span className="text-sm text-slate-300">{tool.performance.successRate.toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })()}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ToolOrchestrator;

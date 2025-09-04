import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Brain, 
  Zap, 
  Database, 
  Workflow, 
  Monitor, 
  Settings,
  Play,
  Pause,
  RotateCcw,
  BarChart3,
  Network,
  Code2
} from 'lucide-react';
import HelloWorldPanel from './components/HelloWorldPanel';
import ContextCompressionPanel from './components/ContextCompressionPanel';
import AIAgentPanel from './components/AIAgentPanel';
import PerformanceDashboard from './components/PerformanceDashboard';
import ToolOrchestrator from './components/ToolOrchestrator';
import './App.css';

interface SystemStatus {
  status: 'running' | 'paused' | 'stopped';
  uptime: number;
  activeConnections: number;
  totalRequests: number;
  successRate: number;
}

const App: React.FC = () => {
  const [activePanel, setActivePanel] = useState('hello-world');
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    status: 'running',
    uptime: 0,
    activeConnections: 0,
    totalRequests: 0,
    successRate: 0
  });
  const [isConnected, setIsConnected] = useState(false);

  // Simulate real-time system status updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStatus(prev => ({
        ...prev,
        uptime: prev.uptime + 1,
        activeConnections: Math.floor(Math.random() * 50) + 10,
        totalRequests: prev.totalRequests + Math.floor(Math.random() * 10),
        successRate: 95 + Math.random() * 5
      }));
    }, 1000);

    // Simulate connection
    setTimeout(() => setIsConnected(true), 2000);

    return () => clearInterval(interval);
  }, []);

  const panels = [
    { id: 'hello-world', name: 'Hello World', icon: Play, color: 'bg-blue-500' },
    { id: 'context-compression', name: 'Context Compression', icon: Brain, color: 'bg-purple-500' },
    { id: 'ai-agents', name: 'AI Agents', icon: Zap, color: 'bg-green-500' },
    { id: 'performance', name: 'Performance', icon: BarChart3, color: 'bg-orange-500' },
    { id: 'tools', name: 'Tool Orchestrator', icon: Settings, color: 'bg-red-500' }
  ];

  const renderActivePanel = () => {
    switch (activePanel) {
      case 'hello-world':
        return <HelloWorldPanel />;
      case 'context-compression':
        return <ContextCompressionPanel />;
      case 'ai-agents':
        return <AIAgentPanel />;
      case 'performance':
        return <PerformanceDashboard systemStatus={systemStatus} />;
      case 'tools':
        return <ToolOrchestrator />;
      default:
        return <HelloWorldPanel />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
                className="flex items-center space-x-2"
              >
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-xl font-bold text-white">
                  Context Engineering Master
                </h1>
              </motion.div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* System Status Indicator */}
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                } animate-pulse`} />
                <span className="text-sm text-slate-300">
                  {isConnected ? 'Connected' : 'Connecting...'}
                </span>
              </div>
              
              {/* System Stats */}
              <div className="hidden md:flex items-center space-x-4 text-sm text-slate-300">
                <div className="flex items-center space-x-1">
                  <Network className="w-4 h-4" />
                  <span>{systemStatus.activeConnections}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Monitor className="w-4 h-4" />
                  <span>{systemStatus.totalRequests}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <BarChart3 className="w-4 h-4" />
                  <span>{systemStatus.successRate.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <nav className="space-y-2">
              {panels.map((panel) => {
                const Icon = panel.icon;
                return (
                  <motion.button
                    key={panel.id}
                    onClick={() => setActivePanel(panel.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                      activePanel === panel.id
                        ? 'bg-slate-700 text-white shadow-lg'
                        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{panel.name}</span>
                  </motion.button>
                );
              })}
            </nav>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <AnimatePresence mode="wait">
              <motion.div
                key={activePanel}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6"
              >
                {renderActivePanel()}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-16 bg-slate-800/50 backdrop-blur-sm border-t border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-slate-400">
            <p className="text-sm">
              Powered by <span className="text-blue-400 font-semibold">Motia</span> • 
              Built with <span className="text-purple-400 font-semibold">Context Engineering</span> • 
              Unified Backend Framework
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;

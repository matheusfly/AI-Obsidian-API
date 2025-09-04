import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Zap, 
  Brain, 
  Network, 
  MessageSquare, 
  Send,
  Bot,
  CheckCircle,
  Clock,
  Activity,
  Users,
  Settings,
  Play,
  Pause
} from 'lucide-react';

interface AIAgent {
  id: string;
  type: 'context-engineer' | 'knowledge-extractor' | 'workflow-optimizer' | 'performance-monitor';
  name: string;
  status: 'active' | 'idle' | 'processing';
  lastActivity: string;
  tasksCompleted: number;
  successRate: number;
}

interface AgentResponse {
  agentType: string;
  task: string;
  solution: string;
  confidence: number;
  reasoning: string[];
  nextSteps: string[];
  performance: {
    responseTime: number;
    resourceUsage: number;
    successRate: number;
  };
}

const AIAgentPanel: React.FC = () => {
  const [agents, setAgents] = useState<AIAgent[]>([
    {
      id: '1',
      type: 'context-engineer',
      name: 'Context Engineer',
      status: 'active',
      lastActivity: '2 minutes ago',
      tasksCompleted: 15,
      successRate: 95
    },
    {
      id: '2',
      type: 'knowledge-extractor',
      name: 'Knowledge Extractor',
      status: 'processing',
      lastActivity: '30 seconds ago',
      tasksCompleted: 8,
      successRate: 92
    },
    {
      id: '3',
      type: 'workflow-optimizer',
      name: 'Workflow Optimizer',
      status: 'idle',
      lastActivity: '5 minutes ago',
      tasksCompleted: 12,
      successRate: 88
    },
    {
      id: '4',
      type: 'performance-monitor',
      name: 'Performance Monitor',
      status: 'active',
      lastActivity: '1 minute ago',
      tasksCompleted: 20,
      successRate: 98
    }
  ]);

  const [selectedAgent, setSelectedAgent] = useState<string>('1');
  const [task, setTask] = useState('');
  const [responses, setResponses] = useState<AgentResponse[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isAutoMode, setIsAutoMode] = useState(false);

  // Simulate agent activity
  useEffect(() => {
    const interval = setInterval(() => {
      setAgents(prev => prev.map(agent => ({
        ...agent,
        lastActivity: `${Math.floor(Math.random() * 5) + 1} minutes ago`,
        tasksCompleted: agent.tasksCompleted + (Math.random() > 0.7 ? 1 : 0),
        successRate: Math.min(100, agent.successRate + (Math.random() - 0.5) * 2)
      })));
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const handleTaskSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.trim()) return;

    setIsProcessing(true);
    
    const selectedAgentData = agents.find(a => a.id === selectedAgent);
    if (!selectedAgentData) return;

    // Simulate AI agent processing
    await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000));

    const mockResponse: AgentResponse = {
      agentType: selectedAgentData.type,
      task: task,
      solution: generateMockSolution(selectedAgentData.type, task),
      confidence: 0.85 + Math.random() * 0.15,
      reasoning: generateMockReasoning(selectedAgentData.type),
      nextSteps: generateMockNextSteps(selectedAgentData.type),
      performance: {
        responseTime: Math.random() * 1000 + 500,
        resourceUsage: Math.random() * 100,
        successRate: selectedAgentData.successRate
      }
    };

    setResponses(prev => [mockResponse, ...prev.slice(0, 4)]);
    setTask('');
    setIsProcessing(false);
  };

  const generateMockSolution = (agentType: string, task: string): string => {
    const solutions = {
      'context-engineer': `Analyzed the context engineering requirements for "${task}". Implemented a unified architecture using Motia framework with Flyde visual flows, MCP integration, and Context7 memory system. Created comprehensive context compression algorithms and real-time synchronization protocols.`,
      'knowledge-extractor': `Extracted and processed knowledge related to "${task}". Identified key patterns, relationships, and actionable insights. Compressed knowledge while preserving semantic meaning and created searchable knowledge base with automated extraction pipelines.`,
      'workflow-optimizer': `Optimized workflow patterns for "${task}". Created reusable templates, implemented automated optimization strategies, and established performance benchmarks. Reduced processing time by 40% and improved resource utilization.`,
      'performance-monitor': `Implemented comprehensive monitoring for "${task}". Created real-time dashboards, alerting mechanisms, and performance analytics. Established health check protocols and automated scaling strategies.`
    };
    return solutions[agentType as keyof typeof solutions] || `Processed task: ${task}`;
  };

  const generateMockReasoning = (agentType: string): string[] => {
    const reasoning = {
      'context-engineer': [
        'Analyzed existing tool fragmentation patterns',
        'Designed unified architecture using Motia framework',
        'Implemented context compression algorithms',
        'Created visual programming interface with Flyde',
        'Established MCP communication protocols'
      ],
      'knowledge-extractor': [
        'Analyzed documentation patterns across tools',
        'Identified common architectural patterns',
        'Extracted key insights and relationships',
        'Compressed knowledge while preserving meaning',
        'Created searchable knowledge base'
      ],
      'workflow-optimizer': [
        'Analyzed existing workflow patterns',
        'Identified optimization opportunities',
        'Created reusable workflow templates',
        'Implemented automated optimization',
        'Established performance benchmarks'
      ],
      'performance-monitor': [
        'Designed monitoring architecture',
        'Implemented real-time metrics collection',
        'Created alerting and notification system',
        'Set up performance dashboards',
        'Established health check protocols'
      ]
    };
    return reasoning[agentType as keyof typeof reasoning] || ['Processed task', 'Generated solution'];
  };

  const generateMockNextSteps = (agentType: string): string[] => {
    const nextSteps = {
      'context-engineer': [
        'Deploy interactive web UI',
        'Set up real-time monitoring',
        'Implement automated testing',
        'Create documentation system'
      ],
      'knowledge-extractor': [
        'Implement semantic search',
        'Create knowledge graphs',
        'Set up automated extraction',
        'Build recommendation engine'
      ],
      'workflow-optimizer': [
        'Deploy optimization algorithms',
        'Create workflow templates',
        'Implement performance monitoring',
        'Set up automated testing'
      ],
      'performance-monitor': [
        'Deploy monitoring infrastructure',
        'Set up alerting rules',
        'Create performance dashboards',
        'Implement automated scaling'
      ]
    };
    return nextSteps[agentType as keyof typeof nextSteps] || ['Continue processing', 'Monitor results'];
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
          <Zap className="w-6 h-6 text-green-400" />
          <h2 className="text-2xl font-bold text-white">AI Agent Coordination</h2>
          <Zap className="w-6 h-6 text-green-400" />
        </motion.div>
        <p className="text-slate-400">
          Multi-agent system for context engineering and tool orchestration
        </p>
      </div>

      {/* Agent Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {agents.map((agent) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`bg-slate-700/50 rounded-lg p-4 cursor-pointer transition-all duration-200 ${
              selectedAgent === agent.id ? 'ring-2 ring-green-500' : 'hover:bg-slate-600/50'
            }`}
            onClick={() => setSelectedAgent(agent.id)}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Bot className="w-5 h-5 text-green-400" />
                <h3 className="font-medium text-white">{agent.name}</h3>
              </div>
              <div className={`w-3 h-3 rounded-full ${
                agent.status === 'active' ? 'bg-green-500' :
                agent.status === 'processing' ? 'bg-yellow-500 animate-pulse' :
                'bg-slate-500'
              }`} />
            </div>
            
            <div className="space-y-1 text-sm text-slate-300">
              <div className="flex justify-between">
                <span>Tasks:</span>
                <span>{agent.tasksCompleted}</span>
              </div>
              <div className="flex justify-between">
                <span>Success:</span>
                <span>{agent.successRate.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Last Activity:</span>
                <span>{agent.lastActivity}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Task Input */}
      <div className="bg-slate-700/50 rounded-lg p-6">
        <form onSubmit={handleTaskSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Task Description
            </label>
            <textarea
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="Describe the task for the selected AI agent..."
              rows={3}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="auto-mode"
                checked={isAutoMode}
                onChange={(e) => setIsAutoMode(e.target.checked)}
                className="w-4 h-4 text-green-500 bg-slate-800 border-slate-600 rounded focus:ring-green-500"
              />
              <label htmlFor="auto-mode" className="text-sm text-slate-300">
                Auto Mode
              </label>
            </div>
            
            <motion.button
              type="submit"
              disabled={isProcessing || !task.trim()}
              className="bg-gradient-to-r from-green-500 to-blue-500 text-white py-2 px-6 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isProcessing ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-4 h-4 border-2 border-white border-t-transparent rounded-full"
                  />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Send Task</span>
                </>
              )}
            </motion.button>
          </div>
        </form>
      </div>

      {/* Agent Responses */}
      <AnimatePresence>
        {responses.map((response, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ delay: index * 0.1 }}
            className="bg-slate-700/50 rounded-lg p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <h3 className="text-lg font-semibold text-white">
                  {response.agentType.replace('-', ' ').toUpperCase()} Response
                </h3>
              </div>
              <div className="flex items-center space-x-4 text-sm text-slate-400">
                <div className="flex items-center space-x-1">
                  <Clock className="w-4 h-4" />
                  <span>{response.performance.responseTime.toFixed(0)}ms</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Activity className="w-4 h-4" />
                  <span>{response.performance.resourceUsage.toFixed(1)}%</span>
                </div>
                <div className="flex items-center space-x-1">
                  <BarChart3 className="w-4 h-4" />
                  <span>{(response.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-slate-800 rounded-lg p-4">
                <h4 className="font-medium text-white mb-2">Solution</h4>
                <p className="text-slate-300">{response.solution}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-800/50 rounded-lg p-4">
                  <h4 className="font-medium text-white mb-2 flex items-center space-x-2">
                    <Brain className="w-4 h-4 text-purple-400" />
                    <span>Reasoning</span>
                  </h4>
                  <ul className="space-y-1 text-sm text-slate-300">
                    {response.reasoning.map((reason, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <span className="text-purple-400 mt-1">•</span>
                        <span>{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-slate-800/50 rounded-lg p-4">
                  <h4 className="font-medium text-white mb-2 flex items-center space-x-2">
                    <Settings className="w-4 h-4 text-blue-400" />
                    <span>Next Steps</span>
                  </h4>
                  <ul className="space-y-1 text-sm text-slate-300">
                    {response.nextSteps.map((step, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <span className="text-blue-400 mt-1">•</span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Empty State */}
      {responses.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <Bot className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-400 mb-2">
            No agent responses yet
          </h3>
          <p className="text-slate-500">
            Select an agent and send a task to see AI coordination in action
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default AIAgentPanel;

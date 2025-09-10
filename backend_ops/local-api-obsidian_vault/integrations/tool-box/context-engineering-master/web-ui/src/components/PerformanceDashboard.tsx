import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  Activity, 
  Clock, 
  Zap,
  Database,
  Network,
  Cpu,
  MemoryStick,
  HardDrive
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface SystemStatus {
  status: 'running' | 'paused' | 'stopped';
  uptime: number;
  activeConnections: number;
  totalRequests: number;
  successRate: number;
}

interface PerformanceMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  responseTime: number;
  throughput: number;
}

const PerformanceDashboard: React.FC<{ systemStatus: SystemStatus }> = ({ systemStatus }) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    cpu: 45,
    memory: 62,
    disk: 38,
    network: 78,
    responseTime: 120,
    throughput: 850
  });

  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([]);
  const [isRealTime, setIsRealTime] = useState(true);

  // Generate mock time series data
  useEffect(() => {
    const generateData = () => {
      const data = [];
      const now = new Date();
      
      for (let i = 29; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60000); // Every minute
        data.push({
          time: time.toLocaleTimeString(),
          cpu: 30 + Math.random() * 40,
          memory: 40 + Math.random() * 30,
          requests: Math.floor(Math.random() * 100) + 50,
          responseTime: 50 + Math.random() * 200
        });
      }
      
      return data;
    };

    setTimeSeriesData(generateData());

    if (isRealTime) {
      const interval = setInterval(() => {
        setMetrics(prev => ({
          cpu: Math.max(0, Math.min(100, prev.cpu + (Math.random() - 0.5) * 10)),
          memory: Math.max(0, Math.min(100, prev.memory + (Math.random() - 0.5) * 5)),
          disk: Math.max(0, Math.min(100, prev.disk + (Math.random() - 0.5) * 3)),
          network: Math.max(0, Math.min(100, prev.network + (Math.random() - 0.5) * 15)),
          responseTime: Math.max(50, prev.responseTime + (Math.random() - 0.5) * 50),
          throughput: Math.max(100, prev.throughput + (Math.random() - 0.5) * 100)
        }));

        // Update time series data
        setTimeSeriesData(prev => {
          const newData = [...prev];
          newData.shift();
          const now = new Date();
          newData.push({
            time: now.toLocaleTimeString(),
            cpu: 30 + Math.random() * 40,
            memory: 40 + Math.random() * 30,
            requests: Math.floor(Math.random() * 100) + 50,
            responseTime: 50 + Math.random() * 200
          });
          return newData;
        });
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [isRealTime]);

  const pieData = [
    { name: 'API Calls', value: 45, color: '#3B82F6' },
    { name: 'Event Processing', value: 25, color: '#10B981' },
    { name: 'AI Agent Tasks', value: 20, color: '#F59E0B' },
    { name: 'Context Compression', value: 10, color: '#EF4444' }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400';
      case 'paused': return 'text-yellow-400';
      case 'stopped': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getMetricColor = (value: number, type: 'cpu' | 'memory' | 'disk' | 'network') => {
    if (value > 80) return 'text-red-400';
    if (value > 60) return 'text-yellow-400';
    return 'text-green-400';
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
          <BarChart3 className="w-6 h-6 text-orange-400" />
          <h2 className="text-2xl font-bold text-white">Performance Dashboard</h2>
          <BarChart3 className="w-6 h-6 text-orange-400" />
        </motion.div>
        <p className="text-slate-400">
          Real-time system monitoring and performance analytics
        </p>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">System Status</h3>
            <Activity className="w-5 h-5 text-slate-400" />
          </div>
          <div className={`text-2xl font-bold ${getStatusColor(systemStatus.status)}`}>
            {systemStatus.status.toUpperCase()}
          </div>
          <div className="text-sm text-slate-400">
            Uptime: {Math.floor(systemStatus.uptime / 60)}m {systemStatus.uptime % 60}s
          </div>
        </div>

        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">Active Connections</h3>
            <Network className="w-5 h-5 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-blue-400">
            {systemStatus.activeConnections}
          </div>
          <div className="text-sm text-slate-400">
            Real-time connections
          </div>
        </div>

        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">Total Requests</h3>
            <Zap className="w-5 h-5 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-green-400">
            {systemStatus.totalRequests.toLocaleString()}
          </div>
          <div className="text-sm text-slate-400">
            Since startup
          </div>
        </div>

        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">Success Rate</h3>
            <TrendingUp className="w-5 h-5 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-purple-400">
            {systemStatus.successRate.toFixed(1)}%
          </div>
          <div className="text-sm text-slate-400">
            Request success rate
          </div>
        </div>
      </div>

      {/* Resource Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">CPU Usage</h3>
            <Cpu className="w-5 h-5 text-slate-400" />
          </div>
          <div className={`text-2xl font-bold ${getMetricColor(metrics.cpu, 'cpu')}`}>
            {metrics.cpu.toFixed(1)}%
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 mt-2">
            <motion.div
              className="bg-blue-500 h-2 rounded-full"
              style={{ width: `${metrics.cpu}%` }}
              animate={{ width: `${metrics.cpu}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">Memory Usage</h3>
            <MemoryStick className="w-5 h-5 text-slate-400" />
          </div>
          <div className={`text-2xl font-bold ${getMetricColor(metrics.memory, 'memory')}`}>
            {metrics.memory.toFixed(1)}%
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 mt-2">
            <motion.div
              className="bg-green-500 h-2 rounded-full"
              style={{ width: `${metrics.memory}%` }}
              animate={{ width: `${metrics.memory}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">Disk Usage</h3>
            <HardDrive className="w-5 h-5 text-slate-400" />
          </div>
          <div className={`text-2xl font-bold ${getMetricColor(metrics.disk, 'disk')}`}>
            {metrics.disk.toFixed(1)}%
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 mt-2">
            <motion.div
              className="bg-yellow-500 h-2 rounded-full"
              style={{ width: `${metrics.disk}%` }}
              animate={{ width: `${metrics.disk}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        <div className="bg-slate-700/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-white">Network I/O</h3>
            <Network className="w-5 h-5 text-slate-400" />
          </div>
          <div className={`text-2xl font-bold ${getMetricColor(metrics.network, 'network')}`}>
            {metrics.network.toFixed(1)}%
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 mt-2">
            <motion.div
              className="bg-purple-500 h-2 rounded-full"
              style={{ width: `${metrics.network}%` }}
              animate={{ width: `${metrics.network}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Time Series Chart */}
        <div className="bg-slate-700/50 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">System Metrics Over Time</h3>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsRealTime(!isRealTime)}
                className={`px-3 py-1 rounded text-sm ${
                  isRealTime 
                    ? 'bg-green-500 text-white' 
                    : 'bg-slate-600 text-slate-300'
                }`}
              >
                {isRealTime ? 'Live' : 'Paused'}
              </button>
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }} 
              />
              <Line type="monotone" dataKey="cpu" stroke="#3B82F6" strokeWidth={2} />
              <Line type="monotone" dataKey="memory" stroke="#10B981" strokeWidth={2} />
              <Line type="monotone" dataKey="requests" stroke="#F59E0B" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Activity Distribution */}
        <div className="bg-slate-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Activity Distribution</h3>
          
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }} 
              />
            </PieChart>
          </ResponsiveContainer>
          
          <div className="mt-4 space-y-2">
            {pieData.map((item, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-slate-300">{item.name}</span>
                </div>
                <span className="text-slate-400">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Performance Summary */}
      <div className="bg-slate-700/50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Performance Summary</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {metrics.responseTime.toFixed(0)}ms
            </div>
            <div className="text-sm text-slate-400">Average Response Time</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">
              {metrics.throughput.toFixed(0)}
            </div>
            <div className="text-sm text-slate-400">Requests per Second</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">
              {systemStatus.successRate.toFixed(1)}%
            </div>
            <div className="text-sm text-slate-400">Success Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard;

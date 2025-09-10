import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Request interceptor for auth
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Health and system status
  async getHealth() {
    return this.client.get('/health');
  }

  async getMetrics() {
    return this.client.get('/metrics');
  }

  async getSystemStatus() {
    return this.client.get('/api/v1/system/status');
  }

  // Notes management
  async getNotes(folder = null, limit = 50) {
    const params = { limit };
    if (folder) params.folder = folder;
    return this.client.get('/api/v1/notes', { params });
  }

  async getNote(path) {
    return this.client.get(`/api/v1/notes/${encodeURIComponent(path)}`);
  }

  async createNote(noteData) {
    return this.client.post('/api/v1/notes', noteData);
  }

  async updateNote(path, content) {
    return this.client.put(`/api/v1/notes/${encodeURIComponent(path)}`, { content });
  }

  async deleteNote(path) {
    return this.client.delete(`/api/v1/notes/${encodeURIComponent(path)}`);
  }

  // Search functionality
  async searchNotes(query, options = {}) {
    const searchData = {
      query,
      limit: options.limit || 10,
      semantic: options.semantic || false
    };
    return this.client.post('/api/v1/search', searchData);
  }

  // MCP Tools
  async getMCPTools() {
    return this.client.get('/api/v1/mcp/tools');
  }

  async callMCPTool(tool, arguments) {
    return this.client.post('/api/v1/mcp/tools/call', { tool, arguments });
  }

  // AI and RAG
  async enhancedRAG(query, agentId, options = {}) {
    const requestData = {
      query,
      agent_id: agentId,
      use_hierarchical: options.hierarchical || true,
      max_depth: options.maxDepth || 3,
      context_history: options.contextHistory || null
    };
    return this.client.post('/api/v1/rag/enhanced', requestData);
  }

  async batchRAG(queries, agentId, batchSize = 5) {
    return this.client.post('/api/v1/rag/batch', {
      queries,
      agent_id: agentId,
      batch_size: batchSize
    });
  }

  // Analytics and performance
  async getPerformanceMetrics() {
    return this.client.get('/api/v1/performance/metrics');
  }

  async getAgentAnalytics(agentId, days = 7) {
    return this.client.get(`/api/v1/agents/${agentId}/analytics?days=${days}`);
  }

  // Supabase integration
  async getSupabaseHealth() {
    return this.client.get('/api/v1/supabase/health');
  }

  async updateAgentContext(agentId, context) {
    return this.client.post('/api/v1/agents/context', {
      agent_id: agentId,
      context
    });
  }

  // File operations
  async uploadFile(file, path) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('path', path);
    
    return this.client.post('/api/v1/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }

  // Workflow management (n8n integration)
  async getWorkflows() {
    return this.client.get('/api/v1/workflows');
  }

  async executeWorkflow(workflowId, data = {}) {
    return this.client.post(`/api/v1/workflows/${workflowId}/execute`, data);
  }

  // Real-time features
  connectWebSocket(onMessage, onError) {
    const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws';
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('WebSocket message parse error:', error);
      }
    };
    
    ws.onerror = onError;
    
    return ws;
  }
}

export const apiService = new ApiService();
export default apiService;